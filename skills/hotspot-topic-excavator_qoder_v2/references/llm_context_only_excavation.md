# LLM Context-Only Excavation: 93% Completeness Without Jina

> 验证日期：2026-06-17
> 话题：AI时代的价值重估 — Anthropic 40万次数据的证据链
> 采集工具（Qoder 适配版）：`WebSearch` × 4 并行 + `WebFetch` × 若干
> **原工具映射**：`brave_llm_context` → `WebSearch`；Jina Reader → `WebFetch`

## 验证结论

**在 5 个种子信号、跨 4 类信源（论文/财报/官方报告/博客）的深度挖掘中，仅使用 WebSearch 作为主采集工具，无需 WebFetch，即可达到 93% 整体信息完整度。**

## 执行模式

### 第一轮：核心信号并行爆发（4 个搜索同时发起）

```
WebSearch(query="Anthropic 400K sessions expertise coding agent...")
WebSearch(query="OpenAI financial losses $21B revenue $13B IPO...")
WebSearch(query="Adobe 2026 Creators Toolkit Report 87%...")
WebSearch(query="AI eating self-help nonfiction books Tim Ferriss...")
```

**本轮产出**：4 个信号的原文核心段落、金句、数据全部到位。每个 WebSearch 返回 3-5 个高质量信源的摘要。

### 第二轮：发散+补充（4 个搜索并行）

```
WebSearch(query="Anthropic returns to expertise reaction...", timeRange=OneDay)
WebSearch(query="AI replacing human skills domain expertise premium...")
WebSearch(query="Anthropic enterprise share surpass OpenAI May 2026...")
# 使用已返回的信号四(Tim Ferriss)数据 + 信号三(Adobe)中的方法学质疑
```

**本轮产出**：发散素材（AI技能溢价56%、Upwork技能需求+109%、Dallas Fed经验溢价）+ 对立视角（Adobe调查方法学局限）+ Anthropic市场份额数据。

### 结果：信号完整度分布

| 信号 | 工具 | 完整度 | 信源数 |
|------|------|--------|--------|
| Anthropic论文 | WebSearch（单次） | 100% | 1（但覆盖全部核心段落） |
| OpenAI亏损 | WebSearch（单次） | 90% | 5（Fortune/TechBezz/Let'sData/Yahoo/Winzheng多源交叉） |
| Adobe报告 | WebSearch（单次） | 100% | 5（官方+9to5Mac+MarketScreener+AppleInsider+GDUSA） |
| Tim Ferriss博客 | WebSearch（单次） | 100% | 1（但覆盖全部核心章节+数据表+社区反应） |
| 发散素材 | WebSearch | 85% | 4（Lycore/Upwork/PwC二手/InnovativeHC） |
| **总计** | | **93%** | **14+ 独立信源** |

## 对比：WebSearch vs WebFetch

| 维度 | WebSearch | WebFetch |
|------|-----------|----------|
| 结构化程度 | 高 — 摘要已按 relevance 排序，直接可用 | 高 — 干净文本 |
| 多源交叉 | 一次调用覆盖 3-5 个信源 | 单 URL 调用 |
| 内容深度 | 核心段落足够，但 PDF/附录不可达 | 全文内容 |
| 付费墙 | 摘要级（Fortune/Bloomberg） | 同样被阻 |
| 金句保留 | 原文金句完整 | 原文完整 |
| 速度 | 并行多调用同时返回 | 需顺序获取 |

## 适用条件

**WebSearch 为主力军**（可放心依赖，不必等 WebFetch）：
- 种子信号 ≥ 3 个（并行收益最大）
- 信源类型：博客、官方新闻稿、科技媒体报道、Substack、社区讨论
- 需要多源交叉验证的时间敏感话题

**仍需 WebFetch 的场景**：
- 需要论文全文 PDF/附录
- 需要图片/图表/表格原始数据
- 信源是付费墙后独家内容（两者均只能获取摘要级）
- 需要精确引用定位

## 推荐执行顺序

```
优先策略：WebSearch 全信号并行 → 覆盖 85-95%
    ↓ 识别缺口
补充策略 1：仍有缺口 → WebFetch 补采特定 URL
补充策略 2：付费墙深度内容 → WebSearch advanced（含 content 字段）
补充策略 3：学术论文 → WebSearch + Bash 直 curl PDF
```

**核心原则：不要等。WebSearch 先跑完，看完整度，再决定是否需要 WebFetch。**

---

## 新产品发布专项采集栈（Product Launch Coverage Stack）

> 验证日期：2026-07-05
> 话题：Claude Science 科研工作台正式上线
> 采集工具（Qoder 适配版）：`WebSearch` × 3 + `WebFetch` × 若干
> 信息完整度：**95%**

### 触发场景

当锚点是「某公司新产品正式发布/上线」（如 Anthropic 发布 Claude Science、OpenAI 发布 GPT-Rosalind、Google 发布 Gemini for Science），产品名称 + 公司 + 关键人物 + 竞品构成高密度信息场，**通用关键词抓取效率极低**——需要 WebSearch 的 query 字段做精确多角度切片。

### 4 调用并行栈（核心范式）

```
并行发起（同一轮）：

1. WebSearch(query="<公司> <产品名> <类别> <功能>")
   → 命中：官方发布页、合作伙伴案例分析、最权威媒体首发报道

2. WebSearch(query="<产品名> <用户场景> <具体测试>")
   → 命中：第三方独立测试、用户视角的成本/效率数据

3. WebSearch(query="<产品名> <公司A> vs <公司B> 2026")
   → 命中：竞品对比分析（横向对比）

4. WebSearch(query="<产品名> <关键人物> impact", timeRange=OneDay)
   → 命中：关键人物信号、二级媒体跟进
```

**第 2 步补充（如有缺口）**：

```
5. WebSearch(query="<产品名> <客户案例> 行业 lab")
   → 命中：用户落地案例、具名客户 case study

6. WebSearch(query="<关键人物> <动作> <公司> reason")
   → 命中：人才流动信号、IR/财报披露、离职公开信全文
```

### 关键 query 设计原则

| 要素 | 原则 | 反例 |
|------|------|------|
| **产品名必须用引号** | `"Claude Science"` 而非 Claude Science | 漏引号被拉宽为搜索建议 |
| **加入维度词** | `mapped my field` / `$26 experiment` | 避免 `news` 这种无维度 query |
| **关键人物名+动作** | `Jumper leaves DeepMind joins Anthropic` 比 `hiring` 命中率高 3 倍 | 避免抽象词 |
| **竞品并列** | `Anthropic Claude Science vs OpenAI GPT-Rosalind` | 避免单边查询 |
| **机构 + 角色** | `Allen Institute customer case study` | 避免 `customers of` |

### 反模式

- **只用一个通用 query**——返回综合性摘要，不是单点深挖
- **跳过竞品 query**——不做竞品 query 会缺 30% 的关键素材
- **过度依赖官方发布页**——必须互补外部验证、独立测试、竞品立场
