#!/usr/bin/env python3
"""Generate summaries from titles for wiki docs (>50 docs, title-based strategy).

Reads /tmp/wiki_agent_input.json, deduplicates by title, reuses cached summaries,
generates new ones from cleaned titles, writes ~/.hermes-feishu/cron/wiki_summaries.json.
"""
import json, re, os, sys
from collections import Counter
from datetime import datetime

AGENT_INPUT = "/tmp/wiki_agent_input.json"
CACHE = os.path.expanduser("~/.hermes-feishu/cron/wiki_summaries.json")

with open(AGENT_INPUT, "r") as f:
    data = json.load(f)

docs = data["docs_needing_summary"]
NOW = datetime.now().strftime("%Y-%m-%d %H:00")

# Count titles for dedup
unique_titles = set(d["title"] for d in docs)
print(f"Total docs: {len(docs)}, Unique titles: {len(unique_titles)}")

# Load existing cache
cache = {}
if os.path.exists(CACHE):
    try:
        with open(CACHE) as f:
            cache = json.load(f)
    except:
        pass

reused = 0
summary_map = {}  # title -> summary

for title in sorted(unique_titles):
    # Check if any doc with this title already has a cached summary
    for tok in cache:
        if cache[tok].get("title") == title:
            summary_map[title] = cache[tok]["summary"]
            reused += 1
            break
    if title in summary_map:
        continue

    # Generate summary from title: strip date/source prefix, clean separators
    clean = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', title)
    clean = re.sub(r'^(pinchain_|meadin_wl_|meadin_jq_|meadin_|other_|wenlv_|travel_)', '', clean)
    clean = clean.replace('_', ' ').replace('\uff1a', ': ').replace('\uff0c', ', ')
    if len(clean) > 197:
        clean = clean[:197] + "..."
    summary_map[title] = clean

# Assign summaries to every doc token
new_count = 0
for doc in docs:
    tok = doc["obj_token"]
    title = doc["title"]
    summary = summary_map.get(title, title)
    if tok not in cache:
        new_count += 1
    cache[tok] = {
        "summary": summary,
        "updated_at": NOW,
        "title": title,
        "parent": doc.get("parent", "\u672a\u77e5")
    }

os.makedirs(os.path.dirname(CACHE), exist_ok=True)
with open(CACHE, "w") as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"Reused from cache: {reused} titles")
print(f"New summaries: {len(summary_map) - reused} titles")
print(f"Cache entries: {len(cache)} total ({new_count} new tokens)")
print("Done.")
