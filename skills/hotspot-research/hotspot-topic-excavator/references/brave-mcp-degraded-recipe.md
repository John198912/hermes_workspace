# Brave MCP 全面故障 · 降级 Recipe（2026-07-05 验证）

> **触发条件**：Brave MCP 返回 `ClosedResourceError: ClosedResourceError()` 或
> `MCP server 'brave-search' is unreachable after 3 consecutive failures`，
> 连续 ≥ 3 次 auto-retry（间隔 ~30s/次），且 `brave_llm_context` + `brave_web_search` + `brave_news_search` 全挂。

> **不要假设会自动恢复**——三次会话连续（0630 NYT、0701 多 P0、0705 Ramp）的降级路径已被反复验证，直接执行。

---

## 五工具并行降级链（按顺序）

### Tool 1：先清僵尸进程 + Brave 直连（保留 MCP 的 fallback）

```bash
# 清理 Brave MCP 残留（hermes-stale-cleanup.sh，~5s）
bash ~/.hermes/scripts/brave-stale-cleanup.sh -q 2>&1 | tail -5

# Brave 直连（绕过 MCP stub，30s 内返结果）
python3 ~/.hermes/scripts/brave_direct.py web "<核心种子查询>" -n 10 2>&1
```

典型输出：JSON 数组，每条含 `title` / `url` / `description` / `age`。
注意 `age` 字段——本会话验证：Brave 直连对 4 天内的报道 `age: "4 days ago"` 准确。

### Tool 2：Tavily 多组并行（最佳覆盖深度的兜底）

```bash
cd ~/.hermes/skills/tavily-search
python3 scripts/tavily_search.py -q "<精确查询1>" --topic news --days 30 -n 12 2>&1
# 复杂概念换深度模式：
python3 scripts/tavily_search.py -q "<学术框架查询>" --topic general --search-depth advanced -n 10 2>&1
```

Tavily 返回 `answer`（AI 摘要）+ `results[].content`（原文核心段落，非仅 snippet）——这是 4 路工具中**唯一同时给答案+原文**的源。

### Tool 3：豆包搜索（中文 + 中国视角，~10s 内）

```bash
cd ~/.hermes/skills/byted-web-search
python3 scripts/web_search.py "<中文查询>" --time-range OneMonth --count 10 2>&1 | head -60
```

`--time-range` 可选：`OneWeek` / `OneMonth` / `OneYear`。中文话题**优先用豆包**——海外源对中国实操案例覆盖弱（中国企业 AI 落地报告仅有中国源）。

### Tool 4：Jina Reader（提取原文核心段落，最高质量）

```bash
python3 -c "
import requests
urls = ['<URL1>', '<URL2>', '<URL3>']
for url in urls:
    try:
        r = requests.get(f'https://r.jina.ai/{url}',
                         headers={'Accept': 'text/markdown',
                                  'X-Respond-With': 'markdown'}, timeout=30)
        print(f'=== {url} === STATUS: {r.status_code} LEN: {len(r.text)}')
        print(r.text[:5000])
        print('---END---')
    except Exception as e:
        print(f'=== {url} === ERROR: {e}')
" 2>&1
```

**注意**（0705 验证）：
- `r.jina.ai/` 对 Substack / 个人博客 / 新闻媒体回 200（25-70KB Markdown）——优质
- 对 PDF（学术论文 / 工作论文）回 200 并把全文解析为 Markdown（120KB Stanford 论文验证成功）——优质
- 仅对部分付费墙媒体（Bloomberg/WSJ 全文）效果不稳定——降级到第 ⑤ 步

### Tool 5：Brave 直连 news（仅当需要时效信号时）

```bash
python3 ~/.hermes/scripts/brave_direct.py news "<时效查询>" --freshness pm -n 8 2>&1
```

`freshness`：`pd`（24h）/ `pw`（7d）/ `pm`（31d）/ `py`（365d）。

---

## ⚡ 0613 / 0701 / 0705 三次验证结果

| 日期 | 话题 | 工具调用数 | 信息完整度 | 备注 |
|------|------|-----------|-----------|------|
| 0613 NYT「AI 扼杀经济」| 12 次 | 85% | 0024 已建立稳定降级路径 |
| 0701 Token 末日 | 15+ | 93% | Brave + Tavily 协同 |
| 0705 Ramp 黑箱化 | 23+ | **95%** | 4 路全并行 + Jina 处理 120KB PDF |

> **结论**：Brave MCP 全面故障**不再是阻塞事件**。从第 ① 步开始即视为降级路径启动。

---

## Pitfalls（避免重蹈）

1. **不要等 Brave MCP auto-retry**——`Auto-retry available in ~57s` 是假的，会再挂 3 次。直接降级。

2. **不要单独依赖 Jina**——Jina IP 信誉（AS30058）随地区不同表现不同，本会话 0705 工作得很好，但下一会话可能挂。要并行调用至少 3 路。

3. **Tavily `--search-depth advanced`** 仅用于学术框架/复杂概念（cost 高）——日常用 `--topic general -n 8` 即可。

4. **豆包搜索有时返 502**（0701 验证：`AI 大模型关键词组` 503）——这种情况切换到**主话题查询的子话题**重试，而不是放弃豆包。

5. **不要编造信息**——本会话 0705 严格遵循：所有具体数字（10.2%、12%、16%、$30/人/月）必须能在 §五参考资料清单的链接中找到原文，否则标注「⚠️ 最优先补充动作」。

---

## 输出验收清单

完成降级采集后，逐项检查：

- [ ] 每个核心种子都至少有 2 个独立信源
- [ ] 至少有 1 个信源是 P1（一手原文 / 官方报告 / 学术 PDF）
- [ ] 中国版（豆包或国内媒体）至少 1 条（除非纯海外话题）
- [ ] 反对/边界条件至少有 1 条（TechCrunch 因果混淆、权威机构 reverse evidence 等）
- [ ] 时间戳都在 ±30 天内
- [ ] §五参考资料清单**链接都实测可打开**（不是看似可信的假链接）

未达标 → 进入第二轮降级，第 ⑤ 步「标注具体缺失项」不阻塞主流程。
