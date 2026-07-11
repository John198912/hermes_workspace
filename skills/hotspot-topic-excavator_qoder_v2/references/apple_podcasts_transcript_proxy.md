# Apple Podcasts Show Notes 作为播客 Transcript 替代信源

> 版本：v1.0 · 2026-07-08 · Naval "Live in the Future" 实证
> **Qoder 工具适配版**：原 Brave web_search → WebSearch

## 问题

播客类话题深挖时，完整逐字稿（transcript）是最理想的素材源。但在以下情况下无法获取：

| 场景 | 典型失败 |
|------|---------|
| YouTube 字幕 API | `youtube_transcript_api` 版本 API 变更；`yt-dlp` 未安装 |
| 播客官网 show notes 极简 | nav.al 仅 26 词摘要 + 主题标签 |
| 播客 RSS content:encoded | 仅标题+链接，无正文 |

## 发现：Apple Podcasts Show Notes = 高密度素材源

当 WebSearch 命中 Apple Podcasts 条目时，搜索结果中包含该集完整的 **章节时间码 + 金句**列表。

### 实证案例：Naval "Live in the Future" (Jul 2 2026)

**WebSearch 返回的 Apple Podcasts 条目包含：**

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
- **完整度**：约 90%——缺失的是论证细节和来回对话

### 采集方法

```
# WebSearch 命中 Apple Podcasts
WebSearch(query="[Podcast Name] episode title guest name Apple Podcasts")
```

### 适用条件

| 条件 | 必须？ |
|------|--------|
| 播客是 Apple Podcasts 上架的热门节目 | ✅ 必要条件 |
| 发布者手动添加了章节标记 | ✅ 内容质量前提 |
| WebSearch 能命中该 Apple Podcasts 条目 | ✅ 技术前提 |

### 不适用场景

- 非英语或非主流播客（Apple Podcasts 收录不完整）
- 发布者未添加章节（只有标题无时间码）
- 需要逐字对话细节

## 与 YouTube Transcript API 的关系

| 路径 | 成功率 | 信息密度 | 适用 |
|------|--------|---------|------|
| YouTube Transcript API (Bash+Python) | ~70%（API 变动 + 网络限制） | 极高（逐字稿） | 首选 |
| Apple Podcasts show notes (WebSearch) | ~60%（需要 WebSearch 命中 + 播客有章节） | 高（金句+结构） | **并行第二选择** |
| 二者都失败 | ~10% | — | 标注 [BLOCKED]，看降级路径 |

**建议工作流**：
1. YouTube transcript 和 Apple Podcasts show notes **同时并行尝试**
2. 任一成功即可进入素材组织阶段
3. 两者都成功 → 互校验，提升金句准确性

## `youtube_transcript_api` 诊断

```
# 正确调用链
ts_list = YouTubeTranscriptApi.list("video_id")     # 获取可用 transcript 列表
ts = ts_list.find_transcript(['en'])                    # 找到英文 transcript
transcript = ts.fetch()                                 # 获取逐字稿
```

> ⚠️ `youtube_transcript_api` 的 API 在不同版本间有过 breaking changes。如果以上仍不工作，**不要在此阻塞**——直接切 Apple Podcasts show notes 路径，标注 [NO_YT_TRANSCRIPT]。
