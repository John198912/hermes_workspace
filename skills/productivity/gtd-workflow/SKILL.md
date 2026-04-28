---
name: gtd-workflow
description: Full Getting Things Done (GTD) productivity system integrated with Hermes agent tools. Capture, clarify, organize, reflect, and engage across tasks, projects, and life areas — leveraging apple-reminders and google-workspace for execution.
tags: [gtd, productivity, task-management, workflow, personal-efficiency]
---

# GTD Workflow

Full Getting Things Done (GTD) system for solopreneurs and content creators. Translates natural-language input into a structured task management pipeline — Capture → Clarify → Organize → Reflect → Engage — using Hermes' existing tools (apple-reminders, google-workspace) as the execution layer.

## When to Use

Use this skill when:
- Brain dumping ideas, tasks, or commitments that need processing
- Planning your day/week and need structured output
- Feeling overwhelmed by too many open loops
- Doing your weekly review
- Breaking down a project (content series, product launch) into actionable steps
- Deciding what to work on right now

## Architecture

```
Input: Natural language dump / project description / weekly prompt
  ↓
Phase 1: CAPTURE
  → Collect everything into an inbox (verbal brain dump, ideas, tasks, commitments)
  ↓
Phase 2: CLARIFY (Process each item)
  → Is it actionable?
    ├─ YES → What's the next action? Is it a single step or a project?
    └─ NO  → Trash / Someday / Reference
  ↓
Phase 3: ORGANIZE
  → Projects (multi-step outcomes) → linear list with next action
  → Next Actions (single step, doable now)
  → Waiting For (delegated items)
  → Calendar (time-specific)
  → Someday/Maybe (future consideration)
  → Reference (non-actionable info)
  ↓
Phase 4: REFLECT (Weekly/Daily Review)
  → Review all lists, update priorities, clear inbox to zero
  ↓
Phase 5: ENGAGE
  → Decision framework: Context → Time Available → Energy Available → Priority
  ↓
Output: Structured task list organized by GTD categories + synced to apple-reminders
```

## Procedure

### Phase 1: CAPTURE — Brain Dump Processing

Given any input (verbal dump, text, voice memo, notes), extract and categorize:

**Extraction rules:**
1. Everything goes into the Inbox first — no judgment, no filtering
2. Flag items with time/date constraints as Calendar items
3. Flag items with explicit or implicit commitments as Tasks
4. Flag ideas, wishes, and "maybe" items as Someday/Maybe

**Input format example:**
```
User: "我脑子里装了好多事——B站视频还没写、下周要跟一个嘉宾连麦、想学
      一下AI视频生成、信用卡账单忘了交、小红书上周的数据还没看、
      想整理一下obsidian笔记、年底要不要去泰国待一个月..."
```

**Output:**
```markdown
## 📥 收集箱

| # | 原始输入 | 类型 | 处理状态 |
|---|---------|------|---------|
| 1 | B站视频还没写 | 项目 | ⏳ 待处理 |
| 2 | 下周跟嘉宾连麦 | 日历 | ⏳ 待处理 |
| 3 | 想学AI视频生成 | someday | ⏳ 待处理 |
| 4 | 信用卡账单忘了交 | 任务 | ⏳ 待处理 |
| 5 | 小红书上周数据 | 任务 | ⏳ 待处理 |
| 6 | 整理obsidian笔记 | 项目 | ⏳ 待处理 |
| 7 | 年底去泰国一个月 | someday | ⏳ 待处理 |
```

### Phase 2: CLARIFY — Process Each Item

For each inbox item, apply this decision tree:

```
Is it actionable?
├── NO
│   ├── Is it trash? → DELETE
│   ├── Is it reference? → Reference folder
│   └── Is it someday? → Someday/Maybe list
└── YES
    ├── Single step (< 5 min)? → DO IT NOW (note in completed list)
    ├── Needs delegation? → Waiting For list
    └── Multi-step outcome?
        ├── Need a project plan? → Projects list
        └── Already clear on next action? → Next Actions list
```

**Output (after processing):**

```markdown
## 📋 项目清单
| 项目 | 下一步行动 | 截止日期 | 状态 |
|------|-----------|---------|------|
| B站视频 [选题名] | 写RIVET骨架 | 本周五 | 活跃 |

## ⚡ 下一步行动
| 行动 | 预计耗时 | 上下文 | 优先级 |
|------|---------|--------|-------|
| 交信用卡账单 | 5min | 手机 | ⭐ 高 |
| 看小红书上周数据 | 15min | 电脑 | 中 |
| 准备连麦大纲 | 30min | 电脑 | ⭐ 高 |

## ⏳ 等待他人
| 事项 | 等待谁 | 跟进日期 |
|------|--------|---------|
| 嘉宾确认连麦时间 | 嘉宾 | 明天 |

## 📅 日历
| 事项 | 时间 | 备注 |
|------|------|------|
| 与嘉宾连麦 | 下周 [日期] [时间] | 提前准备 |

## ☁️ 将来/也许
| 事项 | 触发条件 |
|------|---------|
| 学AI视频生成 | 做完当前3个视频后 |
| 年底去泰国一个月 | 9月再评估 |

## 📚 参考资料
| 资料 | 存放位置 |
|------|---------|
| AI视频生成工具列表 | Obsidian笔记 |
```

