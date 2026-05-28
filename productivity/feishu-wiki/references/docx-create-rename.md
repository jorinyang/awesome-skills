# Feishu docx Create/Rename/Move — Session 2025-05-25 (Second Session)

## Block Insertion Constraints

**Only heading types work** via `POST /docx/v1/documents/{doc_token}/blocks/{block_id}/children`:

| block_type | Type | Result |
|---|---|---|
| 3 | heading1 | ✅ Works |
| 4 | heading2 | ✅ Works |
| 5 | heading3 | ✅ Works |
| 2 | text | ❌ `block not support to create` |
| 7 | bullet | ❌ `block not support to create` |
| 12 | callout | ❌ `1770001 invalid param` |
| 13 | quote | ❌ `1770001 invalid param` |
| 14 | ordered | ❌ `block not support to create` |
| 15 | unordered | ❌ `block not support to create` |

**Confirmed working document**: `AvjZdMeZBoFDfBxYdKKc5t6bnbd` — created via `POST /docx/v1/documents`, populated entirely with heading blocks.

## Rename API Failures

All rename attempts failed:

```
PATCH /docx/v1/documents/{doc_id}
→ {"code":1770001,"msg":"invalid param"}

POST /docx/v1/documents/{doc_id}/rename
→ 404

PATCH /drive/v1/files/{file_token}
→ {"code":99992402,"msg":"...type field required"}
```

**Root cause**: `type` field is immutable post-creation via drive API. The document type is set at creation time and cannot be changed.

**Workaround**: Create document with the correct name upfront (if possible), or have the user rename manually in Feishu UI.

## Move/Organize API Failures

Wiki space enumeration returns empty:
```bash
GET /wiki/v2/spaces → {"code":0,"data":{"has_more":false,"items":[]}}
```

`get_by_obj_token` fails with `131002 space_id is not int` for string-form node tokens. The wiki v2 API expects integer space_id but the wiki setup uses string tokens.

**Workaround**: Create document in root folder, then user manually moves it to the correct knowledge base directory in Feishu UI.

## Key Insight

The Feishu Open API for docx has significant limitations compared to the UI:
- Cannot set document title at creation time (must be done in UI or via separate rename endpoint)
- Cannot insert non-heading block types
- Cannot move documents between folders via API
- Wiki space enumeration is unreliable with current app permissions

For complex documents, the API is best used to create a blank structural container; the user should populate content and organize via the Feishu UI.
