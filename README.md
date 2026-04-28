# Hermes Workspace — SOUL 超级个体成长合伙人

## 工作区结构

```
hermes_workspace/
├── reports/          # 热点采集报告（每日/每周）
│   ├── daily/       # 日报 (- 每日8:00自动生成)
│   └── weekly/      # 周报 (- 每周一8:00自动生成)
├── plans/            # 系统设计方案与调研报告
├── skills/           # Skill 核心定义 (SKILL.md, 不含脚本)
│   ├── research/    # 研究类: hotspot-engine, competitive-analysis
│   └── productivity/# 效率类: gtd-workflow
├── scripts/          # 可执行脚本 (版本受控)
├── config/           # 配置文件与身份定义
│   └── SOUL.md      # SOUL 超级个体身份
└── data/             # 数据快照 (指纹库等)
```

## 自动归档的任务

| 任务 | 频率 | 路径 |
|------|------|------|
| AI×超级个体 热点采集日报 | 每日8:00 | `reports/daily/report_daily.md` |
| AI×超级个体 热点深度周报 | 每周一8:00 | `reports/weekly/report_weekly.md` |
| 指纹去重数据库 | 每次采集后 | `data/fingerprints_*.json` |
| 系统设计方案 | 按需 | `plans/*.md` |
## 验证推送 2026年 4月28日 星期二 23时17分01秒 CST
