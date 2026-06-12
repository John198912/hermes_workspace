#!/usr/bin/env python3
"""
SoloPM 飞书客户端封装
- tenant_access_token 自动刷新
- 限流（写锁 + 退避重试）
- API 配额计数（budget.py 集成）
- 幂等写（client_token）
"""

import os
import time
import json
import hashlib
import logging
import threading
from pathlib import Path
from datetime import datetime, timedelta

import requests

logger = logging.getLogger("feishu_client")

# ─── 配置 ───────────────────────────────────────────────
SOLOPM_DIR = Path(os.environ.get("SOLOPM_DIR", Path(__file__).resolve().parent.parent))
STATE_DIR = SOLOPM_DIR / "state"
BUDGET_FILE = STATE_DIR / "api_budget.json"

FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_BASE = "https://open.feishu.cn/open-apis"

# ─── 全局状态 ───────────────────────────────────────────
_token_cache = {"token": None, "expires_at": 0}
_token_lock = threading.Lock()
_write_lock = threading.Lock()  # ADR: 同一时刻只允许一个写操作


# ═══════════════════════════════════════════════════════════
#  Token 与鉴权
# ═══════════════════════════════════════════════════════════

def get_tenant_token() -> str:
    """获取 tenant_access_token，自动刷新。"""
    now = time.time()
    with _token_lock:
        if _token_cache["token"] and now < _token_cache["expires_at"] - 300:
            return _token_cache["token"]

        if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
            raise RuntimeError("FEISHU_APP_ID / FEISHU_APP_SECRET 未设置")

        resp = requests.post(
            f"{FEISHU_BASE}/auth/v3/tenant_access_token/internal",
            json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
            timeout=10,
        )
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"获取 token 失败: {data}")

        _token_cache["token"] = data["tenant_access_token"]
        _token_cache["expires_at"] = now + data.get("expire", 7200)
        return _token_cache["token"]


def _headers():
    return {
        "Authorization": f"Bearer {get_tenant_token()}",
        "Content-Type": "application/json; charset=utf-8",
    }


# ═══════════════════════════════════════════════════════════
#  配额账本
# ═══════════════════════════════════════════════════════════

def _load_budget() -> dict:
    if BUDGET_FILE.exists():
        return json.loads(BUDGET_FILE.read_text())
    now = datetime.now()
    return {
        "month": f"{now.year}-{now.month:02d}",
        "count": 0,
        "limit": 10000,
    }


def _save_budget(b: dict):
    BUDGET_FILE.parent.mkdir(parents=True, exist_ok=True)
    BUDGET_FILE.write_text(json.dumps(b, indent=2))


def check_budget(action: str = "read") -> str:
    """
    检查配额，返回 "ok" / "warn" / "critical"。
    - "ok": 正常
    - "warn": >80%，停用非关键写入
    - "critical": >95%，全面降级只读
    """
    b = _load_budget()
    # 翻月重置
    now_month = f"{datetime.now().year}-{datetime.now().month:02d}"
    if b.get("month") != now_month:
        b = {"month": now_month, "count": 0, "limit": b.get("limit", 10000)}
        _save_budget(b)

    pct = b["count"] / b["limit"] if b["limit"] > 0 else 0
    if pct >= 0.95:
        return "critical"
    if pct >= 0.80:
        return "warn"
    return "ok"


def _count_call():
    """记录一次 API 调用。"""
    b = _load_budget()
    now_month = f"{datetime.now().year}-{datetime.now().month:02d}"
    if b.get("month") != now_month:
        b = {"month": now_month, "count": 0, "limit": b.get("limit", 10000)}
    b["count"] += 1
    _save_budget(b)


# ═══════════════════════════════════════════════════════════
#  HTTP 基础请求（带重试与限流）
# ═══════════════════════════════════════════════════════════

def _request(
    method: str,
    path: str,
    json_body: dict = None,
    params: dict = None,
    timeout: int = 30,
    max_retries: int = 3,
) -> dict:
    """统一请求入口：配额检查 → 重试 → 解析响应。"""
    url = f"{FEISHU_BASE}{path}"

    for attempt in range(max_retries):
        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=_headers(),
                json=json_body,
                params=params,
                timeout=timeout,
            )
            data = resp.json()
            code = data.get("code", -1)

            # Write conflict (1254291) → 退避重试
            if code == 1254291 and attempt < max_retries - 1:
                wait = (2 ** attempt) * 0.5  # 0.5, 1.0, 2.0
                logger.warning(f"Write conflict, retrying in {wait}s (attempt {attempt+1})")
                time.sleep(wait)
                continue

            # 配额超限
            if code == 99991403:
                logger.error("API quota exceeded!")
                return {"code": code, "msg": "quota_exceeded", "data": {}}

            _count_call()
            return data

        except requests.RequestException as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                logger.warning(f"Request error: {e}, retrying in {wait}s")
                time.sleep(wait)
            else:
                raise

    return {"code": -1, "msg": "max_retries_exceeded", "data": {}}


def _check_write_permission() -> bool:
    """检查是否允许写操作（配额护栏）。"""
    budget_status = check_budget("write")
    if budget_status == "critical":
        logger.error("配额 >95%，拒绝写入")
        return False
    return True


# ═══════════════════════════════════════════════════════════
#  Bitable API 封装
# ═══════════════════════════════════════════════════════════

