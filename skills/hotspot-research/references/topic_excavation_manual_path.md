# 话题素材深挖：手动执行路径 (Manual Excavation Path)

> **状态：过渡方案** — 当 `hotspot-topic-excavator` 独立 skill 尚未创建时，使用此手动路径替代。
> **相关条目：** hotspot-research SKILL.md 执行节奏表中引用的 "热点主题素材深挖 | 按需 | 手动触发"
> **创建日期：** 2026-06-23（基于 Pew 悖论实战验证）
> **最后更新：** 2026-07-08（新增模型 G：数据趋势/结构性转折型 · BAIR博客智能成本归零实战验证 · WordPress URL 发现技巧 + 新增 references/model_g_trend_structural_shift.md）

---

## 为什么需要这个过渡方案

`hotspot-topic-excavator` skill 在热点采集系统的执行节奏表中被引用为独立 skill（"v2, 双轴模型"），但截至 2026-06-23 尚未作为独立 skill 创建。以下手动执行路径已在实际话题中验证有效，产出质量达标。

---

## ⚠️ 执行前必检 · 重复覆盖检测（2026-06-27 实战验证后新增）

**触发条件**：当用户请求"深度挖掘"/"深度素材挖掘"/"hotspot-topic-excavator"某个热点话题时，**先做 4 项检查**，再决定是否进入 Step 1。

### 检测步骤（30-60s 完成，避免浪费 30+ 分钟做重复劳动）

```
1. 日报库检索
   search_files path=~/hermes_workspace/reports/hotspot pattern="<话题关键词>" target=content
   → 找出最近 14 天内所有日报/周报是否已收录此话题

2. excavation 目录检索
   ls ~/hermes_workspace/reports/hotspot/topic_excavation/
   search_files pattern="<话题关键词>" target=content path=~/hermes_workspace/reports/hotspot/topic_excavation/
   → 找出今日/近期是否已有兄弟 excavation

3. 线索库检索
   grep -lE "<话题关键词>" ~/hermes_workspace/reports/hotspot/report_*.md | head -5
   → 检查「📡 本周线索」section 是否已标记此话题

4. 完整度评估
   对比已存在内容的覆盖维度（数据/反方/中国版/可操作框架等）
   → 识别本次可以真正"增量"的角度
```

### 三条决策路径（用 `clarify` 工具问用户选择，**卷哥交互偏好**）

| 路径 | 适用场景 | 执行内容 |
|------|---------|---------|
| **A. 重新全量采集** | 已存在内容严重过时（>30 天）/ 数据源已更新 / 用户明确要求独立文档 | 绕开已有报告，从原报告 URL 开始，独立产出新 topic_materials.md + deep_analysis_plan.md |
| **B. 增量深挖** ⭐ **默认推荐** | 已存在 1-2 篇相关日报 + 可能有兄弟 excavation | 聚焦新维度（反方/中国版/原报告全文/数学模型），不重复已写角度 |
| **C. 直接进入内容生产** | 已存在日报 + excavation 完整且覆盖了 SOUL 框架 | 跳过素材挖掘，按已有方案直接产出三平台分发内容 |
| **D. 我判断错了** | 用户明确表态"已覆盖不等于不能再做" | 全量执行，但归档到带日期后缀的子目录避免覆盖 |

### 🆕 W-clue 自动 B-path 规则（2026-07-05 实战验证）

当话题已在 `_week_clues.json` 中**追踪 ≥ 5 天**且日报有定性覆盖时，**自动走 B 路径，不再用 `clarify()` 询问**——直接提案 5-6 个增量维度并立即执行。

**判断逻辑：**
```
话题在 W-clue 追踪天数 ≥ 5 天
  + 日报已覆盖定性分析（深度分析有 #x 编号）
  + excavation 目录中无兄弟版本
  → 自动判定：B 路径
  → 提案：3-5 个增量维度
  → 用一句话 + 直接执行（不二次确认）
```

**为什么这个规则：** 2026-07-04/05 连续 4 次深挖（创意产业/技能周期/七部门/NYT），用户每次都选 B——模式已经稳定。"用 `clarify()` 选路径" 在已稳态场景下变成仪式性摩擦，浪费一轮交互。

