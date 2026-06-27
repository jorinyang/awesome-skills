---
name: darwin-skill
description: "Use when optimizing agent skills, evaluating skill quality, or running skill review — 技能自主优化器：9维评分体系 + 棘轮机制 + 人在回路。触发词：优化skill、skill评分、自动优化、skill质量检查、达尔文、darwin、帮我改改skill、skill怎么样、提升skill质量、skill review、skill打分。"
version: 2.1.1
author: Alchain (花叔), adapted for Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skill-optimizer, evaluation, quality, meta-skill, darwin]
    related_skills: [hermes-agent-skill-authoring, double-evolution]
---

# Darwin Skill 2.0 (Hermes Edition)

> **v2.0 · 2026-05-28** — 吸收 Microsoft Research SkillLens（arXiv 2605.23899）的 9 维评分药方 + SkillOpt（arXiv 2605.23904）的 validation-gated 验证机制 + human in the loop 三层守关。
>
> 借鉴 Karpathy autoresearch 的自主实验循环，对 skills 进行持续优化。
> 核心理念：**评估 → 改进 → 实测验证 → 人类确认 → 保留或回滚 → 生成成果卡片**
> 原始项目：https://github.com/alchaincyf/darwin-skill

---

## 设计哲学

1. **单一可编辑资产** — 每次只改一个 SKILL.md
2. **双重评估** — 结构评分（静态分析）+ 效果验证（跑测试看输出）
3. **棘轮机制** — 只保留改进，自动回滚退步
4. **独立评分** — 评分用 `delegate_task` 子 agent，避免「自己改自己评」的偏差
5. **人在回路** — 每个 skill 优化完后暂停，用户确认再继续

---

## Hermes 适配说明

本版本针对 Hermes Agent 做了以下适配：

| 原版 (Claude Code) | Hermes 版本 |
|---|---|
| `spawn 子agent` | `delegate_task` 工具 |
| `.claude/skills/*/SKILL.md` | `~/.hermes-feishu/skills/*/SKILL.md` |
| Claude Code 特有工具引用 | Runtime-neutral 措辞 |
| `npx skills add` 安装 | 手动复制到 `~/.hermes-feishu/skills/` |

---

## 系统级评估

当需要评估一个**外部方法论/框架**（如开源技能、论文框架、最佳实践文档）是否应融入整个 Hermes 技能生态时，使用 [零冲突吸收方法论](references/zero-conflict-absorption.md)。该方法是本技能（单技能质量评估）的互补能力——聚焦于外部框架与现有技能体系的冲突分析、分类吸收和系统影响评估。

已积累的评估案例：
- [execplan-skill 吸收 → answer v1.4.0](references/methodology-absorption.md) — 单仓库 13 特征 × 23 技能
- [BMad-METHOD + CIS 双仓库评估](references/bmad-evaluation-case-study.md) — 双仓库 32 特征 × 5 分类矩阵（🟢5 🔵5 🟡16 🔴7 ⚪4），新增依赖兼容性 + 哲学冲突维度 + CIS 创意套件
- [ARA 前提翻转再评估](references/ara-premise-shift-case-study.md) — 前提从"通用 Agent"切换到"论文产出工具"后，吸收结论从 🔴 仅思想 翻转为 🟢 全量基础设施吸收，沉淀了"前提审问"检查项

---

## 评估 Rubric（9维度，总分100）

> **设计依据**：基于 SkillLens 论文实证发现——LLM-as-judge 评估 skill 质量准确率仅 46.4%（接近随机），加入 meta-skill 三维度后提升到 73.8%。

### 结构维度（59分）— 静态分析

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 1 | **Frontmatter质量** | 7 | name规范、description包含做什么+何时用+触发词、≤1024字符、**禁结尾加"灵活应用/根据情况判断"等空话尾巴** |
| 2 | **工作流清晰度** | 12 | 步骤明确可执行、有序号、每步有明确输入/输出 |
| 3 | **失败模式编码** | 12 | **必须显式编码失败模式**（写出"如果 X 失败 → Y"的明确分支）；有fallback路径、错误恢复 |
| 4 | **检查点设计** | 6 | 关键决策前有用户确认、防止自主失控；**检查点必须显性标记（🔴/STOP/CHECKPOINT）** |
| 5 | **可执行具体性** | 17 | 不模糊、有具体参数/格式/示例、可直接执行；**禁止"建议/可以考虑/根据情况/灵活把握/视情况而定"等软化措辞** |
| 6 | **资源整合度** | 4 | references/scripts/assets引用正确、路径可达 |

