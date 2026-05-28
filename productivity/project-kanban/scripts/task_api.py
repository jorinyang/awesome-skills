#!/usr/bin/env python3
"""Feishu Task API — create/update/delete tasks with assignment and due date.

Usage:
  python3 task_api.py create --summary "..." [--collaborator X] [--follower X] [--deadline yyyy-MM-dd]
  python3 task_api.py update <task_id> [opts]
  python3 task_api.py delete <task_id>
  python3 task_api.py list
"""

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

BASE = "https://open.feishu.cn/open-apis/task/v1"

NAME_MAP = {
    "月夜": "ou_4c0471c3b58da8dd7883d095c3bb0843",
    "余媛天": "ou_b2853971fa42584d441b98f280524619",
    "夏与": "ou_13398e00296204b96873d16486e278af",
}

TZ = timezone(timedelta(hours=8))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_mgr import get_token


def api(method, path, body=None):
    token = get_token()
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data:
        req.add_header("Content-Type", "application/json")
    return json.loads(urllib.request.urlopen(req).read())


def resolve_names(s):
    """Convert comma-separated names to open_id list."""
    if not s:
        return None
    return [NAME_MAP.get(n.strip(), n.strip()) for n in s.split(",")]


def date_to_ts(date_str):
    """yyyy-MM-dd → unix seconds for Task due.time field."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    dt = dt.replace(tzinfo=TZ)
    # For is_all_day=true, use the time at 00:00 UTC+8
    return str(int(dt.timestamp()))


def cmd_create(args):
    body = {
        "summary": args.summary,
        "origin": {"platform_i18n_name": '{"en_us":"Hermes Kanban","zh_cn":"Hermes Kanban"}'},
    }
    if args.description:
        body["description"] = args.description
    if args.collaborator:
        body["collaborator_ids"] = resolve_names(args.collaborator)
    if args.follower:
        body["follower_ids"] = resolve_names(args.follower)
    if args.deadline:
        body["due"] = {
            "time": date_to_ts(args.deadline),
            "is_all_day": True,
            "timezone": "Asia/Shanghai",
        }

    r = api("POST", "/tasks?user_id_type=open_id", body)
    if r.get("code") == 0:
        t = r["data"]["task"]
        due = t.get("due", {})
        print(json.dumps({
            "task_id": t["id"],
            "summary": t["summary"],
            "collaborators": [c.get("id") for c in t.get("collaborators", [])],
            "followers": [f.get("id") for f in t.get("followers", [])],
            "due": due.get("time", "0"),
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        sys.exit(1)


def cmd_update(args):
    task = {}
    update_fields = []

    for field in ["summary", "description"]:
        val = getattr(args, field, None)
        if val:
            task[field] = val
            update_fields.append(field)

    if args.collaborator:
        task["collaborator_ids"] = resolve_names(args.collaborator)
        update_fields.append("collaborator_ids")
    if args.follower:
        task["follower_ids"] = resolve_names(args.follower)
        update_fields.append("follower_ids")
    if args.deadline:
        task["due"] = {
            "time": date_to_ts(args.deadline),
            "is_all_day": True,
            "timezone": "Asia/Shanghai",
        }
        update_fields.append("due")

    if not task:
        print(json.dumps({"error": "no fields to update"}))
        sys.exit(1)

    body = {"task": task, "update_fields": update_fields}
    r = api("PATCH", f"/tasks/{args.task_id}?user_id_type=open_id", body)
    if r.get("code") == 0:
        t = r["data"]["task"]
        due = t.get("due", {})
        print(json.dumps({
            "task_id": t["id"],
            "summary": t["summary"],
            "due": due.get("time", "0"),
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        sys.exit(1)


def cmd_delete(args):
    r = api("DELETE", f"/tasks/{args.task_id}")
    print(json.dumps({"deleted": r.get("code") == 0, "task_id": args.task_id}))


def cmd_list(args):
    r = api("GET", "/tasks?page_size=50")
    tasks = r.get("data", {}).get("items", [])
    results = []
    for t in tasks:
        due = t.get("due", {})
        results.append({
            "task_id": t["id"],
            "summary": t.get("summary", ""),
            "collaborators": [c.get("id") for c in t.get("collaborators", [])],
            "followers": [f.get("id") for f in t.get("followers", [])],
            "due": due.get("time", "0"),
            "complete_time": t.get("complete_time", "0"),
        })
    print(json.dumps(results, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Feishu Task CLI")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("create")
    p.add_argument("--summary", required=True)
    p.add_argument("--description")
    p.add_argument("--collaborator", help="Comma-separated names")
    p.add_argument("--follower", help="Comma-separated names")
    p.add_argument("--deadline", help="yyyy-MM-dd")

    p = sub.add_parser("update")
    p.add_argument("task_id")
    p.add_argument("--summary")
    p.add_argument("--description")
    p.add_argument("--collaborator")
    p.add_argument("--follower")
    p.add_argument("--deadline", help="yyyy-MM-dd")

    p = sub.add_parser("delete")
    p.add_argument("task_id")

    sub.add_parser("list")

    args = parser.parse_args()
    cmds = {
        "create": cmd_create,
        "update": cmd_update,
        "delete": cmd_delete,
        "list": cmd_list,
    }
    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
