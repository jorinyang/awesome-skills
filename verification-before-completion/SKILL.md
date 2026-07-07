---
name: verification-before-completion
description: 当即将声称工作完成、修复成功、测试通过，或在提交/部署/发布前——要求先运行验证命令并确认输出，证据先于声明。触发：完成了/修好了/通过了/build成功/发布/deploy/提交
version: 1.0.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [quality, verification, discipline, anti-slop]
    related_skills: [test-driven-development, systematic-debugging, requesting-code-review]
  source: 吸收自 https://github.com/obra/superpowers (v6.1.1)
---

# Verification Before Completion

> **吸收自**: [obra/superpowers](https://github.com/obra/superpowers) v6.1.1

## Overview

没有验证就声称工作完成是不诚实，不是效率。

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

如果这条消息里没有运行验证命令，你就不能声称它通过了。

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: 什么命令能证明这个声明？
2. RUN: 执行完整命令（全新、完整）
3. READ: 完整输出，检查退出码，数失败数
4. VERIFY: 输出是否确认声明？
   - If NO: 用证据陈述实际状态
   - If YES: 带证据陈述声明
5. ONLY THEN: 做声明

跳过任何步骤 = 撒谎，不是验证
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |
| OSS 上传成功 | curl 验证文件可访问 | 上传命令 exit 0 |
| 飞书文档已写入 | fetch 验证 revision_id > 1 + 内容存在 | 创建命令 exit 0 |
| 部署完成 | 浏览器访问 URL 验证 | CI passed |

## Hermes 特有验证场景

### 文件操作验证
```bash
# ❌ "文件已写入"
# ✅ [stat 文件] → [cat 文件前 10 行] → "文件已写入，XX 字节，内容以 '...' 开头"
```

### OSS 上传验证
```bash
# ❌ "上传成功"
# ✅ [curl -I OSS_URL] → [HTTP 200] → "OSS 上传成功，URL: XXX，状态码: 200"
```

### 飞书文档写入验证
```bash
# ❌ "文档已创建"
# ✅ [lark-cli docs +fetch] → [revision_id > 1 且 blocks > 0] → "文档已创建: ID=XXX, revision=N"
```

### 技能创建验证
```bash
# ❌ "技能已创建"
# ✅ [skill_view(name)] → [内容存在] → "技能已创建: name=XXX, 行数=NNN"
```

### 部署验证
```bash
# ❌ "部署完成"
# ✅ [curl 实际 URL] → [HTTP 200 + 预期内容] → "部署完成，页面可访问: URL"
```

## Red Flags - STOP

- 使用 "should", "probably", "seems to", "应该", "大概", "好像"
- 在验证前表达满意 ("Great!", "Perfect!", "Done!", "搞定了!")
- 即将 commit/push/deploy 但未验证
- 信任子代理的成功报告
- 依赖部分验证
- 想"就这一次"
- 累了想赶紧结束
- **任何暗示成功但未运行验证的措辞**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "应该能工作了" | 跑验证 |
| "我很有信心" | 信心 ≠ 证据 |
| "就这一次" | 没有例外 |
| "Linter 过了" | Linter ≠ 编译器 |
| "Agent 说成功了" | 独立验证 |
| "我累了" | 疲惫 ≠ 借口 |
| "部分检查够了" | 部分什么也证明不了 |
| "换个说法规则就不适用" | 精神高于字面 |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

**OSS Upload:**
```
✅ [ossutil cp] → [curl -I OSS_URL] → [HTTP 200] → "上传成功，CDN 可访问"
❌ "上传完成" (仅凭 exit 0)
```

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, deploying, publishing
- Creating PRs, merging
- Moving to next task
- Delegating to agents
- Reporting to user

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.

> 吸收自: https://github.com/obra/superpowers (v6.1.1)
