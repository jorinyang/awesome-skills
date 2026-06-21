#!/usr/bin/env python3
"""browser_collector — agent-browser 多引擎/多平台采集 → JSON / 飞书 Wiki

L1 通用搜索: 百度 + 夸克 (行业+竞品关键词)
L3 平台直搜: B站 (视频内容，竞品洞察)

本地 WSL 运行，依赖 agent-browser 0.27+ + Chromium 150+。

Usage:
    python3 browser_collector.py                               # 全量 L1+L3，输出 JSON
    python3 browser_collector.py --mode industry               # 仅行业关键词
    python3 browser_collector.py --mode competitor             # 仅竞品关键词
    python3 browser_collector.py --channel L1                  # 仅百度+夸克
    python3 browser_collector.py --channel L3                  # 仅 B站
    python3 browser_collector.py --push                        # 采集后推送到飞书 Wiki
    python3 browser_collector.py --push --dry-run              # 模拟推送
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
import urllib.parse
from datetime import date

log = logging.getLogger(__name__)

# ── agent-browser 路径 ─────────────────────────────────────
AGENT_BROWSER = os.path.expanduser("~/.local/bin/agent-browser")
CHROMIUM_PATH = os.path.expanduser("~/.chromium/chrome-linux/chrome")

# ── 代理环境变量 ───────────────────────────────────────────
PROXY_VARS = [
    "http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
    "ALL_PROXY", "NO_PROXY",
]

MAX_PER_KEYWORD = 8
MAX_PER_PLATFORM = 5  # 平台直搜每条关键词取更少（视频质量>数量）

# ── L1 通用搜索关键词 ──────────────────────────────────────
INDUSTRY_KEYWORDS = [
    "贵州旅游 最新 2026 景区 政策",
    "贵州户外运动 探洞 桨板 漂流 新线路",
    "贵州康养旅居 避暑旅游 2026",
    "黔西南 黔南 黔东南 旅游新项目",
    "贵州世界级旅游目的地 规划",
]

COMPETITOR_KEYWORDS = [
    "探洞 天坑 贵州 户外 攻略",
    "桨板 SUP 贵州 水上运动",
    "贵州 洞穴探险 新发现 线路",
    "贵州 溯溪 瀑降 户外新玩法",
    "兴义 安龙 贞丰 户外旅游 新项目",
]

# ── L3 B站直搜关键词 ──────────────────────────────────────
BILIBILI_KEYWORDS = [
    "贵州 探洞",
    "贵州 桨板 SUP",
    "贵州 瀑降 溯溪",
    "贵州 天坑 户外",
    "贵州 洞穴探险 溶洞",
    "兴义 万峰林 户外",
]

# ── L3 头条直搜关键词 ─────────────────────────────────────
TOUTIAO_KEYWORDS = [
    "贵州 探洞 户外",
    "贵州 桨板 SUP 水上运动",
    "贵州 溶洞 洞穴探险",
    "贵州 溯溪 瀑降",
    "兴义 户外 旅游",
    "黔西南 万峰林 户外",
]

# ── 噪音过滤正则 ───────────────────────────────────────────
NOISE_PATTERNS = [
    r"^(探|桨|洞|穴)[（(]",
    r"^[探桨洞穴]$",
    r"字的|的解释|的拼音|怎么读|笔顺|部首",
    r"精选笔记$",
    r"百度图片$",
    r"视频大全.*在线观看$",
    r"买东西逛淘宝",
    r"批发厂家.*爱采购",
    r"^\d+小时前$|^\d+分钟前$",
    r"^携程旅行$",
    r"^百度百科$",
]
NOISE_RE = re.compile("|".join(NOISE_PATTERNS))

# ── 飞书 Wiki 节点 ─────────────────────────────────────────
WIKI_NODES = {
    "industry": "V0Lhwl7KYiWYDDk1vCncv2GhnYf",
    "competitor": "EAMYw1CPoipVWtkObbtcR2oDnNc",
}


# ═══════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════

def clean_env() -> dict:
    env = os.environ.copy()
    for v in PROXY_VARS:
        env.pop(v, None)
    return env


def check_agent_browser() -> bool:
    if not os.path.exists(AGENT_BROWSER):
        log.error("agent-browser not found at %s", AGENT_BROWSER)
        return False
    if not os.path.exists(CHROMIUM_PATH):
        log.error("Chromium not found at %s", CHROMIUM_PATH)
        return False
    return True


def agent_eval(js_code: str, timeout: int = 15) -> str:
    env = clean_env()
    try:
        proc = subprocess.run(
            [AGENT_BROWSER, "eval", js_code],
            capture_output=True, text=True, timeout=timeout, env=env,
        )
        return proc.stdout.strip() if proc.returncode == 0 else ""
    except Exception:
        return ""


def parse_agent_json(raw: str, label: str = "") -> list:
    """解析 agent-browser 返回的 JSON（处理外层引号包裹）"""
    if not raw or raw == "[]":
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        log.debug("  JSON parse failed for %s", label)
        return []
    if isinstance(parsed, str):
        try:
            parsed = json.loads(parsed)
        except (json.JSONDecodeError, TypeError):
            return []
    if not isinstance(parsed, list):
        return []
    return parsed


def is_noise(title: str) -> bool:
    t = title.strip()
    if len(t) < 5:
        return True
    if NOISE_RE.search(t):
        return True
    if "\n" in t and ("精选" in t or "图片" in t):
        return True
    return False


def dedup_results(results: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for r in results:
        url = r["url"]
        norm = re.sub(r"http://www\.baidu\.com/link\?url=.*", url, url)
        # B站视频去重：BV号
        bv = re.search(r"(BV[a-zA-Z0-9]+)", url)
        if bv:
            norm = f"bilibili:{bv.group(1)}"
        if norm not in seen:
            seen.add(norm)
            deduped.append(r)
    return deduped


def classify_result(item: dict) -> str:
    kw = item.get("kw_category", "")
    for ck in COMPETITOR_KEYWORDS + BILIBILI_KEYWORDS + TOUTIAO_KEYWORDS:
        if ck[:8] in kw:
            return "competitor"
    return "industry"


# ═══════════════════════════════════════════════════════════════
# L1: 百度 + 夸克 通用搜索
# ═══════════════════════════════════════════════════════════════

def _current_url() -> str:
    """获取当前页面 URL，用于检测反爬跳转"""
    return agent_eval("window.location.href", timeout=5)

def search_baidu(keyword: str) -> list[dict]:
    env = clean_env()
    query_enc = urllib.parse.quote(keyword)
    url = f"https://www.baidu.com/s?wd={query_enc}"

    results = []
    MAX_RETRIES = 1  # 百度验证码是会话级的，重试无意义；仅一次尝试
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            proc = subprocess.run(
                [AGENT_BROWSER, "open", url],
                capture_output=True, text=True, timeout=20, env=env,
            )
            if proc.returncode != 0:
                log.warning("  [百度] open failed (attempt=%d)", attempt)
                return results
            time.sleep(4)

            # ★ 检测百度反爬验证码跳转 (2026-06-13)
            page_url = _current_url()
            if "wappass.baidu.com" in page_url or "captcha" in page_url:
                if attempt < MAX_RETRIES:
                    log.warning("  [百度] captcha/verify page detected, retry %d/%d",
                                attempt, MAX_RETRIES)
                    time.sleep(10)
                    continue
                else:
                    log.warning("  [百度] captcha persists after %d retries, skip", MAX_RETRIES)
                    return results

            log.info("  [百度] ✓ %s", keyword[:30])

            # ★ 多选择器兜底 (2026-06-13): 百度页面 DOM 可能随版本变化
            # 优先使用新版选择器，回退到旧版
            js_code = (
                "(()=>{const sel=['.result h3 a','.c-container h3 a',"
                "'h3.c-title a','h3.t a','h3 a'];"
                "for(const s of sel){"
                "const els=document.querySelectorAll(s);"
                "if(els.length)return JSON.stringify(Array.from(els)"
                f".slice(0,{MAX_PER_KEYWORD})"
                ".map(a=>({title:a.textContent.trim(),url:a.href})))}"
                "return '[]'})()"
            )
            raw = agent_eval(js_code)
            for item in parse_agent_json(raw, keyword):
                title = (item.get("title") or "").strip()
                url_val = (item.get("url") or "").strip()
                if not title or not url_val or is_noise(title):
                    continue
                results.append({
                    "title": title, "url": url_val,
                    "source": "baidu", "channel": "L1",
                })
            log.info("  [百度] ↳ %d results", len(results))
            break  # success — exit retry loop

        except subprocess.TimeoutExpired:
            log.warning("  [百度] timeout (attempt=%d)", attempt)
            if attempt < MAX_RETRIES:
                time.sleep(5)
        except Exception as e:
            log.exception("  [百度] error: %s (attempt=%d)", e, attempt)
            break
    return results


def search_quark(keyword: str) -> list[dict]:
    env = clean_env()
    query_enc = urllib.parse.quote(keyword)
    url = f"https://www.quark.cn/s?q={query_enc}"

    results = []
    try:
        proc = subprocess.run(
            [AGENT_BROWSER, "open", url],
            capture_output=True, text=True, timeout=20, env=env,
        )
        if proc.returncode != 0:
            log.warning("  [夸克] open failed")
            return results
        log.info("  [夸克] ✓ %s", keyword[:30])
        time.sleep(5)

        js_code = (
            "JSON.stringify(Array.from(document.querySelectorAll("
            "'article a[href]'"
            f")).slice(0,{MAX_PER_KEYWORD * 2})"
            ".map(a=>({title:a.textContent.trim(),url:a.href}))"
            ")"
        )
        raw = agent_eval(js_code)
        seen = set()
        for item in parse_agent_json(raw, keyword):
            title = (item.get("title") or "").strip()
            url_val = (item.get("url") or "").strip()
            if not title or not url_val or is_noise(title):
                continue
            if url_val in seen:
                continue
            seen.add(url_val)
            results.append({
                "title": title, "url": url_val,
                "source": "quark", "channel": "L1",
            })
            if len(results) >= MAX_PER_KEYWORD:
                break
        log.info("  [夸克] ↳ %d results", len(results))
    except subprocess.TimeoutExpired:
        log.warning("  [夸克] timeout")
    except Exception as e:
        log.exception("  [夸克] error: %s", e)
    return results


# ═══════════════════════════════════════════════════════════════
# L3: B站 平台直搜
# ═══════════════════════════════════════════════════════════════

def search_bilibili(keyword: str) -> list[dict]:
    """B站视频搜索 — 提取标题/URL/UP主"""
    env = clean_env()
    query_enc = urllib.parse.quote(keyword)
    url = f"https://search.bilibili.com/all?keyword={query_enc}&order=pubdate"

    results = []
    try:
        proc = subprocess.run(
            [AGENT_BROWSER, "open", url],
            capture_output=True, text=True, timeout=20, env=env,
        )
        if proc.returncode != 0:
            log.warning("  [B站] open failed")
            return results
        log.info("  [B站] ✓ %s", keyword[:30])
        time.sleep(6)  # B站渲染较慢

        js_code = (
            "JSON.stringify(Array.from(document.querySelectorAll("
            "'.bili-video-card'"
            f")).slice(0,{MAX_PER_PLATFORM})"
            ".map(card=>{"
            "const a=card.querySelector('a');"
            "const tit=card.querySelector('.bili-video-card__info--tit');"
            "const author=card.querySelector('.bili-video-card__info--author');"
            "const meta=card.querySelector('.bili-video-card__info--meta');"
            "return{"
            "title:tit?tit.textContent.trim():'',"
            "url:a?a.href:'',"
            "author:author?author.textContent.trim():'',"
            "meta:meta?meta.textContent.trim():''"
            "}}))"
        )
        raw = agent_eval(js_code, timeout=15)
        for item in parse_agent_json(raw, keyword):
            title = (item.get("title") or "").strip()
            url_val = (item.get("url") or "").strip()
            author = (item.get("author") or "").strip()
            if not title or not url_val:
                continue
            if not url_val.startswith("https://www.bilibili.com/video/"):
                continue
            meta = item.get("meta", "")
            results.append({
                "title": title, "url": url_val,
                "source": "bilibili", "channel": "L3",
                "author": author, "meta": meta,
            })
        log.info("  [B站] ↳ %d videos", len(results))
    except subprocess.TimeoutExpired:
        log.warning("  [B站] timeout")
    except Exception as e:
        log.exception("  [B站] error: %s", e)
    return results


# ═══════════════════════════════════════════════════════════════
# L3: 头条 平台直搜
# ═══════════════════════════════════════════════════════════════

def _decode_toutiao_url(jump_url: str) -> str:
    """解码头条双层跳转 URL → 真实 article URL"""
    try:
        from urllib.parse import urlparse, parse_qs, unquote
        parsed = urlparse(jump_url)
        params = parse_qs(parsed.query)
        inner = params.get("url", [jump_url])[0]
        # 第一层解码
        decoded1 = unquote(inner)
        # 如果还是 jump URL，再解一层
        if "sou.toutiao.com/search/jump" in decoded1:
            inner2 = urlparse(decoded1)
            params2 = parse_qs(inner2.query)
            real = params2.get("url", [decoded1])[0]
            return unquote(real)
        return decoded1
    except Exception:
        return jump_url


def search_toutiao(keyword: str) -> list[dict]:
    """头条搜索 — 滚动页面后提取关键词匹配的资讯+视频"""
    env = clean_env()
    query_enc = urllib.parse.quote(keyword)
    url = f"https://so.toutiao.com/search?dvpf=pc&source=input&keyword={query_enc}"

    results = []
    try:
        proc = subprocess.run(
            [AGENT_BROWSER, "open", url],
            capture_output=True, text=True, timeout=20, env=env,
        )
        if proc.returncode != 0:
            return results
        log.info("  [头条] ✓ %s", keyword[:30])
        time.sleep(5)

        # 滚动到搜索结果区（跳过热榜）
        subprocess.run(
            [AGENT_BROWSER, "scroll", "down", "800"],
            capture_output=True, text=True, timeout=5, env=env,
        )
        time.sleep(2)

        # 提取含关键词的链接（排除热榜的 trending/event_type=hot_board）
        kw_chars = keyword.replace(" ", "|")
        js_code = (
            "JSON.stringify(Array.from(document.querySelectorAll('a'))"
            ".filter(a=>{const t=a.textContent.trim();const h=a.href||'';"
            f"return t.length>10 && /{kw_chars}/.test(t) && !h.includes('event_type=hot_board')"
            "})"
            f".slice(0,{MAX_PER_PLATFORM})"
            ".map(a=>({title:a.textContent.trim().substring(0,100),url:a.href}))"
            ")"
        )
        raw = agent_eval(js_code, timeout=12)

        for item in parse_agent_json(raw, keyword):
            title = (item.get("title") or "").strip()
            url_val = (item.get("url") or "").strip()
            if not title or not url_val or is_noise(title):
                continue
            # 解码双层跳转 URL
            real_url = _decode_toutiao_url(url_val)
            results.append({
                "title": title, "url": real_url,
                "source": "toutiao", "channel": "L3",
            })
        log.info("  [头条] ↳ %d results", len(results))
    except subprocess.TimeoutExpired:
        log.warning("  [头条] timeout")
    except Exception as e:
        log.exception("  [头条] error: %s", e)
    return results


# ═══════════════════════════════════════════════════════════════
# 主采集 + 推送
# ═══════════════════════════════════════════════════════════════

def collect(mode: str = "all", channels: list[str] = None) -> dict:
    """主采集函数"""
    if channels is None:
        channels = ["L1", "L3"]

    all_kw = []
    if "L1" in channels:
        if mode in ("all", "industry"):
            all_kw.extend([("baidu", kw) for kw in INDUSTRY_KEYWORDS])
            all_kw.extend([("quark", kw) for kw in INDUSTRY_KEYWORDS])
        if mode in ("all", "competitor"):
            all_kw.extend([("baidu", kw) for kw in COMPETITOR_KEYWORDS])
            all_kw.extend([("quark", kw) for kw in COMPETITOR_KEYWORDS])

    if "L3" in channels:
        if mode in ("all", "competitor"):
            all_kw.extend([("bilibili", kw) for kw in BILIBILI_KEYWORDS])
            all_kw.extend([("toutiao", kw) for kw in TOUTIAO_KEYWORDS])

    ENGINES = {
        "baidu": search_baidu, "quark": search_quark,
        "bilibili": search_bilibili, "toutiao": search_toutiao,
    }

    all_results = []
    for eng, kw in all_kw:
        fn = ENGINES.get(eng)
        if not fn:
            continue
        results = fn(kw)
        for r in results:
            r["kw_category"] = kw
            r["date"] = date.today().isoformat()
        all_results.extend(results)
        time.sleep(2)

    all_results = dedup_results(all_results)

    industry_list = [r for r in all_results if classify_result(r) == "industry"]
    competitor_list = [r for r in all_results if classify_result(r) == "competitor"]

    log.info("Total: %d (industry=%d, competitor=%d, L1=%d, L3=%d)",
             len(all_results), len(industry_list), len(competitor_list),
             sum(1 for r in all_results if r["channel"] == "L1"),
             sum(1 for r in all_results if r["channel"] == "L3"))

    return {
        "industry": industry_list,
        "competitor": competitor_list,
        "total": len(all_results),
        "date": date.today().isoformat(),
    }


def _sanitize_title(raw: str, max_len: int = 40) -> str:
    """生成洁净、有意义的 Wiki 文档标题片段。

    - 移除控制字符/换行/多余空白
    - 保留中英文、数字、常用标点
    - 在自然断点处截断（句号/逗号/空格）
    - 返回 stripped 文本，最小 4 字符
    """
    if not raw:
        return ""
    s = raw.strip()
    # 移除控制字符和换行
    s = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s)
    # 折叠连续空白
    s = re.sub(r'\s+', ' ', s)
    # 移除 emoji 和特殊符号（保留中英文、数字、基本标点）
    s = re.sub(
        r'[^\w\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef'
        r'.,!?;:()（）【】《》""''、。，！？；：…—+#@&/-]',
        '', s,
    )
    s = s.strip()

    if len(s) <= max_len:
        return s

    # 在自然断点处截断
    truncated = s[:max_len]
    for sep in ['。', '？', '！', '…', '，', '；', '：', ' ', ',', ';', ':']:
        idx = truncated.rfind(sep)
        if idx > max_len * 0.6:
            return truncated[:idx].strip().rstrip('.,!?;:，。！？；：')
    return truncated.strip().rstrip('.,!?;:，。！？；：')


def _make_doc_title(item: dict, total_max: int = 60) -> str:
    """生成 Wiki 文档标题。

    格式: YYYY-MM-DD_[source]_简短主题
    兜底: 使用搜索关键词而非 channel_source_date 泛名
    """
    date_str = item.get("date", date.today().isoformat())
    source = (item.get("source") or "unknown")[:10]
    prefix = f"{date_str}_{source}"
    # 标题片段可用空间
    body_max = total_max - len(prefix) - 1  # -1 for underscore between prefix and body

    title = _sanitize_title(item.get("title", ""), max_len=max(body_max, 20))

    if len(title) < 4:
        # 兜底：用搜索关键词
        kw = item.get("kw_category", "")
        kw_clean = re.sub(r'\s+', '', kw)[:40]
        # 去掉太长太泛的关键词前缀
        kw_clean = re.sub(r'^(贵州旅游|贵州户外|贵州)', '', kw_clean)
        if len(kw_clean) < 4:
            kw_clean = kw_clean or f"采集"
        title = _sanitize_title(kw_clean, max_len=body_max)

    if len(title) < 3:
        title = f"{source}_采集"

    return f"{prefix}_{title}"[:total_max]

def push_to_wiki(results: dict, dry_run: bool = False) -> dict:
    """通过 lark-cli docs +create 创建文档到飞书 Wiki。

    注意：lark-cli docs +fetch 有 bug（始终显示 blocks=0），
    实际内容已正确写入——用 REST API GET /blocks/{id}/children 可验证。
    """
    INDUSTRY_PARENT = WIKI_NODES["industry"]
    COMPETITOR_PARENT = WIKI_NODES["competitor"]

    created = {"industry": 0, "competitor": 0, "errors": 0}

    for category, parent_token, items in [
        ("industry", INDUSTRY_PARENT, results.get("industry", [])),
        ("competitor", COMPETITOR_PARENT, results.get("competitor", [])),
    ]:
        for item in items:
            doc_title = _make_doc_title(item)

            if dry_run:
                log.info("  [DRY-RUN] %s → %s", doc_title[:60], category)
                created[category] += 1
                continue

            try:
                ch = item.get("channel", "?")
                src = item.get("source", "?")
                extra = ""
                if item.get("author"):
                    extra += f"\n\n**UP主/作者:** {item['author']}"
                if item.get("meta"):
                    extra += f"\n\n**播放/时间:** {item['meta']}"

                orig_title = item.get("title", doc_title)
                content_md = (
                    f"# {orig_title}\n\n"
                    f"**通道:** {ch} | **来源:** {src}{extra}\n\n"
                    f"**原文链接:** {item['url']}\n\n"
                    f"**采集日期:** {item['date']}\n\n"
                    f"**搜索关键词:** {item.get('kw_category', '')}"
                )
                cmd = [
                    "lark-cli", "docs", "+create",
                    "--wiki-node", parent_token,
                    "--title", doc_title,
                    "--markdown", content_md,
                    "--as", "bot",
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if proc.returncode == 0:
                    created[category] += 1
                    log.info("  ✓ %s", doc_title[:50])
                else:
                    created["errors"] += 1
                    log.warning("  ✗ %s — %s", doc_title[:50], proc.stderr.strip()[:100])
            except Exception as e:
                created["errors"] += 1
                log.exception("  ✗ %s", doc_title[:50])
            time.sleep(1.5)

    return created


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    p = argparse.ArgumentParser(description="agent-browser multi-engine/platform collector")
    p.add_argument("--mode", default="all", choices=["all", "industry", "competitor"])
    p.add_argument("--channel", default="L1,L3",
                   help="comma-separated: L1(百度+夸克), L3(B站+头条)")
    p.add_argument("--push", action="store_true", help="Push to Feishu Wiki")
    p.add_argument("--dry-run", action="store_true", help="Dry-run push (no actual write)")
    p.add_argument("--json", action="store_true", help="Output JSON to stdout only")
    args = p.parse_args()

    if not check_agent_browser():
        log.error("agent-browser not available.")
        sys.exit(1)

    channels = [c.strip() for c in args.channel.split(",") if c.strip()]

    results = collect(args.mode, channels=channels)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        sys.exit(0)

    push_stats = None
    if args.push or args.dry_run:
        push_stats = push_to_wiki(results, dry_run=args.dry_run)

    l1_count = sum(1 for r in results.get("industry", []) + results.get("competitor", []) if r.get("channel") == "L1")
    l3_bili = sum(1 for r in results.get("industry", []) + results.get("competitor", []) if r.get("source") == "bilibili")
    l3_tt = sum(1 for r in results.get("industry", []) + results.get("competitor", []) if r.get("source") == "toutiao")

    print(f"\n{'='*50}")
    print(f"browser_collector — {results['date']} (通道: {','.join(channels)})")
    print(f"  L1 百度+夸克: {l1_count} 条")
    print(f"  L3 B站: {l3_bili}  | 头条: {l3_tt}")
    print(f"  行业: {len(results['industry'])} | 竞品: {len(results['competitor'])} | 总计: {results['total']}")
    if push_stats:
        print(f"\n推送: 行业{push_stats['industry']} 竞品{push_stats['competitor']} 失败{push_stats['errors']}")
    print(f"{'='*50}")
