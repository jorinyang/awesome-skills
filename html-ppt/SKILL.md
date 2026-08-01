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
2. 使用简化 slide 架构：`position:absolute` 叠加 + `opacity/visibility` 切换（**不要用 `display:none/block`** — 无法做 CSS transition 动画）
3. 用 `.stagger > *:nth-child(N)` 做元素依次入场动画（详见 references/inline-only-fallback-pattern.md）
4. 键盘翻页用原生 `keydown` 事件监听（← → Space Home End）
5. 移动端触控用 `touchstart/touchend` 检测 swipe
6. 配色用内联 CSS 变量（`var(--c-*) `），从推荐主题中人工移植 3-5 个核心色
7. 部署仍走 `feishu-html` 的 OSS 流程

**完整代码模板和组件库**：见 `references/inline-only-fallback-pattern.md`（已验证：47 页 / 147KB / 零依赖 / 全功能）。该参考文件还包含：
- 三区域点击导航（左/中/右 1/3，防止误触内容链接）
- 底部 20px 进度条 + 页码叠加变体
- SVG 架构图模式（深色背景三层结构，配箭头连线）
- 密集内容排版模式（教材级信息密度：完整句子、代码块、对比表格、callout）
- 讲师介绍页模式（封面后插入：左照片右文字，含认证/经验标签/行业背景）
- 教材→PPT重构方法论（1610行教材→47页幻灯片，内容不缩水）
- 浏览器验证清单（键盘/点击/全屏/Overview 逐项测试）
- **讲师照片 base64 内嵌方案**（解决 file:// 协议加载失败）
- **评分标准页 grid 对齐模式**（替代易错的多列 flex）
- **Apple 白底设计规范速查**（配色/圆角/字体/对比度）

此回退方案的交付质量（15-38 页 PPT，Playwright 全验证通过，0 控制台错误）已验证可行。但首次使用仍需尝试 `find ~/.hermes/skills/html-ppt/ -name 'deck.html'` 确认文件是否存在，不存在再回退。

**三花集团 AI 培训 PPT 验证案例**：47 页 / 147KB，包含：
- 讲师介绍页（照片 base64 内嵌，解决 file:// 加载失败）
- SVG 架构图：已按用户要求从深色改为白色底（含颜色映射表）
- 评分标准 grid 对齐布局
- 教材级信息密度（完整句子+代码块+对比表格）
- Apple 白底设计规范（#fff 底 + #1d1d1f 文字 + 蓝/绿/橙强调色）
- slide 内部滚动条美化（6px 圆角浅灰滑块）
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
│   ├── authoring-guide.md       # 完整工作流
│   ├── apple-design-white-theme.md  # Apple白底设计规范
│   └── inline-only-fallback-pattern.md  # 零依赖回退模式（含47页验证）
│   └── training-document-cascade.md  # 培训文档级联更新流程+同步检查清单
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

## Apple 设计规范速查（用户明确要求遵守）

### 配色
- **背景**：`#ffffff` 纯白为主，`#f5f5f7` 浅灰仅用于分隔区块
- **文字**：`#1d1d1f` 深色标题，`#515154` 正文，`#86868b` 辅助说明
- **强调色**：`#0071e3` 蓝（主色）、`#34c759` 绿（正确/能做）、`#ff9500` 橙（注意/不做）、`#ff3b30` 红（错误/禁止）
- **禁止**：大面积灰色背景+灰色文字、深色底+浅色文字作为默认主题

### 圆角与阴影
- 卡片圆角：12px-20px
- 阴影：`0 2px 12px rgba(0,0,0,0.06)` 标准，`0 8px 30px rgba(0,0,0,0.08)` 悬停
- 避免生硬直角边框

### 字体
- 系统字体栈：`-apple-system, 'SF Pro Display', 'PingFang SC', sans-serif`
- 标题：2rem+ / 700-800 weight
- 正文：1.05rem / 400 weight
- 辅助：0.82rem / 600 weight / uppercase / letter-spacing 0.05em

