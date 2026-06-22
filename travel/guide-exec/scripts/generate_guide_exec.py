#!/usr/bin/env python3
"""贵州之客导游执行单生成器 — guide-exec
用法: python3 generate_guide_exec.py <trip_json_path> [--parent-token <wiki_node_token>]
输出: 飞书 docx 文档链接
"""

import json, sys, subprocess, tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path.home() / ".hermes-feishu/cache"
PARENT_TOKEN = "HmnBwlKhsixk45kjNa9cmCRDndb"  # 03-出团执行


def load_trip(path):
    with open(path) as f:
        return json.load(f)


def esc(text):
    """Escape special markdown characters for Feishu"""
    return str(text).replace("\\", "\\\\").replace("`", "\\`").replace("*", "\\*").replace("_", "\\_").replace("#", "\\#").replace("|", "\\|").replace("~", "\\~")


def build_markdown(trip):
    g = trip["group"]
    lines = []
    
    # Title
    lines.append(f"# 导游执行单 — {esc(g['name'])}")
    lines.append(f"")
    lines.append(f"> 团号：{esc(g['id'])} | 日期：{esc(g['dates']['start'])} — {esc(g['dates']['end'])} | 人数：{g['size']['total']}人 | 类型：{esc(g.get('type','团建'))}")
    lines.append(f"")
    
    # === 团基本信息 ===
    lines.append(f"## 一、团基本信息")
    lines.append(f"")
    lines.append(f"| 项目 | 内容 |")
    lines.append(f"|------|------|")
    lines.append(f"| 团号 | {esc(g['id'])} |")
    lines.append(f"| 团名 | {esc(g['name'])} |")
    lines.append(f"| 日期 | {esc(g['dates']['start'])} — {esc(g['dates']['end'])} |")
    lines.append(f"| 人数 | {g['size']['total']}人（成人{g['size']['adults']}人） |")
    lines.append(f"| 客户 | {esc(g['customer']['company'])} · {esc(g['customer']['contact_name'])} {esc(g['customer']['contact_phone'])} |")
    lines.append(f"| 特殊需求 | {esc(g['customer'].get('special_requests','无'))} |")
    lines.append(f"| 导游 | {esc(g['guide']['name'])} {esc(g['guide']['phone'])} |")
    lines.append(f"| 助理 | {esc(g['guide']['assistant_name'])} {esc(g['guide']['assistant_phone'])} |")
    lines.append(f"| 计调 | {esc(g['planner']['name'])} {esc(g['planner']['phone'])} |")
    lines.append(f"| 紧急联系人 | {esc(g['emergency_contact']['name'])} {esc(g['emergency_contact']['phone'])} |")
    lines.append(f"")
    
    # === 客户名单 ===
    lines.append(f"## 二、客户名单")
    lines.append(f"")
    lines.append(f"| 姓名 | 电话 | 身份证号 | 保险单号 | 饮食 | 室友 | 备注 |")
    lines.append(f"|------|------|----------|----------|------|------|------|")
    for c in trip.get("customers", []):
        lines.append(f"| {esc(c['name'])} | {esc(c['phone'])} | {esc(c.get('id',''))} | {esc(c.get('insurance',''))} | {esc(c.get('diet','正常'))} | {esc(c.get('roommate',''))} | {esc(c.get('notes',''))} |")
    if not trip.get("customers"):
        lines.append(f"| （待补充） |  |  |  |  |  |  |")
    lines.append(f"")
    
    # === 行程明细 ===
    lines.append(f"## 三、行程明细")
    for day_data in trip["itinerary"]:
        lines.append(f"")
        lines.append(f"### Day {day_data['day']} · {esc(day_data['date'])} · {esc(day_data['title'])}")
        lines.append(f"")
        lines.append(f"| 时间 | 时长 | 活动 | 地点 | 详情 | 注意事项 |")
        lines.append(f"|------|------|------|------|------|----------|")
        for item in day_data["items"]:
            lines.append(f"| {esc(item['time'])} | {esc(item.get('duration',''))} | {esc(item['activity'])} | {esc(item['location'])} | {esc(item['detail'])} |  |")
        lines.append(f"")
    
    # === 景点对接 ===
    lines.append(f"## 四、景点对接")
    lines.append(f"")
    lines.append(f"| 景点 | 对接人 | 电话 | 票务 |")
    lines.append(f"|------|--------|------|------|")
    for a in trip["suppliers"]["attractions"]:
        lines.append(f"| {esc(a['name'])} | {esc(a['contact'])} | {esc(a['phone'])} | {esc(a.get('tickets',''))} |")
    lines.append(f"")
    lines.append(f"**☐ 已提前联系确认 — 导游签字：_______**")
    lines.append(f"")
    
    # === 餐饮安排 ===
    lines.append(f"## 五、餐饮安排")
    lines.append(f"")
    lines.append(f"| 日期 | 餐别 | 餐厅 | 对接人 | 电话 | 菜单 | 特殊需求 |")
    lines.append(f"|------|------|------|--------|------|------|----------|")
    for m in trip["suppliers"]["restaurants"]:
        lines.append(f"| Day{m['day']} | {esc(m['meal'])} | {esc(m['name'])} | {esc(m['contact'])} | {esc(m['phone'])} | {esc(m.get('menu',''))} | {esc(m.get('special',''))} |")
    lines.append(f"")
    lines.append(f"**客户特殊饮食**：{esc(g['customer'].get('special_requests','无'))}")
    lines.append(f"")
    
    # === 住宿信息 ===
    lines.append(f"## 六、住宿信息")
    lines.append(f"")
    for h in trip["suppliers"]["hotels"]:
        rooms = "、".join(h["room_types"])
        lines.append(f"- **{esc(h['name'])}** · {esc(h['contact'])} {esc(h['phone'])}")
        lines.append(f"  - 入住：{esc(h['checkin'])} · 退房：{esc(h['checkout'])}")
        lines.append(f"  - 房型：{esc(rooms)} · 共{h.get('rooms_booked','?')}间")
        lines.append(f"  - ☐ 已确认  ☐ 房型分配完成")
    lines.append(f"")
    
    # === 车辆信息 ===
    t = trip["suppliers"]["transport"]
    lines.append(f"## 七、车辆信息")
    lines.append(f"")
    lines.append(f"- **{esc(t['company'])}** · {esc(t['type'])} · {esc(t.get('seats','?'))}座")
    lines.append(f"- 车牌：{esc(t.get('plate',''))} · 司机：{esc(t['driver'])} {esc(t['phone'])}")
    lines.append(f"- 接车点：贵阳北站 · 时间：{esc(g['dates']['departure_time'])}")
    lines.append(f"- 送车点：贵阳北站 · 时间：{esc(g['dates']['return_time'])}")
    lines.append(f"- ☐ 出发前已确认车辆  ☐ 已告知司机行程")
    lines.append(f"")
    
    # === 物资清单 ===
    lines.append(f"## 八、物资核对清单")
    lines.append(f"")
    lines.append(f"> 出团前逐项核对，核对人签字：______")
    lines.append(f"")
    lines.append(f"| 类别 | 物资 | 数量 | 核对 | 备注 |")
    lines.append(f"|------|------|------|------|------|")
    for cat in trip.get("supplies", []):
        cat_name = cat["category"]
        for item in cat["items"]:
            qty = f"{item['qty']}{item.get('unit','')}"
            lines.append(f"| {esc(cat_name)} | {esc(item['name'])} | {esc(qty)} | ☐ | {esc(item.get('note',''))} |")
    lines.append(f"")
    
    # === 财务 ===
    lines.append(f"## 九、财务信息")
    lines.append(f"")
    lines.append(f"| 项目 | 金额 | 备注 |")
    lines.append(f"|------|------|------|")
    for item in trip["pricing"]["items"]:
        sub = item["unit_price"] * item["quantity"]
        lines.append(f"| {esc(item['name'])} | ¥{sub:,} | {item['quantity']}{item['unit']} × ¥{item['unit_price']:,} |")
    total = sum(i["unit_price"] * i["quantity"] for i in trip["pricing"]["items"] if i.get("includes_in_price", True))
    lines.append(f"| **合计** | **¥{total:,}** | |")
    lines.append(f"")
    lines.append(f"- 备用金：¥______ · 已领取 ☐")
    lines.append(f"- 垫付记录：")
    lines.append(f"")
    
    # === 应急预案 ===
    ep = trip.get("emergency_plan", {})
    lines.append(f"## 十、应急预案")
    lines.append(f"")
    
    if "weather_rain" in ep:
        lines.append(f"### 🌧️ 下雨")
        lines.append(f"- 小雨：{esc(ep['weather_rain'].get('light',''))}")
        lines.append(f"- 大雨：{esc(ep['weather_rain'].get('heavy',''))}")
        lines.append(f"")
    
    if "injury" in ep:
        lines.append(f"### 🏥 伤病")
        lines.append(f"- 轻伤：{esc(ep['injury'].get('minor',''))}")
        lines.append(f"- 重伤：{esc(ep['injury'].get('serious',''))}")
        lines.append(f"")
    
    if "transport" in ep:
        lines.append(f"### 🚗 交通")
        lines.append(f"- 车辆故障：{esc(ep['transport'].get('breakdown',''))}")
        lines.append(f"")
    
    if "lost_contact" in ep:
        lines.append(f"### 📡 失联")
        lines.append(f"- {esc(ep['lost_contact'].get('procedure',''))}")
        lines.append(f"")
    
    # === 天气预报 ===
    lines.append(f"## 十一、天气预报")
    lines.append(f"")
    lines.append(f"- {esc(trip['weather']['forecast'])}")
    lines.append(f"- 预警：{esc(trip['weather'].get('warning','无'))}")
    lines.append(f"- {esc(trip['weather'].get('advice',''))}")
    lines.append(f"")
    
    # === 行前确认 ===
    lines.append(f"## 十二、行前确认清单")
    lines.append(f"")
    checks = [
        "客户名单确认（含身份证号、保险单号）",
        "住宿已确认（房型分配完成）",
        "餐饮已确认（含特殊饮食）",
        "车辆已确认（司机已知行程）",
        "景点已确认（对接人已联系）",
        "物资已核对（见第八章清单）",
        "保险已生效（核对保单有效期）",
        "天气预报已查看",
        "备用金已领取",
        "出团通知书已打印（导游携带×1）",
        "急救包有效期已检查",
        "对讲机已充足电",
    ]
    for i, c in enumerate(checks, 1):
        lines.append(f"- ☐ {i}. {c}")
    lines.append(f"")
    lines.append(f"**确认人签字：_______**  **日期：_______**")
    
    return "\n".join(lines)


