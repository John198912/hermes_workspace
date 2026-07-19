# 热点主题素材深挖报告

> **话题**：Schema Harness 在 ARC-AGI-3 公开集上取得约 99% — "不改模型改框架"的新范式
> **日期**：2026-07-17
> **配置**：深挖70%/发散30%
> **信源完整度**：88%

---

## ⚠️ 真伪验证 · 事实校准

> 用户提供了预消化摘要，以下为逐项交叉验证结果。

| 验证项 | 用户版本 | 实际（多源确认） | 差异说明 |
|--------|---------|-----------------|---------|
| **主体名称** | Schema 框架 | Schema Harness（Schema-harness.github.io 官方发布） | ✅ 一致。由 Impossible Research 团队开发，Naval Ravikant 旗下 |
| **99% RHAE** | 99% | 官方表述 "~99%"，精确值为 **98.98%**（Opus 4.8 + Fable 5） | ✅ 一致。需标注为"~99%"而非精确 100% |
| **此前最强模型 7.78%** | 7.78% | GPT-5.6 Sol max 在 **Semi-private 集**上的官方最高分 7.78%；Public 集官方最高 13.33% | ⚠️ **需区分 Public vs Semi-private**：7.78% 是 Semi-private 集分数，Public 集为 13.33%。Schema 的 99% 仅在 Public 集上测量 |
| **不修改模型权重** | 不修改模型权重 | ✅ 正确。Schema 是 harness（框架），不修改底层模型 | ✅ 一致 |
| **将观测转化为可编辑程序** | 将观测转化为可编辑程序 | 更精确：三个核心约束——①将世界模型编码为可运行的 step() 程序 ②用 run_backtest 对完整历史记录验证 ③仅通过 commit_actions 发送动作 | ⚠️ 用户表述为简化版，技术细节更丰富 |
| **$20K 计算预算** | 未提及 | Schema 未公布成本。对比参考：Continual Harness $774/20.54%；Hermes 基线 $5,674/8.25% | ⚠️ 成本信息缺失，需标注 |
| **证明状态** | "ARC-AGI-3 测试被突破" | 98.98% 和 95.35% 是 **自报结果**，**未经 ARC Prize 独立验证** | ⚠️ **需强调**：Self-reported，未独立验证 |

---

## Layer 1 ｜ 素材包

### 1. 热点资讯流

| # | 信息 | 来源 | 时效 | 层级 |
|---|------|------|------|------|
| 1 | Impossible Research 发布 Schema Harness，在 ARC-AGI-3 Public 集上 Opus 4.8 + Fable 5 达 98.98%，GPT-5.6 Sol 达 95.35% | schema-harness.github.io / X | 7/16-17 | 🔴 |
| 2 | Haven Feng 描述 Schema 为让 LLM "像物理学家一样思考"的方式 | X 推文 | 7/16-17 | 🔴 |
| 3 | Naval Ravikant 称 Schema 是他的 Impossible Research 团队工具，能玩游戏、写代码、"饱和"基准 | X 推文 / Digg | 7/16-17 | 🔴 |
| 4 | Wenjie Ma 解释系统从经验构建程序化世界模型、对历史验证、在模型中搜索解 | X 推文 / Digg | 7/16-17 | 🔴 |
| 5 | HN 讨论帖 #48935905 热议：公开集 99% vs 私有集未知、是否算"gaming benchmark" | HN | 7/17 | 🔴 |
| 6 | Reddit r/accelerate 讨论："The harness seems to benchmaxx specific problems" | Reddit | 7/17 | 🔴 |
| 7 | ARC Prize 官方规则：官方排行榜仅接受通过 API 调用、使用统一系统提示的模型结果，**不接受定制 harness 方案** | datalearner.com | 持续 | 🟡 |
| 8 | ARC-AGI-3 基准历史：3 月发布时最强 0.51%（Semi-private）→ 7 月 Sol max 达 7.78%（Semi-private）/ 13.33%（Public） | arcprize.org | 持续 | 🟡 |
| 9 | Symbolica 的 Agentica 框架 3 月首日取得 36.08%（Public）—— 此前"harness 突破"先例 | 智源社区/新智元 | 3/28 | 🟡 |
| 10 | Continual Harness 20.54%（Public），成本仅 $774（Seth Karten, Princeton） | Seth Karten X / Substack | 7/14 | 🟡 |
| 11 | François Chollet 此前认为 ARC-AGI-6/7 将是"最后的测试"——LLM 能否通过仍需观察 | Reddit r/singularity | 持续 | 🟡 |

