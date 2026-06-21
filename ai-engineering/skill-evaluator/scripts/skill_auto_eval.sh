#!/usr/bin/env bash
set -euo pipefail
# Wrapper for skill-evaluator auto trigger (cron no_agent mode)
# Runs auto_eval_trigger.py with --mode incremental, output delivered to feishu.
#
# ⚠️  THREE PITFALLS (verified 2026-06-22):
#  1. Do NOT use symlinks — $0/dirname resolve to the link target, breaking
#     relative path derivation. Write the script directly in place.
#  2. Cron env has NO venv python3 on PATH. Use absolute venv path.
#  3. Use absolute paths for Python script — do not derive from $0.

# Handle bare cron environment where HOME may be unset
if [ -z "${HOME:-}" ]; then
    export HOME="/home/aorus"
fi

exec /home/aorus/.hermes/hermes-agent/venv/bin/python3 \
  /home/aorus/.hermes-feishu/skills/ai-engineering/skill-evaluator/scripts/auto_eval_trigger.py \
  --mode incremental
