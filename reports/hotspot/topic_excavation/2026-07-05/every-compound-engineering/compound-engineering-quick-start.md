# 🚀 Quick Start：今晚就建你的 CLAUDE.md

> **配套报告**：Every 复利工程深度挖掘（report.md）
> **行动等级**：可信（基于一手 Every 公开方法论 + GitHub README 验证）
> **预期时长**：30 分钟看到第一个复利资产

---

## 1 分钟理解版

> **复利工程 = 让 AI 记住你犯过的每一个错。**
> **不是写更多，是知道更多。**

Every 公司的 15 人维护 5 款产品，每天一份 AI 简报，年收 7 位数。但他们的工程师**几乎不写代码**——他们写的是**CLAUDE.md**（一个让 AI 自动读取的项目记忆文件）。

今晚你要做的，就是这一步。

---

## 30 分钟 3 步行动

### 第 1 步：选项目（5 分钟）

**打开你的 git 仓库**。找到**最小的一个**——一个长跑了一段时间的项目。

> ⚠️ **不要选最想要成功的项目**。选最有感觉的——那种「这个我想好好做下去」的项目。
>
> 为什么？复利的本质是**长期主义**——今晚只是开始。选一个能跑一年的，比一个"看起来高大上"的更值得。

**候选项目**：
- ✓ 你的个人网站 / 博客
- ✓ 一个 side project（哪怕只是 idea 阶段）
- ✓ 你在公司的小工具 / 内部脚本
- ✓ 一份长期更新的笔记 / 文档系统
- ✗ 太大的（先复制小项目练手）
- ✗ 完全空的（不能写"失败的修复"）

---

### 第 2 步：装工具（10 分钟）

#### 选项 A：Claude Code CLI（推荐，免费）

```bash
# 安装（macOS/Linux）
curl -fsSL https://claude.ai/install.sh | sh

# 启动
cd /path/to/your-project
claude
```

