---
name: hotspot-engine
description: |
  Automated content hotspot collection engine with fingerprint-based dedup,
  multi-platform web scraping, cron-based scheduling (daily + weekly),
  and structured markdown report generation.
  Used for AI × personal brand × solopreneur content research.
tags: [hotspot, research, scraping, dedup, cron, content-strategy]
---

# Hotspot Engine

Production-grade content hotspot collection system (860+ lines, single file) with fingerprint dedup, multi-source scraping, and cron scheduling. Designed for the AI × personal brand × solopreneur content niche.

## Architecture

```python
hotspot_engine.py
├── FingerprintStore         # Hash-based dedup + TTL expiry (7d daily, 30d weekly)
├── SourceCollector           # Multi-platform scraping
│   ├── collect_xxx() methods (14 sources: one per platform)
│   ├── _try_web()           # HTTP GET with UA spoofing, returns str|None
│   ├── _add_result()        # Checks fingerprints, marks repeats, appends to list
│   └── unknown_sources[]    # Collects failure diagnostics for report
├── generate_markdown_report()  # Structured .md with section headings
└── __main__                 # CLI: python3 hotspot_engine.py [daily|weekly]
```

## File Paths

| Path | Purpose |
|------|---------|
| `~/.hermes/scripts/hotspot_engine.py` | Main script |
| `~/.hermes/skills/hotspot-research/scripts/hotspot_engine.py` | Skill sync copy |
| `~/.hermes/cron/output/hotspot/report_daily.md` | Daily report |
| `~/.hermes/cron/output/hotspot/report_weekly.md` | Weekly report |
| `~/.hermes/cron/output/hotspot/fingerprints_daily.json` | Daily fingerpint store |
| `~/.hermes/cron/output/hotspot/fingerprints_weekly.json` | Weekly fingerprint store |
| `~/.hermes/cron/output/hotspot/prev_{mode}_fingerprints.json` | Last report fingerprints (pre-check) |

## Source Reliability Matrix (tested 2026-04-28)

| Source | Method | Reliability | Anti-crawl? | Typical yield | Key detail |
|--------|--------|-------------|-------------|---------------|------------|
| **Reddit** (5 s/subreddits) | JSON API (`hot.json`) | ✅ High | No | ~20 items | r/Entrepreneur, solopreneur, singularity, artificial, MachineLearning |
| **HackerNews** | Firebase JSON API | ✅ High | No | ~20 items | `topstories.json` → expand each; set `score >= 5` to avoid keyword filter |
| **Baidu Hotlist** | HTML regex parse | ✅ Medium | Weak | ~50 items | Uses **`"word"`** as JSON key, NOT `"title"` |
| **Bilibili** (rid=36 + rid=1) | JSON API | ✅ Medium | No | ~20 items | Remove keyword filter — collect all items, let report curate |
| **36kr newsflash** | JSON API | ⚠️ Unstable | Yes | ~10 items | Sometimes returns anti-crawl HTML; always wrap in try-except |
| **Sogou WeChat** | HTML regex parse | ⚠️ Low | Strong | ~15 items | Needs `import urllib.parse` inside method; anti-crawl heavy |
| **Overseas blogs** | HTML regex parse | ✅ Medium | No | ~5 items | Sam Altman, Paul Graham, Naval, Benedict Evans, Simon Willison |
| **Substack/newsletters** | HTML regex parse | ✅ Medium | No | ~5 items | First post only; 8s timeout each |
| **B站全站热门** (rid=1) | JSON API | ✅ Medium | No | ~10 items | Broad content, s/upplements tech focus |
| **Youtube trends** | HTTP | ❌ Fails | JS-rendered | — | Returns template code |
| **Weibo hot** | JSON API | ❌ Fails | Login required | — | Mark as unknown with suggestion |
| **Douyin / Zhihu** | HTTP | ❌ Fails | Strong | — | — |
| **tophub.today** | HTTP | ❌ Fails | JS-rendered (Vue) | — | Returns `'+ snapshot.time +'` template syntax |
| **即刻App** | HTTP | ❌ Fails | Strong | — | Try RSSHub as fallback |

