#!/usr/bin/env python3
"""Dual-source inventory scanner for hermes skills.
Phase 1+2 of the github-release-readme pipeline.
Scans local ~/.hermes-feishu/skills/ and GitHub /tmp/awesome-skills/,
classifies every skill (self-built/third-party/official/unclassified),
and produces a sync plan.
"""
import os
import re
import subprocess
from pathlib import Path
from collections import defaultdict

LOCAL_SKILLS_DIR = os.path.expanduser("~/.hermes-feishu/skills")
GITHUB_SKILLS_DIR = "/tmp/awesome-skills"

# Permanent excludes (never sync to GitHub)
PERMANENTLY_EXCLUDED = {
    'plan', 'spike', 'dingtalk-channel', 'ocr-and-documents'
}

def get_all_skill_dirs(base_dir):
    """Get all skill directories (with SKILL.md) from base_dir."""
    skills = {}
    if not os.path.isdir(base_dir):
        return skills
    for root, dirs, files in os.walk(base_dir):
        if 'SKILL.md' in files:
            skill_name = os.path.basename(root)
            rel_path = os.path.relpath(root, base_dir)
            skills[skill_name] = os.path.join(root, 'SKILL.md')
    return skills

def read_skill_md_author(path):
    """Extract author from YAML frontmatter of SKILL.md."""
    try:
        with open(path, 'r') as f:
            content = f.read(3000)
    except:
        return None, ''
    author_match = re.search(r'author:\s*(.+)', content)
    author = author_match.group(1).strip() if author_match else None
    return author, content

def classify_skill(skill_name, content, author):
    """Classify skill as self-built, third-party, or official."""
    # 0. Permanent excludes
    if skill_name in PERMANENTLY_EXCLUDED:
        return 'official'

    # 1. Official/plugin markers
    official_markers = [
        'plugin:', 'superpowers:', 'hermes builtin',
        'hermes官方', 'from hermes core'
    ]
    if any(m in content for m in official_markers):
        return 'official'

    # 2. Self-built markers
    self_built_authors = ['杨瑒', '月夜', 'jorinyang']
    if author and any(a in author for a in self_built_authors):
        return 'self-built'

    # 3. Third-party absorption markers
    third_party_markers = ['吸收自', 'adapted from']
    if any(m in content.lower() for m in third_party_markers):
        return 'third-party'

    # Known upstream patterns
    known_upstreams = [
        'leonxlnx', 'cocoon', 'nutlope', 'vercel', 'chenglou',
        'agents365', 'coleam00', 'helloianneo', 'yizhiyanhua',
        'freestylefly', 'open-pencil', 'openeuler', 'lijigang',
        'orchestra', 'deepjai',
    ]
    if any(f'adapted from {u}' in content.lower() for u in known_upstreams):
        return 'third-party'

    return 'unclassified'

