#!/usr/bin/env python3
"""
精简飞书 API 客户端 —— Spark Diary 专用。
从 ~/.hermes/.env 读取 FEISHU_APP_ID/FEISHU_APP_SECRET。
只做三件事：读写表格记录、创建文档、发送消息。
"""

import json, os, time, requests
from pathlib import Path

API_BASE = "https://open.feishu.cn/open-apis"
ENV_PATH = Path.home() / ".hermes" / ".env"

def _load_env():
    env = {}
    if ENV_PATH.exists():
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env

class FeishuAPI:
    """飞书 v1 API 精简客户端"""

    def __init__(self):
        env = _load_env()
        self.app_id = env.get("FEISHU_APP_ID", "")
        self.app_secret = env.get("FEISHU_APP_SECRET", "")
        self._token = None
        self._token_expires = 0

    def _get_token(self):
        now = time.time()
        if self._token and now < self._token_expires - 60:
            return self._token
        r = requests.post(f"{API_BASE}/auth/v3/tenant_access_token/internal", json={
            "app_id": self.app_id, "app_secret": self.app_secret
        }, timeout=10)
        data = r.json()
        if data.get("code") != 0:
            raise Exception(f"Token error: {data.get('msg')}")
        self._token = data["tenant_access_token"]
        self._token_expires = now + data.get("expire", 7200)
        return self._token

    def _req(self, method, path, **kwargs):
        url = f"{API_BASE}{path}"
        headers = {"Authorization": f"Bearer {self._get_token()}"}
        for attempt in range(3):
            try:
                r = requests.request(method, url, headers=headers, timeout=15, **kwargs)
                data = r.json()
                if data.get("code") == 0:
                    return data.get("data", data)
                # token 过期
                if data.get("code") in (99991663, 99991664, 99991665, 99991666, 99991667, 99991668, 99991669):
                    self._token = None
                    headers["Authorization"] = f"Bearer {self._get_token()}"
                    continue
                raise Exception(f"API error: {data.get('msg')} (code={data.get('code')})")
            except requests.RequestException:
                if attempt == 2:
                    raise
                time.sleep(0.5 * (2 ** attempt))

    # ── 表格记录 ──
    def list_records(self, base_token, table_id, page_size=50):
        return self._req("GET", f"/bitable/v1/apps/{base_token}/tables/{table_id}/records",
                         params={"page_size": page_size})

    def create_record(self, base_token, table_id, fields):
        return self._req("POST", f"/bitable/v1/apps/{base_token}/tables/{table_id}/records",
                         json={"fields": fields})

    def update_record(self, base_token, table_id, record_id, fields):
        return self._req("PUT", f"/bitable/v1/apps/{base_token}/tables/{table_id}/records/{record_id}",
                         json={"fields": fields})

    def search_records(self, base_token, table_id, keyword, page_size=20):
        return self._req("GET", f"/bitable/v1/apps/{base_token}/tables/{table_id}/records/search",
                         params={"search": keyword, "page_size": page_size})

    # ── 文档 ──
    def create_document(self, title, folder_token=""):
        body = {"title": title}
        if folder_token:
            body["folder_token"] = folder_token
        return self._req("POST", "/docx/v1/documents", json=body)

    def append_blocks(self, doc_id, blocks, revision=-1):
        """blocks: list of {block_type, text/content/...}"""
        # 先获取最新 revision
        if revision < 0:
            meta = self._req("GET", f"/docx/v1/documents/{doc_id}")
            revision = meta.get("document", {}).get("revision", 0)
        return self._req("PATCH", f"/docx/v1/documents/{doc_id}/blocks/{doc_id}",
                         json={"blocks": blocks, "revision": revision})

    def create_children_blocks(self, doc_id, block_id, children, index=-1):
        """Create children blocks under a parent block.
        children: list of {block_type, text/content/...}
        index: insertion position (-1 for append to end)
        """
        body = {"children": children}
        if index >= 0:
            body["index"] = index
        return self._req("POST",
                         f"/docx/v1/documents/{doc_id}/blocks/{block_id}/children",
                         json=body)

    # ── 消息 ──
    def send_message(self, receive_id_type, receive_id, msg_type, content):
        return self._req("POST", "/im/v1/messages", params={
            "receive_id_type": receive_id_type
        }, json={
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": json.dumps(content) if isinstance(content, dict) else content
        })

    def send_text(self, open_id, text):
        return self.send_message("open_id", open_id, "text", {"text": text})
