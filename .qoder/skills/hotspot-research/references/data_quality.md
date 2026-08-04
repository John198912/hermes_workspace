# 数据质量与审核参考 (Data Quality)

> **用途**：三关审核详细表、各源审计指南、已知问题。
> **加载时机**：Agent 审核采集结果时加载。

---

## 三关审核 — 详细标准

### 第一关：时效关 (Timeliness)

| 任务 | 要求 | 判断方式 |
|------|------|---------|
| 日报 | 24 小时内 | 采集时间、HN/Reddit API 时间戳、标题关键词（"今日"/"刚刚"）、文章日期文本 |
| 周报 | 7 天内 | 同上，7 天窗口 |

**时效信号保留规则**：

采集阶段必须保留每条原始信号的时效字段，不可只取标题摘要而丢弃日期。

| 采集源 | 时效字段 | 格式 | 保留方式 |
|--------|---------|------|---------|
| WebSearch 结果 | `page_age`（如 "1 day ago"） | 相对时间 | 转换为绝对日期 |
| HackerNews | `time` (Unix timestamp) | epoch seconds | `datetime.fromtimestamp(time)` |
| Reddit | `created_utc` (Unix timestamp) | epoch seconds | 同上 |
| 搜狗微信 | 文章页日期文本 | 混合 | 从页面提取，置信度中等 |
| Python Engine JSON | `first_seen` 字段 | ISO-8601 | 直接保留 |

**转换公式**（相对时间 → 绝对日期）：
- "15 hours ago" + 当前时间 = 绝对日期
- "1 day ago" → 当前日期 - 1（仍可能 < 24h）
- "3 days ago" → 自动降级 P2（除非有持续发酵论证）
- 保守推定：如仅有相对时间无精确时间，取最晚可能时间

**已知时效问题**：
- 百度热搜：无法确定发布时间 → 默认低优先级，仅在含 AI/转型 关键词且有独立时效证据时保留
- 搜狗微信：无法准确确定发布时间 → 同上处理
- 36氪 API：可能返回缓存数据 → 需检查日期字段

### 第二关：来源可信度 (Source Credibility)

| 评级 (platforms.md) | 信任级别 | 处理方式 |
|---------------------|---------|---------|
| S | 高 | 优先使用 |
| A | 中高 | 可用 |
| B | 中 | 按内容判断；无特殊价值则丢弃 |
| N/A (未知) | 低 | 丢弃 |

Python 脚本的 `platform_rating` 字段（S/A/B）仅供参考，Agent 做最终判断：
- **S**（关键博客/Newsletter）：可信，优先
- **A**（Reddit/HN/B站）：可信，需判断赛道匹配
- **B**（百度/搜狗微信）：内容必须通过匹配检查
- **C**（百度噪声）：默认丢弃，除非明确相关

### 第三关：赛道匹配 (Topic Match)

| 标签组合 | 优先级 | 含义 |
|---------|--------|------|
| [AI] + [超级个体] | **P0** | 双标签命中，直接相关 |
| [AI] only | P1 | 需关联到超级个体/转型 |
| [超级个体] only | P1 | 需找 AI 角度 |
| 子标签命中（工具/职场/情绪等） | P2 | 趋势信号或可蹭热度 |
| 无标签命中 | 丢弃 | 与赛道无关 |

匹配不仅基于关键词——使用对内容与赛道相关性的理解。

### 第四关：信息完整度 (Information Completeness)

| 级别 | 标准 | 判断方式 | 处理 |
|------|------|---------|------|
| **完整 (100%)** | 通过 Jina Reader / WebFetch 获取全文 | 干净 Markdown 含段落 | P0 目标 |
| **高 (80%)** | WebSearch + WebFetch 交叉验证 | 两源关键事实一致 | P0/P1 可接受 |
| **中 (60%)** | 单一搜索摘要 | 仅一个来源 | P1 最低要求 |
| **低 (30%)** | 仅标题 + 短摘要 | 无深度来源 | 仅参考，不做深度分析 |

P0 热点必须完整度 ≥ 80%。如 < 80%，降级为 P1。

---

## Jina Reader 重试策略

```
Jina Reader 调用
    ↓
┌─ 200 + 有效 Markdown → 使用
├─ 200 + 空内容 → 重试 1 次（等待 3s）
│   ├─ 第二次成功 → 使用
│   └─ 第二次仍空 → 降级到 WebSearch / WebFetch
├─ 403/503 → 重试 1 次（等待 5s）
│   ├─ 第二次成功 → 使用
│   └─ 第二次仍失败 → 标记 [BLOCKED]，使用 WebSearch
└─ 超时 (>10s) → 重试 1 次（缩短 max-time 8s）
    ├─ 第二次成功 → 使用
    └─ 第二次超时 → 标记 [BLOCKED]，使用 WebSearch

总成本：每个失败源 +3-5s（vs 旧"立即跳过"）
```

---

## 各源审计指南

