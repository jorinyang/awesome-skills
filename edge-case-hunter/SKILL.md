---
name: edge-case-hunter
description: 穷举遍历所有分支路径和边界条件，只报告未处理的。方法论驱动非直觉驱动——机械式走查每条路径。与对抗性审查正交。触发：边界检查/edge case/穷举测试/边界条件/boundary check/所有情况都覆盖了吗。
version: 1.0.0
author: Hermes Agent (adapted from BMAD bmad-review-edge-case-hunter)
license: MIT
metadata:
  hermes:
    tags: [edge-case, testing, review, boundaries, quality, security]
    related_skills: [github-code-review, systematic-debugging, feishu-html]
---

# Edge Case Hunter — 边界条件穷举审查

## 概述

不判断代码好坏。只做一件事：机械式遍历所有分支路径和边界条件，报告哪些路径缺少处理。

**你是纯路径追踪器。** 从不评论代码好坏；只列出缺失的处理逻辑。

## 触发条件

- "检查边界条件"
- "edge case 都覆盖了吗"
- "穷举一下所有情况"
- "有没有遗漏的分支"
- "boundary check"
- "测试够不够全"

## 输入

- **content**（必需）— 待审查的内容：diff / 完整文件 / 函数
- **also_consider**（可选）— 审查过程中额外需要考虑的方面

## 审查范围

- 有 diff → 只扫描 diff hunks 中可到达的边界，只报告 diff 中缺少显式 guard 的
- 无 diff（完整文件/函数）→ 整个内容为范围
- 忽略代码库其余部分（除非内容显式引用外部函数）

---

## 执行流程

### Step 1: 接收内容

- 从输入加载待审查内容
- 空内容 → 返回 `[{"location":"N/A","trigger_condition":"输入为空","guard_snippet":"提供有效内容","potential_consequence":"审查跳过"}]`
- 识别内容类型（diff / 完整文件 / 函数）

### Step 2: 穷举路径分析

**走查每一条分支路径和边界条件——只报告未处理的。**

分析维度：

| 维度 | 检查项 |
|------|--------|
| **控制流** | 条件分支(缺少else/default)、循环(off-by-one)、错误处理(缺catch)、提前返回(无后续清理) |
| **数据边界** | null/undefined/空字符串/空数组、零值/负数/极大值、类型边界(整数溢出/浮点精度)、编码边界(特殊字符/超长输入) |
| **状态边界** | 初始状态、过渡状态、终态、并发状态竞争 |
| **时间边界** | 超时、时钟回拨、操作顺序颠倒 |
| **资源边界** | 文件不存在/无权限/被占用、网络断开/慢速、内存耗尽 |
| **用户边界** | 无输入、格式错误、恶意输入、权限不足 |
| **隐式边界** | 隐式类型转换、API版本变更、配置缺失 |

**对每条路径**：确定内容是否处理了它 → 只收集未处理的 → 丢弃已处理的。

### Step 3: 完整性验证

- 重访 Step 2 的每个边界类
- 补充新发现的未处理路径
- 确认已丢弃的确实是已处理的

### Step 4: 输出发现

**输出 JSON 数组，每个发现包含 4 个字段：**

```json
[{
  "location": "file:start-end (or file:line, or file:hunk)",
  "trigger_condition": "触发条件（≤15词中文）",
  "guard_snippet": "关闭此缺口的最小代码草图（单行，无实际换行/无未转义引号）",
  "potential_consequence": "可能发生的后果（≤15词中文）"
}]
```

- 无额外文字、无解释、无 markdown 包装
- 空数组 `[]` 表示未发现未处理路径（这是有效结果）
- 如果 also_consider 已提供，在分析中纳入这些方面

---

## 与 Hermes 技能的集成

### 被 github-code-review 调用

```
在代码审查中增加 Edge Case Hunter 层：
加载 edge-case-hunter，对 PR diff 运行穷举路径分析，
将 JSON 发现合并到审查报告的 Critical/Warnings 中。
```

### 被 feishu-html 阶段五调用

```
部署前：
加载 edge-case-hunter 检查 HTML 中所有交互路径是否覆盖了边界条件：
- 空状态/加载中/错误/权限不足 是否都有处理
- 所有按钮是否有 hover/active/focus/disabled 态
- 触控区域是否 ≥44×44px
```

### 被 systematic-debugging Phase 1 调用

```
在确定根因后：
加载 edge-case-hunter 穷举该代码区域的所有边界，
确认修复方案覆盖了所有边界而不仅是当前触发的那一个。
```

---

## 约束

- **不做质量判断** — 不评论代码好坏，只报告缺失
- **不编造发现** — 如果路径被处理了就说处理了，不硬找问题
- **不解释处理了的问题** — 丢弃静默，报告简洁
- 不输出 markdown — 纯 JSON

## 常见陷阱

1. **找问题而不是找缺失** → 这个技能不找问题(bugs)，只找缺失(missing guards)
2. **过度解释** → 输出必须是最小可行的 JSON
3. **忽略 also_consider** → 如果提供了，必须纳入分析
4. **把已处理的标记为缺失** → 误报不如漏报

## 验证清单

- [ ] 内容非空且可解码
- [ ] 走查了所有控制流分支
- [ ] 走查了所有数据边界
- [ ] 只报告了未处理路径（已处理静默丢弃）
- [ ] 输出为有效 JSON 数组（含4字段）
- [ ] 无 markdown 包装、无额外文字
