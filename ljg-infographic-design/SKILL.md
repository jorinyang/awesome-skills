---
name: ljg-infographic-design
description: baoyu-infographic 增强层——注入 ljg-card 的密度×结构×情绪判断框架。在信息图设计前自动进行内容诊断。触发：做信息图/信息图/可视化/infographic时自动伴随 baoyu-infographic 加载。
version: 1.0.0
source: 吸收自 lijigang/ljg-skills (ljg-card)，作为 baoyu-infographic 的设计判断增强层
metadata:
  hermes:
    tags: [infographic, design, methodology, companion]
      related_skills: [double-evolution]
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

### 触发场景矩阵

#### 技术信息图
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 架构图 | 用户要做系统架构可视化 | "把这个微服务架构做成信息图" |
| 技术对比 | 用户要对比技术方案 | "把PostgreSQL和MongoDB对比做成信息图" |
| 数据报告 | 用户有性能/监控数据要可视化 | "把Q3的性能数据做成信息图" |
| AI/ML流水线 | 用户要可视化ML流程 | "把训练pipeline做成信息图" |
| 技术趋势 | 用户要可视化技术演进 | "把Web框架10年演进做成信息图" |

#### 商业/营销信息图
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 商业模型 | 用户要可视化商业模式 | "把我们的商业模式做成信息图" |
| 市场数据 | 用户要可视化市场分析 | "把这季度的市场调研做成信息图" |
| 竞品对比 | 用户要对比竞品 | "把我们和3家竞品对比做成信息图" |
| 增长漏斗 | 用户要可视化转化流程 | "把用户增长漏斗做成信息图" |
| 客户旅程 | 用户要可视化客户体验 | "把客户从发现到续费的旅程做成信息图" |

#### 教育/培训信息图
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 概念解释 | 用户要可视化解释复杂概念 | "把CAP定理做成信息图" |
| 流程教程 | 用户要可视化操作流程 | "把Git工作流做成信息图" |
| 知识总结 | 用户要总结大量知识点 | "把这门课的核心知识点做成信息图" |
| 历史/时间线 | 用户要可视化时间线 | "把AI发展史做成信息图" |

#### 内容/创意信息图
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 文章配图 | 用户要为文章做信息图 | "这篇博客的配图做一张信息图" |
| 社交传播 | 用户要做可传播的视觉内容 | "把核心观点做成一张能社交传播的图" |
| 报告封面 | 用户要做报告首页可视化 | "这份报告的executive summary做成信息图" |
| 演讲配图 | 用户要做演讲用的视觉辅助 | "这个演讲的核心论点做成一张图" |

### 自动伴随加载

当 `baoyu-infographic` 被触发时（用户说"信息图/可视化/infographic/做成图"），本技能应同时加载，在其 Step 3 之前执行内容诊断。

### 手动触发关键词
信息图设计判断、信息图、可视化、infographic、做成图、做成卡片、做成海报、视觉笔记、sketchnote、数据可视化、架构可视化

### 不触发
- 纯装饰性图片（"帮我做一张配图"不涉及数据/信息结构）→ 用图像生成工具
- 已有明确layout/style指定的信息图（"用bento-grid+crafthandmade做"）→ 用户已指定，不需要诊断
- 标准图表的简单美化（"把这个折线图弄好看点"）→ 不需要三维诊断
- SVG架构图/架构图（用户明确说"画架构图"）→ 用architecture-diagram
