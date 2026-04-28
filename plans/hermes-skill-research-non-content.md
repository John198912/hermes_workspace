# 🧠 内容创作以外的高质量通用 Skill 调研报告

> 调研时间：2026-04-28  
> 调研范围：7 大领域的 Prompt 模式、工具链集成、优先级评估  
> 当前 Hermes 技能：74 个已注册技能（~18 个分类）

---

## 一、现状总览

在执行本调研前，已完整审计了 Hermes 现有技能体系（~/.hermes/skills + ~/.hermes/.skills_prompt_snapshot.json）。**已有但可深化**的领域标记为 🔄，**完全缺失**的领域标记为 🆕。

### 与调研范围直接相关的现有技能

| 领域 | 已有技能 | 状态 |
|------|---------|------|
| PKM | obsidian | ✅ 基本 CRUD（读/写/搜索） |
| 项目管理 | linear, notion | ✅ 完整 CRUD |
| 工程效率 | github-code-review, github-pr-workflow, github-issues, writing-plans, plan | ✅ 较完整 |
| 工程效率 | systematic-debugging, test-driven-development | ✅ 较完整 |
| 研究与学习 | arxiv, research-paper-writing, blogwatcher, llm-wiki | ✅ 较完整 |
| 数据分析 | jupyter-live-kernel | ⚠️ 仅有 notebook |
| 个人效率 | apple-reminders, google-workspace | ✅ 部分覆盖 |
| 商业分析 | — | 🆕 完全缺失 |
| 知识图谱 | — | 🆕 完全缺失 |
| 间隔复习 | — | 🆕 完全缺失 |
| 技术债务管理 | — | 🆕 完全缺失 |
| 数据清洗/ETL | — | 🆕 完全缺失 |
| GTD / 习惯追踪 | — | 🆕 完全缺失 |

---

## 二、各领域详细调研

### 领域 1：个人知识管理 (PKM) 系统

#### (a) 可落地的功能模块

| 模块 | 说明 | 优先级 |
|------|------|--------|
| 🆕 `obsidian-advanced` | 在现有 obsidian skill 基础上增加：通配链接发现、反向链接分析、孤岛笔记检测、Zettelkasten 原子笔记拆分 | **高** |
| 🆕 `knowledge-graph-builder` | 从笔记集合中自动提取实体和关系，构建知识图谱（输出到 Neo4j/Dgraph 或本地 JSON） | **中** |
| 🆕 `spaced-repetition-note` | 基于 Anki/SM-2/SM-4 算法的间隔复习助手：从笔记提取 Q&A、生成复习卡片、安排复习计划 | **高** |
| 🆕 `vault-health` | Obsidian 仓库健康检查：断裂链接、未索引笔记、重复内容、标签一致性 | **中** |

#### (b) Prompt 模式 / 工具链集成

```markdown
# Obsidian Advanced - Prompt 模式

## Zettelkasten 原子化
当你需要将一个长笔记拆解为原子笔记时：
1. 读取笔记内容 `cat "$VAULT/长笔记.md"`
2. 识别独立概念/想法
3. 为每个想法创建独立笔记（20-30行，一个核心思想）
4. 在笔记之间添加 [[WikiLinks]]
5. 更新原笔记为"索引笔记"，仅包含链接列表

## 知识图谱构建
使用工具链组合：
1. `find "$VAULT" -name "*.md"` 列出所有笔记
2. `grep -roh '\[\[.*?\]\]' "$VAULT"` 提取所有链接
3. Python 脚本构建邻接矩阵 → 输出 JSON 图谱
4. Python + graphviz/mermaid 生成可视化

## 间隔复习卡片生成
当用户说"从最近的 20 篇笔记生成复习卡片"：
1. 读取每篇笔记
2. 提取问题-答案对（使用 Q/A 模式匹配）
3. 生成 Anki 兼容的 CSV/APKG
4. 按 SM-2 算法排序输出
```

#### (c) 优先级评估

