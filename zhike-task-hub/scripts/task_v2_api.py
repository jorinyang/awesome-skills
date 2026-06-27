#!/usr/bin/env python3
"""Feishu Task v2 API wrapper — full CRUD with tasklist support.

Usage:
    from task_v2_api import TaskV2API, TaskStatus

    api = TaskV2API()
    guid = api.create_task("设计评审", description="首页UI评审")
    api.add_to_tasklist(guid, tasklist_guid)
    tasks = api.list_tasks(tasklist_guid)
    detail = api.get_task(guid)  # includes description
    api.complete_task(guid)
"""

import json
import logging
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

# Reuse existing token manager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "project-kanban", "scripts"))
from token_mgr import get_token  # noqa: E402

log = logging.getLogger(__name__)

BASE = "https://open.feishu.cn/open-apis/task/v2"
TIMEOUT = 15
PAGE_SIZE = 50
RETRY_MAX = 2
RETRY_DELAY = 1.5

NAME_MAP = {
    "月夜": "ou_4c0471c3b58da8dd7883d095c3bb0843",
    "余媛天": "ou_b2853971fa42584d441b98f280524619",
    "夏与": "ou_13398e00296204b96873d16486e278af",
}
ID_TO_NAME = {v: k for k, v in NAME_MAP.items()}


class TaskStatus:
    TODO = "todo"
    COMPLETED = "completed"


# ── field names that can be patched ──────────────────────────
PATCHABLE_FIELDS = {
    "agent_task_progress", "agent_task_status", "completed_at",
    "custom_complete", "custom_fields", "description", "due",
    "extra", "is_milestone", "mode", "repeat_rule",
    "start", "summary", "text_deliveries",
}


def _resolve_name(name: str) -> str:
    """人名 → open_id"""
    return NAME_MAP.get(name, name)


def _open_id_to_name(oid: str) -> str:
    """open_id → 人名 (fallback to id itself)"""
    return ID_TO_NAME.get(oid, oid)


def _date_to_sec(date_str: str) -> str:
    """yyyy-MM-dd → 秒级 UTC 午夜时间戳 (Task v2 due.timestamp)。
    使用 UTC 避免 API 的时区偏移导致日期回退 1 天。
    """
    import datetime
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    dt = dt.replace(tzinfo=datetime.timezone.utc)
    return str(int(dt.timestamp()))


# ═══════════════════════════════════════════════════════════════
#  TaskV2API
# ═══════════════════════════════════════════════════════════════