### 2. 硬核事实

| # | 事实 | 数据 | 来源(P1/P2/P3) | 层级 |
|---|------|------|----------------|------|
| 1 | Schema 在 Public 集上 Opus 4.8 + Fable 5 达 98.98%，GPT-5.6 Sol 达 95.35% | 98.98% / 95.35% | P1 | 🔴 |
| 2 | 受控对比：同模型 Opus + Fable，Claude Code baseline 42.83% → Schema 98.98%（+56.15pp） | +56.15pp | P1 | 🔴 |
| 3 | GPT-5.6 Sol 官方基准：Sol max Public 13.33%，Semi-private 7.78% | 13.33% / 7.78% | P1 | 🔴 |
| 4 | Schema 三个核心约束：①step() 程序化世界模型 ②run_backtest 对完整历史验证 ③commit_actions + 预测错误立即丢弃 | 架构约束 | P1 | 🔴 |
| 5 | RHAE 指标：(人类动作数 ÷ Agent 动作数)²，上限 1.15，后关卡权重递增 | 评分公式 | P1 | 🔴 |
| 6 | 关键案例：M0R0 Level 4，Agent 用 42 个动作，人类用 500 个动作（12 倍效率） | 42 vs 500 | P1 | 🔴 |
| 7 | 关键案例：RE86 的 393/393 全精确验证后，61 步一次性计划清关 | 393/393 exact | P1 | 🔴 |
| 8 | Schema 分数是自报结果（Self-reported），**未经 ARC Prize 独立验证** | 验证状态 | P1 | 🔴 |
| 9 | Schema 仅在 Public 25 个游戏上测量，未在 Semi-private 集上验证 | 25 public games | P1 | 🔴 |
| 10 | ARC Prize 官方排行榜**不接受定制 harness 方案** | 规则限制 | P2 | 🔴 |
| 11 | ARC-AGI-3 3 月发布时：最强模型 Semi-private 0.51%，所有前沿模型得 0 | arcprize.org | P1 | 🟡 |
| 12 | Symbolica Agentica 3 月首日 36.08%（Public），通关 113/182 关卡 | 36.08% / 113/182 | P2 | 🟡 |
| 13 | Continual Harness 20.54%（Public），成本 $774，超过 Hermes 基线 8.25%/$5,674 | 20.54% / $774 | P2 | 🟡 |
| 14 | Schema 使用 Fable 5 作为 fallback——低于 80 分的游戏用 Fable 5 重跑 | 模型切换策略 | P1 | 🔴 |

### 3. 权威引述

| # | 引述（英文原文） | 中译 | 来源 | 层级 |
|---|----------------|------|------|------|
| 1 | "The agent must act while its model of the game is still provisional, forming hypotheses about what the grid represents, how actions change it, and what counts as success, then revising both its model and its plan as new observations arrive." | 「智能体必须在游戏模型仍然临时时行动，对网格代表什么、动作如何改变它、什么算作成功形成假设，然后随着新观察修正模型和计划。」 | Schema Harness 官方（描述 ARC-AGI-3 的挑战） | 🔴 |
| 2 | "The physicist's way" — Schema 让 LLM "像物理学家一样思考" | 物理学家的方式 | Haven Feng X 推文 | 🔴 |
| 3 | "How you use the model matters a lot." | 「你如何使用模型非常重要。」 | Schema Harness 官方（核心论点） | 🔴 |
| 4 | "A general mechanism is not one that never changes. It is one whose revisions preserve earlier explanatory machinery and compress the cost of new levels." | 「一个好的通用机制不是永远不会改变的那个，而是其修正保留了先前的解释机制并压缩了新关卡的成本。」 | Schema Harness 官方 | 🔴 |
| 5 | "Our self-reported 98.98% continues this trajectory rather than breaking from it." | 「我们自报的 98.98% 是延续了这一轨迹，而非突破了它。」 | Schema Harness 官方（谨慎表述） | 🔴 |
| 6 | HN 评论: "Systems that can score ~90% on the public sets of the previous ARC's can comfortably reach 70-80% on the corresponding private test sets" | 「在之前 ARC 的公开集上能拿到约 90% 的系统，在对应的私有测试集上可以轻松达到 70-80%」 | HN 用户（支持公开集分数有意义） | 🔴 |
| 7 | HN 评论: "The harness seems to benchmaxx specific problems" | 「这个框架似乎是在 benchmaxxing 特定问题（即针对公开集过拟合）」 | Reddit r/accelerate | 🔴 |
| 8 | "This is genuinely one of the most interesting AI projects I've seen in a long time. The idea of forcing LLMs to build and verify executable world models instead of just predicting tokens is incredibly exciting." | 「这是我长期以来见过的最有趣的 AI 项目之一。强迫 LLM 构建和验证可执行的世界模型而不只是预测 token，这个想法令人难以置信地兴奋。」 | @Eli_802 on X | 🟡 |
| 9 | Naval Ravikant: Schema is a tool from his team at Impossible Research that can play games, write code and "saturate" the benchmark | Schema 是他的团队在 Impossible Research 的工具，能玩游戏、写代码并"饱和"基准 | Naval Ravikant X / Digg | 🟡 |

