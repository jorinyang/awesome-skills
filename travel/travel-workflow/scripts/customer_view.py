#!/usr/bin/env python3
"""贵州之客客户视角文档包 — customer-view
用法: python3 customer_view.py <trip_json_path>
输出: 客户全套PDF打包（报价单+出团通知书+出行须知）
"""

import json, sys, subprocess
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path.home() / ".hermes-feishu/cache"

WEEKDAYS = ["周一","周二","周三","周四","周五","周六","周日"]

def esc(t): return str(t).replace("\\","\\\\").replace("|","\\|")
def fmt_price(n): return f"{n:,}"

def load_trip(path):
    with open(path) as f: return json.load(f)

def build_customer_pack(trip):
    """Build HTML customer pack (quote + briefing + essentials all in one)"""
    g = trip["group"]
    days = len(trip["itinerary"])
    included = [i for i in trip["pricing"]["items"] if i.get("includes_in_price", True)]
    total = sum(i["unit_price"] * i["quantity"] for i in included)
    pp = int(total / g["size"]["total"])
    start_date = datetime.strptime(g["dates"]["start"], "%Y-%m-%d")
    dow = WEEKDAYS[start_date.weekday()]
    
    # Itinerary rows
    it_rows = []
    for day in trip["itinerary"]:
        it_rows.append(
            f'<tr style="background:#e8f5e9;"><td colspan="4" style="font-weight:700;color:#1B8C3E;">'
            f'Day {day["day"]} · {day["date"]} · {day["title"]}</td></tr>'
        )
        for item in day["items"]:
            it_rows.append(
                f'<tr><td style="width:60px;color:#1B8C3E;font-weight:600;">{item["time"]}</td>'
                f'<td style="width:100px;">{item["activity"]}</td>'
                f'<td style="width:100px;color:#888;">{item["location"]}</td>'
                f'<td>{item["detail"]}</td></tr>'
            )
    
    # Pricing rows
    price_rows = []
    for item in included:
        sub = item["unit_price"] * item["quantity"]
        price_rows.append(
            f'<tr><td>{item["category"]}</td><td>{item["name"]}</td>'
            f'<td style="text-align:right">¥{fmt_price(item["unit_price"])}</td>'
            f'<td style="text-align:center">{item["quantity"]}{item["unit"]}</td>'
            f'<td style="text-align:right">¥{fmt_price(sub)}</td></tr>'
        )
    
    # Hotel info
    h = trip["suppliers"]["hotels"][0] if trip["suppliers"]["hotels"] else {}
    t = trip["suppliers"]["transport"]
    
    # Meals summary
    meals = []
    for m in trip["suppliers"]["restaurants"]:
        meals.append(f'<tr><td>Day{m["day"]} {m["meal"]}</td><td>{m["name"]} · {m.get("menu","")}</td></tr>')
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>贵州之客 · {esc(g['name'])}</title>
<style>
@page {{ size: A4; margin: 12mm 16mm; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:"Noto Sans SC","PingFang SC",sans-serif; color:#1a1a1a; font-size:10pt; line-height:1.5; }}

.cover {{ page-break-after:always; text-align:center; padding-top:120px; }}
.cover h1 {{ font-size:28pt; color:#1B8C3E; letter-spacing:3px; }}
.cover .sub {{ font-size:12pt; color:#888; margin:16px 0; }}
.cover .date {{ font-size:14pt; color:#333; }}
.cover .footer {{ margin-top:80px; font-size:9pt; color:#aaa; }}

.page {{ page-break-before:always; }}
h2 {{ font-size:14pt; color:#1B8C3E; border-bottom:2px solid #1B8C3E; padding-bottom:4px; margin:16px 0 10px; }}
h3 {{ font-size:11pt; color:#333; margin:12px 0 6px; }}

.info-grid {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px; }}
.info-grid .item {{ flex:0 0 calc(50% - 4px); background:#f5f5f5; padding:8px 12px; border-radius:4px; font-size:9pt; }}
.info-grid .label {{ color:#888; font-size:7.5pt; }}
.info-grid .value {{ font-weight:600; }}

table {{ width:100%; border-collapse:collapse; margin:8px 0; font-size:9pt; }}
th {{ background:#1B8C3E; color:#fff; padding:6px 8px; text-align:left; }}
td {{ padding:6px 8px; border-bottom:1px solid #eee; }}

.banner {{ background:linear-gradient(135deg,#1B8C3E,#2d8f4e); color:#fff; padding:16px 20px; margin:12px 0; display:flex; justify-content:space-between; align-items:center; }}
.banner .amount {{ font-size:24pt; font-weight:700; }}

.chip {{ display:inline-block; background:#e8f5e9; color:#2e7d32; padding:3px 12px; border-radius:12px; font-size:8.5pt; margin:2px; }}

.alert {{ background:#fff3cd; border-left:4px solid #ffc107; padding:8px 12px; margin:8px 0; font-size:9pt; }}

.footer-note {{ text-align:center; font-size:8pt; color:#bbb; margin-top:20px; padding-top:12px; border-top:1px solid #eee; }}
</style></head>
<body>

<!-- 封面 -->
<div class="cover">
  <h1>贵州之客</h1>
  <div class="sub">{esc(g['name'])}</div>
  <div class="date">{esc(g['dates']['start'])} — {esc(g['dates']['end'])} · {g['size']['total']}人团</div>
  <div class="footer">客户：{esc(g['customer']['company'])}<br>专属顾问：{esc(g['planner']['name'])} {esc(g['planner']['phone'])}</div>
</div>

<!-- 行程概览 -->
<div class="page">
<h2>行程概览</h2>
<div class="info-grid">
<div class="item"><div class="label">团号</div><div class="value">{esc(g['id'])}</div></div>
<div class="item"><div class="label">日期</div><div class="value">{esc(g['dates']['start'])} — {esc(g['dates']['end'])}</div></div>
<div class="item"><div class="label">天数</div><div class="value">{days}天{days-1}晚</div></div>
<div class="item"><div class="label">人数</div><div class="value">{g['size']['total']}人</div></div>
<div class="item"><div class="label">集合</div><div class="value">{esc(g['dates']['departure_time'])} · 贵阳北站</div></div>
<div class="item"><div class="label">导游</div><div class="value">{esc(g['guide']['name'])} {esc(g['guide']['phone'])}</div></div>
</div>

<h3>每日行程</h3>
<table><tr><th>时间</th><th>活动</th><th>地点</th><th>详情</th></tr>
{"".join(it_rows)}
</table>
</div>

<!-- 费用说明 -->
<div class="page">
<h2>费用说明</h2>
<div class="banner">
  <div>人均参考价</div>
  <div class="amount">¥{fmt_price(pp)}<span style="font-size:12pt;">/人</span></div>
</div>

<table><tr><th>类别</th><th>项目</th><th style="text-align:right">单价</th><th style="text-align:center">数量</th><th style="text-align:right">小计</th></tr>
{"".join(price_rows)}
<tr style="font-weight:700;background:#f0f0f0;"><td colspan="4">合计</td><td style="text-align:right">¥{fmt_price(total)}</td></tr>
</table>

<h3>✅ 费用包含</h3>
<div>{" ".join(f'<span class="chip">{i["name"]}</span>' for i in included)}</div>
<div style="font-size:8.5pt;color:#888;margin-top:8px;"><strong>不含：</strong>往返大交通、个人消费、酒水饮料、未列明项目</div>
</div>

<!-- 出行信息 -->
<div class="page">
<h2>住宿与交通</h2>
<h3>🏨 住宿</h3>
<p><strong>{esc(h.get('name',''))}</strong> · {esc(h.get('contact',''))} {esc(h.get('phone',''))}</p>
<p>入住：{esc(h.get('checkin',''))} · 退房：{esc(h.get('checkout',''))} · {', '.join(h.get('room_types',[]))}</p>

<h3>🚌 交通</h3>
<p>{esc(t.get('company',''))} · {esc(t.get('type',''))} · {t.get('seats','?')}座 · {esc(t.get('plate',''))}</p>
<p>司机：{esc(t.get('driver',''))} {esc(t.get('phone',''))}</p>

<h3>🍽️ 餐饮</h3>
<table><tr><th>时间</th><th>安排</th></tr>
{"".join(meals)}
</table>
<div class="alert"><strong>特殊饮食：</strong>{esc(g['customer'].get('special_requests','无'))}</div>

<h2>物品建议</h2>
<div style="display:flex;gap:16px;">
<div style="flex:1;"><h3>🧳 建议自备</h3>
<ul style="font-size:9pt;"><li>防晒霜、太阳镜、遮阳帽</li><li>换洗衣物</li><li>手机防水袋</li><li>运动鞋+凉鞋</li><li>个人常用药品</li></ul></div>
<div style="flex:1;"><h3>🎒 免费提供</h3>
<ul style="font-size:9pt;"><li>桨板+桨+救生衣</li><li>头盔+头灯+手套</li><li>防水袋</li><li>矿泉水</li><li>急救包</li></ul></div>
</div>

<h2>安全须知</h2>
<p style="font-size:9pt;">✅ 教练配比≥1:5 · 已购户外保险 · SRT装备CE认证 · 急救包全程随队</p>
<p style="font-size:9pt;">🚨 紧急联系：{esc(g['emergency_contact']['name'])} {esc(g['emergency_contact']['phone'])}</p>

<div class="footer-note">
  贵州之客旅行社有限公司 · {esc(g['planner']['phone'])}<br>
  祝旅途愉快！
</div>
</div>

</body></html>"""
    return html


def html_to_pdf(html, name):
    html_path = OUTPUT_DIR / name.replace(".pdf", ".html")
    pdf_path = OUTPUT_DIR / name
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
        print("用法: python3 customer_view.py <trip_json>"); sys.exit(1)
    
    trip = load_trip(sys.argv[1])
    gid = trip["group"]["id"]
    html = build_customer_pack(trip)
    pdf = html_to_pdf(html, f"customer_pack_{gid}.pdf")
    
    print(f"✅ 客户视角文档包")
    print(f"   PDF: {pdf}")
    print(f"   团号: {gid}")
    return pdf

if __name__ == "__main__":
    main()
