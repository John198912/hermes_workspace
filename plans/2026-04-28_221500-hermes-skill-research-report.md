# 完整调研报告：Hermes Skill 系统升级与生态整合方案

> 调研时间：2026-04-28 21:00-22:15  
> 调研范围：3 条线并行，累计 40+ API 调用，耗时约 25 分钟  
> 报告提交者：江小马（Hermes Agent，SOUL 人格激活）

---

## 执行摘要

本次调研覆盖三大方向：

| 调研线 | 覆盖范围 | 核心发现 | 产出文件 |
|--------|---------|---------|---------|
| **Hermes Skill 系统** | 源码+文档+测试+71个bundled skill | 架构极其完善，7+外部hub集成，渐进式披露设计精妙 | `research_report.md` |
| **MCP/OpenAI SDK/Claude Code 生态** | 5027+ MCP servers、smithery.ai、awesome-mcp-servers、Claude Code hooks | 8个P0 MCP servers可零代码接入；hooks系统是最大可迁移价值 | `research_report.md` |
| **通用Skill案例（非内容创作）** | 7个领域（PKM/项目管理/工程/研究/数据/效率/商业分析） | 5个P0新skill、3个P1升级skill、2个P2skill | `plans/hermes-skill-research-non-content.md` |

**核心结论：Hermes Agent 的 skill 系统是当前 AI Agent 生态中最成熟的架构之一**，不存在"从零构建"的问题，而是"如何最大化利用已有生态"的问题。

---

## 第一章：Hermes Agent Skill 系统深度分析

### 1.1 架构评价（★★★★★）

Hermes 的 skill 系统是目前最完善的 AI Agent 技能系统之一。

**突出优势**：

1. **渐进式披露**（Progressive Disclosure）：3 级加载机制——`skills_list()` 仅返回 3k tokens 的元数据 → `skill_view(name)` 按需加载完整内容 → `skill_view(name, file_path)` 加载引用文件。零 token 成本直到使用。

2. **安全体系多层防护**：正则扫描 + 信任策略（`builtin` > `official` > `trusted` > `community`）+ path traversal 防护 + env var 保密 + skip_content_exfiltration

3. **生态集成广泛**：支持 openai/skills、anthropics/skills、skills.sh、ClawHub、LobeHub、Claude marketplace、自定义 tap 等 7+ 外部资源来源

4. **开发者体验优秀**：零注册、零配置、纯 Markdown 格式、agent 可自主创建（`skill_manage` tool）、放进去即用

5. **同步机制健壮**：manifest + MD5 hash 对比 + 用户修改保护 + 原子写入

### 1.2 架构原则（来自官方文档和源码）

| 原则 | 说明 | 对你的意义 |
|------|------|-----------|
| **Skill优先于Tool** | 除非需要端到端API集成/二进制处理/流式事件，否则用Skill | 绝大部分新能力都可以做成skill |
| **一个skill只做一件事** | 保持聚焦，不贪多 | 你的rivet-generator和content-adapter应该分开 |
| **渐进式披露** | 层级递进，不要把所有内容塞进description | SKILL.md内部也要遵循这个原则 |
| **条件激活** | `requires_toolsets`/`fallback_for_toolsets` | skill可以自动适配不同的工具环境 |
| **外部目录只读** | `skills.external_dirs` 配置 | 适合共享团队的只读技能库 |

### 1.3 71个 Bundled Skill 质量分析

**已覆盖的类别**（25个分类，74个skills）：

| 类别 | 数量 | 代表skill | 对你的价值 |
|------|------|-----------|-----------|
| software-development | 6 | plan, TDD, debug, code-review | 工程效率基线已覆盖 |
| creative | 9 | manim, p5js, excalidraw, pixel-art | 内容创作需求已有部分覆盖 |
| research | 7 | arxiv, blogwatcher, research-paper-writing | 研究工具链完整 |
| mlops | 12 | llama-cpp, vllm, unsloth, axolotl | AI工程能力齐全 |
| github | 6 | PR, code-review, issues, repo-mgmt | 完整GitHub工作流 |
| productivity | 8 | notion, linear, google-workspace, pdf | 生产力工具已覆盖主流 |
| apple | 4 | iMessage, Reminders, Notes, FindMy | 苹果生态集成 |

**明显的缺失**（也是这次调研要填补的）：

