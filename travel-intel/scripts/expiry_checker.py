#!/usr/bin/env python3
"""过期校验 — 扫描 Wiki 节点 → 匹配15类规则 → 添加评论标记
v2: 使用 REST API 获取 obj_edit_time 作为日期回退；支持 YYYY_WW周_ 格式

Usage:
    python3 expiry_checker.py [--dry-run]
"""

import argparse, datetime, json, logging, os, re, subprocess, sys, time, yaml

log = logging.getLogger(__name__)
RULES_FILE = os.path.join(os.path.dirname(__file__), "..", "references", "expiry-rules.yaml")
NODES = ["V0Lhwl7KYiWYDDk1vCncv2GhnYf", "EAMYw1CPoipVWtkObbtcR2oDnNc",
         "UF7Cw5w2WiHGfjkKVvBcxj8Hnib"]
SPACE_ID = "7643710721485753535"
TZ = datetime.timezone(datetime.timedelta(hours=8))
TIMEOUT = 20
PAGE_SIZE = 50

# Date patterns: YYYY-MM-DD_ or YYYY_WW周_
TITLE_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})_")
WEEK_TITLE_RE = re.compile(r"^(\d{4})_(\d{1,2})周_")

# Cache for tenant_access_token
_token_cache = {"token": None, "expires_at": 0}


def get_tenant_token():
    """Get tenant_access_token, with 1-hour cache."""
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"]:
        return _token_cache["token"]
    app_id = os.environ.get("FEISHU_APP_ID", "")
    app_secret = os.environ.get("FEISHU_APP_SECRET", "")
    r = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
         "-H", "Content-Type: application/json",
         "-d", json.dumps({"app_id": app_id, "app_secret": app_secret})],
        capture_output=True, text=True, timeout=TIMEOUT,
    )
    data = json.loads(r.stdout)
    token = data["tenant_access_token"]
    _token_cache["token"] = token
    _token_cache["expires_at"] = now + 3600  # 1 hour
    return token


def parse_title_date(title):
    """Parse date from title. Supports YYYY-MM-DD_ and YYYY_WW周_ patterns."""
    m = TITLE_DATE_RE.match(title)
    if m:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = WEEK_TITLE_RE.match(title)
    if m:
        year, week = int(m.group(1)), int(m.group(2))
        # Week N Monday: Jan 1 + (week-1)*7 days, adjusted to Monday
        jan1 = datetime.date(year, 1, 1)
        # ISO week: Monday of week N
        days_offset = (week - 1) * 7 - jan1.weekday()
        return jan1 + datetime.timedelta(days=days_offset)
    return None


def parse_unix_time(ts_str):
    """Parse Unix timestamp string to date in Asia/Shanghai timezone."""
    if not ts_str:
        return None
    try:
        ts = int(ts_str)
        return datetime.datetime.fromtimestamp(ts, tz=TZ).date()
    except (ValueError, OSError):
        return None


def load_rules():
    with open(RULES_FILE) as f:
        return yaml.safe_load(f).get("rules", [])


def classify_doc(title):
    """Classify document by title keywords, return rule type name."""
    title_lower = title.lower()
    if any(k in title_lower for k in ["价格", "门票", "免票", "优惠", "票价", "收费"]):
        if any(k in title_lower for k in ["酒店", "交通", "机票", "高铁", "大巴"]):
            return "酒店/交通价格"
        return "门票/开放时间"
    if any(k in title_lower for k in ["酒店", "民宿", "度假村", "住宿", "康养", "旅居", "研学"]):
        if any(k in title_lower for k in ["开业", "新开", "设施"]):
            return "酒店设施/交通线路"
        return "酒店/交通价格"
    if any(k in title_lower for k in ["交通", "高铁", "航线", "高速", "通车"]):
        return "酒店设施/交通线路"
    if any(k in title_lower for k in ["节庆", "赛事", "活动", "音乐节", "嘉年华", "庙会",
                                       "端午", "中秋", "国庆", "春节", "五一", "十一"]):
        return "节庆/活动"
    if any(k in title_lower for k in ["攻略", "游记", "马蜂窝", "携程", "点评", "推荐", "户外", "徒步"]):
        return "攻略/游记/评价"
    if any(k in title_lower for k in ["报告", "趋势", "洞察", "分析", "周度", "综合"]):
        return "行业报告/趋势"
    if any(k in title_lower for k in ["政策", "规定", "通知", "方案", "文旅厅", "人民政府", "国务院"]):
        if any(k in title_lower for k in ["国务院", "国家", "部委", "中央"]):
            return "政策法规（国家级）"
        return "政策法规（地方/临时）"
    if any(k in title_lower for k in ["免票", "优惠", "文旅"]):
        return "政策法规（地方/临时）"
    if any(k in title_lower for k in ["竞品", "探洞", "天坑", "桨板", "sup", "溯溪", "漂流"]):
        if any(k in title_lower for k in ["价格"]):
            return "竞品价格"
        if any(k in title_lower for k in ["社媒", "社交", "话题"]):
            return "竞品社媒动态"
        return "竞品新品/营销"
    if any(k in title_lower for k in ["话题", "热搜", "热议"]):
        return "社媒热议话题"
    if any(k in title_lower for k in ["季节", "春季", "夏季", "秋季", "冬季", "赏花", "避暑", "滑雪"]):
        return "季节性信息"
    if any(k in title_lower for k in ["景点", "景区", "5a"]):
        return "景点基础信息"
    return None


