# 热点主题素材深挖报告

> **话题**：GPT-5.6 Sol Ultra 一小时内证明悬而未决 50 年的图论猜想 — AI 对数学实践的影响
> **日期**：2026-07-13
> **配置**：深挖70%/发散30%
> **信源完整度**：90%

---

## ⚠️ 真伪验证 · 事实校准

> 用户提供了预消化摘要，以下为逐项交叉验证结果。

| 验证项 | 用户版本 | 实际（多源确认） | 差异说明 |
|--------|---------|-----------------|---------|
| **证明对象** | 循环双覆盖猜想 | Cycle Double Cover Conjecture (CDC)，由 Szekeres (1973) 和 Seymour (1979) 独立提出 | ✅ 一致。补充：Tutte、Itai、Rodeh 也独立提出过 |
| **悬而未决时间** | 50 年 | 约 50 年（1973/1979 → 2026） | ✅ 一致 |
| **模型名称** | GPT-5.6 Sol Ultra | GPT-5.6 Sol Ultra（OpenAI 官方公告） | ✅ 一致 |
| **时间** | 不到一小时 | "just under one hour"（Ethan Knight 推文），prompt 设定 8 小时上限 | ✅ 一致。AI 在 1 小时内完成，远早于 8 小时上限 |
| **64 个并行子智能体** | 64 个并行子智能体+对抗智能体 | 64 concurrent subagents + adversarial agents（MLQ、The Decoder 多源确认） | ✅ 一致。对抗智能体是子智能体的一部分，负责寻找反例和错误 |
| **$20K 计算预算** | $20K 计算预算 | HN 社区估算：标准 Sol 定价 $275-$485；Cerebras 基础设施估算最高 $13,000 | ⚠️ **未找到 $20K 的原始出处**。社区估算范围 $275-$13,000，$20K 可能为含基础设施的粗略上限估算。报告中应标注为"估算值" |
| **证明状态** | 完整证明 | 未经同行评审的预印本，Thomas Bloom 初步验证"未发现错误" | ⚠️ **需强调**：尚未正式同行评审，CDC 猜想历史上有多次错误证明先例 |

---

## Layer 1 ｜ 素材包

### 1. 热点资讯流

| # | 信息 | 来源 | 时效 | 层级 |
|---|------|------|------|------|
| 1 | OpenAI 于 7/10 发布 GPT-5.6 Sol Ultra 生成的 CDC 猜想证明 PDF 及 prompt PDF | OpenAI CDN / Ethan Knight 推文 | 7/10 | 🔴 |
| 2 | 数学家 Thomas Bloom 初步评估：「非常好的证明」「短、初等、1980 年代就可能被发现」 | Thomas Bloom X 推文 | 7/11 | 🔴 |
| 3 | Bloom 批评证明未引用 1983 年 Bermond, Jackson, Jaeger 的奠基性论文 | Thomas Bloom X 推文 | 7/11 | 🔴 |
| 4 | MathOverflow 开设专题讨论帖「Purported proof of the cycle double cover conjecture」 | MathOverflow | 7/11 | 🔴 |
| 5 | HN 讨论帖获大量关注，社区讨论成本估算、Lean 形式化可行性 | HN #48863490 | 7/12 | 🔴 |
| 6 | 陶哲轩 5/1 在斯坦福 Future of Mathematics 研讨会发表主题演讲「New Mathematical Workflows」 | Stanford Events | 5/1 | 🟡 |
| 7 | Quanta Magazine 6/8 长文《How Terry Tao Became an Evangelist for AI in Math》 | Quanta Magazine | 6/8 | 🟡 |
| 8 | Quanta Magazine 4/13《The AI Revolution in Math Has Arrived》 | Quanta Magazine | 4/13 | 🟡 |
| 9 | OpenAI 5/20 用通用推理模型推翻了 Erdős 1946 年平面单位距离猜想 | OpenAI / Forbes | 5/20 | 🟡 |
| 10 | Jeremy Avigad 3/3 发表 arXiv 论文《Mathematicians in the Age of AI》 | arXiv | 3/3 | 🟡 |
| 11 | 陶哲轩 6/23 在 IEANTN 项目中发现 AI 形式化证明速度突破临界点 | 智源社区/量子位 | 6/23 | 🟡 |
| 12 | 陶哲轩 3/29 博客《Mathematical methods and human thought in the age of AI》 | terrytao.wordpress.com | 3/29 | 🟡 |

