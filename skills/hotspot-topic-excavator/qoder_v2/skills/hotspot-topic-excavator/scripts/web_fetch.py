#!/usr/bin/env python3
"""
降级路径·网页直连抓取脚本（Qoder 适配版）

当 WebFetch 返回不完整内容或被 Cloudflare WAF 阻断时，
使用本脚本通过 Python requests + 浏览器 UA 直连抓取。

用法:
    python3 scripts/web_fetch.py <url> [--output markdown|html] [--max-length 50000]

输出:
    打印抓取结果到 stdout
    返回码: 0=成功, 1=参数错误, 2=网络错误, 3=内容为空, 4=WAF 阻断
"""

import argparse
import re
import html
import sys

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: 缺少依赖包。请执行: pip3 install --user requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5,zh-CN;q=0.5,zh;q=0.4',
}

WAF_MARKERS = ['please wait', 'verifying', 'checking your browser', 'cloudflare', 'challenge']


def is_waf_blocked(text):
    """检测是否被 Cloudflare WAF 阻断"""
    lower = text.lower()
    if len(text) < 500:
        for marker in WAF_MARKERS:
            if marker in lower:
                return True
    return False


def html_to_markdown(html_content):
    """将 HTML 内容转换为 Markdown"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 移除 script、style、nav、footer、header 等非内容元素
    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        tag.decompose()

    # 提取正文区域（按优先级）
    content_selectors = [
        'article',
        '[class*="entry-content"]',
        '[class*="post-content"]',
        '[class*="article-body"]',
        '[class*="article_content"]',
        '[class*="single-content"]',
        'main',
    ]

    content_el = None
    for selector in content_selectors:
        content_el = soup.select_one(selector)
        if content_el:
            break

    if not content_el:
        content_el = soup.body if soup.body else soup

    lines = []

    for el in content_el.descendants:
        if el.name is None:  # NavigableString
            text = str(el).strip()
            if text:
                lines.append(text)
            continue

        if el.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(el.name[1])
            text = el.get_text(strip=True)
            lines.append('')
            lines.append('#' * level + ' ' + text)
            lines.append('')
        elif el.name == 'p':
            text = el.get_text(strip=True)
            if text:
                lines.append('')
                lines.append(text)
        elif el.name == 'br':
            lines.append('')
        elif el.name == 'strong' or el.name == 'b':
            text = el.get_text(strip=True)
            if text:
                lines.append('**' + text + '**')
        elif el.name == 'em' or el.name == 'i':
            text = el.get_text(strip=True)
            if text:
                lines.append('*' + text + '*')
        elif el.name == 'a':
            text = el.get_text(strip=True)
            href = el.get('href', '')
            if text and href:
                lines.append(f'[{text}]({href})')
        elif el.name in ['ul', 'ol']:
            lines.append('')
        elif el.name == 'li':
            text = el.get_text(strip=True)
            if text:
                lines.append('- ' + text)
        elif el.name == 'blockquote':
            text = el.get_text(strip=True)
            if text:
                lines.append('> ' + text)
        elif el.name == 'code':
            text = el.get_text(strip=True)
            if text:
                lines.append('`' + text + '`')
        elif el.name == 'pre':
            text = el.get_text(strip=True)
            if text:
                lines.append('```')
                lines.append(text)
                lines.append('```')
        elif el.name == 'img':
            alt = el.get('alt', '')
            src = el.get('src', '')
            if src:
                lines.append(f'![{alt}]({src})')

    # 合并多余空行
    result = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                result.append('')
                prev_empty = True
        else:
            result.append(line)
            prev_empty = False

    return '\n'.join(result)


def fetch_url(url, output_format='markdown', max_length=50000):
    """抓取指定 URL 的内容"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30, verify=False)
    except Exception as e:
        print(f"ERROR: 网络请求失败 - {e}", file=sys.stderr)
        sys.exit(2)

    if resp.status_code != 200:
        print(f"ERROR: HTTP {resp.status_code}", file=sys.stderr)
        sys.exit(2)

    text = resp.text

    if is_waf_blocked(text):
        print("WARNING: 可能被 Cloudflare WAF 阻断", file=sys.stderr)
        sys.exit(4)

    if not text or len(text) < 100:
        print("WARNING: 返回内容过短，可能抓取失败", file=sys.stderr)
        sys.exit(3)

    # 输出状态信息
    print(f"[FETCH] URL: {url}", file=sys.stderr)
    print(f"[FETCH] Status: {resp.status_code}, Size: {len(text)} bytes", file=sys.stderr)

    if output_format == 'markdown':
        content = html_to_markdown(text)
    else:
        content = text

    if len(content) > max_length:
        content = content[:max_length]
        print(f"[FETCH] 内容已截断至 {max_length} 字符", file=sys.stderr)

    print(content)
    print(f"[FETCH] 完成，内容长度: {len(content)} 字符", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description='降级路径·网页直连抓取')
    parser.add_argument('url', help='目标 URL')
    parser.add_argument('--output', '-o', choices=['markdown', 'html'], default='markdown',
                        help='输出格式 (默认: markdown)')
    parser.add_argument('--max-length', '-m', type=int, default=50000,
                        help='最大输出长度 (默认: 50000)')

    args = parser.parse_args()
    fetch_url(args.url, args.output, args.max_length)


if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
