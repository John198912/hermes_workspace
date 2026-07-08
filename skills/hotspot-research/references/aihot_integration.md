# aihot 集成实现方案 v1.0

> 基于 2026-05-14 实测验证数据编写。所有数字均可复现。

---

## 一、数据源规格

> [WARN] **2026-07-08 认证墙发现**：`aihot.virxact.com` 的所有 API 端点（包括 `/api/public/items` 和 `/api/articles`）现均已重定向到 `suite-passport` 登录页（返回 HTML, 非 JSON）。匿名 curl 请求均返回 `<html lang="zh-CN">` 含 `suite-passport-compile-at` meta 标签、无 JSON body。Python `urllib.request` 加 `Accept: application/json` 同样被重定向。**AI HOT 在恢复匿名访问前不可用于 cron 采集**。替代方案见本文档末尾 [NEW] Section 七之一「认证墙降级路径」。

### 1.1 API 端点（[WARN] 2026-07-08 起需登录认证）

| 端点 | 用途 | 参数 |
|------|------|------|
| `GET /api/public/items?mode=selected&since={ISO}&take=100` | 全量精选条目（日报/周报基准） | `since`: ISO-8601 UTC 时间 |
| `GET /api/public/items?mode=selected&category={cat}&take=100` | 按类别拉取（周报补充） | `category`: ai-models/ai-products/industry/paper/tip |
| `GET /api/public/items?...&cursor={cursor}` | 分页翻页（周报用） | `cursor`: 上一页返回的 opaque token |

Base URL: `https://aihot.virxact.com`

