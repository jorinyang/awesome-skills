---
name: wsl-browser-cdp
description: Connect Hermes browser tools to Windows Chrome via CDP when running in WSL — fix the Node.js PATH issue, start Chrome with remote debugging, configure browser.cdp_url, and verify connectivity.
category: devops
related_skills: [double-evolution]
tags: [wsl, browser, cdp, chrome, hermes]
---

# WSL Browser CDP Setup

When Hermes runs in WSL and browser tools (`browser_navigate`, `browser_snapshot`, etc.) are needed, the Linux-side browser won't open a visible window on the Windows desktop. The solution: connect Hermes to a Windows Chrome instance via Chrome DevTools Protocol (CDP).

This skill covers the full setup: Node.js PATH fix, Chrome launch with remote debugging, Windows host IP discovery, Hermes config, and verification.

## When to use this skill

- Hermes is running in WSL and browser tools produce errors (no display, Node.js not found)
- User says "open this web page" / "use the browser" and `browser_navigate` returns CDP or Node.js errors
- The error `/usr/bin/env: 'node': No such file or directory` appears when calling browser tools
- User explicitly asks to use "Agent-browser + CDP" from WSL

## Step 1: Fix Node.js PATH for non-interactive shells

Hermes browser tools spawn subprocesses with a clean environment (default system PATH). Node.js installed in `~/.hermes/node/bin/` or `~/.local/bin/` won't be found.

**Symptom:** `browser_navigate` returns `{"success": false, "error": "/usr/bin/env: 'node': No such file or directory"}`

**Fix — create a system-level symlink (needs sudo once):**

```bash
sudo ln -sf ~/.hermes/node/bin/node /usr/local/bin/node
```

Verify:
```bash
env -i PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" node --version
# Should print v22.x.x
```

## Step 2: Discover Windows host IP from WSL

WSL2 runs in a separate VM. Windows host IP is NOT `localhost`.

```bash
# Method A — default route (most reliable)
WINDOWS_HOST=$(ip route show default | awk '{print $3}')
echo $WINDOWS_HOST  # e.g. 172.24.48.1

# Method B — resolv.conf nameserver
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
```

Use the IP from Method A. It can change on reboot (DHCP lease).

## Step 3: Find Chrome on Windows

```bash
# Chrome (primary)
ls "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"

# Edge (fallback — also supports CDP)
ls "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
```

## Step 4: Start Chrome with remote debugging

Use a **separate user-data-dir** to avoid conflicts with the user's existing Chrome session. Launch as background process (Chrome is long-lived).

```bash
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0 \
  --user-data-dir="C:\temp\chrome-cdp" \
  --no-first-run \
  --no-default-browser-check \
  --disable-session-crashed-bubble \
  "about:blank" &

sleep 3
```

Key flags:
- `--remote-debugging-port=9222` — CDP port
- `--remote-debugging-address=0.0.0.0` — allow connections from WSL VM (not just localhost)
- `--user-data-dir` — separate profile, avoids lock conflicts
- `--no-first-run` / `--no-default-browser-check` / `--disable-session-crashed-bubble` — suppress startup dialogs

Use `terminal(background=true)` to launch since Chrome never exits.

## Step 5: Verify CDP connectivity

```bash
curl -s "http://$WINDOWS_HOST:9222/json/version" | head -5
```

Expected output includes:
```json
{"Browser": "Chrome/150...", "Protocol-Version": "1.3", ...}
```

## Step 6: Configure Hermes CDP URL

```bash
hermes config set browser.cdp_url "http://WINDOWS_HOST_IP:9222"
# e.g. hermes config set browser.cdp_url "http://172.24.48.1:9222"
```

This takes effect on the next `browser_navigate` call — no restart needed.

## Step 7: Navigate and verify

```bash
# Now browser tools should work
browser_navigate(url="https://example.com")
```

The page opens in the user's visible Windows Chrome window. Snapshots, clicks, and console access work via CDP.

## Quick diagnostics

| Problem | Check |
|---------|-------|
| Browser tool still fails | `env -i PATH="..." node --version` — is Node.js in default PATH? |
| CDP curl fails | Is Chrome running? `ps aux | grep chrome.exe` |
| | Is `--remote-debugging-address=0.0.0.0` set? (without it, Chrome only listens on 127.0.0.1, unreachable from WSL2 VM) |
| | Did Windows host IP change? Re-run `ip route show default` |
| | Windows firewall blocking port 9222? Test from WSL: `nc -zv $WINDOWS_HOST 9222` |
| Auth / login pages | The browser window is visible on the Windows desktop — user can interactively log in |
| Page content in iframes | Use `browser_console` with `expression` to run JavaScript in the iframe's `contentDocument` for text extraction |

## Headless Mode

Add `--headless=new` to the Chrome launch command for background automation without a visible window:

```bash
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0 \
  --user-data-dir="C:\temp\chrome-cdp" \
  --no-first-run \
  --no-default-browser-check \
  --disable-session-crashed-bubble \
  --headless=new \
  "about:blank" &
```

Use `--headless=new` (modern, full rendering) — NOT `--headless` (legacy, deprecated).

## Using agent-browser CLI directly

agent-browser CLI (v0.27+) has native `--auto-connect` and `--cdp` flags:

```bash
# Connect to already-running CDP
agent-browser --cdp 9222 snapshot

# Auto-discover and connect
agent-browser --auto-connect snapshot

# Or via env var
AGENT_BROWSER_AUTO_CONNECT=1 agent-browser snapshot
```

Source repo: `github.com/vercel-labs/agent-browser` (Rust, Apache-2.0). Install: `npm install -g agent-browser && agent-browser install`.

## Full startup script

See `scripts/wsl-chrome-cdp.sh` for a one-command launcher that handles IP discovery, Chrome launch, and CDP readiness check.

## Chrome CDP flags reference

See `references/chrome-cdp-flags.md` for the complete flag reference including session isolation, headless modes, and troubleshooting.

## WeChat Article Extraction

See `references/wechat-article-extraction.md` for the browser_console + `#js_content` extraction pattern when `browser_navigate` times out or `browser_snapshot` truncates 微信文章.

## Cleanup

Chrome CDP session persists until the Chrome window is closed. To stop:

```bash
# Kill the CDP Chrome instance (NOT the user's main Chrome)
taskkill.exe /F /IM chrome.exe /FI "WINDOWTITLE eq about:blank" 2>/dev/null
# Or just close the window manually
```

## Pitfalls

- **Windows host IP changes on reboot.** Re-run Step 2 and update `browser.cdp_url` if CDP suddenly unreachable.
- **Chrome already running without CDP.** The `--user-data-dir="C:\temp\chrome-cdp"` flag creates a separate instance — no conflict.
- **Multiple CDP sessions.** Only one browser session is active at a time. Starting a new `browser_navigate` reuses the same CDP connection.
- **`--remote-debugging-address=0.0.0.0` is critical.** Without it, Chrome binds only to Windows `127.0.0.1`, which is NOT reachable from WSL2's VM network.
- **Node.js symlink persists across reboots.** The `sudo ln -sf` in `/usr/local/bin` survives — only needed once.
