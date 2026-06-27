---
name: zhike-task-hub
description: 贵州之客任务中枢 — Todo(Bitable)存档 + 早晚周月报 + 对话查询，基于飞书 Task v2 API。
triggers:
  - "查任务"
  - "我的待办"
  - "有什么任务"
  - "待办事项"
  - "我的任务"
  - "任务列表"
  - "XX项目进度"
  - "XX项目任务"
  - "逾期任务"
  - "哪些逾期了"
  - "谁的逾期最多"
  - "检查逾期"
  - "督办"
  - "创建任务"
  - "新建任务"
  - "加个任务"
  - "分配任务给"
  - "完成任务"
  - "标记完成"
  - "做完了"
  - "最近忙什么"
  - "最近怎么样"
  - "项目有进展吗"
  - "那件事做了吗"
  - "进展如何"
tags: [feishu, task, bitable, cron, report]
category: productivity
related_skills: [double-evolution]
version: 1.0.0
---

# zhike-task-hub — 贵州之客任务中枢

三位一体：**同步存档** + **周期报告** + **对话查询**。

## 架构

```
Todo (Task v2) ──sync──→ Bitable (存档)
     │                        │
     ├──早晚报(cron)──→ 群消息   │
     ├──周报(cron)───→ 飞书文档  │
     ├──月报(cron)───→ 飞书文档  ←── 对话查询
```

## 配置

```yaml
tasklist_guid: "c900dbc8-fa00-4154-a6a7-059669427b0f"
chat_id: "oc_40570cc921ca1f645f8667151c1e85e6"  # 贵州之客群
```

## 子模块

| 模块 | 文件 | 触发 |
|------|------|------|
| Task v2 API 封装 | `scripts/task_v2_api.py` | 所有模块依赖 |
| 每日同步 | `scripts/sync_todo_to_bitable.py` | cron 3:00 |
| 早报 | `scripts/report_morning.py` | cron 9:00 |
| 晚报 | `scripts/report_evening.py` | cron 23:00 |
| 周报数据收集 | `scripts/report_weekly.py` | cron 周一 8:00 |
| 月报数据收集 | `scripts/report_monthly.py` | cron 1日 7:30 |
| 对话查询 | `scripts/query_handler.py` | 关键词触发 |

## 使用方式

### 1. 对话触发（关键词自动匹配）

| 级别 | 关键词示例 | 行为 |
|:----:|-----------|------|
| 🟢 | `我的待办` `XX项目进度` `逾期任务` | 扫 Bitable → 格式化回复 |
| 🟢 | `创建任务` `完成任务` | 调 Task v2 API → 确认 |
| 🟡 | `最近忙什么` `进展如何` | 反问确认 → 确认后扫 |
| 🔴 | `有个事` `工作` | 不触发 |

## Cron 定时任务（已部署 5 个）

所有 cron 使用 `~/.hermes-feishu/scripts/zhike_*.py` 包装脚本（硬编码 tasklist_guid），位于 skill 目录外的 scripts/ 以便 cron 独立调用。

| Job ID | 名称 | 调度 | 模式 | 说明 |
|--------|------|------|:--:|------|
| `d21e728651f5` | zhike-sync | 0 3 * * * | no-agent, deliver=local | 每日同步 Todo→Bitable，仅本地存档不推送 |
| `87f28de012ed` | zhike-morning | 0 9 * * * | no-agent | 早报：今日截止+逾期，脚本直出格式化文本 |
| `24891c7bd7a8` | zhike-evening | 0 23 * * * | no-agent | 晚报：完成/未完成对比+明日预警 |
| `c2d478f5c5dc` | zhike-weekly | 0 8 * * 1 | **agent** | 脚本收集JSON → LLM分析 → 飞书文档 → 群链接 |
| `b8230ecd4a98` | zhike-monthly | 30 7 1 * * | **agent** | 脚本收集JSON → LLM深度分析 → 飞书文档 → 群链接 |

**模式说明**：
- **no-agent**：脚本 stdout 直接推送（早/晚报脚本已输出格式化文本，无需 LLM）
- **agent**：脚本 stdout 作为上下文注入 agent prompt → LLM 分析 → 创建飞书文档 → 推送摘要+链接（周/月报需要深度分析）

**关键技巧**：agent 模式 cron 的 `script` 只做数据收集（输出 JSON），`prompt` 定义分析任务。脚本的 stdout 自动注入为上下文，无需手动传参。

**⚠️ agent 模式坑**：避免加载大技能（如 `feishu-doc` 1575+ 行）到 agent cron job——会导致 context 膨胀到 ~31K tokens，DeepSeek-V4-Pro 流式超时 180s 后断连（`[Errno 32] Broken pipe`）。把文档创建命令直接嵌入 prompt 替代加载大技能。详见 `references/cron-agent-pattern.md`。

**tasklist_guid**：`c900dbc8-fa00-4154-a6a7-059669427b0f`

**重构命令参考**（非当前状态）：

```bash
# 同步 (no-agent, local)
hermes cron create --name zhike-sync --schedule "0 3 * * *" \
  --script zhike_sync.py --no-agent true --deliver local

# 早报 (no-agent)
hermes cron create --name zhike-morning --schedule "0 9 * * *" \
  --script zhike_morning.py --no-agent true \
  --deliver feishu:oc_40570cc921ca1f645f8667151c1e85e6

# 周报 (agent 模式 — 脚本收集 + LLM分析)
hermes cron create --name zhike-weekly --schedule "0 8 * * 1" \
  --script zhike_weekly.py --no-agent false \
  --skills zhike-task-hub,feishu-doc,zhike-content-output \
  --prompt "脚本已收集本周数据(见上方JSON)。请统计+语义分析+建议→创建飞书文档→推送链接。" \
  --deliver feishu:oc_40570cc921ca1f645f8667151c1e85e6
```

## 关键约束

1. **Todo 只读** — 同步方向始终 Todo → Bitable，不在 Bitable 中创建/编辑任务
2. **报告优先读 Todo** — 早晚周月报直接从 Task v2 API 拉取，不用 Bitable 快照
3. **不空发** — 周期内无任务则跳过报告
4. **缺详情标记** — 任务 description 为空时标记「缺详情」，不视为错误
5. **周末节假日照发** — 不因节假日跳过

## 依赖

- `project-kanban` — 共用 token_mgr.py 和 Bitable 结构
- `feishu-table` — Bitable CRUD (lark-cli base)
- `feishu-doc` — 飞书文档创建 (周报/月报)
- `zhike-content-output` — 报告文案质量规范（对客铁律）

## 参考

- `references/task-v2-api.md` — v2 API 端点、字段映射、陷阱
- `references/cron-agent-pattern.md` — cron agent 模式：脚本收集 + LLM 分析
- `templates/report_prompt.md` — 周报/月报 LLM 提示词模板

### 包装脚本（cron 使用）

位于 `~/.hermes-feishu/scripts/zhike_*.py`（独立于 skill 目录，硬编码 tasklist_guid）：