### 效果维度（35分）— 需要实测

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 7 | **整体架构** | 12 | 结构层次清晰、不冗余不遗漏 |
| 8 | **实测表现** | 23 | 用测试prompt跑一遍，输出质量是否符合skill宣称的能力 |

### Meta-skill 维度（6分）

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 9 | **反例与黑名单** | 6 | skill 必须有"不要做什么"的反例清单；红灯/危险动作/反模式应单独章节列出 |

### 评分规则
- 维度1-7、9：每个维度打 1-10 分，乘以权重得到该维度得分
- 维度8（实测表现）：跑2-3个测试prompt，按输出质量打1-10分
- **总分 = Σ(维度分 × 权重) / 10**，满分100
- 改进后总分必须 **严格高于** 改进前才保留

→ 详细论文证据见 [references/skilllens-evidence.md](references/skilllens-evidence.md)
→ 真实审计发现（14技能短板模式）见 [references/real-world-audit-findings.md](references/real-world-audit-findings.md)

---

## Runtime 适配性审查（gate 项）

skill 应当能在任何 skills-compatible runtime 中通用。审查时机和规则见 [references/runtime-neutrality.md](references/runtime-neutrality.md)。

Phase 1 基线评估时强制跑一次红灯扫描：

```bash
grep -nE "(在 Claude Code|Claude Code skill|Claude Code 用户|Cursor only|Codex 中|^\[!\[Claude Code|~/\.claude/skills/[a-z]|/plugin install\b)" SKILL.md README.md 2>/dev/null
```

---

## 自主优化循环

### Phase 0: 初始化

```
1. 确认优化范围：
   - 全部skills → 扫描 ~/.hermes-feishu/skills/*/SKILL.md
   - 指定skills → 用户指定列表
2. 创建 git 分支：auto-optimize/YYYYMMDD-HHMM
3. 初始化 results.tsv（如不存在）
```

### Phase 0.5: 测试Prompt设计

```
for each skill:
  1. 读取 SKILL.md，理解它做什么
  2. 设计2-3个测试prompt，覆盖：
     - 最典型的使用场景（happy path）
     - 一个稍复杂或有歧义的场景
  3. 保存到 skill目录/test-prompts.json：
     [
       {"id": 1, "prompt": "用户会说的话", "expected": "期望输出的简短描述"},
       {"id": 2, "prompt": "...", "expected": "..."}
     ]
```

展示所有测试prompt给用户，**确认后再进入评估**。

### Phase 1: 基线评估（Baseline）

```
for each skill in 优化范围:
  # 结构评分（主agent可以做）
  1. 读取 SKILL.md 全文
  2. 按维度1-7逐项打分（附简短理由）

  # 效果评分（用 delegate_task 做，独立于主agent）
  3. 对每个测试prompt，spawn子agent：
     - with_skill: 带着SKILL.md执行测试prompt
     - baseline: 不带skill执行同一prompt
  4. 对比两组输出，打维度8的分

  # 汇总
  5. 计算加权总分
  6. 记录到 results.tsv
```

**Hermes 子 agent 用法**：使用 `delegate_task` 工具，每个测试prompt spawn一个独立的子agent。
若 `delegate_task` 不可用，维度8用干跑验证打分，标注 `dry_run`。

> **实践指南**：依赖外部 API 的 skill（飞书、高德、OSS 等）dim8 实测成本极高且不可复现。对此类 skill，dim8 默认 `dry_run`，以 skill 内容质量和结构完整性间接评估即可。`dry_run` 不违反「强制至少 1 个真实 full_test」规则——从自包含 skill（如 dogfood、yuanbao）中选 1 个做 real test 即可满足。

基线评估完成后，展示评分卡：

```
┌──────────────────────────┬───────┬──────────────┬──────────────┐
│ Skill                    │ Score │ 结构短板      │ 效果短板      │
├──────────────────────────┼───────┼──────────────┼──────────────┤
│ example-skill            │ 78    │ 边界条件      │ 测试prompt2  │
└──────────────────────────┴───────┴──────────────┴──────────────┘
```