| 缺失领域 | 影响 | 填补方案（见后文） |
|----------|------|-------------------|
| 内容创作产线（RIVET骨架、多平台适配、人设审核） | 🔴 直接影响你的核心工作流 | 4个新skill（见上一份计划）|
| 竞品分析/市场调研自动化 | 🟡 选题决策依赖直觉 | competitive-analysis skill |
| 个人GTD/效率系统 | 🟡 任务管理散乱 | gtd-workflow skill |
| 数据分析管道 | 🟢 报告生成依赖手动 | data-cleaner + report-automation |
| 知识管理高级功能 | 🟢 Obsidian只有基础CRUD | obsidian-advanced skill |

### 1.4 Skills Hub 集成生态

Hermes 通过 `tools/skills_hub.py` 集成了多个外部资源来源，这意味着**不需要全部自己写**：

```
skills.sh            → Vercel 的公开技能目录
ClawHub              → 社区技能市场
LobeHub              → 开源工具技能集
Claude marketplace   → Anthropic 官方技能
openai/skills        → OpenAI 技能合集
anthropics/skills    → Anthropic 技能合集
GitHub tap           → 自定义 GitHub 仓库
```

**对你而言**：在创建新skill前，先检查这些hub中是否已有现成的。如果有，直接 `hermes skills install` 即可。

---

## 第二章：MCP 生态可迁移能力分析

### 2.1 核心发现：Hermes 已经是最好的 MCP 客户端之一

`native-mcp` skill 是 Hermes 内置的 MCP 客户端，支持 stdio/HTTP 传输、自动重连、安全过滤、零配置工具注入。这意味着 **5027+ 个 MCP 服务器的能力立即可用**。

### 2.2 P0 可接入 MCP 服务器（零代码，30分钟内完成）

按优先级和对你赛道（AI×超级个体×内容创业）的价值排列：

| 优先级 | MCP 服务器 | 填补的空白 | 与你的关联 |
|--------|-----------|-----------|-----------|
| 🔴 **P0** | **brave-search** / **exa** | Hermes缺少专用网络搜索工具（当前web_search依赖特定provider） | 选题研究、素材查找、热点验证 |
| 🔴 **P0** | **server-memory** | 跨session持久化知识图谱（目前memory只是简单的char-limit存储） | 选题池、竞争情报库、长期记忆 |
| 🔴 **P0** | **obsidian-mcp-pro** (23工具) | 现有obsidian skill只有基础CRUD | 知识管理全流程自动化 |
| 🔴 **P0** | **duckdb-mcp** | 缺失的数据分析能力（SQL查询csv/parquet/json） | 批量处理采集数据、报告生成 |
| 🟡 **P1** | **google_workspace_mcp** | 完整日历/邮件/文档API | 项目管理、内容排期、自动归档 |
| 🟡 **P1** | **upstash/context7** | RAG文档检索 | 快速查阅技术文档、前沿论文 |
| 🟡 **P1** | **papersflow-mcp** | 4.74亿学术论文搜索 | 研究深度，追踪AI前沿 |
| 🟡 **P1** | **saga-mcp** / **linear-mcp** | AI原生项目追踪 | 内容生产项目管理 |

### 2.3 需要引擎层改造才能迁移的能力（非MCP）

| 能力 | 来源 | 复杂度 | 对你的价值 | 改造方式 |
|------|------|--------|-----------|---------|
| **钩子系统 (Hooks)** | Claude Code | 🔴 高 | 极高 | 在Hermes agent循环中注册PreToolUse/SessionStart/Stop回调 |
| **输入/输出护栏** | OpenAI Agents SDK | 🟡 中 | 中 | 在tools层加校验filter |
| **多agent并发搜索模式** | OpenAI research bot | 🟡 中 | 高 | 用subagent-driven-development已有的能力实现 |
| **Structured Output 强制模式** | OpenAI SDK的json_schema | 🟢 低 | 中 | Hermes已有outlines skill |

**核心建议**：hooks 系统值得长期投入，但对你的短期内容生产影响不大。现阶段优先通过 MCP 和 skill 补齐能力。

---

## 第三章：非内容创作的高质量通用Skill（7个领域分析）

### 3.1 领域总览

