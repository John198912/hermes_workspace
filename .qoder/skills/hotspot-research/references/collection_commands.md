# 采集命令参考 (Collection Commands)

> **用途**：各信息源的采集命令。Agent 执行采集步骤时按需加载。
> **工具链**：Bash（curl / python3）、WebSearch、WebFetch、Agent（子代理并行）

---

## 1. Jina Reader（主方案，默认使用）

Jina Reader 将任意 URL 转为 LLM-ready Markdown——无需逐源写正则，一行命令搞定。
免费可用，无需 API Key。单个请求 ~2-4s。

### 1.1 关键人物博客（8人并行）

**方式 A — 使用脚本批量采集（推荐）**：
```bash
python3 <skill_path>/scripts/jina_blogs_template.py
```
脚本自动采集 8 人博客，输出到 `~/Desktop/qoder_workspace/hermes_workspace_tmp/reports/hotspot-research_qoder/jina_cache/`。

**方式 B — 逐个 curl（通过 Bash 工具）**：
```bash
# Sam Altman
curl -sL --max-time 15 "https://r.jina.ai/https://blog.samaltman.com/" -H "Accept: text/markdown"

# Karpathy GitHub
curl -sL --max-time 15 "https://r.jina.ai/https://karpathy.github.io/" -H "Accept: text/markdown"

# Karpathy Bear Blog
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

**方式 C — 使用 WebFetch 工具（Qoder 原生）**：
直接使用 `WebFetch` 工具，URL 填 `https://r.jina.ai/https://blog.samaltman.com/`

### 1.2 深度补采原文

```bash
curl -sL --max-time 15 "https://r.jina.ai/{ARTICLE_URL}" -H "Accept: text/markdown"
```
或使用 `WebFetch` 工具直接获取 `https://r.jina.ai/{ARTICLE_URL}`。

### 1.3 Jina Reader 已知特征
- 博客类（Sam Altman/Naval/PG/Karpathy Bear）：完美提取，格式保留好
- 导航重网站（Forbes）：内容主体完整但掺杂导航/菜单文本，不影响可用性
- JS 渲染页面（Anthropic Research）：Jina 服务端有渲染能力，但复杂 SPA 可能缺部分内容
- 失败信号：返回空 / HTTP 403 / 超时 → 降级到旧 curl 方案或 WebSearch

### 1.4 降级路径

```
Jina 失败
    ↓
1. WebFetch 工具直接获取原文 URL
    ↓ 仍失败
2. P0 热点？ → WebSearch 搜索 + Browser MCP 获取
   非 P0  → 标注 [BLOCKED] 跳过
```

---

## 2. WebSearch 搜索命令（Qoder 内置）

使用 `WebSearch` 工具进行关键词搜索，获取实时搜索结果。

### 2.1 海外关键词搜索
```
搜索词 1: "AI agent" "solopreneur" 2026
搜索词 2: "AI personal brand" content creation
搜索词 3: "one-person business" AI automation
搜索词 4: AGI timeline latest 2026
搜索词 5: "AI job displacement" 2026
```

### 2.2 中文关键词搜索（补充路径，当 AI HOT 未覆盖时补充）
```
搜索词 1: AI 大模型 最新动态
搜索词 2: DeepSeek 最新进展
搜索词 3: AI Agent 落地应用 中国
搜索词 4: 超级个体 AI 副业
搜索词 5: AI 创业 一人公司
```

每个搜索 → top 5-8 结果 → 使用 WebFetch 提取高价值页面 → 标注 `[WebSearch]` → 三关审核。

### 2.3 使用 WebFetch 提取搜索结果
对 WebSearch 返回的高价值 URL，使用 `WebFetch` 工具获取页面内容：
- URL: 搜索结果中的文章 URL
- query: 提取关键词

---

## 3. HackerNews 热门（Bash curl Firebase API）

```bash
# 获取 top 20 story IDs
curl -sL --max-time 10 "https://hacker-news.firebaseio.com/v0/topstories.json"

# 逐个获取 story 详情
curl -sL --max-time 8 "https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
# 字段：title / url / score / time (Unix timestamp) / descendants (评论数)
```

---

## 4. Reddit 热门（Bash curl JSON API）

