---
name: feishu-table
description: Use when creating, managing, or querying Feishu Bitable (多维表格) and Spreadsheet (电子表格). Covers table/field/record/view CRUD, lark-cli base 78 commands, REST API endpoints, business templates (CRM, orders, products), batch operations, and sheet data read/write via lark-cli api. Bitable via lark-cli base; Sheet via lark-cli api REST.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feishu, bitable, spreadsheet, table, database, crm, lark-cli]
    related_skills: [feishu-doc, feishu-wiki, kanban-orchestrator]
---

# Feishu Table — 飞书多维表格 + 电子表格

## Overview

飞书表格操作的统一入口，分工明确：

| 工具 | 操作方式 | 适用场景 |
|------|----------|----------|
| **多维表格 (Bitable)** | `lark-cli base` (78 子命令) | CRM、产品库、订单、看板、结构化数据 |
| **电子表格 (Sheet)** | `lark-cli api` 调用 REST 端点 | 财务报表、公式计算、预算、成本核算 |

共用 `lark-cli` 认证体系（App ID: `cli_aa9ead14c2641cc3`），无需额外配置。

---

## When to Use

- 创建/管理飞书多维表格（表、字段、记录、视图、仪表盘）
- 批量导入数据到多维表格（CSV/JSON → Bitable）
- 设计业务数据模型（客户 CRM、订单、产品库）
- 操作飞书电子表格（读/写/公式/样式）
- 在飞书文档中嵌入表格
- 搜索/过滤/聚合表格数据

**Don't use for:**
- 飞书文档内容创建 → `feishu-doc`
- 知识库 Wiki 管理 → `feishu-wiki`
- 任务分解编排 → `kanban-orchestrator`

---

## Token 获取

lark-cli 已配置完成（`cli_aa9ead14c2641cc3`），每次命令自动处理 token。手动 API 调用时：

```bash
FEISHU_APP_ID=cli_aa9ead14c2641cc3
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$FEISHU_APP_ID\",\"app_secret\":\"$FEISHU_APP_SECRET\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")
```

---

# Part A: 多维表格 (Bitable) via lark-cli base

## 资源层级

```
App (base_token)
├── Table (table_id, 以 tbl 开头)
│   ├── Field (field_id, 以 fld 开头)
│   ├── Record (record_id, 以 rec 开头)
│   └── View (view_id, 以 vew 开头)
├── Dashboard (block_id, 以 blk 开头)
├── Role (role_id)
│   └── Member (member_id)
└── Workflow (workflow_id)
```

### 获取 Token/ID

| 资源 | 获取方式 |
|------|----------|
| `app_token` | 多维表格 URL 中 `/base/` 后的部分；或知识库 wiki node 的 `obj_token`（当 `obj_type=bitable`） |
| `table_id` | URL 中 `?table=` 后的值；或 `lark-cli base +table-list --base-token` |
| `view_id` | URL 中 `?viewId=` 后的值；或 `lark-cli base +view-list` |
| `field_id` | `lark-cli base +field-list` 返回 |
| `record_id` | `lark-cli base +record-list` 或 `+record-search` 返回 |

---

## 命令速查

### Base 级别

```bash
lark-cli base +base-create --name "表格名称" --as bot
lark-cli base +base-get --base-token <token> --as bot
lark-cli base +base-copy --base-token <src> --name "副本" --as bot
```

### Table 级别

```bash
lark-cli base +table-list --base-token <token> --as bot
lark-cli base +table-create --base-token <token> --name "新表" --fields '[...]' --as bot
lark-cli base +table-delete --base-token <token> --table-id <id> --yes --as bot
lark-cli base +table-update --base-token <token> --table-id <id> --name "新名" --as bot
```

### Field 级别

```bash
# 列出
lark-cli base +field-list --base-token <token> --table-id <id> --as bot

# 新增（⚠️ --json 只支持 name+type，不支持 property。带选项的 select 字段需用 REST API）
lark-cli base +field-create --base-token <token> --table-id <id> \
  --json '{"field_name":"状态","type":"select"}' \
  --as bot

# 带选项的 select 字段 → 用 REST API
lark-cli api POST "/open-apis/bitable/v1/apps/<token>/tables/<tid>/fields" \
  --data '{"field_name":"状态","type":3,"property":{"options":[{"name":"待办","color":0}]}}' --as bot

# 更新（⚠️ 必须同时传 field_name + type，缺 type 报 99992402）
lark-cli base +field-update --base-token <token> --table-id <id> \
  --field-id <fld_id> --json '{"field_name":"新名称","type":1}' --as bot

# 删除
lark-cli base +field-delete --base-token <token> --table-id <id> --field-id <fld_id> --as bot
```

