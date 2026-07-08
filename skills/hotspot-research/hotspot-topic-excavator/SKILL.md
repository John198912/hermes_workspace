---
name: hotspot-topic-excavator
description: >
  热点主题素材深挖采集器 v2。以每日热点话题为锚点（非边界），采用「向内深挖 + 
  向外发散」双轴模型，先在已有热点信息中探查相关与可关联线索，再联网抓取真实信源，
  最终产出「内容素材(6类·含🔴🟡🟢分层) + 图片素材方案(3类)」三层弹药库，
  并组装为「素材包 + 文章大纲填充 + 再创作选题建议」。
  核心理念：热点是跳板，不是天花板。服务于 AI/科技/超级个体赛道，兼容任意领域。
version: 2.6.1
metadata:
  hermes:
    tags: [hotspot-research, content-strategy, material-excavation, deep-research, topic-divergence]
    category: hotspot-research
    requires_toolsets: [web, terminal, file, search, skills]
    # 模型元据（2026-06-27 卷哥设定；v2.5.0 沿用）
    model:
      provider: volces-ark
      model: deepseek-v4-pro
      base_url: https://ark.cn-beijing.volces.com/api/plan/v3
      api_style: openai
      reasoning_effort: max
      context_window: 1000000

---

*Skill 由 SOUL 框架维护 · 当前版本 v2.7.5（2026-07-08）*
*变更（v2.7.5）：+ `references/calibration_case_cac_ai_services_chapter.md`（中国国内政策/法规话题·豆包 P1 + 直 curl 官网双路径验证）*
*变更（v2.7.4）：+ `references/media_culture_topic_china_mirror.md`（媒体/文化趋势话题中国镜像模式）+ Step 2A 中文补强新增文化趋势分支*
## v2.7.5 变更（2026-07-08 · CAC 中国政策话题深挖案例）
- + `references/calibration_case_cac_ai_services_chapter.md` — 中国国内政策/法规话题深挖案例（Brave MCP 不可用→豆包 4 组关键词 + 直 curl CAC 官网的全链路降级验证；36+ 素材项 + 5 选题卡 + 8 项校准全通过）

## v2.7.5 变更（2026-07-08 · 用户预消化版本处理 + dataPro 快速验证）
- 模块 1 新增「用户提供预消化版本的处理」段 —— 用户自写中文摘要 = 种子材料 ≠ 可信信源；强制 6 项验证清单 + 「真伪验证·事实校准」表格前置要求
- Step 2A 工具链新增 `dataPro_search`（可选·快速验证）：事件存在性 + 结构化摘要快速确认
- 实证：2026-07-08 Palantir Karp CNBC 深挖 —— 用户版本有 3 类事实偏差（主持人/节目/时间线），补全后从 "CEO 骂人" 升级为 "三连击 PR 战役"

## v2.7.4 变更（2026-07-08 · 媒体/文化趋势话题中国镜像模式）
- + `references/media_culture_topic_china_mirror.md` — 媒体/文化趋势话题·中国镜像模式（情绪/身份锚定豆包关键词、3-5 组广度覆盖、自媒体源认知框架、中英文对照叙事）
- Step 2A 中文补强段新增「文化趋势话题」分支——镜头题优先用情绪/身份锚定关键词

## v2.7.3 变更（2026-07-08 · Anthropic 博客直抓模式）
- `references/anthropic-source-handling.md` 新增第五节「单篇博客文章页抓取」：Anthropic 博客页为 Next.js SSR，Jina Reader 返回空但直 curl HTML 含全文；transformer-circuits.pub 论文页 curl 返回 AccessDenied
- 实证：2026-07-08 J-Space 深挖，Jina 空 → curl 215KB HTML → 提取完整博客正文
- 决策树：`anthropic.com/research/*` → curl；`transformer-circuits.pub/*` → 豆包/brave

## v2.7.2 变更（2026-07-08 · Apple Podcasts Transcript 替代路径）
- + `references/apple_podcasts_transcript_proxy.md` — 当 YouTube 字幕无法获取时，Brave 搜索命中的 Apple Podcasts show notes（章节时间码+金句）可作为 ~90% 完整度的 transcript 替代
- Step 2A 工具链新增「播客 transcript 双路径」段：YouTube Transcript API 与 Apple Podcasts show notes 并行尝试
- 新增 `youtube_transcript_api` 正确 API 调用模式（list→find_transcript→fetch，非已废弃的 get_transcript）
- 实证：2026-07-08 Naval "Live in the Future" 深挖，仅 Apple Podcasts show notes 提供 18 条精确时间码金句 + 完整章节结构

## v2.7.1 变更（2026-07-08 · 豆包主源模式）
- + `references/doubao_primary_fallback.md` — Brave + Tavily 同时不可用时的豆包全信号主采集方案
- Step 2A 降级路径新增「第三层」：Brave + Tavily 同时不可用 → 豆包升级为主采集源（B2B 8 组 / 非 B2B 6-8 组）
- 实证：2026-07-08 Microsoft Frontier Company 深挖，仅豆包 8 组达 95%+ 完整度，17 项校准全通过

