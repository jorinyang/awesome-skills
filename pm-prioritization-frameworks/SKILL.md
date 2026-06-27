---
name: pm-prioritization-frameworks
description: "9种优先级排序框架速查——ICE/RICE/Opportunity Score/Kano/MoSCoW等。公式、使用场景决策表、模板链接。当需要做优先级排序、方案筛选、需求排期、ROI评估时触发。"
triggers:
  - "优先级排序"
  - "怎么排优先级"
  - "优先做哪个"
  - "先做什么"
  - "哪个方案更值得投入"
  - "需求优先级"
  - "功能排期怎么排"
  - "RICE还是ICE"
  - "Kano模型"
  - "MoSCoW"
  - "opportunity score"
  - "优先级框架"
  - "排序框架"
tags: [prioritization, decision-making, frameworks, pm, reference]
category: productivity
related_skills: [double-evolution]
version: 1.0.0
---

# 优先级排序框架速查

> 核心原则：**永远不要让客户设计解决方案。排优先级 = 排问题（机会），不是排功能。**

---

## 快速决策表

| 场景 | 推荐框架 |
|------|---------|
| 个人任务管理 | Eisenhower Matrix |
| 快速分类（<15分钟） | Impact vs Effort |
| 客户问题排序 | **Opportunity Score** ⭐ |
| 想法/创意快速排序 | **ICE** |
| 大团队、需要精细化的想法排序 | **RICE** |
| 需求管理（Must/Should/Could） | **MoSCoW** |
| 理解用户期望 | Kano Model |
| 多因素决策、需要stakeholder buy-in | Weighted Decision Matrix |
| 含不确定性 | Risk vs Reward |

---

## ① Opportunity Score（Dan Olsen, *The Lean Product Playbook*）

**推荐作为客户问题排序的首选框架。**

### 公式

调查客户对每个需求的 **Importance（重要性）** 和 **Satisfaction（满意度）**，归一化到 0–1。

```
Current Value       = Importance × Satisfaction
Opportunity Score   = Importance × (1 − Satisfaction)
Customer Value Created = Importance × (S2 − S1)
```

### 解读

- **高 Importance + 低 Satisfaction = 最高 Opportunity Score = 最佳机会**
- 画 Importance vs Satisfaction 图表 → 左上角象限是最值得投入的区域
- 这个框架**排的是问题，不是功能**

---

## ② ICE 框架

适用于想法/创意/方案的快速排序。综合考虑价值、风险和成本。

```
ICE Score = I × C × E
  I (Impact)    = Opportunity Score × 受影响的客户数
  C (Confidence) = 我们有多确定？(1–10)
  E (Ease)       = 实现有多容易？(1–10)
```

**优点**：简单快速
**缺点**：Impact 合并了"人均价值"和"人数"两个维度

---

## ③ RICE 框架

ICE 的升级版——将 Impact 拆分为 Reach 和 Impact 两个独立维度。

```
RICE Score = (R × I × C) / E
  R (Reach)      = 受影响的客户数量
  I (Impact)     = Opportunity Score（人均价值）
  C (Confidence) = 我们有多确定？(0–100%)
  E (Effort)     = 实现需要多少人月？
```

**适用**：大团队、需要更细粒度的想法排序

---

## ④ MoSCoW

适用于需求/功能管理，源自项目管理领域。

| 级别 | 含义 | 规则 |
|------|------|------|
| **Must have** | 必须有 | 没有它产品不可用 |
| **Should have** | 应该有 | 重要但不是致命 |
| **Could have** | 可以有 | 锦上添花 |
| **Won't have** | 不做 | 明确排除 |

⚠️ MoSCoW 是项目管理工具——**用于 scope 管理，不是战略排序**。不适合做创新优先级决策。

---

## ⑤ Kano Model

用于**理解**用户期望，不是排序工具。

| 类型 | 含义 | 例子 |
|------|------|------|
| **Must-be** | 基本需求 | 没有会极度不满，有也不会增加满意度（如酒店的床） |
| **Performance** | 性能需求 | 越多越满意（如网速） |
| **Attractive** | 魅力需求 | 没有不会不满，有了会惊喜（如酒店免费升级） |
| **Indifferent** | 无差异 | 用户不在乎 |
| **Reverse** | 反向需求 | 有些人喜欢、有些人不喜欢 |

