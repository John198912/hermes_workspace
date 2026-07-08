"""Ad-hoc verification template for hotspot-research daily/weekly report.

Background: After a cron run that produces a report_daily_YYYY-MM-DD.md or
report_weekly_YYYY-MM-DD.md, the system may ask for a verification script.
The path requested is usually /var/folders/.../T/ (macOS tempdir), but
Hermes write_file blocks that as a sensitive system path.

USAGE (copy & adapt — never run this file directly without editing the
REPORT and SOFTLINK paths):

    1. Copy to /tmp/hermes-verify-YYYY-MM-DD.py (the `hermes-verify-` prefix
       satisfies the naming request; the /tmp/ path is allowed by write_file).
    2. Edit REPORT and SOFTLINK if weekly run or different date.
    3. Run: python3 /tmp/hermes-verify-YYYY-MM-DD.py 2>&1 | tee /tmp/hermes-verify-YYYY-MM-DD.out.log
    4. Report results in the final reply as "ad-hoc verification only, not a full test suite".
    5. Clean up: rm -f /tmp/hermes-verify-YYYY-MM-DD.py /tmp/hermes-verify-YYYY-MM-DD.out.log

WHAT IT CHECKS (structural correctness only — does NOT verify semantic accuracy):
- File exists and is non-trivial size (>10KB, >200 lines)
- All 8 required SOUL template sections present
- Hotspot table: 5 P0 + 7 P1 rows = 12 total (daily); adjust for weekly
- All hotspot Chinese summary columns contain CJK characters
- SOUL framework keywords used 8+ times each in deep analysis
- Weekly signals: 14+ unique W-IDs (daily); 5+ W-IDs in weekly
- 3 deep-dive candidates C-1..C-3
- Softlink points to today's report
- Git commit exists for today's report

WHAT IT DOES NOT CHECK (must be spot-checked manually by reading source
articles via Jina Reader):
- Whether 4-source cross-validation claims are correct
- Whether SOUL analysis reasoning actually fits the source content
- Whether weekly signal strength ratings match the supporting evidence
"""
import os
import re
import subprocess
import sys
from pathlib import Path

# === EDIT THESE FOR THE SPECIFIC RUN ===
REPORT = Path("/Users/lizhenjiang/hermes_workspace/reports/hotspot/report_daily_2026-06-26.md")
SOFTLINK = Path("/Users/lizhenjiang/hermes_workspace/reports/hotspot/report_daily.md")
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

# 5. SOUL framework mentions
for kw in ["控制性理念", "通过仪式阶段", "认知重构点"]:
    cnt = text.count(kw)
    check(f"Deep analysis uses '{kw}' (>=8 times)", cnt >= 8, f"{cnt} occurrences")

# 6. Weekly signals
weekly = re.findall(r"\| \*\*(W-\d{2})\*\* \|", text)
unique_weekly = sorted(set(weekly))
check("Weekly signals >=14 unique W-IDs", len(unique_weekly) >= 14,
      f"found {len(unique_weekly)}: {unique_weekly[:5]}...")

# 7. Deep-dive candidates
deep_candidates = len(re.findall(r"^\| C-\d \|", text, re.M))
check("Has 3 deep-dive candidates C-1..C-3", deep_candidates == 3, f"found {deep_candidates}")

# 8. Softlink
if SOFTLINK.is_symlink() or SOFTLINK.exists():
    try:
        target = os.readlink(SOFTLINK)
        check("Softlink report_daily.md -> today's file",
              "2026-06-26" in target, f"target={target}")
    except OSError:
        check("Softlink readable", False, "could not readlink")
else:
    check("Softlink exists", False, "report_daily.md not found")

# 9. Git commit
try:
    result = subprocess.run(
        ["git", "log", "--oneline", "-5", "--", "reports/hotspot/report_daily_2026-06-26.md"],
        cwd="/Users/lizhenjiang/hermes_workspace",
        capture_output=True, text=True, timeout=10,
    )
    committed = "hotspot report 2026-06-26" in result.stdout
    check("Git commit exists for today's report", committed, result.stdout[:200])
except Exception as e:
    check("Git log queryable", False, str(e))

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
