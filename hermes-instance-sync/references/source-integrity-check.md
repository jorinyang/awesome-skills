# Source Integrity Check — Reference

## Problem

When running instance-to-instance sync, the "source" directory may not actually be authoritative. Common failure: source entries are symlinks pointing back to the target directory. Creating new symlinks from target→source in that state produces circular chains:

```
~/.hermes/skills/foo → ~/.hermes-feishu/skills/foo → ~/.hermes/skills/foo
```

`test -e` reports these as broken (ELOOP / too many symlink levels), but `ln -s` creates them silently without error.

## Detection Logic

For each entry shared between source and target:

1. Is the source entry a real directory (not a symlink)? → `REAL` — safe.
2. Is the source entry a symlink? Read its target:
   - Points to a path under the target directory? → `BACKLINK` — BLOCK.
   - Points elsewhere (third location, e.g., `../../.agents/skills/`)? → `EXTERNAL` — note, skip.
   - Points to a path under the source directory itself? → Self-referential, treat as `BACKLINK`.

## Real-World Example (2025-06-28)

Source: `~/.hermes-feishu/skills/`, Target: `~/.hermes/skills/`

- 26 entries were `REAL` (real dirs in feishu)
- 83 entries were `BACKLINK` (symlinks in feishu pointing to hermes)
- 26 entries were `EXTERNAL` (lark-* symlinks pointing to `../../.agents/skills/`)

The attempted sync created 56 circular symlinks before detection. Full rollback from `.archive/sync_20250628_040202/` recovered cleanly.

## Resolution Path

To fix a BACKLINK situation:

1. For each BACKLINK entry, the real content lives in the target directory
2. Copy the real content into the source directory, replacing the backward symlink
3. Re-run Phase 0 — should now show `REAL`
4. Proceed with normal sync (target gets symlinks to source)
