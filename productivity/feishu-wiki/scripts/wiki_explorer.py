#!/usr/bin/env python3
"""
Wiki Explorer — Full knowledge base directory exploration and snapshot generation.

Usage:
  python3 wiki_explorer.py              # Print directory structure as JSON
  python3 wiki_explorer.py --save       # Save snapshot to ~/.hermes-feishu/cron/wiki_snapshot.json
  python3 wiki_explorer.py --xml        # Generate homepage XML (print to stdout)
  python3 wiki_explorer.py --compare    # Compare current structure with last snapshot
"""

import json, os, sys, subprocess, datetime
from pathlib import Path

SPACE_ID = "7643710721485753535"
SNAPSHOT_FILE = Path.home() / ".hermes-feishu" / "cron" / "wiki_snapshot.json"
HOMEPAGE_OBJ = "Y4LYd1X8Yo1Du9x9WtNcYD51nte"
CHANGELOG_OBJ = "LJ7RdGzVVoUX6rxmzwpcH3L0npg"

# Category display names and their scope descriptions
CATEGORY_META = {
    "企业文化": "价值观、使命、愿景、文化 等",
    "团队管理": "组织架构、KPI、OKR、招聘 等",
    "产品研发": "产品、研发、技术、开发 等",
    "运营策略": "运营、推广、渠道、用户增长 等",
    "业务规范": "SOP、流程、规范、标准 等",
    "会议纪要": "会议记录、讨论纪要 等",
    "方案计划": "项目方案、执行计划、提案 等",
    "汇报资料": "汇报、报告、材料 等",
    "文案素材": "文案、素材、模板 等",
    "行业资讯": "酒店、交通、政策、活动、景点、竞品专题 等",
    "竞品动态": "竞品简报、竞品分析、动态汇总 等",
    "AI Native 工作流": "AI 工作流、技能、自动化 等",
}

# Naming convention rules for categorization
CATEGORY_RULES = [
    # (pattern_in_title, expected_category)
    # Order matters: first match wins. Put more specific patterns first.
    (r"竞品简报", "竞品动态"),
    (r"竞品分析", "竞品动态"),
    (r"^纪要_", "会议纪要"),
    (r"^\d{4}-\d{2}-\d{2}_酒店_", "行业资讯"),
    (r"^\d{4}-\d{2}-\d{2}_交通_", "行业资讯"),
    (r"^\d{4}-\d{2}-\d{2}_政策_", "行业资讯"),
    (r"^\d{4}-\d{2}-\d{2}_活动_", "行业资讯"),
    (r"^\d{4}-\d{2}-\d{2}_景点_", "行业资讯"),
    (r"^\d{4}-\d{2}-\d{2}_竞品_", "行业资讯"),
    (r"^\d{4}_\d{2}周_综合洞察", "行业资讯"),  # 综合洞察→行业资讯
    (r"^\d{4}_\d{2}周_竞品", "竞品动态"),      # 竞品周报→竞品动态
]


def get_token():
    """Get tenant access token from env vars."""
    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
         "-H", "Content-Type: application/json",
         "-d", json.dumps({"app_id": os.environ["FEISHU_APP_ID"],
                           "app_secret": os.environ["FEISHU_APP_SECRET"]})],
        capture_output=True, text=True, timeout=15
    )
    return json.loads(result.stdout)["tenant_access_token"]


def api_get(path, token):
    """Make a GET request to Feishu Open API."""
    result = subprocess.run(
        ["curl", "-s", f"https://open.feishu.cn/open-apis{path}",
         "-H", f"Authorization: Bearer {token}"],
        capture_output=True, text=True, timeout=15
    )
    return json.loads(result.stdout)


def get_summary(obj_token, token):
    """Get document content summary (first 150 chars)."""
    try:
        data = api_get(f"/docx/v1/documents/{obj_token}/raw_content", token)
        if data.get("code") == 0:
            content = data["data"]["content"]
            # Clean whitespace
            content = " ".join(content.split())[:150]
            return content
    except Exception:
        pass
    return ""


