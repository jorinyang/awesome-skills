# WSL 适配状态报告

> 适配背景：Hermes 已从 WSL 迁移至 Windows 原生环境（2026-07-01）
> 仓库：jorinyang/awesome-skills
> 版本：v5.4.6

---

## 适配策略

| 类别 | 处理方式 |
|------|---------|
| 核心 WSL 技能（3个） | 标记为 `仅WSL环境适用`，保留供WSL用户参考 |
| 附带 WSL 引用（10个） | 替换为 Windows 原生环境等效路径/命令 |
| 误匹配（3个） | 无需处理（newsletter 匹配到 "wsl"） |

---

## 🔴 核心 WSL 技能（已标记）

### wsl-browser-cdp
- **原功能**: WSL 环境下通过 CDP 连接 Windows Chrome
- **Windows 原生**: Chrome + Node.js 在 PATH 中，CDP 直连
- **处理**: 添加 `wsl_only: true` metadata + ⚠️ 顶部提示
- **状态**: ✅ 仅 WSL

### wsl-docker-deploy
- **原功能**: WSL2 Docker Desktop 代理部署——解决 daemon 无法拉取镜像
- **Windows 原生**: Docker Desktop 直连
- **处理**: 添加 `wsl_only: true` metadata + ⚠️ 顶部提示
- **状态**: ✅ 仅 WSL

### windows-troubleshooting-from-wsl
- **原功能**: bash→PowerShell 桥接诊断修复 Windows 组件
- **Windows 原生**: PowerShell 直接可用
- **处理**: 添加 `wsl_only: true` metadata + ⚠️ 顶部提示
- **状态**: ✅ 仅 WSL

---

## 🟡 附带引用（已修复）

| 技能 | 原引用 | 修复后 |
|------|--------|--------|
| travel-intel | 21处 "WSL本地" 标注 | "本地" |
| github-release-readme | "WSL push 铁律" | "Push 建议" |
| github-absorb | 引用 `wsl-browser-cdp` | Chrome 直连命令 |
| jimeng-video | WSL 浏览器登录 workaround | 移除 |
| feishu-doc | `/mnt/c/Users/` 路径 | `C:\Users\` |
| image-analysis | "not installed (common in WSL)" | "not installed" |
| firecrawl-web | 引用 `wsl-docker-deploy` | 通用 Docker 文档 |
| dingtalk-cli | "WSL 精简环境" unzip | "精简环境" |
| strategy-plan-writing | "WSL search workarounds" | 通用描述 |
| double-evolution | 分类映射含 WSL 技能 | 移除 WSL 技能名 |

---

## 🔮 后续待办

- [ ] `windows-troubleshooting-from-wsl` → 可重写为纯 Windows 版本（移除 bash→PS 桥接层）
- [ ] `wsl-browser-cdp` → 长期评估是否归档
- [ ] `wsl-docker-deploy` → 长期评估是否归档

---

*最后更新：2026-07-01 | v5.4.6*