**反模式：** 第一次深挖某话题（无 W-clue 历史）→ 必须用 `clarify()` 走完整 A/B/C/D 选项，因为用户偏好未知。

**典型案例：** 2026-07-05 NYT AI扼杀经济——W-27-02 已追踪 7 天 + 0630日报定性分析#8 存在 + 无兄弟 excavation → 自动走 B，提案 6 维度，直接执行。

### 反模式（pitfalls）

- ❌ **不检测就默认全量执行** — 浪费 30+ 分钟产出与日报 90% 重叠的内容，用户被迫说"这不是我要的"
- ❌ **不提供决策路径直接问"做不做"** — 用户偏好路径选择题而非是非题（卷哥交互偏好）
- ❌ **声称"已存在 = 不需要再做"** — 用户可能仍需要更新数据源视角，正确做法是给增量维度的提案
- ❌ **不区分"兄弟 excavation" vs "日报覆盖"** — 两者意义不同：日报是来源记录，excavation 是已整合素材库，可能引用同一话题但角度不同

### 实战案例（2026-06-27 Stripe 经济学）

- **6/22**：Stripe Economics 报告首发 → 6/23 日报 P0#1 收录
- **6/26**：FourWeekMBA + Forbes 二次验证 → 6/26 日报 P0#1 + 选题一
- **6/27 同时段**：用户请求深度挖掘
- **6/27 已存在**：`pieter-levels-creator-economy/` 兄弟 excavation（引用 Stripe 数据但聚焦个人案例）
- **检测结果**：走 **B 增量路径**——聚焦 4 个新维度（Stripe 原报告全文 / Top decile 5 特征 / 4 类反欺诈论证 / 中国 OPC 反方）
- **产出**：`stripe-superindividual-economics/`（25.8KB topic_materials + 22.6KB deep_analysis_plan），与 pieter-levels 形成互补而非重复

### 🆕 实战案例（2026-07-04 同日双话题深挖）

- **场景**：用户在一次对话中连续请求深挖 2 个不同话题（`creative-industry-ai-trust-2026` + `gartner-skill-lifecycle-2026`）
- **当日同目录已存在兄弟 excavation**：`openai-eu-workforce-archetypes/` + `seven-ministries-ai-opc/`（其他兄弟话题）
- **第一次深挖流程**：30-60s 检测 → 全走路径 A（全量采集，无重复）→ 写入 `topic_materials.md` + `deep_analysis_plan.md`（共 30KB）
- **第二次深挖流程**：检测到第一篇已写 → 验证是不同话题（不是同一话题的兄弟版本）→ 路径 A → 写入第二份（27KB）
- **产出**：4 个 excavation 目录在同一日期（2026-07-04）共存——互不覆盖，分别服务于不同选题
- **关键学习**：同 session 多话题深挖**不应该复用兄弟目录**——每个话题的 topic_slug 是独立的，即使同一天也用独立目录。这与"兄弟 excavation 增量模式"（路径 B 用 `_v2`/`_incremental` 后缀）不同——后者是同一话题的增量，前者是不同话题的并行
- **批量操作注意事项**：每个 `write_file` 调用必须单独进行（飞书 DM session 中嵌入 heredoc/管道会被审批拦截）；本环境用 `write_file` 直接写最稳

### 🆕 实战案例（2026-07-05 单日 5 次深挖 · 全模型矩阵验证）

| # | 话题 | 路径 | 编译模型 | 产出 |
|---|------|------|---------|------|
| 1 | 创意产业 AI 焦虑 | A 全量 | 模型 A 悖论型 | 8K+12K |
| 2 | 技能生命周期 2-5 年 | A 全量 | 模型 B 框架型 | 13K+14K |
| 3 | 七部门 AI 一人公司 | B 增量 | 模型 C 政策型 | 15K+16K |
| 4 | NYT AI 扼杀经济 | B 增量（自动） | 模型 D 观点批判型 | 21K+17K |
| 5 | OpenAI 国有化 × 战后经济史 | A 全量 | **混合模型（跨时代对照）🆕** | 21K+18K |