def main():
    print("=" * 60)
    print("Phase 1: Dual-Source Scan")
    print("=" * 60)

    # Scan local (resolve symlinks to unique real skills)
    local_raw = get_all_skill_dirs(LOCAL_SKILLS_DIR)
    local_skills = {}
    for name, path in local_raw.items():
        try:
            real = os.path.realpath(path)
            real_dir = os.path.dirname(real)
            if real_dir not in [v for v in local_skills.values()]:
                local_skills[name] = real_dir
        except:
            local_skills[name] = os.path.dirname(path)

    # Scan GitHub
    github_skills = get_all_skill_dirs(GITHUB_SKILLS_DIR)
    github_skills = {k: os.path.dirname(v) for k, v in github_skills.items()}

    print(f"\n本地: {len(local_skills)} 技能 | GitHub: {len(github_skills)} 技能")

    shared = set(local_skills.keys()) & set(github_skills.keys())
    local_only = set(local_skills.keys()) - set(github_skills.keys())
    github_only = set(github_skills.keys()) - set(local_skills.keys())

    print(f"共享: {len(shared)} | 仅本地: {len(local_only)} | 仅GitHub: {len(github_only)}")

    # Classify
    print("\n" + "=" * 60)
    print("Phase 2: Classification")
    print("=" * 60)

    classifications = {}
    for name in local_skills:
        path = os.path.join(local_skills[name], 'SKILL.md')
        author, content = read_skill_md_author(path)
        cls = classify_skill(name, content, author)
        classifications[name] = {'class': cls, 'author': author, 'path': local_skills[name]}

    for name in github_only:
        path = os.path.join(github_skills[name], 'SKILL.md')
        author, content = read_skill_md_author(path)
        cls = classify_skill(name, content, author)
        classifications[name] = {'class': cls, 'author': author, 'path': github_skills[name]}

    by_class = defaultdict(list)
    for name, info in classifications.items():
        by_class[info['class']].append(name)

    print(f"\n自建 (self-built): {len(by_class['self-built'])}")
    print(f"   {', '.join(sorted(by_class['self-built']))}")
    print(f"\n第三方吸收 (third-party): {len(by_class['third-party'])}")
    print(f"   {', '.join(sorted(by_class['third-party']))}")
    print(f"\n官方/插件 (official): {len(by_class['official'])}")
    print(f"\n未分类 (unclassified): {len(by_class['unclassified'])}")
    if by_class['unclassified']:
        print(f"   ⚠️  {', '.join(sorted(by_class['unclassified']))}")

    # Sync candidates
    sync_candidates = []
    for name in local_only:
        cls = classifications.get(name, {}).get('class', 'unclassified')
        if cls in ('self-built', 'third-party'):
            sync_candidates.append(('NEW', name, cls))

    content_diff = []
    for name in sorted(shared):
        local_path = os.path.join(local_skills[name], 'SKILL.md')
        github_path = os.path.join(github_skills[name], 'SKILL.md')
        try:
            with open(local_path, 'r') as f:
                local_content = f.read()
            with open(github_path, 'r') as f:
                github_content = f.read()
            if local_content.strip() != github_content.strip():
                content_diff.append(('MOD', name, classifications.get(name, {}).get('class', 'unknown')))
        except:
            pass

    print("\n" + "=" * 60)
    print("Phase 3: Sync Plan")
    print("=" * 60)

    print(f"\n待新增 (本地独有-自建/三方): {len(sync_candidates)}")
    for action, name, cls in sync_candidates:
        print(f"  + {name} ({cls})")

    print(f"\n待更新 (内容差异): {len(content_diff)}")
    for action, name, cls in content_diff:
        print(f"  ~ {name} ({cls})")

    print(f"\nGitHub独有 (仅远端): {len(github_only)}")
    for name in sorted(github_only):
        cls = classifications.get(name, {}).get('class', 'unknown')
        print(f"  - {name} ({cls})")

    has_changes = len(sync_candidates) > 0 or len(content_diff) > 0
    print(f"\n{'🔄 有变更需要同步' if has_changes else '✅ 无需同步，本地与GitHub一致'}")

    # Write result marker for downstream phases
    with open('/tmp/scan_result.txt', 'w') as f:
        f.write(f"HAS_CHANGES={has_changes}\n")
        f.write(f"NEW_COUNT={len(sync_candidates)}\n")
        f.write(f"MOD_COUNT={len(content_diff)}\n")
        f.write(f"GITHUB_ONLY={len(github_only)}\n")
        f.write(f"TOTAL_AFTER={len(github_skills) + len(sync_candidates)}\n")

    return {
        'has_changes': has_changes,
        'new_skills': sync_candidates,
        'modified_skills': content_diff,
        'github_only': list(github_only),
        'classifications': classifications,
        'local_skills': local_skills,
        'github_skills': github_skills,
        'total_after_sync': len(github_skills) + len(sync_candidates),
    }

if __name__ == '__main__':
    main()
