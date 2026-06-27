---
name: skill-ab-test
description: >
  Skill A/B 对比测试引擎。同一个 Skill 的两个版本（或加 Skill vs 不加 Skill），用同一批测试用例自动执行对比评测，
  输出「能力 × 成本 × 稳定性」三维对比报告和「通过/打回」决策建议。触发：AB测试、对比两个skill、skill A/B、
  这个skill改了之后变好了吗、对比评测、哪个版本更好、灰度测试。
version: 1.0.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [skill-evaluation, ab-testing, comparison, quality, ai-engineering]
    related_skills: [skill-evaluator, benchmark-generator, double-evolution]
triggers:
  - "AB 测试"
  - "A/B 测试"
  - "对比两个 skill"
  - "skill A/B"
  - "这个 skill 改了之后变好了吗"
  - "对比评测"
  - "哪个版本更好"
  - "灰度测试"
  - "ab test"
  - "compare skills"
  - "skill comparison"
  - "这个改动有没有提升"
---

# Skill A/B Test — 技能对比测试引擎

> **定位**：不是"感觉好点了"的主观判断——是同一套测试用例下，对照组(A) vs 实验组(B)的「能力 × 成本 × 稳定性」三维量化对比。
>
> **核心理念**：Skill 改了之后到底有没有变好？拿数据说话，用同一把尺子量。

## 触发条件

| 信号 | 示例 |
|------|------|
| 用户要求对比 Skill 版本 | "帮我对比一下 troubleshooter v1 和 v2" |
| 用户询问改动效果 | "这个 skill 改了之后变好了吗？" |
| 用户要求灰度测试 | "对 email-sender 做一次 A/B 灰度测试" |
| 用户评估 Skill 价值 | "diagnosis skill 到底有没有用？对比一下加和不加的效果" |

## 核心概念

| 术语 | 含义 |
|------|------|
| **对照组 (A / Baseline)** | 不加 Skill 或使用旧版本 Skill |
| **实验组 (B / Skill)** | 加 Skill 或使用新版本 Skill |
| **用例 (Case)** | 测试数据集中的一道题 |
| **轮 (Round)** | 同一道题重复执行的次数（消除随机性） |
| **侧 (Side)** | A 侧 = 对照组，B 侧 = 实验组 |
| **Run** | 一次具体的执行 = 某个用例 × 某轮 × 某侧 |

一个 3 用例 × 2 轮的 A/B 测试会产生 `3 × 2 × 2 = 12` 个 run。

---

## 执行流程

### Phase 1: 确认测试配置

从用户输入中提取以下信息，缺失的追问：

1. **目标 Skill**：Skill 名称和两个版本（或 "不加 Skill vs 加 Skill"）
2. **测试用例集**：用哪些用例来测？
   - 如已有 benchmark 测试集 → 直接使用
   - 如没有 → 调用 `benchmark-generator` 技能自动生成
   - 如用户指定 → 使用用户提供的用例
3. **重复轮数**（默认 2 轮）：每道题重复几次以消除 LLM 随机性
4. **评测模型**：用于 LLM 法官打分的模型（默认使用当前会话模型）

```
用户: 对比 troubleshooter v1.0 和 v1.1，用 5 个故障案例测 2 轮

提取结果:
├── Skill: troubleshooter
├── A 侧: v1.0 (旧版)
├── B 侧: v1.1 (新版)
├── 用例数: 5
├── 重复轮数: 2
└── 总 run 数: 5 × 2 × 2 = 20
```

### Phase 2: 准备测试环境

1. **加载测试用例**：从 benchmark 数据集中读取或用 `benchmark-generator` 生成
2. **准备 Skill 环境**：
   - A 侧：确保 v1.0 可用
   - B 侧：确保 v1.1 可用
3. **创建结果目录**：`~/.hermes-feishu/ab_results/{skill_name}/{timestamp}/`

### Phase 3: 执行对比测试

对每个用例 × 每轮 × 每侧，依次执行：

```
for case in cases:
    for round in range(rounds):
        # A 侧执行
        run_with_skill(A_version, case, label="A")
        # B 侧执行
        run_with_skill(B_version, case, label="B")
```

