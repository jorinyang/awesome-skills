---
name: opportunity-solution-tree
description: "构建机会方案树——将期望结果映射为机会→方案→实验的四层发现结构。基于Teresa Torres的Continuous Discovery Habits。当需要结构化产品发现、梳理机会空间、避免跳入方案陷阱时触发。"
triggers:
  - "机会方案树"
  - "opportunity solution tree"
  - "OST"
  - "产品发现"
  - "机会空间"
  - "用户需求梳理"
  - "从问题到方案"
  - "发现框架"
  - "continuous discovery"
  - "先诊断再开药"
  - "梳理机会"
  - "Teresa Torres"
tags: [discovery, product-management, opportunity, framework, JTBD]
category: productivity
related_skills: [double-evolution]
version: 1.0.0
---

# 机会方案树 (Opportunity Solution Tree)

> 核心原则：**「永远不要让客户设计解决方案。排优先级 = 排机会（问题），不是排功能。」**
>
> 基于 Teresa Torres *Continuous Discovery Habits* 的发现骨架。

---

## 四层结构

```
                       ┌──────────────────┐
                       │  Desired Outcome  │ ← 一个可衡量的期望结果
                       │  期望结果          │   (来自OKR或产品战略)
                       └────────┬─────────┘
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
           ┌──────────┐  ┌──────────┐  ┌──────────┐
           │Opportunity│  │Opportunity│  │Opportunity│ ← 客户需求/痛点/期望
           │   机会    │  │   机会    │  │   机会    │   从客户视角描述
           └─────┬────┘  └────┬─────┘  └────┬─────┘    「我挣扎于…」「我希望我能…」
                 │            │            │
           ┌─────┼────┐       │       ┌────┼─────┐
           ▼     ▼    ▼       ▼       ▼    ▼     ▼
        [方案] [方案] [方案]                ← 每个机会至少3个方案
           │     │     │                     (PM+Designer+Engineer一起想)
           ▼     ▼     ▼
        [实验] [实验] [实验]                ← 快速便宜的验证
```

---

## 使用步骤

### Step 1: 定义期望结果

一个**单一的、可衡量的**业务或产品结果。放在树的最顶端。

**好的期望结果**：
- 「将 7 天留存率从 25% 提升到 40%」
- 「将客单价提升 15%」
- 「激活率从 12% 提升到 30%」

**不好的期望结果**：
- 「改善用户体验」（不可衡量）
- 「做增长 + 变现」（多个结果混在一起）

### Step 2: 映射机会

从研究数据（访谈/问卷/分析/用户反馈）中提取 3–7 个客户机会。**从客户视角描述**：

| 格式 | 例子 |
|------|------|
| 「我挣扎于…」 | 「我挣扎于找到上次看到的那个功能」 |
| 「我希望我能…」 | 「我希望我能一键导出数据给老板看」 |
| 「如果…就好了」 | 「如果预订前能看到实时价格就好了」 |

**Group 相关机会**：将相似的机会聚拢，减少层级混乱。

### Step 3: 优先级排序

用 **Opportunity Score** 排序机会：

```
Opportunity Score = Importance × (1 − Satisfaction)
（重要性和满意度均归一化到 0–1）
```

聚焦在得分最高的 **Top 2–3** 个机会。

### Step 4: 生成方案

对每个优先机会，**从至少 3 个角度**生成方案：

| 视角 | 关注点 | 典型方案方向 |
|------|--------|-----------|
| **PM**（产品经理） | 业务价值、市场机会 | 「做一个智能搜索 + 历史记录模块」 |
| **Designer**（设计师） | 用户体验、交互流程 | 「在首页增加最近使用功能的快捷入口」 |
| **Engineer**（工程师） | 技术可行性、架构约束 | 「用本地缓存 + 模糊匹配实现搜索」 |

> 「最好的想法往往来自工程师。」— Marty Cagan

### Step 5: 设计实验

对最有希望的方案，设计 1–2 个快速便宜的实验：

| 实验方法 | 说明 | 成本 |
|---------|------|:---:|
| **原型测试** | 高保真原型 + 5个用户访谈 | 低 |
| **假门测试** | 放一个按钮看多少人点击（实际未开发） | 极低 |
| **Wizard of Oz** | 用户以为用产品，实际是人工在背后操作 | 低 |
| **A/B 测试** | 已上线产品的对比测试 | 中 |
| **Concierge** | 人工为少量客户手动提供「服务」 | 低 |

每个实验需包含：**假设 → 方法 → 衡量指标 → 成功阈值**。

---

## 关键原则

1. **一次一个结果**：不要同时追两个期望结果。专注。
2. **机会 ≠ 功能**：机会是什么问题值得解决；功能是怎么解决。永远不要跳过机会直接跳进方案。
3. **对比再选**：每个机会至少 3 个方案。避免"第一个想法"陷阱。
4. **发现不是线性的**：实验结果不佳 → 回到方案层或机会层。方案验证失败 → 果断 Kill。
5. **持续更新**：每周更新树。新访谈、新分析、新实验都在树上反映。

---

## 常见反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| 跳过机会层直接到方案 | 「我们需要一个XX功能」——功能驱动而非问题驱动 | 追问：「这个功能要解决什么客户问题？」 |
| 只有一个方案 | 过早承诺，未探索更好的路径 | 强制每个机会至少 3 个方案 |
| 机会太宽泛 | 「提高用户满意度」——不可操作 | 拆解为具体客户痛点：「搜索不到想找的内容」 |
| 实验太贵 | 完整开发一个功能来「验证」 | 用原型/假门/Wizard of Oz 先探 |
| 树从不更新 | 「我们上季度画过一次」——脱离现实 | 每周review，把新发现映射回来 |

---

## 输出格式

```markdown
# 机会方案树: {产品/项目名}

## 期望结果
单个、可衡量的结果。

## 机会层 (3–7条)
### O1: {机会描述（客户视角）}
- 证据来源: {访谈/数据/反馈}

### O2: ...
...

## 优先排序
| 机会 | Importance | Satisfaction | Opportunity Score | 优先级 |
|------|:----------:|:------------:|:-----------------:|:------:|
| O1 | 0.9 | 0.2 | 0.72 | 1 |
| O2 | 0.8 | 0.4 | 0.48 | 2 |

## Top 2–3 机会的方案与实验
[按机会展开…]

## 实验进度
[当前运行中的实验和结论]
```

## 参考资源

- [The Extended Opportunity Solution Tree](https://www.productcompass.pm/p/the-extended-opportunity-solution-tree)
- [What Is Product Discovery? The Ultimate Guide](https://www.productcompass.pm/p/what-exactly-is-product-discovery)
- [Product Trio: Beyond the Obvious](https://www.productcompass.pm/p/product-trio)
- [Continuous Product Discovery Masterclass (CPDM)](https://www.productcompass.pm/p/cpdm) (video course)
- [Teresa Torres, *Continuous Discovery Habits*](https://www.amazon.com/Continuous-Discovery-Habits-Discover-Products/dp/1736633309/)