### 2. 硬核事实

| # | 事实 | 数据 | 来源(P1/P2/P3) | 层级 |
|---|------|------|----------------|------|
| 1 | CDC 猜想：每个无桥无向图都存在一组环，使得每条边恰好出现在两个环中 | 图论基本概念 | P1 | 🔴 |
| 2 | 证明方法：归约到三次图 → 利用 8-flow 定理 → GF(3) 上线性代数构造边标记 | 代数图论 + 线性代数 | P1 | 🔴 |
| 3 | Prompt 设计：禁止互联网搜索、禁止回答"猜想未解决"、对抗智能体检查错误、64 子智能体互相不知情 | 工程化 prompt | P1 | 🔴 |
| 4 | Bloom：证明「短、初等、不需要新理论，巧妙组合已知工具」 | 定性评估 | P2 | 🔴 |
| 5 | Bloom：关键步骤涉及「小的、反直觉的推理转折」——人类会放弃，AI 不会气馁 | 机器坚持 vs 人类放弃 | P2 | 🔴 |
| 6 | 证明未引用 1983 年 Bermond, Jackson, Jaeger 的奠基性论文 | 引用缺失 | P2 | 🔴 |
| 7 | CDC 猜想历史有多次声称证明后被发现有缺陷或被撤回的记录 | 历史背景 | P2 | 🔴 |
| 8 | 证明未在 Lean 或其他证明助手中形式化验证 | 形式化状态 | P2/P3 | 🔴 |
| 9 | HN 社区成本估算：标准 Sol 定价约 $275-$485；Cerebras 最高 ~$13,000 | 成本范围 | P3 | 🔴 |
| 10 | 2025 夏：多个 AI 模型在 IMO 6 题中解出 5 题 | IMO 2025 | P2 | 🟡 |
| 11 | 2026/2 First Proof 挑战赛：10 道研究级题目，AI 解出超过一半 | >5/10 | P2 | 🟡 |
| 12 | OpenAI 5/20 推翻 Erdős 1946 平面单位距离猜想（反例构造，非证明） | 反例 | P1/P2 | 🟡 |
| 13 | 陶哲轩 IEANTN 项目：AI 几小时完成过去志愿者需数周的形式化任务 | 数周→数小时 | P1 | 🟡 |
| 14 | 陶哲轩发现 AI 清晰边界：擅长局部 code golf，无法自发全局重构 | 局部 vs 全局 | P1 | 🟡 |

### 3. 权威引述

