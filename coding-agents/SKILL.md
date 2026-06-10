---
name: coding-agents
description: "Delegate coding tasks to external AI coding agent CLIs: Claude Code, OpenAI Codex, and OpenCode. Provider comparison, mode selection, and orchestration patterns via Hermes terminal."
version: 1.0.0
author: Hermes Agent (consolidated umbrella)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Claude, Codex, OpenCode, Delegation, PTY, Automation]
    related_skills: [hermes-agent, kanban]
---

# Coding Agent Delegation

Delegate coding tasks to external AI coding agent CLIs through the Hermes terminal. Each agent has different strengths, auth methods, and operational modes.

## Provider Comparison

| Feature | Claude Code | OpenAI Codex | OpenCode |
|---------|------------|-------------|----------|
| Provider | Anthropic | OpenAI | Multi-provider |
| Install | `npm i -g @anthropic-ai/claude-code` | `npm i -g @openai/codex` | `npm i -g opencode-ai` |
| Auth | `claude auth login` / `ANTHROPIC_API_KEY` | Codex OAuth / `OPENAI_API_KEY` | `opencode auth login` |
| One-shot | `claude -p "task"` ✅ | `codex exec "task"` ✅ | `opencode run "task"` ✅ |
| Interactive | TUI (requires tmux) | TUI (requires PTY) | TUI (requires PTY) |
| Structured output | JSON schema (`--output-format json`) | No | No |
| PTY needed | No for `-p`, yes for interactive | Yes | No for `run`, yes for TUI |

## Mode Selection

**Print/exec mode** (preferred for most tasks):
```bash
# Claude Code
claude -p "Add error handling to API calls" --allowedTools "Read,Edit" --max-turns 10

# Codex
codex exec "Add error handling to API calls"

# OpenCode
opencode run "Add error handling to API calls"
```

**Interactive mode** (for multi-turn iterative work):
```bash
# Start in tmux
tmux new-session -d -s agent -x 140 -y 40
tmux send-keys -t agent 'cd /project && claude' Enter
```

## Provider Deep Dives

- **Claude Code** — richest feature set: JSON output, session continuation, MCP, hooks, agents, teams. Full reference: `references/claude-code.md`
- **OpenAI Codex** — simplest: `codex exec` + `--full-auto` / `--yolo` flags. Full reference: `references/codex.md`
- **OpenCode** — provider-agnostic: `opencode run` + `-f` for file attachments. Full reference: `references/opencode.md`

## Common Rules

1. **Always set `workdir`** — keep the agent focused on the right project
2. **Use isolated worktrees for parallel tasks** — avoid collisions
3. **Monitor long tasks** — use `process(action="poll"|"log")` for background sessions
4. **Clean up** — kill tmux sessions and remove temp worktrees when done
5. **Prefer one-shot mode** — cleaner than interactive for bounded tasks
6. **Set turn/budget limits** — prevents runaway costs in one-shot mode

## Pitfalls

1. **Interactive TUI requires PTY/tmux** — `pty=true` or tmux for TUI agents
2. **Codex requires git repo** — use `mktemp -d && git init` for scratch work
3. **Claude's `--dangerously-skip-permissions` dialog defaults to "No"** — send Down+Enter in tmux
4. **OpenCode `/exit` opens agent selector** — use Ctrl+C instead
5. **PATH mismatch** — check `which opencode` / `which codex` if behavior differs
