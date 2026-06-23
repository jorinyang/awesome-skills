# CPU Monitor — long-running background sampler
# Usage: powershell -ExecutionPolicy Bypass -File cpu-monitor.ps1
# Output: cpu_monitor.log in current directory

$duration_minutes = 20
$interval_seconds = 10
$total_samples = ($duration_minutes * 60) / $interval_seconds
$logfile = "cpu_monitor.log"

"=== CPU Monitor Started at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $logfile
"Duration: $duration_minutes min, Interval: ${interval_seconds}s, Samples: $total_samples" | Out-File $logfile -Append
"" | Out-File $logfile -Append

$sample = 0
$alerts = @()

while ($sample -lt $total_samples) {
    $sample++
    $ts = Get-Date -Format 'HH:mm:ss'
    $top = Get-Process | Sort-Object CPU -Descending | Select-Object -First 5
    $total_cpu = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
    $entry = "[$ts] Sample $sample/$total_samples | CPU Load: $total_cpu%"
    
    $high_cpu = @()
    foreach ($p in $top) {
        if ($p.CPU -gt 10) {
            $detail = "$($p.ProcessName) (PID $($p.Id)): CPU=$([math]::Round($p.CPU,1))s"
            $high_cpu += $detail
        }
    }
    if ($high_cpu.Count -gt 0) {
        $entry += " | High: " + ($high_cpu -join ", ")
    }
    $entry | Out-File $logfile -Append

    $cua = Get-Process -Name 'cua-driver*' -ErrorAction SilentlyContinue
    if ($cua) {
        "[$ts] [WARN] cua-driver detected: PID=$($cua.Id) CPU=$($cua.CPU)s" | Out-File $logfile -Append
        $alerts += "[$ts] cua-driver PID=$($cua.Id)"
    }

    $store = Get-Process | Where-Object { $_.ProcessName -match 'wsappx|wuauclt|usoclient|dosvc|waasmedic' } -ErrorAction SilentlyContinue
    if ($store) {
        "[$ts] [WARN] Store/Update process: $($store.ProcessName) PID=$($store.Id)" | Out-File $logfile -Append
        $alerts += "[$ts] $($store.ProcessName) PID=$($store.Id)"
    }
    
    Start-Sleep -Seconds $interval_seconds
}

"" | Out-File $logfile -Append
"=== CPU Monitor Completed at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $logfile -Append
if ($alerts.Count -gt 0) {
    "`n=== ALERTS ($($alerts.Count)) ===" | Out-File $logfile -Append
    $alerts | Out-File $logfile -Append
}
Write-Host "Monitor complete. $total_samples samples. $($alerts.Count) alerts. Log: $logfile"
