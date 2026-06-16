#!/usr/bin/env python3
"""Write blank day record to T3."""
import sys, yaml
sys.path.insert(0, '/Users/lizhenjiang/hermes_workspace/spark-diary/shared/scripts')
from feishu_client import FeishuAPI
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json

# Read config for base_token
config_path = Path('/Users/lizhenjiang/hermes_workspace/spark-diary/diary.yaml')
with open(config_path) as f:
    config = yaml.safe_load(f)
BASE_TOKEN = config['feishu']['base_app_token']

cst = timezone(timedelta(hours=8))
dt = datetime(2026, 6, 16, 0, 0, 0, tzinfo=cst)
ts_ms = int(dt.timestamp() * 1000)

api = FeishuAPI()
TABLE_MATERIALS = 'tblBtmKRLwZm2yzf'

fields = {
    '日期': ts_ms,
    '当日灵感数': 0,
    '日结状态': '空白日',
}
try:
    result = api.create_record(BASE_TOKEN, TABLE_MATERIALS, fields)
    print(json.dumps({'status': 'ok', 'ts': ts_ms, 'date': '2026-06-16', 'record': str(result)[:200]}, ensure_ascii=False))
except Exception as e:
    print(json.dumps({'status': 'error', 'error': str(e)}, ensure_ascii=False))