| # | 引述（英文原文） | 中译 | 来源 | 层级 |
|---|----------------|------|------|------|
| 1 | "One can imagine trying the natural labelling first, checking the linear algebra, and when that failed shrugging and thinking 'oh well, I was expecting to fail' — while the AI does not get discouraged and keeps trying small variations." | 「你可以想象先尝试自然的标记方法，失败后耸耸肩想'看来不能这么简单做到'——而 AI 不会气馁，持续尝试小的变体。」 | Thomas Bloom | 🔴 |
| 2 | "This is a frequent issue with AI-generated proofs and papers: they use ideas and proof strategies taken from the literature without proper citation." | 「这是 AI 生成的证明和论文的常见问题：它们使用了文献中的思想和证明策略，却没有正确引用。」 | Thomas Bloom | 🔴 |
| 3 | "In this strange new world where big AI companies are spending a lot of time and money attacking many open problems at once (and only reporting the successes, of course), we will soon find out more of what was within our reach all along." | 「在这个奇怪的新世界里，大型 AI 公司花费大量时间和金钱同时攻击许多开放问题（当然只报告成功），我们很快就会发现更多一直就在我们触手可及之处的东西。」 | Thomas Bloom | 🔴 |
| 4 | "The correct metric is not so much whether the proof has been generated or whether it has been verified, but whether someone can give a talk about it and take questions." | 「正确的指标不在于证明是否已生成或验证，而在于是否有人能就此做一场报告并回答提问。」 | 陶哲轩（斯坦福） | 🔴 |
| 5 | "2025 was the year when AI really started being useful for many different tasks." | 「2025 年是 AI 真正开始在许多不同任务中变得有用的一年。」 | 陶哲轩（Quanta） | 🟡 |
| 6 | "With these tools you can solve thousands of problems at once and start doing statistical studies." | 「有了这些工具，你可以同时解决数千个问题，开始做统计研究。」 | 陶哲轩（Quanta） | 🟡 |
| 7 | "Maybe we can outsource thinking in the next few years, but understanding is something that you cannot outsource. You have to do the understanding for yourself." | 「也许未来几年我们可以外包思考，但理解是你无法外包的。你必须自己去理解。」 | Sébastien Bubeck (OpenAI) | 🟡 |
| 8 | "It's very likely that this technology is bigger than the computer." | 「这项技术很可能比计算机更重大。」 | Daniel Litt (多伦多大学) | 🟡 |
| 9 | "If you look at what AlphaEvolve was thinking, I was super surprised. If it was a human, it would be an extremely creative human." | 「如果你看看 AlphaEvolve 在想什么，我会超级惊讶。如果它是人类，那将是一个极具创造力的人。」 | Jordan Ellenberg | 🟡 |
| 10 | "数学的本质，不是积累正确证明的数量，是让人类理解这个世界为什么是这样运行的。" | 同上 | 陶哲轩（斯坦福） | 🔴 |
| 11 | "AI 可以在技术层面解决显性目标，给出一个逻辑上正确的证明。但它生成的证明不引用已有文献，不突出核心思想，不启发后续研究，不帮任何人变得更聪明。" | 同上 | 陶哲轩（斯坦福/新智元转述） | 🔴 |
| 12 | "Both were major open problems that turned out to be much easier than expected — no big new theories were required." | 「这两个主要开放问题最终比预期容易得多——不需要重大的新理论。」 | Thomas Bloom | 🔴 |

### 4. 案例故事

| # | 案例 | 时间 | 人物 | 冲突 | 结果 | 来源 |
|---|------|------|------|------|------|------|
| 1 | GPT-5.6 Sol Ultra 证明 CDC 猜想 | 2026/7/10 | OpenAI GPT-5.6 Sol Ultra | 50 年未解 vs 1 小时解决 | 生成完整证明，等待社区验证 | OpenAI / Bloom |
| 2 | 陶哲轩用 AI 编码代理移植 27 年前 Java 代码 | 2026/7/11 | 陶哲轩 | 27 年代码中的隐藏 bug | 数小时完成移植，发现 2 个隐藏 bug | HN 399pts |
| 3 | 陶哲轩 PFR 猜想形式化项目 | 2023/11 | 陶哲轩 + 全球志愿者 | 将刚证明的定理在 Lean 中形式化 | 1 天内全球响应，数周完成 | Quanta |
| 4 | 陶哲轩 Equational Theories 项目 | 2024/9 | 陶哲轩 + 志愿者 | 2200 万个逻辑蕴含需检查 | 缩至 238 个，发现新数学构造 | Quanta |
| 5 | Ernest Ryu 用 ChatGPT 证明 Nesterov 42 年猜想 | 2025/10 | Ernest Ryu | 42 年未解决的收敛性问题 | 3 天累计 12 小时完成，后加入 OpenAI | Quanta |
| 6 | AlphaEvolve 发现 Bruhat 区间超立方体结构 | 2025/10 | Ellenberg 等 5 位数学家 | AI 寻找 d-不变量最大值 | 发现 50 年未见的超立方体结构 | Quanta |
| 7 | OpenAI 推翻 Erdős 平面单位距离猜想 | 2026/5/20 | OpenAI 通用推理模型 | 80 年来主流猜想 | AI 构造反例推翻（非证明） | OpenAI / Forbes |
| 8 | 陶哲轩 IEANTN 项目 AI 形式化临界点 | 2026/6 | 陶哲轩 | AI 生成速度远超人类消化速度 | Issue 队列清空，但证明太臃肿 | 陶哲轩 Mathstodon |

