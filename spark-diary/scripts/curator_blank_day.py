#!/usr/bin/env python3
"""Blank-day T3 write for spark-curator — parameterized.
Usage: python3 curator_blank_day.py [YYYY-MM-DD]
Defaults to today (Asia/Shanghai) if no date given.
Reads tokens from diary.yaml at runtime to avoid secret redaction issues."""
import sys, json, yaml
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, '/Users/lizhenjiang/hermes_workspace/spark-diary/shared/scripts')
from feishu_client import FeishuAPI

# Parse date argument
cst = timezone(timedelta(hours=8))
if len(sys.argv) > 1:
    try:
        dt = datetime.strptime(sys.argv[1], '%Y-%m-%d').replace(tzinfo=cst)
    except ValueError:
        print(json.dumps({"error": f"Invalid date: {sys.argv[1]}, expected YYYY-MM-DD"}))
        sys.exit(1)
else:
    now_cst = datetime.now(cst)
    dt = now_cst.replace(hour=0, minute=0, second=0, microsecond=0)

date_str = dt.strftime('%Y-%m-%d')
ts_ms = int(dt.timestamp() * 1000)

# Read config from diary.yaml
config_path = Path('/Users/lizhenjiang/hermes_workspace/spark-diary/diary.yaml')
with open(config_path) as f:
    config = yaml.safe_load(f)

feishu = config['feishu']
bt = feishu['base_app_token']
mt = feishu['table_ids']['materials']

report = {
    "date": date_str,
    "is_blank_day": True,
    "timestamp_ms": ts_ms,
}

api = FeishuAPI()

# Check if T3 already has a record for today
try:
    existing = api.list_records(bt, mt)
    items = existing.get('items') or []
    report["existing_t3_count"] = len(items)
except Exception as e:
    report["list_error"] = str(e)
    items = []

# Check if today already written
already_written = False
for item in items:
    fields = item.get('fields', {})
    fdate = fields.get('\u65e5\u671f', 0)
    if fdate == ts_ms:
        already_written = True
        report["already_exists"] = True
        report["existing_record_id"] = item.get('record_id')
        break

if not already_written:
    t3_fields = {
        "\u65e5\u671f": ts_ms,
        "\u5f53\u65e5\u7075\u611f\u6570": 0,
        "\u65e5\u7ed3\u72b6\u6001": "\u7a7a\u767d\u65e5",
    }
    try:
        result = api.create_record(bt, mt, t3_fields)
        report["t3_written"] = True
        report["t3_record"] = result.get('record', {}).get('record_id', 'unknown')
    except Exception as e:
        report["t3_error"] = str(e)
else:
    report["t3_skipped"] = "Record for today already exists"

print(json.dumps(report, indent=2, ensure_ascii=False))
