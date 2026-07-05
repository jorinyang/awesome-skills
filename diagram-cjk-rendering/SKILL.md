---
name: diagram-cjk-rendering
description: CJK 字体渲染兜底——cairosvg 产生「口」字时的检测→修复→验证流程。与 fireworks-tech-graph 协同工作。
---

# 中文 SVG 图表字体渲染

## 触发

当 fireworks-tech-graph 生成的 SVG 含中文，通过 cairosvg 导出 PNG 后出现「口」字（tofu box）时触发本流程。

## 检测

```bash
fc-list :lang=zh | head -5
```

Linux/WSL 可用字体：`Noto Sans SC` (首选)、`WenQuanYi Zen Hei`、`Microsoft YaHei`。

## SVG 字体修正

SVG `<style>` 中 font-family 第一候选必须是系统实际存在的字体：

```css
font-family: "Noto Sans SC", "WenQuanYi Zen Hei", "Microsoft YaHei", sans-serif;
```

**不要**使用 design-language.yaml 的默认 `PingFang SC`（仅 macOS 存在）。

## PNG 渲染

### 方式一：cairosvg（改字体后重试）

```bash
python3 -c "import cairosvg; cairosvg.svg2png(url='in.svg', write_to='out.png', scale=2, dpi=144)"
```

### 方式二：Playwright（cairosvg 持续「口」字时）

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox','--disable-gpu'])
    page = browser.new_page(viewport={"width":2400,"height":1600}, device_scale_factor=2)
    page.goto(f"file://{svg_path}")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=png_path, full_page=True)
    browser.close()
```

首次使用：`python3 -m playwright install chromium`

## 验证

用 vision 工具抽查 PNG：`请检查所有中文是否正常显示，有无方块或乱码。`

## 结构对齐

生成图表前，必须从知识源提取实际章节/步骤编号和名称作为节点骨架，禁止套用通用模板或自行编造层次名称。