**关键验证：**
- **模型覆盖扩展**：A/B/C/D + 跨时代对照混合模型 = 5 种模型在单日内全部被实战验证
- **用户素材优先整合**：第 5 个话题用户提供了 ~3000 字战后经济史预编译素材——联网搜索角色从"找素材"切换为"补充+验证"
- **跨时代对照话题特征**：锚点是当前事件（OpenAI 5%），论证主轴是历史数据（战后 26 年计划体制），编译结构为六维（事件全貌→历史纵深→学术辩论→跨时代矩阵→多方观点→四视角整合）
- **互补矩阵扩展为 5 维**：感觉(Marcus)/方法(Lily)/位置(Z)/资产(Alex)/规则(所有受众)

### 🆕 三层采集降级链（2026-07-05 实战整合）

topic_excavation 的 Step 1 必须先确认采集降级链——这是 hotspot-research 主 skill 已建立的，但 topic_excavation 之前未引用：

```
                主路径               降级1              降级2              降级3
中文采集：       豆包搜索       →    豆包+Tavily      →    AI HOT        →    跳过中文
英文采集：       MCP Brave      →    Brave 直连      →    Tavily        →    豆包搜索
原文提取：       web_extract    →    Jina Python     →    Jina curl     →    Tavily 摘要
                                          bypass              ⚠️ 付费墙 451
```

**关键约束：**
- 单次采集每类工具**最多尝试 3 次失败**——第 4 次失败必须切换降级
- Brave MCP 失败 3 次后**绝不再试**（已知 stdio 僵死问题，重试无意义）
- Jina Reader 付费墙 451 是**站点策略**，不是网络问题——直接走 Tavily+Brave 摘要交叉还原路径
- 主路径/降级1/降级2 失败后，写入 `/tmp/_excavation_failed_sources.json`，标注"本次采集不可用源"，避免下次重复踩坑

**与 hotspot-research 主 skill 的差异：** 主 skill 用于 cron 定时采集（450-500s 硬截止），降级速度优先；本 manual path 用于按需交互深挖（无时间限制），完整度优先——可以接受 Tavily 摘要还原 70% 论证链，而不是放弃 NYT 原文。

### 关键校准（卷哥工作风格确认于 2026-06-27 实战）

- **首次执行新话题**（日报/周报/excavation 均无覆盖）→ 默认 A 路径
- **已存在 1 篇日报或周报** → 默认 B 路径（避免重复）
- **已存在日报 + excavation** → 强烈推荐 B，提案 3-5 个真正增量维度让用户选
- **用户明确说"全量做"** → 走 A，但建议用日期后缀子目录避免覆盖兄弟 excavation
- **卷哥偏好**：执行前确认，确认后增量优先而非全量重做；问「增量维度」而非问「做不做」
- **🆕 clarify 工具交互模式（2026-07-04 验证）**：用 `clarify(choices=[...], question="...")` 呈现 A/B/C 三条路径。
  - 默认路径放第一个（`choices[0]`），标注"（推荐）"
  - question 中简要说明检测结果（如"0630日报已覆盖定性，但素材深度空白"）
  - 用户选择后立即执行，不二次确认

### 🆕 Git push 归档坑（2026-07-05 实战验证）

`topic_excavation` 产出物通常比日报小（15-25KB vs 40-50KB），但 git push 经常踩到 ref-lock 坑：

**症状：**
```
! [remote rejected] main -> main (cannot lock ref 'refs/heads/main':
  is at a80df84a63... but expected 620ae87ee2...)
error: failed to push some refs
```

**根因：** 本地分支比 origin/main 落后若干 commit（HTTPS push 间歇性失败后，其他工具曾成功推送），但工作树已干净——git 以为本地有新 commit 要推，实际是 origin 已经被推进了。

**修复：**
```bash
cd ~/hermes_workspace
git pull --rebase  # 通常显示 "Already up to date"
git push  # 显示 "Everything up-to-date" 表示成功
```

**反模式：**
- ❌ 用 `git push --force` 覆盖——会丢失其他会话的 commit
- ❌ 反复重试 `git push`——GFW 抖动是已知问题，重试不能改变 ref-lock
- ❌ 改 remote URL（HTTPS ↔ SSH）——ref-lock 与协议无关
- ❌ 误以为 commit 失败——实际上 `git commit` 成功了，只是 push 失败

