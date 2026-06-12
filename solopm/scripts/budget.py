#!/usr/bin/env python3
"""
SoloPM API 配额账本 (budget)
- status: 显示当前配额使用情况 {used, limit, pct}
- rollover: 翻月重置计数
- 读取/写入 state/api_budget.json
- 与 feishu_client.py 共享预算文件，提供独立的 CLI 管理入口
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))

SOLOPM_DIR = Path(os.environ.get("SOLOPM_DIR", Path(__file__).resolve().parent.parent))
STATE_DIR = SOLOPM_DIR / "state"
BUDGET_FILE = STATE_DIR / "api_budget.json"

# 默认值
DEFAULT_LIMIT = 10000
WARN_PCT = 0.80
CRITICAL_PCT = 0.95


# ═══════════════════════════════════════════════════════════
#  配额账本核心
# ═══════════════════════════════════════════════════════════

def _ensure_dir():
    """确保 state 目录存在。"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_budget() -> dict:
    """加载配额账本，不存在则初始化。"""
    if BUDGET_FILE.exists():
        try:
            data = json.loads(BUDGET_FILE.read_text())
            # 兼容旧格式
            if not isinstance(data, dict):
                data = {}
            return data
        except (json.JSONDecodeError, ValueError):
            return _new_budget()

    return _new_budget()


def _new_budget() -> dict:
    """创建新的配额账本。"""
    now = datetime.now()
    return {
        "month": f"{now.year}-{now.month:02d}",
        "count": 0,
        "limit": DEFAULT_LIMIT,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }


def save_budget(b: dict):
    """写入配额账本。"""
    _ensure_dir()
    b["updated_at"] = datetime.now().isoformat()
    BUDGET_FILE.write_text(json.dumps(b, ensure_ascii=False, indent=2) + "\n")


def get_status() -> dict:
    """
    获取配额状态：自动检测跨月并重置。
    返回 {month, used, limit, pct, status, message}。
    """
    b = load_budget()
    now_month = f"{datetime.now().year}-{datetime.now().month:02d}"

    # 跨月自动重置
    if b.get("month") != now_month:
        # 保存上个月用量（可选审计）
        previous = {
            "month": b.get("month", ""),
            "used": b.get("count", 0),
            "limit": b.get("limit", DEFAULT_LIMIT),
        }
        b = {
            "month": now_month,
            "count": 0,
            "limit": b.get("limit", DEFAULT_LIMIT),
            "previous": previous,
            "rollover_at": datetime.now().isoformat(),
        }
        save_budget(b)

    used = b.get("count", 0)
    limit = b.get("limit", DEFAULT_LIMIT)
    pct = used / limit if limit > 0 else 0

    # 状态判定
    if pct >= CRITICAL_PCT:
        status = "critical"
        msg = f"配额已用 {pct:.1%}，超过 {CRITICAL_PCT:.0%} 临界线，全面只读"
    elif pct >= WARN_PCT:
        status = "warn"
        msg = f"配额已用 {pct:.1%}，超过 {WARN_PCT:.0%} 警戒线，停用非关键写入"
    else:
        status = "ok"
        msg = f"配额正常，已用 {pct:.1%}"

    return {
        "month": now_month,
        "used": used,
        "limit": limit,
        "pct": round(pct, 4),
        "status": status,
        "message": msg,
        "remaining": limit - used,
    }


def rollover(force: bool = False) -> dict:
    """
    翻月重置。
    如果当前月份和目标月份相同且不强制，则跳过。
    """
    b = load_budget()
    now_month = f"{datetime.now().year}-{datetime.now().month:02d}"
    old_month = b.get("month", "")

    if old_month == now_month and not force:
        return {
            "rolled": False,
            "message": f"当前月份 {now_month} 无需重置（使用 --force 强制）",
            "month": old_month,
            "used": b.get("count", 0),
        }

    previous = {
        "month": old_month,
        "used": b.get("count", 0),
        "limit": b.get("limit", DEFAULT_LIMIT),
    }

    new_b = {
        "month": now_month,
        "count": 0,
        "limit": b.get("limit", DEFAULT_LIMIT),
        "previous": previous,
        "rollover_at": datetime.now().isoformat(),
    }
    save_budget(new_b)

    return {
        "rolled": True,
        "message": f"已翻月: {old_month} → {now_month}（上月用量: {previous['used']}）",
        "from": old_month,
        "to": now_month,
        "previous_count": previous["used"],
    }


def set_limit(new_limit: int) -> dict:
    """设置新的月度配额上限。"""
    if new_limit < 1:
        raise ValueError(f"配额上限必须 > 0，收到: {new_limit}")

    b = load_budget()
    old_limit = b.get("limit", DEFAULT_LIMIT)
    b["limit"] = new_limit
    save_budget(b)

    return {
        "changed": True,
        "old_limit": old_limit,
        "new_limit": new_limit,
        "message": f"配额上限已更新: {old_limit} → {new_limit}",
    }


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="SoloPM API 配额账本管理")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # status
    p_status = sub.add_parser("status", help="显示当前配额使用情况")
    p_status.add_argument("--json", action="store_true", default=True,
                          help="JSON 输出（默认）")

    # rollover
    p_rollover = sub.add_parser("rollover", help="翻月重置配额")
    p_rollover.add_argument("--force", action="store_true",
                            help="强制重置（即使月份未变）")

    # set-limit
    p_set = sub.add_parser("set-limit", help="设置月度配额上限")
    p_set.add_argument("limit", type=int, help="新的月度上限")

    args = parser.parse_args()

    if args.cmd == "status":
        s = get_status()
        if getattr(args, "json", True):
            print(json.dumps(s, ensure_ascii=False, indent=2))
        else:
            icon = {"ok": "🟢", "warn": "🟡", "critical": "🔴"}.get(s["status"], "❓")
            print(f"{icon} 配额状态 [{s['month']}]")
            print(f"   已用: {s['used']} / {s['limit']} ({s['pct']:.1%})")
            print(f"   剩余: {s['remaining']}")
            print(f"   状态: {s['status']} — {s['message']}")

    elif args.cmd == "rollover":
        r = rollover(force=args.force)
        print(json.dumps(r, ensure_ascii=False, indent=2))

    elif args.cmd == "set-limit":
        r = set_limit(args.limit)
        print(json.dumps(r, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
