# Disable Microsoft Store Auto-Update

When the user wants to stop the Store from auto-updating apps (not repair a broken Store),
the approach is different from the repair ladder. This disables the auto-update mechanism
without breaking Store functionality.

## Services to disable

| Service | Display Name | Role |
|---------|-------------|------|
| `UsoSvc` | Update Orchestrator Service | Coordinates both Windows Update and Store updates |
| `WaaSMedicSvc` | WaaSMedicSvc | Auto-repairs Windows Update components when broken |

`wuauserv` (Windows Update) can remain Stopped/Manual — Store depends on it indirectly
but doesn't need it running for basic browsing and install.

## Registry policy (no admin needed for HKLM write)

```powershell
# Disable Store auto-download/install of apps
$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\WindowsStore"
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}
Set-ItemProperty -Path $regPath -Name "AutoDownload" -Value 2 -Type DWord -Force
# AutoDownload values:
#   2 = Never auto-download or install updates
#   3 = Auto-download but don't install (notify)
#   4 = Auto-download and install (default)

# Also disable OS upgrade nag
Set-ItemProperty -Path $regPath -Name "DisableOSUpgrade" -Value 1 -Type DWord -Force
```

## Stop services (can be done without admin for Manual-start services)

```powershell
Stop-Service -Name 'UsoSvc' -Force
Stop-Service -Name 'WaaSMedicSvc' -Force
```

## Set services to Disabled (REQUIRES full admin)

```powershell
# These REQUIRES admin elevation (won't work from WSL context)
Set-Service -Name 'UsoSvc' -StartupType Disabled
Set-Service -Name 'WaaSMedicSvc' -StartupType Disabled
```

If admin elevation unavailable, registry fallback:
```powershell
# Start = 4 means Disabled, 3 = Manual, 2 = Automatic
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\UsoSvc" -Name Start -Value 4 -Type DWord -Force
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\WaaSMedicSvc" -Name Start -Value 4 -Type DWord -Force
```

## Verify

```powershell
Get-Service 'UsoSvc','WaaSMedicSvc','wuauserv' | Format-Table Name, Status, StartType
Get-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\WindowsStore" -Name "AutoDownload"
```
