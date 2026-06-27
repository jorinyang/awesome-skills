#!/usr/bin/env python3
"""
Travel Intel Expiry Checker v3
Scans Feishu Wiki nodes, applies 15-category expiry rules,
adds full-document comments for expired docs.

Usage: python3 expiry_checker.py
Requires: FEISHU_APP_ID, FEISHU_APP_SECRET env vars
"""

import json, os, subprocess, sys, re, time
from datetime import datetime, timezone, date, timedelta
from collections import Counter

SPACE_ID = "7643710721485753535"
TARGET_NODES = [
    ("industry", "V0Lhwl7KYiWYDDk1vCncv2GhnYf"),
    ("competitor", "EAMYw1CPoipVWtkObbtcR2oDnNc"),
]
TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(TZ).date()

RULES = [
    (r"(社媒|热搜|热议|话题|微博|知乎|热榜|trending)", 7, "社媒热议话题"),
    (r"竞品.*(社媒|社交|话题|微博|知乎|小红书)", 14, "竞品社媒动态"),
    (r"竞品.*(价格|降价|涨价|调价|促销|优惠)", 14, "竞品价格"),
    (r"竞品|新品|营销|探洞|天坑|桨板|SUP|坝盘|速降|户外装备", 30, "竞品新品/营销"),
    (r"(节庆|赛事|活动|音乐节|嘉年华|庙会|端午|中秋|国庆|春节|五一|十一|暑期|开幕|启幕|启航|开漂)", 14, "节庆/活动"),
    (r"(门票|免票|票价|收费|优惠票|免费|半价|折扣|囤|爆款|好价格)", 30, "门票/开放时间"),
    (r"(酒店|民宿|住宿|机票|高铁|大巴|航线).*(价格|涨价|降价|促销|优惠|折扣)", 30, "酒店/交通价格"),
    (r"(政策|通知|通告|公告|管理办法|规定|方案).*(省|市|县|区|文旅厅|旅游局|人民政府)", 60, "政策法规(地方/临时)"),
    (r"(国务院|国家|部委|中央|文旅部|统计局|发改委).*(政策|规划|通知|方案|公报)", 180, "政策法规(国家级)"),
    (r"(酒店|民宿|度假村|住宿|交通|高铁|航线|高速|通车|开业|新开|设施)", 90, "酒店设施/交通线路"),
    (r"(报告|趋势|洞察|分析|周度|综合|统计|数据|年报|白皮书)", 90, "行业报告/趋势"),
    (r"(季节|春季|夏季|秋季|冬季|赏花|避暑|滑雪|温泉|赏秋|踏青|露营)", 90, "季节性信息"),
    (r"(攻略|游记|推荐|点评|打卡|路线|行程)", 365, "攻略/游记/评价"),
    (r"(景点|景区|5A|4A|地质公园|世界遗产|名山|古镇|古村|峡谷|瀑布|湖泊)", 180, "景点基础信息"),
    (r".", 60, "未分类"),
]
TITLE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_")

def get_token():
    auth_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    body = json.dumps({
        "app_id": os.environ["FEISHU_APP_ID"],
        "app_secret": os.environ["FEISHU_APP_SECRET"],
    })
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", auth_url,
         "-H", "Content-Type: application/json", "-d", body],
        capture_output=True, text=True, timeout=15)
    d = json.loads(r.stdout)
    t = d.get("tenant_access_token", "")
    if not t:
        print("TOKEN ERROR: " + str(d), file=sys.stderr)
        sys.exit(1)
    return t

