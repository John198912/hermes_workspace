# SoloPM 实施进度

> 基于 SoloPM_产品设计方案_v1.1_OpenClaw适配版
> 适配为 Hermes Agent 原生实现

---

## Phase 0' · MVP 完成状态

| 任务 | 内容 | 状态 |
|------|------|------|
| E0-1 | 仓库脚手架 + pydantic 契约模型 | ✅ |
| E0-2 | feishu_client.py：token/限流/配额/退避 | ✅ |
| E0-3 | bootstrap.py + S1 | ✅ |
| E0-4 | task.py / inbox.py：任务卡 CRUD + 状态机 | ✅ 14/14 测试通过 |
| E0-5 | sync.py：双向增量同步（字段级合并） | ✅ |
| E0-6' | Hermes 环境 + 12 Skills | ✅ |
| E0-7 | S2/S3：capture 与 triage | ✅ |
| E0-8' | 12 skills 落盘 + TOOLS.md 约定 | ✅ |
| E0-9' | Cron 清单（见 SETUP.md） | ✅ |

## Phase 1' · V1 待部署

| 任务 | 内容 | 状态 |
|------|------|------|
| E1-1' | 周回顾持久会话 + pm-report 飞书文档 | ⬜ 待人工验证 |
| E1-2' | 健康评估 + 心跳告警三场景 | ⬜ 待人工验证 |
| E1-3' | L3 告警双通道 + budget 护栏 | ⬜ 待人工验证 |
| E1-4' | 安全硬化清单 | ⬜ |

---

## 技术栈

- Python 3.9+，仅标准库 + requests + yaml
- 12 个 Python 脚本（~3,300 行）
- 14 个 pytest 测试（全部通过）
- 12 个 Hermes SKILL.md 技能
- 飞书 Bitable API (tenant_access_token 鉴权)

## 差异说明（v1.1 设计 ← 实际实施）

- **OpenClaw → Hermes Agent**：原设计 OpenClaw Gateway 作为常驻运行时，实际 Hermes 已具备 cron/skills/飞书集成/terminal 等能力，全部原生实现
- **ACP dispatch**：Hermes 的 delegate_task 作为替代方案，功能对等
- **心跳 → Hermes cron**：heartbeat 巡检改为 cron + 技能组合
- **安全硬化**：Hermes 自带沙箱 + token 管理，部分项目可简化

---

更新：2026-06-13
