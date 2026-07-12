# 静态图片导出（海报/Banner/高清图）

## 交付物判断

当用户明确要"图片/海报/高清图/下载"而非"链接/页面/在线看"时，**不要走 OSS 部署流程**。直接用 Playwright 截图输出 PNG。

| 用户说法 | 正确交付 | 错误做法 |
|---------|---------|---------|
| "看看效果" / "做个页面" | OSS HTML 链接 | 直接给 PNG |
| "生成图片" / "下载" / "高清图" / "海报" | PNG 文件（MEDIA: 路径） | 部署 OSS 链接 |

## Playwright 高清截图流程

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # 海报类：手机比例 375×667 → 3x 高清 = 1125×2001
    page = browser.new_page(viewport={'width': 1125, 'height': 2001})

    # 本地 HTML 用 file:// 协议
    page.goto('file:///path/to/poster.html', timeout=15000)
    page.wait_for_timeout(1000)  # 等渲染完成

    # 精确截取目标元素
    el = page.query_selector('#poster')
    el.screenshot(path='/output/poster.png')

    browser.close()
```

## 分辨率建议

| 用途 | 基准尺寸 | 3x 高清 |
|------|---------|--------|
| 手机海报 | 375×667 | 1125×2001 |
| 方形海报 | 375×375 | 1125×1125 |
| 横版 Banner | 750×375 | 2250×1125 |
| 桌面壁纸 | 1280×720 | 2560×1440 |

## 验证

截图后用 `mcp_minimax_mcp_understand_image` 检查渲染是否完整（Logo/文字/标签有无裁切错位）。批量生成时抽检 2 张即可——不必全部检查。

## 设计参考

海报布局、配色、字体策略见 `claude-design` 技能的 `references/chinese-promo-poster-patterns.md`——**生成海报前必读**。核心原则：优先使用实景照片做背景（全幅铺满），文字用描边+投影直接压在照片上，而非毛玻璃卡片。纯渐变/抽象背景仅作为无照片时的降级方案。

## 陷阱

- **不要用 OSS 部署作为中间步骤再截图** — 用户要的是图片文件，不是网页
- **`file://` 协议的 CSS `background-image` 必须用绝对路径** — Playwright 打开 `file:///path/to/poster.html` 时，CSS 中的 `background: url('bg/01.jpg')` 相对路径不会正确解析。使用 `url('file:///home/user/.../bg/01.jpg')` 绝对路径。
- **`device_scale_factor=1` 配合大 viewport** — 用 viewport 控制分辨率，不用 scale_factor 放大（后者会导致部分 CSS 渲染异常）
- **必须用 `element.screenshot()` 而非 `page.screenshot()`** — 页面截图可能包含 body 背景色边距
- **Playwright 截图优先用 Python 路径** — `python3 -c "from playwright.sync_api import ..."` 而非 Node.js `require('playwright')`。后者可能因 npm global module 路径问题报 `MODULE_NOT_FOUND`。
- **B2B 海报避免全图叠加文字** — 当照片主体（人物）靠近画面下部时，信息区不要叠在照片上。改用上下分区：上部照片 + 底部纯色背景承载所有信息。统计栏放在图片下方而非上方，避免遮挡人物。用 `understand_image` 逐版评审迭代。
