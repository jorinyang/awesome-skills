#!/usr/bin/env python3
"""
Flexible trip itinerary extractor from Feishu documents v2.
Supports multiple format variants + section parsing for safety/essentials/precautions.

Usage:
    python3 extract_trip.py --doc DOC_TOKEN [--output trip.json]
"""

import urllib.request, json, re, sys, os, argparse

# ━━━ Auth ━━━
APP_ID = "cli_aa9ead14c2641cc3"
APP_SECRET = "ZUUm7yI7HmfLi42ki8fPTgZzbj2AuTeM"

def get_token():
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
        {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())["tenant_access_token"]

TOKEN = get_token()

def feishu_api(method, path, body=None):
    url = f"https://open.feishu.cn/open-apis/{path}"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data, headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

# ━━━ Itinerary Parsers ━━━
DAY_PATTERNS = [
    (re.compile(r'Day\s*(\d+)', re.IGNORECASE), lambda m: int(m.group(1))),
    (re.compile(r'[Dd](\d+)'), lambda m: int(m.group(1))),
    (re.compile(r'第\s*(\d+)\s*天'), lambda m: int(m.group(1))),
    (re.compile(r'第\s*([一二三四五六七八九十]+)\s*天'), lambda m: 
        '一二三四五六七八九十'.index(m.group(1)) + 1),
]

LOCATION_SEPS = re.compile(r'[→\n\r,，、/|]+')
DURATION_RE = re.compile(r'[（(]\s*(\d+(?:\.\d+)?)\s*(?:小时|h|H|分钟|min)\s*[）)]')
TIME_RE = re.compile(r'(\d{1,2}[:：]\d{2})\s*[-~到]\s*(\d{1,2}[:：]\d{2})')
HOTEL_RE = re.compile(r'(?:宿|住|住宿|酒店|入住|夜宿)[:：]?\s*(.+?)(?:[。\n]|$)')
HOTEL_CLEAN_RE = re.compile(r'^[宿住][:：]?\s*')

STOP_MARKERS = ['费用说明', '价格说明', '参考价格', '价格', '温馨提示', '注意事项', '费用不含',
                 '包含费用', '安全须知', '安全保障', '户外安全', '必备物品', '行前准备',
                 '紧急联系', '联系方式', '行程背景', '目的地介绍', '线路介绍', '行程亮点']

LOCATION_BLACKLIST = {
    '费用', '项目', '标准', '备注', '组', '送站', '交通', '门票', '餐饮', '导游', '保险',
    '含早', '含接送站', '含观光车', '特色黔菜', '全程陪同', '单房差',
    '费用不含', '包含费用', '费用说明', '参考价格', '温馨提示',
}
MIN_LOCATION_LEN = 3

def clean_hotel_name(name):
    return HOTEL_CLEAN_RE.sub('', name).strip() if name else name

def parse_trip_text(content):
    """Parse raw Feishu doc content into structured trip data (days only)."""
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    days = []
    current_day = None
    stopped = False

    for line in lines:
        if any(marker in line for marker in STOP_MARKERS):
            stopped = True
            continue
        if stopped:
            continue

        day_num = None
        day_title = ""
        for pattern, extractor in DAY_PATTERNS:
            m = pattern.search(line)
            if m:
                day_num = extractor(m)
                title_start = m.end()
                day_title = line[title_start:].strip().lstrip('：:：- ').strip()
                if not day_title:
                    day_title = f"Day {day_num}"
                break

        if day_num:
            existing = next((d for d in days if d['day'] == day_num), None)
            if existing:
                current_day = existing
            else:
                current_day = {"day": day_num, "title": day_title, "stops": [], "hotel": None}
                days.append(current_day)
        elif current_day is not None:
            hotel_match = HOTEL_RE.search(line)
            if hotel_match:
                current_day["hotel"] = clean_hotel_name(hotel_match.group(1).strip())
            else:
                parts = LOCATION_SEPS.split(line)
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    clean_name = DURATION_RE.sub('', part).strip()
                    clean_name = TIME_RE.sub('', clean_name).strip()
                    if not clean_name or len(clean_name) < MIN_LOCATION_LEN:
                        continue
                    if clean_name in LOCATION_BLACKLIST:
                        continue
                    if any(bad in clean_name for bad in ['元', '万保额', '套餐', '大1小']):
                        continue
                    dur_match = DURATION_RE.search(part)
                    duration = dur_match.group(1) if dur_match else None
                    current_day["stops"].append({"name": clean_name, "duration": duration})
    return days


