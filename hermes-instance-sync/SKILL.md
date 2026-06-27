---
name: hermes-instance-sync
description: >
  Synchronize skills between Hermes instances using symlinks, or from a GitHub
  skills repo. Compare, classify, backup, and link skill directories. Trigger:
  sync skills from another instance, align skill libraries, clone repo skills.
related_skills: [double-evolution]
---

# Hermes Skill Sync

Two sync modes: **instance-to-instance** (symlink) and **repo-to-local** (copy from GitHub).

## Mode A: Instance-to-Instance Sync

Synchronize skills between Hermes instances using symlinks. Source is authority.

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

When a category has sub-skills only in target (e.g., a document extraction skill):

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

### cp -a double nesting

`cp -a src/ target/sub/` creates `target/sub/sub/` if `target/sub/` doesn't exist. Use `cp -a src/ target/` and rename, or check existence first.

## Rollback

All sync ops backed up to `.archive/sync_<timestamp>/`:

```bash
rm ~/.hermes/skills/$CAT
cp -a ~/.hermes/skills/.archive/sync_TIMESTAMP/$CAT ~/.hermes/skills/
```
