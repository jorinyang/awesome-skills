# GitHub 推送策略（中国大陆网络环境）

## 问题

`git push` 到 GitHub 超时。TLS 握手成功但数据层被 GFW 阻断。
代理（Clash 7890）CONNECT 隧道建立后数据也挂起。

## 可用方案（按优先级）

### 1. SSH 推送（最可靠）

```bash
export HOME=/c/Users/Aorus
export GIT_SSH_COMMAND="ssh -o ConnectTimeout=30 -o StrictHostKeyChecking=accept-new"
git remote set-url origin git@github.com:jorinyang/awesome-skills.git
git push origin main
```

前置条件：`~/.ssh/id_rsa` 存在且已添加到 GitHub。

### 2. gh CLI + Token

```bash
export GH_TOKEN='ghp_...'
gh release create vX.Y.Z --title "..." --notes "..."
```

### 3. GitHub API + Token

```bash
curl -X POST "https://api.github.com/repos/OWNER/REPO/releases" \
  -H "Authorization: Bearer ***" \
  -d @release.json
```

### 4. HTTP 代理（需代理规则允许 GitHub）

```bash
git config --local http.proxy http://127.0.0.1:7890
git config --local https.proxy http://127.0.0.1:7890
```

注意：Clash 规则可能将 `github.com` 设为 REJECT，此时代理无效。

## 诊断命令

```bash
# 检查代理连通性
curl -s -x http://127.0.0.1:7890 https://github.com -o /dev/null -w "%{http_code}"

# 详细推送日志
GIT_CURL_VERBOSE=1 git push origin main 2>&1 | head -20

# 测试 SSH
ssh -T git@github.com
```
