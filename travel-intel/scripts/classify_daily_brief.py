#!/usr/bin/env python3
"""Parse wiki node-list JSON outputs to extract today's documents and classify for daily briefing.

Usage:
    python3 classify_daily_brief.py

Reads raw node-list outputs from /tmp/uf7_nodes.json (or fetches live via lark-cli).
Outputs JSON classification to stdout, with human-readable summary to stderr.
"""
import json, re, sys, subprocess, os

os.environ["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{os.environ.get('PATH', '')}"

TODAY = "2026-06-09"  # Override: python3 classify_daily_brief.py 2026-06-10
if len(sys.argv) > 1:
    TODAY = sys.argv[1]

SPACE_ID = "7643710721485753535"
UF7_TOKEN = "UF7Cw5w2WiHGfjkKVvBcxj8Hnib"
V0_TOKEN = "V0Lhwl7KYiWYDDk1vCncv2GhnYf"
EA_TOKEN = "EAMYw1CPoipVWtkObbtcR2oDnNc"

# Classification keywords
GUIZHOU_KEYWORDS = [
    '贵州', '贵阳', '黔西南', '黔东南', '黔南', '兴义', '安龙', '贞丰',
    '万峰林', '马岭河', '黄果树', '荔波', '梵净山', '毕节', '六盘水',
    '遵义', '铜仁', '龙里', '罗甸', '镇远', '安顺', '贵定', '岑巩', '清镇',
    '花江', '格凸河', '织金洞', '石龙洞', '燕子洞', '平塘', '大小井',
    '旅发', '贵州省'
]
POLICY_KEYWORDS = ['办法', '规划', '通知', '统计公报', '印发', '十五五', '免征', '管理条例',
                   '管理办法', '实施方案', '行动计划', '发展规划', '国务院', '文旅部', '教育部',
                   '商务部', '财政部', '交通部', '自然资源部', '发改委', '部等',
                   '专项整治', '安全整治', '监管']
# Outdoor/niche activity keywords (贵州之客核心业务方向)
OUTDOOR_KEYWORDS = ['探洞', '天坑', '桨板', 'SUP', '瀑降', '溯溪', '漂流', '飞拉达', '绳降',
                    '洞穴', '攀岩', '速降', '徒步', '露营', '避暑', '户外探险']

# Competitor brand/company names (OTA, travel platforms, direct competitors)
COMPETITOR_KEYWORDS = ['马蜂窝', '蚂蜂窝', '穷游', '8264',
                       '携程', '飞猪', '美团旅游', '同程', '途牛', '驴妈妈',
                       '新东方文旅', '广之旅', '凯撒', '众信', '中青旅',
                       '绿云', '抖音旅游', '小红书旅游']
NOISE_PATTERNS = ['迈点空间租赁', '迈点今日头条', '酒店采购需求发布', '供应链产品和服务',
                  '酒店项目信息服务', '内容开放平台', 'supports@']


def classify(title):
    """Classify a document title. Returns (category, priority) or (None, None) for noise."""
    for npatt in NOISE_PATTERNS:
        if npatt in title:
            return None, None

    is_policy = any(kw in title for kw in POLICY_KEYWORDS)
    is_guizhou = any(kw in title for kw in GUIZHOU_KEYWORDS)
    is_outdoor = any(kw in title for kw in OUTDOOR_KEYWORDS)
    is_competitor = any(kw in title for kw in COMPETITOR_KEYWORDS)

    # "黔江" is Chongqing, not Guizhou
    if '黔江' in title and not any(g in title for g in ['黔西南', '黔南', '黔东南']):
        is_guizhou = False

    # Other provinces with similar short names: 滇(云南), 川(四川), 桂(广西), 渝(重庆)
    # Only mark as Guizhou when贵州 keywords are actually present
    other_province_markers = ['红河', '大理', '丽江', '西双版纳', '腾冲', '楚雄',
                              '成都', '重庆渝', '桂林', '北海']
    if any(m in title for m in other_province_markers) and not is_guizhou:
        # Not Guizhou — don't falsely elevate
        pass

    # "标准" alone isn't policy — it could be a commercial product standard
    has_policy_standard = any(p in title for p in ['国家标准', '行业标准', '标准化', '服务标准体系'])
    if '标准' in title and not has_policy_standard:
        if any(w in title for w in ['发布', '推出', '上线', 'IP', '产品', '新品']):
            is_policy = False

    if is_policy:
        return ('policy', '🔴' if is_guizhou else '🏛️')
    elif is_guizhou:
        sub = 'guizhou_competitor' if is_competitor else 'guizhou_local'
        return ('guizhou_high', '🔴')
    elif is_outdoor:
        sub = 'competitor' if is_competitor else 'outdoor'
        return ('guizhou_high', '🔴')
    elif is_competitor:
        return ('competitor', '🟡')
    else:
        return ('general', '🟡')


def fetch_node_list(node_token, page_token=""):
    """Fetch wiki node list via lark-cli, handles pagination. Returns parsed nodes list."""
    cmd = [
        'lark-cli', 'wiki', '+node-list',
        '--space-id', SPACE_ID,
        '--parent-node-token', node_token,
        '--page-all', '--page-limit', '20', '--as', 'bot'
    ]

# ^ --page-limit 25 (1250 docs): safe for nodes with 1100+ entries.
#   --page-limit 0 times out at 60s+; 20 is the current sweet spot.
#   See travel-intel SKILL.md: "wiki +node-list --page-all 静默截断陷阱"
    if page_token:
        cmd += ['--page-token', page_token]

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    raw = r.stdout

    # JSON-first parsing (handles inner quotes properly)
    idx = raw.find('{')
    if idx < 0:
        return [], ""
    try:
        data = json.loads(raw[idx:])
    except json.JSONDecodeError:
        # Control characters in titles → clean and retry
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw[idx:])
        data = json.loads(cleaned)

    nodes = data.get('data', {}).get('nodes', [])
    has_more = data.get('data', {}).get('has_more', False)
    next_page_token = data.get('data', {}).get('page_token', '')
    return nodes, next_page_token if has_more else ""