**🔴 CHECKPOINT · 🛑 STOP：暂停等用户确认，再进入优化循环。**

### Phase 2: 优化循环

```
for each skill:
  round = 0
  while round < MAX_ROUNDS (默认3):
    round += 1

    # Step 1: 诊断
    找出得分最低的维度
    # HL-3 警告：dim2/dim3/dim4 是相关簇，修一个时另两个常跟着涨

    # Step 2: 提出改进方案
    针对最低维度，生成1个具体改进方案

    # Step 3: 执行改进
    编辑 SKILL.md
    git add + commit

    # Step 4: 重新评估
    - 结构维度：主agent重新打分
    - 效果维度：用 delegate_task spawn独立子agent重跑测试prompt

    # Step 5: 决策
    if 新总分 > 旧总分:
      status = "keep"
      # HL-4 见好就收：连续2轮 Δ < 2 分 → break
      if last_delta < 2.0 and this_delta < 2.0:
        break
    else:
      status = "revert"
      git revert HEAD
      break

  # 🔴 CHECKPOINT · 每个 skill 优化完后强制人审
  展示改动摘要（git diff + 分数变化 + 测试输出对比）
  等用户确认 OK 再继续下一个skill。
```

### Phase 2.5: 探索性重写（按需触发）

当 hill-climbing 连续2个skill都在 round 1 就 break 时，提议探索性重写。
**🔴 CHECKPOINT · 🛑 STOP：必须征得用户同意后才执行。**

### Phase 3: 汇总报告 + 质量验证矩阵

展示总览：优化skills数、总实验次数、保留改进比例、分数变化表。

**🔴 Phase 3 最后一步：质量验证矩阵（gate 项）**

所有轮次结束后，必须跑一次 5 标记一致性检查——子 agent 并行优化后，不同子 agent 可能使用不同的章节命名导致标记检测失败：

```python
# 对每个 skill 检查 5 个标记是否存在
checks = {
    '🔴': 'CHECKPOINT' in content or '🛑' in content,
    '⛔': '⛔' in content or '反例与禁止' in content or '禁止操作' in content,
    '📚': '引用文件索引' in content,
    'D3': '失败模式' in content or ('if' in content and '失败' in content and 'fallback' in content.lower()),
    'I/O': '输入' in content and '输出' in content,
}
# 输出矩阵，标记 ❌ 的 skill 需要补修
```

5 标记全绿才算通过。任何 ❌ 都是子 agent 输出偏差或遗漏，必须修复后再结束。

---

## results.tsv 格式

```tsv
timestamp	commit	skill	old_score	new_score	status	dimension	note	eval_mode
2026-03-31T10:00	baseline	example-skill	-	78	baseline	-	初始评估	full_test
```

文件位置：`~/.hermes-feishu/skills/software-development/darwin-skill/results.tsv`

---

## 实战 high-leverage 操作

- **HL-1（dim4）显性视觉标记是杠杆**：加 🔴 CHECKPOINT / 🛑 STOP，4 行改动撬动 dim4 +3 分
- **HL-2（dim3）if-then 三段式 fallback 表**：把「症状/解法」升级为「触发条件 / 一线修复 / 仍失败兜底」
- **HL-3（Phase 2 诊断）维度相关簇警告**：dim2/3/4 是相关簇
- **HL-4（Phase 2 退出）触顶自动 break**：连续 2 轮 Δ < 2 分 → break
- **HL-5（多轮优化）已验证的 6 轮收敛数据**：14 个 skill 实测（基线 44-75 → 最终 71-83）
  - **R1**：D3+D4+D6+D9 — 高杠杆基础建设
  - **R2**：D1+D2+D5 — 工作流升级
  - **R3**：D7 去冗余 — 架构清理，5/14 无改动可 skip
  - **R4**：交叉引用修正 + ⛔ 标记补全 — 一致性收尾
  - **R5-R6**：Δ < 2 收敛 + 低分 skill 体积超标 → 触发 Phase 2.5 回退
  - **收敛定律**：R3 起大部分 skill Δ < 2，R4+ 仅有标记补全。6 轮最多 4 轮有效改动。
  - **dim8 天花板**：dry_run 下大型 skill 上限 ≈83，小型 skill 上限 ≈72。要继续突破必须实测。

