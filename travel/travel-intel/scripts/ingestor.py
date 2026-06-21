#!/usr/bin/env python3
"""入库引擎 — 采集结果 → 飞书文档

分类路由: 竞品关键词→EAMYw1CPoi / 行业→V0Lhwl7KYi
命名: YYYY-MM-DD_类型_主题

Usage:
    python3 ingestor.py --input collector_output.json [--dry-run] [--delay 3]

Note: Feishu API rate-limits ~10 creates/minute (99991400). Use --delay 3 (default)
to avoid hitting the limit.
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
import shutil

log = logging.getLogger(__name__)

COMPETITOR_KW = re.compile(
    r"探洞|洞穴|溶洞|绳降|天坑|速降|平塘|大石围|"
    r"桨板|SUP|竞品|新品上线|价格调整|营销活动|促销",
    re.IGNORECASE,
)

COMPETITOR_NODE = "EAMYw1CPoipVWtkObbtcR2oDnNc"
INDUSTRY_NODE = "V0Lhwl7KYiYDDk1vCncv2GhnYf"
DEFAULT_DELAY = 3   # seconds between API calls to avoid rate limit 99991400
TIMEOUT = 60       # seconds for lark-cli subprocess
LARK_CLI = shutil.which("lark-cli") or "/home/aorus/.local/bin/lark-cli"


def classify(text: str) -> str:
    if COMPETITOR_KW.search(text):
        return "competitor"
    return "industry"


def node_for_class(cls: str) -> str:
    return COMPETITOR_NODE if cls == "competitor" else INDUSTRY_NODE


def build_xml(item: dict, cls: str, date_str: str) -> str:
    title = item.get("title", "无标题")[:80]
    url = item.get("url", "")
    snippet = item.get("snippet", "")[:300]
    source = item.get("source", "未知")
    trust = item.get("trust", "medium")
    tlabel = "竞品" if cls == "competitor" else "行业"

    # Escape text for XML — preserve existing HTML entities
    title_esc = re.sub(r'&(?!\w+;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', title)
    title_esc = title_esc.replace("<", "&lt;").replace(">", "&gt;")
    snippet_esc = re.sub(r'&(?!\w+;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', snippet)
    snippet_esc = snippet_esc.replace("<", "&lt;").replace(">", "&gt;")

    return f'''<title>{date_str}_{tlabel}_{title_esc[:40]}</title>
<callout emoji="📄" background-color="light-blue" border-color="blue">
  <p><b>{title_esc}</b></p>
  <p>来源：{source} ｜ 采集日期：{date_str} ｜ 可信度：{trust}</p>
  <p><a href="{url}">查看原文</a></p>
</callout>
<p>{snippet_esc}</p>
<hr/>'''


def ingest(items: list[dict], date_str: str = "", dry_run: bool = False, delay: float = DEFAULT_DELAY) -> dict:
    if not date_str:
        date_str = time.strftime("%Y-%m-%d")

    stats = {"total": len(items), "created": 0, "skipped": 0, "failed": 0}

    for i, item in enumerate(items):
        combined = (item.get("title", "") + " " + item.get("snippet", ""))[:200]
        cls = classify(combined)
        node = node_for_class(cls)

        xml = build_xml(item, cls, date_str)
        xml_file = f"/tmp/intel_ingest_{int(time.time()*1000000)}.xml"

        try:
            with open(xml_file, "w", encoding="utf-8") as f:
                f.write(xml)

            if dry_run:
                log.info("[DRY RUN] %s → %s", item.get("title", "")[:50], cls)
                stats["created"] += 1
                os.unlink(xml_file)
                continue

            result = subprocess.run(
                [LARK_CLI, "docs", "+create", "--api-version", "v2",
                 "--doc-format", "xml", "--content", f"@{os.path.basename(xml_file)}",
                 "--parent-token", node, "--as", "bot"],
                capture_output=True, text=True, timeout=TIMEOUT,
                cwd="/tmp",
            )

            if result.returncode == 0 and result.stdout.strip():
                # Parse JSON from stdout — may have status lines before JSON
                lines = result.stdout.split("\n")
                json_start = next((i for i, l in enumerate(lines) if l.strip().startswith("{")), None)
                if json_start is not None:
                    resp = json.loads("\n".join(lines[json_start:]))
                else:
                    resp = {"ok": False, "error": "no JSON in output"}
                if resp.get("ok"):
                    stats["created"] += 1
                    log.info("created: %s", item.get("title", "")[:50])
                else:
                    log.warning("API error: %s", result.stdout[:150])
                    stats["failed"] += 1
            else:
                log.warning("CLI error: %s", result.stderr[:150])
                stats["failed"] += 1

        except Exception as e:
            log.exception("ingest failed: %s", e)
            stats["failed"] += 1
        finally:
            if os.path.exists(xml_file):
                os.unlink(xml_file)

        # Rate-limit protection: delay between API calls
        if i < len(items) - 1 and delay > 0 and not dry_run:
            time.sleep(delay)

    log.info("ingest done: %s", json.dumps(stats, ensure_ascii=False))
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="")
    p.add_argument("--stdin", action="store_true")
    p.add_argument("--date", default="")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--delay", type=float, default=DEFAULT_DELAY,
                   help="Seconds between API calls (default: 3)")
    args = p.parse_args()

    if args.stdin:
        items = json.loads(sys.stdin.read())
    elif args.input:
        with open(args.input) as f:
            items = json.load(f)
    else:
        sys.exit(1)

    stats = ingest(items, args.date, args.dry_run, args.delay)
    print(json.dumps(stats, ensure_ascii=False))