**预防：** push 前先 `git status` + `git log --oneline origin/main..HEAD` 看本地是否有未推送 commit；如果本地干净但 push 失败，ref-lock 是首要怀疑方向。

---

## 手动执行三步法

### Step 1：多源联网采集（替代 skill 自动采集）

```
1. MCP Brave Search — 3-5 组关键词，覆盖：
   a) 核心数据源（如 "Pew 2026 AI survey data skepticism"）
   b) 学术理论框架（如 "AI opposition root causes psychology philosophy"）
   c) 结构性推力（如 "why people compelled to use AI FOMO workplace pressure"）
   d) 关联悖论（如 "AI adoption vs opposition paradox cognitive dissonance"）
   e) 中文补充（如 "AI 民意调查 反对原因 2026"）

   ⚠️ Brave MCP 僵死快速诊断（2026-07-04 多次验证）：
   当连续 3 次返回 "fetch failed" 时，不要重试——这是 stdio 管道断裂
   （进程运行 >1 周的已知问题，修复需 `hermes mcp test brave-search`）。
   立即切换到豆包搜索 + Tavily 双源，不阻塞采集流程。
   不要在同一轮中调用第 4 次 Brave MCP——每轮 3 次失败后必须切换。

2. 🆕 豆包搜索（byted-web-search）——中文话题的主力源：
   当话题涉及中国政策/企业/市场时，豆包搜索是第一优先级中文源：
   - 对中文政策文件的覆盖（人民网/央广网/法治网/政府网站）远超 Brave/Tavily
   - 权威来源标注（S/A/B 评级）可直接用于来源审核
   - 执行：cd ~/.hermes/skills/byted-web-search && python3 scripts/web_search.py "关键词" --time-range OneWeek --count 10
   - 通常 3-5 组关键词并行调用，覆盖不同角度

3. Tavily 搜索——英文深度补充：
   用于国际视角和海外对比，与豆包搜索形成中英文双覆盖。
   python3 ~/.hermes/skills/tavily-search/scripts/tavily_search.py -q "query" --topic news --days 7 -n 10

4. 关键报告全文提取：
   【首选】web_extract（最多5个URL并行）— 返回markdown，成功率远高于Jina Reader
   【降级】Jina Reader: curl -sL "https://r.jina.ai/{REPORT_URL}" -H "Accept: text/markdown" -o /tmp/jina_report.md
   【再降级】Python bypass（见 jina_ssl_bypass.md）
   ⚠️ Jina Reader 频繁超时（exit 28）时直接切换 web_extract，不要反复重试——已验证 5 个 URL 并行提取全部成功
   ⚠️ 中国政府网站（gov.cn）Jina Reader 经常超时——不阻塞，用豆包搜索返回的媒体解读替代原文
   🆕 验证数据（2026-07-04 创意产业+技能生命周期双话题）：Jina Reader 对全部 5 个 URL 超时（exit 28），web_extract 成功提取 Creative Boom(882人调查)、Envato(1,780人报告)、虎嗅、Humbl Design、Clutch、Gartner、IT-Online、HCAMag、Performance+、Medium 共 10 篇文章，零失败

   🆕 **WordPress 博客 URL 发现技巧（2026-07-08 BAIR Blog 实战验证）**：WordPress 博客的文章 URL slug 在首页上常被截断（如 "Intelligence is Free, Now What?" → slug 可能为 `intelligence-is-free-now-what/` 而非 `intelligence-is-free/`）。当 browser navigate 返回 404 时：
   1. 用 `curl -sL "{BLOG_URL}/YYYY/MM/DD/"` 列出该日期的目录索引（Apache/Nginx 默认开启时有效）
   2. 或 browser navigate 到博客首页，从 `<a href>` 中提取完整 slug
   3. BAIR Blog 案例：首页 slug 为 `intelligence-is-free/` → 实际 URL 为 `/blog/2026/07/07/intelligence-is-free-now-what/`——截断发生在首页摘要，完整 URL 在目录索引中
   - **不适用场景**：静态站点（无目录索引）、自定义路由（非 /YYYY/MM/DD/ 结构）

   ⚠️ **🆕 NYT/Atlantic/Bloomberg/WSJ 等付费墙 geo-block（HTTP 451, 2026-07-05 验证）**：
   - 症状：Jina Reader 返回 `SecurityCompromiseError: Anonymous access to domain www.nytimes.com blocked`
   - 根因：Jina 的 IP 信誉池把 NYT/Atlantic 标记为需付费墙保护的站点
   - **不是网络问题**，不是配置问题——是该站点的反爬策略
   - **恢复路径（已验证，2026-07-05 NYT 深挖）：**
     1. Tavily 的 AI 摘要 + Brave description 交叉还原论证链（HTTP 451 不影响 Tavily/Brave 摘要层）
     2. 用 Tavily 答案字段的 `answer` 直接提取核心论点
     3. 用 Brave 直连 description 字段提取关键引语
     4. 同时尝试其他 4 篇相关文章（同一事件的二级报道，如 Semafor/Axios 转载 BIS 报告）——这些通常没有付费墙
     5. 信息完整度可接受 60-70%（论证结构清晰 + 关键引语保留），不需要 100% 全文
   - **反模式**：重试 Jina Reader / 换不同 Jina endpoint —— 都是浪费时间，付费墙是站点策略不会因为重试而放开
   - **典型案例（NYT AI扼杀经济）**：NYT 原文 451 → Tavily+Brave 还原 70% 论证 → Semafor/Axios/Atlantic/Man Group 4 篇替代源全部成功 → 总信息完整度达 80%+

5. 关联报告补充：
   - 追踪被核心报告引用的关联数据源（如 Stanford HAI AI Index）
   - 搜索报道核心报告的权威媒体（Forbes/CNET/The Verge 等）

6. 🆕 用户提供素材优先整合（2026-07-05 OpenAI国有化实战验证）：
   当用户**直接提供了丰富的预编译素材**（如视频内容总结、研究报告摘要、长文分析）时：
   - 用户素材 = 第一优先级信源（权重 > 联网搜索结果）
   - 联网搜索的角色从"找素材"切换为"补充+验证"：
     a) 验证用户素材中的关键数据点（交叉检查数字/日期/引用）
     b) 补充用户素材中缺失的维度（反方观点/中国版对照/最新进展）
     c) 用学术来源/权威媒体为用户的论点提供额外支撑
   - topic_materials.md 中明确标注"用户提供素材"vs"联网补充素材"
   - deep_analysis_plan 中用户素材作为论证主轴，联网补充作为旁证
   - 反模式：把用户素材当"一条普通搜索结果"处理——用户花时间整理的素材，权重应远高于一条 Brave snippet
   - 典型案例：OpenAI国有化话题——用户提供战后经济史完整分析（~3000字），以此为历史对照轴，联网搜索补充 OpenAI 5% 事件细节 + 学术辩论 + 中文视角
```

