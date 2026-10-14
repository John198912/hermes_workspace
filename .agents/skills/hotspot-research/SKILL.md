---
name: hotspot-research
description: >
  跨平台内容热点采集与深度分析工作流，聚焦 AI × 个人品牌 × 超级个体赛道。
  当用户请求热点分析、趋势追踪、关键人物观点采集、受众痛点挖掘、每日/每周热点采集或生成结构化内容策略报告时触发。
  触发词：热点采集、每日热点、每周汇总、趋势分析、热点报告、hotspot research。
---

# Hotspot Research Skill (Antigravity 适配版)

跨平台内容热点采集与深度分析系统的**策略大脑与执行手册**。适配 Antigravity Agent 工具链与 macOS 执行环境。

- **工作区根目录**：`/Users/jiang/Desktop/qoder_workspace/hotspot`
- **报告输出目录**：`reports/hotspot/`
- **核心采集引擎**：`scripts/hotspot_engine.py` (零外部依赖，内置 AI HOT v1、Jina 8人博客、微博热搜、B站、百度、HackerNews)
- **合规审计脚本**：`skills/hotspot-research/scripts/verify_report_template.py`

---

## 🛠️ Antigravity 工具链映射表

| 任务环节 | Antigravity 工具 | 用法与说明 |
|---------|-----------------|-----------|
| **自动化批量采集** | `run_command` | 执行 `python3 scripts/hotspot_engine.py daily`（或 `weekly`），自动完成全源抓取、指纹去重与数据导出 |
| **8人思想家博客直读** | `run_command` / `read_url_content` | 执行 `python3 skills/hotspot-research/scripts/jina_blogs_template.py` 或直读 `https://r.jina.ai/{URL}` |
| **全网/海外信号搜索** | `search_web` | 检索 Twitter、Reddit、海外 AI 社区最新动态，补充受限源 |
| **长文正文与细节提取** | `read_url_content` | 读取文章原文，提取数据、冲突点与一手引文 |
| **报告编写与修改** | `write_to_file` / `replace_file_content` | 撰写或更新 `reports/hotspot/report_daily_YYYY-MM-DD.md` |
| **报告结构合规审查** | `run_command` | 执行 `python3 skills/hotspot-research/scripts/verify_report_template.py` |
| **定时调度设置** | `schedule` / `/schedule` | 设置每日自动运行热点采集定时器 |

---

## 📋 执行流程（六步完整闭环）

### Step 0：预检与版本防覆盖（原则 #16）

1. **确定执行模式**：`daily`（每日热点）或 `weekly`（每周汇总）。
2. **AM/PM 版本防覆盖检查**：
   - 检查 `reports/hotspot/report_daily_{YYYY-MM-DD}.md` 是否存在：
   - 若上午已有报告且当前为下午/晚上运行：自动保留原有报告为 `_am.md`，新报告写为 `_pm.md`；
   - 若已存在 `_pm.md`：新报告写为 `_pm_v2.md`；
   - 严禁单日多次执行直接覆盖已有成果！
3. **AI HOT v1 接口预检**：
   ```bash
   curl -s --compressed -A 'aihot-api/2.0.0 aihot-skill' 'https://aihot.news/api/v1/items?mode=selected&window=24h&limit=1'
   ```
   确认返回状态为正常 JSON，而非认证重定向页。

---

### Step 1：多源信息采集

#### 方式 A：自动化引擎批量扫描（推荐，快速获取全景底表）
在终端运行：
```bash
python3 scripts/hotspot_engine.py daily
```
- 自动提取并持久化：
  - S 级：`AI HOT v1` 24h 精选（中国 AI 圈核心）
  - S 级：8 位核心人物博客（Sam Altman, Karpathy, Naval, Paul Graham, Anthropic, Ethan Mollick, Benedict Evans）
  - A 级：HackerNews Top 讨论、微博热搜榜（带 Referer 反爬修复）、B站科技与全站热门、百度热搜
- 输出文件：
  - 原始聚合 JSON：`reports/hotspot/hotspot_daily_{DATE}.json`
  - 初步结构草案：`reports/hotspot/report_daily_{DATE}.md`

#### 方式 B：交互式补充与深度挖掘
针对海外社区与专业源，使用 Antigravity 原生工具精准补充：
- 海外讨论检索：调用 `search_web`（关键词：`AI agent solopreneur 2026`, `AI workflow one-person business` 等）。
- 重点文章深读：调用 `read_url_content` 提取文章全文，挖掘深度论据。

---

### Step 2：3关筛选与 24h 时效宣誓（核心原则 #18）

在进入深度分析前，对候选条目严格执行三关审核：
1. **关卡 1：信源可信度与去重**
   - 优先 S 级（官方博客/AI HOT）与 A 级技术社区；
   - 检查是否在 `reports/hotspot/fingerprints_daily.json` 中标记多次，过滤老旧条目。
2. **关卡 2：赛道契合度**
   - 强相关赛道：**AI转型 × 个人品牌 × 超级个体**；
   - 过滤与赛道无关的纯娱乐/社会八卦新闻。
3. **关卡 3：三问时效宣誓（原则 #18 强制硬约束）**
   - ① 首次发布时间是什么？
   - ② 是否在报告生成时间前 24h 内？（>24h 需有持续发酵信号；>48h 降级 P2 标注 `⚠️ 回溯`；>72h 直接丢弃）
   - ③ 日期来源是否清晰？不可用模糊时间词（如"此前"、"近日"）。

---

### Step 3：深度内容策略报告撰写（SOUL 标准）

根据采集与深挖结果，在 `reports/hotspot/report_daily_{DATE}.md`（或 `_pm.md`）中输出完整的深度策略报告。

报告必须包含以下核心板块（参照 `templates/report_template.md`）：

1. **📋 本期热点清单（Top 20 优先排序表格）**：
   - 优先级：P0（必追，3-5条）、P1（可追，5-8条）、P2（参考）
   - 标题格式：`[English Title]（中文准确翻译标题）`（强制中英双语，禁止只写单语）
   - 中文摘要：按「【主体】/【动作】/【关键数字】/【影响】」四要素结构化呈现（60-120字）
   - 概览 4 字段结构化：`• 冲突/异常`、`• 数据锚点`、`• 受众关联`、`• 叙事钩子`
   - 与赛道关联度 & 建议内容方向
2. **🇨🇳 今日中国 AI 圈动态（AI HOT v1 精选）**：
   - 🔴 直接选题（P0）
   - 🟡 行业动态（P1-P2）
3. **👤 关键人物观点追踪**：
   - 核心观点一句话提炼 + 原文精准引用 + 选题切入角度
4. **🔍 深度分析（Top 10）**：
   - 事件核心冲突、受众焦虑镜像、认知重构点与超级个体行动路径
5. **💡 选题建议（Top 5，含落地执行路径）**：
   - 切入角度、内容形式（口播/长视频/图文）、目标受众与具体大纲
6. **📈 本期热点标签分布与受限源附录**

---

### Step 4：报告结构合规审查

报告撰写完成后，必须执行合规审查脚本：
```bash
python3 skills/hotspot-research/scripts/verify_report_template.py
```
- 检查项涵盖：文件大小、板块完整度、P0 条目数、中英文双语标题、软链接等。
- 确保输出 `ALL CHECKS PASSED`。

---

### Step 5：软链接维护

确保软链接指向当日最新生成的报告版本：
```bash
ln -sf report_daily_{DATE}_pm.md reports/hotspot/report_daily.md
```
（`scripts/hotspot_engine.py` 会自动完成软链接更新）。
