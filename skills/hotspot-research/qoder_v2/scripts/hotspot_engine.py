#!/usr/bin/env python3
"""
hotspot_engine.py — 热点采集核心引擎
======================================
职责：
  1. 指纹去重（基于标题+来源+时间的哈希，带过期机制）
  2. 多平台信息源采集（web_scrape / RSS / 聚合器）
  3. 指纹存储与读取（JSON文件，按日/周分桶）
  4. 重复标记与排除逻辑

用法（被 Qoder Bash 工具调用）：
  python3 hotspot_engine.py daily   # 每日采集
  python3 hotspot_engine.py weekly  # 每周采集

指纹去重策略（采集前 vs 采集后）：
  【混合策略 — 推荐】
  阶段1（采集前）：读取上一次报告指纹 → 对每个源先做轻量预检，跳过已知内容
  阶段2（采集后）：对全部采集结果做完整对比 → 标记重复 → 已标记过2次则排除
  每日只对比每日指纹库，每周只对比每周指纹库。

报告输出目录：~/Documents/qoder_workspace/hotspot/reports/hotspot/
"""

import json
import hashlib
import os
import time
import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlparse

# ============================================================
# 配置
# ============================================================
DATA_DIR = os.path.expanduser("~/Documents/qoder_workspace/hotspot/reports/hotspot")
DAILY_FINGERPRINT_FILE = os.path.join(DATA_DIR, "fingerprints_daily.json")
WEEKLY_FINGERPRINT_FILE = os.path.join(DATA_DIR, "fingerprints_weekly.json")
DAILY_REPORT_FILE = os.path.join(DATA_DIR, "report_daily.md")
WEEKLY_REPORT_FILE = os.path.join(DATA_DIR, "report_weekly.md")

# 指纹过期：每日指纹保留7天，每周指纹保留30天
FINGERPRINT_DAILY_TTL_DAYS = 7
FINGERPRINT_WEEKLY_TTL_DAYS = 30

os.makedirs(DATA_DIR, exist_ok=True)


