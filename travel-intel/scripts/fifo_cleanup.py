#!/usr/bin/env python3
"""
FIFO 清理：每日采集入库后，删除等量的最早文档，保持节点不超 2000 上限。

规则：采集入库 N 条 → 删除最早 N 条（按标题日期 YYYY-MM-DD 排序）。
仅在 N > 0 时执行。

Usage:
    python3 fifo_cleanup.py <count>
    python3 fifo_cleanup.py 45   # 删除最早 45 篇
"""
import subprocess, json, os, sys, re, time

NPM_PATH = r"C:\Users\Aorus\AppData\Roaming\npm"
ENV = os.environ.copy()
ENV["PATH"] = f"{NPM_PATH};{ENV.get('PATH', '')}"
LARK_CLI = r"C:\Users\Aorus\AppData\Roaming\npm\lark-cli.cmd"

SPACE_ID = "7643710721485753535"
NODE_TOKEN = "UF7Cw5w2WiHGfjkKVvBcxj8Hnib"  # 咨询洞察 一级节点
PAGE_LIMIT = 40  # page-limit for node-list (40×50=2000, covers full node)
API_TIMEOUT = 60
DELETE_DELAY = 1.0  # seconds between deletes (rate-limit safety)


def list_docs_by_date():
    """List all docs under 咨询洞察, return sorted by date (oldest first)."""
    cmd = [
        LARK_CLI, "wiki", "+node-list",
        "--space-id", SPACE_ID,
        "--parent-node-token", NODE_TOKEN,
        "--page-all", f"--page-limit={PAGE_LIMIT}",
        "--as", "bot",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=API_TIMEOUT, env=ENV)
    if r.returncode != 0:
        print(f"ERROR: node-list failed RC={r.returncode} stderr={r.stderr[:200]}")
        return []

    try:
        data = json.loads(r.stdout.strip())
    except json.JSONDecodeError:
        print(f"ERROR: node-list returned non-JSON: {r.stdout[:200]}")
        return []

    nodes = data.get("data", {}).get("nodes", [])
    print(f"node-list returned {len(nodes)} nodes")

    # Parse date from title prefix: YYYY-MM-DD_source_topic
    dated = []
    for node in nodes:
        title = node.get("title", "")
        m = re.match(r"(\d{4}-\d{2}-\d{2})", title)
        if m:
            dated.append((m.group(1), node))
        else:
            # No date prefix → treat as very old (sort first to clean up)
            dated.append(("0000-00-00", node))

    dated.sort(key=lambda x: x[0])  # oldest first
    return dated


def trash_node(node_token):
    """Move a wiki node to trash via lark-cli wiki +node-delete.

    2026-07-04 fix: raw API DELETE /open-apis/wiki/v2/spaces/{id}/nodes/{nt} returns 404.
    Use the typed `wiki +node-delete` command instead.
    """
    cmd = [
        LARK_CLI, "wiki", "+node-delete",
        "--node-token", node_token,
        "--obj-type", "wiki",
        "--yes",
        "--as", "bot",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=ENV)
    raw = r.stdout.strip() or r.stderr.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return False, f"non-JSON: {raw[:100]}"

    # lark-cli typed commands (e.g. wiki +node-delete) wrap success in {"ok": true, ...}
    # lark-cli api uses raw Feishu {"code": 0, ...} format. Accept both.
    if data.get("ok") is True:
        return True, "ok"
    code = data.get("code", -1)
    if code == 0:
        return True, "ok"
    return False, f"code={code} msg={data.get('msg', '?')[:80]}"


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if count <= 0:
        print("FIFO cleanup: count=0, nothing to do")
        return

    print(f"=== FIFO CLEANUP ===")
    print(f"Target: delete {count} oldest docs from 咨询洞察")

    docs = list_docs_by_date()
    if not docs:
        print("ERROR: no docs found or node-list failed — aborting cleanup")
        sys.exit(1)

    print(f"Total docs with date prefix: {len(docs)}")

    if len(docs) <= count:
        print(f"WARNING: only {len(docs)} docs, trimming to {len(docs) - 10} (keep 10 minimum)")
        count = max(0, len(docs) - 10)

    if count <= 0:
        print("Nothing to delete after safety trim")
        return

    to_delete = docs[:count]
    oldest_date = to_delete[0][0]
    newest_delete_date = to_delete[-1][0]
    print(f"Deleting {len(to_delete)} docs ({oldest_date} → {newest_delete_date})")

    deleted = 0
    failed = 0
    for i, (date_str, node) in enumerate(to_delete):
        nt = node.get("node_token", "")
        title = node.get("title", "?")[:60]
        if not nt:
            print(f"  ⚠️  [{i+1}/{len(to_delete)}] {date_str}: {title} — no node_token, skip")
            failed += 1
            continue

        ok, detail = trash_node(nt)
        if ok:
            deleted += 1
            if deleted % 10 == 0 or i == len(to_delete) - 1:
                print(f"  ✅ [{deleted}/{len(to_delete)}] {date_str}: {title}")
        else:
            failed += 1
            print(f"  ❌ [{i+1}/{len(to_delete)}] {date_str}: {title} — {detail}")

        time.sleep(DELETE_DELAY)

    print(f"\n=== CLEANUP SUMMARY ===")
    print(f"Deleted: {deleted}/{len(to_delete)}  Failed: {failed}")
    print(f"Estimated node size after: {len(docs) - deleted}")


if __name__ == "__main__":
    main()
