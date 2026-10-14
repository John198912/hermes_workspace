#!/usr/bin/env python3
"""
hotspot_engine.py — 热点采集核心引擎 (Antigravity & Zero-Dependency 适配版)
========================================================================
职责：
  1. 指纹去重（基于标题+来源+时间的哈希，带过期与生命周期机制）
  2. 多平台信息源采集（AI HOT v1 / Jina 8人博客 / 微博 / B站 / 百度 / HackerNews 等）
  3. 指纹存储与读取（JSON文件，按日/周分桶，支持跨日期去重）
  4. 严格遵循原则 #16（AM/PM版本保留，防止多次运行相互覆盖）
  5. 零外部依赖（纯 Python 标准库 urllib/ssl/json/gzip，兼容 Python 3.9 ~ 3.12+）
  6. 自动动态定位当前工作区 reports/hotspot/ 目录

用法：
  python3 scripts/hotspot_engine.py daily   # 每日采集
  python3 scripts/hotspot_engine.py weekly  # 每周汇总采集
"""

import os
import sys
import time
import json
import hashlib
import re
import ssl
import gzip
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Set
from urllib.parse import urlparse

# ============================================================
# 动态工作区与路径探测
# ============================================================
def get_project_root() -> str:
    """动态获取项目根目录，避免硬编码用户主目录"""
    if "HOTSPOT_DIR" in os.environ and os.path.exists(os.environ["HOTSPOT_DIR"]):
        return os.path.abspath(os.environ["HOTSPOT_DIR"])
    
    # 尝试由当前执行目录推断
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, "reports", "hotspot")) or os.path.exists(os.path.join(cwd, "config")):
        return cwd
        
    # 尝试由脚本文件自身位置向上探测
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(script_dir)
    if os.path.exists(os.path.join(parent, "reports", "hotspot")) or os.path.exists(os.path.join(parent, "config")):
        return parent
    if os.path.exists(os.path.join(script_dir, "reports", "hotspot")):
        return script_dir
        
    return cwd

PROJECT_ROOT = get_project_root()
DATA_DIR = os.path.join(PROJECT_ROOT, "reports", "hotspot")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
os.makedirs(DATA_DIR, exist_ok=True)

DAILY_FINGERPRINT_FILE = os.path.join(DATA_DIR, "fingerprints_daily.json")
WEEKLY_FINGERPRINT_FILE = os.path.join(DATA_DIR, "fingerprints_weekly.json")

# 最新报告软链接（方便工具/Agent直接读取最新报告）
DAILY_REPORT_LATEST = os.path.join(DATA_DIR, "report_daily.md")
WEEKLY_REPORT_LATEST = os.path.join(DATA_DIR, "report_weekly.md")
DAILY_DATA_LATEST = os.path.join(DATA_DIR, "hotspot_daily.json")
WEEKLY_DATA_LATEST = os.path.join(DATA_DIR, "hotspot_weekly.json")

# 指纹过期：每日指纹保留7天，每周指纹保留30天
FINGERPRINT_DAILY_TTL_DAYS = 7
FINGERPRINT_WEEKLY_TTL_DAYS = 30

# 高质量源去重阈值
HIGH_QUALITY_SOURCES = ["AI HOT", "HackerNews", "博客", "blog", "Anthropic", "Altman", "Karpathy"]
HIGH_QUALITY_EXCLUDE_THRESHOLD = 4  # 高质量源seen_count>=4才排除
DEFAULT_EXCLUDE_THRESHOLD = 2       # 普通源seen_count>=2排除，降低跨日期低质重复
MAX_DAILY_ITEMS = 120               # 提高上限，确保S级与A级源充分覆盖


