# Curl Fetch Commands

> **Purpose:** Exact curl commands for each source. Load when stepping through a specific source fetch and needing the command syntax.
> **Loaded when:** Agent reaches Step 〇·一 (MCP/Search) or Step 1 (Key Person blogs) or Step 4 (Deep-dive).

---

## Step 1 & 4: Jina Reader（主方案，默认使用）

**Jina Reader 将任意 URL 转为 LLM-ready Markdown**——无需逐源写正则，一行命令搞定。
免费可用，无需 API Key。单个请求 ~2-4s。

### Step 1：关键人物博客

```bash
# 8 人并行，每个独立 terminal：
# Sam Altman
curl -sL --max-time 15 "https://r.jina.ai/https://blog.samaltman.com/" -H "Accept: text/markdown"

# Karpathy github.io
curl -sL --max-time 15 "https://r.jina.ai/https://karpathy.github.io/" -H "Accept: text/markdown"

# Karpathy Bear Blog（当前活跃博客）
curl -sL --max-time 15 "https://r.jina.ai/https://karpathy.bearblog.dev/blog/" -H "Accept: text/markdown"

# Naval
curl -sL --max-time 15 "https://r.jina.ai/https://nav.al/" -H "Accept: text/markdown"

# Paul Graham
curl -sL --max-time 15 "https://r.jina.ai/http://paulgraham.com/articles.html" -H "Accept: text/markdown"

# Benedict Evans
curl -sL --max-time 15 "https://r.jina.ai/https://www.ben-evans.com/" -H "Accept: text/markdown"

# Ethan Mollick (RSS feed)
curl -sL --max-time 15 "https://r.jina.ai/https://www.oneusefulthing.org/feed" -H "Accept: text/markdown"

# Anthropic Research
curl -sL --max-time 15 "https://r.jina.ai/https://www.anthropic.com/research" -H "Accept: text/markdown"
```

### Step 4：深度补采原文

```bash
curl -sL --max-time 15 "https://r.jina.ai/{ARTICLE_URL}" -H "Accept: text/markdown"
```

输出即干净 Markdown 正文（标题、段落、链接全保留）。Agent 从中提取核心观点。

### Jina Reader 已知特征
- ✅ **博客类**（Sam Altman/Naval/PG/Karpathy Bear）：完美提取，格式保留好
- ⚠️ **导航重网站**（Forbes）：内容主体完整但掺杂导航/菜单文本，不影响可用性
- ⚠️ **JS 渲染页面**（Anthropic Research）：Jina 服务端有渲染能力，但复杂 SPA 可能缺部分内容
- ❌ **失败信号**：返回空 / HTTP 403 / 超时 → 降级到旧 curl 方案或 Scrapling

### 降级路径
```
Jina 失败
    ↓
1. 直 curl 原文（见下方 Step 1 / Step 4 旧命令）
    ↓ 仍失败
2. P0 热点？ → /skill scrapling → StealthyFetcher
   非 P0  → 标注 [BLOCKED] 跳过
```

---

## Step 〇·一: Brave Search MCP Keywords

```
搜索词 1: "AI agent" "solopreneur" 2026
搜索词 2: "AI 转型" "超级个体" 最新
搜索词 3: AI personal brand content creation
搜索词 4: "一人企业" AI automation
搜索词 5: AGI timeline latest 2026
```

Each query → top 5-8 results → merge dedup → tag `[MCP]` → three-gate review.

---

## Step 〇·一: Newsletter Curls

### import.ai — Jack Clark (Substack — JS-rendered)
⚠️ Main page is React/JS rendered; regex on raw HTML finds nothing.
**Workaround: Use RSS feed** (server-rendered XML):
```bash
curl -sL "https://importai.substack.com/feed" | python3 -c "
import sys, re
html = sys.stdin.read()
items = re.findall(r'<title><!\[CDATA\[([^\]]+)\]\]></title>', html)
urls = re.findall(r'<link>([^<]+)</link>', html)
for t, u in zip(items[1:6], urls[1:6]):  # skip feed title
    print(f'{t.strip()} → {u}')
"
```

### deeplearning.ai — The Batch
```bash
curl -sL "https://www.deeplearning.ai/the-batch/" | python3 -c "
import sys, re
html = sys.stdin.read()
items = re.findall(r'<h2[^>]*>([^<]+)</h2>', html)
for t in items[:5]:
    print(t.strip())
"
```

