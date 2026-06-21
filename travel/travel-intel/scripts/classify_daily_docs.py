#!/usr/bin/env python3
"""Classify today's Wiki documents for daily brief.

Usage: python3 classify_daily_docs.py /tmp/wiki_nodes.json YYYY-MM-DD

Outputs: grouped lists by category (high_gz, high_outdoor, policy, regular, noise)
Prints summary stats + each category's items with obj_token for cross-reference.
"""

import json, re, sys

if len(sys.argv) < 3:
    print("Usage: python3 classify_daily_docs.py <wiki_nodes.json> <YYYY-MM-DD>")
    sys.exit(1)

input_file = sys.argv[1]
date_prefix = sys.argv[2]

# ── Configuration ──────────────────────────────────────────
HIGH_PRIO_GUIZHOU = [
    '贵州', '贵阳', '黔西南', '黔南', '黔东南', '兴义', '安龙', '贞丰',
    '万峰林', '马岭河', '黄果树', '荔波', '梵净山', '旅发', '遵义',
    '毕节', '铜仁', '赤水', '镇远', '西江', '百里杜鹃', '龙宫'
]

COMPETITOR_KEYWORDS = [
    '马蜂窝', '蚂蜂窝', '穷游', '携程', '飞猪', '美团', '同程', '途牛',
    '驴妈妈', '新东方文旅', '广之旅', '凯撒', '众信', '中青旅', '绿云',
    '8264', '抖音旅游', '小红书旅游', '竞品', '新品上线'
]

OUTDOOR_KEYWORDS = [
    '探洞', '天坑', '桨板', 'SUP', '漂流', '溯溪', '徒步', '户外',
    '攀岩', '速降', '洞穴', '飞拉达'
]

POLICY_KEYWORDS = [
    '办法', '规划', '通知', '统计公报', '印发', '十五五', '条例',
    '管理规定', '实施方案', '意见', '安全提示', '汛期'
]

NOISE_PATTERNS = [
    '迈点空间', '迈点今日头条', '酒店采购需求', '供应链产品',
    '酒店项目信息', '内容开放平台', 'test_'
]

# Other-province abbreviations that should NOT trigger Guizhou
NOT_GUIZHOU_ABBREV = ['滇', '川', '渝', '桂', '湘', '鄂', '赣']

# ── Helpers ────────────────────────────────────────────────

def classify(title):
    """Returns (category, clean_title)."""
    # Strip date and source prefix
    clean = re.sub(r'^\d{4}-\d{2}-\d{2}_[a-z]+_', '', title).strip()

    # Noise filter
    for pat in NOISE_PATTERNS:
        if re.search(pat, clean):
            return 'noise', clean

    # Check for other-province false positive
    has_other_prov = any(abbr in clean for abbr in NOT_GUIZHOU_ABBREV)

    # Check Guizhou keywords (with 黔江 exception)
    has_gz = False
    for kw in HIGH_PRIO_GUIZHOU:
        if kw in clean:
            if kw == '黔' and '黔江' in clean:
                continue  # 重庆黔江区, not Guizhou
            has_gz = True
            break

    # If another province abbreviation is present but no Guizhou
    # keyword, it's NOT Guizhou content
    if has_other_prov and not has_gz:
        has_gz = False

    has_outdoor = any(kw in clean for kw in OUTDOOR_KEYWORDS)
    has_competitor = any(kw in clean for kw in COMPETITOR_KEYWORDS)
    has_policy = any(kw in clean for kw in POLICY_KEYWORDS)

    # "标准" alone isn't policy — could be commercial product standard
    if '标准' in clean and not any(p in clean for p in ['国家标准', '行业标准', '标准化']):
        if any(w in clean for w in ['发布', '推出', '上线', 'IP', '产品', '新品']):
            has_policy = False

    if has_gz:
        return 'high_gz', clean
    elif has_outdoor:
        return 'high_outdoor', clean
    elif has_policy:
        return 'policy', clean
    elif has_competitor:
        return 'competitor', clean
    else:
        return 'regular', clean


# ── Main ───────────────────────────────────────────────────

with open(input_file) as f:
    raw = f.read()

# Extract JSON after "Found N node(s)" line
lines = raw.split('\n')
json_start = next(i for i, l in enumerate(lines) if l.strip().startswith('{'))
data = json.loads('\n'.join(lines[json_start:]))

nodes = data.get('data', data).get('nodes', [])

# Filter today's documents
today = []
seen_tokens = set()
for n in nodes:
    title = n.get('title', '')
    if re.match(rf'{date_prefix}_', title):
        obj = n.get('obj_token', '')
        if obj not in seen_tokens:
            seen_tokens.add(obj)
            today.append({
                'title': title,
                'obj_token': obj,
                'node_token': n.get('node_token', '')
            })

# Classify
buckets = {'high_gz': [], 'high_outdoor': [], 'policy': [], 'competitor': [], 'regular': [], 'noise': []}
for doc in today:
    cat, clean_title = classify(doc['title'])
    doc['clean_title'] = clean_title
    buckets[cat].append(doc)

# Output
labels = {
    'high_gz': '🔴 贵州高优',
    'high_outdoor': '🏕️ 户外/竞品',
    'policy': '🏛️ 政策',
    'competitor': '🏢 竞品动态',
    'regular': '🟡 常规',
    'noise': '🗑️ 噪音'
}

print(f"DATE: {date_prefix}")
print(f"TOTAL: {len(today)}")
for cat in ['high_gz', 'high_outdoor', 'policy', 'competitor', 'regular', 'noise']:
    print(f"{labels[cat]}: {len(buckets[cat])}")
print("---")

for cat in ['high_gz', 'high_outdoor', 'policy', 'competitor', 'regular']:
    docs = buckets[cat]
    if docs:
        print(f"\n### {labels[cat]} ({len(docs)}条)")
        for d in docs:
            print(f"  [{d['obj_token']}] {d['clean_title']}")