def get_all_docs(node_token):
    """Fetch all documents from a wiki node, handling pagination."""
    all_nodes = []
    page_token = ""
    while True:
        nodes, page_token = fetch_node_list(node_token, page_token)
        all_nodes.extend(nodes)
        if not page_token:
            break
    return all_nodes


def main():
    all_docs = []
    seen_titles = set()

    for label, token in [("UF7", UF7_TOKEN), ("V0", V0_TOKEN), ("EA", EA_TOKEN)]:
        print(f"Fetching {label}...", file=sys.stderr)
        nodes = get_all_docs(token)
        for node in nodes:
            title = node.get('title', '')
            if title.startswith(TODAY) and node.get('obj_type') == 'docx':
                if title not in seen_titles:
                    seen_titles.add(title)
                    source = 'unknown'
                    sm = re.match(r'\d{4}-\d{2}-\d{2}_(\w+)_', title)
                    if sm:
                        source = sm.group(1)
                    all_docs.append({
                        'title': title,
                        'obj_token': node.get('obj_token', ''),
                        'node_token': node.get('node_token', ''),
                        'source': source
                    })
        print(f"  Found {sum(1 for d in all_docs if d['title'] in seen_titles)} today docs so far", file=sys.stderr)

    print(f"\nTotal unique today docs: {len(all_docs)}", file=sys.stderr)

    # Classify
    categories = {'guizhou_high': [], 'policy': [], 'competitor': [], 'general': [], 'dropped': []}
    for d in all_docs:
        cat, priority = classify(d['title'])
        if cat is None:
            categories['dropped'].append(d)
        else:
            d['priority'] = priority
            categories[cat].append(d)

    # Print summary to stderr
    print(f"\n=== CLASSIFICATION ===", file=sys.stderr)
    for cat in ['guizhou_high', 'competitor', 'policy', 'general']:
        print(f"{cat}: {len(categories[cat])} docs", file=sys.stderr)
        for d in categories[cat]:
            print(f"  [{d['priority']}] {d['source']} | {d['title']}", file=sys.stderr)
    print(f"dropped (noise): {len(categories['dropped'])} docs", file=sys.stderr)

    # Output JSON to stdout
    print(json.dumps({
        'date': TODAY,
        'total': len(all_docs),
        'dropped': len(categories['dropped']),
        'categories': {k: v for k, v in categories.items()}
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
