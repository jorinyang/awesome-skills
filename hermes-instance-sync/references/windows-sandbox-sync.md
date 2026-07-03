# Windows 沙箱环境下的 Repo-to-Local 同步

> 适用于：Hermes 从 WSL 迁移到 Windows 原生环境后，WSL bash 损坏无法使用 `terminal` 工具时的备选方案。

## 问题

1. **`terminal` 工具不可用**：WSL 迁移后 bash 层返回 `WSL_E_LOCAL_SYSTEM_NOT_SUPPORTED`
2. **沙箱路径问题**：`~` 解析为 `C:\Windows\system32\config\systemprofile`，不是 `C:\Users\Aorus`
3. **沙箱 HTTPS 限制**：`git push`/`git ls-remote` 超时（沙箱网络隔离）
4. **WSL 路径不可达**：`/tmp/awesome-skills` 在沙箱的 Windows Python 中无法访问

## 解决方案：Python ZIP 下载流程

### Step 1: 下载 repo ZIP

```python
import urllib.request
import os

HOME = r"C:\Users\Aorus"
TMP = os.path.join(HOME, ".hermes", "tmp")
os.makedirs(TMP, exist_ok=True)

url = "https://api.github.com/repos/jorinyang/awesome-skills/zipball/main"
zip_path = os.path.join(TMP, "awesome-skills.zip")
urllib.request.urlretrieve(url, zip_path)
```

### Step 2: 提取并解包

```python
import zipfile, shutil

extract_dir = os.path.join(TMP, "awesome-skills-extracted")
if os.path.exists(extract_dir):
    shutil.rmtree(extract_dir)

with zipfile.ZipFile(zip_path) as z:
    z.extractall(extract_dir)

# GitHub ZIP 包装了一层 OWNER-REPO-COMMIT/ 目录，需要解包
repo_dir = None
for d in os.listdir(extract_dir):
    full = os.path.join(extract_dir, d)
    if os.path.isdir(full) and os.path.exists(os.path.join(full, "README.md")):
        repo_dir = full
        break
```

### Step 3: 构建仓库清单

```python
repo_skills = {}
for item in os.listdir(repo_dir):
    if item.startswith('.'): continue
    if item == 'README.md': continue
    ipath = os.path.join(repo_dir, item)
    if os.path.isdir(ipath) and os.path.exists(os.path.join(ipath, "SKILL.md")):
        repo_skills[item] = ipath
```

### Step 4: 构建本地清单

```python
local_base = os.path.join(HOME, ".hermes", "skills")  # 注意：绝对路径！
local_skills = {}
for item in os.listdir(local_base):
    if item.startswith('.'): continue
    ipath = os.path.join(local_base, item)
    if os.path.isdir(ipath) and os.path.exists(os.path.join(ipath, "SKILL.md")):
        local_skills[item] = "real"
    elif os.path.islink(ipath):
        local_skills[item] = "symlink"
```

### Step 5: 差分并复制

```python
repo_set = set(repo_skills.keys())
local_set = set(local_skills.keys())
only_repo = repo_set - local_set

for s in only_repo:
    src = repo_skills[s]
    dst = os.path.join(local_base, s)
    if not os.path.exists(dst):
        shutil.copytree(src, dst)
```

### Step 6: 清理

```python
os.remove(zip_path)
shutil.rmtree(extract_dir)
```

## 关键陷阱

- **`~` 路径陷阱**：沙箱中 `os.path.expanduser("~")` 返回 SYSTEM 路径，不是用户路径。始终用 `C:\Users\Aorus` 绝对路径
- **`/tmp/` 不可用**：WSL 的 `/tmp/` 在 Windows Python 中不可访问，也不可通过 `\\wsl$\` 网络路径访问
- **push 必须手动**：沙箱环境无法 `git push`（HTTPS 超时），需用户在本地终端执行
- **git clone 可用但 push 不行**：沙箱可以执行 `git clone`（走 HTTPS），但 `git push`/`git ls-remote` 始终超时

## 与 Mode B 原始流程的关系

原始 Mode B 假设 `bash`/`terminal` 可用、可以 `git clone` 到 `/tmp/`。本参考文件是**沙箱备选方案**——当这些假设不成立时使用。
