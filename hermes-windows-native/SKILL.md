---
name: hermes-windows-native
description: Configure and troubleshoot Hermes Agent on native Windows (post-WSL).
version: 1.2.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [windows, hermes, terminal, powershell, wsl-migration, troubleshooting]
    related_skills: [systematic-debugging]
---

# Hermes Windows Native — 配置与排障

Hermes Agent 在原生 Windows 环境（非 WSL）的配置、终端后端切换、网络推送及故障诊断。

## 触发条件

- Hermes 终端工具返回异常（`WSL_E_LOCAL_SYSTEM_NOT_SUPPORTED`）
- WSL 已移除/迁移，需要将终端后端从 bash 切换至 PowerShell
- `git push` 到 GitHub 超时或失败
- Hermes 命令在 Windows 上行为异常

---

## 终端后端配置

### Shell 选择机制

Hermes Windows 终端后端 (`tools/environments/local.py`) 通过 `_find_bash()` 定位 Git Bash：

**查找优先级**:
1. `os.environ.get("HERMES_GIT_BASH_PATH")` — 环境变量显式指定
2. `%LOCALAPPDATA%\hermes\git\bin\bash.exe` — PortableGit（Hermes 自带，优先）
3. `%LOCALAPPDATA%\hermes\git\usr\bin\bash.exe` — MinGit（旧版回退）
4. `%ProgramFiles%\Git\bin\bash.exe` — 系统 Git
5. `%ProgramFiles(x86)%\Git\bin\bash.exe` — 32 位 Git
6. `%LOCALAPPDATA%\Programs\Git\bin\bash.exe` — 用户级 Git

**关键**: `_find_bash()` 在 Python 进程中运行，读取的是 **Python 进程的环境变量**，不是 bash 子进程的环境。`.env` 文件只在 Hermes 启动时加载到 Python 进程，因此修改 `.env` 后**必须重启网关**才能生效。

### 手动指定 Git Bash 路径

```bash
# 在 .env 文件中（所有相关位置都需设置）
HERMES_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe
```

**注意**: Hermes 可能从多个 profile 读取 `.env`。检查以下位置：
- `%HERMES_HOME%\.env` — 当前 profile 的 .env
- `%HOME%\.hermes\.env` — Python 进程 HOME 下的 .env（Windows 服务/SYSTEM 账户下可能是 `C:\Windows\system32\config\systemprofile\.hermes\.env`）

---

## 诊断流程

### 终端工具无响应 / 返回乱码

**症状 A**: 终端返回 PowerShell 解析错误（`标记'||'不是此版本中的有效语句分隔符`），即使 `HERMES_GIT_BASH_PATH` 在 `.env` 中已设置。

**根因**: `HERMES_GIT_BASH_PATH` 不在 **Python 进程环境**中。`.env` 文件虽然在磁盘上，但未被加载到当前会话的 Python 进程。

**诊断**:
```python
import os
print(os.environ.get('HERMES_GIT_BASH_PATH', 'NOT SET'))
# 如果返回 NOT SET → 终端后端回退失败，bash 语法被 PowerShell 解析
```

**修复**:
1. 确保所有相关 `.env` 文件都有该设置（见上方"手动指定 Git Bash 路径"）
2. 重启网关：`hermes gateway restart`
3. `.env` 在 Hermes 启动时加载，修改后必须重启

**症状 B**: 终端完全无响应或返回其他异常。

1. 确认 WSL 状态：
```powershell
wsl --status
Get-Service LxssManager  # 不存在 = WSL 已移除
```

2. 检查 bash 解析：
```python
import shutil
shutil.which("bash")  # 如果返回 C:\Windows\system32\bash.exe → WSL 残留
```

3. 检查 `HERMES_GIT_BASH_PATH` 是否生效：
```
HERMES_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe
```

4. 测试正确的 bash：
```bash
"C:\Program Files\Git\bin\bash.exe" -c "echo test"
```

### GitHub 推送失败

**症状**: `git push` 超时，TLS 握手成功但数据层挂起。

**诊断**:
```bash
GIT_CURL_VERBOSE=1 git push origin main 2>&1 | head -20
```

**方案优先级**:

1. **SSH 推送**（最可靠）：
```bash
export HOME=/c/Users/Aorus
git remote set-url origin git@github.com:jorinyang/awesome-skills.git
git push origin main
```

2. **代理推送**（需代理允许 GitHub）：
```bash
git config --local http.proxy http://127.0.0.1:7890
git config --local https.proxy http://127.0.0.1:7890
```

3. **gh CLI**（需 token）：
```bash
gh release create vX.Y.Z --title "..." --notes "..."
```

### 模块热加载

修改 `tools/environments/local.py` 后无需重启 Hermes：

