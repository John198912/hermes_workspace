---
name: hotspot-research
description: >
  Cross-platform content hotspot research and analysis workflow for
  AI × personal brand × solopreneur niche. Use when user requests trending
  topic analysis, key figure tracking, audience pain point mining, or
  structured content strategy reports across domestic and overseas platforms.
---

# Hotspot Research Skill

这是热点采集系统的**策略大脑和执行手册**。Agent 每次执行 cron 任务时严格按以下流程执行。

> ⚠️ **执行前必读（2026-07-08）**：以下两个配置陷阱是沉默的杀手——不会报错但会导致错误模型/低质量产出：
> 1. **`agent.reasoning_effort` 不能写 `xhigh`**：volces-ark API 只支持 max/high/medium/low。写 `xhigh` → API 400 → Hermes 静默 fallback 到 minimax-chat → 用户看到"新会话走了 MiniMax"。正确值：`max`。详见 `references/provider_volces_ark.md`。
> 2. **Provider `name` 字段不能写 `minimax`**：Hermes 内部硬编码映射 `minimax` → `api.minimax.io/anthropic`，覆盖你写的 base_url。必须用 `minimax-chat` 或 `volces-ark` 等自定义名。详见 `references/provider_configuration.md`。
> 3. **Cron 不继承 reasoning_effort**：`cronjob update` 的 model 参数不接受 reasoning_effort。唯一入口是 cron prompt 开头的硬指令。详见 `references/provider_configuration.md` → Cron Prompt 修复模板。
> 4. 🆕 **Python 脚本 urllib3 兼容性陷阱（2026-07-08 实战验证）**：hermes-agent venv 的 Python 3.11 + urllib3 存在 `TypeError: unsupported operand type(s) for |: 'type' and 'type'` 兼容性问题，导致所有 `import requests` 的 Python 脚本（tavily-search、byted-web-search、hotspot_engine.py 等）全部不可用。**症状**：任何 Python 脚本在导入 requests 时崩溃。**根因**：urllib3 `_base_connection.py` 使用了 Python 3.10+ 的 `X | Y` union syntax，但 venv 内安装的 urllib3 版本不兼容。**降级路径**：① Brave MCP（npm 进程，不经过 Python venv）② browser 直接导航+快照 ③ terminal curl 直接请求（不 import requests）。详见 `references/python_venv_urllib3_fix.md`。
> 5. 🆕 **AI HOT API 认证墙（2026-07-08 起）**：`aihot.virxact.com` 所有 API 端点返回 HTML 登录页（suite-passport），非 JSON。**症状**：curl 返回 `<html lang="zh-CN">` 含 `suite-passport-compile-at` meta 标签。**这不是临时故障——是系统变更**，不可重试。**替代采集路径**：Brave News 中文关键词搜索 + 搜狗微信（engine）+ 手动补采小红书/微博（交互 session）。每次 cron 运行应先快速检测 AI HOT 状态（curl -sI 看 Content-Type），若是 text/html → 立即跳过 + 标注 [aihot:AUTH_WALL]。详见 `references/aihot_integration.md` §7.1。

> [NEW] **核心原则 #16：AM/PM 版本保留规则（2026-07-08 卷哥硬约束）**
> 
> 当同一日期的 cron 多次运行时（如上午8点+下午6点），后续运行**不得覆盖**已有报告。
> 
> **执行逻辑**：
> 1. 检查目标文件是否存在 → 存在则重命名为 `_am.md`（如尚无上午版）
> 2. 新报告写为当日下午版 → 更新软链接到最新版本
> 3. 如上午版和下午版均已存在且第三次运行 → 写为 `_pm_v2.md`
> 
> **理由**：上午版有AI HOT（中国AI圈全景）但信息时间跨度大，下午版有最新的海外信号但缺中国视角——两者互补。覆盖=丢失上午版独有的AI HOT数据。
> 
> **反模式**：直接用新报告覆盖已有同日文件。参见 `references/incident_2026-07-08_am_pm_overwrite.md`。

> [NEW] **核心原则 #17：AI HOT 认证墙预检（2026-07-08 新增）**
> 
> AI HOT API 自 2026-07-08 起需要登录认证，匿名 curl 返回 HTML 登录页而非 JSON。
> 
> **每次 cron 运行前必须执行预检**：
> ```bash
> curl -sI --max-time 5 "https://aihot.virxact.com/api/articles?type=24h&limit=1" 2>&1 | grep -i content-type
> ```
> - `Content-Type: application/json` → AI HOT 可用，正常采集
> - `Content-Type: text/html` 或空 → AI HOT 认证墙，立即跳过
> 
> **跳过后的替代采集路径**：Brave News 中文搜索 + 搜狗微信(engine) + 手动补采(交互 session)。
> 报告标注：`[WARN] AI HOT 本期不可用（suite-passport 认证墙），中国AI圈内容来自替代源。`
> 详见 `references/aihot_integration.md` §7.1。

