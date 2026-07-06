---
name: dynamic-workflow
description: "Auto-build and execute dynamic multi-agent workflows using 6 isolation patterns from Claude Code Harness. Three-layer trigger: business context → task type → dimension scores. Automatically triggers on complex tasks, builds the optimal agent pipeline, and executes via delegate_task."
version: 2.0.0
author: Yueye Yang
metadata:
  hermes:
    tags: [workflow, multi-agent, fanout, verification, tournament, isolation, execution, harneess]
    related_skills: [delegate_task, test-driven-development, systematic-debugging, edge-case-hunter, double-evolution]
---

# Dynamic Workflow — 动态工作流执行引擎

> 不是审计清单。是执行引擎。隔离 = 质量。

基于 Claude Code Harness 六种隔离模式，三层触发自动构建 Agent 工作流并通过 `delegate_task` 执行。

## 关键：这是真正的多 Agent 隔离，不是角色模拟

**`delegate_task` 会 spawn 真正的子 Agent 进程**，每个子 Agent 拥有：
- 独立的上下文窗口（不共享父 Agent 的对话历史）
- 独立的终端会话
- 独立的工具集
- 无父 Agent 记忆

这意味着 **③ Adversarial Verification 的隔离是真实的**：verifier 子 Agent 看不到 worker 子 Agent 的推理过程，只看到 worker 的最终产出。不存在同一上下文中"维护先前成果"的自我偏好偏差。

这不是一个 Agent 假装自己是三个不同角色在顺序对话——那是假的隔离，解决不了 Harness 定义的三种故障模式。

---

## 三层触发架构

```
Priority 1: 业务上下文 (references/business-triggers.md)
  → 数据采集 | 内容创作 | 工具编排 | API批量 | 项目决策 | 工作流联动

Priority 2: 任务类型 (7 种，见下方 Layer 1)
  → T1 Audit | T2 Decision | T3 Research | T4 Build | T5 Debug | T6 Creative | T7 Execute

Priority 3: 维度计分上调 (8 维度，见下方 Layer 2)
  → D1-D8 在 Priority 1+2 的默认模式上做增强
```

**自动加载条件（任一命中）：**

| 触发层 | 条件 |
|--------|------|
| 业务 | 报告 ≥ 2 数据源、内容 ≥ 2 版本、工具 ≥ 3 文件、API ≥ 5 次、决策 ≥ 3 方案、编排 ≥ 3 并行模块 |
| 类型 | 匹配 T1-T6 关键词 |
| 维度 | 总分 ≥ 6 或 D3 ≥ 2 或 D7 ≥ 2 |

**总分 ≤ 5 静默跳过。**

---

### 通用领域触发矩阵

6种隔离模式覆盖7大领域，35个子场景。DW根据三层检测自动选择模式组合和Agent数量。

#### AI / 大模型 / 智能体
| 场景 | 触发信号 | 任务类型 | 推荐模式 |
|------|---------|---------|---------|
| 模型选型决策 | 用户对比多个模型/框架做技术选型 | T2 Decision | ④ Gen-Filter + ⑤ Tournament |
| Agent系统审计 | 用户有多Agent编排需要安全性审查 | T1 Audit | ① Classify + ② Fanout + ③ Adversarial |
| RAG/推理优化 | 技术方案对比需要基准测试 | T2 Decision | ④ Gen-Filter + ⑤ Tournament |
| AI应用构建 | 用户搭建AI产品从零开始 | T4 Build | ② Fanout → Synthesize |
| prompt系统调试 | 多链prompt的编排和效果排查 | T5 Debug | ⑥ Loop + ③ Adversarial |
| 模型评测设计 | 用户设计模型评测方案需要多维度 | T3 Research | ② Fanout + ⑥ Loop |

