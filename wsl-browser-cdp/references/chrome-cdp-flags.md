# Chrome CDP Flags Reference

Key Chrome command-line flags for remote debugging from WSL/headless environments.

## Essential for WSL

| Flag | Purpose |
|------|---------|
| `--remote-debugging-port=9222` | Enable CDP on given port |
| `--remote-debugging-address=0.0.0.0` | **Critical for WSL** — bind to all interfaces, not just 127.0.0.1 |
| `--user-data-dir=C:\temp\chrome-cdp` | Isolated profile — avoids conflicts with user's normal Chrome |

## Session isolation

| Flag | Purpose |
|------|---------|
| `--no-first-run` | Skip first-run wizard |
| `--no-default-browser-check` | Don't check if Chrome is default browser |
| `--disable-session-crashed-bubble` | Suppress "restore pages" popup |
| `--disable-features=TranslateUI` | Suppress translation prompts |
| `--disable-sync` | Don't sync with Google account |
| `--no-service-autorun` | Don't auto-start background services |

## Headless modes

| Flag | Purpose |
|------|---------|
| `--headless=new` | Modern headless (full rendering, no window) — preferred |
| `--headless` | Legacy headless (limited rendering) — deprecated |

## Troubleshooting

### "CDP endpoint not reachable from WSL"

Check that `--remote-debugging-address=0.0.0.0` was used. Without it, Chrome binds to 127.0.0.1 only, and WSL's virtual network interface cannot reach it.

Verify from WSL:
```bash
WINDOWS_HOST=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
curl -s "http://${WINDOWS_HOST}:9222/json/version"
```

### "Profile is in use"

Chrome locks the user-data-dir. Use a unique per-port directory:
`--user-data-dir=C:\temp\chrome-cdp-9222`

Or kill the existing process:
```bash
/mnt/c/Windows/System32/taskkill.exe /F /IM chrome.exe 2>/dev/null || true
```

### Port already in use (non-Chrome)

```bash
# Check what's on the port (from Windows)
/mnt/c/Windows/System32/netstat.exe -ano | grep :9222
```

## Chrome discovery paths

| Path | Browser |
|------|---------|
| `/mnt/c/Program Files/Google/Chrome/Application/chrome.exe` | Chrome stable (64-bit) |
| `/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe` | Chrome stable (32-bit) |
| `/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe` | Edge stable (64-bit) |
| `/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe` | Edge stable (32-bit) |
