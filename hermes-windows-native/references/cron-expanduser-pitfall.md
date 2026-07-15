# Cron `os.path.expanduser("~")` 静默失败陷阱

## 症状

WSL 迁移到 Windows 原生后，cron 定时任务中运行的 Python 脚本使用
`os.path.expanduser("~")` 解析用户路径，但在 SYSTEM 账户环境下 `~` 指向
`C:\Windows\system32\config\systemprofile`，而非用户目录。脚本不会报错，
只是扫描空目录、不做任何事，`last_status` 仍显示 `ok`。

## 典型场景

技能同步脚本 `sync-skills.py` 在 WSL 时正常运行，迁移后 cron 每天运行
但从不创建任何 symlink。

## 代码对比

```python
# ❌ cron 以 SYSTEM 运行时 ~ = C:\Windows\system32\config\systemprofile
DEFAULT = os.path.expanduser("~/.hermes/skills")
FEISHU = os.path.expanduser("~/.hermes-feishu/skills")

# ✅ 使用绝对路径 — 不受当前账户影响
DEFAULT = r"C:\Users\Aorus\.hermes\skills"
FEISHU = r"C:\Users\Aorus\.hermes-feishu\skills"
```

## 诊断

```bash
python3 -c "import os; print(os.path.expanduser('~/.hermes/skills'))"
# 如果返回 C:\Windows\system32\config\systemprofile\.hermes\skills → 需修复
```

## 修复清单

迁移后检查所有 cron `script` 字段引用的 `.py`/`.sh` 脚本，
将 `expanduser("~")` 替换为绝对 Windows 路径。

## 相关的 `C:\c\` 幽灵目录

另一相关迁移残留：MSYS 使用 POSIX 路径 `/c/Users/...` 调用 `write_file`
时可能解析为 `C:\c\Users\...`，产生空目录树。

```bash
# 检测
ls -d /c/c/ 2>/dev/null && echo "幽灵目录存在"

# 清理
rm -rf /c/c/
```

根治：始终用 Windows 原生绝对路径 (`C:/Users/...`)。
