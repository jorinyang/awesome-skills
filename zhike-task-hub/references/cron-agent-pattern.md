# Cron Agent 模式 — 脚本收集 + LLM 分析

## 适用场景

cron 任务需要**先收集数据，再由 LLM 综合分析**，最终产出文档/报告。

## 模式

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ script 运行  │ ──→ │ stdout 注入   │ ──→ │ agent 分析   │
│ (数据收集)   │     │ agent prompt  │     │ + 创建文档   │
└─────────────┘     └──────────────┘     └─────────────┘
```

## 配置

```bash
hermes cron create \
  --name <job-name> \
  --script <collector.py> \      # 数据收集脚本（输出JSON到stdout）
  --no-agent false \              # ⚠️ 必须 false，启用LLM
  --skills <skill1,skill2> \      # agent 需要的技能
  --prompt "<分析指令>" \
  --deliver <target>
```

## 脚本要求

- 输出纯 JSON 到 stdout
- 不做格式化、不做分析
- 可直接 `python3 collect.py` 运行
- 示例：

```python
from report_weekly import collect_weekly_tasks
data = collect_weekly_tasks("c900dbc8-...")
print(json.dumps(data, ensure_ascii=False))
```

## 对比

| 模式 | no_agent | script作用 | agent作用 | 适用 |
|------|:--------:|-----------|----------|------|
| 纯脚本 | true | 产出+格式化 | 无 | 早/晚报（固定格式） |
| Agent | false | 仅数据收集 | LLM分析+文档创建 | 周/月报（深度分析） |

## 陷阱

- **script stdout 大小**：JSON 数据过大会挤占 prompt 上下文。建议 ≤500 条任务，单条 ≤500 字符
- **deliver 必须指定群**：agent 最终回复是群消息，不指定 deliver 会导致只发 DM
- **skills 必须包含文档创建技能**：否则 agent 不知道如何创建飞书文档
- **DeepSeek-V4-Pro 大上下文流式超时**（2026-06-08 发现）：
  - 症状：`Stream stale for 180s — no chunks received` → `[Errno 32] Broken pipe`，3 次重试全部失败
  - 根因：技能加载后总 context 膨胀到 ~31K tokens，DeepSeek 在 180s 流式阈值内无法产生任何 token
  - 诊断：查 `errors.log` 搜索 `Stream stale.*model=deepseek`，如果多个 job 同时段出现 → 确认为上下文过大
  - 修复：将技能从 3 个减到 1 个（只保留数据收集技能，如 `zhike-task-hub`），把文档创建命令和输出规范直接嵌入 prompt，context 从 ~31K → ~8K tokens
  - 实测：zhike-weekly 修复后秒级响应（API cache hit 100%）
  - 同样影响：任何加载 `feishu-doc`（1575+ 行）的 agent 模式 cron job 都有此风险
