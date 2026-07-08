# 平台信息源 (Platforms) — 更新版 v2.0

## 1. 国内平台

### 1.1 小红书（S级核心平台）
| 监测对象 | 评级 | 赛道相关性 | 获取方式 |
|---------|------|----------|---------|
| 小红书热搜榜 | S | 直接命中 | 直接访问 |
| #超级个体 话题 | S | 直接命中 | 直接访问 |
| #AI副业 话题 | A | 直接命中 | 直接访问 |
| #35岁转型 话题 | A | 直接命中 | 直接访问 |
| #一人公司 话题 | A | 直接命中 | 直接访问 |

### 1.2 B站（深度内容平台）
| 监测对象 | 评级 | 赛道相关性 | 获取方式 |
|---------|------|----------|---------|
| B站热门·科技区 | A | 高相关 | 直接访问 |
| 硅谷101 | A | 直接命中 | B站可访问 |
| 老石谈芯 | A | 高相关 | B站可访问 |
| 李自然说 | A | 极度命中（竞品） | 直接访问 |
| 回形针PaperClip | B | 高相关 | B站可访问 |

### 1.3 抖音（第一发布平台）
| 监测对象 | 评级 | 用途 | 获取方式 |
|---------|------|------|---------|
| 抖音热榜·科技/职场 | S | 受众当下焦虑 | 今日热榜聚合可访问 |
| 巨量算数·趋势词 | A | 关键词热度监测 | 需注册 |
| 竞品账号监测 | A | 选题策略参考 | 直接访问 |

### 1.4 微博热搜
- 采集重点：科技/职场/AI相关热搜话题
- 评论区情绪词采集

### 1.5 知乎热榜
- 采集重点：AI/职场/超级个体相关问答
- 高赞回答中的痛点挖掘

### 1.6 投资界/惊蛰研究所（pedaily.cn）
- 评级：A
- 赛道相关性：直接命中（"一人公司"系统性深度报道）
- 特点：提供国内最完整的AI超级个体赛道实操图谱，包含真实案例+可复制路径
- 获取方式：Jina Reader（r.jina.ai），已验证高质量Markdown提取
- 注意：文章日期通常为发布后3-7天，时效性中等，适合做深度分析而非快讯

## 2. 海外平台

### 2.1 YouTube重点频道
| 频道 | 方向 | 评级 |
|------|------|------|
| Andrej Karpathy | AI技术科普 | S |
| Two Minute Papers | AI研究速览 | A |
| Yannic Kilcher | AI论文解读 | A |
| AI Explained | AI深度解读 | A |
| TheAIGRID | AI工具与趋势 | A |
| Ali Abdaal | 个人品牌/生产力 | A |
| Matt Gray | Solopreneur | A |
| Dan Koe | 一人企业 | A |
| Dickie Bush | 内容创业 | B |
| Matt Wolfe | AI工具 | A |
| Fireship | 技术速览 | A |
| Lex Fridman Podcast | 深度访谈 | S |
| Dwarkesh Patel | 深度访谈 | A |

### 2.2 Reddit重点版块
| 社区 | 评级 | 内容价值 |
|------|------|---------|
| r/Entrepreneur | A | 一人企业/solopreneur真实案例 |
| r/SideProject | A | AI工具+副业项目 |
| r/singularity | A | AGI/AI进展热点讨论 |
| r/ChatGPT | B | AI工具使用热点 |
| r/artificial | A | AI综合讨论 |
| r/MachineLearning | A | AI研究前沿 |
| r/solopreneur | A | 一人企业实践 |
| r/LocalLLaMA | B | 本地AI部署 |

### 2.3 Substack Newsletter（新增）
| Newsletter | 评级 | 赛道相关性 | 获取 |
|-----------|------|----------|------|
| Every (Dan Shipper) | S | 直接命中（AI+个人生产力+创作者经济） | every.to |
| Lenny's Newsletter | A | 直接命中（产品+增长+创业） | Substack |
| The Pragmatic Engineer | A | 高相关（工程师转型+AI） | Substack |
| The Diff (Byrne Hobart) | A | 高相关（科技+金融+个体杠杆） | Substack |

### 2.4 X/Twitter 关键账号（含替代获取方案）
| 账号 | 评级 | 内容方向 | 替代获取 |
|------|------|---------|---------|
| @sama (Sam Altman) | S | OpenAI动态+AGI预测 | blog.samaltman.com |
| @karpathy | S | LLM教育+AI本质论 | karpathy.ai |
| @naval | S | 财富/个体/杠杆哲学 | nav.al |
| @ylecun (LeCun) | A | AI安全争论 | 搜索摘要 |
| @benedictevans | A | 科技产业趋势 | ben-evans.com |
| @paulg | A | 创业+写作 | paulgraham.com |
| @emollick | A | AI+教育+工作 | oneusefulthing.org |

## 3. 优质资讯聚合源
| 评级 | 来源 | 特点 |
|------|------|------|
| S→[WARN] | aihot.virxact.com | [NEW] 中文AI行业全景雷达。[WARN] 2026-07-08 起需登录认证（suite-passport），匿名API返回HTML登录页。恢复匿名访问前不可用于cron采集。替代：Brave News中文搜索+搜狗微信+手动补采小红书/微博。详见 `references/aihot_integration.md` §7.1 |

**🆕 AI HOT 内部来源评级：**（权威来源，其他文件引用此表）
| 来源类型 | 评级 | 示例 | 处理 |
|---------|------|------|------|
| 官方 RSS/官网动态 | S | OpenAI, Anthropic | 等同现有 S 级源，优先使用 |
| X/Twitter 中文 AI 大V | A | 宝玉, 硅基流动, Vista | 一手信息，时效性强 |
| 学术机构博客 | A | CMU ML Blog | 等同于现有学术源 |
| 媒体转载 | B | 各科技媒体 | 二手信息，需交叉验证 |
| 未知来源 | N/A | source 为空或模糊 | 丢弃 |
| S | importai.substack.com | Jack Clark主笔，AI政策与研究权威周报 |
| S | deeplearning.ai/the-batch | 吴恩达团队，综合权威 |
| S | jack-clark.net | AI政策与安全深度 |
| A | interconnects.ai | AI研究深度解读（Nathan Lambert）|
| A | oneusefulthing.org | AI+工作/教育（Ethan Mollick）|
| A | simonwillison.net | AI工具实践，高引用率 |
| A | theaiedge.io | AI工程实践 |
| A | thegradient.pub | AI学术与产业桥梁 |
| B | techcrunch.com/ai | 产业动态 |
| B | technologyreview.com | MIT，深度报道 |
| B | huggingface.co/blog | 开源技术前沿 |

## 4. 行业报告源（新增）
| 来源 | 评级 | 内容特点 | 获取 |
|------|------|---------|------|
| Sam Altman博客 blog.samaltman.com | S | 一手AI预测 | 直接访问 |
| a16z Future future.a16z.com | A | 创投视角AI+创业趋势 | 直接访问 |
| State of AI Report stateof.ai | S | 年度AI全景报告 | 直接访问 |
| 中国信通院AI报告 | A | 中国AI政策+产业数据 | 官网免费获取 |
