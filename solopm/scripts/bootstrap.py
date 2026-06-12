#!/usr/bin/env python3
"""
SoloPM 初始化 (S1: pm-init)
- 创建飞书 Bitable App + 4 张表 + 字段
- 初始化 state 文件（sync_state / budget / 项目卡）
- 幂等：重复运行不报错
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from feishu_client import (
    bitable_create_app,
    bitable_list_tables,
    bitable_create_table,
    bitable_add_fields,
    health_check,
)

SOLOPM_DIR = Path(os.environ.get("SOLOPM_DIR", Path(__file__).resolve().parent.parent))
CONFIG_DIR = SOLOPM_DIR / "config"
STATE_DIR = SOLOPM_DIR / "state"
SCHEMA_FILE = CONFIG_DIR / "schema.yaml"
SYNC_STATE_FILE = STATE_DIR / "sync_state.json"
BUDGET_FILE = STATE_DIR / "api_budget.json"


def load_schema() -> dict:
    """加载表结构定义。"""
    return yaml.safe_load(SCHEMA_FILE.read_text(encoding="utf-8"))


def _field_def(f: dict) -> dict:
    """将 schema.yaml 的字段定义转为 Bitable API 格式。"""
    fd = {"field_name": f["field_name"], "type": f["type"]}
    # 单选/多选需要 options
    # 这里只设基本类型，options 需人工在 UI 配置或后续完善
    return fd


def init_bitable(dry_run: bool = False) -> dict:
    """
    创建 Bitable App + 表。返回 {app_token, tables: {name: table_id}}。
    幂等：已有则跳过。
    """
    if dry_run:
        print("[DRY RUN] 飞书 API 调用已模拟")
        return {"app_token": "MOCK_APP_TOKEN", "tables": {}}

    # 1. 连通性检查
    h = health_check()
    if h["status"] != "ok":
        print(f"❌ 飞书 API 不通: {h}")
        return {}

    schema = load_schema()

    # 2. 创建 App（暂时人工创建，此处仅打印提示）
    print("请先在飞书手动创建多维表格 App（或在下方输入现有 app_token）")
    print("飞书 → 新建 → 多维表格 → 命名为 'SoloPM 中枢'")
    app_token = input("app_token (留空则自动创建): ").strip()

    if not app_token:
        print("创建 App（需 bitable:app 权限）...")
        resp = bitable_create_app("SoloPM 中枢")
        if resp.get("code") == 0:
            app_token = resp["data"]["app"]["app_token"]
            print(f"✅ App 已创建: {app_token}")
        else:
            print(f"❌ 创建失败: {resp}")
            return {}

    # 3. 获取现有表
    tables_resp = bitable_list_tables(app_token)
    existing_tables = {}
    if tables_resp.get("code") == 0:
        for item in tables_resp.get("data", {}).get("items", []):
            existing_tables[item.get("name")] = item.get("table_id")

    table_ids = {}
    for table_name, table_def in schema["tables"].items():
        if table_name in existing_tables:
            print(f"⏭️  表 {table_name} 已存在 (table_id={existing_tables[table_name]})")
            table_ids[table_name] = existing_tables[table_name]
        else:
            print(f"创建表 {table_name}...")
            fields = [_field_def(f) for f in table_def["fields"]]
            resp = bitable_create_table(app_token, table_name, fields)
            if resp.get("code") == 0:
                tid = resp["data"]["table"]["table_id"]
                table_ids[table_name] = tid
                print(f"✅ {table_name} (table_id={tid})")
            else:
                print(f"❌ {table_name} 创建失败: {resp}")

    return {"app_token": app_token, "tables": table_ids}


def init_state(result: dict):
    """初始化 state/ 目录的文件。"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "tasks").mkdir(exist_ok=True)
    (STATE_DIR / "projects").mkdir(exist_ok=True)
    (STATE_DIR / "digests").mkdir(exist_ok=True)
    (STATE_DIR / "reviews").mkdir(exist_ok=True)

    # sync_state.json
    sync_state = {
        "app_token": result.get("app_token", ""),
        "table_ids": result.get("tables", {}),
        "last_pull": None,
        "last_push": None,
        "record_map": {},  # {tid: record_id}
        "field_hashes": {},  # {record_id: md5}
    }
    SYNC_STATE_FILE.write_text(json.dumps(sync_state, indent=2, ensure_ascii=False))
    print(f"✅ sync_state 已初始化")

    # api_budget.json
    now = datetime.now()
    budget = {
        "month": f"{now.year}-{now.month:02d}",
        "count": 0,
        "limit": 10000,
    }
    BUDGET_FILE.write_text(json.dumps(budget, indent=2))
    print(f"✅ api_budget 已初始化")

    # 项目卡模板
    projects = {
        "P-quant": {"pid": "P-quant", "name": "QuantSolo 量化系统 v4.0", "status": "Active", "para": "Project", "health": "OnTrack", "outcome": "", "deadline": "", "milestones": []},
        "P-aigc": {"pid": "P-aigc", "name": "AIGC 短视频创作", "status": "Active", "para": "Project", "health": "OnTrack", "outcome": "", "deadline": "", "milestones": []},
        "P-thesis": {"pid": "P-thesis", "name": "虚拟世界论文 v5", "status": "Active", "para": "Project", "health": "OnTrack", "outcome": "", "deadline": "", "milestones": []},
        "A-ops": {"pid": "A-ops", "name": "运营与生活事务", "status": "Active", "para": "Area", "health": "OnTrack", "outcome": "", "deadline": "", "milestones": []},
    }
    for pid, proj in projects.items():
        p = STATE_DIR / "projects" / f"{pid}.yaml"
        if not p.exists():
            p.write_text(yaml.dump(proj, allow_unicode=True, default_flow_style=False, sort_keys=False), encoding="utf-8")
    print("✅ 项目卡已初始化")

    print("\n📋 初始化完成！请将以下信息回填到 config/solopm.toml:")
    print(f"   app_token = \"{result.get('app_token', '')}\"")
    for name, tid in result.get("tables", {}).items():
        print(f"   {name} table_id = \"{tid}\"")


def main():
    parser = argparse.ArgumentParser(description="SoloPM 初始化")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--state-only", action="store_true", help="仅初始化 state 文件")
    args = parser.parse_args()

    print("🚀 SoloPM 初始化...")
    print(f"   项目目录: {SOLOPM_DIR}")

    if not args.state_only:
        result = init_bitable(dry_run=args.dry_run)
        if not result:
            print("⚠️ Bitable 初始化未完成，继续初始化本地 state...")
            result = {"app_token": "PENDING", "tables": {}}
    else:
        result = {"app_token": "MANUAL", "tables": {}}

    init_state(result)


if __name__ == "__main__":
    main()