## Dedup Strategy (Mixed Phase)

### Phase 1 (pre-collection)
Load prev report fingerprints into a `set`. Before each `_add_result()`, check if the fingerprint already exists in the prev set — if so, skip the HTTP request entirely. Saves ~30% HTTP calls on ~consecutive runs.

### Phase 2 (post-collection)
Full cross-check against `fingerprints_{mode}.json`:
- **Daily mode**: exclude items with `seen_count >= 3` (appeared in 2 prior reports)
- **Weekly mode**: exclude items with `seen_count >= 2`
- **Repeat marking**: items with `seen_count > 1` get `[🔄 第N次出现]` tag
- Daily and weekly fingerprint stores are **independent**

### Fingerprint generation
```python
norm_title = re.sub(r'\s+', ' ', title.strip().lower())[:80]
domain = urlparse(url).netloc.replace("www.", "") if url else ""
raw = f"{norm_title}|{source}|{domain}"
fingerprint = hashlib.md5(raw.encode("utf-8")).hexdigest()
```

### TTL
- Daily fingerprints: expire after 7 days
- Weekly fingerprints: expire after 30 days

## Collection Patterns

### Pattern A: JSON API (preferred)
Reddit, HackerNews, Bilibili, 36kr.
```python
html = self._try_web(api_url)
data = json.loads(html)
for item in data["data"]["list"]:
    self._add_result(title=item["title"], source="Name", ...)
```

### Pattern B: HTML regex parse
Baidu (`"word"` key), overseas blogs, newsletters, Sogou WeChat.
```python
html = self._try_web(url)
for match in re.finditer(r'"word":"([^"]+)"', html):
    word = match.group(1)
    self._add_result(...)
```

### Pattern C: Known failure → mark with actionable suggestion
```python
self.unknown_sources.append({
    "source": "Name",
    "method": "HTTP",
    "status": "JS-rendered / anti-crawl / login required",
    "suggestion": "Use alternative: ..."
})
```

## Cron Scheduling

### Tool limitation
The `cronjob` tool does NOT accept standard cron expressions (`0 8 * * *`) — it raises "Cron expressions require croniter package" even when croniter is installed in the Hermes venv. This is a tool-internal detection bug.

### Workaround
Use `every 1440m` for daily / `every 10080m` for weekly. These use `schedule.kind = "interval"` which does NOT require croniter.

### Aligning to exact time (e.g., 8am)
`once at <ISO>` + `repeat=forever` does NOT work — `compute_next_run()` returns `None` for once-type after first execution regardless of repeat setting.

Two workable methods:

**Method 1: Calculate minutes-to-target and schedule with `every Xm`**
```python
# Calculate exact minutes from now to next 8am
now = datetime.now().astimezone()
target = now.replace(hour=8, minute=0, second=0, microsecond=0)
if now >= target: target += timedelta(days=1)  # daily
# or for weekly: target += timedelta(days=(7 - now.weekday()) % 7 or 7)
minutes = int((target - now).total_seconds() / 60)
```

**Method 2: Edit `~/.hermes/cron/jobs.json` directly**
Set `next_run_at` to desired ISO timestamp, keep `schedule.kind = "interval"` and `schedule.minutes = 1440` or `10080`. The scheduler checks `next_run_at <= now`, so this anchors the first run to your exact target time.

### Recommended final schedule
```
Daily:  schedule.kind=interval, schedule.minutes=1440, next_run_at=tomorrowT08:00:00+08:00
Weekly: schedule.kind=interval, schedule.minutes=10080, next_run_at=next_mondayT08:00:00+08:00
```

## Common Pitfalls (Field Experience)

### 1. JS-rendered aggregators fail silently
**tophub.today** uses Vue SSR. HTTP GET returns `'+ snapshot.time +'` template code. Do not attempt regex parsing — mark as failed with actionable suggestion.

