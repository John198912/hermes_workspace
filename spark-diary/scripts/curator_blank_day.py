#!/usr/bin/env python3
"""Blank-day T3 write for spark-curator — 2026-06-20.
Reads tokens from diary.yaml at runtime to avoid secret redaction issues."""
import sys, json, yaml
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, '/Users/lizhenjiang/hermes_workspace/spark-diary/shared/scripts')
from feishu_client import FeishuAPI

# Read config from diary.yaml
config_path = Path('/Users/lizhenjiang/hermes_workspace/spark-diary/diary.yaml')
with open(config_path) as f:
    config = yaml.safe_load(f)

BASE_TOKEN = config['feishu']['base_app_token']
TABLE_MATERIALS = config['feishu']['table_ids']['materials']

# Today in Asia/Shanghai, 00:00
cst = timezone(timedelta(hours=8))
dt = datetime(2026, 6, 20, 0, 0, 0, tzinfo=cst)
ts_ms = int(dt.timestamp() * 1000)

report = {
    "date": "2026-06-20",
    "is_blank_day": True,
    "timestamp_ms": ts_ms,
}

api = FeishuAPI()

# Check if T3 already has a record for today
try:
    existing = api.list_records(BASE_TOKEN, TABLE_MATERIALS)
    items = existing.get('items') or []
    report["existing_t3_count"] = len(items)
except Exception as e:
    report["list_error"] = str(e)
    items = []

# Check if today already written
already_written = False
for item in items:
    fields = item.get('fields', {})
    fdate = fields.get('日期', 0)
    if fdate == ts_ms:
        already_written = True
        report["already_exists"] = True
        report["existing_record_id"] = item.get('record_id')
        break

if not already_written:
    t3_fields = {
        "日期": ts_ms,
        "当日灵感数": 0,
        "日结状态": "空白日",
    }
    try:
        result = api.create_record(BASE_TOKEN, TABLE_MATERIALS, t3_fields)
        report["t3_written"] = True
        report["t3_record"] = result.get('record', {}).get('record_id', 'unknown')
    except Exception as e:
        report["t3_error"] = str(e)
else:
    report["t3_skipped"] = "Record for today already exists"

print(json.dumps(report, indent=2, ensure_ascii=False))
