# Wiki API 认证 Scope 与 Token 陷阱

本参考记录飞书 Wiki API 操作中常见的认证 scope 区别和 token 使用陷阱。

## Scope 区别

飞书 Wiki API 存在两个容易混淆的 scope：

| Scope | 覆盖范围 | 典型命令 |
|-------|---------|---------|
| `wiki:node:read` | 仅 `wiki spaces get_node` API | `lark-cli wiki spaces get_node --params '{"token":"..."}'` |
| `wiki:node:retrieve` | Shortcut 命令 | `+node-get`、`+node-list`、`+node-create` 等 |
| `wiki:member:retrieve` | 成员管理 shortcut | `+member-list`、`+member-add`、`+member-remove` |

**关键教训**：
- `wiki:node:read` 授权后 `spaces get_node` 可用，但 `+node-get` / `+node-list` 仍会报 `missing scope: wiki:node:retrieve`
- 需要 Wiki 节点操作时建议直接用 `--scope "wiki:node:retrieve"` 一步到位
- 需要成员管理时额外补 `wiki:member:retrieve`

## Token 截断陷阱

Hermes 内存的字符限制可能导致存储的 token 被截断。

**实例**：
- 记忆中存储：`Y4LYd1X8Yo`（截断）
- 实际完整 token：`Y4LYd1X8Yo1Du9x9WtNcYD51nte`

截断 token 调用 API 返回 `131005 not found`，容易误导为权限问题。

**正确做法**：不盲目信任记忆中的 token。先用 `wiki +node-list --space-id <space_id>` 获取节点列表，从中提取真实完整的 `obj_token` 和 `node_token`。

## `+node-get` 的 `--obj-type` 要求

当向 `+node-get` 传入原始 `obj_token`（非 wiki `node_token`）时，必须同时传 `--obj-type`：

```
--obj-type 可选值：doc | docx | sheet | bitable | mindnote | slides | file
```

否则传入带类型的飞书 URL（如 `/docx/<token>`）让 CLI 自动推断。

**推荐流程**：先用 `wiki +node-list` 获取 `node_token` 和 `obj_type`，再用 `+node-get --node-token <node_token>`。
