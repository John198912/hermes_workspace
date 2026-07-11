# 搜索工具全面故障 · 降级 Recipe（Qoder 适配版）

> **触发条件**：WebSearch 连续 ≥3 次失败或返回异常，且 WebFetch 也不可用。
> **Qoder 工具适配版**：原 Brave MCP → WebSearch；原 Tavily → WebSearch；原 Jina → WebFetch；原 豆包 → WebSearch（中文关键词）

> **不要假设会自动恢复**——直接执行降级链路。

---

## 降级链（按顺序）

### Tool 1：WebSearch 多角度并行（保留主搜索能力）

```
# 多组不同角度的查询并行
WebSearch(query="<核心种子查询1>")
WebSearch(query="<核心种子查询2>")
WebSearch(query="<核心种子查询3>", timeRange=OneWeek)
```

典型输出：搜索结果含 title / url / description / snippet。
注意 snippet 中的内容——对 4 天内的报道时效性准确。

### Tool 2：WebFetch 直连已知 URL（最高质量原文提取）

```
# 对已发现的 URL 用 WebFetch 获取原文
WebFetch(url="<URL1>")
WebFetch(url="<URL2>")
WebFetch(url="<URL3>")
```

WebFetch 返回的内容是**原文核心段落**——这是降级链中质量最高的源。

### Tool 3：中文关键词搜索（中文 + 中国视角）

```
# WebSearch 使用中文关键词
WebSearch(query="<中文查询> 2026")
```

中文话题**优先用中文关键词搜索**——海外源对中国实操案例覆盖弱。

### Tool 4：Bash + Python requests（提取原文核心段落）

```bash
python3 -c "
import requests
urls = ['<URL1>', '<URL2>', '<URL3>']
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=30, verify=False)
        print(f'=== {url} === STATUS: {r.status_code} LEN: {len(r.text)}')
        print(r.text[:5000])
        print('---END---')
    except Exception as e:
        print(f'=== {url} === ERROR: {e}')
"
```

### Tool 5：Bash + curl（直连新闻，仅当需要时效信号时）

```bash
curl -sL -H "User-Agent: Mozilla/5.0" "<URL>" --max-time 30
```

---

## 验证结果

| 日期 | 话题 | 工具调用数 | 信息完整度 | 备注 |
|------|------|-----------|-----------|------|
| 0613 NYT「AI 扼杀经济」| 12 次 | 85% | 降级路径已建立 |
| 0701 Token 末日 | 15+ | 93% | 多路协同 |
| 0705 Ramp 黑箱化 | 23+ | **95%** | 全并行 + Python 处理 120KB PDF |

> **结论**：搜索工具故障**不再是阻塞事件**。从第 1 步开始即视为降级路径启动。

---

## Pitfalls（避免重蹈）

1. **不要等自动恢复**——直接降级。
2. **不要单独依赖 WebFetch**——要并行调用至少 3 路。
3. **不要编造信息**——所有具体数字必须能在参考资料的链接中找到原文，否则标注「⚠️ 最优先补充动作」。

---

## 输出验收清单

完成降级采集后，逐项检查：

- [ ] 每个核心种子都至少有 2 个独立信源
- [ ] 至少有 1 个信源是 P1（一手原文 / 官方报告 / 学术 PDF）
- [ ] 中国版至少 1 条（除非纯海外话题）
- [ ] 反对/边界条件至少有 1 条
- [ ] 时间戳都在 ±30 天内
- [ ] 参考资料清单链接都实测可打开（不是看似可信的假链接）

未达标 → 进入第二轮降级，第 ⑤ 步「标注具体缺失项」不阻塞主流程。