### 5. 对立张力

| # | 争议点 | 正方观点 | 反方观点 | 来源 |
|---|--------|---------|---------|------|
| 1 | AI 证明是否算"真正的"数学发现？ | 里程碑——AI 独立解决了 Wikipedia 未解列表上的猜想 | 证明「初等」「1980 年代就可能被发现」，AI 只是更有耐心 | Bloom vs OpenAI |
| 2 | AI 证明的引用缺失 | Prompt 禁止搜索互联网 | 使用了文献策略却不引用——AI 生成数学的系统性问题 | Bloom |
| 3 | 证明的"理解"价值 | 技术上正确的证明就是进步 | 陶哲轩：「理解没有增长一毫米」——显性目标与隐性目标被解耦 | 陶哲轩 |
| 4 | AI 是"发现"还是"重组"？ | AlphaEvolve 发现了人类 50 年未见的结构 | Bloom 倾向认为 AI「仅仅」重组已有知识 | Ellenberg vs Bloom |
| 5 | 选择偏差 | AI 公司投入大量资源攻击多个开放问题 | 「当然只报告成功」——看不到失败的海洋 | Bloom |
| 6 | 形式化验证的紧迫性 | 需要 Lean 等工具机械化验证 | 图论形式化库不够成熟，短期无法自动化验证 | HN |
| 7 | 数学的未来形态 | 数学家将成为"证明工程架构师" | Venkatesh：「文化中有宝贵的东西应该保留」 | 斯坦福研讨会 |

### 6. 可视化依据

| # | 图表内容 | 原始数据 | 数据出处 |
|---|---------|---------|---------|
| 1 | AI 数学证明时间线：2024 IMO → 2025 夏 IMO 5/6 → 2026/2 First Proof → 2026/5 单位距离猜想反例 → 2026/7 CDC 证明 | 事件序列 | Quanta / OpenAI |
| 2 | 陶哲轩「三阶段」模型：证明生成（AI 已攻克）→ 证明验证（Lean 半自动化）→ 证明消化（完全空白） | 概念框架 | 陶哲轩斯坦福演讲 |
| 3 | CDC 证明成本估算对比：$275-$485 vs ~$13,000 vs $20K(用户引用) | 社区估算 | HN |
| 4 | 数学论文作者数量趋势 vs 其他学科 | 论文署名统计 | 陶哲轩斯坦福演讲 |

### 图片素材方案

| 类型 | 内容 | 来源/链接 | 授权类型 |
|------|------|----------|---------|
| 1. 文章内可用配图 | 陶哲轩在斯坦福 Future of Mathematics 研讨会照片 | Stanford Daily | 需联系授权 |
| 2. 可下载图源 | Quanta 的 Lean 证明助手结构图、超立方体结构图 | Quanta Magazine | CC BY-NC-ND 4.0 |
| 3. AI 绘图 prompt 概要 | ① "A vast network graph glowing with golden cycles, each edge illuminated exactly twice, digital art" ② "64 parallel AI agents as luminous threads weaving through a mathematical proof landscape" ③ "Terence Tao at the intersection of human thought and AI, chalkboard with graph theory" | N/A | AI 生成 |

---

## Layer 2 ｜ 文章/视频大纲 + 素材填充

### RIVET 结构

**R · 场景爆破（Rupture）**
- 钩子：「一个 50 年没人解出来的数学猜想，AI 用一小时解决了。但菲尔兹奖得主陶哲轩说：这道题被解了，数学的理解没有增长一毫米。」
- 反常识：不是 AI 多聪明，而是这道题「比预期简单得多」——证明是「初等的」，1980 年代就可能被发现。人类失败的原因不是能力不够，而是「尝试一次失败后就放弃了」。
- 情绪弧线：震惊 → 困惑 → 更深的震惊