## 常见陷阱

### ⚠️ patch 工具截断 base64 数据（最高优先级）

**绝对不要用 `patch` 工具编辑包含 base64 data URI 的 HTML 文件。** patch 的 diff 算法在处理超长 base64 字符串时会截断数据，导致 img 标签损坏（实测：148KB 的 PNG base64 被截断到只剩开头标签）。

**正确做法**：用 `terminal` 或 `execute_code` 运行 Python 脚本做全文 `str.replace()` 或 `re.sub()`，然后 `write_file` 写回。详见"讲师照片 file:// 协议加载失败"章节的代码示例。

### 模板文件缺失

html-ppt 技能通过 `skill_manage` 创建时，仅 SKILL.md 被同步。`assets/`、`templates/`、`scripts/` 目录不会自动附带。检测方法：`ls ~/.hermes/skills/html-ppt/templates/` 为空或不存在。

**回退方案**：手写内联 HTML PPT。结构如下：
- 单文件 HTML，所有 CSS/JS 内联
- 每页一个 `<div class="slide">`，通过 `display:none/block` 切换
- 键盘 ← → Space 翻页，Home/End 首尾
- 移动端 touch swipe
- 响应式：`@media (max-width:768px)` 单列布局

参考产出：profit-sharing-ppt（15页内部版）和 profit-sharing-ppt-lecturer（6页讲师精简版），均在 `gzzhike.cn/web-spa/` 下。

### 讲师照片 file:// 协议加载失败

用户反馈"讲师照片无法显示"是常见问题。原因：浏览器安全策略阻止 `file://` 页面加载同目录图片（CORS 限制）。

**检测方法**：打开 PPT 后讲师页照片区域空白或显示 broken image 图标。

**修复方案**：将照片转为 base64 内嵌 HTML，不引用外部文件。

**⚠️ 关键陷阱：不要用 `patch` 工具替换 base64 数据！** patch 的 diff 机制会截断 base64 数据 URI（实测：148KB 的 PNG base64 被截断到只剩开头）。必须用 `terminal` 运行 Python 脚本做全文替换。

```python
# ✅ 正确做法：用 terminal/execute_code 运行 Python 全文替换
import re

# 1. 生成 data URI（两种方案）
# 方案A：JPEG（小，但无透明度）
from PIL import Image
import io, base64
img = Image.open("讲师照片.png")
img = img.resize((280, 340), Image.LANCZOS)
if img.mode == "RGBA":
    img = img.convert("RGB")  # JPEG 不支持 alpha
buf = io.BytesIO()
img.save(buf, format="JPEG", quality=80, optimize=True)
data_uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

# 方案B：PNG 保留透明度（用户要求"保持背景透明"时用）
img = Image.open("讲师照片.png")
img = img.resize((480, 576), Image.LANCZOS)  # 保持 RGBA
img = img.quantize(colors=128, method=2)  # 量化减小体积，保留 alpha
buf = io.BytesIO()
img.save(buf, format="PNG", optimize=True)
data_uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

# 方案C：原图不压缩（用户说"别压缩"时）
with open("讲师照片.png", "rb") as f:
    data_uri = "data:image/png;base64," + base64.b64encode(f.read()).decode()

# 2. 全文替换（用 regex 匹配现有 data URI）
with open("PPT.html", "r", encoding="utf-8") as f:
    content = f.read()
pattern = r'src="data:image/[^;]+;base64,[A-Za-z0-9+/=]+"'
content = re.sub(pattern, 'src="' + data_uri + '"', content)
with open("PPT.html", "w", encoding="utf-8") as f:
    f.write(content)

# ❌ 错误做法：用 patch 工具 — 会截断 base64 数据！
```

**图片大小参考**：
- JPEG 280×340 quality=80 ≈ 8KB base64（最小，无透明度）
- PNG 480×576 量化128色 ≈ 35KB base64（保留透明度，推荐）
- 原图 PNG 不压缩 ≈ 150KB base64（最佳质量，用户明确要求时用）

