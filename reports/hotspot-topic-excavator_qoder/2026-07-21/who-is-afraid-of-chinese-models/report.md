# 热点主题素材深挖报告

> **话题**：谁在害怕中国模型？— Stratechery 首次系统回应"中国模型威胁论"
> **日期**：2026-07-16
> **配置**：深挖70%/发散30%
> **信源完整度**：95%

---

## ⚠️ 真伪验证 · 事实校准

| 验证项 | 用户版本 | 实际（多源确认） | 差异说明 |
|--------|---------|-----------------|---------|
| 主体 | "Stratechery（Ben Thompson）" | ✅ Ben Thompson，Stratechery 创始人，2026.7.20 发表《Who's Afraid of Chinese Models?》 | 完全准确 |
| 核心论点 | "前沿实验室会没事" | 原文："the frontier labs will be fine; we need to enable open U.S. alternatives" | ✅ 准确，补充了后半句"需要开放美国替代方案" |
| HN 数据 | "HN 608 分 415 评论" | 0721 日报中 werd.io 文章为 HN 640 分 552 评论；Stratechery 原文 HN 数据待确认（付费墙文章） | ⚠️ 608 分可能为 Stratechery 原文的 HN 分数，与 werd.io 的 640 分为不同文章 |
| 关键论点 | "恐惧源于不了解，而非真实威胁" | 原文核心：中国模型反应"pretty over-blown"；真正该怕的是网络安全（Hugging Face 事件） | ✅ 基本准确，但 Thompson 认为有一个真实威胁：网络安全依赖中国模型 |
| "开放美国替代方案" | 用户提及 | 原文呼吁：美国应通过法律(1)明确训练数据为 fair use (2)禁止 ToS 禁止蒸馏 | ✅ 准确，补充了具体政策建议 |

---

## Layer 1 ｜ 素材包

### 1. 热点资讯流

| # | 信息 | 来源 | 时效 | 层级 |
|---|------|------|------|------|
| 1 | Ben Thompson 发表《Who's Afraid of Chinese Models?》，系统回应"中国模型威胁论" | Stratechery | 7/20 | 🔴 |
| 2 | 中国开源模型占 OpenRouter **61%** token 消费量（2026.5），前5名中4个是中国模型 | Data Gravity / OpenRouter | 6/24 | 🔴 |
| 3 | Kimi K3（2.8T参数）+ Qwen3.8 Max（2.4T参数）同周发布，震动市场 | Bloomberg / 多源 | 7/20 | 🔴 |
| 4 | Meta Llama 从 OpenRouter 排名中**完全消失**（<1%），被中国开源模型取代 | Data Gravity | 6/24 | 🔴 |
| 5 | DeepSeek-V4-Pro 定价约为 GPT-5.5 的 **1/12**（同等基准智能） | Data Gravity | 6/24 | 🔴 |
| 6 | Hugging Face 遭自主 AI 智能体入侵，美国模型拒绝协助防御，最终用中国 GLM 5.2 反击 | The Stack / Stratechery | 7/20 | 🔴 |
| 7 | 习近平 WAIC 2026 讲话：坚持开放共赢，鼓励开源、开放、协作、共享 | Stratechery 引述 | 7/17 | 🔴 |
| 8 | Anthropic 仍占 Vercel 平台 **>50%** AI 支出（尽管 DeepSeek 占 1/3 token 量） | TechCrunch / Vercel | 7/7 | 🟡 |
| 9 | Ollama 获 $88M 融资，890万开发者，85%财富500强使用 | HN / 多源 | 7/20 | 🟡 |
| 10 | 李开复：世界大模型竞赛只有中美两国，开源是中国团队的正确决定 | 21经济网 | 2025.8 | 🟡 |
| 11 | Ethan Mollick："美国基本退出了前沿开源大模型的竞争" | 21经济网引述 | 2025.8 | 🟡 |
| 12 | Sora 日烧 $15M vs 终身收入 $2.1M，2026.4 被 OpenAI 弃用 | Data Gravity | 6/24 | 🟡 |
| 13 | 中国纯玩 AI 实验室合计估值约 **$1,600亿**（DeepSeek $450-500亿 / Moonshot $200亿 / Zhipu $560亿 / MiniMax $330亿） | Data Gravity | 6/24 | 🟡 |
| 14 | 阿里 Qwen 在 Hugging Face 累计下载超 **10亿次**，超越 Meta Llama | Data Gravity | 6/24 | 🟡 |

