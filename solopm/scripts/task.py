#!/usr/bin/env python3
"""
SoloPM 任务卡管理（C1 契约）
- 任务卡 CRUD（YAML 文件为唯一事实源）
- 状态机校验
- 事件日志写入（C6）
"""

import os
import sys
import json
import uuid
import argparse
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Optional

import yaml

logger = logging.getLogger("task")

SOLOPM_DIR = Path(os.environ.get("SOLOPM_DIR", Path(__file__).resolve().parent.parent))
STATE_DIR = SOLOPM_DIR / "state"
TASKS_DIR = STATE_DIR / "tasks"
EVENT_LOG = STATE_DIR / "event_log.jsonl"

# 状态机定义
VALID_STATUSES = ["Inbox", "Todo", "Doing", "Review", "Done", "Someday", "Cancelled"]
VALID_PRIORITIES = ["P0", "P1", "P2", "P3"]
VALID_EFFORTS = ["XS", "S", "M", "L", "XL"]
VALID_CONTEXTS = ["@deep", "@quick", "@waiting", "@errand"]
VALID_EXEC_MODES = ["human", "agent", "hybrid"]

# 合法状态流转
ALLOWED_TRANSITIONS = {
    "Inbox": ["Todo", "Someday", "Cancelled"],
    "Todo": ["Doing", "Cancelled", "Someday"],
    "Doing": ["Review", "Cancelled", "Todo"],
    "Review": ["Done", "Doing", "Cancelled"],
    "Done": ["Todo"],  # 重新打开
    "Someday": ["Todo", "Cancelled"],
    "Cancelled": ["Todo", "Someday"],
}

# Doing WIP 限制
WIP_LIMIT = 3


def generate_tid(prefix: str = "T") -> str:
    """生成任务 ID: T-20260613-001"""
    today = date.today().strftime("%Y%m%d")
    # 查找今天已有的最大序号
    max_seq = 0
    if TASKS_DIR.exists():
        for f in TASKS_DIR.glob(f"{prefix}-{today}-*.yaml"):
            try:
                seq = int(f.stem.split("-")[-1])
                max_seq = max(max_seq, seq)
            except (ValueError, IndexError):
                pass
    return f"{prefix}-{today}-{max_seq + 1:03d}"


# ═══════════════════════════════════════════════════════════
#  事件日志
# ═══════════════════════════════════════════════════════════

def log_event(kind: str, ref: str, detail: str = "", by: str = "cli"):
    """追加事件到 C6 event_log.jsonl"""
    EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "kind": kind,
        "ref": ref,
        "detail": detail,
        "by": by,
    }
    with open(EVENT_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ═══════════════════════════════════════════════════════════
#  任务卡读写
# ═══════════════════════════════════════════════════════════

def task_path(tid: str) -> Path:
    return TASKS_DIR / f"{tid}.yaml"


def task_exists(tid: str) -> bool:
    return task_path(tid).exists()


def read_task(tid: str) -> dict:
    """读取任务卡。"""
    p = task_path(tid)
    if not p.exists():
        raise FileNotFoundError(f"任务 {tid} 不存在: {p}")
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def write_task(tid: str, data: dict):
    """写入任务卡。"""
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    p = task_path(tid)
    p.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False), encoding="utf-8")


def create_task(
    title: str,
    project: str = "",
    status: str = "Inbox",
    priority: str = "P2",
    due_date: str = "",
    effort: str = "M",
    context: str = "@deep",
    exec_mode: str = "human",
    desc: str = "",
    acceptance: list[str] = None,
    this_week: bool = False,
    tid: str = None,
) -> str:
    """创建任务卡，返回 tid。"""
    if tid is None:
        tid = generate_tid()

    # 校验
    if status not in VALID_STATUSES:
        raise ValueError(f"无效状态: {status}，合法值: {VALID_STATUSES}")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"无效优先级: {priority}")
    if effort not in VALID_EFFORTS:
        raise ValueError(f"无效工作量: {effort}")
    if context not in VALID_CONTEXTS:
        raise ValueError(f"无效上下文: {context}")
    if exec_mode not in VALID_EXEC_MODES:
        raise ValueError(f"无效执行模式: {exec_mode}")

    if task_exists(tid):
        raise FileExistsError(f"任务 {tid} 已存在")

    task = {
        "tid": tid,
        "title": title,
        "project": project,
        "status": status,
        "priority": priority,
        "blocked": False,
        "due_date": due_date,
        "effort": effort,
        "context": context,
        "exec_mode": exec_mode,
        "this_week": this_week,
        "desc": desc,
        "acceptance": acceptance or [],
        "outputs": [],
        "log": [
            {"ts": datetime.now().isoformat(), "event": "created", "by": "cli"}
        ],
    }
    write_task(tid, task)
    log_event("created", tid, f"status={status} project={project}")
    return tid


def set_status(tid: str, new_status: str, by: str = "cli") -> bool:
    """变更任务状态（带状态机校验）。"""
    if new_status not in VALID_STATUSES:
        raise ValueError(f"无效状态: {new_status}")

    task = read_task(tid)
    old_status = task.get("status", "Inbox")

    if old_status == new_status:
        logger.info(f"状态未变化: {tid} {old_status}")
        return False

    # WIP 限制：进 Doing 时检查
    if new_status == "Doing":
        doing_count = count_doing()
        if doing_count >= WIP_LIMIT:
            logger.warning(f"WIP 超限! 当前 Doing={doing_count}, 上限={WIP_LIMIT}")

    # 状态机流转校验（允许任意流转，但记录非标准流转）
    if new_status not in ALLOWED_TRANSITIONS.get(old_status, []):
        logger.warning(f"非标准流转: {tid}: {old_status} → {new_status}")

    # 进 Done 时检查 outputs
    if new_status == "Done" and not task.get("outputs"):
        logger.warning(f"任务 {tid} 进 Done 但 outputs 为空")

    task["status"] = new_status
    task["log"].append({
        "ts": datetime.now().isoformat(),
        "event": f"status: {old_status}→{new_status}",
        "by": by,
    })

    if new_status == "Done":
        task["done_at"] = date.today().isoformat()

    write_task(tid, task)
    log_event("status_change", tid, f"{old_status}→{new_status}", by)
    return True


