#!/usr/bin/env python3
"""
自动触发评测脚本 — 监控 Hermes 会话，检测 Skill 使用后自动触发评测。

设计：
  - 作为 cron job 或 post-session hook 运行
  - 检测最近的会话是否使用了 Skill
  - 若使用了 Skill，自动调用 skill-evaluator 进行评测
  - 结果存入 eval_results 目录

用法:
  # 检查最近 N 条会话
  python3 auto_eval_trigger.py --recent 5

  # 检查指定 Skill
  python3 auto_eval_trigger.py --skill troubleshooter

  # 作为 cron job (每次运行检查上次运行后新增的会话)
  python3 auto_eval_trigger.py --mode incremental

  # 静默模式 (只输出 JSON)
  python3 auto_eval_trigger.py --recent 5 --quiet
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 数据目录
EVAL_DIR = os.path.expanduser("~/.hermes-feishu/eval_results")
STATE_FILE = os.path.join(EVAL_DIR, "_auto_trigger_state.json")
INDEX_FILE = os.path.join(EVAL_DIR, "index.json")


def ensure_dirs():
    Path(EVAL_DIR).mkdir(parents=True, exist_ok=True)


def load_state() -> dict:
    """加载上次运行状态。"""
    if os.path.exists(STATE_FILE):
        try:
            return json.loads(Path(STATE_FILE).read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"last_check": None, "last_session_id": None}


def save_state(state: dict):
    ensure_dirs()
    Path(STATE_FILE).write_text(json.dumps(state, indent=2, default=str))


def get_recent_sessions(count: int = 10) -> list[dict]:
    """
    获取最近的会话记录。
    尝试多种数据源：session DB → 日志文件 → eval 索引。
    """
    sessions = []

    # 尝试从 session search 机制获取近期会话
    # （这里依赖 Hermes 的本地存储）
    try:
        # 检查 eval_results 中是否有之前的会话索引
        if os.path.exists(INDEX_FILE):
            index = json.loads(Path(INDEX_FILE).read_text())
            recent = sorted(
                index.get("recent_sessions", []),
                key=lambda s: s.get("timestamp", ""),
                reverse=True,
            )
            sessions = recent[:count]
    except Exception:
        pass

    return sessions


def extract_skills_from_session(session: dict) -> list[str]:
    """从会话数据中提取使用的 Skill 名称列表。"""
    skills = set()

    # 检查显式 skill 字段
    for key in ["skills", "invoked_skills", "active_skills", "loaded_skills"]:
        if key in session and isinstance(session[key], list):
            skills.update(session[key])

    # 检查 content 中的 skill 引用
    content = json.dumps(session)
    # Hermes skill 引用常见模式
    import re
    for match in re.finditer(r'skill[_\s]*(?:name|view|load)[\s:"\']+([a-zA-Z][a-zA-Z0-9_-]+)', content, re.IGNORECASE):
        skills.add(match.group(1))

    return list(skills)


def check_skill_sessions(sessions: list[dict]) -> list[dict]:
    """
    检查会话中是否使用了 Skill，返回需要评测的会话列表。
    每条记录包含: session_id, skill_names, timestamp
    """
    to_evaluate = []

    for session in sessions:
        skills = extract_skills_from_session(session)
        if skills:
            to_evaluate.append({
                "session_id": session.get("id") or session.get("session_id"),
                "skill_names": skills,
                "timestamp": session.get("timestamp") or session.get("created_at"),
                "summary": str(session.get("summary") or session.get("content", ""))[:200],
            })

    return to_evaluate


def trigger_evaluation(skill_name: str, session_id: str = None) -> dict:
    """触发一次评测。返回评测结果摘要。"""
    result = {
        "skill_name": skill_name,
        "session_id": session_id,
        "triggered_at": datetime.now().isoformat(),
        "status": "pending",
        "output_file": None,
    }

    # 生成输出路径
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    skill_dir = os.path.join(EVAL_DIR, skill_name)
    Path(skill_dir).mkdir(parents=True, exist_ok=True)

    output_path = os.path.join(skill_dir, f"{timestamp}_auto.json")

    # 调用 collect_trace.py 采集数据
    import subprocess
    script_dir = os.path.dirname(os.path.abspath(__file__))
    collector = os.path.join(script_dir, "collect_trace.py")

    try:
        proc = subprocess.run(
            [sys.executable, collector, "--skill", skill_name, "--sessions", "5", "--output", output_path],
            capture_output=True, text=True, timeout=60,
        )
        result["collector_output"] = proc.stdout
        result["collector_stderr"] = proc.stderr
        result["status"] = "collected" if proc.returncode == 0 else "collect_failed"
        result["output_file"] = output_path
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def update_index(eval_result: dict):
    """更新评测索引。"""
    ensure_dirs()

    index = {}
    if os.path.exists(INDEX_FILE):
        try:
            index = json.loads(Path(INDEX_FILE).read_text())
        except (json.JSONDecodeError, OSError):
            pass

    skill = eval_result["skill_name"]

    # 更新 Skill 索引
    if "skills" not in index:
        index["skills"] = {}
    if skill not in index["skills"]:
        index["skills"][skill] = {"eval_count": 0, "last_eval": None, "recent_results": []}

    index["skills"][skill]["eval_count"] += 1
    index["skills"][skill]["last_eval"] = eval_result["triggered_at"]
    index["skills"][skill]["recent_results"].insert(0, {
        "time": eval_result["triggered_at"],
        "status": eval_result["status"],
        "file": eval_result.get("output_file"),
    })
    # 只保留最近 20 条
    index["skills"][skill]["recent_results"] = index["skills"][skill]["recent_results"][:20]

    Path(INDEX_FILE).write_text(json.dumps(index, indent=2, ensure_ascii=False))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="自动触发 Skill 评测")
    parser.add_argument("--recent", type=int, default=10, help="检查最近 N 条会话")
    parser.add_argument("--skill", default=None, help="只检查指定 Skill")
    parser.add_argument("--mode", choices=["once", "incremental"], default="once",
                        help="once=单次检查, incremental=增量检查(基于上次状态)")
    parser.add_argument("--quiet", action="store_true", help="静默模式")
    parser.add_argument("--dry-run", action="store_true", help="只检测不执行评测")
    args = parser.parse_args()

    ensure_dirs()
    state = load_state()

    sessions = get_recent_sessions(args.recent)

    if not sessions:
        if not args.quiet:
            print("⚠️ 未找到近期会话记录。请确认 Hermes 数据源可用。")
        return

    to_evaluate = check_skill_sessions(sessions)

    if args.skill:
        to_evaluate = [s for s in to_evaluate if args.skill in s["skill_names"]]

    if not to_evaluate:
        if not args.quiet:
            print("ℹ️ 近期会话中未检测到 Skill 使用。")
        return

    if not args.quiet:
        print(f"🔍 检测到 {len(to_evaluate)} 个会话使用了 Skill：")
        for s in to_evaluate:
            print(f"  - {s['session_id'][:16]}... → {', '.join(s['skill_names'])}")

    if args.dry_run:
        if not args.quiet:
            print("🏁 Dry-run 模式，跳过实际评测。")
        return

    # 执行评测
    total = len(to_evaluate)
    for i, session_info in enumerate(to_evaluate):
        for skill_name in session_info["skill_names"]:
            if not args.quiet:
                print(f"[{i+1}/{total}] 评测 Skill: {skill_name} ...", end=" ")

            result = trigger_evaluation(skill_name, session_info["session_id"])
            update_index(result)

            if not args.quiet:
                status_icon = "✅" if result["status"] == "collected" else "❌"
                print(f"{status_icon} ({result['status']})")

    # 保存状态
    if sessions:
        state["last_check"] = datetime.now().isoformat()
        state["last_session_id"] = sessions[0].get("id") or sessions[0].get("session_id")
        save_state(state)

    if not args.quiet:
        print(f"\n✅ 完成！共触发 {len(to_evaluate)} 个会话的评测。")
        print(f"   结果存储在: {EVAL_DIR}/")


if __name__ == "__main__":
    main()
