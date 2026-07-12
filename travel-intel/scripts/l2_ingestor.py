#!/usr/bin/env python3
"""
Simplified L2 Ingestor — create Wiki skeleton docs for curated L2 results.
Batches of 8 with 12s cooling between batches to avoid 99991400 rate limits.

Replaces the broken scripts/ingestor.py that returns 3380002 for all items.
See SKILL.md pitfalls: "ingestor.py 全量 3380002 故障 (2026-06-03)"

2026-06-04: Switched from sub-classification tokens (both stale/3380002) to
first-level token UF7Cw5w2WiHGfjkKVvBcxj8Hnib (咨询洞察). 69/69 confirmed working.

Usage:
    python3 l2_ingestor.py [date_str] [input_file]
"""
import subprocess, json, os, sys, time, re

# Force unbuffered output for background process visibility (2026-06-05)
sys.stdout.reconfigure(line_buffering=True)

NPM_PATH = r"C:\Users\Aorus\AppData\Roaming\npm"
LOCAL_BIN = os.path.expanduser("~/.local/bin")
ENV = os.environ.copy()
# Prepend both candidate paths (npm is the actual location on this Windows host)
existing = ENV.get("PATH", "")
ENV["PATH"] = ";".join([NPM_PATH, LOCAL_BIN, existing]) if os.name == "nt" else f"{NPM_PATH}:{LOCAL_BIN}:{existing}"

COMPETITOR_KW = re.compile(
    r"探洞|洞穴|溶洞|绳降|天坑|速降|平塘|大石围|"
    r"桨板|SUP|竞品|新品上线|价格调整|营销活动|促销",
    re.IGNORECASE,
)
COMPETITOR_NODE = "E7xyw9pSfibEEckZVEIcU5AynJs"  # ⚠️ stale 2026-06-04 (3380002)
INDUSTRY_NODE = "MYQtwtPEOiu4nZkma9NcEEQ3n6V"    # ⚠️ stale 2026-06-04 (3380002)
FALLBACK_NODE = "UF7Cw5w2WiHGfjkKVvBcxj8Hnib"    # ✅ 一级分类 咨询洞察 (confirmed working)
# Use FALLBACK_NODE as primary until sub-tokens are refreshed
DEFAULT_NODE = FALLBACK_NODE
WIKI_SPACE_ID = "7643710721485753535"   # 贵州之客知识库 space_id
BATCH_SIZE = 6  # reduced from 8 (2026-06-05: 17/64 rate-limited with 8)
COOL_DOWN = 15  # increased from 12s (first-after-cooldown still vulnerable at 12s)
ITEM_DELAY = 5  # seconds between individual API calls (was 4s)
RETRY_DELAY = 15  # seconds to wait before retrying a 99991400 failure