def create_feishu_doc(markdown_content, title, parent_token):
    """Create Feishu docx via lark-cli"""
    md_path = OUTPUT_DIR / f"guide_exec_{title.replace(' ','_')}.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    with open(md_path, "w") as f:
        f.write(markdown_content)
    
    cmd = [
        "lark-cli", "docs", "+create",
        "--api-version", "v2",
        "--doc-format", "markdown",
        "--content", f"@{md_path.name}",
        "--parent-token", parent_token,
        "--as", "bot"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(OUTPUT_DIR), timeout=30)
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            url = data.get("data", {}).get("document", {}).get("url", "")
            return url, str(md_path)
        except:
            pass
    
    return None, str(md_path)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_guide_exec.py <trip_json> [--parent-token <wiki_node_token>]")
        sys.exit(1)
    
    trip_path = sys.argv[1]
    parent_token = PARENT_TOKEN
    if "--parent-token" in sys.argv:
        idx = sys.argv.index("--parent-token")
        parent_token = sys.argv[idx + 1]
    
    trip = load_trip(trip_path)
    md = build_markdown(trip)
    
    title = f"导游执行单_{trip['group']['id']}"
    url, local_path = create_feishu_doc(md, title, parent_token)
    
    print(f"✅ 导游执行单已生成")
    if url:
        print(f"   飞书文档: {url}")
    else:
        print(f"   ⚠️ 飞书创建失败，本地文件: {local_path}")
        print(f"   可手动导入: lark-cli drive +import --type docx --file {local_path}")
    print(f"   本地备份: {local_path}")
    print(f"   团号: {trip['group']['id']}")
    
    return url or local_path


if __name__ == "__main__":
    main()