**I · 照亮盲区（Illuminate）**
- 核心论证：AI 对数学的影响不是「替代数学家」，而是暴露了一个更深层的问题——**数学的瓶颈从来不是证明，而是理解**。
- 陶哲轩的三阶段框架：证明生成（AI 已攻克）→ 证明验证（Lean 半自动化）→ 证明消化（完全空白）。前两阶段越快，第三阶段越追不上。
- Bloom 的关键洞察：AI 的优势是「计算坚持」而非「概念创新」——它不会气馁，持续尝试小变体直到成功。但这恰恰意味着它不理解自己在做什么。
- 古德哈特定律在数学界发作：「谁第一个证明了这个定理」曾经是衡量数学进步的好指标。AI 让这个指标和真正的数学进步脱钩了。

**V · 验证处境（Validate）**
- 数据支撑：
  - 2025 夏：AI 解出 IMO 6 题中的 5 题
  - 2026/2 First Proof 挑战赛：10 道研究级题目，AI 解出超过一半
  - 2026/5：OpenAI 用通用推理模型推翻 80 年猜想
  - 2026/7：CDC 猜想证明——64 并行子智能体，1 小时
  - 陶哲轩 IEANTN 项目：AI 形式化从数周缩短到数小时
  - Erdős 问题网站：约 20 篇 AI 辅助解题方案积压待审
- 关键引述：Daniel Litt「这项技术很可能比计算机更重大」；Bubeck「理解是你无法外包的」

**E · 具身化（Embody）**
- 核心隐喻：**「砖块与建筑」**——AI 能无限供应砖块（证明），但建筑师比砖匠更重要。问题是，连建筑师都快被埋在砖堆下面了。
- 辅助隐喻：**「考试拿满分但什么都没学到」**——AI 解出了猜想，但数学界对该猜想的理解没有增长。就像学生拿了满分，走出考场却一片空白。
- 跨领域迁移：「产出爆炸 vs 理解停滞」不是数学独有的——代码可以被 AI 大量生成但没人 review，论文可以批量写出但没人读，诊断可以秒出但医生来不及理解推理过程。

**T · 转化行动（Transform）**
- 行动建议（面向超级个体 / AI 实践者）：

**A. 工具链级自检表**

| 工具/场景 | 检查什么 | 为什么 |
|-----------|---------|--------|
| ChatGPT / Claude / Gemini 做分析 | 验证 AI 推理的每一步，不要只看结论 | AI 会给出「技术上正确但缺乏理解」的答案 |
| Cursor / Claude Code 写代码 | 对 AI 生成的代码做全局 review | 陶哲轩发现 AI 擅长局部优化，无法全局重构 |
| AI 辅助学习数学/新领域 | 让 AI 解释后，自己重新推导一遍 | 「理解不能外包」——AI 解释 ≠ 你理解了 |
| Dify / Coze / n8n 编排 AI 工作流 | 设计对抗性验证环节 | CDC 证明的 prompt 就使用了对抗智能体 |
| AI 辅助内容创作 | 确保你的独特洞察在 AI 输出之上 | 古德哈特定律：产出速度和真正进步会脱钩 |
| API Key 管理 | 按服务分开、设额度上限 | CDC 证明花了 $275-$13,000，大规模调用成本不低 |
| Lean / 形式化验证工具 | 关注形式化验证生态发展 | 数学界的新基础设施 |
| 个人知识管理 | 建立自己的「证明消化」系统 | 瓶颈不在生产端，在消化端 |

**B. 通用 5 步行动清单**
1. **接受新现实**：AI 已能批量产出「技术上正确」的成果。你的价值不在于「产出」，在于「消化和整合」。
2. **投资理解力**：每次用 AI 完成任务后，花时间理解「为什么这样做是对的」——这是 AI 无法替代的隐性目标。
3. **设计对抗性验证**：学 CDC 证明的 prompt 工程——用对抗性思维检查 AI 输出。
4. **成为架构师**：从「亲自执行」转向「设计任务结构让 AI 产出可整合」——陶哲轩称之为「证明工程架构师」。
5. **警惕选择偏差**：AI 公司只报告成功。当你看到「AI 一小时解决 50 年难题」时，记住还有无数未被报告的失败。

