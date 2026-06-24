#!/usr/bin/env python3
"""贵州之客团后归档器 — trip-archive
用法: python3 trip_archive.py <trip_json_path>
输出: 飞书归档节点 + 归档报告
"""

import json, sys, subprocess
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path.home() / ".hermes-feishu/cache"
SKILL_DIR = Path(__file__).resolve().parent.parent

KB_NODES = {
    "01-产品研发": {"token": "XysVwyHOmiOOstkCjj9cXDBlnQb", "docs": ["路线方案", "成本核算"]},
    "02-销售转化": {"token": "Rcdow4tcRiYL88kwCZDcjNw8nBf", "docs": ["报价单", "合同"]},
    "03-出团执行": {"token": "HmnBwlKhsixk45kjNa9cmCRDndb", "docs": ["出团通知书", "导游执行单", "物资核对"]},
    "04-供应商对接": {"token": "HbYIw1R93ihXRFkwgZ5cPmWnneb", "docs": ["酒店对接", "车辆对接", "地接对接"]},
    "05-归档结算": {"token": "KuyvwJWGki1D7vkBslWchymWn2f", "docs": ["团后总结", "财务结算"]},
}

def esc(t): return str(t).replace("\\","\\\\").replace("|","\\|")

def build_summary(trip, archive_links):
    """Build archive summary markdown"""
    g = trip["group"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = [
        f"# 团档 — {esc(g['name'])}",
        f"",
        f"> 团号：{esc(g['id'])} | 归档时间：{now}",
        f"",
        f"## 基本信息",
        f"",
        f"| 项目 | 内容 |",
        f"|------|------|",
        f"| 团号 | {esc(g['id'])} |",
        f"| 日期 | {esc(g['dates']['start'])} — {esc(g['dates']['end'])} |",
        f"| 人数 | {g['size']['total']}人 |",
        f"| 客户 | {esc(g['customer']['company'])} |",
        f"| 导游 | {esc(g['guide']['name'])} |",
        f"| 类型 | {esc(g.get('type','团建'))} |",
        f"",
        f"## 归档文档",
        f"",
    ]
    
    for node_name, docs in archive_links.items():
        lines.append(f"### {node_name}")
        for doc_name, url in docs:
            lines.append(f"- [{esc(doc_name)}]({url})")
        lines.append("")
    
    lines.extend([
        f"## 归档完成确认",
        f"",
        f"- ☐ 所有文档已归档至对应知识库节点",
        f"- ☐ 客户反馈已收集",
        f"- ☐ 财务结算已完成",
        f"- ☐ 物资已归还入库",
        f"",
        f"**归档人：_______** **日期：_______**",
    ])
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 trip_archive.py <trip_json>"); sys.exit(1)
    
    trip = json.load(open(sys.argv[1]))
    g = trip["group"]
    
    # Map existing docs to KB nodes
    archive_links = {}
    
    # Check which docs exist in cache
    cache_files = list(OUTPUT_DIR.glob(f"*{g['id']}*"))
    
    for f in cache_files:
        name = f.stem
        for node_name, info in KB_NODES.items():
            for doc_type in info["docs"]:
                if doc_type.replace(" ","").lower() in name.lower():
                    if node_name not in archive_links:
                        archive_links[node_name] = []
                    archive_links[node_name].append((doc_type, f"file://{f}"))
                    break
    
    # Build summary and create Feishu doc
    md = build_summary(trip, archive_links if archive_links else {n: [("待补充", "")] for n in KB_NODES})
    
    md_path = OUTPUT_DIR / f"archive_{g['id']}.md"
    with open(md_path, "w") as f: f.write(md)
    
    # Create in 05-归档结算
    cmd = ["lark-cli","docs","+create","--api-version","v2","--doc-format","markdown",
           "--content",f"@{md_path.name}","--parent-token",KB_NODES["05-归档结算"]["token"],"--as","bot"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(OUTPUT_DIR), timeout=30)
    url = None
    if r.returncode == 0:
        url = json.loads(r.stdout).get("data",{}).get("document",{}).get("url","")
    
    print(f"✅ 团后归档完成")
    print(f"   {'飞书: '+url if url else '本地: '+str(md_path)}")
    print(f"   团号: {g['id']}")
    
    if archive_links:
        for node, docs in archive_links.items():
            print(f"   {node}: {len(docs)}份文档")
    
    return url or str(md_path)

if __name__ == "__main__":
    main()
