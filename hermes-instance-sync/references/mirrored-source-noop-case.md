# Mirrored Source No-Op Case — 2026-07-03

## The pattern

Source: `~/.hermes-feishu/skills/` (125 entries)
Target: `~/.hermes/skills/` (169 entries)

Phase 0 result: **65 BACKLINK symlinks** at top level (out of 125 source entries = 52% BACKLINK ratio).

This is the inverse of the playbook's assumed architecture. The skill's "Source is authority" assumption failed — source wasn't an authority, it was a *mirror view* the user (or some setup script) had built pointing back at target.

## What it looks like

Most source entries were symlinks into target's own skills:

```bash
$ find ~/.hermes-feishu/skills/ -maxdepth 1 -type l -exec readlink {} \; | grep 'hermes/skills/' | head -3
/c/Users/Aorus/.hermes/skills/advanced-elicitation
/c/Users/Aorus/.hermes/skills/agent-native-cli-design
/c/Users/Aorus/.hermes/skills/answer
```

And several REAL-looking entries in source had BACKLINKs *inside* them:

```bash
$ ls ~/.hermes-feishu/skills/openclaw-imports/ | head -3
chart-generator -> /c/Users/Aorus/.hermes/skills/openclaw-imports/chart-generator
clawdchat -> /c/Users/Aorus/.hermes/skills/openclaw-imports/clawdchat
```

These would silently fail Phase 3 if treated as REAL.

## Source-only candidates that weren't skills

`comm -23 source target` flagged 2 candidates (`ppt`, `ppt_engine`). Inspection revealed:

- `ppt_engine/` contained `__init__.py`, `schema.py`, `structure_parser.py` etc. — **Python application code**, not a SKILL.md. Should never be in `skills/` at all.
- `ppt/` was a meta-category with two sub-folders; both were already present at target top level as `ppt-structure-parser` and `ppt-template-filler`.

**Lesson**: when a source-only candidate looks like a sync target, always check whether it has a `SKILL.md` before treating it as a skill. Categories and code dirs both flow through comm but neither is a skill.

## Correct outcome: report-only, no changes

Per the high-BACKLINK-ratio short-circuit the skill now encodes:

```
Added:    0
Updated:  0
Removed:  0
Skipped (BACKLINK safety): 67
Broken-link check:         0 (Phase 5 ✅)
```

## Detection recipe (now in SKILL.md)

See Phase 0's "Mirrored Source pattern" section. Two probes:

1. Top-level BACKLINK ratio.
2. Per-category internal BACKLINK count for any REAL entry still in the running.

If both probes fire, the run is a mirror audit, not a sync.
