# Terminal Tool: WSL 迁移后修复

## 问题

Hermes 从 WSL 迁移到 Windows 原生环境后，WSL 被移除，但 `C:\Windows\system32\bash.exe`（WSL 启动器存根）仍残留在系统 PATH 中。
Hermes 的 `_find_bash()` 优先匹配到该存根，导致 `terminal` 工具全线崩溃，返回：
```
WSL_E_LOCAL_SYSTEM_NOT_SUPPORTED
```

## 诊断

```powershell
# 检查哪个 bash 被优先匹配
where bash
# 输出: C:\Windows\system32\bash.exe  ← WSL 残留，已失效

# 测试正确的 bash
"C:\Program Files\Git\bin\bash.exe" -c "echo works"
# 输出: works  ← Git for Windows 的 bash 正常
```

## 修复

### 1. 设置环境变量（推荐）

在 `~/.hermes/.env` 中添加：
```
HERMES_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe
```

同时设置用户级变量（供其他进程继承）：
```powershell
[Environment]::SetEnvironmentVariable("HERMES_GIT_BASH_PATH", "C:\Program Files\Git\bin\bash.exe", "User")
```

Hermes `_find_bash()` 优先读取 `HERMES_GIT_BASH_PATH`，不再依赖系统 PATH 搜索。

### 2. 重装 Hermes（可选）

```bash
cd D:\.hermes
.\venv\Scripts\python.exe -m pip install --upgrade hermes-agent
```

### 3. 重装 Git for Windows（如果 bash.exe 本身也损坏）

```bash
choco upgrade git -y --force
```

## SSH 推送（GitHub 在中国）

HTTPS 推送常被 GFW 阻断。SSH 更可靠：

```bash
export HOME=/c/Users/Aorus
export GIT_SSH_COMMAND="ssh -o ConnectTimeout=30 -o StrictHostKeyChecking=accept-new"
git remote set-url origin git@github.com:jorinyang/awesome-skills.git
git push origin main
```

> `HOME` 必须设置——工具链的 bash 默认为 SYSTEM 账户，`~/.ssh/` 指向 `C:\Windows\system32\config\systemprofile`，不包含用户 SSH 密钥。

## 代理注意事项

Clash/V2Ray 代理（如 `127.0.0.1:7890`）可能拦截 GitHub：
- HTTP CONNECT 隧道成功建立（200）
- 但 TLS Client Hello 后代理丢弃连接
- 这是代理规则将 `github.com` 设为 REJECT 的结果

解决：用 SSH 直连（绕过代理），或在代理规则中将 GitHub 改为 PROXY。
