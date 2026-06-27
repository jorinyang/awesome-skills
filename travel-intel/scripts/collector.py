#!/usr/bin/env python3
"""旅游信息采集器 — 云采集端（L2 urllib站点 + L3 Bitable分发）

L1 已迁移至 WSL本地 browser_collector.py (百度+夸克 agent-browser)。
此脚本仅用于云端 cron: L2 urllib 站点直抓 + L3 关键词分发到 Bitable 队列。

Usage:
    python3 collector.py --channels urllib [--date YYYY-MM-DD]
"""

import argparse
import datetime
import json
import logging
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request

log = logging.getLogger(__name__)

# ── 站点配置 ──────────────────────────────────────────────
# 2026-05-30 通道诊断后更新:
#   - 新增: meadin.com(迈点网) 文旅/景区频道, wenlvnews.com(闻旅)
#   - 移除: 贵州文旅厅/8264/中国旅游报 (已迁移至JS-SPA, urllib不可爬)
#   - 保留: pinchain.com(品橙, 唯一原站可用), tripvivid.com(执惠, 低产)
#   - 模式: 新增站用 title= 属性匹配 (现代CMS标准), 原站维持原regex
SITES = [
    {
        "name": "品橙旅游",
        "url": "https://www.pinchain.com/",
        "encoding": "utf-8",
        "pattern": r'<a[^>]*href="(https?://[^"]+)"[^>]*title="([^"]+)"',
        "trust": "medium",
    },
    {
        "name": "迈点网-文旅",
        "url": "https://www.meadin.com/wl/",
        "encoding": "utf-8",
        "pattern": r'<a[^>]*href="([^"]*)"[^>]*>\s*<img[^>]*alt="([^"]+)"',
        "trust": "medium",
    },
    {
        "name": "迈点网-景区",
        "url": "https://www.meadin.com/jq/",
        "encoding": "utf-8",
        "pattern": r'<a[^>]*href="([^"]*)"[^>]*>\s*<img[^>]*alt="([^"]+)"',
        "trust": "medium",
    },
    {
        "name": "闻旅",
        "url": "https://www.wenlvnews.com/",
        "encoding": "utf-8",
        "pattern": r'<a[^>]*href="([^"]*)"[^>]*title="([^"]+)"',
        "trust": "medium",
    },
    {
        "name": "执惠旅游",
        "url": "https://www.tripvivid.com/",
        "encoding": "utf-8",
        "pattern": r'<a[^>]*href="(/[^"]*)"[^>]*>(.{10,80})</a>',
        "trust": "medium",
    },
]

# ── 已退役站点 (JS-SPA, urllib不可爬) ────────────────────
# 贵州文旅厅 whhly.guizhou.gov.cn — 44KB HTML全是document.write壳
# 8264户外 8264.com — 4KB JS壳, 所有内容异步加载
# 中国旅游报 ctnews.com.cn — 仅导航链接, 文章列表JS渲染

FILTER_KW = (
    "探洞|洞穴|溶洞|天坑|桨板|SUP|漂流|溯溪|户外|山地|体旅|营地|徒步|研学|"
    "旅居|康养|景区|5A|旅游城市|避暑|度假|世界级|贵州|黔西南|黔南|黔东南|"
    "政策|规划|条例|通知|节庆|赛事|价格|新品|营销|活动"
)

TIMEOUT = 15
MAX_RESULTS_PER_SITE = 10
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_site(site: dict) -> list[dict]:
    """抓取单个站点首页，提取标题+URL"""
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(site["url"], headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl_ctx)
        html = resp.read().decode(site["encoding"], errors="ignore")
    except Exception as e:
        log.warning("fetch %s failed: %s", site["name"], e)
        return []

    results = []
    seen = set()
    for match in re.finditer(site["pattern"], html, re.DOTALL):
        groups = match.groups()
        if len(groups) == 2:
            href, title = groups
            # Normalize: title may be in either position
            if href.startswith("http") or href.startswith("/"):
                url, raw_title = href, title
            else:
                raw_title, url = href, title

            title_clean = re.sub(r"<[^>]+>", "", raw_title).strip()
            if len(title_clean) < 8 or len(title_clean) > 100:
                continue
            if not re.search(FILTER_KW, title_clean):
                continue

            # Build full URL
            if url.startswith("/"):
                base = re.match(r"(https?://[^/]+)", site["url"]).group(1)
                url = base + url

            if url in seen:
                continue
            seen.add(url)

            results.append({
                "title": title_clean,
                "url": url,
                "snippet": "",
                "source": site["name"],
                "trust": site["trust"],
            })

            if len(results) >= MAX_RESULTS_PER_SITE:
                break

    log.info("  %s: %d results", site["name"], len(results))
    return results


def collect_urllib(sites: list = None) -> list[dict]:
    """L2: urllib 站点直抓"""
    if sites is None:
        sites = SITES
    all_results = []
    for site in sites:
        try:
            results = fetch_site(site)
            all_results.extend(results)
        except Exception as e:
            log.exception("site %s error: %s", site["name"], e)
    return all_results


def collect_web_search(keywords: list[str]) -> list[dict]:
    """[已废弃] L1 已迁移至 browser_collector.py（百度+夸克 agent-browser WSL本地）。
    保留此函数用于向后兼容，始终返回空列表。"""
    return []


def collect(date_str: str = "", channels: list[str] = None) -> list[dict]:
    """主入口：按通道采集"""
    if channels is None:
        channels = ["urllib"]

    today = date_str or datetime.date.today().isoformat()
    all_results = []

    for ch in channels:
        if ch == "urllib":
            results = collect_urllib()
            for r in results:
                r["date"] = today
            all_results.extend(results)

        elif ch == "web":
            # [已废弃] L1 已迁移至 browser_collector.py (百度+夸克)
            log.info("web_search channel: deprecated, L1 now handled by browser_collector.py")

        elif ch == "browser":
            log.warning("agent-browser: only available in WSL local env")

    # Deduplicate by URL (normalize m. vs www. for wenlvnews.com)
    seen = set()
    deduped = []
    for r in all_results:
        url = r["url"]
        # Normalize wenlvnews.com subdomains: m.wenlvnews.com/p/ID.html == www.wenlvnews.com/p/ID.html
        normalized = re.sub(r'https?://(m|www)\.wenlvnews\.com/', 'https://wenlvnews.com/', url)
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(r)

    log.info("collect done: %d results (%d after dedup)", len(all_results), len(deduped))
    return deduped


# ── CLI ────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    p = argparse.ArgumentParser(description="Travel intel collector")
    p.add_argument("--channels", default="urllib", help="comma-separated: urllib (L1→browser_collector.py, L3→l3_poller.py)")
    p.add_argument("--date", default="", help="YYYY-MM-DD, default today")
    args = p.parse_args()

    channels = args.channels.split(",")
    results = collect(args.date, channels)
    print(json.dumps(results, ensure_ascii=False, indent=2))
