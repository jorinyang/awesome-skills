# 电子表格 (Sheet) REST API 速查

> 来源：飞书开放平台 Sheets v2 + v3
> 接口基础 URL：`https://open.feishu.cn/open-apis`
> 工具：`lark-cli api` 直调

---

## 表格级别

### 创建电子表格
```bash
lark-cli api POST "/open-apis/sheets/v3/spreadsheets" \
  --data '{"title":"财务报表","folder_token":"<folder_token>"}' --as bot
```

### 获取表格信息
```bash
lark-cli api GET "/open-apis/sheets/v3/spreadsheets/<spreadsheet_token>" --as bot
# 返回：title, sheets[], sheetId, rowCount, columnCount, blockInfo 等
```

### 修改表格属性
```bash
lark-cli api PATCH "/open-apis/sheets/v3/spreadsheets/<spreadsheet_token>" \
  --data '{"title":"新名称"}' --as bot
```

---

## 工作表级别

### 查询工作表
```bash
lark-cli api GET "/open-apis/sheets/v3/spreadsheets/<token>/sheets/query" --as bot
```

### 移动行列
```bash
lark-cli api POST "/open-apis/sheets/v3/spreadsheets/<token>/sheets/<sheet_id>/move_dimension" \
  --data '{"source":{"majorDimension":"ROWS","startIndex":0,"endIndex":2},"destinationIndex":5}' --as bot
```

---

## 数据读写 (v2)

### 读取单个范围
```bash
lark-cli api GET "/open-apis/sheets/v2/spreadsheets/<token>/values/<sheet_id>!A1:D10" \
  --params '{"valueRenderOption":"ToString","dateTimeRenderOption":"FormattedString"}' --as bot
```

### 读取多个范围
```bash
lark-cli api GET "/open-apis/sheets/v2/spreadsheets/<token>/values_batch_get" \
  --params '{"ranges":["<sheet1>!A1:B5","<sheet2>!D1:E5"],"valueRenderOption":"ToString"}' --as bot
```

### 写入单个范围
```bash
lark-cli api PUT "/open-apis/sheets/v2/spreadsheets/<token>/values" \
  --data '{
    "valueRange": {
      "range": "<sheet_id>!A1:B2",
      "values": [
        ["姓名", "金额"],
        ["张三", 1000]
      ]
    }
  }' --as bot
```

### 写入多个范围
```bash
lark-cli api PUT "/open-apis/sheets/v2/spreadsheets/<token>/values_batch_update" \
  --data '{
    "valueRanges": [
      {"range": "<sheet_id>!A1:B2", "values": [["姓名","金额"],["张三",1000]]},
      {"range": "<sheet_id>!D1:E2", "values": [["日期","备注"],["2026-01-01",""]]}
    ]
  }' --as bot
```

### 插入数据（向下推已有数据）
```bash
lark-cli api POST "/open-apis/sheets/v2/spreadsheets/<token>/values_prepend" \
  --data '{"valueRange":{"range":"<sheet_id>!A:B","values":[["新行"]]}}' --as bot
```

### 追加数据（加到末尾）
```bash
lark-cli api POST "/open-apis/sheets/v2/spreadsheets/<token>/values_append" \
  --data '{"valueRange":{"range":"<sheet_id>!A:B","values":[["新数据", 2000]]}}' --as bot
```

---

## 行列操作 (v2)

### 插入/增加/更新/删除行列
```bash
# 插入行列（在指定位置插入空白行列）
lark-cli api POST "/open-apis/sheets/v2/spreadsheets/<token>/insert_dimension_range" \
  --data '{"dimension":{"sheetId":"<sheet_id>","majorDimension":"ROWS","startIndex":0,"endIndex":1},"inheritStyle":"BEFORE"}' --as bot

# 增加行列（在末尾增加）
lark-cli api POST "/open-apis/sheets/v2/spreadsheets/<token>/create_dimension_range" \
  --data '{"dimension":{"sheetId":"<sheet_id>","majorDimension":"COLUMNS","length":3}}' --as bot

# 更新行列属性
lark-cli api PUT "/open-apis/sheets/v2/spreadsheets/<token>/dimension_range" \
  --data '{"dimension":{"sheetId":"<sheet_id>","majorDimension":"ROWS","startIndex":0,"endIndex":1},"dimensionProperties":{"pixelSize":40}}' --as bot

# 删除行列
lark-cli api DELETE "/open-apis/sheets/v2/spreadsheets/<token>/dimension_range" \
  --data '{"dimension":{"sheetId":"<sheet_id>","majorDimension":"COLUMNS","startIndex":1,"endIndex":2}}' --as bot
```

---

## 单元格样式 (v2)

### 设置样式
```bash
lark-cli api PUT "/open-apis/sheets/v2/spreadsheets/<token>/style" \
  --data '{
    "appendStyle": {
      "range": "<sheet_id>!A1:C1",
      "style": {
        "bold": true,
        "fontSize": 14,
        "fontColor": "#000000",
        "backgroundColor": "#FFFF00",
        "hAlign": "center",
        "vAlign": "middle"
      }
    }
  }' --as bot
```

### 批量设置样式
```bash
lark-cli api PUT "/open-apis/sheets/v2/spreadsheets/<token>/styles_batch_update" \
  --data '{
    "data": [
      {"ranges": ["<sheet_id>!A1:C1"], "style": {"bold": true, "fontSize": 14}},
      {"ranges": ["<sheet_id>!A2:C10"], "style": {"fontSize": 12}}
    ]
  }' --as bot
```

---

## 合并单元格 (v2)

```bash
# 合并
lark-cli api POST "/open-apis/sheets/v2/spreadsheets/<token>/merge_cells" \
  --data '{"range":"<sheet_id>!A1:C1","mergeType":"MERGE_ALL"}' --as bot

# 拆分
lark-cli api POST "/open-apis/sheets/v2/spreadsheets/<token>/unmerge_cells" \
  --data '{"range":"<sheet_id>!A1:C1"}' --as bot
```

mergeType: `MERGE_ALL` | `MERGE_ROWS` | `MERGE_COLUMNS`

---

## Range 格式

| 格式 | 示例 | 说明 |
|------|------|------|
| 精确范围 | `<sheetId>!A1:B5` | A1 到 B5 |
| 列范围 | `<sheetId>!A:B` | A 列到 B 列全部 |
| 混合范围 | `<sheetId>!A2:B` | A2 起 + A-B 列 |
| 全表 | `<sheetId>` | 整个工作表 |

**获取 sheetId：** 从 `/sheets/v3/spreadsheets/{token}` 响应的 `sheets[].sheetId` 字段。
