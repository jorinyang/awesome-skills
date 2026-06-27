#!/usr/bin/env python3
"""Assemble final homepage XML with summaries inserted from cache.

Reads /tmp/wiki_skeleton.xml, removes placeholder comments,
inserts <br/><em>summary</em> after each </a> tag whose href
matches a cached docx/TOKEN, writes /tmp/wiki_homepage_final.xml.
Insertions are done in reverse position order to avoid offset drift.
"""
import json, re, os, sys

SKELETON = "/tmp/wiki_skeleton.xml"
CACHE = os.path.expanduser("~/.hermes-feishu/cron/wiki_summaries.json")
OUTPUT = "/tmp/wiki_homepage_final.xml"

with open(SKELETON, "r") as f:
    skeleton = f.read()

# Remove all summary placeholder comments
skeleton = re.sub(r'<!-- ##SUMMARY:[^#]+## -->', '', skeleton)

with open(CACHE, "r") as f:
    cache = json.load(f)

# Collect insertions: find </a> after matching docx/TOKEN
insertions = []
no_match = 0
matched = 0

for tok, info in cache.items():
    summary = info.get("summary", "")
    if not summary:
        continue
    needle = "docx/" + tok
    idx = skeleton.find(needle)
    if idx == -1:
        no_match += 1
        continue
    end_tag = skeleton.find("</a>", idx)
    if end_tag == -1:
        no_match += 1
        continue
    insert_text = "<br/><em>" + summary + "</em>"
    insertions.append((end_tag + 4, insert_text))
    matched += 1

# Insert in reverse order to preserve positions
insertions.sort(key=lambda x: x[0], reverse=True)
for pos, text in insertions:
    skeleton = skeleton[:pos] + text + skeleton[pos:]

with open(OUTPUT, "w") as f:
    f.write(skeleton)

print(f"Matched: {matched}, No match: {no_match}")
print(f"Output: {OUTPUT} ({len(skeleton)} chars)")
print("Done.")
