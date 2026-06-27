#!/usr/bin/env python3
"""早报脚本 (cron: 每天 9:00)

从 Task v2 清单拉取 → 筛选今日截止 + 已逾期 → 格式化群消息。
周末节假日照发。周期内无任务则跳过。
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


def _due_to_date(ts_sec: str) -> datetime.date | None:
    try:
        s = int(ts_sec)
        if s <= 0:
            return None
        return datetime.datetime.fromtimestamp(s, tz=TZ).date()
    except (ValueError, TypeError):
        return None


def run_morning(tasklist_guid: str) -> str | None:
    """执行早报，返回消息文本。无任务返回 None。"""
    api = TaskV2API()
    tasks = api.list_tasks(tasklist_guid)
    if not tasks:
        log.info("morning: no tasks, skip")
        return None

    today = datetime.datetime.now(TZ).date()
    due_today = []
    overdue = []

    for t in tasks:
        d = api.task_to_dict(t)
        if d["is_completed"]:
            continue  # 已完成的不在早报展示

        due_dt = _due_to_date(d.get("due_ts_sec", "0"))
        if due_dt is None:
            continue
        if due_dt < today:
            overdue.append(d)
        elif due_dt == today:
            due_today.append(d)

    if not due_today and not overdue:
        log.info("morning: no due/overdue tasks, skip")
        return None

    lines = ["☀️ **早报**"]
    tz_name = "CST"

    if due_today:
        lines.append(f"\n📌 今日截止 ({len(due_today)} 条)")
        for item in due_today:
            assignee = item.get("assignee", "未分配")
            lines.append(f"  • {item['summary']} — {assignee}")

    if overdue:
        lines.append(f"\n⚠️ 已逾期 ({len(overdue)} 条)")
        for item in overdue:
            due_d = _due_to_date(item.get("due_ts_sec", "0"))
            days = (today - due_d).days if due_d else "?"
            assignee = item.get("assignee", "未分配")
            lines.append(f"  • {item['summary']} — 逾期{days}天 — {assignee}")

    msg = "\n".join(lines)
    log.info("morning report: %d due, %d overdue", len(due_today), len(overdue))
    return msg


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    p = argparse.ArgumentParser(description="Morning report")
    p.add_argument("tasklist_guid")
    args = p.parse_args()

    msg = run_morning(args.tasklist_guid)
    if msg:
        print(msg)
    else:
        print("(no tasks, report skipped)")
