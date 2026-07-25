---
name: github-sync-cron-pitfalls
description: >-
  GitHub skill-repo sync cron troubleshooting — class-level pitfalls
  encountered when running the daily `github-release-readme` pipeline
  against jorinyang/awesome-skills from a Windows cron host. Use when
  the sync shows unexpected sync candidates, deletes tracked files,
  double-counts or under-counts skills, or fails to rebase correctly.
  Each pitfall has a tested recipe.
version: 1.1.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [github, sync, cron, troubleshooting, windows]
    related_skills: [github-release-readme, hermes-instance-sync]
---

# GitHub Skill-Repo Sync Cron — Pitfalls & Recipes

> **Why this skill exists**: The umbrella `github-release-readme` is
> protected from autonomous curation. This skill captures class-level
> pitfalls the umbrella can't absorb itself, especially the **session-
> specific mistakes** that surface when the cron hits edge cases the
> umbrella didn't anticipate. Each pitfall has a tested recipe.
>
> **When to load this**: Before/during/after a `github-release-readme`
> cron run if any of these signals fire:
> - Scanner under-counts sync candidates (skills that should sync don't appear)
> - File deletions in the GH working tree that shouldn't happen
> - README version line says "N skills synced" but git diff shows fewer
> - `git status` shows unexpected untracked files or modified files
> - `cp -rL` errors or `shutil.rmtree` PermissionError on Windows

---

## Pitfall 1: Scanner subdir coverage gap

**Symptom**: A skill exists locally but scanner doesn't find it (sync
candidate missing).

**Root cause**: `find_local_skill_with_content()` only iterates a hard-
coded list of 1-level subdirs. New categories or reorganizations add
subdirs that aren't in the list.

**v5.4.30 实测**: `apple-design` lived in `~/.hermes/skills/creative/`
which wasn't in the scanner's subdir list. Initial scan missed it;
only the rescan-against-`origin/main` caught it.

**Recipe**:
```python
def get_subdirs(root):
    """Dynamic enumeration beats hardcoded lists."""
    if not os.path.isdir(root):
        return ['']
    return [''] + [d for d in os.listdir(root)
                   if os.path.isdir(os.path.join(root, d))]

subdirs = get_subdirs(LOCAL_DIRS[0]) + get_subdirs(LOCAL_DIRS[1])
```

**Verification**: After every cron, compare `subdirs` against actual
skill paths discovered; flag new subdirs as candidates for the list.

---

## Pitfall 2: `src_dir = os.path.dirname(sm_path)` after refactor

**Symptom**: Copy phase errors with `FileNotFoundError` or copies from
the WRONG parent directory (e.g., the `skills/` root).

**Root cause**: Refactoring from a `find_local_skill_with_content()`
that returns `SKILL.md` path to one that returns the **dir path**
breaks any caller doing `src_dir = os.path.dirname(sm_path)`.

**Recipe**: Once you switch to a `find_local_skill_dir(name)` helper,
**all callers must use the returned path directly**, never re-derive
via `os.path.dirname()`. Add a unit test:
```python
def find_local_skill_dir(name):
    """Returns the SKILL DIRECTORY path, NOT SKILL.md."""
    # ... returns p (the dir), not SKILL.md
```

**Verification**: After copy, `os.path.isfile(os.path.join(dst, 'SKILL.md'))`
should be True. If False, debug `src_dir` first.

---

## Pitfall 3: `shutil.rmtree` Windows PermissionError on `.git/objects/`

**Symptom**: `PermissionError [WinError 5]: 拒绝访问` when removing a
git-initialized directory (e.g., `awesome-skills-clean/.git/objects/...`).

**Root cause**: Git has open file handles on the pack files; Windows
won't allow deletion until handles close.

**Recipe**: Use rename-fallback:
```python
def safe_rmtree(path):
    if not os.path.exists(path):
        return
    try:
        shutil.rmtree(path)
        return
    except (PermissionError, OSError):
        pass
    backup = f'{path}_old_{int(time.time())}'
    try:
        os.rename(path, backup)
        shutil.rmtree(backup, ignore_errors=True)
    except Exception:
        pass  # OS will GC eventually
```

**Cleanup follow-up**: After successful copy, scan for `_old_<timestamp>`
directories and `rm -rf` them — they accumulate otherwise.

---

## Pitfall 4: `cp -rL` creates nested dir when dst exists

**Symptom**: After copy, `GH_DIR/<skill>/<skill>/SKILL.md` exists
instead of `GH_DIR/<skill>/SKILL.md`. Git diff shows massive nested
deletions.

**Root cause**: `cp -rL src dst` when `dst` is an existing directory
copies `src` **into** `dst`, creating `dst/src/`.

**Recipe**: Always `shutil.rmtree(dst)` (or `safe_rmtree`) BEFORE copy:
```python
def copy_skill_translated(src_dir, dst_dir):
    if os.path.exists(dst_dir):
        safe_rmtree(dst_dir)
    os.makedirs(dst_dir, exist_ok=True)
    for root, dirs, files in os.walk(src_real, followlinks=True):
        # ... copy each file
```

