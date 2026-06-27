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
    '马蜂窝', '蚂蜂窝', '穷游', '8264', '竞品', '新品上线'
]

# OTA brands get their own category (🟠) — industry infrastructure, not direct competitor
OTA_BRANDS = [
    '携程', '飞猪', '美团', '同程旅行', '同程', '途牛',
    '驴妈妈', 'Klook', '客路', 'Trip.com'
]

OUTDOOR_KEYWORDS = [
    '探洞', '天坑', '桨板', 'SUP', '漂流', '溯溪', '徒步', '户外',
    '攀岩', '速降', '洞穴', '飞拉达', '瀑降', '绳降', '露营', '避暑'
]

POLICY_KEYWORDS = [
    '办法', '规划', '通知', '统计公报', '印发', '十五五', '条例',
    '管理规定', '实施方案', '意见', '安全提示', '汛期',
    '商务部', '财政部', '交通部', '教育部', '自然资源部', '发改委',
    '部等',  # matches "X部等N单位" pattern
    '国家标准', '行业标准', '专项整治', '安全整治', '监管'
]

NOISE_PATTERNS = [
    '迈点空间', '迈点今日头条', '酒店采购需求', '供应链产品',
    '酒店项目信息', '内容开放平台', 'test_'
]

# Non-tourism content that passed travel-keyword filter but is irrelevant
NON_TOURISM_NOISE = [
    r'工会.*(过|节日|端午|中秋|春节)',      # 工会福利报道
    r'.*(青年演员|歌手|舞蹈|戏曲).*比赛',    # 文艺比赛
]

# Pure department navigation links (not substantive tourism content)
DEPT_NAV_PATTERNS = [
    r'^[京津沪渝冀晋辽吉黑苏浙皖闽赣鲁豫鄂湘粤桂琼川黔滇藏陕甘青宁新]{2,6}(省|市|自治区).*(旅游|文化).*(厅|局|委员会)$',
    r'.*(文化和|旅游和).*(体育厅|广电|发展委员会)$',
]

import datetime as _dt
_current_year = _dt.date.today().year

# Other-province abbreviations that should NOT trigger Guizhou
NOT_GUIZHOU_ABBREV = ['滇', '川', '渝', '桂', '湘', '鄂', '赣']

# ── Helpers ────────────────────────────────────────────────

def is_noise(clean_title):
    """Check if title is noise — irrelevant or navigation-only content."""
    for pat in NOISE_PATTERNS:
        if re.search(pat, clean_title):
            return True
    for pat in NON_TOURISM_NOISE:
        if re.search(pat, clean_title):
            return True
    for pat in DEPT_NAV_PATTERNS:
        if re.match(pat, clean_title.strip()):
            return True
    return False

def is_stale_year(clean_title):
    """Detect articles with data from 2+ years ago that lack current relevance."""
    m = re.search(r'(19\d{2}|20[0-1]\d|202[0-4])年', clean_title)
    if m:
        year = int(m.group(1))
        if _current_year - year >= 2:
            return True
    return False

def classify(title):
    """Returns (category, clean_title)."""
    # Strip date and source prefix
    clean = re.sub(r'^\d{4}-\d{2}-\d{2}_[a-z]+_', '', title).strip()

    # Noise filter — expanded with non-tourism + dept nav
    if is_noise(clean):
        return 'noise', clean

    # Stale year filter
    if is_stale_year(clean):
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
    has_competitor_direct = any(kw in clean for kw in COMPETITOR_KEYWORDS)
    has_ota = any(kw in clean for kw in OTA_BRANDS)
    has_policy = any(kw in clean for kw in POLICY_KEYWORDS)

    # "标准" alone isn't policy — could be commercial product standard
    if '标准' in clean and not any(p in clean for p in ['国家标准', '行业标准', '标准化']):
        if any(w in clean for w in ['发布', '推出', '上线', 'IP', '产品', '新品', '美团']):
            has_policy = False

    if has_gz:
        return 'high_gz', clean
    elif has_outdoor:
        return 'high_outdoor', clean
    elif has_policy:
        return 'policy', clean
    elif has_ota:
        return 'ota', clean      # 🟠 OTA industry infrastructure moves
    elif has_competitor_direct:
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
buckets = {'high_gz': [], 'high_outdoor': [], 'policy': [], 'ota': [], 'competitor': [], 'regular': [], 'noise': []}
for doc in today:
    cat, clean_title = classify(doc['title'])
    doc['clean_title'] = clean_title
    buckets[cat].append(doc)

# Output
labels = {
    'high_gz': '🔴 贵州高优',
    'high_outdoor': '🏕️ 户外/竞品',
    'policy': '🏛️ 政策',
    'ota': '🟠 OTA动态',
    'competitor': '🏢 竞品动态',
    'regular': '🟡 常规',
    'noise': '🗑️ 噪音'
}

print(f"DATE: {date_prefix}")
print(f"TOTAL: {len(today)}")
for cat in ['high_gz', 'high_outdoor', 'policy', 'ota', 'competitor', 'regular', 'noise']:
    print(f"{labels[cat]}: {len(buckets[cat])}")
print("---")

for cat in ['high_gz', 'high_outdoor', 'policy', 'ota', 'competitor', 'regular']:
    docs = buckets[cat]
    if docs:
        print(f"\n### {labels[cat]} ({len(docs)}条)")
        for d in docs:
            print(f"  [{d['obj_token']}] {d['clean_title']}")