### Every (Dan Shipper)
```bash
curl -sL "https://every.to/" | python3 -c "
import sys, re
html = sys.stdin.read()
items = re.findall(r'<a[^>]*href=\"/([^\"]+)\"[^>]*>([^<]+)</a>', html)
for href, title in items[:8]:
    print(f'{title.strip()} → /{href}')
"
```

### One Useful Thing (Ethan Mollick — Substack, JS-rendered)
⚠️ Use `www.` prefix (bare domain `oneusefulthing.org` returns SSL_ERROR_SYSCALL).
⚠️ Main page is React/JS rendered; regex finds no links.
**Workaround A — Archive page JSON preload:**
```bash
curl -sL -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' "https://www.oneusefulthing.org/archive" | python3 -c "
import sys, json, re
html = sys.stdin.read()
m = re.search(r'window\.__remixContext\s*=\s*(\\{.+?\\});', html, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    posts = data.get('state', {}).get('loaderData', {})
    for k, v in posts.items():
        if isinstance(v, dict) and 'items' in v:
            for item in v['items'][:5]:
                print(f'{item.get(\"title\",\"?\")} -> https://www.oneusefulthing.org/p/{item.get(\"slug\",\"?\")}')
"
```
**Workaround B — RSS feed:**
```bash
curl -sL "https://www.oneusefulthing.org/feed" | python3 -c "
import sys, re
html = sys.stdin.read()
titles = re.findall(r'<title><!\[CDATA\[([^\]]+)\]\]></title>', html)
urls = re.findall(r'<link>([^<]+)</link>', html)
for t, u in zip(titles[1:6], urls[1:6]):
    print(f'{t.strip()} → {u}')
"
```

---

---
## Step 1: Key Person Blog Curls（旧方案——降级/参考用）

> ⚠️ 以下为旧 curl + 正则提取命令。**默认使用 Jina Reader**（见文档顶部）。仅在 Jina Reader 不可用时降级到这些命令。

### Sam Altman (Posthaven)
⚠️ Posthaven renders dates via JS in `<span class="posthaven-formatted-date" data-unix-time="...">`.
⚠️ **In practice, the data-unix-time workaround often yields epoch (1970-01-21)** — the JS that populates these attributes may not execute in curl's raw HTML capture. When all dates show epoch, fall back to: (1) list ordering (top = newest), (2) cross-reference post titles with Brave/Tavily search for external date mentions. Do not block on Sam Altman date verification.
**Best-effort date extraction from data-unix-time attribute:**
```bash
curl -sL "https://blog.samaltman.com/" | python3 -c "
import sys, re, datetime
html = sys.stdin.read()
# First: article titles
items = re.findall(r'<h2><a[^>]*href=\"([^\"]+)\"[^>]*>([^<]+)</a></h2>', html)
for href, title in items[:5]:
    print(f'{title.strip()} → {href}')
# Then: dates from JS-rendered spans
dates = re.findall(r'data-unix-time=\"(\d+)\"', html)
for ts in dates[:5]:
    dt = datetime.datetime.fromtimestamp(int(ts)/1000)
    print(f'Date: {dt.strftime(\"%Y-%m-%d\")}')
"
```

### Naval (WordPress)
```bash
curl -sL "https://nav.al/" | python3 -c "
import sys, json, re
html = sys.stdin.read()
# WordPress JSON-LD Schema
m = re.search(r'\"datePublished\":\"([^\"]+)\"', html)
if m: print(f'Latest post date: {m.group(1)}')
# Extract podcast topics
items = re.findall(r'<h2[^>]*>(?:<a[^>]*>)?([^<]+)', html)
for t in items[:5]:
    if len(t) > 10:
        print(t.strip())
"
```

### Karpathy (3 blogs — check all three!)
Karpathy maintains three blog surfaces with different content:
1. **karpathy.github.io** — Main deep technical blog; most recent post (Feb 2026): microgpt
2. **karpathy.bearblog.dev** (redirect from karpathy.ai) — Current blog, ~12 posts Sep 2024–Dec 2025
3. **karpathy.ai** — Landing page with links to both blogs

**Check GitHub blog first** (most recent content):
```bash
curl -sL "https://karpathy.github.io/" | python3 -c "
import sys, re
html = sys.stdin.read()
# GitHub Pages blog uses <h2><a> for post list
items = re.findall(r'<a[^>]*href=\"([^\"]+)\"[^>]*>([^<]+)</a>', html)
# Filter to find meaningful post links
for h, t in items:
    if len(t) > 15 and not 'github.io' in h:
        print(f'{t.strip()} → https://karpathy.github.io{h}')
"
```