### Step 2：结构化编译（替代 topic_materials_compilation 自动提取）

```
按 material-reserve-workflow.md 的 5+3 模型编译元素材储备文档：

五层理性论证：
  1. 数据事实层 — 核心调查数据的完整呈现
  2. 行为驱动层 — 解释"为什么用"的结构性推力
  3. 认知机制层 — 解释"为什么反"的心理机制
  4. 结构归因层 — 从个人到社会的视野拉升
  5. 存在论层 — 最深层的哲学根基

三层荒诞行为（可选，增强传播力）：
  6. 决策层荒诞 — 精英叙事与公众感知的矛盾
  7. 成本层荒诞 — 经济逻辑的自我矛盾
  8. 制度层荒诞 — 组织规则制造的行为扭曲

输出格式：topic_materials.md（见 material-reserve-workflow.md 模板）
```

#### 🆕 话题类型适配：两种编译模型（2026-07-04 实战验证）

不同话题类型需要不同的素材编译结构。一刀切用 5+3 模型会导致某些话题"被强行套入不匹配的框架"。

**模型 A：悖论/行为分析型（适用 5+3 原版）**

触发条件：话题核心是"用但反"式的行为悖论（如 Pew 调查、创意产业异化）
- 五层理性论证 + 三层荒诞行为完整展开
- 核心驱动：解释"为什么行为数据和态度数据方向相反"
- 典型案例：Pew 悖论（"用 AI 但反对 AI"）、创意产业异化（"用不信任的工具"）

