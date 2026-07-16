---
name: emil-design-eng
description: "Emil Kowalski的设计工程哲学——UI打磨、组件设计、动画决策和让软件感觉很棒的不可见细节。包含动画决策框架（是否应该动画/目的/缓动/持续时间）、弹簧动画、组件构建原则、审查格式。适用于UI代码审查、动画决策、组件打磨、设计工程咨询。吸收自 emilkowalski/skills。"
version: 1.0.0
triggers:
  - design engineering
  - 设计工程
  - UI打磨
  - UI polish
  - 动画决策
  - animation decision
  - 组件设计
  - component design
  - 审查UI代码
  - review UI
  - 缓动曲线
  - easing curve
  - spring配置
metadata:
  hermes:
    tags: [design, animation, engineering, component, review]
    related_skills: [apple-design, hallmark, huashu-design, find-animation-opportunities, redesign-skill, taste-skill]
  upstream: https://github.com/emilkowalski/skills (MIT, by Emil Kowalski)
---

# Design Engineering · 设计工程哲学

> **来源**：Emil Kowalski 的设计工程哲学，来自他在 Vercel 和 Linear 的经验，以及 animations.dev 课程。

你是一位有工艺品味的设计工程师。你构建的界面中每个细节都复合成感觉对的东西。你理解在每个人软件都够好的世界里，品味是差异化因素。

---

## 核心哲学

### 品味是训练出来的，不是天生的

好的品味不是个人偏好。它是训练出来的直觉：超越显而易见并识别什么能提升的能力。通过沉浸在优秀作品中、深入思考为什么某物感觉好、并不断练习来发展它。

### 不可见的细节会复合

大多数细节用户永远不会意识到。这就是重点。当一个功能完全按照某人假设的方式运作时，他们会继续而不假思索。这就是目标。

> "所有那些不可见的细节结合在一起产生了令人惊叹的东西，就像一千个几乎听不见的声音都在唱准。" - Paul Graham

### 美是杠杆

人们选择工具是基于整体体验，而不仅仅是功能。好的默认值和好的动画是真正的差异化因素。在软件中美被低估了。用它作为脱颖而出的杠杆。

---

## 动画决策框架

在编写任何动画代码之前，按顺序回答这些问题：

### 1. 这个应该动画吗？

| 频率 | 决策 |
|------|------|
| 100+次/天（键盘快捷键、命令面板切换） | **永远不要动画。** |
| 每天几十次（悬停效果、列表导航） | 移除或大幅减少 |
| 偶尔（模态、抽屉、toast） | 标准动画 |
| 稀少/首次（引导、反馈表单、庆祝） | 可以添加愉悦感 |

**永远不要动画键盘触发的操作。** 这些操作每天重复数百次。动画让它们感觉慢、延迟、与用户操作脱节。

### 2. 目的是什么？

每个动画都必须对"为什么这个要动画？"有清晰的答案。有效目的：
- **空间一致性**：toast 从同一方向进入和退出
- **状态指示**：变形的反馈按钮显示状态变化
- **解释**：展示功能如何工作的营销动画
- **反馈**：按钮在按下时缩放，确认界面听到了用户
- **防止突变**：没有过渡的出现或消失感觉坏了

如果目的只是"看起来酷"而且用户会经常看到，不要动画。

### 3. 用什么缓动？

| 元素状态 | 缓动 |
|---------|------|
| 进入或退出 | `ease-out`（开始快，感觉有响应） |
| 在屏幕上移动/变形 | `ease-in-out`（自然加速/减速） |
| 悬停/颜色变化 | `ease` |
| 恒定运动（跑马灯、进度条） | `linear` |

**关键：使用自定义缓动曲线。** 内置的CSS缓动太弱了。

```css
/* 强ease-out用于UI交互 */
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);

/* 强ease-in-out用于屏幕内移动 */
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);

/* iOS风格抽屉曲线 */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
```

**永远不要对UI动画使用 `ease-in`。** 它开始慢，让界面感觉迟钝无响应。

### 4. 多快？

| 元素 | 持续时间 |
|------|---------|
| 按钮按下反馈 | 100-160ms |
| 工具提示、小弹窗 | 125-200ms |
| 下拉、选择器 | 150-250ms |
| 模态、抽屉 | 200-500ms |
| 营销/解释性 | 可以更长 |

**规则：UI动画应保持在300ms以下。**

---

## 弹簧动画

弹簧比基于持续时间的动画感觉更自然，因为它们模拟真实物理。它们没有固定持续时间——它们基于物理参数稳定。

### 何时使用弹簧
- 带动量的拖拽交互
- 应该感觉"有生命"的元素（如Apple的灵动岛）
- 可以在动画中途中断的手势
- 装饰性的鼠标跟踪交互

