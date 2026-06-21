# Dynamic Workflow 完整设计 — 决策架构

## 核心问题：分数驱动 vs. 任务类型驱动？

**答案：任务类型定基调，维度分数做调整。** 两层决策：

```
Layer 1: Task Type → 默认模式组合（经验最优）
Layer 2: Dimension Scores → 向上增强或向下降级
```

---

## Layer 1: 任务类型 → 默认模式组合

### 任务类型分类

根据用户输入的关键词 + 任务结构特征，自动归类到 7 种任务类型之一：

| Type | 识别特征 | 默认模式 | 理由 |
|------|---------|---------|------|
| **T1: Audit（审查审计）** | "审查""审计""检查""扫描" + 多文件/多目标 | ① + ② + ③ | Classify 分类型 → Fanout 并行审 → Adversarial 隔离验证 |
| **T2: Decision（方案选型）** | "选哪个""对比""评估方案""技术选型" | ④ + ⑤ | Gen 多方案 → Tournament 两两淘汰 → winner |
| **T3: Research（调研分析）** | "调研""分析""探索""了解一下" + 多维度 | ② + ⑥ | Fanout 多维度并行 → Loop 深挖直到收敛 |
| **T4: Build（构建实现）** | "写""实现""开发""创建" + 具体产出物 | ② | Fanout 并行构建 → Synthesize 合并 |
| **T5: Debug（调试修复）** | "修""debug""排查""为什么" + 异常现象 | ⑥ + ③ | Loop 追踪根因 → Adversarial 验证修复 |
| **T6: Creative（创意生成）** | "头脑风暴""起名""想点子""创意" + 发散 | ④ | Gen 大量候选 → Filter + Dedupe |
| **T7: Execute（直接执行）** | 单一步骤、明确指令、无拆解需求 | 无 | 不触发动态工作流，直接执行 |

### 每类任务的默认 Agent 配置

```
T1: Audit
  ├─ ① Classify: 1 classifier → N 个专业 reviewer
  ├─ ② Fanout: N 个 reviewer（按文件/模块并行）
  └─ ③ Adversarial: 2 个 verifier（误报检查 + 漏报检查）

T2: Decision  
  ├─ ④ Gen: 3 个 generator（不同偏好加权）
  ├─ Filter: 1 个 filter（rubric 打分）
  └─ ⑤ Tournament: pairwise judge → final arbiter

T3: Research
  ├─ ② Fanout: N 个 researcher（按维度并行）
  └─ ⑥ Loop: 每轮判定是否有新发现，spawn 下一轮

T4: Build
  └─ ② Fanout: N 个 builder（按模块并行）

T5: Debug
  ├─ ⑥ Loop: 每轮深入一层，直到根因
  └─ ③ Adversarial: verifier 验证修复是否真正解决问题

T6: Creative
  └─ ④ Gen-Filter: 5 个 generator → rubric + dedupe → top N

T7: Execute
  └─ 直接执行，不触发本技能
```

---

## Layer 2: 维度分数 → 上调/降级

每种任务类型的默认模式组合是**最低配置**。维度分数可以**向上增强**（加模式、加 Agent 数量），但不能**向下降级**到低于默认。

### 上调规则（OR 逻辑，命中即触发）

| 维度 | 条件 | 上调动作 |
|------|------|---------|
| D3 风险 | ≥ 2 | 强制加 ③ Adversarial（如果默认没有） |
| D3 风险 | = 3 | ③ 的 verifier 从 1 个升级到 2-3 个 |
| D1 并行 | ≥ 2 且默认无 ② | 加 ② Fanout |
| D1 并行 | = 3 | ② 的 agent 数量 = 文件数/模块数（上限受 D8 限制） |
| D4 广度 | ≥ 2 且默认无 ④ | 加 ④ Generate-Filter |
| D5 评价 | ≥ 2 且 D4 ≥ 1 且默认无 ⑤ | 加 ⑤ Tournament |
| D6 探索 | ≥ 2 且默认无 ⑥ | 加 ⑥ Loop |
| D7 模糊 | ≥ 2 | 先 Clarify，再重新分类+计分 |
| D8 依赖 | ≥ 2 | ② Fanout 从全并行降为分阶段 + 部分串行 |

### 降级规则（极其保守，仅以下情况）

| 条件 | 降级动作 |
|------|---------|
| D8 依赖 = 3（完全未知） | ② Fanout 暂时禁用，先 ⑥ Loop 探索依赖结构 |
| D7 模糊 = 3（一句话需求） | 所有模式暂停，先 Clarify |
| 总分 ≤ 5 | 全部跳过，直接执行 |