**模型 B：框架/分类诊断型（5+3 简化变体）🆕**

触发条件：话题核心是一个分类框架或诊断工具（如 OpenAI 四原型、Gartner 技能生命周期分类）
- 五层论证以**框架本身的结构**为组织主轴（而非从数据到存在论的线性递进）
- 三层荒诞行为**可选跳过**——分类框架的"荒诞"通常体现在反直觉发现（如失业悖论），而非行为矛盾
- 补充话题围绕**框架的关键维度**展开（如人类必要性、需求弹性、能力悬垂），而非围绕"为什么反"
- 四视角整合分析（叙事/心理/人类学/产品）**必须保留**——这是 SOUL 的差异化锚点
- 典型案例：OpenAI 四原型（框架即诊断工具）、Gartner 技能生命周期（分类即核心洞察）

**选择决策树：**
```
话题核心是"行为悖论"、"分类框架"、"政策/机会事件"、"观点/批判"、"事件+数据混合"、"信号分析"、"数据趋势/结构性转折"还是"跨时代对照/历史类比"？
    ├── 行为悖论 → 模型 A（5+3 完整版）
    │     例：Pew 调查、创意产业调查
    ├── 分类框架 → 模型 B（框架主轴 + 补充话题 + 四视角）
    │     例：OpenAI 四原型、Gartner 技能分类
    ├── 政策/机会事件 → 模型 C（增量维度 + 历史脉络 + 实操路径）🆕
    │     例：七部门AI一人公司、中国AI产业政策
    ├── 观点/批判 → 模型 D（多视角三角 + 历史类比 + 反直觉翻转）🆕 2026-07-05
    │     例：NYT "AI扼杀经济"、BIS "AI泡沫警告"
    ├── 事件+数据混合型 → 模型 E 🆕 2026-07-08
    │     例：Claude Cowork云化+120万条使用数据揭示范式转移
    │     特征：产品发布+伴随使用数据，数据推翻行业共识→范式转移
    │     编译策略：核心数据矩阵（5张表）+ RIVET三层递进（详见 references/model_e_event_data_hybrid.md）
    │     关键：数据反直觉是核心叙事引擎——"行业喊X，数据说Y"
    ├── 信号分析型 → 模型 F 🆕 2026-07-08
    │     例：微软MAI替换OpenAI/Anthropic——大企业AI消费降级
    │     特征：事件锚点本身信息量不大，但结构信号极强——标志一个趋势转折
    │     编译策略：五层递进（事件→技术→商业→行业→信号）+ 跨行业证据矩阵（详见 references/signal_analysis_model.md）
    │     关键：受众反应不是"我知道了"而是"这对我的决策意味着什么？"
    │     反直觉翻转："不是AI退潮，是AI太行了所以必须便宜下来"
    ├── 数据趋势/结构性转折 → 模型 G 🆕 2026-07-08
    │     例：AI推理成本年降50倍→个体与组织起跑线拉平
    │     特征：核心驱动是数据趋势（多源交叉验证的定价曲线）而非单一事件或框架
    │     编译策略：五维结构——核心事实→数据事实层(时间线)→驱动力层→反力层→个体×组织含义
    │     关键：不是解释"为什么发生"（驱动力层），而是揭示"发生之后权力结构如何变化"（含义层）
    │     SOUL适配：第四部分从"反刍恐惧"→"反刍方向校准"——不是安抚焦虑而是重新校准价值坐标
    └── 跨时代对照/历史类比 → 混合模型 🆕 2026-07-05
          例：OpenAI国有化 × 战后经济史对照
          特征：话题锚点是当前事件，但论证框架依赖历史数据作为主要论据轴
          编译策略：六维素材结构（事件全貌→历史纵深→学术辩论→跨时代矩阵→多方观点→四视角整合）
          deep_analysis_plan 适配：七段式保留，第二部分从"推力+机制"→"历史纵深对照轴"，
          第三部分从"结构归因"→"反方观点+关键区分"，第五部分保留反直觉翻转 + ZPD 行动
          关键：跨时代对照话题的情感弧线核心是"历史押韵感"——"1971年的人也看不懂，你现在看不懂是正常的"
```