def explore_space(token, space_id=SPACE_ID):
    """Explore the full wiki space structure."""
    # Get root nodes
    root_data = api_get(f"/wiki/v2/spaces/{space_id}/nodes?page_size=50", token)
    root_nodes = root_data.get("data", {}).get("items", [])

    categories = {}
    all_docs = []
    
    for node in root_nodes:
        title = node["title"]
        nt = node["node_token"]
        has_child = node.get("has_child", False)
        obj_token = node.get("obj_token", "")
        obj_type = node.get("obj_type", "docx")
        obj_edit_time = node.get("obj_edit_time", "")

        children = []
        if has_child:
            child_data = api_get(
                f"/wiki/v2/spaces/{space_id}/nodes?page_size=50&parent_node_token={nt}",
                token
            )
            for c in child_data.get("data", {}).get("items", []):
                child_info = {
                    "title": c["title"],
                    "node_token": c["node_token"],
                    "obj_token": c.get("obj_token", ""),
                    "obj_type": c.get("obj_type", "docx"),
                    "obj_edit_time": c.get("obj_edit_time", ""),
                    "parent_node_token": nt,
                }
                children.append(child_info)
                all_docs.append(child_info)

        if title not in ["首页", "最近更新"]:
            categories[title] = {
                "node_token": nt,
                "obj_token": obj_token,
                "has_child": has_child,
                "children": children,
                "count": len(children),
            }

    return categories, all_docs


def detect_misplacements(categories):
    """Detect docs that are in the wrong category based on naming rules."""
    import re
    issues = []
    
    for cat_name, cat_info in categories.items():
        for doc in cat_info["children"]:
            title = doc["title"]
            for pattern, expected_cat in CATEGORY_RULES:
                if re.search(pattern, title):
                    if cat_name != expected_cat:
                        issues.append({
                            "title": title,
                            "current": cat_name,
                            "suggested": expected_cat,
                            "node_token": doc["node_token"],
                            "reason": f"命名规则匹配: {pattern}",
                        })
                    break  # First match wins
    
    return issues


def compare_snapshots(old, new):
    """Compare two snapshots and return changes."""
    changes = {"added": [], "removed": [], "moved": [], "updated": []}
    
    old_docs = {}
    for cat_name, cat_info in old.get("categories", {}).items():
        for doc in cat_info.get("children", []):
            old_docs[doc["node_token"]] = {**doc, "category": cat_name}
    
    new_docs = {}
    for cat_name, cat_info in new.get("categories", {}).items():
        for doc in cat_info.get("children", []):
            new_docs[doc["node_token"]] = {**doc, "category": cat_name}
    
    old_tokens = set(old_docs.keys())
    new_tokens = set(new_docs.keys())
    
    # Added docs
    for nt in new_tokens - old_tokens:
        changes["added"].append(new_docs[nt])
    
    # Removed docs
    for nt in old_tokens - new_tokens:
        changes["removed"].append(old_docs[nt])
    
    # Moved or updated docs
    for nt in old_tokens & new_tokens:
        old_doc = old_docs[nt]
        new_doc = new_docs[nt]
        
        if old_doc["category"] != new_doc["category"]:
            changes["moved"].append({
                **new_doc,
                "old_category": old_doc["category"],
            })
        elif old_doc.get("obj_edit_time") != new_doc.get("obj_edit_time"):
            changes["updated"].append(new_doc)
    
    return changes


def generate_homepage_xml(categories, timestamp):
    """Generate the homepage directory XML."""
    total_docs = sum(c["count"] for c in categories.values())
    total_cats = len(categories)
    
    xml = []
    xml.append(f"<title>首页</title>")
    xml.append(f"<p>🕐 最后更新：{timestamp} CST</p>")
    xml.append(f"<hr/>")
    xml.append(f"<h2>📂 知识库目录</h2>")
    xml.append(f"<p>共 <b>{total_cats}</b> 个分类，<b>{total_docs}</b> 篇文档</p>")
    xml.append(f"<hr/>")
    
    # Sort: folders with children first, then empty, then leaf docs
    sorted_cats = sorted(categories.items(), key=lambda x: (-x[1]["count"], x[0]))
    
    for cat_name, cat_info in sorted_cats:
        count = cat_info["count"]
        scope = CATEGORY_META.get(cat_name, "")
        
        xml.append(f"<h3>📁 {cat_name} ({count}篇)</h3>")
        if scope:
            xml.append(f"<p><em>收录范围：{scope}</em></p>")
        
        if count == 0:
            xml.append(f"<p>（暂无文档）</p>")
        else:
            xml.append(f"<ul>")
            for doc in cat_info["children"]:
                title = doc["title"]
                # Truncate very long titles
                if len(title) > 80:
                    title = title[:77] + "..."
                # Escape XML special chars in title
                title_escaped = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                url = f"https://acn3kz7weyc0.feishu.cn/wiki/{doc['node_token']}"
                xml.append(f'<li><a href="{url}">{title_escaped}</a></li>')
            xml.append(f"</ul>")
        xml.append(f"<hr/>")
    
    return "\n".join(xml)


