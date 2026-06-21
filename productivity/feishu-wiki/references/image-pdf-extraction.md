# 图片型 PDF 内容提取 → 知识库入库工作流

当 PDF 是纯图片画册/宣传册（PyPDF2、pymupdf 只能提取 1-2 页文字的），使用本工作流。

## 触发场景

- 用户发来图片型 PDF（画册、宣传册、杂志扫描件）
- PyPDF2/pymupdf `get_text()` 只返回极少文字（如 54 页只 2 页有文字）
- 需要将 PDF 内容学习后入库到飞书 Wiki 知识库

## 步骤

### 1. 下载 PDF

飞书消息附件：用 `lark-cli im +threads-messages-list` 找到 file 类型消息，提取 `file_key`，然后用 `+messages-resources-download` 下载：

```bash
# 查找文件消息
lark-cli im +threads-messages-list --thread <thread_id> --as bot --json

# 下载（需提供 file_key 和 type）
lark-cli im +messages-resources-download \
  --message-id <msg_id> \
  --file-key <file_key> \
  --type file --as bot
```

### 2. 安装 pymupdf（如未安装）

```bash
pip3 install --break-system-packages pymupdf
```

### 3. 转换 PDF 页为图片（200 DPI）

```python
import pymupdf, os

doc = pymupdf.open('/tmp/input.pdf')
os.makedirs('/tmp/pages', exist_ok=True)

for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=200)
    pix.save(f'/tmp/pages/page_{i+1:02d}.png')
```

### 4. 批量 OCR 提取

用 `understand_image`（MiniMax vision）逐页提取。**策略**：
- 先读前几页了解结构（封面、目录）
- 目录页可一次性获得全部章节结构，用于后续跳页定位
- 跳过纯图片页（无文字），聚焦文字信息页
- 每批 3 页并行调用（vision 工具支持并发）

```python
# Prompt 模板
"提取所有中文文字，包括标题、正文、数据说明。按原文顺序。"
```

### 5. 编译入库

将提取内容整理为结构化 Markdown，用 `lark-cli docs +create` 创建飞书文档，再用 `wiki +node-create --node-type shortcut` 添加到知识库：

```bash
# 创建文档
lark-cli docs +create --api-version v2 --doc-format markdown \
  --content @guide.md --as bot

# 添加 Wiki 快捷方式（指向已有 doc_token）
lark-cli wiki +node-create \
  --parent-node-token <分类_node_token> \
  --node-type shortcut \
  --origin-node-token <doc_token> \
  --title "YYYY-MM-DD_来源_标题" --as bot
```

## 效率参考

| 规模 | 耗时 |
|------|------|
| 54 页画册 | ~15-20 次 vision 调用，专注文字页 |

## 已知陷阱

- **PyPDF2/pymupdf `get_text()` 对图片 PDF 无效**：通常只能提取 0-2 页文字。不要浪费时间重试。
- **`pdftoppm`/`pdftocairo` 可能未安装**：直接用 pymupdf 的 `get_pixmap()` 替代。
- **逐页全量 OCR 太慢**：利用目录页快速定位章节，只对文字信息页做 OCR。
- **bot 身份创建文档后权限**：bot 创建的文档可能需要手动授权给团队成员。
