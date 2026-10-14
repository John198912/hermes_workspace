#!/usr/bin/env python3
"""
jina_blogs_template.py — 8位关键人物与研究博客提取工具 (Zero-Dependency Python 版本)
================================================================================
使用 Jina Reader (https://r.jina.ai/) 将博客 URL 提取为 Markdown 格式。
针对 macOS LibreSSL 环境做了纯标准库 SSL Context 适配，不依赖 requests 或外部 pip 包。
"""

import os
import sys
import time
import ssl
import gzip
import urllib.request

BLOGS = [
    ("altman",          "https://blog.samaltman.com/"),
    ("karpathy_github", "https://karpathy.github.io/"),
    ("karpathy_bear",   "https://karpathy.bearblog.dev/blog/"),
    ("naval",           "https://nav.al/"),
    ("pg",              "http://paulgraham.com/articles.html"),
    ("anthropic",       "https://www.anthropic.com/research"),
    ("mollick",         "https://www.oneusefulthing.org/feed"),
    ("evans",           "https://www.ben-evans.com/"),
]

OUTDIR = os.environ.get("JINA_CACHE_DIR", "/tmp")
os.makedirs(OUTDIR, exist_ok=True)
results = {}

# 创建宽松 SSL 上下文以兼容 macOS LibreSSL 握手
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for name, url in BLOGS:
    outfile = os.path.join(OUTDIR, f"jina_{name}.md")
    jina_url = f"https://r.jina.ai/{url}"
    try:
        req = urllib.request.Request(
            jina_url,
            headers={
                "Accept": "text/markdown",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)",
                "Accept-Encoding": "gzip"
            }
        )
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            raw = resp.read()
            if resp.info().get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            text = raw.decode("utf-8", errors="replace")
            
            if len(text) > 200:
                with open(outfile, "w", encoding="utf-8") as f:
                    f.write(text)
                sz = len(text)
                results[name] = f"OK ({sz:,} bytes) -> {outfile}"
            else:
                results[name] = f"WARN (短文本 len={len(text)})"
    except Exception as e:
        results[name] = f"ERROR {type(e).__name__}: {str(e)[:60]}"
    time.sleep(0.3)

print("=== Jina Reader Python Bypass Results ===")
for n, r in results.items():
    print(f"  {n:18s} → {r}")