# ━━━ Section Parsing (v2) ━━━

SECTION_PATTERNS = [
    # (section_key, [header keywords])
    ("overview",     ["行程背景", "目的地介绍", "线路介绍", "行程简介"]),
    ("background",   ["文化背景", "地理背景", "地方特色"]),
    ("highlights",   ["行程亮点", "特色体验", "不容错过"]),
    ("essentials",   ["必备物品", "行前准备", "携带物品", "建议携带"]),
    ("precautions",  ["注意事项", "禁忌", "温馨提示", "特别提醒"]),
    ("safety",       ["安全须知", "安全保障", "户外安全", "安全提示"]),
    ("emergency",    ["紧急联系", "联系方式", "救援电话", "急救电话"]),
    ("pricing",      ["费用说明", "价格说明", "参考价格", "费用包含", "费用不含"]),
    ("difficulty",   ["难度等级", "适合人群", "体能要求"]),
    ("best_season",  ["最佳季节", "推荐时间", "适宜月份"]),
]

SUB_SECTION_PATTERNS = {
    "protection":          ["防护措施", "户外防护", "防晒", "防蚊", "防护"],
    "self_rescue":         ["自救", "受伤处理", "应急处理", "急救"],
    "disaster":            ["灾害", "天气提醒", "自然灾害", "预警"],
    "emergency_procedures": ["处置流程", "应急预案", "意外事故", "突发情况", "求救"],
}

def parse_sections(content):
    """Parse document sections after the itinerary for safety/essentials/precautions etc."""
    lines = content.split('\n')
    
    # Find where sections start (first occurrence of any section keyword after itinerary)
    current_section = None
    section_content = {}  # section_key -> list of lines
    section_lines = {}    # section_key -> list of (line_idx, line_text)
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
            
        # Check if this line is a section header
        matched = False
        for sec_key, keywords in SECTION_PATTERNS:
            for kw in keywords:
                if kw in stripped and len(stripped) < 30:
                    current_section = sec_key
                    if sec_key not in section_content:
                        section_content[sec_key] = []
                    matched = True
                    break
            if matched:
                break
        
        if matched:
            continue
        
        if current_section:
            section_content.setdefault(current_section, []).append(stripped)
    
    # Process extracted content
    result = {}
    
    # Overview / Background
    overview_lines = section_content.get("overview", [])
    if overview_lines:
        result["overview"] = '\n'.join(overview_lines[:5])
    bg_lines = section_content.get("background", [])
    if bg_lines:
        result["background"] = '\n'.join(bg_lines[:5])
    
    # Highlights
    hl_lines = section_content.get("highlights", [])
    if hl_lines:
        highlights = [l.lstrip('-·•1234567890.、 ') for l in hl_lines if len(l) > 3]
        result["highlights"] = highlights[:8]
    
    # Essentials
    ess_lines = section_content.get("essentials", [])
    if ess_lines:
        items = [l.lstrip('-·•1234567890.、 ').strip() for l in ess_lines if len(l.strip()) > 2]
        result["essentials"] = items[:20]
    
    # Precautions
    prec_lines = section_content.get("precautions", [])
    if prec_lines:
        items = [l.lstrip('-·•1234567890.、 ').strip() for l in prec_lines if len(l.strip()) > 2]
        result["precautions"] = items[:15]
    
    # Safety (with sub-sections)
    safety_lines = section_content.get("safety", [])
    if safety_lines:
        safety = {"protection": "", "self_rescue": "", "disaster": "", "emergency_procedures": ""}
        current_sub = None
        sub_content = {}
        
        for line in safety_lines:
            matched = False
            for sub_key, keywords in SUB_SECTION_PATTERNS.items():
                for kw in keywords:
                    if kw in line and len(line) < 25:
                        current_sub = sub_key
                        sub_content.setdefault(current_sub, []).append(line)
                        matched = True
                        break
                if matched:
                    break
            if not matched and current_sub:
                sub_content.setdefault(current_sub, []).append(line)
        
        for key, lines in sub_content.items():
            safety[key] = '\n'.join(lines)
        
        # If no sub-sections detected, put everything into protection
        if not any(safety.values()):
            safety["protection"] = '\n'.join(safety_lines)
        
        result["safety"] = safety
    
    # Emergency contacts
    em_lines = section_content.get("emergency", [])
    if em_lines:
        contacts = []
        for line in em_lines:
            # Try to extract name + phone pattern
            phone_match = re.search(r'(1[3-9]\d{9}|\d{3,4}[-]?\d{7,8}|1[12]0)', line)
            name = re.sub(r'(1[3-9]\d{9}|\d{3,4}[-]?\d{7,8}|1[12]0)', '', line).strip().rstrip('：:：- ').strip()
            if phone_match:
                contacts.append({"name": name or "紧急联系", "phone": phone_match.group(1)})
        result["emergency_contacts"] = contacts[:6]
    
    # Pricing
    pr_lines = section_content.get("pricing", [])
    if pr_lines:
        result["pricing_note"] = '\n'.join(pr_lines[:5])
        inclusions = [l.lstrip('-·•1234567890.、含').strip() for l in pr_lines if '含' in l and len(l) > 4]
        exclusions = [l.lstrip('-·•1234567890.、不含').strip() for l in pr_lines if '不含' in l and len(l) > 4]
        if inclusions:
            result["inclusions"] = inclusions[:10]
        if exclusions:
            result["exclusions"] = exclusions[:10]
    
    # Difficulty
    diff_lines = section_content.get("difficulty", [])
    if diff_lines:
        text = ' '.join(diff_lines)
        for level in ['挑战', '适中', '轻松', '休闲']:
            if level in text:
                result["difficulty"] = level
                break
        if "difficulty" not in result:
            result["difficulty"] = text[:20]
    
    # Best season
    season_lines = section_content.get("best_season", [])
    if season_lines:
        result["best_season"] = ' '.join(season_lines)[:30]
    
    return result


