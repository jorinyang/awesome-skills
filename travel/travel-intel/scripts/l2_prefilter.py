#!/usr/bin/env python3
"""L2 三阶段预过滤：去模板 → 旅行关键词 → 去导航链接+去重
Usage: python3 l2_prefilter.py [/tmp/l2_results.json] [--output /tmp/l2_ingest.json]
默认读 /tmp/l2_results.json，写 /tmp/l2_ingest.json
"""
import json, re, sys, os

INPUT = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else '/tmp/l2_results.json'
OUTPUT = '/tmp/l2_ingest.json'
for i, a in enumerate(sys.argv):
    if a == '--output' and i+1 < len(sys.argv):
        OUTPUT = sys.argv[i+1]

# ── 旅行关键词 (与 references/l2-pre-filter-keywords.md 同步) ──
TRAVEL_KEYWORDS = [
    # Core
    '旅游', '旅行', '景区', '景点', '酒店', '民宿', '文旅', '户外',
    '登山', '徒步', '漂流', '滑雪', '露营', '探洞', '天坑', '桨板', 'SUP',
    '避暑', '康养', '旅居', '研学', '入境游', '出境游', '邮轮', '自驾',
    '公园', '乐园', '度假', '温泉', '缆车', '索道', '航线', '航班',
    # OTA/平台
    '携程', '同程', '美团', '飞猪', '马蜂窝', '途牛', '众信', '凯撒',
    'OTA', '旅行社', '导游',
    # 目的地
    '贵州', '黔西南', '黔南', '黔东南', '兴义', '安龙', '贞丰', '安顺',
    '万峰林', '马岭河', '黄果树', '荔波', '梵净山', '普者黑',
    '黄山', '张家界', '桂林', '丽江', '三亚', '九寨', '莫干山',
    '曲江', '慈溪', '德清', '祥云', '红河', '玉溪',
    # 产品/业态
    '门票', '文创', '非遗', '演艺', '演出', '音乐节', '艺术节', '夜市', '灯光秀',
    '环球', '迪士尼', '方特', '长隆', '主题公园', '水上乐园',
    '古城', '古镇', '古村', '客栈',
    '赛事', '马拉松', '骑行', '越野',
    '乡村振兴', '乡村旅游', '工业旅游', '研学旅游', '红色旅游',
    # 政策/行业
    '国际', '入境', '出境', '签证', '口岸',
    '文旅惠报', 'ITB', '深度游', '康养',
    '文旅部', '旅游厅', '旅游局', '文旅局',
    '统计公报', 'A级景区', '旅游收入', '旅游人次',
]

# 部门名称模式 (纯导航链接，非实际文章)
DEPT_NAME_PATTERNS = [
    r'^(国家|.{1,2}省|.{1,2}市|.{1,3}自治区|.{1,3}特别行政区).*文化和旅游[厅局部]$',
    r'^(国家|.{1,2}省|.{1,2}市).*旅游局$',
    r'^.*文化和旅游[厅局]$',
]

# 执惠/闻旅 页脚噪音
FOOTER_NOISE = ['版权', 'ICP', '备案', 'Copyright', '关于我们', '联系我们', '友情链接',
                '首页', '上一页', '下一页', '未页', '返回', 'TOP']

# ── 加载 ──
with open(INPUT) as f:
    data = json.load(f)
total_in = len(data)
print(f"[阶段0] 输入: {total_in} 条")

# ── 阶段1: 去模板占位符 + 空白/过短 ──
clean = [d for d in data
         if d.get('title', '').strip() not in ('', '{{name}}', '{name}', '{title}')
         and not d.get('title', '').startswith('{{')
         and len(d['title']) >= 8]
print(f"[阶段1] 去模板: {len(clean)} 条 (过滤 {total_in - len(clean)} 条)")

# ── 阶段2: 旅行相关性 ──
def is_travel(t):
    tl = t.lower()
    return any(kw.lower() in tl for kw in TRAVEL_KEYWORDS)

travel = [d for d in clean if is_travel(d['title'])]
print(f"[阶段2] 旅行关键词: {len(travel)} 条 (过滤 {len(clean) - len(travel)} 条)")

# ── 阶段3a: 去部门导航链接 ──
final = []
for d in travel:
    t = d['title'].strip()
    skip = any(re.match(pat, t) for pat in DEPT_NAME_PATTERNS)
    # 页脚噪音
    skip = skip or any(kw in t for kw in FOOTER_NOISE)
    if not skip:
        final.append(d)
print(f"[阶段3a] 去导航/页脚: {len(final)} 条 (过滤 {len(travel) - len(final)} 条)")

# ── 阶段3b: 标题去重 (case-insensitive) ──
seen = set()
unique = [d for d in final
          if not (d['title'].strip().lower() in seen or seen.add(d['title'].strip().lower()))]
print(f"[阶段3b] 去重: {len(unique)} 条 (过滤 {len(final) - len(unique)} 条)")

# ── 统计来源分布 ──
from collections import Counter
src_dist = Counter(d['source'] for d in unique)
print(f"\n来源分布:")
for src, cnt in src_dist.most_common():
    print(f"  {src}: {cnt} 条")

# ── 输出 ──
with open(OUTPUT, 'w') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

print(f"\n→ {OUTPUT} ({len(unique)} 条)")
# 估算入库耗时 (BATCH=6, DELAY=5s, COOL=15s)
est_s = (len(unique) // 6) * (6 * 5 + 15) + (len(unique) % 6) * 5
print(f"  估算入库耗时: ~{est_s}s ({est_s/60:.0f}min) @ BATCH=6")
