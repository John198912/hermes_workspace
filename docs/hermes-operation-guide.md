# Hermes 操作技巧指导文档

> 基于 Hermes Agent v2.0+ · 当前配置: DeepSeek V4 Pro · 上下文窗口 1,000,000 tokens

---

## 目录

1. [会话隔离：核心概念](#一会话隔离核心概念)
2. [会话管理命令速查](#二会话管理命令速查)
3. [上下文隔离：实战场景](#三上下文隔离实战场景)
4. [Profile 完全隔离方案](#四profile-完全隔离方案)
5. [压缩机制：让长对话不爆炸](#五压缩机制让长对话不爆炸)
6. [子代理与并行会话](#六子代理与并行会话)
7. [飞书平台专用技巧](#七飞书平台专用技巧)
8. [常见问题排查](#八常见问题排查)

---

## 一、会话隔离：核心概念

### 1.1 Hermes 的会话模型

Hermes 默认是 **累积式上下文** ——每次发消息，整个对话历史都会塞进系统提示词发给模型。这意味着：

| 行为 | 结果 |
|------|------|
| 同一个 Feishu 聊天窗口连续对话 | 上下文累积，模型"记住"之前说的 |
| 终端 `hermes` 模式连续 `/new` | 每次 `/new` 是**全新会话**，完全清零 |
| 同一个 topic/thread 内多条消息 | 上下文共享（同一 session_id） |
| Feishu 侧边栏开多个 DM 窗口 | **不同 session，完全隔离** |

### 1.2 什么情况下会"串台"

```
会话污染（context contamination）发生的条件：
┌─────────────────────────────────────────────────┐
│ 条件 1: 共享同一个 session_id                    │
│ 条件 2: 话题 A 的上下文还没被压缩出去             │
│ 条件 3: 话题 B 的讨论触发了与话题 A 相关的记忆     │
└─────────────────────────────────────────────────┘
```

**不会串台的场景**（放心）：
- 不同 Feishu 聊天窗口 → 不同 session_id ✅
- 终端 `hermes --profile <name>` 不同 profile → 完全隔离 ✅
- 使用 `/new` 后的会话 → 全新的 session_id ✅
- `delegate_task` 子代理 → 独立的对话上下文 ✅

---

## 二、会话管理命令速查

### 2.1 核心命令一览

| 命令 | 作用 | 适用平台 |
|------|------|----------|
| `/new` 或 `/reset` | **开启全新会话**——最彻底的隔离方式 | CLI + Feishu |
| `/branch` 或 `/fork` | 分支当前会话——克隆上下文但独立发展 | CLI |
| `/clear` | 清屏 + 新会话（仅 CLI） | CLI |
| `/compress` | 手动触发上下文压缩 | CLI + Feishu |
| `/title [名称]` | 为当前会话命名，方便后续 resume | CLI + Feishu |
| `/resume [名称]` | 恢复之前命名的会话 | CLI |
| `/undo` | 移除最后一条对话轮次 | CLI |
| `/save` | 保存对话到文件 | CLI |

### 2.2 CLI 启动命令

```bash
# 全新会话（默认）
hermes

# 继续最近的会话
hermes --continue

# 按会话名称恢复
hermes --resume "内容策略讨论"

# 按 session_id 恢复
hermes --resume 20260508_114300_a1b2c3
```

### 2.3 会话列表与管理

```bash
# 列出最近的会话
hermes sessions list

# 交互式浏览
hermes sessions browse

# 导出会话到 JSONL
hermes sessions export ~/backups/sessions_$(date +%Y%m%d).jsonl

# 重命名
hermes sessions rename SESSION_ID "新名称"

# 删除
hermes sessions delete SESSION_ID

# 清理 N 天前的旧会话
hermes sessions prune --older-than 30

# 会话统计
hermes sessions stats
```

---

## 三、上下文隔离：实战场景

### 场景 A：一个 DM 窗口做多件事——如何不串台

这是卷哥最关心的场景。在 Feishu 的同一个 DM 窗口中，你可能：
- 早上讨论代码重构
- 中午让 SOUL 分析一篇文章
- 下午规划内容选题

**问题**：这些都发生在同一个 session 中，后面的讨论会"看到"前面的上下文。

**解决方案**（按推荐度排序）：

#### 方案 1：`/new` 强隔离 ⭐⭐⭐⭐⭐

```
你：/new
    ↓ 旧会话归档，全新 session 开始
你：现在帮我分析这篇文章 [链接]
```

最彻底。每次不同话题前执行 `/new`。

#### 方案 2：上下文清道夫法 ⭐⭐⭐⭐

```
你：以上内容都完成了，请把后续需要的信息总结出来，然后我们开启一个新话题：[新话题描述]
```

让模型自己做"上下文交接"——保留必要信息，释放不必要的历史。

#### 方案 3：飞书多窗口法 ⭐⭐⭐⭐

在飞书中同时开多个 DM 窗口（侧边栏可以同时存在），每个窗口自动对应一个独立 session_id。关键是要在不同的聊天入口中发起：

- 窗口 1：从飞书工作台入口进入 → session_A
- 窗口 2：从侧边栏搜索进入 → session_B
- 窗口 3：从群聊 `@` 转发到 DM → session_C

> ⚠️ 注意：飞书平台的 session 路由取决于入口方式。同一个入口反复进入 = 同一个 session。建议用不同入口（比如从不同群聊跳转）来开独立 DM。

#### 方案 4：`/compress` 手动压缩 ⭐⭐⭐

```
你：/compress
```

强制压缩上下文。压缩后旧内容变成摘要（不再是逐字对话），新话题的污染降至最低。

### 场景 B：同时跑多个独立任务

```bash
# 终端 A：内容创作相关
hermes --profile soul
# 内部：/skill soul

# 终端 B：代码开发相关
hermes --profile dev
# 内部：/skill claude-code

# 终端 C：热点研究 cron
hermes cron run <job_id>
```

三个 terminal 窗口 = 三个完全独立的 session。零串台风险。

### 场景 C：同一话题的多阶段工作

不需要完全隔离，但需要"阶段性保存"：

```
阶段 1（分析）：
你：帮我分析最近 AI 领域的热点 → [模型回复]
你：/title AI热点分析-阶段1

阶段 2（策略讨论，几天后）：
你：/title AI热点分析-阶段2
你：基于上次的分析，现在讨论内容选题策略...
```

通过命名 + 定期 `/compress`，保持上下文聚焦。

### 场景 D：SOUL 人格 vs 普通助手模式

当你想在同一个窗口切换"SOUL 身份"和"普通助手身份"：

```
# 启动 SOUL 模式
你：/skill soul
[此时 SOUL 人格加载]

# 切换回普通模式
你：/new
你：请帮我查一下 git 命令怎么撤销最后一次 commit
[全新会话，无 SOUL 人格影响]
```

---

## 四、Profile 完全隔离方案

Profile 是 Hermes 最强隔离机制——每个 profile 有独立的：
- 配置文件 (`config.yaml`)
- API 密钥 (`.env`)
- 技能集 (`skills/`)
- 会话存储 (`sessions/`)
- 记忆 (`memory`)
- 日志 (`logs/`)

### 4.1 创建专用 Profile

```bash
# 创建 SOUL 内容创作 profile
hermes profile create soul \
  --clone          # 从当前配置克隆

# 创建开发 profile
hermes profile create dev \
  --clone-from default  # 从特定 profile 克隆

# 创建热点研究 profile（精简版）
hermes profile create hotspot \
  --clone-from default
```

### 4.2 配置不同 Profile

```bash
# 切换到 soul profile
hermes --profile soul config edit
# 设置为 DeepSeek + SOUL 专属 skills

# 切换到 dev profile
hermes --profile dev config edit
# 设置为 Claude Sonnet + coding skills
```

### 4.3 使用 Profile

```bash
# 启动指定 profile
hermes --profile soul
hermes --profile dev

# 查看所有 profile
hermes profile list

# 设置默认
hermes profile use soul
```

### 4.4 Profile 隔离矩阵

```
┌───────────┬─────────┬──────────┬─────────┬─────────┐
│ Profile   │ 模型    │ Skills   │ 记忆    │ 上下文  │
├───────────┼─────────┼──────────┼─────────┼─────────┤
│ soul      │ DeepSeek│ content  │ SOUL专属│ 独立    │
│ dev       │ Claude  │ coding   │ 项目信息│ 独立    │
│ hotspot   │ 快速模型│ research │ 热点历史│ 独立    │
│ default   │ DeepSeek│ 通用     │ 通用    │ 独立    │
└───────────┴─────────┴──────────┴─────────┴─────────┘
```

> 💡 **最佳实践**：为长线项目（如 SOUL 内容品牌）创建专属 profile，避免日常杂务污染品牌人格。

---

## 五、压缩机制：让长对话不爆炸

### 5.1 当前配置解读

你的当前压缩配置（来自 `~/.hermes/config.yaml`）：

| 参数 | 当前值 | 含义 |
|------|--------|------|
| `compression.enabled` | `true` | 自动压缩已开启 |
| `compression.threshold` | `0.70` | 当上下文使用率达 70% 时触发压缩 |
| `compression.target_ratio` | `0.20` | 压缩后保留 20% token 预算给压缩内容 |
| `compression.protect_last_n` | `20` | 保护最近 20 条消息不被压缩 |
| `context.engine` | `compressor` | 使用压缩引擎（非滑动窗口） |
| `model.context_length` | `1,000,000` | DeepSeek V4 Pro 上下文窗口 |

### 5.2 压缩的实际效果

以 100 万 token 窗口为例：

```
时间线 ─────────────────────────────────────────────────►

消息 1-100          消息 101-120           消息 121-150
(打包压缩)          (保护区域)             (新增对话)
    ↓
变成一段摘要        保留原文              未压缩

总消耗: ~140K tokens (摘要) + 消息101-150 的 token
```

**这意味着**：当旧话题被压缩后，它对后续讨论的影响已经大幅降低，相当于"自然隔离"。

### 5.3 如何使用压缩做隔离

```bash
# 方法 1：调到更激进的压缩
hermes config set compression.threshold 0.4
# 上下文使用 40% 就触发压缩（更快"遗忘"旧话题）

# 方法 2：保护更少的消息
hermes config set compression.protect_last_n 5
# 只保护最近 5 条，旧内容更快被压缩

# 方法 3：手动触发
输入 /compress
```

### 5.4 压缩 vs `/new` 的选择

| | `/new` | 压缩 |
|------|--------|--------|
| 隔离程度 | 100%（完全清零） | 80-90%（摘要残留） |
| 保留信息 | 无 | 保留压缩后的关键信息 |
| 适用场景 | 话题完全切换 | 同一话题但想"换口气" |
| 成本 | 需要重新加载 skill/人格 | 无缝衔接 |

---

## 六、子代理与并行会话

### 6.1 `delegate_task` 隔离机制

`delegate_task` 创建的每个子代理拥有**完全独立的对话上下文**：

```
父代理（你的主会话）
├── 子代理 A：独立的 system prompt + 工具集 + 上下文
├── 子代理 B：独立的 system prompt + 工具集 + 上下文
└── 子代理 C：独立的 system prompt + 工具集 + 上下文
```

每个子代理：
- 不知道父代理的对话历史（除非你通过 `context` 参数传给它）
- 不知道其他子代理的存在
- 完成后只返回摘要

### 6.2 使用场景

```
# 场景：同时研究 3 个独立话题，互不干扰
delegate_task(
    tasks=[
        {"goal": "研究 OpenAI 最新动态", "context": "关注 AGI 政策"},
        {"goal": "研究 Anthropic 最新动态", "context": "关注安全研究"},
        {"goal": "研究国内 AI 动态", "context": "关注产品发布"}
    ]
)
```

### 6.3 终端级并行会话

```bash
# 使用 tmux 完全独立运行
# 窗口 1
tmux new-session -d -s soul-agent 'hermes --profile soul'
tmux send-keys -t soul-agent "分析最近的 AI 热点" Enter

# 窗口 2
tmux new-session -d -s dev-agent 'hermes --profile dev'
tmux send-keys -t dev-agent "重构用户模块" Enter

# 查看各自输出
tmux capture-pane -t soul-agent -p | tail -20
tmux capture-pane -t dev-agent -p | tail -20
```

---

## 七、飞书平台专用技巧

### 7.1 识别当前 Session

飞书平台上，你可以在消息中包含以下问句来了解当前会话状态：

```
你：当前是什么 session？
# Hermes 会返回 session_id

你：/status
# 显示会话信息
```

### 7.2 飞书多 Session 的入口策略

```
飞书 DM 的 session 路由规则（经验总结）：

入口 A：飞书工作台 → Hermes → DM
  └→ session_id: feishu_direct_worker_xxx

入口 B：群聊 @Hermes → 对话展开 → 点进 DM
  └→ session_id: feishu_group_bridge_xxx

入口 C：搜索栏搜索 Hermes → 进入 DM
  └→ session_id: feishu_search_xxx

每个入口 = 独立 session = 独立上下文
```

### 7.3 飞书平台的限制

| 机制 | 飞书是否支持 |
|------|-------------|
| `/new` 开新会话 | ✅ 支持 |
| `/branch` 分支 | ❌ 平台不支持 |
| `/compress` 手动压缩 | ✅ 支持 |
| `/title` 命名 | ✅ 支持 |
| `/resume` 恢复 | ❌ 仅 CLI |

### 7.4 飞书平台隔离最佳实践

```
实践 1：不同话题用不同入口进 DM
  - 内容讨论：从工作台进
  - 技术问题：从群聊跳转进
  - 日常问答：从搜索进

实践 2：话题间主动 /new
  - 每完成一个大话题后 /new
  - 避免"早上讨论代码 → 下午讨论内容"的串台

实践 3：长话题用 /compress 刷新
  - 如果同一个话题讨论超过 50 轮
  - /compress 一下再继续
```

---

## 八、常见问题排查

### Q1: 为什么感觉 Hermes 在"翻旧账"？

**症状**：当前讨论的话题 A，Hermes 突然引用了 30 分钟前的话题 B 的信息。

**原因**：压缩还没触发，旧上下文仍然完整存在。

**解决**：
```
1. 输入 /compress （立即压缩）
2. 或输入 /new （完全清除）
3. 考虑调低 compression.threshold 到 0.4
```

### Q2: `/new` 后 SOUL 人格"没了"？

**症状**：`/new` 之后，SOUL 的说话风格恢复默认。

**原因**：`/new` 重置了 system prompt，skill 需要重新加载。

**解决**：
```
输入 /skill soul   # 重新加载 SOUL 人格
```

或在启动时指定：
```bash
hermes --skills soul
```

### Q3: 不同 Feishu DM 窗口串台了？

**症状**：窗口 A 的对话影响到了窗口 B。

**排查**：
```
1. 检查是否从同一个入口进入（比如都是工作台）
2. 每个窗口问一次：当前 session_id 是什么？
3. 如果 session_id 相同 → 换入口重进
```

### Q4: 压缩后丢失了重要信息？

**症状**：`/compress` 之后，模型不记得你需要的关键上下文。

**预防**：
```
在压缩前主动说：
"请把后续工作需要的所有关键信息总结出来。
包括：[项目信息]、[待办事项]、[重要决策]"
```

### Q5: 怎么查看当前 token 使用量？

```
# CLI 模式
/usage

# 配置中查看
hermes config edit  # 看 context_length 和 compression.threshold
```

---

## 附录：决策流程图

```
开始新话题
    │
    ├─ 和当前话题完全无关？
    │   ├─ 是 → /new （最彻底）
    │   └─ 否 → 继续判断
    │
    ├─ 和当前话题有关联但需要"换口气"？
    │   ├─ 是 → /compress
    │   └─ 否 → 继续判断
    │
    ├─ 只想临时开个子线程？
    │   ├─ 是 → delegate_task （并行隔离）
    │   └─ 否 → 继续判断
    │
    └─ 需要永久隔离（不同人格/不同项目）？
        └─ 是 → hermes --profile <name>（完全隔离）
```

---

## 附录：卷哥的推荐配置

基于你的使用习惯和工作流：

```yaml
# 推荐调整项（可选）
compression:
  threshold: 0.5        # 从 0.7 调到 0.5，更早压缩
  protect_last_n: 10    # 从 20 调到 10，减少旧信息保护

# 创建 SOUL 品牌专用 profile
# hermes profile create soul --clone
# 然后在 soul profile 中：
#   - 固定使用 SOUL skill
#   - 独立的记忆（不吸收日常对话）
#   - 独立的会话历史
```

---

> **核心原则**：`/new` 是最简单的隔离，`profile` 是最彻底的隔离，`compress` 是最自然的渐进隔离。三者配合使用，根据不同场景选择不同方案。

*文档生成时间：2026-05-08*
*基于 Hermes Agent v2.0 · 配置快照：DeepSeek V4 Pro, context_length=1M*
