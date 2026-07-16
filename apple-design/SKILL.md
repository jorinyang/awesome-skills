---
name: apple-design
description: "Apple设计原则与流体交互——基于WWDC设计演讲提炼的17条设计与动效原则，翻译为Web可落地的实现方案。覆盖弹簧动画、手势交互、可中断性、速度传递、动量投影、毛玻璃材质、字体细节等。适用于构建手势驱动UI、spring动画、拖拽/滑动/弹窗交互、动量与可中断转场、半透明材质与深度、排版（光学尺寸、字距、行高）、减弱动效、以及Apple风格界面背后的设计基础。吸收自 emilkowalski/skills。"
version: 1.0.0
triggers:
  - apple design
  - Apple风格
  - 流体交互
  - fluid interface
  - spring动画
  - 弹簧动画
  - 手势交互
  - gesture UI
  - 可中断动画
  - interruptible animation
  - iOS风格
  - 毛玻璃
  - backdrop-filter
  - Apple设计原则
metadata:
  hermes:
    tags: [design, animation, interaction, apple, spring, gesture]
    related_skills: [huashu-design, hallmark, emil-design-eng, taste-skill, find-animation-opportunities, redesign-skill]
  upstream: https://github.com/emilkowalski/skills (MIT, by Emil Kowalski)
---

# Apple Design · 流体界面设计原则

> **来源**：Apple WWDC 设计演讲（主要是 _Designing Fluid Interfaces_ WWDC 2018），提炼并翻译为 Web 平台实现（CSS、Pointer Events、`requestAnimationFrame`、spring库如 Motion/Framer Motion）。

**核心理念**：当界面与我们的思考和移动方式对齐时，魔法就会发生——它不再感觉像计算机，而是感觉像我们的无缝延伸。

**贯穿线索**：**当动画从当前屏幕值开始、继承用户速度、向前投射动量、并且可以在任何瞬间被抓取和反转时，界面就感觉有生命力。**

---

## 核心思想

Apple 将设计框架为服务于四种人类需求：**安全感/可预测性、理解、成就、喜悦。** 这里的每一条规则都服务于其中之一。

界面在以下情况下是流体的：即时响应、连续移动、携带动量、在边界处抵抗、并且可以在运动中被重定向。

---

## 17条设计与动效原则

### 1. 响应——消灭延迟

延迟一出现，直接感就会"悬崖式"下降。响应是其他一切的基础。

- **在 pointer-down 时响应，而不是在释放时**。按钮按下瞬间就要高亮。等待 `click`/touch-up 才显示反馈感觉死气沉沉。
- **警惕每一个延迟**。审查 debounce、人工计时器、过渡等待和约300ms的点击延迟。输入路径上的任何非必需都是退化。
- **反馈必须在交互过程中持续**，而不仅仅在结束时。拖拽、滑块或抽屉，整个过程都要1:1跟随指针更新UI——永远不要只在手势完成后才动画。

```css
/* 反馈在按下时触发，且是即时的 */
.button:active {
  transform: scale(0.97);
  transition: transform 100ms ease-out;
}
```

### 2. 直接操作——1:1跟踪

> "触摸和内容应该一起移动。"

用户拖拽某物时，它必须粘在手指上——并且尊重**抓取位置的偏移**。抓取时吸附到元素中心会立即打破幻觉。

- 使用 Pointer Events 和 `setPointerCapture`，这样即使指针离开元素边界，跟踪也会继续。
- 跟踪简短的**速度/位置历史**（最近几个 `pointermove` 事件），而不仅仅是当前点——释放时需要速度。

```js
el.addEventListener('pointerdown', (e) => {
  el.setPointerCapture(e.pointerId);
  const grabOffset = e.clientY - el.getBoundingClientRect().top; // 尊重抓取位置
  // ...跟踪位置+时间戳历史以计算速度
});
```

### 3. 可中断性——最重要的原则

> "思想和手势并行发生。"

每个动画都必须可以在任何时刻被中断和重定向。用户必须能够在动画飞行中抓住移动的元素并反转它，而无需等待动画完成。

- **在过渡期间永远不要锁定输入。**
- **始终从*呈现*（当前）值开始动画，永远不要从目标值开始**。中断时，读取元素的实时屏幕变换并从那里开始新动画。从逻辑/目标值开始会导致可见的跳跃。
- **避免对任何手势驱动的动画使用 CSS transitions 和 `@keyframes`**——它们无法在飞行中被平滑抓取和反转。弹簧默认从当前值开始动画，这正是中断所需要的。
- **当手势反转时，混合速度——不要硬切**。在反转点替换一个动画为另一个会产生速度不连续，即"砖墙"感。
- **将2D运动分解为独立的X和Y弹簧**。2D距离上的单个弹簧在X和Y速度不同时会不同步。

