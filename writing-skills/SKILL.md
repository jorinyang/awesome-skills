---
name: writing-skills
description: 创建新技能、编辑已有技能、或在部署前验证技能有效性时使用——将 TDD 方法论应用于 Agent 技能文档工程。触发：创建技能/写skill/技能测试/skill验证/技能质量/技能反模式
version: 1.0.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [skill-engineering, tdd, quality, methodology, meta-skill]
    related_skills: [test-driven-development, skill-evaluator, benchmark-generator, darwin-skill, hermes-agent-skill-authoring]
  source: 吸收自 https://github.com/obra/superpowers (v6.1.1)
---

# Writing Skills — TDD 驱动的技能工程

> **吸收自**: [obra/superpowers](https://github.com/obra/superpowers) v6.1.1，Jesse Vincent / Prime Radiant
>
> **核心洞察**: 写技能 = 对过程文档执行 TDD。压力测试驱动 → 基线失败 → 写技能 → 验证合规 → 封堵漏洞。

## Overview

**Writing skills IS Test-Driven Development applied to process documentation.**

你写测试用例（带子代理的压力场景），看它们失败（基线行为），写技能（文档），看测试通过（Agent 遵守），然后重构（封堵漏洞）。

**Core principle:** If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.

**REQUIRED BACKGROUND:** 必须先理解 `test-driven-development` 技能的 RED-GREEN-REFACTOR 循环。本技能将 TDD 适配到文档领域。

## What is a Skill?

A **skill** 是可复用技术、模式、工具的参考指南。技能帮助未来的 Agent 找到并应用有效方法。

**Skills are:** 可复用技术、模式、工具、参考指南

**Skills are NOT:** 关于"你怎么解决过一次问题"的叙事

## TDD Mapping for Skills

| TDD Concept | Skill Creation |
|-------------|----------------|
| **Test case** | 带子代理的压力场景 |
| **Production code** | 技能文档 (SKILL.md) |
| **Test fails (RED)** | Agent 在没有技能时违反规则（基线） |
| **Test passes (GREEN)** | Agent 在有技能时遵守规则 |
| **Refactor** | 封堵漏洞，保持合规 |
| **Write test first** | 写技能前先跑基线场景 |
| **Watch it fail** | 记录 Agent 使用的确切合理化借口 |
| **Minimal code** | 写技能针对那些具体的违规 |
| **Watch it pass** | 验证 Agent 现在遵守 |
| **Refactor cycle** | 发现新合理化 → 封堵 → 重新验证 |

## When to Create a Skill

**Create when:**
- 技术/方法对你来说不是直觉性的
- 你会跨项目再次引用
- 模式广泛适用（非项目特定）
- 其他人会受益
- 你发现自己反复纠正 Agent 同一个错误

**Don't create for:**
- 一次性解决方案
- 已被广泛文档化的标准实践
- 项目特定约定（放入项目 instructions 文件）
- 机械性约束（如果可用 regex/validation 自动化，自动化它——文档留给判断类决策）

## Skill Types

### Technique（技法）
有步骤的具体方法（condition-based-waiting、root-cause-tracing）

### Pattern（模式）
思考问题的方式（flatten-with-flags、test-invariants）

### Reference（参考）
API 文档、语法指南、工具文档

## Directory Structure

```
skills/
  skill-name/
    SKILL.md              # 主参考文件（必需）
    references/           # 参考文件（方法论、模板、案例）
    scripts/              # 可执行脚本
    templates/            # 输出模板
```

**Hermes 技能结构**（比 superpowers 更丰富）：
- `references/` 放重参考（100+ 行）、方法论框架
- `scripts/` 放可执行工具
- `templates/` 放输出模板
- 原则、概念、短代码模式保持内联

## SKILL.md Structure

**Frontmatter (YAML):**
- 必需字段: `name`, `description`
- `name`: 仅用字母、数字、连字符
- `description`: 第三人称，描述**何时使用**（非技能做什么）
  - 以 "Use when..." 或 "当...时使用" 开头
  - 包含具体触发条件、症状、场景
  - **绝不总结技能的工作流**（见 SDO 章节说明）

```markdown
---
name: skill-name-with-hyphens
description: 当 [具体触发条件和症状] 时使用
version: 1.0.0
metadata:
  hermes:
    tags: [tag1, tag2]
    related_skills: [skill-a, skill-b]
---

# Skill Name

## Overview
这是什么？1-2 句核心原则。

## When to Use
[仅在决策不明显时使用小型内联流程图]

触发条件列表
何时不使用

## Core Pattern (for techniques/patterns)
Before/after 代码对比

## Quick Reference
常见操作的速查表

## Implementation
简单模式内联代码；重参考或可复用工具外链文件

## Common Mistakes
什么会出错 + 修复方法

## Real-World Impact (optional)
具体结果
```

## Skill Discovery Optimization (SDO)

**Critical for discovery:** 未来的 Agent 需要找到你的技能。

### 1. Rich Description Field

**Purpose:** Agent 读 description 来决定是否为当前任务加载此技能。

**Format:** 以触发条件开头，不总结工作流。

**CRITICAL: Description = When to Use, NOT What the Skill Does**

description 应该**只**描述触发条件。绝不在 description 中总结技能的工作流。

**Why:** 测试发现，当 description 总结了工作流时，Agent 可能照着 description 做而**不读完整技能内容**。一个 description 写"在任务间做代码审查"导致 Agent 只做一次审查，而技能流程图明确写了两次审查。

```yaml
# ❌ BAD: 总结了工作流 - Agent 可能照此执行而不读技能
description: 执行计划时分派子代理，在任务间做代码审查

# ❌ BAD: 过程细节太多
description: TDD 时用 - 先写测试，看它失败，写最少代码，重构

# ✅ GOOD: 只有触发条件，无工作流摘要
description: 当执行含独立任务的实现计划时使用，在当前会话中

# ✅ GOOD: 仅触发条件
description: 当实现任何功能或 bugfix 时，在写实现代码之前使用
```

### 2. Keyword Coverage

使用 Agent 会搜索的词：
- 错误消息: "Hook timed out", "ENOTEMPTY", "race condition"
- 症状: "flaky", "hanging", "zombie", "污染"
- 同义词: "timeout/hang/freeze", "cleanup/teardown"
- 工具: 实际命令、库名、文件类型
- **中文触发词**: 必须包含 ≥3 个中文触发场景

### 3. Descriptive Naming

**动词优先，主动语态:**
- ✅ `creating-skills` 不是 `skill-creation`
- ✅ `condition-based-waiting` 不是 `async-test-helpers`

**以你做的动作或核心洞察命名:**
- ✅ `condition-based-waiting` > `async-test-helpers`
- ✅ `root-cause-tracing` > `debugging-techniques`

**-ing 形式适合流程:**
- `creating-skills`, `testing-skills`, `debugging-with-logs`

### 4. Token Efficiency

**Problem:** 频繁加载的技能进入每次对话。每个 token 都算数。

**Move details to tool help:**
```bash
# ❌ BAD: 在 SKILL.md 中记录所有 flags
search-conversations 支持 --text, --both, --after DATE, --before DATE, --limit N

# ✅ GOOD: 引用 --help
search-conversations 支持多种模式和过滤。运行 --help 查看详情。
```

**Use cross-references:**
```markdown
# ❌ BAD: 重复工作流细节
搜索时，分派子代理使用模板...
[20 行重复指令]

# ✅ GOOD: 引用其他技能
始终使用子代理（节省 50-100x 上下文）。REQUIRED: 使用 [other-skill-name] 获取工作流。
```

**Eliminate redundancy:**
- 不重复交叉引用的技能内容
- 不解释命令本身就清楚的
- 不包含同一模式的多个示例

### 5. Cross-Referencing Other Skills

使用技能名，加显式要求标记:
- ✅ Good: `**REQUIRED SUB-SKILL:** 使用 test-driven-development`
- ✅ Good: `**REQUIRED BACKGROUND:** 必须理解 systematic-debugging`
- ❌ Bad: `参见 skills/testing/test-driven-development`（不清楚是否必需）
- ❌ Bad: `@skills/testing/test-driven-development/SKILL.md`（强制加载、燃烧上下文）

## Flowchart Usage

**仅在以下情况使用流程图:**
- 非显而易见的决策点
- 可能过早停止的流程循环
- "何时用 A vs B"决策

**绝不使用流程图:**
- 参考材料 → 表格、列表
- 代码示例 → Markdown 块
- 线性指令 → 编号列表
- 无语义含义的标签 (step1, helper2)

## Code Examples

**一个优秀的示例胜过许多平庸的示例**

选择最相关的语言:
- 测试技术 → TypeScript/JavaScript
- 系统调试 → Shell/Python
- 数据处理 → Python

**Good example:**
- 完整且可运行
- 良好注释解释 WHY
- 来自真实场景
- 清晰展示模式
- 可直接适配

**Don't:**
- 实现 5+ 种语言
- 创建填空模板
- 写人为构建的示例

## The Iron Law

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

这适用于新技能**和**对已有技能的编辑。

写技能之前没有测试？删除。重新开始。
编辑技能没有测试？同样的违规。

**No exceptions:**
- 不是对"简单添加"
- 不是对"只是加一节"
- 不是对"文档更新"
- 不保留未测试的修改作为"参考"
- 不在跑测试时"适配"
- 删除就是删除

**REQUIRED BACKGROUND:** `test-driven-development` 技能解释了为什么这很重要。

## Match the Form to the Failure

写指导前，分类基线失败。一种失败类型有效的形式可能在另一种上适得其反。

| 基线失败 | 正确形式 | 错误形式 |
|---|---|---|
| 压力下跳过/违反规则（知道更好，还是做了） | 禁令 + 合理化表格 + Red Flags | 软指导 ("prefer...", "consider...") |
| 合规但输出形状不对（臃肿 prompt、埋没结论、重述 spec） | 正面配方或合约：陈述输出 IS——组成部分、顺序 | 禁令列表 ("don't restate", "never narrate") |
| 从已产出内容中遗漏必需元素 | 结构性：他们填的模板中的 REQUIRED 字段 | 模板附近的散文提醒 |
| 行为应依条件而定 | 基于可观察谓词的条件 ("if the brief exists, reference it") | 无条件规则 + 豁免条款 |

## Bulletproofing Skills Against Rationalization

执行纪律的技能需要抵抗合理化。Agent 在压力下很聪明，会找漏洞。

### Close Every Loophole Explicitly

不只声明规则——禁止具体的变通方法:

<Bad>
```markdown
在测试前写了代码？删除它。
```
</Bad>

<Good>
```markdown
在测试前写了代码？删除它。重新开始。

**No exceptions:**
- 不作为"参考"保留
- 不在写测试时"适配"
- 不看它
- 删除就是删除
```
</Good>

### Address "Spirit vs Letter" Arguments

早期添加基本原则:

```markdown
**Violating the letter of the rules is violating the spirit of the rules.**
```

这切断了整类"我遵循精神"的合理化。

### Build Rationalization Table

从基线测试中捕获合理化。Agent 制造的每个借口都进表格:

```markdown
| Excuse | Reality |
|--------|---------|
| "太简单不需要测试" | 简单代码也会坏。测试只要 30 秒。 |
| "我之后会测" | 之后通过的测试什么也证明不了。 |
| "之后的测试达到同样目标" | 之后测 = "这个做什么？" 先测 = "这个应该做什么？" |
```

### Create Red Flags List

让 Agent 在合理化时自我检查:

```markdown
## Red Flags - STOP and Start Over

- 代码在测试之前
- "我已经手动测过了"
- "之后的测试达到同样目的"
- "这是关于精神不是仪式"
- "这不一样因为..."

**所有这些都意味着：删除代码。用 TDD 重新开始。**
```

## RED-GREEN-REFACTOR for Skills

### RED: Write Failing Test (Baseline)

在没有技能的情况下跑压力场景。记录确切行为:
- Agent 做了什么选择？
- 使用了什么合理化（逐字）？
- 哪些压力触发了违规？

这是"看测试失败"——必须看到 Agent 在没有技能时自然做什么。

### GREEN: Write Minimal Skill

写针对那些具体合理化的技能。不为假设情况添加额外内容。

用同样的场景**带技能**跑。Agent 现在应该合规。

### REFACTOR: Close Loopholes

Agent 找到了新合理化？添加显式反击。重新测试直到无懈可击。

### Micro-Test Wording Before Full Scenarios

完整的压力场景跑是最终门禁，但每次迭代慢且贵。先用微测试验证措辞:

1. **每次调用一个全新上下文样本**——原始 API 调用，或单次子代理。System prompt = 指导将存在的真实上下文；User message = 诱惑失败的任务。
2. **始终包含无指导对照组。** 如果对照组不展现失败，就没有什么要修复的——停止。
3. **每个变体 5+ 次重复。** 单样本会说谎。
4. **手动读取每个标记匹配。** 模板回显和被引用的反例会伪装成命中；自动化计数会高估失败和成功。
5. **方差是度量。** 指导落地后，重复应收敛到同一形状。五次重复五种不同解释 = 措辞不具备约束力——在加词之前收紧形式。

### Hermes 环境的测试方法

在 Hermes 中测试技能的特殊考量:

1. **多模型测试**: 同一技能在 DeepSeek/Claude/GPT 下表现不同。至少测试 2 个模型。
2. **Cron 触发测试**: 如果技能有自动触发逻辑，验证 cron 调度下的行为。
3. **跨 Profile 测试**: 如果技能引用其他技能，验证依赖链在干净 profile 中可用。
4. **Token 约束测试**: 验证技能在上下文窗口压力下仍然完整触发。

## Skill Creation Checklist (TDD Adapted)

**IMPORTANT: 为以下每一项创建 todo。**

**RED Phase - Write Failing Test:**
- [ ] 创建压力场景（纪律技能 3+ 组合压力）
- [ ] 不带技能跑场景 - 逐字记录基线行为
- [ ] 识别失败/合理化模式

**GREEN Phase - Write Minimal Skill:**
- [ ] 名称仅用字母、数字、连字符
- [ ] YAML frontmatter 含必需 `name` 和 `description`（≤1024 字符）
- [ ] Description 以触发条件开头，含具体触发/症状
- [ ] Description 用第三人称
- [ ] 全文分布关键词（错误、症状、工具）
- [ ] 含核心原则的清晰 overview
- [ ] 针对 RED 阶段发现的具体基线失败
- [ ] 指导形式匹配失败类型（见 Match the Form to the Failure）
- [ ] 代码内联或链接到单独文件
- [ ] 一个优秀示例（不多语言）
- [ ] 带技能跑场景 - 验证 Agent 现在合规

**REFACTOR Phase - Close Loopholes:**
- [ ] 从测试中识别新合理化
- [ ] 添加显式反击（如纪律技能）
- [ ] 从所有测试迭代构建合理化表格
- [ ] 创建 Red Flags 列表
- [ ] 重新测试直到无懈可击

**Quality Checks:**
- [ ] 仅在决策不明显时使用小流程图
- [ ] 速查表
- [ ] 常见错误章节
- [ ] 无叙事性讲故事
- [ ] 支持文件仅用于工具或重参考

**Deployment (Hermes):**
- [ ] 通过 `skill_manage(action='create')` 注册技能
- [ ] 更新 related_skills 引用网络
- [ ] 同步到 GitHub awesome-skills 仓库
- [ ] 如适用，更新 README 索引

## Anti-Patterns

### ❌ Narrative Example
"在 2025-10-03 的会话中，我们发现空 projectDir 导致..."
**Why bad:** 太具体，不可复用

### ❌ Multi-Language Dilution
example-js.js, example-py.py, example-go.go
**Why bad:** 平庸质量，维护负担

### ❌ Code in Flowcharts
```dot
step1 [label="import fs"];
step2 [label="read file"];
```
**Why bad:** 无法复制粘贴，难读

### ❌ Generic Labels
helper1, helper2, step3, pattern4
**Why bad:** 标签应有语义含义

### ❌ 跳过基线测试
"我知道 Agent 会做什么"
**Why bad:** 你其实不知道。Agent 在不同模型下表现不同。

### ❌ Hermes 特有反模式
- 用 `skill_manage(action='edit')` 做小修改（应该用 `patch`）
- 不更新 metadata.related_skills 就创建技能（孤立技能 = 死技能）
- 不测试跨模型行为就部署（DeepSeek vs Claude 触发逻辑差异显著）

## The Bottom Line

**Creating skills IS TDD for process documentation.**

Same Iron Law: No skill without failing test first.
Same cycle: RED (baseline) → GREEN (write skill) → REFACTOR (close loopholes).
Same benefits: Better quality, fewer surprises, bulletproof results.

如果你对代码遵循 TDD，对技能也遵循它。这是同一套纪律应用于文档。

## 与 Hermes 原生技能的关系

| 技能 | 关系 | 使用方式 |
|------|:---:|---------|
| `test-driven-development` | upstream | RED-GREEN-REFACTOR 基础方法论 |
| `skill-evaluator` | downstream | 创建后的三维评测 |
| `benchmark-generator` | downstream | 自动生成技能的 routing 测试集 |
| `darwin-skill` | downstream | 创建后的 L1 静态检查 |
| `hermes-agent-skill-authoring` | sibling | Hermes 特定语法和规范 |

> 吸收自: https://github.com/obra/superpowers (v6.1.1)