### Phase 3: ORGANIZE — Sync to Execution Tools

Before syncing, apply the **2-minute rule**: any task taking < 2 minutes → do immediately and remove from list.

Then sync actionable items to [apple-reminders] and [google-workspace]:

**Priority Rules:**
- ⭐ High (red flag) → Must do today
- Medium (yellow) → This week
- Low → Whenever

**Context Tags (for filtering when deciding what to do):**
- `@phone` — can do on mobile
- `@computer` — needs computer
- `@home` — at home only
- `@errand` — out of house
- `@think` — needs focused thinking time

### Phase 4: REFLECT — Weekly Review Template

Conduct a structured weekly review:

```markdown
## 📆 每周回顾: [日期]

### 1. 清理收集箱
- [ ] 收集箱清空（所有项目都已处理）

### 2. 回顾项目清单
- [ ] 每个项目都有明确的下一步行动吗？
- [ ] 有项目需要搁置/取消吗？
- [ ] 有什么新项目要加入？

### 3. 回顾下一步行动
- [ ] 哪些没做完？需要重新排期还是放弃？
- [ ] 有没有超过2周没动的任务？需要处理还是删除？

### 4. 回顾日历
- [ ] 过去一周的预约都完成了？
- [ ] 未来一周有什么需要准备的？

### 5. 回顾等待清单
- [ ] 给等待的人发跟进消息

### 6. 回顾将来/也许
- [ ] 有什么可以转为项目了吗？
- [ ] 有什么确定不要的？删除

### 7. 内容创作专项
- [ ] 本周发布了多少条内容？
- [ ] 每条内容的数据如何？
- [ ] 下周的选题定了吗？
- [ ] 选题池里还有什么值得做的？

### 8. 本周 Wins 🏆
[写3件值得庆祝的事]
```

### Phase 5: ENGAGE — Decision Framework

When deciding what to work on right now:

1. **Context**: Where are you? (@phone / @computer / @home / @errand)
2. **Time available**: How much time before your next commitment? (5min / 15min / 1hr / 3hr)
3. **Energy level**: High / Medium / Low
4. **Priority**: Does this move the needle on your current goals?

```markdown
## 🎯 现在做什么？

当前环境: @computer
可用时间: 2小时
精力水平: 中高

建议:
1. ⭐ 写B站视频RIVET骨架 (60min) — 高优先级，需要电脑
2. 交信用卡账单 (5min) — 马上做了，避免忘记
3. 看小红书上周数据 (15min) — 中等优先级
```

## Weekly Rituals

### Daily Startup (5 min)
```markdown
1. 快速扫描收集箱（有新的扔进来吗？）
2. 查看今天的日历事件
3. 选3件今天必须完成的事
4. 检查下一步行动清单，选最高优先级开始做
```

### Daily Shutdown (5 min)
```markdown
1. 收集箱清空（今天的想法/任务全部处理）
2. 更新任务状态（完成/推迟/取消）
3. 看看明天的日历
4. 笔记：今天完成的一件事
```

### Weekly Review (30 min)
Use the REFLECT template above. Best done Friday afternoon or Sunday evening.

## Best Practices

- **Inbox Zero as a habit** — don't let the inbox accumulate more than 24h
- **The 2-minute rule saves hours** — if it takes < 2 min, DO IT NOW
- **Projects ≠ tasks** — a project has multiple steps; the next action is what goes on the list
- **Review rhythm is everything** — daily 5min + weekly 30min keeps the system alive
- **Trust the system** — once you write it down, you can forget about it until review time

## Integration with Existing Tools

| Function | Hermes Tool | Usage |
|----------|------------|-------|
| Task storage | apple-reminders skill | Create/complete/update reminders |
| Calendar events | google-workspace skill | Time-specific items |
| Reference notes | obsidian skill or apple-notes skill | Non-actionable info |
| Project tracking | local markdown or apple-reminders | Multi-step outcomes |

## Pitfalls

- **Don't over-organize** — GTD is a system for getting things DONE, not a system for organizing things forever
- **Don't use GTD as a procrastination tool** — organizing is not doing
- **Don't skip the weekly review** — the system decays fast without it
- **Don't put someday items in your active lists** — that's how you get overwhelmed
- **Don't be rigid** — adapt the system to your reality as a solopreneur/content creator

## Verification

A healthy GTD system has:
- [ ] Inbox: Empty or < 5 items
- [ ] Next Actions: < 20 items (all doable)
- [ ] Projects: < 10 active projects
- [ ] Waiting For: < 5 items
- [ ] Calendar: Only time-specific items (not general todos)
- [ ] Weekly review done within the last 7 days