def check_expiry(doc, rules):
    """Check if document is expired. Returns (age_days, rule) or (0, None)."""
    title = doc.get("title", "")
    doc_date = parse_title_date(title)
    # Fallback: use obj_edit_time if title date not parseable
    if not doc_date:
        doc_date = parse_unix_time(doc.get("obj_edit_time"))

    if not doc_date:
        return 0, None

    today = datetime.datetime.now(TZ).date()
    age = (today - doc_date).days
    if age <= 0:
        return 0, None

    rule_type = classify_doc(title)
    if not rule_type:
        # Fallback: use broadest threshold (180 days)
        if age > 180:
            return age, {"type": "攻略/游记/评价", "days": 180, "weight": 0.6,
                         "label": "⚠️ 时效性降低"}
        return 0, None

    for rule in rules:
        if rule["type"] == rule_type:
            rd = rule.get("days")
            if rd and age > rd:
                return age, rule
            return 0, None
    return 0, None


def list_docs(node_token):
    """List all docs in a Wiki node using REST API (returns obj_edit_time)."""
    token = get_tenant_token()
    docs = []
    page_token = None
    while True:
        url = (f"https://open.feishu.cn/open-apis/wiki/v2/spaces/{SPACE_ID}"
               f"/nodes?parent_node_token={node_token}&page_size={PAGE_SIZE}")
        if page_token:
            url += f"&page_token={page_token}"
        auth_hdr = "Authorization: Bearer " + token
        r = subprocess.run(
            ["curl", "-s", url, "-H", auth_hdr],
            capture_output=True, text=True, timeout=TIMEOUT,
        )
        try:
            data = json.loads(r.stdout)
            inner = data.get("data", data)
            nodes = inner.get("nodes", inner.get("items", []))
            if not nodes:
                break
            docs.extend([
                {
                    "title": n.get("title", ""),
                    "obj_token": n.get("obj_token", ""),
                    "node": node_token,
                    "obj_edit_time": n.get("obj_edit_time", ""),
                }
                for n in nodes if n.get("obj_type") == "docx"
            ])
            has_more = inner.get("has_more", False)
            page_token = inner.get("page_token") if has_more else None
            if not has_more:
                break
        except json.JSONDecodeError:
            break
    return docs


def mark_expired(doc, rule, age, dry_run=False):
    """Add expiry comment to document."""
    comment = (f"[{rule.get('type','UNKNOWN')}] AGE:{age}d "
               f"WT:x{rule.get('weight',0):.1f}")
    if dry_run:
        log.info("[DRY RUN] %s → %s", doc["title"][:60], comment)
        return True
    env = os.environ.copy()
    # 2026-07-03: Windows npm lark-cli is lark-cli.cmd — plain "lark-cli" fails FileNotFoundError.
    # Use explicit .cmd suffix on Windows; append Aorus npm dir (system user expanduser resolves wrong).
    aorus_npm = r"C:\Users\Aorus\AppData\Roaming\npm"
    if os.path.isdir(aorus_npm) and aorus_npm not in env.get("PATH", ""):
        env["PATH"] = aorus_npm + os.pathsep + env["PATH"]
    lark_bin = "lark-cli.cmd" if os.name == "nt" else "lark-cli"
    r = subprocess.run(
        [lark_bin, "drive", "+add-comment", "--type", "docx",
         "--doc", doc["obj_token"], "--full-comment", "--as", "bot",
         "--content", json.dumps([{"type": "text", "text": comment}])],
        capture_output=True, text=True, timeout=TIMEOUT, env=env,
    )
    log.info("Marked: %s (rc=%d)", doc["title"][:60], r.returncode)
    return r.returncode == 0


def run(dry_run=False):
    rules = load_rules()
    log.info("loaded %d rules", len(rules))

    all_docs = []
    for node in NODES:
        docs = list_docs(node)
        all_docs.extend(docs)
        log.info("node %s: %d docs", node[-8:], len(docs))

    stats = {"total": len(all_docs), "expired": 0, "marked": 0,
             "skipped": 0, "errors": 0, "no_date": 0}
    expired = []

    for doc in all_docs:
        age, rule = check_expiry(doc, rules)
        if rule is None:
            stats["skipped"] += 1
            # Track how many have no date at all
            if not parse_title_date(doc.get("title", "")) and not parse_unix_time(doc.get("obj_edit_time")):
                stats["no_date"] += 1
            continue
        stats["expired"] += 1
        expired.append({
            "title": doc["title"],
            "age_days": age,
            "type": rule["type"],
            "label": rule.get("label", ""),
        })
        if mark_expired(doc, rule, age, dry_run):
            stats["marked"] += 1
            time.sleep(1)  # rate limit
        else:
            stats["errors"] += 1

    log.info("done: %s", json.dumps(stats, ensure_ascii=False))
    return {"stats": stats, "expired": expired}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    result = run(args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