| 模块 | 通用性 | 效率提升 | 优先级 | 理由 |
|------|--------|---------|--------|------|
| obsidian-advanced | ★★★★ | ★★★★ | **高** | 对任何 PKM 用户都极有价值；增量升级已有 skill |
| spaced-repetition-note | ★★★★ | ★★★★ | **高** | 学习效率翻倍；独立于任何工具 |
| knowledge-graph-builder | ★★★ | ★★★ | **中** | 需要 Neo4j 等基础设施；小众但高价值 |
| vault-health | ★★★ | ★★ | **中** | 维护性 skill；使用频率低但防止灾难 |

---

### 领域 2：产品管理与项目管理

#### (a) 可落地的功能模块

| 模块 | 说明 | 优先级 |
|------|------|--------|
| 🆕 `prd-writer` | 从产品概念/商业需求自动生成 PRD：用户故事、验收标准、技术约束、风险评估 | **高** |
| 🆕 `user-story-splitter` | 将大型史诗/需求拆解为 INVEZT 合规的用户故事，输出到 Linear/Notion | **高** |
| 🆕 `roadmap-manager` | Linear 项目 Roadmap 管理：里程碑创建、依赖分析、时间线冲突检测 | **中** |
| 🆕 `sprint-standup` | 从 Linear issues 自动生成站会摘要、sprint 回顾报告、团队 velocity 分析 | **中** |

#### (b) Prompt 模式 / 工具链集成

```markdown
# PRD Writer - Prompt 模式

当你需要生成 PRD 时：
1. 理解产品概念和目标用户
2. 按以下框架组织：
   - 产品背景与动机
   - 目标用户与场景
   - 功能需求（MoSCoW 优先级）
   - 技术约束与依赖
   - 验收标准（Given/When/Then）
   - 风险与缓解方案
3. 若用户提供了 Linear 项目/issue，联动 `linear` skill 提取已有信息
4. 输出 Markdown 格式 PRD，可选同步到 Notion

# User Story Splitter - Prompt 模式

1. 接收大型需求/史诗描述
2. 按 INVEZT 原则拆分：Independent, Negotiable, Valuable, Estimable, Small, Testable
3. 为每个故事生成：标题 + 描述 + 验收条件 + 故事点估计
4. 使用 `linear` skill 批量创建 issues（通过 GraphQL mutation）

工具链：
```bash
# Batch create issues from user stories
# Uses Linear API variables
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($input: IssueCreateInput!) { issueCreate(input: $input) { success issue { identifier title url } } }",
    "variables": {
      "input": {
        "teamId": "$TEAM_ID",
        "title": "Story title",
        "description": "## Acceptance Criteria\n- Given...\n- When...\n- Then...",
        "priority": 2
      }
    }
  }'
```
```

#### (c) 优先级评估

| 模块 | 通用性 | 效率提升 | 优先级 | 理由 |
|------|--------|---------|--------|------|
| prd-writer | ★★★★★ | ★★★★ | **高** | 产品/PM 角色最频繁的需求；与 linear/notion 深度集成 |
| user-story-splitter | ★★★★★ | ★★★★★ | **高** | 史诗拆解是最耗时的人力工作之一 |
| roadmap-manager | ★★★ | ★★★ | **中** | 依赖现有 roadmap 数据；使用频率较低 |
| sprint-standup | ★★★ | ★★★ | **中** | 对 Scrum 团队有帮助；需要团队文化和习惯养成 |

---

### 领域 3：工程效率

#### (a) 可落地的功能模块

| 模块 | 说明 | 优先级 |
|------|------|--------|
| 🆕 `code-review-assistant` | **强化已有** `github-code-review`：增加安全扫描、性能分析、架构合规检查、自动生成 review summary | **高** |
| 🆕 `tech-debt-tracker` | 扫描代码库标记 TDO/FIXME/HACK/XXX，生成技术债务清单，关联 Linear issues | **高** |
| 🆕 `doc-generator` | 从代码注释/README 模板自动生成 API 文档、架构文档、CHANGELOG | **高** |
| 🆕 `release-notes` | 从 git log + PR 描述生成结构化 release notes（conventional commit 解析） | **中** |
| 🔄 `test-driven-development` | 已有但可提升：增加测试覆盖率报告、边界条件自动建议 | **中** |

#### (b) Prompt 模式 / 工具链集成

