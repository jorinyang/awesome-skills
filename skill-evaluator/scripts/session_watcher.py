#!/usr/bin/env python3
"""
B-2 方案：Post-session Hook 文件监听器

无需 inotify/watchdog，纯 Python 轮询实现。
监听 Hermes 会话目录，检测到新会话文件后立即触发评测。

用法:
  # 前台运行（调试）
  python3 session_watcher.py

  # 后台运行（生产）
  python3 session_watcher.py --daemon

  # 单次模式（用于 cron 替代）
  python3 session_watcher.py --once

工作原理:
  1. 轮询 ~/.hermes/sessions/ 和 ~/.hermes-feishu/sessions/
  2. 发现新/修改的 .json 文件 → 记录到已知清单
  3. 检查文件内容是否使用了 Skill
  4. 是 → 立即触发评测
  5. 否 → 跳过

与 cron 方案的区别:
  - cron: 10分钟一次，批量检查，可能漏掉间隔内的会话
  - watcher: 5秒轮询，发现即处理，不会遗漏
"""

import json
import os
import sys
import time
import subprocess
import re
from datetime import datetime
from pathlib import Path

# 配置
WATCH_DIRS = [
    os.path.expanduser("~/.hermes/sessions"),
    os.path.expanduser("~/.hermes-feishu/sessions"),
]
POLL_INTERVAL = 5  # 秒
KNOWN_FILES = os.path.expanduser("~/.hermes-feishu/eval_results/_watcher_known.json")
EVAL_SCRIPT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "auto_eval_trigger.py",
)


def ensure_dirs():
    Path(os.path.dirname(KNOWN_FILES)).mkdir(parents=True, exist_ok=True)


def load_known():
    """加载已知文件清单（避免重复处理）"""
    if os.path.exists(KNOWN_FILES):
        try:
            return set(json.loads(Path(KNOWN_FILES).read_text()))
        except (json.JSONDecodeError, OSError):
            pass
    return set()


def save_known(known: set):
    ensure_dirs()
    # 只保留最近 1000 条，防止文件无限增长
    recent = sorted(known, reverse=True)[:1000]
    Path(KNOWN_FILES).write_text(json.dumps(recent, indent=2))


def find_new_sessions(known: set) -> list[tuple[str, str, float]]:
    """发现新会话文件。返回 [(路径, 文件名, mtime), ...]"""
    new_files = []
    for watch_dir in WATCH_DIRS:
        if not os.path.isdir(watch_dir):
            continue
        for f in os.listdir(watch_dir):
            if not f.endswith(".json"):
                continue
            full_path = os.path.join(watch_dir, f)
            try:
                mtime = os.path.getmtime(full_path)
            except OSError:
                continue

            file_key = f"{watch_dir}/{f}"
            if file_key not in known:
                new_files.append((full_path, f, mtime))
                known.add(file_key)

    return sorted(new_files, key=lambda x: x[2])


def extract_skills_from_file(filepath: str) -> list[str]:
    """快速扫描文件中是否使用了 Skill（不完整解析，只做模式匹配）"""
    skills = set()
    try:
        # 只读前 50KB 做快速扫描（完整文件可能几 MB）
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(50_000)

        # 匹配 skill 引用模式
        patterns = [
            r'"skill_name"\s*:\s*"([^"]+)"',
            r'"invokedSkills"\s*:\s*\[([^\]]+)\]',
            r'"active_skill"\s*:\s*"([^"]+)"',
            r'skill.view\("([^"]+)"\)',
            r'/skills/([a-zA-Z][a-zA-Z0-9_-]+)/',
            r'"skills?"\s*:\s*\[([^\]]+)\]',
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                val = match.group(1)
                # 提取技能名（可能是逗号分隔的列表）
                for name in re.findall(r'"([^"]+)"', val):
                    skills.add(name)
                if val and '"' not in val:
                    skills.add(val.strip())

    except (OSError, UnicodeDecodeError):
        pass

    return list(skills)


def trigger_evaluation_for_skills(skills: list[str], session_file: str):
    """对发现的 Skill 触发评测"""
    for skill in skills:
        try:
            subprocess.run(
                [
                    sys.executable,
                    EVAL_SCRIPT,
                    "--skill", skill,
                    "--recent", "1",
                    "--quiet",
                ],
                timeout=30,
                capture_output=True,
            )
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass


def run_once():
    """单次扫描模式"""
    known = load_known()
    new_sessions = find_new_sessions(known)

    if not new_sessions:
        print("ℹ️ 无新会话")
        return

    evaluated = 0
    for filepath, filename, _ in new_sessions:
        skills = extract_skills_from_file(filepath)
        if skills:
            print(f"🔍 {filename} → {', '.join(skills)}")
            trigger_evaluation_for_skills(skills, filepath)
            evaluated += 1

    save_known(known)
    print(f"✅ 处理完成: {len(new_sessions)} 个新会话, {evaluated} 个含 Skill 使用")


def run_daemon():
    """持续监听模式"""
    print(f"🟢 B-2 Session Watcher 启动")
    print(f"   监听目录: {', '.join(WATCH_DIRS)}")
    print(f"   轮询间隔: {POLL_INTERVAL}s")
    print(f"   按 Ctrl+C 停止\n")

    known = load_known()
    last_save = time.time()

    try:
        while True:
            new_sessions = find_new_sessions(known)

            for filepath, filename, _ in new_sessions:
                skills = extract_skills_from_file(filepath)
                if skills:
                    ts = datetime.now().strftime("%H:%M:%S")
                    print(f"[{ts}] 🎯 {filename[:40]} → {', '.join(skills)}")
                    trigger_evaluation_for_skills(skills, filepath)

            # 定期保存已知清单
            if time.time() - last_save > 300:  # 每 5 分钟
                save_known(known)
                last_save = time.time()

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n⏹️ 停止监听")
        save_known(known)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="B-2 Session Watcher")
    parser.add_argument("--daemon", action="store_true", help="持续监听模式")
    parser.add_argument("--once", action="store_true", help="单次扫描后退出")
    args = parser.parse_args()

    ensure_dirs()

    if args.daemon:
        run_daemon()
    else:
        run_once()


if __name__ == "__main__":
    main()