| 来源 | 采集方式 | 时效可靠性 | 来源信任 | 典型匹配 | 审计备注 |
|------|---------|-----------|---------|---------|---------|
| Sam Altman blog | Jina Reader | 高 — 博客有日期 | S | 高 | OpenAI 战略、AGI 预测。注意：无标题帖子 Jina 渲染为 `## [-]` |
| Naval podcast | Jina Reader | 中 — 有主题但无精确日期 | S | 高 | 超级个体哲学 |
| Karpathy blog | Jina Reader | 低 — 更新不频繁 | S | 高 | LLM 教育。需检查 3 个博客面（github.io + bearblog + ai） |
| Anthropic Research | Jina Reader | 高 — 页面有日期 | S | 高 | research = 论文/安全；news = 产品发布。注意区分 |
| Benedict Evans | Jina Reader | 高 — 博客有日期 | S | 中 | 科技趋势。建议用 sitemap.xml 获取全部帖子 |
| Ethan Mollick | Jina Reader (article URL) | 高 | S | 高 | RSS feed 标题为空（Substack quirk），需从 URL slug 判断 |
| HackerNews | Bash curl Firebase API | 高 — API 时间戳 | A | 中 | 技术趋势；Agent 判断赛道匹配 |
| Reddit | Bash curl JSON API | 高 — API 时间戳 | A | 中 | 高分 + 多评论 = 强信号。Jina 对 Reddit 深度链接可能 403 |
| B站科技区 | Bash curl API | 中 — 有发布日期 | B | 低 | 全品类混合；只关注 AI 标签项 |
| 百度热搜 | Bash curl | 无法确定 | C | 极低 | 默认丢弃；仅在含 AI/转型 关键词 + 高匹配时保留 |
| 搜狗微信 | Bash curl | 无法准确确定 | B | 中 | 仅在标题含 AI/转型/超级个体 关键词时保留。成功率约 20% |
| AI HOT (aihot.virxact.com) | Bash curl REST API | 高 — publishedAt ISO 8601 | S | 高 | 中文AI行业全景雷达。需带 aihot-skill UA。score 0-100 可辅助判断重要性。5 个分类，关键词搜索 |
| 投资界/惊蛰研究所 | Jina Reader | 中 — 文章有日期 | A | 高 | 国内"一人公司"最完整实操图谱 |

### Wikipedia 作为交叉验证源

**场景**：当出现重大 AI 治理/资本事件（如"X 公司与 Y 政府谈判"），单一二手来源可信度可能被怀疑。

**使用模式**（仅用于 P0 治理/资本事件）：
1. WebSearch 已捕获信号 → 标记候选 P0
2. 用 Jina Reader 获取 `https://r.jina.ai/https://en.wikipedia.org/wiki/{Company}` → 查找 Controversies / Government relations / Acquisitions / Funding 章节
3. 找到匹配段落 + 脚注引用 → 升级为 P0 高置信度
4. 未找到 → 保持 P0 但需进一步深读一手报道

**反模式**：不要把 Wikipedia 作为主要信息源——它是交叉验证工具，不是首发源。

---

## Jina Reader 已知行为

| 站点类型 | 质量 | 备注 |
|---------|------|------|
| 简单博客 (Sam Altman/Naval/PG) | 完美 | Markdown 干净，日期保留 |
| Bear/blog (Karpathy) | 完美 | 干净提取 |
| 导航重网站 (Forbes) | 警告 | 80-95% 是导航/菜单文本。可用但需跳过噪声 |
| Fortune.com | 阻断 | DDoS 防护 |
| TIME Magazine | 阻断 | DDoS 防护 |
| The Guardian | 阻断 | DDoS 防护 |
| Reddit | Jina 阻断 + API 不稳定 | 使用 Python 脚本 + WebSearch 摘要 |
| TechCrunch | 阻断 | DDoS 防护。使用 WebSearch 摘要 |
| NYT | 阻断 | CAPTCHA 墙。使用 WebSearch 摘要 |
| Bloomberg | 阻断 | 付费墙 + 反爬 |
| Paul Graham | 完美 | 简单 HTML，无日期，列表顶部=最新 |

**通用模式**：任何有 DDoS 防护或严格 CORS 的新闻网站都可能阻断 Jina Reader。接受搜索摘要作为主要来源——不要重试。

---

## Python 脚本已知问题

1. **36氪**：可能返回缓存数据 → 已在引擎中标记为需检查日期
2. **搜狗微信**：重反爬 — 可用时使用，不可用不强求。成功率约 20%，质量 B 级
3. **百度热搜**：50 条 → 通常仅 1-3 条相关。激进过滤。偶尔回历史垃圾数据 → 整批丢弃
4. **指纹去重**：普通源 seen_count≥3 排除，高质量源(Reddit/HN) ≥4 排除
5. **时间戳**：多数源脚本不采集发布时间 → Agent 必须通过其他信号推断时效

### JSON 输出格式

`hotspot_engine.py` 输出两种 JSON：

1. **日报 JSON** (`hotspot_daily_YYYY-MM-DD.json`)：字典结构 `{items: [...], mode: ..., stats: ...}`
2. **指纹 JSON** (`fingerprints_daily.json`)：指纹去重记录

每条 item 含：`title`, `source`, `url`, `snippet`, `platform`, `platform_rating`, `tags`, `is_repeat`, `repeat_count`, `fingerprint`