```markdown
# Tech Debt Tracker - Prompt 模式

1. 扫描当前项目目录所有代码文件
2. 使用 regex 匹配标记模式：
   - `# TODO:` / `// TODO:` → 计划未做的功能
   - `# FIXME:` / `// FIXME:` → 已知缺陷
   - `# HACK:` / `// HACK:` → 临时解决方案
   - `# XXX:` / `// XXX:` → 危险区域
   - `# BUG:` / `// BUG:` → 已确认 bug
3. 对每个标记提取：文件路径、行号、上下文代码、优先级（基于关键词）
4. 对高优先级标记，使用 `github-issues` skill 创建 GitHub issues 或 `linear` skill 创建 Linear issues

工具链：
```bash
# Scan for tech debt markers
grep -rn 'TODO\|FIXME\|HACK\|XXX\|BUG\|OPTIMIZE' --include='*.py' --include='*.js' --include='*.ts' --include='*.go' --include='*.rs' --include='*.java' .

# Extract with context
grep -rn -B2 -A2 'TODO\|FIXME\|HACK' --include='*.py' . | head -100

# Generate markdown report
python3 << 'PYEOF'
import re, subprocess, json
result = subprocess.run(['grep', '-rn', 'TODO\|FIXME\|HACK\|XXX\|BUG', '--include=*.py', '.'],
    capture_output=True, text=True)
# Parse and categorize...
PYEOF
```

# Doc Generator - Prompt 模式

1. 遍历项目文件结构
2. 提取模块/函数/类的文档字符串 (docstrings)
3. 根据语言选择格式化器：
   - Python → Sphinx/Google style
   - JS/TS → JSDoc style
   - Go → GoDoc style
   - Rust → Rustdoc style
4. 生成 README.md、CONTRIBUTING.md、API.md
5. 可选：用 Python 的 mkdocs 或 Rust 的 mdbook 生成完整文档站
```

#### (c) 优先级评估

| 模块 | 通用性 | 效率提升 | 优先级 | 理由 |
|------|--------|---------|--------|------|
| code-review-assistant | ★★★★★ | ★★★★ | **高** | 已有 `github-code-review`，增量升级性价比极高 |
| tech-debt-tracker | ★★★★ | ★★★★ | **高** | 对任何规模的项目都有用；容易实现 |
| doc-generator | ★★★★★ | ★★★★★ | **高** | 文档是最多人抱怨但没人愿意做的事 |
| release-notes | ★★★ | ★★★ | **中** | 已有 github-repo-management 含 release 功能 |

---

### 领域 4：研究与学习

#### (a) 可落地的功能模块

| 模块 | 说明 | 优先级 |
|------|------|--------|
| 🆕 `litreview-assistant` | 从 arxiv/论文集合自动生成文献综述：自动分类、对比分析、研究空白识别 | **高** |
| 🆕 `note-to-article` | 将笔记/碎片想法转换为正式文章/博客/推特长 thread | **高** |
| 🔄 `arxiv` | 已有但可强化：增加引用格式导出（BibTeX/APA/MLA）、相关论文推荐、RAG 增强的论文问答 | **中** |
| 🆕 `anki-integration` | 与 AnkiConnect API 集成：自动创建/更新卡片、同步笔记中的高亮内容 | **中** |

#### (b) Prompt 模式 / 工具链集成

```markdown
# Note-to-Article - Prompt 模式

1. 读取用户的笔记/思维导图/大纲
2. 识别核心论点和结构
3. 根据目标输出格式重组：
   - 博客文章：引言 → 背景 → 论点 → 论据 → 结论
   - Twitter Thread：10-20 条推文，每条一个观点
   - Newsletter：开篇钩子 → 3 个核心点 → 个人洞察 → CTA
   - LinkedIn 帖子：问题导向的叙事
4. 保持原文的语气和风格
5. 可选：同时输出不同长度版本（长文/短文/摘要）

# Literature Review Assistant - Prompt 模式

1. 运行 `arxiv` skill 搜索相关论文
2. 使用 `web_extract` 获取每篇论文的摘要和全文
3. 按主题分类论文
4. 自动生成对比表格（方法/数据集/结果/局限性）
5. 识别研究空白和未来方向
6. 输出结构化的文献综述草稿 + BibTeX 引用文件

