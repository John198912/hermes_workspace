# 校准案例库 · 案例 3：OpenRouter 数据口径与时序错配

> **创建时间**：2026-07-05
> **触发话题**：中国 AI 模型 OpenRouter 九周领跑——美国份额 72%→33%
> **累计案例**：案例 1（认知投降·学术溯源）+ 案例 2（Forbes 10% vs The Next Web 11.7% 信心提升冲突）→ 本案例为案例 3

---

## 陷阱 A · 口径错配：「中国 AI 占 61%」与「72%→33%」混用

### 原始陷阱

2026 年 6 月的多篇媒体报道中，至少两个数字被同时引用：

| 数字 | 来源 | 真实口径 |
|------|------|---------|
| **「中国 AI 占 61%」** | KuCoin、CryptoBriefing、多个中文媒体 | **单一周（2026 年 2 月）+ Top 10 子样本** |
| **「美国份额 72%→33%」** | Yahoo Finance、Equipment Finance News、Dealroom | **OpenRouter 全平台 400+ 模型 + 同比对比** |

**结果**：如果不加区分，会把"61% 是某一小份样本的瞬时份额"误读为"全平台整体份额 61%"——前者是子集，后者是总体。**子集不能代表总体**。

### 为什么危险

- **量级放大**：61% > 33%，读者会以为"中国已经占多数"，与"美国仍占 1/3"的稳健口径冲突
- **错误归因**：单周数据可能是偶发峰值（如某热门模型发布周），不代表持续趋势
- **政策含义**：监管/投资判断会基于错误比例做出错误决策

### 修正动作

1. **数据并列展示**：报告中必须同时列出"61% 子样本"和"33%→52% 全平台"两个口径，明确各自身份
2. **明确标注子集属性**：61% 加注「单周 + Top 10 子样本」
3. **优先引用全平台数据**：72%→33% 同比是更稳健的口径，作为主数据；61% 仅作为"短期高峰"参考

### 验证信号

触发器：**TechTimes 5 月 29 日报道**——明确揭示 "The 61 percent figure traces to a single week in February 2026 and measures share among the top 10 most-used models — not across all 400-plus models on the platform."

---

## 陷阱 B · 时序错配：「连续 9 周」是周调用量第一，不是市场份额 9 周

### 原始陷阱

原日报标题：「中国 AI 模型连续九周全球领跑」——读者可能误读为"中国 AI 在 9 周内一直是市场份额第一"。

**真实含义**（Pandaily + 证券时报 + Dealroom 多源验证）：
- 9 周 = OpenRouter **周调用量（Token 数）**排名第一的连续周数
- 9 周 ≠ 市场份额 9 周（即不是"中国份额占多数 9 周"）
- 9 周 ≠ "排名第一模型固定不变"（实际上第一名的具体模型在 9 周内可能换过：DeepSeek V4 Flash 6 周 + MiMo/Kimi/GLM 等轮替）

### 为什么危险

- **量级错觉**：周调用量第一 ≠ 市场份额第一（OpenRouter 上 400+ 模型，Top 1 占总调用量比例仍可能 < 20%）
- **稳定性错觉**：连续 9 周第一 ≠ 中国模型整体稳定第一（单模型轮替意味着竞争激烈）
- **战略误判**："领跑"和"主导"是两回事，前者是指标，后者是结构

### 修正动作

1. **明确维度**：「连续 9 周全球第一」必须加注维度——「周 Token 调用量」
2. **区分领跑与主导**：报告/选题标题避免用「主导」「碾压」代替「领跑」「领先」
3. **补充结构数据**：如果能拿到 Top N 模型的具体分布（如 DeepSeek 占 17.6%、小米占 X% 等），可呈现"中国厂商整体领跑，但内部激烈竞争"的结构

### 验证信号

触发器：StockAlarm Pro 投资者分析文章明确区分「DeepSeek alone commands 17.6% of the platform, Chinese-origin companies hold 46% of identified」——单家公司 vs 整体是两个数字，不能合并。

---

## 陷阱 C · 身份混同：LongCat Owl Alpha ≠ 另一个模型 = LongCat-2.0 同一模型两阶段

### 原始陷阱