### Record 级别

```bash
# 列出（支持分页 + 筛选）
lark-cli base +record-list --base-token <token> --table-id <id> \
  --params '{"filter":"CurrentValue.[状态]=\\\"待办\\\"}"' --page-all --as bot

# 搜索（keyword 搜索模式 — ⚠️ 非 Open API 的 filter/conditions 格式）
lark-cli base +record-search --base-token <token> --table-id <id> \
  --json '{"keyword":"<搜索词>","search_fields":["<字段名1>","<字段名2>"]}' \
  --as bot

# 结构化筛选（需用 +record-list 配合视图过滤，或 REST API 的 filter DSL）

# 新增单条
lark-cli base +record-create --base-token <token> --table-id <id> \
  --json '{"fields":{"任务标题":"原型设计","状态":"待办","优先级":"P1-高"}}' --as bot

# 批量新增（单次 ≤1000 条，列式格式）
lark-cli base +record-batch-create --base-token <token> --table-id <id> \
  --json '{"fields":["标题","状态"],"rows":[["任务A","待办"],["任务B","完成"]]}' --as bot

# 更新（推荐用 REST API 直调，避免 lark-cli 封装的格式限制）
lark-cli api PUT "/open-apis/bitable/v1/apps/<token>/tables/<tid>/records/<rec_id>" \
  --data '{"fields":{"状态":"已完成"}}' --as bot

# 批量更新
lark-cli base +record-batch-update --base-token <token> --table-id <id> \
  --json '[{"record_id":"rec_xxx","fields":{"状态":"已完成"}}]' --as bot

# Upsert（存在则更新，不存在则创建）
lark-cli base +record-upsert --base-token <token> --table-id <id> \
  --json '{"fields":{"标题":"唯一值"}}' --as bot

# 删除
lark-cli base +record-delete --base-token <token> --table-id <id> \
  --record-id <rec_id> --as bot

# 附件操作
lark-cli base +record-upload-attachment --base-token <token> --table-id <id> \
  --record-id <rec_id> --file /path/to/file.pdf --field-name "附件" --as bot
```

### View 级别

```bash
# 列出视图
lark-cli base +view-list --base-token <token> --table-id <id> --as bot

# 创建视图（grid/kanban/gallery/gantt/form）
lark-cli base +view-create --base-token <token> --table-id <id> \
  --json '{"name":"看板视图","type":"kanban"}' --as bot

# 设置筛选/排序/分组
lark-cli base +view-set-filter --base-token <token> --table-id <id> \
  --view-id <vid> --json '{"conditions":[{"field_name":"状态","operator":"is","value":["待办"]}],"conjunction":"and"}' --as bot

lark-cli base +view-set-sort --base-token <token> --table-id <id> \
  --view-id <vid> --json '[{"field_name":"截止日期","desc":false}]' --as bot
```

### Dashboard 级别

```bash
lark-cli base +dashboard-list --base-token <token> --as bot
lark-cli base +dashboard-create --base-token <token> --name "数据看板" --as bot
lark-cli base +dashboard-block-create --base-token <token> --dashboard-id <id> \
  --json '{"type":"chart","config":{...}}' --as bot
```

### 高级权限

```bash
lark-cli base +advperm-enable --base-token <token> --as bot
lark-cli base +role-create --base-token <token> --json '{"role_name":"销售","table_perm":{...}}' --as bot
lark-cli base +role-list --base-token <token> --as bot
```

### 自动化流程

```bash
lark-cli base +workflow-list --base-token <token> --as bot
lark-cli base +workflow-enable --base-token <token> --workflow-id <id> --as bot
```

### 数据聚合查询

```bash
lark-cli base +data-query --base-token <token> --dsl '{
  "table_id": "tbl_xxx",
  "aggregations": [{"field": "金额", "agg_type": "SUM"}],
  "groups": [{"field": "状态"}]
}' --as bot
```

---

## 字段类型速查