工具链：
```bash
# Extract paper metadata
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300" | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
for entry in root.findall('a:entry', ns):
    title = entry.find('a:title', ns).text.strip().replace('\\n', ' ')
    authors = [a.find('a:name', ns).text for a in entry.findall('a:author', ns)]
    abstract = entry.find('a:summary', ns).text.strip()[:300]
    print(f'TITLE: {title}\\nAUTHORS: {\", \".join(authors)}\\nABSTRACT: {abstract}\\n')
"

# BibTeX export
python3 << 'PYEOF'
import xml.etree.ElementTree as ET
# Parse arxiv XML → convert to BibTeX entries
PYEOF
```
```

#### (c) 优先级评估

| 模块 | 通用性 | 效率提升 | 优先级 | 理由 |
|------|--------|---------|--------|------|
| litreview-assistant | ★★★ | ★★★★★ | **高** | 对研究人员价值极高；与现有 arxiv skill 天然互补 |
| note-to-article | ★★★★★ | ★★★★ | **高** | 内容创作者和研究人员的通用痛点 |
| arxiv-upgrade | ★★★ | ★★★ | **中** | 增量改进，不改变核心使用场景 |
| anki-integration | ★★★ | ★★★ | **中** | 需要 Anki 生态；用户群较小 |

---

### 领域 5：数据工程与分析

#### (a) 可落地的功能模块

| 模块 | 说明 | 优先级 |
|------|------|--------|
| 🆕 `data-cleaner` | 从 CSV/JSON/parquet 文件自动识别并清洗数据：缺失值处理、类型推断、异常值检测、标准化 | **高** |
| 🆕 `viz-automation` | 从数据自动生成 matplotlib/plotly/vega-lite 可视化：描述性统计 + 最适合的图表类型 | **高** |
| 🆕 `report-automation` | 定时或按需生成数据报告：从 SQL/CSV 读取数据 → 分析 → 可视化 → 输出 HTML/PDF/Notion | **中** |
| 🆕 `etl-pipeline` | 轻量级 ETL：从 API/数据库/文件读取 → 转换 → 写入目标（SQLite/Postgres/CSV） | **中** |

#### (b) Prompt 模式 / 工具链集成

```markdown
# Data Cleaner - Prompt 模式

1. 读取数据文件（自动识别格式）
2. 执行数据质量检查：
   - 缺失值分布和模式
   - 列类型推断（string/numeric/datetime/categorical）
   - 异常值检测（IQR/Z-score/Isolation Forest）
   - 重复行检测
   - 格式不一致（如日期格式混合）
3. 自动生成清洗方案
4. 执行清洗并输出清洗后文件 + 数据质量报告

工具链（Python 脚本化，通过 terminal 执行）：
```python
import pandas as pd
import numpy as np

def auto_clean(df):
    report = {}
    # Missing values
    report['missing'] = df.isnull().sum().to_dict()
    # Type inference
    report['dtypes'] = {col: str(dt) for col, dt in df.dtypes.items()}
    # Outliers (numeric columns)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outliers = {}
    for col in numeric_cols:
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers[col] = int(((df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)).sum())
    report['outliers'] = outliers
    return df.dropna(), report
```

# Viz Automation - Prompt 模式

1. 分析数据特征（数值列数、分类列数、时间序列等）
2. 自动选择最佳可视化类型：
   - 单变量：直方图/箱线图 → 使用 matplotlib/seaborn
   - 双变量：散点图/柱状图
   - 时间序列：折线图
   - 多变量：热力图/平行坐标
   - 地理数据：地图（plotly express）
