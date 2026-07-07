#!/usr/bin/env python3
"""
技能引用网络双源审计脚本。
扫描本地 + GitHub 双源技能库，输出：反向引用缺口/孤儿引用/孤立技能/连通聚类。
用法: python3 scripts/audit-reference-network.py /tmp/awesome-skills ~/.hermes-feishu/skills
"""

import re, yaml, sys
from pathlib import Path
from collections import defaultdict


def extract_skill(skill_dir):
    md = skill_dir / "SKILL.md"
    if not md.exists():
        return None
    content = md.read_text(encoding='utf-8', errors='replace')
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    fm = {}
    if fm_match:
        try:
            fm = yaml.safe_load(fm_match.group(1)) or {}
        except: pass
    name = fm.get('name', skill_dir.name)
    related = fm.get('metadata', {}).get('hermes', {}).get('related_skills', [])
    if not related:
        related = fm.get('related_skills', [])
    has_cross = bool(re.search(r'##\s+与其他技能的关系', content))
    has_guidance = bool(re.search(r'##\s+关联技能指引', content))
    return {'name': name, 'related_skills': related, 'has_cross_ref': has_cross, 'has_guidance': has_guidance}


def audit(gh_root, local_root):
    all_skills = {}
    for base in [Path(gh_root), Path(local_root)]:
        if not base.exists():
            continue
        for md in base.rglob("SKILL.md"):
            info = extract_skill(md.parent)
            if info and info['name'] not in all_skills:
                all_skills[info['name']] = info

    all_names = set(all_skills.keys())

    print("=" * 70)
    print("1. REVERSE REFERENCE GAPS (A -> B but B -/> A)")
    print("=" * 70)
    gaps = []
    for name, info in sorted(all_skills.items()):
        for ref in info['related_skills']:
            if ref in all_names and name not in all_skills[ref]['related_skills']:
                gaps.append((name, ref))
    for a, b in gaps:
        print(f"  WARN {a} -> {b}")
    print(f"  Total: {len(gaps)}\n")

    print("=" * 70)
    print("2. ORPHAN REFERENCES")
    print("=" * 70)
    orphans = [(n, r) for n, i in all_skills.items() for r in i['related_skills'] if r not in all_names]
    for a, b in orphans:
        print(f"  ERR {a} -> {b}")
    print(f"  Total: {len(orphans)}\n")

    print("=" * 70)
    print("3. ISOLATED SKILLS")
    print("=" * 70)
    isolated = [n for n, i in all_skills.items() if not i['related_skills'] and not i['has_cross_ref'] and not i['has_guidance']]
    print(f"  Total: {len(isolated)}")
    for n in sorted(isolated):
        print(f"    {n}")
    print()

    print("=" * 70)
    print("4. WITH GUIDANCE SECTIONS")
    print("=" * 70)
    with_xr = [(n, i) for n, i in all_skills.items() if i['has_cross_ref'] or i['has_guidance']]
    print(f"  Total: {len(with_xr)}")
    for n, i in sorted(with_xr):
        print(f"    {n}  cross_ref={'Y' if i['has_cross_ref'] else 'N'} guidance={'Y' if i['has_guidance'] else 'N'}")
    print()

    print("=" * 70)
    print("5. CLUSTERS")
    print("=" * 70)
    adj = defaultdict(set)
    for name, info in all_skills.items():
        for ref in info['related_skills']:
            if ref in all_names:
                adj[name].add(ref)
                adj[ref].add(name)
    visited = set()
    clusters = []
    for name in all_names:
        if name not in visited and adj[name]:
            comp = set()
            queue = [name]
            while queue:
                n = queue.pop(0)
                if n in visited: continue
                visited.add(n)
                comp.add(n)
                for nb in adj[n]:
                    if nb not in visited:
                        queue.append(nb)
            clusters.append(comp)
    for name in all_names:
        if name not in visited:
            clusters.append({name})
    clusters.sort(key=len, reverse=True)
    for i, c in enumerate(clusters):
        if len(c) == 1:
            print(f"  Cluster {i+1} (solo): {list(c)[0]}")
        else:
            print(f"  Cluster {i+1} ({len(c)}): {', '.join(sorted(c))}")


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        audit(sys.argv[1], sys.argv[2])
    else:
        print(f"Usage: {sys.argv[0]} <github-skills-dir> <local-skills-dir>")