[官方文档](https://docs.claude.com/en/docs/claude-code) · 安装问题：先 `claude --version` 验证

#### 选项 B：Cursor 编辑器（图形化，免费层）

1. 下载：https://www.cursor.com/
2. 打开 → 选择你刚才选的项目文件夹
3. 按 `Ctrl+K`（Windows/Linux）或 `Cmd+K`（Mac）调起 AI

#### 选项 C（进阶）：装 Every 复利工程 plugin

这是 Dan Shipper 的开源方法论——包含 26 个 review agents + 23 个 workflow commands：

```bash
# 安装 plugin
claude /plugin marketplace add https://github.com/EveryInc/every-marketplace
claude /plugin install compound-engineering

# 验证
ls ~/.claude/plugins/compound-engineering  # 应该看到 agents/ commands/ skills/
```

[GitHub: EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin)

---

### 第 3 步：写第一条复利（10 分钟）

在项目根目录建一个文件 `CLAUDE.md`。

**最小版本**：

```markdown
# 项目代号：<你的项目名>

## 项目背景
- 这是做什么的（1-2 句）
- 给谁用（用户是谁）

## 我的偏好（AI 必须遵守）
- 代码风格偏好（如：用 functional 风格）
- 注释偏好（如：关键函数都要解释 why）
- 禁止项（如：不引入第三方 UI 库）

## 项目规则
- 每次重要修改都要更新本文件
- docs/solutions/ 里保存踩过的坑
- 不要的方案也要记录原因

## 当前正在进行
- （留空，工作中更新）
```

**实战小贴士**：
- ✓ **从 1 行开始**：不要想写完美。先写 1 行 = 写过 = 复利的种子
- ✓ **append-only**：只往后加内容，从不删除——这是复利的关键（vibe coding 时代教的是"删得更快"，但复利工程是"加得更聪明"）
- ✓ **说人话**：CLAUDE.md 不是文档，是给 AI 看的"用户须知"——像对聪明的实习生说"我偏好 X"

---

## 下周工作流（每个工作日花 5 分钟）

每天工作时，遇到任何 **AI 犯的错**（「哦它又这样写了」「又踩这个坑了」），

**不要只修复**——加一行到 CLAUDE.md：

```markdown
## 2026-07-XX: <简短的教训标题>
- 发生了什么：一句话说
- AI 的错误：具体写错的地方
- 期望行为：下次 AI 应该怎么做
```

把"如何修复这个 bug"写进 `docs/solutions/YYYY-MM-DD-bug-name.md`（如有装 plugin）：

```bash
# plugin 装好后用这个命令
/ce-compound
```

下次 AI 会**自动读**这份文档——会避开同样的坑。

---

## 30 天后预期的复利效果

| 阶段 | 你的感觉 | 指标 |
|------|---------|------|
| **第 1 周** | AI 还是老犯同样错 | CLAUDE.md 5 行 |
| **第 2 周** | AI 开始按你偏好写 | CLAUDE.md 15 行 |
| **第 4 周** | AI 写出来直接可用，修改 < 30% | CLAUDE.md 50 行，docs/solutions 5-8 篇 |
| **第 12 周** | 同事能用你的 CLAUDE.md 半小时上手你的项目 | docs/solutions 20 篇，新人入项 1 天 |

> **类比**：CLAUDE.md 是你的「**项目级个人品味博物馆**」。AI 每次开新会话从 0 开始，但你的 CLAUDE.md 让它**直接跳到认识你 1 个月的状态**。

---

## 进阶：完整 7 步循环（v2 升级版）

如果你的项目变大了，需要更系统的方法——这是 Kieran Klaassen 在 2026 年 5 月发布的升级版：

```
Ideate → Brainstorm → Plan → Work → Review → Polish → Compound
```

| 步数 | 你做什么 | AI 做什么 |
|------|---------|----------|
| **Ideate** | 决定做什么 | — |
| **Brainstorm** | 一对一问答 | 问清晰问题 |
| **Plan** | 验证方案 | 研究代码库 + 外部文档 + 设计 |
| **Work** | 监控 | 执行 + 跑测试 + 修小 bug |
| **Review** | 拍板 | 多 agent 并行审 + P1/P2/P3 三级 |
| **Polish** | 点击判断「感觉不对」| 修反馈 + 重测 |
| **Compound** | 写复利文档 | — |

> **核心洞察**：**人做头（Ideate + Brainstorm）和尾（Polish + Compound）**。**AI 做中间（Plan + Work + Review）**。
> 
> 这就是 Kieran 的 AI Sandwich：**AI 是肉馅，你是面包。**

---

## FAQ（卷哥会被问到的问题）

**Q：写了 CLAUDE.md 后 AI 真的会读吗？**
A：会。Claude Code 和 Cursor 的 agent 模式启动时会**自动读 CLAUDE.md**——这是官方设计。你可以验证：起一个新会话，让 AI 读你的文件，问它"我的项目用什么代码风格？"它会答。

**Q：多久需要更新一次？**
A：每次 AI 犯一个"明显的错"就加 1 行。一周 1-3 行是合理节奏。不要写完后期待 AI 永远不犯——它会，但**会少犯**。

**Q：和 Cursor `.cursorrules` 有什么区别？**
A：相同理念，格式略不同。CLAUDE.md 是 Anthropic 生态，.cursorrules 是 Cursor 生态。**建议**：项目根目录**同时建两个**——内容基本一致，互为备份。

**Q：这不会"教会"AI 替换我吗？**
A：反了。**你**在 CLAUDE.md 上写的是**你的**品味。AI 没有品味——所以你不可替代。这和你写一份 onboarding 文档给新人是同一件事，只是现在新人叫 AI。

**Q：复利工程的真正反方？**
A：见主报告「五、反方与质疑」。Booking.com 说「跨团队协作是新瓶颈」，但那是大公司问题；对超级个体（1-3 人），CLAUDE.md 直接解决了个人知识沉淀问题——复利是反解药。

---

## 90 天挑战（可选）

如果你准备认真做：

1. **第 1-30 天**：每天花 5 分钟写 CLAUDE.md
2. **第 31-60 天**：开始写 docs/solutions/（每周 1-2 篇）
3. **第 61-90 天**：邀请一个朋友一起用——**两个 CLAUDE.md 比一个有用 10 倍**

> 这个挑战的核心不是写得多，是**持续**——复利靠的是每天 1 行，不是周更 1000 行。

---

## 想进一步？

| 你想知道 | 看哪里 |
|---------|--------|
| Every 复利工程理论 | https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents |
| Every 复利工程操作 | https://every.to/guides/compound-engineering |
| Kieran 实战手册 | https://creatoreconomy.so/p/how-to-make-claude-code-better-every-time-kieran-klaassen |
| 完整 GitHub repo | https://github.com/EveryInc/compound-engineering-plugin |
| 深度长文拆解 | `report.md`（本目录） |
| 多平台内容脚本 | `content-production-multi-platform.md`（本目录） |

---

**今晚你只有一件事**：建一个 CLAUDE.md，写一行。

> **AI 是工具，哲学是地基，你才是杠杆的支点。**
> **从一行开始，复利自动启动。**
