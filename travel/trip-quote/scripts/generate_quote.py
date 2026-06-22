#!/usr/bin/env python3
"""贵州之客报价单生成器 v1.1 — 支持四风格
风格: 团建/私人定制/研学/散客 (根据 group.type 自动选择)
"""

import json, sys
from pathlib import Path
from datetime import datetime, timedelta

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = {
    "团建": SKILL_DIR / "templates/quote_团建.html",
    "私人定制": SKILL_DIR / "templates/quote_私人定制.html",
    "研学": SKILL_DIR / "templates/quote_研学.html",
    "散客": SKILL_DIR / "templates/quote_散客.html",
}
OUTPUT_DIR = Path.home() / ".hermes-feishu/cache"

WEEKDAYS = ["周一","周二","周三","周四","周五","周六","周日"]

def load_trip(path):
    with open(path) as f: return json.load(f)

def fmt_price(n): return f"{n:,}"

def render_itinerary_compact(trip, style):
    """Compact itinerary for 私人定制/散客"""
    if style == "私人定制":
        blocks = []
        for day in trip["itinerary"]:
            items = "".join(
                f'<div class="day-item"><div class="time">{i["time"]}</div>'
                f'<div class="act">{i["activity"]}</div><div class="desc">{i["detail"]}</div></div>'
                for i in day["items"]
            )
            blocks.append(f'<div class="day-title">Day {day["day"]} · {day["date"]} · {day["title"]}</div>{items}')
        return "\n".join(blocks)
    
    elif style == "散客":
        blocks = []
        for day in trip["itinerary"]:
            rows = "".join(
                f'<div class="row"><div class="time">{i["time"]}</div>'
                f'<div class="act"><strong>{i["activity"]}</strong><span>{i["detail"]}</span></div></div>'
                for i in day["items"]
            )
            blocks.append(
                f'<div class="day-card"><div class="day-header">Day {day["day"]} · {day["date"]} · {day["title"]}</div>'
                f'<div class="day-body">{rows}</div></div>'
            )
        return "\n".join(blocks)
    return ""


def render_itinerary_full(trip):
    """Full table itinerary for 团建/研学"""
    rows = []
    for day in trip["itinerary"]:
        rows.append(f'<tr class="day-header"><td colspan="5">Day {day["day"]} · {day["date"]} · {day["title"]}</td></tr>')
        for item in day["items"]:
            note = item.get("detail", "")
            rows.append(
                f"<tr><td></td><td>{item['time']}</td><td>{item['activity']}</td>"
                f"<td>{item['location']}</td><td>{note}</td></tr>"
            )
    return "\n".join(rows)


def render_itinerary_study(trip):
    """Itinerary for 研学 style with learning focus column"""
    rows = []
    for day in trip["itinerary"]:
        rows.append(f'<tr class="day-sep"><td colspan="6">Day {day["day"]} · {day["date"]} · {day["title"]}</td></tr>')
        for item in day["items"]:
            rows.append(
                f"<tr><td></td><td>{item['time']}</td><td>{item['activity']}</td>"
                f"<td>{item['location']}</td><td>{item['detail']}</td><td>—</td></tr>"
            )
    return "\n".join(rows)


def render_pricing(trip, style="团建"):
    """Pricing rows for all styles"""
    included = [i for i in trip["pricing"]["items"] if i.get("includes_in_price", True)]
    if style in ("散客", "私人定制"):
        rows = []
        for item in included:
            sub = item["unit_price"] * item["quantity"]
            rows.append(
                f'<tr><td>{item["name"]}</td><td class="inc">✓ 含</td>'
                f'<td style="text-align:right">¥{fmt_price(sub)}</td></tr>'
            )
        return "\n".join(rows)
    else:
        rows = []
        for item in included:
            sub = item["unit_price"] * item["quantity"]
            rows.append(
                f'<tr><td class="category">{item["category"]}</td><td>{item["name"]}</td>'
                f'<td style="text-align:right">¥{fmt_price(item["unit_price"])}</td>'
                f'<td style="text-align:center">{item["quantity"]}{item["unit"]}</td>'
                f'<td style="text-align:right">¥{fmt_price(sub)}</td></tr>'
            )
        return "\n".join(rows)


