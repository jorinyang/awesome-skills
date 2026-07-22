#!/usr/bin/env python3
"""
verify_sync_state.py — Pre-commit verification suite for github-release-readme cron.

Runs the 5 invariants from SKILL.md §Quick Verification Suite. Exits 0 if
clean, 1 if any issue detected. Use BEFORE `git add -A && git commit` to
catch the 4 most common pitfalls before they hit the remote.

Usage:
    python verify_sync_state.py [GH_DIR] [EXPECTED_SYNC_NAMES_FILE]

If EXPECTED_SYNC_NAMES_FILE is omitted, the SKILL.md version history
table is parsed for the most-recent entry's sync list.
"""
import os
import re
import sys
import subprocess
import json

def verify_no_cleanup_artifacts(gh_dir):
    """Pitfall 3 follow-up: `_old_<ts>` dirs from failed rmtree."""
    issues = []
    for d in os.listdir(gh_dir):
        if '_old_' in d:
            issues.append(f'leftover cleanup dir: {d} (run `rm -rf` to clean)')
    return issues


def verify_no_symlinks(gh_dir):
    """Pitfall from PHASE 5G: symlinks in GH_DIR break git push."""
    result = subprocess.run(['find', gh_dir, '-type', 'l'],
                            capture_output=True, text=True, shell=True, timeout=60)
    symlinks = [l for l in result.stdout.splitlines() if l.strip()]
    if symlinks:
        return [f'{len(symlinks)} symlinks in GH_DIR (cp -rL failed?)',
                f'  First 3: {symlinks[:3]}']
    return []


def verify_no_pycache(gh_dir):
    """Pitfall from PHASE 5G: __pycache__ pollutes repo."""
    result = subprocess.run(['find', gh_dir, '-name', '__pycache__', '-type', 'd'],
                            capture_output=True, text=True, shell=True, timeout=60)
    caches = [l for l in result.stdout.splitlines() if l.strip()]
    if caches:
        return [f'{len(caches)} __pycache__ dirs leaked (run cleanup)',
                f'  First 3: {caches[:3]}']
    return []


def verify_sync_list_matches_diff(gh_dir, expected_names):
    """Pitfall 6: version line lists N skills but git diff shows M."""
    result = subprocess.run(['git', '-C', gh_dir, 'diff', '--name-only',
                            'origin/main', '--', '*/SKILL.md'],
                           capture_output=True, text=True)
    diff_names = set()
    for line in result.stdout.splitlines():
        # line: '<skill>/SKILL.md'
        if line.endswith('/SKILL.md'):
            diff_names.add(line[:-len('/SKILL.md')])
    expected_set = set(expected_names)
    missing = expected_set - diff_names  # in version line but not diff
    extra = diff_names - expected_set    # in diff but not version line
    issues = []
    if missing:
        issues.append(f'version line lists {sorted(missing)} but git diff has no changes')
    if extra:
        issues.append(f'git diff has {sorted(extra)} not listed in version line')
    return issues


def verify_badge_matches_count(gh_dir):
    """Pitfall 7: badge count drift."""
    readme_path = os.path.join(gh_dir, 'README.md')
    if not os.path.isfile(readme_path):
        return ['README.md not found']
    readme = open(readme_path, encoding='utf-8').read()
    m = re.search(r'\[!\[Skills\]\(https://img\.shields\.io/badge/Skills-(\d+)-blue\)\]', readme)
    if not m:
        return ['Badge pattern not found in README']
    badge_count = int(m.group(1))
    # Actual count
    actual = sum(1 for d in os.listdir(gh_dir)
                if os.path.isdir(os.path.join(gh_dir, d))
                and not d.startswith('.')
                and '_old_' not in d
                and not d.endswith('.md')
                and not d.endswith('.txt'))
    if badge_count != actual:
        return [f'badge says {badge_count} but actual dirs = {actual}']
    return []


def parse_latest_version_sync_names(gh_dir):
    """Read README's most-recent version row and extract skill names."""
    readme = open(os.path.join(gh_dir, 'README.md'), encoding='utf-8').read()
    # Find the version history table
    table_idx = readme.find('| 版本 | 日期 | 变更 |')
    if table_idx < 0:
        return []
    # Find first row after header
    header_end = readme.find('\n\n', table_idx)
    if header_end < 0:
        return []
    # Skip the |---| separator row
    table_section = readme[table_idx:header_end]
    lines = table_section.splitlines()
    # First data row is lines[2] (after header + separator)
    if len(lines) < 3:
        return []
    first_row = lines[2]
    # Extract skill names from parenthesized list like (skill1/skill2/skill3)
    # or prose mentions
    m = re.search(r'\(([^)]+)\)', first_row)
    if m:
        names_str = m.group(1)
        # Split by / and strip
        return [n.strip() for n in names_str.split('/') if n.strip()]
    return []


def main():
    if len(sys.argv) > 1:
        gh_dir = sys.argv[1]
    else:
        gh_dir = r'C:\tmp\awesome-skills-clean'

    if len(sys.argv) > 2:
        with open(sys.argv[2], encoding='utf-8') as f:
            expected = [line.strip() for line in f if line.strip()]
    else:
        expected = parse_latest_version_sync_names(gh_dir)
        if expected:
            print(f'[*] Auto-extracted {len(expected)} sync names from README version row')

    if not os.path.isdir(gh_dir):
        print(f'[✗] GH_DIR not found: {gh_dir}')
        sys.exit(2)

    print(f'[*] Verifying sync state in: {gh_dir}')
    print(f'[*] Expected sync names: {expected}')
    print()

    all_issues = []
    print('  [1/5] checking no _old_ cleanup artifacts...')
    all_issues += verify_no_cleanup_artifacts(gh_dir)
    print('  [2/5] checking no symlinks...')
    all_issues += verify_no_symlinks(gh_dir)
    print('  [3/5] checking no __pycache__...')
    all_issues += verify_no_pycache(gh_dir)
    print('  [4/5] checking sync list matches git diff...')
    if expected:
        all_issues += verify_sync_list_matches_diff(gh_dir, expected)
    else:
        print('       (skipped — no expected list provided)')
    print('  [5/5] checking badge matches dir count...')
    all_issues += verify_badge_matches_count(gh_dir)
    print()

    if all_issues:
        print(f'[✗] {len(all_issues)} issue(s) found:')
        for i, issue in enumerate(all_issues, 1):
            print(f'  {i}. {issue}')
        print()
        print('DO NOT COMMIT. Fix the issues above and re-run.')
        sys.exit(1)
    else:
        print('[✓] All invariants satisfied. Safe to commit.')
        sys.exit(0)


if __name__ == '__main__':
    main()