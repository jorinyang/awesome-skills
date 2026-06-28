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

🔴 **CHECKPOINT** — 测试配置已确认。验证通过后继续：
>- [ ] Skill 名、A/B 版本均已明确？
>- [ ] 用例来源（benchmark/生成/用户提供）已确定？
>- [ ] 重复轮数 ≥ 2？
>- [ ] 总 run 数是否在可接受范围（建议 < 50）？
>- [ ] 若配置不完整 → 追问用户补齐

🛑 验证通过 → 继续 Phase 2

### Phase 2: 准备测试环境

1. **加载测试用例**：从 benchmark 数据集中读取或用 `benchmark-generator` 生成
2. **准备 Skill 环境**：
   - A 侧：确保 v1.0 可用
   - B 侧：确保 v1.1 可用
3. **创建结果目录**：`~/.hermes-feishu/ab_results/{skill_name}/{timestamp}/`

🔴 **CHECKPOINT** — 测试环境就绪。验证通过后继续：
>- [ ] 测试用例已全部加载（数量与 Phase 1 配置一致）？
>- [ ] A/B 两侧 Skill 均已可用（文件存在且可解析）？
>- [ ] 结果目录已创建且有写入权限？
>- [ ] 若环境未就绪 → 回到 Phase 2 对应步骤修复

🛑 验证通过 → 继续 Phase 3 执行

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

🔴 **CHECKPOINT** — 数据收集与显著性检验完成。决策前验证：
>- [ ] 所有 run 均已执行（无遗漏）？
>- [ ] A/B 两侧 run 数相等？
>- [ ] 异常 run 已标记且不影响统计？
>- [ ] 若存在未完成 run → 回退 Phase 3 补执行

🛑 验证通过 → 进入 Phase 6 决策

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

## 失败模式与恢复

| # | 触发条件 | 症状 | 一线修复 | 仍失败兜底 |
|---|---------|------|---------|-----------|
| 1 | 子 Agent 执行超时 | 单个 run 超过 120s 无响应 | 对该 run 重试 1 次，缩短上下文 | 标记该用例 `✗ FAILED(timeout)`，继续下一用例 |
| 2 | A/B 两侧结果不可比 | 同一用例两侧 token 消耗差 > 10× 或输出格式不兼容 | 检查两侧是否使用相同模型和上下文模板 | 标记该用例为 `incomparable`，从统计中剔除 |
| 3 | 评测法官不可用 | `skill-evaluator` 调用失败或返回非结构化结果 | 回退到 Phase 4 内嵌指标（精准度/耗时/token）做量化对比 | 标记 `⚠️ no_judge_fallback`，决策矩阵仅基于量化指标 |
| 4 | 测试用例集为空 | benchmark 目录不存在或无匹配文件 | 调用 `benchmark-generator` 自动生成，最少 5 routing + 3 outcome | 向用户报告缺失，请求手动提供 3 个场景 |
| 5 | 结果目录写入失败 | `EACCES` 或 `ENOSPC` | 检查并创建目录，若磁盘满则清理旧结果（保留最近 5 次） | 写入 `/tmp/ab_results/` 备用路径 |
| 6 | 全部子 Agent 失败 | 所有 run 返回 `✗ FAILED` | 回退为单 Agent 直接对比（不加 Skill vs 加 Skill），仅测 1 轮 | 报告失败原因，输出 raw 输出供人工审查 |

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

## ⛔ 反例与禁止

以下行为将导致 A/B 测试结论不可信：

| ❌ 反例 | 正确做法 |
|---------|---------|
| 凭主观印象判断"哪个更好" | 必须用 Phase 4-5 量化指标 + 显著性检验 |
| A/B 两侧使用不同模型或不同上下文 | 两侧必须在相同条件下对比，仅 Skill 不同 |
| 只跑 1 轮就下结论 | 每用例至少 2 轮以消除 LLM 随机性 |
| 样本量 < 3 用例就做决策 | 最少 3 用例，低于此数标记 `⚠️ insufficient_sample` |
| 只看精准度忽略成本和稳定性 | 必须输出 Phase 4 三维对比报告 |
| 显著性不显著时仍声称"显著提升" | 若 `|delta| < std_avg`，必须声明差异不显著 |
| 重复使用同一评测法官评估自己是 A/B 的被执行者 | 法官必须独立，优先用非当前会话模型 |
| 测试执行到一半因超时中断就基于半截数据决策 | 必须检查 CHECKPOINT 完整性，不完整则补执行 |

---

## 参考文件

- `references/ab-report-template.md` — A/B 对比报告模板
- `references/decision-matrix.md` — 决策矩阵详细说明