### 4. 行为优于动画——使用弹簧

> "把动画想象成你和物体之间的对话，而不是界面规定的某物。"

预编程的、固定持续时间的动画无法响应新输入。弹簧可以——新输入只需改变目标，运动就保持连续。对于任何用户可以触摸的东西，都要使用弹簧。

Apple 用两个设计师友好的参数替换了物理三元组（质量/刚度/阻尼）：

- **阻尼比** — 控制过冲。`1.0` = 临界阻尼，无弹跳，平滑稳定。`< 1.0` = 过冲并振荡。越低弹跳越多。
- **响应** — 值达到目标的速度，以秒为单位。越低越快。**这不是"持续时间"**——弹簧没有固定持续时间；它的稳定时间从参数中涌现。

**默认值：**
- 大多数UI从**阻尼 `1.0`**（临界阻尼）开始——优雅且不分散注意力。
- **仅在手势本身携带动量时**（甩动、投掷、拖拽释放）添加弹跳（**阻尼约 `0.8`**）。菜单淡入时过冲感觉不对；你甩动的卡片过冲感觉对了。

**Apple 发布的具体值：**

| 交互 | 阻尼 | 响应 |
|------|------|------|
| 移动/重定位（如PiP） | `1.0` | `0.4` |
| 旋转 | `0.8` | `0.4` |
| 抽屉/弹窗 | `0.8` | `0.3` |

**Web映射（Motion/Framer Motion）：** `bounce` + `duration` spring API 与 Apple 的 damping + response 密切对应。安全的风格是默认到处使用 `damping: 1.0` 弹簧；为动量驱动的物理交互保留弹跳。

```js
import { animate } from 'motion';

// 临界阻尼默认（无过冲）
animate(el, { y: 0 }, { type: 'spring', bounce: 0, duration: 0.4 });

// 动量交互——轻微弹跳，仅因为之前有甩动
animate(el, { y: target }, { type: 'spring', bounce: 0.2, duration: 0.4 });
```

### 5. 速度交接——拖拽与动画之间的接缝

手势结束时，动画必须**以手指的确切速度继续**，这样拖拽和动画之间就没有可见的接缝。这是最能区分"流体"和"还行"的细节。

将指针的释放速度作为弹簧的初始速度传递。某些弹簧API需要**相对**速度——按到目标的剩余距离归一化：

```
relativeVelocity = gestureVelocity / (targetValue − currentValue)
```

### 6. 动量投射——动画到手势*要去*的地方

> "取一个小输入，做一个大输出。"

不要从*释放点*吸附到最近的边界。使用速度来**投射静止位置**——就像滚动减速一样——然后吸附到最接近投射点的目标。这就是让甩动感觉像在扔元素的原因。

Apple 的精确投射函数：

```js
// decelerationRate ≈ 0.998 正常滚动感；0.99 更快
function project(initialVelocity, decelerationRate = 0.998) {
  return (initialVelocity / 1000) * decelerationRate / (1 - decelerationRate);
}

const projectedEndpoint = currentPosition + project(releaseVelocity);
const target = nearestSnapPoint(projectedEndpoint);
animateSpringTo(target, { velocity: releaseVelocity });
```

### 7. 空间一致性——对称路径，锚定起源

> "如果某物从一个方向消失，我们期望它从它来的地方出现。"

- **沿相同路径进入和退出。** 从右侧滑入的面板必须向右侧消失。
- **将交互锚定到它们的来源。** 菜单、弹窗或抽屉应从触发它的元素起源——设置 `transform-origin` 到触发器。
- **在可反转过渡上镜像缓动**，使出站路径与返回路径匹配。

### 8. 在手势方向上暗示

人类从轨迹预测最终状态。中间运动应该预告事物的去向——不仅仅是盲目插值。

### 9. 橡皮筋——软边界

在边缘处，渐进地抵抗而不是硬停。硬停读作"冻结"；持续抵抗读作"有响应，但这里没有更多了"。

```js
function rubberband(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}
```

### 10. 手势设计细节（"感觉"清单）

- **点击：** 在 touch-*down* 时高亮（即时），在 touch-*up* 时提交。添加约10px的滞后/命中填充，允许通过拖走并返回来取消。
- **拖拽/滑动：** 在提交方向之前需要小的移动阈值（滞后，约10px），然后1:1跟踪。
- **从第一次移动开始并行检测所有可能的手势**，然后在意图明确时自信地取消失败者。
- **最小化消歧延迟。** 双击检测不可避免地延迟单击；只在真正存在双击的地方支付该成本。

### 11. 帧级平滑

