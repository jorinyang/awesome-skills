# Cron 任务推送格式参考

> 2026-05-28 实测验证。适用于 travel-knowledge 和 travel-monitor 的 cron 任务。

## 群内消息格式（固定，不可定制）

```
Cronjob Response: {任务名} (job_id: {job_id})
<-- cron agent 的 final response 内容 -->
To stop or manage this job, send me a new message (e.g. "stop reminder {任务名}")
```

- **头部**：标识任务来源，群成员可据此判断信息类型
- **内容体**：cron agent 的 `final response`，即 agent 完成任务后的最终回复
- **尾部**：管理指令提示，群内发送 `stop reminder {任务名}` 可暂停任务

## 关键原则

### 1. content = agent's final response

cron agent 的**最终回复**就是群内看到的内容。如果 agent 只创建了文档但没有输出摘要，群内只能看到 header + footer 夹着空白或"任务完成"。

**每个 prompt 必须包含**：

```
**关键：在你的最终回复中输出可见摘要，包括：**
- {信息项 1}
- {信息项 2}
- 创建的文档链接
```

### 2. deliver 必须指定群 chat_id

| 值 | 去向 |
|----|------|
| `origin` | 创建时的 DM（仅自己可见） |
| `feishu:oc_XXXX` | 指定群聊（团队可见） |

**贵州之客群** chat_id：`oc_40570cc921ca1f645f8667151c1e85e6`

获取方式：`send_message(action='list')` → 查找群名 → 提取 chat_id

### 3. 已部署任务一览

| Job ID | 任务名 | 调度 | deliver |
|--------|--------|------|---------|
| `22fc10b1731c` | travel-knowledge-collect | 每日 07:00 | 贵州之客群 |
| `7bb67e31398b` | travel-monitor-morning | 每日 08:00 | 贵州之客群 |
| `d9e08267c622` | travel-monitor-evening | 每日 18:00 | 贵州之客群 |
| `7304faf4af71` | travel-monitor-weekly | 每周一 09:00 | 贵州之客群 |
| `ca0accd38ac8` | travel-expire-check | 每日 03:00 | 贵州之客群 |

## Prompt 设计模板

```markdown
执行 {任务描述}。

{具体步骤 1}
{具体步骤 2}
{具体步骤 3}

最终回复格式（纯文本，≤3000字符，你的回复会自动推到群）：
```
{输出模板，包含 emoji + 字段名 + 占位符}
```
```

最后一句明确告知 agent 其回复的去向，有助于 agent 调整输出格式。

### 消息长度限制（99992402 错误）

飞书群消息有长度限制。实测：agent 输出超过 ~4000 字符或包含复杂格式时会触发 `99992402 field validation failed`，消息静默丢弃。

**强制约束**：
- 最终回复 ≤ **3000 字符**（留安全余量）
- **纯文本** + 基础 markdown（`**加粗**`、`[链接](url)`、`` `代码` ``）
- 禁止表格、代码块、多级列表
- 详细内容放到飞书文档，消息只含摘要 + 链接

## 验证方法

1. 创建一次性测试任务 → `cronjob create --schedule "2100-01-01T00:00:00" --repeat 1`
2. 手动触发 → `cronjob run --job-id {id}`
3. 检查群内是否出现消息
4. 清理测试任务 → `cronjob remove --job-id {id}`（一次性的执行后自动清理也可）