> [NEW] **核心原则 #18：时效宣誓——每条热点标注发布日期（2026-07-08 卷哥硬约束）**
> 
> 在第三步「筛选与深度挖掘」完成后、第四步「按模板生成报告」开始前，**必须**对每个 P0/P1 条目逐条执行时效检查：
> 
> **三问宣誓**：
> 1. "这条信息的首次发布时间是什么？"——从采集源获取具体日期时间
> 2. "是否在报告生成时间前 24h 内？"——超过 24h 但无持续发酵论证 → 降级 P2；超过 48h → 标注 `⚠️ 回溯`；超过 72h → 直接丢弃
> 3. "日期信息从哪个采集源获取的？"——优先 Brave News `page_age` > AI HOT `publishedAt` > 网页 meta date
> 
> **禁止行为**：
> - 从历史报告/缓存中提取"主题相似"的材料充当今日论据（长程检索过拟合）
> - 用「某某曾说过」「此前某某发文称」等模糊时间词规避时效检查
> - 在深度分析中将超过 7 天前的历史观点作为"今日延伸"引用——历史引用仅允许在"背景交代"中，且必须标注原日期
> - P0 条目缺少发布日期 → 该条目不可标记为 P0
> - P1 条目缺少发布日期 → 降级为 P2 并标注 `❓ 无日期`
> 
> **合理例外**（允许超过 24h 但必须标注）：
> - 持续发酵事件：如"Fable 5 封禁"→ 标注 `[持续追踪 D+8]` 并说明今日新增信号
> - 周末回补：周一报告覆盖周五-周日信息 → 标注 `[周末回补 M/D]`
> - 长周期分析发布：如 Anthropic 发布 5 月使用数据分析（7/7 发布）→ 发布日期标注为 `7/7`（分析发布日），数据日期在摘要中说明
> 
> **反模式**：参见 `references/incident_2026-07-08_hard_coupling.md`（把 Karpathy 4/30 演讲、Altman 5/6 发文关联到 7/5 报告的 Meta 大溃败/Sonnet 5）——这是"长程检索过拟合"的典型案例。

> **注意：本 SKILL.md 为核心流程骨架。详细命令和参考数据在以下文件中：**
- `references/curl_examples.md` — 所有来源的 curl 命令 (含 🆕 AI HOT API 日报/周报采集命令)
> - `references/data_quality_notes.md` — 三关审核详细表、各源审计指南、已知问题 (含🆕 AI HOT、🆕 报告内容 emoji 拦截 2026-07-07、🆕 write_file stream timeout on large content 2026-07-07)
> - `references/jina_ssl_bypass.md` — 🆕 Jina Reader 故障模式与修复方案 (2026-07-04 重写：根因诊断 + Python bypass 协议层差异)
> - `references/root_cause_diagnosis.md` — 🆕 四层诊断法 (DNS/TCP/TLS/HTTP) + 已验证案例（Jina/Brave/Engine）+ 修复 vs 降级决策树 (2026-07-04 卷哥硬约束)
- `references/python_venv_urllib3_fix.md` — 🆕 Python venv urllib3 兼容性故障：诊断/修复/降级路径 (2026-07-08 实战验证)
- `references/web_extract_degradation.md` — 🆕 web_extract 作为 Jina Reader 降级路径（交互 session 专用，2026-07-04 实战验证）
> - `references/platforms.md` — 完整平台评级、采集对象 (含 🆕 aihot.virxact.com S级聚合源)
> - `references/key_persons.md` — 人物追踪清单
> - `references/keywords.md` — 采集方向关键词
> - `references/tags.md` — 筛选排序规则
> - `references/creator_profile.md` — 人设和受众定义
> - `references/aihot_integration.md` — 🆕 AI HOT API 详细信息、端点、降级策略
> - `references/provider_configuration.md` — 🆕 Cron job 模型配置速查（MiniMax-M3 / 模型切换 / 上下文限制）
> - `references/provider_volces_ark.md` — 🆕 火山方舟 volces-ark/deepseek-v4-pro 配置（推荐用于 hotspot-topic-excavator）
> `references/incident_2026-07-05_timeline_and_drift.md` — 🆕 2026-07-05 报告质量事件：时序倒置 + Reference 腐化双重故障案例
- `references/incident_2026-07-08_hard_coupling.md` — 🆕 2026-07-08 用户反馈事件：cron 默认推理≠max + "硬凑老材料" + 24h 时间窗缺失
- `references/incident_2026-07-08_am_pm_overwrite.md` — 🆕 2026-07-08 AM/PM 报告覆盖事件：cron多次运行覆盖已有报告，根因与修复
- `references/daily_weekly_cooperation.md` — 🆕 日报→周报协作机制、线索格式、汇聚逻辑
> - `references/deep_dive_pattern.md` — 🆕 横纵深度专题模板、选择逻辑、超时保护
> - `references/topic_materials_compilation.md` — 🆕 话题元素材采集：从已有日/周报库提取+关联+整合为特定话题的补充素材
- `references/topic_type_bias_case_study.md` — 🆕 话题类型偏差案例：案例型 vs 事件型话题在素材深挖推荐中的结构性劣势及五维加权修正方案 (2026-06-27)
> - `templates/report_template.md` — 报告输出格式
> `scripts/hotspot_engine.py` — Python 批量扫描引擎
> `scripts/jina_blogs_template.py` — 🆕 8 人博客合并采集模板（2026-07-06 验证：~5-12s 单脚本完成 8/8）
> `references/week27_weekly_run_template.md` — 🆕 Week 27 周报 6 分钟完整跑通的执行模板（2026-07-06 实战验证）：含 ① 关键博客"文件大小 > 发布日期"判断规则 ② heredoc 内含 .dev URL 的 Tirith Lookalike TLD 阻止 + write_file 绕过 ③ git push 拆分两个 terminal 的具体写法 ④ Tavily env 前缀的真实失败案例 ⑤ 五维加权排序的实战选 5 选题。可被未来周报直接复用
> `references/theory_neutrality_diagnostic.md` — 🆕 框架污染诊断模式（2026-07-07）：哲学家理论如何通过 system prompt→模板标签→人设标签 三条间接路径渗入采集报告，诊断方法与修复清单
> `scripts/ocr_chinese_image.swift` — 🆕 macOS 中文图片 OCR 工具 (无视觉模型时降级方案)
> - `scripts/verify_report_template.py` — 🆕 报告后置 ad-hoc 验证模板（22 项结构检查，cron 完成后按需使用）