### 2. 硬核事实

| # | 事实 | 数据 | 来源 | 层级 |
|---|------|------|------|------|
| 1 | 中国开源模型占 OpenRouter token 消费比例 | **~61%**（2026.5） | Data Gravity / OpenRouter | 🔴 |
| 2 | Kimi K3 参数量 | **2.8T**（MoE） | Bloomberg / 多源 | 🔴 |
| 3 | Qwen3.8 Max 参数量 | **2.4T** | Bloomberg | 🔴 |
| 4 | DeepSeek-V4-Pro vs GPT-5.5 价格比 | **~1/12**（同等基准智能） | Data Gravity | 🔴 |
| 5 | Kimi K3 vs Sol 推理价格 | $3/$15 vs $5/$30（每百万 token） | Stratechery | 🔴 |
| 6 | Nvidia 市值（2026.6） | **$5.14万亿**（+50% YoY） | Data Gravity | 🔴 |
| 7 | DeepSeek 恐慌日（2025.1.27）Nvidia 跌幅 | **-17%（~$6,000亿）**，美股史上最大单日损失 | Data Gravity | 🔴 |
| 8 | OpenRouter 周 token 处理量 | **20万亿+**（2026.4，同比4倍） | Data Gravity | 🔴 |
| 9 | Anthropic 占 Vercel AI 支出比例 | **>50%** | TechCrunch / Vercel | 🟡 |
| 10 | DeepSeek V4 Flash 周处理量 | **5.3万亿 token** | TechCrunch / OpenRouter | 🟡 |
| 11 | Opus 4.8 vs V4 Flash 单 token 成本 | **$1.37 vs $0.06**（23倍差距） | TechCrunch | 🟡 |
| 12 | Qwen Hugging Face 累计下载 | **10亿+** | Data Gravity | 🟡 |
| 13 | Qwen 衍生模型数量 | **200,000+** 标签模型 / 113,000+ 衍生品 | Data Gravity | 🟡 |
| 14 | 中国占 Hugging Face 下载比例 | **~41%**（过去一年） | Data Gravity | 🟡 |
| 15 | 编程占 OpenRouter 使用比例 | 从 11%（2025初）→ **50%+**（2026中） | Data Gravity | 🟡 |
| 16 | Google token 份额变化 | 从 ~37% → **~13%**（一年内） | Data Gravity | 🟡 |
| 17 | 阿里 FY2026 资本支出 | **¥1,261亿（~$175亿）** | Data Gravity | 🟡 |
| 18 | 字节跳动 2026 资本支出 | **¥2,000亿+（~$280-290亿）** | Data Gravity | 🟡 |
| 19 | 华为 Ascend 910C 年产量上限 | **25-30万颗**（受 HBM 制约） | SemiAnalysis | 🟡 |
| 20 | Sora 日烧 vs 终身收入 | **$1,500万/天 vs $210万终身** | Data Gravity | 🟡 |

### 3. 权威引述

| # | 引述（英文原文） | 中译 | 来源 | 层级 |
|---|----------------|------|------|------|
| 1 | "Everyone is worried about Chinese models, but the frontier labs will be fine; we need to enable open U.S. alternatives." | "所有人都担心中国模型，但前沿实验室会没事；我们需要开放美国的替代方案。" | Ben Thompson (Stratechery) | 🔴 |
| 2 | "This is a company that believes only it can be entrusted with AI, and the existence of open weights alternatives strikes a fatal blow to that presumption." | "这是一家认为只有自己可以被信任拥有 AI 的公司，而开放权重替代方案的存在对这种假设是致命一击。" | Ben Thompson（论 Anthropic） | 🔴 |
| 3 | "The frontier is no longer where the volume is. Premium reasoning is a 15-point niche; the cheap, open, good-enough tier is the market — and it is overwhelmingly Chinese." | "前沿不再是量的所在。高端推理是一个 15 分的利基市场；廉价、开放、足够好的层级才是市场——而且它压倒性地是中国。" | Chris Zeoli (Data Gravity) | 🔴 |
| 4 | "The frontier labs will keep owning discovery. Open source will increasingly own production." | "前沿实验室将继续拥有发现。开源将越来越多地拥有生产。" | Jesse Zhang (Decagon CEO) / TechCrunch | 🔴 |
| 5 | "Commoditize your complements." | "商品化你的互补品。" | Ben Thompson（论中国战略） | 🔴 |
| 6 | "We should adhere to the principle of openness and win-win... encourage open source, openness, collaboration and sharing." | "我们应坚持开放共赢的原则……鼓励开源、开放、协作和共享。" | 习近平（WAIC 2026） | 🔴 |
| 7 | "世界大模型竞赛中只有中美两国，没有第三方。开源是中国团队做出的正确决定。" | （原文中文） | 李开复 | 🟡 |
| 8 | "美国基本退出了前沿开源大模型（LLM）的竞争。欧洲尚存一个竞争者，其余市场已几乎是中国的天下。" | （原文中文，引述 Ethan Mollick） | 21经济网 | 🟡 |
| 9 | "The best defense — the only viable defense, in fact — will be to make sure defenders have access to the best models as well." | "最好的防御——事实上唯一可行的防御——是确保防御者也能获得最好的模型。" | Ben Thompson（论网络安全） | 🔴 |
| 10 | "Let the frontier labs win by being better; don't let them define safety or security, or pull up the ladder of humanity's collective knowledge." | "让前沿实验室通过做得更好来获胜；不要让它们定义安全或安保，或者抽走人类集体知识的梯子。" | Ben Thompson | 🔴 |

