#!/usr/bin/env python3
"""Fetch public WeChat article URLs into the archive schema."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html as html_module
import json
import mimetypes
import os
import re
import shutil
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit

try:
    import requests
    from lxml import html
except ImportError as exc:
    raise SystemExit(
        "collect_articles.py requires the Python packages requests and lxml"
    ) from exc

from archive_common import CSV_COLUMNS, normalize_url, output_path, sanitize_name


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
)
ARTICLE_HOSTS = {"mp.weixin.qq.com"}
IMAGE_HOSTS = {"mmbiz.qpic.cn", "mmbiz.qlogo.cn", "wx.qlogo.cn"}
RASTER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VARIABLES = {
    "title": ("msg_title",),
    "author_name": ("nickname",),
    "biz": ("biz", "__biz"),
    "mid": ("mid", "appmsgid"),
    "idx": ("idx",),
    "sn": ("sn",),
}
TIME_VARIABLES = (
    "ct",
    "publish_time",
    "create_time",
    "ori_create_time",
    "msg_create_time",
    "appmsg_ct",
)
BLOCK_TAGS = {"p", "div", "section", "article", "main"}
BAD_PAGE_MARKERS = (
    "完成验证后即可继续访问",
    "访问过于频繁",
    "环境异常",
    "此内容因违规无法查看",
    "该内容已被发布者删除",
)


def decode_js_string(value: str) -> str:
    value = html_module.unescape(value.strip())
    try:
        return json.loads(f'"{value}"')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return value.replace("\\x26", "&").replace("\\/", "/")


def script_value(source: str, names: tuple[str, ...]) -> str:
    for name in names:
        patterns = (
            rf'(?:var\s+)?{re.escape(name)}\s*=\s*"((?:\\.|[^"\\])*)"',
            rf"(?:var\s+)?{re.escape(name)}\s*=\s*'((?:\\.|[^'\\])*)'",
            rf'["\']{re.escape(name)}["\']\s*:\s*"((?:\\.|[^"\\])*)"',
            rf'["\']{re.escape(name)}["\']\s*:\s*\'((?:\\.|[^\'\\])*)\'',
            rf"(?:var\s+)?{re.escape(name)}\s*=\s*(\d+)\s*;",
        )
        for pattern in patterns:
            match = re.search(pattern, source, re.S)
            if match:
                return decode_js_string(match.group(1)).strip()
    return ""


def first_text(tree: html.HtmlElement, expressions: tuple[str, ...]) -> str:
    for expression in expressions:
        values = tree.xpath(expression)
        for value in values:
            text = value if isinstance(value, str) else value.text_content()
            text = re.sub(r"\s+", " ", text or "").strip()
            if text:
                return text
    return ""


def parse_timestamp(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if value.isdigit():
        number = int(value)
        if number > 10_000_000_000:
            number //= 1000
        try:
            return datetime.fromtimestamp(number).strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError, OverflowError):
            return ""
    match = re.search(r"20\d{2}[-/.年]\d{1,2}[-/.月]\d{1,2}(?:日)?(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?", value)
    if not match:
        return ""
    normalized = (
        match.group(0)
        .replace("年", "-")
        .replace("月", "-")
        .replace("日", "")
        .replace("/", "-")
        .replace(".", "-")
    )
    return normalized


def url_identifiers(url: str) -> dict[str, str]:
    query = parse_qs(urlsplit(url).query)
    return {
        "biz": (query.get("__biz") or query.get("biz") or [""])[0],
        "mid": (query.get("mid") or query.get("appmsgid") or [""])[0],
        "idx": (query.get("idx") or [""])[0],
        "sn": (query.get("sn") or [""])[0],
    }


def parse_article(source: str, url: str) -> dict[str, object]:
    tree = html.fromstring(source)
    title = first_text(
        tree,
        (
            "//*[@id='activity-name']",
            "//meta[@property='og:title']/@content",
            "//title",
        ),
    ) or script_value(source, VARIABLES["title"])
    author = first_text(
        tree,
        (
            "//*[@id='js_name']",
            "//meta[@name='author']/@content",
        ),
    ) or script_value(source, VARIABLES["author_name"])
    identifiers = url_identifiers(url)
    for key in ("biz", "mid", "idx", "sn"):
        identifiers[key] = identifiers[key] or script_value(source, VARIABLES[key])

    publish_time = first_text(
        tree,
        (
            "//*[@id='publish_time']",
            "//*[contains(@class,'rich_media_meta_text')]",
        ),
    )
    time_confidence = "high" if parse_timestamp(publish_time) else "unknown"
    publish_time = parse_timestamp(publish_time)
    if not publish_time:
        for name in TIME_VARIABLES:
            publish_time = parse_timestamp(script_value(source, (name,)))
            if publish_time:
                time_confidence = "high"
                break

    body_nodes = tree.xpath("//*[@id='js_content']")
    if not body_nodes:
        body_nodes = tree.xpath("//*[contains(@class,'rich_media_content')]")
    if not body_nodes:
        raise ValueError("article body not found")

    links: list[str] = []
    for href in tree.xpath("//a/@href"):
        candidate = normalize_url(urljoin(url, html_module.unescape(href)))
        if candidate and urlsplit(candidate).hostname == "mp.weixin.qq.com":
            links.append(candidate)

    return {
        "title": title or "",
        "author_name": author or "",
        "publish_time": publish_time or "未知",
        "time_confidence": time_confidence,
        "body": body_nodes[0],
        "links": list(dict.fromkeys(links)),
        **identifiers,
    }


def cache_key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def retry_request(
    url: str,
    *,
    headers: dict[str, str],
    timeout: int,
    retries: int,
    limit: int,
) -> tuple[bytes, str, str]:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with requests.get(
                url,
                headers=headers,
                timeout=timeout,
                stream=True,
                allow_redirects=True,
            ) as response:
                response.raise_for_status()
                content = read_limited(response, limit)
                return (
                    content,
                    response.url,
                    response.headers.get("content-type", ""),
                )
        except (requests.RequestException, OSError, ValueError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2**attempt, 8))
    raise RuntimeError(f"request failed after {retries + 1} attempt(s): {last_error}")


def fetch_html(
    url: str, timeout: int, retries: int, cache_dir: Path | None
) -> str:
    host = (urlsplit(url).hostname or "").lower()
    if host not in ARTICLE_HOSTS:
        raise ValueError(f"unsupported article host: {host}")
    cache_path = cache_dir / "html" / f"{cache_key(url)}.html" if cache_dir else None
    if cache_path and cache_path.is_file():
        source = cache_path.read_text(encoding="utf-8", errors="replace")
        if not any(marker in source for marker in BAD_PAGE_MARKERS):
            return source
    content, final_url, _ = retry_request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "zh-CN,zh;q=0.9"},
        timeout=timeout,
        retries=retries,
        limit=10 * 1024 * 1024,
    )
    if (urlsplit(final_url).hostname or "").lower() not in ARTICLE_HOSTS:
        raise ValueError("article redirected to an unsupported host")
    source = content.decode("utf-8", errors="replace")
    marker = next((item for item in BAD_PAGE_MARKERS if item in source), "")
    if marker:
        raise ValueError(f"article returned an unavailable page: {marker}")
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(source, encoding="utf-8")
    return source


def read_limited(response: requests.Response, limit: int) -> bytes:
    chunks: list[bytes] = []
    size = 0
    for chunk in response.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue
        size += len(chunk)
        if size > limit:
            raise ValueError(f"response exceeds {limit} bytes")
        chunks.append(chunk)
    return b"".join(chunks)


def image_extension(url: str, content_type: str) -> str:
    extension = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ""
    if extension == ".jpe":
        extension = ".jpg"
    if extension in RASTER_EXTENSIONS:
        return extension
    suffix = Path(urlsplit(url).path).suffix.lower()
    return suffix if suffix in RASTER_EXTENSIONS else ".jpg"


def download_image(
    remote: str,
    article_url: str,
    timeout: int,
    retries: int,
    cache_dir: Path | None,
) -> tuple[bytes, str]:
    key = cache_key(remote)
    cache_parent = cache_dir / "images" if cache_dir else None
    if cache_parent:
        matches = list(cache_parent.glob(f"{key}.*"))
        if matches:
            return matches[0].read_bytes(), matches[0].suffix
    content, final_url, content_type = retry_request(
        remote,
        headers={"User-Agent": USER_AGENT, "Referer": article_url},
        timeout=timeout,
        retries=retries,
        limit=20 * 1024 * 1024,
    )
    final_host = (urlsplit(final_url).hostname or "").lower()
    if final_host not in IMAGE_HOSTS or not content_type.lower().startswith("image/"):
        raise ValueError("image redirected or returned non-image content")
    extension = image_extension(final_url, content_type)
    if cache_parent:
        cache_parent.mkdir(parents=True, exist_ok=True)
        (cache_parent / f"{key}{extension}").write_bytes(content)
    return content, extension


def localize_images(
    body: html.HtmlElement,
    article_url: str,
    images_dir: Path,
    timeout: int,
    retries: int,
    image_workers: int,
    cache_dir: Path | None,
) -> int:
    images_dir.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[int, html.HtmlElement, str]] = []
    failures = 0
    for number, node in enumerate(body.xpath(".//img"), start=1):
        remote = (
            node.get("data-src")
            or node.get("data-original")
            or node.get("src")
            or ""
        ).strip()
        remote = urljoin(article_url, html_module.unescape(remote))
        host = (urlsplit(remote).hostname or "").lower()
        if urlsplit(remote).scheme not in {"http", "https"} or host not in IMAGE_HOSTS:
            node.drop_tree()
            failures += 1
            continue
        jobs.append((number, node, remote))

    results: dict[str, tuple[bytes, str] | Exception] = {}
    remotes = list(dict.fromkeys(remote for _, _, remote in jobs))
    with ThreadPoolExecutor(max_workers=max(1, min(image_workers, 16))) as pool:
        future_map = {
            pool.submit(
                download_image,
                remote,
                article_url,
                timeout,
                retries,
                cache_dir,
            ): remote
            for remote in remotes
        }
        for future in as_completed(future_map):
            remote = future_map[future]
            try:
                results[remote] = future.result()
            except Exception as exc:
                results[remote] = exc

    for number, node, remote in jobs:
        result = results[remote]
        if isinstance(result, Exception):
            node.drop_tree()
            failures += 1
        else:
            content, extension = result
            name = f"image-{number:02d}{extension}"
            (images_dir / name).write_bytes(content)
            node.set("data-local-path", f"images/{name}")
    return failures


def inline_markdown(node: html.HtmlElement) -> str:
    tag = (node.tag or "").lower() if isinstance(node.tag, str) else ""
    if tag == "img":
        local = node.get("data-local-path", "")
        alt = re.sub(r"\s+", " ", node.get("alt", "")).strip()
        return f"![{alt}]({local})" if local else ""
    content = node.text or ""
    for child in node:
        content += element_markdown(child)
        content += child.tail or ""
    content = re.sub(r"[ \t]+", " ", content)
    if tag in {"strong", "b"} and content.strip():
        return f"**{content.strip()}**"
    if tag in {"em", "i"} and content.strip():
        return f"*{content.strip()}*"
    if tag == "a":
        href = html_module.unescape(node.get("href", "")).strip()
        label = content.strip()
        return f"[{label}]({href})" if href and label else label
    if tag == "code" and content.strip():
        escaped = content.strip().replace("`", "\\`")
        return f"`{escaped}`"
    if tag == "br":
        return "\n"
    return content


def element_markdown(node: html.HtmlElement) -> str:
    tag = (node.tag or "").lower() if isinstance(node.tag, str) else ""
    if tag in {"script", "style", "noscript"}:
        return ""
    if tag == "img":
        return inline_markdown(node)
    if re.fullmatch(r"h[1-6]", tag):
        return f"\n{'#' * int(tag[1])} {inline_markdown(node).strip()}\n\n"
    if tag == "blockquote":
        text = inline_markdown(node).strip().replace("\n", "\n> ")
        return f"\n> {text}\n\n" if text else ""
    if tag == "pre":
        text = node.text_content().strip()
        return f"\n```\n{text}\n```\n\n" if text else ""
    if tag == "table":
        rows = []
        for row in node.xpath(".//tr"):
            cells = [
                re.sub(r"\s+", " ", cell.text_content()).strip().replace("|", "\\|")
                for cell in row.xpath("./th|./td")
            ]
            if cells:
                rows.append(cells)
        if not rows:
            return ""
        width = max(len(row) for row in rows)
        rows = [row + [""] * (width - len(row)) for row in rows]
        lines = [
            "| " + " | ".join(rows[0]) + " |",
            "| " + " | ".join(["---"] * width) + " |",
        ]
        lines.extend("| " + " | ".join(row) + " |" for row in rows[1:])
        return "\n" + "\n".join(lines) + "\n\n"
    if tag in {"video", "audio", "iframe"}:
        source = node.get("src", "") or first_text(node, (".//source/@src",))
        source = html_module.unescape(source).strip()
        label = {"video": "视频", "audio": "音频", "iframe": "嵌入内容"}[tag]
        return f"\n[{label}]({source})\n\n" if source else f"\n[{label}未能本地化]\n\n"
    if tag == "li":
        text = inline_markdown(node).strip()
        return f"\n- {text}" if text else ""
    content = inline_markdown(node)
    if tag in BLOCK_TAGS or tag in {"ul", "ol"}:
        return f"\n{content.strip()}\n\n" if content.strip() else ""
    return content


def body_to_markdown(body: html.HtmlElement) -> str:
    result = (body.text or "") + "".join(
        element_markdown(child) + (child.tail or "") for child in body
    )
    result = re.sub(r"[ \t]+\n", "\n", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def remove_unreferenced_images(images_dir: Path, markdown: str) -> None:
    referenced = {
        Path(match).name
        for match in re.findall(r"!\[[^\]]*\]\((images/[^)\s]+)\)", markdown)
    }
    for path in images_dir.iterdir():
        if path.is_file() and path.name not in referenced:
            path.unlink()


def fetch_candidate(
    candidate: dict[str, str],
    timeout: int,
    retries: int,
    cache_dir: Path | None,
) -> dict[str, object]:
    url = normalize_url(candidate.get("url", ""))
    if not url:
        raise ValueError("invalid URL")
    source = fetch_html(url, timeout, retries, cache_dir)
    parsed = parse_article(source, url)
    if not str(parsed["title"]).strip():
        raise ValueError("article title not found")
    if not str(parsed["author_name"]).strip():
        raise ValueError("article author not found")
    parsed.update(
        {
            "url": url,
            "source_type": candidate.get("source_type", "provided"),
            "identity_key": candidate.get("identity_key", ""),
            "candidate_biz": candidate.get("biz", ""),
        }
    )
    if candidate.get("publish_time") and parsed["publish_time"] == "未知":
        parsed["publish_time"] = candidate["publish_time"]
        parsed["time_confidence"] = candidate.get("time_confidence") or "medium"
    return parsed


def fetch_candidates(
    candidates: list[dict[str, str]],
    *,
    workers: int,
    article_delay: float,
    timeout: int,
    retries: int,
    cache_dir: Path | None,
) -> tuple[list[dict[str, object]], list[tuple[dict[str, str], str]]]:
    fetched: list[dict[str, object]] = []
    failures: list[tuple[dict[str, str], str]] = []
    if workers == 1:
        for index, candidate in enumerate(candidates):
            try:
                fetched.append(fetch_candidate(candidate, timeout, retries, cache_dir))
            except Exception as exc:
                failures.append((candidate, str(exc)))
            if article_delay and index < len(candidates) - 1:
                time.sleep(article_delay)
        return fetched, failures

    with ThreadPoolExecutor(max_workers=max(1, min(workers, 4))) as pool:
        future_map = {}
        for index, candidate in enumerate(candidates):
            future_map[
                pool.submit(fetch_candidate, candidate, timeout, retries, cache_dir)
            ] = candidate
            if article_delay and index < len(candidates) - 1:
                time.sleep(article_delay)
        for future in as_completed(future_map):
            candidate = future_map[future]
            try:
                fetched.append(future.result())
            except Exception as exc:
                failures.append((candidate, str(exc)))
    return fetched, failures


def read_candidates(path: Path | None, urls: list[str]) -> list[dict[str, str]]:
    candidates = [{"url": url, "source_type": "provided"} for url in urls]
    if path:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            candidates.extend(dict(row) for row in csv.DictReader(handle))
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for candidate in candidates:
        normalized = normalize_url(candidate.get("url", ""))
        if normalized and normalized not in seen:
            seen.add(normalized)
            candidate["url"] = normalized
            result.append(candidate)
    return result


def sortable_time(value: object) -> tuple[int, str]:
    text = str(value or "")
    return (0 if text == "未知" else 1, text)


def load_existing_articles(root: Path) -> dict[str, dict[str, object]]:
    csv_path = output_path(root, "article_list")
    if not csv_path.is_file():
        return {}
    existing: dict[str, dict[str, object]] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if not row.get("article_dir", "").strip():
                continue
            url = normalize_url(row.get("url", ""))
            article_dir = root / row.get("article_dir", "")
            markdown = article_dir / row.get("markdown_file", "")
            images_dir = article_dir / "images"
            if not url or not markdown.is_file() or not images_dir.is_dir():
                continue
            text = markdown.read_text(encoding="utf-8")
            parts = re.split(r"(?m)^---\s*$", text, maxsplit=1)
            if len(parts) != 2:
                continue
            identifiers = url_identifiers(url)
            existing[url] = {
                "title": row.get("title", ""),
                "author_name": row.get("author_name", ""),
                "publish_time": row.get("publish_time", "未知") or "未知",
                "time_confidence": (
                    "unknown"
                    if row.get("publish_time", "").strip() in {"", "未知"}
                    else "high"
                ),
                "url": url,
                "source_type": "existing_archive",
                "identity_key": (
                    f"biz:{identifiers['biz']}" if identifiers["biz"] else ""
                ),
                "biz": identifiers["biz"],
                "mid": identifiers["mid"],
                "idx": identifiers["idx"],
                "sn": identifiers["sn"],
                "links": [],
                "existing_body": parts[1].strip(),
                "existing_images": images_dir,
            }
    return existing


def content_quality_warning(body: html.HtmlElement, markdown: str) -> str:
    source_text = re.sub(r"\s+", "", body.text_content())
    markdown_text = re.sub(r"!\[[^\]]*\]\([^)]*\)|[`#>*_|\-\s]", "", markdown)
    warnings: list[str] = []
    if len(source_text) >= 100 and len(markdown_text) < max(40, len(source_text) // 5):
        warnings.append("low_text_retention")
    if len(markdown_text) < 20:
        warnings.append("very_short_body")
    return ",".join(warnings)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="*")
    parser.add_argument("--candidate-csv", type=Path)
    parser.add_argument("--author-root", required=True, type=Path)
    parser.add_argument("--discover-links", action="store_true")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--image-workers", type=int, default=2)
    parser.add_argument("--article-delay", type=float, default=2.0)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path.home() / ".cache/wechat-article-archive/content",
    )
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--timeline-complete", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    if (
        args.limit < 1
        or args.timeout < 1
        or args.workers < 1
        or args.image_workers < 1
        or args.article_delay < 0
        or args.retries < 0
    ):
        print(
            "limits, timeouts and workers must be positive; "
            "retries and article-delay cannot be negative",
            file=sys.stderr,
        )
        return 2

    requested_root = args.author_root.expanduser().absolute()
    if requested_root.is_symlink():
        print("author_root must not be a symbolic link", file=sys.stderr)
        return 2
    root = requested_root.resolve()
    if root.exists() and any(root.iterdir()) and not (args.replace or args.resume):
        print("archive exists; use --resume to reuse it or --replace to rebuild", file=sys.stderr)
        return 2
    cache_dir = None if args.no_cache else args.cache_dir.expanduser().resolve()
    existing = load_existing_articles(root) if args.resume and root.exists() else {}
    candidates = read_candidates(args.candidate_csv, args.urls)
    if not candidates:
        print("no valid candidate URLs", file=sys.stderr)
        return 2

    fetched: list[dict[str, object]] = []
    failures: list[tuple[dict[str, str], str]] = []
    pending_candidates: list[dict[str, str]] = []
    for candidate in candidates:
        existing_item = existing.get(candidate["url"])
        if existing_item:
            reused = dict(existing_item)
            reused["source_type"] = candidate.get("source_type") or reused["source_type"]
            if candidate.get("publish_time"):
                reused["publish_time"] = candidate["publish_time"]
                reused["time_confidence"] = candidate.get("time_confidence") or "medium"
            for key in ("biz", "mid", "idx", "sn"):
                if candidate.get(key):
                    reused[key] = candidate[key]
            if candidate.get("identity_key"):
                reused["identity_key"] = candidate["identity_key"]
            fetched.append(reused)
        else:
            pending_candidates.append(candidate)
    newly_fetched, new_failures = fetch_candidates(
        pending_candidates,
        workers=args.workers,
        article_delay=args.article_delay,
        timeout=args.timeout,
        retries=args.retries,
        cache_dir=cache_dir,
    )
    fetched.extend(newly_fetched)
    failures.extend(new_failures)

    if args.discover_links:
        known = {item["url"] for item in fetched}
        discovered = [
            {"url": link, "source_type": "explicit_link"}
            for item in fetched
            for link in item["links"]
            if link not in known
        ][: max(args.limit * 2, args.limit)]
        discovered_items, discovered_failures = fetch_candidates(
            discovered,
            workers=args.workers,
            article_delay=args.article_delay,
            timeout=args.timeout,
            retries=args.retries,
            cache_dir=cache_dir,
        )
        for item in discovered_items:
            if item["url"] not in known:
                known.add(item["url"])
                fetched.append(item)
        failures.extend(discovered_failures)

    if not fetched:
        print("no articles could be fetched", file=sys.stderr)
        return 1
    identity_values = {
        str(item["biz"]).strip()
        or str(item["identity_key"]).strip().split(":", 1)[-1]
        for item in fetched
    }
    if (
        "" in {str(item["author_name"]).strip() for item in fetched}
        or "" in identity_values
        or len(identity_values) != 1
    ):
        print("articles do not resolve to one stable author identity", file=sys.stderr)
        return 1
    identity_value = next(iter(identity_values))
    identity_key = (
        f"biz:{identity_value}"
        if any(str(item["biz"]).strip() for item in fetched)
        else f"fakeid:{identity_value}"
    )

    fetched.sort(key=lambda item: sortable_time(item["publish_time"]), reverse=True)
    unique_fetched: list[dict[str, object]] = []
    seen_article_keys: set[tuple[str, str, str]] = set()
    seen_urls: set[str] = set()
    for item in fetched:
        url_key = normalize_url(str(item["url"]))
        article_key = (str(item["biz"]), str(item["mid"]), str(item["idx"]))
        if url_key in seen_urls or (all(article_key) and article_key in seen_article_keys):
            continue
        seen_urls.add(url_key)
        if all(article_key):
            seen_article_keys.add(article_key)
        unique_fetched.append(item)
    fetched = unique_fetched[: args.limit]
    verified_failures: list[tuple[dict[str, str], str, dict[str, str]]] = []
    identity_aliases = {identity_key}
    identity_aliases.update(
        str(item.get("identity_key", "")).strip()
        for item in fetched
        if str(item.get("identity_key", "")).strip()
    )
    for candidate, error in sorted(failures, key=lambda item: item[0].get("url", "")):
        identifiers = url_identifiers(candidate.get("url", ""))
        candidate_biz = candidate.get("biz", "").strip() or identifiers["biz"]
        candidate_key = (
            f"biz:{candidate_biz}"
            if candidate_biz
            else candidate.get("identity_key", "").strip()
        )
        if candidate_key in identity_aliases:
            identifiers["biz"] = candidate_biz
            verified_failures.append((candidate, error, identifiers))
        else:
            print(
                f"skipped unverified failed candidate: {candidate.get('url', '')}",
                file=sys.stderr,
            )
    timeline_complete = (
        args.timeline_complete
        and not verified_failures
        and all(item["publish_time"] != "未知" for item in fetched)
    )
    if args.timeline_complete and not timeline_complete:
        print(
            "timeline_complete downgraded to false because times or fetches are incomplete",
            file=sys.stderr,
        )

    root.parent.mkdir(parents=True, exist_ok=True)
    build_root = Path(
        tempfile.mkdtemp(prefix=f".{root.name}.build-", dir=str(root.parent))
    )
    articles_root = build_root / "articles"
    articles_root.mkdir(parents=True)

    try:
        rows: list[dict[str, str]] = []
        for index, item in enumerate(fetched, start=1):
            title = sanitize_name(str(item["title"]))
            directory_name = f"{index:02d}-{title}"
            article_dir = articles_root / directory_name
            images_dir = article_dir / "images"
            article_dir.mkdir(parents=True, exist_ok=False)
            quality_warning = ""
            if item.get("existing_body") is not None:
                shutil.copytree(item["existing_images"], images_dir)
                markdown_body = str(item["existing_body"]).strip()
                image_failures = 0
            else:
                image_failures = localize_images(
                    item["body"],
                    str(item["url"]),
                    images_dir,
                    args.timeout,
                    args.retries,
                    args.image_workers,
                    cache_dir,
                )
                markdown_body = body_to_markdown(item["body"])
                remove_unreferenced_images(images_dir, markdown_body)
                quality_warning = content_quality_warning(item["body"], markdown_body)
            markdown_name = f"{title}.md"
            metadata_biz = str(item["biz"]) or "未知"
            markdown = (
                f"# {item['title']}\n\n"
                f"- 公众号：{item['author_name']}\n"
                f"- 公众号标识：{metadata_biz}\n"
                f"- 原文链接：{item['url']}\n"
                f"- 发布时间：{item['publish_time']}\n"
                f"- 采集来源：{item['source_type']}\n\n"
                "---\n\n"
                f"{markdown_body}\n"
            )
            (article_dir / markdown_name).write_text(markdown, encoding="utf-8")
            rows.append(
                {
                    "index": str(index),
                    "title": str(item["title"]).strip(),
                    "url": str(item["url"]),
                    "publish_time": str(item["publish_time"]),
                    "time_confidence": str(item["time_confidence"]),
                    "timeline_complete": str(timeline_complete).lower(),
                    "source_type": str(item["source_type"]),
                    "status": "archived",
                    "error": ";".join(
                        part
                        for part in (
                            f"image_failures={image_failures}" if image_failures else "",
                            f"quality_warning={quality_warning}" if quality_warning else "",
                        )
                        if part
                    ),
                    "author_name": str(item["author_name"]),
                    "identity_key": identity_key,
                    "biz": str(item["biz"]),
                    "mid": str(item["mid"]),
                    "idx": str(item["idx"]),
                    "sn": str(item["sn"]),
                    "article_dir": f"articles/{directory_name}",
                    "markdown_file": markdown_name,
                }
            )

        next_index = len(rows) + 1
        for candidate, error, identifiers in verified_failures:
            rows.append(
                {
                    "index": str(next_index),
                    "title": candidate.get("title", ""),
                    "url": candidate.get("url", ""),
                    "publish_time": candidate.get("publish_time", "未知") or "未知",
                    "time_confidence": candidate.get("time_confidence", "unknown") or "unknown",
                    "timeline_complete": "false",
                    "source_type": candidate.get("source_type", "provided"),
                    "status": "failed",
                    "error": error[:500],
                    "author_name": str(fetched[0]["author_name"]),
                    "identity_key": identity_key,
                    "biz": identifiers["biz"],
                    "mid": identifiers["mid"],
                    "idx": identifiers["idx"],
                    "sn": identifiers["sn"],
                    "article_dir": "",
                    "markdown_file": "",
                }
            )
            next_index += 1

        with output_path(build_root, "article_list").open(
            "w", encoding="utf-8-sig", newline=""
        ) as handle:
            writer = csv.DictWriter(
                handle, fieldnames=CSV_COLUMNS, extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(rows)

        from validate_archive import validate_archive

        validation_errors, _ = validate_archive(build_root)
        if validation_errors:
            raise ValueError("build validation failed: " + "; ".join(validation_errors))
        if root.exists():
            backup = root.parent / f".{root.name}.backup-{os.getpid()}"
            shutil.rmtree(backup, ignore_errors=True)
            root.rename(backup)
            try:
                build_root.rename(root)
            except Exception:
                backup.rename(root)
                raise
            shutil.rmtree(backup)
        else:
            build_root.rename(root)
        print(root)
        return 0
    except Exception as exc:
        shutil.rmtree(build_root, ignore_errors=True)
        print(f"collection failed without replacing existing archive: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