**选择依据**：用户说"保持背景透明"→ 方案B（量化PNG）；用户说"别压缩"→ 方案C（原图）；其他 → 方案A（JPEG）。

### 评分标准页进度条对齐

进度条+百分比+说明文字的多列 flex 布局容易对齐错位。用户反馈"进度条和文字对齐有问题"。

**正确模式**：每行用统一的 `grid-template-columns` 而非各自 flex，确保列宽一致：

```css
.score-row {
  display: grid;
  grid-template-columns: 60px 1fr 100px 200px;  /* % | bar | name | desc */
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
}
```

**常见错误**：每行用独立 flex + `min-width`，导致不同行的列宽不一致，进度条长短不一。

### 暗→亮背景切换的级联颜色审计（三花血泪教训）

当把 `.slide--dark` 背景从深色改为白色时，**必须系统性审计三层颜色覆盖**，否则会出现白字白底（文字不可见）：

**第一层：CSS 类规则** — 改 `.slide--dark` 的背景色和文字色：
```css
/* 改前 */
.slide--dark{background:#1d1d1f;color:#fff}
.slide--dark p,.slide--dark li{color:rgba(255,255,255,.92)}
/* 改后 */
.slide--dark{background:#fff;color:#1d1d1f}
.slide--dark p,.slide--dark li{color:rgba(0,0,0,.82)}
```

**第二层：内联 style 样式** — grep 所有在 `slide--dark` 区域内的 `color:#fff` 和 `rgba(255,255,255,...)`：
```bash
# 找出所有白色文字的内联样式
grep -n 'color:#fff\|color:rgba(255,255,255' PPT.html | grep -v 'slide--blue\|slide--gradient\|Q & A\|linear-gradient'
```

**第三层：嵌套卡片/组件** — 特别注意 `card` 内的内联 `color:#fff`，这些最容易遗漏：
```html
<!-- ❌ 白底上白字不可见 -->
<h3 style="color:#fff">AI已进入Agent时代</h3>
<p style="color:rgba(255,255,255,.7)">描述文字</p>

<!-- ✅ 修复 -->
<h3 style="color:#1d1d1f">AI已进入Agent时代</h3>
<p style="color:rgba(0,0,0,.7)">描述文字</p>
```

**安全的颜色替换规则**：
| 原值（深色背景用） | 替换值（白底用） | 用途 |
|---|---|---|
| `color:#fff` | `color:#1d1d1f` | 主文字 |
| `color:rgba(255,255,255,.92)` | `color:rgba(0,0,0,.82)` | 正文 |
| `color:rgba(255,255,255,.7)` | `color:rgba(0,0,0,.6)` | 副标题 |
| `color:rgba(255,255,255,.5)` | `color:rgba(0,0,0,.45)` | 辅助文字 |
| `color:rgba(255,255,255,.3)` | `color:rgba(0,0,0,.3)` | 极淡提示 |
| `background:rgba(255,255,255,.08)` | `background:#f5f5f7` | 信息卡片背景 |
| `background:rgba(255,255,255,.1)` | `background:rgba(0,0,0,.06)` | 键盘按键背景 |
| `color:#5ac8fa` | `color:#0071e3` | 标签文字（蓝） |

**例外（不要改）**：蓝色渐变背景（Q&A页等 `background:linear-gradient`）的白色文字是正确的；彩色圆形徽章（蓝/绿/橙底）内的白色文字是正确的。

**验证方法**：改完后必须逐页浏览器截图检查，重点看：
- 封面页（通常有大量内联白字）
- 最后几页（总结/回顾页常用 `slide--dark` 类）
- 带卡片的深色页面（卡片内嵌套的白字最容易遗漏）

### HTML PPT 内联 JS 导航函数的闭包陷阱

手写内联 HTML PPT 中，`go(n)`/`next()`/`prev()` 等导航函数通常在 IIFE 闭包内，**从浏览器控制台无法直接调用**。