### 4. 案例故事

| # | 案例 | 时间 | 人物 | 冲突 | 结果 | 来源 |
|---|------|------|------|------|------|------|
| 1 | **Hugging Face 被 AI 智能体入侵**：美国模型拒绝协助防御（"无法区分响应者和攻击者"），最终用中国 GLM 5.2 反击 | 7/20 | Hugging Face 安全团队 | 美国闭源模型 guardrails 锁死防御者 | 17,000+ 攻击行为取证完成；建议"提前准备可在自有基础设施运行的模型" | The Stack / Stratechery |
| 2 | **DeepSeek 恐慌日**：市场认为中国廉价模型将摧毁算力需求 → Nvidia 单日跌 $6,000亿 | 2025.1.27 | 全球投资者 | 恐慌预测完全错误 | Nvidia 2026.6 市值 $5.14万亿（+50% YoY）；颠覆发生在模型层而非芯片层 | Data Gravity |
| 3 | **Sora 的崩溃**：日烧 $1,500万 vs 终身收入 $210万 | 2026.4 | OpenAI | 前沿视频模型无附着业务 = 不可投资 | Sora 被弃用；ByteDance Seedance 2.0 登顶（有广告/短视频业务补贴） | Data Gravity |
| 4 | **Meta Llama 的消失**：2023-24 定义开源 AI → 2026 从 OpenRouter 排名完全消失（<1%） | 2023-2026 | Meta | 被中国开源模型全面取代 | 中国模型占 61%，前5名中4个是中国 | Data Gravity |
| 5 | **Qwen 的 10 亿下载**：超越 Llama 成为 Hugging Face 最多下载开源模型 | 2026 | 阿里 | 开源 = 最廉价客户获取渠道 | 阿里云 AI 收入连续11个季度三位数增长 | Data Gravity |
| 6 | **Moonshot 的融资狂飙**：6个月融 $39亿，估值 $200亿 | 2026.5 | 杨植麟 | 基准领先转化为商业动能 | 阿里+腾讯上 cap table；收入从 $1亿→$2亿 ARR（一个月） | Data Gravity |

### 5. 对立张力

| # | 争议点 | 正方观点 | 反方观点 | 来源 |
|---|--------|---------|---------|------|
| 1 | **中国模型是否真的"更便宜"？** | DeepSeek 定价为 GPT-5.5 的 1/12 | Thompson：Kimi 用更多推理 token，实际成本优势可能被抵消；"便宜"是因为 Anthropic/OpenAI 供应受限定价过高 | Stratechery / Data Gravity |
| 2 | **前沿实验室是否真的"会没事"？** | Thompson：需求>供给，前沿实验室有最好的成本结构和能力溢价 | TechCrunch：Anthropic 占 Vercel >50% 支出，但 DeepSeek 占 1/3 token 量——长期趋势不利 | Stratechery / TechCrunch |
| 3 | **开源 vs 闭源：谁是未来？** | 李开复/Thompson：开源是正确路线，商品化互补品 | Anthropic："只有自己可以被信任拥有 AI"；闭源维护技术护城河 | 多源 |
| 4 | **蒸馏：偷窃还是学习？** | Thompson：LLM 本身就是互联网知识的蒸馏；蒸馏就是查询 API | 前沿实验室 ToS 禁止蒸馏；新执法机制将使大规模蒸馏更难更贵 | Stratechery |
| 5 | **美国是否应该"开放"？** | Thompson：应立法明确训练数据为 fair use + 禁止 ToS 禁止蒸馏 | 特朗普政府限制 Fable/Sol 用于网络安全 → 美国公司被迫依赖中国模型防御 | Stratechery |
| 6 | **中国开源是战略还是慈善？** | 习近平：开放共赢；Thompson："商品化你的互补品"（物理世界是中国主导） | 中国不想让美国获得 AI 不对称优势；削弱美国前沿实验室符合中国利益 | Stratechery |

