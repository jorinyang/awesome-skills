#!/usr/bin/env python3
"""周报数据收集脚本 (cron: 周一 8:00)

从 Task v2 清单拉取本周任务（含 description） → 输出 JSON。
Agent 读取此 JSON → LLM 分析 → 创建飞书文档 → 发送群链接。
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


def collect_weekly_tasks(tasklist_guid: str) -> list[dict]:
    """收集本周全部任务（含详情），转为报告用格式。"""
    api = TaskV2API()
    tasks = api.list_tasks_full(tasklist_guid)

    if not tasks:
        return []

    today = datetime.datetime.now(TZ).date()
    week_start = today - datetime.timedelta(days=today.weekday())  # 本周一

    results = []
    for t in tasks:
        d = api.task_to_dict(t)
        # 只取本周的任务（按创建时间或截止日期）
        due_dt = None
        due_ts = d.get("due_ts_sec", "0") or "0"
        try:
            s = int(due_ts)
            if s > 0:
                due_dt = datetime.datetime.fromtimestamp(s, tz=TZ).date()
        except (ValueError, TypeError):
            pass

        created = d.get("created_at", "0") or "0"
        try:
            created_ms = int(created)
            if created_ms > 0:
                created_dt = datetime.datetime.fromtimestamp(created_ms / 1000, tz=TZ).date()
            else:
                created_dt = None
        except (ValueError, TypeError):
            created_dt = None

        # 截止日期在本周 OR 创建日期在本周
        in_scope = (
            (due_dt and week_start <= due_dt <= today + datetime.timedelta(days=6))
            or (created_dt and week_start <= created_dt <= today)
        )
        if not in_scope:
            continue

        desc = d.get("description", "") or ""
        results.append({
            "summary": d["summary"],
            "description": desc if desc.strip() else "【缺详情】",
            "is_completed": d["is_completed"],
            "due_date": d.get("due_date", ""),
            "assignee": "",  # 从 collaborator_ids 解析
            "project": "",
        })

    log.info("weekly: collected %d tasks (total: %d)", len(results), len(tasks))
    return results


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    p = argparse.ArgumentParser(description="Weekly report data collector")
    p.add_argument("tasklist_guid")
    args = p.parse_args()

    data = collect_weekly_tasks(args.tasklist_guid)
    print(json.dumps(data, ensure_ascii=False, indent=2))