class TaskV2API:
    """Feishu Task v2 REST wrapper (bot identity)."""

    def __init__(self):
        self._token: Optional[str] = None
        self._token_ts: float = 0

    # ── token ────────────────────────────────────────────────

    def _ensure_token(self) -> str:
        now = time.time()
        if self._token and (now - self._token_ts) < 5400:  # 90 min缓存
            return self._token
        self._token = get_token()
        self._token_ts = now
        return self._token

    # ── HTTP helpers ─────────────────────────────────────────

    def _req(self, method: str, path: str, body: dict = None):
        url = f"{BASE}{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self._ensure_token()}")
        if data:
            req.add_header("Content-Type", "application/json")
        return json.loads(urllib.request.urlopen(req, timeout=TIMEOUT).read())

    def _req_retry(self, method: str, path: str, body: dict = None) -> dict:
        last_err = None
        for attempt in range(1 + RETRY_MAX):
            try:
                return self._req(method, path, body)
            except urllib.error.HTTPError as e:
                body_text = e.read().decode(errors="replace")[:400]
                last_err = f"HTTP {e.code}: {body_text}"
                if e.code in (429, 503):  # rate-limit / transient
                    time.sleep(RETRY_DELAY * attempt)
                    continue
                raise
            except Exception as e:
                last_err = str(e)
                if attempt < RETRY_MAX:
                    time.sleep(RETRY_DELAY)
                    continue
                raise
        raise RuntimeError(f"Retries exhausted: {last_err}")

    def _check(self, resp: dict, op: str = "") -> dict:
        code = resp.get("code", -1)
        if code != 0:
            msg = resp.get("msg", "unknown")
            raise RuntimeError(f"{op} failed: code={code} msg={msg}")
        return resp.get("data", {})

    # ── tasklist ─────────────────────────────────────────────

    def create_tasklist(self, name: str, member_open_ids: list = None) -> str:
        """创建任务清单，返回 guid。"""
        body = {"name": name}
        if member_open_ids:
            body["members"] = [{"id": uid, "role": "editor"} for uid in member_open_ids]
        data = self._check(self._req_retry("POST", "/tasklists?user_id_type=open_id", body), "create_tasklist")
        guid = data["tasklist"]["guid"]
        log.info("created tasklist %s guid=%s", name, guid)
        return guid

    def delete_tasklist(self, guid: str):
        self._check(self._req_retry("DELETE", f"/tasklists/{guid}"), "delete_tasklist")
        log.info("deleted tasklist guid=%s", guid)

    # ── task ─────────────────────────────────────────────────

    def create_task(
        self,
        summary: str,
        description: str = "",
        due_date: str = "",        # yyyy-MM-dd
        collaborator_names: str = "",  # comma-separated 人名
        follower_names: str = "",
    ) -> str:
        """创建任务，返回 task guid。"""
        body: dict = {
            "summary": summary,
        }
        if description:
            body["description"] = description
        if due_date:
            body["due"] = {
                "timestamp": _date_to_sec(due_date),
                "is_all_day": False,
            }
        if collaborator_names:
            body["collaborator_ids"] = [
                _resolve_name(n.strip()) for n in collaborator_names.split(",")
            ]
        if follower_names:
            body["follower_ids"] = [
                _resolve_name(n.strip()) for n in follower_names.split(",")
            ]

        data = self._check(
            self._req_retry("POST", "/tasks?user_id_type=open_id", body),
            "create_task",
        )
        guid = data["task"]["guid"]
        log.info("created task '%s' guid=%s", summary, guid)
        return guid

    def get_task(self, guid: str) -> dict:
        """获取单任务完整详情（含 description）。"""
        data = self._check(self._req_retry("GET", f"/tasks/{guid}"), "get_task")
        return data["task"]

    def update_task(self, guid: str, **fields) -> dict:
        """PATCH 可更新字段。fields 仅允许 PATCHABLE_FIELDS 子集。"""
        task = {}
        update_fields = []
        for k, v in fields.items():
            if k not in PATCHABLE_FIELDS:
                log.warning("field '%s' not patchable, skipping", k)
                continue
            task[k] = v
            update_fields.append(k)

        if not task:
            raise ValueError("no patchable fields provided")

        body = {"task": task, "update_fields": update_fields}
        data = self._check(
            self._req_retry("PATCH", f"/tasks/{guid}?user_id_type=open_id", body),
            "update_task",
        )
        return data["task"]

    def complete_task(self, guid: str) -> dict:
        """标记任务完成。"""
        ts = str(int(time.time() * 1000))  # completed_at 是毫秒
        return self.update_task(guid, completed_at=ts)

    def reopen_task(self, guid: str) -> dict:
        """重新打开已完成任务。"""
        return self.update_task(guid, completed_at="0")

    def delete_task(self, guid: str):
        self._check(self._req_retry("DELETE", f"/tasks/{guid}"), "delete_task")
        log.info("deleted task guid=%s", guid)

    # ── tasklist ↔ task ──────────────────────────────────────

    def add_to_tasklist(self, task_guid: str, tasklist_guid: str):
        """将任务添加到清单（通过 lark-cli，REST 端点待确认）。"""
        result = subprocess.run(
            [
                "lark-cli", "task", "+tasklist-task-add",
                "--tasklist-id", tasklist_guid,
                "--task-id", task_guid,
                "--as", "bot",
            ],
            capture_output=True, text=True, timeout=TIMEOUT,
        )
        if result.returncode != 0:
            raise RuntimeError(f"lark-cli tasklist-task-add failed: {result.stderr}")
        resp = json.loads(result.stdout)
        if not resp.get("ok"):
            raise RuntimeError(f"lark-cli returned error: {resp}")
        log.info("added task %s → tasklist %s", task_guid, tasklist_guid)

    # ── list / search ────────────────────────────────────────

    def list_tasks(self, tasklist_guid: str, page_size: int = PAGE_SIZE) -> list[dict]:
        """列出清单中的所有任务（摘要视图，不含 description）。自动翻页。"""
        all_items = []
        page_token = ""
        while True:
            url = f"/tasklists/{tasklist_guid}/tasks?page_size={page_size}"
            if page_token:
                url += f"&page_token={page_token}"
            data = self._check(self._req_retry("GET", url), "list_tasks")
            items = data.get("items", [])
            all_items.extend(items)
            if not data.get("has_more"):
                break
            page_token = data.get("page_token", "")
        log.info("listed %d tasks from tasklist %s", len(all_items), tasklist_guid)
        return all_items

    # ── convenience ──────────────────────────────────────────

    def list_tasks_full(self, tasklist_guid: str) -> list[dict]:
        """列出清单所有任务并逐个获取详情（含 description）。
        注意：每个任务额外 1 次 API 调用。
        """
        summaries = self.list_tasks(tasklist_guid)
        full = []
        for s in summaries:
            try:
                detail = self.get_task(s["guid"])
                full.append(detail)
            except Exception:
                log.exception("failed to get detail for %s, using summary", s.get("guid"))
                full.append(s)
        return full

    @staticmethod
    def _parse_due(due_raw) -> dict:
        """v2 API 返回的 due 可能是 Python dict 字符串 (ast) 或 JSON 字符串。"""
        if isinstance(due_raw, dict):
            return due_raw
        if isinstance(due_raw, str) and due_raw.strip():
            # 先试 JSON，再试 Python literal
            for parser in (json.loads, __import__("ast").literal_eval):
                try:
                    parsed = parser(due_raw)
                    if isinstance(parsed, dict):
                        return parsed
                except Exception:
                    continue
        return {}

    def task_to_dict(self, task: dict) -> dict:
        """将 Task v2 原始数据转为标准化 dict（供报告/同步使用）。"""
        due = self._parse_due(task.get("due"))
        due_ts = due.get("timestamp", "0")
        due_str = ""
        if due_ts and due_ts != "0":
            try:
                import datetime
                ts_int = int(due_ts)
                # 用 CST 显示日期，兼容 UTC 午夜和本地时间戳
                dt_cst = datetime.datetime.fromtimestamp(
                    ts_int, tz=datetime.timezone(datetime.timedelta(hours=8))
                )
                due_str = dt_cst.strftime("%Y-%m-%d")
            except Exception:
                due_str = str(due_ts)

        completed_at = task.get("completed_at", "0")
        is_completed = int(completed_at) > 0 if completed_at else False

        collaborators = task.get("collaborators", []) or []
        followers = task.get("followers", []) or []

        # creator 也可能是字符串化的 dict
        creator_raw = task.get("creator")
        creator_id = ""
        if isinstance(creator_raw, dict):
            creator_id = creator_raw.get("id", "")
        elif isinstance(creator_raw, str):
            try:
                parsed = __import__("ast").literal_eval(creator_raw)
                if isinstance(parsed, dict):
                    creator_id = parsed.get("id", "")
            except Exception:
                pass

        return {
            "guid": task.get("guid", ""),
            "summary": task.get("summary", ""),
            "description": task.get("description", ""),
            "is_completed": is_completed,
            "due_date": due_str,
            "due_ts_sec": due_ts,
            "creator": creator_id,
            "collaborator_ids": [c.get("id", "") for c in collaborators if isinstance(c, dict)],
            "follower_ids": [f.get("id", "") for f in followers if isinstance(f, dict)],
            "created_at": task.get("created_at", ""),
            "completed_at": completed_at,
            "url": task.get("url", ""),
        }

    def setup_tasklist(self, name: str, member_names: list = None) -> str:
        """一站式：创建清单 → 加入成员 → 返回 guid。
        如果成员名不在 NAME_MAP 中则跳过。
        """
        member_ids = []
        if member_names:
            for name in member_names:
                oid = NAME_MAP.get(name)
                if oid:
                    member_ids.append(oid)
                else:
                    log.warning("unknown member name '%s', skipped", name)
        return self.create_tasklist(name, member_ids)


