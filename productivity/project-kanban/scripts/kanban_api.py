#!/usr/bin/env python3
"""Project Kanban — Bitable CRUD for 贵州之客项目看板.

Usage:
  python3 kanban_api.py init                           # show table info
  python3 kanban_api.py create --title "..." [opts]    # create task card
  python3 kanban_api.py update <record_id> [opts]      # update task card
  python3 kanban_api.py list [--status X] [--project X] [--owner X]
  python3 kanban_api.py review                         # check overdue + near-due
"""

import argparse
import json
import os
import sys
import time
import urllib.request

APP_TOKEN = "OGvAbDyubamXiTs96kkccJKKnCb"
TABLE_ID = "tblY9D4T0P4uSqnc"
BASE = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}"

# Field ID map (2026-05-27)
FIELDS = {
    "任务标题": "fldkfhfIyd", "状态": "fldK9lkJMx", "截止日期": "fld1feSjMb",
    "相关文件": "fldxvAW4CR", "优先级": "fldWXpVEtu", "负责人": "flds9M0qni",
    "执行人": "fldK49Ny8y", "所属项目": "fldmRQ4Smg", "开始日期": "fldpv0sYxo",
    "任务详情": "fldE0Bpp1L",
}

# Name → open_id mapping for user fields
NAME_MAP = {
    "月夜": "ou_4c0471c3b58da8dd7883d095c3bb0843",
    "余媛天": "ou_b2853971fa42584d441b98f280524619",
    "夏与": "ou_13398e00296204b96873d16486e278af",
}

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_mgr import get_token


def name_to_user(name_str):
    """Convert comma-separated names to user field value (list of {id})."""
    if not name_str:
        return None
    return [{"id": NAME_MAP.get(n.strip(), n.strip())} for n in name_str.split(",")]


def api(method, path, body=None):
    token = get_token()
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data:
        req.add_header("Content-Type", "application/json")
    return json.loads(urllib.request.urlopen(req).read())


def date_to_ts(date_str):
    from datetime import datetime
    return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp() * 1000)


def ts_to_date(ts):
    if not ts or ts == "0":
        return ""
    from datetime import datetime, timezone, timedelta
    tz = timezone(timedelta(hours=8))
    return datetime.fromtimestamp(int(ts) / 1000, tz=tz).strftime("%Y-%m-%d")


def cmd_init():
    r = api("GET", "/fields")
    print(json.dumps({"app_token": APP_TOKEN, "table_id": TABLE_ID,
                       "fields": r["data"]["items"]}, ensure_ascii=False, indent=2))


def cmd_create(args):
    fields = {}
    if args.title:
        fields["任务标题"] = args.title
    if args.status:
        fields["状态"] = args.status
    if args.priority:
        fields["优先级"] = args.priority
    if args.owner:
        fields["负责人"] = name_to_user(args.owner)
    if args.executor:
        fields["执行人"] = name_to_user(args.executor)
    if args.project:
        fields["所属项目"] = args.project
    if args.start:
        fields["开始日期"] = date_to_ts(args.start)
    if args.deadline:
        fields["截止日期"] = date_to_ts(args.deadline)
    if args.detail:
        fields["任务详情"] = args.detail

    if not fields:
        print(json.dumps({"error": "at least --title required"}))
        sys.exit(1)

    r = api("POST", "/records", {"fields": fields})
    if r.get("code") == 0:
        rec = r["data"]["record"]
        print(json.dumps({"record_id": rec["record_id"], "fields": rec["fields"]},
                         ensure_ascii=False, indent=2))
    else:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        sys.exit(1)


