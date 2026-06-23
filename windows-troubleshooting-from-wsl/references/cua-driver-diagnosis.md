# cua-driver Diagnosis & Repair (Windows, from WSL)

## Quick facts

| Fact | Detail |
|------|--------|
| Binary | `cua-driver.exe` (Rust, ~10MB) |
| Install | `irm https://raw.githubusercontent.com/trycua/cua/main/libs/cua-driver/scripts/install.ps1 \| iex` |
| Install path | `%LOCALAPPDATA%\Programs\Cua\cua-driver\bin\cua-driver.exe` |
| WSL path | `/mnt/c/Users/<user>/AppData/Local/Programs/Cua/cua-driver/bin/cua-driver.exe` |
| MCP mode | `cua-driver.exe mcp` (stdio JSON-RPC) |
| Autostart | Registered as Scheduled Task — disable with `cua-driver.exe autostart disable` |

## Common issues

### 1. High CPU from cursor overlay (v0.5.3 and earlier)

**Symptom**: `cua-driver.exe` consumes ~95% of one CPU core continuously, even when idle.

**Root cause**: `agent_cursor.enabled` defaults to `true`, and the animated cursor overlay
continuously repaints. v0.5.3 and earlier have no idle-timeout on the overlay.

**Diagnose**:
```powershell
Get-Process -Name 'cua-driver*' | Select Id, CPU
# Real-time CPU:
Get-Counter '\Process(cua-driver*)\% Processor Time'
```

**Fix**:
```powershell
# Upgrade to v0.5.7+ (cursor overlay has idle-timeout)
irm https://raw.githubusercontent.com/trycua/cua/main/libs/cua-driver/scripts/install.ps1 | iex
```

**Post-upgrade**: re-disable autostart (`cua-driver.exe autostart disable`).

### 2. Orphaned cua-driver processes after Hermes restart

**Symptom**: Multiple `cua-driver.exe mcp` processes linger after Hermes gateway is killed.

**Root cause**: `kill -9` on the Hermes gateway doesn't close stdin to the Windows child
process. The child becomes orphaned and never exits.

**Fix**:
```powershell
taskkill /F /IM cua-driver.exe
```

**Prevention**: Use SIGTERM (regular `kill`, not `kill -9`) on Hermes gateways. The MCP
stdio pipe closes cleanly, and the Windows child detects EOF and exits with code 0.

### 3. Autostart re-registered after update

Every `irm install.ps1 | iex` re-registers the `cua-driver-serve` Scheduled Task.
After an update, always run:
```bash
"/mnt/c/Users/Aorus/AppData/Local/Programs/Cua/cua-driver/bin/cua-driver.exe" autostart disable
```

### 4. `Set-Service` fails for WaaSMedicSvc without admin

`WaaSMedicSvc` can be stopped but its StartType cannot be changed from "Manual"
without full admin elevation. Registry-based disable is an alternative:
```powershell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\WaaSMedicSvc" -Name Start -Value 4 -Type DWord -Force
```

## CPU monitoring from WSL

Quick one-shot CPU check:
```powershell
# Top 5 cumulative CPU (since boot)
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 Id, ProcessName, CPU

# Real-time CPU % per-process
Get-Counter '\Process(*)\% Processor Time'

# Overall CPU load %
(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
```

Long-running monitor (write as .ps1, run on Windows):
```powershell
$duration_minutes = 20
$interval_seconds = 10
# ... full script in scripts/cpu-monitor.ps1
```
