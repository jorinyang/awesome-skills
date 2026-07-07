---
name: executing-plans
description: 当你有书面的实现计划要在单独会话中执行，带审查检查点时使用——加载计划、批判性审查、执行所有任务、完成后报告。触发：执行计划/实现/按计划构建/跑任务清单
version: 1.0.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [execution, plan, implementation, workflow]
    related_skills: [writing-plans, subagent-driven-development, finishing-a-development-branch, verification-before-completion]
  source: 吸收自 https://github.com/obra/superpowers (v6.1.1)
---

# Executing Plans

> **吸收自**: [obra/superpowers](https://github.com/obra/superpowers) v6.1.1

## Overview

加载计划、批判性审查、执行所有任务、完成后报告。

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Note:** 告诉用户，Superpowers 在能访问子代理时工作更好。如果在有子代理支持的平台上运行（Hermes 支持 `delegate_task`），使用 `subagent-driven-development` 代替本技能。本技能用于子代理不可用或任务高度耦合的场景。

## The Process

### Step 1: Load and Review Plan
1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create todos for the plan items and proceed

### Step 2: Execute Tasks

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed
5. **Apply `verification-before-completion`** — never mark complete without evidence

### Step 3: Complete Development

After all tasks complete and verified:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use `finishing-a-development-branch`
- Follow that skill to verify tests, present options, execute choice

## Hermes 适配说明

在 Hermes 环境中：
- 使用 `todo` 工具管理任务状态
- 使用 `subagent-driven-development` 作为优先方案（当任务可独立并行时）
- 本技能作为回退方案（任务高度耦合、需要人工检查点）
- 每个任务完成后强制运行 `verification-before-completion`

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent
- **Evidence before completion claims**

## Integration

**Required workflow skills:**
- `writing-plans` - Creates the plan this skill executes
- `subagent-driven-development` - Preferred alternative (parallel task execution)
- `finishing-a-development-branch` - Complete development after all tasks
- `verification-before-completion` - Quality gate before every completion claim

> 吸收自: https://github.com/obra/superpowers (v6.1.1)
