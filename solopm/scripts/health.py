#!/usr/bin/env python3
"""
SoloPM 项目健康评估
- 读取 projects/*.yaml
- 计算 deadline 临近度 × 任务完成率
- 输出 OnTrack / AtRisk / OffTrack
CLI: python scripts/health.py [--json]
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
from task import list_tasks

logger = logging.getLogger("health")

SOLOPM_DIR = Path(os.environ.get("SOLOPM_DIR", Path(__file__).resolve().parent.parent))
STATE_DIR = SOLOPM_DIR / "state"
PROJECTS_DIR = STATE_DIR / "projects"

# 权重配置
DEADLINE_WEIGHT = 0.5          # deadline 临近权重
COMPLETION_WEIGHT = 0.5        # 任务完成率权重
DEADLINE_CRITICAL_DAYS = 3     # <3 天 → 高危
DEADLINE_WARN_DAYS = 7         # <7 天 → 警告
COMPLETION_CRITICAL_THRESHOLD = 0.3   # 完成率 <30% → 高危
COMPLETION_WARN_THRESHOLD = 0.6       # 完成率 <60% → 警告


def load_projects() -> dict[str, dict]:
    """加载所有项目卡。"""
    projects = {}
    if not PROJECTS_DIR.exists():
        return projects
    for f in sorted(PROJECTS_DIR.glob("*.yaml")):
        try:
            proj = yaml.safe_load(f.read_text(encoding="utf-8"))
            if proj and isinstance(proj, dict):
                pid = proj.get("pid", f.stem)
                projects[pid] = proj
        except Exception as e:
            logger.warning(f"跳过损坏的项目卡 {f}: {e}")
    return projects


def project_task_stats(pid: str) -> dict:
    """统计单个项目的任务。"""
    tasks = list_tasks(project=pid)
    total = len(tasks)
    done = sum(1 for t in tasks if t.get("status") == "Done")
    doing = sum(1 for t in tasks if t.get("status") == "Doing")
    todo = sum(1 for t in tasks if t.get("status") == "Todo")
    blocked = sum(1 for t in tasks if t.get("blocked"))

    completion_rate = done / total if total > 0 else 0.0
    return {
        "total": total,
        "done": done,
        "doing": doing,
        "todo": todo,
        "blocked": blocked,
        "completion_rate": round(completion_rate, 2),
    }


def deadline_risk(deadline_str: str) -> tuple[str, int]:
    """
    评估 deadline 风险。
    返回 (risk_level, days_remaining)。
    risk_level: "critical" | "warn" | "ok" | "none"（无截止日）
    """
    if not deadline_str:
        return ("none", 0)

    try:
        dl = date.fromisoformat(deadline_str)
    except (ValueError, TypeError):
        return ("none", 0)

    today = date.today()
    days = (dl - today).days

    if days < 0:
        return ("critical", days)   # 已逾期
    elif days <= DEADLINE_CRITICAL_DAYS:
        return ("critical", days)
    elif days <= DEADLINE_WARN_DAYS:
        return ("warn", days)
    else:
        return ("ok", days)


def completion_risk(rate: float) -> str:
    """评估完成率风险。"""
    if rate < COMPLETION_CRITICAL_THRESHOLD:
        return "critical"
    elif rate < COMPLETION_WARN_THRESHOLD:
        return "warn"
    else:
        return "ok"


def compute_health(deadline_risk_level: str, completion_risk_level: str) -> str:
    """
    综合 deadline 风险和完成率风险，计算健康状态。
    - OnTrack: 两项都 ok
    - AtRisk: 至少一项 warn
    - OffTrack: 至少一项 critical
    """
    risk_map = {"none": "ok", "ok": "ok", "warn": "warn", "critical": "critical"}
    dr = risk_map.get(deadline_risk_level, "ok")
    cr = risk_map.get(completion_risk_level, "ok")

    risks = [dr, cr]
    if "critical" in risks:
        return "OffTrack"
    elif "warn" in risks:
        return "AtRisk"
    else:
        return "OnTrack"


def assess_all_projects() -> list[dict]:
    """评估所有项目的健康状态。"""
    projects = load_projects()
    results = []

    for pid, proj in sorted(projects.items()):
        tstats = project_task_stats(pid)

        dl_risk, days_left = deadline_risk(proj.get("deadline", ""))
        c_risk = completion_risk(tstats["completion_rate"])
        health = compute_health(dl_risk, c_risk)

        # 判断是否需要更新项目卡
        current_health = proj.get("health", "OnTrack")
        health_changed = (health != current_health)

        result = {
            "pid": pid,
            "name": proj.get("name", pid),
            "para": proj.get("para", "Project"),
            "deadline": proj.get("deadline", ""),
            "days_left": days_left,
            "deadline_risk": dl_risk,
            "completion_rate": tstats["completion_rate"],
            "completion_risk": c_risk,
            "current_health": current_health,
            "computed_health": health,
            "health_changed": health_changed,
            "task_stats": tstats,
        }
        results.append(result)

    return results


def update_project_health(pid: str, new_health: str, old_health: str):
    """更新项目卡中的 health 字段。"""
    p_file = PROJECTS_DIR / f"{pid}.yaml"
    if not p_file.exists():
        return
    proj = yaml.safe_load(p_file.read_text(encoding="utf-8"))
    proj["health"] = new_health
    proj["updated_at"] = datetime.now().isoformat()
    p_file.write_text(
        yaml.dump(proj, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def format_table(results: list[dict]) -> str:
    """格式化表格输出。"""
    lines = []
    lines.append(f"{'Project':<12} {'Health':<10} {'Deadline':<14} {'Days':<6} {'Done/Total':<10} {'Rate':<7}")
    lines.append("-" * 65)

    health_icon = {"OnTrack": "🟢", "AtRisk": "🟡", "OffTrack": "🔴"}

    for r in results:
        icon = health_icon.get(r["computed_health"], "⚪")
        ts = r["task_stats"]
        lines.append(
            f"{r['pid']:<12} {icon} {r['computed_health']:<7} "
            f"{r['deadline']:<14} {r['days_left'] if r['days_left'] else '-':<6} "
            f"{ts['done']}/{ts['total']:<10} {r['completion_rate']:.0%}"
        )

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="SoloPM 项目健康评估")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--update", action="store_true", help="自动更新项目卡 health")
    args = parser.parse_args()

    results = assess_all_projects()

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print("\n📊 SoloPM 项目健康评估")
    print(format_table(results))

    # 列出健康变化的项目
    changed = [r for r in results if r["health_changed"]]
    if changed:
        print("\n⚠️  健康状态变化：")
        for r in changed:
            print(f"  {r['pid']}: {r['current_health']} → {r['computed_health']}")

        if args.update:
            for r in changed:
                update_project_health(r["pid"], r["computed_health"], r["current_health"])
                print(f"  ✅ {r['pid']} 已更新为 {r['computed_health']}")
        else:
            print("  使用 --update 自动更新项目卡。")

    # 详情
    print("\n📋 详情：")
    for r in results:
        ts = r["task_stats"]
        reasons = []
        if r["deadline_risk"] == "critical":
            if r["days_left"] < 0:
                reasons.append(f"已逾期 {abs(r['days_left'])} 天")
            else:
                reasons.append(f"距截止日仅 {r['days_left']} 天")
        elif r["deadline_risk"] == "warn":
            reasons.append(f"距截止日 {r['days_left']} 天")
        if r["completion_risk"] == "critical":
            reasons.append(f"完成率仅 {r['completion_rate']:.0%}")
        elif r["completion_risk"] == "warn":
            reasons.append(f"完成率偏低 {r['completion_rate']:.0%}")

        reason_str = "; ".join(reasons) if reasons else "一切正常"
        print(f"  {r['pid']}: {r['computed_health']} — {reason_str}")

    print(f"\n✅ 共评估 {len(results)} 个项目。")


if __name__ == "__main__":
    main()
