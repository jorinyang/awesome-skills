# 本地 PDF 生成方案（非飞书交付）

当 answer 产出物需要以本地文件形式交给外部（非飞书 Wiki）时，使用此方案。

## 生成链路

```
Markdown 主文档
    ↓ markdown.markdown() + CSS
HTML（可选：嵌入 Mermaid CDN 渲染图表）
    ↓ Chrome headless --print-to-pdf --virtual-time-budget
PDF 最终交付物
```

## 适用场景

- 外部客户交付（非飞书生态内）
- 需要打印/签字的正式文档
- Markdown + PDF 双格式需求

## 技术细节

### Step 1: Markdown → HTML

```python
import markdown

with open('doc.md', 'r', encoding='utf-8') as f:
    html_body = markdown.markdown(f.read(), extensions=['tables', 'fenced_code'])

css = '@page{size:A4;margin:1.8cm 2cm}body{font-family:"Microsoft YaHei","Noto Sans SC","SimSun",sans-serif;font-size:10.5pt;line-height:1.75;...}'

# 如果需要 Mermaid 图表渲染：
mermaid_cdn = '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script><script>mermaid.initialize({startOnLoad:true});</script>'

html = f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><style>{css}</style></head><body>{html_body}{mermaid_cdn}</body></html>'
```

### Step 2: HTML → PDF (Chrome headless)

```bash
# 基础版本（无 JS 图表）
chrome --headless --disable-gpu --print-to-pdf="output.pdf" --no-margins "file:///path/to/doc.html"

# 含 Mermaid 图表（需要给 JS 执行时间）
chrome --headless --disable-gpu --print-to-pdf="output.pdf" --no-margins --virtual-time-budget=15000 "file:///path/to/doc.html"
```

**关键参数**：
- `--virtual-time-budget=15000`：模拟 15 秒时间流逝，给 CDN 脚本下载和 Mermaid 渲染足够时间。无此参数时 Mermaid 图表只会显示原始代码块。
- `--no-margins`：配合 CSS `@page{margin:...}` 使用，避免双重 margin。
- Chrome 路径在 Windows 上通常为 `C:\Program Files\Google\Chrome\Application\chrome.exe`（git-bash 中用 `/c/Program Files/Google/Chrome/Application/chrome.exe`）。

### Step 3: 验证

```bash
ls -la output.pdf  # 确认文件存在且大小合理（含图表时通常 1.5-2MB）
```

## 失败 fallback 链

按优先级尝试：

| # | 方案 | 依赖 | Windows 可靠性 |
|---|------|------|---------------|
| 1 | Chrome headless | Chrome 浏览器 | ★★★★★（几乎总是可用） |
| 2 | pandoc + wkhtmltopdf | pandoc, wkhtmltopdf | ★★（需预装，winget 在 bash 中不可用） |
| 3 | weasyprint | GTK/Pango 系统库 | ★（Windows 上几乎不可用） |
| 4 | xhtml2pdf | 纯 Python | ★★（有权限/编码坑） |

**首选永远是 Chrome headless。** 不需要额外安装，Windows 上 Chrome 几乎必定存在。

## 已知坑

- **Chrome 路径含空格**：git-bash 中路径必须加双引号，URL 部分用 `file:///` 协议。
- **中文文件名 URL 编码**：`file:///` 后的路径需要 URL-encode 中文字符（`%E6%80%9D%E5%A5%94` 等）。可用 Python 预生成：`urllib.parse.quote(path)`。
- **ERROR: WSALookupServiceBegin failed**：headless Chrome 在 Windows 上的正常日志，不影响 PDF 生成，可忽略。
- **Mermaid 不渲染**：检查是否加了 `--virtual-time-budget` 且数值足够（≥ 10000）。
- **PDF 中文字体**：CSS `font-family` 必须包含 Windows 可用字体（`Microsoft YaHei`, `SimSun`），不要只用 `Noto Sans SC`。
