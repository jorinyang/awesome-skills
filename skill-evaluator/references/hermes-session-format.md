# Hermes Session JSON 格式与数据提取

> 从本次实现中总结的 session 文件结构和提取陷阱。

## 文件位置

```
~/.hermes/sessions/session_*.json          # 主 profile 会话
~/.hermes-feishu/sessions/session_*.json   # Feishu gateway 会话
```

文件数量可能非常大（3000+），不能用全量扫描。

## 文件结构

```json
{
  "session_id": "sess_abc123",
  "model": "deepseek-v4-pro",
  "base_url": "...",
  "platform": "feishu",
  "session_start": "2026-06-21T12:00:00",
  "last_updated": "2026-06-21T12:05:00",
  "system_prompt": "You are Hermes Agent...",
  "message_count": 32,
  "messages": [
    {"role": "user", "content": "..."},
    {
      "role": "assistant",
      "content": "...",
      "reasoning": "...",
      "finish_reason": "tool_calls",
      "tool_calls": [
        {
          "id": "call_xxx",
          "type": "function",
          "function": {
            "name": "skill_view",
            "arguments": "{\"name\": \"clawshell-dev\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "call_xxx",
      "content": "{\"success\": true, ...}"
    }
  ]
}
```

## 提取 Skill 名称的正确方式

**只从 `skill_view` 和 `skill_manage` 工具调用中提取**，不要全文搜索：

```python
for msg in data.get("messages", []):
    for tc in msg.get("tool_calls", []):
        func = tc.get("function", {})
        if func.get("name") in ("skill_view", "skill_manage"):
            args = json.loads(func.get("arguments", "{}"))
            skill_name = args.get("name", "")
```

**为什么不能全文 grep**：
- `session_cron_*` 文件的 system_prompt 含有全量 skill 列表（噪声）
- skill 名称可能出现在聊天内容中但并非实际调用
- 需要排除 cron session：`"session_cron_" not in filename`

## 性能注意事项

- 3200+ 文件，每个可能 1-2MB
- **必须用 grep 预筛选**，只解析匹配的文件：
  ```bash
  grep -rl --include="session_*.json" "<skill_name>" <dir>
  ```
- `--include` 必须加，否则 grep 会扫描所有文件（包括 sessions.json 索引）导致超时
- 按 mtime 排序取最新的，避免解析大量历史文件

## Token 统计的局限

Hermes session 的 messages 数组**不包含 per-message token 计数**。
没有 `usage` 字段。可以统计的替代指标：
- `total_input_chars`: 所有 user 消息的字符总数
- `total_output_chars`: 所有 assistant 消息（content + reasoning）的字符总数
- 精确 Token 计数需要接入 OTel（Plan A）或通过 API response 记录
