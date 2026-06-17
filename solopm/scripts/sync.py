#!/usr/bin/env python3
"""
SoloPM 双向增量同步 (S4: pm-sync)
- Bitable ↔ 文件仓库 双向字段级合并
- ADR-1: status/priority/due_date 以 Bitable 为准（人优先）
- ADR-1: title/desc/acceptance/outputs 以文件为准（Agent 优先）
- 增量：hash 比对，无变更不发请求
- v1.1: 默认命令模式（零 token），通过 exec 工具调用
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, date
from typing import Optional

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from feishu_client import (
    bitable_list_records,
    bitable_batch_create_records,
    bitable_batch_update_records,
    bitable_get_record,
    bitable_batch_delete_records,
    check_budget,
)
from task import read_task, write_task, create_task, set_status, log_event

SOLOPM_DIR = Path(os.environ.get("SOLOPM_DIR", Path(__file__).resolve().parent.parent))
STATE_DIR = SOLOPM_DIR / "state"
TASKS_DIR = STATE_DIR / "tasks"
SYNC_STATE_FILE = STATE_DIR / "sync_state.json"

# 字段归属规则
BITABLE_OWNS = {"status", "priority", "due_date", "blocked", "this_week"}
FILE_OWNS = {"title", "desc", "acceptance", "outputs", "exec_mode", "context", "effort"}
SHARED = {"project", "tid"}


def load_sync_state() -> dict:
    if SYNC_STATE_FILE.exists():
        return json.loads(SYNC_STATE_FILE.read_text())
    return {"app_token": "", "table_ids": {}, "last_pull": None, "record_map": {}, "field_hashes": {}}


def save_sync_state(ss: dict):
    ss["last_pull"] = datetime.now().isoformat()
    SYNC_STATE_FILE.write_text(json.dumps(ss, indent=2, ensure_ascii=False))


def fields_hash(fields: dict) -> str:
    """计算字段内容的 MD5（用于增量检测）。"""
    raw = json.dumps(fields, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(raw.encode()).hexdigest()


# ═══════════════════════════════════════════════════════════
#  PULL: Bitable → 文件
# ═══════════════════════════════════════════════════════════

def pull_from_bitable(app_token: str, table_id: str, ss: dict) -> dict:
    """
    从 Bitable 拉取变更，按字段归属合并到本地文件。
    返回 {changed, conflicts}.
    """
    changed = []
    conflicts = []
    page_token = None

    while True:
        resp = bitable_list_records(app_token, table_id, page_token=page_token)
        if resp.get("code") != 0:
            print(f"⚠️ pull 失败: {resp}")
            break

        data = resp.get("data", {})
        for item in data.get("items") or []:
            record_id = item.get("record_id")
            fields = item.get("fields", {})
            tid = fields.get("tid")

            if not tid:
                continue

            # 取前 6 个文本字段：如果 tid 在数组里
            if isinstance(tid, list):
                tid = tid[0].get("text", "") if tid else ""

            fhash = fields_hash(fields)

            # 检查文件是否存在
            if not (TASKS_DIR / f"{tid}.yaml").exists():
                # Bitable 有新任务，文件没有 → 用 Bitable 数据创建文件
                try:
                    create_task(
                        tid=tid,
                        title=fields.get("title", ""),
                        project=_extract_text(fields.get("project", "")),
                        status=_extract_text(fields.get("status", "Inbox")),
                        priority=_extract_text(fields.get("priority", "P2")),
                        due_date=_extract_date(fields.get("due_date")),
                        effort=_extract_text(fields.get("effort", "M")),
                        context=_extract_text(fields.get("context", "@deep")),
                        exec_mode=_extract_text(fields.get("exec_mode", "human")),
                    )
                    changed.append({"tid": tid, "action": "created_from_bitable"})
                except Exception as e:
                    conflicts.append({"tid": tid, "error": str(e)})
                continue

            # 文件存在 → 字段级合并
            try:
                local = read_task(tid)
                prev_hash = ss.get("field_hashes", {}).get(record_id, "")

                if fhash == prev_hash:
                    continue  # 无变化，跳过

                # 合并：Bitable 拥有的字段覆盖本地
                updated = False
                for bfield in BITABLE_OWNS:
                    if bfield in fields:
                        bval = _extract_value(fields[bfield])
                        if bval is not None and local.get(bfield) != bval:
                            local[bfield] = bval
                            updated = True

                if updated:
                    local["log"].append({
                        "ts": datetime.now().isoformat(),
                        "event": "synced_from_bitable",
                        "by": "sync-pull",
                    })
                    write_task(tid, local)
                    changed.append({"tid": tid, "action": "merged_from_bitable"})

                ss["field_hashes"][record_id] = fhash
                ss["record_map"][tid] = record_id

            except Exception as e:
                conflicts.append({"tid": tid, "error": str(e)})

        # 翻页
        if data.get("has_more"):
            page_token = data.get("page_token")
        else:
            break

    return {"changed": changed, "conflicts": conflicts, "pulled_at": datetime.now().isoformat()}


# ═══════════════════════════════════════════════════════════
#  PUSH: 文件 → Bitable
# ═══════════════════════════════════════════════════════════

def push_to_bitable(app_token: str, table_id: str, ss: dict) -> dict:
    """
    把本地文件变更推送到 Bitable。
    只推送 FILE_OWNS 字段（Bitable 侧不覆盖人在 UI 改的状态）。
    返回 {created, updated, deleted}.
    """
    created = []
    updated = []
    deleted = []

    if not TASKS_DIR.exists():
        return {"created": 0, "updated": 0, "deleted": 0}

    # 预算检查
    budget_status = check_budget("write")
    if budget_status == "critical":
        print("⚠️ 配额 >95%，跳过 push")
        return {"created": 0, "updated": 0, "deleted": 0, "skipped": "quota"}

    records_updates = []
    records_create = []

    for f in sorted(TASKS_DIR.glob("*.yaml")):
        try:
            task = yaml.safe_load(f.read_text(encoding="utf-8"))
            if not task:
                continue
            tid = task.get("tid")
            if not tid:
                continue

            record_id = ss.get("record_map", {}).get(tid)

            # 准备推送的字段（只包含 FILE_OWNS + SHARED）
            fields = {}
            for fname in FILE_OWNS | SHARED:
                val = task.get(fname)
                if val is not None:
                    # 数组字段转文本
                    if isinstance(val, list):
                        if fname == "outputs":
                            fields[fname] = json.dumps(val, ensure_ascii=False)
                        else:
                            fields[fname] = "\n".join(str(v) for v in val)
                    elif isinstance(val, bool):
                        fields[fname] = val
                    else:
                        fields[fname] = str(val) if val else ""

            # 添加 card_path
            fields["card_path"] = str(TASKS_DIR / f"{tid}.yaml")

            if record_id:
                # 比较 hash
                fhash = fields_hash(fields)
                if ss.get("field_hashes", {}).get(record_id) == fhash:
                    continue
                records_updates.append({"record_id": record_id, "fields": fields})
                ss["field_hashes"][record_id] = fhash
            else:
                records_create.append({"fields": fields})

        except Exception as e:
            print(f"⚠️ 跳过 {f}: {e}")

    # 批量执行
    if records_create:
        batch_size = 500
        for i in range(0, len(records_create), batch_size):
            batch = records_create[i:i+batch_size]
            resp = bitable_batch_create_records(app_token, table_id, batch)
            if resp.get("code") == 0:
                created_count = len(resp.get("data", {}).get("records", []))
                created.append(created_count)
                # 回写 record_id 到 sync_state
                for item in resp.get("data", {}).get("records", []):
                    tid = item.get("fields", {}).get("tid")
                    if tid:
                        ss["record_map"][tid] = item.get("record_id")
            else:
                print(f"⚠️ batch_create 失败: {resp}")

    if records_updates:
        batch_size = 1000
        for i in range(0, len(records_updates), batch_size):
            batch = records_updates[i:i+batch_size]
            resp = bitable_batch_update_records(app_token, table_id, batch)
            if resp.get("code") == 0:
                updated.append(len(batch))
            else:
                print(f"⚠️ batch_update 失败: {resp}")

    return {
        "created": sum(created),
        "updated": sum(updated),
        "deleted": 0,
        "pushed_at": datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════
#  工具函数
# ═══════════════════════════════════════════════════════════

def _extract_text(val) -> str:
    """从飞书字段值提取文本。"""
    if val is None:
        return ""
    if isinstance(val, str):
        return val
    if isinstance(val, list):
        if val and isinstance(val[0], dict):
            return val[0].get("text", "")
    if isinstance(val, bool):
        return str(val)
    return str(val)


def _extract_date(val) -> str:
    """从飞书日期字段提取 ISO 日期字符串。"""
    if val is None:
        return ""
    if isinstance(val, str):
        return val
    if isinstance(val, int):
        # Unix timestamp (ms)
        try:
            return datetime.fromtimestamp(val / 1000).strftime("%Y-%m-%d")
        except:
            return str(val)
    return str(val)


def _extract_value(val):
    """通用值提取：保留原始类型。"""
    if val is None:
        return None
    if isinstance(val, (str, bool, int, float)):
        return val
    if isinstance(val, list):
        if not val:
            return None
        if isinstance(val[0], dict):
            return val[0].get("text", str(val[0]))
        return val[0]
    return str(val)


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="SoloPM 双向同步")
    parser.add_argument("--pull-only", action="store_true", help="仅拉取")
    parser.add_argument("--push-only", action="store_true", help="仅推送")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    ss = load_sync_state()
    app_token = os.environ.get("SOLOPM_APP_TOKEN", ss.get("app_token", ""))
    table_id = os.environ.get("SOLOPM_TASKS_TABLE_ID", ss.get("table_ids", {}).get("Tasks", ""))

    if not app_token or not table_id:
        print(json.dumps({"error": "app_token 或 table_id 未配置"}, ensure_ascii=False))
        sys.exit(1)

    result = {"pull": None, "push": None}

    if not args.push_only:
        result["pull"] = pull_from_bitable(app_token, table_id, ss)

    if not args.pull_only:
        result["push"] = push_to_bitable(app_token, table_id, ss)

    save_sync_state(ss)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"📥 Pull: {result.get('pull', {}).get('changed', [])}")
        print(f"📤 Push: {result.get('push', {})}")


if __name__ == "__main__":
    main()
