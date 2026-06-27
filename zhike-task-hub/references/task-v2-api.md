# Feishu Task v2 API 参考

> Bot identity 已验证可用的全部 v2 端点。基于 2026-05-30 探测结果。

## 端点速查

| 操作 | 方法 | 端点 | 备注 |
|------|:--:|------|------|
| 创建清单 | POST | `/task/v2/tasklists` | 返回 guid |
| 删除清单 | DELETE | `/task/v2/tasklists/{guid}` | |
| 创建任务 | POST | `/task/v2/tasks` | 创建时不可直接绑定清单 |
| 获取任务 | GET | `/task/v2/tasks/{guid}` | **含 description** |
| 更新任务 | PATCH | `/task/v2/tasks/{guid}` | 有限字段集 |
| 删除任务 | DELETE | `/task/v2/tasks/{guid}` | |
| 列清单任务 | GET | `/task/v2/tasklists/{guid}/tasks` | **不含 description**，支持分页 |
| 任务归入清单 | lark-cli | `+tasklist-task-add --as bot` | REST 端点待确认 |

## 可 PATCH 字段

`update_fields` 仅接受这些值：
```
agent_task_progress, agent_task_status, completed_at, custom_complete,
custom_fields, description, due, extra, is_milestone, mode, repeat_rule,
start, summary, text_deliveries
```

**不可 PATCH**：tasklists、tasklist_guids、collaborator_ids、follower_ids
→ 清单归属用 `lark-cli +tasklist-task-add`，协作者/关注人暂时无法通过 Bot 修改。

## 字段映射: Task v2 → Bitable

| Task v2 字段 | 类型 | Bitable 字段 | field_id | 转换 |
|-------------|------|-------------|----------|------|
| summary | str | 任务标题 | fldkfhfIyd | 直接 |
| description | str | 任务详情 | fldE0Bpp1L | 空→"【缺详情】" |
| completed_at | str | 状态 | fldK9lkJMx | >0→"已完成", =0→"待办"/"进行中" |
| due.timestamp | str(秒) | 截止日期 | fld1feSjMb | ×1000 → 毫秒 |
| creator.id | str | 分配人 | fldAzegKl1 | open_id |
| collaborators[0].id | str | 负责人 | flds9M0qni | 第一个协作者 |
| collaborators[1:].id | []str | 咨询人 | fldK49Ny8y | 其余协作者 |
| followers[].id | []str | 关注人 | fldskv6Bf1 | 全部 |
| — | — | 所属项目 | fldmRQ4Smg | 从任务标题或自定义解析 |
| — | — | 优先级 | fldWXpVEtu | 从自定义字段或默认 |

## 时间戳差异

| 系统 | 字段 | 单位 | 
|------|------|:--:|
| Task v2 due.timestamp | 字符串 | **秒** |
| Task v2 created_at | 字符串 | **毫秒** |
| Task v2 completed_at | 字符串 | **毫秒** |
| Bitable 日期字段 | 整数 | **毫秒** |

**转换**：`bitable_ms = int(task_due_sec) * 1000`

**⚠️ 重要：创建任务时用 UTC 午夜时间戳。** API 对 CST 午夜有 13 分钟偏移会导致日期回退 1 天。代码中 `_date_to_sec()` 已使用 `datetime.utc` 时区。

## 状态判断

```python
is_completed = int(task.get("completed_at", "0")) > 0
status = "已完成" if is_completed else "待办"
```

## 列表接口 vs 详情接口

```
GET /task/v2/tasklists/{guid}/tasks
  → 返回: summary, completed_at, status, guid
  → 不返回: description, due, collaborators, followers

GET /task/v2/tasks/{guid}
  → 返回: 全部字段
```

**策略**：
- 同步/早报/晚报 → 用列表接口（快）
- 周报/月报 → 列表获取 guid → 逐个 GET 详情（补 description）

## 已知陷阱

1. **创建任务时 `tasklist_guid` 无效** — 任务创建后 tasklists 仍为空 `[]`，必须用 `+tasklist-task-add` 事后关联
2. **`GET /task/v2/tasks` 不带参数返回 0** — v2 任务必须在 tasklist 上下文中查询
3. **`GET /task/v2/tasks?tasklist_guid=xxx` 无效** — 必须用 `/tasklists/{guid}/tasks` 端点
4. **completed_at 是毫秒时间戳** — 不是秒，与 due.timestamp 不同
5. **PATCH tasklists 返回 1470400** — 不支持，必须走 tasklist-task-add
6. **status 字段在列表接口返回 None** — 用 completed_at 判断完成状态
7. **`add_to_tasklist()` 依赖 `lark-cli` 在 PATH** — `subprocess.run(["lark-cli", ...])` 需 `~/.local/bin` 在 PATH。execute_code 下 PATH 不包含，需 `os.environ["PATH"] = os.path.expanduser("~/.local/bin") + ":" + os.environ["PATH"]`；或用 `terminal()` 调用脚本（PATH 已设置）
