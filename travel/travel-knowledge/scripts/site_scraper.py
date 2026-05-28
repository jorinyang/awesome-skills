#!/usr/bin/env python3
"""
行业站点抓取器 — 为 blogwatcher RSS 源补充非 RSS 站点的内容采集
调用方式: python3 site_scraper.py [--type knowledge|monitor] [--output json|text]
"""
import urllib.request, ssl, re, sys, json, os, time

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ── 站点配置 ──
SITES = [
    {
        "name": "环球旅讯",
        "url": "https://www.traveldaily.cn/",
        "encoding": "utf-8",
        "article_pattern": r'<a[^>]*href="(/article/\d+)"[^>]*>(.{10,200})</a>',
        "base_url": "https://www.traveldaily.cn",
        "filter_kw": "探洞|洞穴|溶洞|天坑|桨板|SUP|漂流|溯溪|户外|山地|体旅|营地|徒步|研学|贵州|民宿|露营|景区|门票|交通|政策",
    },
    {
        "name": "执惠旅游",
        "url": "https://www.tripvivid.com/",
        "encoding": "utf-8",
        "article_pattern": r'<a[^>]*href="(https?://(?:www\.)?tripvivid\.com/(?:meeting|deep|sentiment)?/?(?:\d+)\.html)"[^>]*>(.{10,200})</a>',
        "base_url": "https://www.tripvivid.com",
        "filter_kw": "探洞|洞穴|溶洞|天坑|桨板|SUP|漂流|溯溪|户外|山地|体旅|营地|徒步|研学|贵州|民宿|露营|马蜂窝|赛事|旅游产业|文旅惠报",
    },
    {
        "name": "8264户外",
        "url": "https://www.8264.com/",
        "encoding": "gbk",
        "article_pattern": r'<a[^>]*href="(https?://(?:www\.)?8264\.com/viewnews-\d+-page-1\.html)"[^>]*>(.{10,200})</a>',
        "base_url": "https://www.8264.com",
        "filter_kw": "探洞|洞穴|溶洞|天坑|桨板|SUP|漂流|溯溪|户外|山地|贵州|徒步|攀岩|绳降|露营|装备",
    },
    {
        "name": "贵州文旅厅",
        "url": "https://whhly.guizhou.gov.cn/",
        "encoding": "utf-8",
        "article_pattern": r'<a[^>]*href="(https?://whhly\.guizhou\.gov\.cn/xwzx/[a-z]+/\d+/t\d{8}_\d+\.html)"[^>]*title="([^"]{10,200})"',
        "base_url": "https://whhly.guizhou.gov.cn",
        "filter_kw": "旅游|景区|民宿|户外|山地|体育|赛事|活动|政策|优惠|补贴|通知|公告|探洞|天坑|桨板|漂流|村超|旅居",
    },
    {
        "name": "中国旅游报",
        "url": "http://www.ctnews.com.cn/",
        "encoding": "utf-8",
        "article_pattern": r'<a[^>]*href="(https?://(?:www\.)?ctnews\.com\.cn/[^"]+?content/[^"]+?content_\d+\.html)"[^>]*>(.{10,200})</a>',
        "base_url": "http://www.ctnews.com.cn",
        "filter_kw": "旅游|户外|山地|贵州|景区|民宿|露营|徒步|政策|优惠|探洞|天坑|桨板",
    },
]

SEARCH_URLS = [
    ("环球旅讯-贵州", "https://www.traveldaily.cn/search?keyword=%E8%B4%B5%E5%B7%9E", "utf-8",
     r'<a[^>]*href="(/article/\d+)"[^>]*>(.{10,200})</a>',
     "https://www.traveldaily.cn"),
    ("环球旅讯-户外", "https://www.traveldaily.cn/search?keyword=%E6%88%B7%E5%A4%96", "utf-8",
     r'<a[^>]*href="(/article/\d+)"[^>]*>(.{10,200})</a>',
     "https://www.traveldaily.cn"),
]

