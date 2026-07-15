# WSL_E_LOCAL_SYSTEM_NOT_SUPPORTED 错误诊断

## 症状

Hermes 终端工具所有命令返回乱码，解码后为 UTF-16LE 编码的：
```
bash/WSL_E_LOCAL_SYSTEM_NOT_SUPPORTED
```

## 根因

`shutil.which("bash")` 在 PATH 中找到了 `C:\Windows\system32\bash.exe`，这是 WSL 启动器。
WSL 迁移/移除后，该文件仍然存在但无法运行，返回 `WSL_E_LOCAL_SYSTEM_NOT_SUPPORTED`。

Git for Windows 的正确 bash 在 `C:\Program Files\Git\bin\bash.exe`，但 PATH 优先级低于 system32。

## 修复

1. 设置 `HERMES_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe`（`.env` + 用户环境变量）
2. 或在 `local.py` 第 290 行附近修改 `_find_shell` 逻辑

## 切换至 PowerShell（推荐）

```
HERMES_SHELL=powershell
```

修改 `tools/environments/local.py`：
- 添加 `_find_powershell()` 函数
- 修改 `_run_bash()` 支持 `-NoProfile -Command` 参数
- 跳过 MSYS 路径转换

## 验证

```python
import shutil
# 修复前：返回 C:\Windows\system32\bash.exe
# 修复后：返回 C:\Program Files\Git\bin\bash.exe 或 None
print(shutil.which("bash"))
```
