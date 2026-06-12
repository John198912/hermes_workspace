#!/usr/bin/env python3
"""
SoloPM GTD 周回顾自动化
- 列 Inbox 未分拣 / Doing / 本周 Done
- 引导确认每个项目的 health
- 勾选下周 this_week 任务
- 生成 state/reviews/YYYY-Www.md
CLI: python scripts/review.py [--json]
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, date, timedelta

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from task import list_tasks, read_task, write_task, log_event
from inbox import list_inbox

logger = logging.getLogger("review")

SOLOPM_DIR = Path(os.environ.get("SOLOPM_DIR", Path(__file__).resolve().parent.parent))
STATE_DIR = SOLOPM_DIR / "state"
PROJECTS_DIR = STATE_DIR / "projects"
REVIEWS_DIR = STATE_DIR / "reviews"

HEALTH_OPTIONS = ["OnTrack", "AtRisk", "OffTrack"]


def week_label(d: date = None) -> str:
    """返回 ISO 周标签 YYYY-Www。"""
    d = d or date.today()
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def week_range(d: date = None) -> tuple[date, date]:
    """返回本周的周一和周日。"""
    d = d or date.today()
    start = d - timedelta(days=d.weekday())
    end = start + timedelta(days=6)
    return start, end


def collect_review_data() -> dict:
    """收集回顾所需数据。"""
    today = date.today()
    monday, sunday = week_range(today)

    # 未分拣收件箱
    inbox_items = [i for i in list_inbox(triaged=False)]

    # Doing 任务
    doing_tasks = list_tasks(status="Doing")

    # 本周 Done（done_at 在本周范围内）
    all_tasks = list_tasks()
    week_done = []
    for t in all_tasks:
        if t.get("status") != "Done":
            continue
        done_at = t.get("done_at", "")
        if done_at:
            try:
                d = date.fromisoformat(done_at)
                if monday <= d <= sunday:
                    week_done.append(t)
            except (ValueError, TypeError):
                pass

    # 加载所有项目
    projects = {}
    if PROJECTS_DIR.exists():
        for f in sorted(PROJECTS_DIR.glob("*.yaml")):
            try:
                proj = yaml.safe_load(f.read_text(encoding="utf-8"))
                if proj and isinstance(proj, dict):
                    pid = proj.get("pid", f.stem)
                    projects[pid] = proj
            except Exception as e:
                logger.warning(f"跳过损坏的项目卡 {f}: {e}")

    # 本周聚焦任务
    this_week_tasks = list_tasks(this_week=True)

    # 任务统计
    stats = {
        "inbox_untriaged": len(inbox_items),
        "doing": len(doing_tasks),
        "done_this_week": len(week_done),
        "this_week": len(this_week_tasks),
    }

    return {
        "week": week_label(today),
        "monday": monday.isoformat(),
        "sunday": sunday.isoformat(),
        "generated_at": datetime.now().isoformat(),
        "inbox_untriaged": inbox_items,
        "doing": doing_tasks,
        "done_this_week": week_done,
        "projects": projects,
        "this_week_tasks": this_week_tasks,
        "stats": stats,
        "all_tasks": all_tasks,
    }


def interactive_health_check(projects: dict) -> dict:
    """交互式确认每个项目的 health 状态。"""
    print("\n📊 项目健康检查（输入 OnTrack / AtRisk / OffTrack，回车保持现状）")
    updates = {}
    for pid, proj in sorted(projects.items()):
        current = proj.get("health", "OnTrack")
        resp = input(f"  {proj.get('name', pid)} [{current}]: ").strip()
        if resp and resp in HEALTH_OPTIONS and resp != current:
            updates[pid] = resp
    return updates


def interactive_pick_this_week(all_tasks: list[dict]) -> list[str]:
    """交互式勾选下周 this_week 任务。"""
    print("\n⭐ 勾选下周聚焦任务（Todo/Doing 状态）")
    candidates = [
        t for t in all_tasks
        if t.get("status") in ("Todo", "Doing") and not t.get("this_week")
    ]
    if not candidates:
        print("  没有候选任务。")
        return []

    for i, t in enumerate(candidates):
        print(f"  [{i:2d}] {t['tid']}: {t['title']} [{t.get('priority', '?')}]")

    selection = input("\n  输入序号（逗号分隔，回车跳过）: ").strip()
    if not selection:
        return []

    picked = []
    for part in selection.split(","):
        try:
            idx = int(part.strip())
            if 0 <= idx < len(candidates):
                picked.append(candidates[idx]["tid"])
        except ValueError:
            pass
    return picked


def apply_review(data: dict, health_updates: dict, picked_tids: list[str]):
    """应用回顾中的变更。"""
    # 更新项目 health
    for pid, health in health_updates.items():
        p_file = PROJECTS_DIR / f"{pid}.yaml"
        if p_file.exists():
            proj = yaml.safe_load(p_file.read_text(encoding="utf-8"))
            old = proj.get("health", "OnTrack")
            proj["health"] = health
            proj["updated_at"] = datetime.now().isoformat()
            p_file.write_text(
                yaml.dump(proj, allow_unicode=True, default_flow_style=False, sort_keys=False),
                encoding="utf-8",
            )
            log_event("health_update", pid, f"{old}→{health}", by="review")

    # 设置 this_week
    for tid in picked_tids:
        try:
            t = read_task(tid)
            if not t.get("this_week"):
                t["this_week"] = True
                t["log"].append({
                    "ts": datetime.now().isoformat(),
                    "event": "this_week flagged by review",
                    "by": "review",
                })
                write_task(tid, t)
                log_event("this_week", tid, "flagged", by="review")
        except Exception as e:
            logger.warning(f"标记 this_week 失败 {tid}: {e}")


def generate_review_md(data: dict) -> str:
    """生成周回顾 Markdown。"""
    lines = []
    lines.append(f"# SoloPM 周回顾 {data['week']}")
    lines.append(f"**周期**: {data['monday']} → {data['sunday']}")
    lines.append(f"**生成时间**: {data['generated_at']}")
    lines.append("")

    stats = data["stats"]
    lines.append("## 📊 概览")
    lines.append(f"- 未分拣收件箱: **{stats['inbox_untriaged']}**")
    lines.append(f"- Doing 任务: **{stats['doing']}**")
    lines.append(f"- 本周完成: **{stats['done_this_week']}**")
    lines.append(f"- 本周聚焦: **{stats['this_week']}**")
    lines.append("")

    if data["inbox_untriaged"]:
        lines.append("## 📥 未分拣收件箱")
        for item in data["inbox_untriaged"]:
            lines.append(f"- #{item['id']}: {item['raw']} [{item.get('source', '?')}]")
        lines.append("")

    if data["doing"]:
        lines.append("## 🔄 Doing 任务")
        for t in data["doing"]:
            lines.append(f"- **{t['tid']}**: {t['title']} [{t.get('priority', '?')}]")
        lines.append("")

    if data["done_this_week"]:
        lines.append("## ✅ 本周完成")
        for t in data["done_this_week"]:
            lines.append(f"- **{t['tid']}**: {t['title']}")
        lines.append("")

    lines.append("## 📁 项目健康")
    for pid, proj in sorted(data["projects"].items()):
        health_icon = {"OnTrack": "🟢", "AtRisk": "🟡", "OffTrack": "🔴"}.get(
            proj.get("health", "OnTrack"), "⚪"
        )
        lines.append(
            f"- {health_icon} **{proj.get('name', pid)}**: {proj.get('health', 'OnTrack')}"
        )
    lines.append("")

    if data["this_week_tasks"]:
        lines.append("## ⭐ 本周聚焦")
        for t in data["this_week_tasks"]:
            lines.append(f"- **{t['tid']}**: {t['title']} [{t.get('status', '?')}]")
        lines.append("")

    return "\n".join(lines)


def save_review_md(data: dict):
    """保存周回顾到 state/reviews/。"""
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    path = REVIEWS_DIR / f"{data['week']}.md"
    content = generate_review_md(data)
    path.write_text(content, encoding="utf-8")
    print(f"\n✅ 周回顾已保存: {path}")


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="SoloPM GTD 周回顾")
    parser.add_argument("--json", action="store_true", help="仅输出 JSON 数据（非交互）")
    parser.add_argument("--no-save", action="store_true", help="不保存 Markdown")
    args = parser.parse_args()

    data = collect_review_data()
    week = data["week"]

    if args.json:
        # 去除非 JSON 安全的字段（如 Path 对象）
        output = {
            "week": data["week"],
            "monday": data["monday"],
            "sunday": data["sunday"],
            "generated_at": data["generated_at"],
            "stats": data["stats"],
            "inbox_count": len(data["inbox_untriaged"]),
            "doing_count": len(data["doing"]),
            "done_count": len(data["done_this_week"]),
            "projects": {
                pid: {
                    "name": p.get("name", ""),
                    "health": p.get("health", "OnTrack"),
                    "deadline": p.get("deadline", ""),
                }
                for pid, p in data["projects"].items()
            },
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print(f"\n📋 SoloPM 周回顾 — {week}")
    print(f"   周期: {data['monday']} → {data['sunday']}")
    print(f"   未分拣: {data['stats']['inbox_untriaged']} | Doing: {data['stats']['doing']} | 本周完成: {data['stats']['done_this_week']}")

    # 1. 项目健康检查
    health_updates = interactive_health_check(data["projects"])

    # 2. 勾选下周聚焦任务
    picked = interactive_pick_this_week(data["all_tasks"])

    # 3. 应用变更
    if health_updates or picked:
        print("\n📝 应用变更...")
        apply_review(data, health_updates, picked)

    # 4. 保存回顾
    if not args.no_save:
        # 重新收集以包含最新变更
        data = collect_review_data()
        save_review_md(data)

    print("✅ 周回顾完成。")


if __name__ == "__main__":
    main()
