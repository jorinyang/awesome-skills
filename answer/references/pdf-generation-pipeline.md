# PDF 生成管线：Markdown → 高质量 PDF

> 适用场景：answer Phase 6 Build 产出需要导出 PDF 交付客户时使用。

## 推荐管线（按可靠性排序）

### 管线 A：Markdown → HTML → Playwright/Chromium PDF ✅ 最推荐

```
.md → python-markdown 转 HTML → Playwright headless Chromium → PDF
```

**优点**：表格对齐完美、中文渲染正确、CSS可控性强、支持A3横版等定制纸张

**依赖**：
- `pip install markdown`
- `npm install playwright`
- Chromium 二进制（需预先下载：`npx playwright install chromium`）

**关键代码**：
```python
import markdown

with open('doc.md') as f:
    body = markdown.markdown(f.read(), extensions=['tables', 'fenced_code'])

html = f'<html><head><meta charset="UTF-8"><style>...</style></head><body>{body}</body></html>'

# 写入临时 HTML → 用 Playwright 渲染
```

```javascript
const { chromium } = require('playwright');
const browser = await chromium.launch({
    headless: true,
    executablePath: 'C:/Users/.../chrome.exe'  // 手动指定路径
});
const page = await browser.newPage();
await page.goto('file:///path/to/doc.html');
await page.pdf({ path: 'output.pdf', format: 'A4', printBackground: true });
```

**踩坑**：
- Chromium 路径可能不在默认位置。用 `find ~/AppData/Local/ms-playwright -name "chrome.exe"` 查找
- A3 横版表格用 `format: 'A3', landscape: true`
- 中文字体：CSS 指定 `"Microsoft YaHei", "PingFang SC", "SimSun"`

### 管线 B：Python fpdf2 直接生成 ⚠️ 仅简单文档

**缺点**：表格对齐差、不支持复杂CSS、中文字体需手动注册

**不推荐**用于含大量表格的文档（如 PRD、功能对比清单）。仅适用于纯文本为主、表格简单的文档。

### 管线 C：WeasyPrint ⚠️ Windows 需 GTK

Windows 环境下几乎不可用（需安装 GTK3 运行库）。Linux 服务器环境推荐。

### 管线 D：Word COM 自动化 ❌ 不可靠

依赖 Microsoft Word 已安装且 COM 注册正常。服务账户/容器环境不可用。

## 不可用的方案

| 方案 | 原因 |
|------|------|
| wkhtmltopdf + pdfkit | wkhtmltopdf 未预装，安装耗时 |
| LibreOffice CLI | 未预装 |
| pandoc PDF | 未预装 |
