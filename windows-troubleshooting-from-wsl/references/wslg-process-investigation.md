# WSLg Process Investigation & Architecture

How to trace Windows processes from WSL, understand WSLg's auto-restart
behavior, and distinguish WSLg RDP clients from traditional Remote Desktop.

## Quick Reference: WSLg Architecture

```
wslservice.exe  (PID ~5316, AUTO_START, runs as LocalSystem)
  └── wslhost.exe  (one per channel, --vm-id {GUID}, --handle NNNN)
        ├── msrdc.exe  (00000001 = Graphics/Wayland/Weston compositor)
        └── msrdc.exe  (00000002 = Audio/PulseAudio)
```

- **wslservice.exe**: Master WSL service, starts at boot. If killed, WSL dies.
- **wslhost.exe**: Per-channel manager spawned by wslservice. Monitors msrdc.exe
  and restarts it on exit.
- **msrdc.exe**: Microsoft Remote Desktop Client repurposed by WSLg.
  Command line includes `/wslg /silent` and a Hyper-V socket service ID.
  PID 8 (System) owns the actual TCP/UDP 3389 listener.

## Finding WSLg RDP Processes from WSL

### Get all msrdc.exe instances with parent chain

```powershell
# From WSL, use full path if interop PATH is missing:
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command "
Get-CimInstance Win32_Process -Filter \"Name = 'msrdc.exe'\" |
    Select-Object ProcessId, ParentProcessId, CommandLine
"
```

Each msrdc.exe command line reveals the channel type:
- `hvsocketserviceid:00000001-FACB-...` → Graphics channel
- `hvsocketserviceid:00000002-FACB-...` → Audio channel

### Trace parent all the way up

```powershell
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command "
# Given msrdc PID (e.g. 162648), walk up the chain:
$pid = 162648
while ($pid) {
    $p = Get-CimInstance Win32_Process -Filter \"ProcessId = $pid\" |
         Select ProcessId, Name, ParentProcessId
    Write-Host ('PID ' + $p.ProcessId + ' (' + $p.Name + ') -> parent=' + $p.ParentProcessId)
    $pid = $p.ParentProcessId
}
"
```

Typical chain: `msrdc.exe → wslhost.exe → wslservice.exe` (or `wsl.exe` for
non-service WSL instances).

### Get running services (WSL + RDP)

```powershell
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command "
Get-Service -Name '*RemoteDesktop*','*TermService*','*SessionEnv*','*UmRdpService*','wslservice' |
    Format-Table Name, DisplayName, Status, StartType -AutoSize
"
```

## Auto-Restart Root Cause

When you kill `msrdc.exe`, it comes back because:

1. **wslservice.exe** is `AUTO_START` — Windows starts it at boot, not
   killable without stopping the service.
2. **wslhost.exe** is the direct parent of msrdc.exe, spawned by wslservice.
   It monitors the child and restarts on exit (like systemd `Restart=always`).
3. No Windows service trigger (`sc.exe qtriggerinfo`) is registered —
   the restart is purely parent-process monitoring, not OS-level restart manager.

This is by design for WSLg reliability. Killing msrdc.exe breaks WSL GUI
rendering (Windows of Linux apps go blank) and audio.

## Kill vs Disable Decision Tree

| Goal | Method | Side Effects |
|------|--------|-------------|
| Kill temporarily | `Stop-Process -Id <PID> -Force` | Restarts in <3 seconds |
| Disable WSLg | Add `guiApplications=false` to `%USERPROFILE%\.wslconfig` + `wsl --shutdown` | All Linux GUI apps stop working |
| Stop WSL entirely | `sc.exe stop wslservice` | All WSL distros stop |
| Kill service permanently | `sc.exe config wslservice start= disabled` + reboot | WSL won't start at all |

## Detection: msrdc.exe vs mstsc.exe

| Property | msrdc.exe (WSLg) | mstsc.exe (User RDP) |
|----------|-----------------|---------------------|
| Path | `C:\Program Files\WSL\msrdc.exe` | `C:\Windows\System32\mstsc.exe` |
| CmdLine | `/wslg /silent /v:{GUID}` | `/v:<hostname or IP>` |
| Parent | `wslhost.exe` | `explorer.exe` or user shell |
| User | Same as WSL user | Interactive user |
| Count | Usually 2 | 0-N per active session |

`mstsc.exe` found via `tasklist | findstr mstsc` or
`Get-Process -Name mstsc`. If neither returns anything, the user may be
seeing WSLg's msrdc.exe in the system tray and mistaking it for a user RDP
session.

## Port 3389 Listener

```powershell
netstat -ano | findstr ':3389'
```

If PID is 8 (System), it's the kernel-mode Terminal Server driver, NOT
a user-initiated RDP session. This means Remote Desktop is *enabled* in
Windows Settings but not necessarily in use.

Check enablement:
```powershell
Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server' \
    -Name 'fDenyTSConnections'
```
- `0` = RDP enabled (port 3389 listening)
- `1` = RDP disabled
