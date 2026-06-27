#!/usr/bin/env python3
"""贵州之客供应商对接单生成器 — vendor-brief
用法: python3 generate_vendor_brief.py <trip_json_path>
输出: 酒店/车辆/地接 三个 PDF 文件
"""

import json, sys
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path.home() / ".hermes-feishu/cache"


def esc(t): return str(t).replace("\\","\\\\")


def build_hotel_brief(trip):
    """酒店对接单 HTML"""
    g = trip["group"]
    h = trip["suppliers"]["hotels"][0] if trip["suppliers"]["hotels"] else {}
    rooms_html = "<br>".join(f"  {r}" for r in h.get("room_types", []))
    
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><style>
@page {{ size: A4; margin: 15mm; }}
body {{ font-family: "Noto Sans SC", sans-serif; font-size: 10.5pt; }}
h1 {{ font-size: 16pt; color: #2563EB; border-bottom: 2px solid #2563EB; padding-bottom: 6px; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
td {{ padding: 8px 10px; border: 1px solid #ddd; font-size: 10pt; vertical-align: top; }}
td.label {{ background: #f0f4ff; width: 25%; font-weight: 600; }}
.confirm {{ border: 2px dashed #2563EB; padding: 14px; margin-top: 20px; }}
</style></head><body>
<h1>酒店对接单</h1>
<table>
<tr><td class="label">团号</td><td>{esc(g['id'])}</td></tr>
<tr><td class="label">入住日期</td><td>{esc(g['dates']['start'])} {esc(h.get('checkin',''))}</td></tr>
<tr><td class="label">退房日期</td><td>{esc(g['dates']['end'])} {esc(h.get('checkout',''))}</td></tr>
<tr><td class="label">酒店</td><td>{esc(h.get('name',''))}</td></tr>
<tr><td class="label">房型 × 数量</td><td>{rooms_html} · 共{h.get('rooms_booked','?')}间</td></tr>
<tr><td class="label">人数</td><td>{g['size']['total']}人</td></tr>
<tr><td class="label">特殊需求</td><td>{esc(g['customer'].get('special_requests','无'))}</td></tr>
<tr><td class="label">导游</td><td>{esc(g['guide']['name'])} {esc(g['guide']['phone'])}</td></tr>
</table>
<div class="confirm">
<p><strong>请确认以上信息，签字或微信回复确认。</strong></p>
<p>酒店签字：_______ 日期：_______</p>
<p>贵州之客旅行社 · {esc(g['planner']['name'])} {esc(g['planner']['phone'])}</p>
</div>
</body></html>"""


def build_transport_brief(trip):
    """车辆对接单 HTML"""
    g = trip["group"]
    t = trip["suppliers"]["transport"]
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><style>
@page {{ size: A4; margin: 15mm; }}
body {{ font-family: "Noto Sans SC", sans-serif; font-size: 10.5pt; }}
h1 {{ font-size: 16pt; color: #DC2626; border-bottom: 2px solid #DC2626; padding-bottom: 6px; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
td {{ padding: 8px 10px; border: 1px solid #ddd; font-size: 10pt; vertical-align: top; }}
td.label {{ background: #fef2f2; width: 25%; font-weight: 600; }}
.confirm {{ border: 2px dashed #DC2626; padding: 14px; margin-top: 20px; }}
</style></head><body>
<h1>车辆对接单</h1>
<table>
<tr><td class="label">团号</td><td>{esc(g['id'])}</td></tr>
<tr><td class="label">日期</td><td>{esc(g['dates']['start'])} — {esc(g['dates']['end'])}</td></tr>
<tr><td class="label">车辆公司</td><td>{esc(t.get('company',''))}</td></tr>
<tr><td class="label">车型 · 座位</td><td>{esc(t.get('type',''))} · {t.get('seats','?')}座</td></tr>
<tr><td class="label">车牌号</td><td>{esc(t.get('plate',''))}</td></tr>
<tr><td class="label">司机</td><td>{esc(t.get('driver',''))} {esc(t.get('phone',''))}</td></tr>
<tr><td class="label">接车</td><td>{esc(g['dates']['start'])} {esc(g['dates']['departure_time'])} · 贵阳北站</td></tr>
<tr><td class="label">送车</td><td>{esc(g['dates']['end'])} {esc(g['dates']['return_time'])} · 贵阳北站</td></tr>
<tr><td class="label">人数</td><td>{g['size']['total']}人</td></tr>
<tr><td class="label">导游</td><td>{esc(g['guide']['name'])} {esc(g['guide']['phone'])}</td></tr>
</table>
<div class="confirm">
<p><strong>请确认以上信息，微信回复即可。</strong></p>
<p>贵州之客旅行社 · {esc(g['planner']['name'])} {esc(g['planner']['phone'])}</p>
</div>
</body></html>"""


def build_ground_brief(trip):
    """地接对接单 HTML"""
    g = trip["group"]
    attractions = trip["suppliers"].get("attractions", [])
    attr_lines = "<br>".join(f"  {a['name']} · {a.get('contact','')} {a.get('phone','')}" for a in attractions[1:])  # skip first
    
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><style>
@page {{ size: A4; margin: 15mm; }}
body {{ font-family: "Noto Sans SC", sans-serif; font-size: 10.5pt; }}
h1 {{ font-size: 16pt; color: #059669; border-bottom: 2px solid #059669; padding-bottom: 6px; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
td {{ padding: 8px 10px; border: 1px solid #ddd; font-size: 10pt; vertical-align: top; }}
td.label {{ background: #ecfdf5; width: 25%; font-weight: 600; }}
.confirm {{ border: 2px dashed #059669; padding: 14px; margin-top: 20px; }}
</style></head><body>
<h1>地接对接单</h1>
<table>
<tr><td class="label">团号</td><td>{esc(g['id'])}</td></tr>
<tr><td class="label">日期</td><td>{esc(g['dates']['start'])} — {esc(g['dates']['end'])}</td></tr>
<tr><td class="label">人数</td><td>{g['size']['total']}人</td></tr>
<tr><td class="label">对接项目</td><td>{attr_lines}</td></tr>
<tr><td class="label">导游</td><td>{esc(g['guide']['name'])} {esc(g['guide']['phone'])}</td></tr>
</table>
<div class="confirm">
<p><strong>请确认以上信息，微信回复即可。</strong></p>
<p>贵州之客旅行社 · {esc(g['planner']['name'])} {esc(g['planner']['phone'])}</p>
</div>
</body></html>"""


def html_to_pdf(html, name):
    pdf_path = OUTPUT_DIR / name
    html_path = OUTPUT_DIR / name.replace(".pdf", ".html")
    with open(html_path, "w") as f: f.write(html)
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
        print("用法: python3 generate_vendor_brief.py <trip_json>"); sys.exit(1)
    trip = json.load(open(sys.argv[1]))
    gid = trip["group"]["id"]
    
    results = []
    for name, builder in [("hotel", build_hotel_brief), ("transport", build_transport_brief), ("ground", build_ground_brief)]:
        html = builder(trip)
        pdf = html_to_pdf(html, f"vendor_{name}_{gid}.pdf")
        results.append((name, pdf))
    
    print(f"✅ 供应商对接单（3份）")
    for name, path in results:
        print(f"   {name}: {path}")
    return [p for _, p in results]


if __name__ == "__main__":
    main()