**执行要点**：
- 同一用例的 A/B 两侧使用**相同的系统提示和上下文**（除了 Skill 差异）
- 每次执行后自动调用 `skill-evaluator` 做三维打分
- 记录：Token 消耗、耗时、工具调用序列、错误信息、最终产出

### Phase 4: 对比分析

收集所有 run 结果后，按以下维度对比：

#### 4.1 能力对比 (Capability)

| 指标 | A 侧 | B 侧 | 变化 | 结论 |
|------|:---:|:---:|:---:|------|
| 执行精准度均分 | {a_score} | {b_score} | {delta} | {verdict} |
| 任务成功率 | {a_rate}% | {b_rate}% | {delta}% | {verdict} |
| 步骤偏离率 | {a_dev}% | {b_dev}% | {delta}% | {verdict} |
| LLM 法官评分 | {a_judge} | {b_judge} | {delta} | {verdict} |

#### 4.2 成本对比 (Cost)

| 指标 | A 侧 | B 侧 | 变化 | 结论 |
|------|:---:|:---:|:---:|------|
| 平均 Token 消耗 | {a_tok} | {b_tok} | {delta}% | {verdict} |
| 平均耗时 (ms) | {a_ms} | {b_ms} | {delta}% | {verdict} |
| CPSR | ${a_cpsr} | ${b_cpsr} | {delta}% | {verdict} |

#### 4.3 稳定性对比 (Stability)

| 指标 | A 侧 | B 侧 | 变化 | 结论 |
|------|:---:|:---:|:---:|------|
| 评分标准差 | {a_std} | {b_std} | {delta} | {verdict} |
| 异常率 | {a_err}% | {b_err}% | {delta}% | {verdict} |
| 结果一致性 | {a_con}% | {b_con}% | {delta}% | {verdict} |

### Phase 5: 统计显著性检验

对于关键指标，进行简单的显著性检验：

```
若 B 侧精准度 > A 侧精准度 且 |delta| > 2 × max(std_a, std_b):
    → "B 侧显著优于 A 侧 (p < 0.05 等效)"
若 |delta| < std_avg:
    → "差异不显著，可能在随机波动范围内"
```

### Phase 6: 决策建议

根据三维对比结果，自动给出决策：

```
┌─────────────────────────────────────────────┐
│               A/B 测试决策矩阵                │
├──────────┬──────────┬──────────┬────────────┤
│ 能力提升  │ 成本变化  │ 稳定性变化 │ 决策        │
├──────────┼──────────┼──────────┼────────────┤
│ ↑ 显著    │ ↓ 或 →   │ ↑ 或 →   │ ✅ 通过     │
│ ↑ 显著    │ ↑ 显著    │ →        │ ⚠️ 有条件通过│
│ ↑ 轻微    │ ↓        │ ↑        │ ⚠️ 建议再测  │
│ → 或 ↓   │ —        │ —        │ ❌ 打回     │
│ ↑         │ ↑        │ ↓        │ ❌ 打回     │
└──────────┴──────────┴──────────┴────────────┘
```

---

## 输出格式

完整 A/B 对比报告见 `references/ab-report-template.md`。

### 简要决策输出

```markdown
# A/B 测试结果：troubleshooter v1.0 → v1.1

| 维度 | A (v1.0) | B (v1.1) | 变化 | 
|------|:---:|:---:|:---:|
| 精准度 | 3.8/5 | 4.4/5 | **+15.8%** ↑ |
| 耗时 | 32s | 28s | -12.5% ↓ |
| Token | 45k | 38k | -15.6% ↓ |
| 成功率 | 80% | 95% | +18.8% ↑ |

**决策：✅ 通过 — 建议上线 v1.1**

理由：精准度显著提升 (+16%)，同时成本和耗时均有下降。
没有发现稳定性退步。建议推广使用。
```

---

## 参考文件

- `references/ab-report-template.md` — A/B 对比报告模板
- `references/decision-matrix.md` — 决策矩阵详细说明
