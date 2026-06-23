#!/usr/bin/env bash
# wsl-handoff.sh — drop a .ps1 to Windows desktop and print the run command
#
# Usage:
#   wsl-handoff.sh <ps1-file> [user-name]
#
# Example:
#   wsl-handoff.sh /tmp/fix-store-4.ps1
#   wsl-handoff.sh /tmp/fix-store-4.ps1 Aorus
#
# Effect:
#   1. Copies <ps1-file> to /mnt/c/Users/<user-name>/Desktop/
#   2. Prints the two-line PowerShell command the user should run as admin
#
# Why this exists:
#   WSL paths (/tmp/...) are NOT visible to Windows PowerShell.
#   /mnt/c/Users/<user>/Desktop/ is the canonical handoff location.
#   Files written this way bypass Windows Notepad's GBK encoding gotcha.

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <ps1-file> [user-name]" >&2
    echo "Example: $0 /tmp/fix-store-4.ps1" >&2
    exit 2
fi

SRC="$1"
USER_NAME="${2:-${USER:-aorus}}"

if [[ ! -f "$SRC" ]]; then
    echo "[h] source not found: $SRC" >&2
    exit 1
fi

FILENAME="$(basename "$SRC")"
DEST_DIR="/mnt/c/Users/${USER_NAME}/Desktop"
DEST="${DEST_DIR}/${FILENAME}"

if [[ ! -d "$DEST_DIR" ]]; then
    echo "[h] desktop not found: $DEST_DIR" >&2
    echo "[h] user-name might be wrong; pass it as 2nd arg" >&2
    exit 1
fi

cp -f "$SRC" "$DEST"
echo "[h] copied: $DEST"
echo ""
echo "================================================================"
echo "  Run in ADMIN PowerShell (right-click Start -> Terminal Admin):"
echo "================================================================"
echo ""
echo "  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass"
echo "  & \"C:\\Users\\${USER_NAME}\\Desktop\\${FILENAME}\""
echo ""
echo "================================================================"
echo ""
echo "Reminder: script must be PURE ASCII (no Chinese in code lines)."
echo "If you wrote it with Chinese comments, regenerate without them."
