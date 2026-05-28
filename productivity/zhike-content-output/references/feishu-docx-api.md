# Feishu Docx API Reference

> 飞书在线文档 API 关键技术约束 — 2026-05-25 实测更新

## 凭证

```
App ID:     cli_aa9ead14c2641cc3
App Secret: ZUUm7yI7HmfLi42ki8fPTgZzbj2AuTeM  (~/.hermes-feishu/.env: FEISHU_APP_SECRET)
Token刷新:  POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
```

## Block Types 实测结果（2026-05-25 实测修正）

| block_type | 类型 | 字段名 | 创建结果 |
|------------|------|--------|---------|
| 2 | 文本段落 | `"text"` | ✅ 成功 |
| 3 | 一级标题 | `"heading1"` | ✅ 成功 |
| 4 | 二级标题 | `"heading2"` | ✅ 成功 |
| 5 | 三级标题 | `"heading3"` | ✅ 成功 |
| 7 | 无序列表 | `"bullet"` | ❌ block not support to create |
| 9 | 引用块 | `"quote"` | ❌ invalid param |
| 10 | callout | `"callout"` | ❌ invalid param |
| 12 | （旧称，废弃） | — | ❌ invalid param |
| 13 | 有序列表 | `"ordered"` | ❌ block not support to create |
| 15 | 引用块 | `"quote"` | ❌ invalid param |
| 22 | 分割线 | `"divider"` | ❌ invalid param |

**结论：飞书在线文档 API 仅支持 text、heading1、heading2、heading3 四种块类型。**

**关键细节：**
- `block_type=2` 必须使用字段名 `"text"`，不能写成 `"bullet"`、`"quote"` 等
- `text` 块的 elements 结构：`{"text_run": {"content": "...", "text_element_style": {}}}`
- `heading` 块的 elements 结构相同，区别仅在于 `block_type` 和字段名
- 两种块的 `text_element_style` 和 `style` 字段均不可省略（否则 1770001 invalid param）

## 关键 API 端点

```
获取 Token:     POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
创建文档:       POST https://open.feishu.cn/open-apis/docx/v1/documents
读取原始内容:   GET  https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/raw_content
读取块:        GET  https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}/children
创建块:        POST https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}/children
批量删除块:    DELETE https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}/children/batch_delete
                Body: {"start_index": int, "end_index": int}
重命名文档:     PATCH https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}  (需查文档确认)
移动/复制文件:  drive/v1/files/{file_token}/move, /copy
```

## 清空文档并重建流程

当文档内容需要大幅修改时（推荐先删后建）：

1. **获取所有块**：GET `/blocks/{doc_id}/children?page_size=500`
2. **批量删除**：对 page block（`block_id = doc_id`）调用 batch_delete，每次删除 start_index=0, end_index=10
3. **重建**：用 `POST .../children` 批量插入新块（最多 50 个/次）

## 文档移动到知识库

知识库 API 需要权限：`wiki:space:readonly` / `wiki:space:full_access`
当前 App 凭证权限不足，无法通过 API 操作知识库节点。

父目录 parent_token（文档当前所在位置，根目录）: `nodcnilpIWVPJxWc721NCV1Ij0I`
知识库 space_id: `7643710721485753535`

## 安全注意

- App Secret 不要硬编码，通过 `~/.hermes-feishu/.env` 读取 `FEISHU_APP_SECRET`
- tenant_access_token 有效期约 2 小时，超时需刷新
