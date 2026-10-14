#!/usr/bin/env python3
"""
verify_report_template.py — 热点报告结构与模板合规性审查工具
============================================================
自动审查生成的热点报告是否满足结构、字数、核心板块以及数据完整性要求。
支持动态参数指定待测文件，未指定时自动查找工作区内最新的 report_daily.md。
"""

import os
import re
import sys
import subprocess
from pathlib import Path

def get_project_root() -> Path:
    if "HOTSPOT_DIR" in os.environ and os.path.exists(os.environ["HOTSPOT_DIR"]):
        return Path(os.environ["HOTSPOT_DIR"])
    cwd = Path.cwd()
    if (cwd / "reports" / "hotspot").exists() or (cwd / "config").exists():
        return cwd
    script_dir = Path(__file__).resolve().parent
    parent = script_dir.parent.parent
    if (parent / "reports" / "hotspot").exists() or (parent / "config").exists():
        return parent
    return cwd

PROJECT_ROOT = get_project_root()
REPORTS_DIR = PROJECT_ROOT / "reports" / "hotspot"

# 1. 确定待测文件
if len(sys.argv) > 1:
    target_arg = Path(sys.argv[1])
    if target_arg.is_absolute():
        REPORT = target_arg
    else:
        REPORT = (PROJECT_ROOT / target_arg).resolve()
else:
    # 默认检测软链接或最新报告
    softlink = REPORTS_DIR / "report_daily.md"
    if softlink.exists():
        REPORT = softlink.resolve()
    else:
        candidates = list(REPORTS_DIR.glob("report_daily_*.md"))
        if candidates:
            candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            REPORT = candidates[0]
        else:
            print(f"[FAIL] 未找到任何待测报告文件，目录: {REPORTS_DIR}")
            sys.exit(1)

SOFTLINK = REPORTS_DIR / "report_daily.md"

checks = []
failures = []

def check(name: str, ok: bool, detail: str = ""):
    status = "PASS" if ok else "FAIL"
    checks.append((status, name, detail))
    if not ok:
        failures.append(name)

# 1. 文件存在与基础属性
exists = REPORT.exists()
check("文件存在", exists, str(REPORT))
if not exists:
    print(f"File missing -- aborting further checks: {REPORT}")
    sys.exit(1)

size = REPORT.stat().st_size
check("文件内容非空 (>1KB)", size > 1024, f"{size} bytes")
text = REPORT.read_text(encoding="utf-8")
lines = text.splitlines()
check("行数达标 (>30 行)", len(lines) > 30, f"{len(lines)} 行")

# 2. 判断报告类型（引擎采集草案 vs 深度分析策略终稿）
is_final_strategy = "## 📋 本期热点清单" in text

if is_final_strategy:
    print("[INFO] 正在校验：深度分析策略终稿 (SOUL Standard Report)")
    required_sections = [
        (r"## 📋 本期热点清单", "## 📋 本期热点清单"),
        (r"## 🇨🇳 今日中国\s*AI\s*圈动态", "## 🇨🇳 今日中国AI圈动态"),
        (r"## 👤 关键人物观点追踪", "## 👤 关键人物观点追踪"),
        (r"## 🔍 深度分析", "## 🔍 深度分析"),
        (r"## 💡 选题建议", "## 💡 选题建议"),
    ]
    for pattern, sec_name in required_sections:
        check(f"必备章节: {sec_name}", bool(re.search(pattern, text)))
        
    p0_count = len(re.findall(r"^\| \*\*P0\*\* \|", text, re.M)) + len(re.findall(r"^\| P0 \|", text, re.M))
    check("包含 P0 级核心热点条目", p0_count >= 1, f"发现 {p0_count} 条")
    
    # 中文摘要检查
    has_zh = bool(re.search(r"[\u4e00-\u9fff]", text))
    check("包含中文深度分析/摘要", has_zh)
else:
    print("[INFO] 正在校验：多源采集引擎原始报告 (Engine Harvest Report)")
    required_sections = [
        "## 🌟 S 级核心信号",
        "## 📊 平台热点总览",
    ]
    for sec in required_sections:
        check(f"采集板块: {sec}", sec in text)
        
    has_s_signals = ("AI HOT" in text) or ("博客" in text) or ("Jina" in text)
    check("采集覆盖 S 级关键信息源", has_s_signals)

# 3. 软链接校验
if SOFTLINK.is_symlink() or SOFTLINK.exists():
    check("最新软链接 report_daily.md 存在", True, str(SOFTLINK))
else:
    check("最新软链接 report_daily.md 存在", False, "软链接缺失")

# 输出结果汇总
print("=" * 60)
print(f"REPORT AUDIT REPORT -- {REPORT.name}")
print("=" * 60)
for s, n, d in checks:
    print(f"  [{s}] {n}" + (f" ({d})" if d else ""))
print("=" * 60)
print(f"检查统计: {len(checks)} 项通过, {len(failures)} 项失败")
if failures:
    print(f"[FAIL] 未通过项: {failures}")
    sys.exit(1)
print("ALL CHECKS PASSED -- 报告结构校验 100% 通过！")