---

## 校准审查记录表

| 步骤 | 类型 | 检查结果 | 修正动作 |
|------|------|---------|---------|
| A | 事实校准 | $20K 计算预算未找到原始出处，社区估算 $275-$13,000 | 标注为"估算值"，给出完整范围 |
| B | 事实补充 | 补充 5 月推翻单位距离猜想（注意是"推翻"不是"证明"）；First Proof 挑战赛数据 | 已纳入 |
| C | 表述校准 | 避免"AI 解决了数学"的过度表述；区分"生成证明"vs"理解证明" | 全文调整 |
| D | 框架补充 | 陶哲轩「古德哈特定律」框架；「显性 vs 隐性目标」解耦 | 纳入 I 段 |
| E | 对立视角 | Venkatesh 谨慎立场；Bloom 选择偏差警示 | 已纳入 |
| F | 理论偏向 | 使用陶哲轩三阶段框架和古德哈特定律——标注来源为陶哲轩演讲 | 框架来源：陶哲轩斯坦福演讲 |
| G | 叙事引力 | 高引力话题。「反引力锚已加入」：Bloom「初等的」「1980 年代就可能被发现」「AI 只是更有耐心」；陶哲轩「理解没有增长一毫米」 | 主线已平衡 |
| H | 受众工具链翻译 | T-Transform 段含 8 行工具链自检表 + 5 步行动清单 | ✅ |
| I | 三角叙事补洞 | 第三点：陶哲轩同期推动的「新数学工作流」改革——华人世界最受尊敬的数学家，对中文受众有特殊分量 | 已强化陶哲轩线索 |

---

## 采集路径摘要

| # | 采集对象 | 路径类型 | 工具 | 备注 |
|---|---------|---------|------|------|
| 1 | OpenAI CDC 证明公告 + MLQ 报道 | ✅ 主路径 | WebSearch + WebFetch | 完整获取 |
| 2 | HN 讨论 #48863490 | ✅ 主路径 | WebFetch | 3556 行，部分读取 |
| 3 | The Decoder 报道 | ✅ 主路径 | WebFetch | 完整获取 |
| 4 | Thomas Bloom X 推文评估 | ✅ 主路径 | WebSearch + WebFetch (via MLQ) | 间接获取 |
| 5 | Quanta - How Tao Became Evangelist | ✅ 主路径 | WebFetch | 完整获取 |
| 6 | Quanta - AI Revolution in Math | ✅ 主路径 | WebFetch | 完整获取 |
| 7 | 陶哲轩博客 terrytao.wordpress.com | ⚠️ 降级 | WebFetch 内容有限 | 通过中文转述补充 |
| 8 | 智源社区 - IEANTN 项目 | ✅ 主路径 | WebFetch | 完整获取 |
| 9 | 知乎 - 陶哲轩斯坦福演讲解读 | ✅ 主路径 | WebFetch | 完整获取 |
| 10 | Stanford Daily 研讨会报道 | ✅ 主路径 | WebFetch | 完整获取 |
| 11 | arXiv - Mathematicians in the Age of AI | ✅ 主路径 | WebFetch | 完整获取 |
| 12 | Forbes - OpenAI AI Disproves Math Conjecture | ✅ 主路径 | WebFetch | 完整获取 |
| 13 | MathOverflow 讨论帖 | ⚠️ 降级 | WebFetch 403 | 通过其他信源补充 |
| 14 | MIT 科技评论中文版 | ⚠️ 降级 | WebFetch 需 JS | 通过知乎转述补充 |

> 本报告中降级路径触发次数：**3** 次

---

## 参考资料清单