3. 生成并保存图表（PNG/SVG/交互式 HTML）
4. 输出图表的描述性解读
```

#### (c) 优先级评估

| 模块 | 通用性 | 效率提升 | 优先级 | 理由 |
|------|--------|---------|--------|------|
| data-cleaner | ★★★★★ | ★★★★★ | **高** | 数据分析的第一也是最耗时的步骤；python 脚本化容易实现 |
| viz-automation | ★★★★★ | ★★★★ | **高** | 从数据到洞察的核心桥梁；现有 jupyter-live-kernel 可配合 |
| report-automation | ★★★ | ★★★ | **中** | 更复杂；需要 cron 集成 |
| etl-pipeline | ★★★ | ★★★ | **中** | 有 Airflow/Prefect 等成熟方案；Hermes 做轻量级即可 |

---

### 领域 6：个人效率

#### (a) 可落地的功能模块

| 模块 | 说明 | 优先级 |
|------|------|--------|
| 🆕 `gtd-workflow` | GTD（Getting Things Done）方法论集成：收件箱 → 处理 → 组织 → 执行 → 回顾的完整流程 | **高** |
| 🆕 `calendar-master` | 从日程/Google Calendar 自动优化时间块：深度工作时段保护、会议时间建议、日程冲突检测 | **高** |
| 🆕 `habit-tracker` | 基于本地存储的习惯追踪：打卡、Streak 追踪、周期性习惯提醒、可视化报告 | **中** |
| 🆕 `daily-planner` | 每日计划生成：从 Toodledo/Apple Reminders/Linear 未完成事项 + 日历事件 → 优先级排序 → TODO 列表 | **中** |
| 🔄 `apple-reminders` | 已有但可强化：增加批量处理、智能分类、与 calendar 联动 | **中** |

#### (b) Prompt 模式 / 工具链集成

```markdown
# GTD Workflow - Prompt 模式

1. **Capture**: 从多个来源收集（用户输入、Apple Reminders、email、笔记）
2. **Clarify**: 对每个输入判断：
   - 是否需要行动？→ 下一步行动
   - 是否小于 2 分钟？→ 立即做
   - 是否可以委派？→ 指派
   - 是否只是参考？→ 存档
3. **Organize**: 按上下文分类（@phone, @computer, @errand, @waiting）
4. **Reflect**: 每周回顾检查清单
5. **Engage**: 基于优先级和上下文输出今日行动列表

工具链：
```bash
# Read Apple Reminders
remindctl list --completed false | head -50

# Read Google Calendar events for today
python3 ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py calendar list --today

# Create structured GTD output
python3 << 'PYEOF'
# GTD processing logic
# Categorize items by context, priority, and energy level
PYEOF
```

# Calendar Master - Prompt 模式

1. 读取下周日历事件
2. 分析时间使用情况（会议时间/深度工作时间/缓冲时间）
3. 建议优化：
   - 任务批处理（将类似小任务集中处理）
   - 深度工作保护（建议 2-3 小时无会议时段）
   - 能量管理（高难度任务放在高能量时段）
4. 可选：自动在日历中创建/调整事件

工具链：
```bash
# Get calendar data
python3 ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py calendar list --days 7

# Parse and analyze with Python
python3 << 'PYEOF'
# Time blocking analysis
# Category events: meeting, deep_work, admin, break
# Calculate optimal schedule
PYEOF
```
```

#### (c) 优先级评估

| 模块 | 通用性 | 效率提升 | 优先级 | 理由 |
|------|--------|---------|--------|------|
| gtd-workflow | ★★★★★ | ★★★★★ | **高** | GTD 是最广泛使用的个人效率系统；与 apple-reminders/google-workspace 深度集成 |
| calendar-master | ★★★★ | ★★★★ | **高** | 时间管理是所有人的痛点；与 google-workspace 协同 |
| habit-tracker | ★★★ | ★★★ | **中** | 容易被取代（第三方 app）；但深度集成 Hermes 的 habit-tracker 有独特价值 |
| daily-planner | ★★★ | ★★★ | **中** | 与 GTD 有重叠；可视为 GTD 的子功能 |

---

### 领域 7：商业分析

#### (a) 可落地的功能模块

| 模块 | 说明 | 优先级 |
|------|------|--------|
| 🆕 `competitive-analysis` | 竞品分析：抓取竞品网站/产品信息 → SWOT 分析 → 对比矩阵 → 差异化建议 | **高** |
| 🆕 `market-research` | 市场调研：搜索行业报告 → 提取关键数据 → 市场规模估计 → 趋势识别 | **高** |
| 🆕 `data-driven-decision` | 数据驱动决策框架：从假设 → 数据收集 → 分析 → 建议的端到端流程 | **中** |
| 🆕 `business-model-canvas` | 商业模式画布生成：从产品描述自动填充 9 个模块（价值主张/客户细分/收入流等） | **中** |

#### (b) Prompt 模式 / 工具链集成

```markdown
# Competitive Analysis - Prompt 模式

