# Microsoft Store "initialization failed" — full repair script

Copy-paste this as a fresh file (or use the wsl-handoff script in `../scripts/` to drop it to the Windows desktop). The script is pure-ASCII, safe to run on Win10/Win11 with admin PowerShell.

## Symptoms this script targets

- Store opens but shows: "其中一个更新服务未正常运行"
- Store shows: "出现错误，microsoft store初始化失败，请尝试刷新或稍后返回"
- Store hangs on splash
- `ClipSVC` service stopped
- `wuauserv` service stopped

## How to run

1. From WSL: `cp /tmp/fix-store-4.ps1 /mnt/c/Users/Aorus/Desktop/fix-store-4.ps1`
2. Open admin PowerShell on Windows (right-click Start → Terminal (Admin))
3. Run:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   & "C:\Users\Aorus\Desktop\fix-store-4.ps1"
   ```
4. Read the colored output. Each step shows `[OK] / [WARN] / [FAIL]`.

## The canonical 7-step script

The actual file content (kept here so you can copy it without a separate download):

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
$ErrorActionPreference = 'Continue'

function Sec($t) { Write-Host "" ; Write-Host "=== $t ===" -ForegroundColor Cyan }
function OK($t)   { Write-Host "  [OK]   $t" -ForegroundColor Green }
function Warn($t) { Write-Host "  [WARN] $t" -ForegroundColor Yellow }
function Fail($t) { Write-Host "  [FAIL] $t" -ForegroundColor Red }

# Step 1: kill store procs
Sec "Step 1: end WinStore.App and wsappx"
Get-Process -Name 'WinStore.App','wsappx' -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  Stopping PID $($_.Id) ($($_.ProcessName))"
    try { Stop-Process -Id $_.Id -Force -ErrorAction Stop; OK "stopped" }
    catch { Warn "skip: $($_.Exception.Message)" }
}

# Step 2: delete Store local cache
Sec "Step 2: delete Store local cache (Store will rebuild)"
$paths = @(
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsStore_8wekyb3d8bbwe\AC\INetCache",
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsStore_8wekyb3d8bbwe\AC\INetCookies",
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsStore_8wekyb3d8bbwe\LocalCache",
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsStore_8wekyb3d8bbwe\LocalState\Microsoft\Windows Store\Cache",
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsStore_8wekyb3d8bbwe\Settings",
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsStore_8wekyb3d8bbwe\RoamingState",
    "$env:LOCALAPPDATA\Microsoft\Windows Store"
)
foreach ($p in $paths) {
    if (Test-Path $p) {
        try { Remove-Item -Path $p -Recurse -Force -ErrorAction Stop; OK "removed $p" }
        catch { Warn "skip $p : $($_.Exception.Message)" }
    } else {
        Write-Host "  [--]   not exist: $p"
    }
}

# Step 3: clean SoftwareDistribution
Sec "Step 3: clean SoftwareDistribution (Windows Update cache)"
try {
    Stop-Service -Name wuauserv -Force -ErrorAction Stop
    Stop-Service -Name bits     -Force -ErrorAction Stop
    OK "stopped wuauserv + bits"
} catch {
    Warn "stop services: $($_.Exception.Message)"
}

$sdPath = "$env:WINDIR\SoftwareDistribution"
if (Test-Path $sdPath) {
    try {
        Get-ChildItem -Path $sdPath -Recurse -Force -ErrorAction SilentlyContinue |
            Where-Object { -not $_.PSIsContainer } | ForEach-Object {
                Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
            }
        OK "cleaned $sdPath contents"
    } catch {
        Warn "clean SoftwareDistribution: $($_.Exception.Message)"
    }
}

try {
    Start-Service -Name wuauserv -ErrorAction Stop
    Start-Service -Name bits     -ErrorAction Stop
    OK "restarted wuauserv + bits"
} catch {
    Warn "start services: $($_.Exception.Message)"
}

# Step 4: re-register Store package
Sec "Step 4: re-register Store package"
$store = Get-AppxPackage -AllUsers Microsoft.WindowsStore
if ($store) {
    $manifest = Join-Path $store.InstallLocation 'AppXManifest.xml'
    if (Test-Path $manifest) {
        try {
            Add-AppxPackage -DisableDevelopmentMode -Register $manifest -ErrorAction Stop
            OK "re-registered: $($store.PackageFullName)"
        } catch {
            $err = $_.Exception.Message
            if ($err -match 'currently in use') {
                Warn "store still running, kill and retry..."
                Get-Process -Name 'WinStore.App','wsappx' -ErrorAction SilentlyContinue |
                    Stop-Process -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
                try {
                    Add-AppxPackage -DisableDevelopmentMode -Register $manifest -ErrorAction Stop
                    OK "re-registered after retry"
                } catch { Fail "re-register: $($_.Exception.Message)" }
            } else {
                Fail "re-register: $err"
            }
        }
    } else {
        Fail "manifest not found: $manifest"
    }
} else {
    Fail "Store package not found"
}

# Step 5: wsreset
Sec "Step 5: run wsreset.exe"
try {
    Start-Process -FilePath "$env:SystemRoot\System32\wsreset.exe" -Wait -WindowStyle Hidden
    OK "wsreset done"
} catch {
    Warn "wsreset: $($_.Exception.Message)"
}

# Step 6: restart services
Sec "Step 6: restart ClipSVC / AppXSvc / AppReadiness"
foreach ($s in 'ClipSVC','AppXSvc','AppReadiness') {
    try {
        Stop-Service -Name $s -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
        Start-Service -Name $s -ErrorAction Stop
        OK "$s restarted"
    } catch {
        Warn "$s restart: $($_.Exception.Message)"
    }
}

# Step 7: launch Store and verify
Sec "Step 7: launch Store and verify"
Start-Process "ms-windows-store:"
Start-Sleep -Seconds 4
$proc = Get-Process -Name WinStore.App -ErrorAction SilentlyContinue
if ($proc) {
    OK "Store running, PID=$($proc.Id)"
} else {
    Warn "Store not detected, try manually"
}

Sec "DONE"
Write-Host "If still fails, run: Get-AppPackageLog -ActivityID <id>  (get ID from the new error dialog)" -ForegroundColor Cyan
```

## ActivityID-based log harvesting

When the Store still fails, the error dialog contains a `Get-AppPackageLog -ActivityID` hint. Use this to fetch the real failure cause:

```powershell
$id = "REPLACE-WITH-ACTIVITYID-FROM-ERROR"
try {
    Get-AppPackageLog -ActivityID $id -ErrorAction Stop | Select-Object -First 80
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "=== Fallback: AppX deployment events from event log ==="
    Get-WinEvent -LogName "Microsoft-Windows-AppxDeploymentServer/Operational" -MaxEvents 30 -ErrorAction SilentlyContinue |
        Where-Object {$_.Level -le 3} |
        Select-Object -First 15 TimeCreated, Id, LevelDisplayName, Message |
        Format-List
}
```

## When to escalate past this script

- `wuauserv` fails to start even after `sc config wuauserv start= auto` → `DISM /Online /Cleanup-Image /RestoreHealth` (15-30 min)
- `sfc /scannow` reports "found corrupt files but could not fix" → in-place repair install or fresh image
- `Add-AppxPackage` keeps failing with the same error after retry → `Get-AppPackageLog` for root cause
- `Microsoft Store` package disappears entirely (`Get-AppxPackage` returns null) → `wsreset` + `Get-AppxPackage -AllUsers Microsoft.WindowsStore | Reset-AppxPackage` (note: not always supported for built-in Store)