#### 产品 / 商业
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 产品方案选型 | 用户有多个产品方案需要对比 | T2 Decision → ④+⑤ |
| 商业策略调研 | 用户需要多维度市场调研 | T3 Research → ②+⑥ |
| 定价方案决策 | 用户有多个定价方案需要评估 | T2 Decision → ④+⑤ Tournament |
| 产品路线图规划 | 用户需要并行拆解产品路线图 | T4 Build → ② Fanout |
| 用户反馈分析 | 用户有大量用户反馈需要分类审计 | T1 Audit → ① Classify + ② Fanout + ③ |

#### 企业管理 / 战略
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 战略方向决策 | 用户有多个战略方向需要系统对比 | T2 Decision → ④+⑤ |
| 组织诊断审计 | 用户需要对企业现状做多维度审计 | T1 Audit → ①+②+③ |
| 流程优化调研 | 用户需要调研最佳实践后部署 | T3 Research → ②+⑥ |
| 多部门协同构建 | 用户需要跨部门并行推进 | ② Fanout (D2≥2 → ① Classify first) |
| 项目复盘排查 | 用户需要排查项目失败的根因 | T5 Debug → ⑥ Loop + ③ |

#### 学术 / 研究
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 文献多维度调研 | 用户需要从多角度调研一个研究领域 | T3 Research → ② Fanout + ⑥ Loop |
| 实验方案对比 | 用户有多个实验设计方案需要对比 | T2 Decision → ④+⑤ |
| 论文审查 | 用户有多篇论文需要交叉审查 | T1 Audit → ② Fanout + ③ Adversarial |
| 假设验证 | 用户有多个假设需要并行验证 | ② Fanout |
| 研究方法论证 | 用户需要评估不同研究方法的优劣 | T2 Decision → ④ Gen-Filter + ⑤ |

#### 安全 / 合规
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 安全漏洞审计 | 用户有代码/系统需要安全审查 | T1 Audit → ①+②+③ (verifier ×3) |
| 合规方案审查 | 用户有合规方案需要多维度审计 | T1 Audit → ② Fanout + ③ Adversarial |
| 渗透测试编排 | 用户需要并行多向量渗透测试 | T1 Audit → ① Classify + ② Fanout |
| 风险评估 | 用户有多个风险维度需要评估 | T3 Research → ②+⑥ Loop |
| 隐私影响评估 | 用户有数据处理方案需要审查 | T1 Audit → ③ Adversarial |

#### 技术 / 架构
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 技术选型对比 | 用户需要对比多个技术栈 | T2 Decision → ④ Gen-Filter + ⑤ Tournament |
| 系统架构审计 | 用户有微服务/分布式系统需要审查 | T1 Audit → ① Classify + ② Fanout + ③ |
| 性能瓶颈排查 | 用户有多层性能问题需要定位根因 | T5 Debug → ⑥ Loop + ③ Adversarial |
| 代码审查规模化 | 用户有多个模块/仓库需要并行审查 | T1 Audit → ② Fanout + ③ |
| 重构方案决策 | 用户有多个重构方案需要评估 | T2 Decision → ④+⑤ |
| 多模块并行构建 | 用户需要并行构建多个独立模块 | T4 Build → ② Fanout |

#### 内容 / 创作
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 创意头脑风暴 | 用户需要多个方向的创意方案 | T6 Creative → ④ Generate-Filter |
| 多版本内容生产 | 用户需要同一主题的多个版本 | ② Fanout (N builders) |
| 内容质量审查 | 用户有多个内容单元需要审查 | T1 Audit → ②+③ |
| 命名/文案选型 | 用户需要从多个方案中选最佳 | T6 Creative → ④+⑤ Tournament |
| 营销策略方案 | 用户需要多渠道策略的并行方案 | ② Fanout → Synthesize |

---

## Layer 1: 任务类型 → 默认模式

根据关键词 + 任务结构自动归类：

