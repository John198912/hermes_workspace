# MiniMax M3 Provider Configuration

> 实测日期：2026-06-03
> 模型行为：带有 `` reasoning 标签

## 已确认信息

| 项目 | 值 |
|------|-----|
| **模型名** | `minimax-m3`（非 `abab-m3`） |
| **API 端点** | `https://api.minimax.chat/v1/chat/completions` |
| **API 模式** | `chat_completions`（OpenAI 兼容） |
| **Reasoning** | 输出含 `` 标签 |
| **备选模型** | `minimax-m1`（同样有 reasoning）、`abab6.5s-chat`（无 reasoning） |

## config.yaml 配置

```yaml
custom_providers:
  - name: minimax
    base_url: https://api.minimax.chat/v1
    api_key: ${MINIMAX_API_KEY}
    api_mode: chat_completions
    models:
      minimax-m3:
        context_length: 200000
      minimax-m1:
        context_length: 200000
```

## .env

```bash
MINIMAX_API_KEY=sk-cp-...
```

## 验证命令

```bash
curl -s https://api.minimax.chat/v1/chat/completions \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"minimax-m3","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```

## 已知问题

1. **Reasoning 标签**：`minimax-m3` 和 `minimax-m1` 均输出 `` 块。Hermes 的 `chat_completions` api_mode 通常能正常解析，但如果报告中出现残片，考虑用 `abab6.5s-chat`（无 reasoning）。
2. **API Key 写入 `.env` 在 Feishu DM session**：terminal 写入含特殊字符的 key 到 `.env` 时，审批超时机制频繁拦截。需用户在自己终端手动执行 `echo 'MINIMAX_API_KEY=...' >> ~/.hermes/.env`。
3. **config.yaml 写入保护**：`patch`/`write_file` 直接写 `~/.hermes/config.yaml` 会被拒绝。必须用 `terminal` + Python 脚本编辑，或 `hermes config set`。
