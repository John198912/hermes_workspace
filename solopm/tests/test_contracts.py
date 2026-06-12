#!/usr/bin/env python3
"""
SoloPM 契约测试
- 任务卡 Schema 校验
- 状态机流转校验
- 文件契约校验

用法: SOLOPM_DIR=/tmp/solopm_test pytest tests/test_contracts.py -v
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import date

# 设置测试专用目录（必须在 import 模块之前）
TEST_DIR = Path(os.environ.get("SOLOPM_DIR", tempfile.mkdtemp(prefix="solopm_test_")))
TEST_DIR.mkdir(parents=True, exist_ok=True)
os.environ["SOLOPM_DIR"] = str(TEST_DIR)

# 将 scripts/ 加入路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import yaml
import pytest

from task import (
    create_task,
    read_task,
    set_status,
    list_tasks,
    get_stats,
    generate_tid,
    VALID_STATUSES,
    VALID_PRIORITIES,
    WIP_LIMIT,
)


@pytest.fixture(autouse=True)
def clean_state():
    """每个测试前清理 state 目录"""
    import shutil
    state_dir = TEST_DIR / "state"
    if state_dir.exists():
        shutil.rmtree(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "tasks").mkdir(exist_ok=True)
    (state_dir / "projects").mkdir(exist_ok=True)
    yield
    if state_dir.exists():
        shutil.rmtree(state_dir)


class TestTaskCard:
    """C1 任务卡契约测试"""

    def test_create_task_minimal(self):
        """最小任务卡创建"""
        tid = create_task(
            title="测试任务",
            project="P-test",
            status="Todo",
        )
        assert tid.startswith("T-")
        assert (TEST_DIR / "state" / "tasks" / f"{tid}.yaml").exists()

        t = read_task(tid)
        assert t["title"] == "测试任务"
        assert t["status"] == "Todo"
        assert t["priority"] == "P2"
        assert t["log"][0]["event"] == "created"

    def test_create_task_all_fields(self):
        """完整任务卡创建"""
        tid = create_task(
            title="完整测试",
            project="P-quant",
            status="Doing",
            priority="P1",
            due_date="2026-06-20",
            effort="L",
            context="@quick",
            exec_mode="hybrid",
            desc="这是一个测试任务描述",
            acceptance=["测试通过", "代码审查"],
            this_week=True,
        )
        t = read_task(tid)
        assert t["priority"] == "P1"
        assert t["effort"] == "L"
        assert t["due_date"] == "2026-06-20"
        assert t["context"] == "@quick"
        assert t["exec_mode"] == "hybrid"
        assert t["this_week"] is True
        assert len(t["acceptance"]) == 2

    def test_create_duplicate_tid_fails(self):
        """重复 TID 拒绝创建"""
        create_task("任务A", tid="T-FIXED-001")
        with pytest.raises(FileExistsError):
            create_task("任务B", tid="T-FIXED-001")

    def test_invalid_status_rejected(self):
        """无效状态拒绝"""
        with pytest.raises(ValueError, match="无效状态"):
            create_task("测试", status="INVALID")

    def test_invalid_priority_rejected(self):
        """无效优先级拒绝"""
        with pytest.raises(ValueError, match="无效优先级"):
            create_task("测试", priority="P5")


class TestStateMachine:
    """状态机流转测试"""

    @pytest.fixture
    def task(self):
        tid = create_task("状态机测试", project="P-test")
        return tid

    def test_normal_flow(self, task):
        """正常流转: Todo → Doing → Review → Done"""
        assert set_status(task, "Doing")
        assert read_task(task)["status"] == "Doing"
        assert set_status(task, "Review")
        assert set_status(task, "Done")
        t = read_task(task)
        assert t["status"] == "Done"
        assert "done_at" in t

    def test_cancel_and_reopen(self, task):
        """取消后重新打开"""
        set_status(task, "Cancelled")
        assert read_task(task)["status"] == "Cancelled"
        set_status(task, "Todo")
        assert read_task(task)["status"] == "Todo"

    def test_done_sets_done_at(self, task):
        """Done 状态自动设置完成日期"""
        set_status(task, "Doing")
        set_status(task, "Review")
        set_status(task, "Done")
        t = read_task(task)
        assert t["done_at"] == date.today().isoformat()


class TestStats:
    """统计测试"""

    def test_stats_empty(self):
        stats = get_stats()
        assert stats["total"] == 0
        assert stats["doing"] == 0

    def test_stats_with_tasks(self):
        create_task("Task 1", project="P-test", status="Todo")
        create_task("Task 2", project="P-test", status="Doing")
        create_task("Task 3", project="P-test", status="Done")
        stats = get_stats()
        assert stats["total"] == 3
        assert stats["doing"] == 1
        assert stats["by_status"]["Done"] == 1

    def test_wip_warning(self):
        for i in range(WIP_LIMIT + 2):
            create_task(f"Task {i}", project="P-test", status="Doing")
        stats = get_stats()
        assert stats["wip_warning"] is True
        assert stats["doing"] > WIP_LIMIT


class TestTaskList:
    """任务列表过滤测试"""

    def test_filter_by_status(self):
        create_task("A", status="Todo")
        create_task("B", status="Doing")
        create_task("C", status="Done")
        assert len(list_tasks(status="Doing")) == 1
        assert len(list_tasks(status="Todo")) == 1

    def test_filter_by_project(self):
        create_task("A", project="P-a")
        create_task("B", project="P-b")
        assert len(list_tasks(project="P-a")) == 1

    def test_filter_due_today(self):
        today = date.today().isoformat()
        create_task("Today", due_date=today)
        create_task("Future", due_date="2099-01-01")
        assert len(list_tasks(due_today=True)) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