def list_tasks(
    status: str = None,
    project: str = None,
    this_week: bool = None,
    blocked: bool = None,
    due_before: str = None,
    due_today: bool = False,
) -> list[dict]:
    """列出任务（支持过滤）。"""
    tasks = []
    if not TASKS_DIR.exists():
        return tasks

    today = date.today().isoformat()
    for f in sorted(TASKS_DIR.glob("*.yaml")):
        try:
            t = yaml.safe_load(f.read_text(encoding="utf-8"))
            if not t or not isinstance(t, dict):
                continue
            # 过滤
            if status and t.get("status") != status:
                continue
            if project and t.get("project") != project:
                continue
            if this_week is True and not t.get("this_week"):
                continue
            if blocked is True and not t.get("blocked"):
                continue
            if due_before and t.get("due_date", "") > due_before:
                continue
            if due_today and t.get("due_date") != today:
                continue
            tasks.append(t)
        except Exception as e:
            logger.warning(f"跳过损坏的任务卡 {f}: {e}")

    return tasks


def count_doing() -> int:
    return len(list_tasks(status="Doing"))


def count_by_status(status: str) -> int:
    return len(list_tasks(status=status))


def get_stats() -> dict:
    """任务统计摘要。"""
    stats = {s: 0 for s in VALID_STATUSES}
    blocked = 0
    due_today = 0
    this_week = 0
    today = date.today().isoformat()

    for t in list_tasks():
        stats[t.get("status", "Inbox")] += 1
        if t.get("blocked"):
            blocked += 1
        if t.get("due_date") == today:
            due_today += 1
        if t.get("this_week"):
            this_week += 1

    return {
        "by_status": stats,
        "blocked": blocked,
        "due_today": due_today,
        "this_week": this_week,
        "doing": stats.get("Doing", 0),
        "total": sum(stats.values()),
        "wip_limit": WIP_LIMIT,
        "wip_warning": stats.get("Doing", 0) > WIP_LIMIT,
    }


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="SoloPM 任务管理")
    sub = parser.add_subparsers(dest="cmd")

    # create
    p_create = sub.add_parser("create", help="创建任务")
    p_create.add_argument("title")
    p_create.add_argument("--project", "-p", default="")
    p_create.add_argument("--status", "-s", default="Todo")
    p_create.add_argument("--priority", default="P2")
    p_create.add_argument("--due", default="", help="YYYY-MM-DD")
    p_create.add_argument("--effort", default="M")
    p_create.add_argument("--context", default="@deep")
    p_create.add_argument("--exec-mode", default="human")
    p_create.add_argument("--desc", default="")
    p_create.add_argument("--this-week", action="store_true")

    # set-status
    p_ss = sub.add_parser("set-status", help="修改状态")
    p_ss.add_argument("tid")
    p_ss.add_argument("status")

    # list
    p_list = sub.add_parser("list", help="列出任务")
    p_list.add_argument("--status", "-s", default=None)
    p_list.add_argument("--project", "-p", default=None)
    p_list.add_argument("--this-week", action="store_true")
    p_list.add_argument("--due-today", action="store_true")
    p_list.add_argument("--blocked", action="store_true")
    p_list.add_argument("--format", default="table", choices=["table", "json"])

    # show
    p_show = sub.add_parser("show", help="查看任务")
    p_show.add_argument("tid")

    # stats
    sub.add_parser("stats", help="统计")

    args = parser.parse_args()

    if args.cmd == "create":
        tid = create_task(
            title=args.title,
            project=args.project,
            status=args.status,
            priority=args.priority,
            due_date=args.due,
            effort=args.effort,
            context=args.context,
            exec_mode=args.exec_mode,
            desc=args.desc,
            this_week=args.this_week,
        )
        print(f"✅ 任务创建: {tid}")

    elif args.cmd == "set-status":
        set_status(args.tid, args.status)
        print(f"✅ {args.tid} → {args.status}")

    elif args.cmd == "list":
        tasks = list_tasks(
            status=args.status,
            project=args.project,
            this_week=args.this_week,
            due_today=args.due_today,
            blocked=args.blocked,
        )
        if args.format == "json":
            print(json.dumps(tasks, ensure_ascii=False, indent=2))
        else:
            if not tasks:
                print("暂无任务")
            for t in tasks:
                icon = {"Done": "✅", "Doing": "🔄", "Todo": "⬜", "Review": "👀", "Cancelled": "❌", "Inbox": "📥", "Someday": "⏳"}.get(t["status"], "❓")
                due = f" | 📅{t.get('due_date','')}" if t.get("due_date") else ""
                blocked = " | 🚫阻塞" if t.get("blocked") else ""
                w = " | ⭐本周" if t.get("this_week") else ""
                print(f"{icon} [{t['priority']}] {t['tid']}: {t['title']}{due}{blocked}{w}")

    elif args.cmd == "show":
        t = read_task(args.tid)
        print(yaml.dump(t, allow_unicode=True, default_flow_style=False, sort_keys=False))

    elif args.cmd == "stats":
        stats = get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
