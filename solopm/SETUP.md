# SoloPM 部署与初始化指南

> 在 Hermes Agent 上部署 SoloPM —— 超级个体项目管理 Agent 系统

---

## 前置条件

- [x] Hermes Agent 运行中（当前环境）
- [ ] 飞书自建应用已创建（权限：`bitable:app`、`im:message:send_as_bot`、`im:message`、`docx:document`、`drive:drive`）
- [ ] 飞书多维表格 App 已创建（手动或通过 pm-init）
- [ ] 环境变量 `FEISHU_APP_ID` / `FEISHU_APP_SECRET` 已设置

---

## 一、飞书应用配置（人工一次性操作）

1. 访问 [飞书开放平台](https://open.feishu.cn/app) → 创建企业自建应用
2. 获取 **App ID** 和 **App Secret** → 填入环境变量
3. 在「权限管理」申请：
   - `bitable:app` — 多维表格读写
   - `im:message:send_as_bot` — 机器人发消息
   - `im:message` — 消息接收
   - `docx:document` — 文档创建
   - `drive:drive` — 云空间
4. 创建版本并发布
5. 将应用添加为多维表格 **协作者**（否则 API 返回 403）

---

## 二、初始化 Bitable 数据底座

```bash
# 在 Hermes 对话中执行（或命令行）
/python3 ~/hermes_workspace/solopm/scripts/bootstrap.py
```

或在 Hermes 对话中说：**「初始化 SoloPM」** 触发 `solopm-init` 技能。

完成后将输出的 app_token 和 table_id 回填到：
```
~/hermes_workspace/solopm/config/solopm.toml
```

---

## 三、Cron 调度设置

### 3.1 Hermes Cron 任务

在 Hermes 对话中依次执行以下命令：

```
# 每日摘要 (08:30，已包含隐式 sync pull)
/cronjob create --schedule "30 8 * * *" --name "SoloPM 每日摘要" "运行 solopm-daily-digest skill：先执行 sync.py --pull-only，再生成今日摘要。无到期且无阻塞时回复 NO_REPLY。"

# 双向同步 (13:00)
/cronjob create --schedule "0 13 * * *" --name "SoloPM 午间同步" "执行 terminal: python3 ~/hermes_workspace/solopm/scripts/sync.py"

# 双向同步 (22:00)  
/cronjob create --schedule "0 22 * * *" --name "SoloPM 晚间同步" "执行 terminal: python3 ~/hermes_workspace/solopm/scripts/sync.py"

# Inbox 分拣 (22:10)
/cronjob create --schedule "10 22 * * *" --name "SoloPM Inbox分拣" "运行 solopm-triage skill：分拣收件箱。无新条目则 NO_REPLY。"

# 项目健康 (周一 09:00)
/cronjob create --schedule "0 9 * * 1" --name "SoloPM 项目健康" "运行 solopm-project-health skill：评估所有项目健康度并报告"

# 周回顾 (周五 17:00)
/cronjob create --schedule "0 17 * * 5" --name "SoloPM 周回顾" "运行 solopm-weekly-review skill：执行周回顾，生成报告后运行 solopm-report 生成飞书文档"

# 归档 (每月1日 03:00)
/cronjob create --schedule "0 3 1 * *" --name "SoloPM 月归档" "执行 terminal: python3 ~/hermes_workspace/solopm/scripts/archive.py && python3 ~/hermes_workspace/solopm/scripts/budget.py rollover"
```

### 3.2 配额预算

当前免费版配额：10,000 次/月。设计目标 ≤ 4,500 次/月（留 55% 余量）。

```bash
# 查看当前配额
python3 ~/hermes_workspace/solopm/scripts/budget.py status
```

---

## 四、日常使用

### Hermes 对话命令

| 命令 | 功能 | 示例 |
|------|------|------|
| 初始化SoloPM | 创建 Bitable 表 | 触发 solopm-init |
| /pm-capture 或 "记一下：..." | 快速捕获 | 记一下：下午处理合同 |
| /pm-triage | 分拣收件箱 | 自动判断归属/优先级 |
| /pm-digest 或 "今天做什么" | 今日摘要 | ≤400字简报 |
| /pm-review | 周回顾 | 互动引导选下周任务 |
| /pm-health | 项目健康 | 风险雷达 |
| /pm-report weekly | 周报文档 | 生成飞书 docx |
| /pm-dispatch T-xxx | 派发编码 | agent 执行后回填 |
| /pm-archive | 归档 | Done>30天清理 |
| /pm-budget | 配额查询 | 查看 API 用量 |

### 飞书移动端

1. **改任务状态**：直接在 Bitable 视图修改（人优先）
2. **快速捕获**：在 Bitable Inbox 表新增行
3. **收通知**：每日摘要、到期提醒、告警

---

## 五、测试

```bash
cd ~/hermes_workspace/solopm
SOLOPM_DIR=/tmp/solopm_test python3 -m pytest tests/test_contracts.py -v
```

预期：14 passed

---

## 六、当前环境确认

| 项目 | 状态 |
|------|------|
| 项目目录 | `~/hermes_workspace/solopm/` ✅ |
| 12 个 Python 脚本 | `scripts/` 下完整 ✅ |
| 14 个测试全部通过 | ✅ |
| 12 个 Hermes Skills | `~/.hermes/skills/solopm-*/` ✅ |
| 飞书 App ID/Secret | 已设置 ✅ |
| Bitable App | ⚠️ 待运行 pm-init 创建 |
| Cron 任务 | ⚠️ 待上文命令创建 |
