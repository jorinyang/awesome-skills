---
name: hallmark
description: Anti-AI-slop 设计质量门禁——对 HTML 产出执行 58 道关卡检查、预发射自评、audit 评分、study 设计 DNA 提取。当用户要求审查页面是否有 AI 味、检查设计质量、提取参考设计 DNA、或对 feishu-html/huashu-design 产出做最终把关时触发。
version: 1.0.0
license: MIT (adapted from Nutlope/hallmark)
triggers:
  - 审查这个页面有没有 AI 味
  - 检查设计质量
  - audit 这个页面
  - 提取这个设计的设计 DNA
  - 分析这个参考设计
  - 发射前检查
  - 反 AI slop
  - 用 Hallmark 检查
  - hallmark
metadata:
  hermes:
    tags: [design, quality, anti-slop, audit, study]
    related_skills: [huashu-design, feishu-html, design-md, humanizer]
  upstream: https://github.com/Nutlope/hallmark (MIT, by Together AI)
---

# Hallmark · Anti-AI-Slop 设计质量门禁

Hallmark 是设计产出在交付前的最后一道质量关卡。它不负责"怎么设计"（那是 huashu-design 的职责），它负责"设计完之后检查什么"——确保页面不像 AI 生成的。

**定位**：在 huashu-design（创意）→ feishu-html（部署）之间，Hallmark 作为质量门禁层运行。

## 触发条件

| 触发词 | 动作 |
|--------|------|
| "审查/检查这个页面的 AI 味" | 对指定页面运行 audit |
| "提取这个设计的设计 DNA" / "分析这个参考" | 运行 study（截图或 URL） |
| "发射前检查" / "最终把关" | 对即将部署的 HTML 运行 slop test |
| 在 feishu-html 阶段五（页面校验）中 | 自动触发 slop test（见集成规则） |

---

## 三个动词

### 1. audit — 对现有页面评分

**输入**：HTML 文件路径或在线 URL
**输出**：评分报告 + punch list（只诊断，不修改）

**执行流程**：
1. 读取目标 HTML/CSS 代码
2. 逐项对照以下"关键反模式清单"（完整 58 道关卡见 upstream `references/slop-test.md`）
3. 输出：`通过/不通过` + 具体违规位置 + 修复建议
4. 总评分：P/H/E/S/R/V 六轴各 1-5 分

### 2. study — 提取设计 DNA

**输入**：截图附件 或 URL
**输出**：设计 DNA 诊断报告（宏观结构、字体配对、色彩锚点、组件原型）

**注意事项**：
- 不复制像素、不克隆页面
- 提取的是"骨架"而非"皮肤"
- URL 模式可提取精确色值和字体名；截图模式只能推断角色
- 拒绝模板市场 URL（ThemeForest 等）

### 3. 默认 — 发射前质量门禁（slop test）

在 HTML 产出交付前，自动运行关键关卡检查。

---

## 核心 Guardrails（精简自上游 58 道关卡）

### 一、视觉反模式（无需加载完整文件）

| # | 检查项 | 违规特征 |
|---|--------|---------|
| V1 | 展示字体 | 禁止 Inter / Roboto / Open Sans / Poppins / Lato 做 display 字体 |
| V2 | 紫色渐变 | 禁止任何紫→蓝或青→品红渐变，含 `background-clip: text` 渐变标题 |
| V3 | 三列卡片阵 | 禁止 3 等宽列 + 图标在上标题在下 → Hero → CTA → Footer 模板 |
| V4 | 卡片嵌套 | 禁止卡片内部再嵌套卡片 |
| V5 | 左侧彩色边条卡片 | 禁止厚彩色左边框 accent card |
| V6 | 英雄区全居中 | 禁止 hero 100vh + 所有元素居中对齐；最多 2 个居中元素 |
| V7 | 纯黑纯白 | 禁止 `#000` / `#fff` 作为基础色（modern-minimal 风格允许纯白纸） |

### 二、排版纪律

| # | 检查项 | 违规特征 |
|---|--------|---------|
| T1 | 字体数量 | 全页不超过 3 种字体族（display + body + 最多 1 个 outlier） |
| T2 | 斜体标题 | **禁止任何标题使用斜体**（h1-h6, hero title, wordmark）。标题永远 roman |
| T3 | Outlier 用途 | outlier 字体最多用 2 处（默认 wordmark + hero stat） |
| T4 | 全大写按钮 | 禁止按钮文字全大写 |
| T5 | 标题字号匹配长度 | ≤7 词/≤50 字符 → display 字号；51-90 字符 → display-s；>90 字符 → 4xl 或重写 |

### 三、交互与动效

| # | 检查项 | 违规特征 |
|---|--------|---------|
| I1 | transition-all | 禁止 `transition: all`，必须指定具体属性 |
| I2 | hover:scale-105 泛滥 | 禁止多个无关元素统一 scale |
| I3 | 弹跳缓动 | 禁止 UI 状态变化使用 overshoot easing |
| I4 | 多重 hover 效果 | 每个元素最多 1 个 hover 效果 |
| I5 | 动画属性 | 禁止动画 `width/height/top/left/margin/padding`，只允许 `transform + opacity` |
| I6 | focus ring 淡入 | focus ring 必须即时出现（0ms），不可 fade in |
| I7 | 组件 8 态 | 每个交互元素必须有 default/hover/focus-visible/active/disabled 五态；表单额外需 loading/error/success |
| I8 | 无障碍 | 所有 motion 必须有 `prefers-reduced-motion: reduce` fallback |

