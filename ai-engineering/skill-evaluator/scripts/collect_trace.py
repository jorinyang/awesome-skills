#!/usr/bin/env python3
"""
执行数据采集脚本 — 直读 Hermes session JSON 文件提取 Skill 执行数据。

数据源:
  ~/.hermes/sessions/session_*.json
  ~/.hermes-feishu/sessions/session_*.json

Hermes session 格式:
  {
    "session_id": "sess_...",
    "model": "...",
    "messages": [
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "...", "tool_calls": [
        {"id": "...", "type": "function", "function": {"name": "skill_view", "arguments": "{\"name\":\"...\"}"}}
      ]},
      {"role": "tool", "tool_call_id": "...", "content": "..."},
      ...
    ]
  }

用法:
    python3 collect_trace.py --skill <skill_name> [--sessions <N>] [--output <path>]
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── 配置 ──────────────────────────────────────────────────
SESSION_DIRS = [
    os.path.expanduser("~/.hermes/sessions"),
    os.path.expanduser("~/.hermes-feishu/sessions"),
]

# 只扫描这些前缀的文件（跳过 request_dump 和 sessions.json 索引文件）
SESSION_GLOB = "session_*.json"


def scan_session_files(max_files: int = 200) -> list[Path]:
    """扫描所有会话目录，返回按修改时间倒序的 session 文件列表。"""
    files = []
    for d in SESSION_DIRS:
        if not os.path.isdir(d):
            continue
        for f in Path(d).glob(SESSION_GLOB):
            files.append(f)
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:max_files]


def extract_skills_from_session(filepath: Path) -> set[str]:
    """
    从 session 文件中提取被调用的 Skill 名称。
    只读 skill_view 工具调用（不扫描全文，避免误匹配）。
    """
    skills = set()
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return skills

    messages = data.get("messages", []) if isinstance(data, dict) else data
    if not isinstance(messages, list):
        return skills

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        tool_calls = msg.get("tool_calls", [])
        if not isinstance(tool_calls, list):
            continue
        for tc in tool_calls:
            if not isinstance(tc, dict):
                continue
            func = tc.get("function", {})
            name = func.get("name", "")
            if name in ("skill_view", "skill_manage"):
                try:
                    args = json.loads(func.get("arguments", "{}"))
                    skill = args.get("name", "")
                    if skill:
                        skills.add(skill)
                except (json.JSONDecodeError, TypeError):
                    pass

    return skills


def find_skill_sessions(skill_name: str, max_sessions: int = 10) -> list[dict]:
    """查找包含目标 Skill 的会话记录。
    
    策略: 
    1. grep 快速定位含 skill_name 的文件
    2. 跳过 session_cron_* 文件（系统提示中包含所有 skill 列表，噪声太多）
    3. 逐个解析剩余文件，提取 skill_view 调用中的 skill 名称
    """
    import subprocess
    
    results = []
    
    for d in SESSION_DIRS:
        if not os.path.isdir(d):
            continue
        try:
            proc = subprocess.run(
                ["grep", "-rl", "--include=session_*.json", skill_name, str(d)],
                capture_output=True, text=True, timeout=60,
            )
            if proc.returncode != 0:
                continue
            
            matched = [Path(p) for p in proc.stdout.strip().split("\n") if p]
            # 排除 cron session（系统提示含全量 skill 列表）
            user_sessions = [p for p in matched if "session_cron_" not in str(p)]
            # 按 mtime 倒序
            user_sessions.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            
            for fp in user_sessions:
                skills = extract_skills_from_session(fp)
                if skill_name in skills:
                    results.append({
                        "source": str(fp),
                        "session_id": fp.stem,
                        "timestamp": datetime.fromtimestamp(fp.stat().st_mtime).isoformat(),
                        "skills_used": list(skills),
                    })
                    if len(results) >= max_sessions:
                        return results
        except (subprocess.TimeoutExpired, Exception):
            continue
    
    return results


def extract_trace_from_file(filepath: str) -> Optional[dict]:
    """从单个 session 文件中提取执行 trace 数据。"""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    messages = data.get("messages", []) if isinstance(data, dict) else data
    if not isinstance(messages, list):
        return None

    trace = {
        "session_id": data.get("session_id") if isinstance(data, dict) else None,
        "model": data.get("model") if isinstance(data, dict) else None,
        "message_count": len(messages),
        "tool_calls": [],
        "errors": [],
        "skills_used": set(),
        "total_input_chars": 0,
        "total_output_chars": 0,
    }

    for msg in messages:
        if not isinstance(msg, dict):
            continue

        role = msg.get("role", "")

        # ── 用户输入统计 ──
        if role == "user":
            trace["total_input_chars"] += len(str(msg.get("content", "")))

        # ── 助手输出统计 ──
        if role == "assistant":
            content = str(msg.get("content", ""))
            reasoning = str(msg.get("reasoning", ""))
            trace["total_output_chars"] += len(content) + len(reasoning)

            # ── 工具调用 ──
            tool_calls = msg.get("tool_calls", [])
            if isinstance(tool_calls, list):
                for tc in tool_calls:
                    if not isinstance(tc, dict):
                        continue
                    func = tc.get("function", {})
                    call_info = {
                        "tool": func.get("name", "unknown"),
                        "arguments": func.get("arguments", ""),
                        "call_id": tc.get("id", ""),
                    }

                    # 查找该 tool_call 对应的 tool result
                    tc_id = tc.get("id", "")
                    for m2 in messages:
                        if isinstance(m2, dict) and m2.get("role") == "tool" and m2.get("tool_call_id") == tc_id:
                            result_content = str(m2.get("content", ""))
                            call_info["result_length"] = len(result_content)
                            call_info["result_preview"] = result_content[:200]
                            call_info["is_error"] = "error" in result_content[:100].lower() or "failed" in result_content[:100].lower()
                            break

                    trace["tool_calls"].append(call_info)

                    # 提取 Skill 名称
                    if func.get("name") in ("skill_view", "skill_manage"):
                        try:
                            args = json.loads(func.get("arguments", "{}"))
                            skill_name = args.get("name", "")
                            if skill_name:
                                trace["skills_used"].add(skill_name)
                        except (json.JSONDecodeError, TypeError):
                            pass

    trace["skills_used"] = sorted(trace["skills_used"])
    trace["tool_count"] = len(trace["tool_calls"])
    trace["status"] = "failed" if trace["errors"] else "success"

    return trace


def aggregate_traces(traces: list[dict]) -> dict:
    """聚合多次执行的数据。"""
    if not traces:
        return {"error": "无执行数据"}

    all_skills = set()
    for t in traces:
        all_skills.update(t.get("skills_used", []))

    total_tools = sum(t.get("tool_count", 0) for t in traces)
    total_errors = sum(len(t.get("errors", [])) for t in traces)
    success_count = sum(1 for t in traces if t.get("status") == "success")
    total_input = sum(t.get("total_input_chars", 0) for t in traces)
    total_output = sum(t.get("total_output_chars", 0) for t in traces)

    return {
        "session_count": len(traces),
        "success_rate": round(success_count / len(traces) * 100, 1) if traces else 0,
        "total_tool_calls": total_tools,
        "avg_tool_calls_per_session": round(total_tools / len(traces), 1) if traces else 0,
        "total_errors": total_errors,
        "total_input_chars": total_input,
        "total_output_chars": total_output,
        "skills_observed": sorted(all_skills),
        "traces": traces,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="采集 Skill 执行数据")
    parser.add_argument("--skill", required=True, help="目标 Skill 名称")
    parser.add_argument("--sessions", type=int, default=5, help="最多分析的会话数")
    parser.add_argument("--output", default=None, help="输出 JSON 文件路径")
    parser.add_argument("--quiet", action="store_true", help="静默模式")
    args = parser.parse_args()

    # Step 1: 发现含目标 Skill 的会话
    sessions = find_skill_sessions(args.skill, args.sessions)

    if not sessions:
        result = {
            "skill_name": args.skill,
            "collected_at": datetime.now().isoformat(),
            "sessions_found": 0,
            "error": f"未找到包含 Skill '{args.skill}' 的会话记录",
        }
    else:
        if not args.quiet:
            print(f"🔍 找到 {len(sessions)} 个含有 '{args.skill}' 的会话")

        # Step 2: 逐会话提取 trace
        traces = []
        for s in sessions:
            trace = extract_trace_from_file(s["source"])
            if trace:
                trace["source_file"] = s["source"]
                traces.append(trace)

        aggregated = aggregate_traces(traces)

        result = {
            "skill_name": args.skill,
            "collected_at": datetime.now().isoformat(),
            "sessions_found": len(sessions),
            "traces_extracted": len(traces),
            "aggregation": aggregated,
        }

    output_json = json.dumps(result, ensure_ascii=False, indent=2, default=str)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output_json)
        if not args.quiet:
            print(f"📁 数据已写入 {args.output}")

    print(output_json)


if __name__ == "__main__":
    main()
