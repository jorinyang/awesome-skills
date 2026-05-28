#!/usr/bin/env python3
"""
Wiki Monitor — Daily knowledge base monitoring and change tracking.

Intended to be run as a cron job script (no_agent=true) that:
1. Scans the wiki structure
2. Compares with last snapshot
3. Generates changelog and homepage XML
4. Outputs change summary for delivery

The actual docx writes are handled by the agent prompt in the cron job.
"""

import json, os, sys, subprocess, datetime
from pathlib import Path

SPACE_ID = "7643710721485753535"
SNAPSHOT_FILE = Path.home() / ".hermes-feishu" / "cron" / "wiki_snapshot.json"

# Import explorer functions (same directory)
sys.path.insert(0, str(Path(__file__).parent))
from wiki_explorer import (
    get_token, explore_space, detect_misplacements,
    compare_snapshots, generate_homepage_xml, generate_changelog_xml,
    save_snapshot, load_snapshot
)


def main():
    token = get_token()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 1. Explore current structure
    categories, all_docs = explore_space(token)
    
    # 2. Compare with last snapshot
    old = load_snapshot()
    has_changes = False
    changes = {"added": [], "removed": [], "moved": [], "updated": []}
    
    if old:
        changes = compare_snapshots(old, {"categories": categories})
        has_changes = any(v for v in changes.values())
    
    # 3. Detect misplacements
    misplacements = detect_misplacements(categories)
    
    # 4. Generate homepage XML (always regenerate for up-to-date counts)
    homepage_xml = generate_homepage_xml(categories, timestamp)
    homepage_path = Path("/tmp/wiki_homepage.xml")
    homepage_path.write_text(homepage_xml)
    
    # 5. If changes exist, generate changelog entry
    changelog_entry = ""
    if has_changes or misplacements:
        changelog_entry = generate_changelog_xml(changes, misplacements, timestamp)
    
    changelog_path = Path("/tmp/wiki_changelog_entry.xml")
    changelog_path.write_text(changelog_entry) if changelog_entry else changelog_path.write_text("")
    
    # 6. Save new snapshot
    snapshot_path = save_snapshot(categories, timestamp)
    
    # 7. Build summary for delivery
    total_docs = len(all_docs)
    total_cats = len(categories)
    
    summary_parts = [f"📊 知识库巡检 ({timestamp})"]
    summary_parts.append(f"  {total_cats} 个分类，{total_docs} 篇文档")
    
    if has_changes:
        summary_parts.append(f"\n📝 变动检测：")
        if changes["added"]:
            for d in changes["added"]:
                summary_parts.append(f"  + {d['title'][:50]} → {d['category']}")
        if changes["removed"]:
            for d in changes["removed"]:
                summary_parts.append(f"  - {d['title'][:50]} (原{d['category']})")
        if changes["moved"]:
            for d in changes["moved"]:
                summary_parts.append(f"  → {d['title'][:50]}：{d['old_category']} → {d['category']}")
        if changes["updated"]:
            summary_parts.append(f"  ✏️ {len(changes['updated'])} 篇文档内容更新")
    else:
        summary_parts.append(f"  ✅ 无结构变动")
    
    if misplacements:
        summary_parts.append(f"\n⚠️ 分类建议 ({len(misplacements)}条)：")
        for m in misplacements[:5]:
            summary_parts.append(f"  • {m['title'][:40]} → {m['suggested']}（当前：{m['current']}）")
        if len(misplacements) > 5:
            summary_parts.append(f"  ...共 {len(misplacements)} 条")
    
    summary_parts.append(f"\n📄 快照: {snapshot_path}")
    summary_parts.append(f"📄 首页XML: {homepage_path}")
    if changelog_entry:
        summary_parts.append(f"📄 变更条目: {changelog_path}")
    
    print("\n".join(summary_parts))


if __name__ == "__main__":
    main()
