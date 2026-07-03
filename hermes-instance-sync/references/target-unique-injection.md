# Target-Unique Sub-Skill Injection: Full Recipe & Recovery

## The Problem

When syncing a category where both source and target have real directories, and
target has sub-skills that source lacks (e.g., `codebase-inspection` inside
`github/`), the naive approach fails:

1. `find ... -exec dirname {} \;` with `comm` produces mixed full-paths and
   `SKILL.md` strings — the comparison is garbage.
2. Source may already have symlinks for those sub-skills pointing into target's
   copy of the same category (BACKLINK residues). `cp -a` over a broken symlink
   is undefined behavior.
3. If you delete target and symlink first, the cp source is gone.
4. After re-linking, internal symlinks in source become circular.

## Correct Recipe

```bash
SOURCE="C:/Users/Aorus/.hermes-feishu/skills"
TARGET="C:/Users/Aorus/.hermes/skills"
CAT="github"  # the category being merged

# 1. Find target-unique sub-skills (compare directory basenames, not paths)
source_subs=$(find "$SOURCE/$CAT" -maxdepth 2 -name "SKILL.md" \
  -exec sh -c 'basename "$(dirname "$1")"' _ {} \; | sort -u)
target_subs=$(find "$TARGET/$CAT" -maxdepth 2 -name "SKILL.md" \
  -exec sh -c 'basename "$(dirname "$1")"' _ {} \; | sort -u)
unique=$(comm -13 <(echo "$source_subs") <(echo "$target_subs"))

# 2. Remove stale symlinks in source that would collide
for sub in $unique; do
  src_path="$SOURCE/$CAT/$sub"
  if [ -L "$src_path" ]; then
    rm -f "$src_path"
  fi
done

# 3. Copy real content from target (MUST do this BEFORE Phase 3 deletes target)
for sub in $unique; do
  cp -a "$TARGET/$CAT/$sub" "$SOURCE/$CAT/"
done

# 4. Now run Phase 3: backup target, delete, symlink
TS=$(date +%Y%m%d_%H%M%S)
BACKUP="$TARGET/.archive/sync_$TS"
mkdir -p "$BACKUP"
cp -a "$TARGET/$CAT" "$BACKUP/"
rm -rf "$TARGET/$CAT"
ln -s "$SOURCE/$CAT" "$TARGET/$CAT"

# 5. Clean any remaining broken internal symlinks in source
find "$SOURCE" -type l -not -exec test -e {} \; -delete
```

## Recovery When Injection Fails

If you already deleted target and created the symlink, but injection silently
failed (e.g., `cp -a` hit broken symlinks and did nothing):

```bash
# 1. Remove the broken symlink
rm -f "$TARGET/$CAT"

# 2. Restore from backup
cp -a "$BACKUP/$CAT" "$TARGET/"

# 3. Now run the correct injection recipe above (steps 1-3)
# 4. Re-create symlink (step 4)
# 5. Clean internal broken symlinks (step 5)
```

## Real-World Example (2026-06-29)

Source `github/` had:
- `drawio-generation/` (REAL, unique to source)
- `codebase-inspection -> C:/Users/Aorus/.hermes/skills/github/codebase-inspection` (BACKLINK symlink)
- `github-release-readme -> C:/Users/Aorus/.hermes/skills/github/github-release-readme` (BACKLINK symlink)
- 5 other broken BACKLINK symlinks

Target `github/` had:
- `SKILL.md` (top-level, making github itself a skill)
- `codebase-inspection/` (REAL)
- `github-release-readme/` (REAL)

First attempt failed: `comm` comparison mixed paths, `cp -a` hit broken
symlinks silently, injection produced nothing. Recovery: restore from backup,
run correct recipe. Result: source gained `codebase-inspection/`,
`github-release-readme/`, and `github-workflow/` (from target's top-level
SKILL.md). 5 stale broken symlinks cleaned.

## Key Principle

**Copy real content from target BEFORE deleting it.** Once target is a symlink
to source, internal symlinks become circular and content is unrecoverable
without the backup.
