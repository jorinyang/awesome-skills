#!/usr/bin/env python3
"""
执行数据采集脚本 — 从 Hermes 会话记录中提取 Skill 执行数据。

用法:
    python3 scripts/collect_trace.py --skill <skill_name> [--sessions <N>] [--output <path>]

输出:
    JSON 格式的执行数据，包含:
    - 工具调用序列和时间
    - Token 消耗
    - 错误/异常信息
    - 最终产出摘要
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Hermes 会话存储路径
HERMES_DATA_DIR = os.path.expanduser("~/.hermes")
SESSION_DB = os.path.join(HERMES_DATA_DIR, "sessions.db")

# 如果数据库不可用，尝试从日志文件读取
LOG_DIRS = [
    os.path.expanduser("~/.hermes/logs"),
    os.path.expanduser("~/.hermes-feishu/logs"),
    "/tmp/hermes_logs",
]


def find_skill_sessions(skill_name: str, max_sessions: int = 10) -> list[dict]:
    """查找包含目标 Skill 的会话记录。"""
    sessions = []

    # 尝试从 session_search 获取
    try:
        import sqlite3
        if os.path.exists(SESSION_DB):
            conn = sqlite3.connect(SESSION_DB)
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT * FROM sessions WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?",
                (f"%{skill_name}%", max_sessions),
            )
            for row in cur.fetchall():
                sessions.append(dict(row))
            conn.close()
    except Exception:
        pass

    # Fallback: 扫描日志文件
    if not sessions:
        for log_dir in LOG_DIRS:
            if not os.path.isdir(log_dir):
                continue
            for f in sorted(Path(log_dir).rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
                try:
                    data = json.loads(f.read_text())
                    content = json.dumps(data)
                    if skill_name.lower() in content.lower():
                        sessions.append({
                            "source": str(f),
                            "timestamp": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                            "data": data,
                        })
                        if len(sessions) >= max_sessions:
                            break
                except (json.JSONDecodeError, OSError):
                    continue
            if sessions:
                break

    return sessions


def extract_trace_from_session(session: dict) -> dict:
    """从单次会话中提取执行数据。"""
    trace = {
        "session_id": session.get("id") or session.get("session_id") or session.get("source"),
        "timestamp": session.get("timestamp") or session.get("created_at"),
        "skill_name": None,
        "tool_calls": [],
        "errors": [],
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_duration_ms": 0,
        "final_output": None,
        "status": "unknown",
    }

    data = session.get("data", session)

    # 提取工具调用
    if isinstance(data, list):
        for item in data:
            _extract_item(item, trace)
    elif isinstance(data, dict):
        _extract_item(data, trace)
        # 递归处理嵌套
        for key in ["messages", "steps", "interactions", "tool_calls"]:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    _extract_item(item, trace)

    trace["status"] = "success" if not trace["errors"] else "partial_success" if trace["final_output"] else "failed"
    return trace


def _extract_item(item: dict, trace: dict):
    """从单个交互项中提取信息。"""
    if not isinstance(item, dict):
        return

    # Token 统计
    if "usage" in item:
        usage = item["usage"]
        trace["total_input_tokens"] += usage.get("input_tokens", 0) or usage.get("prompt_tokens", 0)
        trace["total_output_tokens"] += usage.get("output_tokens", 0) or usage.get("completion_tokens", 0)

    if "input_tokens" in item:
        trace["total_input_tokens"] += item.get("input_tokens", 0)
    if "output_tokens" in item:
        trace["total_output_tokens"] += item.get("output_tokens", 0)

    # 工具调用
    if item.get("type") in ("tool_call", "tool_use", "function_call"):
        trace["tool_calls"].append({
            "tool": item.get("name") or item.get("function", {}).get("name", "unknown"),
            "input": item.get("input") or item.get("arguments", {}),
            "output": item.get("output") or item.get("result"),
            "duration_ms": item.get("duration_ms") or item.get("elapsed", 0),
            "status": "error" if item.get("is_error") else "success",
        })

    # Skill 名称
    if not trace["skill_name"]:
        for key in ["skill", "skill_name", "invoked_skill", "active_skill"]:
            if key in item and item[key]:
                trace["skill_name"] = item[key]
                break

    # 错误信息
    if item.get("is_error") or item.get("level") == "error" or "error" in str(item).lower():
        trace["errors"].append({
            "message": item.get("message") or item.get("error") or str(item.get("output", ""))[:200],
            "type": item.get("error_type") or item.get("exception_type", "unknown"),
        })

    # 最终输出
    if item.get("role") == "assistant" and item.get("content") and not item.get("tool_calls"):
        # 最后一个 assistant 消息通常是最终输出
        trace["final_output"] = str(item["content"])[:500]


def aggregate_traces(traces: list[dict]) -> dict:
    """聚合多次执行的数据。"""
    if not traces:
        return {"error": "无执行数据"}

    total_tokens = sum(t["total_input_tokens"] + t["total_output_tokens"] for t in traces)
    total_duration = sum(t["total_duration_ms"] for t in traces)
    total_errors = sum(len(t["errors"]) for t in traces)
    total_tool_calls = sum(len(t["tool_calls"]) for t in traces)
    success_count = sum(1 for t in traces if t["status"] == "success")

    return {
        "session_count": len(traces),
        "success_rate": success_count / len(traces) if traces else 0,
        "total_tokens": total_tokens,
        "avg_tokens_per_session": total_tokens / len(traces) if traces else 0,
        "total_duration_ms": total_duration,
        "avg_duration_ms": total_duration / len(traces) if traces else 0,
        "total_errors": total_errors,
        "total_tool_calls": total_tool_calls,
        "tool_call_errors": sum(1 for t in traces for tc in t["tool_calls"] if tc["status"] == "error"),
        "traces": traces,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="采集 Skill 执行数据")
    parser.add_argument("--skill", required=True, help="目标 Skill 名称")
    parser.add_argument("--sessions", type=int, default=10, help="最多查询的会话数")
    parser.add_argument("--output", default=None, help="输出文件路径")
    args = parser.parse_args()

    sessions = find_skill_sessions(args.skill, args.sessions)
    traces = [extract_trace_from_session(s) for s in sessions]
    aggregated = aggregate_traces(traces)

    result = {
        "skill_name": args.skill,
        "collected_at": datetime.now().isoformat(),
        "sessions_found": len(sessions),
        "aggregation": aggregated,
    }

    output_json = json.dumps(result, ensure_ascii=False, indent=2, default=str)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output_json)
        print(f"数据已写入 {args.output}")

    print(output_json)


if __name__ == "__main__":
    main()