**🆕 模型 D：观点/批判型（2026-07-05 NYT AI扼杀经济实战验证）**

触发条件：话题核心是主流媒体/权威机构的**批判性观点**（如 NYT Opinion、BIS 年报、IMF 警告、央行行长发言），而非新数据/新政/新框架
- 不使用 5+3 模型——批判型话题的核心不是"恐惧层次"，是"论证结构"
- 不使用框架主轴——批判型话题的命题通常是"X正在做Y坏事"，不是"X提供了分类工具"
- **多视角三角结构**：围绕核心命题，建立 [正方论证 / 反方反驳 / 综合判断] 三方论证网
- **常见维度池**（按需选取 4-6 个）：
  - 原文论证链完整还原（核心论点/数据锚点/关键引语）
  - 量化数据交叉验证（多家机构/多份报告/多个数据点）
  - 关联机构报告串联（BIS/IMF/Goldman/McKinsey/Atlantic——多个权威源共振）
  - 中国版对照（同一现象的中国数据/视角）
  - 反方观点系统化（拥护者如何反驳、为什么他们也合理）
  - 历史类比（铁路泡沫/互联网泡沫/电力泡沫——技术革命的历史规律）
- deep_analysis_plan 适配：
  - 七段式结构保留，但内容替换：
    - 引子：批判性观点+多家权威源并排引用
    - 第一部分：四层递进拆解（资金/人才/土地/芯片，或类似 4-layer 结构）
    - 第二部分：揭示推力——为什么是现在？用 BIS 历史规律 + Acemoglu 定向技术进步
    - 第三部分：结构归因——不是你的焦虑出了问题（集体分离阶段 + Token源头）
    - 第四部分：反刍——重命名情绪 + **反直觉翻转**（批判型话题的核心情感转折点）
    - 第五部分：ZPD 行动——在"被挤出"中找到"不可挤出"的资产
  - 关键：批判型话题的 **反直觉翻转** 是情感弧线的核心——从"AI在毁掉一切"翻转到"泡沫期是个体最好的时候" / "穿越周期的不是最聪明的投资者"
- 典型案例：NYT AI扼杀经济（2026-07-05），6增量维度：
  ①NYT原文论证链 ②挤出效应量化数据 ③BIS/IMF等机构关联 ④中国版对照 ⑤反方三角 ⑥历史类比

**🆕 模型 C：政策/机会型（2026-07-04 七部门OPC实战验证）**

触发条件：话题核心是一个政策发布/行业事件，对受众有直接行动影响（如"国家发文了，你该怎么做"）
- 不使用 5+3 模型——政策话题没有"恐惧层次"和"荒诞行为"
- 不使用框架主轴——政策话题的核心是"事件拆解"而非"分类诊断"
- **增量维度模型**：围绕话题识别 3-5 个真正增量的维度（vs 日报已覆盖的"定性定调"），每个维度独立成章
- **常见增量维度池**（按需选取 3-5 个）：
  - 政策原文拆解（文号/日期/部门/条款/治理逻辑）
  - 地方配套案例（各城市具体政策对比）
  - 历史演进脉络（相关政策的演进时间线，提供"为什么是现在"的纵深）
  - 实操路径展开（启动步骤/成本拆解/工具推荐/最小行动）
  - 全球对比（中国 vs 海外同类政策，提供坐标系）
  - 反方/风险（政策落地的不确定性、已有质疑）
  - 数据验证（政策的量化影响——多少人已受益？增长速度？）
- deep_analysis_plan 适配：
  - 七段式结构保留，但内容替换：
    - 第一部分从"逐层解剖恐惧"→"政策逐条拆解"
    - 第二部分从"推力+机制"→"地方竞赛+实操逻辑"
    - 第三部分从"结构归因"→"历史纵深（政策演进脉络）"
    - 第五部分保留 ZPD 行动框架（政策型话题的行动转化率天然高）
  - 关键：政策型话题的 **行动转化率** 是最核心指标——受众看完要知道"我今天能做什么"
- 典型案例：七部门AI一人公司（2026-07-04），5增量维度：
  ①政策原文拆解 ②地方配套案例 ③46年历史演进脉络 ④实操路径（启动<5000元+10个项目） ⑤全球对比

