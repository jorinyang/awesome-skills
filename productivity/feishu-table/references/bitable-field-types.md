# 多维表格字段类型全集

> 来源：飞书开放平台 API v1.0.0.3331 — 字段编辑指南
> 验证日期：2026-05-27

## 字段基本结构

```json
{
    "field_id": "fldYWaldeW",
    "field_name": "字段名",
    "type": 1,
    "description": "描述",
    "is_primary": true,
    "property": null,
    "ui_type": "Text",
    "is_hidden": false
}
```

## type 枚举全集（27 种）

| type | 名称 | ui_type | 可写 | property 说明 |
|:--:|------|---------|:--:|--------------|
| 1 | 文本 | Text/Email/Barcode | ✅ | `null` |
| 2 | 数字 | Number/Progress/Currency/Rating | ✅ | 数字：`{"decimal_places":2,"use_separate":true}`；进度：`{"range":{"min":0,"max":100},"show_percent":true}`；货币：`{"currency_type":"CNY","decimal_places":2}`；评分：`{"max":5,"icon":"star"}` |
| 3 | 单选 | SingleSelect | ✅ | `{"options":[{"name":"选项","color":0,"id":"opt_xxx"}]}` |
| 4 | 多选 | MultiSelect | ✅ | 同上 |
| 5 | 日期 | DateTime | ✅ | `{"format":"yyyy/MM/dd"}` — 值用毫秒时间戳 |
| 7 | 复选框 | Checkbox | ✅ | `null` |
| 11 | 人员 | User | ✅ | `{"is_multiple":false,"is_notified":false}` |
| 13 | 电话号码 | Phone | ✅ | `null` |
| 15 | 超链接 | Url | ✅ | `{"type":"link"}` |
| 17 | 附件 | Attachment | ✅ | `null` |
| 18 | 单向关联 | SingleLink | ✅ | `{"table_id":"tbl_xxx","view_id":"vew_xxx"}` — 目标表必须存在 |
| 19 | 查找引用 | Lookup | ✅ | `{"table_id":"...","field_id":"...","filter":{"conditions":[...]}}` |
| 20 | 公式 | Formula | ⚠️ 只读 | `{"expression":"[金额]*[人数]","formatter":"number"}` — API 可创建但公式复杂时建议 UI 配置 |
| 21 | 双向关联 | DuplexLink | ✅ | `{"table_id":"tbl_xxx"}` — 目标表必须存在 |
| 22 | 地理位置 | Location | ✅ | `null` |
| 23 | 群组 | GroupChat | ✅ | `null` |
| 24 | 流程 | Stage | ❌ 只读 | 不支持写接口新增/编辑 |
| 1001 | 创建时间 | CreatedTime | ❌ 自动 | `null` — 系统自动填充 |
| 1002 | 最后更新时间 | ModifiedTime | ❌ 自动 | `null` |
| 1003 | 创建人 | CreatedUser | ❌ 自动 | `null` |
| 1004 | 修改人 | ModifiedUser | ❌ 自动 | `null` |
| 1005 | 自动编号 | AutoNumber | ❌ 自动 | `{"type":"custom","rules":[{"type":"created_time","value":"yyyyMMdd"},{"type":"auto_number","value":4}]}` |
| 3001 | 按钮 | Button | ❌ 只读 | 不支持写接口新增/编辑 |

## 写入值格式参考

| type | 写入值 | 示例 |
|:--:|--------|------|
| 1 | string | `"张三"` |
| 2 | number | `123.45` |
| 3 | string（选项名） | `"待联系"` |
| 4 | string[] | `["标签A","标签B"]` |
| 5 | int64 (ms) | `1704067200000` |
| 7 | boolean | `true` |
| 11 | `[{"id":"ou_xxx"}]` | 人员数组 |
| 13 | string | `"13800138000"` |
| 15 | `{"link":"url","text":"显示"}` | 链接对象 |
| 17 | `[{"file_token":"..."}]` | 附件 token 数组 |
| 18 | `["rec_xxx"]` | 关联记录 ID 数组 |
| 21 | `["rec_xxx"]` | 关联记录 ID 数组 |
| 22 | `{"location":"","address":"","pname":"","cityname":"","adname":""}` | 位置对象 |
| 23 | `["oc_xxx"]` | 群组 ID 数组 |

## 索引字段 (is_primary=true)

第一列为索引列，不可删除/移动/隐藏，仅支持 type: 1, 2, 5, 13, 15, 20, 22。

## 默认字段

每个新表自带 4 个不可删除的字段：

| 默认名称 | type | 可重命名 |
|----------|:--:|:--:|
| 文本 | 1 | ✅ |
| 单选 | 3 | ✅ |
| 日期 | 5 | ✅ |
| 附件 | 17 | ✅ |

> ⚠️ 重命名时 `PUT /fields/{id}` 必须同时传 `field_name` + `type`。

## 单选/多选选项结构

```json
{
  "options": [
    {"name": "待联系", "color": 0, "id": "opt_xxx"},
    {"name": "已联系", "color": 1, "id": "opt_yyy"}
  ]
}
```

颜色值：0=灰, 1=蓝, 2=绿, 3=黄, 4=红, 5=紫, 6=青, 7=橙, 8=粉色, 9=靛蓝...