### 4. 案例故事

| # | 案例 | 时间 | 人物 | 冲突 | 结果 | 来源 |
|---|------|------|------|------|------|------|
| 1 | Schema Harness 在 ARC-AGI-3 Public 集达 98.98% | 2026/7/16-17 | Impossible Research (Haven Feng, Wenjie Ma 等) | 此前最强模型仅 7.78%（Semi-private） | 自报 99%，未经独立验证 | Schema 官网 / X |
| 2 | Agentica 框架首日 36.08% | 2026/3/27-28 | Symbolica | ARC-AGI-3 发布时所有前沿模型得 0 | 首日突破 36%，通关 113/182 关卡 | 智源社区/新智元 |
| 3 | Continual Harness 20.54% 仅花 $774 | 2026/7/14 | Seth Karten (Princeton PhD) | Hermes 基线 $5,674 仅得 8.25% | 效率超越 7 倍成本 | Seth Karten X |
| 4 | ARC-AGI-3 发布时全模型得 0 | 2026/3/25 | François Chollet + ARC Prize | 所有前沿模型在新交互基准上得 0 | 人类满分，AI 惨败 | arcprize.org |
| 5 | Claude Opus 4.8 ARC-AGI-3 达 1.5% | 2026/7 | Anthropic | 此前所有模型 <1% | 首次单模型超过 1%（但仍远低于人类） | MindStudio |
| 6 | Schema 的 M0R0 案例：42 vs 500 动作 | 2026/7/16-17 | Schema + Opus 4.8 | 人类 500 动作的最难关 | Agent 用 42 动作通关（12 倍效率） | Schema 官网 |
| 7 | Schema 的 KA59 案例：杀死"epicycle"规则 | 2026/7/16-17 | Schema + Opus 4.8 | 两条完整运行记录有相同的成本模式 | Agent 用完整历史证据否定了一个巧合性的"规则" | Schema 官网 |

### 5. 对立张力

| # | 争议点 | 正方观点 | 反方观点 | 来源 |
|---|--------|---------|---------|------|
| 1 | **公开集 99% 是否代表 ARC-AGI-3 被"突破"？** | 公开集高分有意义——"之前 ARC 公开集 90% 的系统在私有集 70-80%" | 公开集仅 25 个游戏，可能"benchmaxx"特定问题；Semi-private 集分数未知 | HN vs Reddit |
| 2 | **Schema 是"harness"还是"benchmark gaming"？** | 不改模型权重，仅改框架，证明"如何使用模型很重要" | ARC Prize 官方明确不接受定制 harness 方案——评测目标是"模型自身通用智能" | Schema 团队 vs ARC Prize 规则 |
| 3 | **99% 是否真的意味着 AI 推理突破？** | 世界模型 + 验证 + 搜索 = 一种新的推理范式 | 这只是"scaffolding"——模型本身的推理能力没有提升 | 社区讨论 |
| 4 | **"物理学家方式"是否被夸大？** | Schema 要求模型形成假设、验证、修正——确实是科学方法 | 这更像是"程序化建模"而非"物理直觉"——LLM 并不理解物理 | Haven Feng 描述 vs 社区质疑 |
| 5 | **公开集 vs 私有集的可迁移性** | Schema 自报 98.98%，且声称延续轨迹而非突破 | "98.98% public maps to Semi-private is unknown until measured"——Schema 自己也承认不确定 | Schema 官网（诚实表述） |
| 6 | **成本与效率** | 未公布成本，但同类 harness（Continual Harness $774 达 20.54%）已很高效 | "不改模型改框架"的隐含成本——可能仍然很高 | 社区讨论 |

### 6. 可视化依据

