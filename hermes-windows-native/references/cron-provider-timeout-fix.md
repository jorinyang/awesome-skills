# Cron Job Provider Timeout — 诊断与修复

## 症状

Cron job 返回错误消息：`provider timeout. Fallback chain was exhausted or unavailable.`

`cronjob list` 中该 job 的 `last_status` 可能仍显示 `ok`（上次成功运行的状态），但用户收到了超时错误通知。

## 根因

Cron job 配置的 provider/model 在 cron 执行时不可用（API 超时），且 fallback 链也未能兜底。

常见场景：
- MiniMax-M3 (`minimax-cn`) 在凌晨时段 API 不稳定
- 小 provider 的 API 偶尔超时，fallback deepseek 也未生效

## 诊断流程

1. **确认失败 job**：`cronjob list` 找到 `last_status` 异常或用户报告的 job_id
2. **检查当前 model**：看 job 的 `model` / `provider` 字段
3. **对比可用 provider**：当前交互式会话使用哪个 provider 正常工作？用它作为修复目标

## 修复方案

### 方案 A：配置全局 fallback_providers（推荐，一次修复覆盖所有 cron job）

当多个 cron job 使用同一 provider（如 minimax-cn）时，不必逐个切换 model。在 `config.yaml` 中配置 fallback 链：

```yaml
# config.yaml
fallback_providers:
- deepseek
```

**效果**：任何 provider 超时 → 自动切到 fallback 链的下一个 provider → 任务不中断。

**验证**：
```bash
sed -n '1,10p' ~/.hermes/config.yaml | grep -A2 fallback_providers
# 应输出：fallback_providers:\n- deepseek
```

配置后重启 gateway 生效（或等下一次 cron tick 自动加载）。

**注意**：`patch` 工具在 Windows MSYS2 下对 `/c/Users/...` 路径可能解析为 `C:\c\Users\...`（重复盘符前缀），此时用 `sed -i` 直接修改：
```bash
sed -i 's/fallback_providers: \[\]/fallback_providers:\n- deepseek/' "/c/Users/Aorus/.hermes/config.yaml"
```

### 方案 B：切换单个 cron job 的 model/provider

```json
// cronjob update，同时更新 model 和 enabled_toolsets
{
  "action": "update",
  "job_id": "<job_id>",
  "model": {"model": "deepseek-v4-pro", "provider": "deepseek"},
  "enabled_toolsets": ["terminal", "file", "skills", "feishu_doc", "delegation"]
}
```

## ⚠️ 陷阱：`cronjob update` 只传 model 会重置 enabled_toolsets

**症状**：更新 model 后发现 job 无法使用某些工具（如 feishu_doc），因为 `enabled_toolsets` 被静默重置了。

**原因**：`cronjob update` 对未显式传入的数组字段使用默认值覆盖，不是 partial merge。

**正确做法**：更新 model 时**必须同时显式传入 `enabled_toolsets`**，值从更新前的 job 配置中复制。

```json
// ❌ 错误：只传 model，enabled_toolsets 被重置
{
  "action": "update",
  "job_id": "<job_id>",
  "model": {"model": "deepseek-v4-pro", "provider": "deepseek"}
}

// ✅ 正确：同时传入 enabled_toolsets
{
  "action": "update",
  "job_id": "<job_id>",
  "model": {"model": "deepseek-v4-pro", "provider": "deepseek"},
  "enabled_toolsets": ["terminal", "file", "skills", "feishu_doc", "delegation"]
}
```

**检测方法**：更新后用 `cronjob list` 检查 job 的 `enabled_toolsets` 是否与更新前一致。不一致则补发一次 update 修正。

## 修复后验证

- `cronjob list` 确认 `model`/`provider` 已切换
- `enabled_toolsets` 与更新前一致
- `next_run_at` 时间正确
- 如果不放心，可以 `cronjob run` 手动触发一次测试