def sanitize_for_xml(text):
    """Basic XML text escaping."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    return text


def make_doc_title(item, cls, date_str):
    """Create doc title: YYYY-MM-DD_source_topic (max 60 chars)."""
    title = item.get("title", "无标题")
    source = item.get("source", "未知")
    source_short = {
        "品橙旅游": "pinchain",
        "迈点文旅": "meadin_wl",
        "迈点景区": "meadin_jq",
        "闻旅": "wenlv",
    }.get(source, "other")

    topic = re.sub(r'[「」《》【】""'']', '', title)
    topic = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\n\r\t]', '', topic)

    prefix = f"{date_str}_{source_short}_"
    max_topic = 60 - len(prefix)
    if len(topic) > max_topic:
        topic = topic[:max_topic]
        for sep in ['。', '，', '、', ' ', ',']:
            idx = topic.rfind(sep)
            if idx > max_topic * 0.6:
                topic = topic[:idx]
                break

    return f"{prefix}{topic}"[:60]


def build_xml(item, cls, date_str):
    title = item.get("title", "无标题")
    url = item.get("url", "")
    source = item.get("source", "未知")

    doc_title = make_doc_title(item, cls, date_str)
    title_safe = sanitize_for_xml(title)
    doc_title_safe = sanitize_for_xml(doc_title)

    bookmark = f'<bookmark name="原文链接" href="{url}"/>' if url else ""

    xml = f'<title>{doc_title_safe}</title>\n'
    xml += f'<callout emoji="📄" background-color="light-blue" border-color="blue">\n'
    xml += f'  <p><b>{title_safe}</b></p>\n'
    xml += f'  <p>来源：{source} ｜ 采集日期：{date_str}</p>\n'
    if bookmark:
        xml += f'  {bookmark}\n'
    xml += '</callout>\n<hr/>'
    return xml


MAX_RETRIES = 3  # retry on 99991400 rate-limit errors

# Use Windows TEMP so both Python os.open and lark-cli (Node) see the same dir
# (Python /tmp → C:\tmp; Node /tmp → C:\Users\<u>\AppData\Local\Temp — mismatch)
TEMP_DIR = os.environ.get("TEMP") or os.environ.get("TMP") or r"C:\Users\Aorus\AppData\Local\Temp"

# On Windows, lark-cli (no ext) is a POSIX shell script that CreateProcess can't exec.
# Use lark-cli.cmd explicitly so subprocess.run works regardless of cwd.
LARK_CLI = r"C:\Users\Aorus\AppData\Roaming\npm\lark-cli.cmd"

def ingest_one(item, cls, node, date_str):
    xml = build_xml(item, cls, date_str)
    xml_file = os.path.join(TEMP_DIR, f"l2_{int(time.time()*1000000)}.xml")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with open(xml_file, "w", encoding="utf-8") as f:
                f.write(xml)

            basename = os.path.basename(xml_file)
            cmd = [LARK_CLI, "docs", "+create", "--api-version", "v2",
                   "--doc-format", "xml", "--content", f"@{basename}",
                   "--parent-token", node, "--as", "bot"]

            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                              cwd=TEMP_DIR, env=ENV)

            if r.returncode != 0:
                return False, f"RC={r.returncode} stderr={r.stderr[:200]}"

            data = json.loads(r.stdout.strip())
            if data.get("ok"):
                doc_id = data.get("data", {}).get("document", {}).get("document_id", "?")
                
                # Step 2: Move into wiki tree (docs+create --parent-token only sets Drive parent, NOT wiki node)
                move_cmd = [LARK_CLI, "wiki", "+move",
                           "--obj-token", doc_id, "--obj-type", "docx",
                           "--target-parent-token", node,
                           "--target-space-id", WIKI_SPACE_ID,
                           "--as", "bot"]
                r2 = subprocess.run(move_cmd, capture_output=True, text=True, timeout=30,
                                   cwd=TEMP_DIR, env=ENV)
                if r2.returncode != 0:
                    return False, f"doc_id={doc_id} wiki+move RC={r2.returncode}"
                move_data = json.loads(r2.stdout.strip())
                if move_data.get("ok"):
                    return True, f"doc_id={doc_id} wiki_node={move_data.get('data',{}).get('node_token','?')}"
                else:
                    move_err = move_data.get("error", {})
                    return False, f"doc_id={doc_id} wiki+move: code={move_err.get('code')} {move_err.get('message','')[:80]}"
            else:
                err = data.get("error", {})
                code = err.get('code', 0)
                msg = err.get('message', '')
                if code == 99991400 and attempt < MAX_RETRIES:
                    print(f"    ⏳ 99991400 rate-limit, retry {attempt}/{MAX_RETRIES} in {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)
                    continue
                return False, f"code={code} msg={msg[:100]}"
        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"    ⏳ Exception, retry {attempt}/{MAX_RETRIES} in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
                continue
            return False, str(e)[:150]
        finally:
            if os.path.exists(xml_file):
                os.unlink(xml_file)

    return False, "max retries exceeded"


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else time.strftime("%Y-%m-%d")
    input_file = sys.argv[2] if len(sys.argv) > 2 else "/tmp/l2_ingest.json"

    with open(input_file) as f:
        items = json.load(f)

    stats = {"total": len(items), "created": 0, "failed": 0,
             "competitor": 0, "industry": 0}

    for i, item in enumerate(items):
        title = item.get("title", "")
        cls = "competitor" if COMPETITOR_KW.search(title) else "industry"
        node = DEFAULT_NODE  # sub-tokens stale 2026-06-04; use first-level fallback
        stats[cls] += 1

        ok, detail = ingest_one(item, cls, node, date_str)
        if ok:
            stats["created"] += 1
            print(f"  ✅ [{i+1}/{len(items)}] {cls}: {title[:50]}")
        else:
            stats["failed"] += 1
            print(f"  ❌ [{i+1}/{len(items)}] {cls}: {title[:50]} — {detail}")

        if i < len(items) - 1:
            time.sleep(ITEM_DELAY)

        if (i + 1) % BATCH_SIZE == 0 and i < len(items) - 1:
            print(f"  --- Cooling {COOL_DOWN}s (batch {(i+1)//BATCH_SIZE}) ---")
            time.sleep(COOL_DOWN)

    print(f"\n=== INGEST SUMMARY ===")
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