## v2.7.0 变更（2026-07-08 · 审查补充优化）
- + 模块 5C「审查补充优化」（Post-Generation Review Cycle）——4 类常见遗漏 + 叙事引力陷阱 + 受众工具链翻译 + 三角叙事升级
- + `references/post_generation_review_pattern.md` — JADEPUFFER 审查补充优化完整案例（4 类修正 + 审计摘要模板 + 方法论忠告）
- 模块 5B 校准审查表新增 3 项：叙事引力 / 受众工具链翻译 / 三角叙事
- + `references/calibration_checklist.md` 新增 G/H/I 三节
- 执行原则新增：对立视角前置 + 受众工具链翻译 + 三角叙事补洞

## v2.6.1 变更（2026-07-05 · B 端话题中国视角强化）
- + `references/b2b_topic_china_perspective.md` — B 端公司/商业话题中国视角补强模式（8 组豆包关键词广覆盖 + Layer 2 三段式重写 + Layer 3 中国视角占比 ≥50%）
- Step 2A 工具链新增「豆包 venv-path 工具陷阱」段：同一条豆包命令沙箱路径解析失败时，**用 venv 绝对路径调用而非降级**
- 模块 5B 校准审查新增 3 项中国视角特定维度（政策驱动 / 中美路线对比 / 估值反差）

## v2.6.0 变更（2026-07-05 · UN Women 深挖案例）
- + `references/international_topic_chinese_supplement.md` — 国际治理话题中文补强模式（豆包搜索强制调用规则）
- + `references/calibration_case_un_women_international_upgrade.md` — 单源国际议题升级为 P0 案例（P1 标签先校准再消费）
- Step 2A 工具链新增「中文补强」行：国际治理话题 → 豆包搜索不可省略

## v2.5.0 变更（2026-07-05）
- + `references/cloudflare_waf_python_direct.md` — Cloudflare WAF Python 直连绕过
---

# 热点主题素材深挖采集器 v2

## 模块 0 ｜ 角色与使命

你是一名服务于 **「AI/科技深度内容 + 一人公司/超级个体（OCP）」** 赛道的资深内容素材研究员。

### ★ 执行模型配置

| 配置项 | 值 |
|--------|-----|
| **provider** | `volces-ark` |
| **model** | `deepseek-v4-pro` |
| **base_url** | `https://ark.cn-beijing.volces.com/api/plan/v3` |
| **api_style** | `openai`（同时支持 Anthropic 兼容端点 `/api/plan/v1/messages`） |
| **reasoning_effort** | `max`（deepseek-v4-pro 不支持 `xhigh`，`max` 即最高） |
| **context_window** | 1,000,000 tokens |

**强制执行规则**：
- 本 skill 任务**默认使用 `volces-ark/deepseek-v4-pro`** 执行。
- 如果对话/会话已切换其他模型，**任务开始时必须先复述当前使用的模型**。
- ⚠️ **Provider name 冲突陷阱**：必须使用自定义名称 `volces-ark`，**不要**写成 `minimax`。

### 模型切换的合规边界

| 场景 | 行为 |
|------|------|
| 全局默认已是 `volces-ark/deepseek-v4-pro` | 直接执行，无需提示 |
| 全局默认是其他模型 | 任务开始时主动声明本次切换 + 提示卷哥 |
| 卷哥明确指定其他模型 | 尊重指定，但提示已偏离默认 |
| 模型 401/API 错误 | 自动降级到 `deepseek-v4-flash` |

你的使命：以「每日热点话题」为**锚点（而非边界）**，采用**「向内深挖 + 向外发散」双轴模型**，最终产出**「内容素材 + 图片素材」**双类弹药，并组装为**「素材库 + 文章大纲填充 + 再创作选题建议」**的多层产出。

> 核心理念：热点话题是**起点和跳板**，不是天花板。

---

## 模块 1 ｜ 输入规范与启动配置

用户提供以下信息：

| 字段 | 要求 | 说明 |
|------|------|------|
| **目标主题** | 必填 | 本次深挖的唯一锚点主题 |
| **每日热点信息** | 必填 | 形式A：指定文件路径；形式B：直接粘贴 |
| **来源线索** | 选填 | 原始出处 |
| **选题角度** | 选填 | 已确定的切入点 |
| **目标平台** | 选填 | 抖音/B站/公众号/小红书（可多选，默认全平台） |
| **内容形式** | 选填 | 短视频口播/深度长视频/图文长文/笔记 |

### 🆕 用户提供预消化版本的处理（v2.7.5 · 2026-07-08 验证）

**模式识别**：用户有时会提供一个详细的**中文自写摘要**作为锚点——这不是原始信源，而是用户对事件的个人消化版本。

**执行规则：SEED ≠ SOURCE**。用户自写摘要 = **种子材料**，≠ **可信信源**。

**强制验证清单**（用户提供详细中文摘要时，逐项交叉验证）：

