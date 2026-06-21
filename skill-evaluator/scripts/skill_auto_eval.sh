#!/usr/bin/env bash
set -euo pipefail
# Wrapper for skill-evaluator auto trigger (cron no_agent mode)
# Runs auto_eval_trigger.py with --mode incremental, output delivered to feishu.

# Handle bare cron environment where HOME may be unset
if [ -z "${HOME:-}" ]; then
    export HOME="/home/aorus"
fi

PY_SCRIPT="/home/aorus/.hermes-feishu/skills/ai-engineering/skill-evaluator/scripts/auto_eval_trigger.py"

exec python3 "$PY_SCRIPT" --mode incremental
