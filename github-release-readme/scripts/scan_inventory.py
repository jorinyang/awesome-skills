#!/usr/bin/env python3
"""Dual-source inventory scanner for hermes skills — v3.0 symlink-safe.
Phase 1+2 of the github-release-readme pipeline.

Uses shell glob (subprocess) instead of os.walk/find -L to safely traverse
200+ symlinked skill directories without hitting ELOOP or exponential traversal.
"""
import os, re, sys, json, subprocess
from collections import defaultdict

LOCAL = os.path.expanduser("~/.hermes-feishu/skills")
GITHUB = "/tmp/awesome-skills"
PERMA_EXCLUDE = {'plan', 'spike', 'dingtalk-channel', 'ocr-and-documents'}

# ── Phase 1: Shell-based scan (symlink-safe) ──

def shell_list(base, depth=2):
    """Use shell glob to list skills — handles symlinks without ELOOP.
    Bash glob expands one level at a time, then we check for SKILL.md
    explicitly. This avoids the core problem with os.walk(followlinks=True)
    and find -L: they traverse into the same directory through multiple
    symlink paths, causing exponential blowup and timeout.
    """
    skills = {}
    # Level 1: base/*/SKILL.md
    cmd = f'for d in "{base}"/*/; do [ -f "${{d}}SKILL.md" ] && echo "$d"; done'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    for line in r.stdout.strip().split('\n'):
        if not line:
            continue
        name = os.path.basename(line.rstrip('/'))
        skills[name] = os.path.join(line.rstrip('/'), 'SKILL.md')
    # Level 2: base/*/*/SKILL.md (subdirectory skills like ai-engineering/agent-tool-system/)
    if depth >= 2:
        cmd2 = f'for d in "{base}"/*/*/; do [ -f "${{d}}SKILL.md" ] && echo "$d"; done'
        r2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=10)
        for line in r2.stdout.strip().split('\n'):
            if not line:
                continue
            name = os.path.basename(line.rstrip('/'))
            if name not in skills:
                skills[name] = os.path.join(line.rstrip('/'), 'SKILL.md')
    return skills

# ── Phase 2: Classification ──

def read_md(path):
    try:
        with open(path) as f:
            c = f.read(5000)
        m = re.search(r'author:\s*(.+)', c)
        return m.group(1).strip() if m else None, c
    except:
        return None, ''

def classify(name, content, author):
    if name in PERMA_EXCLUDE:
        return 'official'
    if author and any(a in author for a in ['杨瑒', '月夜', 'jorinyang']):
        return 'self-built'
    if any(m in content for m in ['plugin:', 'superpowers:', 'hermes builtin',
                                   'hermes官方', 'from hermes core']):
        return 'official'
    if any(m in content.lower() for m in ['吸收自', 'adapted from']):
        return 'third-party'
    return 'unclassified'

# ── Phase 3: Sync plan ──

def main():
    print("=" * 60)
    print("Phase 1: Dual-Source Scan (shell-glob, symlink-safe)")
    print("=" * 60)

    local = shell_list(LOCAL)
    gh = shell_list(GITHUB)

    print(f"\n本地: {len(local)} 技能 | GitHub: {len(gh)} 技能")
    shared = set(local) & set(gh)
    local_only = set(local) - set(gh)
    gh_only = set(gh) - set(local)
    print(f"共享: {len(shared)} | 仅本地: {len(local_only)} | 仅GitHub: {len(gh_only)}")

    print("\n" + "=" * 60)
    print("Phase 2: Classification")
    print("=" * 60)

    cc = {}
    for name in set(local) | set(gh):
        path = local.get(name) or gh.get(name)
        author, content = read_md(path)
        cc[name] = {'class': classify(name, content, author), 'author': author}

    by = defaultdict(list)
    for n, i in cc.items():
        by[i['class']].append(n)

    for cls in ['self-built', 'third-party', 'official', 'unclassified']:
        ns = sorted(by[cls])
        print(f"\n{cls}: {len(ns)}")
        if len(ns) <= 30:
            print(f"   {', '.join(ns)}")
        else:
            print(f"   {', '.join(ns[:15])} ... (+{len(ns)-15} more)")

    print("\n" + "=" * 60)
    print("Phase 3: Sync Plan")
    print("=" * 60)

    new_cands = [(name, cc[name]['class']) for name in sorted(local_only)
                 if cc[name]['class'] in ('self-built', 'third-party')]
    mod_cands = []
    for name in sorted(shared):
        cls = cc[name]['class']
        if cls == 'official':
            continue
        try:
            lc = open(local[name]).read()
            gc = open(gh[name]).read()
            if lc.strip() != gc.strip():
                mod_cands.append((name, cls))
        except:
            pass

    print(f"\n待新增 (本地独有-自建/三方): {len(new_cands)}")
    for n, c in new_cands:
        print(f"  + {n} ({c})")

    print(f"\n待更新 (内容差异): {len(mod_cands)}")
    for n, c in mod_cands:
        print(f"  ~ {n} ({c})")

    unclassified_local = [n for n in local_only if cc[n]['class'] == 'unclassified']
    if unclassified_local:
        print(f"\n⚠️ 本地独有-未分类: {len(unclassified_local)}")
        for n in sorted(unclassified_local)[:10]:
            print(f"  ? {n}")
        if len(unclassified_local) > 10:
            print(f"  ... (+{len(unclassified_local)-10} more)")

    total_after = len(gh) + len(new_cands)
    has = len(new_cands) > 0 or len(mod_cands) > 0
    print(f"\n{'🔄 有变更需要同步' if has else '✅ 无需同步'} (预期同步后: {total_after} 技能)")

    # Write result file for downstream phases
    with open('/tmp/scan_result.txt', 'w') as f:
        f.write(f"HAS_CHANGES={has}\nNEW_COUNT={len(new_cands)}\nMOD_COUNT={len(mod_cands)}\n")
        f.write(f"LOCAL_TOTAL={len(local)}\nGITHUB_TOTAL={len(gh)}\nTOTAL_AFTER={total_after}\n")

    with open('/tmp/scan_data.json', 'w') as f:
        json.dump({
            'new': [(n, c) for n, c in new_cands],
            'mod': [(n, c) for n, c in mod_cands],
            'has_changes': has, 'local': local, 'gh': gh, 'cc': cc,
            'shared': sorted(shared), 'local_only': sorted(local_only),
            'gh_only': sorted(gh_only), 'total_after': total_after
        }, f, ensure_ascii=False, indent=2)

    return 0 if not has else 1

if __name__ == '__main__':
    sys.exit(main())