| # | 图表内容 | 原始数据 | 数据出处 |
|---|---------|---------|---------|
| 1 | ARC-AGI-3 成绩进化时间线：3 月 0.51% → Agentica 36% → Sol max 13.33%(Public) / 7.78%(Semi-private) → Schema 98.98%(Public) | 分数序列 | arcprize.org + 各团队 |
| 2 | Schema 核心架构三约束图：step() 程序 → run_backtest 验证 → commit_actions | 概念图 | Schema 官网 |
| 3 | 受控对比柱状图：Claude Code 42.83% vs Schema 98.98%（同模型，仅换框架） | +56.15pp | Schema 官网 |
| 4 | RHAE 评分公式图解：(人类动作/AI动作)²，后关卡权重递增 | 公式可视化 | arcprize.org |
| 5 | M0R0 Level 4 效率对比：42 动作（Agent）vs 500 动作（人类） | 12 倍效率 | Schema 官网 |

### 图片素材方案

| 类型 | 内容 | 来源/链接 | 授权类型 |
|------|------|----------|---------|
| 1. 文章内可用配图 | ARC-AGI-3 交互式游戏界面截图 | arcprize.org | 需联系授权 |
| 2. 可下载图源 | Schema Harness 官网的性能对比图表（Figure 4, 5） | schema-harness.github.io | 需联系授权 |
| 3. AI 绘图 prompt 概要 | ① "A physicist-like AI agent exploring a mysterious 64x64 pixel grid world, building executable program models, digital art" ② "64x64 colorful grid with hidden rules being decoded by an AI agent, showing hypothesis-verification-revision cycle" ③ "Side by side: a human spending 500 actions vs AI spending 42 actions on the same puzzle level" | N/A | AI 生成 |

---

## Layer 2 ｜ 文章/视频大纲 + 素材填充

### RIVET 结构

**R · 场景爆破（Rupture）**
- 钩子：「一个被设计来让 AI 得零分的考试，在发布 4 个月后就被一个'不改模型只改框架'的工具考了 99 分。但这个 99 分，可能什么都说明不了。」
- 反常识：ARC-AGI-3 被设计为"AI 最难考试"——3 月发布时所有前沿模型得 0，Chollet 说这将测试"真正的智能"。但一个来自 Naval Ravikant 旗下公司的框架，在公开集上拿到了接近满分。**问题是：这算"突破"还是"作弊"？**
- 情绪弧线：震惊 → 好奇 → 怀疑 → 深度理解

**I · 照亮盲区（Illuminate）**
- 核心论证：Schema 的真正价值不在 99% 这个数字——**在于它证明了一个反直觉的事实：同一个模型，换个框架可以从 42% 跳到 99%。** 这意味着 AI 能力的瓶颈可能不在模型本身，而在我们如何使用模型。
- Schema 的三个核心约束不是"更强的 AI"——而是更聪明的"使用方式"：
  1. 强制模型把信念写成**可运行代码**（而非隐藏在上下文中的模糊推理）
  2. 对**完整历史记录**验证每一条规则（而非凭记忆做判断）
  3. 预测错误时**立即丢弃计划**（而非在错误路径上越走越远）
- 这与 ARC Prize 官方规则的冲突：ARC Prize 明确不接受定制 harness 方案，因为评测目标是"模型自身的通用智能"。Schema 恰好挑战了这个定义——什么是"模型自身的智能"？
- "物理学家方式"的本质：不是 AI 有了物理直觉，而是框架强制 AI 按照**假设 → 实验 → 验证 → 修正**的科学方法论行动。

**V · 验证处境（Validate）**
- 数据支撑：
  - ARC-AGI-3 3 月发布：最强模型 Semi-private 0.51%，Public 集所有模型 <1%
  - Agentica 3 月首日 36.08%（Public）—— harness 突破先例
  - GPT-5.6 Sol max 7 月达 13.33%（Public）/ 7.78%（Semi-private）—— 官方最高分
  - Continual Harness 20.54%（Public），仅 $774
  - Schema 受控对比：同模型 Claude Code 42.83% → Schema 98.98%（+56.15pp）
  - M0R0 Level 4：Agent 42 动作 vs 人类 500 动作
  - RE86：393/393 全精确验证，61 步一次性计划清关
- ARC Prize 规则明确不接受定制 harness——99% 不在官方排行榜上
- Schema 自报结果，未经 ARC Prize 独立验证

