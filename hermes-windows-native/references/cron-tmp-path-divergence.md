# Cron / Windows 下 `/tmp` 路径分叉陷阱

## 症状

脚本里同时使用 bash 和 Python（或 `write_file` 工具）操作 `/tmp/foo.txt`，
bash 能写入成功、Python `open('/tmp/foo.txt')` 却报
`FileNotFoundError`。或者反过来：`write_file('/tmp/report.md')` 写入成功，
但下一个 bash 调用 `cat /tmp/report.md` 找不到文件。

## 三个工具看到的是三个不同目录

| 工具 | `/tmp` 解析到 | 备注 |
|------|--------------|------|
| bash (MSYS / Git Bash) | `C:\Windows\Temp` (system TEMP) | `mount` 显示 `C:/Windows/TEMP on /tmp type ntfs` |
| Python (`/tmp/...`) | `C:\Windows\Temp` (system TEMP) | `tempfile.gettempdir()` 返回 `C:\Windows\TEMP` |
| Hermes `write_file` (绝对路径 `/tmp/...`) | **`C:\tmp\` (literal, drive root)** | 写到用户家之外的根目录，与终端 cwd 不一致 |

## 验证

```python
import os, tempfile
print('python expanduser /tmp →', os.path.realpath('/tmp'))
print('tempfile.gettempdir  →', tempfile.gettempdir())
```

```bash
# bash 这边
ls -la /tmp/scores_*.tsv 2>&1 | head -3
mount | grep tmp
```

## 修复方案

**方案 A（推荐）**：统一用 Windows 原生绝对路径，跨工具都能找到：

```bash
# 三个工具都能解析到同一物理位置
echo data > C:/Windows/Temp/scores.tsv
# 或写脚本阶段用用户目录
echo data > C:/Users/Aorus/AppData/Local/Temp/scores.tsv
```

**方案 B**：临时文件全部写在用户工作区下 (`C:/tmp/work`)，
保证不被系统清理且三个工具都看得到同一棵子树。

**方案 C（仅调试用）**：在 Python 里显式给完整路径：

```python
# 不要写
with open('/tmp/scores.tsv') as f: ...
# 写
with open('C:/Windows/Temp/scores.tsv') as f: ...
```

## 相关陷阱：`write_file` 的 workspace 相对路径

`write_file('/tmp/foo')` 会警告：
> Relative path '/tmp/foo' resolved to 'C:\tmp\foo', which is OUTSIDE the active workspace

`write_file` 解析绝对路径时把它当作字面字符串，
不像 bash/Python 走 `%TEMP%`。如果当前 cwd 是 git 工作区，
而你又要写共享临时文件，要么走方案 A 要么走用户家目录：
`C:/Users/Aorus/AppData/Local/Temp/foo`。

## 根因诊断清单

1. 想确认三个工具指向同一物理位置：
   ```bash
   bash$:  ls -la /tmp/
   python: import os; print(os.listdir('/tmp')[:5])
   ```
2. 看 `write_file` 的实际落点：检查 `Resolved path:` 警告字段。
3. cron's `working_directory` 决定了 bash 的 cwd（默认 `C:\Users\Aorus\workspace`），
   `/tmp` 解析与 cwd **无关**，仅依赖 MSYS mount 表。

## 与 `expanduser` 陷阱的差异

- `expanduser('~')` 问题：HOME 错误，~ 指向 `systemprofile`。
- 本陷阱：HOME 正确，三个工具对 `/tmp` 都有合法解析，
  但 `write_file` 的解析路径不遵守 MSYS mount，把 `/tmp` 当字面路径。

两个陷阱互相独立，可在同一脚本里同时踩到。
