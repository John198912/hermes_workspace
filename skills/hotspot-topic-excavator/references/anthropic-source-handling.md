# Anthropic Research 信源处理指南

> 2026-06-17 验证 · 关联技能: hotspot-topic-excavator

---

## 一、研究页面结构

`https://www.anthropic.com/research` 的出版物列表通过 **JavaScript 增量加载**。

| 方法 | 结果 | 说明 |
|------|------|------|
| Jina Reader (`r.jina.ai`) | ❌ 仅返回 ~12 条首页项（3.5KB） | JS 渲染内容不可见，\"See more\" 链接不可追踪 |
| 浏览器 + `browser_click(\"See more\")` | ❌ 不触发额外加载 | 按钮可能无 JS handler，或列表已全部加载 |
| `brave_web_search` + `site:anthropic.com/research` | ✅ 返回多种路径下的研究页面 URL | 覆盖主页面 + 独立论文页 + 经济指数页 + /news/ 路径 |
| `brave_llm_context` 对已发现 URL | ✅ 获取完整论文摘要和核心段落 | P1 原文内容，95% 信息完整度 |

## 二、推荐的完整获取流程

```
Step 1: brave_web_search(query="site:anthropic.com/research 2026", count=15)
        → 获取散布在不同路径的研究页面 URL 列表

Step 2: 浏览器 browser_navigate → browser_console
        → JS 提取: querySelectorAll('main a[href*="/research/"]')
        → 辅助补充首页可见项（去重用）

Step 3: brave_llm_context(query="Anthropic [论文主题关键词] ...", count=5)
        → 对每篇目标论文获取核心段落

Step 4: 合并去重 → 编译论文表格
```

## 三、已知约束

- 首页列表 vs 经济指数报告分属不同路径（`/research/` vs `/research/economic-index-*` vs `/news/`）
- `/research` 页面上的 \"See more\" 按钮在浏览器 session 中也不可靠（2026-06-17 验证：点击后列表无变化）
- 部分报告发布于 `/features/` 路径（如 Project Deal）而非 `/research/`
- 经济指数系列按月份独立发布（1月/3月/5月），不在主 Research 列表中出现

## 四、实际案例（2026-06-17）

- 首页列表返回：13 篇（Jun 2025 - Jun 2026）
- `brave_web_search` 补充发现：7 篇（经济指数3篇 + Labor Market + AI Fluency + India Brief + TAI Agenda）
- 最终合并：20 篇（2025-12 → 2026-06，6个月跨度）
- 方法学验证通过，可复用于后续 Anthropic 研究追踪

---

## 五、🆕 单篇博客文章页抓取（v2.7.3 · 2026-07-08 验证）

**场景**：Anthropic 研究博客的单篇文章页（如 `anthropic.com/research/global-workspace`）使用 Next.js 渲染，但**全文内容嵌入在 HTML 源码中**——不需要 JS 执行即可提取。

### 现象与根因

| 方法 | 结果 | 说明 |
|------|------|------|
| Jina Reader (`r.jina.ai`) | ❌ 返回空（0 字节） | Next.js SSR 页面结构导致 Jina 无法提取 |
| 直 curl | ✅ 返回 ~215KB HTML，正文段落可见 | 内容在 `<p class="...post-text">` 标签中 |
| `browser_navigate` | ✅ 可渲染（但慢） | 不必要——HTML 源码已含全文 |

**根因**：Anthropic 博客使用 Next.js 服务端渲染（SSR），HTML 源码中已包含所有文本内容（`<p>` 标签 + 图片 alt + 引用块）。Jina Reader 对这类 JS-heavy 但 SSR 友好的页面处理异常。

### 推荐获取流程

```
Step 1: curl -sL "https://www.anthropic.com/research/{slug}" \
         -H "User-Agent: Mozilla/5.0" --max-time 30
        → 获取 ~200KB HTML 源码

Step 2: 从 HTML 中提取正文段落
        → 搜索 <p class="...post-text"> 标签（Anthropic 博客特征 class）
        → 或用浏览器工具 browser_console 提取：
           document.querySelectorAll('p.post-text, .Body-module-scss-module__z40yvW__reading-column')
        → 或用 Python re.findall 批量提取

Step 3: 验证完整性
        → 正文应包含论文核心发现 + 5 项 GWT 属性 + Ablation 结果
        → ≥10 个 <p> 标签 → 确认抓取完整
```

### 实证

- **2026-07-08 J-Space 深挖**：Jina Reader 返回空 → `curl` 获取 215KB HTML → 提取到完整博客正文（论文核心发现、五项属性、Ablation 实验、安全监控案例、研究团队）
- **transformer-circuits.pub 论文页**：`curl` 返回 `AccessDenied` XML 错误（不同于 anthropic.com 的 SSR 模式）
- **关键区分**：`anthropic.com/research/*` 博客页 → curl 可用；`transformer-circuits.pub/*` 论文页 → curl 被拒

### 决策树更新

```
目标：Anthropic 单篇研究博客
    ↓
优先：curl 直抓 HTML（Jina 大概率空）
    ├─ anthropic.com/research/* → curl 200 + HTML → 正则提取 <p> 正文
    └─ transformer-circuits.pub/* → curl AccessDenied → 降级到 豆包/brave_web_search 获取第三方解读
```

### 与现有方法的协同

| 页面类型 | 推荐方法 | 降级 |
|---------|---------|------|
| `/research` 列表页 | brave_web_search + browser | 见本文第二节 |
| `/research/{slug}` 单篇博客 | **直 curl**（新增） | 豆包搜索中文解读 |
| `transformer-circuits.pub/*` 论文 | 豆包/brave_web_search | browser_navigate（如有必要） |
| `/news/*` 新闻页 | brave_web_search | 直 curl |
