#!/usr/bin/env python3
"""
SoloPM 统一通知出口 (notify)
- digest 模式: 读取 digest 文件，生成消息并发送
- alert 模式: 发送告警通知
- l3 模式: L3 级别领导升级通知
- 优先走飞书 im_send_message，备用群 webhook
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from feishu_client import im_send_message

logger = logging.getLogger("notify")

SOLOPM_DIR = Path(os.environ.get("SOLOPM_DIR", Path(__file__).resolve().parent.parent))
STATE_DIR = SOLOPM_DIR / "state"
DIGESTS_DIR = STATE_DIR / "digests"

# 飞书配置（从环境变量或配置文件读取）
FEISHU_USER_OPEN_ID = os.environ.get("FEISHU_USER_OPEN_ID", "")
FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "")
FEISHU_WEBHOOK_SECRET = os.environ.get("FEISHU_WEBHOOK_SECRET", "")


# ═══════════════════════════════════════════════════════════
#  消息构建
# ═══════════════════════════════════════════════════════════

def build_digest_message(file_path: Optional[str] = None) -> str:
    """从 digest 文件或默认位置构建消息内容。"""
    if file_path:
        p = Path(file_path)
    else:
        # 找最新 digest
        today = datetime.now().strftime("%Y-%m-%d")
        p = DIGESTS_DIR / f"{today}.md"

    if not p.exists():
        # 找不到当日 digest，回溯查找最近的
        if DIGESTS_DIR.exists():
            digests = sorted(DIGESTS_DIR.glob("*.md"), reverse=True)
            if digests:
                p = digests[0]

    if not p.exists():
        return f"📋 SoloPM 每日摘要\n\n⚠️ 暂无 digest 文件: {p}"

    text = p.read_text(encoding="utf-8")

    # 截取关键部分：前 4000 字符（飞书消息体限制约 30KB，这里保守）
    if len(text) > 4000:
        text = text[:4000] + "\n\n...(内容过长，已截断)"

    return text


def build_alert_message(text: str, level: str = "warn") -> str:
    """构建告警消息。"""
    icons = {"info": "ℹ️", "warn": "⚠️", "error": "🚨", "critical": "🔴"}
    icon = icons.get(level, "⚠️")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        f"{icon} SoloPM 告警 [{level.upper()}]\n"
        f"时间: {ts}\n"
        f"内容: {text}"
    )


def build_l3_message(text: str) -> str:
    """构建 L3 升级消息（领导级别）。"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"🔴🔴  L3 升级通知 🔴🔴\n"
        f"时间: {ts}\n"
        f"触发原因: 关键指标持续异常\n"
        f"详情: {text}\n\n"
        f"请立即关注并采取行动。"
    )


# ═══════════════════════════════════════════════════════════
#  发送渠道
# ═══════════════════════════════════════════════════════════

def _send_via_feishu_im(content: str) -> dict:
    """通过飞书应用消息发送。"""
    if not FEISHU_USER_OPEN_ID:
        return {"code": -1, "msg": "FEISHU_USER_OPEN_ID 未配置", "channel": "feishu_im"}

    # 飞书消息内容需为 JSON 字符串（interactive 或 text 格式）
    msg_content = json.dumps({"text": content}, ensure_ascii=False)

    return im_send_message(
        receive_id_type="open_id",
        receive_id=FEISHU_USER_OPEN_ID,
        msg_type="text",
        content=msg_content,
    )


def _send_via_webhook(content: str) -> dict:
    """通过群自定义 Webhook 发送（备用）。"""
    if not FEISHU_WEBHOOK_URL:
        return {"code": -1, "msg": "FEISHU_WEBHOOK_URL 未配置", "channel": "webhook"}

    try:
        # 构造飞书富文本消息
        body = {
            "msg_type": "text",
            "content": {"text": content},
        }

        # 如果有 secret，计算签名
        # 注：飞书 webhook 签名算法需要 timestamp + secret 做 HMAC-SHA256
        if FEISHU_WEBHOOK_SECRET:
            import hmac
            import hashlib
            import time as _time
            timestamp = str(int(_time.time()))
            sign_string = f"{timestamp}\n{FEISHU_WEBHOOK_SECRET}"
            sign = hmac.new(
                FEISHU_WEBHOOK_SECRET.encode("utf-8"),
                sign_string.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).hexdigest()
            body["timestamp"] = timestamp
            body["sign"] = sign

        resp = requests.post(FEISHU_WEBHOOK_URL, json=body, timeout=15)
        data = resp.json()
        if data.get("code") == 0:
            return {"code": 0, "msg": "ok", "channel": "webhook"}
        return {"code": data.get("code", -1), "msg": data.get("msg", str(data)), "channel": "webhook"}

    except Exception as e:
        return {"code": -1, "msg": str(e), "channel": "webhook"}


def send_message(content: str, prefer_feishu: bool = True) -> dict:
    """
    统一发送入口：优先飞书 IM，失败则走 Webhook。
    返回发送结果。
    """
    results = []

    if prefer_feishu and FEISHU_USER_OPEN_ID:
        r = _send_via_feishu_im(content)
        results.append(r)
        if r.get("code") == 0:
            return {"sent": True, "channel": "feishu_im", "results": results}

    # 备用 webhook
    r = _send_via_webhook(content)
    results.append(r)
    if r.get("code") == 0:
        return {"sent": True, "channel": "webhook", "results": results}

    return {"sent": False, "channel": "none", "results": results}


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="SoloPM 统一通知")
    sub = parser.add_subparsers(dest="mode", required=True)

    # digest
    p_digest = sub.add_parser("digest", help="发送每日摘要")
    p_digest.add_argument("--file", "-f", default=None, help="指定 digest 文件路径")
    p_digest.add_argument("--text", "-t", default=None, help="附加文本")
    p_digest.add_argument("--dry-run", action="store_true", help="仅预览消息，不发送")

    # alert
    p_alert = sub.add_parser("alert", help="发送告警通知")
    p_alert.add_argument("--text", "-t", required=True, help="告警内容")
    p_alert.add_argument("--level", "-l", default="warn",
                         choices=["info", "warn", "error", "critical"],
                         help="告警级别")
    p_alert.add_argument("--dry-run", action="store_true", help="仅预览消息，不发送")

    # l3
    p_l3 = sub.add_parser("l3", help="L3 领导升级通知")
    p_l3.add_argument("--text", "-t", required=True, help="升级说明")
    p_l3.add_argument("--dry-run", action="store_true", help="仅预览消息，不发送")

    args = parser.parse_args()

    if args.mode == "digest":
        content = build_digest_message(args.file)
        if args.text:
            content = content + "\n\n" + args.text

    elif args.mode == "alert":
        content = build_alert_message(args.text, args.level)

    elif args.mode == "l3":
        content = build_l3_message(args.text)

    else:
        parser.print_help()
        sys.exit(1)

    # 预览
    if args.dry_run:
        print("=== 消息预览 ===")
        print(content)
        print("=== 预览结束（未发送）===")
        return

    # 发送
    result = send_message(content)
    if result.get("sent"):
        print(json.dumps({"status": "sent", **result}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"status": "failed", **result}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
