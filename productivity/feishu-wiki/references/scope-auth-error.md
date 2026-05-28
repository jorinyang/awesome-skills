# Feishu Wiki Scope Auth Error — Session 2025-05-25

## URLs Attempted
- Doc-based wiki: `wiki/XcArwqB42is4ugkSuCIcOleInpd?fromScene=spaceOverview` (使命/愿景/价值观)
- Space home: `wiki/NBW2wANDViY5BSkbVA1cnETfnEf?fromScene=spaceOverview&open_tab_from=wiki_home` (知识库首页)

## Error Sequence

### 1. feishu_doc_read — not in Feishu comment context
```
"Feishu client not available (not in a Feishu comment context)"
```
Tool only works during active comment/reply sessions.

### 2. Wiki API — 99991672 Scope Error
```bash
curl "https://open.feishu.cn/open-apis/wiki/v2/spaces/get_by_obj_token?obj_token=XcArwqB42is4ugkSuCIcOleInpd&obj_type=wiki"
```
```json
{"code":99991672,"msg":"Access denied. One of: [wiki:wiki, wiki:wiki:readonly, wiki:space:read]"}
```
**Root cause:** Scope authorized + published BUT app version NOT published.

### 3. After publish — 131002 param err
```bash
curl "https://open.feishu.cn/open-apis/wiki/v2/spaces/get_by_obj_token?obj_token=XcArwqB42is4ugkSuCIcOleInpd&obj_type=4"
```
```json
{"code":131002,"msg":"param err: space_id is not int"}
```
`get_by_obj_token` fails for this wiki. Not usable.

### 4. Wiki spaces list — empty
```bash
curl "https://open.feishu.cn/open-apis/wiki/v2/spaces"
```
```json
{"code":0,"data":{"has_more":false,"items":[]}}
```
App has no access to any wiki spaces via wiki API.

### 5. Doc API — SUCCESS ✅
```bash
# Metadata
curl "https://open.feishu.cn/open-apis/docx/v1/documents/<obj_token>"
# Returns: {"code":0,"data":{"document":{..."title":"..."}}}

# Raw content
curl "https://open.feishu.cn/open-apis/docx/v1/documents/<obj_token>/raw_content"
# Returns: full document content in markdown
```

## Key Insights

1. **Scope + authorization ≠ published**: Adding a scope in the console does NOT update the token until a new app version is published. 「版本管理与发布」→ 「创建版本」→ 「发布」

2. **Doc API works for both patterns**: For doc-based wikis (most common), `obj_token` IS the `document_id`. The Doc API (`docx/v1/documents/<obj_token>/raw_content`) bypasses the wiki layer entirely and works for:
   - Individual doc-based wiki nodes
   - Space overview pages (`?fromScene=spaceOverview&open_tab_from=wiki_home`)

3. **Wiki API is for native wiki nodes only**: `wiki/v2/spaces/get_by_obj_token` and `wiki/v2/nodes/...` are for pages created natively in wiki — not doc-backed wiki pages.

4. **`obj_type=4`** is the correct integer for wiki node resolution (not the string "wiki").

## Resolution Path
1. Confirm scope is authorized (developer console shows green)
2. Go to 「版本管理与发布」→ 「创建版本」→ 「发布」
3. Re-fetch tenant_access_token (old token has old scopes)
4. Use Doc API: `GET /docx/v1/documents/<obj_token>/raw_content`
5. If Doc API 404 → try Wiki Nodes API as fallback
