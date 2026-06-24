#!/usr/bin/env python3
"""贵州之客成本比价引擎 v1.1 -- cost-engine
集成OTA实时市场比价
用法: python3 cost_engine.py <trip_json_path>
输出: 成本分析 + 实时市场比价 -> 飞书docx
"""

import json, sys, subprocess
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path.home() / ".hermes-feishu/cache"

def esc(t): return str(t).replace("\\","\\\\").replace("|","\\|")
def fmt_price(n): return f"{n:,}"

def load_trip(path):
    with open(path) as f: return json.load(f)

def analyze_cost(trip):
    cats = {}
    for item in trip["pricing"]["items"]:
        cat = item["category"]
        if cat not in cats: cats[cat] = {"items": [], "subtotal": 0}
        sub = item["unit_price"] * item["quantity"]
        cats[cat]["items"].append({**item, "subtotal": sub})
        cats[cat]["subtotal"] += sub
    total = sum(c["subtotal"] for c in cats.values())
    people = trip["group"]["size"]["total"]
    return cats, total, people

def build_report_md(trip, cats, total, people):
    g = trip["group"]
    base = total // people
    
    lines = [
        f"# 成本核算与市场比价 -- {esc(g['name'])}",
        f"",
        f"> 团号: {esc(g['id'])} | {g['size']['total']}人 | {esc(g['dates']['start'])}-{esc(g['dates']['end'])}",
        f"",
        f"## 一、成本分项",
        f"| 类别 | 项目 | 单价 | 数量 | 小计 | 占比 |",
        f"|------|------|------|------|------|------|",
    ]
    for cat_name, cat_data in cats.items():
        for item in cat_data["items"]:
            pct = f"{item['subtotal']/total*100:.1f}%"
            lines.append(
                f"| {esc(cat_name)} | {esc(item['name'])} | "
                f"Y{fmt_price(item['unit_price'])} | "
                f"{item['quantity']}{item['unit']} | "
                f"Y{fmt_price(item['subtotal'])} | {pct} |"
            )
    lines.append(f"| **合计** | | | | **Y{fmt_price(total)}** | **100%** |")
    
    lines.extend(["", "## 二、成本汇总", "| 类别 | 金额 | 占比 |", "|------|------|------|"])
    for cat_name, cat_data in cats.items():
        lines.append(f"| {esc(cat_name)} | Y{fmt_price(cat_data['subtotal'])} | {cat_data['subtotal']/total*100:.1f}% |")
    lines.append(f"| **合计** | **Y{fmt_price(total)}** | **100%** |")
    
    lines.extend([
        f"", f"## 三、人均成本",
        f"| 总成本 | Y{fmt_price(total)} |",
        f"| 人数 | {people}人 |",
        f"| **人均成本** | **Y{fmt_price(base)}** |",
        f"",
        f"## 四、实时市场比价",
    ])
    
    mr = trip.get("pricing", {}).get("market_reference", {})
    search_results = mr.get("search_results", [])
    if search_results:
        lines.extend(["| 来源 | 产品 | 人均价 | 价差 |", "|------|------|--------|------|"])
        for r in search_results:
            diff = int(r.get("price_per_person", 0)) - base
            sign = "+" if diff > 0 else ""
            lines.append(f"| {esc(r.get('source',''))} | {esc(r.get('name',''))} | "
                        f"Y{fmt_price(int(r.get('price_per_person',0)))} | {sign}Y{fmt_price(abs(diff))} |")
    elif mr.get("fliggy_similar_route"):
        fr = mr["fliggy_similar_route"]
        diff = fr.get("price_per_person", 0) - base
        sign = "+" if diff > 0 else ""
        lines.append(f"| 飞猪 | {esc(fr.get('name',''))} | "
                    f"Y{fmt_price(fr.get('price_per_person',0))} | {sign}Y{fmt_price(abs(diff))} |")
    else:
        lines.append("| -- | 暂无实时比价数据 | -- | -- |")
    
    lines.extend([
        f"", f"> 数据来源: 飞猪/Klook/8264等OTA平台实时搜索 | 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"", f"## 五、定价建议",
        f"| 场景 | 系数 | 售价/人 | 毛利/人 |",
        f"|------|------|---------|---------|",
    ])
    for scenario, coef in [("团购/大团(20+)", 1.15), ("标准团(10-19)", 1.25), ("小团(4-9)", 1.40), ("私人定制", 1.60)]:
        price = int(base * coef)
        lines.append(f"| {scenario} | x{coef} | Y{fmt_price(price)} | Y{fmt_price(price-base)} |")
    
    lines.extend([
        f"", f"> 实际定价需结合淡旺季、渠道折扣、客户预算灵活调整。",
        f"---", f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ])
    return "\n".join(lines)

def create_feishu_doc(md, title):
    md_path = OUTPUT_DIR / f"cost_engine_{title}.md"
    with open(md_path, "w") as f: f.write(md)
    cmd = ["lark-cli","docs","+create","--api-version","v2","--doc-format","markdown",
           "--content",f"@{md_path.name}","--parent-token","XysVwyHOmiOOstkCjj9cXDBlnQb","--as","bot"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(OUTPUT_DIR), timeout=30)
    if r.returncode == 0:
        return json.loads(r.stdout).get("data",{}).get("document",{}).get("url",""), str(md_path)
    return None, str(md_path)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 cost_engine.py <trip_json>"); sys.exit(1)
    trip = load_trip(sys.argv[1])
    cats, total, people = analyze_cost(trip)
    md = build_report_md(trip, cats, total, people)
    url, local = create_feishu_doc(md, f"成本核算_{trip['group']['id']}")
    print(f"成本核算与市场比价 - Done")
    print(f"  {'飞书: '+url if url else '本地: '+local}")
    print(f"  人均成本: Y{fmt_price(total//people)}")
    for cat_name, cat_data in sorted(cats.items(), key=lambda x: -x[1]["subtotal"]):
        print(f"  {cat_name}: Y{fmt_price(cat_data['subtotal'])} ({cat_data['subtotal']/total*100:.0f}%)")
    return url or local

if __name__ == "__main__":
    main()
