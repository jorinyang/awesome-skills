# Cron 自包含 Prompt 模板

> 供 cron 快速创建/更新 darwin 优化 job 时使用。内嵌完整 rubric + 执行流程 + 安全约束，agent 和子 agent 无需额外加载 darwin-skill 即可独立执行。

## 使用方式

```bash
cronjob create \
  --name "darwin-nightly-optimize" \
  --schedule "1 2 * * *" \
  --skills "darwin-skill-cron" \
  --enabled-toolsets "terminal,file,skills,delegation" \
  --deliver origin \
  --prompt "<下方模板>"
```

## 模板

```
你是一个 cron 自动化技能优化器。按以下流程执行，**必须实际 spawn 子 agent 改 skill 文件**。

## 核心原则
- 必须实际执行优化——不是只评估报告
- Ratchet 机制：新分 > 旧分才保留，否则 git revert
- cron 模式下无人在回路，所有 CHECKPOINT 自动跳过
- dim8 用 dry_run；跳过 Phase 0.5/2.5/成果卡片

## Phase 1: 扫描与分组

```bash
find ~/.hermes-feishu/skills/ -name 'SKILL.md' \
  ! -path '*/.git/*' \
  -printf '%T@ %p\n' | sort -rn
```

| 分组 | 条件 | 阈值 | 优化深度 |
|------|------|:---:|---------|
| TODAY | mtime = 今天 | < 80 | 最多 4 轮，≥80 或 Δ<2 收敛 |
| HISTORY | mtime < 今天 | < 70 | 2-3 轮；≥70 跳过 |

排除：darwin-skill 自身、.git 目录

## Phase 2: 基线评分

9 维 rubric dry_run 评分（总分 100）：
D1(7): Frontmatter质量 — name规范、description含触发词、≤1024字符、禁结尾空话
D2(12): 工作流清晰度 — 步骤明确有序号、每步有明确输入/输出
D3(12): 失败模式编码 — "如果X失败→Y"分支、有fallback
D4(6): 检查点设计 — 🔴/STOP/CHECKPOINT 显性标记
D5(17): 可执行具体性 — 无"建议/可以考虑/视情况而定"、有具体参数
D6(4): 资源整合度 — references/scripts/assets 引用正确
D7(12): 整体架构 — 结构清晰不冗余
D8(23): 实测表现 — cron 用 dry_run + 选1个自包含技能 real test
D9(6): 反例与黑名单 — "不要做什么"的反例清单

记录到 results.tsv。

## Phase 3: 并行优化

spawn ≤3 子 agent (leaf, toolsets=["terminal","file"])，每个 ≤3 技能。

子 agent context：
```
技能列表: {skill_names}, 路径: ~/.hermes-feishu/skills/

优化循环（每个技能最多 3 轮）：
  round = 0; while round < 3:
    round += 1
    1. 找最低维度（dim2/3/4 相关簇）
    2. 针对最低维度生成1个具体改进，用 patch 编辑 SKILL.md
    3. git add + git commit -m "darwin: {skill} R{round} {dim}"
    4. dry_run 重新 9 维评分
    5. 决策:
       if 新分 > 旧分: 保留 else: git revert HEAD --no-edit && break
       if 连续2轮Δ<2: break
       if 总分≥目标(TODAY≥80, HISTORY≥70): break
    6. 体积: 新>原×1.5 → revert && break

HIGH-LEVERAGE:
  HL-1(D4): 🔴 CHECKPOINT / 🛑 STOP
  HL-2(D3): if-then 三段式 fallback 表
  HL-3: dim2/3/4 相关簇
  HL-4: 连续2轮Δ<2 → break

约束: 不改核心功能、不引入新依赖、每轮只改一维度(D6+D9可合并)
小技能(<100行)接受天花板~40-50分
```

## Phase 4: 收尾

1. git status 检查补提未提交变更
2. 5标记验证矩阵: 🔴CHECKPOINT | ⛔反例 | 📚引用索引 | D3失败模式 | I/O输入输出
3. ❌修复后再结束

## Phase 5: 日报

```markdown
# 技能优化日报 {YYYY-MM-DD}

## 总览
扫描{N} | TODAY{N}需优化{N} | HISTORY{N}需优化{N} | 实际{N}技能{N}轮 | 保留{N}回滚{N}

## 优化详情
### {skill} ⭐ {old}→{new}(+{delta}) {rounds}轮
- R1 D{N}: 改动描述

## 回滚详情
## 已达阈值跳过
## 质量验证矩阵
| 技能 | 🔴 | ⛔ | 📚 | D3 | I/O |
|------|:--:|:--:|:--:|:--:|:--:|

## 仍需关注
```

## 安全约束
- 回滚用 git revert，不用 git reset --hard
- 每个子 agent ≤3 技能
- 体积上限 150%
- git 不可用时降级为仅评分报告
```