→ 详细案例数据见 [references/skilllens-evidence.md](references/skilllens-evidence.md)
→ 收敛数据与天花板分析见 [references/convergence-data-14skills-6rounds.md](references/convergence-data-14skills-6rounds.md)

---

## 优化策略库（按优先级）

### P0: Runtime 适配性问题
- SKILL.md 出现红灯措辞 → 替换为 runtime-neutral 措辞
- Badge 钉死单一 runtime → 改为中立 badge
- 安装命令只给一种路径 → 改为多层结构

### P0: 效果问题（实测发现的）
- 测试输出偏离用户意图 → 检查误导性指令
- 带skill比不带还差 → 精简过度约束

### P1: 结构性问题
- Frontmatter缺少触发词 → 补充
- 缺少Phase/Step结构 → 重组

### P2: 具体性问题
- 步骤模糊 → 改为具体操作和参数
- 缺少异常处理 → 补充 fallback

---

## 反例黑名单（dim9 应用：优化时不要做的事）

| # | 反模式 | 为什么不要做 | 替代做法 |
|---|---|---|---|
| 1 | **同 context 自评自改** | LLM 自评准确率仅 46.4% | 必须用 `delegate_task` spawn 独立子 agent 评分 |
| 2 | **`git reset --hard` 当回滚** | 丢工作树未提交改动 | 用 `git revert HEAD` |
| 3 | **为凑分增冗余** | 触顶后硬改加废话 | 触顶信号 → break |
| 4 | **跳过 test-prompts 直接评分** | dim8 权重 23% 变成编造 | Phase 0.5 强制设计 prompts |
| 5 | **轮内改多个维度** | 多变量无法归因 | 每轮 1 个维度 |
| 6 | **dry_run 比例 > 30%** | dim8 形同虚设 | 强制至少 1 个真实 full_test |
| 7 | **静默跳过异常** | 破坏 ratchet 完整性 | 异常先告知用户再处理 |
| 8 | **忽视维度相关性单独优化** | dim2/3/4 是相关簇 | 找最低维度时同时看相关簇 |
| 9 | **信任子 agent 自述不改验证** | 子 agent 可能声称「已加 I/O」但实际未写 | Phase 3 强制跑质量验证矩阵 |
| 10 | **提交 `__pycache__/` 和构建产物** | 污染 git 历史、增大体积 | 优化前加 `.gitignore`：`__pycache__/`、`*.pyc` |
| 11 | **多轮无限膨胀低分 skill** | 小范围 skill（<150行基线）经 3+ 轮优化后体积常超 200%，但分数仍难突破 dim8 天花板 | R3 后检查 volume check；超线即停，转入 Phase 2.5 探索性重写或接受现状 |

---

## 异常与边界条件

| 场景 | 触发条件 | 处理动作 |
|---|---|---|
| 不在 git 仓库 | `git rev-parse` 失败 | 询问用户：`git init` 或文件备份 |
| results.tsv 缺失 | 文件不存在 | 新建并写表头行 |
| results.tsv 损坏 | 列数不匹配 | 备份后重建，告知用户 |
| `git revert` 失败 | 冲突 | 先 `git stash`，重试 |
| MAX_ROUNDS 触顶 | 已跑3轮 | 展示当前最弱维度问用户 |
| 优化后超 150% 体积 | 新文件 > 原 × 1.5 | 拒绝提交，`git revert` 回退到上轮；小 skill 接受天花板上限 |
| 用户要求「全部 80+」但 dry_run 已触顶 | 小范围 skill 结构满分仍 < 80 | 如实告知：需 dim8 实测或缩小目标；不通过膨胀体积硬凑分 |

---

## 成果卡片生成（Result Card）

每个skill优化完成后生成视觉成果卡片。

模板位置：`templates/result-card.html`，3种风格（swiss/terminal/newspaper）。

### 生成流程

```
1. 复制 templates/result-card.html 到临时工作文件
2. 替换占位数据（skill名、分数变化、改进摘要、日期）
3. 随机选择风格：hash 设为 swiss/terminal/newspaper 之一
4. 截图：
   # 方式 A（推荐）：用 hermes browser_vision 打开 file:// 路径截图
   # 方式 B：npx playwright screenshot "file:///path/to/card.html" output.png \
   #   --viewport-size=960,1280 --wait-for-timeout=2000
   # 方式 C：用 scripts/screenshot.mjs（需先安装 playwright：npm i -g playwright）
5. 提示用户查看成果卡片
```

