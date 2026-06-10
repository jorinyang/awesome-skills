---
name: writing-plans
description: "Write implementation plans: bite-sized tasks, paths, code."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, design, implementation, workflow, documentation]
    related_skills: [subagent-driven-development, test-driven-development, requesting-code-review]
---

# Writing Implementation Plans

## Overview

Write comprehensive implementation plans assuming the implementer has zero context for the codebase and questionable taste. Document everything they need: which files to touch, complete code, testing commands, docs to check, how to verify. Give them bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume the implementer is a skilled developer but knows almost nothing about the toolset or problem domain. Assume they don't know good test design very well.

**Core principle:** A good plan makes implementation obvious. If someone has to guess, the plan is incomplete.

## When to Use

**Always use before:**
- Implementing multi-step features
- Breaking down complex requirements
- Delegating to subagents via subagent-driven-development

**Don't skip when:**
- Feature seems simple (assumptions cause bugs)
- You plan to implement it yourself (future you needs guidance)
- Working alone (documentation matters)

## Bite-Sized Task Granularity

**Each task = 2-5 minutes of focused work.**

Every step is one action:
- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

**Too big:**
```markdown
### Task 1: Build authentication system
[50 lines of code across 5 files]
```

**Right size:**
```markdown
### Task 1: Create User model with email field
[10 lines, 1 file]

### Task 2: Add password hash field to User
[8 lines, 1 file]

### Task 3: Create password hashing utility
[15 lines, 1 file]
```

## Plan Document Structure

### Header (Required)

Every plan MUST start with:

```markdown
# [Feature Name] Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

### Task Structure

Each task follows this format:

````markdown
### Task N: [Descriptive Name]

**Objective:** What this task accomplishes (one sentence)

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67` (line numbers if known)
- Test: `tests/path/to/test_file.py`

**Step 1: Write failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify failure**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: FAIL — "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify pass**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## Writing Process

### Step 1: Understand Requirements

Read and understand:
- Feature requirements
- Design documents or user description
- Acceptance criteria
- Constraints

### Step 2: Explore the Codebase

Use Hermes tools to understand the project:

```python
# Understand project structure
search_files("*.py", target="files", path="src/")

# Look at similar features
search_files("similar_pattern", path="src/", file_glob="*.py")

# Check existing tests
search_files("*.py", target="files", path="tests/")

# Read key files
read_file("src/app.py")
```

### Step 3: Design Approach

Decide:
- Architecture pattern
- File organization
- Dependencies needed
- Testing strategy

### Step 4: Write Tasks

Create tasks in order:
1. Setup/infrastructure
2. Core functionality (TDD for each)
3. Edge cases
4. Integration
5. Cleanup/documentation

### Step 5: Add Complete Details

For each task, include:
- **Exact file paths** (not "the config file" but `src/config/settings.py`)
- **Complete code examples** (not "add validation" but the actual code)
- **Exact commands** with expected output
- **Verification steps** that prove the task works

### Step 6: Review the Plan

Check:
- [ ] Tasks are sequential and logical
- [ ] Each task is bite-sized (2-5 min)
- [ ] File paths are exact
- [ ] Code examples are complete (copy-pasteable)
- [ ] Commands are exact with expected output
- [ ] No missing context
- [ ] DRY, YAGNI, TDD principles applied

### Step 7: Save the Plan

```bash
mkdir -p docs/plans
# Save plan to docs/plans/YYYY-MM-DD-feature-name.md
git add docs/plans/
git commit -m "docs: add implementation plan for [feature]"
```

---

## 活文档章节（Living Document）

> 借鉴 execplan 的 Living Document 方法论——计划不是写完就扔的，而是实施过程中持续更新的单一真源。

每个计划必须包含以下四个强制章节，并在实施过程中持续更新：

### Progress（进度追踪，强制）

用 checklist 记录每一步的完成状态，带时间戳 (UTC+8)：

```markdown
## Progress

- [x] (2026-06-05 14:00) Task 1: Create User model — 3/3 tests passing, committed.
- [ ] (2026-06-05 14:15) Task 2: Add password hashing — in progress.
- [ ] Task 3: Create login endpoint — waiting on Task 2.

使用时间戳衡量进度节奏。每个停止点必须记录，即使需要拆分已完成和未完成部分。
```

### Decision Log（决策日志，强制）

记录实施过程中每次改变方向或做出关键选择的决策：

```markdown
## Decision Log

### D-001: Password hashing 选用 bcrypt 而非 argon2
- 决策：使用 bcrypt 作为密码哈希算法
- 理由：项目已有 bcrypt 依赖，argon2 需要额外 C 编译，增加 CI 复杂度
- 替代方案：argon2（放弃原因：需要 gcc + libargon2-dev，CI 环境不兼容）
- 日期/作者：2026-06-05 / 月夜
```

### Surprises & Discoveries（意外发现，强制）

记录实施中发现的非预期行为、bug、性能 tradeoff：

```markdown
## Surprises & Discoveries

- 发现：SQLite 在并发 > 50 连接时写入性能骤降
  证据：`ab -n 1000 -c 100` 测试中 p99 延迟从 12ms 升到 480ms
  影响：需要为 Task 5 (API endpoint) 增加连接池限制
```

### Outcomes & Retrospective（成果回顾，完成后填写）

全部任务完成后，对照原计划总结：