# ━━━ Amap Enrichment ━━━

POI_OVERRIDES = {
    "安龙古城": {"lng": 105.4427, "lat": 25.099, "name": "贵州省黔西南布依族苗族自治州安龙县安龙古城"},
    "安龙招堤": {"lng": 105.4777, "lat": 25.1108, "name": "贵州省黔西南布依族苗族自治州安龙县招堤"},
}

def enrich_with_amap(days):
    """Add coordinates and route info via Amap API for each stop."""
    KEY = "bdd24d613825549ee07b6c32c032c59b"
    
    def geocode_poi(name, city_hint=None):
        if name in POI_OVERRIDES:
            return POI_OVERRIDES[name]
        return None
    
    def geocode(address, city_hint=None):
        encoded = urllib.parse.quote(address, safe='')
        cities = [city_hint] if city_hint else ['黔西南', '兴义', '安龙', '贵州']
        
        for city in cities:
            try:
                city_enc = urllib.parse.quote(city, safe='')
                url = f"https://restapi.amap.com/v3/geocode/geo?key={KEY}&address={encoded}&city={city_enc}"
                req = urllib.request.Request(url, headers={"User-Agent": "Hermes-Agent/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read())
                    geos = data.get('geocodes', [])
                    if geos and geos[0].get('location'):
                        loc = geos[0]['location'].split(',')
                        return {"lng": float(loc[0]), "lat": float(loc[1]),
                                "name": geos[0].get('formatted_address', address), "city": city}
            except:
                continue
        
        try:
            url = f"https://restapi.amap.com/v3/geocode/geo?key={KEY}&address={encoded}"
            req = urllib.request.Request(url, headers={"User-Agent": "Hermes-Agent/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                geos = data.get('geocodes', [])
                if geos and geos[0].get('location'):
                    loc = geos[0]['location'].split(',')
                    return {"lng": float(loc[0]), "lat": float(loc[1]),
                            "name": geos[0].get('formatted_address', address)}
        except:
            pass
        return {"lng": None, "lat": None, "name": address}
    
    def get_route(origin_lnglat, dest_lnglat):
        url = f"https://restapi.amap.com/v3/direction/driving?key={KEY}&origin={origin_lnglat}&destination={dest_lnglat}&extensions=base"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
                if data['status'] == '1' and data['route']['paths']:
                    route = data['route']['paths'][0]
                    return {"distance_km": round(int(route['distance'])/1000, 1),
                            "duration_min": round(int(route['duration'])/60)}
        except:
            pass
        return None
    
    for day in days:
        all_stops = day["stops"].copy()
        if day.get("hotel"):
            all_stops.append({"name": day["hotel"]})
        
        for stop in all_stops:
            if stop.get("lng") is not None:
                continue
            name = stop["name"]
            city_hint = '黔西南'
            if '安龙' in name: city_hint = '安龙'
            elif '兴义' in name: city_hint = '兴义'
            
            geo = geocode_poi(name, city_hint=city_hint)
            if not geo or geo.get('lng') is None:
                geo = geocode(name, city_hint=city_hint)
            
            if geo.get('lng') and geo.get('lat'):
                formatted = geo.get('formatted_name', '')
                if '云南' in formatted or '丽江' in formatted:
                    geo = geocode(f"安龙县{name}", city_hint='安龙')
            
            if geo.get('lng') is None:
                prefix = '安龙县' if '安龙' in name else '兴义市'
                geo = geocode(f"{prefix}{name}", city_hint=city_hint)
            
            stop["lng"] = geo["lng"]
            stop["lat"] = geo["lat"]
            stop["formatted_name"] = geo["name"]
    
    transport = []
    for day in days:
        points = day["stops"].copy()
        for i in range(len(points) - 1):
            a, b = points[i], points[i + 1]
            if a.get("lng") and b.get("lng"):
                entry = {"from": a["name"], "to": b["name"],
                         "from_lng": a["lng"], "from_lat": a["lat"],
                         "to_lng": b["lng"], "to_lat": b["lat"]}
                route = get_route(f"{a['lng']},{a['lat']}", f"{b['lng']},{b['lat']}")
                if route:
                    entry.update(route)
                transport.append(entry)
    
    return days, transport


# ━━━ Main ━━━

def main():
    parser = argparse.ArgumentParser(description="Extract trip from Feishu doc v2")
    parser.add_argument("--doc", required=True, help="Feishu doc token")
    parser.add_argument("--output", default="trip_data.json", help="Output JSON file")
    args = parser.parse_args()
    
    print(f"📄 Reading doc: {args.doc}", file=sys.stderr)
    r = feishu_api("GET", f"docx/v1/documents/{args.doc}/raw_content")
    content = r['data']['content']
    
    r2 = feishu_api("GET", f"docx/v1/documents/{args.doc}")
    title = r2['data']['document']['title']
    
    # Parse itinerary
    print("🔍 Parsing itinerary...", file=sys.stderr)
    days = parse_trip_text(content)
    
    # Parse sections (safety, essentials, etc.)
    print("📋 Parsing sections (safety, essentials, etc.)...", file=sys.stderr)
    section_data = parse_sections(content)
    
    # Enrich with Amap
    print("🗺️  Enriching with Amap coordinates and routes...", file=sys.stderr)
    days, transport = enrich_with_amap(days)
    
    # Build output
    trip_data = {
        "title": title,
        "total_days": len(days),
        "stops_count": sum(len(d['stops']) for d in days),
        "days": days,
        "transport": transport,
        # Section data
        "overview": section_data.get("overview", ""),
        "background": section_data.get("background", ""),
        "highlights": section_data.get("highlights", []),
        "difficulty": section_data.get("difficulty", "适中"),
        "best_season": section_data.get("best_season", "全年"),
        "essentials": section_data.get("essentials", []),
        "precautions": section_data.get("precautions", []),
        "safety": section_data.get("safety", {}),
        "emergency_contacts": section_data.get("emergency_contacts", []),
        "pricing_note": section_data.get("pricing_note", ""),
        "inclusions": section_data.get("inclusions", []),
        "exclusions": section_data.get("exclusions", []),
    }
    
    with open(args.output, 'w') as f:
        json.dump(trip_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Extracted {len(days)} days, {trip_data['stops_count']} stops → {args.output}", file=sys.stderr)
    print(json.dumps(trip_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
