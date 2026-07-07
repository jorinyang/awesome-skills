# Phase 6B 引用过滤标准

> 核心原则：不是所有反向引用都值得补。盲目补全会制造噪音和假耦合。

## 应加引用指引的场景（加）

### 1. 流水线上下游（产出→消费）

下游技能需要上游产出才能工作。下游应声明"我依赖 X 的 Y 产出"。

**信号**：A 生成 [某格式]，B 消费 [某格式]。

```
✅ trip-quote → cost-engine    ← 报价需要成本数据
✅ guide-exec → supply-check   ← 执行单需要物资清单
✅ trip-briefing → customer-view ← 通知书需要客户信息
```

### 2. 增强层→基础层

增强技能声明"我扩展了 X，在 Y 场景下应加载我而非直接用 X"。

**信号**：技能是另一个技能的"增强版"或"补充包"。

```
✅ ljg-elicitation-modes → advanced-elicitation
✅ ljg-writing-voice → humanizer
✅ ljg-infographic-design → baoyu-infographic
```

### 3. 枢纽→辐条

总纲/编排技能声明"我的子技能有哪些，各在什么场景下加载"。

**信号**：技能描述为"编排器"或"总纲"，引用了多个子技能。

```
✅ travel-workflow → trip-quote, trip-briefing, guide-exec ...
```

### 4. 流水线顺序链（A完成后通常做B）

同一工作流的两个步骤有自然先后关系。

**信号**：技能描述中提到"完成 A 后通常进入 B"。

```
✅ editorial-review-structure → editorial-review-prose
✅ benchmark-generator → skill-ab-test
```

## 不应加引用指引的场景（不加）

### 1. 通用工具被调用

一个工具被很多技能调用是正常的——它不需要反向知道所有调用方。

```
❌ skill-evaluator → benchmark-generator  ← 评测工具被调用，不需要反向知道
❌ answer → blue-team                     ← 通用工作流引擎，同理
❌ advanced-elicitation → deep-think      ← 审视方法论，同理
```

### 2. 格式/规范引用

技能引用了输出规范，但规范不需要反向知道谁引用它。

```
❌ zhike-content-output → author-methodology-analysis  ← 内容输出规范
❌ editorial-review-prose → blue-team                  ← 审查规范
```

### 3. 方法论启发

A 借鉴了 B 的思想但运行时不依赖 B 的产出。

```
❌ domain-decompose → deep-think            ← 思维工具，各自独立触发
❌ book-deconstruct → domain-decompose      ← 同为思维工具
```

### 4. 平台工具间的互相引用

lark-* / feishu-* 系列边界已由 CLI 定义，不需要技能层交叉引用。

```
❌ feishu-html → feishu-doc
❌ feishu-table → feishu-wiki
```

## 判断流程

```
1. A 的产出是 B 的运行输入吗？
   YES → 加 downstream 引用
   NO → 继续

2. A 是 B 的增强层吗？
   YES → 加 sibling 引用
   NO → 继续

3. A 是编排多个子技能的枢纽吗？
   YES → 加 downstream 引用（枢纽→子技能）
   NO → 继续

4. A完成后的自然下一步是B吗？
   YES → 加 downstream 引用
   NO → 不加（通用工具/格式/启发/平台工具类引用）
```
