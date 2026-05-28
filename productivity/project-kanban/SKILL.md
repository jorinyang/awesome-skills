---
name: project-kanban
description: 贵州之客项目看板 — 飞书多维表格（看板）+ 日历（日程）+ 任务（分配），三引擎一站式项目跟踪。
triggers:
  - "创建任务/项目/卡片"
  - "安排会议/日程/时间"
  - "分配给XX/XX负责"
  - "检查逾期/督办/review"
  - "我的待办/月夜的任务"
  - "XX项目进度"
tags: [feishu, kanban, calendar, task, project-management]
category: productivity
---

# 项目看板 (Project Kanban)

三引擎联动：Bitable（看板卡片）→ Calendar（日程安排）→ Task（人员分配）

## 部署信息

| 项目 | 值 |
|------|-----|
| Bitable app_token | `OGvAbDyubamXiTs96kkccJKKnCb` |
| Bitable table_id | `tblY9D4T0P4uSqnc` |
| Calendar ID | `feishu.cn_TzRmyorcXMoC2w2t8sh4pe@group.calendar.feishu.cn` |
| Wiki 节点 token | `ONc1wDc3qiZOXOkdD9ochSvOnfg` |
| 脚本目录 | `~/.hermes-feishu/skills/productivity/project-kanban/scripts/` |

## 脚本

```bash
SCRIPTS=~/.hermes-feishu/skills/productivity/project-kanban/scripts

# 看板
python3 $SCRIPTS/kanban_api.py init
python3 $SCRIPTS/kanban_api.py create --title "..." [--priority P0-P3] [--owner 月夜] [--executor 余媛天] [--project "..."] [--start yyyy-MM-dd] [--deadline yyyy-MM-dd] [--detail "..."]
python3 $SCRIPTS/kanban_api.py update <record_id> [--status ...] [--owner ...] [--deadline ...]
python3 $SCRIPTS/kanban_api.py list [--status 待办] [--project ...] [--owner ...]
python3 $SCRIPTS/kanban_api.py review

# 日历
python3 $SCRIPTS/calendar_api.py create --summary "..." --start "yyyy-MM-dd HH:mm" --end "..." [--attendees "月夜,余媛天"] [--description "..."]
python3 $SCRIPTS/calendar_api.py update <event_id> [--summary ...] [--start ...] [--end ...]
python3 $SCRIPTS/calendar_api.py delete <event_id>
python3 $SCRIPTS/calendar_api.py list [--days 30]

# 任务
python3 $SCRIPTS/task_api.py create --summary "..." [--collaborator "余媛天"] [--follower "月夜"] [--description "..."] [--deadline "2026-06-10"]
python3 $SCRIPTS/task_api.py update <task_id> [--summary ...] [--collaborator ...] [--follower ...] [--deadline ...]
python3 $SCRIPTS/task_api.py delete <task_id>
python3 $SCRIPTS/task_api.py list
```

## 三引擎联动规则

| 用户意图 | Bitable | Calendar | Task |
|----------|:-------:|:--------:|:----:|
| "创建一个任务/项目" | ✅ 卡片 | — | ✅ 分配执行人 |
| "安排一个会议/日程" | — | ✅ 日程 | — |
| "把某事分配给XX" | ✅ 负责人 | — | ✅ collaborator |
| "XX事情的截止日期" | ✅ 截止日期 | ✅ 日程提醒 | — |
| "检查逾期" | ✅ review | ✅ 过期日程 | — |

## 人员映射

| 姓名 | open_id |
|------|---------|
| 月夜 | ou_4c0471c3b58da8dd7883d095c3bb0843 |
| 余媛天 | ou_b2853971fa42584d441b98f280524619 |
| "XX事情的截止日期" | ✅ 截止日期 | ✅ 日程提醒 | ✅ due |

## 时间戳差异 (关键陷阱)

| 引擎 | 字段 | 单位 | 字段名 |
|------|------|:----:|--------|
| Bitable | 开始日期/截止日期 | **毫秒** | Unix timestamp × 1000 |
| Calendar | start_time/end_time | **秒** | `"timestamp"` 字符串 |
| Task | due | 秒 | `"time"` 字段（非 `timestamp` 非 `date`） |

### Task due 的正确格式

```json
{
  "due": {
    "time": "1809292800",           // 秒级 unix 时间戳，字符串
    "is_all_day": true,              // true=全天，false=精确时间
    "timezone": "Asia/Shanghai"      // 时区
  }
}
```

⚠️ Task API 的截止时间字段名是 `time`，不是 `timestamp`，也不是 `date`。其它服务的 `timestamp` 字段拷贝过去会报 1470439。

## 人员字段 (重要)

Bitable 的「负责人」「执行人」字段类型为 type=11 (User, multiple=true)。

**REST API 不支持创建人员字段** — type=7 是复选框，type=10 报 validation failed。必须用 lark-cli：

```bash
lark-cli base +field-create \
  --base-token <app_token> \
  --table-id <table_id> \
  --json '{"name":"负责人","type":"user"}' \
  --as bot
```

## 字段模型 (10 字段)

| 字段名 | field_id | type | 说明 |
|--------|----------|:----:|------|
| 任务标题 | fldkfhfIyd | 1 (文本) | 主字段 |
| 状态 | fldK9lkJMx | 3 (单选) | 待办/进行中/已完成/已逾期 |
| 截止日期 | fld1feSjMb | 5 (日期) | 毫秒时间戳 |
| 相关文件 | fldxvAW4CR | 17 (附件) | 默认字段，不可删除 |
| 优先级 | fldWXpVEtu | 3 (单选) | P0-紧急/P1-高/P2-中/P3-低 |
| 负责人 | flds9M0qni | 11 (人员) | 用 lark-cli 创建 |
| 执行人 | fldK49Ny8y | 11 (人员) | 用 lark-cli 创建 |
| 所属项目 | fldmRQ4Smg | 1 (文本) |  |
| 开始日期 | fldpv0sYxo | 5 (日期) | 毫秒时间戳 |
| 任务详情 | fldE0Bpp1L | 1 (文本) |  |

## 参考

- `references/bitable-api.md` — Bitable API 字段类型/陷阱
- `references/calendar-api.md` — Calendar API 端点/时间格式
- `references/task-api.md` — Task API 创建/分配格式
- `.hermes/plans/2026-05-27_project-kanban-plan.md` — 完整实施方案
