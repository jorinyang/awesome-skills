---
name: darwin-skill
description: "Use when optimizing agent skills, evaluating skill quality, or running skill review — 技能自主优化器：9维评分体系 + 棘轮机制 + 人在回路。支持 Cron 自动化模式。触发词：优化skill、skill评分、自动优化、达尔文、darwin、skill review。"
version: 2.1.2
author: Alchain (花叔), adapted by 杨瑒 (月夜)
metadata:
  hermes:
    tags: [skill-optimizer, evaluation, quality, meta-skill, darwin]
    related_skills: [skill-evaluator, double-evolution]
---

# Darwin Skill (Hermes Edition)

> 主版本：`~/.hermes-feishu/skills/darwin-skill/SKILL.md`（symlink → `~/.hermes/skills/darwin-skill/`）
> 本副本提供 default profile tooling 访问 + Cron 模式参考文档。

## Cron 自动化模式

Cron job 通过本技能每日自动执行技能巡检与优化，无人在回路。安全依赖 Ratchet 机制。

### 分组策略

| 分组 | mtime | 阈值 | 优化深度 |
|------|-------|:---:|---------|
| TODAY | = 今天 | < 80 | 最多 4 轮，≥80 或 Δ<2 收敛 |
| HISTORY | < 今天 | < 70 | 2-3 轮；≥70 跳过 |

### 跳过项

- Phase 0.5（不设计 test-prompts）
- Phase 2.5（不提议探索性重写）
- 所有 🔴 CHECKPOINT（自动跳过）
- 成果卡片生成

### 约束

- 并行优化 ≤3 子 agent，toolsets: `["terminal", "file"]`
- 每个子 agent ≤3 技能（4+ 技能 × 3 轮易超 leaf 子 agent max_iterations ~50次 tool call）
- 回滚用 `git revert`，不用 `git reset --hard`（cron 安全策略拦截）
- 体积上限 150%，小技能（<100 行）接受天花板（~40-50）
- 父 agent 在子 agent 返回后检查 `git status`，补提未提交变更

→ 实战案例：[references/cron-execution-pattern.md](references/cron-execution-pattern.md)