| Type | 识别特征 | 默认模式 | Agent 配置 |
|------|---------|---------|-----------|
| **T1 Audit** | "审查""审计""检查""扫描" + 多目标 | ①+②+③ | classifier → N reviewers → 2 verifiers |
| **T2 Decision** | "选哪个""对比""评估方案" + 多候选 | ④+⑤ | 3 generators → filter → pairwise judge |
| **T3 Research** | "调研""分析""探索" + 多维度 | ②+⑥ | N researchers 并行 → loop convergence |
| **T4 Build** | "写""实现""创建""搭建" + 具体产出 | ② | N builders 并行 → synthesize |
| **T5 Debug** | "修""debug""排查""为什么" + 异常 | ⑥+③ | loop root-cause → verifier check |
| **T6 Creative** | "头脑风暴""起名""创意" + 发散 | ④ | 5 generators → rubric + dedupe |
| **T7 Execute** | 单一步骤、明确指令 | — | 不触发本技能 |

---

## Layer 2: 维度计分 → 上调/降级

每种任务类型有默认最低配置。维度分数只能**向上增强**（加模式、加 Agent 数量），**不能降级低于默认**。降级仅两个例外。

### 上调规则

| 维度 | 条件 | 动作 |
|------|------|------|
| D1 并行度 | ≥ 2 且默认无 ② | 加 ② Fanout |
| D1 并行度 | = 3 | ② agent 数 = 实际拆分数量 |
| D3 风险 | ≥ 2 且默认无 ③ | 加 ③ Adversarial |
| D3 风险 | = 3 | ③ verifier 从 1 → 2-3 个 |
| D4 方案广度 | ≥ 2 且默认无 ④ | 加 ④ Gen-Filter |
| D5 评价难度 | ≥ 2 且 D4 ≥ 1 且默认无 ⑤ | 加 ⑤ Tournament |
| D6 探索深度 | ≥ 2 且默认无 ⑥ | 加 ⑥ Loop |
| D7 模糊度 | ≥ 2 | 先 Clarify，再重新分类+计分 |
| D8 依赖 | ≥ 2 | ② Fanout 从全并行 → 分阶段串行 |

### 降级规则（仅此两条）

| 条件 | 动作 |
|------|------|
| D7 = 3（一句话需求） | 所有模式暂停，先 Clarify |
| D8 = 3（完全未知依赖） | ② Fanout 暂禁，先 ⑥ Loop 探索 |
| 总分 ≤ 5 | 全部跳过，直接执行 |

### D1-D8 计分标准

| D# | 维度 | 0 | 1 | 2 | 3 |
|----|------|---|---|---|---|
| D1 | 可并行度 | 不可拆 | 2 个子任务 | 3-5 个 | 6+ 批量 |
| D2 | 领域离散度 | 单一领域 | 2 关联领域 | 3+ 不关联 | 边界模糊 |
| D3 | 风险等级 | 无后果 | 用户可见 | 数据/发布 | 安全/合规 |
| D4 | 方案广度 | 单一答案 | 2-3 方案 | 4-10 方案 | 11+ 探索 |
| D5 | 评价难度 | 明确指标 | 有主观 | 标准模糊 | 多利益方 |
| D6 | 探索深度 | 一步到位 | 2-3 轮 | 深度未知 | 开放式 |
| D7 | 任务模糊度 | 规格完整 | 方向明确 | 目标模糊 | 一句话 |
| D8 | 依赖复杂度 | 完全并行 | 简单 DAG | 复杂 DAG | 依赖未知 |

---

## 决策示例

### 示例 1: "审查所有微服务的 SQL 注入风险"

```
Layer 1: T1 Audit → Default: ①+②+③

Layer 2:
  D1=3 → ② 升级: N 个 reviewer（每文件）
  D3=3 → ③ 升级: 3 verifier（误报/漏报/修复质量）
  D2=0 D4=0 D5=0 D6=0 D7=0 D8=0

Final: ① + ②(×N) + ③(×3)
  → Classify 分文件组 → N reviewer 并行 → 汇总 → 3 verifier 交叉验证
```

### 示例 2: "选一个最适合的技术栈"