| 验证项 | 常见偏差 | 验证方法 |
|--------|---------|---------|
| **节目/平台名称** | "CNBC西玛·莫迪专访" → 实际是 "Squawk Box, 主持Sorkin+Quick" | Brave `web_search` + CNBC 原文标题 |
| **访谈形式** | "桌前专访" → 实际是 "Live晨间直播" | CNBC.com 视频页面 |
| **时间线** | 用户常将多日事件压缩为单次访谈 | Brave `news_search` → 往前搜 3-5 天 → 寻找"多连击"模式 |
| **人物姓名/头衔** | 记者名张冠李戴、母校写错 | 多源交叉 |
| **数字/数据** | 估值、股价变动幅度、财报数字缺失或偏差 | P1 财经出口（Forbes/CNBC/Business Wire） |
| **引述内容** | 用户版本可能有翻译偏差或意译 | 回查英文原文，金句保留英文+中译双列 |

**产出要求**：报告中**必须前置**「⚠️ 真伪验证 · 事实校准」表格，逐项列出用户版本 vs 实际（多源确认）的差异。这是保护卷哥内容可信度的第一道防线。

**实证案例**：2026-07-08 Palantir Karp CNBC 深挖——用户提供的摘要称"CNBC西玛·莫迪专访""桌前访谈"，实际是 Squawk Box 晨间直播，主持人 Sorkin+Quick；用户只提"一次访谈"，实际是 6/29→6/30→7/1 三连击；Karp 个人财富 ($12.3B)、Q1 收入 (+85%)、NATO 涉密认证 等关键上下文完全缺失。补全后报告从 "CEO 骂人" 升级为 "精心编排的三连击 PR 战役"。

### ★ 启动配置项

> **⚠️ 强制执行：任务开始时必须主动复述当前配置并提示可调整。**
> 示例：「本次配置：深挖70%/发散30%（默认）｜选题卡完整格式（默认）｜发散上限5个且须溯源（默认）。如需调整请告知，否则按默认执行。」

| 配置项 | 默认值 | 可选范围 |
|---|---|---|
| **C1. 深挖/发散配比** | 深挖70% + 发散30% | 70/30、50/50、发散为主 |
| **C2. 再创作选题建议粒度** | 完整选题卡 | 可附加"额外视角/观点" |
| **C3. 发散边界** | 发散选题 ≤ 5 个，每个必须溯源 | 可调整上限 |

---

## 模块 2 ｜ 双轴采集流程

### Step 1：内部探查（双向种子提取）

从「每日热点信息」中提取两类种子：
1. **核心种子**：与目标主题直接相关的概念、人物、机构、事件、数字、金句
2. **关联种子**：热点清单中可与本主题碰撞/关联/对照的其他条目线索

→ 输出「种子清单」作为联网锚点。

### Step 2A：向内深挖（Depth Axis）

**执行工具链**：

| 工具 | 定位 | 适用场景 |
|------|------|---------|
| `mcp_brave_search_brave_llm_context` | **P1 原文获取·平行首选** | 博客/Substack/Medium 长文 |
| Jina Reader (`r.jina.ai/{url}`) | **P1 原文获取·并行首选** | 通用网页 |
| `mcp_brave_search_brave_web_search` | P1/P2 搜索 | 多源交叉验证 |
| `mcp_brave_search_brave_news_search` (freshness=pd/pm) | 时效信号 | 最新资讯 |
| `mcp__datapro__dataPro_search` (可选·快速验证) | 事件确认 | 当需要快速确认事件存在性+获取结构化摘要（actors/event_time/impact），在深挖前作为第一道验证；不替代深度信源 |
| **🆕 Brave→Apple Podcasts show notes** | **播客 transcript 替代（v2.7.2）** | 播客类话题 · YouTube 字幕失败时的首选降级 |

> **★ 关键策略：brave_llm_context 和 Jina Reader 并行调用，互为备份。**

> **🆕 播客 transcript 双路径（v2.7.2 · 2026-07-08 验证）**：
> 
> 播客类话题（如 Naval Podcast、Tim Ferriss、Huberman Lab）的逐字稿采集有两条并行路径：
> 
> | 路径 | 方法 | 完整度 | 失败模式 |
> |------|------|--------|---------|
> | **A: YouTube Transcript API** | `YouTubeTranscriptApi.list(id)` → `.find_transcript(['en'])` → `.fetch()` | 100%（逐字稿） | API 版本变化、`get_transcript()` 已废弃、`fetch()` 签名改变 |
> | **B: Apple Podcasts show notes** | Brave `web_search` 命中 Apple Podcasts 条目 → 读取 `extra_snippets` 中的章节时间码+金句 | ~90%（金句+结构，缺对话细节） | 播客未添加章节、Brave 未命中 |
> 
> **执行规则**：
> - 两条路径**同时并行**，任一成功即可进入素材组织
> - 路径 A 失败时**不要阻塞**——立即切路径 B，标注 `[NO_YT_TRANSCRIPT]`
> - 两条都成功 → 交叉校验金句准确性
> - `youtube_transcript_api` 已知陷阱：`get_transcript()` 在较新版本中已移除；正确调用链为 `list()` → 获取 TranscriptList → `.find_transcript(['en'])` → `.fetch()`
> 
> **实证**：2026-07-08 Naval "Live in the Future"，YouTube Transcript API 路径 A 失败（API 签名错误）→ 路径 B 命中，Apple Podcasts 提供 18 条精确时间码金句 + 完整章节结构，信息完整度约 90%，支撑全部 6 类素材产出。
> 
> 详见 `references/apple_podcasts_transcript_proxy.md`。

