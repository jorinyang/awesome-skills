# MSYS2 PATH Setup for Cron

## Problem
On Windows, cron jobs run via git-bash/MSYS2 as SYSTEM user. MSYS2 builds its PATH from `/etc/profile.d/` scripts and does NOT automatically inherit Windows system or user PATH environment variables.

## Symptom
Cron tasks report `command not found` for npm global tools (lark-cli, etc.) that work fine in interactive terminal.

## Root Cause
1. Windows system PATH (`[Environment]::SetEnvironmentVariable('Path', ..., 'Machine')`) is NOT picked up by MSYS2 bash
2. MSYS2 `/etc/profile.d/` lives at `C:\Program Files\Git\etc\profile.d\`
3. npm global bin is at `C:\Users\<user>\AppData\Roaming\npm` → `/c/Users/<user>/AppData/Roaming/npm` in MSYS2

## Fix

Create `C:\Program Files\Git\etc\profile.d\npm_path.sh`:

```bash
NPM_BIN="/c/Users/Aorus/AppData/Roaming/npm"
case ":$PATH:" in
  *":$NPM_BIN:"*) ;;
  *) export PATH="$PATH:$NPM_BIN" ;;
esac
```

Verify: `/bin/bash -lc 'lark-cli --version'`

## write_file Gotcha
On Windows, `write_file` with Unix paths like `/etc/profile.d/npm_path.sh` resolves to `C:\etc\profile.d\npm_path.sh` (wrong). Must use Windows absolute path: `C:/Program Files/Git/etc/profile.d/npm_path.sh`.
