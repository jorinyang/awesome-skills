#!/usr/bin/env python3
"""Phase 0: Source Integrity Check for hermes-instance-sync.

Usage: python3 check-source-integrity.py <source_dir> <target_dir>

Classifies each shared entry as REAL, BACKLINK, or EXTERNAL.
Exits non-zero if any BACKLINK detected (sync should abort).
"""

import os
import sys


def classify(source_dir: str, target_dir: str) -> dict[str, list[str]]:
    """Classify shared entries between source and target."""
    results: dict[str, list[str]] = {"REAL": [], "BACKLINK": [], "EXTERNAL": [], "SOURCE_ONLY": [], "TARGET_ONLY": []}

    if not os.path.isdir(source_dir):
        print(f"ERROR: source directory does not exist: {source_dir}")
        sys.exit(2)
    if not os.path.isdir(target_dir):
        print(f"ERROR: target directory does not exist: {target_dir}")
        sys.exit(2)

    source_entries = set(
        e for e in os.listdir(source_dir)
        if not e.startswith(".") and (os.path.isdir(os.path.join(source_dir, e)) or os.path.islink(os.path.join(source_dir, e)))
    )
    target_entries = set(
        e for e in os.listdir(target_dir)
        if not e.startswith(".") and (os.path.isdir(os.path.join(target_dir, e)) or os.path.islink(os.path.join(target_dir, e)))
    )

    results["SOURCE_ONLY"] = sorted(source_entries - target_entries)
    results["TARGET_ONLY"] = sorted(target_entries - source_entries)

    shared = sorted(source_entries & target_entries)

    for entry in shared:
        sp = os.path.join(source_dir, entry)
        tp = os.path.join(target_dir, entry)

        if os.path.isdir(sp) and not os.path.islink(sp):
            results["REAL"].append(entry)
        elif os.path.islink(sp):
            link_target = os.readlink(sp)
            link_target_abs = os.path.normpath(os.path.join(os.path.dirname(sp), link_target))

            # Check if pointing into target directory
            target_abs = os.path.normpath(target_dir)
            if link_target_abs.startswith(target_abs + os.sep) or link_target_abs == target_abs:
                results["BACKLINK"].append(entry)
            else:
                results["EXTERNAL"].append(entry)
        else:
            # File or missing — shouldn't happen for skill dirs
            results["EXTERNAL"].append(entry)

    return results


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <source_dir> <target_dir>")
        sys.exit(2)

    source = os.path.expanduser(sys.argv[1])
    target = os.path.expanduser(sys.argv[2])

    results = classify(source, target)

    print("=== Source Integrity Check ===")
    print(f"Source: {source}")
    print(f"Target: {target}")
    print()

    for cls in ["REAL", "BACKLINK", "EXTERNAL", "SOURCE_ONLY", "TARGET_ONLY"]:
        entries = results[cls]
        print(f"{cls}: {len(entries)}")
        if entries and len(entries) <= 30:
            for e in entries:
                print(f"  {e}")
        elif entries:
            print(f"  (showing first 10 of {len(entries)})")
            for e in entries[:10]:
                print(f"  {e}")
            print(f"  ...")

    print()

    backlinks = len(results["BACKLINK"])
    if backlinks > 0:
        print(f"🛑 BLOCKED: {backlinks} BACKLINK entries detected.")
        print("   Source has symlinks pointing TO target — circular dependency risk.")
        print("   Fix: migrate real content into source first, then retry sync.")
        sys.exit(1)
    else:
        print("✅ CLEAN: No backlinks. Source is authoritative. Safe to proceed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