完整 27 种类型见 `references/bitable-field-types.md`。

**高频字段类型：**

| type | 名称 | 写入值格式 | 创建示例 |
|:--:|------|-----------|----------|
| 1 | 文本 | `"string"` | `{"field_name":"标题","type":1}` |
| 2 | 数字 | `123.45` | `{"field_name":"金额","type":2}` |
| 3 | 单选 | `"选项名"` | `{"type":3,"property":{"options":[...]}}` |
| 4 | 多选 | `["A","B"]` | `{"type":4,"property":{"options":[...]}}` |
| 5 | 日期 | `1704067200000` (ms) | `{"field_name":"日期","type":5}` |
| 7 | 复选框 | `true/false` | `{"field_name":"已确认","type":7}` |
| 11 | 人员 | `{"id":"ou_xxx"}` | `{"field_name":"负责人","type":11}` |
| 13 | 电话 | `"13800138000"` | `{"field_name":"电话","type":13}` |
| 15 | 超链接 | `{"link":"url","text":"显示"}` | `{"field_name":"链接","type":15}` |
| 17 | 附件 | `[{"file_token":"..."}]` | `{"field_name":"文件","type":17}` |
| 18 | 单向关联 | `["rec_id"]` | `{"field_name":"关联表","type":18}` |
| 20 | 公式 | 只读 | UI 配置 |
| 21 | 双向关联 | `["rec_id"]` | `{"field_name":"订单","type":21}` |
| 22 | 地理位置 | `{"location":"...","address":"..."}` | `{"field_name":"位置","type":22}` |
| 1001 | 创建时间 | 自动 | 自动字段 |
| 1005 | 自动编号 | 自动 | 自动字段 |

---

## 业务模板

### 模板 1：客户 CRM 表

```bash
lark-cli base +table-create \
  --base-token <app_token> \
  --json '{
    "name": "客户管理",
    "fields": [
      {"field_name": "客户姓名", "type": 1},
      {"field_name": "联系电话", "type": 13},
      {"field_name": "客户来源", "type": 3, "property": {"options": [
        {"name": "广告投放", "color": 0}, {"name": "老客推荐", "color": 1},
        {"name": "社交平台", "color": 2}, {"name": "线下活动", "color": 3},
        {"name": "其他", "color": 4}
      ]}},
      {"field_name": "意向线路", "type": 1},
      {"field_name": "意向人数", "type": 2},
      {"field_name": "意向日期", "type": 5},
      {"field_name": "跟单人", "type": 11},
      {"field_name": "跟进状态", "type": 3, "property": {"options": [
        {"name": "待联系", "color": 0}, {"name": "已联系", "color": 1},
        {"name": "已报价", "color": 2}, {"name": "已成单", "color": 3},
        {"name": "已流失", "color": 4}
      ]}},
      {"field_name": "备注", "type": 1}
    ]
  }'
```

### 模板 2：订单总表

```bash
lark-cli base +table-create \
  --base-token <app_token> \
  --json '{
    "name": "订单管理",
    "fields": [
      {"field_name": "订单编号", "type": 1},
      {"field_name": "客户姓名", "type": 1},
      {"field_name": "线路名称", "type": 1},
      {"field_name": "出行日期", "type": 5},
      {"field_name": "人数", "type": 2},
      {"field_name": "单价", "type": 2, "ui_type": "Currency"},
      {"field_name": "订单金额", "type": 2, "ui_type": "Currency"},
      {"field_name": "订单状态", "type": 3, "property": {"options": [
        {"name": "待确认", "color": 0}, {"name": "已确认", "color": 1},
        {"name": "已收款", "color": 2}, {"name": "已出行", "color": 3},
        {"name": "已取消", "color": 4}
      ]}},
      {"field_name": "导游", "type": 1},
      {"field_name": "车辆", "type": 1},
      {"field_name": "备注", "type": 1}
    ]
  }'
```

### 模板 3：线路产品库