# ============================================================
# 指纹引擎
# ============================================================
class FingerprintStore:
    """
    指纹存储与管理。
    每条记录: {fingerprint: str, title: str, source: str, seen_count: int, first_seen: str, last_seen: str}
    """
    
    def __init__(self, mode: str):
        assert mode in ("daily", "weekly")
        self.mode = mode
        self.fingerprint_file = DAILY_FINGERPRINT_FILE if mode == "daily" else WEEKLY_FINGERPRINT_FILE
        self.ttl_days = FINGERPRINT_DAILY_TTL_DAYS if mode == "daily" else FINGERPRINT_WEEKLY_TTL_DAYS
        self.fingerprints: dict = self._load()
    
    def _load(self) -> dict:
        if os.path.exists(self.fingerprint_file):
            try:
                with open(self.fingerprint_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save(self):
        with open(self.fingerprint_file, "w") as f:
            json.dump(self.fingerprints, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def make_fingerprint(title: str, source: str, url: str = "") -> str:
        """生成唯一指纹：标题归一化 + 来源域名 + URL路径摘要"""
        norm_title = re.sub(r'\s+', ' ', title.strip().lower())[:80]
        domain = ""
        if url:
            try:
                domain = urlparse(url).netloc.replace("www.", "")
            except:
                pass
        raw = f"{norm_title}|{source}|{domain}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()
    
    def is_known(self, fingerprint: str) -> bool:
        """检查指纹是否已存在"""
        return fingerprint in self.fingerprints
    
    def mark_seen(self, fingerprint: str, title: str, source: str):
        """记录/更新指纹。如已存在则+1 seen_count"""
        now = datetime.now().isoformat()
        if fingerprint in self.fingerprints:
            self.fingerprints[fingerprint]["seen_count"] += 1
            self.fingerprints[fingerprint]["last_seen"] = now
        else:
            self.fingerprints[fingerprint] = {
                "title": title[:120],
                "source": source,
                "seen_count": 1,
                "first_seen": now,
                "last_seen": now
            }
        self._save()
    
    def should_exclude(self, fingerprint: str) -> bool:
        """
        判断是否应该排除：
        - seen_count >= 3 且 mode=daily（已在前2次日报中出现过，第3次排除）
        - seen_count >= 2 且 mode=weekly
        """
        if fingerprint not in self.fingerprints:
            return False
        threshold = 3 if self.mode == "daily" else 2
        return self.fingerprints[fingerprint]["seen_count"] >= threshold
    
    def get_marked_count(self, fingerprint: str) -> int:
        """获取该指纹已被标记的次数"""
        if fingerprint not in self.fingerprints:
            return 0
        return self.fingerprints[fingerprint]["seen_count"] - 1  # 首次不算标记
    
    def cleanup_expired(self):
        """清理过期指纹"""
        now = datetime.now()
        cutoff = now - timedelta(days=self.ttl_days)
        to_delete = []
        for fp, record in self.fingerprints.items():
            try:
                last_seen = datetime.fromisoformat(record["last_seen"])
                if last_seen < cutoff:
                    to_delete.append(fp)
            except:
                to_delete.append(fp)
        for fp in to_delete:
            del self.fingerprints[fp]
        if to_delete:
            self._save()
        return len(to_delete)


# ============================================================
# 信息源采集器
# ============================================================
class SourceCollector:
    """
    信息源采集。
    按platforms.md中的信息源评级，使用可用的采集方式。
    获取方式优先级：直接HTTP > 聚合器 > 搜索
    """
    
    def __init__(self, fingerprint_store: FingerprintStore, report_fingerprints: set = None):
        self.fp = fingerprint_store
        # report_fingerprints: 上一次报告中的所有指纹，用于采集前预检
        self.report_fingerprints = report_fingerprints or set()
        self.collected = []  # [{title, source, url, snippet, platform, tag, ...}]
        self.unknown_sources = []  # 无法获取的信息源，输出建议
    
    def _is_duplicate_of_prev_report(self, title: str, source: str, url: str = "") -> bool:
        """采集前预检：如果指纹在上一次报告中已存在，跳过（省资源）"""
        fp = FingerprintStore.make_fingerprint(title, source, url)
        return fp in self.report_fingerprints
    
    def _add_result(self, title: str, source: str, url: str, snippet: str, 
                    platform: str, tags: list, platform_rating: str = "B",
                    source_type: str = "web"):
        """添加采集结果（经过指纹去重后）"""
        fp = FingerprintStore.make_fingerprint(title, source, url)
        
        # 如果指纹已被排除（seen太多遍），跳过
        if self.fp.should_exclude(fp):
            return
        
        # 记录新采集
        self.fp.mark_seen(fp, title, source)
        
        # 计算这是第几次出现（用于标记）
        seen_count = self.fp.fingerprints[fp]["seen_count"]
        
        self.collected.append({
            "fingerprint": fp,
            "title": title,
            "source": source,
            "url": url,
            "snippet": snippet[:300] if snippet else "",
            "platform": platform,
            "platform_rating": platform_rating,
            "source_type": source_type,
            "tags": tags,
            "is_repeat": seen_count > 1,
            "repeat_count": seen_count - 1,
            "collected_at": datetime.now().isoformat()
        })
    
    def _try_web(self, url: str, timeout: int = 10, headers: dict = None) -> Optional[str]:
        """尝试HTTP获取页面内容"""
        try:
            import urllib.request
            default_headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/125.0.0.0 Safari/537.36"
            }
            if headers:
                default_headers.update(headers)
            req = urllib.request.Request(url, headers=default_headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            return None
    
    def _extract_text(self, html: str) -> str:
        """简单提取文本（去除HTML标签）"""
        if not html:
            return ""
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:5000]
    
    # ---------- 具体信息源采集方法 ----------
    
    def collect_weibo_hot(self):
        """微博热搜 — 直接API获取"""
        html = self._try_web("https://weibo.com/ajax/side/hotSearch")
        if not html:
            self.unknown_sources.append({
                "source": "微博热搜(API)",
                "method": "JSON API",
                "status": "失败 - 反爬限制",
                "suggestion": "通过 WebSearch 搜索微博热搜"
            })
            return
        
        # 从JSON API提取
        try:
            data = json.loads(html)
            items = data.get("data", {}).get("realtime", [])
            if not items:
                self.unknown_sources.append({
                    "source": "微博热搜",
                    "method": "JSON API",
                    "status": "API返回格式变化",
                    "suggestion": "检查weibo.com/ajax/side/hotSearch的返回结构"
                })
                return
            for item in items[:15]:
                word = item.get("word", "").strip()
                if len(word) > 3:
                    self._add_result(
                        title=word[:80],
                        source="微博热搜",
                        url="https://weibo.com",
                        snippet=f"微博热搜: {word} (热度: {item.get('raw_hot', 'N/A')})",
                        platform="weibo",
                        tags=["微博热搜"],
                        platform_rating="S"
                    )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.unknown_sources.append({
                "source": "微博热搜",
                "method": "JSON解析",
                "status": f"解析失败: {str(e)[:50]}",
                "suggestion": "通过 WebSearch 搜索微博热搜"
            })
    
    def collect_zhihu_hot(self):
        """知乎热榜 — 直接访问"""
        html = self._try_web("https://www.zhihu.com/hot")
        if not html:
            self.unknown_sources.append({
                "source": "知乎热榜",
                "method": "HTTP直连",
                "status": "无法访问（反爬限制）",
                "suggestion": "使用 WebSearch 搜索知乎热榜"
            })
            return
        
        # 从HTML中提取话题标题
        for match in re.finditer(r'"title"\s*:\s*"([^"]+)"', html):
            title = match.group(1)
            if len(title) > 5 and not title.startswith('知乎') and not title.startswith('首页'):
                self._add_result(
                    title=title[:80],
                    source="知乎热榜",
                    url="https://www.zhihu.com/hot",
                    snippet=f"知乎话题: {title[:120]}",
                    platform="zhihu",
                    tags=["知乎热榜"],
                    platform_rating="A"
                )
                if len(self.collected) > 200:  # 防止爆量
                    break
    
    def collect_bilibili_hot(self):
        """B站热门 — 全品类宽泛采集"""
        rids = {
            36: "B站科技区", 
            1: "B站全站热门",
        }
        for rid, source_name in rids.items():
            api_html = self._try_web(f"https://api.bilibili.com/x/web-interface/ranking/v2?rid={rid}")
            if not api_html:
                continue
            try:
                data = json.loads(api_html)
                if data.get("code") == 0:
                    items = data["data"].get("list", [])
                    if not items:
                        self.unknown_sources.append({
                            "source": source_name,
                            "method": "API",
                            "status": f"rid={rid} 返回空列表",
                            "suggestion": "检查B站API是否有rid变更"
                        })
                    for item in items[:10]:
                        title = item.get("title", "")
                        self._add_result(
                            title=title[:80],
                            source=source_name,
                            url=f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                            snippet=f"播放:{item.get('stat',{}).get('view','?')} 弹幕:{item.get('stat',{}).get('danmaku','?')} | {item.get('owner',{}).get('name','')}",
                            platform="bilibili",
                            tags=["B站热门"],
                            platform_rating="A"
                        )
                    return
            except Exception as e:
                self.unknown_sources.append({
                    "source": source_name,
                    "method": "API解析",
                    "status": f"解析失败: {str(e)[:40]}",
                    "suggestion": "检查B站API结构"
                })
                continue
        self.unknown_sources.append({
            "source": "B站热门",
            "method": "API",
            "status": "所有rid均失败",
            "suggestion": "检查B站API可用性"
        })
    
    def collect_36kr(self):
        """36氪科技资讯 — 全量采集"""
        api_html = self._try_web("https://36kr.com/pp/api/newsflash")
        if api_html:
            try:
                data = json.loads(api_html)
                items = data.get("data", {}).get("items", [])
                if items:
                    for item in items[:20]:
                        title = item.get("title", "") or item.get("description", "")
                        if title and len(title) > 5:
                            self._add_result(
                                title=title[:80],
                                source="36氪",
                                url=item.get("news_url", "https://36kr.com"),
                                snippet=title[:200],
                                platform="36kr",
                                tags=["科技资讯"],
                                platform_rating="A"
                            )
                    return
            except:
                pass
        
        # fallback: HTML提取
        html = self._try_web("https://36kr.com/newsflashes")
        if not html:
            self.unknown_sources.append({
                "source": "36氪快讯",
                "method": "HTTP直连",
                "status": "失败",
                "suggestion": "检查36kr.com/newsflashes是否可访问"
            })
            return
        text = self._extract_text(html)
        count = 0
        for match in re.finditer(r'"title"\s*:\s*"([^"]+)"', html):
            title = match.group(1)
            if count >= 20:
                break
            if len(title) > 5:
                self._add_result(
                    title=title[:80],
                    source="36氪",
                    url="https://36kr.com",
                    snippet=title[:200],
                    platform="36kr",
                    tags=["科技资讯"],
                    platform_rating="A"
                )
                count += 1
    
    def collect_ai_newsletters(self):
        """AI行业周报/newsletter"""
        sources = [
            ("Import AI", "https://importai.substack.com/"),
            ("The Batch", "https://www.deeplearning.ai/the-batch/"),
            ("Interconnects", "https://interconnects.ai/"),
            ("One Useful Thing", "https://www.oneusefulthing.org/"),
            ("Simon Willison", "https://simonwillison.net/"),
        ]
        for name, url in sources:
            html = self._try_web(url, timeout=12)
            if not html:
                self.unknown_sources.append({
                    "source": name,
                    "method": "HTTP直连",
                    "status": f"无法访问 {url}",
                    "suggestion": "检查网络连接；或从RSS获取（如存在）"
                })
                continue
            text = self._extract_text(html)
            for match in re.finditer(r'<h[1-3][^>]*>(.*?)</h[1-3]>', html, re.DOTALL):
                title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                if len(title) > 10 and any(kw in title.lower() for kw in ['ai', 'agent', 'gpt', 'llm', 'model', 'openai', 'google', 'anthropic', '创业', 'work', 'future']):
                    self._add_result(
                        title=title[:100],
                        source=name,
                        url=url,
                        snippet=title,
                        platform="newsletter",
                        tags=["AI行业资讯"],
                        platform_rating="S"
                    )
                    break  # 只取第一篇
    
    def collect_hackernews(self):
        """HackerNews 热门 — 可通过Firebase API直接获取"""
        html = self._try_web("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        if not html:
            self.unknown_sources.append({
                "source": "HackerNews",
                "method": "Firebase API",
                "status": "无法获取topstories列表",
                "suggestion": "使用 algolia API hn.algolia.com/api/v1/search?tags=front_page"
            })
            return
        try:
            story_ids = json.loads(html)[:20]  # 取top 20
            for sid in story_ids:
                story_html = self._try_web(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=8)
                if not story_html:
                    continue
                story = json.loads(story_html)
                title = story.get("title", "")
                url = story.get("url", f"https://news.ycombinator.com/item?id={sid}")
                score = story.get("score", 0)
                if title and score >= 5:
                    self._add_result(
                        title=title[:120],
                        source="HackerNews",
                        url=url,
                        snippet=f"↑{score} | HN热门",
                        platform="hackernews",
                        tags=["海外讨论"],
                        platform_rating="A"
                    )
        except (json.JSONDecodeError, KeyError) as e:
            self.unknown_sources.append({
                "source": "HackerNews",
                "method": "JSON解析",
                "status": f"解析失败: {str(e)[:50]}",
                "suggestion": "手动访问 news.ycombinator.com"
            })
    
    def collect_baidu_hot(self):
        """百度热搜 — 从HTML中提取热搜词条"""
        html = self._try_web("https://top.baidu.com/board?tab=realtime", timeout=10)
        if not html:
            self.unknown_sources.append({
                "source": "百度热搜",
                "method": "HTTP直连",
                "status": "无法访问",
                "suggestion": "尝试移动版 m.baidu.com/s?word=热搜榜"
            })
            return
        for match in re.finditer(r'"word":"([^"]+)"', html):
            word = match.group(1)
            if len(word) > 5 and not word.startswith('百度'):
                self._add_result(
                    title=word[:80],
                    source="百度热搜",
                    url="https://top.baidu.com/board?tab=realtime",
                    snippet=f"百度热搜: {word}",
                    platform="baidu",
                    tags=["百度热搜"],
                    platform_rating="A"
                )
    
    def collect_sogou_weixin(self):
        """搜狗微信搜索 — 国内AI/科技相关内容"""
        import urllib.parse
        keywords = ['AI', '大模型', '人工智能', '裁员', '超级个体', '一人公司', '副业', '创业']
        for kw in keywords[:3]:  # 每次跑3个关键词，控制请求量
            encoded_kw = urllib.parse.quote(kw)
            url = f"https://weixin.sogou.com/weixin?type=2&query={encoded_kw}&ie=utf8"
            html = self._try_web(url, timeout=10)
            if not html:
                self.unknown_sources.append({
                    "source": f"搜狗微信 (关键词:{kw})",
                    "method": "HTTP直连",
                    "status": "无法访问",
                    "suggestion": "搜狗微信有反爬，尝试用 WebSearch 搜索微信文章"
                })
                continue
            
            items_found = 0
            for match in re.finditer(r'<h3>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL):
                href, title_html = match.group(1), match.group(2)
                title = re.sub(r'<[^>]+>', '', title_html).strip()
                if title and len(title) > 5 and items_found < 5:
                    items_found += 1
                    if href.startswith('//'):
                        href = 'https:' + href
                    elif href.startswith('/'):
                        href = 'https://weixin.sogou.com' + href
                    self._add_result(
                        title=title[:80],
                        source=f"搜狗微信",
                        url=href,
                        snippet=f"微信文章 | 关键词: {kw}",
                        platform="weixin",
                        tags=["国内内容", "微信文章"],
                        platform_rating="A"
                    )
            
            if items_found == 0 and kw == keywords[0]:
                self.unknown_sources.append({
                    "source": "搜狗微信",
                    "method": "HTML解析",
                    "status": "解析失败（搜狗页面结构变化或反爬）",
                    "suggestion": "使用 WebSearch 搜索微信文章"
                })
    
    def collect_reddit_hot(self):
        """Reddit热门讨论"""
        subreddits = [
            ("r/Entrepreneur", "https://www.reddit.com/r/Entrepreneur/hot.json?limit=10"),
            ("r/solopreneur", "https://www.reddit.com/r/solopreneur/hot.json?limit=10"),
            ("r/singularity", "https://www.reddit.com/r/singularity/hot.json?limit=10"),
            ("r/artificial", "https://www.reddit.com/r/artificial/hot.json?limit=10"),
            ("r/MachineLearning", "https://www.reddit.com/r/MachineLearning/hot.json?limit=10"),
        ]
        for name, url in subreddits:
            html = self._try_web(url, timeout=12)
            if not html:
                self.unknown_sources.append({
                    "source": f"Reddit {name}",
                    "method": "JSON API",
                    "status": "无法获取",
                    "suggestion": "Reddit API限制；尝试old.reddit.com或使用缓存的RSS"
                })
                continue
            try:
                data = json.loads(html)
                for post in data.get("data", {}).get("children", []):
                    pdata = post.get("data", {})
                    title = pdata.get("title", "")
                    if any(kw in title.lower() for kw in ['ai', 'agent', 'solopreneur', 'business', 'side', '创业', 'future', 'work', 'layoff', 'career']):
                        self._add_result(
                            title=title[:120],
                            source=f"Reddit {name}",
                            url=f"https://reddit.com{pdata.get('permalink', '')}",
                            snippet=f"↑{pdata.get('ups',0)} | {pdata.get('num_comments',0)}条评论",
                            platform="reddit",
                            tags=["海外讨论"],
                            platform_rating="A"
                        )
            except:
                continue
    
    def collect_aihot(self):
        """AI HOT 中文AI资讯采集 — 使用 /api/public/items 端点
        
        aihot.virxact.com 提供公开匿名 REST API，覆盖中国 AI 行业动态。
        必须带特定 User-Agent (aihot-skill/X.Y.Z) 以避免 nginx UA 黑名单 403。
        限流：60 req/min/IP，串行调用。
        数据窗口：items 端点仅返回最近 7 天。
        
        优化：先检查 /api/public/fingerprint（~100字节），指纹未变化则跳过全量拉取。
        """
        AIHOT_UA = "aihot-skill/0.3.4 (+https://aihot.virxact.com/aihot-skill/)"
        aihot_headers = {"User-Agent": AIHOT_UA}
        
        # 计算 24h 前的时间（UTC ISO 8601）
        since = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # 先检查 fingerprint（轻量，~100字节）
        fp_url = "https://aihot.virxact.com/api/public/fingerprint"
        fp_html = self._try_web(fp_url, timeout=5, headers=aihot_headers)
        fp_cache_file = os.path.join(DATA_DIR, "aihot_fingerprint.json")
        
        if fp_html:
            try:
                fp_data = json.loads(fp_html)
                current_fp = fp_data.get("selected", "")
                if os.path.exists(fp_cache_file):
                    try:
                        with open(fp_cache_file) as f:
                            prev_fp = json.load(f).get("selected", "")
                        if current_fp and current_fp == prev_fp:
                            print(f"[hotspot_engine] AI HOT 指纹未变化（{current_fp}），跳过采集")
                            return
                    except (json.JSONDecodeError, IOError):
                        pass  # 缓存损坏，继续拉取
                # 保存新指纹
                with open(fp_cache_file, "w") as f:
                    json.dump(fp_data, f, ensure_ascii=False)
            except json.JSONDecodeError:
                pass  # fingerprint 解析失败，继续拉 items
        
        # 拉取最近 24h 精选（日报默认路径）
        api_url = f"https://aihot.virxact.com/api/public/items?mode=selected&since={since}&take=50"
        html = self._try_web(api_url, timeout=15, headers=aihot_headers)
        
        if not html:
            self.unknown_sources.append({
                "source": "AI HOT (aihot.virxact.com)",
                "method": "REST API /api/public/items",
                "status": "API 不可达（网络问题或临时限流）",
                "suggestion": "检查网络连接；或改用 WebSearch 中文关键词搜索替代"
            })
            return
        
        try:
            data = json.loads(html)
        except json.JSONDecodeError:
            # 可能返回了 HTML 认证墙（旧版行为）或 403 页面
            self.unknown_sources.append({
                "source": "AI HOT (aihot.virxact.com)",
                "method": "REST API /api/public/items",
                "status": "响应非 JSON（可能认证墙或临时故障）",
                "suggestion": "稍后重试；或改用 WebSearch 中文关键词搜索"
            })
            return
        
        items = data.get("items", [])
        if not items:
            # API 正常但无数据（周末/深夜可能出现）
            print(f"[hotspot_engine] AI HOT 返回 0 条精选（since={since}）")
            return
        
        for item in items:
            title = item.get("title", "").strip()
            if not title or len(title) < 3:
                continue
            
            title_en = item.get("title_en", "")  # 原英文标题（可能为 null）
            source_name = item.get("source", "AI HOT")
            url = item.get("url", "")  # 第三方原文
            permalink = item.get("permalink", "")  # 站内中文阅读页
            published_at = item.get("publishedAt", "")  # ISO 8601 UTC
            summary = item.get("summary", "")  # 中文摘要（LLM 生成）
            category = item.get("category", "")  # ai-models/ai-products/industry/paper/tip
            score = item.get("score")  # 0-100 评分（可能为 null）
            selected = item.get("selected", True)
            
            # 构建 snippet：中文摘要 + 发布时间（结构化，便于 Step 3 时效检查解析）
            snippet_parts = []
            if summary:
                snippet_parts.append(summary[:200])
            if published_at:
                snippet_parts.append(f"publishedAt:{published_at}")
            if score is not None:
                snippet_parts.append(f"score:{score}")
            snippet = " | ".join(snippet_parts)
            
            # 映射 category 到标签
            category_tags = {
                "ai-models": "AI模型",
                "ai-products": "AI产品",
                "industry": "AI行业",
                "paper": "AI论文",
                "tip": "AI技巧",
            }
            tags = ["AI HOT"]
            if category and category in category_tags:
                tags.append(category_tags[category])
            if source_name and "X" in source_name:
                tags.append("X/Twitter")
            
            # 显示标题：中文标题 + 英文原文（如有且不同）
            display_title = title[:80]
            if title_en and title_en != title:
                display_title = f"{title_en[:50]}（{title[:30]}）"
            
            # 优先使用站内 permalink（中文、无墙），回退到第三方 url
            item_url = permalink if permalink else url
            
            self._add_result(
                title=display_title[:120],
                source="AI HOT",
                url=item_url,
                snippet=snippet[:300],
                platform="aihot",
                tags=tags,
                platform_rating="S"
            )
        
        print(f"[hotspot_engine] AI HOT 采集完成：{len(items)} 条精选（since={since}）")
    
    def collect_aihot_hot_topics(self):
        """AI HOT 当前热点 — 多源热度排序，回答“现在最热”"""
        AIHOT_UA = "aihot-skill/0.3.4 (+https://aihot.virxact.com/aihot-skill/)"
        aihot_headers = {"User-Agent": AIHOT_UA}
        
        api_url = "https://aihot.virxact.com/api/public/hot-topics"
        html = self._try_web(api_url, timeout=10, headers=aihot_headers)
        
        if not html:
            return  # 静默失败，不阻塞流程
        
        try:
            data = json.loads(html)
        except json.JSONDecodeError:
            return
        
        items = data.get("items", [])
        for item in items[:10]:
            title = item.get("title", "").strip()
            if not title or len(title) < 3:
                continue
            
            source_name = item.get("source", "AI HOT")
            permalink = item.get("permalink", "")
            url = item.get("url", "")
            source_count = item.get("sourceCount", 0)
            
            snippet = f"热点排序 | sourceCount:{source_count}"
            if source_name:
                snippet += f" | source:{source_name}"
            
            tags = ["AI HOT", "当前热点"]
            if source_count >= 5:
                tags.append("多源共振")
            
            self._add_result(
                title=title[:120],
                source="AI HOT 热点",
                url=permalink if permalink else url,
                snippet=snippet[:300],
                platform="aihot",
                tags=tags,
                platform_rating="S"
            )
        
        if items:
            print(f"[hotspot_engine] AI HOT 热点采集完成：{len(items)} 条（top {min(len(items),10)} 入报告）")
    
    def collect_tophub(self):
        """今日热榜聚合器（tophub.today）— 已知JS渲染，标记为受限源"""
        self.unknown_sources.append({
            "source": "tophub.today 科技热榜 (https://tophub.today/c/tech)",
            "method": "HTTP直连",
            "status": "JS渲染页面，无法直接获取",
            "suggestion": "使用 Browser MCP；或改用平台自有API/热榜"
        })
    
    def collect_douyin_hot(self):
        """抖音热榜 — 标记受限，通过替代方案"""
        self.unknown_sources.append({
            "source": "抖音热榜",
            "method": "聚合器/API",
            "status": "tophub JS渲染 + 抖音反爬",
            "suggestion": "使用巨量算数(trends.oceanengine.com)热度趋势；或 Browser MCP"
        })
    
    def collect_jike_hot(self):
        """即刻App — 热门圈子话题"""
        url = "https://m.okjike.com/"
        html = self._try_web(url, timeout=10)
        if not html:
            rss_url = "https://rsshub.app/jike/popular"
            html = self._try_web(rss_url, timeout=10)
            if not html:
                self.unknown_sources.append({
                    "source": "即刻App热门",
                    "method": "HTTP直连 + RSSHub",
                    "status": "无法获取（即刻严格反爬 + RSSHub可能不可用）",
                    "suggestion": "方案1: 本地部署RSSHub；方案2: Browser MCP；方案3: 即刻开放平台API"
                })
                return
            items_found = 0
            for match in re.finditer(r'<title><!\[CDATA\[(.*?)\]\]></title>', html):
                title = match.group(1).strip()
                if title and len(title) > 5 and items_found < 10:
                    items_found += 1
                    self._add_result(
                        title=title[:80],
                        source="即刻热门(RSSHub)",
                        url=url,
                        snippet="即刻App热门话题",
                        platform="jike",
                        tags=["即刻热门", "社区讨论"],
                        platform_rating="B"
                    )
            if items_found > 0:
                return
        
        items_found = 0
        for match in re.finditer(r'"content"[:\s]*"([^"]{10,})"', html):
            content = match.group(1)
            if items_found < 10:
                items_found += 1
                self._add_result(
                    title=content[:80],
                    source="即刻App",
                    url="https://m.okjike.com/",
                    snippet=content[:200],
                    platform="jike",
                    tags=["即刻热门", "社区讨论"],
                    platform_rating="A"
                )
        
        if items_found == 0:
            self.unknown_sources.append({
                "source": "即刻App热门",
                "method": "HTML提取",
                "status": "即刻移动版页面结构无法解析",
                "suggestion": "方案1: RSSHub rsshub.app/jike/popular；方案2: Browser MCP"
            })
    
    def collect_youtube_trends(self):
        """YouTube热门AI/科技视频（通过热门页面）"""
        urls = [
            ("YouTube AI热门", "https://www.youtube.com/feed/explore"),
        ]
        for name, url in urls:
            html = self._try_web(url, timeout=12)
            if not html:
                self.unknown_sources.append({
                    "source": name,
                    "method": "HTTP直连",
                    "status": "Youtube限制访问",
                    "suggestion": "使用 Browser MCP 或 YouTube Data API v3"
                })
                continue
            self.unknown_sources.append({
                "source": name,
                "method": "HTTP直连",
                "status": "JS渲染，获取信息有限",
                "suggestion": "使用 Browser MCP 或 RSS (https://www.youtube.com/feeds/videos.xml?channel_id=...)"
            })
    
    def collect_overseas_blog(self):
        """海外关键人物博客/网站"""
        sources = [
            ("Sam Altman博客", "https://blog.samaltman.com/"),
            ("Paul Graham", "http://paulgraham.com/articles.html"),
            ("Naval", "https://nav.al/"),
            ("Benedict Evans", "https://www.ben-evans.com/"),
        ]
        for name, url in sources:
            html = self._try_web(url, timeout=12)
            if not html:
                self.unknown_sources.append({
                    "source": name,
                    "method": "HTTP直连",
                    "status": f"无法访问 {url}",
                    "suggestion": "检查网络连接；或使用 Jina Reader (r.jina.ai/{url})"
                })
                continue
            text = self._extract_text(html)
            for match in re.finditer(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL):
                href, link_text = match.group(1), match.group(2)
                link_text = re.sub(r'<[^>]+>', '', link_text).strip()
                if len(link_text) > 15 and not href.startswith('#') and not href.startswith('javascript'):
                    self._add_result(
                        title=link_text[:100],
                        source=name,
                        url=url + href if not href.startswith('http') else href,
                        snippet=link_text,
                        platform="blog",
                        tags=["海外观点"],
                        platform_rating="S"
                    )
                    break  # 只取最新一篇
    
    def get_unknown_sources_summary(self):
        """返回无法获取的信息源列表及获取建议"""
        return self.unknown_sources
    
    def run_daily_collection(self):
        """执行每日采集（所有信息源，每个源独立try-except防止单源失败阻塞全流程）"""
        collectors = [
            self.collect_aihot,
            self.collect_aihot_hot_topics,
            self.collect_36kr,
            self.collect_reddit_hot,
            self.collect_hackernews,
            self.collect_baidu_hot,
            self.collect_bilibili_hot,
            self.collect_sogou_weixin,
            self.collect_weibo_hot,
            self.collect_douyin_hot,
            self.collect_zhihu_hot,
            self.collect_jike_hot,
            self.collect_tophub,
        ]
        for collector in collectors:
            try:
                collector()
            except Exception as e:
                print(f"[hotspot_engine] ⚠️ 采集器 {collector.__name__} 失败: {e}")
        return self.collected
    
    def run_weekly_collection(self):
        """执行每周采集（宽幅扫描）"""
        self.run_daily_collection()
        weekly_collectors = [
            self.collect_youtube_trends,
            self.collect_ai_newsletters,
            self.collect_overseas_blog,
        ]
        for collector in weekly_collectors:
            try:
                collector()
            except Exception as e:
                print(f"[hotspot_engine] ⚠️ 周采集器 {collector.__name__} 失败: {e}")
        return self.collected


# ============================================================
# 报告生成器
# ============================================================
def generate_markdown_report(collected: list, mode: str, unknown_sources: list, 
                             dedup_stats: dict = None) -> str:
    """生成结构化Markdown报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    mode_label = "每日" if mode == "daily" else "每周"
    
    lines = []
    lines.append(f"# 🔥 AI×超级个体 热点采集报告 ({mode_label})")
    lines.append(f"> 报告生成时间：{now}")
    lines.append(f"> 采集方式：自动调度 · `hotspot_engine.py`")
    lines.append(f"> 信息源数量：{len(set(item['source'] for item in collected))}个")
    lines.append(f"> 采集条目数：{len(collected)}条")
    if dedup_stats:
        lines.append(f"> 去重统计：采集前排除 {dedup_stats.get('pre_excluded', 0)} 条 · " 
                     f"已标记重复 {dedup_stats.get('marked_repeats', 0)} 条 · "
                     f"已排除 {dedup_stats.get('excluded_stale', 0)} 条")
    lines.append("")
    
    # ---- 按平台分类 ----
    lines.append("---")
    lines.append("## 📊 各平台热点总览")
    lines.append("")
    
    platforms_order = ["AI HOT", "AI HOT 热点", "百度热搜", "HackerNews", "36氪", "搜狗微信", "即刻App", "即刻热门(RSSHub)",
                       "tophub.today", "微博热搜", "抖音热榜", "B站科技区", "B站全站热门",
                       "知乎热榜", "Reddit", "newsletter", "blog", "YouTube AI热门",
                       "Sam Altman博客", "Paul Graham", "Naval", "Benedict Evans",
                       "Import AI", "The Batch", "Interconnects", "One Useful Thing",
                       "Simon Willison"]
    
    for platform in platforms_order:
        platform_items = [item for item in collected if platform in item["source"]]
        if not platform_items:
            continue
        rating = platform_items[0].get("platform_rating", "B")
        rating_icon = {"S": "🔴", "A": "🟡", "B": "🟢"}.get(rating, "⚪")
        lines.append(f"### {rating_icon} {platform}")
        lines.append("")
        
        for item in platform_items:
            repeat_tag = ""
            if item.get("is_repeat"):
                repeat_tag = f" [🔄 第{item['repeat_count']+1}次出现]"
            tags_str = ", ".join(item.get("tags", []))
            url_str = item.get("url", "")
            snippet = item.get("snippet", "")[:150]
            lines.append(f"- **{item['title']}**{repeat_tag}")
            if snippet:
                lines.append(f"  - {snippet}")
            if url_str:
                lines.append(f"  - 📎 {url_str}")
            if tags_str:
                lines.append(f"  - 🏷️ {tags_str}")
            lines.append("")
    
    # ---- 重点人物观点 ----
    lines.append("---")
    lines.append("## 👤 重点人物观点追踪")
    lines.append("")
    person_items = [item for item in collected if item["source"] in [
        "Sam Altman博客", "Paul Graham", "Naval", "Benedict Evans",
        "Import AI", "The Batch", "Interconnects", "One Useful Thing",
        "Simon Willison"
    ]]
    if person_items:
        for item in person_items:
            lines.append(f"- **{item['source']}**：{item['title']}")
            if item.get("snippet"):
                lines.append(f"  > {item['snippet'][:200]}")
            lines.append("")
    else:
        lines.append("> 本期未获取到有效观点（部分海外源受限，见下方附录）")
        lines.append("")
    
    # ---- 受众标签分析 ----
    lines.append("---")
    lines.append("## 📈 本期热点标签分布")
    lines.append("")
    
    tag_counts = {}
    for item in collected:
        for tag in item.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        bar = "█" * min(count, 20)
        lines.append(f"  {tag}: {bar} {count}")
    lines.append("")
    
    # ---- 无法获取的信息源 + 获取建议 ----
    lines.append("---")
    lines.append("## ⚠️ 附录：受限信息源及获取建议")
    lines.append("")
    lines.append("以下信息源本次无法通过HTTP直连获取，需要替代方案：")
    lines.append("")
    lines.append("| 信息源 | 失败原因 | 建议替代方案 |")
    lines.append("|--------|---------|-------------|")
    
    # 去重
    seen_sources = set()
    for s in unknown_sources:
        key = s["source"]
        if key in seen_sources:
            continue
        seen_sources.add(key)
        lines.append(f"| {s['source']} | {s.get('status', '未知')[:40]} | {s.get('suggestion', '')[:60]} |")
    
    lines.append("")
    
    # ---- 选题建议 ----
    lines.append("---")
    lines.append("## 💡 选题建议")
    lines.append("")
    
    noise_titles = ['百度实时热点', '微博热搜榜', '今日热榜', '首页 晚报', '综合 科技', '更多']
    high_priority = [item for item in collected 
                     if item.get("platform_rating") in ("S", "A") 
                     and not item.get("is_repeat")
                     and not any(nt in item['title'] for nt in noise_titles)
                     and item['source'] != 'tophub.today']  # 跳过聚合器本身，取具体平台条目
    
    if not high_priority:
        high_priority = [item for item in collected 
                         if item.get("platform_rating") in ("S", "A")
                         and not item.get("is_repeat")
                         and len(item['title']) > 10]
    
    if high_priority:
        lines.append("基于本次采集，以下方向值得追：")
        lines.append("")
        for i, item in enumerate(high_priority[:5], 1):
            lines.append(f"{i}. **{item['title']}** — 来源：{item['source']}")
            lines.append(f"   建议切入角度：结合[超级个体/AI转型]框架 + {item['tags'][0] if item.get('tags') else '受众共鸣'}")
            lines.append("")
    else:
        lines.append("> 本期未发现高优先级的全新热点，建议关注受限信息源补充后评估。")
        lines.append("")
    
    lines.append("---")
    lines.append(f"*报告由 hotspot_engine.py 自动生成 · {now}*")
    
    return "\n".join(lines)


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "daily"
    assert mode in ("daily", "weekly"), "mode must be 'daily' or 'weekly'"
    
    print(f"[hotspot_engine] 启动{mode}采集模式...")
    
    # 初始化指纹存储
    fp_store = FingerprintStore(mode=mode)
    
    # 清理过期指纹
    expired = fp_store.cleanup_expired()
    if expired:
        print(f"[hotspot_engine] 清理了 {expired} 条过期指纹")
    
    # 读取上一次报告的指纹（用于采集前预检）
    report_file = DAILY_REPORT_FILE if mode == "daily" else WEEKLY_REPORT_FILE
    prev_fingerprints = set()
    prev_report_dir = os.path.join(DATA_DIR, f"prev_{mode}_fingerprints.json")
    if os.path.exists(prev_report_dir):
        try:
            with open(prev_report_dir, "r") as f:
                prev_fingerprints = set(json.load(f))
            print(f"[hotspot_engine] 加载了 {len(prev_fingerprints)} 条上一次报告指纹用于预检")
        except:
            pass
    
    # 初始化采集器
    collector = SourceCollector(fp_store, report_fingerprints=prev_fingerprints)
    
    # 执行采集
    if mode == "daily":
        results = collector.run_daily_collection()
    else:
        results = collector.run_weekly_collection()
    
    print(f"[hotspot_engine] 采集完成：{len(results)} 条")
    
    # 统计去重信息
    dedup_stats = {
        "pre_excluded": len(prev_fingerprints) - len(results) if prev_fingerprints else 0,
        "marked_repeats": sum(1 for r in results if r.get("is_repeat")),
        "excluded_stale": sum(1 for r in results if r.get("repeat_count", 0) >= 2),
        "total_fingerprints": len(fp_store.fingerprints),
    }
    
    # 生成报告
    report = generate_markdown_report(
        results, mode, 
        collector.get_unknown_sources_summary(),
        dedup_stats
    )
    
    # 写入报告文件
    report_file_path = DAILY_REPORT_FILE if mode == "daily" else WEEKLY_REPORT_FILE
    with open(report_file_path, "w") as f:
        f.write(report)
    
    # 保存本次报告的所有指纹（供下一次预检）
    result_fingerprints = [r["fingerprint"] for r in results]
    with open(prev_report_dir, "w") as f:
        json.dump(result_fingerprints, f)
    
    print(f"[hotspot_engine] 报告已生成：{report_file_path}")
    print(f"[hotspot_engine] 完成！")
    
    # 输出报告前500字符作为预览
    print(f"\n--- 报告预览 ---")
    print(report[:500])
    print("...")
