# Windows 上 Markdown 转 PDF 的可靠方案

> 在生产环境中验证的降级链。当 answer Phase 6 Build 需要产出 PDF 格式交付物时使用。

## 首选方案：Chrome Headless `--print-to-pdf`

**适用**：Windows 上有 Chrome/Edge 浏览器即可，零额外依赖。

```bash
# 1. 先将 Markdown 转为 HTML（Python，内联 CSS）
python3 -c "
import markdown
with open('input.md','r',encoding='utf-8') as f:
    body = markdown.markdown(f.read(), extensions=['tables','fenced_code'])
css = '@page{size:A4;margin:1.8cm 2cm}body{font-family:\"Microsoft YaHei\",\"SimSun\",sans-serif;font-size:10.5pt;line-height:1.75;color:#333}h1{font-size:20pt;text-align:center;margin-top:2.5cm;color:#2c3e50}h2{font-size:15pt;border-bottom:2px solid #e67e22;padding-bottom:3px;margin-top:1.2cm}h3{font-size:12pt;color:#c0392b;margin-top:0.8cm}table{border-collapse:collapse;width:100%;margin:0.8em 0;font-size:8.5pt}th{background:#2c3e50;color:white;padding:5px 8px}td{border:1px solid #ccc;padding:4px 8px}tr:nth-child(even){background:#f9f9f9}blockquote{border-left:3px solid #e67e22;padding:5px 12px;background:#fef9f4;margin:0.8em 0}code{background:#f4f4f4;padding:1px 4px;font-size:8.5pt}'
html = '<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><style>'+css+'</style></head><body>'+body+'</body></html>'
with open('output.html','w',encoding='utf-8') as f: f.write(html)
"

# 2. Chrome headless 转 PDF
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless --disable-gpu \
  --print-to-pdf="/c/path/to/output.pdf" \
  --no-margins \
  "file:///c:/path/to/output.html"
```

**关键参数**：
- `--headless` + `--disable-gpu`：无界面模式
- `--print-to-pdf=<路径>`：直接输出 PDF，不走打印对话框
- `--no-margins`：PDF 自身 margin 由 @page CSS 控制，不需要浏览器默认边距
- `file:///` URL 必须使用**正斜杠**且**完整绝对路径**

**CSS 要点**：
- `@page { size: A4; margin: 1.8cm 2cm }` — 页边距由此控制
- `font-family: "Microsoft YaHei", "SimSun", sans-serif` — Windows 中文 fallback 链
- 表格字号 `font-size: 8.5pt` — 中文表格在 A4 上最佳阅读字号
- `page-break-after: avoid` 放 h2/h3 上防止标题孤悬页底

## 失败方案记录（不要重复尝试）

| 方案 | 失败原因 |
|------|---------|
| `weasyprint` | 依赖 GTK/Pango 系统库（`libgobject-2.0-0`），Windows 下不可用 |
| `xhtml2pdf` | pip 安装到 venv 后有权限问题（`.pyd` 文件被锁） |
| `pandoc --pdf-engine` | 需要额外安装 LaTeX 发行版或 wkhtmltopdf |

## 替代方案：Edge 浏览器

如果 Chrome 不可用，Windows 10/11 自带 Edge：

```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --headless --disable-gpu \
  --print-to-pdf="/c/path/to/output.pdf" \
  "file:///c:/path/to/output.html"
```

Edge 和 Chrome 在此场景下行为完全一致（共享 Chromium 渲染引擎）。