```bash
lark-cli base +table-create \
  --base-token <app_token> \
  --json '{
    "name": "线路产品库",
    "fields": [
      {"field_name": "线路名称", "type": 1},
      {"field_name": "天数", "type": 2},
      {"field_name": "主题", "type": 3, "property": {"options": [
        {"name": "自然风光", "color": 0}, {"name": "民族文化", "color": 1},
        {"name": "美食之旅", "color": 2}, {"name": "户外探险", "color": 3},
        {"name": "亲子研学", "color": 4}, {"name": "康养度假", "color": 5}
      ]}},
      {"field_name": "成本价", "type": 2, "ui_type": "Currency"},
      {"field_name": "售价", "type": 2, "ui_type": "Currency"},
      {"field_name": "产品状态", "type": 3, "property": {"options": [
        {"name": "在售", "color": 0}, {"name": "下架", "color": 1},
        {"name": "草稿", "color": 2}
      ]}},
      {"field_name": "行程亮点", "type": 1},
      {"field_name": "包含项目", "type": 1},
      {"field_name": "注意事项", "type": 1}
    ]
  }'
```

### 创建完整运营中心

```bash
# ⚠️ 关键：要在知识库中管理，必须从 Wiki API 创建，而非 +base-create
# 错误做法：lark-cli base +base-create（创建的是独立 Base，无法归档到 Wiki）
# 正确做法：

# 1. 从 Wiki 创建 Bitable 节点
lark-cli wiki +node-create --obj-type bitable \
  --space-id 7643710721485753535 \
  --parent-node-token <分类节点token> \
  --title "贵州之客运营中心" \
  --as bot
# 返回：node_token (Wiki用) + obj_token (即 base_token, API用)

# 2. 先创建业务表（不能删最后一张表，必须先建后删）
lark-cli base +table-create --base-token <obj_token> --name "客户管理" --fields '[...]' --as bot

# 3. 再删除默认空表
lark-cli base +table-delete --base-token <obj_token> --table-id <default_tid> --yes --as bot
# 4. 添加视图
```

---

# Part B: 电子表格 (Sheet) via lark-cli api

完整参考见 `references/sheets-api.md`。

## 核心操作

```bash
# 获取电子表格元数据
lark-cli api GET "/open-apis/sheets/v3/spreadsheets/<spreadsheet_token>" --as bot

# 读取数据
lark-cli api GET "/open-apis/sheets/v2/spreadsheets/<token>/values/<sheet_id>!A1:D10" \
  --params '{"valueRenderOption":"ToString"}' --as bot

# 写入数据
lark-cli api PUT "/open-apis/sheets/v2/spreadsheets/<token>/values" \
  --data '{"valueRange":{"range":"<sheet_id>!A1:B2","values":[["姓名","金额"],["张三",1000]]}}' --as bot

# 追加数据
lark-cli api POST "/open-apis/sheets/v2/spreadsheets/<token>/values_append" \
  --data '{"valueRange":{"range":"<sheet_id>!A:B","values":[["新数据",2000]]}}' --as bot

# 创建电子表格
lark-cli api POST "/open-apis/sheets/v3/spreadsheets" \
  --data '{"title":"财务报表","folder_token":"<folder_token>"}' --as bot

# 在文档中嵌入 Sheet（通过 feishu-doc XML）
# <sheet type="blank"></sheet>
```

---

## 关键陷阱

