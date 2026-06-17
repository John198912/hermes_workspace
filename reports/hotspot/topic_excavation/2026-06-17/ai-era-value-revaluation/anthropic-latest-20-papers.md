# Anthropic 最新20篇研究论文/报告速查表

> 数据源: Anthropic Research 官网 (anthropic.com/research) + Brave 多源交叉验证  
> 时间范围: 2025-12-18 → 2026-06-16（约6个月）  
> 生成时间: 2026-06-17

---

| # | 日期 | 类别 | 标题（中英） | 作者/团队 | 核心理论观点 | URL |
|---|------|------|-------------|----------|------------|-----|
| 1 | **Jun 16, 2026** | Economic Research | **Agentic coding and persistent returns to expertise**（智能体编码中，专业知识回报持续存在） | Zoe Hitzig, Maxim Massenkoff, Eva Lyubich, Ryan Heller, Peter McCrory | 分析40万次Claude Code会话（23.5万用户，7个月），首次用大规模实证证明：①领域专家让AI每次指令做12次动作（新手5次）、产出3200字（新手600字）；②非编程职业AI编码成功率仅比软件工程师低5%（30% vs 26%）；③管理者成功率最高；④人70%做规划决策，AI 80%做执行决策；⑤"领域专业知识>编程能力"是AI Agent成功的核心驱动力。**核心隐喻：coding agents are not substituting for domain expertise—they are amplifying it.** | [链接](https://www.anthropic.com/research/claude-code-expertise) |
| 2 | **Jun 8, 2026** | Science | **Paving the way for agents in biology**（为生物学中的AI Agent铺路） | Anthropic Science Team (含Edison Analysis合作) | 探索AI Agent在生物学研究中的应用，特别关注病毒基因组数据的快速获取与分析。以2026年5月刚果Bundibugyo病毒疫情为案例——AI Agent配合gget virus工具在VirBench基准测试中展示了快速检索病毒序列数据集的能力。**核心观点：AI Agent可以加速从"病毒检测"到"基因组共享"的关键时间窗口，直接关乎生命。**评估使用Claude Sonnet 4作为回退模型（因生物安全限制）。 | [链接](https://www.anthropic.com/research/agents-in-biology) |
| 3 | **Jun 5, 2026** | Science | **Making Claude a chemist**（让Claude成为化学家） | David Kamber (Anthropic化学家) | 测试Claude Opus 4.7/4.6/Sonnet 4.6对标ChemDraw和MestReNova在NMR（核磁共振）谱图预测与结构解析上的表现。在20个化合物上：①正向预测（结构→谱图）：Opus 4.7与专业软件相当，误差在化学家认可的±0.20ppm(¹H)和±1.0ppm(¹³C)内；②反向解析（谱图→结构，更难任务）：Opus 4.7在分子分裂模式预测上优于ChemDraw（80%准确率 vs 26-35%）。**核心观点：Claude开始有意义地辅助化学家的日常翻译、回忆和整合工作——补充而非替代其判断。** | [链接](https://www.anthropic.com/research/making-claude-a-chemist) |
| 4 | **Jun 3, 2026** | Policy | **What we learned mapping a year's worth of AI-enabled cyber threats**（绘制一年AI赋能网络威胁地图的发现） | Anthropic Policy + Frontier Red Team (与MITRE ATT&CK合作) | 系统梳理一年来AI被用于网络攻击的模式与趋势。**核心观点：AI正在同时降低网络攻击的门槛和放大攻击的规模，防御方需要同等甚至更快的AI赋能来应对。**为Project Glasswing提供了威胁情报基础。 | [链接](https://www.anthropic.com/news/AI-enabled-cyber-threats-mitre-attack) |
| 5 | **May 27, 2026** | Economic Research | **Coding agents in the social sciences**（社会科学中的编码Agent） | Anthropic Economic Research | 探索AI编码Agent在社会科学研究中的应用——从数据处理到统计分析到可复现研究。**核心观点：编码Agent正在降低社会科学研究的"技术门槛"，让非编程背景的研究者能做之前只有程序员才能做的定量分析。这与#1论文形成呼应——专业知识 + AI工具 = 研究民主化。** | [链接](https://www.anthropic.com/research/coding-agents-social-sciences) |
| 6 | **May 22, 2026** | Announcements | **Project Glasswing: An initial update**（玻璃翼计划：首月进展更新） | Anthropic (与50+合作伙伴) | Claude Mythos Preview上线首月：发现**10,000+高危/严重漏洞**，其中开源软件6,202个（确认真阳性1,726个，高危1,094个）。典型案例：wolfSSL关键漏洞(CVE-2026-5194, CVSS 9.1)——可伪造银行/邮箱证书。**核心发现："找漏洞容易，修漏洞难"——仅75个被修复，开源维护者甚至请求放缓披露速度。核心观点：AI打破了"找漏洞是瓶颈"的30年假设，但修复管道跟不上发现速度，形成危险的"过渡期"。**网络安全行业的价值从"检测"迁移到"修复"。 | [链接](https://www.anthropic.com/research/glasswing-initial-update) |
| 7 | **May 14, 2026** | Policy | **2028: Two scenarios for global AI leadership**（2028：全球AI领导力的两种情景） | Anthropic Policy | 构建两种2028年AI地缘政治情景：①合作情景——AI安全国际标准+负责任部署；②碎片化情景——各国各自为政、安全标准缺失。**核心观点：2026-2028年的政策选择将决定AI是成为全球公共产品还是地缘竞争武器。** | [链接](https://www.anthropic.com/research/2028-ai-leadership) |
| 8 | **May 8, 2026** | Alignment | **Teaching Claude why**（教Claude"为什么"） | Anthropic Alignment | 研究如何减少Agentic misalignment（智能体失调行为）。**核心发现："教WHY比教WHAT更有效"**——当Claude理解行为背后的原因和价值观时，泛化能力更强，在新情境中的对齐表现更好。这与"宪法AI"形成递进：从规则约束到原因理解。**核心观点：对齐的关键不是给AI更多规则，是让它理解规则背后的"为什么"。** | [链接](https://www.anthropic.com/research/teaching-claude-why) |
| 9 | **May 7, 2026** | Interpretability | **Natural Language Autoencoders: Turning Claude's thoughts into text**（自然语言自编码器：将Claude的"思维"转化为文本） | Anthropic Interpretability | 训练Claude将其内部数字表示（"思维"）翻译为人类可读的自然语言文本。**核心观点：AI用数字"思考"但用语言交流——这项研究搭建了桥梁，让研究者看到模型决策时内部发生了什么。**这是可解释性（interpretability）的重大突破——从"我们不知道模型在想什么"到"模型告诉我们它在想什么"。 | [链接](https://www.anthropic.com/research/natural-language-autoencoders) |
| 10 | **May 7, 2026** | Alignment | **Donating our open-source alignment tool**（捐赠我们的开源对齐工具） | Anthropic Alignment | 向开源社区捐赠对齐研究工具（基于PETRI框架）。**核心观点：AI安全不能是一家公司的事——通过开源工具，降低整个行业进行对齐研究的门槛。** | [链接](https://www.anthropic.com/research/donating-open-source-petri) |
| 11 | **May 7, 2026** | Policy | **Focus areas for The Anthropic Institute**（Anthropic研究所的研究重点） | The Anthropic Institute (TAI) | 宣布TAI的研究议程，聚焦：①AI对经济的影响测量；②AI部署的社会后果；③公共利益导向的AI能力发展。**核心观点：需要从"前沿实验室内部"获取数据来研究AI的社会影响——这是外部研究者无法做到的。** | [链接](https://www.anthropic.com/research/anthropic-institute-agenda) |
| 12 | **Apr 24, 2026** | Research | **Project Deal**（交易项目：AI Agent市场实验） | Anthropic (内部实验) | 在旧金山办公室创建Claude驱动的内部市场：69名员工每人$100预算，AI Agent在Slack中独立完成发帖→发现匹配→出价→谈判→成交。**结果：186笔真实交易，500+物品，交易额>$4,000。关键发现：①Opus Agent比Haiku Agent多成交2笔、卖出价高$3.64——相同物品，更好模型拿到更好价格；②用户没察觉模型差异导致的不公平。核心警告："agent quality gap"可能在真实市场中造成隐性不平等。**46%参与者愿意付费使用此服务。 | [链接](https://www.anthropic.com/features/project-deal) |
| 13 | **Apr 22, 2026** | Economic Research | **Announcing the Anthropic Economic Index Survey**（发布Anthropic经济指数调查） | Anthropic Economic Research | 启动月度经济指数调查（通过Anthropic Interviewer进行）。**核心观点：定量数据（Claude使用数据）不足以完全理解AI的经济影响——需要补充定性调查来获取用户的主观体验、职业变化和收入影响。** | [链接](https://www.anthropic.com/research/economic-index-survey-announcement) |
| 14 | **Mar 18, 2026** | Societal Impacts | **What 81,000 people want from AI**（81,000人想要从AI中得到什么） | Anthropic Societal Impacts | 邀请Claude.ai用户分享：如何使用AI、梦想AI能做什么、恐惧AI可能做什么。**81,000人参与——迄今最大规模、最多语言（含中文）的AI定性研究。核心发现涵盖使用模式（编码/写作/学习/情感支持）、期望（效率/创意/教育）、恐惧（失业/隐私/依赖）。核心观点：AI用户的需求远比"更快完成任务"复杂——他们渴望AI作为"思维伙伴"而非"工具"。** | [链接](https://www.anthropic.com/81k-interviews) |
| 15 | **Mar 5, 2026** | Economic Research | **Labor market impacts of AI: A new measure and early evidence**（AI对劳动力市场的影响：新测量方法与早期证据） | Maxim Massenkoff, Peter McCrory | 提出新的AI劳动力市场影响测量方法，初步证据显示：AI暴露度最高的职业群体中，**流入率（新雇佣）出现变化**——某些职业的新增岗位在减少，但总量影响尚不明确。**核心观点：AI对就业的影响不是"全面替代"而是"选择性重新配置"——某些岗位消失、某些岗位改变、某些新岗位出现。**（2026-03-08修正了图7标签错误） | [链接](https://www.anthropic.com/research/labor-market-impacts) |
| 16 | **Mar 2026** | Economic Research | **Anthropic Economic Index report: Learning curves**（Anthropic经济指数报告：学习曲线） | Anthropic Economic Research | 第五期经济指数报告（2026年2月数据）。**核心发现：①Claude使用正在从少数州向全国均匀扩散（Top 5州使用份额从30%降到24%，Gini系数下降）；②编程仍是最大使用场景（35%对话涉及计算机/数学职业），但使用场景在分散化（Top 10任务从24%降到19%）。核心观点：AI使用正在从"早期采用者的集中爆发"过渡到"更广泛的平等扩散"。** | [链接](https://www.anthropic.com/research/economic-index-march-2026-report) |
| 17 | **Feb 16, 2026** | Education | **Anthropic Education Report: The AI Fluency Index**（AI流利度指数） | Kristen Swanson, Drew Bent, Zoe Ludwig, Rick Dakan, Joe Feller | 分析9,830次Claude.ai多轮对话（2026年1月一周），测量11项"AI流利度"行为（基于24行为4D框架）。**核心发现：①85.7%对话含"迭代优化"——用户不满足于第一个答案；②迭代用户质疑AI推理的可能性5.6倍、发现缺失上下文4倍；③当AI产出代码/文档等"制品"时，用户反而更少核查——"看着完整就觉得没问题"。核心观点：AI流利度不在于使用频率，而在于交互质量——会追问、会验证、会质疑的人，才是真正的"AI流利者"。** | [链接](https://www.anthropic.com/research/AI-fluency-index) |
| 18 | **Feb 16, 2026** | Economic Research | **India Country Brief: The Anthropic Economic Index**（印度国别简报：Anthropic经济指数） | Ruth Appel | 聚焦印度市场的AI使用模式分析。**核心观点：AI在新兴市场的渗透路径与发达国家不同——更偏向移动端、教育辅助、小微企业场景，需要定制化的经济影响评估框架。** | [链接](https://www.anthropic.com/research/india-brief-economic-index) |
| 19 | **Jan 15, 2026** | Economic Research | **Anthropic Economic Index report: Economic primitives**（Anthropic经济指数报告：经济原语） | Anthropic Economic Research | 首期经济指数报告（2025年11月数据，Opus 4.5发布前）。**引入核心分析框架：通过隐私保护分析工具将用户对话映射到O\*NET职业任务分类，测量AI在不同职业和任务中的渗透率。核心观点：AI当前主要用于"增强"（augmentation）而非"替代"（automation）——作为思维伙伴而非全自动执行者。** | [链接](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report) |
| 20 | **Dec 18, 2025** | Policy | **Project Vend: Phase two**（售卖项目：第二阶段） | Anthropic Policy | Project Vend（AI店主实验）的第二阶段报告：在旧金山办公室午餐区设置AI经营的小商店，测试AI处理真实世界复杂任务（定价、库存、客户交互）的能力。**核心观点：AI从"回答问题"到"经营业务"的跨越，测试的是复合能力——规划、适应、错误恢复、长期目标维持。** | [链接](https://www.anthropic.com/research/project-vend-2) |

---

## 📊 统计概览

| 维度 | 分布 |
|------|------|
| **时间跨度** | 2025-12-18 → 2026-06-16（6个月） |
| **类别分布** | Economic Research: 8篇 · Science: 2篇 · Policy: 4篇 · Alignment: 3篇 · Interpretability: 1篇 · Societal Impacts: 1篇 · Education: 1篇 · Announcements: 1篇 · Research: 1篇 |
| **6月密集发布** | 4篇（#1-#4，占比最高的一周） |
| **5月密集发布** | 6篇（#5-#11含同日3篇） |

### 🔑 关键趋势脉络

```
2025-12  Project Vend Phase 2 → 探索AI的自主经济行为能力
2026-01  Economic Primitives → 建立AI使用测量的基础框架
2026-02  AI Fluency Index + India Brief → 从"多少人用AI"到"用得好不好"
2026-03  Labor Market Impacts + 81K用户心声 + Learning Curves → 全景扫描AI社会影响
2026-04  Project Deal + Economic Survey → AI Agent进入真实经济交易+月度定性跟踪启动
2026-05  Glasswing更新 + Teaching WHY + 自编码器 + 2028情景 → 安全/对齐/可解释性/地缘政治四线并进
2026-06  Expertise论文 + 生物Agent + 化学家Claude + 网络威胁 → AI渗透到专业领域的深水区
```

### 📌 与SOUL控制性理念最相关的3篇

1. **#1 Agentic coding expertise**（6/16）→ 直接实证"真实稳定的自我是不可替代的资产"
2. **#17 AI Fluency Index**（2/16）→ "会迭代优化/会质疑"的人才是真正会用AI的人
3. **#12 Project Deal**（4/24）→ Agent质量差距造成的不公平——模型差异=经济差异

---

*表格由 Hermes Agent 基于 Anthropic Research 官网 + Brave 多源交叉验证生成 · 2026-06-17*