| 领域 | Hermes现状 | 建议新增/升级 | 优先级 |
|------|-----------|-------------|--------|
| **个人知识管理(PKM)** | 基础obsidian skill（CRUD） | obsidian-advanced (Zettelkasten+图谱) | 🟡 P1 |
| **项目管理** | linear + notion 已覆盖 | prd-writer（产品需求文档自动化） | 🟡 P1 |
| **工程效率** | GitHub完整套件+TDD+debug | 技术债务分析、changelog自动生成 | 🟢 P2 |
| **研究学习** | arxiv + blogwatcher + research-paper-writing | lit-review（文献综述助手） | 🟡 P1 |
| **数据分析** | jupyter-live-kernel（基础） | data-cleaner + report-automation | 🟡 P1 |
| **个人效率** | apple-reminders + google-workspace | gtd-workflow（完整GTD系统） | 🟡 P1 |
| **商业分析** | **完全缺失** | competitive-analysis（竞品分析） | 🔴 P0 |

### 3.2 P0 Skill 详细定义

#### (1) `competitive-analysis` — 竞品分析框架

**为什么是P0**：这个领域在Hermes中完全空白，而做内容创业需要持续监测同行动向、市场变化。

**输入**：竞品名称/赛道关键词  
**输出**：结构化竞品分析报告（定位、内容策略、增长路径、差异化机会）

**核心能力**：
1. 竞品矩阵对比（定位/受众/内容形式/变现模式/数据表现）
2. 差异化空间识别（SOUL的"反常识"角度 vs 竞品的表述）
3. 市场动态追踪（新入局者、关键动作、行业变化）
4. SWOT+建议输出

**对你而言**：每次想发某个话题前的"竞品检查"——看看有谁说过、怎么说的、你要怎么差异化。

#### (2) `gtd-workflow` — 完整GTD系统

**为什么是P0**：现有apple-reminders skill只是"增删改查"，缺乏完整的任务管理流程。对于全职自媒体的你，GTD系统直接影响执行力。

**输入**：语音/文本描述的任务、项目、想法  
**输出**：按照 GTD 五阶段（Capture → Clarify → Organize → Reflect → Engage）组织好的任务清单

**核心能力**：
1. 自然语言输入→结构化任务（自动分类：今日/本周/本月/将来/参考）
2. 项目分解（一个"做一期B站视频"拆成5-8个可执行步骤）
3. 每周回顾提示（"检查你上周搁置的3个选题"）
4. 与现有apple-reminders和google-workspace skill联动

**对你而言**：管理多线内容生产（选题→写稿→拍摄→剪辑→发布）的关键杠杆。

#### (3) `data-cleaner` — 数据清洗管道

**输入**：csv/json文件（如采集到的热点数据、评论数据、竞品发布记录）  
**输出**：清洗后的结构化数据 + 质量报告

**核心能力**：
1. 自动检测常见问题（空值、格式不一致、重复记录、离群值）
2. 批量清洗（去重规则可配置、格式统一）
3. 数据质量报告（哪个字段质量差、建议如何修复）

**对你而言**：hotspot-engine 采集的数据需要清洗后才能做高质量分析。

### 3.3 P1 Skill 详细定义

| Skill | 描述 | 对应现有skill | 增量 |
|-------|------|-------------|------|
| `obsidian-advanced` | 完整知识管理系统（Zettelkasten、图谱可视化、双向链接分析、间隔复习） | `obsidian` (基础CRUD) | ++三倍能力 |
| `prd-writer` | 产品需求文档自动化（用户故事拆分、验收标准、优先级排序） | `linear` + `notion` | 联动已有工具 |
| `lit-review` | 文献综述助手（论文摘要→关联分析→综述草稿） | `arxiv` + `research-paper-writing` | 填中间断点 |
| `report-automation` | 自动生成结构化报告（多种格式：markdown/html/pdf） | 无对应 | 数据分析场景 |
| `meeting-notes` | 会议记录自动化（audio → 结构化笔记 → 行动项 → calendar） | 无对应 | 远程协作 |

### 3.4 P2 Skill 参考

| Skill | 描述 | 优先级原因 |
|-------|------|-----------|
| `tech-debt-analyzer` | 代码库技术债务扫描（复杂度/覆盖率/老化代码） | 对你不紧迫 |
| `changelog-generator` | git log→changelog自动生成 | nice-to-have |
| `habit-tracker` | 习惯追踪与分析 | 实验性质 |
| `interview-bot` | 模拟面试对话（结构化练习） | 低频率需求 |

---

## 第四章：MCP vs Skill vs Tool 的决策框架

根据 Hermes 官方 `CONTRIBUTING.md` 和本次调研，给出你的场景下的选择标准：

| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| 调用外部 API（搜索、数据库、SaaS） | **MCP 接入** | 零代码，Hermes原生支持 |
| 自定义工作流 + 链式推理 | **Skill (SKILL.md)** | 渐进式披露，按需加载，token高效 |
| 二进制数据处理（音视频编译） | **Tool (Python)** | 需要端到端处理能力 |
| 与其他 Agent 协作执行 | **subagent-driven-development** + Skill | 已有完善机制 |
| 定时调度执行 | **cron job** + Skill | Hermes cron 系统已就绪 |
| 复杂多步工作流 | **subagent** + **chain of skills** | 跨上下文隔离 |

**对你的场景的映射**：

```
MCP 接入的内容（零代码）:
  → 网络搜索（research/选题）
  → 知识图谱/记忆（选题池）
  → 数据分析（采集数据清洗）
  → 学术搜索（深度研究）

Skill 新建的内容（需编写SKILL.md）:
  → content-strategy（选题评估）
  → rivet-content-generator（RIVET骨架）
  → content-adapter（多平台适配）
  → voice-keeper（人设审核）
  → competitive-analysis（竞品分析）
  → gtd-workflow（GTD系统）

Tool 不需要（Hermes已有完善的tool层）:
  → file read/write/search
  → terminal
  → web_extract
  → session_search
  → delegate_task
```

---

## 第五章：整合行动路线图

### 阶段一：立即可做（30分钟）

**配置 MCP 服务器**，无需写任何代码：

1. 配置 brave-search MCP → 立即获得自主网络搜索能力
2. 配置 server-memory → 跨 session 持久化知识图谱
3. 配置 duckdb-mcp → 数据分析能力

### 阶段二：核心内容产线（4-6小时）

4 个内容创作skill（来自上一份计划）：
1. `content-strategy`
2. `rivet-content-generator`
3. `content-adapter`
4. `voice-keeper`

### 阶段三：通用提效（6-8小时）

5 个通用skill：
1. `competitive-analysis`（竞品分析）
2. `gtd-workflow`（GTD系统）
3. `obsidian-advanced`（知识管理升级）
4. `data-cleaner`（数据清洗）
5. `prd-writer`（PRD自动化）

### 完整优先级矩阵

```
          高价值
            │
    voice-keeper  ●  ● content-strategy
    gtd-workflow  ●  ● rivet-content-generator
    competitive   ●    ● content-adapter
    analysis      │
                  │
            ──────┼──────→ 高紧急
                  │
    obsidian-adv  │   lit-review
    data-cleaner  ●
    prd-writer    │
    report-auto   │  tech-debt
                  │  changelog
           低价值 ●  ● habit-tracker
```

---

## 第六章：不建议做的事

从调研中得出的**反模式**，帮你节省时间：

### ❌ 不要重复造轮子
Hermes 已经有的 skill：
- GitHub 完整工作流（PR/Review/Issues/Repo）→ 直接用
- Google Workspace（Gmail/Calendar/Drive/Docs/Sheets）→ 直接用
- Linear/Notion 项目管理 → 直接用
- 邮件客户端（himalaya → IMAP/SMTP）→ 直接用

### ❌ 不要试图改造引擎层（现阶段）
- 钩子系统（Hooks）→ 复杂度高，对你的内容生产工作流影响有限
- Guardrails → Hermes 的安全机制已经够用
- agent 间路由 → subagent-driven-development 已满足需求

### ❌ 不要引入外部 Python 依赖
Hermes skill 最佳实践推荐只用 stdlib + curl + shell。如果某个功能需要 `pip install`，优先考虑 MCP 接入或者作为独立脚本放在 `scripts/` 目录。

### ❌ 不要追求"一次性覆盖所有"
- **宁愿先做好3个skill，也不要建10个半成品**
- content-strategy + rivet-content-generator 如果能做到每天帮你省2小时，就已经值回投入

---

## 附录：关键参考链接

| 资源 | 链接 | 用途 |
|------|------|------|
| Hermes Skills Hub | 系统内置 `hermes skills` CLI | 搜索和安装社区技能 |
| MCP Servers 注册中心 | smithery.ai | 发现和配置 MCP 服务器 |
| awesome-mcp-servers | GitHub 18600+ stars | MCP 服务器目录 |
| OpenAI Agents SDK | GitHub 101K+ stars | 代理模式参考 |
| Claude Code 插件 | Anthropic 官方 | 钩子模式参考 |
| agentskills.io | Vercel 托管 | 技能市场标准 |

---

*报告结束。如果需要，下一步我可以直接开始执行任何一个阶段。*