```
Layer 1: T2 Decision → Default: ④+⑤

Layer 2:
  D1=1 D2=0 D3=1 D4=2 D5=2 D6=0 D7=1 D8=1
  无上调触发（默认已覆盖 ④+⑤）

Final: ④ + ⑤
  → 3 generator（不同偏好）→ Filter → Pairwise → Winner
```

---

## 执行流程

```
Phase 1: Classify（内部推理，不输出）
  ├─ 业务上下文匹配 → 任务类型归类 → D1-D8 计分
  └─ Final = Default ∪ Upgrades \ Downgrades

Phase 2: Build（构建 delegate_task 调用，不输出表格）
  └─ 按下方的执行模板生成具体的 task goals + toolsets + context

🔴 **CHECKPOINT** — 工作流已构建。确认后执行：
>- [ ] 选择的模式组合是否匹配 Layer 1 默认 + Layer 2 上调？
>- [ ] 子 Agent 数量是否在并发限制内（≤3/批）？
>- [ ] 每个 task 的 goal 是否有明确验收标准？
>- [ ] toolsets 分配是否符合分配规则？
>- [ ] 若配置不当 → 回到 Phase 1 重新计分

🛑 确认通过 → 进入 Phase 3 执行

Phase 3: Execute（实际执行，用户可见）
  ├─ delegate_task 并行分派 → 汇总 → 质量门验证
  └─ 每步完成后输出状态

Phase 4: Deliver（最终交付）
  └─ 整合所有子 Agent 产出 → 一份最终结果
```

---

## 执行模板（每个模式组合一个模板）

以下模板是 Phase 2 Build 的产出物。直接按模板构造 `delegate_task` 调用。

### 模板 A: ② Fanout + ③ Adversarial（审查/审计类）

适用于 T1 Audit，或任何 D1≥2 + D3≥2 的组合。

```
Step 1: 并行审查（② Fanout）
  delegate_task(tasks=[
    {goal: "<子任务1的完整描述，含输入文件/路径/检查标准>", toolsets: ["terminal","file"], context: "..."},
    {goal: "<子任务2>", toolsets: [...]},
    ...  # N 个子任务，N = D1≥3 时按实际数量
  ])
  # 子任务数量 > 3 时分批，每批 3 个

Step 2: 汇总综合（② Synthesize）
  delegate_task(
    goal: "将以上 N 个审查结果合并去重，按严重程度排序，输出 consolidated report",
    context: "<Step 1 所有子任务的关键发现摘要>"
  )

Step 3: 独立验证（③ Adversarial）
  delegate_task(tasks=[
    {goal: "独立验证 consolidated report —— 检查是否有误报。逐条验证每个 finding 的证据", 
     context: "你是独立验证者，未参与原始审查。只评价证据是否充分，不评价审查质量"},
    {goal: "独立验证 consolidated report —— 检查是否有漏报。对比原始文件列表和 finding 覆盖",
     context: "你是独立验证者，检查覆盖率"}
  ])

Step 4: 最终交付
  将验证后的 report 作为最终结果输出给用户
```

### 模板 B: ④ Generate-Filter + ⑤ Tournament（决策/选型类）

适用于 T2 Decision。

```
Step 1: Rubric 先行（必须在生成前定义）
  明确评分标准: 维度1(权重) / 维度2(权重) / 维度3(权重)
  向用户确认 rubric 是否合理

🔴 **CHECKPOINT** — Rubric 需用户确认后才能继续。若用户未确认，暂停并等待。

Step 2: 并行生成（④ Generate）
  delegate_task(tasks=[
    {goal: "产出方案 A：倾向 <维度1优先>，输出结构化方案",
     context: "rubric: <维度1权重0.5, 维度2权重0.3, 维度3权重0.2>"},
    {goal: "产出方案 B：倾向 <维度2优先>",
     context: "rubric: ..."},
    {goal: "产出方案 C：倾向 <维度3优先>",
     context: "rubric: ..."},
  ])

Step 3: Rubric 筛选（④ Filter）
  delegate_task(
    goal: "按 rubric 对 3 个方案打分排序，筛选 top 2，输出评分表和各方案优劣",
    context: "<rubric + 3 个方案摘要>"
  )

Step 4: 两两比较（⑤ Tournament）
  delegate_task(
    goal: "对 top 2 方案做 pairwise 比较。从 <N个维度> 逐项对比，说明每项谁优谁劣及理由，最终给出 winner 和推荐理由",
    context: "<top 2 方案全文 + rubric>"
  )

Step 5: 最终交付
  输出 winner + 对比理由
```

