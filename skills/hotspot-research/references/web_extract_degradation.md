# Web Extract 作为 Jina Reader 降级路径（交互 session）

> **创建日期：** 2026-07-04
> **状态：** 实战验证有效，补充进 hotspot-research 工具链
> **目的：** 填补 Jina Reader 在某些时段不可用时的稳定降级路径

---

## 一、为什么需要这个降级

Jina Reader 在 2026-07-04 session 中**连续 4 次 curl 调用全部超时**（exit 28，connect timeout to `r.jina.ai:443`）。而**同一 session**内，`web_extract` 工具 5 个 URL 并行调用**全部成功**，输出干净的 Markdown 内容。

这是非平凡的工具替代模式——Jina 不通时 `web_extract` 是完美降级。

## 二、工具对比

| 维度 | Jina Reader (`r.jina.ai`) | `web_extract` (Hermes 内置) |
|------|--------------------------|------------------------------|
| 调用形式 | `curl -sL "https://r.jina.ai/{URL}"` | `web_extract(urls=[...])` 工具调用 |
| 输出 | Markdown | Markdown (LLM-summarized，>5000 字符自动截断) |
| 并发 | 需手动串联（foreground terminal 不支持 `&`） | 原生支持批量（最多 5 URLs/调用） |
| 提取质量 | 全文保留，导航噪声少 | 智能提取正文，过滤导航/广告 |
| 可用性 | 受 LibreSSL TLS / AS30058 IP 信誉影响 | 通过 Hermes gateway，绕过本地 TLS 问题 |
| 长度限制 | 无（但 50KB+ 输出建议不读全文） | >5000 字符自动 LLM 摘要 |

## ⚠️ 环境依赖警告（2026-07-05 实战验证）

`web_extract` **不是 Hermes 通用工具**——它是部分安装/版本的可选工具。**2026-07-05 实战**：尝试调用 `web_extract` 返回 `Tool 'web_extract' does not exist`。在该环境下必须用替代路径。

**环境检测规则（强制前置）：**
```
Step 1：在降级到 web_extract 前先确认工具存在
        → 尝试一次调用，失败立即切换。
```

**按环境分类的降级路径：**
| 环境 | Jina 失败时首选 | 备选 |
|------|---------------|------|
| **有 `web_extract`** | `web_extract(urls=[...])`（如本节原描述） | Tavily snippet / Python requests |
| **无 `web_extract`（2026-07-05 实测环境）** | `mcp__brave_search__brave_llm_context` + Python `requests` 组合 | Python `requests` 直连 + BeautifulSoup/regex |

**关键反模式**：永远**不要**默认假设 `web_extract` 可用——它是环境可选工具，按需检测。

## 三、何时使用 web_extract 替代 Jina（仅当工具已确认可用时）

| 触发条件 | 优先选择 | 理由 |
|---------|---------|------|
| 已确认 `web_extract` 在当前环境可用 + Jina Reader 在当前 session 内连续超时（exit 28/35/147字节错误）| **`web_extract` 优先** | 本地 TLS/IP 信誉问题影响 Jina，但不影响 Hermes gateway |
| 已确认可用 + 5+ 个 URL 需要并行提取 | `web_extract` | 单次最多 5 URLs，避免 terminal 串联慢 |
| 关键文章需要逐字引用（>5000 字）| Jina Reader | `web_extract` 会被 LLM 摘要截断 |
| 博客首页（无具体文章 URL）| Jina Reader | `web_extract` 对博客列表页提取质量不稳定 |
| cron session | Jina Reader（Python bypass） | `web_extract` 在 cron 中可能不可用（SKILL.md 已知约束）|
| 交互 session + 短文/单篇文章 + 工具已确认可用 | `web_extract` | 单次调用，省去 Python 脚本 |
| **`web_extract` 不可用**（实测：返回 `Tool 'web_extract' does not exist`） | **`brave_llm_context` + Python `requests` 组合**——详见 references/llm_brave_context_alternative_path.md | 不依赖环境可选工具 |

## 四、实战调用模式

```python
# 交互 session 中（直接调用 Hermes 工具）
web_extract(urls=[
    "https://www.creativeboom.com/news/state-of-creative-industry-2026",
    "https://author.envato.com/hub/beyond-adoption-ai-creative-work-2026",
    "https://www.huxiu.com/article/4856551.html",
    "https://humbldesign.io/blog-posts/will-ai-replace-designers-2026",
    "https://clutch.co/resources/graphic-design-industry-2026",
])
# → 一次调用返回 5 个 URL 的结构化 Markdown
# → 失败 URL 在 results[i].error 字段标注
```

## 五、降级链路完整决策树

```
需要提取网页内容
    ↓
Jina Reader 可用？
    ├─ YES → 用 Jina（Python bypass 默认，curl 仅当 Python 不可用）
    │         ↓
    │     输出干净？→ YES 用 / NO（>5000 字符导航噪声）→ web_extract
    │
    └─ NO（连续 2 次 Jina 超时/失败）
         ↓
         session 类型？
         ├─ 交互 session → web_extract（首选）
         │                  ↓
         │              批量 URLs 仍失败？→ Tavily/Brave snippet 替代（信息完整度 60%）
         │
         └─ cron session → Python bypass（requests + verify=False）
                            ↓
                        AS30058 IP 阻止？→ AI HOT + Tavily snippet 推断
```

## 六、与现有 reference 的关系

- **本文件**：聚焦"web_extract 在交互 session 作为 Jina 降级"——本次会话实战产出
- **`references/jina_ssl_bypass.md`**：聚焦"Python bypass 修复 LibreSSL TLS 问题"——cron session 默认路径
- **两者互补**：交互 session 用 web_extract，cron session 用 Python bypass，互不冲突

## 七、关键学习点（卷哥工作风格）

1. **不要因为一个工具失败就跳过任务**——`web_extract` 救了本次 2 个深挖任务
2. **同一 session 内多工具降级是常见模式**——不需要切换 session，只需切换调用方式
3. **结构化 JSON 输出便于二次处理**——`web_extract` 的 `results[].error` 字段比 Jina 的 silent fail 更友好
4. **批量调用是降级路径的隐藏优势**——5 URLs/调用 vs Jina 的逐个 curl 串联

---

*实战日期：2026-07-04（creative-industry-ai-trust-2026 + gartner-skill-lifecycle-2026 两次深挖中均使用）*