**症状**：`go(45)` → `ReferenceError: go is not defined`；`document.getElementById('navNext').click()` 在控制台返回 null 但不生效。

**可用的导航方法**（按可靠性排序）：
1. **点击导航按钮**：`document.getElementById('navNext').click()` — 页面上的 `<button>` 元素点击是可靠的
2. **总览模式跳转**：按 `o` 键打开总览 → 找到目标缩略图 → 点击
3. **键盘事件**：`document.dispatchEvent(new KeyboardEvent('keydown', {key:'ArrowRight', bubbles:true}))` — 部分 PPT 可用
4. **End/Home 键**：跳到最后一张或第一张，再往回翻
5. **URL hash**：如果 PPT 支持 `#/45` 格式，直接改 URL

**批量翻页技巧**（跳到第 N 张）：
```javascript
// 方法1：点击按钮 N 次（最可靠）
const btn = document.getElementById('navNext');
for(let i=0; i < N; i++) { btn.click(); }

// 方法2：总览模式
document.dispatchEvent(new KeyboardEvent('keydown', {key:'o'}));
// 然后用 browser_vision 截图找到目标缩略图，点击
```

### 文字对比度不足

用户反馈"文字和底色太相近不容易看到"。Apple 设计规范要求：
- 白色背景 (`#fff`) 上用 `--ink: #1d1d1f` 深色文字
- 浅灰背景 (`#f5f5f7`) 上也可以用 `--ink`，但避免用 `--ink-3: #86868b` 作为正文
- 深色背景上必须用 `#fff` 或 `#e6edf3` 文字

**检测方法**：截图后目视检查，或用浏览器 DevTools 的 Contrast 检查器。WCAG AA 标准要求正文对比度 ≥ 4.5:1。

**常见错误**：`.slide--gray` 页面上用 `--ink-3: #86868b` 作为正文颜色，导致浅灰底+浅灰字。

### 代码块文字颜色在浅色背景上不可见

用户反馈"红底和绿底看不到字"。代码块（`<pre>`）使用了深色背景专用的文字颜色 `#e6edf3`，但容器背景是浅色（如 `rgba(255,59,48,.1)` 浅粉、`rgba(52,199,89,.1)` 浅绿）。

**根因**：`#e6edf3` 是为深色代码块（`.code-block` 黑色背景）设计的浅灰文字色。当代码块嵌入浅色卡片（对比卡、好坏示例等）时，浅灰文字在浅色背景上几乎不可见。

**检测方法**：grep 所有 `<pre` 标签，检查其 `color` 值是否与所在容器的背景色对比度足够。

```bash
# 找出所有使用 #e6edf3 的 pre 标签
grep -n 'pre.*#e6edf3\|#e6edf3.*pre' PPT.html
```

**修复**：将 `#e6edf3` 改为 `#1d1d1f`（深色文字）：
```html
<!-- ❌ 浅色背景上不可见 -->
<pre style="margin:0;background:none;padding:0;color:#e6edf3">内容</pre>

<!-- ✅ 浅色背景上清晰可读 -->
<pre style="margin:0;background:none;padding:0;color:#1d1d1f">内容</pre>
```

**注意**：不要改深色 `.code-block` 容器内的 `#e6edf3`——那是有意设计的深色代码块样式。只改嵌入浅色卡片/对比区域内的 `<pre>` 标签。

### max-height 限制破坏 flex 等高卡片

用户反馈"页面框体和内容框体大小不一致，内容框体仅页面框体的一半高度"。

**根因**：flex 容器中的子卡片应该等高（flexbox 默认 `align-items: stretch`），但卡片内的代码块设置了 `max-height:160px`，导致该卡片被压缩到远小于兄弟卡片的高度。

