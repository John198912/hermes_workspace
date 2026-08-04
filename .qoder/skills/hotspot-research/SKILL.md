---
name: hotspot-research
description: >
  跨平台内容热点采集与分析工作流，聚焦 AI x 个人品牌 x 超级个体赛道。
  当用户请求热点分析、趋势追踪、关键人物观点采集、受众痛点挖掘、
  或生成结构化内容策略报告时触发。支持每日采集和每周汇总两种模式。
  触发词：热点采集、每日热点、每周汇总、趋势分析、热点报告、hotspot research。
---

# Hotspot Research Skill

跨平台内容热点采集与分析系统的**策略大脑和执行手册**。Agent 每次执行时严格按以下流程操作。

> **报告输出目录**：`~/Desktop/qoder_workspace/hermes_workspace_tmp/reports/hotspot-research_qoder/`
> **脚本目录**：本 skill 目录下的 `scripts/`

---

## 工具映射表（Hermes → Qoder）

| Hermes 工具 | Qoder 工具 | 说明 |
|-------------|-----------|------|
| `write_file` | `Write` / `SearchReplace` | 写入/编辑报告文件 |
| `mcp_brave_search` / `tavily_search` | `WebSearch` + `WebFetch` | 搜索引擎 + 页面内容提取 |
| `execute_code` | `Bash` | 执行 Python 脚本和 curl 命令 |
| `delegate_task` | `Agent` (子代理) | 并行采集多个信息源 |
| `session_search` | `Grep` / `Glob` | 搜索历史报告文件 |
| `search_files` | `Grep` / `Glob` | 搜索文件内容 |
| Jina Reader (curl) | `Bash` curl / `WebFetch` | URL → Markdown 提取 |
| Browser 采集 | Browser MCP | 需要 JS 渲染的页面 |

---

## 执行流程（七步）

### Step 0：预检与初始化

1. **确定模式**：`daily`（每日）或 `weekly`（每周）
2. **AM/PM 版本检查**：检查目标报告文件是否存在
   - 存在且为当日首份 → 重命名为 `_am.md`
   - 已有 `_am.md` → 新报告写为 `_pm.md`
   - 已有 `_am.md` 和 `_pm.md` → 写为 `_pm_v2.md`
3. **AI HOT 预检**：
   ```bash
   UA="aihot-skill/0.3.4 (+https://aihot.virxact.com/aihot-skill/)"
   curl -sH "User-Agent: $UA" "https://aihot.virxact.com/api/public/fingerprint" --max-time 5
   ```
   - 返回有效 JSON → API 可用，继续 Step 1 采集
   - 超时/错误/无响应 → 标注 `[aihot:UNAVAILABLE]`，使用替代路径（WebSearch 中文搜索 + 搜狗微信）
4. **加载指纹库**：读取上次报告的指纹用于去重预检
   - 日报指纹保留 7 天，周报指纹保留 30 天

### Step 1：多源信息采集

**采集优先级**：S 级源 > A 级源 > B 级源

**方式 A — Python 引擎批量采集（推荐用于 cron 自动模式）**：
```bash
python3 <skill_path>/scripts/hotspot_engine.py daily   # 或 weekly
```
引擎自动执行全部信息源采集、指纹去重、报告生成。详见 `scripts/hotspot_engine.py`。

**方式 B — Qoder 工具链交互式采集（推荐用于对话模式）**：

按以下分组并行采集（使用 `Agent` 子代理或直接调用）：

#### 1.1 关键人物博客（Jina Reader 通过 Bash curl）
```bash
# 8 人博客并行采集（使用 jina_blogs_template.py 脚本）
python3 <skill_path>/scripts/jina_blogs_template.py
```
或逐个通过 `WebFetch` 获取：
- Sam Altman: `https://r.jina.ai/https://blog.samaltman.com/`
- Karpathy: `https://r.jina.ai/https://karpathy.github.io/`
- Naval: `https://r.jina.ai/https://nav.al/`
- Paul Graham: `https://r.jina.ai/http://paulgraham.com/articles.html`
- Benedict Evans: `https://r.jina.ai/https://www.ben-evans.com/`
- Ethan Mollick: `https://r.jina.ai/https://www.oneusefulthing.org/feed`
- Anthropic Research: `https://r.jina.ai/https://www.anthropic.com/research`
- Karpathy Bear Blog: `https://r.jina.ai/https://karpathy.bearblog.dev/blog/`

