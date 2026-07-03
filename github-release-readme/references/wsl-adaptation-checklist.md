# WSL → Windows 适配检查清单

当 Hermes 从 WSL 迁移到 Windows 原生环境时，对技能仓库执行以下扫描和修复。

## Phase 1: 全局扫描

```bash
# 搜索 WSL 引用
grep -rn "wsl\|/mnt/c/\|bash.exe\|wsl.exe" --include="SKILL.md" .
```

## Phase 2: 分类处理

| 匹配类型 | 处理方式 | 示例 |
|---------|---------|------|
| 技能名含 `wsl` | 添加 `wsl_only: true` metadata + ⚠️ 顶部提示 | wsl-browser-cdp, wsl-docker-deploy |
| 路径 `/mnt/c/` | 替换为 `C:\` | feishu-doc |
| "WSL本地" 标注 | 改为 "本地" | travel-intel |
| WSL 特定 workaround | 移除或通用化 | jimeng-video WSL浏览器登录 |
| 引用 WSL 技能 | 移除或改为通用替代 | github-absorb 引用 wsl-browser-cdp |
| "WSL push 铁律" | 改为通用网络建议 | github-release-readme |
| 误匹配 | 不处理 | newsletter→"wsl" 匹配 |

## Phase 3: metadata 标记

对于保留给 WSL 用户参考的技能，在 frontmatter 添加：

```yaml
metadata:
  wsl_only: true  # 仅 WSL 环境适用
```

并在 SKILL.md body 顶部添加：

```markdown
> ⚠️ **仅 WSL 环境适用** | 此技能专为 WSL/Linux 环境设计。
```

## Phase 4: 产出物

- 创建 `WSL_ADAPTATION_STATUS.md` 跟踪所有变更
- README 版本号 PATCH bump（适配 = PATCH）