**Check Bear Blog** (needs User-Agent):
```bash
curl -sL -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' "https://karpathy.bearblog.dev/blog/" | python3 -c "
import sys, re
html = sys.stdin.read()
items = re.findall(r'<a[^>]*href=\"([^\"]+)\"[^>]*>([^<]+)</a>', html)
for h, t in items:
    if len(t) > 15:
        print(f'{t.strip()} → {h}')
"
```

### Paul Graham
```bash
curl -sL "http://paulgraham.com/articles.html" | python3 -c "
import sys, re
html = sys.stdin.read()
# 列表顶部通常最新, 页面无明确日期
items = re.findall(r'<a[^>]*href=\"([^\"]+\.html)\"[^>]*>([^<]+)</a>', html)
for href, title in items[:8]:
    print(f'{title.strip()} → {href}')
"
```

### Benedict Evans
⚠️ Homepage only shows 3 most recent posts (lazy loading).
**Better: Use sitemap.xml** (serves all ~490 posts with dates):
```bash
curl -sL "https://www.ben-evans.com/sitemap.xml" | python3 -c "
import sys, re, xml.etree.ElementTree as ET
tree = ET.fromstring(sys.stdin.read())
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls = [(u.find('s:loc', ns).text, u.find('s:lastmod', ns).text) for u in tree.findall('s:url', ns)]
urls.sort(key=lambda x: x[1], reverse=True)
for url, date in urls[:5]:
    print(f'{date} -> {url}')
"
```

**Homepage fallback:**
```bash
curl -sL "https://www.ben-evans.com/" | python3 -c "
import sys, re
html = sys.stdin.read()
items = re.findall(r'<a[^>]*href=\"([^\"]+)\"[^>]*>([^<]+)</a>', html)
for href, title in items[:10]:
    if len(title) > 15:
        print(f'{title.strip()} → {href}')
"
```

---

---
## Step 4: Deep-dive Curls（旧方案——降级/参考用）

> ⚠️ 默认使用 Jina Reader（`r.jina.ai/{url}`）。仅在 Jina 不可用或 Reddit JSON API 场景下降级。

### Reddit JSON API (post metadata)
```bash
# Get score, timestamp, num_comments, selftext
curl -sL --max-time 15 "https://reddit.com/r/subreddit/comments/postid/title/.json"
# → JSON path: data.children[0].data
# Fields: title / score / created_utc / num_comments / selftext / url
# created_utc = Unix timestamp → Python datetime.fromtimestamp(utc, tz=timezone.utc)
# Note: may be rate-limited; try ?limit=1 or retry after delay
```

### Original Article Content (generic)
```bash
curl -sL --max-time 15 "ARTICLE_URL" | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '\\n', text)
lines = [l.strip() for l in text.split('\\n') if l.strip() and len(l.strip()) > 20]
for l in lines[:30]: print(l[:300])
"
```

### Date Extraction Tips (by source)
- **Sam Altman blog** (Posthaven): Date in JS variables; first link on list page = latest
- **Naval** (WordPress): JSON-LD `"datePublished":"2026-02-19T..."` in HTML
- **Paul Graham**: No date on page; list top = newest; cross-validate timeliness
- **Substack / Anthropic blog**: Header text has readable date (e.g. "Apr 28, 2026")
- **HN / Reddit API**: `time` / `created_utc` = Unix timestamp → UTC

---

## 🆕 Step 0.3: AI HOT 中文 AI 资讯全量拉取

> **完整 API 规格、数据结构、并行策略、降级路径见 `references/aihot_integration.md`。**
> 本文件仅保留最小化命令示例，避免与 aihot_integration.md 重复维护。

### 通用配置

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
# 所有 /api/public/* 请求必须带 -H "User-Agent: $UA"，否则 403
```

### 日报快速命令（24h，单次请求）

```bash
since=$(python3 -c "from datetime import datetime, timedelta, timezone; print((datetime.now(timezone.utc) - timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ'))")
curl -sH "User-Agent: $UA" "https://aihot.virxact.com/api/public/items?mode=selected&since=$since&take=100" --max-time 10 -o /tmp/aihot_daily.json
```

### 周报快速命令（7d，需分页）

> 完整分页逻辑和按类别拉取命令见 `references/aihot_integration.md` 第 2.3 节。

```bash
since=$(python3 -c "from datetime import datetime, timedelta, timezone; print((datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ'))")
curl -sH "User-Agent: $UA" "https://aihot.virxact.com/api/public/items?mode=selected&since=$since&take=100" --max-time 10 -o /tmp/aihot_weekly_base.json
# 检查 hasNext → 如有则按类别分页补齐（见 aihot_integration.md）
```
