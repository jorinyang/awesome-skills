---
name: darwin-skill-cron
description: "Darwin Skill Cron 自动化模式 — 技能每日自主优化：9维评分 + 棘轮机制 + 并行子 agent 执行。含自包含 prompt 模板和两日实战数据。触发词：darwin cron、技能自动巡检、skill nightly optimize。"
version: 1.0.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [skill-optimizer, cron, darwin, meta-skill]
    related_skills: [darwin-skill, skill-evaluator, double-evolution]
---

# Darwin Skill — Cron 自动化模式

> 为 cron job 提供的 darwin-skill 自包含执行参考。
> 主版本: `~/.hermes-feishu/skills/darwin-skill/SKILL.md`

## Cron 自动化模式

Cron job 每日自动执行技能优化，无人在回路。安全依赖 Ratchet 机制（新分 > 旧分才保留，否则 git revert）。

### 分组策略

| 分组 | mtime | 阈值 | 优化深度 |
|------|-------|:---:|---------|
| TODAY | = 今天 | < 80 | 最多 4 轮，≥80 或 Δ<2 收敛 |
| HISTORY | < 今天 | < 70 | 2-3 轮；≥70 跳过 |

### 跳过项

- Phase 0.5（不设计 test-prompts）
- Phase 2.5（不提议探索性重写）
- 所有 🔴 CHECKPOINT（自动跳过）
> ⚠️ **绝对不要加 `delegation`** — sub-agent 通过 delegation 可绕过父 agent 的 toolsets 约束，已在 2026-07-04 导致 `.hermes/skills/` 被删至仅剩 13 个目录（~155 技能丢失，需从 awesome-skills 恢复）。`skills` toolset 足以让 agent 直接 patch/write_file 修改技能文件。

## 🔴 安全边界（CRITICAL）

### delegation 禁令
- **禁止**在 cron job 的 `enabled-toolsets` 中加入 `delegation`
- **禁止**在 cron prompt 中 instruct 父 agent 调用 `delegate_task`
- 子 agent 不得获得 `delegation` — 即使 prompt 中声明 `toolsets=["terminal","file"]`，实际 cron job 的 enabled-toolsets 会覆盖子 agent 的约束

### 技能目录保护
- **禁止**子 agent 执行 `rm -rf`、目录级删除、或将技能目录整体移出 git 管理范围
- 子 agent 只允许 `patch`（单文件精确编辑）和 `write_file`（创建/覆盖单文件），不得操作整个目录
- 所有修改必须在 `.hermes/skills/` git repo 内完成，修改前检查 `git status` 确保仓库正常

### Pre-flight 检查（Phase 0）
在进入 Phase 1 之前，父 agent 必须执行：
```bash
cd ~/.hermes/skills && git status --short | grep "^ D" | wc -l
```
若已有 D (deleted) 状态文件 > 0：中止优化，报告异常。

**Git 初始提交检查**：`git log -1` 失败（`No commits yet`）时，repo 虽已 `git init` 但从未 commit，Phase 2 优化和 ratchet 回滚均不可用。修复：先做初始提交（建议先加 `.gitignore` 排除 `.usage.json`/`.curator_state`/`__pycache__/`）。

### 恢复预案
若发生技能目录大规模丢失：
1. 源：`~/.hermes/skills/` 是 git repo（提交 34461a0 后完整）
2. 备源：`~/awesome-skills/` 含 88 个已发布技能
3. 交叉备源：`~/.hermes/hermes-agent/skills/` 含少数独有技能（如 yuanbao、dogfood）
4. 恢复流程：`cp -r ~/awesome-skills/<name> ~/.hermes/skills/` → 检查 symlink → `git add -A && git commit`
5. 参考记录：[references/disaster-recovery-2026-07-04.md](references/disaster-recovery-2026-07-04.md)

### 约束
- **前置**：repo 必须有初始提交（`git log -1` 成功），否则 Phase 2 不可用
- 并行优化 ≤3 子 agent (leaf, toolsets: `["terminal", "file"]`)
- 每个子 agent ≤3 技能（4+ 技能 × 3 轮易超 leaf 子 agent max_iterations）
- 回滚用 `git revert`，不用 `git reset --hard`
- 体积上限 150%，小技能（<100 行）接受天花板
- 父 agent 检查 `git status`，补提未提交变更

## 关键资源

| 文件 | 用途 |
|------|------|
| [cron-prompt-template.md](references/cron-prompt-template.md) | 创建/更新 cron job 的自包含 prompt，内嵌完整 rubric |
| [cron-execution-pattern.md](references/cron-execution-pattern.md) | 两日实战数据（13 技能）+ 收敛规律 + 回滚案例 |

## 创建 Cron Job

```bash
cronjob create \
  --name "darwin-nightly-optimize" \
  --schedule "1 2 * * *" \
  --skills "darwin-skill-cron" \
  --enabled-toolsets "terminal,file,skills" \
  --deliver origin \
  --prompt "$(cat references/cron-prompt-template.md)"
```
> ⚠️ **绝对不要加 `delegation`** — sub-agent 通过 delegation 可绕过父 agent 的 toolsets 约束，已在 2026-07-04 导致 `.hermes/skills/` 被删至仅剩 13 个目录（~155 技能丢失，需从 awesome-skills 恢复）。`skills` toolset 足以让 agent 直接 patch/write_file 修改技能文件。