```bash
# 各 subreddit 热门帖子
curl -sL --max-time 12 "https://www.reddit.com/r/Entrepreneur/hot.json?limit=10"
curl -sL --max-time 12 "https://www.reddit.com/r/solopreneur/hot.json?limit=10"
curl -sL --max-time 12 "https://www.reddit.com/r/singularity/hot.json?limit=10"
curl -sL --max-time 12 "https://www.reddit.com/r/artificial/hot.json?limit=10"
curl -sL --max-time 12 "https://www.reddit.com/r/MachineLearning/hot.json?limit=10"
# 字段：data.children[].data.{title, permalink, ups, num_comments, created_utc}
```

---

## 5. B站热门（Bash curl API）

```bash
# B站科技区热门
curl -sL --max-time 10 "https://api.bilibili.com/x/web-interface/ranking/v2?rid=36"
# B站全站热门
curl -sL --max-time 10 "https://api.bilibili.com/x/web-interface/ranking/v2?rid=1"
# 字段：data.list[].{title, bvid, stat.{view, danmaku}, owner.name}
```

---

## 6. 百度热搜（Bash curl）

```bash
curl -sL --max-time 10 "https://top.baidu.com/board?tab=realtime"
# 从 HTML 中提取 "word" 字段
```

---

## 7. 微博热搜（Bash curl API）

```bash
curl -sL --max-time 10 "https://weibo.com/ajax/side/hotSearch"
# 字段：data.realtime[].{word, raw_hot}
# 注意：可能被反爬限制，降级为 WebSearch 搜索
```

---

## 8. 36氪快讯（Bash curl API）

```bash
curl -sL --max-time 10 "https://36kr.com/pp/api/newsflash"
# 字段：data.items[].{title, news_url}
# Fallback: curl https://36kr.com/newsflashes (HTML 提取)
```

---

## 9. 搜狗微信搜索（Bash curl）

```bash
# 搜索关键词（每次跑3个关键词，控制请求量）
curl -sL --max-time 10 "https://weixin.sogou.com/weixin?type=2&query=AI&ie=utf8"
curl -sL --max-time 10 "https://weixin.sogou.com/weixin?type=2&query=大模型&ie=utf8"
curl -sL --max-time 10 "https://weixin.sogou.com/weixin?type=2&query=超级个体&ie=utf8"
# 注意：搜狗微信有反爬，成功率约 20%。成功时质量 B 级。
```

---

## 10. Newsletter RSS 提取（Bash curl + python3）

### import.ai — Jack Clark (Substack)
```bash
curl -sL "https://importai.substack.com/feed" | python3 -c "
import sys, re
html = sys.stdin.read()
items = re.findall(r'<title><!\[CDATA\[([^\]]+)\]\]></title>', html)
urls = re.findall(r'<link>([^<]+)</link>', html)
for t, u in zip(items[1:6], urls[1:6]):
    print(f'{t.strip()} → {u}')
"
```

### One Useful Thing (Ethan Mollick — Substack)
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

## 11. AI HOT REST API（中文 AI 行业动态 · v2.0.0）

AI HOT（aihot.news）提供公开免费 REST API，覆盖中国 AI 行业动态。旧域名 `aihot.virxact.com` 与 `/api/public/*` 将于 **2026-10-31** 停用，新脚本一律使用 `aihot.news/api/v1/*`。

### 11.1 先决条件：必须带 User-Agent

```bash
UA="aihot-api/2.0.0 aihot-skill"
```

### 11.2 预检（轻量 items 请求）

```bash
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/items?mode=selected&window=24h&limit=1" --max-time 8
# 返回含 "items" 的 JSON → API 可用，继续采集
# 超时/错误 → API 不可用，跳过并使用替代路径
```

### 11.3 精选拉取（日报默认路径）

```bash
# 拉最近 24h 精选（日报默认）
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/items?mode=selected&window=24h&limit=50" --max-time 15 -o /tmp/aihot_daily.json

# 拉最近 7 天精选（周报默认；limit 最大 100，翻页见 11.8）
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/items?mode=selected&window=7d&limit=100" --max-time 20 -o /tmp/aihot_weekly.json
```

**响应字段**：`items[]` 每条包含 `id/title/originalTitle/summary/source.name/links.aihot/links.original/publishedAt/discoveredAt/category/score/selected/reason`；分页信息在 `page.nextCursor` / `page.hasMore`。

**注意**：`window` 只支持 `24h` 和 `7d`；不支持 `30d`。30 天视图请用 11.6 的周报拼接。

