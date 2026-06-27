#!/usr/bin/env bash
# wsl-chrome-cdp.sh — Launch Windows Chrome with CDP from WSL
#
# Usage: bash wsl-chrome-cdp.sh [port] [url]
#   port: CDP debug port (default: 9222)
#   url:  Initial page to open (default: about:blank)
#
# Examples:
#   bash wsl-chrome-cdp.sh                           # default port 9222
#   bash wsl-chrome-cdp.sh 9223                      # custom port
#   bash wsl-chrome-cdp.sh 9222 "https://example.com" # with URL

set -euo pipefail

PORT="${1:-9222}"
OPEN_URL="${2:-about:blank}"

# --- Detect WSL ---
if ! grep -qi "microsoft\|wsl" /proc/version 2>/dev/null; then
  echo "[WARN] Not running in WSL. This script is for WSL → Windows Chrome CDP."
  echo "       On native Linux, use: google-chrome --remote-debugging-port=$PORT"
  exit 1
fi

# --- Find Windows host IP ---
WINDOWS_HOST=""
if [ -f /etc/resolv.conf ]; then
  WINDOWS_HOST=$(grep nameserver /etc/resolv.conf | awk '{print $2}' | head -1)
fi
if [ -z "$WINDOWS_HOST" ]; then
  WINDOWS_HOST=$(ip route show default 2>/dev/null | awk '{print $3}' | head -1)
fi
if [ -z "$WINDOWS_HOST" ]; then
  echo "[FAIL] Cannot determine Windows host IP. Check /etc/resolv.conf or ip route."
  exit 1
fi
echo "[OK] Windows host IP: $WINDOWS_HOST"

# --- Check if CDP is already running ---
if curl -sf "http://${WINDOWS_HOST}:${PORT}/json/version" > /dev/null 2>&1; then
  echo "[OK] CDP already running on ${WINDOWS_HOST}:${PORT}"
  echo "     Set: hermes config set browser.cdp_url \"http://${WINDOWS_HOST}:${PORT}\""
  exit 0
fi

# --- Find Chrome/Edge ---
CHROME_EXE=""
for candidate in \
  "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" \
  "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
  "/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe" \
  "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
do
  if [ -f "$candidate" ]; then
    CHROME_EXE="$candidate"
    break
  fi
done

if [ -z "$CHROME_EXE" ]; then
  echo "[FAIL] No Chrome or Edge installation found on Windows."
  echo "       Checked: /mnt/c/Program Files/..."
  exit 1
fi
echo "[OK] Found browser: $CHROME_EXE"

# --- Launch Chrome ---
echo "[..] Launching Chrome with CDP on port $PORT..."
"$CHROME_EXE" \
  --remote-debugging-port="$PORT" \
  --remote-debugging-address=0.0.0.0 \
  --user-data-dir="C:\\temp\\chrome-cdp-${PORT}" \
  --no-first-run \
  --no-default-browser-check \
  --disable-session-crashed-bubble \
  --headless=new \
  "$OPEN_URL" \
  > /dev/null 2>&1 &

# --- Wait for CDP readiness ---
for i in $(seq 1 10); do
  sleep 1
  if curl -sf "http://${WINDOWS_HOST}:${PORT}/json/version" > /dev/null 2>&1; then
    echo "[OK] CDP ready on ws://${WINDOWS_HOST}:${PORT}/devtools/browser/..."
    echo ""
    echo "  To use with Hermes:"
    echo "    hermes config set browser.cdp_url \"http://${WINDOWS_HOST}:${PORT}\""
    echo ""
    echo "  To use with agent-browser CLI:"
    echo "    agent-browser --cdp $PORT snapshot"
    exit 0
  fi
done

echo "[FAIL] Chrome launched but CDP did not become ready after 10s."
echo "       Check: Chrome may need first-run setup or be blocked by antivirus."
exit 1
