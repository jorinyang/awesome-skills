---
name: windows-troubleshooting-from-wsl
description: Diagnose and repair Windows components (services, Store, AppX packages, registry) from a WSL session by bridging to Windows PowerShell. Use when a user reports a Windows-side problem but the agent's shell is WSL.
category: devops
---

# Windows Troubleshooting from WSL

When the user reports a Windows problem (Store won't open, service failed, AppX broken) and the agent is in WSL, the workflow is: **write the fix as a `.ps1` on the Windows side, then have the user run it in an admin PowerShell**. Pure-ASCII + `/mnt/c/Users/<user>/Desktop/` is the only reliable handoff.

## When to use this skill

- User says "Microsoft Store doesn't work" / "Windows service X failed" / "I get error 0x... in [Windows app]"
- User has authorized running PowerShell commands on the Windows host
- You're in a WSL session (Ubuntu on Windows) and want to fix Windows state
- The fix needs admin (Service start, AppX re-register, registry edit, sfc/DISM)

## The handoff contract

WSL and Windows have **independent filesystems and shells** that don't auto-bridge. There is exactly one reliable pattern for "user runs a PS1 I wrote from WSL":

1. Write a **pure-ASCII** `.ps1` (no Chinese, no emoji, no `===` markers at line start)
2. Save it to **`/mnt/c/Users/<user>/Desktop/<name>.ps1`** (visible to Windows as `C:\Users\<user>\Desktop\<name>.ps1`)
3. Give the user the exact two-line run command:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   & "C:\Users\<user>\Desktop\<name>.ps1"
   ```
4. **Never** give them a path starting with `/tmp/...` (WSL-only), `\\wsl$\...` (works but fragile), or any Linux path

WSL helper to drop a script to desktop (always use this instead of asking user to copy-paste):
```bash
cp /tmp/my-fix.ps1 /mnt/c/Users/Aorus/Desktop/my-fix.ps1
```

## Hard rules (read these first, they're all learned from failures)

### 0. WSL→Windows privilege boundary — you are a regular user

**Hard truth**: when your shell is WSL (Ubuntu on Windows) and you call `cmd.exe /c sc ...` or `powershell.exe ...`, you are running as the **same unelevated user** as your Windows login. There is no `sudo` from WSL→Windows that triggers UAC. UAC is a Windows-kernel feature, and WSL processes cannot invoke it.

What this means in practice:
- `reg add HKLM\...` from WSL → `拒绝访问 / Access is denied` even if the user is a Windows admin
- `sc config wuauserv start= auto` from WSL → `OpenService 失败 5: 拒绝访问`
- `reg query HKLM\...` from WSL → may even fail (HKLM read usually works, but SYSTEM-protected subkeys deny)
- `reagentc /info` from WSL → access denied

**Do not** waste turns trying `sudo cmd.exe /c ...` or `psexec` — they don't work from WSL.

**`Start-Process powershell -Verb RunAs` DOES work from WSL** — it triggers a UAC elevation dialog on the Windows desktop. The user must click "Yes" in the dialog, but the command itself fires from WSL correctly. This is the preferred pattern for portproxy, firewall rules, and other netsh/admin operations. Example:

```bash
powershell.exe -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -Command \"netsh interface portproxy add v4tov4 listenport=8787 listenaddress=127.0.0.1 connectport=8787 connectaddress=172.24.49.212\"'"
```

Wait a few seconds after the command for the user to approve UAC, then verify with a read-only `netsh interface portproxy show all` (no admin needed for show).

**The correct workflow** is: detect the boundary (`whoami /groups | findstr S-1-16` returns `S-1-16-8192` for medium, `S-1-16-12288` for high), then **hand the script to the user to run in an admin PowerShell on Windows** via the handoff contract below. Plan your fix as a deliverable, not as autonomous execution.

### 1. Pure-ASCII only inside .ps1 body

- No Chinese characters in any code line, comment, or `Write-Host` message
- No `===` markers at start of comment lines — PowerShell 5.1 tries to parse them as commands
- Use `[OK] / [WARN] / [FAIL]` English status tags, not colored Chinese
- Use ASCII arrows (`->`) not unicode (`→`)
- Exception: file path strings and registry values can contain unicode (Windows is fine with these)

If you must include Chinese in a `Write-Host` for the user, force UTF-8 at script top:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
```
…but this still doesn't fix **comment-line parsing**. Keep comments English.

### 2. Save files via WSL, not Windows Notepad

Notepad defaults to ANSI/GBK on Chinese Windows. If you give the user a script and they save it via Notepad, the Chinese gets garbled (`鎴栬€呭皾璇?` etc.) and the script breaks with parse errors. Solution: **always write the file from WSL to `/mnt/c/Users/.../Desktop/`**. Never ask the user to "save this to a .ps1 file via Notepad".

### 3. Detect partial admin early

If `Set-Service -StartupType Automatic` returns `Access is denied` but `Start-Service` works, the user's PowerShell is **not full admin** (likely UAC-restricted token, or local admin without full privileges). Two paths:

- Try `sc.exe config <svc> start= auto` instead — sometimes bypasses the PS constraint
- If `sc.exe` also fails, you need SYSTEM-level access; tell the user and stop

Don't loop retrying `Set-Service` — it'll just keep failing.

### 4. WSL→Windows path translation is NOT automatic

| From WSL | To Windows | Works? |
|---|---|---|
| `/tmp/foo.ps1` | `C:\tmp\foo.ps1` | ❌ Doesn't exist (no auto-translation) |
| `/mnt/c/Users/Aorus/Desktop/foo.ps1` | `C:\Users\Aorus\Desktop\foo.ps1` | ✅ |
| `\\wsl$\Ubuntu\tmp\foo.ps1` | (WSL distro path) | ✅ but only with WSL installed and distro name correct |

Use `/mnt/c/Users/<user>/Desktop/` always.

### 5. `$pid` is a read-only automatic variable in PowerShell

If you write a loop like `foreach ($pid in $pids) { ... }`, PowerShell throws `无法覆盖变量 PID，因为该变量为只读变量或常量 / Cannot overwrite variable PID`. This is a script-breaking bug that looks like a logic error at first glance.

**Fix**: rename the loop variable. `$procId` or `$procPid` works. `$PID` (PowerShell's built-in for "current process ID") is reserved. Same for `$?`, `$^`, `$_`, `$Args`, `$Input`, `$Host`, `$HOME`, `$true`, `$false`, `$null` — don't reuse them as loop variables or function parameters.

### 6. `===` markers in code blocks the user pastes into PS 5.1

When the user pastes a multi-line block of code into a Win10/11 PowerShell 5.1 prompt, **any line that starts with `===` (even inside a comment)** is parsed as a command token. Symptom: `=== : 无法将"==="项识别为 cmdlet`. This bites when you give the user a transcript-style block with section headers.

**Fix options**:
- Use `# ===` (commented out) or `[OK] / [WARN] / [FAIL]` status tags in your code blocks
- Or instruct the user to save the block to a `.ps1` file and run it (not paste it), so PS doesn't try to parse comment-shaped text

The canonical way to deliver a multi-step script is still: write the file to `/mnt/c/Users/<user>/Desktop/`, give the user the 2-line `Set-ExecutionPolicy ... && & "..."` runner. The user pastes 2 lines, the script does the rest. Never have the user paste the whole script body.

### 7. Never inline PowerShell in bash strings — use .ps1 files

When calling `powershell.exe` from WSL bash, bash expands `$_`, `$pid`, `$args`, and
other `$`-prefixed tokens before PowerShell ever sees them. The result is garbled
script text that PowerShell can't parse:

```bash
# ❌ $_ becomes a bash artifact (e.g. /tmp/cua.Source)
powershell.exe -Command "Get-Process | ForEach-Object { $_.Name }"

# ✅ Write the script to /mnt/c/... first, then -File it
powershell.exe -ExecutionPolicy Bypass -File "C:\Users\Aorus\temp.ps1"
```

Single-quoted heredocs do NOT fully protect against this — bash still expands some
constructs inside command substitution and pipeline contexts. The only reliable
pattern is a `.ps1` file on the Windows filesystem, executed via `-File`.

## Diagnostic workflow

For "X Windows feature is broken", the standard read-only ladder is:

```powershell
# 1. Services (which ones stopped, which are set to manual)
Get-Service <svc1>, <svc2> | Format-Table Name, Status, StartType -AutoSize

# 2. The package itself (Store, etc.)
Get-AppxPackage -AllUsers -Name <PackageName> | Format-List Name, Version, State, InstallLocation, SignatureKind

# 3. The EventLog for the actual error
Get-WinEvent -LogName "Microsoft-Windows-AppxDeploymentServer/Operational" -MaxEvents 200 |
    Where-Object { $_.Level -le 3 } | Select-Object -First 15 ... | Format-List

# 4. Process holding the resource
Get-Process -Name <proc> | Format-Table Id, ProcessName, StartTime

# 5. AppX deployment log for a specific failure
Get-AppPackageLog -ActivityID <id-from-error>
```

Output garbled to WSL console? Add at top of script:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
```

## Microsoft Store specific fix ladder

When user says "Microsoft Store won't open / says update service not running / says initialization failed":

1. **Check core services** — `ClipSVC`, `AppXSvc`, `AppReadiness` are the relevant ones. If `ClipSVC` is Stopped, start it (this fixes ~80% of "initialization failed" cases).
2. **`wsreset.exe`** — official Microsoft cache reset tool. Run as separate process:
   ```powershell
   Start-Process -FilePath "$env:SystemRoot\System32\wsreset.exe" -Wait -WindowStyle Hidden
   ```
3. **Clear local cache** (not the package itself):
   - `$env:LOCALAPPDATA\Packages\Microsoft.WindowsStore_8wekyb3d8bbwe\AC\INetCache`
   - `$env:LOCALAPPDATA\Packages\Microsoft.WindowsStore_8wekyb3d8bbwe\LocalCache`
   - `$env:LOCALAPPDATA\Packages\Microsoft.WindowsStore_8wekyb3d8bbwe\Settings` (locked while Store running — kill it first)
   - `$env:LOCALAPPDATA\Microsoft\Windows Store`
4. **Clean `SoftwareDistribution`** (WUA cache) — stop `wuauserv` + `bits` first
5. **Re-register Store package** — required to fail with `0x80073D02` first (means file lock) then auto-retry after kill
6. **`sfc /scannow`** — last resort, takes 5-15 min, often needs a reboot
7. **`DISM /Online /Cleanup-Image /RestoreHealth`** — even more last-resort, takes 15-30 min

Always re-run the Store at the end to verify: `Start-Process "ms-windows-store:"` then check `Get-Process -Name WinStore.App`.

### Deeper root cause: wuauserv StartType=Disabled

If steps 1-5 above succeed (services Running, re-register OK) but the Store still reports "initialization failed", check the **wuauserv** state specifically:

```powershell
Get-Service wuauserv | Format-List Name, Status, StartType
# StartType = Disabled  →  this is the real problem, not ClipSVC
```

`wuauserv` being **Disabled** (not just Stopped) means it was deliberately turned off — usually by a "tweak" tool, group policy, or by hand. The Store depends on it indirectly (Store license validation, app update checks, telemetry sync). When it's Disabled:
- Standard `Start-Service wuauserv` → `StartService 失败 1058` (cannot start a disabled service)
- The 7-step fix ladder above will "succeed" at each step but the Store still won't initialize, because the dependent pipeline is broken
- Fix requires flipping StartType to auto, which needs full admin:
  ```powershell
  # From admin PowerShell, NOT from WSL (see Hard rule #0)
  sc.exe config wuauserv start= auto
  sc.exe start wuauserv
  ```
- If `sc.exe` returns `OpenService 失败 5: 拒绝访问` even from admin PS, the user has a constrained-token admin. Fallback: edit registry directly:
  ```powershell
  Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\wuauserv" -Name Start -Value 2 -Type DWord -Force
  # Then reboot
  ```

### Event ID decoder for AppX deployment failures

When the Store re-register step 5 fails, look at the AppX deployment operational log and the activity ID log for the **Event ID**, not the message text:

| Event ID | Meaning | Action |
|----------|---------|--------|
| 401 | Deployment operation failed (parent) | Read the child event in the same sequence |
| 404 | Specific deployment failure with HRESULT | Look at the HRESULT for the actual error |
| **419** | **`0x80073D02: 需要关闭以下应用`** | AppX package is in use — kill `WinStore.App` and `wsappx`, retry |
| **638** | **`程序包未更新，因为受影响的应用仍在运行`** | Same as 419, but at the resolution stage. PID list: `{Microsoft.WindowsStore_8wekyb3d8bbwe!App}` |
| **672** | **Dependency version too low** (`The package's version is lower than the required MinVersion`) | The VCLibs/UI.Xaml/.NET Native dep needs updating separately. Common after a Store version bump: `Microsoft.VCLibs.140.00.UWPDesktop` lags behind. Fix: install the latest VCLibs from the Store bundle, or `Add-AppxPackage` it from a higher-version source. |
| 702 | Cannot remove: package not installed for this user | A different user's package; skip |
| 605 | ResolvedDeferredRegistrations failed | Cascade from one of the above; look for the earliest failure in the same sequence |

Always grep the log by **Event ID**, not by error message text — the message changes with locale, the Event ID is invariant.

## WSL2 Interop Quirks

### Windows PATH is not inherited when `systemd=true`

If `/etc/wsl.conf` has `[boot] systemd=true` (or the `[interop]` section
is missing/`appendWindowsPath=false`), WSL does **not** append Windows
`%PATH%` directories. `cmd.exe`, `powershell.exe`, and other Windows
binaries are **not** found by bare name (`which cmd.exe` returns nothing).

Instead use full `/mnt/c/...` paths:

```bash
/mnt/c/Windows/System32/cmd.exe /c "echo works"
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -File "C:\...\script.ps1"
```

To check interop status: `cat /proc/sys/fs/binfmt_misc/WSLInterop` — should
show `enabled`.

### WSL2 localhost forwarding is unreliable for custom ports

Windows services bound to `127.0.0.1:PORT` may **not** be reachable from
WSL via `localhost:PORT` (curl exit code 7: "Connection refused").
`netstat -ano` on Windows confirms the port is LISTENING, but WSL2's
localhost forwarding doesn't bridge it for custom high ports.

**Workaround A — Windows host gateway IP** (for services bound to `0.0.0.0`):
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}')  # e.g. 172.24.48.1
nc -z -w 2 $WINDOWS_HOST $PORT
```

**Workaround B — netsh portproxy** (for any service, initiated from either side):

*Use case 1: Windows service bound to 127.0.0.1 → expose to WSL*

On Windows (admin PowerShell):
```powershell
netsh interface portproxy add v4tov4 `
    listenaddress=0.0.0.0 listenport=EXTERNAL_PORT `
    connectaddress=127.0.0.1 connectport=INTERNAL_PORT
```
Then reach the service from WSL via `$WINDOWS_HOST:EXTERNAL_PORT`.

*Use case 2: WSL service → map to Windows localhost (initiate from WSL)*

This maps a WSL-side service (e.g. Hermes WebUI on 172.24.49.212:8787) to Windows `127.0.0.1:8787` so that Windows browsers and tools can access it via localhost:

```bash
# Initiate admin netsh from WSL via UAC elevation
powershell.exe -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -Command \"netsh interface portproxy add v4tov4 listenport=8787 listenaddress=127.0.0.1 connectport=8787 connectaddress=WSL_IP\"'"

# Wait for UAC approval, then verify (show = no admin needed)
powershell.exe -Command "netsh interface portproxy show all | Select-String 8787"
```

If the service is reachable via direct WSL IP but times out through portproxy (TCP connects, HTTP fails), add a Windows Firewall inbound rule for the listen port:

```bash
powershell.exe -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -Command \"netsh advfirewall firewall add rule name=\\\"\"WSL Service PORT\\\"\" dir=in action=allow protocol=TCP localport=PORT\"'"
```

Verify end-to-end:
```bash
# From WSL: check TCP connectivity
powershell.exe -Command "Test-NetConnection -ComputerName 127.0.0.1 -Port PORT"

# From WSL: check HTTP
powershell.exe -Command "(Invoke-WebRequest http://127.0.0.1:PORT -UseBasicParsing -TimeoutSec 5).StatusCode"
```

**Caution**: If WSL uses mirrored networking (IP in 172.x.x.x range), the IP changes on reboot. The portproxy rule is persistent but its `connectaddress` will be stale after a WSL IP change. Update it with `netsh interface portproxy set v4tov4`.

**Caution**: The Windows host gateway IP can change on reboot (DHCP). For
persistent services, consider pinning a static IP in `.wslconfig` or
using `host.docker.internal` if Docker Desktop is installed.

### Windows PE executables are directly executable from `/mnt/c/`

WSL can execute Windows `.exe` files directly via their `/mnt/c/...` path
— no `cmd.exe /c` or PowerShell wrapper needed. stdin/stdout/stderr pipes
work correctly across the WSL↔Windows boundary. Verified for JSON-RPC
(MCP) communication including multi-round interaction and base64-encoded
binary payloads.

```bash
# Direct execution (preferred)
/mnt/c/Windows/System32/ipconfig.exe
/mnt/c/Users/Aorus/.cua/cua-driver.exe mcp

# subprocess from Python (works for MCP stdio)
subprocess.Popen(['/mnt/c/Users/Aorus/.cua/cua-driver.exe', 'mcp'],
                 stdin=PIPE, stdout=PIPE, stderr=PIPE)
```

`\r\n` in stdout is normal (Windows line endings) — `json.loads()` and
Python `readline()` handle it transparently.

## Port Conflict Diagnosis (WSL service → Windows localhost)

When a WSL service is reachable via its direct IP (`172.x.x.x:PORT`) but NOT via `127.0.0.1:PORT`, even though WSL's `wslrelay.exe` or a `netsh portproxy` rule is in place, the root cause is almost always **multiple processes competing for the same port**.

### Diagnosis workflow

```bash
# 1. List ALL listeners on the port (not just one)
powershell.exe -NoProfile -Command 'netstat -ano | findstr ":PORT"'
# Look for multiple LISTENING entries — each one is a competitor

# 2. Identify each process
powershell.exe -NoProfile -Command 'Get-Process -Id PID1,PID2 | Format-Table Id,ProcessName,Path'

# 3. Typical culprits (in descending order of likelihood):
#    - ssh.exe     → SSH tunnel (`ssh -L PORT:...`) silently occupying the port
#    - wslrelay.exe → WSL built-in forwarder (this is the one you want)
#    - netsh portproxy → manually added rule, redundant with wslrelay
```

### Common conflict scenario: ssh.exe tunnel

```
ssh.exe  -L 8787:localhost:8788 user@remote-host
wslrelay.exe  → forwarding WSL:8787 → Windows:8787
netsh portproxy  127.0.0.1:8787 → 172.x.x.x:8787
```

All three bind to `127.0.0.1:8787`. The first to `accept()` a connection wins — if ssh.exe wins, the request is forwarded to the remote host (where nothing useful is listening), and the user sees "connection refused" or "forcibly closed".

**Fix**: kill the ssh tunnel and remove the redundant portproxy rule. Leave only `wslrelay` — WSL2 already handles forwarding automatically.

```bash
# Kill conflicting ssh tunnel
powershell.exe -NoProfile -Command 'Stop-Process -Id <ssh_pid> -Force'

# Remove redundant portproxy (requires admin via UAC)
powershell.exe -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -Command \"netsh interface portproxy delete v4tov4 listenport=PORT listenaddress=127.0.0.1\"'"

# Verify: only ONE LISTENING entry should remain (wslrelay)
powershell.exe -NoProfile -Command 'netstat -ano | findstr ":PORT"'
```

### Warning: Browserbase is NOT localhost

**Never** use `browser_navigate` to test `http://127.0.0.1:PORT` connectivity. Browserbase runs on a cloud server — its `127.0.0.1` is the cloud VM's loopback, not the user's machine. A successful `browser_navigate` result is a **false positive**.

For local connectivity verification, always use PowerShell from WSL:
```bash
# TCP check
powershell.exe -NoProfile -Command "Test-NetConnection -ComputerName 127.0.0.1 -Port PORT"

# HTTP check
powershell.exe -NoProfile -Command "try { (Invoke-WebRequest http://127.0.0.1:PORT -UseBasicParsing -TimeoutSec 5).StatusCode } catch { Write-Host \$_.Exception.Message }"
```

### netsh portproxy is redundant when wslrelay is active

WSL2 ships with `wslrelay.exe` that auto-forwards WSL ports to Windows localhost. Adding a `netsh portproxy` rule creates a second listener competing with wslrelay. Unless `localhostForwarding=false` is set in `.wslconfig`, do NOT add portproxy rules — use wslrelay alone. The proper fix for "port not reachable" is to diagnose conflicts, not add more listeners.

## Pitfalls learned the hard way

- **`Set-Service` doesn't work without full admin** — check first, don't loop retry
- **Store package re-register fails with `0x80073D02`** — script must auto-kill `WinStore.App` and `wsappx` and retry
- **`wuauserv` not starting** — usually means Windows Update component is broken, not a permissions issue; needs `DISM` not `Set-Service`
- **`Get-AppxPackage -AllUsers` requires admin** in some Win11 builds; if you see "拒绝访问" the user isn't admin
- **`Settings/settings.dat` is locked while Store is open** — must `Stop-Process WinStore.App -Force` before deleting
- **Process management**: if `pkill` would be needed, ask user first (environment safety blocks it). For your own WSL-side processes (e.g. Electron), just verify with `ps -ef` whether cleanup is actually needed before any action
- **Don't loop on fixes** — if a step failed twice with the same error, escalate to user with diagnostic data; don't keep patching
- **Stop sign after 3 fix attempts**: if a Windows-side fix failed 3 times (e.g. Store still won't open after re-register + service restart + cache clear), **stop and present the user with the full diagnosis + manual options** instead of trying a 4th approach. The user has the right to know the fix is no longer autonomous and to take over. This matches the user's overall preference (in their profile) for manual control when scope expands into system-level Windows changes.
- **sshd "Connection closed" → `Match Group administrators` trap**: TCP connects but SSH disconnects immediately with "end of file" — don't assume firewall or network issue. Check if `C:\ProgramData\ssh\administrators_authorized_keys` exists. If missing and the connecting user is in the Administrators group, the `Match Group administrators` block in `sshd_config` redirects authorized_keys to a non-existent file, and sshd silently closes the session. Fix: comment out the `Match Group administrators` block in `C:\ProgramData\ssh\sshd_config` and restart sshd. See `references/windows-sshd-repair.md` for full diagnosis ladder.

## Verification

After any fix:
1. `Get-Service <key services>` — confirm Running
2. `Get-AppxPackage -AllUsers <name>` — confirm State = Ok
3. `Start-Process "ms-windows-store:"` (or relevant app) then `Get-Process` — confirm it stays up
4. Re-check user's original symptom by launching the app

### WSLg Process Investigation

When the user reports "Remote Desktop" processes they can't kill (especially system-tray icons), suspect **WSLg's `msrdc.exe`** — not traditional `mstsc.exe`. See `references/wslg-process-investigation.md` for architecture, parent-chain tracing with `Get-CimInstance Win32_Process`, and auto-restart root cause analysis.

## Reference files

- `references/microsoft-store-repair.md` — complete ready-to-run script for "Microsoft Store won't open" + ActivityID-based log harvesting
- `references/windows-sshd-repair.md` — Windows OpenSSH Server diagnosis: service stopped, administrators_authorized_keys missing, shell misconfigured; fix ladder and verification steps
- `references/wslg-process-investigation.md` — WSLg architecture, msrdc.exe vs mstsc.exe, process parent-chain tracing, auto-restart root cause
- `scripts/wsl-handoff.sh` — bash helper that copies a .ps1 to Windows desktop and prints the run command
