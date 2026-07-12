#!/usr/bin/env python3
"""Validate an article archive directory and optional ZIP package."""

from __future__ import annotations

import html
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from archive_common import (
    FORBIDDEN_NAMES,
    FORBIDDEN_SUFFIXES,
    REQUIRED_COLUMNS,
    expected_archive_entries,
    is_within,
    normalize_url,
    output_name,
    output_path,
    package_files,
    read_article_rows,
    safe_article_dir,
    sanitize_name,
)


MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+['\"].*?['\"])?\s*\)")
REFERENCE_IMAGE_RE = re.compile(r"!\[[^\]]*\]\[([^\]]+)\]")
REFERENCE_DEF_RE = re.compile(r"^\s*\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))", re.MULTILINE)
HTML_IMAGE_RE = re.compile(r"<img\b[^>]*\bsrc\s*=\s*['\"]([^'\"]+)['\"]", re.I)
META_LABELS = {
    "公众号": "author_name",
    "公众号标识": "biz",
    "原文链接": "url",
    "发布时间": "publish_time",
    "采集来源": "source_type",
}


def markdown_image_refs(text: str) -> list[str]:
    refs = [first or second for first, second in MARKDOWN_IMAGE_RE.findall(text)]
    definitions = {
        key.strip().lower(): first or second
        for key, first, second in REFERENCE_DEF_RE.findall(text)
    }
    refs.extend(
        definitions[key.strip().lower()]
        for key in REFERENCE_IMAGE_RE.findall(text)
        if key.strip().lower() in definitions
    )
    refs.extend(html.unescape(value) for value in HTML_IMAGE_RE.findall(text))
    return refs


