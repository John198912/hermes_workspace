# Hotspot Research — 实战发现日志

> 每次 cron 执行过程中发现的经验和教训，供后续 Agent 参考。
> 最后更新：2026-04-29

## Sam Altman 博客日期获取
- Posthaven 博客列表页无发布日期文本（日期在 JS 变量中）
- 最新文章是列表中的第一个链接，按逆序排列
- 当前最新文章：Abundant Intelligence（AI 基础设施工厂愿景）
- 获取单篇文章页后，搜索 JSON-LD 的 datePublished 字段获取日期

## HN Firebase API 时间戳缓存
- 单个 item JSON 的 time 字段偶尔返回错误的过去时间（如 2025 年）
- 同时 score 字段可能返回 None（缓存问题）
- 解决：从 topstories.json 拿 ID 列表后，查前5个ID逐个获取，取最新时间戳作为当天参考

## 搜狗微信验证码墙
- 第二次及后续请求几乎必定触发验证码
- 返回 VerifyCode 页面，无法获取正文
- 结论：搜狗微信来源只能提供"标题信号"
- 处理方式：标题含强相关关键词的列为 P2 趋势信号，不承诺原文验证

## GitHub 项目内容获取
- GitHub 页面 JS 渲染，直接 curl 返回不可读的 React 初始化 JSON
- 正确方法：raw.githubusercontent.com/{owner}/{repo}/main/README.md
- 备选：api.github.com/repos/{owner}/{repo} 获取描述和 stars

## 深度补采源差异化策略
| 源类型 | 获取方法 | 备注 |
|--------|---------|------|
| Posthaven 博客 | 列表页无日期，读单篇后搜 JSON-LD datePublished | Sam Altman |
| GitHub 项目 | raw.githubusercontent.com 获取 README | 避免 JS 渲染 |
| Substack | 页面头部有日期文本如 "Apr 28, 2026" | Ethan Mollick 等 |
| 搜狗微信 | 仅标题信号，无正文 | 验证码墙 |
| WordPress 博客 | JSON-LD datePublished 字段可用 | Naval 博客 |

## VibeVoice 类项目参考
- Microsoft VibeVoice：开源语音 AI（ASR+TTS），支持 50+ 语言长音频
- 采集方式：raw.githubusercontent.com/microsoft/VibeVoice/main/README.md
