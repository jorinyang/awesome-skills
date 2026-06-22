---
name: hermes-instance-sync
description: >
  Synchronize skills between Hermes instances using symlinks. Compare, classify,
  backup, and link skill directories across instances (default, feishu, dingtalk).
  Trigger: sync skills from another instance, align skill libraries.
---

# Hermes Instance Skill Sync

Synchronize skills between two Hermes instances using symlinks. The source instance is the authority — target instance skills become symlinks pointing to source.

## Workflow

### Phase 1: Discovery

```bash
# List skills in both instances (top-level dirs only, exclude hidden)
ls ~/.hermes/skills/ | sort > /tmp/target.txt
ls ~/.hermes-feishu/skills/ | sort > /tmp/source.txt

# Three-way diff
comm -23 /tmp/source.txt /tmp/target.txt   # source-only: target is missing -> ADD
comm -13 /tmp/source.txt /tmp/target.txt   # target-only: no source counterpart -> KEEP
comm -12 /tmp/source.txt /tmp/target.txt   # shared: both have -> CLASSIFY
```

### Phase 2: Classify shared directories

For each shared entry, determine type by checking for `SKILL.md` (individual skill) vs subdirectories with SKILL.md (category). Also check symlink status:

```bash
# Check if symlink. CRITICAL: strip trailing slash before testing
for d in ~/.hermes/skills/*; do
  if [ -L "$d" ]; then
    echo "SYMLINK: $(basename $d) -> $(readlink $d)"
  fi
done
```

Classify each shared entry into one of:

| Class | Condition | Action |
|-------|-----------|--------|
| Already linked | Target is symlink to source | No action |
| Safe to sync | Both independent, identical sub-skill sets | Replace with symlink |
| Source-enriched | Source has extra sub-skills target lacks | Replace with symlink |
| Target-unique | Target has sub-skills source lacks | Symlink then restore unique to source |
| Structural mismatch | Different structure (individual vs category) | Skip, keep independent |
| Broken link | Symlink target does not exist | Remove the symlink |

### Phase 3: Backup and Replace

```bash
TS=$(date +%Y%m%d_%H%M%S)
BACKUP="~/.hermes/skills/.archive/sync_$TS"
mkdir -p "$BACKUP"

# For each safe-to-sync or source-enriched category:
cp -a ~/.hermes/skills/$CAT "$BACKUP/"
rm -rf ~/.hermes/skills/$CAT
ln -s ~/.hermes-feishu/skills/$CAT ~/.hermes/skills/$CAT
```

### Phase 4: Handle target-unique sub-skills

When replacing a category that has target-unique sub-skills (example: default has `ocr-and-documents` but feishu does not):

```bash
# After symlinking the category to source:
cp -a "$BACKUP/$CAT/unique-sub-skill" ~/.hermes-feishu/skills/$CAT/
```

This injects the unique skill into the source so both instances have the complete union.

### Phase 5: Verify

```bash
# All symlinks must be valid
find ~/.hermes/skills/ -maxdepth 1 -type l -not -exec test -e {} \; -print
# Empty output means no broken links

# Count final state
echo "Symlinks: $(find ~/.hermes/skills/ -maxdepth 1 -type l | wc -l)"
```

## Critical Pitfalls

### Symlink detection with trailing slash

```bash
# WRONG - resolves symlink target, not the symlink itself
[ -L "/path/to/symlink_dir/" ]

# RIGHT - strip trailing slash first
[ -L "${d%/}" ]
```

`for d in path/*/` loops add trailing slashes. For symlinks-to-directories, `test -L` on slash-suffixed paths dereferences to the target and returns false. Always strip the slash before testing.

### find -type d misses symlinks

`find -type d` only matches actual directories, NOT symlinks-to-directories. Use `find -type l` for symlink counts. Total entries = actual dirs + symlinks.

## Instance Topology

```
Hermes instances: default(~/.hermes), dingtalk(~/.hermes-dingtalk), feishu(~/.hermes-feishu)
Binary: /usr/local/bin/hermes (single binary)

Sync directions:
  default -> feishu: 49 category symlinks (lark-*, ai-engineering, etc.)
  feishu -> default: 5 symlinks (dogfood, memos-cloud, tech-doc, etc.)
  dingtalk: fills gaps from feishu/default (comm -23 -> ln -s)

Note: feishu lark-* skills are symlinks to ~/.agents/skills/lark-* (central repo)
```

## Rollback

All sync operations are backed up to `.archive/sync_<timestamp>/`. To rollback:

```bash
rm ~/.hermes/skills/$CAT
cp -a ~/.hermes/skills/.archive/sync_TIMESTAMP/$CAT ~/.hermes/skills/
```