### 模板 C: ② Fanout + ⑥ Loop（调研/探索类）

适用于 T3 Research。

```
Step 1: 并行初探（② Fanout）
  delegate_task(tasks=[
    {goal: "从维度 <1> 调研 <主题>，输出初步发现和关键数据", toolsets: ["web"]},
    {goal: "从维度 <2> 调研 <主题>", toolsets: ["web"]},
    {goal: "从维度 <3> 调研 <主题>", toolsets: ["web"]},
  ])

Step 2: 收敛判断（⑥ Loop）
  检查 Step 1 的发现：是否有值得深入的新线索？
  
  → YES: spawn 下一轮
    max_iter = D6 × 3（上限 10）
    每轮追问: "上轮发现中提到的 <新线索>，深入挖掘"
    
  → NO: 进入 Step 3

Step 3: 综合报告
  delegate_task(
    goal: "将所有轮次的发现整合为一份结构化调研报告",
    context: "<所有轮次的摘要>"
  )
```

### 模板 D: ② Fanout only（构建/实现类）

适用于 T4 Build。

```
Step 1: 并行构建（② Fanout）
  delegate_task(tasks=[
    {goal: "构建模块 <1>：<具体产出要求 + 验收标准>", toolsets: ["terminal","file"]},
    {goal: "构建模块 <2>：<具体产出要求>", toolsets: [...]},
    ...
  ])

Step 2: 整合综合（② Synthesize）
  delegate_task(
    goal: "整合所有模块产出，确保接口一致、无冲突，输出最终交付物",
    context: "<各模块产出摘要>"
  )
```

### 模板 E: ⑥ Loop + ③ Adversarial（Debug/排查类）

适用于 T5 Debug。

```
Step 1: 逐层排查（⑥ Loop）
  max_iter = D6 × 3
  
  迭代 1: delegate_task(goal: "排查 <异常现象> 的可能原因，输出初步诊断和下一步调查方向")
  检查: 是否定位到根因？
    → NO: spawn 迭代 2，context 传入迭代 1 的诊断结果
    → YES: 进入 Step 2

Step 2: 修复方案
  delegate_task(goal: "根据根因 <X> 给出修复方案，含具体代码变更和回滚方案")

🔴 **CHECKPOINT** — 修复方案需审查后才能部署验证。确认修复不引入副作用后继续。

Step 3: 独立验证（③ Adversarial）
  delegate_task(
    goal: "验证修复方案是否真正解决根因，且不引入新问题。检查边界情况",
    context: "你是独立验证者，未参与诊断和修复"
  )
```

### 模板 F: ① Classify + ② Fanout（跨领域分派类）

适用于 D2≥2 的多领域任务。

```
Step 1: 领域分类（① Classify）
  按领域拆分 task groups:
  - group-code: 代码相关的子任务
  - group-content: 内容/文案相关的子任务
  - group-ops: 运维/部署相关的子任务
  
Step 2: 并行分派（② Fanout）
  delegate_task(tasks=[
    {goal: "<group-code 所有子任务>", toolsets: ["terminal","file"], context: "你只负责代码部分"},
    {goal: "<group-content 所有子任务>", toolsets: ["file","web"], context: "你只负责内容部分"},
    {goal: "<group-ops 所有子任务>", toolsets: ["terminal"], context: "你只负责运维部分"},
  ])

Step 3: 整合交付
  合并各领域产出
```