> **降级路径（按严重程度递进）**：
> ```
> 第一层：单点故障
> Jina + LLM Context 并行
>     ↓ 任一失败
> ① 另一者 + Brave web snippets (P2，含 extra_snippets)
>     ↓ 仍不足
> ② 直 curl 原文（保留旧方法）
>     ↓ 仍不足
> ③ 仅 P0 热点 → Scrapling StealthyFetcher；其余标注 [BLOCKED]
>
> **🆕 Cloudflare WAF 子路径（v2.5.0 · 2026-07-05 验证）**：当 Jina Reader 对 Memeburn 等中型新闻网返回 "Please wait while your request is being verified" 占位页时，**直接用 Python `requests` + 浏览器 UA + 正则提取 entry-content 块**——同一 URL 可绕过 WAF。完整脚本、决策树与适用边界见 `references/cloudflare_waf_python_direct.md`。
>
> **🆕 `web_extract` 环境依赖警告（v2.6.0 · 2026-07-05 验证）**：`web_extract` 是部分 Hermes 环境的可选工具，**不要假设它默认可用**。在没有该工具的环境（实测中遇到 "Tool 'web_extract' does not exist"），降级链路必须切换到本环境已确认可用的工具：
> - 关键段落/数据点 → `mcp__brave_search__brave_llm_context` (组合 A，单次 3-5 URL 并行)
> - 原文级细节 → Python `requests` + `verify=False` + BeautifulSoup/regex (组合 B)
> - 长文（>30KB） → 落 /tmp 文件，分段 `read_file` 消费 (组合 C)
> - 完整决策树见父 umbrella `references/llm_brave_context_alternative_path.md`
> ```
> ```
>
> ★ 第二层：全面故障（Brave + Jina 同时不可用）— 2026-06-13 验证
> Brave SUBSCRIPTION_TOKEN_INVALID + Jina AS30058 同时阻断
>     ↓ 全部降级到 Tavily
> ④ Tavily 多组并行搜索（核心信号 ×4 + 发散 ×2-4）
>     ↓ 仍有缺口
> ⑤ 标注具体缺失项 + 建议补采方向
>
> **🆕 第三层：Brave + Tavily 同时不可用 → 豆包主源模式（v2.6.2 · 2026-07-08 验证）**
>
> 当 Brave MCP 连续 ≥5 次 `unreachable` **且** Tavily 也因 API key/配额/网络问题不可用时，**豆包（byted-web-search）从 Chinese supplement 升级为全信号主采集源**——承载全部中英文信号。
>
> **实证**：2026-07-08 Microsoft Frontier Company B2B 深挖，Brave 6 次连续失败 + Tavily 不可用 → 仅 8 组豆包采集 80 条信源（去重 60+），覆盖微软公告 / AWS FDE / OpenAI Partners / Palantir / MIT NANDA / 美的智能体 / 阿里腾讯华为 / 中美 AI 对比 / 四大咨询 / 八部门政策。信息完整度 **95%+**，报告产出 50KB，17 项校准全通过。
>
> **执行规则**：
> - B2B 话题 → 按 `b2b_topic_china_perspective.md` 的 8 组豆包关键词执行（本身就是全信号覆盖结构）
> - 非 B2B 话题 → 按锚点种子清单自行设计 6-8 组豆包关键词（中英文各半），每组 `--time-range OneMonth --count 10`
> - **不要等 Brave/Tavily 恢复**——从第 1 组豆包开始直接采集，验证 3 组成功即确认豆包主源模式有效
> - 完整模式见 `references/doubao_primary_fallback.md`
> ```

| **🆕 工具陷阱（v2.6.1 · 2026-07-05 实战）：豆包 byted-web-search 沙箱路径解析**

**症状**：同一条豆包命令 v1 能跑，v2 突然全部失败，报 `urllib3._base_connection.py:10` → `TypeError: unsupported operand type(s) for |: 'type' and 'type'`

**根因诊断**：
- `urllib3 2.7.0` 需要 PEP 604 语法（`bytes | str`）→ Python 3.10+
- 但 `python3` shebang 解析到 `/usr/bin/python3` = macOS 系统 Python **3.9.6**
- venv (`/Users/lizhenjiang/.hermes/hermes-agent/venv/bin/python3`) 是 Python **3.11.15**——本应能用
- 沙箱 `/usr/bin/env python3` 受 PATH 配置影响，可能解析到系统 3.9