**使用方式**：先识别 Must-be → 保证 Performance → 用 Attractive 做差异化。

---

## ⑥ Impact vs Effort

最直观的 2×2 矩阵。

```
        高 Impact
           │
  ┌────────┼────────┐
  │  Quick Wins  │  Big Bets    │  ← 高 Effort
  ├─────────────┼─────────────┤
  │  Fill-Ins    │  Time Sinks  │  ← 低 Effort
  └─────────────┴─────────────┘
        低 Impact
```

**策略**：优先 Quick Wins（高 Impact + 低 Effort），Big Bets 需要验证后再投入。

---

## ⑦ Eisenhower Matrix

个人任务管理。

```
        紧急
         │
  ┌──────┼──────┐
  │ 立刻做  │ 计划做  │ ← 重要
  ├──────┼──────┤
  │ 委派    │ 删掉    │ ← 不重要
  └──────┴──────┘
         不紧急
```

---

## ⑧ Risk vs Reward

像 Impact vs Effort 但用 Risk 替代 Effort。

- **高风险 + 高回报** = 需要验证的 Big Bets
- **低风险 + 高回报** = 安全的赢面
- **高风险 + 低回报** = 避免
- **低风险 + 低回报** = 只在不费事时考虑

---

## ⑨ Weighted Decision Matrix（加权决策矩阵）

适用于多因素决策、需要 stakeholder buy-in 的场景。

### 步骤

1. 列出评价标准
2. 给每个标准分配权重（总和 = 100%）
3. 每个选项按每个标准打分（1–5）
4. 加权求和：`Score = Σ(Weight_i × Rating_i)`

### 例子：选供应商

| 标准 | 权重 | 供应商A | 供应商B | 供应商C |
|------|:---:|:------:|:------:|:------:|
| 价格 | 30% | 4 | 3 | 5 |
| 质量 | 40% | 5 | 4 | 3 |
| 服务 | 20% | 3 | 5 | 3 |
| 交付速度 | 10% | 4 | 3 | 4 |
| **加权总分** | | **4.3** | 3.9 | 3.7 |

---

## 框架速查表

| 框架 | 最适合 | 核心公式/逻辑 | 排什么 |
|------|--------|-------------|--------|
| **Opportunity Score** ⭐ | 客户问题 | Importance × (1−Satisfaction) | 问题 |
| **ICE** | 想法快速排序 | Impact × Confidence × Ease | 想法 |
| **RICE** | 想法精细化排序 | (Reach × Impact × Conf) / Effort | 想法 |
| **MoSCoW** | 需求管理 | Must/Should/Could/Won't | 需求 |
| **Kano** | 理解期望 | Must-be/Perf/Attr/Indiff/Reverse | 不排序 |
| **Eisenhower** | 个人任务 | Urgent vs Important | 任务 |
| **Impact vs Effort** | 快速分类 | 2×2 矩阵 | 任务 |
| **Risk vs Reward** | 含不确定性 | 2×2 矩阵 | 方案 |
| **Weighted Matrix** | 多因素决策 | Σ(Weight × Score) | 选项 |

---

## 使用原则

1. **先分类，再选框架**：排序对象是问题/想法/需求/任务？
2. **一个团队一个框架**：不要在同一个 backlog 里混用 ICE 和 RICE
3. **不要迷信公式**：框架是辅助思考的工具，不是替代判断
4. **定期回顾**：优先级不是一次排定的——市场和认知在变化
5. **排问题，不排方案**：先确认问题值得解决，再讨论用什么方案

---

## 参考资源

- [Opportunity Score 介绍 (PDF)](https://drive.google.com/file/d/1ENbYPmk1i1AKO7UnfyTuULL5GucTVufW/view)
- [ICE 模板 (Google Sheets)](https://docs.google.com/spreadsheets/d/1LUfnsPolhZgm7X2oij-7EUe0CJT-Dwr-/edit)
- [RICE 模板 (Google Sheets)](https://docs.google.com/spreadsheets/d/1S-6QpyOz5MCrV7B67LUWdZkAzn38Eahv/edit)
- [The Product Management Frameworks Compendium](https://www.productcompass.pm/p/the-product-frameworks-compendium)
- [Kano Model: How to Delight Your Customers](https://www.productcompass.pm/p/kano-model-how-to-delight-your-customers)
