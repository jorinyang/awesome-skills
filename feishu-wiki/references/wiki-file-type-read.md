# Wiki 文件类型节点读取

## 问题

当 Wiki 节点不是原生飞书文档（docx）而是上传文件（PDF/Word/图片等）时，`lark-cli docs +fetch` 会失败：

```
error 3380002: "Unsupported document type 'file'. Only docx is supported."
```

`feishu_doc_read` 工具同理不可用（要求 docx 类型）。

## 诊断

收到 Wiki URL 后，不要直接调用 `docs +fetch`。先用 `wiki +node-get` 确认节点类型：

```bash
lark-cli wiki +node-get --node-token <token> --format json
```

查看返回的 `data.node.node_type`：
- `docx` → 用 `docs +fetch --api-version v2` 正常读取
- `file` → 走下方 Drive 下载路径
- `folder` → 用 `wiki +node-list` 列出子节点

## 解决：Drive 下载路径

```bash
# 1. 确认节点类型 + 提取 obj_token
lark-cli wiki +node-get --node-token <token> --format json
# 返回中 obj_token 在 data.node.obj_token

# 2. 下载文件
lark-cli drive +download --token <obj_token> --output ./downloaded_file

# 3. 根据文件类型解析
# PDF → pymupdf 提取文字，或 vision 工具 OCR（图片型 PDF）
# Word (.docx) → python-docx 读取
# 图片 → vision 工具识别
```

## 所需 Scope

- `wiki:node:retrieve` — 调用 `wiki +node-get`
- Drive 下载可能需要 `drive:drive:readonly`

缺失时使用 split-flow 授权：
```bash
lark-cli auth login --scope "wiki:node:retrieve" --no-wait --json
```

## 触发条件

- `docs +fetch` 对 Wiki URL 返回 3380002
- `feishu_doc_read` 对 Wiki token 返回 "not a docx" 类错误
- 用户提供的 Wiki 链接无法直接读取内容