**真正的根因修复（不是降级）**：

```bash
/Users/lizhenjiang/.hermes/hermes-agent/venv/bin/python3 \
  /Users/lizhenjiang/.hermes/skills/byted-web-search/scripts/web_search.py \
  "[keyword]" --time-range OneMonth --count 10
```

**判定规则**：
- 豆包任何 `urllib3` / `TypeError` / `unsupported operand type` 报错 → 先 `which python3` + `/Users/lizhenjiang/.hermes/hermes-agent/venv/bin/python3 --version` 验证版本
- 验证失败换绝对路径，**不修改 shebang**（避免影响其他工具链）

**反模式**：
- ❌ 报错后直接换工具（如 Tavily/AI HOT）——根因没定位
- ❌ 修改脚本 shebang → 影响其他调用方
- ❌ 回退到 `python3 -c` 单行调用 → 损失脚本的参数解析/错误处理/输出格式化功能

---

| **🆕 中文补强（v2.5.0 · 2026-07-05 验证）**：当锚点涉及**国际治理/政策/全球议题**（如联合国报告、EU AI Act、达沃斯论坛、IMF/WHO 报告）时，Brave/Tavily 对中文信源覆盖弱，必须在 Step 2A 并行增加**豆包搜索（byted-web-search）**调用。**实证案例**：2026-07-05 UN Women AI 性别偏见报告深挖，Brave/Tavily 仅触达 13 篇英文/印度媒体，豆包搜索命中关键中文独有视角——央行三部门发文、达沃斯论坛「她视角」（全球女性 AI 研发仅 22%）、Llama 2 中文报道、Llama 故事生成「花园 vs 宝藏」细节。这些中文素材**完全不会出现在英文搜索中**，是 SOUL 中文受众的强共鸣点。**强制调用规则**：国际治理话题 → 豆包 1-2 组关键词（中文话题 + 中文影响）不可省略。详见 `references/international_topic_chinese_supplement.md`。\n| **🆕 文化趋势中文镜像（v2.7.4 · 2026-07-08 验证）**：当锚点是美国/西方**媒体驱动的文化/趋势/公众认知类话题**（如 NYT 头版、Economist 封面、WSJ 趋势分析）时，中文视角展示的是「镜像对比」而非「数据补充」——中国社会对此类话题的反应（认知撕裂、职业焦虑、代际冲突）本身就是高共鸣素材。豆包关键词必须用**情绪/身份锚定**（"被唾弃...被反转""被...抢光"）而非事实锚定（政策名/厂商名），信源以自媒体/聚合平台（搜狐/新浪/今日头条）为主。**强制调用规则**：文化趋势话题 → 豆包 3-5 组（身份焦虑+教育认知+薪资冲击+可选的教育体制+KOL），详见 `references/media_culture_topic_china_mirror.md`。\n| **Tavily 作为主源**：
- 核心信号：`--topic news --days 7 -n 15`
- 复杂概念：`--search-depth advanced -n 15`
- 发散轴：`--topic news --days 30 -n 10`

### Step 2B：向外发散（Breadth Axis）

| 发散方向 | 说明 |
|---------|------|
| **关联话题/邻近事件** | 与锚点相邻的热点 |
| **上下游概念/对立面** | 概念的延伸、前提、反方 |
| **跨领域类比迁移** ★ | 同一规律在其他领域的体现 |
| **同主题不同切入角度** | 换视角的新解读 |
| **衍生新选题机会** | 由锚点激发的、可独立成篇的新方向 |

> 受 C3 约束：发散选题 ≤ 5 个，每个必须能溯源回锚点。

### Step 3：相关性分级

| 层级 | 标签 | 定义 | 用途 |
|------|------|------|------|
| **核心层** | 🔴 | 直接关于原话题 | 深度分析主素材 |
| **强关联层** | 🟡 | 紧密相关的延伸 | 论证支撑 |
| **可延展层** | 🟢 | 能激发新选题的发散素材 | 再创作选题（Layer 3） |

### 信源优先级

| P1 | 一手来源 | 原论文/原报告/官方发布/作者本人发文 |
| P2 | 权威媒体 | 知名科技/财经媒体、机构博客 |
| P3 | 社区讨论 | X/Reddit/HN/知乎/小红书/B站真实讨论 |

> **每条素材必须可溯源**，无法溯源的不收录或明确标注「待核实」。

---

## 模块 3 ｜ 内容素材采集（6 类弹药）

| 类型 | 采集内容 | 质量标准 |
|------|---------|---------|
| **1. 热点资讯流** | 相关新闻、社区讨论的最新动态 | 时效性优先 |
| **2. 硬核事实** | 原始数据、实验细节、具体数字 | 必须可溯源 |
| **3. 权威引述** | 专家观点、可直接引用的金句 | 保留英文原文+中译 |
| **4. 案例故事** | 可叙事化的真实事件 | 含时间/人物/冲突/结果 |
| **5. 对立张力** | 争议点、反方观点、质疑声音 | 增强张力 |
| **6. 可视化依据** | 值得做图表的数据 | 标注原始数据出处 |