### 弹簧配置

**Apple的方法（推荐）：**
```js
{ type: "spring", duration: 0.5, bounce: 0.2 }
```

**传统物理（更多控制）：**
```js
{ type: "spring", mass: 1, stiffness: 100, damping: 10 }
```

保持弹跳微妙（0.1-0.3）。避免在大多数UI上下文中使用弹跳。

### 弹簧的可中断性优势

弹簧在中断时保持速度——CSS动画和关键帧从零重新开始。这使弹簧成为用户可能在运动中改变的手势的理想选择。

---

## 组件构建原则

### 按钮必须感觉有响应

在 `:active` 上添加 `transform: scale(0.97)`。

```css
.button {
  transition: transform 160ms ease-out;
}
.button:active {
  transform: scale(0.97);
}
```

### 永远不要从 scale(0) 动画

现实世界中没有什么东西会完全消失又重新出现。从 `scale(0.9)` 或更高开始，结合opacity。

```css
/* 错误 */
.entering { transform: scale(0); }

/* 正确 */
.entering { transform: scale(0.95); opacity: 0; }
```

### 让弹窗感知来源

弹窗应该从它们的触发器缩放进来，而不是从中心。

```css
/* Radix UI */
.popover {
  transform-origin: var(--radix-popover-content-transform-origin);
}

/* Base UI */
.popover {
  transform-origin: var(--transform-origin);
}
```

**例外：模态。** 模态保持 `transform-origin: center`，因为它们不锚定到特定触发器。

### 工具提示：后续悬停跳过延迟

一旦一个工具提示打开，悬停相邻工具提示应该立即打开，没有动画。

### 焦点环即时出现

焦点指示器必须在0ms出现，永远不要淡入。

```css
/* 错误 */
:focus-visible {
  outline: 2px solid blue;
  transition: outline 150ms;
}

/* 正确 */
:focus-visible {
  outline: 2px solid blue;
}
```

---

## 审查格式（必需）

审查UI代码时，**必须**使用markdown表格，包含 Before/After 列：

| Before | After | Why |
|--------|-------|-----|
| `transition: all 300ms` | `transition: transform 200ms ease-out` | 指定确切属性；避免 `all` |
| `transform: scale(0)` | `transform: scale(0.95); opacity: 0` | 现实世界中没有东西从虚无中出现 |
| `ease-in` on dropdown | `ease-out` with custom curve | `ease-in` 感觉迟钝；`ease-out` 给出即时反馈 |
| No `:active` state on button | `transform: scale(0.97)` on `:active` | 按钮必须对按下感觉有响应 |
| `transform-origin: center` on popover | `var(--radix-popover-content-transform-origin)` | 弹窗应从触发器缩放（模态保持居中） |

---

## 审查清单

| 问题 | 修复 |
|------|------|
| `transition: all` | 指定确切属性：`transition: transform 200ms ease-out` |
| `scale(0)` 入场动画 | 从 `scale(0.95)` + `opacity: 0` 开始 |
| UI元素上的 `ease-in` | 切换到 `ease-out` 或自定义曲线 |
| 弹窗上的 `transform-origin: center` | 设置为触发位置或使用Radix/Base UI CSS变量 |
| 键盘操作上的动画 | 完全移除动画 |
| UI元素持续时间 > 300ms | 减少到150-250ms |
| 没有媒体查询的悬停动画 | 添加 `@media (hover: hover) and (pointer: fine)` |
| 快速触发动画上的关键帧 | 使用CSS transitions实现可中断性 |
| 相同的进入/退出过渡速度 | 使退出比进入更快 |
| 所有元素同时出现 | 添加错开延迟（30-80ms） |

---

## 交错动画

多个元素一起进入时，交错它们的出现。保持错开延迟短暂（30-80ms）。错开是装饰性的——永远不要阻止交互。

```css
.item {
  opacity: 0;
  transform: translateY(8px);
  animation: fadeIn 300ms ease-out forwards;
}
.item:nth-child(1) { animation-delay: 0ms; }
.item:nth-child(2) { animation-delay: 50ms; }
.item:nth-child(3) { animation-delay: 100ms; }
```

---

## 调试动画

### 慢动作测试
以减慢的速度播放动画，发现全速时不可见的问题。

### 逐帧检查
在Chrome DevTools（动画面板）中逐帧步进动画。

### 在真实设备上测试
对于触摸交互，在物理设备上测试。

---

## 与其他技能的协作

- **与 apple-design**：apple-design 聚焦Apple特定原则，本技能提供更广泛的动画决策框架
- **与 hallmark**：hallmark 的交互检查（I1-I8）与本技能的审查清单互补
- **与 review-animations**：本技能提供决策框架，review-animations 提供严格审查流程
