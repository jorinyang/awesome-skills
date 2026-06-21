# 首页 XML 组装脚本

本脚本对应 Step 3，处理骨架 XML → 删除 SUMMARY 占位符 → 按 token 匹配插入摘要。

## 核心逻辑

骨架 XML 中每个文档链接格式：
```html
<a href="https://acn3kz7weyc0.feishu.cn/docx/TOKEN">TITLE</a><!-- ##SUMMARY:TOKEN## -->
```

## 匹配策略

- **正确**：用 `f"docx/{tok}"` 在 href URL 路径中搜索 token
- **错误**：用 `data-token="TOKEN"` 搜索（骨架中不存在此属性）→ 导致 0 条摘要插入

## 插入排序

必须先收集所有 `(position, insert_text)` 元组，按 position **降序**排列后逐个插入。正向顺序插入会因每次修改改变后续偏移量导致匹配错位。

## 缓存中的孤儿 token

旧缓存中可能存在已从当前骨架删除的 token（`skeleton.find()` 返回 -1），这是正常现象，记入 `not_found` 计数即可。

## 完整脚本

```python
#!/usr/bin/env python3
"""Assemble final homepage XML: remove SUMMARY placeholders, insert summaries sorted by position."""
import json, re, os

SKELETON_PATH = "/tmp/wiki_skeleton.xml"
CACHE_PATH = os.path.expanduser("~/.hermes-feishu/cron/wiki_summaries.json")
OUTPUT_PATH = "/tmp/wiki_homepage_final.xml"

# Read skeleton
with open(SKELETON_PATH) as f:
    skeleton = f.read()

# Step 1: Remove all <!-- ##SUMMARY:TOKEN## --> placeholders
skeleton = re.sub(r'<!-- ##SUMMARY:[^#]+## -->', '', skeleton)

# Load cache
with open(CACHE_PATH) as f:
    cache = json.load(f)

# Build token -> summary map
token_summary = {}
for tok, data in cache.items():
    if isinstance(data, dict) and data.get("summary"):
        token_summary[tok] = data["summary"]

# Step 2: Find all (position, insert_text) tuples, sort descending
insertions = []
for tok, summary in token_summary.items():
    needle = f"docx/{tok}"
    idx = skeleton.find(needle)
    if idx == -1:
        continue
    end_tag = skeleton.find("</a>", idx)
    if end_tag == -1:
        continue
    insertions.append((end_tag + 4, f"<br/><em>{summary}</em>"))

insertions.sort(key=lambda x: x[0], reverse=True)
for pos, text in insertions:
    skeleton = skeleton[:pos] + text + skeleton[pos:]

# Write final
with open(OUTPUT_PATH, "w") as f:
    f.write(skeleton)

print(f"Inserted: {len(insertions)}, Not found: {len(token_summary) - len(insertions)}")
```

## 执行

```bash
python3 /tmp/wiki_assemble_homepage.py
```

cron 模式下必须通过 `write_file` → `terminal python3` 执行，不能使用 `execute_code` 或 heredoc 内联。