def render(trip, style=None):
    style = style or trip["group"].get("type", "团建")
    tmpl_path = TEMPLATES.get(style, TEMPLATES["团建"])
    with open(tmpl_path) as f:
        html = f.read()
    
    g = trip["group"]
    days = len(trip["itinerary"])
    included = [i for i in trip["pricing"]["items"] if i.get("includes_in_price", True)]
    total = sum(i["unit_price"] * i["quantity"] for i in included)
    people = g["size"]["total"]
    price_per = int(total / people)
    
    start_date = datetime.strptime(g["dates"]["start"], "%Y-%m-%d")
    valid_until = (start_date - timedelta(days=3)).strftime("%Y-%m-%d")
    day_of_week = WEEKDAYS[start_date.weekday()]
    
    # Common replacements
    reps = {
        "{{group.id}}": g["id"],
        "{{group.name}}": g["name"],
        "{{group.dates.start}}": g["dates"]["start"],
        "{{group.dates.end}}": g["dates"]["end"],
        "{{group.dates.departure_time}}": g["dates"]["departure_time"],
        "{{group.dates.return_time}}": g["dates"]["return_time"],
        "{{group.size.total}}": str(people),
        "{{group.size.adults}}": str(g["size"]["adults"]),
        "{{group.customer.company}}": g["customer"]["company"],
        "{{group.customer.contact_name}}": g["customer"]["contact_name"],
        "{{group.customer.contact_phone}}": g["customer"]["contact_phone"],
        "{{group.guide.name}}": g["guide"]["name"],
        "{{group.guide.phone}}": g["guide"]["phone"],
        "{{group.planner.name}}": g["planner"]["name"],
        "{{group.planner.phone}}": g["planner"]["phone"],
        "{{days}}": str(days),
        "{{days_minus_1}}": str(days - 1),
        "{{price_per_person}}": fmt_price(price_per),
        "{{total_price}}": fmt_price(total),
        "{{valid_until}}": valid_until,
        "{{day_of_week}}": day_of_week,
    }
    
    for k, v in reps.items():
        html = html.replace(k, v)
    
    # Style-specific content
    if "{{itinerary_rows}}" in html:
        if style == "研学":
            html = html.replace("{{itinerary_rows}}", render_itinerary_study(trip))
        else:
            html = html.replace("{{itinerary_rows}}", render_itinerary_full(trip))
    
    if "{{itinerary_html}}" in html:
        html = html.replace("{{itinerary_html}}", render_itinerary_compact(trip, style))
    
    if "{{pricing_rows}}" in html:
        html = html.replace("{{pricing_rows}}", render_pricing(trip, style))
    
    if "{{includes_list}}" in html:
        tags = [f"<li><strong>{i['category']}：</strong>{'、'.join(j['name'] for j in included if j['category']==i['category'])}</li>" for i in included]
        html = html.replace("{{includes_list}}", "\n".join(dict.fromkeys(tags)))
    
    if "{{includes_tags}}" in html:
        names = [i["name"] for i in included]
        html = html.replace("{{includes_tags}}", " · ".join(names))
    
    if "{{includes_chips}}" in html:
        html = html.replace("{{includes_chips}}", "\n".join(f'<span class="chip">{i["name"]}</span>' for i in included))
    
    if "{{highlight_tags}}" in html:
        highlights = [
            f"<span class=\"tag\">🏔️ 喀斯特地貌</span>",
            f"<span class=\"tag\">🏄 水上桨板</span>",
            f"<span class=\"tag\">🕳️ 洞穴探险</span>",
            f"<span class=\"tag\">🔥 篝火晚会</span>",
            f"<span class=\"tag\">📸 全程跟拍</span>",
        ]
        html = html.replace("{{highlight_tags}}", "\n".join(highlights))
    
    if "{{market_ref_html}}" in html:
        mr = trip["pricing"].get("market_reference", {}).get("fliggy_similar_route", {})
        if mr:
            diff = mr.get("price_per_person", 0) - price_per
            diff_t = f"比市场参考价低 ¥{fmt_price(diff)}" if diff > 0 else ""
            html = html.replace("{{market_ref_html}}",
                f'<div class="market-ref"><strong>📊 市场参考：</strong>飞猪同类「{mr.get("name","")}」约 ¥{fmt_price(mr.get("price_per_person",0))}/人。{diff_t}</div>')
        else:
            html = html.replace("{{market_ref_html}}", "")
    
    # Save & convert
    html_path = OUTPUT_DIR / f"quote_{g['id']}.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    with open(html_path, "w") as f: f.write(html)
    
    pdf_path = OUTPUT_DIR / f"quote_{g['id']}.pdf"
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"file://{html_path}", wait_until="networkidle")
            page.pdf(path=str(pdf_path), format="A4", print_background=True)
            browser.close()
    except ImportError:
        pdf_path = html_path
    
    return str(pdf_path), g['id'], price_per, total


def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_quote.py <trip_json> [--style 团建|私人定制|研学|散客]"); sys.exit(1)
    
    trip_path = sys.argv[1]
    style = None
    if "--style" in sys.argv:
        style = sys.argv[sys.argv.index("--style") + 1]
    
    trip = load_trip(trip_path)
    pdf_path, gid, pp, total = render(trip, style)
    
    print(f"✅ 报价单已生成 ({trip['group'].get('type',style or '团建')}风格)")
    print(f"   PDF: {pdf_path}")
    print(f"   人均: ¥{fmt_price(pp)}  合计: ¥{fmt_price(total)}")

if __name__ == "__main__":
    main()
