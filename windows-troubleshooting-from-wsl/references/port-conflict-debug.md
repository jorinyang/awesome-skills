# Port Conflict Debugging Transcript

Real session where `127.0.0.1:8787` was unreachable despite portproxy
and wslrelay being active. Root cause: 3-way port competition.

## Environment

- WSL2 with mirrored networking (WSL IP: `172.24.49.212/20`)
- Service: Hermes WebUI on `0.0.0.0:8787` (confirm with `ss -tlnp | grep 8787`)
- Windows host IP from WSL: `172.24.48.1`

## Symptom

```bash
# Works: direct WSL IP from Windows
curl http://172.24.49.212:8787  # → 200 OK

# Fails: localhost from Windows browser
# Browser shows: "无法连接到 hermes" / "connection forcibly closed"
```

## Diagnosis Steps

### Step 1: Check what's actually listening

```powershell
netstat -ano | findstr ":8787"
```

Output showed THREE entries on LISTENING:
```
TCP    127.0.0.1:8787    LISTENING    11324   ← ssh.exe
TCP    127.0.0.1:8787    LISTENING    32524   ← wslrelay.exe
TCP    [::1]:8787        LISTENING    11324   ← ssh.exe (IPv6)
```

Plus the netsh portproxy rule (not shown in netstat but present).

### Step 2: Identify the processes

```powershell
Get-Process -Id 11324 | Format-Table Id,ProcessName,Path
# → ssh.exe  C:\Windows\System32\OpenSSH\ssh.exe

Get-Process -Id 32524 | Format-Table Id,ProcessName,Path
# → wslrelay.exe  C:\Program Files\WSL\wslrelay.exe
```

### Step 3: Inspect ssh.exe command line

```powershell
Get-WmiObject Win32_Process -Filter 'ProcessId=11324' | Select CommandLine
# → ssh.exe -L 8787:localhost:8788 yangyang@yangchangdeMacBook-Pro.local
```

The SSH tunnel was forwarding `127.0.0.1:8787` to `localhost:8788` on a
remote MacBook. Since nothing useful was listening on MacBook:8788,
connections that happened to hit ssh.exe first would fail.

### Step 4: Clean up

```bash
# Kill ssh tunnel
powershell.exe -NoProfile -Command 'Stop-Process -Id 11324 -Force'

# Remove redundant portproxy (needs UAC)
powershell.exe -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -Command \"netsh interface portproxy delete v4tov4 listenport=8787 listenaddress=127.0.0.1\"'"
```

### Step 5: Verify

```powershell
# Only wslrelay should remain
netstat -ano | findstr ":8787"
# → TCP  127.0.0.1:8787  LISTENING  32524  (wslrelay only)

# HTTP check from Windows PowerShell
Invoke-WebRequest http://127.0.0.1:8787 -UseBasicParsing -TimeoutSec 5
# → StatusCode: 200 OK
```

## Key Takeaways

1. **Multiple processes CAN bind to the same port on Windows** (via
   `SO_REUSEADDR`). The first to accept wins — this creates
   non-deterministic failures where the port "sometimes works".

2. **ssh.exe tunnels are invisible port thieves**. They show up in
   `netstat` but not in obvious process lists. Always check the command
   line to see where they're forwarding.

3. **netsh portproxy + wslrelay = redundant conflict**. WSL2's
   `wslrelay.exe` already auto-forwards WSL ports to Windows localhost.
   Adding portproxy creates a competing listener with no benefit.

4. **`browser_navigate` to 127.0.0.1 is a false positive**. Browserbase
   runs on cloud servers — its localhost is not the user's machine.
   Always use `powershell.exe Invoke-WebRequest` or `Test-NetConnection`
   for local connectivity tests from WSL.
