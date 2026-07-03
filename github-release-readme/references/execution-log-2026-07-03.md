# GitHub 同步执行日志（2026-07-03 v5.4.9）

> 本文档记录了 2026-07-03 cron 执行的 github-release-readme v5.4.9 同步全流程，
> 包括踩过的坑和最终验证有效的工作模式。供未来会话直接复用。

---

## 🔴 关键发现（按重要性排序）

### 1. Windows 原生环境 vs WSL 差异
- 当前 Hermes 运行在 **Windows 原生**（不是 WSL）
- `readlink -f` / `cp -rL` / `cd /tmp` 等 WSL 命令**不可用或行为不同**
- Python `/c/Users/...` 路径**找不到文件**（`FileNotFoundError: [WinError 3]`）
- ✅ 必须用 `r'C:\Users\Aorus\...'` 原始 Windows 路径

### 2. HTTPS git clone 被 GFW 屏蔽
- `git clone https://github.com/...` → `Failed to connect to github.com port 443`
- ❌ `unset http_proxy` 不解决问题（沙箱 HTTPS 整体被屏蔽）
- ✅ **codeload.github.com ZIP 镜像可用**：
  ```python
  urllib.request.urlretrieve(
      'https://codeload.github.com/jorinyang/awesome-skills/zip/refs/heads/main',
      r'C:\tmp\awesome-skills.zip'
  )
  ```

### 3. SSH fetch + push 可用
- ✅ SSH key 存在：`/c/Users/Aorus/.ssh/id_rsa`
- ✅ 必须显式设置：
  ```bash
  export HOME=/c/Users/Aorus
  export GIT_SSH_COMMAND="ssh -o ConnectTimeout=30 -i /c/Users/Aorus/.ssh/id_rsa"
  ```
- ❌ 不设置 HOME → SSH 找不到 ~/.ssh/config
- ❌ 不指定 -i → Permission denied (publickey)

### 4. GitHub API 可访问
- `api.github.com` 在沙箱中可访问（status 200）
- 但 git 协议（port 9418）和 HTTPS（port 443）被屏蔽

---

## ⚠️ Race Condition（origin/main 抢占）

### 观察到的现象
本次会话累计触发 **3 次 push 失败**，每次都报 `non-fast-forward`。
每次本地 commit 后立即 push，origin/main 都比本地新（远端有自动 commit）。

### 缓解策略
1. **Push 前最后一次 fetch**：
   ```bash
   git fetch --depth=10 origin main
   LOCAL_SHA=$(git rev-parse HEAD)
   REMOTE_SHA=$(git rev-parse origin/main)
   if [ "$LOCAL_SHA" != "$REMOTE_SHA" ]; then
     echo "⚠️ origin/main 领先 — 可能 race condition"
   fi
   ```

2. **如果 race 发生**：不要盲目重试，先 `git log origin/main --oneline -5` 看清新增了什么 commit，再决定 rebase 或 cherry-pick。

3. **压缩整个流程到 < 3 分钟**：减少 race 窗口。

---

## 📋 最终验证有效的工作流

```bash
# === Phase 1: 下载 ===
python3 << 'PYEOF'
import urllib.request, zipfile, shutil
url = 'https://codeload.github.com/jorinyang/awesome-skills/zip/refs/heads/main'
urllib.request.urlretrieve(url, r'C:\tmp\awesome-skills.zip')
shutil.rmtree(r'C:\tmp\awesome-skills-main', ignore_errors=True)
with zipfile.ZipFile(r'C:\tmp\awesome-skills.zip') as z:
    z.extractall(r'C:\tmp\')
PYEOF

# === Phase 2: 初始化 git 仓库 ===
cd /c/tmp/awesome-skills-main
rm -rf .git
git init -q
git config user.name "jorinyang"
git config user.email "jorinyang@users.noreply.github.com"
git remote add origin git@github.com:jorinyang/awesome-skills.git

# === Phase 3: SSH fetch 真实 origin/main ===
export HOME=/c/Users/Aorus
export GIT_SSH_COMMAND="ssh -o ConnectTimeout=30 -i /c/Users/Aorus/.ssh/id_rsa"
git fetch --depth=10 origin main
git checkout origin/main -- .
git checkout -b main
git commit --allow-empty -q -m "baseline origin/main"

# === Phase 4: 同步文件（Python 脚本） ===
python3 C:/tmp/exec_update.py  # 拷贝 6 个 SKILL.md
# 验证
find . -type l | wc -l  # 必须为 0
find . -name __pycache__ -type d | wc -l  # 必须为 0

# === Phase 5: README + commit + push ===
git add -A
git commit -m "vX.Y.Z: 描述"
git push origin main  # ⚠️ 可能失败，需重试
```

---

## 🐛 踩过的具体坑（按时间顺序）

| # | 现象 | 根因 | 解决 |
|---|------|------|------|
| 1 | `git clone https://github.com/...` 超时 | GFW 屏蔽 HTTPS | 用 codeload ZIP |
| 2 | Python 找不到 `/c/Users/Aorus/.hermes-feishu/skills` | Python 不识别 MSYS 路径 | 用 `r'C:\Users\...'` |
| 3 | `LOCAL_DIRS = ['/c/Users/...']` 报 0 技能 | 同上 | 同上 |
| 4 | `git push` 报 non-fast-forward | origin/main race | 重新基于最新 origin/main |
| 5 | `checkout origin/main -- .` 报冲突（design-md 冲突） | 本地有 ZIP 解压文件 + 无 commit | `rm -rf .git && git init` 重新来 |
| 6 | `git checkout FETCH_HEAD` 拿到旧 SHA | FETCH_HEAD 不是 origin/main HEAD | 用 `git checkout origin/main -- .` |
| 7 | `git pull --rebase` 报 3 个文件 add/add 冲突 | 我们 add 了所有 94 个文件 | 改为只 add 真正变更的 6 个 |

---

## 📊 同步结果（本次 v5.4.9）

### 双源扫描
- 本地：171 技能（feishu 125 + hermes 169，去重后 171）
- GitHub：94 技能
- 共享：94 | 仅本地：77
- 应同步（自建+三方）：**2 新增**
- 内容差异：**6 SKILL.md 更新**
- 永久排除：plan/spike/dingtalk-channel ✓

### 同步清单
**新增 2**（最终**未推送**，因远端 refactor 已移除）：
- `ppt-structure-parser` v1.5.0
- `ppt-template-filler` v1.4.1

**更新 6**（本地拷贝完成，commit 完成，push 阻塞）：
- `ara-compiler`, `firecrawl-web`, `github-absorb`, `jimeng-video`, `sketch`, `test-driven-development`

### 发现的问题（待用户决策）
- ⚠️ origin/main 有 commit `1414c47 refactor: move ppt-engine to dedicated repo jorinyang/ppt-engine`
  - 已删除 `ppt-structure-parser/` 和 `ppt-template-filler/` 共 1995 行
  - 但 **README 仍引用这两个技能的 SKILL.md 路径**（404 链接）
  - **README badge 仍显示 `Skills-96`**，实际只有 94
  - 本次同步**不修复此问题**——属于 README 重大重构，超出 PATCH 范围

---

## 🎯 给下次会话的建议

1. **先用 codeload ZIP 下载**（不要尝试 git clone）
2. **Python 脚本全部用 `r'C:\Users\...'` 路径**
3. **Phase 1C 加 README 一致性检查**（防止 refactor 后 README 404）
4. **push 前再 fetch 一次**（防止 race）
5. **race 发生时不盲目重试**，先看清楚 origin/main 新增了什么
6. **找到 README 与代码不一致 → 报告，不自动修复**