### 11.4 分类拉取

5 个 category：`ai-models` / `ai-products` / `industry` / `paper` / `tip`

```bash
# 拉最近 7 天 AI 模型发布
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/items?mode=selected&window=7d&category=ai-models&limit=50"

# 拉最近 7 天 AI 产品发布
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/items?mode=selected&window=7d&category=ai-products&limit=50"

# 拉最近 7 天 AI 行业动态
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/items?mode=selected&window=7d&category=industry&limit=50"

# 拉最近 7 天 AI 论文
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/items?mode=selected&window=7d&category=paper&limit=50"
```

### 11.5 关键词搜索

```bash
# 找 OpenAI 相关
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/items?q=OpenAI&limit=30"

# 找 DeepSeek 相关
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/items?q=DeepSeek&limit=30"

# 关键词 + 时间窗（Anthropic 最近 7 天）
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/items?mode=selected&q=Anthropic&window=7d&limit=30"
```

### 11.6 日报 / 周报 / 月报（Markdown 成品）

```bash
# 最新日报
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/agent/daily"

# 指定日期日报（YYYY-MM-DD）
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/agent/daily/2026-10-19"

# 指定周报（YYYY-Wxx）
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/agent/weekly/2026-W42"

# 指定月报（YYYY-MM）
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/agent/monthly/2026-09"

# 30 天视图：4 份周报 + 边界日报拼接（接口不支持一次拉 30d）
```

### 11.7 热点拉取（当前最热，多源热度排序）

```bash
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/hot-topics" --max-time 15
# 返回每条带 sourceCount / signalCount / participantCount / links.aihot
```

### 11.8 分页拉取（cursor 翻页）

```bash
# 第 1 页
resp1=$(curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/items?mode=all&window=7d&limit=100")
echo "$resp1" | python3 -c "import sys,json; d=json.load(sys.stdin); p=d.get('page',{}); print(f'count={p.get(\"count\")}, hasMore={p.get(\"hasMore\")}, nextCursor={p.get(\"nextCursor\",\"null\")}')"

# 第 2 页（将 page.nextCursor 传入 cursor 参数）
cursor=$(echo "$resp1" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('page',{}).get('nextCursor',''))")
curl -sH "User-Agent: $UA" "https://aihot.news/api/v1/items?mode=all&window=7d&limit=100&cursor=$cursor"
```

**注意**：cursor 是不透明 token，不要解析/递增/跨端点复用。`hasNext=false` 或 `nextCursor=null` 时停止翻页。

### 11.9 限流与降级

- 限流：60 req/min/IP，串行调用，翻页/连续查询间隔 >=1s
- 遇 429 退避 30-60s 后恢复
- 数据窗口：items 端点仅返回最近 7 天
- 降级路径：API 不可用时使用 WebSearch 中文搜索 + 搜狗微信 + 手动补采小红书/微博

---

## 12. 日期提取技巧（按来源）

| 来源 | 日期获取方式 | 可靠性 |
|------|------------|--------|
| Sam Altman blog (Posthaven) | JS 变量中的 `data-unix-time`；列表顶部=最新 | 中 |
| Naval (WordPress) | JSON-LD `"datePublished"` | 高 |
| Paul Graham | 无日期；列表顶部=最新；需交叉验证 | 低 |
| Substack / Anthropic blog | Header 文本日期（如 "Apr 28, 2026"） | 高 |
| HackerNews / Reddit API | `time` / `created_utc` Unix timestamp → UTC | 高 |
| WebSearch 结果 | `page_age` 或 snippet 中的日期文本 | 中 |

---

## 并行采集策略

使用 `Agent` 工具启动子代理并行采集不同信息源组：

| 子代理 | 采集内容 | 预期输出 |
|--------|---------|---------|
| Agent 1 | 8 人关键博客（Jina Reader） | 8 篇博客 Markdown |
| Agent 2 | AI HOT REST API（精选/热点/日报） | 30-50 条中文 AI 动态 |
| Agent 3 | HackerNews + Reddit 热门 | 20-30 条海外热点 |
| Agent 4 | B站 + 百度 + 微博 + 36氪 | 15-20 条国内热点 |
| Agent 5 | WebSearch 关键词搜索（中英文） | 10-15 条搜索结果 |

主线程汇总各子代理结果后执行三关审核。
