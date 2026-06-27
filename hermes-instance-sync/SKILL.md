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

### Phase 0: Source Integrity Check (MANDATORY — run first)

Before touching any target files, verify the source is actually authoritative. The most common failure mode: source has symlinks pointing back to target, creating circular chains when you try to link target→source.

Run `scripts/check-source-integrity.py <source_dir> <target_dir>`. See `references/source-integrity-check.md` for the full logic.

The script produces three classifications:
| Class | Meaning | Action |
|-------|---------|--------|
| `REAL` | Source has real content (directory, not symlink) | ✅ Safe to use as authority |
| `BACKLINK` | Source is a symlink pointing TO the target dir | 🛑 BLOCKED — circular. Fix source first |
| `EXTERNAL` | Source is a symlink pointing elsewhere | ⚠️ Note it, skip this entry |

**If any BACKLINK entries exist, ABORT the sync.** Report which entries need their canonical content migrated into the source first. Do NOT attempt workarounds — this is structural, not a per-entry issue.

Quick shell one-liner for spot checks:
```bash
# Count backlinks from source to target
find ~/.hermes-feishu/skills/ -maxdepth 1 -type l -exec readlink {} \; | grep -c '/hermes/skills/'
# If > 0: source is NOT authoritative — abort
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

When a category has sub-skills only in target (e.g., `ocr-and-documents`):

```bash
cp -a "$BACKUP/$CAT/unique-sub" ~/.hermes-feishu/skills/$CAT/
```

### Phase 5: Verify

```bash
find ~/.hermes/skills/ -maxdepth 1 -type l -not -exec test -e {} \; -print
# Empty = no broken links
```

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

## Rollback

All sync ops backed up to `.archive/sync_<timestamp>/`:

```bash
rm ~/.hermes/skills/$CAT
cp -a ~/.hermes/skills/.archive/sync_TIMESTAMP/$CAT ~/.hermes/skills/
```
