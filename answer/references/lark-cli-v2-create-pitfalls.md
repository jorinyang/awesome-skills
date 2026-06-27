# lark-cli v2 docs +create 三大陷阱

> 2026-06-24 会话发现 · lark-cli v1.0.53

## 陷阱 1：--title 已废弃

`--title` 不再支持。lark-cli v1.0.53+ 报错：
```
docs +create is v2-only; --title is no longer supported
```

**正确做法**：标题写在 markdown 内容的第一行：
```markdown
<title>文档标题</title>

# 正文开始...
```

使用的命令只保留 `--content @file.md`，不加 `--title`：
```bash
lark-cli docs +create --api-version v2 --doc-format markdown \
  --content @_content.md --parent-token TOKEN --as bot
```

## 陷阱 2：@file 只接受 cwd 相对路径

传绝对路径（如 `@/tmp/x.md`）报错：
```
unsafe file path
```

**正确做法**：将文件放在当前工作目录下，用 `@./filename.md` 或 `@filename.md`。

## 陷阱 3：两步法产生空文档

Wiki API 先建节点 + v2 update 写内容的"两步法"在 lark-cli v1.0.40-v1.0.44 上返回 `ok:true` 但 blocks=0，文档永远为空。

**正确做法**：只用一步法——`docs +create` 同时传内容。

## 写入后验证

每次写入后立即验证：
```bash
lark-cli docs +fetch --api-version v2 --doc {document_id} --as bot
# 确认 revision_id > 1 且包含文本内容
```
