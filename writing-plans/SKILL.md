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

# Writing Plans

## 触发条件

### 通用领域触发矩阵

实现计划撰写覆盖7大领域，21个子场景。

| 领域 | 场景 | 触发信号 | 示例 |
|------|------|---------|------|
| **AI/ML** | 模型部署方案 | 用户需要模型上线的实施计划 | "写一个模型serving的implementation plan" |
| AI/ML | RAG系统搭建 | 用户需要RAG系统的构建计划 | "给这个RAG项目写个plan" |
| AI/ML | Fine-tuning方案 | 用户需要微调的实施计划 | "LoRA微调的计划写一下" |
| **Web/后端** | 新功能开发 | 用户需要新功能的实施计划 | "这个payment集成的plan" |
| Web/后端 | 重构方案 | 用户需要重构的实施计划 | "monolith拆微服务的plan写一下" |
| Web/后端 | 性能优化 | 用户需要性能优化的计划 | "这个API性能优化的implementation plan" |
| **前端** | 新页面开发 | 用户需要前端的实施计划 | "dashboard页面的plan写一下" |
| 前端 | 组件库搭建 | 用户需要组件系统的构建计划 | "design system的implementation plan" |
| 前端 | 迁移方案 | 用户需要前端框架迁移计划 | "Vue到React迁移的plan" |
| **数据工程** | 数据管道建设 | 用户需要数据管道的实施计划 | "real-time data pipeline的plan" |
| 数据工程 | 数据湖建设 | 用户需要数据平台的建设计划 | "data lake的implementation plan" |
| 数据工程 | BI搭建 | 用户需要BI系统的构建计划 | "这个BI dashboard的plan写一下" |
| **基础设施** | 云迁移 | 用户需要云迁移的实施计划 | "AWS到GCP迁移的plan" |
| 基础设施 | K8s部署 | 用户需要容器化的实施计划 | "app containerize的plan" |
| 基础设施 | 监控搭建 | 用户需要可观测性的计划 | "observability stack的plan" |
| **安全** | 安全加固 | 用户需要安全加固的实施计划 | "security hardening的plan" |
| 安全 | 合规改造 | 用户需要合规改造的计划 | "SOC2 compliance的implementation plan" |
| 安全 | 零信任 | 用户需要零信任架构的计划 | "zero trust migration plan" |
| **移动** | App开发 | 用户需要移动App的实施计划 | "这个RN app的plan写一下" |
| 移动 | 跨平台方案 | 用户需要跨平台方案的计划 | "Flutter unified app plan" |
| 移动 | App发布 | 用户需要App发布的计划 | "iOS/Android release plan" |

### 手动触发
- "写一个plan"
- "implementation plan"
- "write a plan"
- "实施计划"

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

## Critical Workflow: Plan → Confirm → Execute (Never Skip)

**This user requires explicit plan confirmation before touching any code** (non-negotiable):

1. **Plan first** — Full implementation plan (complete tasks, approach, open questions)
2. **User reviews** — They correct scope, priority, or approach (typically 2-3 rounds)
3. **Revise if needed** — Align before writing code
4. **Only then execute** — After user says "confirmed"

**Do NOT skip to implementation because the plan looks obvious.** The user's corrections at the plan stage prevent hours of wasted work.

### What a Complete Plan Looks Like (for this user)

- **4-item framework** if user gave specific scope (e.g., "only items 1,2,3,4")
- **Real calendar dates** not abstract days ("May 21 - June 30" not "D1-D40")
- **Key milestone anchoring** — explicitly call out fixed dates user mentioned
- **Feature specs** for every new capability (not just bug fixes)
- **Verification method** for every feature — "CDP screenshot", "API call returns X"

### Open Questions Required

At the end of every plan, ALWAYS list:

```markdown
## Open Questions (Pending Your Confirmation)
1. [Specific question about scope]
2. [Specific question about a missing field/behavior]
```


**CRITICAL:** When adding new modules to an existing system, every plan MUST include an explicit "Integration Wiring" phase AFTER implementation and BEFORE shipping.

```
WRONG plan order:  implement → test → ship
RIGHT plan order:  implement → unit test → wire into existing → integration test → ship
```

For each new module, the plan MUST answer:
1. **Who calls this?** — Which existing file/function will import and invoke it?
2. **When does it fire?** — On heartbeat? On event? On API call? On startup?
3. **What if it fails?** — Does the host system break? (Must be try/except guarded)
4. **How do we prove it?** — Integration test that verifies end-to-end data flow

Create `tests/test_integration_<module>.py` for every new module that proves it's actually wired into the system, not just importable.

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

## Further reading (load when relevant)

- **`references/cross-project-adaptation.md`** — Workflow for analyzing an external project and adapting its patterns/modules into your own codebase. Load when the task involves "borrow from X", "adapt Y's architecture", "port Z to our stack".

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
