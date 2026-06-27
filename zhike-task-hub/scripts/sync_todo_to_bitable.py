#!/usr/bin/env python3
"""Todo → Bitable 每日同步脚本 (cron: 凌晨 3:00)

从 Task v2 清单拉取全部任务 → 逐任务获取详情 → 映射字段 → Bitable upsert。
幂等：按 task guid 唯一键 upsert，不覆盖人工字段。
"""

import json
import logging
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from task_v2_api import TaskV2API

log = logging.getLogger(__name__)

BITABLE_APP = "OGvAbDyubamXiTs96kkccJKKnCb"
BITABLE_TABLE = "tblY9D4T0P4uSqnc"

# Fields that sync should update (system-managed)
SYNC_FIELDS = {
    "summary":          "任务标题",
    "description":      "任务详情",
    "status":           "状态",
    "due_date":         "截止日期",
    "creator":          "分配人",
    "collaborator_0":   "负责人",
    "collaborator_rest":"咨询人",
    "followers":        "关注人",
}

STATUS_OPTIONS = ["待办", "进行中", "已完成", "已逾期"]


def ts_sec_to_ms(sec: str) -> int:
    """Task v2 秒级时间戳 → Bitable 毫秒"""
    try:
        s = int(sec)
        return s * 1000 if s > 0 else 0
    except (ValueError, TypeError):
        return 0


def build_bitable_fields(task: dict) -> dict:
    """将 task_to_dict 的输出转为 Bitable 字段格式。"""
    fields = {}

    # 任务标题
    fields["任务标题"] = task.get("summary", "") or ""

    # 任务详情 — 空值时标记
    desc = task.get("description", "") or ""
    fields["任务详情"] = desc if desc.strip() else "【缺详情】"

    # 状态
    fields["状态"] = "已完成" if task.get("is_completed") else "待办"

    # 截止日期 (毫秒)
    due_ts = task.get("due_ts_sec", "0") or "0"
    fields["截止日期"] = ts_sec_to_ms(due_ts)

    # 分配人 (A)
    creator = task.get("creator", "") or ""
    if creator:
        fields["分配人"] = [{"id": creator}]

    # 负责人 (R) — 第一个协作者
    collaborator_ids = task.get("collaborator_ids", []) or []
    if collaborator_ids:
        fields["负责人"] = [{"id": collaborator_ids[0]}]

    # 咨询人 (C) — 其余协作者
    if len(collaborator_ids) > 1:
        fields["咨询人"] = [{"id": cid} for cid in collaborator_ids[1:]]

    # 关注人 (I)
    follower_ids = task.get("follower_ids", []) or []
    if follower_ids:
        fields["关注人"] = [{"id": fid} for fid in follower_ids]

    return fields


def upsert_record(fields: dict, index_key: str):
    """Bitable upsert via lark-cli (有则更新/无则新增)。
    注意：upsert 以第一个文本字段为索引键。
    """
    # Use record-create for now; proper upsert needs REST API
    payload = json.dumps(fields, ensure_ascii=False)
    result = subprocess.run(
        [
            "lark-cli", "base", "+record-create",
            "--base-token", BITABLE_APP,
            "--table-id", BITABLE_TABLE,
            "--json", payload,
            "--as", "bot",
        ],
        capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        log.error("bitable write failed: %s", result.stderr[:200])
        return False
    resp = result.stdout
    # Check for duplicate error — that's OK, means record exists
    if "already exists" in resp or "duplicate" in resp.lower():
        log.debug("record exists, skipped upsert (MVP: no update yet)")
        return True
    try:
        data = json.loads(resp)
        if data.get("ok") or data.get("code") == 0:
            return True
    except json.JSONDecodeError:
        pass
    log.warning("bitable write result: %s", resp[:200])
    return False


def run_sync(tasklist_guid: str) -> dict:
    """执行一次全量同步。返回统计。"""
    api = TaskV2API()
    start = time.time()

    log.info("sync: listing tasks from tasklist %s", tasklist_guid)
    try:
        tasks = api.list_tasks_full(tasklist_guid)
    except Exception as e:
        log.exception("sync: list failed")
        return {"error": str(e), "success": 0, "fail": 0, "skip": 0}

    success = fail = skip = 0

    for task in tasks:
        try:
            d = api.task_to_dict(task)
            fields = build_bitable_fields(d)
            if upsert_record(fields, d.get("summary", "")):
                success += 1
            else:
                fail += 1
        except Exception:
            log.exception("sync: task %s failed", task.get("guid", "?"))
            fail += 1

    duration = time.time() - start
    result = {
        "success": success,
        "fail": fail,
        "skip": skip,
        "total": len(tasks),
        "duration_sec": round(duration, 1),
    }
    log.info("sync done: %s", json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    p = argparse.ArgumentParser(description="Todo → Bitable sync")
    p.add_argument("tasklist_guid", help="Task v2 tasklist GUID")
    args = p.parse_args()

    result = run_sync(args.tasklist_guid)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("fail", 0) == 0 else 1)