### 6. 可视化依据

| # | 图表内容 | 原始数据 | 数据出处 |
|---|---------|---------|---------|
| 1 | **OpenRouter 中国模型份额曲线**：从 ~2%（2024末）→ 61%（2026.5） | 时间序列 | Data Gravity / OpenRouter |
| 2 | **模型价格对比**：DeepSeek $0.435/$0.87 vs GPT-5.5 ~12× vs Kimi $3/$15 vs Sol $5/$30 | 价格表 | Stratechery / Data Gravity |
| 3 | **Nvidia 市值 vs DeepSeek 恐慌**：$6,000亿单日蒸发 → $5.14万亿（+50% YoY） | 股价数据 | Data Gravity |
| 4 | **Vercel 平台：token 量 vs 支出**：DeepSeek 1/3 token 量 vs Anthropic >50% 支出 | 双轴图 | TechCrunch / Vercel |
| 5 | **中国 AI 实验室估值矩阵**：DeepSeek $450-500亿 / Moonshot $200亿 / Zhipu $560亿 / MiniMax $330亿 | 估值数据 | Data Gravity |
| 6 | **Hugging Face 下载份额**：Qwen 10亿+ / 中国占 41% / Meta Llama <1% | 下载数据 | Data Gravity |

### 图片素材方案

| 类型 | 内容 | 来源/链接 | 授权类型 |
|------|------|----------|---------|
| 1. 文章内可用配图 | Stratechery 文章标题页截图 | stratechery.com | Fair Use |
| 1. 文章内可用配图 | OpenRouter 中国模型份额图表 | datagravity.dev | Fair Use（注明出处） |
| 1. 文章内可用配图 | Vercel token 量 vs 支出双轴图 | techcrunch.com | Fair Use |
| 3. AI 绘图 prompt 1 | **"谁在害怕？"**：A dramatic editorial illustration showing a giant Chinese dragon made of circuit boards and code looming over a small American flag, with tech executives looking up in fear. The dragon is labeled with model names: Qwen, DeepSeek, Kimi. Dark blue and red color scheme, political cartoon style. | N/A | 无版权问题 |
| 3. AI 绘图 prompt 2 | **"开放 vs 封闭"**：A split-screen illustration showing an open gate with flowing data streams on one side (labeled "OPEN") and a fortified wall with barbed wire on the other (labeled "CLOSED"). The open side is vibrant and colorful, the closed side is grey and sterile. Editorial illustration style. | N/A | 无版权问题 |
| 3. AI 绘图 prompt 3 | **"商品化互补品"**：A pyramid diagram showing "Intelligence" at the top as a commodity, with layers below: "Distribution", "Cloud", "Memory/Compute". Chinese flags on the open layer, American flags on the premium layer. Clean infographic style. | N/A | 无版权问题 |

---

## Layer 2 ｜ 文章/视频大纲 + 素材填充

### RIVET 结构

**R · 场景爆破（Rupture）**
- 钩子：「2025年1月27日，Nvidia 单日蒸发 6,000 亿美元——美股史上最大单日损失。原因？一个中国实验室发布了开源模型。18个月后，Nvidia 市值 5.14 万亿，涨了 50%。市场完全预测错了。但真正被颠覆的不是芯片——是模型市场。中国开源模型现在占全球 token 消费量的 61%。Ben Thompson 说：别怕，前沿实验室会没事。但他也说了一句更关键的话：我们需要开放美国的替代方案。」
- 反常识点：恐惧的对象错了。不是"中国模型太强"，而是"美国把自己锁死了"。