def parse_metadata(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for label, key in META_LABELS.items():
        match = re.search(rf"(?m)^-\s*{re.escape(label)}：\s*(.*?)\s*$", text)
        if match:
            result[key] = match.group(1).strip()
    return result


def validate_archive(root: Path) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    stats = {
        "archived_rows": 0,
        "failed_rows": 0,
        "article_dirs": 0,
        "markdown_files": 0,
        "missing_image_refs": 0,
        "publish_time_unknown": 0,
        "unexpected_files": 0,
        "short_bodies": 0,
        "quality_warnings": 0,
    }
    csv_path = output_path(root, "article_list")
    articles_root = root / "articles"
    if not csv_path.is_file():
        return [f"missing {csv_path.name}"], stats
    if not articles_root.is_dir():
        return ["missing articles/ directory"], stats

    rows, columns = read_article_rows(root)
    missing_columns = sorted(REQUIRED_COLUMNS - columns)
    if missing_columns:
        errors.append(f"{csv_path.name} missing columns: {', '.join(missing_columns)}")

    indexes: list[int] = []
    seen_urls: set[str] = set()
    seen_keys: set[tuple[str, str, str, str]] = set()
    seen_dirs: set[str] = set()
    identities: set[str] = set()

    for row_number, row in enumerate(rows, start=2):
        index: int | None = None
        archived = bool(
            row.get("article_dir", "").strip()
            and row.get("markdown_file", "").strip()
        )
        if archived:
            stats["archived_rows"] += 1
        else:
            stats["failed_rows"] += 1

        try:
            index = int(row.get("index", ""))
            if index <= 0:
                raise ValueError
            indexes.append(index)
        except ValueError:
            errors.append(f"row {row_number} has invalid index")

        url = normalize_url(row.get("url", ""))
        if not url:
            errors.append(f"row {row_number} has invalid URL")
        elif url in seen_urls:
            errors.append(f"row {row_number} duplicates normalized URL: {url}")
        else:
            seen_urls.add(url)

        author_name = row.get("author_name", "").strip()
        if archived and not author_name:
            errors.append(f"row {row_number} is missing author_name")

        query = parse_qs(urlsplit(url).query) if url else {}
        url_values = {
            "biz": (query.get("__biz") or query.get("biz") or [""])[0],
            "mid": (query.get("mid") or query.get("appmsgid") or [""])[0],
            "idx": (query.get("idx") or [""])[0],
            "sn": (query.get("sn") or [""])[0],
        }
        if url_values["biz"]:
            identities.add(f"biz:{url_values['biz']}")
        article_key = (
            url_values["biz"],
            url_values["mid"],
            url_values["idx"],
            url_values["sn"],
        )
        if all(article_key[:3]):
            if article_key in seen_keys:
                errors.append(f"row {row_number} duplicates biz/mid/idx/sn")
            seen_keys.add(article_key)
        if not archived:
            if not row.get("error", "").strip():
                errors.append(f"failed row {row_number} is missing error")
            if row.get("article_dir", "").strip() or row.get("markdown_file", "").strip():
                errors.append(f"failed row {row_number} must not reference archive files")
            continue

        if not row.get("title", "").strip():
            errors.append(f"row {row_number} has empty title")
        if row.get("publish_time", "").strip() in {"", "未知"}:
            stats["publish_time_unknown"] += 1
        if "quality_warning=" in row.get("error", ""):
            stats["quality_warnings"] += 1

        relative_dir = row.get("article_dir", "").strip()
        article_dir = safe_article_dir(root, relative_dir)
        if article_dir is None:
            errors.append(f"row {row_number} has unsafe article_dir: {relative_dir}")
            continue
        canonical_relative = article_dir.relative_to(root.resolve()).as_posix()
        if canonical_relative != relative_dir:
            errors.append(f"row {row_number} article_dir is not canonical")
        if relative_dir in seen_dirs:
            errors.append(f"row {row_number} duplicates article_dir: {relative_dir}")
        seen_dirs.add(relative_dir)
        if index is not None and not Path(relative_dir).name.startswith(f"{index:02d}-"):
            errors.append(f"row {row_number} article_dir prefix differs from index")
        if not article_dir.is_dir():
            errors.append(f"missing article directory: {relative_dir}")
            continue

        markdown_name = row.get("markdown_file", "").strip()
        if (
            not markdown_name
            or Path(markdown_name).name != markdown_name
            or Path(markdown_name).suffix.lower() != ".md"
        ):
            errors.append(f"row {row_number} has unsafe markdown_file")
            continue

        markdown = (article_dir / markdown_name).resolve()
        if not is_within(markdown, article_dir) or not markdown.is_file():
            errors.append(f"missing Markdown file: {relative_dir}/{markdown_name}")
            continue

        children = list(article_dir.iterdir())
        markdown_files = [path for path in children if path.suffix.lower() == ".md"]
        unexpected = [
            path.name
            for path in children
            if path.name != "images" and path.resolve() != markdown
        ]
        if len(markdown_files) != 1:
            errors.append(f"{relative_dir} must contain exactly one Markdown file")
        if unexpected:
            stats["unexpected_files"] += len(unexpected)
            errors.append(f"{relative_dir} has unexpected entries: {', '.join(unexpected)}")

        if markdown.stem != sanitize_name(row.get("title", "")):
            errors.append(f"{relative_dir} Markdown filename does not match title")

        images_dir = (article_dir / "images").resolve()
        if (
            (article_dir / "images").is_symlink()
            or not is_within(images_dir, article_dir)
            or not images_dir.is_dir()
        ):
            errors.append(f"{relative_dir} is missing images/")

        stats["markdown_files"] += 1
        text = markdown.read_text(encoding="utf-8")
        body_parts = re.split(r"(?m)^---\s*$", text, maxsplit=1)
        if len(body_parts) != 2 or not body_parts[1].strip():
            errors.append(f"{relative_dir} has an empty Markdown body")
        else:
            plain_body = re.sub(r"!\[[^\]]*\]\([^)]*\)|[`#>*_|\-\s]", "", body_parts[1])
            if len(plain_body) < 20:
                stats["short_bodies"] += 1
            for marker in (
                "完成验证后即可继续访问",
                "访问过于频繁",
                "环境异常",
                "此内容因违规无法查看",
                "该内容已被发布者删除",
            ):
                if marker in body_parts[1]:
                    errors.append(f"{relative_dir} contains unavailable-page marker: {marker}")
                    break
        metadata = parse_metadata(text)
        for label, key in META_LABELS.items():
            if key == "biz":
                expected = url_values["biz"]
            else:
                expected = row.get(key, "").strip() or (
                    "未知" if key == "publish_time" else ""
                )
            actual = metadata.get(key, "")
            if not actual:
                errors.append(f"{relative_dir} missing metadata: {label}")
            elif key == "url" and normalize_url(actual) != url:
                errors.append(f"{relative_dir} metadata URL differs from CSV")
            elif key == "source_type":
                pass
            elif key != "url" and expected and actual != expected:
                errors.append(f"{relative_dir} metadata {label} differs from CSV")

        referenced_images: set[Path] = set()
        for raw_ref in markdown_image_refs(text):
            ref = unquote(html.unescape(raw_ref.strip()))
            parsed = urlsplit(ref)
            if parsed.scheme or parsed.netloc:
                errors.append(f"{relative_dir} contains remote image reference: {ref}")
                stats["missing_image_refs"] += 1
                continue
            clean_ref = parsed.path[2:] if parsed.path.startswith("./") else parsed.path
            ref_path = Path(clean_ref)
            image_path = (article_dir / clean_ref).resolve()
            if (
                "\\" in clean_ref
                or ref_path.is_absolute()
                or ".." in ref_path.parts
                or not ref_path.parts
                or ref_path.parts[0] != "images"
                or not is_within(image_path, images_dir)
            ):
                errors.append(f"{relative_dir} contains unsafe image reference: {ref}")
                stats["missing_image_refs"] += 1
            elif not image_path.is_file():
                errors.append(f"{relative_dir} missing referenced image: {ref}")
                stats["missing_image_refs"] += 1
            else:
                referenced_images.add(image_path)

        if images_dir.is_dir():
            actual_images = {path.resolve() for path in images_dir.rglob("*") if path.is_file()}
            for orphan in sorted(actual_images - referenced_images):
                stats["unexpected_files"] += 1
                errors.append(
                    f"{relative_dir} contains unreferenced image: "
                    f"{orphan.relative_to(article_dir)}"
                )

    if indexes and sorted(indexes) != list(range(1, len(rows) + 1)):
        errors.append("CSV indexes must be unique and continuous from 1")
    if len(identities) > 1:
        errors.append("rows contain multiple identity_key values")

    actual_dirs = {
        path.relative_to(root).as_posix()
        for path in articles_root.iterdir()
        if path.is_dir() and not path.is_symlink()
    }
    stats["article_dirs"] = len(actual_dirs)
    for extra in sorted(actual_dirs - seen_dirs):
        errors.append(f"unlisted article directory: {extra}")

    allowed = package_files(root, rows)
    allowed_zip_names = {output_name(root, "archive")}
    for path in root.rglob("*"):
        if path.is_symlink():
            stats["unexpected_files"] += 1
            errors.append(f"symbolic link is not allowed: {path.relative_to(root)}")
            continue
        if not path.is_file():
            continue
        if path.name in allowed_zip_names:
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            stats["unexpected_files"] += 1
            errors.append(f"forbidden file in archive: {path.relative_to(root)}")
        elif path.resolve() not in allowed:
            stats["unexpected_files"] += 1
            errors.append(f"unexpected file in archive: {path.relative_to(root)}")

    return errors, stats


def validate_zip(root: Path, zip_path: Path) -> list[str]:
    if not zip_path.is_file():
        return [f"ZIP not found: {zip_path}"]
    rows, _ = read_article_rows(root)
    expected = expected_archive_entries(root, rows)
    errors: list[str] = []
    try:
        with zipfile.ZipFile(zip_path) as archive:
            file_names = [name for name in archive.namelist() if not name.endswith("/")]
            names = set(file_names)
            if len(file_names) != len(names):
                errors.append("ZIP contains duplicate file entries")
            bad_member = archive.testzip()
            if bad_member:
                errors.append(f"ZIP CRC check failed: {bad_member}")
            missing = sorted(expected - names)
            extra = sorted(names - expected)
            if missing:
                errors.append(f"ZIP is missing {len(missing)} file(s), first: {missing[0]}")
            if extra:
                errors.append(f"ZIP has {len(extra)} unexpected file(s), first: {extra[0]}")
    except zipfile.BadZipFile:
        errors.append("invalid ZIP file")
    return errors


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("author_root", type=Path)
    parser.add_argument("--zip", dest="zip_path", type=Path)
    args = parser.parse_args()
    root = args.author_root.expanduser().resolve()
    errors, stats = validate_archive(root)
    if args.zip_path:
        errors.extend(validate_zip(root, args.zip_path.expanduser().resolve()))
    for key, value in stats.items():
        print(f"{key}: {value}")
    if errors:
        print("validation: failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("validation: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
