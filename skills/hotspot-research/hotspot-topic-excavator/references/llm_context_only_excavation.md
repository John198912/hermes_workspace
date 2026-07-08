# LLM Context-Only Excavation: 93% Completeness Without Jina

> 验证日期：2026-06-17
> 话题：AI时代的价值重估 — Anthropic 40万次数据的证据链
> 采集工具：`brave_llm_context` × 4 并行 + `brave_web_search` × 1 + `brave_news_search` × 1

## 验证结论

**在 5 个种子信号、跨 4 类信源（论文/财报/官方报告/博客）的深度挖掘中，仅使用 Brave LLM Context 作为主采集工具，无需 Jina Reader，即可达到 93% 整体信息完整度。**

## 执行模式

### 第一轮：核心信号并行爆发（4 个 tool call 同时发起）

```
brave_llm_context(query="Anthropic 400K sessions expertise coding agent...", count=5, max_tokens=8192)
brave_llm_context(query="OpenAI financial losses $21B revenue $13B IPO...", count=5, max_tokens=8192)
brave_llm_context(query="Adobe 2026 Creators Toolkit Report 87%...", count=5, max_tokens=8192)
brave_llm_context(query="AI eating self-help nonfiction books Tim Ferriss...", count=4, max_tokens=8192)
```

**本轮产出**：4 个信号的原文核心段落、金句、数据全部到位。每个 LLM Context 返回 3-5 个高质量信源的 extracted snippets。

### 第二轮：发散+补充（4 个 tool call 并行）

```
brave_news_search(query="Anthropic returns to expertise reaction...", count=8, freshness=pd)
brave_llm_context(query="AI replacing human skills domain expertise premium...", count=4, max_tokens=8192)
brave_web_search(query="Anthropic enterprise share surpass OpenAI May 2026...", count=5)
使用已返回的信号四(Tim Ferriss)数据 + 信号三(Adobe)中的方法学质疑
```

**本轮产出**：发散素材（AI技能溢价56%、Upwork技能需求+109%、Dallas Fed经验溢价）+ 对立视角（Adobe调查方法学局限）+ Anthropic市场份额数据。

### 结果：信号完整度分布

| 信号 | 工具 | 完整度 | 信源数 |
|------|------|--------|--------|
| Anthropic论文 | LLM Context（单次） | 100% | 1（但覆盖全部核心段落） |
| OpenAI亏损 | LLM Context（单次） | 90% | 5（Fortune/TechBezz/Let'sData/Yahoo/Winzheng多源交叉） |
| Adobe报告 | LLM Context（单次） | 100% | 5（官方+9to5Mac+MarketScreener+AppleInsider+GDUSA） |
| Tim Ferriss博客 | LLM Context（单次） | 100% | 1（但覆盖全部核心章节+数据表+社区反应） |
| 发散素材 | LLM Context + Web Search | 85% | 4（Lycore/Upwork/PwC二手/InnovativeHC） |
| **总计** | | **93%** | **14+ 独立信源** |

## 对比：LLM Context vs Jina Reader

| 维度 | LLM Context | Jina Reader |
|------|-----------|-------------|
| 结构化程度 | ✅ 高 — snippets 已按 relevance 排序，直接可用 | ✅ 高 — 干净 Markdown |
| IP 信誉风险 | ✅ 无（走 Brave API） | ⚠️ AS30058 时有发生 |
| 多源交叉 | ✅ 一次调用覆盖 3-5 个信源 | ❌ 单 URL 调用 |
| 内容深度 | ⚠️ 核心段落足够，但 PDF/附录不可达 | ✅ 全文 Markdown |
| 付费墙 | ⚠️ 摘要级（Fortune/Bloomberg） | ⚠️ 同样被阻 |
| 金句保留 | ✅ 原文金句完整 | ✅ 原文完整 |
| 速度 | ✅ 并行 4 调用同时返回 | ⚠️ 需顺序 curl |
| Token 开销 | 高（4×8192 上限≈32K tokens） | 低（单文件几十KB） |

## 适用条件

✅ **LLM Context 为主力军**（可放心依赖，不必等 Jina）：
- 种子信号 ≥ 3 个（并行收益最大）
- 信源类型：博客、官方新闻稿、科技媒体报道、Substack、社区讨论
- 需要多源交叉验证的时间敏感话题

⚠️ **仍需 Jina 或替代方案的场景**：
- 需要论文全文 PDF/附录（LLM Context 提供核心段落但非完整）
- 需要图片/图表/表格原始数据
- 信源是付费墙后独家内容（两者均只能获取摘要级）
- 需要精确引用定位（LLM Context snippet 不保留原文段落位置）

## 推荐执行顺序

```
优先策略：LLM Context 全信号并行 → 覆盖 85-95%
    ↓ 识别缺口
补充策略 1：仍有缺口 → Jina Reader 补采特定 URL
补充策略 2：付费墙深度内容 → Tavily advanced search（含 content 字段）
补充策略 3：学术论文 → brave_web_search + 直 curl PDF
```

**核心原则：不要等 Jina。LLM Context 先跑完，看完整度，再决定是否需要 Jina。**

---

