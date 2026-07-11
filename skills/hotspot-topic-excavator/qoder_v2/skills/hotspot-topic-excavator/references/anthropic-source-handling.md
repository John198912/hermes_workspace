# Anthropic Research 信源处理指南

> 2026-06-17 验证 · 关联技能: hotspot-topic-excavator
> **Qoder 工具适配版**：原 Brave → WebSearch；原 Jina → WebFetch；原 browser → WebFetch/Bash

---

## 一、研究页面结构

`https://www.anthropic.com/research` 的出版物列表通过 **JavaScript 增量加载**。

| 方法 | 结果 | 说明 |
|------|------|------|
| WebFetch (`anthropic.com/research`) | 部分 — 仅首页项（~12 条） | JS 渲染内容不可见 |
| `WebSearch` + `site:anthropic.com/research` | 有效 — 返回多种路径下的研究页面 URL | 覆盖主页面 + 独立论文页 |
| `WebFetch` 对已发现 URL | 有效 — 获取完整论文摘要和核心段落 | P1 原文内容，95% 信息完整度 |

## 二、推荐的完整获取流程

```
Step 1: WebSearch(query="site:anthropic.com/research 2026")
        → 获取散布在不同路径的研究页面 URL 列表

Step 2: WebFetch(url="https://www.anthropic.com/research")
        → 获取首页可见项（辅助补充，去重用）

Step 3: WebSearch(query="Anthropic [论文主题关键词] ...")
        → 对每篇目标论文获取核心段落

Step 4: 合并去重 → 编译论文表格
```

## 三、已知约束

- 首页列表 vs 经济指数报告分属不同路径（`/research/` vs `/research/economic-index-*` vs `/news/`）
- 部分报告发布于 `/features/` 路径（如 Project Deal）而非 `/research/`
- 经济指数系列按月份独立发布（1月/3月/5月），不在主 Research 列表中出现

## 四、实际案例（2026-06-17）

- 首页列表返回：13 篇（Jun 2025 - Jun 2026）
- `WebSearch` 补充发现：7 篇（经济指数3篇 + Labor Market + AI Fluency + India Brief + TAI Agenda）
- 最终合并：20 篇（2025-12 → 2026-06，6个月跨度）

---

## 五、单篇博客文章页抓取（v2.7.3 · 2026-07-08 验证）

**场景**：Anthropic 研究博客的单篇文章页（如 `anthropic.com/research/global-workspace`）使用 Next.js 渲染，但**全文内容嵌入在 HTML 源码中**——不需要 JS 执行即可提取。

### 现象与根因

| 方法 | 结果 | 说明 |
|------|------|------|
| WebFetch | 可能返回不完整内容 | Next.js SSR 页面结构导致解析异常 |
| Bash + curl | 有效 — 返回 ~215KB HTML，正文段落可见 | 内容在 `<p class="...post-text">` 标签中 |

**根因**：Anthropic 博客使用 Next.js 服务端渲染（SSR），HTML 源码中已包含所有文本内容。WebFetch 对这类 JS-heavy 但 SSR 友好的页面处理可能异常。

### 推荐获取流程

```
Step 1: Bash + curl -sL "https://www.anthropic.com/research/{slug}" \
         -H "User-Agent: Mozilla/5.0" --max-time 30
        → 获取 ~200KB HTML 源码

Step 2: 从 HTML 中提取正文段落
        → 搜索 <p class="...post-text"> 标签（Anthropic 博客特征 class）
        → 或用 Python re.findall 批量提取

Step 3: 验证完整性
        → 正文应包含论文核心发现 + 5 项属性 + Ablation 结果
        → ≥10 个 <p> 标签 → 确认抓取完整
```

### 决策树

```
目标：Anthropic 单篇研究博客
    ↓
优先：WebFetch 尝试获取
    ├─ 成功 → 直接使用
    └─ 内容不完整 → Bash + curl 直抓 HTML
        ├─ anthropic.com/research/* → curl 200 + HTML → 正则提取 <p> 正文
        └─ transformer-circuits.pub/* → curl AccessDenied → 降级到 WebSearch 获取第三方解读
```

### 与现有方法的协同

| 页面类型 | 推荐方法 | 降级 |
|---------|---------|------|
| `/research` 列表页 | WebSearch | 见本文第二节 |
| `/research/{slug}` 单篇博客 | WebFetch → Bash curl | WebSearch 中文解读 |
| `transformer-circuits.pub/*` 论文 | WebSearch | Bash curl |
| `/news/*` 新闻页 | WebSearch | WebFetch |
