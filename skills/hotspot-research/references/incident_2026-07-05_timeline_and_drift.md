# 2026-07-05 报告质量事件：时序倒置 + Reference 腐化双重故障

> **摘要**：同日发生两个独立但互相关联的故障：(1) JADEPUFFER/Anthropic 时间线被倒置（6 月研究被写成 7 月事件的"后续"）；(2) provider_configuration.md 自 6/21 未更新，导致模型身份误报。两起故障共享一个根因——数据合并时未做交叉验证。

---

## 故障 A：时序倒置叙事（JADEPUFFER + Anthropic）

### 原始错误

报告中将 JADEPUFFER 勒索攻击（7/3 Sysdig 曝光）与 Anthropic 网络威胁系列研究（6/3 + 6/8 发布）写成：

> ❌「继 7 月 3 日 JADEPUFFER 勒索攻击曝光**后**，Anthropic **在** 6 月 8 日、6 月 3 日连续发布 AI 网络威胁系列研究」

### 根因

1. **数据合并时的因果归因错误**：看到两个相关信号（AI 安全话题），自动构造"因果叙事"（攻击 → 回应），未检查时间锚点的相对早晚
2. **追求叙事完整度 > 事实准确**：标题写了"JADEPUFFER 后续"，预设了时间起点，所有后续数据都被装进这个叙事框架
3. **MiniMax-M3 的时序推理短板**（辅助因素）：在快速生成模式下，对时间锚点的相对早晚判断较弱

### 正确时间线

```
6 月 3 日  → Anthropic 发布 "Mapping AI-enabled cyber threats" + "What we learned"
6 月 8 日  → Anthropic 发布 "Measuring LLMs' impact on N-day exploits"
7 月 3 日  → JADEPUFFER 被 Sysdig 首次曝光（首个 AI Agent 自主勒索攻击）
7 月 5 日  → 报告生成
```

### 修正后的叙事（更强）

> ✅「Anthropic 在 6 月 3 日和 6 月 8 日发布的 AI 网络威胁系列研究**早于** JADEPUFFER（7 月 3 日曝光）整整一个月——这不是事后补救，是事前预言」

### 防止措施

已在 SKILL.md「第七步」新增"时间锚点对齐检查"强制步骤（按时间正序排列 → 确认因果方向 → 反模式检查）。

---

## 故障 B：Reference 文件腐化（provider_configuration.md）

### 原始错误

Agent 被问到"今日采集任务用的哪个模型"时，回答 `minimax-m3 (MiniMax-M3)`，但实际的 cron job 是 `volces-ark/deepseek-v4-pro`。

### 根因

1. `references/provider_configuration.md` 第 12-13 行记录的是 6/21 的旧配置（minimax-m3 / minimax-chat）
2. 6/27 左右两个 hotspot cron job 从 minimax 切换到 volces-ark，但该文档从未同步更新
3. Agent 回答模型身份时仅读了 reference 文件，未交叉验证 `cronjob(action='list')` 的实时状态
4. 切换 cron job 时是"单写操作"（只改了 cron 配置，未改文档），引入了腐化

### 正确状态

```
cronjob(action='list'):
  job_id: dfc8a1b2c3d4
  model: "deepseek-v4-pro"
  provider: "volces-ark"  ← 正确，非 minimax

config.yaml:
  custom_providers.volces-ark ← 存在且有效
  delegation.reasoning_effort: max
```

### 防止措施

1. **SKILL.md 核心原则 #14**：Provider/Model 切换后必须同步更新 provider_configuration.md（双写操作）
2. **模型身份回答流程**：先查 `cronjob(action='list')`（实时）→ 再对 `provider_configuration.md`（文档）→ 不一致则更新文档
3. **报告末尾锚点**：每次报告的「⚙️ 执行路径报告」应包含当前 model/provider，形成独立于 reference 文件的验证锚点

---

## 两个故障的交叉影响

故障 B（文档腐化）放大了故障 A 的严重性：

- 如果 Agent 正确使用 volces-ark/deepseek-v4-pro（而非 minimax-m3），时序推理能力会更强，故障 A 可能被及时发现
- 但根因不在模型——即使模型更强，如果没有"时间锚点对齐"的强制步骤，时序错误仍可能发生
- **关键教训**：流程检查（时间锚点对齐） > 模型能力（deepseek > minimax）

---

## 修复清单（2026-07-05 已执行）

| # | 修复项 | 文件 | 操作 |
|---|--------|------|------|
| 1 | 时间锚点对齐检查 | SKILL.md 第七步 | ✅ 新增子步骤（按时间正序排列 → 因果方向确认） |
| 2 | Reference 腐化防护 | SKILL.md 核心原则 #14 | ✅ 新增原则（双写操作 + 交叉验证） |
| 3 | 模型身份验证流程 | SKILL.md 核心原则 #14 | ✅ 嵌入 Agent 回答流程（先查 cron 再查文档） |
| 4 | provider_configuration.md | references/ | ✅ 表更新为 volces-ark/deepseek-v4-pro |
| 5 | JADEPUFFER 报告修正 | report_daily_2026-07-05.md | ✅ 叙事从"后续"改为"事前预言" |
| 6 | 07-05 报告重跑 | report_daily_2026-07-05_v2.md | ✅ volces-ark/deepseek-v4-pro (max) 重新生成 |

---

*记录时间：2026-07-05 · 事件跨度：2026-06-21（文档腐化起点）至 2026-07-05（发现并修复）*
