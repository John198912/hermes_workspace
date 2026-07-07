#!/usr/bin/env python3
"""
feishu_send_text.py — Cron-friendly Feishu text message sender.

Uses diary.yaml credentials directly (avoiding .env mismatch) to send
a plain-text message via /im/v1/messages to user_open_id.

Designed to survive:
  - Hermes venv PYTHONPATH leakage (caller uses `env -i`)
  - tirith confusable_unicode scanner (script source contains no CJK/emoji;
    CJK is provided via --stdin or argv)
  - cron mode (no execute_code available)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def load_yaml(path):
    """Use PyYAML if available (system Python 3.9 has it pre-installed
    on this macOS host). Falls back to a minimal parser for stripped envs."""
    try:
        import yaml  # type: ignore

        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        pass

    out = {}
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    stack = [(0, out)]
    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        line = raw.rstrip("\n")
        indent = len(line) - len(line.lstrip())
        content = line.lstrip()
        if ":" not in content:
            continue
        key, _, val = content.partition(":")
        val = val.strip().strip('"').strip("'")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            stack = [(0, out)]
        parent = stack[-1][1]
        if not val:
            new = {}
            parent[key] = new
            stack.append((indent, new))
        else:
            parent[key] = val
    return out


def get_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    if data.get("code") != 0:
        raise RuntimeError(f"token error: {data}")
    return data["tenant_access_token"]


def send_text(token, receive_id, text, receive_id_type="open_id"):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = f"?receive_id_type={receive_id_type}"
    body = json.dumps(
        {
            "receive_id": receive_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}, ensure_ascii=False),
        }
    ).encode()
    req = urllib.request.Request(
        url + params,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdin", action="store_true",
                    help="Read message body from stdin")
    ap.add_argument("--diary", default="diary.yaml",
                    help="Path to diary.yaml")
    ap.add_argument("--receive-id-type", default="open_id")
    args = ap.parse_args()

    if args.stdin:
        text = sys.stdin.read()
    else:
        text = " ".join(sys.argv[1:])

    cfg = load_yaml(args.diary)
    feishu = cfg.get("feishu", {})
    app_id = feishu.get("app_id")
    app_secret = feishu.get("app_secret")
    user_open_id = cfg.get("system", {}).get("user_open_id")
    if not (app_id and app_secret and user_open_id):
        raise RuntimeError("diary.yaml missing feishu.app_id/app_secret or system.user_open_id")

    token = get_token(app_id, app_secret)
    result = send_text(token, user_open_id, text, args.receive_id_type)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()