### 2. Baidu uses `"word"` not `"title"`
First attempt with `"title"` returned 0 results. Always inspect HTML structure before hardcoding keys.

### 3. re.finditer is not subscriptable
```python
# BROKEN — TypeError: 'callable_iterator' object is not subscriptable
for match in re.finditer(pattern, text)[:30]:
# FIXED
count = 0
for match in re.finditer(pattern, text):
    if count >= 30: break
    count += 1
```

### 4. One failing source blocks all others
Use collector list + try-except pattern:
```python
for collector in [self.collect_a, self.collect_b, ...]:
    try:
        collector()
    except Exception as e:
        print(f"⚠️ {collector.__name__} failed: {e}")
```

### 5. Report platform list MUST stay in sync
After adding a new source, update `platforms_order` in `generate_markdown_report()`. Matching logic is `platform in item["source"]` — substring match against the `source` field in collected data. If the name isn't in the order list, items are collected but never displayed.

Affected example: Baidu, HackerNews, Sogou WeChat, 即刻App all collecting data but invisible in reports because their source names weren't in the order list.

### 6. Method boundary corruption during patch operations
Inserting new methods before an existing one can orphan the `def method_name(self):` line. After patching `collect_sogou_weixin` and `collect_jike_hot` before `collect_reddit_hot`, the reddit method lost its `def` line — only the docstring `"""Reddit热门讨论"""` remained. Always verify method boundaries after multi-line patches.

### 7. 36kr API is unstable
The `/pp/api/newsflash` endpoint sometimes returns anti-crawl HTML instead of JSON. Always wrap in try-except and provide fallback HTML parse.

### 8. urllib.parse scope issue
If method uses `urllib.parse.quote()` but `urllib.parse` isn't imported at module level, add `import urllib.parse` inside the method body.

### 9. croniter detection is environment-sensitive
Hermes declares croniter as an extra dep (`cron = ["croniter>=6.0.0,<7"]`). Even when installed in venv, the cronjob tool's internal detection may fail. Pre-verify:
```bash
/path/to/venv/bin/python3 -c "from croniter import croniter; print('ok')"
```
If ok but tool still fails, use interval syntax as workaround.

### 10. Title-based keyword filters exclude too much
Initial Bilibili and 36kr collectors used keyword filters (`'AI' in title`). These filtered out most content. Better strategy: **collect everything above a minimum threshold (score>=5 for HN, all items for Bilibili) and let the report generator curate**. Human review of titles is more valuable than automated keyword gating.

### 11. Report suggestions must filter noise
The "选题建议" section picks top items by rating + repeat count. Add a noise filter to exclude items containing known garbage strings like '百度实时热点', '微博热搜榜', '今日热榜', '首页 晚报' — these are navigation elements that slip through regex parsing.

## Report Format

Generated by `generate_markdown_report(collected, mode, unknown_sources, dedup_stats)`:

1. **Header** — mode, timestamp, source count, item count, dedup stats
2. **Platform breakdown** — ordered by platforms_order list, each with items, repeat tags, URLs, tags
3. **Key person tracking** — Sam Altman, Paul Graham, Naval, etc. auto-detected by source name list
4. **Tag distribution** — simple ASCII bar chart of content categories
5. **Unknown sources appendix** — table with failure reason + concrete fix suggestion
6. **Content suggestions** — top 5 items (noise-filtered) with editorial angle suggestions

## Adding a New Source

1. Add `collect_xxx(self)` method to `SourceCollector`
2. Add to `run_daily_collection()` or `run_weekly_collection()` list
3. Add source name to `platforms_order` in `generate_markdown_report()`
4. Add to `person_items` filter if it's a key person/blog
5. Test: `python3 ~/.hermes/scripts/hotspot_engine.py daily`
6. Syncing: `cp ~/.hermes/scripts/hotspot_engine.py ~/.hermes/skills/hotspot-research/scripts/`
