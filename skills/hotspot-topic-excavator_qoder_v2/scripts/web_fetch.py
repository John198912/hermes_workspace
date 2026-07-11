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
import ipaddress
import re
import html
import sys
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: 缺少依赖包。请执行: pip3 install -r requirements.txt", file=sys.stderr)
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


def inline_to_markdown(el):
    """将元素内的内联子节点转换为 Markdown 文本（避免重复输出）"""
    parts = []
    for child in el.children:
        if child.name is None:  # NavigableString
            text = str(child).strip()
            if text:
                parts.append(text)
        elif child.name in ['strong', 'b']:
            text = child.get_text(strip=True)
            if text:
                parts.append(f'**{text}**')
        elif child.name in ['em', 'i']:
            text = child.get_text(strip=True)
            if text:
                parts.append(f'*{text}*')
        elif child.name == 'a':
            text = child.get_text(strip=True)
            href = child.get('href', '')
            if text and href:
                parts.append(f'[{text}]({href})')
            elif text:
                parts.append(text)
        elif child.name == 'code':
            text = child.get_text(strip=True)
            if text:
                parts.append(f'`{text}`')
        else:
            text = child.get_text(strip=True)
            if text:
                parts.append(text)
    return ' '.join(parts)


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

    # 仅遍历块级元素，通过 inline_to_markdown 处理内联格式，避免文本重复
    block_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'blockquote', 'pre', 'img', 'br', 'a']
    for el in content_el.find_all(block_tags):
        if el.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(el.name[1])
            text = el.get_text(strip=True)
            if text:
                lines.append('')
                lines.append('#' * level + ' ' + text)
                lines.append('')
        elif el.name == 'p':
            text = inline_to_markdown(el)
            if text:
                lines.append('')
                lines.append(text)
        elif el.name == 'br':
            lines.append('')
        elif el.name == 'a':
            # 仅处理不在块级元素内的独立链接
            if el.parent and el.parent.name in ['p', 'li', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                continue
            text = el.get_text(strip=True)
            href = el.get('href', '')
            if text and href:
                lines.append(f'[{text}]({href})')
        elif el.name == 'li':
            text = inline_to_markdown(el)
            if text:
                lines.append('- ' + text)
        elif el.name == 'blockquote':
            text = el.get_text(strip=True)
            if text:
                lines.append('> ' + text)
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


def is_safe_url(url):
    """检查 URL 是否安全（防止 SSRF）"""
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "URL 解析失败"

    if parsed.scheme not in ('http', 'https'):
        return False, f"不允许的协议: {parsed.scheme}"

    hostname = parsed.hostname
    if not hostname:
        return False, "无法解析主机名"

    # 拒绝 loopback、private、link-local 和 metadata 地址
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False, f"拒绝访问内部/保留地址: {hostname}"
    except ValueError:
        # 不是 IP 地址，检查主机名
        if hostname in ('localhost', 'metadata.google.internal'):
            return False, f"拒绝访问内部主机名: {hostname}"

    return True, ""


def fetch_url(url, output_format='markdown', max_length=50000, insecure=False):
    """抓取指定 URL 的内容"""
    # SSRF 防护
    safe, reason = is_safe_url(url)
    if not safe:
        print(f"ERROR: URL 安全检查失败 - {reason}", file=sys.stderr)
        sys.exit(1)

    verify_tls = not insecure
    if insecure:
        print("[WARN] TLS 验证已关闭（--insecure），存在安全风险", file=sys.stderr)

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30, verify=verify_tls)
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
    parser.add_argument('--insecure', action='store_true',
                        help='跳过 TLS 证书验证（不推荐，仅用于调试）')

    args = parser.parse_args()
    fetch_url(args.url, args.output, args.max_length, args.insecure)


if __name__ == '__main__':
    main()
