# Hermes Hook 配置指南

> 从本次 B-2 实现中总结：Gateway Hook vs Shell Hook 的区别和踩坑记录。

## Hermes 有三种 Hook 系统

| 系统 | 注册方式 | 运行范围 | 适用场景 |
|------|---------|:---:|------|
| **Gateway Hooks** | `HOOK.yaml` + `handler.py` 在 `~/.hermes/hooks/<name>/` | Gateway 专属 | Feishu/Telegram 等平台的事件响应 |
| **Plugin Hooks** | `ctx.register_hook()` 在插件中 | CLI + Gateway | 工具拦截、指标采集 |
| **Shell Hooks** | `hooks:` 块在 `config.yaml` 中 | CLI + Gateway | 简单 shell 脚本 |

## 本次选择的 Gateway Hook（正确方案）

因为用户通过 Feishu 使用 Hermes，需要 Gateway 事件：

```yaml
# ~/.hermes/hooks/skill-eval/HOOK.yaml
name: skill-eval
description: After every agent response, scan for Skill usage and trigger evaluation
events:
  - agent:end
```

```python
# ~/.hermes/hooks/skill-eval/handler.py
async def handle(event_type: str, context: dict):
    # context 包含: platform, user_id, session_id, session_key, message, response
    session_key = context.get("session_key", "")
    response = context.get("response", "")
    # 提取 skill → 触发评测 → 写入共享去重注册表
```

## 踩过的坑

### 坑 1: 误用 Shell Hooks（已纠正）
- ❌ 最初在 `config.yaml` 中配了 `hooks.on_session_end`
- Hermes 报 "No shell hooks configured"
- 原因：`on_session_end` 不是 `VALID_HOOKS` 中的 shell hook 事件名
- ✅ 改用 Gateway Hook 的 `agent:end` 事件

### 坑 2: Hook 脚本路径
- Shell hooks 脚本放 `~/.hermes/agent-hooks/`（约定）
- Gateway hooks 脚本放 `~/.hermes/hooks/<name>/`（HOOK.yaml + handler.py）
- 两者目录不同，不要混放

## 使 Hook 生效

```bash
hermes gateway restart   # 重启 Gateway 后新 hook 生效
```

Hook 是首次自动发现的，不需要显式注册。Gateway 启动时扫描 `~/.hermes/hooks/*/HOOK.yaml`。

## 与 Cron 的去重

Hook（实时）和 Cron（定时）共享同一个去重注册表：
- 文件：`~/.hermes-feishu/eval_results/_evaluated_sessions.json`
- Hook 先执行写 session_id
- Cron 执行时检查已存在则跳过
- 避免同一会话被重复评测
