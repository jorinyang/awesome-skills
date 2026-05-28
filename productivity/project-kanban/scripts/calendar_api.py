#!/usr/bin/env python3
"""Feishu Calendar API — create/update/delete events.

Usage:
  python3 calendar_api.py create --summary "..." --start "yyyy-MM-dd HH:mm" --end "..." [opts]
  python3 calendar_api.py update <event_id> [opts]
  python3 calendar_api.py delete <event_id>
  python3 calendar_api.py list [--days N]
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta

CALENDAR_ID = "feishu.cn_TzRmyorcXMoC2w2t8sh4pe@group.calendar.feishu.cn"
BASE = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{CALENDAR_ID}"

# Name → open_id
NAME_MAP = {
    "月夜": "ou_4c0471c3b58da8dd7883d095c3bb0843",
    "余媛天": "ou_b2853971fa42584d441b98f280524619",
    "夏与": "ou_13398e00296204b96873d16486e278af",
}

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_mgr import get_token

TZ = timezone(timedelta(hours=8))


def api(method, path, body=None):
    token = get_token()
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data:
        req.add_header("Content-Type", "application/json")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def parse_time(s):
    """Parse 'yyyy-MM-dd HH:mm' or 'yyyy/MM/dd HH:mm' → unix seconds."""
    for fmt in ["%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y-%m-%d", "%Y/%m/%d"]:
        try:
            dt = datetime.strptime(s, fmt)
            if fmt.endswith("%d"):
                dt = dt.replace(hour=0, minute=0)
            return int(dt.replace(tzinfo=TZ).timestamp())
        except ValueError:
            continue
    # Try 'HH:mm' today
    try:
        h, m = map(int, s.split(":"))
        now = datetime.now(TZ)
        dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        return int(dt.timestamp())
    except Exception:
        pass
    print(json.dumps({"error": f"cannot parse time: {s}"}))
    sys.exit(1)


def cmd_create(args):
    body = {
        "summary": args.summary,
        "start_time": {
            "timestamp": str(parse_time(args.start)),
            "timezone": "Asia/Shanghai",
        },
        "end_time": {
            "timestamp": str(parse_time(args.end)),
            "timezone": "Asia/Shanghai",
        },
    }
    if args.description:
        body["description"] = args.description
    if args.attendees:
        atts = []
        for name in args.attendees.split(","):
            name = name.strip()
            atts.append({"type": "user", "user_id": NAME_MAP.get(name, name)})
        body["attendees"] = atts

    r = api("POST", "/events", body)
    if r.get("code") == 0:
        ev = r["data"]["event"]
        print(json.dumps({
            "event_id": ev["event_id"],
            "summary": ev["summary"],
            "start_time": ev["start_time"],
            "end_time": ev["end_time"],
            "status": ev.get("status"),
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        sys.exit(1)


def cmd_update(args):
    body = {}
    if args.summary:
        body["summary"] = args.summary
    if args.description:
        body["description"] = args.description
    if args.start:
        body["start_time"] = {"timestamp": str(parse_time(args.start)), "timezone": "Asia/Shanghai"}
    if args.end:
        body["end_time"] = {"timestamp": str(parse_time(args.end)), "timezone": "Asia/Shanghai"}

    if not body:
        print(json.dumps({"error": "no fields to update"}))
        sys.exit(1)

    r = api("PATCH", f"/events/{args.event_id}", body)
    if r.get("code") == 0:
        ev = r["data"]["event"]
        print(json.dumps({"event_id": ev["event_id"], "summary": ev["summary"],
                           "status": ev.get("status")}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        sys.exit(1)


def cmd_delete(args):
    r = api("DELETE", f"/events/{args.event_id}")
    print(json.dumps({"deleted": r.get("code") == 0, "event_id": args.event_id}))


def cmd_list(args):
    days = int(args.days) if args.days else 30
    now = datetime.now(TZ)
    start = str(int(now.timestamp()))
    end = str(int((now + timedelta(days=days)).timestamp()))

    r = api("GET", f"/events?start_time={start}&end_time={end}&page_size=100")
    events = r.get("data", {}).get("items", [])

    results = []
    for ev in events:
        results.append({
            "event_id": ev["event_id"],
            "summary": ev.get("summary", ""),
            "start_time": ev.get("start_time", {}).get("timestamp"),
            "end_time": ev.get("end_time", {}).get("timestamp"),
            "status": ev.get("status"),
        })
    print(json.dumps(results, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Feishu Calendar CLI")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("create")
    p.add_argument("--summary", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--description")
    p.add_argument("--attendees", help="Comma-separated names")

    p = sub.add_parser("update")
    p.add_argument("event_id")
    p.add_argument("--summary")
    p.add_argument("--description")
    p.add_argument("--start")
    p.add_argument("--end")

    p = sub.add_parser("delete")
    p.add_argument("event_id")

    p = sub.add_parser("list")
    p.add_argument("--days", default="30")

    args = parser.parse_args()
    cmds = {"create": cmd_create, "update": cmd_update, "delete": cmd_delete, "list": cmd_list}
    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
