# 飞书电子表格 API 读写模式

当 `feishu_doc_read` 报 "Unsupported document type 'sheet'" 或 `lark-cli docs fetch` 报 3380002 时，需直接用飞书 Sheets API。

## 前置：获取 tenant_access_token

```python
import os, json, subprocess

app_id = os.environ.get('FEISHU_APP_ID', 'cli_aa9ead14c2641cc3')
app_secret = os.environ.get('FEISHU_APP_SECRET', '')

r = subprocess.run([
    'curl', '-s', '-X', 'POST',
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps({"app_id": app_id, "app_secret": app_secret})
], capture_output=True, text=True, timeout=15)
token = json.loads(r.stdout)['tenant_access_token']
auth = 'Bearer ' + token
```

## 关键发现：node_token ≠ obj_token

Wiki 中的电子表格有两个 token：
- `node_token`：知识库节点 token（URL 中可见）
- `obj_token`：底层 sheet 对象的真实 token（API 操作需要此值）

**获取 obj_token**：调用 wiki API：
```bash
curl -s "https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={NODE_TOKEN}" \
  -H "Authorization: Bearer $TOKEN"
```
响应中的 `data.node.obj_token` 即为真实 token。

## 读取表格元数据（获取 sheet_id）

```bash
curl -s "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{OBJ_TOKEN}/sheets/query" \
  -H "Authorization: Bearer $TOKEN"
```
响应中 `data.sheets[].properties.sheetId` 即为 sheet_id（如 `6d0292`）。

## 读取单元格值（v2 API）

Range 格式：`{sheet_id}!A1:L20`——**必须带 sheet_id 前缀**，不能只用 `A1:L20` 或 `Sheet1!A1:L20`。

```bash
curl -s "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{OBJ_TOKEN}/values/{sheet_id}!A1:L30" \
  -H "Authorization: Bearer $TOKEN"
```

响应结构：
```json
{
  "code": 0,
  "data": {
    "valueRange": {
      "values": [["cellA1", "cellB1", ...], ["cellA2", ...]]
    }
  }
}
```

## 批量写入单元格（values_batch_update）

适用于多行多列一次性写入。POST body 中每个 valueRange 指定一个矩形区域：

```python
payload = {
    "valueRanges": [
        {
            "range": "{sheet_id}!J3:L3",
            "values": [["J值", "K值", "L值"]]
        },
        {
            "range": "{sheet_id}!J4:L4",
            "values": [["J值", "K值", "L值"]]
        }
    ]
}

r = subprocess.run([
    'curl', '-s', '-X', 'POST',
    'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{OBJ_TOKEN}/values_batch_update',
    '-H', 'Authorization: ' + auth,
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(payload, ensure_ascii=False).encode('utf-8')
], ...)
```

注意：
- `ensure_ascii=False` 保留中文
- Content-Type 需显式设置
- body 需 `.encode('utf-8')` 避免 curl 编码问题

## 常见错误码

| 错误码 | 含义 | 原因 |
|--------|------|------|
| 1310214 | 无权限 | bot 未被授权访问该表格，或使用了错误的 token 类型 |
| 90215 | sheetId 不存在 | range 中的 sheet_id 不正确，或未带 sheet_id 前缀 |
| 3380002 | 不支持的类型 | `lark-cli docs fetch` 无法读取 sheet，需用 Sheets API |

## 与 feishu_doc_read 的分流规则

- **URL 含 `/wiki/` 且是 docx**：用 `feishu_doc_read(doc_token=...)`
- **URL 含 `/wiki/` 且是 sheet**：先用 wiki API 获取 obj_token，再用 Sheets API
- **飞书评论上下文**：`feishu_doc_read` 大概率可用
- **非评论上下文**：直接用 API curl
