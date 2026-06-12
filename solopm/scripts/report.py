#!/usr/bin/env python3
"""
SoloPM 飞书文档周报/月报生成
- 调用 feishu_client 的 docx_create + docx_add_blocks
- 模板化生成文档内容（摘要 + 项目健康 + 任务统计）
CLI: python scripts/report.py {weekly|monthly} [--dry-run]
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent))
from task import get_stats, list_tasks
from feishu_client import docx_create, docx_add_blocks
from health import assess_all_projects

logger = logging.getLogger("report")

SOLOPM_DIR = Path(os.environ.get("SOLOPM_DIR", Path(__file__).resolve().parent.parent))
STATE_DIR = SOLOPM_DIR / "state"
REPORT_LOG_FILE = STATE_DIR / "report_log.jsonl"


def period_label(kind: str, d: date = None) -> str:
    """生成报告周期标签。"""
    d = d or date.today()
    if kind == "weekly":
        iso = d.isocalendar()
        return f"{iso[0]}年第{iso[1]}周"
    else:
        return f"{d.year}年{d.month}月"


def doc_title(kind: str, d: date = None) -> str:
    """生成文档标题。"""
    d = d or date.today()
    label = "周报" if kind == "weekly" else "月报"
    period = period_label(kind, d)
    return f"SoloPM {label} — {period}"


def collect_report_data(kind: str) -> dict:
    """收集报告所需数据。"""
    today = date.today()
    stats = get_stats()
    projects = assess_all_projects()

    # 本周/本月 完成的
    if kind == "weekly":
        monday = today - timedelta(days=today.weekday())
        start = monday
    else:
        start = today.replace(day=1)

    all_tasks = list_tasks()
    completed = [
        t for t in all_tasks
        if t.get("status") == "Done"
        and t.get("done_at", "")
        and t["done_at"] >= start.isoformat()
    ]

    # 本周聚焦
    this_week = [t for t in all_tasks if t.get("this_week")]
    blocked = [t for t in all_tasks if t.get("blocked")]

    return {
        "kind": kind,
        "period": period_label(kind, today),
        "generated_at": datetime.now().isoformat(),
        "stats": stats,
        "projects": projects,
        "completed": completed,
        "this_week": this_week,
        "blocked": blocked,
    }


def build_doc_blocks(data: dict) -> list[dict]:
    """
    构建飞书文档块。
    飞书 docx block 结构参考：
    - {"block_type": 3, "heading1": {"elements": [{"text_run": {"content": "..."}}]}}
    - {"block_type": 2, "text": {"elements": [{"text_run": {"content": "..."}}]}}
    - {"block_type": 4, "heading2": ...}
    """
    blocks = []

    def h1(text: str):
        return {
            "block_type": 3,
            "heading1": {"elements": [{"text_run": {"content": text}}]},
        }

    def h2(text: str):
        return {
            "block_type": 4,
            "heading2": {"elements": [{"text_run": {"content": text}}]},
        }

    def para(text: str):
        return {
            "block_type": 2,
            "text": {"elements": [{"text_run": {"content": text}}]},
        }

    def bullet(text: str):
        return {
            "block_type": 16,
            "bullet": {"elements": [{"text_run": {"content": text}}]},
        }

    # 标题
    blocks.append(h1(f"SoloPM {data['kind']}报告"))
    blocks.append(para(f"周期: {data['period']}"))
    blocks.append(para(f"生成时间: {data['generated_at']}"))
    blocks.append(para(""))

    # 摘要
    blocks.append(h2("📊 总览"))
    s = data["stats"]
    blocks.append(bullet(f"总任务: {s['total']}"))
    blocks.append(bullet(f"Doing: {s['doing']} / WIP上限: {s['wip_limit']}"))
    blocks.append(bullet(f"本周聚焦: {s['this_week']}"))
    blocks.append(bullet(f"今日到期: {s['due_today']}"))
    blocks.append(bullet(f"阻塞任务: {s['blocked']}"))
    blocks.append(para(""))

    # 项目健康
    blocks.append(h2("📁 项目健康"))
    for p in data["projects"]:
        icon = {"OnTrack": "🟢", "AtRisk": "🟡", "OffTrack": "🔴"}.get(
            p["computed_health"], "⚪"
        )
        ts = p["task_stats"]
        blocks.append(bullet(
            f"{icon} {p['name']}: {p['computed_health']} | "
            f"完成率 {p['completion_rate']:.0%} | {ts['done']}/{ts['total']} 任务"
        ))
    blocks.append(para(""))

    # 任务统计
    blocks.append(h2("📋 任务统计"))
    by_status = s.get("by_status", {})
    for status, count in sorted(by_status.items()):
        if count > 0:
            blocks.append(bullet(f"{status}: {count}"))
    blocks.append(para(""))

    # 本周完成
    if data["completed"]:
        blocks.append(h2("✅ 本周完成"))
        for t in data["completed"]:
            blocks.append(bullet(f"**{t['tid']}**: {t['title']}"))
        blocks.append(para(""))

    # 本周聚焦
    if data["this_week"]:
        blocks.append(h2("⭐ 本周聚焦"))
        for t in data["this_week"]:
            blocks.append(bullet(f"**{t['tid']}**: {t['title']} [{t.get('status', '?')}]"))
        blocks.append(para(""))

    # 阻塞
    if data["blocked"]:
        blocks.append(h2("🚫 阻塞任务"))
        for t in data["blocked"]:
            blocks.append(bullet(f"**{t['tid']}**: {t['title']}"))
        blocks.append(para(""))

    return blocks


def log_report(action: str, detail: dict):
    """记录报告生成事件。"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    entry = {"ts": datetime.now().isoformat(), "action": action, **detail}
    with open(REPORT_LOG_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="SoloPM 飞书文档报告生成")
    parser.add_argument("kind", choices=["weekly", "monthly"], help="报告类型")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不创建文档")
    parser.add_argument("--json", action="store_true", help="仅输出数据 JSON")
    args = parser.parse_args()

    data = collect_report_data(args.kind)
    blocks = build_doc_blocks(data)

    if args.json:
        print(json.dumps({
            "kind": data["kind"],
            "period": data["period"],
            "block_count": len(blocks),
            "stats": data["stats"],
            "project_count": len(data["projects"]),
        }, ensure_ascii=False, indent=2))
        return

    title = doc_title(args.kind)
    print(f"\n📄 生成 {title}")
    print(f"   段落数: {len(blocks)}")
    print(f"   项目数: {len(data['projects'])}")
    print(f"   本周完成: {len(data['completed'])}")
    print(f"   阻塞: {len(data['blocked'])}")

    if args.dry_run:
        print("\n[DRY RUN] 将创建以下文档内容：")
        for i, block in enumerate(blocks):
            block_type = block.get("block_type", "?")
            block_content = block.get("text") or block.get("heading1") or block.get("heading2") or block.get("bullet") or {}
            content_preview = block_content.get("elements", [{}])[0].get("text_run", {}).get("content", "...")
            print(f"  [{i}] type={block_type}: {content_preview[:80]}")
        print("\n[DRY RUN] 未实际调用飞书 API。")
        return

    # 实际调用飞书 API
    try:
        resp = docx_create(title)
        if resp.get("code") != 0:
            print(f"❌ 创建文档失败: {resp}")
            sys.exit(1)

        document_id = resp["data"]["document"]["document_id"]
        print(f"✅ 文档已创建: {document_id}")

        # 分批添加块（飞书限制每批最多 50 块）
        BATCH_SIZE = 50
        for i in range(0, len(blocks), BATCH_SIZE):
            batch = blocks[i:i + BATCH_SIZE]
            add_resp = docx_add_blocks(document_id, batch)
            if add_resp.get("code") != 0:
                print(f"⚠️  添加块失败 (offset={i}): {add_resp}")
            else:
                print(f"  已添加 {len(batch)} 个块 (offset={i})")

        doc_url = f"https://{os.environ.get('FEISHU_HOST', 'bytedance').replace('bytedance', 'feishu')}.feishu.cn/docx/{document_id}"
        print(f"\n🔗 文档链接: {doc_url}")

        log_report("created", {
            "kind": args.kind,
            "document_id": document_id,
            "title": title,
            "block_count": len(blocks),
        })

    except Exception as e:
        print(f"❌ 报告生成出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