**E · 具身化（Embody）**
- 核心隐喻：**「不是换引擎，是换驾驶员」**——同一辆车（模型），不同的驾驶员（框架/harness），可以从业余车手变成 F1 世界冠军。Schema 证明的是"驾驶技术"的价值，而非"引擎"的突破。
- 辅助隐喻：**「物理学家的实验室笔记本」**——Schema 要求模型像物理学家一样工作：先写假设（世界模型），再用实验数据验证（run_backtest），然后才敢下结论（commit_actions）。普通 LLM 就像一个不做实验就写论文的学生——看起来聪明，但结论不可靠。
- 跨领域迁移：「框架 > 模型」的模式不限于 AI 基准——在任何知识工作中，你的产出质量不只取决于你用的工具，更取决于你如何组织工作流。Cursor + 好的工作流 > 更好的模型 + 差的工作流。

**T · 转化行动（Transform）**
- 行动建议（面向超级个体 / AI 实践者）：

**A. 工具链级自检表**

| 工具/场景 | 检查什么 | 为什么 |
|-----------|---------|--------|
| Cursor / Claude Code | 是否强制 AI 写出可验证的中间产物 | Schema 证明：强制程序化 > 隐式推理 |
| Dify / Coze / n8n | 是否有"预测错误立即丢弃"机制 | Schema 的 commit_actions 核心：错了就重来 |
| ChatGPT / Claude 做分析 | 是否要求 AI 对历史数据做完整验证 | run_backtest 思维：不要凭记忆做判断 |
| AI 辅助编程 | 是否有可运行的测试用例作为"世界模型" | Schema 的 step() 程序就是可运行的世界模型 |
| 个人 AI 工作流 | 框架和 prompt 设计 vs 选更好的模型 | Schema 证明同模型换框架可提升 56pp |
| API Key 管理 | 监控 harness 调用成本 | 框架虽不改模型，但多次调用成本不低 |
| AI 评估基准 | 区分"模型能力"和"框架能力" | ARC Prize 不接受 harness 是有原因的 |
| 知识管理 | 建立"假设 → 验证 → 修正"的工作流 | Schema 的"物理学家方式"可直接迁移 |

**B. 通用 5 步行动清单**
1. **先优化框架，再升级模型**：Schema 证明同一个模型换个框架可以从 42% 跳到 99%。在你花更多钱升级模型之前，先看看你的工作流是否拖了后腿。
2. **强制可验证性**：学 Schema 的三个约束——要求 AI 把推理写成可运行/可验证的形式，而非接受"看起来对"的回答。
3. **理解"模型能力"和"框架能力"的区别**：当你看到"AI 突破"的新闻时，问一句——是模型变强了，还是有人找到了更好的使用方式？
4. **对基准测试保持批判**：99% Public 不等于"AI 已经通用智能"。Schema 自己都说"在 Semi-private 上的表现未知"。
5. **投资"物理学家式"工作流**：假设 → 实验 → 验证 → 修正。这不只适用于 AI，适用于任何需要深度思考的知识工作。

---

## 校准审查记录表

| 步骤 | 类型 | 检查结果 | 修正动作 |
|------|------|---------|---------|
| A | 事实校准 | 7.78% 是 Semi-private 集而非 Public 集；Public 集官方最高为 13.33% | 报告全文区分 Public vs Semi-private |
| B | 事实补充 | 补充了 Agentica 36.08%（先例）、Continual Harness $774/20.54%、ARC Prize 官方不接受 harness 规则 | 已纳入 |
| C | 表述校准 | 避免"AI 突破 ARC-AGI-3"的过度表述；明确 Schema 是自报结果 | 全文标注 |
| D | 框架补充 | 补充"模型能力 vs 框架能力"的核心分析框架；补充 ARC Prize 规则冲突 | 纳入 I-Illuminate |
| E | 对立视角 | 纳入 HN "benchmaxx"质疑、ARC Prize 规则限制、Schema 自己的诚实表述 | 已纳入 |
| F | 理论偏向 | 使用了"物理学家方式"隐喻——标注来源为 Haven Feng 的描述，非预设理论 | 框架来源：Schema 团队 |
| G | 叙事引力 | 高引力话题："AI 突破最难考试"→ 引力方向："AGI 已经到来"。**反引力锚**：Schema 自报未验证；Public vs Semi-private 差异；ARC Prize 不接受 harness；"延续轨迹而非突破"（Schema 自己的表述） | 主线已平衡 |
| H | 受众工具链翻译 | T-Transform 段含 8 行工具链自检表 + 5 步行动清单 | ✅ |
| I | 三角叙事补洞 | 第三点：**Symbolica Agentica 3 月首日 36% 的中国视角报道**——证明"harness 赛道"已有多个参与者，不是 Schema 独占。中文受众共鸣：中国团队在 ARC-AGI 领域有参与（如 BAAI 的跟踪报道） | 已纳入 Agentica 线索 |

