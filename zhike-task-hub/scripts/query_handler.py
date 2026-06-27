#!/usr/bin/env python3
"""对话查询处理器 (对话触发词匹配)

识别关键词 → 路由查询类型 → 扫 Bitable → 格式化回复。
由 SKILL.md 的 triggers 触发时调用。
"""

import json
import logging
import os
import subprocess
import sys

log = logging.getLogger(__name__)

BITABLE_APP = "OGvAbDyubamXiTs96kkccJKKnCb"
BITABLE_TABLE = "tblY9D4T0P4uSqnc"


# ── 关键词匹配 ──────────────────────────────────────────────

GREEN_KEYWORDS = [
    "查任务", "我的待办", "有什么任务", "待办事项",
    "我的任务", "任务列表", "查待办"
]

GREEN_PROGRESS = [
    "项目进度", "项目任务", "做到哪了", "怎么样了",
]

GREEN_OVERDUE = [
    "逾期任务", "哪些逾期了", "谁的逾期最多", "检查逾期", "督办",
]

GREEN_CREATE = [
    "创建任务", "新建任务", "加个任务", "分配任务给", "让.*做",
]

GREEN_COMPLETE = [
    "完成任务", "标记完成", "做完了",
]

YELLOW_KEYWORDS = [
    "最近忙什么", "最近怎么样", "项目有进展吗", "那件事做了吗", "进展如何",
]

RED_BLOCK = [
    "有个事", "工作", "项目", "任务",
]


def classify_query(text: str) -> tuple[str, str | None]:
    """返回 (级别, 查询类型)"""
    # 🟢 明确查询
    for kw in GREEN_CREATE:
        if kw in text:
            return ("green", "create")
    for kw in GREEN_COMPLETE:
        if kw in text:
            return ("green", "complete")
    for kw in GREEN_OVERDUE:
        if kw in text:
            return ("green", "overdue")
    for kw in GREEN_PROGRESS:
        if kw in text:
            return ("green", "progress")
    for kw in GREEN_KEYWORDS:
        if kw in text:
            return ("green", "my_tasks")

    # 🟡 模糊
    for kw in YELLOW_KEYWORDS:
        if kw in text:
            return ("yellow", "fuzzy")

    # 🔴 不触发
    return ("red", None)


# ── Bitable 查询 ───────────────────────────────────────────

def query_bitable(filter_condition: str = "", page_all: bool = True) -> list[dict]:
    """通过 lark-cli 查询 Bitable 记录。"""
    cmd = [
        "lark-cli", "base", "+record-list",
        "--base-token", BITABLE_APP,
        "--table-id", BITABLE_TABLE,
        "--as", "bot",
    ]
    if filter_condition:
        cmd.extend(["--params", json.dumps({"filter": filter_condition})])
    if page_all:
        cmd.append("--page-all")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        log.error("bitable query failed: %s", result.stderr[:200])
        return []

    try:
        data = json.loads(result.stdout)
        records = data.get("data", {}).get("items", [])
        return [r.get("fields", {}) for r in records]
    except json.JSONDecodeError:
        log.warning("bitable query parse error: %s", result.stdout[:200])
        return []


def format_task_list(tasks: list[dict]) -> str:
    """格式化任务列表为文本消息。"""
    if not tasks:
        return "📭 暂无相关任务。"

    lines = []
    for i, t in enumerate(tasks[:20], 1):  # 最多显示 20 条
        title = t.get("任务标题", "无标题")
        status = t.get("状态", "未知")
        due = t.get("截止日期", "")
        project = t.get("所属项目", "")

        line = f"{i}. [{status}] {title}"
        if project:
            line += f" ({project})"
        if due:
            line += f" | 截止: {due}"
        lines.append(line)

    if len(tasks) > 20:
        lines.append(f"... 还有 {len(tasks) - 20} 条")

    return "\n".join(lines)


def handle_query(text: str, user_name: str = "") -> dict:
    """处理对话查询，返回结果 dict。"""
    level, qtype = classify_query(text)

    result = {
        "level": level,
        "type": qtype,
        "message": "",
        "tasks": [],
        "needs_clarification": False,
    }

    if level == "red":
        return result  # 不触发

    if level == "yellow":
        result["needs_clarification"] = True
        result["message"] = "你是想查任务进度吗？可以告诉我具体想了解什么？"
        return result

    if qtype == "my_tasks":
        filter_str = ""
        if user_name:
            filter_str = f'CurrentValue.[负责人]="{user_name}"'
        tasks = query_bitable(filter_str)
        result["tasks"] = tasks
        result["message"] = format_task_list(tasks)

    elif qtype == "progress":
        # 提取项目名
        project_name = text
        for kw in GREEN_PROGRESS:
            project_name = project_name.replace(kw, "").strip()
        if project_name:
            filter_str = f'CurrentValue.[所属项目]="{project_name}"'
        else:
            filter_str = ""
        tasks = query_bitable(filter_str if filter_str else "")
        result["tasks"] = tasks
        result["message"] = format_task_list(tasks)

    elif qtype == "overdue":
        filter_str = 'CurrentValue.[状态]="已逾期"'
        tasks = query_bitable(filter_str)
        result["tasks"] = tasks
        result["message"] = format_task_list(tasks)

    elif qtype == "create":
        result["message"] = "请提供：任务标题、负责人、截止日期（可选）。格式：`创建任务：XX事项，余媛天负责，6月15日截止`"

    elif qtype == "complete":
        result["message"] = "请提供任务标题或编号。格式：`完成任务：探洞线路方案定稿`"

    return result


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)

    p = argparse.ArgumentParser(description="Query handler")
    p.add_argument("query", help="用户查询文本")
    p.add_argument("--user", default="", help="查询用户名")
    args = p.parse_args()

    result = handle_query(args.query, args.user)
    print(json.dumps(result, ensure_ascii=False, indent=2))
