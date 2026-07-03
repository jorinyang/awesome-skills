---
name: hermes-instance-sync
description: >
  Synchronize skills between Hermes instances using symlinks, or from a GitHub
  skills repo. Compare, classify, backup, and link skill directories. Trigger:
  sync skills from another instance, align skill libraries, clone repo skills.
---

# Hermes Skill Sync

Two sync modes: **instance-to-instance** (symlink) and **repo-to-local** (copy from GitHub).

## Mode A: Instance-to-Instance Sync

Synchronize skills between Hermes instances using symlinks. Source is authority.

### Cron Mode: Pragmatic Sync (for automated jobs)

When running as a scheduled cron job with the constraint "不覆盖目标实例的手动修改", use this simplified pipeline instead of full Phase 2-4:

1. **Phase -1 — Pre-Cleanup** — remove all broken symlinks in target BEFORE any sync operations. One-liner: `find <target_dir> -xtype l -delete`. This catches stale archive residues and orphaned links in TARGET_ONLY directories (e.g., `mapping/` pointing to nonexistent source paths). Broken links in source can be cleaned with the same command separately.

   **⚠️ PITFALL — `find -delete` may trigger approval in Hermes Agent**: In some Hermes Agent environments, `find -delete` is intercepted as a destructive operation and requires user approval (`pending_approval`). In cron mode this silently fails — the command appears to succeed but no deletion occurs. **Workaround**: split into two steps:
   ```bash
   # Step 1: Count broken links (read-only, no approval needed)
   BROKEN_COUNT=$(find "$TARGET" -xtype l 2>/dev/null | wc -l)
   # Step 2: Only attempt delete if broken links exist; if approval blocks it, report them
   if [ "$BROKEN_COUNT" -gt 0 ]; then
     echo "⚠️ $BROKEN_COUNT broken symlinks found, attempting cleanup..."
     find "$TARGET" -xtype l -delete 2>/dev/null
     REMAINING=$(find "$TARGET" -xtype l 2>/dev/null | wc -l)
     if [ "$REMAINING" -gt 0 ]; then
       echo "⚠️ Could not auto-delete $REMAINING broken links (approval required)"
       echo "  Run manually: find $TARGET -xtype l -delete"
     fi
   fi
   ```
   In practice, if `find -delete` is blocked, just report the count and move on — the sync can still complete safely (broken symlinks don't block new symlink creation).
2. **Phase 0** — source integrity check (same as below). Skip BACKLINK and EXTERNAL, sync only REAL entries.
3. **Handle SOURCE_ONLY** — create symlinks from target → source for all entries only in source
4. **Handle REAL shared** — if target has a real directory (not symlink) for a shared entry, **skip it** to preserve manual modifications. Only symlink if target is already a symlink pointing to the wrong place.
5. **Handle TARGET_ONLY** — keep untouched (target's own additions), but scan for broken internal symlinks inside them: `find <target>/<entry> -xtype l -delete`
6. **Phase 5** — verify top-level links only: `find <target> -maxdepth 1 -xtype l` (should be empty). Internal category broken links found here are NOT pre-existing noise — they should be fixed (see [Broken Symlink Cleanup](#broken-symlink-cleanup)).

This avoids deep sub-skill comparisons and backup/restore cycles that are unnecessary when source and target maintain independent REAL directories by design.

### Phase 0: Source Integrity Check (MANDATORY — run first)

Before touching any target files, verify the source is actually authoritative. The most common failure mode: source has symlinks pointing back to target, creating circular chains when you try to link target→source.

Run `scripts/check-source-integrity.py <source_dir> <target_dir>`. See `references/source-integrity-check.md` for the full logic.

The script produces three classifications:
| Class | Meaning | Action |
|-------|---------|--------|
| `REAL` | Source has real content (directory, not symlink) | ✅ Safe to use as authority |
| `BACKLINK` | Source is a symlink pointing TO the target dir | 🛑 BLOCKED — circular. Fix source first |
| `EXTERNAL` | Source is a symlink pointing elsewhere | ⚠️ Note it, skip this entry |

**If any BACKLINK entries exist, ABORT the sync for those entries.** BACKLINK entries (source symlink → target) cannot be synced source→target without creating circular chains. However, REAL entries (actual directories in source) can still be synced safely — BACKLINK only blocks the entries it affects, not the entire sync. EXTERNAL entries (source symlink → elsewhere) are also skipped.

**Partial sync rule**: classify ALL source entries first, then sync only REAL entries. Skip BACKLINK and EXTERNAL. This is the normal operating mode for cron-driven syncs where the source is a mixed view (categories + aggregated symlinks from other instances).

Quick shell one-liner for spot checks:
```bash
# Count backlinks from source to target
find ~/.hermes-feishu/skills/ -maxdepth 1 -type l -exec readlink {} \; | grep -c 'hermes/skills/'
# If > 0: BACKLINK entries exist — skip them, sync only REAL entries
```

### Phase 1: Discovery

```bash
ls ~/.hermes/skills/ | sort > /tmp/target.txt
ls ~/.hermes-feishu/skills/ | sort > /tmp/source.txt

comm -23 /tmp/source.txt /tmp/target.txt   # source-only: missing -> ADD
comm -13 /tmp/source.txt /tmp/target.txt   # target-only: no counterpart -> KEEP
comm -12 /tmp/source.txt /tmp/target.txt   # shared -> CLASSIFY
```

### Phase 2: Classify

For each shared entry, check symlink status and sub-skill structure:

```bash
# CRITICAL: strip trailing slash before testing symlinks
for d in ~/.hermes/skills/*; do
  if [ -L "$d" ]; then echo "SYMLINK: $(basename $d)"; fi
done
```

| Class | Condition | Action |
|-------|-----------|--------|
| Already linked | Target is symlink to source | No action |
| Safe to sync | Both independent, identical sub-skills | Replace with symlink |
| Source-enriched | Source has extra sub-skills | Replace with symlink |
| Target-unique | Target has sub-skills source lacks | Symlink then inject unique into source |
| Structural mismatch | Different structure (individual vs category) | Skip, keep independent |
| Broken link | Symlink target missing | Remove symlink |

### Phase 3: Backup and Replace

```bash
TS=$(date +%Y%m%d_%H%M%S)
BACKUP="~/.hermes/skills/.archive/sync_$TS"
mkdir -p "$BACKUP"
cp -a ~/.hermes/skills/$CAT "$BACKUP/"
rm -rf ~/.hermes/skills/$CAT
ln -s ~/.hermes-feishu/skills/$CAT ~/.hermes/skills/$CAT
```

### Phase 4: Handle Target-Unique Sub-Skills

When a category has sub-skills only in target (e.g., `codebase-inspection` in target's `github/` but not source's):

```bash
# Step 4a: Identify target-unique sub-skills (compare basenames only!)
source_subs=$(find "$SOURCE/$CAT" -maxdepth 2 -name "SKILL.md" -printf '%f\n' -exec dirname {} \; | sort -u)
target_subs=$(find "$TARGET/$CAT" -maxdepth 2 -name "SKILL.md" -printf '%f\n' -exec dirname {} \; | sort -u)
# Get basenames of dirs containing SKILL.md, not the SKILL.md files themselves
unique=$(comm -13 <(echo "$source_subs") <(echo "$target_subs"))

# Step 4b: Remove stale symlinks in source that would collide
for sub in $unique; do
  src_path="$SOURCE/$CAT/$sub"
  if [ -L "$src_path" ]; then
    rm -f "$src_path"   # must replace symlink with real content
  fi
done

# Step 4c: Copy real content from target (before target is deleted!)
for sub in $unique; do
  cp -a "$TARGET/$CAT/$sub" "$SOURCE/$CAT/"
done

# Step 4d: Now safe to backup, delete target, and symlink (Phase 3)
```

**PITFALL**: Do NOT use `find ... -exec dirname {} \;` directly with `comm` — it outputs mixed full-paths and `SKILL.md` filenames. Use `basename` of the parent directory instead. See `references/target-unique-injection.md` for the full recipe with recovery steps.

**PITFALL**: If source already has symlinks for the target-unique sub-skills (e.g., BACKLINK symlinks inside the category), `cp -a` will silently fail because the symlink target no longer exists after Phase 3. Always remove stale symlinks FIRST (Step 4b), then copy real content while target is still a real directory.

### Phase 5: Verify

```bash
# Prefer -xtype l for broken symlink detection (avoids ELOOP)
find ~/.hermes/skills/ -maxdepth 1 -xtype l
# Empty = no broken links at top level

# Internal category broken symlinks — use -xtype l (same ELOOP-safe approach)
find ~/.hermes-feishu/skills/ -xtype l
# Empty = no broken links anywhere in source categories
```

If broken symlinks are found, remove them with `find <dir> -xtype l -delete`. Do NOT use `find -exec test -e {} \;` — it crashes on circular chains (ELOOP). See `references/source-integrity-check.md` for the full recovery workflow.

## Mode B: Repo-to-Local Sync

Sync skills from a GitHub repo (e.g., `jorinyang/awesome-skills`) to local instance.

### 1. Download (TUN proxy workaround)

When `git clone` is blocked by TUN proxy (Vortex/Clash):

```bash
curl -sL --connect-timeout 10 --max-time 30 \
  "https://api.github.com/repos/OWNER/REPO/zipball/main" \
  -o /tmp/repo.zip
```

Extract with Python (no `unzip` dependency):

```python
import zipfile, os, shutil
with zipfile.ZipFile('/tmp/repo.zip') as z:
    z.extractall('/tmp/extracted')
# Unwrap GitHub's OWNER-REPO-COMMIT/ wrapper
for d in os.listdir('/tmp/extracted'):
    if os.path.isdir(os.path.join('/tmp/extracted', d)):
        shutil.move(os.path.join('/tmp/extracted', d), '/tmp/repo')
        break
```

### 2. Build skill inventory

```python
repo_base = Path('/tmp/repo')
repo_skills = {}
for item in repo_base.iterdir():
    if item.name.startswith('.'): continue
    if item.is_dir() and (item / "SKILL.md").exists():
        repo_skills[item.name] = (None, item)  # top-level
    elif item.is_dir():
        for sub in item.iterdir():
            if sub.is_dir() and (sub / "SKILL.md").exists():
                repo_skills[sub.name] = (item.name, sub)  # categorized
```

### 3. Diff and copy

Build local skill set (walk top-level + category symlinks), exclude unwanted categories (e.g., travel), skip existing skills, copy the rest with `shutil.copytree`.

### 4. Handle duplicates

Repo skills may collide with existing categorized skills. After sync, run `skill_view(name)` on new skills. If "Ambiguous skill name", delete the flat duplicate (keep the categorized one).

## Critical Pitfalls

### Symlink detection with trailing slash

```bash
# WRONG — [ -L "/path/dir/" ] dereferences symlink-to-directory
[ -L "${d%/}" ]  # RIGHT — strip trailing slash first
```

### find -type d misses symlinks

`find -type d` returns actual directories only. Use `find -type l` for symlink counts.

### Circular symlink chains (silent breakage)

The most dangerous failure: source has symlinks pointing back to target. When you then create a symlink from target to source, you get a circular chain that `test -e` reports as broken (too many symlink levels):

```
target/A → source/A → target/A  (💥 broken, no error on creation)
```

**Do NOT create any symlinks until Phase 0 passes clean.** If Phase 0 finds backlinks, the fix is always: migrate real content into source FIRST, then retry the sync. Never attempt to work around by linking in the opposite direction unless the user explicitly redesigns the architecture.

See `scripts/check-source-integrity.py` and `references/source-integrity-check.md` for the full detection logic and a real-world example.

### cp -a double nesting

`cp -a src/ target/sub/` creates `target/sub/sub/` if `target/sub/` doesn't exist. Use `cp -a src/ target/` and rename, or check existence first.

### Internal category symlinks break after re-linking

Category directories may contain symlinks that point inside the same category on the other side:

```
source/github/codebase-inspection → /home/aorus/.hermes/skills/github/codebase-inspection
```

After Phase 3 replaces target with a symlink to source, these become circular:

```
source/github/codebase-inspection → target/github/codebase-inspection → source/github/codebase-inspection (💥)
```

**Fix**: During Phase 4, BEFORE deleting target, scan source for internal symlinks pointing into target's copy of the same category. Remove them and replace with real content from target. After the sync, also scan for any remaining broken symlinks inside source categories:

```bash
# After all sync ops complete — use -xtype l (ELOOP-safe)
find "$SOURCE" -xtype l          # list broken
find "$SOURCE" -xtype l -delete  # clean them in one pass
```

### `test -e` on broken symlinks can cause "Symlink loop" errors

When a symlink chain is circular (`A → B → A`), `test -e` does NOT just report "broken" — it raises a "Symlink loop" / ELOOP error that can crash the calling process. This is especially dangerous in `find -exec test -e {} \;` where a single circular chain aborts the entire scan.

**Preferred approach**: use GNU `find -xtype l` — it matches broken symlinks WITHOUT following or resolving chains, so it never hits ELOOP:

```bash
# BEST: safe, simple, no loop needed
find "$SOURCE" -xtype l         # list broken links
find "$SOURCE" -xtype l -delete # clean them in one pass
```

**Fallback** (if `-xtype l` unavailable on your system): use `readlink` (without `-f`) and check existence:

```bash
# SAFE: detects broken links without following them
find "$SOURCE" -type l | while read link; do
  target=$(readlink "$link" 2>/dev/null)
  if [ ! -e "$link" ] 2>/dev/null; then
    echo "BROKEN: $link -> $target"
  fi
done
```

Note: `readlink` without `-f` returns the raw symlink target string without resolving chains, so it never encounters ELOOP. The `2>/dev/null` on `[ ! -e "$link" ]` suppresses the ELOOP error message if the kernel does raise it.

### `find -delete` blocked by Hermes Agent (cron mode silent failure)

In Hermes Agent environments, `find ... -delete` may trigger a safety guard (pattern `find -delete` → `pending_approval`). In cron mode with no user present, the command appears to succeed but no files are deleted. **This is the most common cause of "broken symlinks persist after sync"**.

**Detection**: always run a read-only check first:
```bash
BROKEN=$(find "$TARGET" -xtype l 2>/dev/null | wc -l)
```
If count > 0 and `find -delete` can't clear them, report the paths — the sync can still proceed safely since broken symlinks don't block new link creation.

### Broken Symlink Cleanup

Broken symlinks in target are the #1 cause of "Connection error" / failed sync notifications in cron mode. Three common sources:

1. **Stale archives** — old `.archive/sync_*` backups whose link targets were deleted
2. **TARGET_ONLY directories with stale internal links** — e.g., `target/mapping/amap-lbs → source/mapping/amap-lbs` where the source directory doesn't exist
3. **Post-sync residues** — links that became circular after a previous sync

**Cleanup procedure** (run before any sync):

⚠️ **Cron mode**: `find -delete` may be blocked by Hermes Agent safety guard. Split into read-only check first:

```bash
# 0. Quick read-only check (always safe)
BROKEN=$(find "$TARGET" -xtype l 2>/dev/null | wc -l)
if [ "$BROKEN" -eq 0 ]; then echo "✔ No broken links"; else echo "⚠️ $BROKEN broken links found"; fi
```

If broken links exist AND you have manual approval capability:
```bash
# 1. Wipe stale archive symlinks (archive dirs are disposable)
find "$TARGET/.archive" -xtype l -delete 2>/dev/null

# 2. Clean target top-level
find "$TARGET" -maxdepth 1 -xtype l -delete

# 3. Clean inside TARGET_ONLY subdirectories
for dir in $(ls -d "$TARGET"/*/ 2>/dev/null); do
  find "$dir" -xtype l -delete 2>/dev/null
done

# 4. Verify
find "$TARGET" -xtype l 2>/dev/null
# Should print nothing
```

## Rollback

All sync ops backed up to `.archive/sync_<timestamp>/`:

```bash
rm ~/.hermes/skills/$CAT
cp -a ~/.hermes/skills/.archive/sync_TIMESTAMP/$CAT ~/.hermes/skills/
```