| # | 标题 | URL | 来源类型 | 访问日期 |
|---|------|-----|---------|---------|
| 1 | OpenAI - A Proof of the Cycle Double Cover Conjecture (PDF) | https://cdn.openai.com/pdf/04d1d1e4-bc75-476a-97cf-49055cd98d31/cdc_proof.pdf | P1 | 2026-07-13 |
| 2 | Ethan Knight X 推文 - CDC 证明公告 | https://x.com/__eknight__/status/2075643450196971805 | P1 | 2026-07-13 |
| 3 | Thomas Bloom X 推文 - CDC 证明评估 | https://x.com/thomasfbloom/status/2075855061494706240 | P2 | 2026-07-13 |
| 4 | MLQ News - OpenAI Claims GPT-5.6 Sol Ultra Solved 50-Year-Old Math Conjecture | https://mlq.ai/news/openai-claims-gpt-56-sol-ultra-solved-50-year-old-math-conjecture-in-under-an-hour/ | P2 | 2026-07-13 |
| 5 | The Decoder - GPT-5.6 Sol Ultra reportedly solves 50-year math problem | https://the-decoder.com/openais-gpt-5-6-sol-ultra-reportedly-solves-a-50-year-old-math-problem-in-under-an-hour/ | P2 | 2026-07-13 |
| 6 | HN Discussion #48863490 | https://news.ycombinator.com/item?id=48863490 | P3 | 2026-07-13 |
| 7 | Quanta - How Terry Tao Became an Evangelist for AI in Math | https://www.quantamagazine.org/how-terry-tao-became-an-evangelist-for-ai-in-math-20260608/ | P2 | 2026-07-13 |
| 8 | Quanta - The AI Revolution in Math Has Arrived | https://www.quantamagazine.org/the-ai-revolution-in-math-has-arrived-20260413/ | P2 | 2026-07-13 |
| 9 | 陶哲轩博客 - Mathematical methods and human thought in the age of AI | https://terrytao.wordpress.com/2026/03/29/mathematical-methods-and-human-thought-in-the-age-of-ai/ | P1 | 2026-07-13 |
| 10 | 陶哲轩 Mathstodon - IEANTN 项目更新 | https://mathstodon.xyz/@tao/116789374373843141 | P1 | 2026-07-13 |
| 11 | Stanford Daily - Symposium weighs effect of AI on mathematics | https://stanforddaily.com/2026/05/06/future-of-mathematics-symposium-2026/ | P2 | 2026-07-13 |
| 12 | arXiv - Mathematicians in the Age of AI | https://arxiv.org/html/2603.03684v1 | P2 | 2026-07-13 |
| 13 | Forbes - OpenAI AI Finds Counterexample to Decades-Old Math Theory | https://www.forbes.com/sites/lanceeliot/2026/05/26/openai-ai-disproves-math-conjecture/ | P2 | 2026-07-13 |
| 14 | 智源社区 - 陶哲轩：AI突破数学形式化临界点 | https://hub.baai.ac.cn/view/55760 | P2 | 2026-07-13 |
| 15 | 知乎/新智元 - 陶哲轩：千年数学规则被AI按下重启键 | https://zhuanlan.zhihu.com/p/2039316672297842614 | P2 | 2026-07-13 |
| 16 | Reddit r/mathematics - GPT 5.6 Ultra CDC proof | https://www.reddit.com/r/mathematics/comments/1usw6r8/ | P3 | 2026-07-13 |
| 17 | Reddit r/math - OpenAI claims CDC proof | https://www.reddit.com/r/math/comments/1uszk3d/ | P3 | 2026-07-13 |
| 18 | MathOverflow - Purported proof of CDC | https://mathoverflow.net/questions/513149/ | P3 | 2026-07-13 |
| 19 | 陶哲轩 YouTube - Machine assistance and the future of research mathematics | https://www.youtube.com/watch?v=zJvuaRVc8Bg | P1 | 2026-07-13 |
| 20 | OpenAI - GPT-5.6 Frontier intelligence | https://openai.com/index/gpt-5-6/ | P1 | 2026-07-13 |

---

*报告由 hotspot-topic-excavator v2.7.5 生成 · 2026-07-13*
