---
name: html-ppt
description: HTML PPT Studio — 用 36 套主题 × 31 种布局 × 47 个动效 × 15 套完整模板快速生成 HTML 演示文稿。纯静态 HTML/CSS/JS，键盘操控，零构建。触发词：PPT、幻灯片、演示、deck、slides、演讲、分享稿、pitch、小红书图文、keynote、reveal、slideshow、演讲稿、做一份 PPT、做一份 slides。
---

# html-ppt · HTML PPT Studio

基于 [lewislulu/html-ppt-skill](https://github.com/lewislulu/html-ppt-skill)（MIT License）的 Hermes 适配版。

## 定位：与现有技能的冲突矩阵

html-ppt 是一个**纯静态 HTML 演示文稿工厂**，与以下 Hermes 技能互补，互不冲突：

| 维度 | html-ppt | powerpoint | huashu-design | feishu-html |
|------|:--------:|:---------:|:-----------:|:---------:|
| **输出格式** | HTML 幻灯片 | .pptx 文件 | HTML 任意形式 | HTML SPA 页面 |
| **预置主题** | ✅ 36 套 | ⚠️ 色板建议 | ❌ 从头设计 | ❌ 从头设计 |
| **布局模板** | ✅ 31 种 | ❌ 手工布局 | ❌ React 组件 | ❌ TAB 结构 |
| **动画系统** | ✅ 27 CSS + 21 FX | ❌ 有限 | ✅ 时间轴驱动 | ⚠️ 轻量 |
| **演讲者模式** | ✅ 磁吸卡片+S键 | ❌ | ❌ | ❌ |
| **部署** | 本地 HTML | 本地文件 | OSS 部署 | OSS 部署 |
| **设计哲学** | Token 驱动, 设计师默认值 | 无 | 设计方法论驱动 | 内容驱动 |
| **适用场景** | 快速出片/标准演示 | Office 生态/正式汇报 | 品牌定制/高保真原型 | 内容 SPA/方案展示 |

**使用决策树**：
- 用户要 `.pptx` 文件 → `powerpoint` 技能
- 用户要自定义品牌视觉的高保真原型/动画 → `huashu-design` 技能
- 用户要对客展示的 WEB SPA/方案页 → `feishu-html` 技能
- 用户要快速做一份好看的 HTML 演示文稿（有现成主题/布局可选）→ **`html-ppt` 技能**

## 何时使用

用户提到以下任一关键词时触发：PPT、幻灯片、演示、deck、slides、演讲、分享稿、pitch deck、小红书图文、keynote、reveal、slideshow、演讲稿、技术分享、产品发布、周报。

**特别触发**：用户提到要**演讲/分享/逐字稿/提词器**，或说"我要去给团队讲xxx" → 使用 `presenter-mode-reveal` 模板。

## 核心资产

| 资产 | 数量 | 位置 |
|------|:---:|------|
| 🎨 主题 | **36** | `assets/themes/*.css` |
| 📑 完整 deck 模板 | **15** | `templates/full-decks/<name>/` |
| 🧩 单页布局 | **31** | `templates/single-page/*.html` |
| ✨ CSS 动画 | **27** | `assets/animations/animations.css` |
| 💥 Canvas FX | **21** | `assets/animations/fx/*.js` |
| 🎤 演讲者模式 | S 键 | `runtime.js` 内置 |

## 默认工作流

### 启动前：三问（不先问清楚不开工）

1. **内容和受众**：讲什么？多少页？听众是谁（工程师/高管/消费者/VC）？
2. **风格/主题**：从 36 个主题推荐 2-3 个，根据调性：
   - 商业/投资人 → `pitch-deck-vc`、`corporate-clean`、`swiss-grid`
   - 技术分享 → `tokyo-night`、`dracula`、`catppuccin-mocha`、`terminal-green`、`blueprint`
   - 小红书图文 → `xiaohongshu-white`、`soft-pastel`、`rainbow-gradient`、`magazine-bold`
   - 学术/报告 → `academic-paper`、`editorial-serif`、`minimal-white`
   - 前沿/赛博/发布 → `cyberpunk-neon`、`vaporwave`、`y2k-chrome`、`neo-brutalism`
3. **起点**：用哪个完整模板打底？提供最接近的 `templates/full-decks/<name>/`。

**严禁直接问三个空泛问题**。基于用户已有内容给出明确推荐：

> 我可以做这份 PPT。三件事确认：
> 1. 内容/页数/听众？
> 2. 风格？我推荐 `tokyo-night`（技术分享）、`xiaohongshu-white`（小红书风）、`corporate-clean`（正式汇报）
> 3. 要不要用现成的 `tech-sharing` 模板打底？

### 执行步骤

1. **脚手架**：复制 `templates/deck.html` 或最近的 full-deck 模板
2. **选主题**：`<link id="theme-link" href="[skill_dir]/assets/themes/NAME.css">`
3. **选布局**：从 `templates/single-page/` 复制 `<section class="slide">` 块，替换示例数据
4. **加动效**：`data-anim="fade-up"` / `data-fx="confetti-cannon"`，每页最多一个重点动效
5. **加备注**：每张 slide 加 `<div class="notes">…</div>`（S 键可查看）
6. **验证**：浏览器打开 → ← → 翻页 → O 概览 → T 切主题 → S 演讲者模式

## 关键规则

- **永远从模板开始**，不要手写空 slide
- **用 CSS 变量，不用裸色值**：`color: var(--text-1)` ✅，`color: #111` ❌
- **不新建布局文件**，优先组合现有 31 种

### ⚠️ 缺失 assets 时的回退

如果技能目录下仅有 `SKILL.md` 而没有 `assets/`、`templates/`、`runtime.js` 等文件（例如通过 `skill_manage` 创建但未同步上游仓库），**不要报错终止**。回退方案：

1. 手写一个完整的内联 HTML 文件，包含所有 CSS/JS
2. 使用简化 slide 架构：`position:absolute` 叠加 + `display:none/active` 切换
3. 键盘翻页用原生 `keydown` 事件监听（← → Space Home End）
4. 移动端触控用 `touchstart/touchend` 检测 swipe
5. 配色用内联 CSS 变量（`var(--c-*) `），从推荐主题中人工移植 3-5 个核心色
6. 部署仍走 `feishu-html` 的 OSS 流程

此回退方案的交付质量（15 页 PPT，Playwright 全验证通过，0 控制台错误）已验证可行。但首次使用仍需尝试 `find ~/.hermes/skills/html-ppt/ -name 'deck.html'` 确认文件是否存在，不存在再回退。
- **每张 slide 必须带 notes**：`<div class="notes">…</div>`
- **禁止把演讲者备注放在 slide 可见区域**：描述性文字（"这一页的重点是…"）必须进 `.notes`
- **保留 chrome 插槽**：`.deck-header`、`.deck-footer`、`.slide-number` 由 runtime 自动管理
- **键盘优先**：必须引入 `runtime.js`

## 主题速查

36 主题分 6 组，全部 token 定义见 `references/themes.md`：

| 分组 | 主题 |
|------|------|
| Light & calm | `minimal-white` `editorial-serif` `soft-pastel` `xiaohongshu-white` `solarized-light` `catppuccin-latte` |
| Bold & statement | `sharp-mono` `neo-brutalism` `bauhaus` `swiss-grid` `memphis-pop` |
| Cool & dark | `catppuccin-mocha` `dracula` `tokyo-night` `nord` `gruvbox-dark` `rose-pine` `arctic-cool` |
| Warm & vibrant | `sunset-warm` |
| Effect-heavy | `glassmorphism` `aurora` `rainbow-gradient` `blueprint` `terminal-green` |
| v2 additions | `corporate-clean` `pitch-deck-vc` `academic-paper` `japanese-minimal` `engineering-whiteprint` `magazine-bold` `news-broadcast` `midcentury` `retro-tv` `cyberpunk-neon` `vaporwave` `y2k-chrome` |

## 布局速查

31 种布局，全部见 `references/layouts.md`：

| 场景 | 布局 |
|------|------|
| 开场 | `cover` `toc` `section-divider` |
| 正文 | `bullets` `two-column` `three-column` `big-quote` |
| 数据 | `stat-highlight` `kpi-grid` `table` `chart-bar` `chart-line` `chart-pie` `chart-radar` |
| 代码 | `code` `diff` `terminal` |
| 图表 | `flow-diagram` `arch-diagram` `process-steps` `mindmap` |
| 计划 | `timeline` `roadmap` `gantt` `comparison` `pros-cons` `todo-checklist` |
| 视觉 | `image-hero` `image-grid` |
| 结尾 | `cta` `thanks` |

## 完整 Deck 模板速查

15 套，全部见 `references/full-decks.md`：

**提炼款**（8 个，从真实作品提取视觉语言）：
- `xhs-white-editorial` — 小红书白底杂志风
- `graphify-dark-graph` — 暗底+力导向知识图谱
- `knowledge-arch-blueprint` — 奶油蓝图架构
- `hermes-cyber-terminal` — 暗终端 honest-review
- `obsidian-claude-gradient` — GitHub 暗紫渐变
- `testing-safety-alert` — 红琥珀警示
- `xhs-pastel-card` — 柔和马卡龙慢生活
- `dir-key-nav-minimal` — 方向键 8 色极简

**场景款**（7 个通用脚手架）：
- `pitch-deck` — 投资人路演
- `product-launch` — 产品发布会
- `tech-sharing` — 技术分享
- `weekly-report` — 周报
- `xhs-post` — 小红书图文（9 张 3:4）
- `course-module` — 教学模块
- **`presenter-mode-reveal`** 🎤 — 演讲模板，每页带 150-300 字逐字稿

## 演讲者模式（S 键）

按 S 键弹出演讲者窗口，4 个可拖拽/可缩放磁吸卡片：
- 🔵 **CURRENT** — 当前页像素级预览
- 🟣 **NEXT** — 下一页预览
- 🟠 **SPEAKER SCRIPT** — 大号逐字稿
- 🟢 **TIMER** — 计时器+翻页按钮

逐字稿 3 条铁律：
1. 不是讲稿，是提示信号 — 加粗关键词 + 过渡句独立成段
2. 每页 150–300 字 — 2–3 分钟/页节奏
3. 用口语 — "所以"不写"因此"，"这个"不写"该"

详细编写指南见 `references/presenter-mode.md`。

## PNG 导出（Hermes 适配版）

原版渲染脚本（`scripts/render.sh`）硬编码 macOS Chrome 路径。Hermes 环境用 **Playwright** 替代：

```python
from playwright.sync_api import sync_playwright

def render_slide(html_path, slide_num, output_path, width=1920, height=1080):
    """渲染单张 slide 为 PNG"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(f"file://{html_path}#/{slide_num}", wait_until="networkidle")
        page.screenshot(path=output_path, full_page=False)
        browser.close()
    return output_path
```

安装：`pip install playwright && playwright install chromium`

## 部署到 OSS（集成 feishu-html）

如需在线访问，调用 `feishu-html` 技能的 OSS 部署流程：
1. 将完整 deck 文件夹（含 index.html）上传至 `web-spa/{slug}/`
2. 访问地址：`https://gzzhike.cn/web-spa/{slug}/index.html`

## 键盘快捷键

```
← → Space PgUp PgDn Home End   翻页
F                               全屏
S                               打开演讲者窗口
N                               底部 notes 抽屉
R                               重置计时器（演讲者窗口内）
O                               slide 总览网格
T                               循环主题
A                               循环演示动画
#/N (URL)                       深链到第 N 页
?preview=N (URL)                预览模式（单页，无 chrome）
Esc                             关闭所有叠加层
```

## 设计理念

- **Token 驱动**：所有颜色/圆角/阴影/字体决策在 CSS 变量中，换一套变量 = 换皮
- **iframe 隔离预览**：主题/布局展示用独立 iframe 渲染，互不污染
- **零构建**：纯静态 HTML/CSS/JS，只走 CDN 加载字体和 chart.js
- **设计师默认值**：字号规律、间距节奏、渐变处理都有态度
- **中英双语一等公民**：预导入 Noto Sans SC / Noto Serif SC

## 文件结构

```
html-ppt/
├── SKILL.md                     # 本文件
├── references/                  # 详细目录（按需加载）
│   ├── themes.md                # 36 主题详解
│   ├── layouts.md               # 31 布局详解
│   ├── animations.md            # 动效目录
│   ├── full-decks.md            # 15 完整模板详解
│   ├── presenter-mode.md        # 演讲者模式+逐字稿指南
│   └── authoring-guide.md       # 完整工作流
├── assets/
│   ├── base.css                 # 共享 token + 基础组件
│   ├── fonts.css                # 字体引入
│   ├── runtime.js               # 键盘+演讲者+概览+主题循环
│   ├── themes/*.css             # 36 主题
│   └── animations/
│       ├── animations.css       # 27 CSS 动画
│       ├── fx-runtime.js        # Canvas FX 运行时
│       └── fx/*.js              # 21 Canvas FX 模块
├── templates/
│   ├── deck.html                # 最小起步模板
│   ├── theme-showcase.html      # iframe 隔离主题 tour
│   ├── layout-showcase.html     # 31 布局展示
│   ├── animation-showcase.html  # 动效展示
│   ├── full-decks-index.html    # 15 deck 画廊
│   ├── full-decks/<name>/       # 15 套完整 deck
│   └── single-page/*.html       # 31 布局文件
├── scripts/
│   ├── new-deck.sh              # 脚手架
│   └── render.sh                # PNG 导出（macOS；Hermes 用 Playwright）
└── examples/demo-deck/          # 完整示例
```

## 常见陷阱

### 模板文件缺失

html-ppt 技能通过 `skill_manage` 创建时，仅 SKILL.md 被同步。`assets/`、`templates/`、`scripts/` 目录不会自动附带。检测方法：`ls ~/.hermes/skills/html-ppt/templates/` 为空或不存在。

**回退方案**：手写内联 HTML PPT。结构如下：
- 单文件 HTML，所有 CSS/JS 内联
- 每页一个 `<div class="slide">`，通过 `display:none/block` 切换
- 键盘 ← → Space 翻页，Home/End 首尾
- 移动端 touch swipe
- 响应式：`@media (max-width:768px)` 单列布局

参考产出：profit-sharing-ppt（15页内部版）和 profit-sharing-ppt-lecturer（6页讲师精简版），均在 `gzzhike.cn/web-spa/` 下。

## 上游与许可

- 上游仓库：[lewislulu/html-ppt-skill](https://github.com/lewislulu/html-ppt-skill)
- 许可：MIT © 2026 lewis
- 版本：基于 main 分支快照，36 主题 / 31 布局 / 47 动效 / 15 完整模板
