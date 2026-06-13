# 暖单色极简系统 · Warm Minimalist System

> 吸收自 upstream taste-skill/minimalist-skill（极简UI风格预设）
> 用于 huashu-design 的 editorial / modern-minimal 方向

## 核心理念

极简不是"少"——是"每一像素都有理由存在"。暖单色 + 高度克制的 accent 使界面像高级编辑出版物而非 Dashboard。

## 调色板：暖单色 + 淡彩 Accent

```
Canvas:     #FFFFFF 或 #F7F6F3（暖骨白）
Surface:    #FFFFFF 或 #F9F9F8
Border:     #EAEAEA 或 rgba(0,0,0,0.06)
Text:       #111111（off-black，不用 #000）
Secondary:  #787774（暖灰）
```

**淡彩 Accent 系统**（仅用于标签/代码背景/图标底色）：

| Accent | 背景 | 文字 | 
|--------|------|------|
| Pale Red | `#FDEBEC` | `#9F2F2D` |
| Pale Blue | `#E1F3FE` | `#1F6C9F` |
| Pale Green | `#EDF3EC` | `#346538` |
| Pale Yellow | `#FBF3DB` | `#956400` |

**规则**：淡彩 accent 仅用于语义标注，不作为大面积底色。大面积保持纯白或暖骨白。

## 排版层级

```
Hero Headings: Serif（Lyon Text / Newsreader / Playfair Display）
  letter-spacing: -0.02em ~ -0.04em
  line-height: 1.1

Body & UI: Sans（SF Pro Display / Geist Sans / Switzer）
  line-height: 1.6

Code & Meta: Mono（Geist Mono / SF Mono / JetBrains Mono）
```

## 组件规范

### Bento 网格
- CSS Grid 非对称布局
- 卡片：`border: 1px solid #EAEAEA`，border-radius 8px-12px（不大圆角）
- 内边距慷慨：24px-40px

### 主 CTA 按钮
- 实心 `#111111` 背景 + `#FFFFFF` 文字
- border-radius 4px-6px
- **无** box-shadow
- hover: 颜色微移到 `#333333`，或微缩放 `scale(0.98)`

### 标签/徽章
- 药丸形（border-radius: 9999px）
- 极小字号（text-xs），大写 + 宽 tracking（0.05em）
- 背景来自淡彩 Accent 系统

### FAQ 折叠
- 剥掉容器盒子
- 仅用 `border-bottom: 1px solid #EAEAEA` 分隔
- 干净利落的 + / - 切换图标

## 隐形动效哲学

动效应"看不见"——存在但不引人注意。目标是安静的精致，不是表演。

| 动效 | 参数 |
|------|------|
| Scroll Entry | translateY(12px) + opacity:0 → 600ms cubic-bezier(0.16, 1, 0.3, 1) |
| Card Hover | box-shadow: 0 0 0 → 0 2px 8px rgba(0,0,0,0.04), 200ms |
| Button Active | scale(0.98) |
| Staggered List | animation-delay: calc(var(--index) * 80ms) |
| Ambient BG | 单个极慢径向渐变 blob（20s+ duration, opacity 0.02-0.04） |

**铁律**：只用 transform + opacity 做动画。不用 top/left/width/height。
