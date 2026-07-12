#!/usr/bin/env python3
"""Discover a public account's recent article URLs through WeChat MP dashboard."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import uuid
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

try:
    import requests
except ImportError as exc:
    raise SystemExit(
        "discover_account_articles.py requires the Python package requests"
    ) from exc


BASE = "https://mp.weixin.qq.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
    ),
    "Referer": f"{BASE}/",
    "Origin": BASE,
    "Accept-Encoding": "identity",
}
CSV_COLUMNS = [
    "title",
    "url",
    "publish_time",
    "time_confidence",
    "source_type",
    "identity_key",
    "biz",
    "mid",
    "idx",
    "sn",
]


class AuthError(RuntimeError):
    pass


def load_session(path: Path) -> tuple[str, str] | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    token = str(data.get("token", "")).strip()
    cookie = str(data.get("cookie", "")).strip()
    return (token, cookie) if token and cookie else None


def save_session(path: Path, token: str, session: requests.Session) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cookie = "; ".join(f"{item.name}={item.value}" for item in session.cookies)
    path.write_text(
        json.dumps({"token": token, "cookie": cookie}, ensure_ascii=False),
        encoding="utf-8",
    )
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def qr_login(qr_path: Path, timeout: int) -> tuple[str, str]:
    session = requests.Session()
    session.headers.update(HEADERS)
    session.get(f"{BASE}/", timeout=20)
    response = session.post(
        f"{BASE}/cgi-bin/bizlogin",
        params={"action": "startlogin"},
        data={
            "userlang": "zh_CN",
            "redirect_url": "",
            "login_type": 3,
            "sessionid": uuid.uuid4().hex,
            "token": "",
            "lang": "zh_CN",
            "f": "json",
            "ajax": 1,
        },
        timeout=20,
    )
    data = response.json()
    if (data.get("base_resp") or {}).get("ret") not in (0, None):
        raise AuthError(f"startlogin failed: {data}")
    if not session.cookies.get("uuid"):
        raise AuthError("startlogin did not return a uuid cookie")

    response = session.get(
        f"{BASE}/cgi-bin/scanloginqrcode",
        params={"action": "getqrcode", "random": int(time.time() * 1000)},
        timeout=20,
    )
    response.raise_for_status()
    if not response.content.startswith((b"\xff\xd8\xff", b"\x89PNG", b"GIF8")):
        raise AuthError("QR endpoint did not return an image")
    qr_path.parent.mkdir(parents=True, exist_ok=True)
    qr_path.write_bytes(response.content)
    print(f"Scan and confirm the QR code: {qr_path}", file=sys.stderr)
    try:
        webbrowser.open(qr_path.resolve().as_uri())
    except Exception:
        pass

    deadline = time.time() + timeout
    while time.time() < deadline:
        result = session.get(
            f"{BASE}/cgi-bin/scanloginqrcode",
            params={"action": "ask", "lang": "zh_CN", "f": "json", "ajax": 1},
            timeout=20,
        ).json()
        if result.get("status") == 1:
            break
        time.sleep(2)
    else:
        raise AuthError(f"QR login timed out after {timeout} seconds")

    result = session.post(
        f"{BASE}/cgi-bin/bizlogin",
        params={"action": "login"},
        data={
            "userlang": "zh_CN",
            "redirect_url": "",
            "cookie_forbidden": 0,
            "cookie_cleaned": 0,
            "plugin_used": 0,
            "login_type": 3,
            "token": "",
            "lang": "zh_CN",
            "f": "json",
            "ajax": 1,
        },
        timeout=20,
    ).json()
    match = re.search(r"[?&]token=(\d+)", result.get("redirect_url", ""))
    if not match:
        raise AuthError(f"login did not return a token: {result}")
    token = match.group(1)
    cookie = "; ".join(f"{item.name}={item.value}" for item in session.cookies)
    return token, cookie


class DashboardClient:
    def __init__(self, token: str, cookie: str, timeout: int, retries: int):
        self.token = token
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({**HEADERS, "Cookie": cookie})

    def get(self, path: str, params: dict[str, object]) -> dict:
        params.update(
            {"token": self.token, "lang": "zh_CN", "f": "json", "ajax": 1}
        )
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.get(
                    f"{BASE}{path}", params=params, timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                ret = (data.get("base_resp") or {}).get("ret")
                if ret == 200003:
                    raise AuthError("dashboard session expired")
                if ret not in (0, None):
                    raise RuntimeError(f"WeChat API returned ret={ret}: {data}")
                return data
            except AuthError:
                raise
            except (requests.RequestException, ValueError, RuntimeError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(min(2**attempt, 8))
        raise RuntimeError(
            f"WeChat API failed after {self.retries + 1} attempt(s): {last_error}"
        )

    def search_accounts(self, query: str) -> list[dict]:
        data = self.get(
            "/cgi-bin/searchbiz",
            {
                "action": "search_biz",
                "begin": 0,
                "count": 10,
                "query": query,
            },
        )
        return data.get("list", []) or []

    def list_articles(self, fakeid: str, begin: int, count: int) -> tuple[list[dict], int, int]:
        data = self.get(
            "/cgi-bin/appmsgpublish",
            {
                "sub": "list",
                "sub_action": "list_ex",
                "type": "101_1",
                "free_publish_type": 1,
                "fakeid": fakeid,
                "begin": begin,
                "count": count,
                "query": "",
            },
        )
        page = json.loads(data.get("publish_page") or "{}")
        articles: list[dict] = []
        publications = page.get("publish_list", []) or []
        for publication in publications:
            info = json.loads(publication.get("publish_info") or "{}")
            articles.extend(info.get("appmsgex", []) or [])
        return articles, len(publications), int(page.get("total_count", 0))


def choose_account(accounts: list[dict], query: str, fakeid: str) -> dict:
    if fakeid:
        matches = [item for item in accounts if item.get("fakeid") == fakeid]
    else:
        matches = [
            item
            for item in accounts
            if str(item.get("nickname", "")).strip() == query.strip()
        ]
    if len(matches) == 1:
        return matches[0]
    options = ", ".join(
        f"{item.get('nickname', 'unknown')} ({item.get('fakeid', 'no fakeid')})"
        for item in accounts
    )
    raise ValueError(
        "account is ambiguous or not found; rerun with --fakeid. "
        f"Search results: {options or 'none'}"
    )


def article_identifiers(article: dict) -> dict[str, str]:
    query = parse_qs(urlsplit(str(article.get("link", ""))).query)
    return {
        "biz": (query.get("__biz") or query.get("biz") or [""])[0],
        "mid": (
            query.get("mid")
            or query.get("appmsgid")
            or [str(article.get("appmsgid") or article.get("aid") or "")]
        )[0],
        "idx": (query.get("idx") or [str(article.get("idx") or "")])[0],
        "sn": (query.get("sn") or [str(article.get("sn") or "")])[0],
    }


def collect_recent(
    client: DashboardClient, fakeid: str, limit: int, delay: float
) -> tuple[list[dict], bool]:
    begin = 0
    page_size = min(20, limit)
    articles: list[dict] = []
    total = 0
    while len(articles) < limit:
        batch, publication_count, total = client.list_articles(
            fakeid, begin, page_size
        )
        if not batch:
            break
        articles.extend(batch)
        begin += publication_count
        if publication_count == 0 or begin >= total:
            break
        time.sleep(delay)

    unique: list[dict] = []
    seen: set[str] = set()
    for article in sorted(
        articles, key=lambda item: int(item.get("create_time") or 0), reverse=True
    ):
        url = str(article.get("link", "")).strip()
        if url and url not in seen:
            seen.add(url)
            unique.append(article)
    return unique[:limit], len(unique) >= min(limit, total)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", required=True, help="Exact public account name")
    parser.add_argument("--fakeid", default="", help="Disambiguate account search")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--session",
        type=Path,
        default=Path.home() / ".cache/wechat-article-archive/session.json",
    )
    parser.add_argument("--qr-path", type=Path, default=Path("wechat-login-qr.jpg"))
    parser.add_argument("--login-timeout", type=int, default=180)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--page-delay", type=float, default=1.0)
    args = parser.parse_args()
    if args.limit < 1 or args.timeout < 1 or args.page_delay < 0 or args.retries < 0:
        print(
            "limit and timeout must be positive; retries and page-delay cannot be negative",
            file=sys.stderr,
        )
        return 2

    session_data = load_session(args.session)
    if session_data is None:
        token, cookie = qr_login(args.qr_path, args.login_timeout)
        cookie_session = requests.Session()
        for part in cookie.split("; "):
            if "=" in part:
                name, value = part.split("=", 1)
                cookie_session.cookies.set(name, value)
        save_session(args.session, token, cookie_session)
    else:
        token, cookie = session_data

    client = DashboardClient(token, cookie, args.timeout, args.retries)
    try:
        account = choose_account(
            client.search_accounts(args.account), args.account, args.fakeid
        )
        fakeid = str(account.get("fakeid", "")).strip()
        articles, timeline_complete = collect_recent(
            client, fakeid, args.limit, args.page_delay
        )
    except AuthError:
        args.session.unlink(missing_ok=True)
        print("dashboard session expired; removed it, rerun to scan a new QR code", file=sys.stderr)
        return 1
    if not articles:
        print("no published articles found", file=sys.stderr)
        return 1

    rows: list[dict[str, str]] = []
    for article in articles:
        timestamp = int(article.get("create_time") or 0)
        publish_time = (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
            if timestamp
            else ""
        )
        identifiers = article_identifiers(article)
        biz = identifiers["biz"]
        rows.append(
            {
                "title": str(article.get("title", "")).strip(),
                "url": str(article.get("link", "")).strip(),
                "publish_time": publish_time,
                "time_confidence": "high" if publish_time else "unknown",
                "source_type": "wechat_dashboard_history",
                "identity_key": f"biz:{biz}" if biz else f"fakeid:{fakeid}",
                **identifiers,
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(
        json.dumps(
            {
                "account": account.get("nickname", args.account),
                "fakeid": fakeid,
                "articles": len(rows),
                "requested": args.limit,
                "timeline_complete": timeline_complete,
                "candidate_csv": str(args.output.resolve()),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
