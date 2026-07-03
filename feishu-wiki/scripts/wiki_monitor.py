#!/usr/bin/env python3
"""Wiki Monitor"""
import os, sys, json, subprocess, time, re, hashlib
from datetime import datetime, timezone, timedelta
from collections import defaultdict

SPACE_ID = "7643710721485753535"
HPT = "Y4LYd1X8Yo1Du9x9WtNcYD51nte"
CLT = "LJ7RdGzVVoUX6rxmzwpcH3L0npg"
CHANGELOG_TOKEN = CLT

# Auto-collected industry news → default to 行业资讯
INDUSTRY_NEWS_TOKEN = "V0Lhwl7KYiWYDDk1vCncv2GhnYf"
AUTO_COLLECT_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}_(pinchain|wenlv|meadin\w*|other)_')

CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST)
TODAY_STR = NOW.strftime("%Y-%m-%d")
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M")

SUMMARY_CACHE = os.path.expanduser("~/.hermes-feishu/cron/wiki_summaries.json")
SNAPSHOT_FILE = os.path.expanduser("~/.hermes-feishu/scripts/.wiki_snapshot")

CATEGORIES = [
    ("企业文化", "KqoZwqut8ilTSFk3SX4cOpQ9nZf", "价值观、使命、愿景、文化、团建、年会"),
    ("团队管理", "PAVdwkNpNiedvfkPLIec1gK7nAU", "组织架构、KPI、OKR、招聘、绩效、培训"),
    ("产品研发", "HrJXwlne7ioywnkDpAlc6p08ngV", "产品、研发、技术、开发、测试、上线"),
    ("运营策略", "JIKCw1IXAi5ZYxkBKW0cYEuanGF", "运营、推广、渠道、用户增长、转化、冷启动、销售、营销"),
    ("业务规范", "FB6DwZlXhijL38k0z6Jcy8znhd", "SOP、流程、规范、标准、协议、制度、授权书、合同"),
    ("会议纪要", "GI1cwlAUviHXIqk291vcjNxvnGb", "会议、纪要、周会、月会、评审、复盘"),
    ("方案计划", "KVPTwrbOKiQMUkkUPlscaEKfnUd", "方案、计划、规划、策划、提案、研学、游览"),
    ("汇报资料", "MebBwjMDgiUH4YkNeEmcLhxFnrb", "汇报、报告、总结、述职、数据报告、洞察、分析、周报、周度"),
    ("文案素材", "J9h6wJgO4ij7NjkXNTCc6mNDnwf", "文案、素材、海报、话术、宣传、模板、脚本、笔记、品牌叙事"),
    ("行业资讯", "V0Lhwl7KYiWYDDk1vCncv2GhnYf", "行业、资讯、新闻、趋势、景点、旅游、文旅、景区、酒店、旅行社、OTA、携程、同程、出境、入境、民宿、航线、邮轮、目的地、签证、文化、机票、高铁、度假、康养、营地、温泉、简报"),
    ("竞品动态", "EAMYw1CPoipVWtkObbtcR2oDnNc", "竞品、竞争、对手、友商、对标"),
    ("AI Native 工作流", "J4EewYIT2ieFuwkRWbxcgWbFnhe", "AI、工作流、自动化、智能、agent、LLM、MCP、BRIEF、ARCHITECTURE、STANDARDS、TASKS、answer、技能化、蓝图"),
    ("最近更新", "LJ7RdGzVVoUX6rxmzwpcH3L0npg", "知识库变动日志"),
]

# Build lookup maps using simple loops (no dict/set comprehensions)
CAT_TOKEN_MAP = dict()
CATEGORY_TOKENS = set()
for _n, _t, _k in CATEGORIES:
    CAT_TOKEN_MAP[_t] = _n
    CATEGORY_TOKENS.add(_t)


