---
name: kanban
description: "Hermes Kanban multi-agent work queue: orchestration, worker lifecycle, Codex lane integration, and task decomposition patterns."
version: 1.0.0
author: Hermes Agent (consolidated umbrella)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, workers, codex, collaboration, work-queue]
---

# Hermes Kanban — Multi-Agent Work Queue

Durable SQLite-backed board for multi-profile / multi-worker collaboration. Users drive it via `hermes kanban <verb>`; dispatcher-spawned workers see a focused `kanban_*` toolset.

## Quick Concepts

- **Board** — hard boundary (workers get `HERMES_KANBAN_BOARD` pinned in env)
- **Tenant** — soft namespace within a board for workspace-path + memory-key isolation
- **Dispatcher** — reclaims stale claims, promotes ready tasks, atomically claims, spawns assigned profiles
- **Worker** — spawned with `--skills kanban-worker`; lifecycle auto-injected as `KANBAN_GUIDANCE`

## Core Workflows

### Orchestrator Role
Decomposition playbook, anti-temptation rules, task graph design, fan-out patterns.
→ See `references/orchestrator.md`

### Worker Role
Lifecycle, handoff shapes, retry diagnostics, notification routing, common pitfalls.
→ See `references/worker.md`

### Codex Lane (Dual-Agent Pattern)
Running Codex CLI as an isolated implementation lane while Hermes owns task lifecycle.
→ See `references/codex-lane.md`

## CLI Quick Reference

| Verb | Purpose |
|------|---------|
| `hermes kanban init` | Initialize board |
| `hermes kanban create "title" --assignee <profile>` | Create task |
| `hermes kanban list` / `ls` | List tasks |
| `hermes kanban show <id>` | Show task details |
| `hermes kanban complete <id>` | Mark done |
| `hermes kanban block <id> "reason"` | Block for human input |
| `hermes kanban link <parent> <child>` | Create dependency |
| `hermes kanban tail <id>` | Follow task log |
| `hermes kanban dispatch` | Manual dispatch cycle |
| `hermes kanban daemon` | Continuous dispatcher |

## Pitfalls

1. **Inventing profile names that don't exist** — dispatcher silently fails. Always run `hermes profile list` first.
2. **Bundling independent lanes** — create separate cards for independent workstreams.
3. **`delegate_task` vs `kanban_create`** — `delegate_task` is for short in-run subtasks; `kanban_create` is for durable cross-agent handoffs.
4. **`clarify` in workers** — workers run headless. Use `kanban_block` + `kanban_comment` instead.
5. **Task state changes between dispatch and startup** — always `kanban_show` first thing in a worker.
