# 飞书多维表格 (Bitable) API 参考

> 验证日期: 2026-05-27 | App ID: cli_aa9ead14c2641cc3

## 凭证获取

复用飞书自建应用 tenant_access_token，与 docx/wiki API 共用同一 token。
无需额外 scope —— 当前 app 的 bitable 权限已开通。

```bash
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")
```

## 已验证的 API 端点

| 操作 | 方法 | 端点 | 状态 |
|------|------|------|:--:|
| 创建多维表格 | POST | `/bitable/v1/apps` | ✅ |
| 删除多维表格 | DELETE | `/bitable/v1/apps/{app_token}` | ✅ |
| 列出所有表格 | GET | `/bitable/v1/apps?page_size=N` | 待测 |
| 添加字段 | POST | `/bitable/v1/apps/{app_token}/tables/{table_id}/fields` | ✅ |
| 删除字段 | DELETE | `/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}` | ✅ |
| 重命名字段 | PUT | `.../fields/{field_id}` | ✅ 需同时传 type |
| 添加记录 | POST | `.../tables/{table_id}/records` | ✅ |
| 更新记录 | PUT | `.../tables/{table_id}/records/{record_id}` | ✅ |
| 查询记录 | GET | `.../tables/{table_id}/records` | ✅ |
| 搜索记录 | POST | `.../tables/{table_id}/records/search` | 待测 |

## 字段类型 (field type)

| type | 名称 | 备注 |
|:----:|------|------|
| 1 | 文本 | 单行文本 |
| 3 | 单选 | **不是 4！** 4=多选 |
| 5 | 日期 | 值用毫秒时间戳 |
| 17 | 附件 | — |
| 1001 | 日期(格式1) | 与 type=5 行为相同 |
| 1002 | 日期(格式2) | 与 type=5 行为相同 |

## 关键陷阱

### 1. 单选是 type=3，不是 type=4
```bash
# ❌ 错误：type=4 是「多选」，记录写入报错 MultiSelectFieldConvFail
-d '{"field_name":"状态","type":4,...}'

# ✅ 正确：type=3 是「单选」
-d '{"field_name":"状态","type":3,...}'
```

### 2. 默认字段可重命名，不可删除
每个新表格自带 4 个默认字段：`文本`(type=1)、`单选`(type=3)、`日期`(type=5)、`附件`(type=17)。
- ❌ 不能通过 API 删除（硬限制）
- ✅ 可以重命名：`PUT /fields/{id}` + `{"field_name":"新名称","type":N}` — **必须同时传 type！**
- ⚠️ 之前的 `99992402` 错误是因为只传了 `field_name` 没传 `type`，API 返回 `"type is required"`

### 3. 日期值使用毫秒时间戳
```python
import datetime
# 2026-01-01 → 1704067200000
ts = int(datetime.datetime(2026, 1, 1).timestamp() * 1000)
```

### 4. 删除比特able会返回非JSON响应
`DELETE /bitable/v1/apps/{app_token}` 在成功时可能返回空响应体而非 JSON。
解析前检查 Content-Type。

## 创建完整看板的字段定义

```bash
# 状态（单选）
{"field_name":"状态","type":3,"property":{"options":[
  {"name":"待办","color":0},{"name":"进行中","color":1},
  {"name":"已完成","color":2},{"name":"已逾期","color":3}
]}}

# 优先级（单选）
{"field_name":"优先级","type":3,"property":{"options":[
  {"name":"P0-紧急","color":0},{"name":"P1-高","color":1},
  {"name":"P2-中","color":2},{"name":"P3-低","color":3}
]}}

# 文本字段
{"field_name":"任务标题","type":1}
{"field_name":"负责人","type":1}
{"field_name":"执行人","type":1}
{"field_name":"所属项目","type":1}
{"field_name":"任务详情","type":1}

# 日期字段
{"field_name":"开始日期","type":5}
{"field_name":"截止日期","type":5}
```

## 记录 CRUD 示例

### 创建
```bash
curl -s -X POST ".../tables/$TABLE/records" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"fields":{
    "任务标题":"产品原型设计",
    "状态":"待办",
    "优先级":"P1-高",
    "负责人":"月夜",
    "执行人":"余媛天",
    "所属项目":"Hermes看板",
    "开始日期":1766851200000,
    "截止日期":1767542400000,
    "任务详情":"完成高保真原型"
  }}'
```

### 更新
```bash
curl -s -X PUT ".../tables/$TABLE/records/$RECORD_ID" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"fields":{"状态":"进行中","任务详情":"原型已完成，进入评审"}}'
```

### 查询
```bash
curl -s ".../tables/$TABLE/records?page_size=20" \
  -H "Authorization: Bearer $TOKEN"
```