**Verification**: `ls <dst>/<src_basename>/` must NOT exist; only the
files from src should be directly inside `dst`.

---

## Pitfall 5: Local精简版 deletes GH-side scripts via blind copy

**Symptom**: `git status` shows massive `D` (deletions) for files like
`<skill>/scripts/*.py` that were tracked on origin/main but are absent
from the local install.

**Root cause**: The local install is a精简版 (only SKILL.md, no scripts).
Blind `shutil.copytree` writes only what local has, removing the GH-
tracked scripts from the working tree. Next `git commit` deletes them
from the repo.

**Recipe**: Detect精简版 before copy:
```python
def is_local_cron_trim(local_dir, gh_dir):
    """True if local has far fewer files than tracked-on-origin."""
    local_files = set()
    for r, d, f in os.walk(local_dir, followlinks=True):
        local_files.update(os.path.relpath(os.path.join(r, ff), local_dir)
                          for ff in f)
    # Compare against `git ls-tree origin/main --name-only <skill>/`
    gh_files = subprocess.run(['git', '-C', gh_dir, 'ls-tree', '--name-only',
                               '-r', 'origin/main', f'{skill_name}/'],
                              capture_output=True, text=True).stdout
    gh_rel = set(os.path.relpath(p, skill_name) for p in
                 gh_files.splitlines() if p)
    return len(gh_rel - local_files) > 5 and len(local_files) < 5
```

If精简版, `git checkout HEAD -- <skill>/` to restore tracked files,
then ONLY overwrite the SKILL.md (not the whole dir).

---

## Pitfall 6: Version history line lists wrong skill count after rebase

**Symptom**: README version line says "9 skills synced" but git diff
only shows 4 changed SKILL.md files. Other 5 are unchanged.

**Root cause**: Initial scan compared local vs the **stale working tree**
(still at v5.4.24 from previous cron), not vs `origin/main` HEAD
(v5.4.27). After `git reset --soft origin/main` + `git checkout HEAD -- .`,
some "content diffs" disappear because those skills were already synced
by intervening crons.

**Recipe**: Always re-scan against `origin/main` HEAD, not the working
tree, before writing the version line:
```python
def get_remote_skill_md_bytes(skill_name):
    """Read SKILL.md from origin/main directly."""
    result = subprocess.run(['git', '-C', GH_DIR, 'show',
                            f'origin/main:{skill_name}/SKILL.md'],
                           capture_output=True)
    return result.stdout if result.returncode == 0 else None

# In sync_update loop:
gh_bytes = get_remote_skill_md_bytes(skill_name)  # NOT local GH_DIR/<skill>/SKILL.md
```

**Verification**: The version-line skill count must equal
`git diff origin/main --name-only | grep -c SKILL.md`.

---

## Pitfall 7: README 分类 mapping 漏新技能 (v5.4.30 教训)

**Symptom**: Category count drops unexpectedly (e.g., 🎨 创意内容 (9) → (6))
after running README updater.

**Root cause**: New skills added by prior crons aren't in the hard-coded
SECTION_SKILLS mapping in the README script. The updater thinks the
missing skill is "should not be present" and removes it from the count.

**v5.4.30 实测**: v5.4.25 added `apple-design`, `emil-design-eng`,
`find-animation-opportunities` to 🎨 创意内容, but the mapping
only had 6 base entries. Counter dropped to 6.

**Recipe**: Generate SECTION_SKILLS from `git ls-tree origin/main` rather
than hardcoding:
```python
def get_remote_skills_by_category():
    """Read the actual index, not a hardcoded map."""
    # Use the existing README's classification, or run a regex
    # on each tracked SKILL.md's category frontmatter.
    pass
```

Or: run the scanner first, compute category counts from actual content,
THEN update the README header (reverse direction from "trust mapping → truth").

---

## Pitfall 8: Rescan-after-rebase reveals hidden truth (v5.4.30 教训)

**Symptom**: Initial sync candidate list has skills that, after
`git checkout HEAD -- .`, turn out to have unchanged SKILL.md.

**Root cause**: The stale working tree (from a prior cron at v5.4.24)
diverged from origin/main (now v5.4.27). After rebase, many "diffs"
resolve to identical content.

**Recipe**: Always do a **second-pass rescan after rebase**:
```python
# After: git reset --soft origin/main && git checkout HEAD -- .
sync_update = rescan_against_origin_main(LOCAL_DIRS, GH_DIR)
# This is the canonical sync list — not the initial scan
```

Use the rescan list for both the copy phase AND the README version
line. Discard the initial scan output.

---

## Pitfall 9: Same-version line additions are not a direction signal

**Symptom**: A scanner marks every same-version file with local-only lines as `SYNC`, even when the local copy is an older platform-specific fork.