# ═══════════════════════════════════════════════════════════════
#  CLI (for testing)
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    api = TaskV2API()

    import argparse
    p = argparse.ArgumentParser(description="Task v2 API CLI")
    sp = p.add_subparsers(dest="cmd")

    c = sp.add_parser("create-tasklist")
    c.add_argument("name")
    c.add_argument("--members", default="")

    c = sp.add_parser("create-task")
    c.add_argument("summary")
    c.add_argument("--description", default="")
    c.add_argument("--due", default="")
    c.add_argument("--collaborators", default="")
    c.add_argument("--followers", default="")

    c = sp.add_parser("list-tasks")
    c.add_argument("tasklist_guid")

    c = sp.add_parser("list-tasks-full")
    c.add_argument("tasklist_guid")

    c = sp.add_parser("get-task")
    c.add_argument("guid")

    c = sp.add_parser("complete-task")
    c.add_argument("guid")

    c = sp.add_parser("delete-task")
    c.add_argument("guid")

    args = p.parse_args()

    if args.cmd == "create-tasklist":
        members = [m.strip() for m in args.members.split(",") if m.strip()] if args.members else None
        guid = api.setup_tasklist(args.name, members)
        print(json.dumps({"guid": guid}, ensure_ascii=False))

    elif args.cmd == "create-task":
        guid = api.create_task(
            args.summary,
            description=args.description,
            due_date=args.due,
            collaborator_names=args.collaborators,
            follower_names=args.followers,
        )
        api.add_to_tasklist(guid, "PLACEHOLDER_TASKLIST_GUID")
        print(json.dumps({"guid": guid}, ensure_ascii=False))

    elif args.cmd == "list-tasks":
        tasks = api.list_tasks(args.tasklist_guid)
        results = [api.task_to_dict(t) for t in tasks]
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.cmd == "list-tasks-full":
        tasks = api.list_tasks_full(args.tasklist_guid)
        results = [api.task_to_dict(t) for t in tasks]
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.cmd == "get-task":
        task = api.get_task(args.guid)
        print(json.dumps(api.task_to_dict(task), ensure_ascii=False, indent=2))

    elif args.cmd == "complete-task":
        api.complete_task(args.guid)
        print(json.dumps({"completed": args.guid}))

    elif args.cmd == "delete-task":
        api.delete_task(args.guid)
        print(json.dumps({"deleted": args.guid}))
