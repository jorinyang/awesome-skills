#!/usr/bin/env python3
"""
技能引用网络审计器 — 扫描技能库中所有非官方技能，检测：
  1. 反向引用缺失（A→B 但 B 不引用 A）
  2. 孤立技能（无任何 related_skills）
  3. 引用到不存在的技能
  4. 缺少「与其他技能的关系」/「关联技能指引」章节

用法：
  python3 scripts/audit-reference-network.py [--skills-dir ~/.hermes-feishu/skills]

输出：结构化审计报告（终端 + JSON）
"""

import yaml, re, os, sys, json
from pathlib import Path
from collections import defaultdict

SKILLS_DIR = Path(os.environ.get("SKILLS_DIR", os.path.expanduser("~/.hermes-feishu/skills")))

# 官方技能（跳过审计）
OFFICIAL_NAMES = {
    "image-analysis", "ocr-and-documents",
    "zhike-task-hub", "project-kanban", "feishu-html",
    "feishu-doc", "feishu-table", "lark-shared", "lark-skill-maker",
}


def extract_skill(skill_path: Path) -> dict | None:
    """从 SKILL.md 提取元数据和引用信息"""
    md = skill_path / "SKILL.md"
    if not md.exists():
        return None
    content = md.read_text(encoding="utf-8", errors="replace")

    # 提取 frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    fm = {}
    if fm_match:
        try:
            fm = yaml.safe_load(fm_match.group(1)) or {}
        except Exception:
            pass

    name = fm.get("name", skill_path.name)
    related = fm.get("metadata", {}).get("hermes", {}).get("related_skills", [])
    if not related:
        related = fm.get("related_skills", [])

    # 检测章节
    has_cross = bool(re.search(
        r"##\s+与其他技能的关系", content
    ))
    has_guidance = bool(re.search(
        r"##\s+关联技能指引", content
    ))

    return {
        "name": name,
        "category": skill_path.parent.name if skill_path.parent != SKILLS_DIR else "root",
        "related_skills": related,
        "has_cross_ref_section": has_cross,
        "has_guidance_section": has_guidance,
    }


def audit() -> dict:
    """执行全库审计"""
    non_official = {}
    for md_path in sorted(SKILLS_DIR.rglob("SKILL.md")):
        info = extract_skill(md_path.parent)
        if info and info["name"] not in OFFICIAL_NAMES:
            non_official[info["name"]] = info

    all_names = set(non_official.keys())

    # 反向引用缺失
    reverse_gaps = []
    for name, info in sorted(non_official.items()):
        for ref in info["related_skills"]:
            if ref in all_names and name not in non_official[ref]["related_skills"]:
                reverse_gaps.append((name, ref))

    # 孤立技能
    orphans = [name for name, info in non_official.items() if not info["related_skills"]]

    # 引用到不存在的技能
    missing_refs = []
    for name, info in sorted(non_official.items()):
        for ref in info["related_skills"]:
            if ref not in all_names:
                missing_refs.append((name, ref))

    # 缺少章节
    missing_cross = [name for name, info in non_official.items() if not info["has_cross_ref_section"]]
    missing_guidance = [name for name, info in non_official.items() if not info["has_guidance_section"]]

    return {
        "summary": {
            "total_non_official": len(non_official),
            "reverse_gaps": len(reverse_gaps),
            "isolated_skills": len(orphans),
            "missing_refs": len(missing_refs),
            "missing_cross_section": len(missing_cross),
            "missing_guidance_section": len(missing_guidance),
        },
        "reverse_gaps": [{"from": a, "to": b} for a, b in reverse_gaps],
        "isolated_skills": orphans,
        "missing_refs": [{"from": a, "to": b} for a, b in missing_refs],
        "missing_cross_section": missing_cross,
        "missing_guidance_section": missing_guidance,
        "skills": {name: info for name, info in sorted(non_official.items())},
    }


def print_report(result: dict):
    """人类可读报告"""
    s = result["summary"]
    print("=" * 60)
    print("技能引用网络审计报告")
    print("=" * 60)
    print(f"非官方技能: {s['total_non_official']}")
    print(f"反向引用缺失: {s['reverse_gaps']}")
    print(f"孤立技能: {s['isolated_skills']}")
    print(f"引用不存在技能: {s['missing_refs']}")
    print(f"缺少 cross_ref 章节: {s['missing_cross_section']}")
    print(f"缺少 guidance 章节: {s['missing_guidance_section']}")
    print()

    if result["reverse_gaps"]:
        print("--- 反向引用缺失 ---")
        for g in result["reverse_gaps"]:
            print(f"  ⚠ {g['from']} → {g['to']}")
        print()

    if result["isolated_skills"]:
        print("--- 孤立技能 ---")
        for name in result["isolated_skills"]:
            print(f"  · {name}")
        print()

    if result["missing_refs"]:
        print("--- 引用到不存在的技能 ---")
        for m in result["missing_refs"]:
            print(f"  ? {m['from']} → {m['to']}")
        print()

    if result["missing_cross_section"]:
        print(f"--- 缺少「与其他技能的关系」章节 ({len(result['missing_cross_section'])} 个) ---")
        for name in result["missing_cross_section"]:
            print(f"  · {name}")

    if result["missing_guidance_section"]:
        print(f"--- 缺少「关联技能指引」章节 ({len(result['missing_guidance_section'])} 个) ---")
        for name in result["missing_guidance_section"]:
            print(f"  · {name}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="技能引用网络审计器")
    p.add_argument("--skills-dir", default=str(SKILLS_DIR), help="技能目录")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    args = p.parse_args()

    global SKILLS_DIR
    SKILLS_DIR = Path(args.skills_dir)

    result = audit()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(result)
