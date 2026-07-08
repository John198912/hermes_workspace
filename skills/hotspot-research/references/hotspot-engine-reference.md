# Hotspot Engine — Python Script Reference

> **Purpose:** Detailed reference for `hotspot_engine.py` — source reliability, dedup strategy, collection patterns, and known pitfalls.
> **Load when:** Debugging collection issues, adding new sources, or understanding script behavior.

## File Paths

| Path | Purpose |
|------|---------|
| `~/.hermes/skills/hotspot-research/scripts/hotspot_engine.py` | Main script |
| `~/.hermes/cron/output/hotspot/report_daily.md` | Daily report |
| `~/.hermes/cron/output/hotspot/report_weekly.md` | Weekly report |
| `~/.hermes/cron/output/hotspot/fingerprints_daily.json` | Daily fingerprint store |
| `~/.hermes/cron/output/hotspot/fingerprints_weekly.json` | Weekly fingerprint store |

## Source Reliability Matrix (tested 2026-04-28)

| Source | Method | Reliability | Anti-crawl? | Typical yield | Key detail |
|--------|--------|-------------|-------------|---------------|------------|
| **Reddit** (5 subreddits) | JSON API (`hot.json`) | ✅ High | No | ~20 items | r/Entrepreneur, solopreneur, singularity, artificial, MachineLearning |
| **HackerNews** | Firebase JSON API | ✅ High | No | ~20 items | `topstories.json` → expand each; set `score >= 5` |
| **Baidu Hotlist** | HTML regex parse | ✅ Medium | Weak | ~50 items | Uses `"word"` as JSON key, NOT `"title"` |
| **Bilibili** (rid=36 + rid=1) | JSON API | ✅ Medium | No | ~20 items | Remove keyword filter — collect all, let Agent curate |
| **36kr newsflash** | JSON API | ⚠️ Unstable | Yes | ~10 items | Sometimes returns anti-crawl HTML; wrap in try-except |
| **Sogou WeChat** | HTML regex parse | ⚠️ Low | Strong | ~15 items | Needs `import urllib.parse` inside method |
| **Overseas blogs** | HTML regex parse | ✅ Medium | No | ~5 items | Sam Altman, Paul Graham, Naval, Benedict Evans, Simon Willison |
| **Substack/newsletters** | HTML regex parse | ✅ Medium | No | ~5 items | First post only; 8s timeout each |
| **YouTube trends** | HTTP | ❌ Fails | JS-rendered | — | Returns template code |
| **Weibo hot** | JSON API | ❌ Fails | Login required | — | Mark as unknown with suggestion |
| **Douyin / Zhihu** | HTTP | ❌ Fails | Strong | — | — |
| **tophub.today** | HTTP | ❌ Fails | JS-rendered (Vue) | — | Returns template syntax |
| **即刻App** | HTTP | ❌ Fails | Strong | — | Try RSSHub as fallback |

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

## Dedup Strategy

### Phase 1 (pre-collection)
Load prev report fingerprints into a `set`. Before each `_add_result()`, check if fingerprint exists — if so, skip HTTP request. Saves ~30% HTTP calls.

### Phase 2 (post-collection)
Full cross-check against `fingerprints_{mode}.json`:
- **Daily**: exclude items with `seen_count >= 3`
- **Weekly**: exclude items with `seen_count >= 2`

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

### Pattern B: HTML regex parse
Baidu (`"word"` key), overseas blogs, newsletters, Sogou WeChat.

### Pattern C: Known failure → mark with actionable suggestion
```python
self.unknown_sources.append({
    "source": "Name", "method": "HTTP",
    "status": "JS-rendered / anti-crawl / login required",
    "suggestion": "Use alternative: ..."
})
```

## Known Pitfalls

1. **JS-rendered aggregators fail silently** — tophub.today returns Vue template code
2. **Baidu uses `"word"` not `"title"`** — first attempt returned 0 results
3. **`re.finditer` is not subscriptable** — use manual counter loop
4. **One failing source blocks all others** — use try-except per collector
5. **Report platform list MUST stay in sync** — new sources invisible if not in `platforms_order`
6. **Method boundary corruption during patches** — verify `def` lines after multi-line patches
7. **36kr API is unstable** — wrap in try-except with HTML fallback
8. **`urllib.parse` scope** — add `import urllib.parse` inside method if needed
9. **Title-based keyword filters exclude too much** — collect all, let Agent curate
10. **Report suggestions must filter noise** — exclude navigation strings

## Adding a New Source

1. Add `collect_xxx(self)` method to `SourceCollector`
2. Add to `run_daily_collection()` or `run_weekly_collection()` list
3. Add source name to `platforms_order` in `generate_markdown_report()`
4. Add to `person_items` filter if it's a key person/blog
5. Test: `python3 ~/.hermes/skills/hotspot-research/scripts/hotspot_engine.py daily`