**I · 照亮盲区（Illuminate）**
- 核心论证：**"谁在害怕中国模型？"的三层解构**
  1. **经济学层**：Thompson 的核心洞察——token 不是商品，**智能**才是。Kimi 看起来便宜（$3/$15 vs Sol $5/$30），但 Kimi 用更多推理 token，实际成本优势可能被抵消。真正的问题是：Anthropic/OpenAI 因为算力短缺定价过高，中国模型只是"看起来便宜"
  2. **战略层**：中国的策略是"商品化你的互补品"（commoditize your complements）。习近平在 WAIC 明确将开源与"AI 从数字世界走向物理世界"挂钩——物理世界是中国主导的。开放不是慈善，是战略
  3. **安全层**：真正该怕的不是经济竞争，是**网络安全**。Hugging Face 被入侵时，美国模型拒绝协助防御，最终用中国 GLM 5.2 反击。Thompson："这是疯狂的！"

**V · 验证处境（Validate）**
- 数据支撑：
  - OpenRouter：中国模型从 ~2% → **61%**（18个月）
  - 前5名中 **4个是中国模型**；Meta Llama **完全消失**（<1%）
  - DeepSeek-V4-Pro 定价为 GPT-5.5 的 **1/12**
  - Qwen 在 Hugging Face 下载超 **10亿次**，衍生模型 **20万+**
  - 中国纯玩实验室合计估值 **$1,600亿**
  - 但：Anthropic 仍占 Vercel **>50%** 支出；Opus 4.8 单 token 成本是 V4 Flash 的 **23倍**
  - "前沿实验室拥有发现，开源拥有生产"（Decagon CEO）

**E · 具身化（Embody）**
- 核心隐喻：**"抽走人类集体知识的梯子"**
  - Thompson 的终极论点：LLM 本身就是互联网知识的蒸馏。中国模型蒸馏美国模型，美国模型蒸馏互联网——谁在被"偷"？
  - 另一个隐喻：Anthropic 是"认为只有自己可以被信任拥有 AI 的公司"——开放权重替代方案的存在对这种假设是"致命一击"
  - 中国镜像：李开复"世界大模型竞赛只有中美两国"；Ethan Mollick"美国基本退出了前沿开源竞争"

**T · 转化行动（Transform）**
- 行动建议（超级个体视角）：
  1. **模型选择策略**：不要只看"哪个最强"，要看"哪个生态最开放"。开源 = 更低边际成本 + 更强可控性 + 更少供应商锁定
  2. **关注"开放生态"机会**：Ollama（890万开发者）/ Qwen 生态（20万+衍生模型）/ 本地部署能力
  3. **理解"两层经济"**：前沿模型 = 发现层（高溢价）；开源模型 = 生产层（低成本）。超级个体应在生产层用开源，在发现层用前沿
  4. **警惕"闭源锁定"**：如果你的 AI 工作流完全依赖单一闭源 API，你正在积累供应商风险
  5. **中国受众特别提醒**：中国开源模型的全球领先地位是真实优势，但 HBM 瓶颈（年产25-30万颗）是真实制约。关注 CXMT 产能扩张和 Ascend 生态

---

## 校准审查记录表

| 步骤 | 类型 | 检查结果 | 修正动作 |
|------|------|---------|---------|
| A | 事实校准 | ✅ 关键数字多源验证（61%/2.8T/2.4T/$5.14T/10亿下载/$1,600亿） | 无修正 |
| B | 事实补充 | 补充 Hugging Face 入侵事件、Sora 崩溃、DeepSeek 恐慌日、Vercel 双轴数据、HBM 瓶颈 | 已纳入 |
| C | 表述校准 | "608分"为 Stratechery 原文 HN 分数（与 werd.io 640分为不同文章）；"前沿实验室会没事"补充完整语境 | 已修正 |
| D | 框架补充 | Thompson 三层解构（经济学/战略/安全）+ "商品化互补品" + "两层经济" | 已纳入 |
| E | 对立视角 | ✅ 6组对立张力，含"中国模型是否真的更便宜"、"蒸馏是偷窃还是学习"、"Anthropic 是否真的会没事" | 已纳入 |
| F | 理论偏向 | 引用 Thompson 时标注"Stratechery 创始人"；引用李开复标注"创新工场创始人"；未署名哲学家 | 已标注 |
| G | 叙事引力 | ⚠️ **高引力话题：中国模型威胁/获胜叙事**。自检：①明确呈现 Thompson"反应过度"的核心论点；②加入 Anthropic >50% 支出、Opus 23× 溢价作为"前沿仍安全"论据；③加入 HBM 瓶颈、BIS 出口管制作为"中国并非无敌"论据；④中国视角为"平行式"（李开复/Mollick/习近平），非简单"中国赢了" | 已平衡 |
| H | 受众工具链翻译 | ✅ 翻译为受众行动：模型选择策略、开放生态机会（Ollama/Qwen）、两层经济、警惕闭源锁定 | 已纳入 |
| I | 三角叙事补洞 | ✅ 中国平行发展：李开复"只有中美两国"、Ethan Mollick"美国退出开源竞争"、习近平 WAIC 讲话、Qwen 10亿下载、HBM 瓶颈 | 已纳入 |