### 四、内容诚信

| # | 检查项 | 违规特征 |
|---|--------|---------|
| C1 | 伪造指标 | 禁止编造 "+47% 转化率"、"10× 更快"、"50,000+ 团队" 等未提供的数据 |
| C2 | 伪造证言 | 禁止编造客户证言、logo 墙、案例数量 |
| C3 | 伪造浏览器壳 | 禁止手绘假浏览器框（URL pill + 红绿灯）、假手机框、假代码窗口 |
| C4 | emoji 图标 | 禁止 ✨🚀⚡🔥🎯✅ 作为功能卡片/价值主张/步骤/价格图标 |

### 五、移动端硬地板

| # | 检查项 | 违规特征 |
|---|--------|---------|
| M1 | 水平滚动 | 320-1920px 任意宽度出现水平滚动条 → 失败 |
| M2 | overflow | `html` 和 `body` 必须设置 `overflow-x: clip`（非 hidden） |
| M3 | 两行按钮 | 禁止按钮文字在 320px 宽度下折行 |
| M4 | 图片网格 | 禁止 `grid-template-columns: 1fr 1fr`，必须 `minmax(0, 1fr)` |
| M5 | 标题溢出 | display 标题需 `overflow-wrap: anywhere; min-width: 0` |

---

## 预发射自评（六轴评分）

交付前自评六轴（1-5 分，<3 分触发修订）：

| 轴 | 名称 | 评分标准 |
|----|------|---------|
| P | Philosophy | 页面有明确的"为什么"——有立场，不只是布局？ |
| H | Hierarchy | 2 秒内能分辨主/次/辅层级？ |
| E | Execution | 细节执行到位？(规则粗细/强调占比/自动换行/focus ring/对比度) |
| S | Specificity | 看起来像"这个项目"而非"可以是任何项目"？ |
| R | Restraint | 去掉了所有不必要的东西？ |
| V | Variety | 与同一项目之前的产出有结构差异（不只是颜色不同）？ |

---

## 与现有技能的集成

```
设计工作流中的 Hallmark 定位：

  用户需求
    │
    ▼
  huashu-design          ← 创意方法论（怎么想、怎么做）
  design-md              ← 品牌 Token 参考
    │
    ▼
  🆕 Hallmark (本技能)   ← 质量门禁层
    │  ├─ audit: 对现有页面评分
    │  ├─ study: 从参考提取 DNA → 输出 design.md
    │  └─ slop test: 发射前 58 道关卡
    │
    ▼
  humanizer              ← 文案反 AI 味
    │
    ▼
  feishu-html            ← 部署管道
```

### 集成点 1：feishu-html 阶段五（页面校验）+ Hallmark

当 `feishu-html` 进入阶段五（页面校验）时，对每个 HTML 产出额外执行：
1. 视觉反模式检查（V1-V7）
2. 内容诚信检查（C1-C4）
3. 移动端硬地板检查（M1-M5）
4. 输出 stamp：`/* Hallmark · pre-emit critique: P? H? E? S? R? V? · gates: N/58 ✓ */`

### 集成点 2：huashu-design 设计方向顾问 + Hallmark

当 `huashu-design` 处于设计方向顾问 Fallback 模式时，用户说"审查这个设计有没有 AI 味" → 触发 Hallmark audit。

### 集成点 3：design-md 品牌提取

当用户说"从这个参考设计提取设计 DNA" 时 → Hallmark study → 可选输出为 `design.md` 格式供后续使用。

---

## 快速使用

### 审查页面
```
"用 Hallmark audit 这个页面：https://xxx.com"
"检查 workshop-voting/index.html 有没有 AI 味"
```

### 提取参考 DNA
```
"用 Hallmark study 分析这个设计：[截图]"
"提取 https://stripe.com 的设计 DNA"
```

### 发射前检查
```
"对 summer-campaign/index.html 做发射前检查"
```

---

## 技术说明

- **上游**：https://github.com/Nutlope/hallmark (MIT, Together AI)
- **完整 58 道关卡**：见 upstream `skills/hallmark/references/slop-test.md`
- **完整反模式清单**：见 upstream `skills/hallmark/references/anti-patterns.md`
- **本技能** 是对上游中适用于 Hermes（HTML 产出审查）的核心规则的精简适配
- **不与 humanizer 冲突**：humanizer 管文案反 AI 味，Hallmark 管 UI 反 AI 味
- **不与 huashu-design 冲突**：huashu 是创意工具（怎么设计），Hallmark 是品控工具（检查设计）
- **实战审计案例**：见 [references/worked-audit-workshop-voting.md](references/worked-audit-workshop-voting.md) — 包含 `transition:all` 修复模板、`:focus-visible` 补全、`overflow-x: clip` 标准写法

---

## 高频陷阱速查

实际审计中最常见的三类失败：

| 陷阱 | 出现频率 | 一句话修复 |
|------|:--:|------|
| `transition: all` | 🔴 极高 | 改为 `transition: background var(--transition), color var(--transition)` |
| 缺 `:focus-visible` | 🟡 高 | `.btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px }` |
| 缺 `overflow-x: clip` | 🟡 高 | `html, body { overflow-x: clip }` — 用 `clip` 而非 `hidden` |