#### 1.2 海外热点（WebSearch + WebFetch）
- 使用 `WebSearch` 搜索关键词（见 `references/keywords.md` 海外部分）
- 使用 `WebFetch` 提取搜索结果中的高价值页面
- HackerNews 热门：通过 Bash curl Firebase API
- Reddit 热门：通过 Bash curl JSON API

#### 1.3 国内热点（WebSearch + Bash curl）
- 百度热搜、微博热搜、B站热门、知乎热榜：通过 Bash curl 各平台 API
- 搜狗微信搜索：通过 Bash curl
- 36氪快讯：通过 Bash curl API
- 小红书/抖音：标注为受限源，需 Browser MCP 或手动补采

#### 1.4 中国 AI 圈动态（AI HOT REST API + WebSearch 补充）— **必做，不可跳过**

> ⛔ **硬约束**：只要 Step 0 预检通过（fingerprint 返回有效 JSON），本步骤采集的数据**必须**进入报告的「🇨🇳 今日中国AI圈动态」章节。仅在 `[aihot:UNAVAILABLE]` 时才允许用替代源。采集失败不报错但跳过该章节 = 静默失败，属重大缺陷。

- **AI HOT（首选）**：通过 Bash curl 调用 `/api/public/items` 端点，获取最近 24h 精选条目
  ```bash
  UA="aihot-skill/0.3.4 (+https://aihot.virxact.com/aihot-skill/)"
  since=$(python3 -c "from datetime import datetime, timedelta, timezone; print((datetime.now(timezone.utc) - timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ'))")
  curl -sH "User-Agent: $UA" "https://aihot.virxact.com/api/public/items?mode=selected&since=$since&take=50"
  ```
  - JSON 响应包含 `title/title_en/source/publishedAt/summary/category/score/selected/permalink` 等字段
- **补充路径**：用 `WebSearch` 搜索 `AI 大模型 最新`、`DeepSeek 最新动态` 等关键词补充 AI HOT 未覆盖的内容

详细采集命令见 `references/collection_commands.md`。

### Step 2：筛选与深度挖掘

对采集结果执行**三关审核**：

| 审核关 | 标准 | 不通过处理 |
|--------|------|-----------|
| **时效关** | 发布时间在 24h 内（合理例外见下方） | 超 24h 无持续发酵 → 降级 P2；超 48h → 标注 `⚠️ 回溯`；超 72h → 丢弃 |
| **赛道关** | 与 AI 转型/超级个体/个人品牌/内容创业相关 | 不相关 → 丢弃或降级 P2 |
| **独家关** | 有独特角度/数据/观点，非纯转载 | 纯转载 → 丢弃或标注 `[二手]` |

**P0/P1/P2 分级标准**：
- **P0**：赛道直接相关 + 多平台共振 + 有数据锚点
- **P1**：相关但需要角度切入，或单平台独有
- **P2**：边缘相关但趋势信号

### Step 3：时效检查（强制）

在报告生成前，对每个 P0/P1 条目逐条执行**三问宣誓**：

1. "这条信息的首次发布时间是什么？" — 从采集源获取具体日期时间
2. "是否在报告生成时间前 24h 内？" — 超过 24h 但无持续发酵论证 → 降级 P2
3. "日期信息从哪个采集源获取的？" — 优先级：AI HOT `publishedAt` > WebSearch 结果日期 > 网页 meta date > 采集时间 - 1h（保守推定）