def generate_changelog_xml(changes, misplacements, timestamp):
    """Generate the changelog XML for prepending."""
    date_str = timestamp[:10]
    entries = []
    
    if changes["added"]:
        for doc in changes["added"]:
            entries.append(f"<li>📂 新增文档：{doc['title'][:60]} → {doc['category']}</li>")
    
    if changes["removed"]:
        for doc in changes["removed"]:
            entries.append(f"<li>🗑️ 删除文档：{doc['title'][:60]}（原{doc['category']}）</li>")
    
    if changes["moved"]:
        for doc in changes["moved"]:
            entries.append(f"<li>📦 移动文档：{doc['title'][:60]} 从「{doc['old_category']}」→「{doc['category']}」</li>")
    
    if changes["updated"]:
        for doc in changes["updated"]:
            entries.append(f"<li>📝 内容更新：{doc['title'][:60]}</li>")
    
    if misplacements:
        for m in misplacements[:5]:  # Top 5 only
            entries.append(f"<li>⚠️ 分类建议：{m['title'][:40]} 当前在「{m['current']}」，建议移至「{m['suggested']}」</li>")
        if len(misplacements) > 5:
            entries.append(f"<li>⚠️ ...共 {len(misplacements)} 条分类建议</li>")
    
    if not entries:
        entries.append("<li>✅ 无变动</li>")
    
    xml = f"""<h2>{date_str} 知识库变动</h2>
<p><em>🕐 检测时间：{timestamp}</em></p>
<ul>
{chr(10).join(entries)}
</ul>
<hr/>"""
    
    return xml


def save_snapshot(categories, timestamp):
    """Save the current directory snapshot."""
    snapshot = {
        "scanned_at": timestamp,
        "space_id": SPACE_ID,
        "categories": {k: {
            "node_token": v["node_token"],
            "children": v["children"],
        } for k, v in categories.items()},
    }
    
    SNAPSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    
    return SNAPSHOT_FILE


def load_snapshot():
    """Load the last saved snapshot."""
    if SNAPSHOT_FILE.exists():
        with open(SNAPSHOT_FILE) as f:
            return json.load(f)
    return None


def main():
    token = get_token()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    categories, all_docs = explore_space(token)
    
    if "--save" in sys.argv:
        path = save_snapshot(categories, timestamp)
        print(f"Snapshot saved to {path}")
    
    elif "--compare" in sys.argv:
        old = load_snapshot()
        if not old:
            print("No previous snapshot found. Run with --save first.")
            sys.exit(1)
        changes = compare_snapshots(old, {"categories": categories})
        misplacements = detect_misplacements(categories)
        print(json.dumps({
            "changes": {k: [{"title": d["title"], "category": d.get("category", d.get("old_category", "?"))} for d in v] for k, v in changes.items() if v},
            "misplacements": misplacements,
        }, ensure_ascii=False, indent=2))
    
    elif "--xml" in sys.argv:
        xml = generate_homepage_xml(categories, timestamp)
        print(xml)
    
    elif "--misplacements" in sys.argv:
        misplacements = detect_misplacements(categories)
        print(json.dumps(misplacements, ensure_ascii=False, indent=2))
    
    else:
        # Default: print full structure
        output = {
            "scanned_at": timestamp,
            "total_categories": len(categories),
            "total_docs": len(all_docs),
            "categories": {k: {"count": v["count"], "children": [c["title"] for c in v["children"]]} for k, v in categories.items()},
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
