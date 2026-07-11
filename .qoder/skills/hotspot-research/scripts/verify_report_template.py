"""
Ad-hoc verification template for hotspot-research daily/weekly report.

USAGE (copy & adapt — never run this file directly without editing the
REPORT and SOFTLINK paths):

    1. Edit REPORT and SOFTLINK if weekly run or different date.
    2. Run: python3 verify_report_template.py
    3. Report results as "ad-hoc verification only, not a full test suite".

WHAT IT CHECKS (structural correctness only — does NOT verify semantic accuracy):
- File exists and is non-trivial size (>10KB, >200 lines)
- All 8 required report sections present
- Hotspot table: 5 P0 + 7 P1 rows = 12 total (daily); adjust for weekly
- All hotspot Chinese summary columns contain CJK characters
- Theory neutrality: no philosopher names or unattributed theory jargon
- Weekly signals: 14+ unique W-IDs (daily); 5+ W-IDs in weekly
- 3 deep-dive candidates C-1..C-3
- Softlink is a real symlink pointing to a dated report file

WHAT IT DOES NOT CHECK (must be spot-checked manually by reading source
articles via Jina Reader / WebFetch):
- Whether 4-source cross-validation claims are correct
- Whether analysis reasoning actually fits the source content
- Whether weekly signal strength ratings match the supporting evidence
"""
import os
import re
import sys
import datetime
from pathlib import Path

# === EDIT THESE FOR THE SPECIFIC RUN ===
REPORT_DIR = Path.home() / "Documents" / "qoder_workspace" / "hotspot" / "reports" / "hotspot" / "hotspot-research_qoder"
_today = datetime.date.today().strftime("%Y-%m-%d")
REPORT = REPORT_DIR / f"report_daily_{_today}_AM.md"   # 带日期+AM/PM 的实际报告文件
SOFTLINK = REPORT_DIR / "report_daily.md"               # 固定软链接路径
# If the actual file uses PM or _v2 suffix, edit REPORT above accordingly.
# ========================================

failures = []
checks = []


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    checks.append((status, name, detail))
    if not ok:
        failures.append(name)


# 1. File exists & non-empty
exists = REPORT.exists()
check("File exists", exists, str(REPORT))
if not exists:
    print("File missing -- aborting further checks")
    for s, n, d in checks:
        print(f"  [{s}] {n}: {d}")
    sys.exit(1)

size = REPORT.stat().st_size
check("File non-trivial size (>10KB)", size > 10000, f"{size} bytes")
text = REPORT.read_text(encoding="utf-8")
lines = text.splitlines()
check("File has >200 lines", len(lines) > 200, f"{len(lines)} lines")

# 2. Required sections (daily template)
required = [
    "## 📋 本期热点清单",
    "## 🇨🇳 今日中国AI圈动态",
    "## 👤 关键人物观点追踪",
    "## 🔍 深度分析",
    "## 💡 选题建议",
    "## ⚙️ 执行路径报告",
    "## 📡 本周线索",
    "## 💡 素材深挖提示",
]
for sec in required:
    check(f"Section present: {sec}", sec in text)

# 3. Hotspot table
p0 = len(re.findall(r"^\| P0 \|", text, re.M))
p1 = len(re.findall(r"^\| P1 \|", text, re.M))
check("Has 5 P0 hotspots", p0 == 5, f"found {p0}")
check("Has 7 P1 hotspots", p1 == 7, f"found {p1}")
check("Total hotspots table = 12", p0 + p1 == 12, f"total={p0+p1}")

# 4. Chinese summaries
hotspot_rows = re.findall(r"^\| P[01] \| (.+?) \| (.+?) \|", text, re.M)
all_have_zh = True
missing_zh = []
for en, zh in hotspot_rows:
    if not re.search(r"[\u4e00-\u9fff]", zh):
        all_have_zh = False
        missing_zh.append(en[:60])
check("All hotspot Chinese summaries have CJK chars", all_have_zh,
      f"missing: {missing_zh}" if missing_zh else "ok")

# 5. Theory neutrality check (reverse — should NOT contain philosopher names)
#    SKILL.md requires: no philosopher attribution in hotspot collection phase
philosopher_names = ["拉康", "福柯", "阿伦特", "德里达", "海德格尔", "萨特", "齐泽克", "韩炳哲"]
found_philosophers = [name for name in philosopher_names if name in text]
check("Theory neutrality: no philosopher names", len(found_philosophers) == 0,
      f"found: {found_philosophers}" if found_philosophers else "ok")

#    Also check for unattributed theory framing ("这证明/这表明" + philosophy jargon)
theory_jargon = ["控制性理念", "通过仪式阶段", "认知重构点", "大他者", "象征界", "镜像阶段"]
found_jargon = [j for j in theory_jargon if j in text]
check("Theory neutrality: no unattributed theory jargon", len(found_jargon) == 0,
      f"found: {found_jargon}" if found_jargon else "ok")

# 6. Weekly signals
weekly = re.findall(r"\| \*\*(W-\d{2})\*\* \|", text)
unique_weekly = sorted(set(weekly))
check("Weekly signals >=14 unique W-IDs", len(unique_weekly) >= 14,
      f"found {len(unique_weekly)}: {unique_weekly[:5]}...")

# 7. Deep-dive candidates
deep_candidates = len(re.findall(r"^\| C-\d \|", text, re.M))
check("Has 3 deep-dive candidates C-1..C-3", deep_candidates == 3, f"found {deep_candidates}")

# 8. Softlink — must be a real symlink pointing to a dated report file
if SOFTLINK.exists() or SOFTLINK.is_symlink():
    is_sym = SOFTLINK.is_symlink()
    if is_sym:
        target = os.readlink(SOFTLINK)
        target_path = Path(target)
        target_name = target_path.name
        # 软链接必须指向带日期的报告文件
        has_date = bool(re.search(r"report_daily_\d{4}-\d{2}-\d{2}", target_name))
        check("Softlink is a real symlink", True, "")
        check("Softlink points to dated report", has_date,
              f"target={target_name}")
    else:
        check("Softlink is a real symlink (not a regular file)", False,
              f"{SOFTLINK.name} is a regular file, not a symlink")
else:
    check("Softlink exists", False, f"{SOFTLINK} not found")

# 9. Git commit (optional — may fail if not in a git repo)
import subprocess
try:
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    report_name = f"report_daily_{today_str}"
    result = subprocess.run(
        ["git", "log", "--oneline", "-5", "--", f"reports/hotspot/{report_name}"],
        cwd=str(REPORT_DIR.parent.parent) if REPORT_DIR.parent.parent.exists() else None,
        capture_output=True, text=True, timeout=10,
    )
    committed = "hotspot" in result.stdout.lower() or today_str in result.stdout
    check("Git commit exists for today's report", committed, result.stdout[:200] if result.stdout else "no output")
except FileNotFoundError:
    check("Git available", False, "git command not found")
except Exception as e:
    check("Git log queryable", False, str(e)[:100])

# Summary
print("=" * 60)
print(f"AD-HOC VERIFICATION -- {REPORT.name}")
print("=" * 60)
for s, n, d in checks:
    print(f"  [{s}] {n}")
    if d and s == "FAIL":
        print(f"         detail: {d}")
print("=" * 60)
print(f"Total: {len(checks)} checks, {len(failures)} failures")
if failures:
    print(f"FAILED: {failures}")
    sys.exit(1)
print("ALL CHECKS PASSED -- ad-hoc verification only (not a full test suite)")
