#!/usr/bin/env python3
"""查询引擎 — 两级回退：Wiki搜索 → 过期降权 → 未命中 → web_search

Usage:
    python3 querier.py --query "黄果树门票"
"""

import argparse
import datetime
import json
import logging
import os
import re
import subprocess
import sys
import yaml

log = logging.getLogger(__name__)
RULES_FILE = os.path.join(os.path.dirname(__file__), "..", "references", "expiry-rules.yaml")
WIKI_NODES = ["MYQtwtPEOiu4nZkma9NcEEQ3n6V", "E7xyw9pSfibEEckZVEIcU5AynJs"]
SPACE_ID = "7643710721485753535"
TZ = datetime.timezone(datetime.timedelta(hours=8))
TIMEOUT = 20
TITLE_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_")
WEIGHT_THRESHOLD = 0.3  # 低于30%不返回


def load_rules():
    with open(RULES_FILE) as f:
        return yaml.safe_load().get("rules", [])


def wiki_search(query: str) -> list[dict]:
    """搜索 Wiki 知识库"""
    docs = []
    # Try lark-cli docs +search first
    try:
        result = subprocess.run(
            ["lark-cli", "docs", "+search", "--query", query, "--as", "user"],
            capture_output=True, text=True, timeout=TIMEOUT,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            items = data.get("data", {}).get("items", [])
            for item in items:
                docs.append({
                    "title": item.get("title", ""),
                    "obj_token": item.get("obj_token", ""),
                    "url": item.get("url", ""),
                    "source": "知识库",
                })
    except Exception:
        pass

    # Fallback: node-list + title match
    if not docs:
        for node in WIKI_NODES:
            try:
                r = subprocess.run(
                    ["lark-cli", "wiki", "+node-list", "--space-id", SPACE_ID,
                     "--parent-node-token", node, "--as", "bot"],
                    capture_output=True, text=True, timeout=TIMEOUT,
                )
                if r.returncode == 0:
                    data = json.loads(r.stdout)
                    nodes = data.get("data", {}).get("nodes", [])
                    for n in nodes:
                        title = n.get("title", "")
                        if query.lower() in title.lower():
                            docs.append({
                                "title": title,
                                "obj_token": n.get("obj_token", ""),
                                "source": "知识库",
                            })
            except Exception:
                continue

    return docs


def apply_expiry(docs: list[dict]) -> list[dict]:
    """对搜索结果应用过期规则，返回带权重的结果"""
    rules = load_rules()
    today = datetime.datetime.now(TZ).date()
    results = []

    for doc in docs:
        m = TITLE_DATE_RE.match(doc.get("title", ""))
        if not m:
            doc["weight"] = 1.0
            doc["status"] = "未知时效"
            results.append(doc)
            continue

        doc_date = datetime.date.fromisoformat(m.group(1))
        age = (today - doc_date).days
        weight = 1.0
        status = "有效"
        matched_rule = None

        for rule in rules:
            rd = rule.get("days")
            if rd and age > rd:
                if rule.get("weight", 0) < weight:
                    weight = rule["weight"]
                    status = rule.get("label", "已过期")
                    matched_rule = rule

        doc["weight"] = weight
        doc["status"] = status
        doc["age_days"] = age

        if weight >= WEIGHT_THRESHOLD:
            results.append(doc)

    return sorted(results, key=lambda x: x.get("weight", 0), reverse=True)


def query(query_str: str) -> dict:
    """主查询入口"""
    # Step 1: Wiki search
    docs = wiki_search(query_str)
    log.info("wiki search: %d results", len(docs))

    # Step 2: Apply expiry
    if docs:
        valid = apply_expiry(docs)
        if valid:
            return {
                "source": "知识库",
                "total": len(valid),
                "results": valid,
                "fallback": False,
            }

    # Step 3: Fallback — return flag for agent to web_search
    return {
        "source": "互联网（实时搜索）",
        "total": 0,
        "results": [],
        "fallback": True,
        "fallback_query": query_str,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    args = p.parse_args()

    result = query(args.query)
    print(json.dumps(result, ensure_ascii=False, indent=2))