def get_token():
    secret = os.environ.get("FEISHU_APP_SECRET", "")
    if not secret:
        try:
            with open(os.path.expanduser("~/.hermes-feishu/feishu_secret")) as f:
                secret = f.read().strip()
        except FileNotFoundError:
            pass
    if not secret:
        raise RuntimeError("FEISHU_APP_SECRET not set")
    app_id = os.environ.get("FEISHU_APP_ID", "cli_aa9ead14c2641cc3")
    r = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(dict(app_id=app_id, app_secret=secret))],
        capture_output=True, text=True, timeout=15)
    return json.loads(r.stdout).get("tenant_access_token", "")


def feishu_get(tok, path, params=None):
    url = "https://open.feishu.cn/open-apis" + path
    if params:
        parts = []
        for k, v in params.items():
            parts.append(k + "=" + str(v))
        url += "?" + "&".join(parts)
    auth_header = "Authorization: Bearer " + tok
    for attempt in range(3):
        try:
            r = subprocess.run(
                ["curl", "-s", "--connect-timeout", "10", "--max-time", "60",
                 url, "-H", auth_header],
                capture_output=True, text=True, timeout=65)
            return json.loads(r.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            if attempt < 2:
                time.sleep(3)
            else:
                return dict(code=-1, msg="timeout")
    return dict(code=-1, msg="unknown")


def list_all_nodes(token):
    all_nodes = []
    resp = feishu_get(token, "/wiki/v2/spaces/" + SPACE_ID + "/nodes",
                       dict(page_size=50))
    if resp.get("code") != 0:
        print("ERROR root: " + str(resp.get("msg", "")), file=sys.stderr)
        return all_nodes
    root_items = resp.get("data", dict()).get("items", [])
    all_nodes.extend(root_items)
    for node in root_items:
        if not node.get("has_child"):
            continue
        p_token = node["node_token"]
        page_token = None
        while True:
            p = dict(parent_node_token=p_token, page_size=50)
            if page_token:
                p["page_token"] = page_token
            cr = feishu_get(token, "/wiki/v2/spaces/" + SPACE_ID + "/nodes", p)
            if cr.get("code") != 0:
                break
            children = cr.get("data", dict()).get("items", [])
            for child in children:
                child["_parent_token"] = p_token
                all_nodes.append(child)
            if not cr.get("data", dict()).get("has_more"):
                break
            page_token = cr["data"]["page_token"]
    return all_nodes


def load_summary_cache():
    try:
        with open(SUMMARY_CACHE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return dict()


def load_snapshot():
    try:
        with open(SNAPSHOT_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def save_snapshot(hash_val):
    with open(SNAPSHOT_FILE, "w") as f:
        f.write(hash_val)


def compute_snapshot(nodes):
    lines = []
    for n in nodes:
        parts = [
            str(n.get("node_token", "")),
            str(n.get("_parent_token", "")),
            str(n.get("obj_token", "")),
            str(n.get("title", "")),
            str(n.get("obj_edit_time", "")),
        ]
        lines.append("|".join(parts))
    lines.sort()
    return hashlib.md5("\n".join(lines).encode()).hexdigest()


def detect_doc_changes(nodes, summary_cache):
    docs_needing = []
    for n in nodes:
        if n.get("obj_type") != "docx":
            continue
        if n.get("has_child"):
            continue
        if n.get("title") in ("首页", "最近更新"):
            continue
        obj_token = n.get("obj_token", "")
        if not obj_token:
            continue
        edit_time = str(n.get("obj_edit_time", ""))
        parent_name = CAT_TOKEN_MAP.get(n.get("_parent_token", ""), "未知")
        cached = summary_cache.get(obj_token)
        if not cached:
            docs_needing.append(dict(
                obj_token=obj_token, title=n.get("title", ""),
                reason="new", parent=parent_name))
        elif cached.get("edit_time", "") != edit_time:
            docs_needing.append(dict(
                obj_token=obj_token, title=n.get("title", ""),
                reason="updated", parent=parent_name))
    return docs_needing


def generate_skeleton_xml(nodes_by_cat, doc_count):
    NL = "\n"
    lines = [
        "<title>首页</title>",
        "<p>&#x1f550; 最后更新：" + NOW_STR + " CST</p>",
        "<hr/>",
        "<h2>&#x1f4c2; 知识库目录</h2>",
        "<p>共 <b>12</b> 个分类，<b>" + str(doc_count) + "</b> 篇文档</p>",
        "<hr/>",
    ]
    for name, node_token, keywords in CATEGORIES:
        if node_token == CHANGELOG_TOKEN:
            continue
        docs = nodes_by_cat.get(node_token, [])
        count = len(docs)
        lines.append("<h3>&#x1f4c1; " + name + " (" + str(count) + "篇)</h3>")
        lines.append("<p><em>收录范围：" + keywords + " 等</em></p>")
        if docs:
            lines.append("<ul>")
            for doc in docs:
                title = doc.get("title", "无标题")
                ot = doc.get("obj_token", "")
                url = "https://acn3kz7weyc0.feishu.cn/docx/" + ot
                placeholder = "<!-- ##SUMMARY:" + ot + "## -->"
                lines.append('<li><a href="' + url + '">' + title + '</a>' + placeholder + '</li>')
            lines.append("</ul>")
        else:
            lines.append("<p>（暂无文档）</p>")
        lines.append("<hr/>")
    return NL.join(lines)


def generate_changelog_xml(docs_needing, has_structure_change, moves):
    NL = "\n"
    lines = [
        "<h2>" + TODAY_STR + " 知识库变动</h2>",
        "<p><em>&#x1f550; 检测时间：" + NOW_STR + " CST</em></p>",
    ]
    entries = []
    if has_structure_change:
        entries.append("&#x1f4c2; 知识库目录结构发生变动")
    entries.extend(moves)
    if docs_needing:
        new_count = sum(1 for d in docs_needing if d["reason"] == "new")
        update_count = sum(1 for d in docs_needing if d["reason"] == "updated")
        if new_count:
            entries.append("&#x1f4c4; 新增 " + str(new_count) + " 篇文档")
        if update_count:
            entries.append("&#x1f504; 更新 " + str(update_count) + " 篇文档")
    if not entries:
        lines.append("<p>&#x2705; 今日无变动</p>")
    else:
        lines.append("<ul>")
        for e in entries:
            lines.append("<li>" + e + "</li>")
        lines.append("</ul>")
    lines.append("<hr/>")
    return NL.join(lines)


def main():
    print("=" * 60)
    print("Wiki Monitor — 每日巡检")
    print("Time: " + NOW_STR + " CST")
    print("=" * 60)

    token = get_token()
    if not token:
        print("FATAL: Failed to get token", file=sys.stderr)
        sys.exit(1)
    print("\n[Token OK]")

    print("\n[Scanning...]")
    nodes = list_all_nodes(token)
    print("  Nodes: " + str(len(nodes)))

    doc_nodes = [n for n in nodes if n.get("obj_type") == "docx"
                 and not n.get("has_child")
                 and n.get("title") not in ("首页", "最近更新")]
    print("  Docs: " + str(len(doc_nodes)))

    nodes_by_cat = defaultdict(list)
    cascade_errors = []
    unclassified = 0
    for n in doc_nodes:
        parent = n.get("_parent_token", "")
        title = n.get("title", "")
        if parent in CATEGORY_TOKENS:
            nodes_by_cat[parent].append(n)
        else:
            # Source-based classification: auto-collected docs → 行业资讯
            if AUTO_COLLECT_PATTERN.match(title):
                nodes_by_cat[INDUSTRY_NEWS_TOKEN].append(n)
                continue
            title_lower = title.lower()
            best_score, best_cat = -1, None
            for name, cat_token, keywords in CATEGORIES:
                if cat_token == CHANGELOG_TOKEN:
                    continue
                score = sum(1 for kw in keywords.split("、") if kw.lower() in title_lower)
                if score > best_score:
                    best_score, best_cat = score, cat_token
            if best_score > 0 and best_cat:
                nodes_by_cat[best_cat].append(n)
            else:
                unclassified += 1
                cascade_errors.append("Unclassified: " + title)

    for ct in CATEGORY_TOKENS:
        nodes_by_cat.setdefault(ct, [])

    total_classified = 0
    for k, v in nodes_by_cat.items():
        if k in CATEGORY_TOKENS and k != CHANGELOG_TOKEN:
            total_classified += len(v)

    print("  Classified: " + str(total_classified) + ", Unclassified: " + str(unclassified))

    curr_hash = compute_snapshot(nodes)
    prev_hash = load_snapshot()
    has_changed = curr_hash != prev_hash
    print("\n[Changes: " + str(has_changed) + "]")

    cache = load_summary_cache()
    flat_docs = []
    for ct in CATEGORY_TOKENS:
        if ct != CHANGELOG_TOKEN:
            flat_docs.extend(nodes_by_cat[ct])
    docs_needing = detect_doc_changes(flat_docs, cache)
    print("  Need summaries: " + str(len(docs_needing)))

    # Output 1: Skeleton XML
    skeleton = generate_skeleton_xml(nodes_by_cat, total_classified)
    with open("/tmp/wiki_skeleton.xml", "w", encoding="utf-8") as f:
        f.write(skeleton)
    print("[Skeleton: " + str(len(skeleton)) + " chars]")

    # Output 2: Docs needing summary
    with open("/tmp/wiki_docs_needing_summary.json", "w", encoding="utf-8") as f:
        json.dump(docs_needing, f, ensure_ascii=False, indent=2)
    print("[Needing: " + str(len(docs_needing)) + " docs]")

    # Output 3: Changelog entry
    changelog = generate_changelog_xml(docs_needing, has_changed, [])
    with open("/tmp/wiki_changelog_entry.xml", "w", encoding="utf-8") as f:
        f.write(changelog)
    print("[Changelog: " + str(len(changelog)) + " chars]")

    # Output 4: Agent input
    healthy = unclassified <= 10
    agent_input = dict(
        space_id=SPACE_ID,
        timestamp=NOW_STR,
        docs_count=len(docs_needing),
        docs_needing_summary=docs_needing,
        summary_cache_path=SUMMARY_CACHE,
        docs_needing_summary_path="/tmp/wiki_docs_needing_summary.json",
        app_id=os.environ.get("FEISHU_APP_ID", "cli_aa9ead14c2641cc3"),
        cascade_check=dict(
            healthy=healthy,
            nodes_total=len(nodes),
            doc_nodes_total=len(doc_nodes),
            classified_total=total_classified,
            unclassified_total=unclassified,
            errors=cascade_errors,
        ),
    )
    with open("/tmp/wiki_agent_input.json", "w", encoding="utf-8") as f:
        json.dump(agent_input, f, ensure_ascii=False, indent=2)
    print("[Agent input done]")

    save_snapshot(curr_hash)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print("Nodes: " + str(len(nodes)))
    print("Docs: " + str(len(doc_nodes)))
    print("Classified: " + str(total_classified))
    print("Unclassified: " + str(unclassified))
    print("Structure changed: " + str(has_changed))
    print("Need summaries: " + str(len(docs_needing)))
    print("Cascade healthy: " + str(healthy))

    if docs_needing:
        new_c = sum(1 for d in docs_needing if d["reason"] == "new")
        upd_c = sum(1 for d in docs_needing if d["reason"] == "updated")
        print("  New: " + str(new_c) + ", Updated: " + str(upd_c))

    print("\nDone: " + NOW_STR + " CST")


if __name__ == "__main__":
    main()
