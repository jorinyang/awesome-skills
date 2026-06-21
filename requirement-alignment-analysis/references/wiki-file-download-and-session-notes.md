# Reading wiki "file" type nodes (PDF, txt, md)

When wiki nodes are uploaded files (`obj_type: "file"`), they cannot be read via `docs +fetch` (error 3380002) or `feishu_doc_read`. Use this two-step workflow:

## Step 1: Resolve with wiki +node-get

```bash
lark-cli wiki +node-get --as user \
  --node-token "https://xxx.feishu.cn/wiki/<token>" \
  --format json
```

Always pass the full URL so `--obj-type` is auto-inferred. Extract `obj_token` from output.

⚠️ **Missing scope trap**: `wiki +node-get` requires `wiki:node:retrieve` scope. If you get `missing_scope` error, run split-flow auth:
```bash
lark-cli auth login --scope "wiki:node:retrieve" --no-wait --json
# → extract verification_url, generate QR with: lark-cli auth qrcode "<url>" --output "./qr.png"
# → send QR to user, wait for confirmation, then: lark-cli auth login --device-code <code>
```

## Step 2: Download with drive +download

```bash
lark-cli drive +download --file-token "<obj_token>" \
  --output "./filename.ext" --as user
```

## Critical Pitfalls

1. `--output` must be a **relative path** within cwd. Absolute paths rejected as "unsafe file path". Use `terminal(workdir=...)` or `cd /tmp` first.
2. Scopes needed: `wiki:node:retrieve` + `drive:file:download`
3. `docs +create --api-version v2` does not support `--title` in v2; title is the first H1 in `--content`.
4. `docs +create --content @file` — the @file path must be relative (same cwd constraint).
5. **3380002 error pattern**: `lark-cli docs +fetch` returning `3380002: Unsupported document type 'file'. Only docx is supported.` means the wiki node is an uploaded file (PDF/txt/md), not a native docx. This is the trigger to switch to the node-get → download path above. Do NOT retry `docs +fetch` — it will fail the same way every time.
6. **feishu_doc_read unavailable**: `"Feishu client not available (not in a Feishu comment context)"` means this tool only works inside Feishu comment replies. Use `lark-cli docs +fetch` or the node-get → download path instead.
