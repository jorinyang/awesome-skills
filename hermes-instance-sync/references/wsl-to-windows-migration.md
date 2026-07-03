# WSL→Windows 迁移技能适配检查清单

当 Hermes 从 WSL 迁移到 Windows 原生环境后，技能仓库中的 WSL 特定引用需要系统性适配。

## 扫描阶段

对仓库中所有 SKILL.md 执行以下模式搜索：

| 模式 | 含义 | 处理 |
|------|------|------|
| 技能名含 `wsl` | 显式WSL技能 | 标记为仅WSL环境适用 |
| `wsl` 关键字 | 引用WSL环境 | 改为通用描述 |
| `/mnt/c/Users/` | WSL路径挂载 | 改为 `C:\Users\` |
| `WSL本地` / `🏠 WSL` | 运行位置标注 | 改为 `本地` |
| `bash.exe` / `wsl.exe` | WSL命令调用 | 改为原生PowerShell/cmd |

## 分类处理

### 核心WSL技能（3类处理）

1. **wsl-browser-cdp**: WSL→Chrome CDP桥接。Windows原生下Chrome直接可用。标记为仅WSL。
2. **wsl-docker-deploy**: WSL Docker代理部署。Windows原生下Docker Desktop直连。标记为仅WSL。
3. **windows-troubleshooting-from-wsl**: bash→PowerShell桥接诊断。Windows原生下PowerShell直接可用。标记为仅WSL。

标记方式：
```yaml
metadata:
  wsl_only: true  # 仅 WSL 环境适用
```

并在SKILL.md正文顶部添加：
```markdown
> ⚠️ **仅 WSL 环境适用** | 此技能专为 WSL/Linux 环境设计。
> 如果你已迁移到 Windows 原生环境，Chrome/Docker/PowerShell 可直接使用。
```

### 附带引用（逐项替换）

- 路径替换: `/mnt/c/Users/` → `C:\Users\`
- 环境标注: `WSL本地` → `本地`
- 特殊处理: `WSL push 铁律` → `Push 建议`（通用化）
- 依赖引用: `wsl-browser-cdp` / `wsl-docker-deploy` → 原生替代方案或移除
- workaround移除: WSL特有的浏览器登录失败、unzip缺失等

## 验证

适配完成后检查：
1. `grep -r "WSL" SKILL.md` 仅命中显式标注为WSL-only的技能
2. `grep -r "/mnt/c/"` 无命中
3. 所有WSL技能的前端matter含 `wsl_only: true`
