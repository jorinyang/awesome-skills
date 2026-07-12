# Cron "Connection Error" 诊断流程

当 `github-auto-sync` cron 报 `Connection error` 时，按以下顺序诊断。

## 诊断优先级

| 步骤 | 命令 | 预期结果 | 失败意味着 |
|------|------|---------|-----------|
| 1 | `gh auth status` | `✓ Logged in to github.com` | token 过期/未登录 |
| 2 | `gh api repos/jorinyang/awesome-skills --jq '.pushed_at'` | 返回 ISO 时间戳 | GitHub API 不可达 |
| 3 | `git clone --depth 1 https://github.com/jorinyang/awesome-skills.git /tmp/awesome-skills` | 克隆成功(可能需要15s+) | WSL HTTPS git 超时(已知问题) |
| 4 | `ssh -T -o ConnectTimeout=10 git@github.com` | `Permission denied (publickey)` 也算"正常" | SSH 不通不影响(技能走HTTPS) |

## 常见根因

### 1. 模型/Provider 连接抖动（最常见）
**症状**：cron 日志 `Connection error`，但手动验证 GitHub 完全正常。
**原因**：cron runner 启动 agent session 时 provider API 瞬断。
**处理**：直接 `cronjob resume`。通常下次执行正常。

### 2. WSL git HTTPS 超时
**症状**：`git clone/pull/push` 前台超时，但 `gh api` 正常。
**原因**：WSL 网络栈的已知问题，git 大对象传输慢。
**处理**：技能已使用 `background=true` 推送。克隆 `--depth 1` 减轻负载。

### 3. SSH 是误导信号（不要误判）
`ssh -T git@github.com` 返回 `Permission denied` 并不意味着 GitHub 不可达。
本技能使用 **HTTPS + gh credential helper**，不走 SSH。
`~/.ssh/clawshell_ecs` 是 ECS 服务器密钥，非 GitHub 密钥。