| # | 陷阱 | 正确做法 |
|---|------|----------|
| 0 | **Bitable API 不支持浏览器 CORS 调用** | 飞书 Open API 不支持从浏览器 JS 直接调用（无 Access-Control-Allow-Origin 头）。前端 SPA 不能直连 Bitable API，必须通过后端代理或 Serverless 函数中转。若需多人共享数据的 Web 工具，考虑用 Supabase 等支持 CORS 的 BaaS，或 OSS JSON + 轻量代理方案（见 feishu-html references/oss-json-backend.md）。 |
|---|------|----------|
| 1 | **lark-cli 用字符串类型名** | `type: "text"/"select"/"number"/"datetime"/"user"` 不是整数 |
| 2 | **+field-create 不支持 property** | 带选项的 select 字段需用 REST API 直调 |
| 3 | **+record-batch-create 用列式** | 格式 `{"fields":["col1","col2"],"rows":[["a","b"]]}` |
| 4 | **+table-create 用 --name + --fields** | 不是 `--json`，fields 是字段数组 |
| 5 | **单选 type=3，不是 4** | type=4 是多选，写记录格式不同 |
| 6 | **重命名必须同时传 type** | 缺 type → `99992402 "type is required"` |
| 7 | **日期毫秒时间戳** | `int(datetime(2026,1,1).timestamp()*1000)` |
| 8 | **默认字段不可删除** | 只能隐藏或重命名 |
| 9 | **批量 ≤1000 条** | 超量需分批 |
| 10 | **搜索 operator 用 isGreater 非 >** | REST API operator 枚举: is/isNot/contains/isGreater/isLess/like/in |
| 11 | **公式/按钮/流程只读** | type=20/3001/24 只能 UI 创建 |
| 12 | **人员字段批写必须用数组** | type=11 写入 `[{"id":"ou_xxx"}]` 不是 `{"id":"ou_xxx"}` |
| 13 | **lark-cli api 用 --data 标志传 JSON** | 不是通过 stdin `input=`。`PATCH` 返回 404，用 `PUT` 更新记录。API 输出在 `stderr` 不是 `stdout`。 |
| 14 | **空字符串字段 API 不返回** | `结果摘要: ""` 的字段在 GET 响应中不会出现，需用 `.get("key", "")` 安全读取 |
| 15 | **+record-search 用 keyword 格式** | `--json '{"keyword":"xx","search_fields":["字段"]}'` 而非 Open API 的 `filter/conditions` 格式。结构化筛选用 `+record-list` + 视图过滤或 REST API。 |
| 16 | **lark-cli api GET 的 parent_node_token 放 URL 会被忽略** | 必须用 `--params '{"parent_node_token":"xxx"}'` 标志传递查询参数，直接拼在 URL query string 中 API 会忽略并返回 root 节点。 |
| 17 | **wiki +node-create 输出前3行是状态信息** | JSON 从第 4 行开始。解析前先 `tail -n +4` 或搜索第一个 `{"ok"` 位置。 |
| 18 | **不能删除 Bitable 的最后一张表** | 错误码 800080004。必须先建新表，再删默认空表。 |
| 19 | **lark-cli 不在 execute_code 的 PATH 中** | 完整路径 `/home/aorus/.local/bin/lark-cli`。或用 `terminal()` 运行脚本（PATH 正常）。 |
| 20 | **+table-create 字段类型错误时表仍创建** | 传入错误的 type 值（如整数而非字符串）时，API 可能返回错误但仍创建了空表（只有默认 auto_number 字段）。检查 `+table-list` 确认，已创建的表需手动加字段或删除重建。 |
| 20 | **+table-create 字段类型错误时表仍创建** | 传入错误的 type 值（如整数而非字符串）时，API 可能返回错误但仍创建了空表（只有默认 auto_number 字段）。检查 `+table-list` 确认，已创建的表需手动加字段或删除重建。 |
| 21 | **+table-create 用 string type vs REST API 用 int type** | lark-cli CLI 用 `"text"`/`"number"`/`"datetime"`；REST API `+api POST .../tables` 用整数 1/2/5。混用会报 `800010701 Invalid discriminator`。 |
| 22 | **+table-create 部分成功（表建了但字段失败）** | 如果 type 格式错误，表本身会创建成功（有 table_id），但字段全部跳过只留 auto_number ID。此时表已存在，重新 create 同名会报 `800010102 validation_error`。正确做法：用 REST API 的 `POST .../tables/{id}/fields` 单独补加字段。 |

---

## 与现有技能的边界

```
feishu-wiki          → 知识库文档读写（Bitable 速查已迁移至此）
feishu-table (本)    → 多维表格 + 电子表格全生命周期
feishu-doc           → 文档中嵌入表格（<bookmark> 或 <sheet> XML）
kanban-orchestrator  → 任务分解编排（底层可调用本技能建表）
```

---

## References

- `references/bitable-field-types.md` — 全部 27 种字段类型、属性结构、写入值格式
- `references/sheets-api.md` — 电子表格 REST API 完整参考（v2 + v3，37+ 端点）
- `references/bitable-spa-integration.md` — 使用 Bitable 作为 Web App 后端：CORS 限制与 FC 代理方案
- `references/bitable-api.md` — 多维表格 REST API 端点详情（继承自 feishu-wiki）

## Templates

- `templates/crm-table.json` — 客户 CRM 表字段定义
- `templates/order-table.json` — 订单总表字段定义
- `templates/product-table.json` — 线路产品库字段定义
- `templates/user-profile-crm.json` — 用户画像 CRM 表（旅行行业·偏好+预算+出行方式）