---

## 决策流程（完整版）

```
Task Received
  │
  ├─ Step 0: 快速扫描任务文本
  │    ├─ 匹配 T1-T7 类型关键词
  │    └─ 识别目标文件/模块数量
  │
  ├─ Step 1: Layer 1 — 确定默认模式组合
  │    Task Type → Default Patterns
  │    例: "审查 SQL 注入" → T1 Audit → ①+②+③
  │
  ├─ Step 2: Layer 2 — 跑 8 维度计分
  │    对任务逐维度打分 (0-3)
  │    确定是否有上调/降级触发
  │
  ├─ Step 3: 合并决策
  │    Final Patterns = Default ∪ Upgrades \ Downgrades
  │    例: T1 Audit = ①+②+③（默认）
  │          D3=3 → ③ 升级到 3 个 verifier
  │          D1=3 → ② 升级到 6 个并行 reviewer
  │          Final = ① + ②(×6) + ③(×3)
  │
  ├─ Step 4: 构建 delegate_task 调用
  │    根据 Final Patterns 生成具体 task goals + toolsets
  │
  └─ Step 5: 执行
       并行分派 → 质量门 → 汇总交付
```

---

## 决策示例

### 示例 A: "审查所有服务的 SQL 注入风险"

```
Step 1: Task Type = T1 Audit
  → Default: ① + ② + ③

Step 2: D-Scores
  D1=3 (50+ 文件批量) → ② 升级: N 个 reviewer
  D2=0 (单一领域)
  D3=3 (安全关键)   → ③ 升级: 3 verifier（误报/漏报/修复方案质量）
  D4=0 D5=0 D6=0 D7=0 D8=0
  
Step 3: Final = ① + ②(×N) + ③(×3)
  → Classifier 分文件组 → N 个 reviewer 并行 → 汇总 → 3 verifier 交叉验证
```

### 示例 B: "选一个最适合的技术栈"

```
Step 1: Task Type = T2 Decision
  → Default: ④ + ⑤

Step 2: D-Scores
  D1=1 (可拆为性能/生态/团队 3 个维度，但相互关联)
  D2=0 D3=1 D4=2 D5=2 D6=0 D7=1 D8=1

Step 3: Final = ④ + ⑤（默认已覆盖，无上调触发）
  → 3 个 generator（不同偏好）→ Filter → Pairwise → Winner
```

### 示例 C: "帮我搞定上线前的所有事"

```
Step 1: Task Type = T7 Execute（无法归类）→ 无默认

Step 2: D7=3（一句话需求）→ 先 Clarify
  "上线涉及哪些环节？代码部署/数据迁移/监控告警/回滚方案/通知团队？"
  
Step 3: Clarify 后 → "代码部署 + 监控 + 通知"
  → 重新分类: T4 Build（部署）+ T1 Audit（检查）+ T7 Execute（通知）
  → D2=2（跨 3 领域）→ ① Classify 先分领域
  → 领域 1（部署）: T4 → ② Fanout
  → 领域 2（检查）: T1 → ② + ③
  → 领域 3（通知）: T7 → 直接执行
```

---

## 任务类型识别关键词表

```
T1 Audit:
  "审查" "审计" "检查" "扫描" "巡检" "排查隐患"
  "review" "audit" "inspect" "scan" "check"
  + 多目标（文件/服务/配置）

T2 Decision:
  "选哪个" "帮决策" "对比" "评估" "推荐" "方案选型"
  "choose" "compare" "evaluate" "recommend" "tradeoff"
  + 多个候选方案

T3 Research:
  "调研" "研究" "分析" "探索" "了解" "是什么" "为什么"
  "research" "investigate" "explore" "analyze" "understand"
  + 多维度/开放式

T4 Build:
  "写" "实现" "开发" "创建" "搭建" "构建" "建一个"
  "write" "implement" "build" "create" "develop"
  + 具体产出物

T5 Debug:
  "修" "debug" "排查" "为什么出错" "不工作" "报错" "bug"
  "fix" "troubleshoot" "diagnose" "broken" "error"
  + 异常现象描述

T6 Creative:
  "头脑风暴" "起名" "想点子" "创意" "灵感" "发散"
  "brainstorm" "ideate" "creative" "name this" "generate ideas"
  + 发散性需求

T7 Execute:
  单一步骤、明确指令、无拆解需求
  不触发本技能，直接执行
```