def bitable_list_records(
    app_token: str,
    table_id: str,
    page_size: int = 500,
    page_token: str = None,
    filter_expr: str = None,
) -> dict:
    """列出记录（分页）。"""
    params = {"page_size": page_size}
    if page_token:
        params["page_token"] = page_token
    if filter_expr:
        params["filter"] = filter_expr

    return _request("GET", f"/bitable/v1/apps/{app_token}/tables/{table_id}/records", params=params)


def bitable_get_record(app_token: str, table_id: str, record_id: str) -> dict:
    """获取单条记录。"""
    return _request("GET", f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}")


def bitable_batch_get_records(
    app_token: str,
    table_id: str,
    record_ids: list[str],
) -> dict:
    """批量获取记录（最多 100 条）。"""
    return _request(
        "POST",
        f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_get",
        json_body={"records": record_ids},
    )


def bitable_create_record(
    app_token: str, table_id: str, fields: dict, client_token: str = None
) -> dict:
    """新增单条记录。"""
    if not _check_write_permission():
        return {"code": -1, "msg": "quota_blocked", "data": {}}

    body = {"fields": fields}
    with _write_lock:
        return _request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records",
            json_body=body,
            params={"client_token": client_token} if client_token else None,
        )


def bitable_batch_create_records(
    app_token: str, table_id: str, records: list[dict],
) -> dict:
    """批量新增（最多 500 条）。"""
    if not _check_write_permission():
        return {"code": -1, "msg": "quota_blocked", "data": {}}

    with _write_lock:
        return _request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
            json_body={"records": records},
        )


def bitable_update_record(
    app_token: str, table_id: str, record_id: str, fields: dict,
) -> dict:
    """更新单条记录。"""
    if not _check_write_permission():
        return {"code": -1, "msg": "quota_blocked", "data": {}}

    with _write_lock:
        return _request(
            "PUT",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
            json_body={"fields": fields},
        )


def bitable_batch_update_records(
    app_token: str, table_id: str, records: list[dict],
) -> dict:
    """批量更新（最多 1000 条）。每项 {"record_id": "...", "fields": {...}}"""
    if not _check_write_permission():
        return {"code": -1, "msg": "quota_blocked", "data": {}}

    with _write_lock:
        return _request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update",
            json_body={"records": records},
        )


def bitable_delete_record(app_token: str, table_id: str, record_id: str) -> dict:
    """删除单条记录。"""
    if not _check_write_permission():
        return {"code": -1, "msg": "quota_blocked", "data": {}}
    with _write_lock:
        return _request("DELETE", f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}")


def bitable_batch_delete_records(
    app_token: str, table_id: str, record_ids: list[str],
) -> dict:
    """批量删除。"""
    if not _check_write_permission():
        return {"code": -1, "msg": "quota_blocked", "data": {}}
    with _write_lock:
        return _request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete",
            json_body={"records": record_ids},
        )


# ═══════════════════════════════════════════════════════════
#  Bitable 元数据 API
# ═══════════════════════════════════════════════════════════

def bitable_create_app(name: str) -> dict:
    """创建多维表格 App。"""
    if not _check_write_permission():
        return {"code": -1, "msg": "quota_blocked"}
    return _request("POST", "/bitable/v1/apps", json_body={"name": name})


def bitable_list_tables(app_token: str) -> dict:
    """列出所有数据表。"""
    return _request("GET", f"/bitable/v1/apps/{app_token}/tables")


def bitable_create_table(app_token: str, table_name: str, fields: list[dict]) -> dict:
    """创建数据表。"""
    if not _check_write_permission():
        return {"code": -1, "msg": "quota_blocked"}
    return _request(
        "POST",
        f"/bitable/v1/apps/{app_token}/tables",
        json_body={"table": {"name": table_name}, "fields": fields},
    )


def bitable_add_fields(app_token: str, table_id: str, fields: list[dict]) -> dict:
    """添加字段。"""
    if not _check_write_permission():
        return {"code": -1, "msg": "quota_blocked"}
    return _request(
        "POST",
        f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
        json_body={"fields": fields},
    )


# ═══════════════════════════════════════════════════════════
#  消息 API
# ═══════════════════════════════════════════════════════════

def im_send_message(
    receive_id_type: str = "open_id",
    receive_id: str = "",
    msg_type: str = "interactive",
    content: str = "",
) -> dict:
    """发送消息（应用机器人）。"""
    if not _check_write_permission():
        return {"code": -1, "msg": "quota_blocked"}
    return _request(
        "POST",
        "/im/v1/messages",
        json_body={
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": content,
        },
        params={"receive_id_type": receive_id_type},
    )


# ═══════════════════════════════════════════════════════════
#  文档 API
# ═══════════════════════════════════════════════════════════

def docx_create(title: str, folder_token: str = "") -> dict:
    """创建飞书文档。"""
    if not _check_write_permission():
        return {"code": -1, "msg": "quota_blocked"}
    return _request(
        "POST",
        "/docx/v1/documents",
        json_body={"title": title, "folder_token": folder_token} if folder_token else {"title": title},
    )


def docx_add_blocks(document_id: str, blocks: list[dict]) -> dict:
    """向文档添加块。"""
    if not _check_write_permission():
        return {"code": -1, "msg": "quota_blocked"}
    return _request(
        "POST",
        f"/docx/v1/documents/{document_id}/blocks",
        json_body={"blocks": blocks},
    )


# ═══════════════════════════════════════════════════════════
#  健康检查
# ═══════════════════════════════════════════════════════════

def health_check() -> dict:
    """快速检查飞书 API 连通性。"""
    try:
        token = get_tenant_token()
        return {"status": "ok", "has_token": bool(token)}
    except Exception as e:
        return {"status": "error", "error": str(e)}
