# Symlink-safe skill scanning

## Problem

`~/.hermes-feishu/skills/` contains 200+ symlinks for cross-profile sharing.
Three common approaches all fail at scale:

| Approach | Why it fails |
|----------|-------------|
| `os.walk(base, followlinks=False)` | Misses symlinked directories entirely → 55/141 skills found |
| `os.walk(base, followlinks=True)` + ELOOP filter | Exponential traversal: directory A → symlink to B → B has symlink back to A → repeat through different paths → 60s timeout |
| `find -L base -maxdepth N` | `-maxdepth` doesn't help with symlink loops inside the tree; "Too many levels of symbolic links" → 60s timeout |

## Solution: Shell glob

```bash
# Level 1: direct child directories
for d in "base"/*/; do [ -f "${d}SKILL.md" ] && echo "$d"; done

# Level 2: grandchild directories
for d in "base"/*/*/; do [ -f "${d}SKILL.md" ] && echo "$d"; done
```

**Why it works**: Bash glob expands one level at a time. Each iteration checks
for a file (`SKILL.md`) via stat, which follows symlinks naturally but doesn't
cause traversal into the linked directory's own children. No recursion, no
ELOOP. O(n) where n = actual entries, not O(n²) from cross-linked traversal.

## Implementation

`scan_inventory.py` v3.0 uses `subprocess.run(cmd, shell=True)` to invoke
the shell glob, then parses stdout. Classification and diff logic remain in
Python for maintainability.

## History

- v2.0 (original): `os.walk(followlinks=False)` — worked when symlinks were few
- v2.1 (2026-07-05): Patched to `followlinks=True` + ELOOP filter — still timed out
  at 200+ symlinks
- v3.0 (2026-07-05): Rewritten to shell-glob approach — reliable <10s for 141 skills