```html
<!-- ❌ 左卡片 max-height 限制导致不等高 -->
<div style="display:flex;gap:14px">
  <div class="card" style="flex:1">
    <div class="code-block" style="max-height:160px;overflow-y:auto">...</div>
  </div>
  <div class="card" style="flex:1">
    <ul>...很多列表项...</ul>
  </div>
</div>

<!-- ✅ 移除 max-height，flex 等高生效 -->
<div style="display:flex;gap:14px">
  <div class="card" style="flex:1">
    <div class="code-block" style="overflow-y:auto">...</div>
  </div>
  <div class="card" style="flex:1">
    <ul>...很多列表项...</ul>
  </div>
</div>
```

**规则**：在 flex 等高布局中，不要对子元素的子元素设置 `max-height`。如果内容确实需要滚动限制，改用 `flex:1` + `overflow-y:auto` 而非固定 `max-height`。

### 说明类文字混入内容

用户要求"移除说明类文档（例如配三花场景，与三花的关系，三花示例等）"。

**定义**：说明类文字是给读者解释"为什么这页内容存在"的元信息，不是内容本身。

**识别特征**：
- "配XX场景"、"与XX的关系"、"XX示例"
- "这一页的重点是…"
- "这里需要说明的是…"

**处理**：全部删除。这些文字放在演讲者备注（`.notes`）里，不放在可见区域。

### 组件大小与文字展示不匹配

用户反馈"大内容框体，但是文字展示仅一般"。

**原因**：卡片/容器很大但内部文字小、留白多、信息密度低。

**修复**：
- 增大字号：正文从 `.9rem` → `1.05rem`
- 增加内容：从关键词列表改为完整句子
- 减少卡片内边距：`padding: 24px` → `padding: 20px`
- 使用多列布局：`cols-2` 或 `cols-3` 填充空间

### 用户要求把暗色 SVG 架构图改成白底（不是保持深色）

当全局已改白底、SVG 还是深色块时，用户会明确说"SVG也改白色底"。**不要坚持保持深色**——按用户要求改。已验证的颜色映射表（直接全文替换即可）：

| 暗色原值 | 白底替换值 | 用途 |
|---------|-----------|------|
| `#0d1117` (SVG背景rect) | `#ffffff` + `stroke="#e8e8ed" stroke-width="1"` | 背景 + 细边框 |
| `#0d1117` (badge内文字) | `#ffffff` | badge本身有彩色底，文字保持白 |
| `#e6edf3` (节点标题) | `#1d1d1f` | 深色主文字 |
| `#8b949e` (节点描述) | `#6e6e73` | 次要文字 |
| `#58a6ff` (蓝色) | `#0071e3` | Apple蓝 |
| `#a78bfa` (紫色) | `#7c3aed` | 保持紫色 |

**操作要点**：先定位 SVG 区域行号范围，只在该范围内做替换，避免误伤 `.code-block`（深色背景+`#e6edf3`文字是有意的代码块样式，**不要**跟着改成白底）。

**例外**：若用户只说"底色尽量白色"但未点名 SVG，且 SVG 作为视觉焦点存在，可保持深色 SVG + 白色 slide 底。一旦用户明确说 SVG 也要白，按上表改。

### Slide 内部滚动条样式

白底 PPT 中部分 slide 内容超出视口时会出现浏览器默认滚动条，视觉上突兀。添加细滚动条样式：

```css
.slide::-webkit-scrollbar{width:6px}
.slide::-webkit-scrollbar-track{background:transparent}
.slide::-webkit-scrollbar-thumb{background:#c1c1c1;border-radius:3px}
.slide::-webkit-scrollbar-thumb:hover{background:#a8a8a8}
```

6px 宽 + 圆角浅灰滑块 + 透明轨道，hover 加深。仅作用于 `.slide`，不影响全局。

## 上游与许可

- 上游仓库：[lewislulu/html-ppt-skill](https://github.com/lewislulu/html-ppt-skill)
- 许可：MIT © 2026 lewis
- 版本：基于 main 分支快照，36 主题 / 31 布局 / 47 动效 / 15 完整模板
