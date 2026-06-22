#!/usr/bin/env python3
"""贵州之客出团通知书生成器 — trip-briefing
用法: python3 generate_briefing.py <trip_json_path>
输出: ~/.hermes-feishu/cache/briefing_{团号}.pdf
"""

import json, sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "templates/briefing.html"
OUTPUT_DIR = Path.home() / ".hermes-feishu/cache"


def load_trip(path):
    with open(path) as f:
        return json.load(f)


def render_itinerary(trip):
    blocks = []
    for day_data in trip["itinerary"]:
        rows = []
        for item in day_data["items"]:
            rows.append(
                f'<div class="row">'
                f'<div class="time">{item["time"]}</div>'
                f'<div class="act">{item["activity"]}</div>'
                f'<div class="loc">{item["location"]}</div>'
                f'<div class="detail">{item["detail"]}</div>'
                f'</div>'
            )
        blocks.append(
            f'<div class="day-block">'
            f'<div class="day-title">Day {day_data["day"]} · {day_data["date"]} · {day_data["title"]}</div>'
            f'<div class="day-items">{"".join(rows)}</div>'
            f'</div>'
        )
    return "\n".join(blocks)


def render_hotels(trip):
    cards = []
    for h in trip["suppliers"]["hotels"]:
        rooms = ", ".join(h["room_types"])
        cards.append(
            f'<div class="contact-card" style="margin-bottom:8px;">'
            f'<div class="name">{h["name"]}</div>'
            f'<div class="role">入住：{h["checkin"]} · 退房：{h["checkout"]} · {rooms}</div>'
            f'<div class="phone">{h["contact"]} {h["phone"]}</div>'
            f'</div>'
        )
    return "\n".join(cards)


def render_meals(trip):
    rows = []
    for m in trip["suppliers"]["restaurants"]:
        special = f" ({m['special']})" if m.get("special") else ""
        rows.append(
            f'<tr><td style="padding:4px 8px;border-bottom:1px solid #f0f0f0;">Day{m["day"]}</td>'
            f'<td style="padding:4px 8px;">{m["meal"]}</td>'
            f'<td style="padding:4px 8px;">{m["name"]} · {m["menu"]}{special}</td></tr>'
        )
    return f'<table style="width:100%;font-size:9pt;border-collapse:collapse;">{"".join(rows)}</table>'


def render_includes(trip):
    included = [i["name"] for i in trip["pricing"]["items"] if i.get("includes_in_price", True)]
    return "、".join(included)


def render(trip):
    with open(TEMPLATE) as f:
        tmpl = f.read()
    
    t = trip["suppliers"]["transport"]
    transport_html = f'{t["company"]} · {t["type"]} · {t["seats"]}座 · {t["plate"]} · 司机：{t["driver"]} {t["phone"]}'
    
    html = tmpl
    g = trip["group"]
    html = html.replace("{{group.id}}", g["id"])
    html = html.replace("{{group.name}}", g["name"])
    html = html.replace("{{group.dates.start}}", g["dates"]["start"])
    html = html.replace("{{group.dates.end}}", g["dates"]["end"])
    html = html.replace("{{group.dates.departure_time}}", g["dates"]["departure_time"])
    html = html.replace("{{group.dates.return_time}}", g["dates"]["return_time"])
    html = html.replace("{{group.size.total}}", str(g["size"]["total"]))
    html = html.replace("{{group.customer.company}}", g["customer"]["company"])
    html = html.replace("{{group.guide.name}}", g["guide"]["name"])
    html = html.replace("{{group.guide.phone}}", g["guide"]["phone"])
    html = html.replace("{{group.planner.name}}", g["planner"]["name"])
    html = html.replace("{{group.planner.phone}}", g["planner"]["phone"])
    html = html.replace("{{group.emergency_contact.name}}", g["emergency_contact"]["name"])
    html = html.replace("{{group.emergency_contact.phone}}", g["emergency_contact"]["phone"])
    
    html = html.replace("{{itinerary_html}}", render_itinerary(trip))
    html = html.replace("{{hotels_html}}", render_hotels(trip))
    html = html.replace("{{meals_html}}", render_meals(trip))
    html = html.replace("{{transport.company}}", t["company"])
    html = html.replace("{{transport.type}}", t["type"])
    html = html.replace("{{transport.seats}}", str(t["seats"]))
    html = html.replace("{{transport.plate}}", t["plate"])
    html = html.replace("{{transport.driver}}", t["driver"])
    html = html.replace("{{transport.phone}}", t["phone"])
    html = html.replace("{{includes_text}}", render_includes(trip))
    html = html.replace("{{weather.forecast}}", trip["weather"]["forecast"])
    html = html.replace("{{weather.advice}}", trip["weather"]["advice"])
    
    html_path = OUTPUT_DIR / f"briefing_{g['id']}.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    with open(html_path, "w") as f:
        f.write(html)
    
    return str(html_path), g["id"]


def html_to_pdf(html_path, output_id):
    pdf_path = OUTPUT_DIR / f"briefing_{output_id}.pdf"
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"file://{html_path}", wait_until="networkidle")
            page.pdf(path=str(pdf_path), format="A4", print_background=True)
            browser.close()
        return str(pdf_path)
    except ImportError:
        return str(html_path)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_briefing.py <trip_json>")
        sys.exit(1)
    
    trip = load_trip(sys.argv[1])
    html_path, output_id = render(trip)
    pdf_path = html_to_pdf(html_path, output_id)
    
    print(f"✅ 出团通知书已生成")
    print(f"   PDF: {pdf_path}")
    print(f"   团号: {trip['group']['id']}")
    
    return pdf_path


if __name__ == "__main__":
    main()
