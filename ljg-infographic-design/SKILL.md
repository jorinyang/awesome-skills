---
name: ljg-infographic-design
description: baoyu-infographic 增强层——注入 ljg-card 的密度×结构×情绪判断框架。在信息图设计前自动进行内容诊断。触发：做信息图/信息图/可视化/infographic时自动伴随 baoyu-infographic 加载。
version: 1.0.0
source: 吸收自 lijigang/ljg-skills (ljg-card)，作为 baoyu-infographic 的设计判断增强层
metadata:
  hermes:
    tags: [infographic, design, methodology, companion]
    category: methodology
    companion_to: [baoyu-infographic]
    co_load_with: [baoyu-infographic]
---

# baoyu-infographic 设计判断增强层

本技能为 `baoyu-infographic` 注入 ljg-card 的密度×结构×情绪三维判断框架。当 baoyu-infographic 被加载时，本技能应同时加载。

**核心信条**：样式为思想而服务。不存在"默认布局"——每一张信息图的视觉形式，都从这个思想的形状中生长出来。

## 密度判断（决定画面的呼吸节奏）

在做任何布局和风格选择之前，先判断内容密度：

| 密度 | 核心内容量 | 画面特征 | 布局建议 |
|------|-----------|---------|---------|
| **稀 (Sparse)** | ≤ 50 字可说清 | 一个巨大元素统治画面。留白 ≥ 60%。震撼来自克制 | hub-spoke / iceberg / single-point |
| **中 (Medium)** | 50-200 字 | 有结构的布局。2-3 个主要区块。留白 30-50% | bento-grid / binary-comparison / funnel |
| **密 (Dense)** | 200+ 字 | 多区块密集排布。标注、网格、分层。实验室手册感 | dense-modules / dashboard / periodic-table |

## 结构判断（决定画面的几何形状）

| 结构 | 信号 | 对应 layout | 视觉几何 |
|------|------|------------|---------|
| 单点 | 一个核心概念 | hub-spoke, iceberg | 一个锚点占据重心，其余退后 |
| 对比 | A vs B、旧 vs 新 | binary-comparison | 分裂、对立、两极 |
| 层级 | 底层支撑上层 | hierarchical-layers, tree-branching | 金字塔、阶梯、嵌套 |
| 流程 | 先后顺序 | linear-progression, winding-roadmap | 纵向瀑布、时间轴、管道 |
| 辐射 | 核心 + 衍生 | hub-spoke, circular-flow | 中心放射 |
| 并列 | 多个并行概念 | bento-grid, comparison-matrix | 非对称网格（禁止等分） |
| 循环 | 周期往复 | circular-flow | 环形回路 |

## 情绪判断（决定画面的温度和风格）

| 情绪 | 信号词 | 对应 style | 排版风格 |
|------|--------|-----------|---------|
| 沉思的 | 哲学、思考、内省 | aged-academia, morandi-journal | 大量留白，serif 主导，低对比 |
| 锐利的 | 颠覆、突破、挑战 | cyberpunk-neon, bold-graphic | 强对比，大字，弹点强调 |
| 温暖的 | 生活、自然、人情 | craft-handmade, storybook-watercolor | 绿色为主，圆润布局，手写感 |
| 技术的 | 数据、架构、原理 | technical-schematic, pop-laboratory | mono 标注，网格底纹，数据密集 |
| 教育的 | 教程、入门、讲解 | chalkboard, hand-drawn-edu | 清晰层级，友好图标 |
| 商业的 | 汇报、方案、提案 | corporate-memphis, ikea-manual | 专业克制，数据驱动 |

## 工作流注入

在 baoyu-infographic 的 Step 3（推荐组合）之前，插入：

### Step 2.5: 内容诊断（ljg-infographic-design）

输出诊断结论：
```
密度：[稀/中/密]
结构：[单点/对比/层级/流程/辐射/并列/循环]
情绪：[沉思/锐利/温暖/技术/教育/商业]
```

然后基于这个诊断来推荐 layout × style 组合，而非仅仅基于关键词匹配。

### 核心原则

- **密度决定呼吸**：稀就大胆留白，密就组织网格，不硬塞
- **结构决定形状**：不要把所有内容塞进 bento-grid。内容是对比就用对立布局，内容是流程就用时间轴
- **情绪决定温度**：同一份数据，沉思用低对比 serif，锐利用高对比 sans + 强调色

## 加载规则

本技能应与 `baoyu-infographic` **同时加载**。当用户触发"信息图/可视化/infographic"时，同时加载 baoyu-infographic + ljg-infographic-design。
