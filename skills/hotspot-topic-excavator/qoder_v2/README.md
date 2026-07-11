# Hotspot Topic Excavator — 热点主题素材深挖采集器

Qoder 原生插件，从 GitHub 仓库 `John198912/hermes_workspace` 的 `hotspot-topic-excavator` skill 适配而来。

## 功能概述

以每日热点话题为锚点（非边界），采用「向内深挖 + 向外发散」双轴模型，产出：

- **Layer 1**: 内容素材包（6 类 + 图片素材 3 类，含红黄绿分层）
- **Layer 2**: 文章/视频大纲 + 素材填充（RIVET 结构）

包含 9 类校准审查（A-I）：事实校准 / 事实补充 / 表述校准 / 框架补充 / 对立视角 / 理论偏向 / 叙事引力 / 受众工具链翻译 / 三角叙事补洞。

## 适配说明

### 工具链映射（Hermes → Qoder）

| 原始工具 (Hermes) | Qoder 适配 |
|---|---|
| `mcp_brave_search_brave_llm_context` | `WebSearch` + `WebFetch` |
| `mcp_brave_search_brave_web_search` | `WebSearch` |
| `mcp_brave_search_brave_news_search` | `WebSearch`（带 timeRange） |
| Jina Reader (`r.jina.ai/{url}`) | `WebFetch` |
| `mcp__datapro__dataPro_search` | `WebSearch` |
| 豆包 byted-web-search | `WebSearch`（中文关键词） |
| Tavily | `WebSearch` |
| Python `requests` + BeautifulSoup | `Bash`（Python 脚本） |
| `youtube_transcript_api` | `Bash`（Python）或 `WebFetch` |
| `web_extract` | `WebFetch` |
| Scrapling StealthyFetcher | `Bash`（Python requests） |

### 模型配置适配

- 移除了 Hermes 专有的 `volces-ark/deepseek-v4-pro` 模型配置
- 保留全部核心功能模块，不删减

### 路径适配

- 报告产出路径：`reports/hotspot/{YYYY-MM-DD}/{topic_slug}/`
- 模板路径：plugin 内 `templates/report_template.md`

## 文件结构

```
hotspot-topic-excavator/
  .qoder-plugin/plugin.json
  README.md
  assets/avatar.svg
  skills/hotspot-topic-excavator/
    SKILL.md                                    # 主 skill 文件
    references/                                 # 23 个 reference 文件
      anthropic-source-handling.md              # Anthropic 信源处理
      apple_podcasts_transcript_proxy.md         # 播客 transcript 替代
      b2b_topic_china_perspective.md            # B2B 话题中国视角
      brave-mcp-degraded-recipe.md              # 搜索工具降级方案
      calibration_case_cac_ai_services_chapter.md  # CAC 政策话题案例
      calibration_case_cognitive_surrender.md  # 认知投降校准案例
      calibration_case_every_compound_engineering.md  # 复利工程校准案例
      calibration_case_openrouter.md            # OpenRouter 校准案例
      calibration_case_un_women_international_upgrade.md  # 国际议题升级案例
      calibration_checklist.md                  # 9 类校准清单
      case_type_topic_excavation.md             # 案例型话题方法论
      changelog.md                              # 变更日志
      cloudflare_waf_python_direct.md            # Cloudflare WAF 绕过
      cross_signal_synthesis.md                 # 三路信号交叉分析
      divergence_patterns.md                    # 8 种发散模式
      doubao_primary_fallback.md                # 中文搜索主源模式
      industry-event-minimal-signal-pattern.md  # 行业事件最小信号集
      international_topic_chinese_supplement.md  # 国际话题中文补强
      llm_context_only_excavation.md            # 搜索优先采集模式
      media_culture_topic_china_mirror.md       # 媒体文化中国镜像
      post_generation_review_pattern.md         # 审查补充优化模式
      rashomon_topic_pattern.md                 # 罗生门型话题分析
      single-topic-multi-round-parallel.md     # 单话题多轮并行采集
      providers/
        minimax-m3.md                           # MiniMax M3 配置参考
    templates/
      report_template.md                        # 报告输出模板
```

## 使用方法

### 触发方式

- "用素材深挖采集器分析XXX"
- "帮我对XXX话题做深度素材挖掘"
- "深挖 [话题名]"
- 引用本 skill 名称："hotspot-topic-excavator"

### 输入

| 字段 | 要求 | 说明 |
|------|------|------|
| 目标主题 | 必填 | 本次深挖的唯一锚点主题 |
| 每日热点信息 | 必填 | 文件路径或直接粘贴 |
| 来源线索 | 选填 | 原始出处 |
| 选题角度 | 选填 | 已确定的切入点 |
| 目标平台 | 选填 | 抖音/B站/公众号/小红书 |
| 内容形式 | 选填 | 短视频口播/深度长视频/图文长文/笔记 |

### 产出路径

报告产出保存到 `reports/hotspot/{YYYY-MM-DD}/{topic_slug}/` 目录下。

## Setup 说明

- 如需使用 Bash 降级路径（Python requests + BeautifulSoup），确保系统安装 Python 3.10+ 和 `requests`、`beautifulsoup4` 包
- 如需使用 YouTube Transcript API，安装 `youtube-transcript-api` Python 包
- 无需额外的 API key 或 MCP 配置
- 一键安装所有依赖：`pip3 install --user -r requirements.txt`

### 降级脚本使用示例

```bash
# 网页直连抓取（当 WebFetch 返回不完整内容时）
python3 skills/hotspot-topic-excavator/scripts/web_fetch.py "https://example.com/article"

# 指定输出格式和最大长度
python3 skills/hotspot-topic-excavator/scripts/web_fetch.py "https://example.com/article" --output markdown --max-length 30000

# YouTube 逐字稿获取
python3 skills/hotspot-topic-excavator/scripts/yt_transcript.py "dQw4w9WgXcQ"

# 从 YouTube URL 获取中文字幕
python3 skills/hotspot-topic-excavator/scripts/yt_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --language zh
```

## 保留的核心功能

1. 双轴采集模型（向内深挖 + 向外发散）
2. 6 类内容素材采集（热点资讯流/硬核事实/权威引述/案例故事/对立张力/可视化依据）
3. 3 类图片素材方案
4. 多层产出组装（Layer 1/2/3）
5. 校准审查 9 类（A-I）
6. 审查补充优化循环（模块 5C）
7. 平台采集适配（抖音/B站/公众号/小红书）
8. 连续性生产流水线
9. 全部 23 个 reference 文件的方法论和案例
10. 降级路径策略（多层级故障处理）

## 来源

- **源仓库**: https://github.com/John198912/hermes_workspace/tree/main/skills/hotspot-topic-excavator
- **版本**: v2.7.5（2026-07-08）
- **适配**: Qoder 原生 plugin 格式