def get_dated_report_path(mode: str = "daily") -> str:
    """
    实现原则 #16：AM/PM 版本保留规则。
    如果同一天多次运行（如上午与下午），不得覆盖已有报告：
    1. 若已有当日首份无后缀报告且当前为下午/晚上 -> 原报告重命名为 _am.md，新报告命名为 _pm.md
    2. 若已存在 _am.md 且当前为下午 -> 生成 _pm.md（若 _pm.md 也存在则生成 _pm_v2.md）
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    if mode != "daily":
        return os.path.join(DATA_DIR, f"report_weekly_{today_str}.md")
        
    hour = datetime.now().hour
    is_pm = hour >= 12
    
    base_file = os.path.join(DATA_DIR, f"report_daily_{today_str}.md")
    am_file = os.path.join(DATA_DIR, f"report_daily_{today_str}_am.md")
    pm_file = os.path.join(DATA_DIR, f"report_daily_{today_str}_pm.md")
    pm_v2_file = os.path.join(DATA_DIR, f"report_daily_{today_str}_pm_v2.md")
    
    if not is_pm:
        # 上午运行
        if os.path.exists(base_file) and not os.path.exists(am_file):
            return am_file
        return base_file
    else:
        # 下午或晚上运行
        if os.path.exists(base_file) and not os.path.exists(am_file):
            try:
                os.rename(base_file, am_file)
                print(f"[hotspot_engine] 遵循原则 #16：已将原有报告归档为 {os.path.basename(am_file)}")
            except Exception as e:
                print(f"[hotspot_engine] 归档上午报告出错: {e}")
            return pm_file
        elif os.path.exists(pm_file):
            return pm_v2_file
        else:
            return pm_file


def get_dated_data_path(mode: str = "daily") -> str:
    today_str = datetime.now().strftime("%Y-%m-%d")
    prefix = "hotspot_daily" if mode == "daily" else "hotspot_weekly"
    hour = datetime.now().hour
    suffix = "_pm" if (hour >= 12 and mode == "daily") else ""
    return os.path.join(DATA_DIR, f"{prefix}_{today_str}{suffix}.json")


# ============================================================
# 指纹引擎
# ============================================================
class FingerprintStore:
    def __init__(self, mode: str):
        assert mode in ("daily", "weekly")
        self.mode = mode
        self.fingerprint_file = DAILY_FINGERPRINT_FILE if mode == "daily" else WEEKLY_FINGERPRINT_FILE
        self.ttl_days = FINGERPRINT_DAILY_TTL_DAYS if mode == "daily" else FINGERPRINT_WEEKLY_TTL_DAYS
        self.fingerprints: dict = self._load()
    
    def _load(self) -> dict:
        if os.path.exists(self.fingerprint_file):
            try:
                with open(self.fingerprint_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save(self):
        try:
            with open(self.fingerprint_file, "w", encoding="utf-8") as f:
                json.dump(self.fingerprints, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[hotspot_engine] 保存指纹库失败: {e}")
    
    @staticmethod
    def make_fingerprint(title: str, source: str, url: str = "") -> str:
        norm_title = re.sub(r'\s+', ' ', title.strip().lower())[:80]
        domain = ""
        if url:
            try:
                domain = urlparse(url).netloc.replace("www.", "")
            except Exception:
                pass
        raw = f"{norm_title}|{source}|{domain}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()
    
    def is_known(self, fingerprint: str) -> bool:
        return fingerprint in self.fingerprints
    
    def mark_seen(self, fingerprint: str, title: str, source: str):
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
    
    def should_exclude(self, fingerprint: str, source: str = "") -> bool:
        if fingerprint not in self.fingerprints:
            return False
        record = self.fingerprints[fingerprint]
        seen = record.get("seen_count", 1)
        if self.mode == "daily":
            is_high_quality = any(hq.lower() in source.lower() for hq in HIGH_QUALITY_SOURCES) if source else False
            threshold = HIGH_QUALITY_EXCLUDE_THRESHOLD if is_high_quality else DEFAULT_EXCLUDE_THRESHOLD
            return seen >= threshold
        else:
            return seen >= 2
    
    def cleanup_expired(self) -> int:
        now = datetime.now()
        cutoff = now - timedelta(days=self.ttl_days)
        to_delete = []
        for fp, record in self.fingerprints.items():
            try:
                last_seen_str = record.get("last_seen", "")
                if last_seen_str:
                    last_seen = datetime.fromisoformat(last_seen_str)
                    if last_seen < cutoff:
                        to_delete.append(fp)
            except Exception:
                to_delete.append(fp)
        for fp in to_delete:
            del self.fingerprints[fp]
        if to_delete:
            self._save()
        return len(to_delete)


# ============================================================
# 信息源采集器 (零依赖纯标准库)
# ============================================================
class SourceCollector:
    def __init__(self, fingerprint_store: FingerprintStore, report_fingerprints: set = None):
        self.fp = fingerprint_store
        self.report_fingerprints = report_fingerprints or set()
        self.collected: List[Dict] = []
        self.unknown_sources: List[Dict] = []
        self.excluded_count = 0
        self.capped_count = 0

    def _add_result(self, title: str, source: str, url: str, snippet: str, 
                    platform: str, tags: list, platform_rating: str = "B",
                    source_type: str = "web",
                    source_quality: str = "B",
                    relevance_hint: str = ""):
        fp = FingerprintStore.make_fingerprint(title, source, url)
        
        if self.fp.should_exclude(fp, source):
            self.excluded_count += 1
            return

        if len(self.collected) >= MAX_DAILY_ITEMS:
            self.capped_count += 1
            return
        
        self.fp.mark_seen(fp, title, source)
        seen_count = self.fp.fingerprints[fp]["seen_count"]
        
        if not relevance_hint:
            ai_kws = ['ai', 'llm', 'gpt', 'agent', '大模型', '人工智能', 'chatgpt', 'openai', 
                      'claude', 'anthropic', 'deepseek', '模型', '算法', '自动化', '裁员', '转型', 
                      '自由职业', '副业', '创业', '个人品牌', '知识付费', '超级个体', '一人公司']
            title_lower = title.lower()
            matched = [kw for kw in ai_kws if kw.lower() in title_lower]
            if matched:
                relevance_hint = f"命中关键词: {', '.join(matched)}"
        
        lifecycle_stage = "rising" if seen_count >= 2 else "new"

        self.collected.append({
            "fingerprint": fp,
            "title": title,
            "source": source,
            "url": url,
            "snippet": snippet[:400] if snippet else "",
            "platform": platform,
            "platform_rating": platform_rating,
            "source_type": source_type,
            "source_quality": source_quality,
            "relevance_hint": relevance_hint,
            "tags": tags,
            "is_repeat": seen_count > 1,
            "repeat_count": seen_count - 1,
            "lifecycle_stage": lifecycle_stage,
            "first_seen": self.fp.fingerprints.get(fp, {}).get("first_seen", ""),
            "collected_at": datetime.now().isoformat()
        })

    def _try_web(self, url: str, timeout: int = 12, headers: dict = None, verify_ssl: bool = True) -> Optional[str]:
        import urllib.request
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        if headers:
            default_headers.update(headers)
        
        ctx = ssl.create_default_context()
        if not verify_ssl:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
        req = urllib.request.Request(url, headers=default_headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                raw = resp.read()
                if resp.info().get("Content-Encoding") == "gzip":
                    try:
                        raw = gzip.decompress(raw)
                    except Exception:
                        pass
                return raw.decode("utf-8", errors="replace")
        except Exception:
            return None

    # ---------- S 级核心信息源 ----------

    def collect_aihot(self):
        """
        AI HOT 聚合源 (aihot.news REST API v1)
        中国 AI 圈高价值精选热点
        """
        api_config_path = os.path.join(CONFIG_DIR, "aihot_api_v1.json")
        endpoint = "https://aihot.news/api/v1/items"
        ua = "aihot-api/2.0.0 aihot-skill"
        limit = 25
        window = "24h"
        
        if os.path.exists(api_config_path):
            try:
                with open(api_config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    endpoint = cfg.get("endpoint", endpoint)
                    ua = cfg.get("headers", {}).get("User-Agent", ua)
                    limit = cfg.get("parameters", {}).get("limit", limit)
                    window = cfg.get("parameters", {}).get("window", window)
            except Exception:
                pass
                
        url = f"{endpoint}?mode=selected&window={window}&limit={limit}"
        html = self._try_web(url, timeout=12, headers={"User-Agent": ua, "Accept-Encoding": "gzip"})
        if not html:
            self.unknown_sources.append({
                "source": "AI HOT (aihot.news)",
                "method": "REST API v1",
                "status": "无法连接或超时",
                "suggestion": "检查网络连接或使用 search_web 降级"
            })
            return
            
        try:
            data = json.loads(html)
            items = data.get("items", [])
            if not items:
                return
            for item in items:
                title = item.get("title", "")
                orig_title = item.get("originalTitle", "")
                full_title = f"{orig_title}（{title}）" if orig_title and orig_title != title else title
                summary = item.get("summary", "")
                links = item.get("links", {})
                orig_url = links.get("original", links.get("aihot", "https://aihot.news"))
                source_info = item.get("source", {}).get("name", "AI HOT")
                pub_date = item.get("publishedAt", "")
                score = item.get("score", 0)
                category = item.get("category", "ai-products")
                
                self._add_result(
                    title=full_title[:150],
                    source=f"AI HOT: {source_info}",
                    url=orig_url,
                    snippet=f"【{category}】{summary} | 发布时间:{pub_date} 得分:{score}",
                    platform="aihot",
                    tags=["AI行业资讯", "中国AI圈", "S级聚合"],
                    platform_rating="S",
                    source_quality="A",
                    relevance_hint=f"AIHOT精选({category})，发布于: {pub_date}"
                )
        except Exception as e:
            self.unknown_sources.append({
                "source": "AI HOT (aihot.news)",
                "method": "JSON解析",
                "status": f"解析失败: {str(e)[:50]}",
                "suggestion": "检查 API 返回结构"
            })

    def collect_jina_blogs(self):
        """
        8 位关键人物与机构博客 (Jina Reader API 提取)
        涵盖 Sam Altman, Karpathy, Naval, Paul Graham, Anthropic 等
        """
        blogs = [
            ("Sam Altman", "https://blog.samaltman.com/"),
            ("Karpathy GitHub", "https://karpathy.github.io/"),
            ("Karpathy Bear Blog", "https://karpathy.bearblog.dev/blog/"),
            ("Naval", "https://nav.al/"),
            ("Paul Graham", "http://paulgraham.com/articles.html"),
            ("Anthropic Research", "https://www.anthropic.com/research"),
            ("Ethan Mollick", "https://www.oneusefulthing.org/feed"),
            ("Benedict Evans", "https://www.ben-evans.com/"),
        ]
        for name, target_url in blogs:
            jina_url = f"https://r.jina.ai/{target_url}"
            md_text = self._try_web(
                jina_url,
                timeout=15,
                headers={"Accept": "text/markdown", "User-Agent": "Mozilla/5.0"},
                verify_ssl=False
            )
            if not md_text or len(md_text) < 150:
                self.unknown_sources.append({
                    "source": f"{name}博客",
                    "method": "Jina Reader",
                    "status": "获取失败或内容过短",
                    "suggestion": f"通过 search_web 查询 {name} 最新动态"
                })
                continue
                
            lines = [l.strip() for l in md_text.splitlines() if l.strip()]
            snippet = " ".join(lines[:6])[:280]
            title_cand = ""
            for line in lines[:10]:
                if line.startswith("#"):
                    clean = re.sub(r'^#+\s*', '', line).strip()
                    if len(clean) > 5 and clean.lower() != name.lower():
                        title_cand = clean
                        break
            if not title_cand:
                title_cand = f"{name} 最新文章与思考"
                
            self._add_result(
                title=f"{name}: {title_cand}"[:120],
                source=f"{name}博客",
                url=target_url,
                snippet=snippet,
                platform="blog",
                tags=["海外观点", "关键人物", "S级核心"],
                platform_rating="S",
                source_quality="A",
                relevance_hint=f"思想家/研究机构博客({name})"
            )
            time.sleep(0.2)

    # ---------- A 级国内与海外源 ----------

    def collect_weibo_hot(self):
        """微博热搜 — 带 Referer 避开反爬"""
        html = self._try_web(
            "https://weibo.com/ajax/side/hotSearch",
            timeout=10,
            headers={
                "Referer": "https://weibo.com/",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            }
        )
        if not html:
            self.unknown_sources.append({
                "source": "微博热搜(API)",
                "method": "JSON API",
                "status": "失败 - 反爬限制或超时",
                "suggestion": "需要 Referer: https://weibo.com/"
            })
            return
        try:
            data = json.loads(html)
            items = data.get("data", {}).get("realtime", [])
            if not items:
                return
            for item in items[:20]:
                word = item.get("word", "").strip()
                if len(word) > 3:
                    self._add_result(
                        title=word[:80],
                        source="微博热搜",
                        url="https://weibo.com",
                        snippet=f"微博热搜: {word} (热度: {item.get('raw_hot', 'N/A')})",
                        platform="weibo",
                        tags=["微博热搜"],
                        platform_rating="A",
                        source_quality="B",
                        relevance_hint=""
                    )
        except Exception as e:
            self.unknown_sources.append({
                "source": "微博热搜",
                "method": "JSON解析",
                "status": f"解析失败: {str(e)[:50]}",
                "suggestion": "检查返回格式"
            })

    def collect_hackernews(self):
        """HackerNews 热门技术与创业讨论 (Firebase API)"""
        html = self._try_web("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        if not html:
            self.unknown_sources.append({
                "source": "HackerNews",
                "method": "Firebase API",
                "status": "无法获取topstories列表",
                "suggestion": "检查国际网络连接"
            })
            return
        try:
            story_ids = json.loads(html)[:20]
            for sid in story_ids:
                story_html = self._try_web(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=6)
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
                        snippet=f"↑{score} | HN热门讨论",
                        platform="hackernews",
                        tags=["海外讨论", "技术前沿"],
                        platform_rating="A",
                        source_quality="A",
                        relevance_hint=""
                    )
        except Exception as e:
            self.unknown_sources.append({
                "source": "HackerNews",
                "method": "JSON解析",
                "status": f"解析失败: {str(e)[:50]}",
                "suggestion": "重试获取"
            })

    def collect_bilibili_hot(self):
        """B站科技区与全站热门"""
        rids = {36: "B站科技区", 1: "B站全站热门"}
        for rid, source_name in rids.items():
            api_html = self._try_web(f"https://api.bilibili.com/x/web-interface/ranking/v2?rid={rid}")
            if not api_html:
                continue
            try:
                data = json.loads(api_html)
                if data.get("code") == 0:
                    items = data.get("data", {}).get("list", [])
                    for item in items[:8]:
                        title = item.get("title", "")
                        self._add_result(
                            title=title[:80],
                            source=source_name,
                            url=f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                            snippet=f"播放:{item.get('stat',{}).get('view','?')} 弹幕:{item.get('stat',{}).get('danmaku','?')} | UP主:{item.get('owner',{}).get('name','')}",
                            platform="bilibili",
                            tags=["B站热门", "视频生态"],
                            platform_rating="A",
                            source_quality="B",
                            relevance_hint=""
                        )
                    return
            except Exception:
                continue
        self.unknown_sources.append({
            "source": "B站热门",
            "method": "API",
            "status": "API访问超时或格式变动",
            "suggestion": "检查 bilibili.com 接口"
        })

    def collect_baidu_hot(self):
        """百度热搜 (噪声过滤与赛道关键词标记)"""
        html = self._try_web("https://top.baidu.com/board?tab=realtime", timeout=10)
        if not html:
            self.unknown_sources.append({
                "source": "百度热搜",
                "method": "HTTP直连",
                "status": "无法访问",
                "suggestion": "检查网络连接"
            })
            return
        count = 0
        for match in re.finditer(r'"word":"([^"]+)"', html):
            word = match.group(1)
            if count >= 20:
                break
            if len(word) > 4 and not word.startswith('百度'):
                count += 1
                relevance = ""
                if any(kw in word.lower() for kw in ['ai', '模型', '裁员', '转型', '创业', '就业', '35',
                                                      'chatgpt', '人工智能', '技术', '工作', '数字', '科技',
                                                      '失业', '副业', '自由', '升级', '教育', '创新']):
                    relevance = f"含赛道关键词"
                self._add_result(
                    title=word[:80],
                    source="百度热搜",
                    url="https://top.baidu.com/board?tab=realtime",
                    snippet=f"百度热搜: {word}",
                    platform="baidu",
                    tags=["百度热搜"],
                    platform_rating="A",
                    source_quality="C",
                    relevance_hint=relevance
                )

    def collect_sogou_weixin(self):
        """搜狗微信搜索科技与副业关键词"""
        import urllib.parse
        keywords = ['AI大模型', '超级个体', 'AI副业']
        for kw in keywords:
            encoded_kw = urllib.parse.quote(kw)
            url = f"https://weixin.sogou.com/weixin?type=2&query={encoded_kw}&ie=utf8"
            html = self._try_web(url, timeout=8)
            if not html:
                continue
            for match in re.finditer(r'<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?</h3>', html, re.DOTALL):
                link, title_raw = match.group(1), match.group(2)
                title = re.sub(r'<[^>]+>', '', title_raw).strip()
                if len(title) > 8:
                    self._add_result(
                        title=title[:90],
                        source=f"微信文章({kw})",
                        url=link if link.startswith("http") else f"https://weixin.sogou.com{link}",
                        snippet=f"微信深度文章: {title}",
                        platform="weixin",
                        tags=["微信生态", "国内内容"],
                        platform_rating="B",
                        source_quality="B",
                        relevance_hint=f"微信公众号文章({kw})"
                    )
                    break

    def collect_reddit_hot(self):
        """Reddit 热门探讨 (受限源检测)"""
        html = self._try_web(
            "https://www.reddit.com/r/singularity/hot.json?limit=5",
            timeout=8,
            headers={"User-Agent": "macOS:hotspot-research:v2.0 (by /u/researcher)"}
        )
        if not html or "<body" in html:
            self.unknown_sources.append({
                "source": "Reddit (r/singularity, r/solopreneur)",
                "method": "JSON API",
                "status": "反爬拦截 (Cloudflare / 403)",
                "suggestion": "降级方案：使用 Antigravity 原生 search_web 工具检索海外讨论"
            })
            return
        try:
            data = json.loads(html)
            posts = data.get("data", {}).get("children", [])
            for post in posts[:5]:
                pdata = post.get("data", {})
                title = pdata.get("title", "")
                if title:
                    self._add_result(
                        title=title[:120],
                        source="Reddit r/singularity",
                        url=f"https://reddit.com{pdata.get('permalink', '')}",
                        snippet=f"Score: {pdata.get('score', 0)} | {title}",
                        platform="reddit",
                        tags=["海外讨论", "社区热议"],
                        platform_rating="A",
                        source_quality="A",
                        relevance_hint="Reddit前沿讨论"
                    )
        except Exception:
            pass

    def run_daily_collection(self) -> List[Dict]:
        """按优先级采集信息源：S级源 -> A级源 -> B级源"""
        collectors = [
            self.collect_aihot,         # S级: AI HOT v1
            self.collect_jina_blogs,    # S级: 8人博客
            self.collect_hackernews,    # A级: HackerNews
            self.collect_weibo_hot,     # A级: 微博热搜 (已修反爬)
            self.collect_bilibili_hot,  # A级: B站
            self.collect_baidu_hot,     # A级/C质: 百度热搜
            self.collect_sogou_weixin,  # B级: 微信
            self.collect_reddit_hot,    # 尝试Reddit
        ]
        for collector in collectors:
            try:
                collector()
                if len(self.collected) >= MAX_DAILY_ITEMS:
                    print(f"[hotspot_engine] 已达采集条目上限 {MAX_DAILY_ITEMS}，完成主力源采集")
                    break
            except Exception as e:
                print(f"[hotspot_engine] ⚠️ 采集器 {collector.__name__} 异常: {e}")
        return self.collected

    def run_weekly_collection(self) -> List[Dict]:
        return self.run_daily_collection()


# ============================================================
# 报告草案生成器
# ============================================================
def generate_markdown_report(collected: list, mode: str, unknown_sources: list, dedup_stats: dict = None) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    mode_label = "每日" if mode == "daily" else "每周"
    
    lines = []
    lines.append(f"# 🔥 AI×超级个体 热点采集报告 ({mode_label})")
    lines.append(f"> 报告生成时间：{now} CST")
    lines.append(f"> 采集引擎：`scripts/hotspot_engine.py` (Antigravity 适配版)")
    lines.append(f"> 采集条目数：{len(collected)} 条 · 信息源覆盖：{len(set(item['source'] for item in collected))} 个")
    if dedup_stats:
        lines.append(f"> 去重统计：指纹库总计 {dedup_stats.get('total_fingerprints', 0)} 条 · "
                     f"跨日期重复 {dedup_stats.get('marked_repeats', 0)} 条 · "
                     f"热度上升中 {dedup_stats.get('rising_items', 0)} 条 · "
                     f"过滤已排除 {dedup_stats.get('excluded_by_dedup', 0)} 条")
    lines.append("")
    
    # ---- S 级核心热点（AI HOT + 思想家博客） ----
    s_items = [i for i in collected if i.get("platform_rating") == "S"]
    lines.append("---")
    lines.append("## 🌟 S 级核心信号（AI HOT & 思想家博客）")
    lines.append("")
    if s_items:
        for idx, item in enumerate(s_items[:20], 1):
            lines.append(f"### {idx}. {item['title']}")
            lines.append(f"- **来源**：{item['source']} | **链接**：[{item['url']}]({item['url']})")
            if item.get("snippet"):
                lines.append(f"- **摘要**：{item['snippet']}")
            if item.get("relevance_hint"):
                lines.append(f"- **标签/线索**：`{item['relevance_hint']}`")
            lines.append("")
    else:
        lines.append("> 本期未采集到 S 级源数据。\n")

    # ---- 各平台热点总览 ----
    lines.append("---")
    lines.append("## 📊 平台热点总览")
    lines.append("")
    
    by_platform = {}
    for item in collected:
        p = item.get("platform", "other")
        by_platform.setdefault(p, []).append(item)
        
    for p_name, p_items in by_platform.items():
        if p_name in ("aihot", "blog"):
            continue
        lines.append(f"### 📍 平台：{p_name.upper()} ({len(p_items)} 条)")
        for item in p_items[:8]:
            repeat_tag = f" `[持续发酵 +{item['repeat_count']}]`" if item.get("is_repeat") else ""
            lines.append(f"- **{item['title']}**{repeat_tag}")
            lines.append(f"  - 来源: {item['source']} | 📎 {item['url']}")
            if item.get("relevance_hint"):
                lines.append(f"  - 💡 {item['relevance_hint']}")
        lines.append("")

    # ---- 受限信息源附录 ----
    lines.append("---")
    lines.append("## ⚠️ 附录：受限信息源及获取建议")
    lines.append("")
    lines.append("| 信息源 | 采集状态 | 建议替代方案 |")
    lines.append("|--------|---------|-------------|")
    seen_unknown = set()
    for s in unknown_sources:
        k = s["source"]
        if k not in seen_unknown:
            seen_unknown.add(k)
            lines.append(f"| {s['source']} | {s.get('status', '未知')} | {s.get('suggestion', '')} |")
    lines.append("")
    
    lines.append("---")
    lines.append(f"*报告由 Antigravity 热点采集引擎自动生成 · {now}*")
    return "\n".join(lines)


def export_collected_json(collected: list, mode: str) -> str:
    today_str = datetime.now().strftime("%Y-%m-%d")
    data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "mode": mode,
            "count": len(collected),
            "project_root": PROJECT_ROOT
        },
        "items": collected
    }
    data_file = get_dated_data_path(mode)
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data_file


# ============================================================
# 主执行入口
# ============================================================
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "daily"
    assert mode in ("daily", "weekly"), "mode must be 'daily' or 'weekly'"
    
    print(f"[hotspot_engine] 启动 {mode} 采集模式...")
    print(f"[hotspot_engine] 工作区根目录: {PROJECT_ROOT}")
    print(f"[hotspot_engine] 数据输出目录: {DATA_DIR}")
    
    fp_store = FingerprintStore(mode=mode)
    expired = fp_store.cleanup_expired()
    if expired:
        print(f"[hotspot_engine] 清理了 {expired} 条过期指纹")
        
    collector = SourceCollector(fp_store)
    if mode == "daily":
        results = collector.run_daily_collection()
    else:
        results = collector.run_weekly_collection()
        
    print(f"[hotspot_engine] 采集完成，共获取 {len(results)} 条数据")
    
    dedup_stats = {
        "total_fingerprints": len(fp_store.fingerprints),
        "excluded_by_dedup": collector.excluded_count,
        "capped_by_limit": collector.capped_count,
        "marked_repeats": sum(1 for r in results if r.get("is_repeat")),
        "rising_items": sum(1 for r in results if r.get("lifecycle_stage") == "rising"),
    }
    
    report_content = generate_markdown_report(
        results, mode, 
        collector.unknown_sources,
        dedup_stats
    )
    
    report_path = get_dated_report_path(mode)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"[hotspot_engine] 报告已保存: {report_path}")
    
    # 更新最新报告软链接
    latest_link = DAILY_REPORT_LATEST if mode == "daily" else WEEKLY_REPORT_LATEST
    try:
        if os.path.exists(latest_link) or os.path.islink(latest_link):
            os.remove(latest_link)
        os.symlink(os.path.basename(report_path), latest_link)
        print(f"[hotspot_engine] 软链接已更新: {latest_link} -> {os.path.basename(report_path)}")
    except Exception as e:
        print(f"[hotspot_engine] 创建软链接失败: {e}")
        
    # 导出 JSON 数据
    json_path = export_collected_json(results, mode)
    latest_json = DAILY_DATA_LATEST if mode == "daily" else WEEKLY_DATA_LATEST
    try:
        if os.path.exists(latest_json) or os.path.islink(latest_json):
            os.remove(latest_json)
        os.symlink(os.path.basename(json_path), latest_json)
    except Exception:
        pass
        
    print(f"[hotspot_engine] JSON 数据已导出: {json_path}")
    print(f"[hotspot_engine] 采集与报告生成全部完成！")
