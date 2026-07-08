# Python venv urllib3 兼容性故障：诊断与修复

> 创建日期：2026-07-08 | 首次验证：hotspot-topic-excavator 话题深挖 session
> 影响范围：所有 `import requests` 的 Python 脚本（tavily_search.py、web_search.py、hotspot_engine.py、jina_blogs_template.py 等）

---

## 症状

任何 Python 脚本在导入 `requests` 时崩溃：

```
Traceback (most recent call last):
  File ".../tavily_search.py", line 11, in <module>
    import requests
  File ".../venv/lib/python3.11/site-packages/requests/__init__.py", line 43, in <module>
    import urllib3
  File ".../venv/lib/python3.11/site-packages/urllib3/__init__.py", line 15, in <module>
    from ._base_connection import _TYPE_BODY
  File ".../venv/lib/python3.11/site-packages/urllib3/_base_connection.py", line 10, in <module>
    bytes, typing.IO[typing.Any], typing.Iterable[bytes | str], str
TypeError: unsupported operand type(s) for |: 'type' and 'type'
```

## 根因

hermes-agent venv（`~/.hermes/hermes-agent/venv/`）的 Python 3.11 + 已安装的 urllib3 版本过于老旧，其 `_base_connection.py` 使用了 `X | Y` union 语法（Python 3.10+），但类型检查时 `typing.Iterable[bytes | str]` 在旧版 Python 3.11 早期补丁级别上因 `typing` 模块的内部变化而失效。

## 已知影响

| 脚本 | 所属 skill | 故障模式 |
|------|----------|---------|
| `tavily_search.py` | tavily-search | `import requests` → TypeError |
| `web_search.py` | byted-web-search | `import requests` → TypeError |
| `hotspot_engine.py` | hotspot-research | `import requests` → TypeError |
| `jina_blogs_template.py` | hotspot-research | `import requests` → TypeError |
| 所有其他 Python 脚本 | — | 任何 `import requests` 都会触发 |

## 修复方案（按优先级）

### 方案一：升级 urllib3（推荐）

```bash
~/.hermes/hermes-agent/venv/bin/pip install --upgrade urllib3 requests
```

> ⚠️ **风险**：hermes-agent 更新后可能被覆盖。需在每次更新后重新执行。

### 方案二：使用系统 Python（降级路径 A）

```bash
/usr/bin/python3 -c "import requests; print('OK')"
```

如果系统 Python 的 requests 可用，将脚本的执行路径改为系统 Python。注意：系统 Python 可能缺少其他依赖。

### 方案三：创建独立 venv（降级路径 B）

```bash
python3 -m venv ~/.hermes/search-venv
~/.hermes/search-venv/bin/pip install requests
```

修改脚本 shebang 指向新 venv。

### 方案四：运行时规避（临时降级，本次交互可用）

| 目标 | 降级工具 | 原因 |
|------|---------|------|
| 英文搜索 | **Brave MCP**（brave_web_search / brave_news_search） | npm 进程，不经过 Python venv |
| 中文搜索 | **terminal curl** 直接调用豆包 API | 绕过 Python import 链 |
| 网页全文 | **browser navigate + snapshot** | 浏览器栈独立于 Python |
| 网页提取 | **terminal curl** + sed/awk 过滤 | 纯 shell，零 Python |

## 反模式

- ❌ 反复重试同一个 Python 脚本——urllib3 的 TypeError 不是瞬态错误，重试无效
- ❌ 尝试 `pip install` 到 venv——hermes 环境中 `pip` 也可能因为同样原因失败
- ❌ 降级后不检查结果——降级路径各有精度损失，需评估信息完整度

## 验证修复

```bash
~/.hermes/hermes-agent/venv/bin/python3 -c "import requests; print('OK')"
```

期望输出：`OK`

## 监控

建议 cron 作业中增加 pre-flight check：

```bash
python3 -c "import requests" 2>&1 || echo "VENV_URLLIB3_BROKEN"
```

若检测到故障，cron job 自动切换至 Brave MCP + curl 降级路径。
