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
metadata:
  hermes:
    related_skills:
      - zhike-task-hub
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
python3 $SCRIPTS/kanban_api.py create --title "..." [--priority P0-P3] [--owner 月夜] [--executor 余媛天] [--assigner 夏与] [--follower "月夜,余媛天"] [--project "..."] [--start yyyy-MM-dd] [--deadline yyyy-MM-dd] [--detail "..."]
python3 $SCRIPTS/kanban_api.py update <record_id> [--status ...] [--owner ...] [--executor ...] [--assigner ...] [--follower ...] [--deadline ...]
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

| 引擎 | 字段 | 单位 | 字段名 | 备注 |
|------|------|:----:|--------|------|
| Bitable | 开始日期/截止日期 | **毫秒** | Unix timestamp × 1000 | |
| Calendar | start_time/end_time | **秒** | `"timestamp"` 字符串 | |
| Task v1 | due | 秒 | `"time"` 字段 | 非 `timestamp` 非 `date` |
| Task v2 | due / completed_at | **秒** | `"timestamp"` 字段 | created_at/updated_at 是**毫秒** |

### Task v1 due 格式

```json
{
  "due": {
    "time": "1809292800",
    "is_all_day": true,
    "timezone": "Asia/Shanghai"
  }
}
```

### Task v2 due 格式

```json
{
  "due": {
    "timestamp": "1809292800",
    "is_all_day": true,
    "timezone": "Asia/Shanghai"
  }
}
```

⚠️ v1 用 `time`，v2 用 `timestamp`。混用会报错。

## 人员字段

Bitable 的人员字段需用 lark-cli 创建（REST API 不支持 type=11 创建）：

```bash
lark-cli base +field-create \
  --base-token <app_token> \
  --table-id <table_id> \
  --json '{"name":"负责人","type":"user"}' \
  --as bot
```

已建人员字段（2026-05-30 确认）：

| 字段 | field_id | 单/多 | RACI |
|------|----------|:---:|:---:|
| 负责人 | flds9M0qni | 单 | R |
| 分配人 | fldAzegKl1 | 单 | A |
| 咨询人 | fldK49Ny8y | 多 | C |
| 关注人 | fldskv6Bf1 | 多 | I |

写入格式: `[{"id":"ou_xxx"}]`（即使 single 也包数组）

## 字段模型 (13 字段，含 RACI)

| 字段名 | field_id | type | RACI | 说明 |
|--------|----------|:----:|:----:|------|
| 任务标题 | fldkfhfIyd | 1 (文本) | — | 主字段 |
| 任务详情 | fldE0Bpp1L | 1 (文本) | — | 任务描述 |
| 状态 | fldK9lkJMx | 3 (单选) | — | 待办/进行中/已完成/已逾期 |
| 优先级 | fldWXpVEtu | 3 (单选) | — | P0-紧急/P1-高/P2-中/P3-低 |
| 截止日期 | fld1feSjMb | 5 (日期) | — | 毫秒时间戳 |
| 开始日期 | fldpv0sYxo | 5 (日期) | — | 毫秒时间戳 |
| 所属项目 | fldmRQ4Smg | 1 (文本) | — |  |
| 相关文件 | fldxvAW4CR | 17 (附件) | — | 默认字段，不可删除 |
| 催办 | fld55n2hsj | button | — | 按钮字段，API 不可写 |
| 负责人 | flds9M0qni | user (单) | **R** | 用 lark-cli 创建 |
| 分配人 | fldAzegKl1 | user (单) | **A** | 任务创建者 |
| 咨询人 | fldK49Ny8y | user (多) | **C** | 原误标为"执行人"，2026-05-30 纠正 |
| 关注人 | fldskv6Bf1 | user (多) | **I** | 任务关注者 |

## Task v2 API (2026-05 新增)

zhike-task-hub 技能已全面验证 Feishu Task v2 API（Bot 可用），推荐后续任务操作优先使用 v2：

| v1 (task_api.py) | v2 (zhike-task-hub) |
|------------------|---------------------|
| 无 tasklist 概念 | 原生 tasklist 支持 |
| `GET /task/v1/tasks` 列全部 | `GET /task/v2/tasklists/{g}/tasks` |
| `complete_time` 秒 | `completed_at` 毫秒 |
| `due` 是 JSON dict | `due` 是 Python dict str（需 `ast.literal_eval`） |

**V2 已知陷阱**：
- 创建任务时不可直接绑定清单，需事后 `+tasklist-task-add`
- 列表接口不含 `description`，需逐个 `GET /tasks/{guid}` 获取详情
- `is_all_day: True` 会导致时间戳偏移（用 `is_all_day: False` 可规避）
- `origin` 字段 v2 格式不同，由系统自动设置，无需手动传

详见 `zhike-task-hub` 技能的 `references/task-v2-api.md`。

## 参考

- `references/ai-native-architecture.md` — 全飞书原生架构决策：SaaS 替代对照、数据底座、自动化 cron、已知缺口
- `references/bitable-api.md` — Bitable API 字段类型/陷阱
- `../zhike-task-hub/references/task-v2-api.md` — Task v2 API 端点速查与陷阱
- `references/calendar-api.md` — Calendar API 端点/时间格式
- `references/task-api.md` — Task v1 API 创建/分配格式
- `references/task-v2-api.md` — **Task v2 API** 端点矩阵、Bot 可用性、陷阱（2026-05-30 端到端探测）
- `.hermes/plans/2026-05-27_project-kanban-plan.md` — 完整实施方案

## 关联技能指引

> 以下指引由 `github-absorb` Phase 6 自动生成

- **sibling → `zhike-task-hub`**：本技能覆盖项目级视角（飞书多维表格看板 + 日历 + 任务分配），`zhike-task-hub` 覆盖个人级视角（Todo 存档 + 早晚周月报）。两技能服务于同一业务体系（贵州之客），协同使用可覆盖项目全景 + 个人执行全貌。
