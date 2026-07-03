# Terminal Tool WSL 迁移修复

> 适用场景：WSL 迁移到 Windows 原生后，`terminal` 工具全部返回 `WSL_E_LOCAL_SYSTEM_NOT_SUPPORTED`

## 根因

`C:\Windows\system32\bash.exe`（WSL 启动器）在系统 PATH 中优先级高于 Git Bash。WSL 移除后该文件变成死链接，但 Hermes 的 `_find_bash()` 优先通过 `shutil.which("bash")` 匹配到它。

Hermes `_find_bash()` 搜索顺序：
1. `shutil.which("bash")` → 找到 `C:\Windows\system32\bash.exe`（WSL残留）
2. `HERMES_GIT_BASH_PATH` 环境变量（如设置则直接返回）
3. `%LOCALAPPDATA%\hermes\git\bin\bash.exe`（Hermes内置）
4. `%ProgramFiles%\Git\bin\bash.exe`（标准 Git 安装）

## 修复方法

### 方法1：环境变量覆盖（推荐，无需管理员）

```powershell
# 用户级环境变量
[Environment]::SetEnvironmentVariable(
    "HERMES_GIT_BASH_PATH",
    "C:\Program Files\Git\bin\bash.exe",
    "User"
)
```

在 `.env` 中持久化：
```
HERMES_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe
```

**重启 Hermes 服务后生效。**

### 方法2：删除 WSL 残留（需管理员）

```powershell
# 以管理员身份运行
takeown /f C:\Windows\system32\bash.exe
icacls C:\Windows\system32\bash.exe /grant Everyone:F
ren C:\Windows\system32\bash.exe bash.exe.wsl_disabled
```

## 验证

修复后第一个命令应正常输出：
```bash
echo "test"
# 预期: test
```

## 相关

- 如果终端工具仍不可用，使用 `execute_code` 备选方案（见 `references/windows-sandbox-sync.md`）
- WSL 完全移除后 `LxssManager` 服务不存在，`wsl --shutdown` 等命令全部失效
