#!/usr/bin/env python3
"""
SoloPM 每日摘要生成器 (digest)
- 拉取今日到期 / Doing / 阻塞 / 本周聚焦任务
- WIP 超限检查（Doing > 3）
- Inbox 积压检查
- 输出 JSON 或 Markdown，写入 state/digests/YYYY-MM-DD.md
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import date, datetime

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from task import list_tasks, get_stats, WIP_LIMIT
from inbox import untriaged_count

SOLOPM_DIR = Path(os.environ.get("SOLOPM_DIR", Path(__file__).resolve().parent.parent))
STATE_DIR = SOLOPM_DIR / "state"
DIGESTS_DIR = STATE_DIR / "digests"


# ═══════════════════════════════════════════════════════════
#  核心逻辑
# ═══════════════════════════════════════════════════════════

def build_digest() -> dict:
    """构建当日摘要数据。"""
    today = date.today().isoformat()
    stats = get_stats()
    all_tasks = list_tasks()

    # 分类任务
    due_today = [t for t in all_tasks if t.get("due_date") == today]
    doing = [t for t in all_tasks if t.get("status") == "Doing"]
    blocked = [t for t in all_tasks if t.get("blocked")]
    this_week = [t for t in all_tasks if t.get("this_week")]
    done_today = [
        t for t in all_tasks
        if t.get("status") == "Done" and t.get("done_at") == today
    ]

    # WIP 检查
    doing_count = len(doing)
    wip_warning = doing_count > WIP_LIMIT
    wip_message = (
        f"⚠️ Doing 任务数 {doing_count}，超过 WIP 上限 {WIP_LIMIT}"
        if wip_warning else ""
    )

    # Inbox 积压
    inbox_count = untriaged_count()
    inbox_warning = inbox_count >= 10
    inbox_message = (
        f"📥 Inbox 未分拣: {inbox_count} 条，建议及时清理"
        if inbox_count > 0 else ""
    )

    # 摘要字段提取
    def _brief(t):
        return {
            "tid": t.get("tid"),
            "title": t.get("title"),
            "status": t.get("status"),
            "priority": t.get("priority"),
            "project": t.get("project", ""),
            "blocked": t.get("blocked", False),
            "due_date": t.get("due_date", ""),
            "effort": t.get("effort", "M"),
        }

    warnings = []
    if wip_warning:
        warnings.append({"type": "wip", "message": wip_message})
    if inbox_warning:
        warnings.append({"type": "inbox", "message": inbox_message})

    return {
        "date": today,
        "generated_at": datetime.now().isoformat(),
        "stats": stats,
        "wip": {
            "current": doing_count,
            "limit": WIP_LIMIT,
            "warning": wip_warning,
        },
        "inbox": {
            "untriaged": inbox_count,
            "warning": inbox_warning,
        },
        "warnings": warnings,
        "due_today": [_brief(t) for t in due_today],
        "doing": [_brief(t) for t in doing],
        "blocked": [_brief(t) for t in blocked],
        "this_week": [_brief(t) for t in this_week],
        "done_today": [_brief(t) for t in done_today],
    }


def format_digest_md(d: dict) -> str:
    """将摘要数据格式化为 Markdown。"""
    lines = [
        f"# 📋 SoloPM 每日摘要 — {d['date']}",
        "",
        f"**生成时间**: {d['generated_at']}",
        "",
    ]

    # WIP
    wip = d["wip"]
    wip_icon = "🔴" if wip["warning"] else "🟢"
    lines.append(f"## {wip_icon} WIP 状态")
    lines.append(f"- Doing: **{wip['current']}** / {wip['limit']}")
    if wip["warning"]:
        lines.append(f"- ⚠️ **WIP 超限!** 请完成或暂停部分任务。")
    lines.append("")

    # Inbox
    inbox = d["inbox"]
    inbox_icon = "🔴" if inbox["warning"] else "🟢"
    lines.append(f"## {inbox_icon} Inbox")
    lines.append(f"- 未分拣: **{inbox['untriaged']}** 条")
    if inbox["warning"]:
        lines.append(f"- ⚠️ Inbox 积压严重，建议及时分拣。")
    lines.append("")

    # 统计
    stats = d["stats"]
    lines.append("## 📊 统计概览")
    lines.append(f"- 总计: {stats['total']} | 阻塞: {stats['blocked']} | 今日到期: {stats['due_today']} | 本周聚焦: {stats['this_week']}")
    bs = stats.get("by_status", {})
    status_line = " | ".join(f"{k}: {v}" for k, v in bs.items() if v > 0)
    lines.append(f"- 状态分布: {status_line}")
    lines.append("")

    # 分区
    sections = [
        ("📅 今日到期", "due_today"),
        ("🔄 Doing", "doing"),
        ("🚫 阻塞", "blocked"),
        ("⭐ 本周聚焦", "this_week"),
        ("✅ 今日完成", "done_today"),
    ]

    for title, key in sections:
        items = d.get(key, [])
        if not items:
            continue
        lines.append(f"## {title} ({len(items)})")
        lines.append("")
        for t in items:
            blocked_mark = " 🚫" if t.get("blocked") else ""
            prio = t.get("priority", "")
            proj = f" [{t['project']}]" if t.get("project") else ""
            due = f" 📅{t['due_date']}" if t.get("due_date") else ""
            lines.append(f"- **{prio}** {t['tid']}: {t['title']}{proj}{blocked_mark}{due}")
        lines.append("")

    # 警告汇总
    if d["warnings"]:
        lines.append("## ⚠️ 注意事项")
        for w in d["warnings"]:
            lines.append(f"- {w['message']}")
        lines.append("")

    return "\n".join(lines)


def write_digest(d: dict) -> Path:
    """写入 digest 文件，返回路径。"""
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    md_content = format_digest_md(d)
    path = DIGESTS_DIR / f"{d['date']}.md"
    path.write_text(md_content, encoding="utf-8")
    return path


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="SoloPM 每日摘要")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--quick", action="store_true", help="快速模式（仅统计，不写文件）")
    parser.add_argument("--no-write", action="store_true", help="不写入 digest 文件")
    args = parser.parse_args()

    d = build_digest()

    # 快速模式：仅输出统计
    if args.quick:
        quick = {
            "date": d["date"],
            "total": d["stats"]["total"],
            "doing": d["wip"]["current"],
            "wip_limit": d["wip"]["limit"],
            "wip_warning": d["wip"]["warning"],
            "inbox_untriaged": d["inbox"]["untriaged"],
            "due_today": len(d["due_today"]),
            "blocked": len(d["blocked"]),
            "this_week": len(d["this_week"]),
        }
        if args.json:
            print(json.dumps(quick, ensure_ascii=False, indent=2))
        else:
            print(f"日期: {quick['date']}")
            print(f"任务总数: {quick['total']}")
            print(f"Doing: {quick['doing']}/{quick['wip_limit']} {'⚠️ 超限!' if quick['wip_warning'] else '✅'}")
            print(f"Inbox 未分拣: {quick['inbox_untriaged']}")
            print(f"今日到期: {quick['due_today']} | 阻塞: {quick['blocked']} | 本周聚焦: {quick['this_week']}")
        return

    # JSON 输出
    if args.json:
        print(json.dumps(d, ensure_ascii=False, indent=2))
    else:
        print(format_digest_md(d))

    # 写文件
    if not args.no_write:
        path = write_digest(d)
        if not args.json:
            print(f"\n📝 已写入: {path}")


if __name__ == "__main__":
    main()
