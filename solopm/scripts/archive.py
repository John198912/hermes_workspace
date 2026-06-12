#!/usr/bin/env python3
"""
SoloPM 任务归档
- 归档 Done>30天 的任务
- 移动任务卡到 state/archive/<tid>.yaml
- 从 Bitable 删除对应行（调用 feishu_client）
- 记录事件日志
CLI: python scripts/archive.py [--dry-run] [--days 30]
"""

import os
import sys
import json
import argparse
import logging
import shutil
from pathlib import Path
from datetime import datetime, date, timedelta

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from task import list_tasks, log_event, TASKS_DIR, STATE_DIR
from feishu_client import bitable_list_records, bitable_delete_record, bitable_batch_delete_records, check_budget

logger = logging.getLogger("archive")

SOLOPM_DIR = Path(os.environ.get("SOLOPM_DIR", Path(__file__).resolve().parent.parent))
ARCHIVE_DIR = STATE_DIR / "archive"
ARCHIVE_LOG_FILE = STATE_DIR / "archive_log.jsonl"


def load_sync_state() -> dict:
    """加载同步状态以获取 record_map。"""
    sf = STATE_DIR / "sync_state.json"
    if sf.exists():
        return json.loads(sf.read_text())
    return {"app_token": "", "table_ids": {}, "record_map": {}}


def find_archivable_tasks(days: int = 30) -> list[dict]:
    """
    查找可归档的 Done 任务（done_at 早于 N 天前）。
    """
    cutoff = date.today() - timedelta(days=days)
    cutoff_str = cutoff.isoformat()

    all_tasks = list_tasks()
    candidates = []

    for t in all_tasks:
        if t.get("status") != "Done":
            continue
        done_at = t.get("done_at", "")
        if not done_at:
            continue
        try:
            d = date.fromisoformat(done_at)
            if d <= cutoff:
                candidates.append(t)
        except (ValueError, TypeError):
            logger.warning(f"无效 done_at: {t.get('tid')} → {done_at}")

    return candidates


