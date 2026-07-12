---
name: ara-rigor-reviewer
description: 论文质量审查器——在论文提交前对 ARA 制品执行六维认识论审查（证据相关性/可证伪性/范围校准/论证连贯性/探索完整性/方法论严谨性），产出评分报告和修改建议。仅论文研究场景触发。
version: 1.0.0
license: MIT (adapted from AmberLJC/Agent-Native-Research-Artifact)
triggers:
  - 审查论文
  - 审查研究质量
  - 审稿
  - ara review
  - rigor review
  - /rigor-reviewer
  - 提交前检查
metadata:
  hermes:
    tags: [research, review, quality, epistemology]
    related_skills: [ara-research-manager, ara-compiler]
    scope: research-only
  upstream: https://github.com/AmberLJC/Agent-Native-Research-Artifact
---

# ARA Rigor Reviewer · 论文质量审查器

**仅论文研究场景触发。** 常态化业务对话不加载此技能。

## 何时触发

| 触发词 | 场景 |
|--------|------|
| "审查论文" / "审查研究质量" | 论文初稿完成，提交前检查 |
| "审稿" / "内部审稿" | 模拟 peer review |
| "rigor review <dir>" / "/rigor-reviewer" | CLI 风格调用 |
| "提交前检查" | 发表前的最终质量把关 |

**不触发**：常规文档审查、飞书文档校对（走 editorial-review 技能）。

---

## 核心定位

ARA Seal Level 2 — **语义认识论审查**。假设 Level 1（结构完整性）已通过。

**不是 bug 检测器，是认识论审稿人**：帮作者发现"声称了 A 但证据只验证了 B"、"声明不可证伪"、"消融实验缺少关键变量"等问题。

---

## 六维审查框架

### D1 · 证据相关性（承重维度）

**核心问题**：每条 Claim 引用的实验是否**实质性地**验证了其断言？

对每对 claim-experiment 绑定检查：

1. **相关性**：实验的 Setup/Procedure/Metrics 是否真正针对声明内容？（不是"链接存在就行"，而是"链接实质相关"）
2. **类型匹配**：从声明措辞推断声明类型，检查实验设计是否匹配：
   | 声明类型 | 信号词 | 所需实验设计 |
   |---------|--------|-------------|
   | 因果 | "导致"、"使"、"enable" | 需要隔离消融实验 |
   | 泛化 | "泛化"、"鲁棒"、"跨" | 需要异质测试条件 |
   | 改进 | "优于"、"提升"、"outperform" | 需要基线对比 |
   | 描述 | "占"、"分布"、"pattern" | 需要代表性采样 |
   | 范围 | "当…时"、"限于"、条件句 | 需要声明边界 |

3. **证据充分性**：单次实验是否足够支撑此声明？声明的范围是否要求多项独立实验？

**评分锚点**：
- 5：所有 claim-experiment 链接实质相关 + 类型匹配 + 证据充分
- 3：多数链接存在，但 1-2 个实验与声称的声明类型不匹配
- 1：多数链接不相关或仅名义上链接

### D2 · 可证伪性质量（承重维度）

**核心问题**：每条声明的证伪标准是否**可操作**？

对每条 Claim 的 `Falsification` 字段：

1. **可操作性**：证伪标准是否给出了具体阈值/条件？"效果更好"不是可证伪标准；"在数据集 X 上用指标 Y 的 p<0.05 假设检验，实验组超过对照组"是可证伪标准。
2. **非循环**：证伪标准是否只是声明的复述？"如果 BERT 不是最好的那就错了"是循环定义。
3. **范围匹配**：证伪标准的难度是否与声明的强度匹配？声称"always works"只需一个反例证伪；声称"在多数情况下优于"需要统计检验。

**评分锚点**：
- 5：所有声明有可操作、非循环、范围匹配的证伪标准
- 3：多数声明有证伪标准，但有 1-2 条不具体或循环
- 1：多数声明无证伪标准或不可操作

### D3 · 范围校准（辅助维度）

**核心问题**：声明是否精确断言了其证据所支持的范围，不多也不少？

- **过度声称**：证据只在 ImageNet 上测试，声明却说"在所有视觉任务上 SOTA"
- **不足声称**：证据支持更强的结论，却用了过弱的措辞（同样损害论文贡献的可感知性）
- **缺失条件**：声明中未提及证据实际依赖的关键前提（"只在 16 卡以上有效"写在实验部分但没写在声明中）

### D4 · 论证连贯性（辅助维度）

**核心问题**：论文的叙事弧线是否从问题→方案→证据逻辑完整？

- **动机链**：Observation → Gap → Insight 是否有清晰的逻辑链条？
- **声明依赖**：声明的依赖关系是否有循环依赖或缺失前提？
- **实验叙事**：实验的顺序是否对应科学发现的自然推进（基线→消融→分析），还是随机排列？
- **related_work 的论证作用**：相关信息是否被用来说明"为什么我们是不同的/更好的"，而非仅仅罗列？

### D5 · 探索完整性（辅助维度）

**核心问题**：探索树是否记录了真实的研究过程，包括失败？

