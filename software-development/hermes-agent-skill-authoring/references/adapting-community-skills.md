# Adapting Community Skills to Hermes

When bringing a community skill (Claude Code, Codex, Cursor, etc.) into Hermes, apply these transformations.

## Path Mapping

| Original (Claude Code convention) | Hermes equivalent |
|---|---|
| `.claude/skills/<name>/` | `~/.hermes-feishu/skills/<category>/<name>/` |
| `~/.claude/skills/` | `~/.hermes-feishu/skills/` |
| `~/.cursor/skills/` | `~/.hermes-feishu/skills/` |
| `~/.codex/skills/` | `~/.hermes-feishu/skills/` |

## Tool Mapping

| Original | Hermes equivalent |
|---|---|
| `spawn 子agent` / `Task` tool | `delegate_task` tool |
| `mcp__*` tools | Hermes MCP tools (via `native-mcp` skill) |
| `Read` / `Write` / `Edit` tools | `read_file` / `write_file` / `patch` |
| `Bash` tool | `terminal` tool |
| `WebSearch` / `WebFetch` | `web_search` / `web_extract` |

## Frontmatter Adaptation

Community skills often use minimal frontmatter (just `name` + `description`). Add full Hermes metadata:

```yaml
---
name: <keep-original-name>
description: "Use when <trigger>. <behavior>. 触发词：<chinese-triggers>."
version: <adaptation-version>
author: <original-author>, adapted for Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [<relevant-tags>]
    related_skills: [<hermes-skill-names>]
---
```

## Runtime Neutrality

Scan for and replace runtime-specific language:

| Red flag (must fix) | Neutral replacement |
|---|---|
| "在 Claude Code 里" | "在你的 agent 里" |
| "Claude Code skill" | "Agent Skill" |
| "Claude Code 用户" | "skills-aware agent 用户" |
| `npx skills add` (Claude-only) | Manual install instructions |
| Single-runtime badge | Multi-runtime badges |

## Asset Adaptation

- **scripts/**: Executable scripts often hardcode platform paths (e.g., macOS home dirs). Add fallback options or note as Hermes-specific.
- **templates/**: Usually portable as-is.
- **assets/**: Images and SVGs are portable. Skip large GIFs/videos (>500KB) to keep skill lean.
- **references/**: Markdown references are portable as-is.

## Example: Darwin-Skill Adaptation

See `darwin-skill` at `~/.hermes-feishu/skills/software-development/darwin-skill/` for a complete adaptation of a community skill (original: https://github.com/alchaincyf/darwin-skill).

Key changes made:
1. All `.claude/skills/` paths → `~/.hermes-feishu/skills/`
2. "spawn子agent" → `delegate_task`
3. Removed Claude-only installation commands (`npx skills add`)
4. Added full Hermes frontmatter metadata
5. Patched screenshot script note for portability
