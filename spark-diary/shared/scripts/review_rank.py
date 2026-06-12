#!/usr/bin/env python3
"""
spark-diary 半衰期回顾权重算法 (review_rank.py)
===============================================

读取所有 01_ideas/*.md 的 frontmatter，按文档 §7.2 算法计算优先级，
返回 Top3（或指定数量）候选灵感，附带随机扰动避免推送序列僵化。

算法 (Readwise 半衰期回忆概率模型简化版):
    recall_p(idea)   = 0.5 ^ (days_since_last_push / half_life_days)
                        未推送过的条目 days_since_last_push 按创建日起算
    priority(idea)   = (1 - recall_p) × weight × quality_mult
    quality_mult:  gem     = 1.5
                   normal  = 1.0
                   fragment = 0   (永不进入回顾池)

规则:
    - fragment 质量条目直接排除
    - S5_ARCHIVED 状态条目排除
    - 同分时随机排序（随机扰动）
    - weight 可由用户在表格端调整（默认 1.0）

用法:
    python review_rank.py [--count N] [--all]

选项:
    --count N   返回前 N 条（默认 3）
    --all       显示全部候选（含优先级详情），不筛选

输出:
    JSON 数组，每条包含: id, title, priority, recall_p, half_life_days,
    days_since_last_push, quality, weight

Python 3.9 兼容.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── 项目根目录推导 ─────────────────────────────────────────────

def _find_project_root() -> Path:
    """向上查找包含 diary.yaml 的目录作为项目根目录。"""
    script_dir = Path(__file__).resolve().parent
    for parent in [script_dir.parent.parent, script_dir.parent.parent.parent]:
        if (parent / "diary.yaml").exists():
            return parent
    return script_dir.parent.parent


PROJECT_ROOT = _find_project_root()
IDEAS_DIR = PROJECT_ROOT / "01_ideas"

# ── 读取 D1 配置（回顾参数） ───────────────────────────────────

def _load_review_config() -> Dict[str, Any]:
    """从 diary.yaml 读取 review 节配置，失败时返回默认值。"""
    diary_path = PROJECT_ROOT / "diary.yaml"
    if not diary_path.exists():
        return {
            "default_half_life_days": 7,
            "max_half_life_days": 90,
            "daily_count": 3,
            "bonus_count": 1,
        }
    try:
        import yaml
    except ImportError:
        print("错误: 需要安装 pyyaml 库。请执行: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    with open(diary_path, "r", encoding="utf-8") as f:
        diary = yaml.safe_load(f)
    review = diary.get("review", {}) if isinstance(diary, dict) else {}
    return {
        "default_half_life_days": review.get("default_half_life_days", 7),
        "max_half_life_days": review.get("max_half_life_days", 90),
        "daily_count": review.get("daily_count", 3),
        "bonus_count": review.get("bonus_count", 1),
    }


REVIEW_CONFIG = _load_review_config()

# ── Frontmatter 解析 ──────────────────────────────────────────

_FRONTMATTER_RE = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL
)


def _parse_frontmatter(file_path: Path) -> Optional[Dict[str, Any]]:
    """从 Markdown 文件提取 YAML frontmatter。"""
    try:
        import yaml
    except ImportError:
        print("错误: 需要安装 pyyaml 库。请执行: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    match = _FRONTMATTER_RE.match(content)
    if not match:
        return None

    try:
        data = yaml.safe_load(match.group(1))
    except Exception:
        return None

    if not isinstance(data, dict):
        return None
    return data


# ── 核心算法 ───────────────────────────────────────────────────

def _parse_date(date_str: Optional[str]) -> date:
    """解析日期字符串，支持 ISO 格式和纯日期格式。"""
    if not date_str:
        return date.today()
    if isinstance(date_str, datetime):
        return date_str.date()
    # 尝试多种格式
    for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
        try:
            # Python 3.9 没有 datetime.fromisoformat 的完整支持
            if fmt == "%Y-%m-%dT%H:%M:%S%z":
                # 手动处理时区
                dt_str = date_str
                if dt_str.endswith("Z"):
                    dt_str = dt_str[:-1] + "+00:00"
                dt = datetime.strptime(dt_str, fmt)
                return dt.date()
            dt = datetime.strptime(date_str, fmt)
            return dt.date()
        except (ValueError, TypeError):
            continue
    # 回退：只取日期部分
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return date.today()


def _days_between(d1: date, d2: date) -> int:
    """计算两个日期之间的天数差。"""
    return (d2 - d1).days


def compute_recall_probability(
    last_pushed: Optional[str],
    created_at: Optional[str],
    half_life_days: int,
) -> float:
    """计算回忆概率 recall_p。

    Args:
        last_pushed: 上次推送日期 (ISO 字符串或 None)。
        created_at: 创建日期 (用于从未推送过的条目)。
        half_life_days: 当前半衰期天数。

    Returns:
        回忆概率 (0.0 ~ 1.0)，未推送过返回 0.0（等价于“完全遗忘”）。
    """
    today = date.today()

    if last_pushed:
        last_date = _parse_date(last_pushed)
        days_since = _days_between(last_date, today)
    elif created_at:
        created_date = _parse_date(created_at)
        days_since = _days_between(created_date, today)
    else:
        # 没有任何时间信息，保守处理：按 0 天算
        days_since = 0

    if days_since < 0:
        days_since = 0

    if half_life_days <= 0:
        half_life_days = 1

    return math.pow(0.5, days_since / half_life_days)


def compute_priority(
    recall_p: float,
    weight: float,
    quality: str,
) -> float:
    """计算推送优先级。

    Args:
        recall_p: 回忆概率。
        weight: 用户可调的回顾权重（默认 1.0）。
        quality: 质量标记 'normal' / 'gem' / 'fragment'。

    Returns:
        优先级分数。fragment 返回 0.0。
    """
    quality_mult = {"gem": 1.5, "normal": 1.0, "fragment": 0.0}.get(quality, 1.0)
    return (1.0 - recall_p) * weight * quality_mult


def _quality_mult(quality: Optional[str]) -> float:
    """获取 quality 对应的乘数。"""
    mapping = {"gem": 1.5, "normal": 1.0, "fragment": 0.0}
    return mapping.get(quality or "normal", 1.0)


# ── 灵感扫描 ───────────────────────────────────────────────────

def scan_ideas() -> List[Dict[str, Any]]:
    """扫描 01_ideas/ 目录下所有 .md 文件，提取 frontmatter 并计算优先级。

    Returns:
        按 priority 降序排列的灵感列表（不含 fragment 和已归档）。
    """
    if not IDEAS_DIR.exists():
        print(f"警告: 灵感目录不存在: {IDEAS_DIR}", file=sys.stderr)
        return []

    results: List[Dict[str, Any]] = []
    default_half_life = REVIEW_CONFIG["default_half_life_days"]
    max_half_life = REVIEW_CONFIG["max_half_life_days"]

    for md_file in sorted(IDEAS_DIR.glob("*.md")):
        fm = _parse_frontmatter(md_file)
        if fm is None:
            continue

        idea_id = fm.get("id", md_file.stem)
        quality = fm.get("quality", "normal")
        status = fm.get("status", "S1_CAPTURED")

        # 排除已归档
        if status == "S5_ARCHIVED":
            continue

        # fragment 不进回顾池
        if quality == "fragment":
            continue

        review = fm.get("review", {}) or {}
        if not isinstance(review, dict):
            review = {}

        weight = review.get("weight", 1.0)
        half_life = review.get("half_life_days", default_half_life)
        last_pushed = review.get("last_pushed", None)
        push_count = review.get("push_count", 0)

        # 半衰期封顶
        if half_life > max_half_life:
            half_life = max_half_life

        recall_p = compute_recall_probability(
            last_pushed=last_pushed,
            created_at=fm.get("created_at"),
            half_life_days=half_life,
        )

        priority = compute_priority(
            recall_p=recall_p,
            weight=weight,
            quality=quality,
        )

        # 计算距上次推送天数（用于展示）
        today = date.today()
        if last_pushed:
            days_since = _days_between(_parse_date(last_pushed), today)
        elif fm.get("created_at"):
            days_since = _days_between(_parse_date(fm["created_at"]), today)
        else:
            days_since = 0

        results.append({
            "id": idea_id,
            "title": fm.get("title", ""),
            "priority": round(priority, 6),
            "recall_p": round(recall_p, 6),
            "half_life_days": half_life,
            "days_since_last_push": max(days_since, 0),
            "quality": quality,
            "weight": weight,
            "push_count": push_count,
            "status": status,
        })

    # 按 priority 降序排列，同分时加入随机扰动
    rng = random.Random()
    # 用稳定的种子确保每次结果有一定随机性但不完全随机
    results.sort(key=lambda x: (-x["priority"], rng.random()))
    return results


def select_top(results: List[Dict[str, Any]], count: int = 3) -> List[Dict[str, Any]]:
    """从已排名的结果中选择 Top N + 随机扰动。

    扰动策略: 在 Top(count*2) 范围内以 70% 概率保留原始排序、30% 概率随机交换。
    """
    if count <= 0 or not results:
        return []

    candidate_pool_size = min(count * 2, len(results))
    pool = results[:candidate_pool_size]

    if len(pool) <= count:
        return pool

    # 随机扰动：对非头部条目做小幅随机交换
    if len(pool) >= 3:
        rng = random.Random()
        for _ in range(1):  # 仅做一轮扰动
            i = rng.randint(1, len(pool) - 1)
            j = rng.randint(1, len(pool) - 1)
            if i != j and rng.random() < 0.3:
                pool[i], pool[j] = pool[j], pool[i]

    return pool[:count]


# ── CLI 入口 ────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="半衰期回顾权重算法 — 计算灵感推送优先级",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python review_rank.py              # 返回 Top 3
    python review_rank.py --count 5    # 返回 Top 5
    python review_rank.py --all        # 显示全部候选详情
        """,
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=None,
        help="返回前 N 条（默认 3，如果指定 --all 则忽略）",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="显示全部候选灵感（含优先级详情）",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        default=True,
        help="以 JSON 格式输出（默认）",
    )

    args = parser.parse_args()

    results = scan_ideas()

    if not results:
        print("[]")
        sys.exit(0)

    if args.all:
        output = results
    else:
        count = args.count if args.count is not None else REVIEW_CONFIG["daily_count"]
        output = select_top(results, count)

    # 只输出关键字段
    slim = []
    for item in output:
        slim.append({
            "id": item["id"],
            "title": item["title"],
            "priority": item["priority"],
            "recall_p": item["recall_p"],
            "half_life_days": item["half_life_days"],
            "days_since_last_push": item["days_since_last_push"],
            "quality": item["quality"],
            "weight": item["weight"],
        })

    print(json.dumps(slim, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