---

## 采集路径摘要

| # | 采集对象 | 路径类型 | 工具 | 备注 |
|---|---------|---------|------|------|
| 1 | Schema Harness 官网 | ✅ 主路径 | WebFetch | 完整获取（227 行） |
| 2 | HN 讨论 #48935905 | ⚠️ 降级 | WebFetch 429 限流 | 通过 Grep 摘要 + WebSearch 补充 |
| 3 | Reddit r/accelerate | ⚠️ 降级 | WebFetch 429 限流 | 通过 WebSearch 摘要补充 |
| 4 | Digg 讨论 | ✅ 主路径 | WebFetch | 完整获取 |
| 5 | ARC Prize 官网 | ✅ 主路径 | WebFetch | 完整获取 |
| 6 | ARC Prize 历史 | ✅ 主路径 | WebFetch | 完整获取 |
| 7 | MindStudio ARC-AGI-3 | ✅ 主路径 | WebFetch | 完整获取 |
| 8 | 智源社区 Agentica 报道 | ✅ 主路径 | WebFetch | 完整获取 |
| 9 | Seth Karten X/LinkedIn | ✅ 主路径 | WebSearch | 间接获取 |
| 10 | X 推文 (Haven Feng, Naval, Wenjie Ma) | ✅ 主路径 | WebSearch + Digg 转述 | 间接获取 |

> 本报告中降级路径触发次数：**2** 次（HN 和 Reddit 429 限流）

---

## 参考资料清单

| # | 标题 | URL | 来源类型 | 访问日期 |
|---|------|-----|---------|---------|
| 1 | Schema Harness 官方发布 | https://schema-harness.github.io/ | P1 | 2026-07-17 |
| 2 | HN Discussion #48935905 | https://news.ycombinator.com/item?id=48935905 | P3 | 2026-07-17 |
| 3 | Reddit r/accelerate | https://www.reddit.com/r/accelerate/comments/1uy8i3l/ | P3 | 2026-07-17 |
| 4 | Digg - Impossible Research Schema Harness | https://digg.com/ai/3a488ugi | P2 | 2026-07-17 |
| 5 | ARC Prize - ARC-AGI-3 | https://arcprize.org/arc-agi/3 | P1 | 2026-07-17 |
| 6 | ARC Prize - History | https://arcprize.org/history | P1 | 2026-07-17 |
| 7 | MindStudio - ARC AGI 3 frontier models score zero | https://www.mindstudio.ai/blog/arc-agi-3-results-frontier-models-score-zero | P2 | 2026-07-17 |
| 8 | MindStudio - What Is Arc AGI 3 | https://www.mindstudio.ai/blog/what-is-arc-agi-3-claude-opus-4-8-fluid-intelligence | P2 | 2026-07-17 |
| 9 | ARC-AGI-3 arXiv paper | https://arxiv.org/html/2603.24621v1 | P1 | 2026-07-17 |
| 10 | 智源社区 - Agentica 36.08% | https://hub.baai.ac.cn/view/53465 | P2 | 2026-07-17 |
| 11 | Seth Karten - Continual Harness | https://x.com/sethkarten | P2 | 2026-07-17 |
| 12 | François Chollet X - ARC-AGI-3 launch | https://x.com/fchollet/status/2036861192619384989 | P1 | 2026-07-17 |
| 13 | DataCamp - ARC-AGI-3 | https://www.datacamp.com/blog/arc-agi-3 | P2 | 2026-07-17 |
| 14 | datalearner - ARC-AGI-3 评测基准 | https://www.datalearner.com/blog/arc-agi-3-benchmark-launch-2026 | P2 | 2026-07-17 |
| 15 | LinkedIn - Xiuyu Li Schema 发布 | https://www.linkedin.com/posts/xiuyu-li-a804b2146 | P2 | 2026-07-17 |
| 16 | X - Zanette_ai "ARC-AGI-3 is an RL problem" | https://x.com/Zanette_ai/status/2077793189608775728 | P3 | 2026-07-17 |
| 17 | HN - ARC-AGI-3 harness 规则讨论 | https://news.ycombinator.com/item?id=47524273 | P3 | 2026-07-17 |

---

*报告由 hotspot-topic-excavator v2.7.5 生成 · 2026-07-17*