1. 确定目标市场/产品类别
2. 使用 `web_extract` 或 `web_search` 工具收集竞品信息：
   - 产品主页和 pricing
   - G2/Capterra 评分和评论
   - Product Hunt/TechCrunch 报道
   - Crunchbase 融资信息
3. 按以下维度分析：
   - 功能对比矩阵
   - 定价策略分析
   - 目标用户定位
   - 核心差异化
   - 优势和劣势（SWOT）
4. 输出结构化报告

工具链示例：
```bash
# Search for competitors
web_extract(urls=["https://www.g2.com/categories/..."])

# Analyze pricing pages
web_extract(urls=["https://competitor.com/pricing"])

# Combine and analyze with LLM
# (Hermes handles this within the conversation loop)
```

# Market Research - Prompt 模式

1. 定义市场范围（地理/行业/细分）
2. 数据收集渠道：
   - 行业报告（通过 web_search）
   - 市场数据 API（如 Statista/Wolfram）
   - 新闻趋势（通过 blogwatcher 或 web_search）
   - 社交媒体分析
3. 结构化输出：
   - TAM/SAM/SOM 估计
   - 增长率趋势
   - 竞争格局
   - 市场驱动因素和阻碍
   - 关键洞察和建议
```

#### (c) 优先级评估

| 模块 | 通用性 | 效率提升 | 优先级 | 理由 |
|------|--------|---------|--------|------|
| competitive-analysis | ★★★★ | ★★★★★ | **高** | 创业/产品/战略角色最频繁的需求；web_extract + LLM 分析即可实现 |
| market-research | ★★★★ | ★★★★ | **高** | 与 competitive-analysis 互补；共享工具链 |
| data-driven-decision | ★★★ | ★★★ | **中** | 更框架性的方法论；较难量化效率提升 |
| business-model-canvas | ★★★ | ★★ | **中** | 低频使用场景；适合模板化 |

---

## 三、优先级综合排名

### P0（最高优先级 - 立即实现）

| 排名 | 模块 | 领域 | 理由 |
|------|------|------|------|
| 1 | 🆕 `competitive-analysis` | 商业分析 | 无现有技能 + 极高的通用性 + web_extract 工具即可实现 |
| 2 | 🆕 `gtd-workflow` | 个人效率 | 与 apple-reminders + google-workspace 深度集成；GTD 是最高频效率系统 |
| 3 | 🆕 `data-cleaner` | 数据分析 | 数据分析最耗时的步骤；Python 脚本即可实现 |
| 4 | 🆕 `prd-writer` | 产品管理 | 产品经理最高频产出；与 linear/notion 集成 |
| 5 | 🆕 `obsidian-advanced` | PKM | 增量升级已有 skill；投入产出比高 |

### P1（高优先级 - 尽快实现）

| 排名 | 模块 | 领域 | 理由 |
|------|------|------|------|
| 6 | 🆕 `spaced-repetition-note` | PKM | 学习效率翻倍；独立工具 |
| 7 | 🆕 `code-review-assistant` | 工程效率 | 在已有 `github-code-review` 基础上增量升级 |
| 8 | 🆕 `tech-debt-tracker` | 工程效率 | 简单实现，高价值产出 |
| 9 | 🆕 `doc-generator` | 工程效率 | 解决长期痛点 |
| 10 | 🆕 `calendar-master` | 个人效率 | 与 google-workspace 深度集成 |
| 11 | 🆕 `viz-automation` | 数据分析 | 数据到洞察的核心桥梁 |
| 12 | 🆕 `litreview-assistant` | 研究与学习 | 对研究人员价值极高 |
| 13 | 🆕 `note-to-article` | 研究与学习 | 通用性强 |
| 14 | 🆕 `user-story-splitter` | 产品管理 | 史诗拆解是高频场景 |
| 15 | 🆕 `market-research` | 商业分析 | 与 competitive-analysis 共享工具链 |

### P2（中等优先级 - 后续扩展）

| 模块 | 领域 | 理由 |
|------|------|------|
| knowledge-graph-builder | PKM | 需要基础设施，小众 |
| vault-health | PKM | 维护性 skill，低频 |
| roadmap-manager | 产品管理 | 依赖现有 roadmap |
| sprint-standup | 产品管理 | 需要团队文化 |
| release-notes | 工程效率 | 已有类似功能 |
| anki-integration | 研究与学习 | 需要 Anki 生态 |
| report-automation | 数据分析 | 较复杂，需要 cron |
| etl-pipeline | 数据分析 | 有成熟外部方案 |
| habit-tracker | 个人效率 | 第三方替代品多 |
| daily-planner | 个人效率 | 与 GTD 重叠 |
| data-driven-decision | 商业分析 | 框架性方法论 |
| business-model-canvas | 商业分析 | 低频场景 |

---

## 四、立即行动方案

### Phase 1：创建 5 个 P0 Skill（预计 2-3 天）

```
Week 1:
  Day 1: competitive-analysis + market-research (共享工具链，可并行)
  Day 2: gtd-workflow + calendar-master (共享工具链，可并行)
  Day 3: data-cleaner + prd-writer (可并行)