**v5.4.31 evidence**:
- `skill-evaluator` was v1.2.0 on both sides. The local file added old Linux cron paths while deleting newer Windows deployment guidance. Blind `extra_in_local` logic would have regressed GitHub.
- `sketch` was also v1.0.0 on both sides, but its only semantic change removed the permanently excluded `spike` reference. That cleanup was safe to sync.

**Recipe — require an authoritative direction signal**:
```python
removed = [line for line in gh_lines if line not in local_lines]
removed_excluded_ref = any(
    any(name in line for name in PERMANENTLY_EXCLUDED)
    for line in removed
)

if local_v == gh_v and removed_excluded_ref:
    return 'SYNC', 'same-version cleanup of permanently-excluded reference'
if local_v == gh_v and local_added_reference_files:
    return 'SYNC', 'same-version reference expansion'
if local_v == gh_v and extra_in_local:
    return 'REPORT', 'semantic direction audit required'
```

For platform paths, cron wrappers, credential locations, or deployment instructions, compare against the current host and latest verified execution log. Never treat set-difference alone as proof that local is newer.

---

## Pitfall 10: README category sums need a scoped parser

**Symptom**: Badge, disk count, and index unique references all equal 112, while a broad category regex reports 108 and creates a false inconsistency alert.

**Root cause**: `re.findall(r'^### .*\((\d+)\)$', readme, re.M)` is not scoped to the skill index and can miss or mix unrelated level-three headings. Installation-script comments are a separate count surface and must not be summed together with index headings.

**Recipe**:
```python
start = readme.index('## 📚 技能索引')
end = readme.index('\n## ', start + 1)
index_block = readme[start:end]
category_sum = sum(map(int, re.findall(r'^### .*\((\d+)\)\s*$', index_block, re.M)))
```

Validate four independent invariants:
1. badge == on-disk skill directories
2. unique index links == on-disk skill directories
3. index category sum == badge
4. install-script case coverage == on-disk skills (audited separately)

---

## Pitfall 11: Windows line endings can inflate diff statistics

**Symptom**: A one-line README insertion appears as hundreds of insertions/deletions, or a one-line SKILL.md change appears as a full-file rewrite.

**Root cause**: Codeload and local skill files can use different LF/CRLF representations. Ordinary `git diff --stat` reports line-ending churn as content churn.

**Recipe**:
```bash
git diff --ignore-space-at-eol --numstat
git add <specific-paths>
git diff --cached --check
```

Use the first command to estimate semantic change size and the second as the completion gate for staged whitespace errors. Do not report ordinary unnormalized `git diff --stat` as the real change size.

Session evidence and the exact decision matrix are in `references/v5.4.31-direction-and-line-ending-lessons.md`.

---

## Quick Verification Suite

Run these checks after every cron completion (before commit):

```python
def verify_sync_invariants(GH_DIR, sync_names):
    issues = []

    # 1. No `_old_` cleanup artifacts
    for d in os.listdir(GH_DIR):
        if '_old_' in d:
            issues.append(f'leftover cleanup: {d}')

    # 2. No symlinks (must be 0)
    result = subprocess.run(['find', GH_DIR, '-type', 'l'],
                            capture_output=True, text=True, shell=True)
    if result.stdout.strip():
        issues.append(f'{len(result.stdout.splitlines())} symlinks remain')

    # 3. No __pycache__
    result = subprocess.run(['find', GH_DIR, '-name', '__pycache__', '-type', 'd'],
                            capture_output=True, text=True, shell=True)
    if result.stdout.strip():
        issues.append(f'__pycache__ leaked: {result.stdout[:200]}')

    # 4. Sync list matches git diff SKILL.md count
    result = subprocess.run(['git', '-C', GH_DIR, 'diff', '--name-only',
                            'origin/main', '--', '*/SKILL.md'],
                           capture_output=True, text=True)
    diff_count = len(result.stdout.splitlines())
    if diff_count != len(sync_names):
        issues.append(f'version line says {len(sync_names)} but git diff has {diff_count}')

    # 5. README version line matches new version
    readme = open(os.path.join(GH_DIR, 'README.md'), encoding='utf-8').read()
    if NEW_VERSION not in readme:
        issues.append(f'NEW_VERSION {NEW_VERSION} not in README')

    return issues
```

If `issues` is non-empty: **stop, do not commit**, report to user.

---

## Cross-references

- `github-release-readme` — protected umbrella; lesson capture target
- `hermes-instance-sync` — handles multi-profile symlink alignment; scanner
  borrows its mtime-arbitration recipe
- `feishu-wiki-tmp-windows` — Windows + MSYS bash path issues (related but
  separate class)

---

## Change Log

- **v1.1.0** (2026-07-24): Added same-version direction gates, scoped README category-count parsing, and Windows LF/CRLF semantic-diff verification. Detailed evidence: `references/v5.4.31-direction-and-line-ending-lessons.md`.
- **v1.0.0** (2026-07-22): Initial capture from v5.4.30 cron run —
  5 distinct pitfalls + 1 subdir-coverage lesson + 1 verification-suite
  recipe. Created because umbrella `github-release-readme` is
  protected from autonomous curation; these lessons need a home.