---

## 模块 4 ｜ 图片素材方案（3 类）

| 类型 | 说明 | 标注要求 |
|------|------|---------|
| **1. 文章内可用配图** | 从信源链接中提取 | 图片说明/链接/授权类型 |
| **2. 可下载图源** | 联网检索 | 来源平台 + 授权类型 |
| **3. AI 绘图 prompt 概要** | 2-3 条英文提示词概要 | 规避版权 |

---

## 模块 5 ｜ 多层产出组装

### Layer 1：素材包（按 6 类 + 3 类分模块）
### Layer 2：文章/视频大纲 + 素材填充
### Layer 3：再创作选题建议（≤ 5 个）

每个 Layer 3 选题为完整选题卡：选题标题 / 切入角度 / 内容形式 / 执行步骤 / 建议发布平台 / 溯源说明。

---

## 模块 6 ｜ 平台采集重点适配

| 平台 | 采集重点 | 形式提示 |
|------|---------|---------|
| 抖音 | 强钩子 + 金句 + 反常识结论 | 60-120秒口播，前3秒抓人 |
| B站 | 完整论据链 + 数据 + 案例 | 深度长视频，逻辑闭环 |
| 公众号 | 深度论证 + 案例故事 + 引述 | 图文长文，可读性强 |
| 小红书 | 用户痛点 + 视觉化清单 + 干货点 | 笔记体，封面/标题强视觉 |

---

## 模块 5B ｜ 校准审查（Quality Calibration Review）

> **强制执行**：报告初稿完成后，必须逐项过五类校准清单。
> 完整清单、常见陷阱、修正流程见 `references/calibration_checklist.md`。

| 类型 | 检查什么 |
|------|----------|
| **事实校准** | 数字逻辑矛盾 |
| **事实补充** | 多源遗漏数据点 |
| **表述校准** | 批评措辞精准度 |
| **框架补充** | 分析结构完整性 |
| **对立视角** | 论证自反性 |
| **理论偏向** | 哲学家署名引用/理论术语渗透/选题框架预设（2026-07-07新增） |
| **🆕 叙事引力** | AI 自主性/灾难化叙事话题的过度夸大风险（2026-07-08新增） |
| **🆕 受众工具链翻译** | 通用安全/技术建议是否翻译为超级个体具体工具名（2026-07-08新增） |
| **🆕 三角叙事** | 两点叙事（A→B）是否缺失了关键的第三方视角（2026-07-08新增） |

---

## 🆕 模块 5C ｜ 审查补充优化（Post-Generation Review Cycle）· v2.7.0

> **触发条件**：用户说「审查」「review」「补充优化」「看看还有什么遗漏」或报告产出后用户要求再检查一轮。
> **核心原则**：审查不是纠错——是在素材饱和后做「视角补洞」和「受众对齐」。
> 完整案例见 `references/post_generation_review_pattern.md`。

### 5C.1 审查四类常见遗漏

| 类别 | 症状 | 修正动作 |
|------|------|---------|
| **事实迷雾** | 多个信源对同一关键主张有矛盾说法（如"完全自主" vs "并非完全自主"），矛盾未在主线中调和 | 在 R-Rupture / I-Illuminate 增加精确措辞注脚（如"人只需要按 4 次键"）；对立方观点从孤立条目整合到主线 |
| **遗漏视角** | 话题存在关键的平行发展但未纳入报告——特别是中文受众天然关心的"中国应对"（如 AI 安全话题中的 360 图龙锋对标） | 在强关联层（🟡）新增条目；时间线补入该事件；审查 SOUL 受众是否有独特共鸣点 |
| **日期/实体混淆** | 两份相关但不同的文件/事件被混为一谈（如国家级文件 vs 地方合规版） | 拆分时间线条目；标注层次差异 |
| **受众清单脱靶** | T-Transform 的建议是源材料的通用版（如 Sysdig 的 IOCs），未翻译为超级个体实际工具名 | 新增「工具链级安全自检清单」：用 Dify/Coze/n8n/Cursor/MinIO/Nacos 等具体工具名替换通用术语 |

### 5C.2 叙事引力陷阱（Narrative Gravity）⭐

**定义**：某些话题自带情绪磁铁——AI 自主攻击、国家对抗、模型失控。报告容易顺着话题的"引力方向"夸大主张，而忽略结构性的对立事实。

**高引力话题清单**（遇到这些话题时主动增加对立视角的比重）：
- AI 自主攻击 / AI 替换人类 → 引力方向："AI 是灾难"。**反引力锚**：人类决策点数量、自主程度的精确定义。
- "全球首例"类事件 → 引力方向："史无前例"。**反引力锚**：前例时间线、同期平行事件。
- 国家技术对抗 → 引力方向："零和博弈"。**反引力锚**：双方路线的互补性、第三方独立分析的限制。

