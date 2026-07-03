# Windows OpenSSH Server Repair

## Symptom

SSH connection fails immediately after TCP handshake with "end of file" error. Connections establish (DNS resolves, TCP connects), but SSH session terminates instantly without reaching authentication. Client sees:

```
ssh_exchange_identification: Connection closed by remote host
```
or
```
Connection closed by 192.168.x.x port 22
```

## Root causes (in descending order of likelihood)

### 1. sshd service is STOPPED (80% of cases)

```bash
sc query sshd
# STATE: 1 STOPPED → start it
sc start sshd
```

### 2. `Match Group administrators` points to non-existent authorized_keys file

This is the #2 most common cause and produces the exact same symptom as service-down.

**How it happens:** The default `C:\ProgramData\ssh\sshd_config` contains:

```
Match Group administrators
       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```

When the user connecting (e.g. `aorus`) is a member of the `Administrators` group, sshd uses THIS authorized_keys path instead of `%USERPROFILE%\.ssh\authorized_keys`. If `administrators_authorized_keys` doesn't exist, sshd closes the connection immediately — before any authentication prompt.

**Diagnosis:**
```bash
# Check if the file exists
ls -la "C:\ProgramData\ssh\administrators_authorized_keys"
# "No such file or directory" → this is the problem

# Check if the Match block is active
cat "C:\ProgramData\ssh\sshd_config" | grep -A2 "Match Group administrators"
```

**Fix — option A (preferred): Comment out the Match block**
This lets sshd fall back to the default `%USERPROFILE%\.ssh\authorized_keys`:
```bash
# Edit C:\ProgramData\ssh\sshd_config
# Change:
#   Match Group administrators
#          AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
# To:
#   #Match Group administrators
#   #       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys

sc stop sshd && sc start sshd
```

**Fix — option B: Create the administrators_authorized_keys file**
```bash
# Copy user's existing authorized_keys
cp "C:\Users\Aorus\.ssh\authorized_keys" "C:\ProgramData\ssh\administrators_authorized_keys"

# CRITICAL: Set correct permissions (Windows OpenSSH enforces them strictly)
# Administrators: Full Control, SYSTEM: Full Control
icacls "C:\ProgramData\ssh\administrators_authorized_keys" /inheritance:r
icacls "C:\ProgramData\ssh\administrators_authorized_keys" /grant "SYSTEM:(F)" /grant "Administrators:(F)"

sc stop sshd && sc start sshd
```

### 3. Default shell misconfigured

Check `C:\ProgramData\ssh\sshd_config` for a `# override default of no subsystems` line. The subsystem should be:

```
Subsystem	sftp	sftp-server.exe
```

If you see a custom shell path (e.g. `C:\cygwin\bin\bash.exe`) pointing to a non-existent executable, sshd will accept the connection but fail to spawn a shell. Fix: comment it out or point to a valid shell.

## Verification

```bash
# 1. Confirm sshd is RUNNING
sc query sshd
# STATE: 4 RUNNING

# 2. Confirm port is LISTENING
netstat -ano | grep ':22 '
# TCP  0.0.0.0:22  0.0.0.0:0  LISTENING  <pid>

# 3. Test local connection with verbose output
ssh -vvv -o StrictHostKeyChecking=no -o ConnectTimeout=5 -p 22 aorus@127.0.0.1 "echo SUCCESS" 2>&1
# Should see: "Authentications that can continue: publickey,password,keyboard-interactive"
# If it reaches this line, the handshake is healthy — only auth is blocking
```

## Diagnostic cheat sheet

| What you see | What it means | Action |
|---|---|---|
| `ssh: connect to host ... port 22: Connection refused` | sshd not running or port wrong | `sc start sshd` |
| `Connection closed by remote host` immediately | sshd running but `administrators_authorized_keys` missing | Comment out Match block |
| Connects but never prompts for password | Shell spawn failure or TTY issue | Check `Subsystem sftp` line in sshd_config |
| Timeout after `SSH2_MSG_SERVICE_ACCEPT` | Auth method mismatch or firewall deep-packet inspection | Check firewall, try different client |
