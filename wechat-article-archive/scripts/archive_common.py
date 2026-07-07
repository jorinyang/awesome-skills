#!/usr/bin/env python3
"""Shared archive schema, path, and packaging helpers."""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


REQUIRED_COLUMNS = {
    "index",
    "title",
    "url",
    "publish_time",
    "error",
    "author_name",
    "article_dir",
    "markdown_file",
}
CSV_COLUMNS = [
    "index",
    "title",
    "url",
    "publish_time",
    "error",
    "author_name",
    "article_dir",
    "markdown_file",
]
OUTPUT_SUFFIXES = {
    "article_list": "文章清单.csv",
    "methodology_report": "方法论报告.md",
    "copywriting_framework": "文案框架.md",
    "analysis_data": "分析数据.json",
    "article_features": "文章特征.csv",
    "dashboard": "方法论看板.html",
    "lark_sync": "飞书同步.json",
    "competitor_samples": "竞品标题样本.json",
    "archive": "文章归档.zip",
}
OPTIONAL_OUTPUT_KEYS = {
    "methodology_report",
    "copywriting_framework",
    "analysis_data",
    "article_features",
    "dashboard",
    "lark_sync",
    "competitor_samples",
}
FORBIDDEN_NAMES = {".DS_Store", "collection-info.json", "article-candidates.json"}
FORBIDDEN_SUFFIXES = {".log", ".bak", ".tmp", ".part"}
UNSAFE_NAME_RE = re.compile(r'[/\\:*?"<>|\x00-\x1f]')


def sanitize_name(value: str, max_length: int = 100) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    value = UNSAFE_NAME_RE.sub(" ", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    if not value:
        value = "article"
    return value[:max_length].rstrip(" .") or "article"


def author_slug(root: Path) -> str:
    name = root.name
    if name.startswith(".") and ".build-" in name:
        name = name[1:].split(".build-", 1)[0]
    return sanitize_name(name)


def output_name(root: Path, key: str) -> str:
    return f"{author_slug(root)}-{OUTPUT_SUFFIXES[key]}"


def output_path(root: Path, key: str) -> Path:
    return root / output_name(root, key)


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").lower()
    value = re.sub(r"[\s\u3000]+", "", value)
    return re.sub(r"[，。！？、；：,.!?;:'\"“”‘’（）()【】\[\]《》<>_-]+$", "", value)


def normalize_url(value: str) -> str:
    parsed = urlsplit((value or "").strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    query_parts = sorted(
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key not in {"scene", "from", "isappinstalled"}
    )
    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            urlencode(query_parts),
            "",
        )
    )


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def safe_article_dir(root: Path, relative: str) -> Path | None:
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return None
    candidate = (root / relative_path).resolve()
    articles_root = (root / "articles").resolve()
    if candidate == articles_root or not is_within(candidate, articles_root):
        return None
    return candidate


def read_article_rows(root: Path) -> tuple[list[dict[str, str]], set[str]]:
    csv_path = output_path(root, "article_list")
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), set(reader.fieldnames or [])


def package_files(root: Path, rows: list[dict[str, str]]) -> set[Path]:
    files = {output_path(root, "article_list")}
    for key in OPTIONAL_OUTPUT_KEYS:
        path = output_path(root, key)
        if path.is_file():
            files.add(path)

    for row in rows:
        if not row.get("article_dir", "").strip():
            continue
        article_dir = safe_article_dir(root, row.get("article_dir", ""))
        if article_dir is None or not article_dir.is_dir():
            continue
        markdown_file = row.get("markdown_file", "").strip()
        if markdown_file:
            files.add(article_dir / markdown_file)
        images_dir = article_dir / "images"
        if images_dir.is_dir():
            files.update(
                path
                for path in images_dir.rglob("*")
                if path.is_file() and not path.is_symlink()
            )
    return {
        path.resolve()
        for path in files
        if path.is_file() and not path.is_symlink() and is_within(path, root)
    }


def expected_archive_entries(root: Path, rows: list[dict[str, str]]) -> set[str]:
    return {
        f"{root.name}/{path.relative_to(root).as_posix()}"
        for path in package_files(root, rows)
    }