### Hermes 截图注意

`scripts/screenshot.mjs` 原始脚本硬编码了原作者 macOS 的 playwright 路径，Hermes/WSL 环境下不可直接用。优先使用 Hermes 自带的 `browser_navigate` + `browser_vision` 截图，或通过 `npx playwright` 命令。

---

## 使用方式

### 全量优化
```
用户："优化所有skills"
→ Phase 0-3 完整流程
→ 默认：先基线评估，按分数升序优先优化最低 5-10 个
```

### 单个优化
```
用户："优化 <skill-name> 这个skill"
→ 只对指定skill执行 Phase 0.5-2
```

### 仅评估不改
```
用户："评估所有skills的质量"
→ 只执行 Phase 0.5-1，不进入优化循环
```

### 批量优化加速（5+ skills）

当优化范围 ≥5 个 skill 且用户要求吞吐优先时，使用并行 delegate_task 加速 Phase 2。

**触发信号**：用户说「全部优化」「继续完成剩余所有」「不用每个都确认」。

**流程**：

```
1. Phase 0-1 照常执行（基线评估）
2. Phase 1 评分卡展示后，🔴 CHECKPOINT 确认一次
3. Phase 2 并行化：
   - 将 N 个 skill 拆成 3 组（每组 ≤5 个）
   - 用 delegate_task tasks[] 并发 spawn 3 个子 agent
   - 每个子 agent 负责一组 skill 的优化 + git commit
   - 子 agent context 中写清楚：目标技能列表、rubric 速查、D4/D6/D9 修复模板
4. 子 agent 返回后，git log 验证、推送、展示汇总

# 示例：14 个 skill → 3 个子 agent (4+5+5)
delegate_task(tasks=[
  {"goal": "Optimize 4 skills: D4 checkpoints + D6 refs. Skills: A,B,C,D"},
  {"goal": "Optimize 5 skills: D4 checkpoints + D9 anti-patterns. Skills: E,F,G,H,I"},
  {"goal": "Optimize 5 skills: D3 failure modes + D4 checkpoints + D9. Skills: J,K,L,M,N"},
])
```

**并行安全规则**：
- 每组 skills **不重叠**（不同子 agent 不改同一文件）
- 子 agent toolset: `["terminal", "file"]`（patch + git commit 即可）
- 子 agent 不需要 delegate_task（leaf 角色）
- 每个子 agent 独立 git commit，按 skill 名区分 commit message

**⚠️ 跳过 CHECKPOINT 的时机**：当用户说「继续完成剩余所有」时，跳过 Phase 2 的 per-skill 🔴 CHECKPOINT，直接并行处理。仅在用户明确要求时才跳过——默认仍然是 per-skill 确认。

**⚠️ 维度合并例外**：批量模式下，允许在单次 commit 中同时修 D6+D9（两个独立的新增章节，不互相干扰），跳过「每轮只改一个维度」规则以加速。但 D3/D4/D5 仍需单独改。

---

## 约束规则

1. **不改变skill的核心功能和用途**
2. **不引入新依赖**
3. **每轮只改一个维度**
4. **保持文件大小合理**（不超过原始150%）
5. **可回滚** — 用 git revert 而非 reset --hard
6. **评分独立性** — 效果维度必须用 `delegate_task` 子agent
7. **Runtime 中立性** — 参见「Runtime 适配性审查」章节

---

## 设计灵感

> "You write the goals and constraints in program.md; let an agent generate and test code deltas indefinitely; keep only what measurably improves the objective."
> — Karpathy, autoresearch

本skill的对应关系：
- **program.md** → 本文件（评估rubric和约束规则）
- **train.py** → 每个SKILL.md
- **val_bpb** → 9维加权总分
- **git ratchet** → 只保留有改进的commit
- **test set** → 每个skill的test-prompts.json

区别：增加了人在回路 + 双重评估机制。

---

## 致谢

原始项目：https://github.com/alchaincyf/darwin-skill by 花叔 (Alchain)

基于：
- SkillLens (arXiv 2605.23899) - Microsoft Research
- SkillOpt (arXiv 2605.23904) - Microsoft Research
- autoresearch - Andrej Karpathy