**模型 B 的 topic_materials.md 结构模板：**
```markdown
## 🔥 核心信息（框架概述表格）
## 框架详解（每个类别一个章节，含数据+机制+受众镜像+翻转）
## 框架维度（框架背后的关键变量，每个一个章节）
## 📎 补充话题（围绕关键维度的深度展开，5-8个）
## 🔗 关联矩阵（ASCII 图展示话题间关系）
## 🎯 SOUL 四视角整合分析（叙事/心理/人类学/产品）
## 📡 线索追踪
## 🔖 素材来源索引
```

**反模式：**
- ❌ 对框架型话题强行套用"八层恐惧分析"——框架型话题没有"恐惧层次"，有"分类维度"
- ❌ 跳过四视角整合——不管什么类型，SOUL 四视角是产出物的差异化锚点，不可省略
- ❌ 把模型 B 当作"简化版"——它是"适配版"，不是偷懒版。框架型话题的补充话题数量和质量要求不低于悖论型

### Step 3：深度分析文档设计（替代 skill 自动生成方案）

```
基于 deep-analysis-plan-template.md（soul skill 的 reference）生成文档设计方案：

核心结构（七段式 + 双核心螺旋）：
  引子（场景爆破）
  → 第一部分：为什么反？（多层逐层解剖）
  → 第二部分：为什么离不开？（推力+机制）
  → 第三部分：结构根源（阈限期+场域）
  → 第四部分：反刍时刻（正常化+重命名）
  → 第五部分：出路（ZPD内行动建议）
  → 尾声（螺旋回环钩子）

输出格式：deep_analysis_plan.md（见 soul/references/deep-analysis-plan-template.md）
```

---

## 产出物目录结构

```
reports/hotspot/topic_excavation/{YYYY-MM-DD}/{topic_slug}/
├── topic_materials.md          # 元素材储备（Step 2 产出）
└── deep_analysis_plan.md       # 深度分析设计方案（Step 3 产出）
```

### 命名规范补充（增量模式专属）

当走 B 路径增量深挖时，建议在目录名加 `_v2` / `_incremental` 后缀，便于和兄弟 excavation 区分：

```
# 兄弟 excavation（同日同话题不同视角）
reports/hotspot/topic_excavation/2026-06-27/pieter-levels-creator-economy/
# 增量 excavation（聚焦新维度）
reports/hotspot/topic_excavation/2026-06-27/stripe-superindividual-economics/

# 命名约定：topic-slug 应明确包含核心视角差异
# ✅ pieter-levels-creator-economy（个人案例视角）
# ✅ stripe-superindividual-economics（统计学硬实视角）
# ❌ solopreneur（太泛，无法区分）
# ❌ 2026-06-27-stripe（日期已在父目录，重复）
```

---

## 与现有工作流的关系

| 组件 | 角色 | 状态 |
|------|------|------|
| `topic_materials_compilation.md` | 从日报库提取已有素材 | ✅ 已存在 |
| 本文件（手动执行路径） | 绕过缺失 skill 的过渡手册 | ✅ 本文件（含重复覆盖检测） |
| `deep-analysis-plan-template.md` | 文档设计方案模板 | ✅ 已存在（soul skill） |
| 🆕 `references/model_e_event_data_hybrid.md` | 模型 E：事件+数据混合型编译指南 | ✅ 新增（2026-07-08 Claude Cowork 实战） |
| 🆕 `references/signal_analysis_model.md` | 模型 F：信号分析型编译指南 | ✅ 新增（2026-07-08 微软MAI消费降级实战） |
| `hotspot-topic-excavator` skill | 自动化上述三步的独立 skill | ❌ 待创建 |
| 🆕 `references/duplicate_coverage_decision_matrix.md` | 重复覆盖决策矩阵 + 增量维度提案模板 | ✅ 建议下次会话创建 |

当 `hotspot-topic-excavator` skill 创建完成后，本文件标记为 `[DEPRECATED]` 归档。**新创建的独立 skill 应内置「重复覆盖检测」作为第一步骤**，避免本会话实战中发现的"用户被迫选路径"问题再次发生。