**禁止行为**：
- 从历史报告/缓存中提取"主题相似"的材料充当今日论据（长程检索过拟合）
- 用「某某曾说过」「此前某某发文称」等模糊时间词规避时效检查
- P0 条目缺少发布日期 → 不可标记为 P0
- P1 条目缺少发布日期 → 降级为 P2 并标注 `❓ 无日期`

**合理例外**（允许超过 24h 但必须标注）：
- 持续发酵事件：标注 `[持续追踪 D+N]` 并说明今日新增信号
- 周末回补：周一报告覆盖周五-周日信息 → 标注 `[周末回补 M/D]`
- 长周期分析发布：标注发布日期，数据日期在摘要中说明

### Step 4：按模板生成报告

使用 `references/report_template.md` 模板，通过 `Write` 工具写入报告文件。

> ⛔ **章节完整性硬约束（日报 9 章节全部必须）**：
> 1. 📋 本期热点清单（P0 5 条 + P1 4-7 条）
> 2. 🇨🇳 今日中国AI圈动态（AI HOT 数据）
> 3. 👤 关键人物观点追踪
> 4. 🔍 深度分析（Top 10）
> 5. 💡 选题建议（Top 5，含执行路径）
> 6. 💔 受众痛点库
> 7. ⚙️ 执行路径报告（含各采集源成功/失败状态）
> 8. 📡 本周线索（更新）
> 9. 💡 素材深挖提示
>
> **规则**：
> - 禁止整章省略。某章节确实无内容时，必须保留章节骨架并写明：「本期无有效信号（原因：XXX，已尝试源：YYY）」
> - P1 低于 4 条时，必须在热点清单下方说明「本期信号不足」的具体原因（如源受限/时效窗口内无相关信号），禁止无说明的 0-3 条
> - 章节省略即静默失败——验证器会拦截，但 Agent 不应依赖拦截，应首次生成即完整

### Step 4.5：报告强制验证（交付前必过）

报告保存后**必须**运行验证器，验证失败则修复后重新验证，**禁止带失败交付**：

```bash
python3 <skill_path>/scripts/verify_report_template.py --report <报告路径> --mode daily   # 或 weekly
```

**处理规则**：
- exit code 0 → 验证通过，继续 Step 5
- exit code 非 0 → 按输出的缺失章节/数量问题修复报告，重新保存后再次验证，直到通过
- 验证器输出 `X/9 章节通过, P0=Y, P1=Z` 结构化摘要，必须将验证结果摘要写入报告的「⚙️ 执行路径报告」章节

**报告命名规范**：
- 日报：`report_daily_YYYY-MM-DD.md`（首份）/ `report_daily_YYYY-MM-DD_am.md`（上午版）/ `report_daily_YYYY-MM-DD_pm.md`（下午版）
- 周报：`report_weekly_YYYY-WXX.md`
- 软链接：`report_daily.md` → 最新日报

**标题与摘要强制规范**：
1. 英文标题必须 100% 翻译 — 格式：`English Original Title（中文翻译标题）`
2. 中文摘要系统化结构化 — 按「主体 / 动作 / 关键数字 / 行业影响」四要素，每条 60-120 字
3. 概览必须包含 4 个固定字段：`[冲突/异常]` + `[数据锚点]` + `[受众关联]` + `[叙事钩子]`，每字段 ≤40 字
4. P0 摘要上限 150 字，P1 ≤ 120 字，P2 ≤ 80 字
5. 中英混排使用全角空格分隔

**发布日期强制规范**：
6. 每条热点必须标注发布日期 — 格式：`M/D HH:MM` 或 `M/D`
7. 超过 48h → 降级 P2 标注 `⚠️ 回溯`；超过 72h → 丢弃
8. 无法确定日期 → 标注 `❓ 无日期`，自动降级 P2

### Step 5：线索更新

更新 `_week_clues.json` 线索文件：
- 每周一线索 ID 格式：`W-{week_num}-{topic_seq}`（如 W-25-01）
- 新增线索追加到末尾并写回
- 过期（>30 天无信号）的线索标记为 `[EXPIRED]` 归档
- 同一线索主题在同周不得获得不同 W-ID

