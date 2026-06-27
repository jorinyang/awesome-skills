# lark-cli v2 操作模式速查

> 本文件记录经过实战验证的 lark-cli v2 命令模式。lark-cli 版本持续更新，以实际测试为准。

## fly 文档创建（一步法）

```bash
cd /tmp  # 必须在文件所在目录执行
cat > doc.md << 'EOF'
# 文档标题

正文内容...
EOF

lark-cli docs +create --api-version v2 --doc-format markdown \
  --content @doc.md --parent-token <wiki_node_token> --as bot
```

**关键约束**：
- `@file` 必须是**相对路径**，传绝对路径（如 `@/tmp/doc.md`）会报 `unsafe file path`
- `--title` 标志已废弃，标题从 markdown 第一个 `# heading` 自动提取
- `--as bot` 创建后会自动授权当前 CLI user `full_access`
- 创建后验证：`lark-cli docs +fetch --api-version v2 --doc <doc_id> --as bot`，确认 `revision_id > 1`

## 文档追加写入

```bash
lark-cli docs +update --api-version v2 --doc <doc_id> \
  --command append --doc-format markdown --content '追加内容...' --as bot
```

**陷阱**：
- `--mode append` 已废弃，必须用 `--command append`
- append 可能返回 `ok: true` 但 `result: failed`（block ID transform 失败），需检查 `result` 字段
- 追加内容中的 markdown 标题（`#`）和表格（`| |`）在飞书渲染中可能格式异常，复杂追加建议用 overwrite 全量替换

## 文档覆盖写入

```bash
cd /tmp
lark-cli docs +update --api-version v2 --doc <doc_id> \
  --command overwrite --doc-format markdown --content @file.md --as bot
```

**陷阱**：overwrite 会清除所有 block（含之前插入的图片）。overwrite 后需重新 `docs +media-insert` 插入图片。

## Wiki 节点创建

```bash
lark-cli wiki +node-create --parent-node-token <token> --title "节点名" --as bot
```

- `--as user` 需要 `wiki:node:create` + `wiki:space:read` scope，首次使用可能缺权限
- `--as bot` 通常可直接创建，并自动授权 user

## Wiki 节点删除

```bash
lark-cli wiki +node-delete --node-token <node_token> --obj-type wiki --as bot --yes
```

- **关键**：`--obj-type wiki` 不是 `docx`。用 `docx` 会 131005 not found
- 删除是异步的，CLI 自动轮询直到完成
- 批量删除需逐个执行，同批次并发可能超时

## Wiki 节点列表

```bash
lark-cli wiki +node-list --space-id <space_id> --parent-node-token <token> --as user --format json
```

**陷阱**：CLI 输出前有 "Found N node(s)" 前缀行，导致 `python3 -c "json.load(sys.stdin)"` 解析失败。
**解决**：用 `--format json | grep` 过滤而非直接 pipe 到 python json parser，或 `tail -n +2` 跳首行。

## 身份选择

| 操作 | 推荐身份 | 原因 |
|------|---------|------|
| docs +create | `--as bot` | 自动授权 user full_access |
| docs +fetch | `--as bot` | 稳定 |
| wiki +node-create | `--as bot` | user 可能缺 scope |
| wiki +node-delete | `--as bot` | 同上 |
| wiki +node-list | `--as user` | bot 需要额外 space_id 参数 |
