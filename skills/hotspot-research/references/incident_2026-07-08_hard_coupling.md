# 2026-07-08 报告质量事件：硬凑老材料 + 默认推理≠max

> **摘要**：用户在 0705 报告发布 3 天后质疑报告质量，发现两个独立但互相关联的问题：(1) 报告深度分析章节把 4/30 的 Karpathy 演讲、5/6 的 Altman 家庭事件关联到 7/5 的 Meta 大溃败/Sonnet 5——这是 medium 推理档下的"长程检索过拟合"；(2) 我之前声称"cron 走 max 推理"是错的，实测 cron 默认走 medium 档。

---

## 故障 A：深度分析"硬凑老材料"

### 现象

0705 报告的「🔍 深度分析」和「💡 选题建议」章节里，多处把历史上的人物发言当作"今日的延伸"引用：
- 引用 Altman 5/6 家庭遭攻击事件 → 与 7/5 Meta 治理危机叙事挂钩
- 引用 Karpathy 11/2025 "the space of minds" → 当作今日讨论的"延伸"
- 把 Naval 5/29 / 6/1 播客 → 当作 7/5 Sonnet 5 发布的"上下文"

用户原话：
> "感觉是硬凑在一起的，现在凑在一起的逻辑是什么？为什么现在总会关联到很早之前的一些信息？比如说卡巴斯基的 4 月 30 号的演讲，还有赛曼奥特曼 5 月 6 号的发文。"

### 根因（3 层）

#### 层 1：推理深度不够

**实测**（2026-07-08 用同一 API key + 同一 endpoint 测）：

| reasoning_effort | reasoning_tokens | 实际档 |
|---|---|---|
| 不传（cron 默认） | 21-36 | medium |
| `low` | 28 | low |
| `medium` | 21 | medium |
| `high` | 70 | high |
| `max` | 89 | max |

cron job 在不传 reasoning_effort 时走 **medium** 档——而 medium 推理深度不足以同时完成：
- 70+ 条原始信号的去重/筛选
- 12 条 Top 12 的叙事压缩
- 时序对齐（防止"事后补救"被写成"事前预言"）
- 独立信号 vs 关联信号的判断

#### 层 2：8 人博客全文缓存导致"长程检索过拟合"

`scripts/jina_blogs_template.py` 把 8 人博客的**全文**写入 `/tmp/jina_*.md`（如 Altman 51KB、Karpathy 6.7KB）。medium 推理在 token 压力下：
- 把全文当作"今日可用素材"（不区分日期）
- 找到"主题相似的历史段落" → 强行拼接到今日分析
- 输出"看似有据"但实际是"历史材料撑今日叙事"

#### 层 3：prompt 缺少 24h 时间窗硬约束

SKILL.md 第七步（生成报告）只规定"信息完整度评分"，**没有要求"主论据必须 24 小时内"**。medium 推理在没有强约束下，会倾向于"使用所有可用文本"——包括博客全文。

### 修复（3 个层面）

1. **cron prompt 注入 reasoning_effort=max 硬指令**（已记录到 provider_configuration.md）
2. **SKILL.md 核心原则 #15 新增"24h 时间窗硬约束"**（已 patch）
3. **jina_blogs 改为摘要模式**（待验证）：只保存"最近 1 篇的标题 + 前 200 字摘要"，不保存全文

---

## 故障 B：声称"cron 走 max"是错的

### 我之前说的话

在 2026-07-05 的 provider_configuration.md 修正版里，我写道：

> `| 每日AI超级个体热点采集 | dfc8a1b2c3d4 | deepseek-v4-pro | volces-ark | max（继承 delegation.reasoning_effort） | Daily 08:00 |`

### 实测反驳

我假设 `delegation.reasoning_effort: max` 会被 cron session 继承——**这是错的**：

- `hermes cron update` 的 `model` 参数 schema 不接受 `reasoning_effort` 字段（实测 `cronjob(action='update', model={"reasoning_effort":"max"})` 调用成功但 `cronjob list` 中 model 字段仍只显示 `model: "deepseek-v4-pro"` + `provider: "volces-ark"`，无 reasoning_effort）
- cron session 没有自动继承 delegation 段的 reasoning_effort
- 实测 cron 跑出来的请求中 `reasoning_effort` 字段缺失 → 默认走 medium 档（reasoning_tokens=21-36）

### 防止措施

1. **provider_configuration.md 已 patch**：明确标注"❌ medium（不传时默认）→ 应在 prompt 强指令 max"，并附实测 reasoning_tokens 数据
2. **SKILL.md 核心原则 #14**：新增"推理深度必须实测，不靠推断"
3. **未来验证流程**：声称"推理深度 = X"之前，必须用同一 API key 实测 X/NONE 两种请求，对比 `usage.completion_tokens_details.reasoning_tokens`

---

## 两个故障的交叉影响

故障 B（推理档=medium）**直接导致**故障 A（硬凑老材料）：
- medium 推理 + 全文博客缓存 + 无时间窗约束 = 长程检索过拟合的完整触发链
- 即使推理档=max，仍可能有少量硬凑，但概率显著降低
- 即使有 max 推理，没有时间窗约束，仍可能硬凑——所以时间窗约束和推理档必须**同时修复**

---

## 修复清单（2026-07-08 已执行）

| # | 修复项 | 文件 | 操作 |
|---|--------|------|------|
| 1 | 推理档实测数据 | references/provider_configuration.md | ✅ 添加实测 reasoning_tokens 表格 + ⚠️ 警告块 |
| 2 | Cron Prompt 修复模板 | references/provider_configuration.md | ✅ 新增「Cron Prompt 修复模板」section |
| 3 | 推理深度硬约束 | SKILL.md 核心原则 #14 | ✅ 已添加（在 SKILL.md 中） |
| 4 | 24h 时间窗硬约束 | SKILL.md 核心原则 #15 | ✅ 已添加（在 SKILL.md 中） |
| 5 | Incident 文档 | references/incident_2026-07-08_hard_coupling.md | ✅ 本文 |
| 6 | 未来 cron prompt 注入 max 硬指令 | cronjob(action='update', ...) | ⏳ 待执行（已记录修复模板） |
| 7 | jina_blogs 摘要化 | scripts/jina_blogs_template.py | ⏳ 待设计 |

---

## ⚠️ 待验证：cron prompt 注入是否真的生效

`hermes cron update` 的 prompt 修改是否能让 cron session 的 API 请求带上 `reasoning_effort=max`？**目前没有实测**——下次 cron 跑完后，需要从 cron log 中抓 `usage.completion_tokens_details.reasoning_tokens` 字段确认是否≈89。

如果 cron prompt 注入无效 → 必须改用 cron `script` 模式（`no_agent=True`）直接调 API，才能 100% 控制 reasoning_effort 参数。

---

*记录时间：2026-07-08 · 事件跨度：2026-07-05（报告生成）至 2026-07-08（用户质疑并实测）*
*关联事件：见 `references/incident_2026-07-05_timeline_and_drift.md`（时序倒置 + Reference 腐化）——两起事件共享"未做交叉验证"根因*