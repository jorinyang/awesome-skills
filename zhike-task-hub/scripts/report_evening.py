#!/usr/bin/env python3
"""晚报脚本 (cron: 每天 23:00)

从 Task v2 清单拉取 → 今日完成/未完成对比 + 明日预警 → 格式化群消息。
空任务跳过。
"""

import datetime
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from task_v2_api import TaskV2API

log = logging.getLogger(__name__)
TZ = datetime.timezone(datetime.timedelta(hours=8))


def _completed_today(task: dict) -> bool:
    """检查任务是否在今天完成。completed_at 是毫秒。"""
    cat = task.get("completed_at", "0") or "0"
    try:
        ms = int(cat)
        if ms <= 0:
            return False
        dt = datetime.datetime.fromtimestamp(ms / 1000, tz=TZ)
        return dt.date() == datetime.datetime.now(TZ).date()
    except (ValueError, TypeError):
        return False


def _due_date(ts_sec: str) -> datetime.date | None:
    try:
        s = int(ts_sec)
        if s <= 0:
            return None
        return datetime.datetime.fromtimestamp(s, tz=TZ).date()
    except (ValueError, TypeError):
        return None


def run_evening(tasklist_guid: str) -> str | None:
    api = TaskV2API()
    tasks = api.list_tasks(tasklist_guid)
    if not tasks:
        return None

    today = datetime.datetime.now(TZ).date()
    tomorrow = today + datetime.timedelta(days=1)

    completed = []
    missed = []
    tomorrow_due = []

    for t in tasks:
        d = api.task_to_dict(t)

        # 今日完成
        if d["is_completed"] and _completed_today(t):
            completed.append(d)
            continue

        # 未完成 — 检查是否今日截止
        if not d["is_completed"]:
            dd = _due_date(d.get("due_ts_sec", "0"))
            if dd == today:
                missed.append(d)
            elif dd == tomorrow:
                tomorrow_due.append(d)

    if not completed and not missed and not tomorrow_due:
        return None

    lines = ["🌙 **晚报**"]

    if completed:
        lines.append(f"\n✅ 今日完成 ({len(completed)} 条)")
        for item in completed:
            lines.append(f"  • ~~{item['summary']}~~")

    if missed:
        lines.append(f"\n❌ 今日未完成 ({len(missed)} 条)")
        for item in missed:
            lines.append(f"  • {item['summary']}")

    if tomorrow_due:
        lines.append(f"\n📅 明日截止 ({len(tomorrow_due)} 条)")
        for item in tomorrow_due:
            lines.append(f"  • {item['summary']}")

    msg = "\n".join(lines)
    return msg


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    p = argparse.ArgumentParser(description="Evening report")
    p.add_argument("tasklist_guid")
    args = p.parse_args()

    msg = run_evening(args.tasklist_guid)
    if msg:
        print(msg)
    else:
        print("(no tasks, report skipped)")
