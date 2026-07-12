# 高级组件模式 · Premium Component Patterns

> 吸收自 upstream taste-skill/soft-skill（高端UI风格预设）
> 用于 huashu-design 的 premium-consumer / atmospheric 方向

## 1. Double-Bezel 嵌套架构

高级卡片/容器不应平放在背景上。用嵌套外壳制造"物理硬件感"：

```
外层壳（Outer Shell）
├── bg-black/5 或 bg-white/5 微妙底色
├── ring-1 ring-black/5 极细外边框
├── p-1.5 到 p-2 外壳内边距
├── rounded-[2rem] 大外圆角
│
└── 内核（Inner Core）
    ├── 独立背景色
    ├── shadow-[inset_0_1px_1px_rgba(255,255,255,0.15)] 内高光
    └── rounded-[calc(2rem-0.375rem)] 数学精确的内圆角
```

**效果**：像一块玻璃板放在铝框里，不是一张平卡片。

## 2. Nested CTA 按钮结构

主按钮里的图标不裸露在文字旁边——嵌套在自己的圆形容器内：

```
按钮本体（rounded-full px-6 py-3）
├── 文字
└── 尾部图标容器
    ├── w-8 h-8 rounded-full
    ├── bg-black/5 dark:bg-white/10
    ├── flex items-center justify-center
    └── 图标（↗）居中对齐
```

## 3. 空间节奏

- **宏观留白**：section 间距 py-24 到 py-40，让设计呼吸
- **微标签（Eyebrow Tags）**：H1/H2 前面放微型药丸徽章
  - `rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] font-medium`
  - 非"QUESTION 05" / "SECTION 01" — 用有意义的描述

## 4. 布局原型（3选1）

### Asymmetrical Bento
类 masonry 的 CSS Grid：`col-span-8 row-span-2` + `col-span-4` 堆叠打破单调。
移动端塌缩为单列。

### Z-Axis Cascade
元素像实体卡片堆叠，有微旋转（-2deg / 3deg）打破数字网格感。
移动端移除所有旋转和负margin重叠。

### Editorial Split
左边大排版（w-1/2），右边可滚动的横向图片 pills 或交错交互卡片。
移动端全宽垂直堆叠。

## 5. 运动编排（Motion）

不要用默认过渡。模拟真实世界的质量和弹簧物理：

```css
transition: all 700ms cubic-bezier(0.32, 0.72, 0, 1);
```

Fluid Island Nav：浮动的玻璃药丸导航（mt-6, mx-auto, w-max, rounded-full），展开时 menu 用 massive 玻璃覆盖层（backdrop-blur-3xl bg-black/80）。
