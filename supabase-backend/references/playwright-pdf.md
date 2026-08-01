# Playwright HTML-to-PDF 生成

## 使用场景

当需要将 Markdown 文档转换为排版精良的 PDF 时，fpdf2/WeasyPrint 等 Python 库在处理中文、复杂表格时效果不佳（表格不对齐、CJK 字体缺失）。Playwright（headless Chromium）是最可靠的替代方案。

## 前提

- Playwright 已安装：`npm install playwright`
- Chromium 二进制已存在（路径见下方）

## 工作流

### 1. Markdown → HTML

```python
import markdown

with open('source.md', 'r', encoding='utf-8') as f:
    md = f.read()

body = markdown.markdown(md, extensions=['tables', 'fenced_code'])
```

### 2. 包装为完整 HTML

CSS 必须在 `<style>` 中完整定义，包括 `@page` 尺寸和表格样式。关键：**表格必须用 `border-collapse: collapse` + 明确 `border` 定义**，否则 PDF 中表格无边框。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
@page { size: A4; margin: 2cm 2.2cm; }
body { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; font-size: 10.5pt; line-height: 1.7; }
table { border-collapse: collapse; width: 100%; font-size: 8.5pt; }
th { background: #e9ecef; border: 1px solid #adb5bd; padding: 5px 7px; }
td { border: 1px solid #ced4da; padding: 4px 7px; }
pre { background: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; font-size: 8pt; }
blockquote { border-left: 3px solid #c41e3a; margin: 8px 0; padding: 4px 12px; color: #666; }
</style>
</head>
<body>{body}</body>
</html>
```

### 3. Playwright 渲染 PDF

```javascript
const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch({
        headless: true,
        // 🔴 Windows 上必须显式指定 chromium 路径
        executablePath: 'C:/Users/Aorus/AppData/Local/ms-playwright/chromium-1223/chrome-win64/chrome.exe'
    });
    const page = await browser.newPage();
    await page.goto('file:///C:/path/to/output.html', { waitUntil: 'networkidle', timeout: 15000 });
    await page.pdf({
        path: 'output.pdf',
        format: 'A4',
        margin: { top: '20mm', bottom: '20mm', left: '22mm', right: '22mm' },
        printBackground: true
    });
    await browser.close();
})();
```

## 常见问题

| 问题 | 原因 | 修复 |
|------|------|------|
| 表格无边框 | CSS 中 border 未定义在 `th`/`td` 上 | 显式定义 `th, td { border: 1px solid #xxx; }` |
| 中文变方框 | 字体不可用 | 用 `"Microsoft YaHei", "PingFang SC", "SimSun", sans-serif` 字体栈 |
| `Executable doesn't exist` | Playwright 找错了 chromium 路径 | 显式设置 `executablePath` |
| 中文字符重叠 | `line-height` 不足 | 设 `line-height: 1.7` |
| 代码块溢出 | `pre` 宽度超出页面 | 设 `overflow-x: auto` + `font-size: 8pt` |

## fpdf2 vs Playwright

| 维度 | fpdf2 | Playwright (Chromium) |
|------|-------|----------------------|
| 表格对齐 | ⚠️ 需手动计算列宽，复杂表格错位 | ✅ 浏览器原生渲染，完美对齐 |
| CJK 字体 | ⚠️ 需手动注册字体文件 | ✅ 系统字体自动可用 |
| CSS 样式 | ❌ 有限支持 | ✅ 完整 CSS 支持 |
| 文件大小 | 小 (~100KB) | 中 (~400KB) |
| 依赖 | 纯 Python | Node.js + Chromium (~300MB) |
| 适用场景 | 简单文档 | **中文、表格密集型文档** |
