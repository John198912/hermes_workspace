#!/usr/bin/env python3
"""
SoloPM 收件箱管理
- 快速捕获：一句话即落 Inbox
- 分拣：Inbox → 生成任务卡
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

import yaml

# 添加父目录到 path（简单调用）
sys.path.insert(0, str(Path(__file__).resolve().parent))

SOLOPM_DIR = Path(os.environ.get("SOLOPM_DIR", Path(__file__).resolve().parent.parent))
STATE_DIR = SOLOPM_DIR / "state"
INBOX_FILE = STATE_DIR / "inbox.jsonl"


def add_inbox(raw: str, source: str = "manual") -> int:
    """向收件箱添加一条。"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "id": _next_id(),
        "raw": raw.strip(),
        "source": source,
        "triaged": False,
        "created_at": datetime.now().isoformat(),
    }
    with open(INBOX_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry["id"]


def list_inbox(triaged: bool = False) -> list[dict]:
    """列出收件箱条目。"""
    if not INBOX_FILE.exists():
        return []
    items = []
    with open(INBOX_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                if item.get("triaged") != triaged:
                    items.append(item)
            except:
                pass
    return items


def mark_triaged(item_id: int):
    """标记为已分拣（重写文件）。"""
    if not INBOX_FILE.exists():
        return
    lines = INBOX_FILE.read_text().strip().split("\n")
    updated = []
    for line in lines:
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            if item.get("id") == item_id:
                item["triaged"] = True
            updated.append(item)
        except:
            pass
    INBOX_FILE.write_text("\n".join(json.dumps(i, ensure_ascii=False) for i in updated) + "\n")


def untriaged_count() -> int:
    return len(list_inbox(triaged=False))


def _next_id() -> int:
    if not INBOX_FILE.exists():
        return 1
    max_id = 0
    with open(INBOX_FILE) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                max_id = max(max_id, item.get("id", 0))
            except:
                pass
    return max_id + 1


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="SoloPM 收件箱")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("count", help="未分拣数量")

    p_add = sub.add_parser("add", help="添加条目")
    p_add.add_argument("raw")
    p_add.add_argument("--source", default="manual")

    p_list = sub.add_parser("list", help="列出条目")
    p_list.add_argument("--all", action="store_true", help="包含已分拣")
    p_list.add_argument("--format", default="table", choices=["table", "json"])

    p_triage = sub.add_parser("triage", help="标记已分拣")
    p_triage.add_argument("id", type=int)

    args = parser.parse_args()

    if args.cmd == "count":
        print(untriaged_count())

    elif args.cmd == "add":
        item_id = add_inbox(args.raw, args.source)
        print(f"📥 #{item_id}: {args.raw}")

    elif args.cmd == "list":
        include_triaged = args.all
        items = list_inbox(triaged=include_triaged)
        if args.format == "json":
            print(json.dumps(items, ensure_ascii=False, indent=2))
        else:
            if not items:
                print("收件箱为空")
            for i in items:
                status = "✅" if i.get("triaged") else "📥"
                print(f"{status} #{i['id']}: {i['raw']} [{i.get('source','?')}]")

    elif args.cmd == "triage":
        mark_triaged(args.id)
        print(f"✅ #{args.id} 已分拣")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
