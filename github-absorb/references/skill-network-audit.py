#!/usr/bin/env python3
"""
技能引用网络审计脚本（github-absorb Phase 6 配套工具）

用途：扫描本地技能库 + GitHub awesome-skills 仓库，生成全量引用网络健康报告。
输出：反向引用缺失、孤立技能、业务聚类、交叉引用章节覆盖度。

用法：
  python3 skill-network-audit.py [--github /path/to/awesome-skills] [--local /path/to/skills]
"""

import re, yaml, sys, os
from pathlib import Path
from collections import defaultdict

GITHUB_DEFAULT = "/tmp/awesome-skills"
LOCAL_DEFAULT = os.path.expanduser("~/.hermes-feishu/skills")


def extract_skill(skill_dir: Path, source: str) -> dict | None:
    """从技能目录提取 name + related_skills + 交叉引用章节信息"""
    md = skill_dir / "SKILL.md"
    if not md.exists():
        return None
    content = md.read_text(encoding="utf-8", errors="replace")
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    fm = {}
    if fm_match:
        try:
            fm = yaml.safe_load(fm_match.group(1)) or {}
        except Exception:
            pass
    name = fm.get("name", skill_dir.name)
    related = fm.get("metadata", {}).get("hermes", {}).get("related_skills", [])
    if not related:
        related = fm.get("related_skills", [])
    has_cross = bool(re.search(r"##\s+与其他技能的关系", content))
    has_guidance = bool(re.search(r"##\s+关联技能指引", content))
    return {
        "name": name,
        "path": str(skill_dir.relative_to(skill_dir.parents[1])),
        "related_skills": related,
        "has_cross_ref": has_cross,
        "has_guidance": has_guidance,
        "source": source,
    }


def load_skills(base: Path, source: str) -> dict:
    """加载目录下所有技能的引用数据"""
    skills = {}
    for md in sorted(base.rglob("SKILL.md")):
        info = extract_skill(md.parent, source)
        if info:
            skills[info["name"]] = info
    return skills


def find_reverse_gaps(all_skills: dict) -> list[tuple[str, str]]:
    """找反向引用缺失: A→B 但 B-→A"""
    all_names = set(all_skills.keys())
    gaps = []
    for name, info in sorted(all_skills.items()):
        for ref in info["related_skills"]:
            if ref in all_names and name not in all_skills[ref]["related_skills"]:
                gaps.append((name, ref))
    return gaps


def find_orphans(all_skills: dict) -> list[tuple[str, str]]:
    """找引用到不存在技能的孤引用"""
    all_names = set(all_skills.keys())
    orphans = []
    for name, info in sorted(all_skills.items()):
        for ref in info["related_skills"]:
            if ref not in all_names:
                orphans.append((name, ref))
    return orphans


def find_isolated(all_skills: dict) -> list[str]:
    """找完全孤立的技能"""
    return [
        name
        for name, info in sorted(all_skills.items())
        if not info["related_skills"]
        and not info["has_cross_ref"]
        and not info["has_guidance"]
    ]


def build_clusters(all_skills: dict) -> list[set[str]]:
    """基于 shared references 构建连通聚类"""
    all_names = set(all_skills.keys())
    adj: defaultdict[str, set] = defaultdict(set)
    for name, info in all_skills.items():
        for ref in info["related_skills"]:
            if ref in all_names:
                adj[name].add(ref)
                adj[ref].add(name)

    visited: set[str] = set()
    clusters: list[set[str]] = []
    for name in all_names:
        if name not in visited:
            comp: set[str] = set()
            queue = [name]
            while queue:
                n = queue.pop(0)
                if n in visited:
                    continue
                visited.add(n)
                comp.add(n)
                for neighbor in adj[n]:
                    if neighbor not in visited:
                        queue.append(neighbor)
            clusters.append(comp)
    clusters.sort(key=len, reverse=True)
    return clusters


def main():
    github_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(GITHUB_DEFAULT)
    local_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(LOCAL_DEFAULT)

    gh = load_skills(github_path, "github") if github_path.exists() else {}
    local = load_skills(local_path, "local") if local_path.exists() else {}

    all_skills = {**gh, **local}  # GitHub 优先

    print(f"Total: {len(all_skills)} (GitHub: {len(gh)}, Local: {len(local)})")
    print()

    # 1. Reverse gaps
    gaps = find_reverse_gaps(all_skills)
    print(f"1. Reverse gaps: {len(gaps)}")
    for a, b in sorted(gaps):
        print(f"   ⚠ {a} → {b}")
    print()

    # 2. Orphans
    orphans = find_orphans(all_skills)
    print(f"2. Orphan refs: {len(orphans)}")
    for a, b in sorted(set(orphans)):
        print(f"   ❌ {a} → {b}")
    print()

    # 3. Isolated
    isolated = find_isolated(all_skills)
    print(f"3. Isolated: {len(isolated)}")
    for n in sorted(isolated):
        src = all_skills[n]["source"]
        print(f"   [{src}] {n}")
    print()

    # 4. Cross-ref sections
    with_xr = [(n, i) for n, i in all_skills.items() if i["has_cross_ref"] or i["has_guidance"]]
    print(f"4. With cross-ref section: {len(with_xr)}")
    for n, i in sorted(with_xr):
        print(f"   [{i['source']}] {n}  xr:{i['has_cross_ref']} guide:{i['has_guidance']}")
    print()

    # 5. Clusters
    clusters = build_clusters(all_skills)
    print(f"5. Clusters: {len(clusters)}")
    for i, c in enumerate(clusters):
        names = sorted(c)
        print(f"   C{i+1} ({len(names)}): {', '.join(names[:8])}{'...' if len(names) > 8 else ''}")


if __name__ == "__main__":
    main()