- **dead_end 存在性**：零 dead_end 节点 → 审查标记（真实研究不会没有死胡同）
- **dead_end 质量**：每个 dead_end 是否包含：假设 + 失败模式 + 教训？（只有标题的空 dead_end 不算）
- **pivot 合理性**：转向节点的触发器是否与 trace 中的 evidence 节点一致？
- **decision 证据**：决策节点是否引用了支持选择的 evidence？

### D6 · 方法论严谨性（承重维度）

**核心问题**：实验设计是否充分严谨？

| 检查项 | 标准 |
|--------|------|
| **基线充分性** | 是否包含了领域公认的最强基线？是否缺少明显的竞争者？ |
| **消融覆盖** | 消融是否涵盖了方法的关键组件？是否有遗漏的"显然该做"的消融？ |
| **统计报告** | 是否报告了方差/标准差/置信区间/显著性检验？ |
| **指标-Claim 对齐** | 使用的指标是否直接度量了声明的性质？"更高效"用 FLOPS，"更准确"用 Accuracy；混用是信号不对齐 |
| **超参敏感性** | 是否分析了关键超参的性能敏感性？还是只报告了最优值？ |
| **可复现信息** | src/environment.md 是否完整？随机种子是否固定？ |

---

## 审查流程

### Step 1：读取 ARA 制品

按固定顺序读取文件：
1. `PAPER.md` → 层索引
2. `logic/claims.md` → 提取所有 Claim（Statement, Status, Falsification, Proof, Dependencies）
3. `logic/experiments.md` → 提取所有 Experiment（Verifies, Setup, Metrics, Baselines）
4. `logic/problem.md` → 提取 Gap + Insight
5. `logic/solution/` → system design, algorithm, heuristics, constraints
6. `logic/related_work.md` → 依赖图
7. `trace/exploration_tree.yaml` → 五类节点
8. `src/environment.md` → 可复现性信息
9. 抽查 `evidence/tables/` 中 2-3 个文件

### Step 2：构建工作映射

- **claim_proof_map**：每条 claim → 引用的实验 ID 集合
- **experiment_verifies_map**：每个实验 → 验证的 claim ID 集合
- **claim_dependency_edges**：claim 之间的有向依赖边
- **gap_set**：problem.md 中的所有 Gap
- **dead_end_nodes** + **pivot_nodes**：探索树中的失败和转向节点
- **decision_nodes**：探索树中的决策节点

### Step 3：逐维度评分

对每个维度，执行语义推理，记录：strengths / weaknesses / suggestions。

### Step 4：产出审查报告

写入 `ara/level2_report.md`：

```
# ARA Seal Level 2 · Epistemic Review Report

## Overall: {Strong Accept / Accept / Weak Accept / Revise / Reject}
### Score: {D1+D2+D3+D4+D5+D6}/30

## Per-Dimension

### D1 · Evidence Relevance: {score}/5
- Strengths: ...
- Weaknesses: ...
- Suggestions: ...

[... D2-D6 同上 ...]

## Severity-Ranked Findings

### 🔴 Critical (Must Fix)
1. [D1] Claim C03 (因果) 引用的实验 E02 是纯描述性统计 → 类型不匹配
2. ...

### 🟡 Major (Should Fix)
3. [D2] Claim C05 缺可操作的证伪标准
4. ...

### 🟢 Minor (Nice to Fix)
5. [D5] 探索树零 dead_end 节点（真实研究不会这样）
6. ...

## Verdict
{一句话结论 + 主要修改方向}
```

---

## 使用示例

```
用户："审查论文 ara/attention/"

Hermes 加载 ara-rigor-reviewer：
→ Step 1-2：读取 ARA，提取 5 Claims、2 Experiments、构建 8 条映射
→ Step 3：
    D1 证据相关性：3/5 — C03 的 claimed 因果但实验 E02 只做了相关性
    D2 可证伪性：4/5 — C05 缺具体阈值
    D3 范围校准：2/5 — C01 声称"all tasks"但只测了 3 个 benchmark
    D4 论证连贯性：4/5
    D5 探索完整性：2/5 — 零 dead_end 节点
    D6 方法论严谨性：3/5 — 消融缺关键变量、未报告方差
→ 总分：18/30 → Weak Accept

输出：ara/level2_report.md 已生成
      🔴 2 Critical · 🟡 3 Major · 🟢 2 Minor
```

---

## 工具适配

| 操作 | Hermes 工具 |
|------|------------|
| 读取 ARA 文件 | read_file（按序读取各层文件） |
| 搜索声明引用 | search_files(target='content', pattern='C\d+') |
| 检查文件存在 | search_files(target='files') |
| 输出报告 | write_file |

---

## 技术说明

- 上游：Orchestra-Research/Agent-Native-Research-Artifact (MIT)
- 本技能为上游 rigor-reviewer 的 Hermes 适配版
- 仅在论文研究场景触发
- 审查是语义推理（需要阅读理解），不是结构性检查（Level 1 已由 compiler 完成）
- 不执行代码、不访问外部 URL、不获取外部数据
