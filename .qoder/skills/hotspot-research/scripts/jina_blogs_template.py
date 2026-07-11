#!/usr/bin/env python3
"""
Jina Reader Python bypass for 8 key blogs (macOS LibreSSL workaround).

Usage:
  python3 jina_blogs_template.py
  → 8/8 blogs extracted in ~5-12 seconds, output to reports/hotspot/jina_cache/

Why Python bypass not curl:
  - macOS LibreSSL 2.8.3 TLS handshake fails with r.jina.ai (curl exit 28/35)
  - Python `requests` uses urllib3 + OpenSSL path → different TLS negotiation
  - verify=False is required because LibreSSL rejects Jina's certificate chain
    at the handshake protocol level (cert is valid, only handshake fails)

Maintenance: edit the BLOGS list to add/remove tracked blogs.
Add new blog:  ("shortname", "https://example.com/blog/")
"""
import requests
import time
import os

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

OUTDIR = os.path.expanduser("~/Desktop/qoder_workspace/hermes_workspace_tmp/reports/hotspot-research_qoder/jina_cache")
os.makedirs(OUTDIR, exist_ok=True)

results = {}

for name, url in BLOGS:
    outfile = os.path.join(OUTDIR, f"jina_{name}.md")
    jina_url = f"https://r.jina.ai/{url}"
    try:
        r = requests.get(
            jina_url,
            headers={"Accept": "text/markdown", "User-Agent": "Mozilla/5.0"},
            verify=False,
            timeout=15,
        )
        if r.status_code == 200 and len(r.text) > 200:
            with open(outfile, "w") as f:
                f.write(r.text)
            sz = len(r.text)
            results[name] = f"OK ({sz:,} bytes)"
        else:
            results[name] = f"FAIL status={r.status_code} len={len(r.text)}"
    except Exception as e:
        results[name] = f"ERROR {type(e).__name__}: {str(e)[:60]}"
    time.sleep(0.5)  # rate limit

print("=== Jina Reader Python Bypass Results ===")
for n, r in results.items():
    print(f"  {n:18s} → {r}")
