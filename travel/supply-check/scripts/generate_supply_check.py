#!/usr/bin/env python3
"""贵州之客物资核对清单生成器 — supply-check
用法: python3 generate_supply_check.py <trip_json_path>
输出: ~/.hermes-feishu/cache/supply_check_{团号}.md + 飞书docx
"""

import json, sys, subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path.home() / ".hermes-feishu/cache"
PARENT_TOKEN = "HmnBwlKhsixk45kjNa9cmCRDndb"  # 03-出团执行


def esc(t): 
    return str(t).replace("\\","\\\\").replace("`","\\`").replace("|","\\|")


def build_markdown(trip):
    g = trip["group"]
    lines = [
        f"# 物资核对清单 — {esc(g['name'])}",
        f"",
        f"> 团号：{esc(g['id'])} | 出团日期：{esc(g['dates']['start'])} | 核对人：_______ | 日期：_______",
        f"",
        f"## 核对总览",
        f"",
    ]
    
    # Count by category
    for cat in trip.get("supplies", []):
        total_items = len(cat["items"])
        total_qty = sum(item["qty"] for item in cat["items"])
        lines.append(f"- **{esc(cat['category'])}**：{total_items} 种 · 共约 {total_qty} 件")

    lines.extend(["", "---", "", "## 逐项核对", ""])
    
    for cat in trip.get("supplies", []):
        lines.append(f"### {esc(cat['category'])}")
        lines.append("")
        lines.append("| 序号 | 物资 | 数量 | 核对 ☐ | 备注 |")
        lines.append("|------|------|------|---------|------|")
        for i, item in enumerate(cat["items"], 1):
            qty = f"{item['qty']}{item.get('unit','')}"
            lines.append(f"| {i} | {esc(item['name'])} | {esc(qty)} | ☐ | {esc(item.get('note',''))} |")
        lines.append("")
        lines.append(f"**{esc(cat['category'])} 核对人签字：_______**")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## 核对规则",
        "",
        "1. 出团前 24 小时完成全部核对",
        "2. 每项物资逐件清点，不跳项、不凭记忆",
        "3. 急救包检查有效期，过期须更换",
        "4. 电子设备（对讲机/头灯）充足电并测试",
        "5. 发现问题立即备注并通知计调",
        "",
        f"**总核对人签字：_______**  **计调确认：_______**",
    ])
    return "\n".join(lines)


def create_feishu(md, title, parent_token):
    md_path = OUTPUT_DIR / f"supply_check_{title}.md"
    with open(md_path, "w") as f: f.write(md)
    cmd = ["lark-cli","docs","+create","--api-version","v2","--doc-format","markdown",
           "--content",f"@{md_path.name}","--parent-token",parent_token,"--as","bot"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(OUTPUT_DIR), timeout=30)
    if r.returncode == 0:
        return json.loads(r.stdout).get("data",{}).get("document",{}).get("url",""), str(md_path)
    return None, str(md_path)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_supply_check.py <trip_json>"); sys.exit(1)
    trip = json.load(open(sys.argv[1]))
    md = build_markdown(trip)
    title = f"物资核对_{trip['group']['id']}"
    url, local = create_feishu(md, title, PARENT_TOKEN)
    print(f"✅ 物资核对清单")
    print(f"   {'飞书: '+url if url else '本地: '+local}")
    return url or local

if __name__ == "__main__":
    main()
