#!/usr/bin/env python3
"""L2 urllib 站点直抓 — reusable collector for cron & manual runs.
Usage: python3 l2_collect.py [YYYY-MM-DD] [--output /tmp/l2_results.json]

Sites: 品橙旅游 (pinchain.com), 迈点·文旅 (meadin.com/wl/),
       迈点·景区 (meadin.com/jq/), 闻旅 (wenlvnews.com), 执惠旅游 (tripvivid.com)

Output: JSON array of {title, url, snippet, source, trust, date} → /tmp/l2_results.json
"""

import urllib.request
import urllib.error
import ssl
import re
import json
import sys
import time
from datetime import datetime
from collections import Counter

TODAY = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else datetime.now().strftime('%Y-%m-%d')
OUTPUT = '/tmp/l2_results.json'
for i, a in enumerate(sys.argv):
    if a == '--output' and i + 1 < len(sys.argv):
        OUTPUT = sys.argv[i + 1]

results = []

# ── SSL context for sites with cert issues ──
ctx_bad = ssl.create_default_context()
ctx_bad.check_hostname = False
ctx_bad.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}


def fetch(url, timeout=20, ssl_ctx=None, encoding='utf-8', decode_errors='ignore'):
    """Fetch URL, return decoded text or None."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx)
        raw = resp.read()
        ct = resp.headers.get('Content-Type', '')
        enc_match = re.search(r'charset=([\w-]+)', ct)
        if enc_match:
            try:
                return raw.decode(enc_match.group(1), errors=decode_errors)
            except Exception:
                pass
        return raw.decode(encoding, errors=decode_errors)
    except Exception as e:
        print(f"  ⚠️ Fetch error: {url[:60]}... → {e}", file=sys.stderr)
        return None


def add(title, url, snippet, source, trust='medium'):
    results.append({
        'title': title.strip(),
        'url': url.strip(),
        'snippet': (snippet or title).strip(),
        'source': source,
        'trust': trust,
        'date': TODAY,
    })


# ════════ 1. 品橙旅游 (pinchain.com) ════════
print("=" * 60, file=sys.stderr)
print("[1/5] 品橙旅游 pinchain.com", file=sys.stderr)
html = fetch('https://www.pinchain.com')
if html:
    # <h2><a href="/article/NNNNN">标题</a></h2>
    matches = re.finditer(r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', html)
    count = 0
    for m in matches:
        url = m.group(1)
        title = m.group(2).strip()
        if not url.startswith('http'):
            url = 'https://www.pinchain.com' + url
        if title and len(title) >= 6:
            add(title, url, title, '品橙旅游', 'high')
            count += 1
    print(f"  ✅ 品橙: {count} 条", file=sys.stderr)
else:
    print(f"  ❌ 品橙: fetch failed", file=sys.stderr)

time.sleep(2)

# ════════ 2. 迈点网 文旅 (meadin.com/wl/) ════════
print("[2/5] 迈点网 文旅 meadin.com/wl/", file=sys.stderr)
html = fetch('https://www.meadin.com/wl/')
if html:
    # ⚠️ Known issue: img alt extraction may return 0 if site changed to SPA
    matches = re.finditer(r'<img[^>]*alt="([^"]+)"[^>]*>', html)
    skip_alts = {'图片', 'logo', '二维码', '微信', '头像', 'icon', 'ICO', 'banner', 'Logo'}
    count = 0
    for m in matches:
        title = m.group(1).strip()
        if title and len(title) >= 6 and title not in skip_alts:
            add(title, 'https://www.meadin.com/wl/', title, '迈点文旅', 'medium')
            count += 1
    print(f"  {'✅' if count else '⚠️'} 迈点文旅: {count} 条", file=sys.stderr)
else:
    print(f"  ❌ 迈点文旅: fetch failed", file=sys.stderr)

time.sleep(2)

# ════════ 3. 迈点网 景区 (meadin.com/jq/) ════════
print("[3/5] 迈点网 景区 meadin.com/jq/", file=sys.stderr)
html = fetch('https://www.meadin.com/jq/')
if html:
    matches = re.finditer(r'<img[^>]*alt="([^"]+)"[^>]*>', html)
    skip_alts = {'图片', 'logo', '二维码', '微信', '头像', 'icon', 'ICO', 'banner', 'Logo'}
    count = 0
    for m in matches:
        title = m.group(1).strip()
        if title and len(title) >= 6 and title not in skip_alts:
            add(title, 'https://www.meadin.com/jq/', title, '迈点景区', 'medium')
            count += 1
    print(f"  {'✅' if count else '⚠️'} 迈点景区: {count} 条", file=sys.stderr)
else:
    print(f"  ❌ 迈点景区: fetch failed", file=sys.stderr)

time.sleep(2)

# ════════ 4. 闻旅 (wenlvnews.com) — SSL 绕过 ════════
print("[4/5] 闻旅 wenlvnews.com (SSL绕过)", file=sys.stderr)
html = fetch('https://www.wenlvnews.com', ssl_ctx=ctx_bad)
if html:
    count = 0
    # Pattern 1: <a href="/article/..." title="...">
    for m in re.finditer(r'<a[^>]*href="(/article/\d+\.html)"[^>]*title="([^"]+)"', html):
        url = 'https://www.wenlvnews.com' + m.group(1)
        title = m.group(2).strip()
        if title and len(title) >= 6:
            add(title, url, title, '闻旅', 'medium')
            count += 1
    # Pattern 2: <h2>/<h3><a href="...">标题</a>
    for m in re.finditer(r'<h[23][^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', html):
        url = m.group(1)
        title = m.group(2).strip()
        if not url.startswith('http'):
            url = 'https://www.wenlvnews.com' + url
        if title and len(title) >= 6:
            add(title, url, title, '闻旅', 'medium')
            count += 1
    print(f"  {'✅' if count else '⚠️'} 闻旅: {count} 条", file=sys.stderr)
else:
    print(f"  ❌ 闻旅: fetch failed", file=sys.stderr)

time.sleep(2)

# ════════ 5. 执惠旅游 (tripvivid.com) ════════
print("[5/5] 执惠旅游 tripvivid.com", file=sys.stderr)
html = fetch('https://www.tripvivid.com')
if html:
    count = 0
    skip_prefixes = ('首页', '关于', '联系', '登录', '注册', '搜索', '更多',
                     '分类', '标签', '归档', 'Copyright', '版权所有')
    # Pattern: <a href="..."><tag>标题</tag></a>
    for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>(?:<[^>]+>)*([^<]{8,})\s*</a>', html):
        url = m.group(1)
        title = m.group(2).strip()
        if not url.startswith('http'):
            url = 'https://www.tripvivid.com' + url
        if title and not title.startswith('<') and not any(title.startswith(w) for w in skip_prefixes):
            add(title, url, title, '执惠旅游', 'high')
            count += 1
    # Fallback: <h2>/<h3><a>... if low yield
    if count < 5:
        for m in re.finditer(r'<(?:h[23]|div[^>]*class="[^"]*title[^"]*")[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', html):
            url = m.group(1)
            title = m.group(2).strip()
            if not url.startswith('http'):
                url = 'https://www.tripvivid.com' + url
            if title and len(title) >= 8:
                add(title, url, title, '执惠旅游', 'high')
                count += 1
    print(f"  {'✅' if count else '⚠️'} 执惠: {count} 条", file=sys.stderr)
else:
    print(f"  ❌ 执惠: fetch failed", file=sys.stderr)

# ════════ Output ════════
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 60}", file=sys.stderr)
print(f"📦 L2 站点直抓完成: {len(results)} 条 → {OUTPUT}", file=sys.stderr)
for src, cnt in Counter(r['source'] for r in results).most_common():
    print(f"   {src}: {cnt} 条", file=sys.stderr)
