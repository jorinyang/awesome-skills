# 终端 PowerShell 回退问题 — 诊断与修复

## 症状

终端工具 (`terminal`) 每次调用都失败，返回 PowerShell 解析错误：

```
所在位置 行:1 字符: 97
+ ... hu/cache/terminal/hermes-snap-78ac626e9bca.sh >/dev/null 2>&1 || true
+                                                                   ~~
标记'||'不是此版本中的有效语句分隔符
```

关键特征：
- 错误格式是 **PowerShell**（`所在位置 行:1 字符:97`），不是 bash
- `||` 是 bash 语法，PowerShell 不支持
- 所有命令在会话初始化脚本阶段就失败，用户命令根本没执行

## 根因

终端后端 `tools/environments/local.py` 中的 `_find_bash()` 负责定位 Git Bash。它首先检查 `os.environ.get("HERMES_GIT_BASH_PATH")`。当此环境变量：
1. 在 Python 进程中未设置 → `_find_bash()` 返回空/错误值
2. 终端包装器脚本（`_wrap_command()`）使用 bash 语法，但被传递给错误的 shell

**为什么 .env 有设置但进程没有**：
- `.env` 文件在 Hermes 启动时加载到 Python 进程
- 不同 session 类型（webui vs feishu gateway vs CLI）可能加载不同的 .env
- SYSTEM 账户运行的服务可能从 `C:\Windows\system32\config\systemprofile\.hermes\.env` 加载，而不是用户目录

## `_find_bash()` 完整回退链

```python
# 1. 显式环境变量
custom = os.environ.get("HERMES_GIT_BASH_PATH")

# 2. PortableGit（Hermes 自带）
os.path.join(os.environ.get("LOCALAPPDATA"), "hermes", "git", "bin", "bash.exe")

# 3. MinGit（旧版回退）
os.path.join(os.environ.get("LOCALAPPDATA"), "hermes", "git", "usr", "bin", "bash.exe")

# 4. 系统 Git
os.path.join(os.environ.get("ProgramFiles"), "Git", "bin", "bash.exe")

# 5. 32 位 Git
os.path.join(os.environ.get("ProgramFiles(x86)"), "Git", "bin", "bash.exe")

# 6. 用户级 Git
os.path.join(os.environ.get("LOCALAPPDATA"), "Programs", "Git", "bin", "bash.exe")
```

**注意**：回退链使用 `os.environ.get()`，在 Python 进程环境中取值。如果 `ProgramFiles` 等系统变量存在（通常存在），回退 **应该** 能找到 bash。但在某些 session 上下文中可能全部失败。

## 诊断步骤

### 1. 检查 Python 进程环境

```python
import os
print(f"HERMES_GIT_BASH_PATH = {os.environ.get('HERMES_GIT_BASH_PATH', 'NOT SET')}")
print(f"ProgramFiles = {os.environ.get('ProgramFiles', 'NOT SET')}")
print(f"HERMES_HOME = {os.environ.get('HERMES_HOME', 'NOT SET')}")
print(f"HOME = {os.environ.get('HOME', 'NOT SET')}")
```

### 2. 验证 bash.exe 存在

```python
import os
path = os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Git", "bin", "bash.exe")
print(f"Fallback: {path}")
print(f"Exists: {os.path.exists(path)}")
```

### 3. 检查所有 .env 文件

```bash
# 当前 profile
cat "$HERMES_HOME/.env" | grep GIT_BASH

# Python 进程 HOME
cat "$HOME/.hermes/.env" | grep GIT_BASH

# Windows 真实用户目录
cat /c/Users/Aorus/.hermes/.env | grep GIT_BASH
cat /c/Users/Aorus/.hermes-feishu/.env | grep GIT_BASH
```

## 修复方案

### 方案 A：写入所有相关 .env（推荐）

```bash
echo 'HERMES_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe' >> /c/Users/Aorus/.hermes/.env
echo 'HERMES_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe' >> /c/Users/Aorus/.hermes-feishu/.env
echo 'HERMES_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe' >> /c/Windows/System32/config/systemprofile/.hermes/.env
```

然后重启网关：`hermes gateway restart`

### 方案 B：execute_code 绕过（即时可用）

当终端不可用但需要立即执行 shell 命令时：

```python
import subprocess, os
bash_path = r"C:\Program Files\Git\bin\bash.exe"
env = {**os.environ, "HOME": "/c/Users/Aorus"}
result = subprocess.run([bash_path, "-c", "你的命令"], capture_output=True, text=True, env=env)
```

### 方案 C：代码级修复（长期）

在 `tools/environments/local.py` 的 `_find_bash()` 中增加更健壮的回退：

```python
# 在回退链末尾增加硬编码路径检查
_HARDCODED_FALLBACKS = [
    r"C:\Program Files\Git\bin\bash.exe",
]
for p in _HARDCODED_FALLBACKS:
    if os.path.isfile(p):
        return p
```

## 已验证的触发场景

| 场景 | HERMES_GIT_BASH_PATH | 结果 |
|------|---------------------|------|
| Feishu gateway session | 未设置（.env有但未加载） | 终端失败 |
| Cron job (hermes-feishu profile) | 已设置（snap中可见） | 终端可用 |
| WebUI session | 取决于代理目录 .env | 可变 |

## 相关代码路径

- `tools/environments/local.py::LocalEnvironment._run_bash()` — 终端命令入口
- `tools/environments/local.py::_find_bash()` — bash 定位逻辑
- `tools/environments/base.py::BaseEnvironment._wrap_command()` — 会话初始化脚本生成
- `tools/environments/base.py::BaseEnvironment.init_session()` — 环境快照创建