def fetch_html(url, encoding="utf-8"):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=12, context=ssl_ctx)
        return resp.read().decode(encoding, errors='ignore')
    except Exception:
        return None

def extract_articles(html, patterns, base_url, filter_kw):
    results = []
    seen = set()
    for pattern in ([patterns] if isinstance(patterns, str) else patterns):
        matches = re.findall(pattern, html)
        for href, raw_title in matches:
            title = re.sub(r'<[^>]+>', '', raw_title).strip()
            title = title.replace('&nbsp;', ' ').replace('&amp;', '&')
            if title in seen or len(title) < 10:
                continue
            skip_words = ['首页', '登录', '注册', '关于', '联系', '导航', '更多', 'javascript']
            if any(w in title for w in skip_words):
                continue
            if re.search(filter_kw, title):
                seen.add(title)
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('//'):
                    full_url = 'https:' + href
                else:
                    full_url = base_url.rstrip('/') + '/' + href.lstrip('/')
                results.append({"title": title, "url": full_url})
    return results[:15]

def fetch_article_detail(url, encoding="utf-8"):
    try:
        html = fetch_html(url, encoding)
        if not html: return ""
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        for selector in [r'<article[^>]*>(.*?)</article>',
                        r'<div[^>]*class="[^"]*article-content[^"]*"[^>]*>(.*?)</div>',
                        r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>']:
            m = re.search(selector, text, re.DOTALL)
            if m: text = m.group(1); break
        text = re.sub(r'<[^>]+>', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()[:300]
    except Exception:
        return ""

def scrape_all(task_type="knowledge"):
    today = time.strftime("%Y-%m-%d")
    all_results = {}
    for site in SITES:
        html = fetch_html(site["url"], site["encoding"])
        if not html:
            all_results[site["name"]] = {"error": "fetch failed", "articles": []}
            continue
        patterns = [site["article_pattern"]] + site.get("extra_patterns", [])
        articles = extract_articles(html, patterns, site["base_url"], site["filter_kw"])
        for a in articles[:3]:
            a["snippet"] = fetch_article_detail(a["url"], site["encoding"])
        all_results[site["name"]] = {"url": site["url"], "count": len(articles), "articles": articles}
    # L2 search
    for name, url, enc, pattern, base in SEARCH_URLS:
        html = fetch_html(url, enc)
        if html:
            articles = extract_articles(html, pattern, base, "")
            if articles:
                existing = {a["title"] for a in all_results.get("环球旅讯", {}).get("articles", [])}
                new_articles = [a for a in articles if a["title"] not in existing][:8]
                if new_articles:
                    all_results[name] = {"count": len(new_articles), "articles": new_articles}
    return {"date": today, "task_type": task_type, "sites": all_results}

def format_output(data, fmt="text"):
    if fmt == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    lines = [f"📰 行业站点抓取 | {data['date']}"]
    for name, site_data in data["sites"].items():
        if "error" in site_data:
            lines.append(f"\n❌ {name}: {site_data['error']}")
            continue
        lines.append(f"\n{'='*50}")
        lines.append(f"📌 {name} | {site_data.get('count', 0)} 篇")
        lines.append(f"{'='*50}")
        for i, a in enumerate(site_data.get("articles", [])[:8]):
            snippet = a.get("snippet", "")
            lines.append(f"  {i+1}. {a['title'][:80]}")
            lines.append(f"     {a['url']}")
            if snippet:
                lines.append(f"     📝 {snippet[:100]}")
    return "\n".join(lines)

if __name__ == "__main__":
    task_type = "monitor" if "--type" in sys.argv and sys.argv[sys.argv.index("--type")+1] == "monitor" else "knowledge"
    output_fmt = "json" if "--output" in sys.argv and sys.argv[sys.argv.index("--output")+1] == "json" else "text"
    data = scrape_all(task_type)
    print(format_output(data, output_fmt))
