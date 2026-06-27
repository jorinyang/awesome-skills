#!/usr/bin/env python3
"""月报数据收集脚本 (cron: 每月 1 日 7:30)

从 Task v2 清单拉取本月全部任务（含 description） → 输出 JSON。
Agent 读取此 JSON → LLM 深度分析 → 创建飞书文档 → 发送群链接。
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


def collect_monthly_tasks(tasklist_guid: str) -> list[dict]:
    """收集本月全部任务（含详情），转为报告用格式。"""
    api = TaskV2API()
    tasks = api.list_tasks_full(tasklist_guid)

    if not tasks:
        return []

    today = datetime.datetime.now(TZ).date()
    month_start = today.replace(day=1)

    results = []
    for t in tasks:
        d = api.task_to_dict(t)

        # 通过 completed_at 或 created_at 判断是否属于本月
        completed_at = d.get("completed_at", "0") or "0"
        created_at = d.get("created_at", "0") or "0"

        in_scope = False
        for ts_ms in [completed_at, created_at]:
            try:
                ms = int(ts_ms)
                if ms > 0:
                    dt = datetime.datetime.fromtimestamp(ms / 1000, tz=TZ).date()
                    if month_start <= dt <= today:
                        in_scope = True
                        break
            except (ValueError, TypeError):
                continue

        if not in_scope:
            # Also check due date
            due_ts = d.get("due_ts_sec", "0") or "0"
            try:
                s = int(due_ts)
                if s > 0:
                    due_dt = datetime.datetime.fromtimestamp(s, tz=TZ).date()
                    if month_start <= due_dt <= today:
                        in_scope = True
            except (ValueError, TypeError):
                pass

        if not in_scope:
            continue

        desc = d.get("description", "") or ""
        results.append({
            "summary": d["summary"],
            "description": desc if desc.strip() else "【缺详情】",
            "is_completed": d["is_completed"],
            "due_date": d.get("due_date", ""),
            "assignee": "",
            "project": "",
            "created_at": d.get("created_at", ""),
            "completed_at": d.get("completed_at", ""),
        })

    log.info("monthly: collected %d tasks (total: %d)", len(results), len(tasks))
    return results


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    p = argparse.ArgumentParser(description="Monthly report data collector")
    p.add_argument("tasklist_guid")
    args = p.parse_args()

    data = collect_monthly_tasks(args.tasklist_guid)
    print(json.dumps(data, ensure_ascii=False, indent=2))
