# 热点采集报告系统重构方案

> 问题诊断：当前 Python 脚本同时做"数据采集"和"报告生成"两件事，
> 后者应交给 AI（LLM + Skill）来完成真正有分析价值的报告。

---

## 一、问题的根因

**当前架构：**
```
Python脚本(hotspot_engine.py)
  ├── 数据采集 ✅（HTTP请求、正则解析、去重） 
  └── 报告生成 ❌（字符串拼接、简单罗列、无分析）
```

Python 脚本的 `generate_markdown_report()` 函数只会做一件事：
把采集到的每条数据按平台分类罗列出来，末尾加几句模板化的"选题建议"。

它**不会**（也不应该会）：
- 理解每条信息对你（卷哥/SOUL）的赛道意味着什么
- 判断这条信息能挖出什么思想深度
- 关联你的受众画像和选题策略
- 指出核心价值和切入角度

这些恰恰是 **LLM 擅长的事情**。

---

## 二、新方案：Python 只做采集，AI 做分析报告

```
Python脚本 → 采集原始数据 → 输出 JSON
                                    ↓
     hotspot-research skill (AI驱动)
        读取 JSON → 调用 SOUL 身份理解每条信息
        按 report_template.md 格式生成分析报告
        调用 brave-search MCP 补充受限源
                                    ↓
        报告写回 → git push
```

### 具体改动

#### 改动 1：Python 脚本只输出 JSON

`hotspot_engine.py` 去掉 `generate_markdown_report()`，改为输出结构化 JSON。

```json
// data/daily_2026-04-29.json
{
  "meta": {
    "mode": "daily",
    "collected_at": "2026-04-29T08:00:00+08:00",
    "total_items": 128,
    "sources_used": 10,
    "sources_failed": ["微博", "抖音", "知乎"]
  },
  "items": [
    {
      "title": "Microsoft and OpenAI end their exclusive deal",
      "source": "HackerNews",
      "url": "https://...",
      "platform": "海外讨论",
      "heat": 914,
      "tags": ["AI", "商业"],
      "is_repeat": false,
      "collected_at": "2026-04-29T08:00:00+08:00"
    },
    ...
  ],
  "failed_sources": [
    {"source": "微博热搜", "reason": "反爬", "suggestion": "Brave Search 补充"}
  ]
}
```

**文件路径**：`~/hermes_workspace/data/daily_2026-04-29.json`

#### 改动 2：cron prompt 用 skill + LLM 生成报告

cron prompt 改为调用 `hotspot-research` skill（绑定上 SOUL 身份），读取 JSON，然后让 LLM 按 `report_template.md` 的格式生成分析报告。

**报告格式（按 report_template.md）：**

```
# 🔥 AI×超级个体 热点采集分析报告 (每日)

## 一、本期热点速览（Top 5 核心洞察）
每条：标题 + 一句话核心价值 + 对你赛道的关联

## 二、热点清单总表（按价值排序）
| 话题 | 来源 | 核心价值 | 内容切入角度 | 优先级 |

## 三、重点人物观点
| 人物 | 观点摘要 | 可转化方向 |

## 四、深度选题建议（Top 3）
每条：切入角度 + SOUL 化叙事方向 + 关联受众 + 建议平台

## 五、受限源补充（Brave Search）

## 六、执行信息
```

#### 改动 3：cron 绑定 hotspot-research skill

将 `hotspot-research`（以及它依赖的 `references/` 配置、`report_template.md`）注册到 cron job 的 `skills` 列表中，确保运行时 LLM 能获取上下文。

---

## 三、执行步骤

| 步骤 | 内容 | 涉及文件 | 估算 |
|------|------|---------|------|
| **1** | 修改 `hotspot_engine.py`：去掉 `generate_markdown_report()`，改为输出 JSON | `hotspot_engine.py` | 0.5h |
| **2** | 更新 `cron job` prompt：改为读 JSON + 调用 skill 生成报告 | cron prompt | 0.5h |
| **3** | 注册 cron job 时绑定 `hotspot-research` skill | cron 配置 | 0.1h |
| **4** | 测试完整流程 | 终端运行 | 0.5h |

**总耗时**：约 1.5h，可以一次性做完。

---

## 四、为什么不全部用 Skill 替代 Python？

Python 脚本仍然保留的原因：

| Python 擅长的（保留） | LLM 擅长的（新方案接管） |
|---------------------|----------------------|
| HTTP 请求（控制超时/重试/UA 伪装） | 理解信息价值 |
| 正则/JSON 解析（百度热搜用 `"word"` key） | 判断选题角度 |
| 指纹去重（MD5 hash + TTL 过期） | 关联 SOUL 身份框架 |
| 并发采集隔离（每个源独立 try-except） | 生成叙事化的分析 |
| 定时调度（cron 触发） | 调用 MCP 工具 |

**Python 做"体力活"，LLM 做"脑力活"**——这才是各自该干的事。
