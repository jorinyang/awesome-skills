#!/usr/bin/env python3
"""Create a deterministic, whitelist-only ZIP for a validated archive."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

from archive_common import output_path, package_files, read_article_rows
from validate_archive import validate_archive


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("author_root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.author_root.expanduser().resolve()
    errors, _ = validate_archive(root)
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    output = (
        args.output.expanduser().resolve()
        if args.output
        else output_path(root, "archive")
    )
    if output.parent == root and output != output_path(root, "archive"):
        print("custom ZIP output must be outside author_root", file=sys.stderr)
        return 2
    rows, _ = read_article_rows(root)
    files = sorted(package_files(root, rows))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)

    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in files:
            arcname = Path(root.name) / path.relative_to(root)
            archive.write(path, arcname.as_posix())
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
