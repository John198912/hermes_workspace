# 单话题多轮并行采集模式

> 来源：2026-06-23 Fable 5 叙事链条完整素材采集实战
> 模式：单一叙事链条话题（非多信号对位结构）× 2-3轮并行 Brave 调用

## 适用场景

当话题是「单一叙事链条」（如"Fable 5从发布到封禁到即将恢复的完整故事"），而非「多信号交叉分析」（如"认知投降：3个独立统计信号在同一周出现"）时，采用此模式。

## 执行模式

```
第一轮：覆盖广度 + 深度（4路并行）
├─ brave_llm_context #1: 核心叙事（如 "Fable 5 Mythos controversy June 2026"）
├─ brave_news_search #1: 时效信号（如 "Fable 5 export controls Trump"）
├─ brave_llm_context #2: 辅助角度（如 "Fable 5 NSA red team John Jumper Anthropic"）
└─ brave_news_search #2: 争议/恢复（如 "Fable 5 unban restored Amazon SK Telecom"）

第二轮：补漏 + 最新预测（4路并行）
├─ brave_news_search: freshness=pd, 最新恢复预测
├─ brave_llm_context: freshness=pd, 最新预测市场数据
├─ brave_llm_context: Amazon whistleblower + Trump statement
└─ brave_llm_context: open-weight model response

总计：6-8轮工具调用 → 30+信源 → 6-8个高价值信号
```

## 关键参数

| 轮次 | 工具组合 | freshness | count | max_tokens | 目标 |
|------|---------|-----------|-------|------------|------|
| R1 | 2× LLM Context + 2× News Search | pm (月) | 10-15 | 16384 | 叙事广度+核心事实 |
| R2 | 1× LLM Context + 2× News Search + 1× LLM Context | pd (日) | 10-15 | 8192 | 最新预测+补漏 |

## 与多信号并行模式的区别

| | 多信号模式 | 单话题多轮模式 |
|------|-----------|--------------|
| 信号结构 | 3-5个独立信号 | 1个叙事链条 |
| 第一轮 | 所有信号同时 LLM Context | 叙事分角度 LLM Context + News Search |
| 第二轮 | 补充发散信号 | 拉取最新时效数据 |
| 产出 | 三位一体交叉分析 | 叙事链条 × 信号清单 × 恢复预测 |
| 目录结构 | 标准 `topic_excavation/{date}/{slug}/` | 同，但包含 `raw-sources-manifest.md` + `latest-restoration-signals.md` |