```markdown
## Outcomes & Retrospective

### 对照原始目标
| 目标 | 实际达成 | 差距 |
|------|---------|------|
| 用户可用邮箱+密码注册 | ✅ 完成 | — |
| 注册响应时间 < 200ms | ⚠️ p95 = 230ms | 需后续优化 |

### 经验教训
1. bcrypt cost factor 12 在 CI 环境耗时 800ms，降到 10 后降至 120ms
2. Task 4 (email verification) 的实现比预期复杂 3x，应在 spike 中先验证

### 可复用资产
- Decision Log D-001（bcrypt vs argon2）→ 未来认证系统选型参考
```

---

## 增强的质量标准

### 自包含检查 (Self-Contained)

> 借鉴 execplan 的 Self-Contained 标准——随机抽取一个 Task，假设自己是"从没见过这个项目的新手"，能否仅看该 Task 的描述独立完成？

在 Review the Plan (Step 6) 中新增：

- [ ] **自包含检查**：随机抽取 1 个 Task，不看上下文能否独立执行？缺少信息则补充。

### 可观测验收标准 (Observable Outcomes)

> 借鉴 execplan 的 Observable Outcomes 方法论。

每个 Task 的验证步骤必须采用「条件 → 操作 → 预期结果」三元格式：

```markdown
**Step 4: Run test to verify pass**
条件：bcrypt 依赖已安装
操作：`pytest tests/test_auth.py::test_password_hash -v`
预期结果：PASS — 4 tests passed, bcrypt hash 验证通过
```

### 幂等性标注 (Idempotence)

> 借鉴 execplan 的 Idempotence 方法论。

每个 Task 必须标注是否可安全重复执行：

```markdown
### Task N: [Name]
**幂等性**：✅ 可重复（创建前检查是否已存在）/ ⚠️ 不可重复（发送通知类操作，重复执行会重复通知）
```

---

## Principles

### DRY (Don't Repeat Yourself)

**Bad:** Copy-paste validation in 3 places
**Good:** Extract validation function, use everywhere

### YAGNI (You Aren't Gonna Need It)

**Bad:** Add "flexibility" for future requirements
**Good:** Implement only what's needed now

```python
# Bad — YAGNI violation
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.preferences = {}  # Not needed yet!
        self.metadata = {}     # Not needed yet!

# Good — YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

### TDD (Test-Driven Development)

Every task that produces code should include the full TDD cycle:
1. Write failing test
2. Run to verify failure
3. Write minimal code
4. Run to verify pass

See `test-driven-development` skill for details.

### Frequent Commits

Commit after every task:
```bash
git add [files]
git commit -m "type: description"
```

### 写作风格选择

> 借鉴 execplan 的 Prose-First Narrative 方法论——根据任务类型选择最适合的写作风格。

| 风格 | 适用场景 | 格式 |
|------|---------|------|
| **Checklist**（默认） | 需求清晰、路径确定、单人短时间实现 | 结构化 Task N + 精确文件路径 + 完整代码块 |
| **Prose Narrative**（可选） | 需求模糊、需要探索、架构探索、多天协作 | 叙事段落描述 milestone + 里程碑级验证 + 内嵌决策理由 |

**Prose Narrative 风格示例**：

```markdown
# User Authentication System — ExecPlan

## Purpose / Big Picture

用户可以用邮箱和密码注册账号。注册后收到验证邮件，点击链接激活账号。激活后可登录。

验收：访问 `POST /register` 传入 email + password，返回 201 + 验证邮件已发送。

## Plan of Work

### Milestone 1: User Model & Password Hashing

首先建立 User 数据模型。选择 bcrypt 而非 argon2，因为项目已有 bcrypt 依赖——argon2 需要额外 C 编译，会增加 CI 复杂度（见 Decision Log D-001）。

创建 `src/models/user.py`，定义 User 类含 email (unique, indexed) 和 password_hash 字段。密码哈希使用 bcrypt cost factor 10——在 CI 环境中 cost 12 耗时 800ms，降到 10 后降至 120ms（见 Surprises S-001）。
```

> 如果选择 Prose Narrative 风格，subagent-driven-development 的执行粒度会从 Task 级别调整为 Milestone 级别。适用于探索性强的项目。

## Common Mistakes

### Vague Tasks

**Bad:** "Add authentication"
**Good:** "Create User model with email and password_hash fields"

### Incomplete Code

**Bad:** "Step 1: Add validation function"
**Good:** "Step 1: Add validation function" followed by the complete function code

### Missing Verification

**Bad:** "Step 3: Test it works"
**Good:** "Step 3: Run `pytest tests/test_auth.py -v`, expected: 3 passed"

### Missing File Paths

**Bad:** "Create the model file"
**Good:** "Create: `src/models/user.py`"

## Execution Handoff

After saving the plan, offer the execution approach:

**"Plan complete and saved. Ready to execute using subagent-driven-development — I'll dispatch a fresh subagent per task with two-stage review (spec compliance then code quality). Shall I proceed?"**

When executing, use the `subagent-driven-development` skill:
- Fresh `delegate_task` per task with full context
- Spec compliance review after each task
- Code quality review after spec passes
- Proceed only when both reviews approve

## Plan-Only Mode

When the user explicitly wants a plan without execution (e.g., /plan command, "just plan it", "don't build yet"), switch to plan-only mode:

- Do not implement code or edit project files except the plan markdown file.
- Do not run mutating terminal commands, commit, push, or perform external actions.
- You may inspect the repo with read-only commands/tools.
- Your deliverable is a markdown plan saved under `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`.
- After saving, reply briefly with what you planned and the saved path.
- If the request is clear enough, write the plan directly. If underspecified, ask a clarifying question.

## Remember

```
Bite-sized tasks (2-5 min each)
Exact file paths
Complete code (copy-pasteable)
Exact commands with expected output
Verification steps
DRY, YAGNI, TDD
Frequent commits
```

**A good plan makes implementation obvious.**