---

## 网络诊断快速排查

当多个工具同时失败时，先用诊断脚本区分：

```bash
# 快速诊断
curl -sI --max-time 5 "https://www.google.com" 2>&1 | head -3
curl -sI --max-time 5 "https://r.jina.ai/" 2>&1 | head -3
```

| 诊断结果 | 含义 | 行动 |
|----------|------|------|
| Google: 200, Jina: 200 | 网络正常 | 检查具体 URL 是否变化 |
| 全部失败 | 网络中断 | 等待恢复，先用已有数据 |
| Jina 返回 147 字节 "AuthenticationRequiredError" | IP 信誉阻止 | 等待自动恢复（<24h），使用 WebSearch 替代 |
| Jina 超时/空 | 临时故障 | 重试 1 次，降级到 WebSearch |

---

## 报告内容质量检查清单

报告生成后应检查：

- [ ] 9 个必须 section 全部存在（缺章节必须保留骨架+原因说明）
- [ ] P0 条目 5 个 + P1 条目 4-7 个（P1 不足 4 条必须说明原因）
- [ ] 每条热点标注发布日期
- [ ] 英文标题全部带中文翻译
- [ ] 中文摘要包含四要素（主体/动作/关键数字/行业影响）
- [ ] 概览包含 4 个固定字段（冲突/异常 + 数据锚点 + 受众关联 + 叙事钩子）
- [ ] 线索 ID 持久化，不重新分配
- [ ] 上期选题反馈不为空（首期除外）
- [ ] 理论中立性检查：无哲学家署名引用
- [ ] 时效检查：无超过 72h 的内容；超过 48h 已标注 `⚠️ 回溯`
- [ ] **已运行强制验证器且 exit code = 0**

强制验证命令（交付前必跑，非可选）：
```bash
python3 <skill_path>/scripts/verify_report_template.py --report <报告路径> --mode daily
```

---

## 各源时效判断指南（补充）

| 采集源 | 时效判断方法 | 置信度 | 注意事项 |
|--------|--------------|--------|---------|
| WebSearch 结果 | 搜索结果中的时间标注（如 "1 day ago"）转绝对日期 | 高 | 无时间标注的页面须 WebFetch 后从正文提取 |
| 百度热搜 | 无时间字段，默认为实时榜 | 中 | 只能证明"当前在榜"，不能证明首次发布时间，需补充搜索确认 |
| 微博热搜 | 无时间字段，默认为实时榜 | 中 | 同上；热度值不代表发布时间 |
| B站热门 | API 返回的 `pubdate` 字段（Unix 时间戳） | 高 | `datetime.fromtimestamp(pubdate)` 转换 |
| 36氪快讯 | API 返回的 `published_at` 字段 | 高 | ISO 格式，直接可用 |
| 搜狗微信 | 文章页日期文本（可能只有"X天前"） | 中 | 相对时间需转绝对；部分文章无日期 → 降为 P2 |
| AI HOT | `publishedAt` ISO 8601 UTC | 高 | 最可靠时效源，优先采用 |
| HackerNews | `time` Unix 时间戳 | 高 | 直接可用 |
| Reddit | `created_utc` Unix 时间戳 | 高 | 直接可用 |
| Jina Reader 博客 | 文章正文日期文本 | 中 | 博客全文可能含多篇旧文，只取最新一篇的日期 |

**无时间字段源的规则**：百度/微博等实时榜源的条目，发布时间只能标注"当日在榜"，不可虚构具体时间点；若需 P0/P1 评级，必须通过 WebSearch 补充确认首次发布时间。

---

## 章节缺失即不合格 — 9 章节与数据源映射表

日报 9 个必需章节各有明确的数据源责任。**章节缺失 = 对应数据源未采集或未入报**，必须在「⚙️ 执行路径报告」中说明：

| 章节 | 主数据源 | 补充源 | 缺失时处理 |
|------|---------|--------|-----------|
| 📋 本期热点清单 | 全部采集源 | - | 不可缺失（P1<4 需说明） |
| 🇨🇳 今日中国AI圈动态 | AI HOT API | WebSearch 中文 + 搜狗微信 | AI HOT 可用时必须用真实数据 |
| 👤 关键人物观点追踪 | 8 人博客 Jina 采集 | WebSearch 人物名 | 无新观点时写骨架+原因 |
| 🔍 深度分析 | P0 条目 + 信号分析模型 | - | 不可缺失 |
| 💡 选题建议 | P0/P1 条目 | 创作者画像 | 不可缺失 |
| 💔 受众痛点库 | 受众痛点相关信号 | creator_profile.md | 无新痛点时写骨架 |
| ⚙️ 执行路径报告 | 采集过程状态 | 验证器输出 | 不可缺失 |
| 📡 本周线索 | 日报线索累积 | _week_clues.json | 不可缺失 |
| 💡 素材深挖提示 | 深度分析候选 | - | 不可缺失 |

**历史教训**：2026-08 曾连续 5 天缺失 6 个章节且无任何告警，报告从 21KB 退化到 7.6KB。见 `anti_patterns.md` AP-4。