def cmd_update(args):
    fields = {}

    # Text fields
    for src, dest in [("title", "任务标题"), ("status", "状态"),
                       ("priority", "优先级"), ("project", "所属项目"),
                       ("detail", "任务详情")]:
        val = getattr(args, src, None)
        if val:
            fields[dest] = val

    # User fields
    if args.owner:
        fields["负责人"] = name_to_user(args.owner)
    if args.executor:
        fields["执行人"] = name_to_user(args.executor)

    # Date fields
    if args.start:
        fields["开始日期"] = date_to_ts(args.start)
    if args.deadline:
        fields["截止日期"] = date_to_ts(args.deadline)

    if not fields:
        print(json.dumps({"error": "no fields to update"}))
        sys.exit(1)

    r = api("PUT", f"/records/{args.record_id}", {"fields": fields})
    if r.get("code") == 0:
        rec = r["data"]["record"]
        print(json.dumps({"record_id": rec["record_id"], "fields": rec["fields"]},
                         ensure_ascii=False, indent=2))
    else:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        sys.exit(1)


def cmd_list(args):
    params = ["page_size=100"]
    if args.status:
        params.append(f'filter=CurrentValue.[状态]="{args.status}"')

    r = api("GET", f"/records?{'&'.join(params)}")
    items = r.get("data", {}).get("items", [])

    results = []
    for item in items:
        rec = item["fields"]
        # Skip client-side filtered items
        if args.project and rec.get("所属项目", "") != args.project:
            continue
        if args.owner:
            owners = rec.get("负责人", [])
            owner_ids = [u.get("id", "") for u in owners] if owners else []
            if args.owner not in owner_ids:
                continue

        results.append({
            "record_id": item["record_id"],
            "title": rec.get("任务标题", ""),
            "status": rec.get("状态", ""),
            "priority": rec.get("优先级", ""),
            "owner": [u.get("id", "") for u in rec.get("负责人", [])] if rec.get("负责人") else [],
            "executor": [u.get("id", "") for u in rec.get("执行人", [])] if rec.get("执行人") else [],
            "project": rec.get("所属项目", ""),
            "deadline": ts_to_date(rec.get("截止日期", "0")),
        })

    print(json.dumps(results, ensure_ascii=False, indent=2))


def cmd_review(args=None):
    now_ts = int(time.time() * 1000)
    three_days = 3 * 24 * 3600 * 1000

    r = api("GET", "/records?page_size=200")
    items = r.get("data", {}).get("items", [])

    overdue, upcoming = [], []
    for item in items:
        rec = item["fields"]
        status = rec.get("状态", "")
        if status in ("已完成",):
            continue

        deadline = int(rec.get("截止日期", "0") or "0")
        if deadline == 0:
            continue

        owners = rec.get("负责人", [])
        owner_ids = [u.get("id", "") for u in owners] if owners else []

        entry = {
            "record_id": item["record_id"],
            "title": rec.get("任务标题", ""),
            "status": status,
            "owner": owner_ids,
            "deadline": ts_to_date(str(deadline)),
        }

        if deadline < now_ts and status != "已完成":
            entry["type"] = "已逾期"
            overdue.append(entry)
        elif 0 < (deadline - now_ts) <= three_days:
            entry["type"] = "即将逾期"
            upcoming.append(entry)

    print(json.dumps({"overdue": overdue, "upcoming": upcoming,
                       "total_overdue": len(overdue), "total_upcoming": len(upcoming)},
                       ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Project Kanban CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init")

    p = sub.add_parser("create")
    p.add_argument("--title")
    p.add_argument("--status", default="待办")
    p.add_argument("--priority", default="P2-中")
    p.add_argument("--owner")
    p.add_argument("--executor")
    p.add_argument("--project")
    p.add_argument("--start")
    p.add_argument("--deadline")
    p.add_argument("--detail")

    p = sub.add_parser("update")
    p.add_argument("record_id")
    p.add_argument("--title")
    p.add_argument("--status")
    p.add_argument("--priority")
    p.add_argument("--owner")
    p.add_argument("--executor")
    p.add_argument("--project")
    p.add_argument("--start")
    p.add_argument("--deadline")
    p.add_argument("--detail")

    p = sub.add_parser("list")
    p.add_argument("--status")
    p.add_argument("--project")
    p.add_argument("--owner")

    sub.add_parser("review")

    args = parser.parse_args()
    cmds = {"init": cmd_init, "create": cmd_create, "update": cmd_update,
             "list": cmd_list, "review": cmd_review}
    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
