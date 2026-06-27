#!/usr/bin/env python3
"""hotlist_collector — L1b 社交热榜扫描 (微博热搜 + 知乎热榜) → 飞书 Wiki

依赖 opencli (Chrome Extension + Daemon)，WSL 本地运行。
采集微博热搜和知乎热榜，过滤旅游相关话题，推送到行业资讯 / 竞品动态 Wiki 节点。

属于 L1 通道的补充——L1a(百度+夸克通用搜索) + L1b(社交热榜扫描) 共同构成本地采集层。

Usage:
    python3 hotlist_collector.py                          # 采集+过滤，输出 JSON
    python3 hotlist_collector.py --push                   # 采集+过滤+推送到 Wiki
    python3 hotlist_collector.py --push --dry-run         # 模拟推送
    python3 hotlist_collector.py --weibo-only             # 仅微博
    python3 hotlist_collector.py --zhihu-only             # 仅知乎
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import date

log = logging.getLogger(__name__)

# ── opencli 路径 ──────────────────────────────────────────
OPENCLI = os.path.expanduser("~/.hermes/node/bin/opencli")

# ── 飞书 Wiki 节点 ────────────────────────────────────────
WIKI_NODES = {
    "industry": "V0Lhwl7KYiWYDDk1vCncv2GhnYf",
    "competitor": "EAMYw1CPoipVWtkObbtcR2oDnNc",
}

# ── 旅游相关关键词过滤器 ──────────────────────────────────
# 两层：贵州直接相关 (高置信度) + 旅游/户外泛类 (趋势信号)
FILTER_KW_GUIZHOU = (
    r"贵州|黔西南|黔南|黔东南|黔中|贵阳|遵义|安顺|毕节|铜仁|六盘水|"
    r"兴义|安龙|贞丰|晴隆|册亨|望谟|"
    r"万峰林|马岭河|黄果树|荔波|梵净山|西江|镇远|肇兴|百里杜鹃|织金洞|龙宫|天眼"
)
FILTER_KW_TRAVEL = (
    r"旅游|旅行|景区|景点|出游|出游季|暑期游|五一|十一|国庆|春节|假期|"
    r"探洞|洞穴|溶洞|天坑|桨板|SUP|漂流|溯溪|瀑降|溪降|"
    r"户外|徒步|登山|攀岩|攀冰|骑行|越野|露营|营地|野营|"
    r"避暑|康养|旅居|度假|民宿|温泉|赏花|观鸟|研学|亲子游|团建|"
    r"山地|峡谷|瀑布|森林|草原|湖泊|喀斯特|丹霞|"
    r"体育旅游|体旅|文旅|非遗"
)

FILTER_RE = re.compile(FILTER_KW_GUIZHOU + "|" + FILTER_KW_TRAVEL)
GUIZHOU_RE = re.compile(FILTER_KW_GUIZHOU)

# ── 噪音过滤 ──────────────────────────────────────────────
NOISE_PATTERNS = [
    r"彩票|中奖|诈骗|车祸|事故|火灾|地震|暴雨|受灾",
    r"房价|楼市|股票|基金|币",
]
NOISE_RE = re.compile("|".join(NOISE_PATTERNS))


def check_opencli() -> bool:
    """检查 opencli 是否可用（二进制 + daemon）"""
    if not os.path.exists(OPENCLI):
        log.error("opencli not found at %s", OPENCLI)
        return False
    try:
        proc = subprocess.run(
            [OPENCLI, "doctor"],
            capture_output=True, text=True, timeout=10,
            env={**os.environ, "PATH": f"{os.path.expanduser('~/.hermes/node/bin')}:{os.environ.get('PATH', '')}"},
        )
        return proc.returncode == 0
    except Exception:
        return False


def _run_opencli(args: list[str], timeout: int = 30) -> list[dict]:
    """Run opencli command and parse JSON output"""
    env = {
        **os.environ,
        "PATH": f"{os.path.expanduser('~/.hermes/node/bin')}:{os.environ.get('PATH', '')}",
    }
    try:
        proc = subprocess.run(
            [OPENCLI] + args,
            capture_output=True, text=True, timeout=timeout, env=env,
        )
        if proc.returncode != 0:
            log.warning("opencli %s failed (exit=%d): %s", args[0], proc.returncode, proc.stderr[:200])
            return []
        raw = proc.stdout.strip()
        if not raw:
            return []
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        return []
    except subprocess.TimeoutExpired:
        log.warning("opencli %s timeout", args[0])
        return []
    except json.JSONDecodeError as e:
        log.warning("opencli %s JSON parse error: %s", args[0], e)
        return []
    except Exception as e:
        log.exception("opencli %s error: %s", args[0], e)
        return []


def fetch_weibo_hot() -> list[dict]:
    """获取微博热搜"""
    raw = _run_opencli(["weibo", "hot", "-f", "json"])
    results = []
    for item in raw:
        word = (item.get("word") or "").strip()
        if not word:
            continue
        results.append({
            "title": word,
            "url": item.get("url", ""),
            "source": "weibo_hot",
            "channel": "L1b",
            "heat": item.get("hot_value", 0),
            "rank": item.get("rank", 0),
            "category": item.get("category", ""),
        })
    log.info("[微博热搜] fetched %d items", len(results))
    return results


def fetch_zhihu_hot() -> list[dict]:
    """获取知乎热榜"""
    raw = _run_opencli(["zhihu", "hot", "-f", "json", "--limit", "50"])
    results = []
    for item in raw:
        title = (item.get("title") or "").strip()
        if not title:
            continue
        # Parse heat value (e.g. "1766万热度" → 17660000)
        heat_str = item.get("heat", "0")
        heat_num = 0
        heat_match = re.search(r"([\d.]+)\s*万", heat_str)
        if heat_match:
            heat_num = int(float(heat_match.group(1)) * 10000)
        else:
            heat_match = re.search(r"(\d+)", str(heat_str))
            if heat_match:
                heat_num = int(heat_match.group(1))

        results.append({
            "title": title,
            "url": item.get("link", ""),
            "source": "zhihu_hot",
            "channel": "L1b",
            "heat": heat_num,
            "rank": 0,  # zhihu hot doesn't have rank in tophub data
            "category": "",
        })
    log.info("[知乎热榜] fetched %d items", len(results))
    return results


def is_guizhou_direct(item: dict) -> bool:
    """是否贵州直接相关"""
    title = item.get("title", "")
    return bool(GUIZHOU_RE.search(title))


def filter_travel(items: list[dict]) -> tuple[list[dict], list[dict]]:
    """过滤旅游相关话题，返回 (贵州直接相关, 泛旅游相关)"""
    guizhou_items = []
    travel_items = []

    for item in items:
        title = item.get("title", "")
        if not title or len(title) < 3:
            continue
        if NOISE_RE.search(title):
            continue
        if not FILTER_RE.search(title):
            continue

        if is_guizhou_direct(item):
            guizhou_items.append(item)
        else:
            travel_items.append(item)

    # Dedup within each list
    def _dedup(items):
        seen = set()
        result = []
        for item in items:
            norm = item["title"].strip()
            if norm not in seen:
                seen.add(norm)
                result.append(item)
        return result

    return _dedup(guizhou_items), _dedup(travel_items)


def classify_social(item: dict) -> str:
    """分类：贵州直接→competitor (高关注)，泛旅游→industry"""
    if is_guizhou_direct(item):
        return "competitor"
    return "industry"


def _sanitize_title(raw: str, max_len: int = 40) -> str:
    """生成洁净、有意义的 Wiki 文档标题片段。"""
    if not raw:
        return ""
    s = raw.strip()
    s = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(
        r'[^\w\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef'
        r'.,!?;:()（）【】《》""''、。，！？；：…—+#@&/-]',
        '', s,
    )
    s = s.strip()
    if len(s) <= max_len:
        return s
    truncated = s[:max_len]
    for sep in ['。', '？', '！', '…', '，', '；', '：', ' ', ',', ';', ':']:
        idx = truncated.rfind(sep)
        if idx > max_len * 0.6:
            return truncated[:idx].strip().rstrip('.,!?;:，。！？；：')
    return truncated.strip().rstrip('.,!?;:，。！？；：')


def _make_doc_title(item: dict, total_max: int = 60) -> str:
    """生成 Wiki 文档标题。格式: YYYY-MM-DD_[source]_简短主题"""
    date_str = item.get("date", date.today().isoformat())
    source = (item.get("source") or "unknown")[:10]
    prefix = f"{date_str}_{source}"
    body_max = total_max - len(prefix) - 1
    title = _sanitize_title(item.get("title", ""), max_len=max(body_max, 20))
    if len(title) < 4:
        kw = item.get("kw_category", "")
        kw_clean = re.sub(r'\s+', '', kw)[:40]
        # 仅去除已知前缀 social_hotlist_，保留有意义的分类词
        kw_clean = re.sub(r'^social_hotlist_', '', kw_clean)
        if len(kw_clean) < 4:
            kw_clean = f"热榜_{kw_clean}" if kw_clean else "热榜采集"
        title = _sanitize_title(kw_clean, max_len=body_max)
    if len(title) < 3:
        title = f"{source}_采集"
    return f"{prefix}_{title}"[:total_max]


def push_to_wiki(items: list[dict], dry_run: bool = False) -> dict:
    """通过 lark-cli docs +create 创建文档到飞书 Wiki。

    原使用 lark-cli doc +create（无效命令），已修正为 docs +create --wiki-node。
    lark-cli docs +fetch 有 bug（始终 blocks=0），实际内容用 REST API 可验证。
    """
    created = {"industry": 0, "competitor": 0, "errors": 0}

    for item in items:
        category = classify_social(item)
        parent_token = WIKI_NODES[category]
        doc_title = _make_doc_title(item)

        orig_title = item.get("title", doc_title)
        heat_display = f"热度:{item.get('heat', '?')}" if item.get('heat') else ""
        content_lines = [
            f"# {orig_title}",
            "",
            f"来源：{item['source']} 热榜",
            f"频道：{item['channel']}",
            f"{heat_display}",
            "",
            f"原文链接：{item.get('url', '')}",
        ]
        if item.get("category"):
            content_lines.insert(3, f"分类：{item['category']}")
        content_md = "\n".join(content_lines)

        if dry_run:
            log.info("[DRY-RUN] would create doc '%s' under %s", doc_title, category)
            created[category] += 1
            continue

        try:
            proc = subprocess.run(
                ["lark-cli", "docs", "+create",
                 "--wiki-node", parent_token,
                 "--title", doc_title,
                 "--markdown", content_md,
                 "--as", "bot"],
                capture_output=True, text=True, timeout=30,
            )
            if proc.returncode == 0:
                log.info("  ✓ created: %s", doc_title[:50])
                created[category] += 1
            else:
                log.warning("  ✗ create failed: %s (exit=%d)", doc_title[:50], proc.returncode)
                created["errors"] += 1
        except subprocess.TimeoutExpired:
            log.warning("  ✗ timeout: %s", doc_title[:50])
            created["errors"] += 1
        except Exception as e:
            log.exception("  ✗ error: %s: %s", doc_title[:50], e)
            created["errors"] += 1

        time.sleep(3)

    return created


def collect(platforms: list[str] = None) -> dict:
    """主采集函数"""
    if platforms is None:
        platforms = ["weibo", "zhihu"]

    all_items = []

    if "weibo" in platforms:
        try:
            all_items.extend(fetch_weibo_hot())
        except Exception as e:
            log.exception("weibo hot fetch error: %s", e)

    if "zhihu" in platforms:
        try:
            all_items.extend(fetch_zhihu_hot())
        except Exception as e:
            log.exception("zhihu hot fetch error: %s", e)

    guizhou, travel = filter_travel(all_items)

    log.info(
        "Hotlist total=%d, 贵州直接=%d, 泛旅游=%d",
        len(all_items), len(guizhou), len(travel),
    )

    # 贵州直接 → competitor (竞品动态，高关注)
    # 泛旅游 → industry (行业资讯，趋势信号)
    for item in guizhou:
        item["date"] = date.today().isoformat()
        item["kw_category"] = "social_hotlist_guizhou"
    for item in travel:
        item["date"] = date.today().isoformat()
        item["kw_category"] = "social_hotlist_travel"

    return {
        "guizhou_direct": guizhou,
        "travel_trend": travel,
        "total_raw": len(all_items),
        "total_filtered": len(guizhou) + len(travel),
        "date": date.today().isoformat(),
    }


# ── CLI ────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    p = argparse.ArgumentParser(description="L1b 社交热榜扫描 (微博+知乎)")
    p.add_argument("--weibo-only", action="store_true", help="仅微博热搜")
    p.add_argument("--zhihu-only", action="store_true", help="仅知乎热榜")
    p.add_argument("--push", action="store_true", help="推送到飞书 Wiki")
    p.add_argument("--dry-run", action="store_true", help="模拟推送，不实际创建文档")

    args = p.parse_args()

    # 确定平台
    if args.weibo_only and args.zhihu_only:
        platforms = ["weibo", "zhihu"]
    elif args.weibo_only:
        platforms = ["weibo"]
    elif args.zhihu_only:
        platforms = ["zhihu"]
    else:
        platforms = ["weibo", "zhihu"]

    # 检查 opencli
    if not check_opencli():
        log.error("opencli not available — is Chrome + daemon running?")
        sys.exit(1)

    # 采集
    results = collect(platforms)

    # 输出摘要
    print(json.dumps({
        "status": "ok",
        "date": results["date"],
        "raw_count": results["total_raw"],
        "filtered_count": results["total_filtered"],
        "guizhou_direct": [
            {"title": item["title"][:80], "heat": item.get("heat", 0), "source": item["source"]}
            for item in results["guizhou_direct"]
        ],
        "travel_trend": [
            {"title": item["title"][:80], "heat": item.get("heat", 0), "source": item["source"]}
            for item in results["travel_trend"]
        ],
    }, ensure_ascii=False, indent=2))

    # 推送
    if args.push:
        all_filtered = results["guizhou_direct"] + results["travel_trend"]
        if not all_filtered:
            log.info("No travel-related items to push")
        else:
            push_result = push_to_wiki(all_filtered, dry_run=args.dry_run)
            print(json.dumps({"push_result": push_result}, ensure_ascii=False))
