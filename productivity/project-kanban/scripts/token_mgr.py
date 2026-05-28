#!/usr/bin/env python3
"""Token manager for Feishu APIs — shared across kanban/calendar/task."""

import json
import os
import time
import urllib.request

CRED = {
    "app_id": "cli_aa9ead14c2641cc3",
    "app_secret": "ZUUm7yI7HmfLi42ki8fPTgZzbj2AuTeM",
}
CACHE_FILE = os.path.expanduser("~/.hermes-feishu/cache/feishu_token.json")
TTL = 7000  # seconds (~1.9 hours, token lives 2h)


def _load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            c = json.load(f)
            if time.time() - c.get("ts", 0) < TTL:
                return c.get("token")
    return None


def _save_cache(token):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump({"token": token, "ts": time.time()}, f)


def get_token():
    """Return valid tenant_access_token (cached)."""
    cached = _load_cache()
    if cached:
        return cached
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps(CRED).encode(),
        headers={"Content-Type": "application/json"},
    )
    resp = json.loads(urllib.request.urlopen(req).read())
    token = resp["tenant_access_token"]
    _save_cache(token)
    return token


if __name__ == "__main__":
    # Just print token for shell scripts: TOKEN=$(python3 token_mgr.py)
    print(get_token())