Meituan LongCat-2.0 在 OpenRouter 上以 "Owl Alpha" 匿名代号领跑 2 个月——如果不仔细查证，可能把 "Owl Alpha" 当作一个独立模型，与 "LongCat-2.0" 并列介绍。

### 修正动作

1. **明确身份关系**：报告中明确"Owl Alpha 是 Meituan LongCat-2.0 在 OpenRouter 上的匿名代号"
2. **时间线整合**：完整呈现"匿名 2 个月领跑（5-6 月）→ 7 月 4 日公开身份 = LongCat-2.0"的完整故事
3. **关键时点标注**：
   - 2026/4/24：DeepSeek V4 发布
   - 2026/5-6 月：Owl Alpha 在 OpenRouter 匿名领跑
   - 2026/7/4：Meituan 官方公开 LongCat-2.0 身份

### 验证信号

多源验证：
- Meituan LongCat X 官方账号（@Meituan_LongCat/status/2071783587205308721）
- Yahoo Tech："LongCat-2.0 stealth AI model" 报道
- VentureBeat：完整报道 LongCat-2.0 开源
- Reddit r/LocalLLaMA：社区确认 owl-alpha = LongCat-2.0

---

## 陷阱 D · 国产化栈边界：LongCat-2.0 "全程国产 AI ASIC 训练"的范围

### 原始陷阱

「美团 LongCat-2.0 全程用国产 AI 芯片训练」——这个表述是对的，但有边界：

- ✅ **正确**：LongCat-2.0 **训练 + 部署**都在国产 AI ASIC 上（Meituan 官方 X 确认）
- ✅ **正确**：这是"训练 + 推理"全栈国产化的里程碑
- ⚠️ **边界**：这里的"国产 AI ASIC"**主要指华为昇腾、寒武纪等**，而非 Nvidia 或 AMD
- ⚠️ **边界**：这个里程碑**仅适用于 LongCat-2.0 一个模型**，不能泛化为"中国所有 AI 模型都全栈国产化"
- ⚠️ **边界**：DeepSeek V4、Kimi K2、GLM-5.2、Qwen 等其他中国模型**仍部分依赖 Nvidia GPU**（受出口管制前的存量 + 部分国产芯片）

### 为什么危险

- **过度泛化**：把"LongCat-2.0 一个模型的成就"夸大为"中国整体 AI 全栈国产化"——会高估中国 AI 自主程度
- **政策含义**：可能影响对中国 AI 出口管制效果的判断

### 修正动作

1. **明确主体**：报告必须明确"国产 AI ASIC 训练 + 部署"是 **LongCat-2.0 一个模型**的成就
2. **区分"全栈国产"与"部分国产"**：DeepSeek V4 等仍部分依赖 Nvidia GPU 存量 + 国产芯片混合
3. **避免"中国 AI 全栈国产化"宏大叙事**：精准表达为"LongCat-2.0 实现单模型全栈国产化里程碑"

### 验证信号

- TestingCatalog X：确认 LongCat-2.0 "Both the full training run and the large-scale deployment are built entirely on AI ASIC superpods"
- AP News：Huawei chips 是中国国产 AI 芯片主力，Nvidia 中国市场"stall"是相对的
- DeepSeek 等其他中国模型仍依赖 Nvidia H100/H200 存量（公开训练文档）

---

## 综合教训：deep dive 必做的"数字溯源"清单

**当话题涉及具体百分比 / 排名 / "连续 N 周" 时，必须做以下溯源**：

| 检查项 | 触发条件 | 验证方式 |
|--------|---------|---------|
| **口径是什么？** | 任何百分比数据 | 全平台 vs 子样本？瞬时 vs 平均？ |
| **时间窗口是什么？** | "连续 N 周""一年内""最近"等模糊表述 | 精确到日期范围 |
| **主体是什么？** | "中国 AI""美国 AI"等整体概念 | 哪些公司/模型？数据来源？ |
| **是否有口径冲突？** | 多源数据差异大 | 并列展示 + 各自实验条件 |
| **是否混用子集与总体？** | 「占 X%」类表述 | 子集永远不能代表总体 |

---

*本案例累积至 references/calibration_case_openrouter.md · 由 hotspot-topic-excavator v2.4.0 校准模块生成 · 2026-07-05*