### 1.2 必要请求头

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
# 所有请求必须带 -H "User-Agent: $UA"，否则返回 403
```

### 1.3 实测数据量

| 场景 | 请求 | 返回条目 | hasNext | 数据时间跨度 |
|------|------|---------|---------|------------|
| 日报 (24h) | `mode=selected&since=24h前&take=100` | **30-70 条** | `False` | 约 24 小时 |
| 日报-高活动日 | 同上 | **50-70 条** | `False` | 重大AI事件日(Google I/O/OpenAI发布等)可翻倍 |
| 🆕 日报-低活动日（2026-06-24 验证） | 同上 | **16 条** | `False` | Fable 5 消化期 D+11 静默日 |
| 周报-基准 (7d) | `mode=selected&since=7d前&take=100` | **100 条** | `True` | 约 5-7 天 |
| 周报-models | `mode=selected&category=ai-models&take=100` | **22 条** | `False` | 约 7 天 |
| 周报-products | `mode=selected&category=ai-products&take=100` | **50 条** | `True` | 约 5 天 |
| 周报-industry | `mode=selected&category=industry&take=100` | **~30 条** | `False` | 约 7 天 |
| 周报-paper | `mode=selected&category=paper&take=100` | **~21 条** | `False` | 约 7 天 |
| 周报-tip | `mode=selected&category=tip&take=100` | **50 条** | `True` | 约 5 天 |

**🆕 AI HOT 24h 数据量方差（2026-06-24 新发现）：**
- 高活动日：50-70 条（Google I/O / OpenAI DevDay / Anthropic 重大发布日）
- 正常日：30-40 条
- **低活动日：16-20 条**（重大事件消化期 D+10+ + 周末/周日）—— **不需要降级**（仍 > 5 阈值），但要在「⚙️ 执行路径报告」标注「AI HOT 本期数据量偏低（X 条）— 行业消化期正常现象」
- 极端低日：< 5 条（已触发 Tavily 中文降级）—— 上方降级逻辑

**结论：**
- 日报 1 次请求全覆盖（35 条 < 100 条上限）
- 周报需要分页：products 和 tip 各需 2 页；其余类别 1 页够用
- 周报总数据量：150-200 条

### 1.4 返回数据结构

```json
{
  "items": [
    {
      "title": "在 Windows 上构建安全有效的沙箱以启用 Codex",
      "titleCn": null,                    // 可能为空
      "source": "OpenAI：官网动态（RSS · 排除企业/客户案例）",
      "url": "https://openai.com/index/...",
      "category": "tip",                   // ai-models|ai-products|industry|paper|tip
      "publishedAt": "2026-05-15T00:00:00.000Z",  // ISO-8601 UTC
      "summary": "..."                     // 中文摘要（部分条目无）
    },
    ...
  ],
  "hasNext": true,
  "nextCursor": "eyJ..."                   // opaque token，翻页用
}
```

### 1.5 来源类型与可信度评级

> **权威来源评级表见 `references/platforms.md` 第3节「AI HOT 内部来源评级」。**
> 本表为 AI HOT 专用视角，如有不一致以 platforms.md 为准。

| 来源特征 | 评级 | 说明 |
|---------|------|------|
| 官方 RSS / 官网动态（OpenAI、Anthropic 等） | **S** | 一手信息 |
| X/Twitter 中文 AI 大V（宝玉、硅基流动等） | **A** | 时效性高，但可能有主观性 |
| 学术机构博客（CMU ML Blog 等） | **A** | 研究前沿，权威 |
| 国内媒体转载 | **B** | 二手信息，需交叉验证 |
| 未知来源（source 为空或模糊） | **N/A** | 丢弃 |

---

## 二、采集工作流

### 2.1 在流程中的位置

```
Step 0:   加载策略 + 历史报告
Step 0.1: MCP Brave Search（海外深度）
Step 0.2: Tavily AI 搜索（全球态势）
Step 0.3: 🆕 aihot 全量拉取（中文 AI 圈全景）  ← 新增
Step 1:   关键人物博客（Jina Reader）
Step 2:   Python 批量扫描（国内平台）
Step 3:   三关审核（含 aihot 条目）
Step 4:   Jina 深度补采 P0
Step 5:   中文翻译
Step 7:   SOUL 框架报告
```

> **aihot 放在 Step 0.3 的理由：** aihot 条目可指导后续采集方向——如果 aihot 显示某国内 AI 产品今日爆发，Step 1-2 可针对性搜索更多信息。

### 2.2 日报采集路径

```bash
# === 单次请求，无需分页 ===
since=$(python3 -c "
from datetime import datetime, timedelta, timezone
print((datetime.now(timezone.utc) - timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ'))
")

curl -sH "User-Agent: $UA" \
  "https://aihot.virxact.com/api/public/items?mode=selected&since=$since&take=100" \
  --max-time 10 \
  -o /tmp/aihot_daily.json
```

**预期：** 30-40 条，1 次请求，耗时 ≤ 10 秒。

### 2.3 周报采集路径

```bash
# === 阶段 1：基准拉取（7 天全量精选） ===
since=$(python3 -c "
from datetime import datetime, timedelta, timezone
print((datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ'))
")

curl -sH "User-Agent: $UA" \
  "https://aihot.virxact.com/api/public/items?mode=selected&since=$since&take=100" \
  --max-time 10 \
  -o /tmp/aihot_weekly_base.json

# === 阶段 2：按类别补齐 ===
# 对 products 和 tip（hasNext=True 的类别），分页拉满
# 对 models、industry、paper（hasNext=False），单次够用

# products（需分页，约 100-120 条）
curl -sH "User-Agent: $UA" \
  "https://aihot.virxact.com/api/public/items?mode=selected&category=ai-products&take=100" \
  --max-time 10 -o /tmp/aihot_products_p1.json
# 检查 hasNext，如有则继续：
# curl ...&cursor={nextCursor} -o /tmp/aihot_products_p2.json

# tip（需分页，约 100-120 条）
curl -sH "User-Agent: $UA" \
  "https://aihot.virxact.com/api/public/items?mode=selected&category=tip&take=100" \
  --max-time 10 -o /tmp/aihot_tip_p1.json
# 同上分页逻辑

# models（无需分页，约 22 条）
curl -sH "User-Agent: $UA" \
  "https://aihot.virxact.com/api/public/items?mode=selected&category=ai-models&take=100" \
  --max-time 10 -o /tmp/aihot_models.json

# industry（无需分页，约 30 条）
curl -sH "User-Agent: $UA" \
  "https://aihot.virxact.com/api/public/items?mode=selected&category=industry&take=100" \
  --max-time 10 -o /tmp/aihot_industry.json

# paper（无需分页，约 21 条）
curl -sH "User-Agent: $UA" \
  "https://aihot.virxact.com/api/public/items?mode=selected&category=paper&take=100" \
  --max-time 10 -o /tmp/aihot_paper.json
```

**预期：** 150-200 条，5-7 次请求（products/tip 可能各需 2 页），并行耗时 ≤ 15 秒。

### 2.4 执行策略

```
周报中 aihot 拉取使用顺序模式（terminal foreground 不支持 & 后台符）：

terminal(aihot 基准拉取 + 翻页检查, --max-time 15)
    ↓ 基准完成后
terminal(aihot models, --max-time 10)
terminal(aihot products, --max-time 10)
terminal(aihot industry, --max-time 10)
terminal(aihot paper, --max-time 10)
terminal(aihot tip, --max-time 10)
    ↓ 类别完成后
检查 products 和 tip 的 hasNext
    ↓ 如需翻页（实测 2026-05-18: 所有类别 hasNext=False，无需翻页）
跳过翻页

或者使用单个 for 循环串联所有类别拉取（效率更高）：
```bash
for cat in ai-models ai-products industry paper tip; do
  curl -sH "User-Agent: $UA" \
    "https://aihot.virxact.com/api/public/items?mode=selected&category=$cat&take=100" \
    --max-time 10 -o /tmp/aihot_${cat}.json
done
```
```

**耗时预算：** 日报 ≤ 10s（单请求），周报 ≤ 60s（1 个基准 + 1 个 for 循环 5 类，顺序执行）。实测 2026-05-18: 所有 5 类 hasNext=False，for 循环约 35s。

---

## 三、质量保障规则

### 3.1 三关审核中的 aihot 特殊规则

#### 第一关：时效

```
aihot 条目自带 publishedAt（ISO-8601 UTC）
  → 无需推测时效
  → 日报：publishedAt >= 当前时间 - 24h → 通过
  → 周报：publishedAt >= 当前时间 - 7d  → 通过
  → 注意：since 参数已过滤，理论上所有条目均通过时效关
```

#### 第二关：来源

```
来源字段以 "X：" 或 "官网动态" 或 "：RSS" 或 媒体名 开头
  → 包含 "X：" 且粉丝数已知的大 V → A 级
  → 包含 "官网动态" 或 "RSS" → S 级
  → 包含已知媒体名（机器之心、量子位、36氪等）→ B 级
  → 来源为空或无法识别 → N/A → 丢弃
```

**已知可靠来源清单（持续更新）：**
| 来源标识 | 评级 | 
|---------|------|
| OpenAI：官网动态 | S |
| Anthropic：官网动态 | S |
| Google DeepMind：官网动态 | S |
| X：宝玉 (@dotey) | A |
| X：硅基流动 SiliconFlow | A |
| X：Vista (@vista8) | A |
| CMU：Machine Learning Blog | A |
| 机器之心 | B |
| 量子位 | B |

#### 第三关：匹配度

```
aihot 条目全部天然携带 [AI] 标签
  → 额外判断：是否与 [超级个体/一人公司/职场转型/内容创作] 相关？
  
  → 直接相关（P0）：
     标题/摘要含 solopreneur, creator, 一人, 超级个体, 自由职业, 
     内容创, 副业, 独立开发, 个人品牌, 写作, 自媒体
     
  → 间接相关（P1）：
     标题/摘要含 AI 工具, 效率, 自动化工作流, Agent, no-code, 
     产品发布（个人可用）, 教育, 学习路径
     
  → 背景信息（P2）：
     纯模型发布, 融资新闻, 学术论文, 企业合作, AI 基础设施
     
  → 不保留（丢弃）：
     纯技术实现（与本赛道无关的底层优化）、企业级 B2B、游戏/娱乐（非创作类）
```

### 3.2 去重规则

```
aihot 条目 vs 自身（同日多次运行）：
  → URL 相同 → 丢弃（保留首次出现的条目）
  → 标题相似度 > 0.85（Jaccard）且来源相同 → 丢弃

aihot 条目 vs 现有系统条目：
  → URL 域名相同 + 路径相似 → 标记为 [重复]，优先保留现有系统版本
  → 标题相似度 > 0.7 → Agent 判断是否为同一事件，若是则标记 [重复]
  → aihot 独有的中文来源条目 → 保留，标记 [aihot独家]
```

### 3.3 数据保存与归档

```
拉取的原始 JSON 保存路径：
  日报：~/hermes_workspace/reports/hotspot/aihot_daily_{YYYY-MM-DD}.json
  周报：~/hermes_workspace/reports/hotspot/aihot_weekly_{YYYY-MM-DD}.json

目的：
  1. 可复现：后续审查时可回溯原始数据
  2. 可审计：三关审核的丢弃决策有据可查
  3. 周报复用：周报可读取本周所有日报的 aihot JSON，避免重复拉取

⚠️ 注意：JSON 文件随报告一起 git push 归档
```

---

## 四、与现有系统的协同规则

### 4.1 交叉引用机制

```
对于每个通过三关审核的 aihot 条目：

1. 在现有系统（Brave/Tavily/Python/Jina）的候选项中搜索相关条目
   → 关键词匹配：提取 aihot 条目的核心实体（公司名/产品名/人名）
   → 在现有候选项中搜索同实体条目

2. 判定交叉状态：
   ┌─ 两源都有 → [交叉验证] P0，置信度最高，优先深度分析
   ├─ 仅 aihot 有 → [aihot独家] P1，标记为"中文AI圈独家视角"
   └─ 仅现有系统有 → 保持现有 P0/P1/P2 评级不变

3. 在报告中的呈现：
   [交叉验证] 条目 → 标注 "📡 aihot + 海外源双重确认"
   [aihot独家] 条目 → 标注 "🇨🇳 中文AI圈独家"
```

### 4.2 aihot 指导后续采集

```
aihot 拉取完成后，提取 Top 5 高频实体（公司/产品/人物）：

python3 << 'EOF'
from collections import Counter
import json, re

with open('/tmp/aihot_daily.json') as f:
    items = json.load(f)['items']

# 提取实体关键词
entities = Counter()
for item in items:
    title = (item.get('title','') + ' ' + (item.get('titleCn') or '')).lower()
    # 常见 AI 公司/产品/人物
    for kw in ['openai','anthropic','google','deepseek','kimi','moonshot',
               'meta','mistral','xai','grok','claude','gpt','gemini',
               'karpathy','altman','amodei','hinton']:
        if kw in title:
            entities[kw] += 1

print("aihot 高频实体 Top 5：")
for entity, count in entities.most_common(5):
    print(f"  {entity}: {count} 次")
EOF

→ 如果某实体在 aihot 高频出现但现有系统未覆盖
→ 在 Step 1（关键博客）和 Step 4（深度补采）中针对性搜索该实体
```

### 4.3 volume signal 注入周报主题识别

```
周报 Step 0 读取本周所有 aihot 日报 JSON 后：

1. 统计本周 aihot 条目中的高频关键词（3-gram / 实体词）
2. 与日报的「📡 本周线索」交叉比对
3. 规则：
   ┌─ 日报线索中出现 + aihot 高频（≥ 10次/周）→ 确认为本周 #1 主题
   ├─ 日报线索中出现 + aihot 中频（5-9次/周）→ 本周辅助主题
   ├─ 仅 aihot 高频 + 日报无提及 → [aihot 信号] 可能被现有系统漏掉的主题
   └─ 仅日报线索 + aihot 无提及 → 主题可能偏向海外视角，保留但降权

4. 确认的 #1 主题自动成为 Step 8 横纵深度专题的分析对象
```

### 4.4 不重复劳动规则

```
aihot 条目的 title + source + url 天然提供了"发生了什么"
→ 日报/周报中 aihot 条目不需要 Jina Reader 深度提取原文
→ aihot 条目的 summary 字段直接作为"事件描述"使用

例外：当 aihot 条目被标记为 [交叉验证] P0 且现有系统无该 URL 时
→ 用 Jina Reader 提取 aihot 条目的 url 做深度补采
→ 但这种情况较少（aihot 来源多为 X/Twitter 短帖，URL 本身信息量不大）
```

---

## 五、报告输出格式

### 5.1 日报中 aihot 的输出板块

```markdown
## 🇨🇳 今日中国AI圈动态（via aihot）

> 以下为 aihot.virxact.com 今日精选的中国 AI 行业动态。
> 标记说明：🔴 P0（直接选题）| 🟡 P1（间接相关）| ⚪ P2（行业背景）

### 🔴 直接选题（P0）
| 类别 | 标题 | 来源 | 匹配关键词 |
|------|------|------|-----------|
| tip | 微信群聊总结Skill | X：宝玉 | 内容创作、AI工具 |

### 🟡 行业动态（P1-P2）
[类别] 标题 —— 来源 (时间)
[类别] 标题 —— 来源 (时间)
...

> 📊 今日 aihot 统计：共 {N} 条 | P0: {n} 条 | P1: {n} 条 | P2: {n} 条
```

### 5.2 周报中 aihot 的输出板块

```markdown
## 🇨🇳 本周中国AI圈全景（via aihot）

> 本周共采集 {N} 条，覆盖 5 大类别。

### 📊 类别分布
| 类别 | 数量 | 占比 |
|------|------|------|
| 模型发布/更新 | {n} | {p}% |
| 产品发布/更新 | {n} | {p}% |
| 行业动态 | {n} | {p}% |
| 论文研究 | {n} | {p}% |
| 技巧与观点 | {n} | {p}% |

### 🔥 本周高频主题（via aihot volume signal）
1. **{主题词}** — 出现 {n} 次 — [与日报线索匹配/不匹配]
2. ...

### 🆚 与海外源的互补分析
| 主题 | aihot 视角 | 海外源视角 | 结论 |
|------|-----------|-----------|------|
| Anthropic 估值 9000 亿 | 融资新闻 | 研究博客深度 | 互补：aihot 提供新闻，海外源提供深度 |
| ... | ... | ... | ... |
```

### 5.3 aihot 条目在"本周线索"机制中的角色

日报的 `📡 本周线索` section 中：

```markdown
## 📡 本周线索

| 线索ID | 主题词 | 今日信号 | 来源 | 简要说明 |
|--------|--------|---------|------|---------|
| W-01 | Anthropic闪电周 | 🟡中 | 海外源(Step1) | Teaching Claude why 第三日 |
| W-02 | 中国AI产品出海 | 🟢新 | aihot独家 | aihot 出现 3 条产品出海相关 |

_aihot volume 参考：今日 aihot 共 35 条，P0 0 条，P1 5 条_
```

---

## 六、性能预算与超时保护

### 6.1 时间预算

| 场景 | aihot 耗时 | 占 cron 总超时 (600s) | 
|------|-----------|---------------------|
| 日报（1 请求） | ≤ 10s | 1.7% |
| 周报（5-7 请求，两轮并行） | ≤ 20s | 3.3% |

aihot 对 cron 超时的影响：**可忽略。**

### 6.2 超时保护

```
单个 aihot 请求：
  --max-time 10（curl 参数）
  → 超时则跳过该请求，不重试
  → 标记为 [aihot:TIMEOUT]

整批 aihot 请求：
  → 日报：单请求超时 → 日报中标注 "今日 aihot 数据不可用"
  → 周报：部分类别请求超时 → 使用已成功拉取的类别数据
  → 全败 → 周报中标注 "本周 aihot 数据不可用"，但不影响主流程
```

### 6.3 API 限流保护

```
速率限制：600 req/min/IP
→ 我们的最大请求量：周报 7 次/分钟 → 远低于限制
→ 无需特殊限流处理
→ 如果某次请求返回 429 → 等 5 秒后重试 1 次，仍失败则跳过
```

---

## 七、降级路径

```
aihot API 调用
    ↓
┌─ 200 OK + 有效 JSON → 正常处理
├─ 403 Forbidden → UA 失效？→ 尝试不带 UA，仍失败 → 跳过 [aihot:BLOCKED]
├─ 429 Rate Limit → 等 5 秒，重试 1 次 → 仍 429 → 跳过 [aihot:RATELIMIT]
├─ 503/超时 → 跳过 [aihot:UNAVAILABLE]
├─ 200 但 JSON 解析失败 → 跳过 [aihot:PARSE_ERROR]
└─ items 数组为空 → 正常（该时间窗口内无数据）

所有降级情况下：
  ✅ 主流程完全不受影响
  ✅ 报告中标注 "aihot 数据不可用（原因：XXX）"
  ✅ 不会阻塞后续 Step 1-7
```

### [NEW] 7.1 认证墙降级路径（2026-07-08 新增）

**症状**：所有 aihot API 端点返回 HTML 登录页（`suite-passport-compile-at` meta 标签），而非 JSON。即使添加 `Accept: application/json` 头也无效。

**诊断**：
```bash
# 确认是否为认证墙
curl -sI --max-time 5 "https://aihot.virxact.com/api/articles?type=24h&limit=50" | head -5
# 返回 Content-Type: text/html（非 application/json）→ 认证墙
```

**降级流程**：
```
aihot API 调用
    ↓
┌─ 200 + text/html（suite-passport 登录页）→ [aihot:AUTH_WALL]
│   → 这不是临时故障，是系统变更——立即跳过，不重试
├─ 200 + 有效 JSON → 正常处理（未来恢复时的路径）
└─ 其他错误 → 走原有降级路径（§七）
```

**替代方案（已验证 2026-07-08 日报）**：
| 中国AI圈信息 | 替代源 | 覆盖质量 | 命令 |
|-------------|--------|---------|------|
| 国内AI公司动态（DeepSeek/Kimi等） | Brave News 中文关键词搜索 | 高（海外媒体报道充分） | `brave_news_search(query="DeepSeek 深度求索 AI model 2026")` |
| 国内AI产品/工具 | 搜狗微信（engine已集成） | 中（成功时质量B级，成功率~20%） | Python engine `collect_wechat()` |
| 国内创作者观点/痛点 | 小红书/微博/即刻 | 低（无cron可用API） | **需卷哥手动补采**（交互session用browser） |
| 模型发布/学术 | HN / arXiv | 高（无国界） | Python engine |

**报告标注**：
```
> [WARN] AI HOT API 已切换为需登录认证（suite-passport），今日数据来自替代源。
> [WARN] 中国AI圈内容存在覆盖盲区（小红书/微博/即刻无cron可用API）。
> 建议卷哥在交互session中手动补采。
```

**恢复条件**：如果未来 aihot 恢复匿名 API 访问（返回 JSON 而非 HTML），自动回退到原有采集路径。

---

## 八、实施检查清单

### 8.1 代码改动

- [ ] `hotspot-research/SKILL.md` — 新增 Step 0.3（aihot 采集 + 降级逻辑）
- [ ] `hotspot-research/SKILL.md` — Step 3 三关审核新增 aihot 特殊规则
- [ ] `hotspot-research/SKILL.md` — Step 7 报告模板新增 aihot 输出板块
- [ ] `templates/report_template.md` — 日报新增「🇨🇳 今日中国AI圈动态」section
- [ ] `templates/report_template.md` — 周报新增「🇨🇳 本周中国AI圈全景」section
- [ ] `references/data_quality_notes.md` — 新增 aihot 来源评级表
- [ ] `references/platforms.md` — 新增 aihot.virxact.com 为 S 级资讯聚合源
- [ ] `references/curl_examples.md` — 新增 aihot 的 curl 命令模板

### 8.2 验证步骤

- [ ] 手动跑一次日报 → 检查 aihot 数据是否正常进入报告
- [ ] 手动跑一次周报 → 检查分页逻辑 + 类别覆盖
- [ ] 模拟 aihot API 故障（curl 一个不存在域名）→ 确认降级不阻塞主流程
- [ ] 检查 git push 是否包含 aihot JSON 归档文件
- [ ] 连续观察 3 天日报 → 确认"本周线索"中 aihot 信号与现有系统信号的交互质量

### 8.3 持续优化项

- [ ] 运行 2 周后，根据实际匹配率调整 aihot 条目的 P0/P1/P2 阈值
- [ ] 运行 1 个月后，评估 aihot 来源评级是否需要更新
- [ ] 如果某类别的匹配率持续为 0，考虑从日报中移除该类别（仅周报保留）

---

## 九、关键约束速查

| 约束 | 值 | 影响 |
|------|-----|------|
| 单次 take 上限 | 100 | 日报一页够；周报需分页 |
| items since 上限 | 7 天 | 早于 7 天自动截断；需更早 → 走日报存档 |
| 中文关键词搜索 | **不可用** | 不要用 `?q=超级个体` → 全量拉取 + 本地筛选 |
| UA 要求 | Chrome 124 UA | 不带 UA → 403 |
| 限流 | 600 req/min | 远超需求，不用管 |
| 单次响应时间 | 6-8 秒 | 并行可降到 10-15 秒总耗时 |
| titleCn 字段 | 可能为 null | 始终以 title 为主，titleCn 为辅助 |