```python
import importlib, os, sys
os.environ['HERMES_SHELL'] = 'powershell'
if 'tools.environments.local' in sys.modules:
    importlib.reload(sys.modules['tools.environments.local'])
```

---

## 用户偏好

### 命令执行
- **主动执行，不要求用户手动操作。** 能用工具完成的就不要推给用户。
- 网络受限时尝试多种方案（SSH/代理/gh CLI）而非放弃。
- 推送 GitHub 时使用 SSH + `HOME=/c/Users/Aorus` 方案。

### 版本号
- 从最小版本开始更新：`v5.2.1` → `v5.2.2`（PATCH），非必要不升级 MINOR。

---

## 常见陷阱

- `C:\Windows\system32\bash.exe` 是 WSL 启动器，WSL 移除后变成死链接。确保 `HERMES_GIT_BASH_PATH` 已设置。

### 终端不可用时的绕过方案

当终端工具完全不可用（如 PowerShell 解析 bash 语法错误），使用 `execute_code` + `subprocess` 直接调用 Git Bash：

```python
import subprocess, os

bash_path = r"C:\Program Files\Git\bin\bash.exe"
env = {**os.environ, "HOME": "/c/Users/Aorus"}

result = subprocess.run(
    [bash_path, "-c", "你的命令"],
    capture_output=True, text=True, timeout=30,
    env=env
)
print(result.stdout)
```

**关键点**:
- 必须显式设置 `HOME=/c/Users/Aorus`（SYSTEM 账户下 HOME 指向 systemprofile）
- npm 全局工具需额外添加 PATH：`env["PATH"] = "/c/Users/Aorus/AppData/Roaming/npm:" + env.get("PATH", "")`
- 此方案绕过终端会话初始化脚本，直接调用 bash，不依赖 `HERMES_GIT_BASH_PATH` 环境变量

- `os.environ['HOME']` 在 SYSTEM 账户下指向错误路径（`C:\\Windows\\system32\\config\\systemprofile`），导致 Git/SSH 找不到密钥。显式 `export HOME=/c/Users/Aorus`。
- **Cron 脚本 `expanduser("~")` 静默失败** — 迁移后 cron 以 SYSTEM 运行时 `~` 指向 `systemprofile`，脚本扫描空目录但 `last_status=ok`。详见 `references/cron-expanduser-pitfall.md`。

### MSYS2 Cron PATH 找不到 npm 全局工具

**症状：** cron 任务报 `command not found: lark-cli`（或其他 npm 全局工具），但终端直接执行正常。

**根因：** cron 运行在 SYSTEM 用户的 git-bash/MSYS2 下，MSYS2 的 PATH 由 `/etc/profile.d/*.sh` 构建，**不自动继承** Windows 系统 PATH。`[Environment]::SetEnvironmentVariable('Path', ..., 'Machine')` 只影响 Windows 进程，不影响 MSYS2。

**修复：** 在 MSYS2 profile.d 中声明 PATH：

```bash
# C:\Program Files\Git\etc\profile.d\npm_path.sh
NPM_BIN="/c/Users/Aorus/AppData/Roaming/npm"
case ":$PATH:" in
  *":$NPM_BIN:"*) ;;
  *) export PATH="$PATH:$NPM_BIN" ;;
esac
```

验证：`/bin/bash -lc 'lark-cli --version'`

**注意：** `write_file` 用 Unix 路径（`/etc/profile.d/`）在 Windows 会上解析到 `C:\etc\`（错误），必须用 Windows 绝对路径 `C:/Program Files/Git/etc/profile.d/`。

详见 `references/msys2-cron-path.md`。

---

## 相关文件

- `D:\.hermes\tools\environments\local.py` — 终端后端核心代码
- `~/.hermes\.env` — 环境变量持久化
- `~/.hermes\config.yaml` — `terminal.backend: local` 配置
- `references/wsl-bash-diagnosis.md` — WSL 残留 bash.exe 诊断与修复
- `references/github-push-china.md` — 中国大陆 GitHub 推送策略
- `references/terminal-powershell-fallback.md` — 终端 PowerShell 回退问题完整诊断与修复
- `references/cron-expanduser-pitfall.md` — Cron 脚本 `expanduser("~")` 静默失败陷阱与 C:\c\ 幽灵目录清理
- `references/cron-tmp-path-divergence.md` — Windows 下 bash / Python / write_file 对 `/tmp` 的不同解析陷阱（三个工具指向三处不同物理目录的诊断与方案 A/B/C）
- `references/cron-provider-timeout-fix.md` — Cron job provider timeout 诊断与修复（含 `cronjob update` 只传 model 会静默重置 enabled_toolsets 的陷阱）
- `references/msys2-cron-path.md` — MSYS2 cron 环境找不到 npm 全局工具（lark-cli 等）的根因与修复：profile.d 脚本而非 Windows 系统 PATH
