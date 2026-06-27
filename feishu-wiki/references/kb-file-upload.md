# KB 文件上传：外部文件入库

当用户要把 PDF/图片/Word 等文件保存到知识库（space_id=7643710721485753535）时，`drive +upload --wiki-token` 不适用（它要求 wiki node token，非 space_id）。正确流程为两步走。

## 完整流程

```bash
# Step 1：上传到 Drive 根目录（--file 必须是相对路径！）
cp /path/to/external-file.pdf .  # 或 cd 到文件所在目录
lark-cli drive +upload --file ./external-file.pdf --as bot
# → 拿到 file_token（如 ESqbbK9uwof8QixGfGmcaXetnBQ）

# Step 2：从 Drive 迁入 KB 根目录（--target-parent-token 不传 = 根目录）
lark-cli wiki +move \
  --obj-type file \
  --obj-token <file_token> \
  --target-space-id 7643710721485753535 \
  --as bot
# → 成功返回 node_token / wiki_token
```

## 关键陷阱

### `drive +upload --file` 必须是相对路径

绝对路径（如 `/tmp/file.pdf`）会被拒绝：
```
unsafe file path: --file must be a relative path within the current directory
```

**修复**：`cd` 到文件目录再执行，或 `cp` 到当前工作目录。

### obj_type 映射

| 文件类型 | `--obj-type` |
|---------|-------------|
| PDF | `file` |
| Word/docx | `docx` |
| Excel | `sheet` |
| 图片 | `file` |
| PPT | `slides` |

### 目标位置控制

| 需求 | 参数 |
|------|------|
| KB 根目录 | 不传 `--target-parent-token` |
| 指定父节点下 | `--target-parent-token <node_token>` |