**实现方式**：线索文件存储在 `~/Desktop/qoder_workspace/hermes_workspace_tmp/reports/hotspot-research_qoder/_week_clues.json`。
- 使用 `Bash` 工具通过 `python3 -c` 或 `jq` 读取/写入 JSON
- 如文件不存在则创建空 JSON `{}`
- 每次报告生成后追加新线索并写回

### Step 6：素材深挖提示（日报专属）

在报告末尾列出 2-3 个适合深度素材挖掘的候选话题：
```
| 候选 | 话题 | 种子信号 | 优先级 |
```

### Step 7：上期选题反馈

- 上期有选题建议 → 逐条标注执行状态（无法验证时标注「待验证」）
- 首期/无上期报告 → 标注「首期报告，无上期反馈」

### Step 8：结果上传至 Git 仓库

报告生成后，**必须**将结果文件提交到 Git 仓库，作为任务闭环的最后一步：

```bash
# 1. 进入 Git 仓库
cd /tmp/hermes_workspace && git pull origin main --rebase

# 2. 复制最新报告到仓库
cp ~/Desktop/qoder_workspace/hermes_workspace_tmp/reports/hotspot-research_qoder/*.md \
   /tmp/hermes_workspace/reports/hotspot-research_qoder/ 2>/dev/null

# 3. 提交并推送
cd /tmp/hermes_workspace && \
git add reports/hotspot-research_qoder/ && \
git commit -m "chore: hotspot-research report $(date +%Y-%m-%d_%H%M)" && \
git push origin main
```

**注意**：
- 如果 `git pull` 有冲突，优先保留远程版本后重新 push
- 如果无新文件变更（`nothing to commit`），跳过 commit 直接结束
- 提交消息格式：`chore: hotspot-research report YYYY-MM-DD_HHMM`

---

## 核心原则

### 原则 #1：AM/PM 版本保留规则

当同一日期多次运行时，后续运行**不得覆盖**已有报告。

**执行逻辑**：
1. 检查目标文件是否存在 → 存在则重命名为 `_am.md`（如尚无上午版）
2. 新报告写为当日下午版 → 更新软链接到最新版本
3. 如上午版和下午版均已存在且第三次运行 → 写为 `_pm_v2.md`

**理由**：上午版有中国 AI 圈全景但信息时间跨度大，下午版有最新海外信号——两者互补。覆盖=丢失上午版独有数据。

### 原则 #2：AI HOT 预检

AI HOT（aihot.virxact.com）提供公开免费 REST API（必须带 aihot-skill UA 以避免 nginx 403）。每次运行前可快速检测：
```bash
UA="aihot-skill/0.3.4 (+https://aihot.virxact.com/aihot-skill/)"
curl -sH "User-Agent: $UA" "https://aihot.virxact.com/api/public/fingerprint" --max-time 5
```
- 返回有效 JSON → API 可用，`collect_aihot` 采集器自动采集
- 超时/错误/无响应 → 标记为受限源，报告中使用 WebSearch 中文搜索 + 搜狗微信替代

### 原则 #3：时效宣誓——每条热点标注发布日期

每条 P0/P1 条目必须执行时效检查（见 Step 3）。禁止长程检索过拟合。

### 原则 #4：理论中立性纪律

本报告为信息采集与分析，**不预设任何哲学框架**。不署名引用哲学家的理论概念。理论框架的引入在内容创作阶段，不在采集阶段。

### 原则 #5：信号分析型话题识别

当话题核心是一个具体事件，但其内容生产价值在于事件承载的结构性信号时，使用信号分析模型进行深度分析。详见 `references/signal_analysis_model.md`。

### 原则 #6：反模式清单（硬禁令）

以下 4 个反模式均来自真实事故，完整案例见 `references/anti_patterns.md`：