def archive_task_file(tid: str, task: dict) -> bool:
    """将任务卡从 state/tasks/ 移动到 state/archive/。"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    src = TASKS_DIR / f"{tid}.yaml"
    dst = ARCHIVE_DIR / f"{tid}.yaml"

    if not src.exists():
        logger.warning(f"任务卡不存在: {src}")
        return False

    # 添加归档元数据
    task["archived_at"] = datetime.now().isoformat()
    task["archive_source"] = str(src)

    # 先写归档副本再删除源文件
    dst.write_text(
        yaml.dump(task, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    src.unlink()

    logger.info(f"已归档: {tid} → {dst}")
    return True


def delete_from_bitable(
    tids: list[str],
    app_token: str,
    table_id: str,
    record_map: dict,
    dry_run: bool = False,
) -> dict:
    """
    从 Bitable 删除已归档任务的对应行。
    返回 {deleted, failed, skipped}。
    """
    result = {"deleted": 0, "failed": 0, "skipped": 0}

    if not app_token or not table_id:
        logger.warning("app_token 或 table_id 未配置，跳过 Bitable 删除")
        result["skipped"] = len(tids)
        return result

    if dry_run:
        result["skipped"] = len(tids)
        return result

    # 配额检查
    budget_status = check_budget("write")
    if budget_status == "critical":
        logger.error("配额 >95%，跳过 Bitable 删除")
        result["skipped"] = len(tids)
        return result

    # 收集 record_ids
    record_ids = []
    tid_to_record = {}
    for tid in tids:
        rid = record_map.get(tid)
        if rid:
            record_ids.append(rid)
            tid_to_record[tid] = rid
        else:
            # 尝试从 Bitable 搜索
            logger.info(f"{tid}: record_id 不在 sync_state 中，跳过")

    if not record_ids:
        result["skipped"] = len(tids)
        return result

    # 批量删除（每次最多 100 条）
    BATCH_SIZE = 100
    for i in range(0, len(record_ids), BATCH_SIZE):
        batch = record_ids[i:i + BATCH_SIZE]
        try:
            resp = bitable_batch_delete_records(app_token, table_id, batch)
            if resp.get("code") == 0:
                result["deleted"] += len(batch)
                logger.info(f"Bitable 批量删除成功: {len(batch)} 条")
            else:
                # 批量删除失败，尝试逐条删除
                logger.warning(f"批量删除失败: {resp}，尝试逐条删除")
                for rid in batch:
                    single_resp = bitable_delete_record(app_token, table_id, rid)
                    if single_resp.get("code") == 0:
                        result["deleted"] += 1
                    else:
                        result["failed"] += 1
                        logger.error(f"删除失败 {rid}: {single_resp}")
        except Exception as e:
            result["failed"] += len(batch)
            logger.error(f"删除异常: {e}")

    return result


def log_archive(tid: str, task: dict, success: bool, error: str = ""):
    """记录归档事件到日志文件。"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "tid": tid,
        "title": task.get("title", ""),
        "project": task.get("project", ""),
        "done_at": task.get("done_at", ""),
        "success": success,
        "error": error,
    }
    with open(ARCHIVE_LOG_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_archive(days: int = 30, dry_run: bool = False) -> dict:
    """
    执行归档流程。
    返回结果统计。
    """
    candidates = find_archivable_tasks(days)
    if not candidates:
        print("没有需要归档的任务。")
        return {"candidates": 0, "archived": 0, "bitable_deleted": 0, "failed": 0}

    print(f"找到 {len(candidates)} 个可归档任务（Done >{days} 天）")

    if dry_run:
        print("\n[DRY RUN] 将归档以下任务：")
        for t in candidates:
            print(f"  - {t['tid']}: {t['title']} (done_at={t.get('done_at', '?')})")
        return {"candidates": len(candidates), "archived": 0, "bitable_deleted": 0, "failed": 0}

    # 文件归档
    archived = 0
    archived_tids = []
    for t in candidates:
        tid = t["tid"]
        try:
            if archive_task_file(tid, t):
                archived += 1
                archived_tids.append(tid)
                log_event("archived", tid, f"done_at={t.get('done_at','')}", by="archive")
                log_archive(tid, t, True)
        except Exception as e:
            logger.error(f"归档文件失败 {tid}: {e}")
            log_archive(tid, t, False, str(e))

    # Bitable 删除
    ss = load_sync_state()
    app_token = os.environ.get("SOLOPM_APP_TOKEN", ss.get("app_token", ""))
    table_id = os.environ.get("SOLOPM_TASKS_TABLE_ID", ss.get("table_ids", {}).get("Tasks", ""))

    bt_result = delete_from_bitable(
        archived_tids, app_token, table_id, ss.get("record_map", {}), dry_run=dry_run
    )

    return {
        "candidates": len(candidates),
        "archived": archived,
        "bitable_deleted": bt_result["deleted"],
        "bitable_failed": bt_result["failed"],
        "bitable_skipped": bt_result["skipped"],
        "failed": len(candidates) - archived,
    }


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="SoloPM 任务归档")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际执行")
    parser.add_argument("--days", type=int, default=30, help="Done 超过多少天归档（默认 30）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    print(f"\n🗄️  SoloPM 任务归档 (Done >{args.days} 天)")
    if args.dry_run:
        print("   [DRY RUN 模式]")

    result = run_archive(days=args.days, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n📊 归档结果:")
        print(f"   候选任务: {result['candidates']}")
        print(f"   文件归档: {result['archived']}")
        print(f"   Bitable 删除: {result['bitable_deleted']}")
        if result.get("bitable_failed", 0) > 0:
            print(f"   Bitable 失败: {result['bitable_failed']}")
        if result.get("bitable_skipped", 0) > 0:
            print(f"   Bitable 跳过: {result['bitable_skipped']}")
        if result["failed"] > 0:
            print(f"   失败: {result['failed']}")

    print("✅ 归档完成。")


if __name__ == "__main__":
    main()