Week 2:
  Day 4-5: obsidian-advanced + spaced-repetition-note
  Day 6-7: code-review-assistant + tech-debt-tracker
```

### Phase 2：创建 5 个 P1 Skill（预计 2-3 天）

```
Week 3:
  Day 1-2: doc-generator + viz-automation
  Day 3: litreview-assistant + note-to-article
  Day 4-5: user-story-splitter
```

### Phase 3：P2 Skill（选做，预计 1-2 天）

```
- knowledge-graph-builder: 依赖 Neo4j，先做 JSON 本地版本
- release-notes: 在 github-repo-management skill 基础上扩展
- anki-integration: 通过 AnkiConnect REST API
```

---

## 五、关键设计原则

### 每个 Skill 的文件结构

```
~/.hermes/skills/{category}/{skill-name}/
├── SKILL.md          # 技能主文件（prompt + 使用说明 + 工具链脚本）
├── references/       # 参考文件（可选）
└── scripts/          # 自动化脚本（Python/bash，可选）
```

### 与现有系统的集成关系

```
                    ┌──────────────────┐
                    │  apple-reminders  │──→ gtd-workflow (收件箱)
                    │  google-workspace │──→ calendar-master
                    │  linear           │──→ prd-writer, user-story-splitter
                    │  notion           │──→ prd-writer (输出)
                    │  obsidian         │──→ obsidian-advanced
                    │  arxiv            │──→ litreview-assistant
                    │  jupyter-kernel   │──→ data-cleaner, viz-automation
                    │  web_extract      │──→ competitive-analysis, market-research
                    │  github-*         │──→ tech-debt-tracker, code-review
                    └──────────────────┘
```

### Prompt 模式模板

每个 Skill 的 Prompt 应遵循"三段式"结构：

1. **识别阶段**：描述何时应触发该 skill（关键词/用户意图识别）
2. **执行阶段**：具体的工具链调用序列（bash/Python 脚本）
3. **输出阶段**：结构化的输出格式（Markdown/JSON/Notion page）

### 不重复造轮子的检查

| 已存在的轮子 | 对应的新 Skill 策略 |
|------------|-------------------|
| `obsidian` (CRUD) | `obsidian-advanced` 只做增量：链接分析 + 原子化 + Zettelkasten |
| `github-code-review` | `code-review-assistant` 只增补：安全扫描 + 架构分析 + 自动化 summary |
| `apple-reminders` | `gtd-workflow` 不替代，而是在上层做 GTD 方法论编排 |
| `google-workspace calendar` | `calendar-master` 不做日历 CRUD，而是做时间块优化建议 |
| `linear` | `prd-writer` 不在 Linear 层做，而是做 PRD 写作 + 生成 issue 到 Linear |
| `arxiv` | `litreview-assistant` 不在论文搜索层做，而是做多论文的对比和综述 |
| `jupyter-live-kernel` | `data-cleaner` 使用笔记本环境但提供独立脚本化的清洗逻辑 |