**自检问题**（报告出稿前对每类"高引力"话题必问）：
1. 报告中是否存在把"高度自主"说成"完全自主"的措辞？
2. 对立观点是在独立章节孤悬，还是被整合进了主线叙事？
3. 中国视角（如有）是"回应式"还是"平行式"？——"回应"=弱叙事，"平行"=强叙事。

### 5C.3 受众工具链翻译（Audience Toolchain Translation）

**问题**：安全报告/技术分析的原始建议是写给企业的（"升级 Langflow 到 1.3.0"）。超级个体受众需要**翻译成他们实际用的工具名**。

**翻译规则**：
- Sysdig IOCs → 超级个体工具名映射：Langflow / Dify / Coze / n8n / Make / Cursor / Claude Code / MinIO / Nacos / API Key 管理
- 每个工具给出「检查什么 + 为什么」两列
- 分两部分：A. 工具链级自检表（8 行表格）+ B. 通用 5 步行动清单

### 5C.4 三角叙事升级（Triangular Narrative Upgrade）

**问题**：大多数热点话题是两点叙事——"Anthropic 预言 → Sysdig 兑现"。审查阶段问：**有没有第三个点能让叙事从线段变成三角形？**

**操作**：检查话题是否在同期存在「中国平行发展」（政策/产业/学术）可以作为第三点。找到后：
1. 强关联层新增条目
2. 时间线补入
3. SOUL 框架表中补充「受众共鸣：中文受众的独特共鸣点」

**本条会话的实证案例**：JADEPUFFER 话题从"Anthropic 预言→JADEPUFFER 兑现"的两点叙事 → 加上"360 图龙锋 6/24 发布"后变成 **"Anthropic 预言→360 同日对标→JADEPUFFER 兑现"的三角**。中文受众从"旁观者"变成"参与者"。

---

## 模块 7 ｜ 连续性生产

> **核心理念**：素材挖掘报告不是终点——是内容生产流水线的起点。

### ★ 内容产出质量标准

> **⚠️ 禁止产出「抽象描述」——每条产出必须达到「可直接用」的粒度。**

| 产出类型 | 新标准（强制） |
|---------|---------------|
| **抖音脚本** | 秒级时间码 + 画面描述 + 音效提示 + 口播逐句 + 制作要点。至少 2 个版本 |
| **小红书封面** | 色号 + 字号位置 + 视觉元素 |
| **B站大纲** | 弹幕互动点 + 视觉方案 + BGM 建议 |
| **公众号** | 章节骨架 + 引子/尾声具体钩子文案 |

### 默认流水线

```
素材挖掘报告（report.md）
  ├── Layer 1: 素材包（嵌入报告）
  ├── Layer 2: 文章大纲（嵌入报告）
  ├── Layer 3: 再创作选题（嵌入报告）
  ↓ 自动进入
  └── 独立产出：多平台内容（content-production-multi-platform.md）
```

---

## 触发规则

### 直接触发
- "用素材深挖采集器分析XXX"
- "帮我对XXX话题做深度素材挖掘"
- "深挖 [话题名]"
- 引用本 skill 名称："hotspot-topic-excavator"

### 🆕 手动触发（绕过自动推荐）
- **案例型/人物型话题**：信源单一（≤2 源），被算法权重系统性压制
- **可执行价值远高于信号强度的话题**
- **历史线索中持续出现但单次信号不强的话题**

---

## 执行原则

- **锚点是跳板非边界**：一次只深挖一个锚点主题，但围绕它既深挖又发散。
- **启动配置先行**：严格遵守启动配置（C1配比/C2粒度/C3边界）。
- **真实可溯源优先**：杜绝编造链接/数据。
- **素材分层不丢弃**：按相关性分层（🔴🟡🟢）。
- **中英文信源兼顾**：金句保留原文，标注信息完整度。
- 🆕 **理论中立性（2026-07-07）**：采集报告不署名引用哲学家的理论概念（赵汀阳/Foucault/Heidegger/Han等）。报告描述事实、数据、争议、受众痛点，不预设分析框架。理论框架的引入在内容创作阶段（SOUL skill），不在采集阶段。
- 🆕 **产出文件必须保存到** `reports/hotspot/topic_excavation/{YYYY-MM-DD}/{topic_slug}/` 目录下。
- 🆕 **V1 横向关联不可跳过**：必须检索日报/周报档案中已有的横向关联话题。
- 🆕 **校准审查强制**：报告初稿完成 → Step A(逻辑扫描) → B(完整性) → C(措辞) → D(框架) → E(对立) → **F(理论偏向)** → **G(叙事引力)** → **H(受众工具链翻译)** → **I(三角叙事补洞)** → 校准记录表嵌入报告末尾。

---

## 📂 关联引用

**配置文件**：
- `~/.hermes/skills/hotspot-research/templates/report_template.md` — 报告输出格式模板