目标是60fps（或在ProMotion显示器上120fps）。避免布局抖动——只动画 `transform` 和 `opacity`。使用 `will-change` 提示浏览器提升到合成层。

### 12. 材质与深度

使用 `backdrop-filter: blur()` 创建半透明层。大的表面需要更强的模糊和阴影，小控件的模糊和阴影要轻一点。该聚焦的时候用遮罩压低背景。

```css
.glass-panel {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
```

### 13. 字体细节

大标题和正文不能共用一套字距。大字需要更紧一点（`letter-spacing: -0.02em`），小字需要更照顾可读性（接近 `0`）。行高也要跟字号一起调。

### 14. 减弱动效

尊重 `prefers-reduced-motion`。使用交叉淡入而不是滑动/弹簧。

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 15. 按钮反馈

按下瞬间就要有反馈。使用 `:active` 伪类，缩放0.95-0.98之间。

### 16. 设计基础（8条原则）

1. **一致性。** 模式、交互、术语——在整个体验中保持一致。
2. **可见性。** 让重要信息显而易见；不要让用户猜测或记忆。
3. **反馈。** 每个操作都有即时、清晰的响应。
4. **约束。** 在正确的时机限制选项——禁用不适用的操作，引导到可能的路径。
5. **对齐。** 对齐创造秩序和清晰度；像素级精度很重要。
6. **层级。** 使用视觉权重来引导注意力到最重要的事情。
7. **工艺。** 毫不妥协的细节关注建立信任。美丽的排版、适应明暗的颜色、清晰的图标、响应迅速的动画。
8. **愉悦。** 做好其他七项的结果，不是附加的装饰。

### 17. 流程

- **交互式原型——一个交互式演示值得"一百万个静态设计"。**
- **同时设计交互和视觉。** "你不应该能分辨一个在哪里结束，另一个在哪里开始。"
- **在真实环境中与真实用户测试**，用新鲜的眼睛审查运动——慢动作/逐帧播放以捕捉全速时不可见的东西。

---

## 快速参考

| 需求 | 技术 | 具体值 |
|------|------|--------|
| 默认UI弹簧 | 临界阻尼，无过冲 | `damping 1.0`, `response 0.3–0.4` |
| 动量/甩动弹簧 | 欠阻尼，轻微弹跳 | `damping ~0.8`, `response 0.3–0.4` |
| 手势→弹簧速度 | 交接释放速度 | `gestureVelocity / (target − current)` |
| 甩动落点 | 投射动量 | `current + (v/1000)·d/(1−d)`, `d ≈ 0.998` |
| 干净中断 | 从呈现（实时）值开始 | 读取屏幕变换 |
| 避免反转"砖墙" | 通过重新目标混合速度 | 混合速度的弹簧 |
| 可反转过渡 | 镜像缓动曲线 | 反向三次贝塞尔 |
| 决定反转vs提交 | 使用速度**符号**，不是位置 | 释放时 |
| 1:1拖拽 | Pointer Events + capture | 尊重抓取偏移 |
| 反馈 | 在pointer-down时，持续 | 永远不要只在结束时 |
| 边界 | 橡皮筋，不要硬停 | 渐进抵抗 |
| 半透明材质 | `backdrop-filter` 层 | 内容在下方滚动 |
| 字体跟踪 | 尺寸特定，永远不要固定 | 大标题收紧(`-0.02em`)，正文接近`0` |
| 减弱动效 | 交叉淡入，不要滑动/弹簧 | `@media (prefers-reduced-motion)` |

---

## 使用场景

| 场景 | 本技能的指导 |
|------|-------------|
| 构建底部弹窗/抽屉 | §4弹簧配置 + §3可中断性 + §9橡皮筋 |
| 手势驱动的卡片交互 | §2直接操作 + §5速度交接 + §6动量投射 |
| 按钮/交互元素反馈 | §1响应 + §15按钮反馈 |
| 毛玻璃/材质效果 | §12材质与深度 |
| 排版与字体细节 | §13字体细节 |
| 无障碍动效 | §14减弱动效 |
| 整体设计方向 | §16设计基础 |

---

## 与其他技能的协作

```
taste-skill 🔮     →  apple-design 🍎     →  hallmark 🛡️
（定方向/风格）        （Apple设计原则执行）    （质量门禁验证）
                         ↕
                    huashu-design 🎨
                    （综合设计执行）
```

- **与 huashu-design**：当用户要求"Apple风格"或"iOS风格"时，先加载本技能获取原则，再用 huashu-design 执行具体设计
- **与 hallmark**：hallmark 的交互检查（I1-I8）与本技能的动效原则互补
- **与 emil-design-eng**：本技能聚焦Apple特定原则，emil-design-eng 提供更广泛的动画决策框架
