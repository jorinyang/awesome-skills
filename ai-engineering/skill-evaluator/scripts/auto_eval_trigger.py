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
from typing import Optional

# 数据目录
EVAL_DIR = os.path.expanduser("~/.hermes-feishu/eval_results")
STATE_FILE = os.path.join(EVAL_DIR, "_auto_trigger_state.json")
INDEX_FILE = os.path.join(EVAL_DIR, "index.json")
# 与 B-2 Gateway hook 共享的去重注册表
EVALUATED_REGISTRY = os.path.join(EVAL_DIR, "_evaluated_sessions.json")


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


def get_recent_sessions(count: int = 10, since: Optional[str] = None) -> list[dict]:
    """
    获取最近的会话记录。
    尝试多种数据源：session 文件 → sessions.json 索引 → eval 索引。

    Args:
        count: 最多返回的会话数
        since: ISO 时间戳字符串，只返回此时间之后修改的会话 (用于增量模式)
    """
    sessions = []
    since_ts = None
    if since:
        try:
            since_ts = datetime.fromisoformat(since).timestamp()
        except (ValueError, TypeError):
            pass

    # 数据源1: 直接扫描 ~/.hermes/sessions/ 目录中的 session JSON 文件
    sessions_dir = os.path.expanduser("~/.hermes/sessions")
    if os.path.isdir(sessions_dir):
        try:
            import glob as glob_mod
            session_files = []
            for f in glob_mod.glob(os.path.join(sessions_dir, "session_*.json")):
                fname = os.path.basename(f)
                # 跳过 request_dump 文件和 .jsonl 日志文件
                if "request_dump" in fname or fname.endswith(".jsonl"):
                    continue
                mtime = os.path.getmtime(f)
                # 增量模式: 跳过上次检查之前就已存在的文件
                if since_ts is not None and mtime <= since_ts:
                    continue
                session_files.append((mtime, f))
            session_files.sort(key=lambda x: x[0], reverse=True)

            for mtime, fpath in session_files[:count]:
                fname = os.path.basename(fpath)
                try:
                    # 尝试提取 session_id
                    session_id = fname
                    if fname.startswith("session_") or fname.startswith("session_cron_"):
                        # 从文件名提取 ID
                        session_id = fname.replace(".json", "")
                    dt = datetime.fromtimestamp(mtime)

                    sessions.append({
                        "id": session_id,
                        "session_id": session_id,
                        "timestamp": dt.isoformat(),
                        "created_at": dt.isoformat(),
                        "_file": fpath,
                        "_mtime": mtime,
                    })
                except Exception:
                    pass
        except Exception:
            pass

    # 数据源2: 检查 sessions.json 索引
    if not sessions:
        sessions_json = os.path.join(sessions_dir, "sessions.json")
        if os.path.exists(sessions_json):
            try:
                index = json.loads(Path(sessions_json).read_text())
                for key, data in index.items():
                    if isinstance(data, dict):
                        ts = data.get("updated_at") or data.get("created_at")
                        # 增量模式: 跳过 last_check 之前的会话
                        if since_ts is not None and ts:
                            try:
                                entry_ts = datetime.fromisoformat(ts).timestamp()
                                if entry_ts <= since_ts:
                                    continue
                            except (ValueError, TypeError):
                                pass
                        sessions.append({
                            "id": data.get("session_id", key),
                            "session_id": data.get("session_id", key),
                            "timestamp": ts,
                            "created_at": data.get("created_at"),
                            "summary": data.get("display_name", ""),
                        })
                sessions.sort(key=lambda s: s.get("timestamp", ""), reverse=True)
                sessions = sessions[:count]
            except Exception:
                pass

    # 数据源3: 检查 eval_results 索引 (历史评测数据)
    if not sessions:
        try:
            if os.path.exists(INDEX_FILE):
                index = json.loads(Path(INDEX_FILE).read_text())
                recent = sorted(
                    index.get("recent_sessions", []),
                    key=lambda s: s.get("timestamp", ""),
                    reverse=True,
                )
                # 增量模式: 过滤 last_check 之前的会话
                if since_ts is not None:
                    filtered = []
                    for s in recent:
                        ts = s.get("timestamp")
                        if ts:
                            try:
                                entry_ts = datetime.fromisoformat(ts).timestamp()
                                if entry_ts <= since_ts:
                                    continue
                            except (ValueError, TypeError):
                                pass
                        filtered.append(s)
                    recent = filtered
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

    # 如果有 _file 字段，读取会话文件内容进行分析
    import re
    content = ""
    if "_file" in session and os.path.exists(session["_file"]):
        try:
            with open(session["_file"], "r") as f:
                content = f.read()
        except Exception:
            pass

    if not content:
        content = json.dumps(session)

    # 检测实际的 skill_view(name="xxx") 调用
    for match in re.finditer(
        r'skill_view\s*\(\s*name\s*=\s*["\']([^"\']+)["\']',
        content,
        re.IGNORECASE,
    ):
        skills.add(match.group(1))

    # 兜底: Hermes skill 引用常见模式
    if not skills:
        for match in re.finditer(
            r'skill[_\s]*(?:name|view|load)[\s:"\']+([a-zA-Z][a-zA-Z0-9_-]+)',
            content,
            re.IGNORECASE,
        ):
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

    # 增量模式：用 last_check 过滤，只检查上次运行后新增的会话
    since = state.get("last_check") if args.mode == "incremental" else None
    # 增量模式取全部新会话 (不受 --recent 限制)，首次运行则用 --recent 兜底
    effective_count = args.recent
    if args.mode == "incremental" and since:
        effective_count = max(args.recent * 10, 100)  # 足够大以覆盖全部新会话
    sessions = get_recent_sessions(effective_count, since=since)

    if not sessions:
        # 无新会话：静默更新 last_check 后退出 (cron no_agent 模式下 stdout 会被投递，空输出=静默)
        if not args.quiet:
            msg = "⚠️ 未找到近期会话记录。请确认 Hermes 数据源可用。"
            if args.mode == "incremental" and state.get("last_check"):
                msg = f"ℹ️ 自 {state['last_check']} 以来无新增会话。"
            # incremental 模式静默 (cron 场景)，once 模式输出到 stderr 供手动排查
            if args.mode == "incremental":
                import sys as _sys
                print(msg, file=_sys.stderr)
            else:
                print(msg)
        if args.mode == "incremental":
            state["last_check"] = datetime.now().isoformat()
            save_state(state)
        return

    to_evaluate = check_skill_sessions(sessions)

    if args.skill:
        to_evaluate = [s for s in to_evaluate if args.skill in s["skill_names"]]

    # ============================================================
    # 去重：跳过已被 B-2 Gateway hook 评测过的会话
    # ============================================================
    if os.path.exists(EVALUATED_REGISTRY):
        try:
            reg = json.loads(Path(EVALUATED_REGISTRY).read_text())
            already = set(reg.get("evaluated_sessions", []))
            before = len(to_evaluate)
            to_evaluate = [s for s in to_evaluate if s["session_id"] not in already]
            skipped = before - len(to_evaluate)
            if skipped > 0 and not args.quiet:
                print(f"⏭️ 跳过 {skipped} 个已由 Hook 评测的会话")
        except Exception:
            pass

    if not to_evaluate:
        # 有会话但无 Skill 使用：incremental 模式静默 (cron 场景)
        if not args.quiet:
            msg = "ℹ️ 近期会话中未检测到 Skill 使用。"
            if args.mode == "incremental":
                import sys as _sys
                print(msg, file=_sys.stderr)
            else:
                print(msg)
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
