#!/bin/bash
# =============================================================================
# B-2 Hermes on_session_end Hook — 真正的事件驱动评测触发
# =============================================================================
#
# 工作原理（与轮询的本质区别）：
#   Hermes 每次会话结束时 → 自动调用此脚本（事件驱动，非轮询）
#   → 扫描会话文件是否使用了 Skill → 是 → 立即触发评测
#
# 与 Cron 的协作去重：
#   两者共享 ~/.hermes-feishu/eval_results/_evaluated_sessions.json
#   Hook 先执行（实时），cron 兜底（定时），已评测的不会重复评测
#
# 安装方法：
#   1. 将此脚本放入 ~/.hermes/hooks/on_session_end.sh
#   2. chmod +x ~/.hermes/hooks/on_session_end.sh
#   3. 在 ~/.hermes/config.yaml 中注册:
#      hooks:
#        on_session_end:
#          - command: "~/.hermes/hooks/on_session_end.sh"
#            timeout: 30
#   4. hermes hooks list   # 验证注册成功
#   5. 首次运行需批准 → hermes hooks test on_session_end
#      （或设置 hooks_auto_accept: true）
#
# =============================================================================

set -e

# 配置
EVAL_STATE_DIR="$HOME/.hermes-feishu/eval_results"
EVALUATED_REGISTRY="$EVAL_STATE_DIR/_evaluated_sessions.json"
LOG_FILE="$EVAL_STATE_DIR/_hook_log.txt"
SESSION_ID="${1:-unknown}"  # Hermes 传入的 session ID（如果支持）
SESSION_FILE="${2:-}"       # Hermes 传入的 session 文件路径（如果支持）

# 确保目录存在
mkdir -p "$EVAL_STATE_DIR"

# 日志函数
log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# =============================================================================
# 1. 去重检查：该会话是否已评测过
# =============================================================================
check_evaluated() {
    local sid="$1"
    if [ -f "$EVALUATED_REGISTRY" ]; then
        if python3 -c "
import json, sys
try:
    data = json.load(open('$EVALUATED_REGISTRY'))
    if '$sid' in data.get('evaluated_sessions', []):
        sys.exit(0)
    sys.exit(1)
except:
    sys.exit(1)
" 2>/dev/null; then
            return 0  # 已评测
        fi
    fi
    return 1  # 未评测
}

# =============================================================================
# 2. 标记会话为已评测
# =============================================================================
mark_evaluated() {
    local sid="$1"
    local skill_name="$2"
    python3 -c "
import json, os
from datetime import datetime

reg_file = '$EVALUATED_REGISTRY'
data = {}
if os.path.exists(reg_file):
    try:
        data = json.load(open(reg_file))
    except:
        pass

if 'evaluated_sessions' not in data:
    data['evaluated_sessions'] = []

# 去重
if '$sid' not in data['evaluated_sessions']:
    data['evaluated_sessions'].append('$sid')
    # 只保留最近 500 条
    data['evaluated_sessions'] = data['evaluated_sessions'][-500:]

data['last_hook_run'] = datetime.now().isoformat()
data['total_hook_evaluations'] = data.get('total_hook_evaluations', 0) + 1

json.dump(data, open(reg_file, 'w'), indent=2)
" 2>/dev/null
}

# =============================================================================
# 3. 从会话文件中提取 Skill 使用信息
# =============================================================================
extract_skills() {
    local session_path="$1"
    python3 -c "
import json, re, sys

try:
    with open('$session_path', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read(50000)  # 只读前 50KB
except:
    sys.exit(1)

skills = set()
patterns = [
    r'\"skill_name\"\s*:\s*\"([^\"]+)\"',
    r'\"invokedSkills\"\s*:\s*\[([^\]]+)\]',
    r'\"active_skill\"\s*:\s*\"([^\"]+)\"',
    r'skill.view\(\"([^\"]+)\"\)',
    r'/skills/([a-zA-Z][a-zA-Z0-9_-]+)/',
]
for pattern in patterns:
    for match in re.finditer(pattern, content, re.IGNORECASE):
        val = match.group(1)
        for name in re.findall(r'\"([^\"]+)\"', val):
            skills.add(name)
        if val and '\"' not in val:
            skills.add(val.strip())

for s in sorted(skills):
    print(s)
" 2>/dev/null
}

# =============================================================================
# 4. 查找最新会话文件
# =============================================================================
find_latest_session() {
    local latest=""
    local latest_time=0
    
    for dir in "$HOME/.hermes/sessions" "$HOME/.hermes-feishu/sessions"; do
        [ -d "$dir" ] || continue
        for f in "$dir"/session_*.json "$dir"/request_dump_*.json; do
            [ -f "$f" ] || continue
            local mtime=$(stat -c %Y "$f" 2>/dev/null || echo 0)
            if [ "$mtime" -gt "$latest_time" ]; then
                latest_time="$mtime"
                latest="$f"
            fi
        done
    done
    
    echo "$latest"
}

# =============================================================================
# 主流程
# =============================================================================

log_msg "Hook triggered: session_id=$SESSION_ID"

# 确定要检查的会话文件
if [ -n "$SESSION_FILE" ] && [ -f "$SESSION_FILE" ]; then
    TARGET_FILE="$SESSION_FILE"
    TARGET_ID="$SESSION_ID"
elif [ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "unknown" ]; then
    # 按 session ID 查找文件
    TARGET_FILE=$(find "$HOME/.hermes/sessions" "$HOME/.hermes-feishu/sessions" \
        -name "*${SESSION_ID}*.json" -type f 2>/dev/null | head -1)
    TARGET_ID="$SESSION_ID"
else
    # 无 session ID，取最新文件
    TARGET_FILE=$(find_latest_session)
    TARGET_ID=$(basename "$TARGET_FILE" .json | head -c 40)
fi

if [ -z "$TARGET_FILE" ] || [ ! -f "$TARGET_FILE" ]; then
    log_msg "No session file found, skipping"
    exit 0
fi

# 去重检查
if check_evaluated "$TARGET_ID"; then
    log_msg "Already evaluated: $TARGET_ID"
    exit 0
fi

# 提取 Skill 使用
SKILLS=$(extract_skills "$TARGET_FILE")

if [ -z "$SKILLS" ]; then
    log_msg "No skills used in session: $TARGET_ID"
    exit 0
fi

log_msg "Skills detected: $SKILLS (session: $TARGET_ID)"

# 触发评测
EVAL_SCRIPT="$HOME/.hermes-feishu/skills/ai-engineering/skill-evaluator/scripts/auto_eval_trigger.py"

for skill in $SKILLS; do
    log_msg "Evaluating skill: $skill"
    python3 "$EVAL_SCRIPT" --skill "$skill" --recent 1 --quiet >> "$LOG_FILE" 2>&1 || true
    mark_evaluated "$TARGET_ID" "$skill"
done

log_msg "Hook completed: evaluated $(echo "$SKILLS" | wc -w) skills"