**References · 采集技术**：
- `references/llm_context_only_excavation.md` — LLM Context-only 模式（93% 完整度）
- `references/anthropic-source-handling.md` — Anthropic Research JS 增量加载抓取
- **`references/cloudflare_waf_python_direct.md` — 🆕 2026-07-05 Cloudflare WAF 站点 Python 直连绕过**（v2.5.0 新增）
- **`references/international_topic_chinese_supplement.md` — 🆕 2026-07-05 国际治理话题中文补强模式**（v2.5.0 新增）
- **`references/b2b_topic_china_perspective.md` — 🆕 2026-07-05 B 端公司/商业话题中国视角补强模式**（v2.6.1 新增；8 组豆包关键词广覆盖 + Layer 2 三段式重写 + Layer 3 中国视角占比 ≥50%）\n- **`references/media_culture_topic_china_mirror.md` — 🆕 2026-07-08 媒体/文化趋势话题中国镜像模式**（v2.7.4 新增；情绪/身份锚定豆包关键词 + 3-5 组广度覆盖 + 自媒体源认知框架）\n- **`references/doubao_primary_fallback.md` — 🆕 2026-07-08 豆包主源模式**（v2.7.1 新增；Brave + Tavily 同时不可用时豆包升级为全信号主采集源）
- **`references/apple_podcasts_transcript_proxy.md` — 🆕 2026-07-08 Apple Podcasts show notes 作为播客 transcript 替代**（v2.7.2 新增；YouTube 字幕失败时的 ~90% 完整度降级路径）
- **`../../hotspot-research/references/llm_brave_context_alternative_path.md` — 🆕 2026-07-05 `web_extract` 不可用环境下的 `brave_llm_context` + Python `requests` 双源降级（v2.6.0 引用）**

**References · 分析方法**：
- `references/cross_signal_synthesis.md` — 三路信号交叉分析模式
- `references/divergence_patterns.md` — 5 种发散模式
- `references/rashomon_topic_pattern.md` — 🆕 罗生门型话题·对立张力分析模式（双方同时为真时如何组织素材）
- `references/case_type_topic_excavation.md` — 案例型话题方法论
- `references/industry-event-minimal-signal-pattern.md` — 行业事件最小信号集
- `references/single-topic-multi-round-parallel.md` — 单话题多轮并行采集

**References · 校准**：
- `references/calibration_checklist.md` — 5 类校准清单
- `references/calibration_case_cognitive_surrender.md` — 校准案例库
- `references/calibration_case_openrouter.md` — OpenRouter 校准案例
- `references/calibration_case_every_compound_engineering.md` — Every Compound Engineering 校准案例
- **`references/calibration_case_un_women_international_upgrade.md` — 🆕 2026-07-05 单源国际议题升级为 P0 案例**（v2.5.0 新增）
- **`references/post_generation_review_pattern.md` — 🆕 2026-07-08 审查补充优化完整案例·JADEPUFFER 实证**（v2.7.0 新增；4 类修正+审计摘要模板+方法论忠告）
- **`references/calibration_case_cac_ai_services_chapter.md` — 🆕 2026-07-08 CAC「智能信息服务」专章深挖案例**（v2.7.5 新增；中国国内政策/法规话题·豆包 P1 主源 + 直 curl 政府官网双路径验证）

**变更日志**：
- `references/changelog.md` — skill 变更日志

---

*Skill 由 SOUL 框架维护 · 当前版本 v2.7.5（2026-07-08）*
*变更（v2.7.5）：模块 1 新增用户预消化版本处理（6 项强制验证 + 真伪校准表格前置）+ Step 2A 工具链新增 dataPro_search 快速验证入口*\n*变更（v2.7.4）：+ `references/media_culture_topic_china_mirror.md`（媒体/文化趋势话题中国镜像模式）+ Step 2A 中文补强新增文化趋势分支*\n*变更（v2.7.3）：`references/anthropic-source-handling.md` 新增第五节「单篇博客文章页抓取」（Jina 空但 curl 含全文，与 transformer-circuits.pub 区分）*\n*变更（v2.7.2）：+ `references/apple_podcasts_transcript_proxy.md`（播客 transcript 替代：Brave→Apple Podcasts show notes ~90% 完整度）+ Step 2A 播客双路径 + `youtube_transcript_api` 正确 API 模式*\n*变更（v2.7.0）：+ 模块 5C「审查补充优化」+ `references/post_generation_review_pattern.md` + 校准审查新增 G/H/I 三项（叙事引力/受众工具链翻译/三角叙事）*\n*变更（v2.6.1）：+ `references/b2b_topic_china_perspective.md`（B 端话题中国视角补强：8 组豆包关键词 + 三段式主选题 + Layer 3 中国视角 ≥50%）+ 豆包沙箱路径工具陷阱修复*\n*变更（v2.6.0）：+ `web_extract` 环境依赖警告 + 引用父 umbrella 的 `references/llm_brave_context_alternative_path.md` 降级路径*\n*变更（v2.5.0）：+ `references/cloudflare_waf_python_direct.md`（Cloudflare WAF Python 直连绕过）*
