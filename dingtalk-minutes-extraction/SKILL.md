---
name: dingtalk-minutes-extraction
description: '从钉钉AI听记URL提取会议转写、AI摘要和待办。'
version: 1.0.0
author: 杨瑒 (月夜)
license: MIT
metadata:
  hermes:
    tags: [dingtalk, minutes, meeting, transcript, mcp]
triggers:
  - "听记"
  - "会议记录"
  - "会议摘要"
  - "transcribes"
  - "minutes"
  - "会议转写"
  - "AI听记"
  - "shanji.dingtalk.com"
---

# DingTalk Minutes Extraction（钉钉AI听记提取）

## When to Use

- 用户提供 `shanji.dingtalk.com/app/transcribes/` 链接
- 用户说"获取会议记录""拉听记""会议摘要"
- 需要从会议听记中提取分工/结论/待办用于后续任务

## 功能

从钉钉AI听记URL中提取taskUuid，通过DingTalk Minutes MCP获取：
- **基本信息**：标题/时间/时长/参与人
- **AI摘要**：结构化总结（议题/结论/分工）
- **全文转写**：逐条语音转写（发言人+文本+时间戳）

## taskUuid提取规则

钉钉听记URL格式：
```
https://shanji.dingtalk.com/app/transcribes/{taskUuid}
```

示例：
```
URL: https://shanji.dingtalk.com/app/transcribes/76327569643339373933353632325f313031393436305f_9
taskUuid: 76327569643339373933353632325f_13019460_9
```

注意：URL中的taskUuid可能包含URL编码（如`_`编码为`5f`），MCP接口接受原始UUID格式。

## MCP工具调用

需先 `tool_search` 搜索 `dingtalk minutes`，然后 `tool_describe` 获取参数schema。

### 推荐调用顺序

1. **基本信息 + AI摘要**（并行，无依赖）：
   - `mcp__dingtalk_minutes__get_minutes_basic_info` — 标题/时间/时长/URL
   - `mcp__dingtalk_minutes__get_minutes_ai_summary` — 结构化AI摘要

2. **全文转写**（可选，内容量大时按需）：
   - `mcp__dingtalk_minutes__get_minutes_transcription` — 逐条转写原文

3. **其他能力**（按需）：
   - `mcp__dingtalk_minutes__get_minutes_keywords` — 关键词列表
   - `mcp__dingtalk_minutes__list_minutes_todos` — 待办事项提取
   - `mcp__dingtalk_minutes__batch_get_minutes_details` — 批量查询

### 参数

所有工具的必填参数均为 `taskUuid: string`。

## 典型工作流

### 场景：获取会议内容用于后续任务

```
1. 从用户提供的URL提取taskUuid
2. 并行调用 get_minutes_basic_info + get_minutes_ai_summary
3. 从AI摘要中提取：参会人/议题/结论/分工/截止日期
4. 如果AI摘要信息不足，追加调用 get_minutes_transcription 获取原文
5. 将提取的结构化信息用于后续任务（如：产出大纲/跟进事项/更新项目状态）
```

### 场景：批量处理多条听记

```
1. 收集所有taskUuid
2. 用 batch_get_minutes_details 获取基础信息列表
3. 对需要深度分析的听记，逐条调用 get_minutes_ai_summary
```

## 注意事项

- **认证**：MCP通过钉钉授权访问，需确保当前登录账号有听记访问权限
- **内容量**：AI摘要通常足够覆盖会议核心内容，全文转写可能非常长，非必要不拉取
- **时效性**：听记在会议结束后自动生成AI摘要，刚结束的会议可能摘要尚未就绪
- **权限**：只能访问当前账号有权限的听记（创建者/共享者/组织内可见）

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 摘要为空 | 会议刚结束，AI摘要生成中 | 等待几分钟后重试 |
| 无权访问 | 听记未共享给当前账号 | 联系听记创建者添加权限 |
| taskUuid提取错误 | URL格式不标准 | 检查URL中`transcribes/`后的完整字符串 |
