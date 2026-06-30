---
name: feishu-wiki-file-routing
description: 飞书知识库 /wiki/ URL 路由降级——当 lark-doc 无法处理 file 类型节点时的发现→下载→提取流程。与 lark-doc/lark-wiki/lark-drive 协同工作。
---

# Feishu Wiki File 路由降级

## 触发条件

当 `lark-cli docs +fetch --api-version v2 --doc <wiki_token>` 返回：
```
"Unsupported document type 'file'. Only docx is supported"
```
或 `lark-cli wiki +node-get` 返回 `"not found: document not found"` 时，说明 wiki 节点是 file 类型（PDF、图片等），需要降级处理。

## 三步降级流程

### 1. 发现真实类型

```bash
lark-cli wiki spaces get_node --params '{"token":"<wiki_token>"}' --as user --format json
```

关键字段：
- `data.node.obj_type` → 实际类型（file / docx / sheet / bitable / slides / mindnote）
- `data.node.obj_token` → 底层对象 token（用于 drive 下载）
- `data.node.title` → 文件名（用于确定输出文件名）

### 2. 按类型路由

| obj_type | 下一步命令 |
|----------|-----------|
| `file` | `lark-cli drive +download --file-token <obj_token> --output ./filename` |
| `docx` | 回到 `lark-cli docs +fetch --api-version v2 --doc <obj_token>` |
| `sheet` | 切到 `lark-sheets` |
| `bitable` | 切到 `lark-base` |

> 首次使用 `wiki spaces get_node` 可能需要授权 scope `wiki:node:retrieve`。使用 `lark-cli auth login --scope "wiki:node:retrieve" --no-wait --json` + QR 码授权。

### 3. 本地提取

| 文件类型 | 提取工具 | 命令示例 |
|----------|---------|---------|
| PDF（文字型） | `pymupdf` | `python3 -c "import pymupdf; doc=pymupdf.open('file.pdf'); print(...)"` |
| PDF（扫描型） | `marker-pdf` | `marker_single file.pdf --output_dir ./out` |
| 图片 | vision 工具 | `mcp_minimax_mcp_understand_image` |

## lark-cli 路径限制

- `--output` 参数只接受相对路径（当前目录下），不接受绝对路径或 `/tmp/` 等
- `lark-cli auth login` 不支持 `--as user` 参数（该 flag 不存在于 auth 子命令）

## 已知案例

- `https://acn3kz7weyc0.feishu.cn/wiki/T0niwkAxVitLWmkd9oGc7u7Gnyd` → "Agentic AI工程师路线图2026.pdf" → obj_type=file → 15页 PDF，pymupdf 提取成功

## Auth Scope 聚合：跨域提前声明

Wiki 任务常涉及 wiki + drive + doc 多域操作。每次缺 scope 触发一次 `auth login` 会造成多轮中断。最佳实践：**在开始任务前预判所需域，一次性申请所有 scope**。

常见组合：
```
wiki:node:retrieve wiki:node:create wiki:space:read drive:file:upload drive:drive.metadata:readonly
```

命令：
```bash
lark-cli auth login --scope "wiki:node:retrieve wiki:node:create wiki:space:read drive:file:upload drive:drive.metadata:readonly" --no-wait --json
```

> 注意事项：`lark-cli auth login` 不支持 `--as user` 参数（不存在此 flag）；scope 增量累积，分批授权也可行但效率低。

## Wiki 根目录上传

当需要向知识库根目录上传文件（与已有文件同级）时：

1. 先用 `wiki spaces get_node` 获取任意已有节点的 `space_id`
2. 创建一个临时节点获取根节点 token：
   ```bash
   lark-cli wiki +node-create --space-id <space_id> --title "临时节点" --as user --format json
   ```
3. 从返回中读取 `parent_node_token`（即根节点 token）
4. 使用根节点 token 上传：
   ```bash
   lark-cli drive +upload --file ./file.png --wiki-token <root_node_token> --name "文件名.png" --as user
   ```
5. 上传完成后可删除临时节点

## 陷阱速查

### `+node-delete` 的 `--obj-type` 陷阱

删除用 `+node-create` 创建的节点时，**必须传 `--obj-type wiki`**（不是 `docx`），即使节点包裹的是 docx 对象。

`--obj-type` 告诉 CLI **如何解析 token**（node_token vs obj_token），不是节点包裹的底层对象类型。

```bash
# ❌ 错误 — 用 docx 会触发 get_node 查 obj_token → 131005 "document not found"
lark-cli wiki +node-delete --node-token WW7Ew... --obj-type docx --as user --yes

# ✅ 正确 — wiki 表示 "token 是 node_token"
lark-cli wiki +node-delete --space-id <space_id> --node-token WW7Ew... --obj-type wiki --as user --yes
```

含 `--space-id` 可以跳过内部 `get_node` 解析步骤，避免额外的 scope 需求。

### `docs +fetch` 报 3380002 时不要切 `+node-get --obj-type docx`

`wiki +node-get --node-token <token> --obj-type docx` 会尝试按 docx obj_token 查找，file 类型节点会返回 131005 "document not found"。正确的流程是直接用 `wiki spaces get_node`（不需 `--obj-type`）获取 `obj_type` 和 `obj_token`。

### `lark-cli auth login` 没有 `--as` 参数

`lark-cli auth login` 不支持 `--as user/bot` flag。直接用 `lark-cli auth login --scope "..."` 即可。

> 未知根节点 token 时，`wiki +node-create` 返回的 `parent_node_token` 即为所在层级的父节点 token。
