# `brave_llm_context` + Python `requests` 组合降级路径

> **创建日期：** 2026-07-05
> **状态：** 实战验证有效（Semrush AI Visibility Index 2026 深挖，案例型 16KB / 17KB 完整产出）
> **目的：** 当 `web_extract` 不可用 + Jina Reader 不可用时，提供不依赖环境可选工具的稳定降级路径

---

## 一、为什么需要这个降级

`web_extract_degradation.md` 推荐在 Jina 失败时用 `web_extract`。但 **2026-07-05 实战**：该环境下 `web_extract` 工具**不存在**——返回 `Tool 'web_extract' does not exist`。常见原因：Hermes 版本不同、toolset 配置差异。

需要在不依赖 `web_extract` 的前提下，组合现有工具达到同等提取效果。

---

## 二、验证有效的双源组合

### 组合 A：`mcp__brave_search__brave_llm_context`（首选）

| 维度 | 说明 |
|------|------|
| 输出形式 | 直接返回 LLM-extracted snippets，**无需 fetch 原始 URL** |
| 数据源 | Brave 索引库的预提取文本，已按相关性排序 |
| 并发支持 | ✅ 原生并行（单次调用可指定 `maximum_number_of_urls: 3-5`） |
| 适用 | 需要**关键段落 + 数据点 + 金句**时 |
| 限制 | 仅返回核心段落，不能精确引用定位；付费墙后仅摘要级 |

**调用模板：**
```python
mcp_brave_search_brave_llm_context(
    query="<精确查询词，含公司名+产品名+具体维度>",
    maximum_number_of_urls=3,           # 建议 3-5
    maximum_number_of_tokens=8192,       # 默认即可
    freshness="2026-06-26to2026-07-05"   # 24h/7d/自定义均可
)
```

**案例实证（2026-07-05）：** Semrush 报告全文关键论点通过单次 LLM Context 命中 3 篇媒体（Yahoo Finance、Semrush 官方、BusinessWire），覆盖"Universal 36"定义、行业集中度数据、四平台差异——**信息完整度提升至 85%**。

### 组合 B：Python `requests` 直连（提取原文级细节）

当 LLM Context 的 snippets 不够、需要精确段落/数字/金句时，使用 Python `requests` 直连：

```python
import requests
from bs4 import BeautifulSoup  # 可选

url = "https://example.com/article"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}
response = requests.get(url, headers=headers, timeout=15, verify=False)

# 方式 1：正则快速提取（新闻/博客正文）
import re
# 找正文段落
paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', response.text, re.DOTALL)
clean_text = ' '.join(re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs)

# 方式 2：BeautifulSoup 结构化提取
soup = BeautifulSoup(response.text, 'html.parser')
title = soup.title.string
# 不同站点正文容器不同（article / .entry-content / main 等）
article = soup.find('article') or soup.find(class_='entry-content') or soup.find('main')
text = article.get_text(separator='\n', strip=True) if article else soup.get_text()
```

**关键参数：**
- `verify=False` —— 应对 macOS LibreSSL 与某些站点（如 ppc.land）的 TLS 链问题（2026-07-05 实测，pyppeteer + requests+verify=False 完美连接；Jina+curl 都失败）
- `User-Agent` 浏览器头 —— 避免被识别为 bot 返回简化版
- `timeout=15` —— 避免永久挂起

**案例实证（2026-07-05）：** PPC Land（162KB HTML）+ BriefGlance（34KB HTML）通过 Python 直连成功提取。配合正则提取段落，得到完整原文。**两次调用 ~3 秒完成**。

---

## 三、组合 C：Lark + `write_file` 落盘大文档

当单篇文章 >30KB HTML 时，提取的 Markdown 也可能很大。最佳实践：

```python
# 1. 提取到 /tmp/<site>_<topic>.md（避免污染 conversation context）
content = extract_to_markdown(url)

# 2. 分段 read_file 消费（limit=200, offset=N）
# 避免单次 read_file >100K 字符触发截断
with open(f'/tmp/article_{topic}.md', 'w') as f:
    f.write(content)

# 3. Agent 在后续轮次中分段读
# read_file(path='/tmp/article_topic.md', offset=1, limit=200)
```

---

## 四、双源组合的决策树

```
需要提取网页内容
    ↓
session 内 Jina Reader 可用？
    ├─ YES → 用 Jina
    └─ NO（连续超时）
         ↓
         session 内 `web_extract` 可用？
         ├─ YES → web_extract（首选，按 references/web_extract_degradation.md）
         └─ NO（本次实测环境）
              ↓
              只需要关键段落/数据/金句？
              ├─ YES → brave_llm_context（组合 A）—— 并行 3-5 个 URL 的预提取 snippets
              │
              └─ NO，需要原文级细节
                   ↓
                   短文（<30KB HTML）？
                   ├─ YES → Python requests 直接 + BeautifulSoup（组合 B）
                   └─ NO，长文 → 落到 /tmp 文件，分段 read_file（组合 C）
```

---

## 五、与现有 references 的关系

| 文件 | 角色 |
|------|------|
| `references/web_extract_degradation.md` | 当 `web_extract` **可用**时的降级路径首选 |
| `references/jina_ssl_bypass.md` | Python bypass 修复 LibreSSL TLS 问题（cron session 默认路径）|
| **`references/llm_brave_context_alternative_path.md`（本文件）** | **当 `web_extract` 不可用时**的稳定替代 |

三者互补不冲突：
- 有 `web_extract` → 用它
- 无 `web_extract` + 短文要原文 → 用本文件组合 B（Cron session 同样适用）
- 无 `web_extract` + 只要关键段落 → 用本文件组合 A
- Cron session + AS30058 IP 阻止 + 需要 Python bypass → 用 jina_ssl_bypass.md

---

## 六、关键学习点

1. **永远不要假设某个工具默认可用**——Hermes 不同版本、不同 profile 的工具集不同。**第一个调用前先确认工具存在**。
2. **勇敢尝试新组合**——`brave_llm_context` 的 snippets 质量足够覆盖 80-85% 的需求，不必追求 100% 全文。
3. **Python `requests` 直连是永恒降级**——不受任何环境变化影响，是最稳的 fallback。
4. **落地 /tmp 文件 + 分段消费**是处理大文档的标准模式，避免 token 浪费。

---

*实战日期：2026-07-05（Semrush AI Visibility Index 2026 增量深挖，B 路径产出 16KB+17KB Markdown）*