def feishu_get(token, path_and_qs):
    """Make a GET request to Feishu API with auth header."""
    url = "https://open.feishu.cn/open-apis" + path_and_qs
    auth_val = "Bearer" + " " + token
    for attempt in range(3):
        try:
            r = subprocess.run(
                ["curl", "-s", "--connect-timeout", "10", "--max-time", "60",
                 url, "-H", "Authorization:" + " " + auth_val],
                capture_output=True, text=True, timeout=65)
            return json.loads(r.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            if attempt < 2:
                time.sleep(5)
            else:
                return {"code": -1, "msg": "timeout after 3 retries"}

def list_docs(token, parent_token):
    """Fetch all leaf docx docs under a parent node."""
    items = []
    pt = None
    base_qs = "/wiki/v2/spaces/" + SPACE_ID + "/nodes?parent_node_token=" + parent_token + "&page_size=50"
    while True:
        qs = base_qs
        if pt:
            qs = qs + "&page_token=" + pt
        data = feishu_get(token, qs)
        if data.get("code") != 0:
            msg = str(data.get("msg", ""))[:60]
            print("  API ERROR: " + msg, file=sys.stderr)
            break
        batch = data.get("data", {}).get("items", [])
        items.extend(batch)
        if not data.get("data", {}).get("has_more"):
            break
        pt = data["data"]["page_token"]
    return [it for it in items if it.get("obj_type") == "docx" and not it.get("has_child")]

def classify(title):
    for pat, days, lbl in RULES:
        if re.search(pat, title):
            return lbl, days
    return "未分类", 60

def get_date(item):
    title = item.get("title", "")
    m = TITLE_RE.match(title)
    if m:
        try:
            return date.fromisoformat(m.group(1))
        except ValueError:
            pass
    ts = item.get("obj_edit_time")
    if ts:
        try:
            return datetime.fromtimestamp(int(ts), tz=TZ).date()
        except:
            pass
    return None

def add_comment(doc_token, text):
    env = os.environ.copy()
    env["PATH"] = os.path.expanduser("~/.local/bin") + ":" + env.get("PATH", "")
    cj = json.dumps([{"type": "text", "text": text}], ensure_ascii=False)
    r = subprocess.run(
        ["lark-cli", "drive", "+add-comment",
         "--doc", doc_token, "--type", "docx", "--full-comment",
         "--content", cj, "--as", "bot"],
        capture_output=True, text=True, timeout=15, env=env)
    raw = r.stdout.strip() or r.stderr.strip()
    try:
        resp = json.loads(raw)
        return resp.get("ok") is True or resp.get("code") == 0
    except:
        return "ok" in raw.lower()

def main():
    print("=" * 60)
    print("Travel Intel Expiry Check v3")
    print("Time: " + datetime.now(TZ).strftime("%Y-%m-%d %H:%M") + " CST")
    print("=" * 60)

    print("\nGetting token...")
    token = get_token()
    print("OK")

    all_docs = []
    for label, ntoken in TARGET_NODES:
        print("\nNode: " + label + " (" + ntoken[:12] + "...)")
        docs = list_docs(token, ntoken)
        print("  " + str(len(docs)) + " docs")
        for d in docs:
            d["_label"] = label
        all_docs.extend(docs)

    print("\nTotal: " + str(len(all_docs)) + " docs")

    no_date = 0
    expired = []
    skipped = 0
    cc = Counter()
    ab = Counter()
    ds = {"title": 0, "edit_time": 0, "none": 0}

    for doc in all_docs:
        title = doc.get("title", "")
        lbl, days = classify(title)
        cc[lbl] += 1

        dd = get_date(doc)
        if dd is None:
            no_date += 1
            ds["none"] += 1
            continue

        if TITLE_RE.match(title):
            ds["title"] += 1
        else:
            ds["edit_time"] += 1

        age = max(0, (TODAY - dd).days)
        if age <= 7: ab["0-7d"] += 1
        elif age <= 30: ab["8-30d"] += 1
        elif age <= 90: ab["31-90d"] += 1
        elif age <= 180: ab["91-180d"] += 1
        else: ab["181+d"] += 1

        if age > days:
            expired.append({
                "title": title, "node": doc.get("_label"),
                "token": doc.get("obj_token") or doc.get("node_token"),
                "age": age, "cat": lbl, "thresh": days
            })
        else:
            skipped += 1

    marked = 0
    merr = 0
    if expired:
        print("\n" + str(len(expired)) + " expired, marking...")
        for i, e in enumerate(expired):
            over = e["age"] - e["thresh"]
            cmt = "[EXPIRED] cat:" + e["cat"] + " thresh:" + str(e["thresh"]) + "d age:" + str(e["age"]) + "d over:" + str(over) + "d"
            ok = add_comment(e["token"], cmt)
            if ok:
                marked += 1
                if i < 3 or i == len(expired) - 1:
                    print("  [" + str(i+1) + "/" + str(len(expired)) + "] OK " + e["title"][:60])
            else:
                merr += 1
                print("  [" + str(i+1) + "/" + str(len(expired)) + "] FAIL " + e["title"][:60])
            time.sleep(0.5)
    else:
        print("\nNo expired docs")

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    nc = Counter(d["_label"] for d in all_docs)
    for lbl, _ in TARGET_NODES:
        nc.setdefault(lbl, 0)

    print("\ntotal_docs: " + str(len(all_docs)))
    print("industry: " + str(nc.get("industry", 0)))
    print("competitor: " + str(nc.get("competitor", 0)))
    print("expired: " + str(len(expired)))
    print("marked: " + str(marked))
    print("skipped: " + str(skipped))
    print("errors: " + str(merr))
    print("no_date: " + str(no_date))

    print("\nAge distribution:")
    td = sum(ab.values())
    for b in ["0-7d", "8-30d", "31-90d", "91-180d", "181+d"]:
        c = ab.get(b, 0)
        p = round(c / td * 100, 1) if td > 0 else 0
        print("  " + b + ": " + str(c) + " (" + str(p) + "%)")

    print("\nCategory distribution (top 8):")
    lt = {lbl: days for _, days, lbl in RULES}
    for cls, cnt in cc.most_common(8):
        th = lt.get(cls, 60)
        print("  " + cls + ": " + str(cnt) + " (thresh=" + str(th) + "d)")

    print("\nDate source:")
    print("  title_prefix: " + str(ds["title"]))
    print("  obj_edit_time: " + str(ds["edit_time"]))
    print("  none: " + str(ds["none"]))

    if expired:
        print("\nExpired details:")
        for e in expired[:20]:
            print("  - " + e["title"][:80])
            print("    node=" + str(e["node"]) + " cat=" + e["cat"] + " age=" + str(e["age"]) + "d thresh=" + str(e["thresh"]) + "d")
        if len(expired) > 20:
            print("  ... and " + str(len(expired) - 20) + " more")

    print("\nDone: " + datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S") + " CST")

if __name__ == "__main__":
    main()