1. **时序倒置**：把时间更早的事件写成较晚事件的"后续/回应"。写多事件叙事前必须按时间正序排列所有锚点，确认因果方向。
2. **长程检索过拟合（硬凑老材料）**：把 24h 之外的历史材料（旧演讲/旧文章）当作今日论据。主论据必须 24h 内，历史引用仅允许出现在"背景交代"且必须标注原日期。
3. **AM/PM 覆盖**：同日多次运行直接覆盖已有报告。必须走 Step 0 的版本命名逻辑（_am/_pm/_pm_v2）。
4. **章节省略（静默失败）**：报告缺章节但不报错。这是最危险的反模式——用户看到"正常交付"的报告，实际内容腰斩（真实案例：5 天内报告从 21KB 退化到 7.6KB，6 个章节持续缺失）。

---

## 报告质量检查清单

报告生成后**必须**逐项检查（全部通过才能交付，自动化检查见 Step 4.5 验证器）：
- [ ] 9 个必须 section 全部存在（缺章节必须保留骨架+原因说明）
- [ ] P0 条目 5 个 + P1 条目 4-7 个（P1 不足 4 条必须说明原因）
- [ ] 每条热点标注发布日期
- [ ] 英文标题全部带中文翻译
- [ ] 中文摘要包含四要素（主体/动作/关键数字/行业影响）
- [ ] 概览包含 4 个固定字段
- [ ] 「🇨🇳 今日中国AI圈动态」章节包含 AI HOT 真实数据（预检通过时）
- [ ] 「👤 关键人物观点追踪」章节存在（无新观点时写骨架+原因）
- [ ] 线索 ID 持久化，不重新分配
- [ ] 上期选题反馈不为空（首期除外）
- [ ] **已运行 Step 4.5 验证器且 exit code = 0**

---

## 参考文件索引

| 文件 | 用途 | 加载时机 |
|------|------|---------|
| `references/platforms.md` | 平台信息源评级、采集对象 | 采集前 |
| `references/keywords.md` | 采集方向关键词 | 采集前 |
| `references/tags.md` | 筛选排序规则 | 筛选时 |
| `references/key_persons.md` | 人物追踪清单 | 采集博客前 |
| `references/creator_profile.md` | 人设和受众定义 | 分析时 |
| `references/collection_commands.md` | 所有来源的采集命令 | 执行采集时 |
| `references/data_quality.md` | 三关审核详细表、各源审计指南、章节-数据源映射 | 筛选审核时 |
| `references/anti_patterns.md` | 5 大反模式案例库（时序倒置/硬凑材料/覆盖/静默失败/文档腐化） | 报告生成前必读 |
| `references/troubleshooting.md` | 四层诊断法 + 修复 vs 降级决策树 | 采集源连续失败时 |
| `references/report_template.md` | 报告输出格式模板 | 生成报告时 |
| `references/deep_dive_pattern.md` | 横纵深度专题模板 | 周报深度分析时 |
| `references/signal_analysis_model.md` | 信号分析型话题编译模型 | 深度分析时 |
| `references/daily_weekly_cooperation.md` | 日报→周报协作机制、线索格式 | 周报汇聚时 |
| `references/topic_materials_compilation.md` | 话题元素材采集工作流 | 话题深挖时 |

## 脚本文件索引

| 脚本 | 用途 | 调用方式 |
|------|------|---------|
| `scripts/hotspot_engine.py` | Python 批量采集引擎（指纹去重+多平台采集+报告生成） | `python3 scripts/hotspot_engine.py [daily\|weekly]` |
| `scripts/jina_blogs_template.py` | 8 人博客 Jina Reader 合并采集 | `python3 scripts/jina_blogs_template.py` |
| `scripts/verify_report_template.py` | 报告后置验证（18 项结构检查） | `python3 scripts/verify_report_template.py` |
| `scripts/ocr_chinese_image.swift` | macOS 中文图片 OCR 工具 | `swift scripts/ocr_chinese_image.swift <image_path>` |
