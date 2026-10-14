# 故障诊断与降级手册 (Troubleshooting)

> **用途**：采集源失败时的四层诊断法 + 修复 vs 降级决策树。
> **加载时机**：任何采集源连续失败 2 次时加载。

---

## 四层诊断法（DNS → TCP → TLS → HTTP）

采集源失败时按以下顺序逐层排查，**不要跳过层级直接换源**：

### 层 1：DNS 解析
```bash
nslookup <domain>   # 或 dig <domain>
```
- 解析失败 → 域名错误或 DNS 污染 → 换源（降级）
- 解析成功 → 进入层 2

### 层 2：TCP 连接
```bash
curl -sv --max-time 8 "https://<domain>" -o /dev/null 2>&1 | grep -E "Connected|connect"
```
- `Connection refused` / `timeout` → 服务器宕机或防火墙拦截 → 换源（降级）
- 连接成功 → 进入层 3

### 层 3：TLS 握手
```bash
curl -sv --max-time 8 "https://<domain>" -o /dev/null 2>&1 | grep -iE "ssl|tls|certificate"
```
- `SSL handshake failed` / `certificate` 错误 → 本地 TLS 栈问题（macOS LibreSSL 常见）
  - **修复**：改用 Python requests（不同 TLS 协商路径），见 `scripts/jina_blogs_template.py` 的 bypass 方案
  - **禁止**：无诊断直接全局关闭证书验证
- 握手成功 → 进入层 4

### 层 4：HTTP 响应
```bash
curl -sI --max-time 8 "https://<domain>/<path>" | head -5
```
- `403` → 检查 User-Agent 要求（如 AI HOT 需 aihot-skill UA）或反爬
- `429` → 限流，等待后重试或降频
- `200 但返回 HTML 而非 JSON` → 认证墙或端点变更 → 换端点或换源
- `200 且格式正确` → 解析层问题，检查响应结构

---

## 修复 vs 降级决策树

```
源失败
├── 层 1/2 失败（DNS/TCP）
│   └── 立即降级到替代源，报告标注 [源名:DOWN]
├── 层 3 失败（TLS）
│   ├── macOS LibreSSL 已知问题 → Python requests bypass（修复）
│   └── 其他 → 降级
├── 层 4 失败（HTTP）
│   ├── 403 + UA 要求明确 → 加正确 UA 重试（修复）
│   ├── 429 → 等待 60s 重试一次，仍失败 → 降级
│   └── 认证墙/结构变更 → 降级 + 记录到执行路径报告
└── 解析失败（JSON 结构变化）
    └── 检查 API 响应字段 → 适配或降级
```

---

## 各源降级路径速查

| 主源 | 降级方案 | 降级标注 |
|------|---------|---------|
| AI HOT `/api/public/items` | WebSearch 中文关键词 + 搜狗微信 | `[aihot:UNAVAILABLE]` |
| Jina Reader (curl) | Python requests bypass → WebFetch | `[jina:BYPASS]` |
| HackerNews Firebase API | algolia API `hn.algolia.com/api/v1/search?tags=front_page` | `[hn:FALLBACK]` |
| Reddit JSON API | old.reddit.com / WebSearch site:reddit.com | `[reddit:FALLBACK]` |
| B站 API | WebSearch "bilibili 热门" | `[bili:FALLBACK]` |
| 微博热搜 | WebSearch "微博热搜 今日" | `[weibo:FALLBACK]` |
| 小红书/抖音（JS渲染） | Browser MCP 或标注受限 | `[受限源]` |

---

## 强制记录义务

任何降级发生后，**必须**在报告的「⚙️ 执行路径报告」章节记录：
- 失败的源名称与失败层级（DNS/TCP/TLS/HTTP/解析）
- 采取的降级路径
- 对报告内容完整度的影响评估

禁止"静默降级"——降级不记录等于数据丢失不可见。

---

*本文件由原版 root_cause_diagnosis.md（四层诊断法）适配 Qoder 工具链提炼。*
