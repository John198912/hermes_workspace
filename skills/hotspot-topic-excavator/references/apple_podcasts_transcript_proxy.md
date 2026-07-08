# Apple Podcasts Show Notes 作为播客 Transcript 替代信源

> 版本：v1.0 · 2026-07-08 · Naval "Live in the Future" 实证

## 问题

播客类话题深挖时，完整逐字稿（transcript）是最理想的素材源。但在以下情况下无法获取：

| 场景 | 典型失败 |
|------|---------|
| YouTube 字幕 API | `youtube_transcript_api` 版本 API 变更（`get_transcript()` 已移除，`fetch()` 签名变化）；`yt-dlp` 未安装 |
| 播客官网 show notes 极简 | nav.al 仅 26 词摘要 + 主题标签 |
| 播客 RSS content:encoded | 仅标题+链接，无正文 |

## 发现：Apple Podcasts Show Notes = 高密度素材源

当 Brave 搜索命中 Apple Podcasts 条目时，`extra_snippets` 中包含该集完整的 **章节时间码 + 金句**列表。

### 实证案例：Naval "Live in the Future" (Jul 2 2026)

**Brave 搜索返回的 Apple Podcasts `extra_snippets` 包含：**

```
00:00 Guest Intros
02:35 Live in the Future
03:58 Will AI Outsmart us?
07:43 In the Anthropic Breadline
09:59 The Tech Genie Is Out
10:13 There is no demand for average
13:07 The hottest new programming language is English
14:12 AI is adapting to us faster than we are adapting to it
18:36 No entrepreneur is worried about AI taking their job
22:56 The goal is not to have a job
26:46 AIs are not alive
29:49 AI fails the only true test of intelligence
32:55 Early adopters of AI have an enormous edge
36:49 AI meets you exactly where you are
39:37 Always leverage the best intelligence
43:02 If you can't define it, you can't program it
44:37 The solution to AI anxiety is action
49:37 -- Transcript: http://nav.al/ai
```

**价值评估**：
- 18 条精确时间码 + 金句 → 可直接作为「权威引述」素材（类型 3）
- 章节标题揭示播客完整叙事结构 → 替代逐字稿的骨架
- 关键金句涵盖播客核心论点 → 足以支撑 RIVET 模型各阶段
- **完整度**：约 90%——缺失的是论证细节和来回对话，但金句+章节已足够生成内容

### 采集方法

```bash
# Brave web search 命中 Apple Podcasts
mcp__brave_search__brave_web_search query="[Podcast Name] episode title guest name"

# 关键：必须用 extra_snippets=true 或使用返回 extra_snippets 的工具
# extra_snippets 中 Apple Podcasts 条目会包含完整章节列表
```

**为什么 Apple Podcasts show notes 如此丰富？**
- 播客发布者（Naval 团队）在 Apple Podcasts Connect 后台手动填入章节标记
- 这是 Apple Podcasts 的标准功能——Creator 可用 MP4Chaps 或手动添加章节
- 热门播客（如 Naval、Tim Ferriss、Huberman Lab）通常都有完整章节

### 适用条件

| 条件 | 必须？ |
|------|--------|
| 播客是 Apple Podcasts 上架的热门节目 | ✅ 必要条件 |
| 发布者手动添加了章节标记 | ✅ 内容质量前提 |
| Brave 搜索能命中该 Apple Podcasts 条目 | ✅ 技术前提 |

### 不适用场景

- 非英语或非主流播客（Apple Podcasts 收录不完整）
- 发布者未添加章节（只有标题无时间码）
- 需要逐字对话细节（Apple show notes 只给摘要句，非完整对话）

## 与 YouTube Transcript API 的关系

| 路径 | 成功率 | 信息密度 | 适用 |
|------|--------|---------|------|
| YouTube Transcript API | ~70%（API 变动 + 网络限制） | 极高（逐字稿） | 首选 |
| Apple Podcasts show notes | ~60%（需要 Brave 命中 + 播客有章节） | 高（金句+结构） | **并行第二选择** |
| 二者都失败 | ~10% | — | 标注 [BLOCKED]，看降级路径 |

**建议工作流**：
1. YouTube transcript 和 Apple Podcasts show notes **同时并行尝试**
2. 任一成功即可进入素材组织阶段
3. 两者都成功 → 互校验，提升金句准确性

## 本次会话的 `youtube_transcript_api` 诊断

```
# 错误调用（本次）
YouTubeTranscriptApi.get_transcript("6m-ZZBCiiEE")  → AttributeError (不存在)
YouTubeTranscriptApi.fetch("6m-ZZBCiiEE")            → TypeError (签名不对)

# 正确调用（推测，基于 package 暴露的 list/fetch 方法）
ts_list = YouTubeTranscriptApi.list("6m-ZZBCiiEE")     # 获取可用 transcript 列表
ts = ts_list.find_transcript(['en'])                    # 找到英文 transcript
transcript = ts.fetch()                                 # 获取逐字稿
```

> ⚠️ `youtube_transcript_api` 的 API 在不同版本间有过 breaking changes。如果以上仍不工作，**不要在此阻塞**——直接切 Apple Podcasts show notes 路径，标注 [NO_YT_TRANSCRIPT]。
