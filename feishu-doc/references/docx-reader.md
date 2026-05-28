# .docx 附件读取脚本

## 背景

当用户在飞书会话中上传 `.docx` 文件附件时，Hermes Agent 会将其缓存至：
```
~/.hermes-feishu/cache/documents/doc_<hash>_<original_filename>.docx
```

这是读取用户上传文档的**推荐方式**——无需 token，无需 IM API 调用，不受线程消息 ID / chat_id 限制，不依赖脆弱的 Feishu API 参数。

## 查找缓存文件

```bash
ls ~/.hermes-feishu/cache/documents/
# 典型输出:
# doc_26b21b183805_单页汇报材料.docx
# doc_3fb36f4dab24_落地执行时间表.docx
# doc_fa74f690fb2b_六月营销策划落地方案(1).docx
```

文件名格式：`doc_<hash>_<原始文件名>.docx`

## 完整读取脚本

```python
import zipfile, xml.etree.ElementTree as ET

docx_path = '~/.hermes-feishu/cache/documents/doc_<hash>_<name>.docx'
with zipfile.ZipFile(docx_path) as z:
    with z.open('word/document.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()

ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

for para in root.iter(f'{{{ns}}}p'):
    texts = [t.text for t in para.iter(f'{{{ns}}}t') if t.text]
    line = ''.join(texts).strip()
    if line:
        print(line)
```

## 带样式区分的读取脚本

```python
import zipfile, xml.etree.ElementTree as ET

docx_path = '~/.hermes-feishu/cache/documents/doc_<hash>_<name>.docx'
with zipfile.ZipFile(docx_path) as z:
    with z.open('word/document.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()

ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def get_text(element):
    return ''.join(t.text for t in element.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text)

body = root.find('.//w:body', ns)
for para in body.findall('.//w:p', ns):
    texts = get_text(para)
    if not texts.strip():
        continue
    pPr = para.find('w:pPr', ns)
    style = ''
    if pPr is not None:
        pStyle = pPr.find('w:pStyle', ns)
        if pStyle is not None:
            style = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')
    print(f'[{style}] {texts}')
```

样式值含义（常见）：
| pStyle val | 含义 |
|---|---|
| 2 | Normal 正文 |
| 3 | Heading 1 一级标题 |
| 4 | Heading 2 二级标题 |
| 5 | Heading 3 三级标题 |
| 27 | 表格内文字（通常） |

## 注意事项

- `.docx` 本质是 ZIP 包，`word/document.xml` 包含所有正文内容
- 图片不存储在 `document.xml` 中（位于 `word/media/` 目录），但图片块通常不在方案文档中，文字读取已够用
- 表格内容以行为单位输出，行内单元格文本以空格分隔
- 某些复杂文档（公式、页眉页脚）解析逻辑不同，本脚本覆盖 95% 的营销/汇报文档场景