---

## 执行规则

### 并行分派规则

1. **子任务 ≤ 3 个**: 一次 `delegate_task(tasks=[...])` 全部并行
2. **子任务 4-6 个**: 分两批，每批 3 个，第一批完成后立即启动第二批
3. **子任务 7+ 个**: 分多批，每批 3 个（Hermes delegation 并发限制）

### 上下文传递规则

1. **worker → verifier**: 传递 worker 的完整产出，但声明 "你是独立验证者，未参与原始工作"
2. **fanout → synthesize**: 传递所有子任务的摘要（每个 ≤ 200 字），不全量传递（节省 token）
3. **loop → next iteration**: 传递上一轮的 "关键发现 + 下一步方向"，不传递完整对话历史

### 工具集分配规则

| 任务性质 | toolsets |
|---------|----------|
| 代码审查/编写/调试 | `["terminal", "file"]` |
| 调研/搜索/分析 | `["web"]` |
| 内容创作/文案 | `["file", "web"]` |
| 数据操作/API 调用 | `["terminal", "file"]` |
| 综合/汇总/判断 | `["file"]` |

### 错误处理

1. **单个子 Agent 失败**: 标记该子任务为 `✗ FAILED`，其他子任务继续。最终交付时说明"<N>/<M> 完成"
2. **全部子 Agent 失败**: 回退为单 Agent 直接执行，并报告失败原因
3. **③ Verifier 发现严重问题**: 回退到 Step 1，用 verifier 的反馈重新执行 worker

---

## 隔离规则（不可违反）

1. **③ 模式下 worker ≠ verifier** — 不同 delegate_task 调用
2. **② 模式并行任务 prompt 同质** — 不因"这个简单"而降级
3. **⑥ 模式必须写死 max_iter** — 默认 D6×3，上限 10
4. **④ rubric 在生成前定义** — 不能生成了再编标准

---

## Pitfalls

1. 简单任务不触发（总分 ≤ 5 静默跳过）
2. ③ 的 verifier 必须独立
3. ⑥ 的 max_iter 必须写死
4. rubric 在生成之前定义

---

## ⛔ 反例与禁止

以下行为违反隔离原则，导致多 Agent 工作流失效：

| ❌ 反例 | 正确做法 |
|---------|---------|
| 用单一 Agent 假装多个角色顺序对话 | 必须用 `delegate_task` spawn 独立子进程 |
| ③ verifier 能看到 worker 的推理过程 | verifier 只接收最终产出，上下文声明独立性 |
| ④ rubric 在生成后再定义 | rubric 必须在生成前定义并确认 |
| ⑥ Loop 的 max_iter 不设上限 | 必须写死 max_iter = D6×3（上限 10） |
| 总分 ≤ 5 的任务强行触发工作流 | 静默跳过，直接单 Agent 执行 |
| 把 ② Fanout 的子任务 prompt 降级简写 | 所有并行任务 prompt 必须同质完整 |
| 子 Agent 失败后静默跳过 | 必须标记 `✗ FAILED`，在最终交付中声明 |
| D7=3 时不等 Clarify 结果就直接执行 | 必须先 Clarify 再重新分类计分 |

---

## 参考文件

| 文件 | 用途 | 何时查阅 |
|------|------|---------|
| `references/business-triggers.md` | 业务上下文触发矩阵（6 领域 × 场景） | Phase 1 Classify 阶段做业务上下文匹配 |
| `references/isolation-patterns.md` | Claude Code Harness 六模式详解 | Phase 2 Build 时确认模式语义细节 |

> 以上文件为本 Skill 运行时依赖。若缺失，使用 SKILL.md 内嵌的六模式描述和领域矩阵。

## Attribution

Claude Code Dynamic Workflows (Harness), Thariq Shihipar & Sid Bidasaria @ Anthropic.
六模式图及钉钉文档解读由秦弋提供参考。