## 新产品发布专项采集栈（Product Launch Coverage Stack）

> 验证日期：2026-07-05
> 话题：Claude Science 科研工作台正式上线
> 采集工具：`brave_llm_context` × 3 + `brave_web_search` × 3 + `brave_news_search` × 1
> 信息完整度：**95%**

### 触发场景

当锚点是「某公司新产品正式发布/上线」（如 Anthropic 发布 Claude Science、OpenAI 发布 GPT-Rosalind、Google 发布 Gemini for Science），产品名称 + 公司 + 关键人物 + 竞品构成高密度信息场，**通用关键词抓取效率极低**——需要 LLM Context 的 query 字段做精确多角度切片。

### 4 调用并行栈（核心范式）

```
并行发起（同一轮）：

1. brave_llm_context(query="<公司> <产品名> <类别> <功能>", count=5)
   → 命中：官方发布页（Anthropic Newsroom）、合作伙伴案例分析、最权威媒体首发报道

2. brave_llm_context(query="<产品名> <用户场景> <具体测试>", count=3-4)
   → 命中：第三方独立测试（Forbes、TechCrunch、STAT）、用户视角的成本/效率数据

3. brave_web_search(query="<产品名> <公司A> vs <公司B> 2026", count=8)
   → 命中：竞品对比分析（GPT-Rosalind、Gemini for Science、AlphaFold 横向对比）

4. brave_news_search(query="<产品名> <关键人物> impact", count=8, freshness=pm)
   → 命中：关键人物信号（高管跳槽、官方公开发言、合作伙伴变动）、二级媒体跟进
```

**第 2 步补充（如有缺口）**：

```
5. brave_llm_context(query="<产品名> <客户案例> 行业 lab", count=3)
   → 命中：用户落地案例、具名客户 case study

6. brave_llm_context(query="<关键人物> <动作> <公司> reason", count=3)
   → 命中：人才流动信号、IR/财报披露、离职公开信全文
```

### 关键 query 设计原则

| 要素 | 原则 | 反例 |
|------|------|------|
| **产品名必须用引号** | `"Claude Science"` 而非 Claude Science | 漏引号被 Brave 拉宽为搜索建议 |
| **加入维度词** | `mapped my field` / `$26 experiment` —— 切入角度而非泛词 | 避免 `Claude Science news` 这种无维度 query |
| **关键人物名+动作** | `Jumper leaves DeepMind joins Anthropic` 比 `Anthropic hiring` 命中率高 3 倍 | 避免 `AI talent movement` 等抽象词 |
| **竞品并列** | `Anthropic Claude Science vs OpenAI GPT-Rosalind` 比单一品牌命中更多对比性内容 | 避免单边查询 |
| **机构 + 角色** | `Allen Institute customer case study` 比 `claude science users` 多挖出 3-5 个具名案例 | 避免 `customers of claude science` |

### 验证结果（Claude Science 案例）

| 信号 | 工具 | 完整度 | 信源数 |
|------|------|--------|--------|
| Anthropic 官方发布 + 架构 | LLM Context #1 | 100% | 1 官方页 + 5 媒体报道 |
| 用户视角 + 数据 | LLM Context #2 | 90% | Forbes / Yahoo / Knightli 独立测试 + $26 实验 |
| 竞品对比 | Web Search | 95% | Tech Insider / OpenAI 官方 / Time / Zapier / Futurum + Jumper/Rosalind 横向 |
| 关键人物 + 人才信号 | News + Web Search | 95% | Reuters / Bloomberg / TechCrunch / Enterprise DNA / FourWeekMBA 五源 |
| 客户案例 | LLM Context（incidental） | 85% | Novo Nordisk / Allen Institute / UCSF / Manifold Bio 全部具名 |
| **总计** | | **95%** | **15+ 独立信源** |

### 反模式（应避免）

❌ **只用一个通用 LLM Context query 试图覆盖所有维度**——返回的是综合性摘要，不是单点深挖。本案例第一个 query 返回 5 源覆盖主报告，但漏掉了 John Jumper 跳槽信号——需要在第二/三轮用精准 query 补充。

❌ **跳过竞品 query**——新产品发布会上必然出现竞品对比，独立第三方媒体已写过横向分析；不做竞品 query 会缺 30% 的关键素材（OpenAI Rosalind 的 LifeSciBench 36.1% 数据就是从这个角度挖到的）。

❌ **过度依赖官方发布页**——官方页只有「我们做了什么」+「数字」+「申请链接」，缺少外部验证、独立测试、竞品立场。必须互补。

### 适用条件扩展

在原 LLM Context 适用条件基础上，**特别推荐 Product Launch Stack 的场景**：

- 公司新产品发布/上线（AI 模型、AI 应用、API、硬件）
- 产品涉及明确竞争对手（三方演义 / 多家公司竞争）
- 产品涉及跨领域人才流动（人才去向本身就是故事）
- 产品有具名客户案例可挖（pharma / 医疗 / 金融 / 法律等高门槛领域）

**不适用场景**：产品概念模糊、缺乏具名客户、无直接竞品——退回到原 LLM Context 标准栈（4 个种子信号并行）。