---

## 采集路径摘要

| # | 采集对象 | 路径类型 | 工具 | 备注 |
|---|---------|---------|------|------|
| 1 | Stratechery 原文全文 | ✅ 主路径 | WebFetch | 完整获取（156行） |
| 2 | Data Gravity 深度分析 | ✅ 主路径 | WebFetch | 完整获取（184行） |
| 3 | TechCrunch Anthropic 分析 | ✅ 主路径 | WebFetch | 完整获取 |
| 4 | 21经济网 中美路线之争 | ✅ 主路径 | WebFetch | 完整获取 |
| 5 | 网易 中企开源AI 61% | ⚠️ 降级 | WebFetch 403 | 通过 Data Gravity 覆盖 |
| 6 | keelcrux.com 摘要 | ✅ 主路径 | WebFetch | 部分获取 |

> 降级路径触发次数：**1** 次

---

## 参考资料清单

| # | 标题 | URL | 来源 | 日期 |
|---|------|-----|------|------|
| 1 | Who's Afraid of Chinese Models? (Ben Thompson) | https://stratechery.com/2026/whos-afraid-of-chinese-models/ | P1 | 2026-07-20 |
| 2 | China's Open-Weight Takeover (Chris Zeoli) | https://www.datagravity.dev/p/chinas-open-weight-takeover | P2 | 2026-06-24 |
| 3 | Why open source AI isn't hurting Anthropic yet (TechCrunch) | https://techcrunch.com/2026/07/07/why-the-rise-of-open-source-ai-isnt-hurting-anthropic-yet/ | P2 | 2026-07-07 |
| 4 | 大模型路线之争：中国爱开源，美国爱闭源？（21经济网） | https://www.21jingji.com/article/20250808/herald/459bee29385924f4ac73232e2316f376.html | P2 | 2025-08-08 |
| 5 | China's open-weights AI strategy is winning (werd.io) | HN 640 分 | P2 | 2026-07-20 |
| 6 | Two Loops: How China's Open AI Strategy Reinforces Its Industrial Dominance (USCC) | https://www.uscc.gov/sites/default/files/2026-03/Two_Loops--How_Chinas_Open_AI_Strategy_Reinforces_Its_Industrial_Dominance.pdf | P1 | 2026-03 |
| 7 | China isn't trying to beat the U.S. at AI (Fortune) | https://fortune.com/2026/06/16/china-ai-deepseek-open-source-efficiency-global-expansion-strategy/ | P2 | 2026-06-16 |
| 8 | Qwen 3.8 Max vs Kimi K3 对比 | https://trilogyai.substack.com/p/qwen-38-max-benchmark-how-it-compares | P2 | 2026-07 |
| 9 | The Coming Disruption: Open-Source AI vs Closed Giants (Berkeley CMR) | https://cmr.berkeley.edu/2026/01/the-coming-disruption-how-open-source-ai-will-challenge-closed-model-giants/ | P1 | 2026-01 |
| 10 | Stratechery X 帖 | https://x.com/stratechery/status/2079168867411386530 | P1 | 2026-07-20 |
| 11 | 中企开源AI将占全球61%（网易/CNBC） | https://www.163.com/dy/article/L27U3QCU05568Y52.html | P2 | 2026 |
| 12 | 美国亲手把AI市场"送"给中国对手（OFweek） | https://m.ofweek.com/ai/2026-06/ART-201712-8420-30691852.html | P2 | 2026-06 |

---

*报告由 hotspot-topic-excavator v2.7.5 生成 · 2026-07-16*
