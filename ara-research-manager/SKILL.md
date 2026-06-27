---
name: ara-research-manager
description: 研究过程捕获器——在论文研究 session 结束后，三阶段流水线（Harvester→Router→Maturity Tracker）自动扫描本轮工作，将决策/实验/死胡同/声明写入 ara/ 四层结构。仅论文研究场景触发，常态化业务不加载。
version: 1.0.0
license: MIT (adapted from AmberLJC/Agent-Native-Research-Artifact)
triggers:
  - 记录研究进展
  - ara capture
  - 研究 session 结束
  - 存档研究过程
  - /research-manager
metadata:
  hermes:
    tags: [research, capture, trace, provenance]
    related_skills: [ara-compiler, ara-rigor-reviewer]
    scope: research-only
  upstream: https://github.com/AmberLJC/Agent-Native-Research-Artifact
---

# ARA Research Manager · 研究过程捕获器

**仅论文研究场景触发。** 常态化业务对话（如飞书文档、架构图、HTML 页面等）不加载此技能。

## 何时触发

| 触发词 | 场景 |
|--------|------|
| "记录研究进展" / "ara capture" | 用户主动要求存档当前 session 的研究产出 |
| "研究 session 结束" / "存档研究过程" | 一个研究阶段结束时 |
| "/research-manager" | 显式调用 |

**不触发**：常规对话、部署、设计、写作（除非用户明确说在做论文研究且要求存档）。

---

## 核心原则

**渐进结晶**：不强制过早结构。观察先进入暂存区，只有在外部可验证的"结晶信号"出现时才固化到 logic/ 层。

**两层可变性**：
- `ara/logic/` — 可变，是当前最优理解
- `ara/trace/` + `ara/staging/` — 只追加，不可修改（除非设置前向指针）

---

## 三阶段流水线

每次触发时执行：

### Stage 1 — Context Harvester（上下文收割器）

扫描本 session 中已发生的操作（通过回顾对话内容和工具输出），提取研究显著事件：

- **AI 执行的动作**：实验运行、代码编辑、文件创建、文献搜索、数据分析
- **研究者表达的方向**：假设提出、设计选择、方法放弃、结论确认

输出候选事件列表。

### Stage 2 — Event Router（事件路由器）

对每个候选事件分类并路由：

**直接路由（journey facts → `ara/trace/exploration_tree.yaml`）**：

| 类型 | 触发信号 | 必含字段 |
|------|---------|---------|
| `decision` | 在多个选项中做了选择 | choice, alternatives, evidence |
| `experiment` | 代码/分析产生了结果 | result, evidence |
| `dead_end` | 方法被放弃/假设被证伪 | hypothesis, failure_mode, lesson |
| `pivot` | 证据驱动的方向转变 | from, to, trigger |
| `question` | 新的研究方向被打开 | description |

**暂存路由（interpretations → `ara/staging/observations.yaml`）**：

| 候选类型 | 触发信号 | 固化目标 |
|----------|---------|---------|
| `claim` | "我认为…" / "系统达到了…" | logic/claims.md |
| `heuristic` | "技巧是…" / "需要…" | logic/solution/heuristics.md |
| `constraint` | "这仅在…条件下有效" | logic/solution/constraints.md |
| `architecture` | 系统设计陈述 | logic/solution/architecture.md |

所有条目附带来源标记：
- `user` — 研究者本人确认
- `ai-suggested` — AI 提出但未经确认
- `ai-executed` — AI 自动执行
- `user-revised` — AI 提出 + 用户修改后确认

### Stage 3 — Maturity Tracker（成熟度追踪器）

遍历 `staging/observations.yaml`，检查是否满足以下四个结晶信号之一：

1. **话题放弃** — 最近 5 轮未涉及该话题 + open_threads 未引用
2. **口头确认** — 用户明确说"对"/"确认"/"就用这个"
3. **实证解决** — 绑定实验已产出结果 + 研究者评论。**若实验证伪，固化为 dead_end 而非 claim**
4. **制品依赖** — 下游制品（decision/config/code）已依赖该观察

满足信号 → 从暂存提升到对应 logic/ 层，标注 `Crystallized via: <signal>`, `From staging: <id>`。

**默认不提升**。过早结晶是此设计要防止的失败模式。

---

## 目录结构

研究项目根目录下自动创建：

```
ara/
  PAPER.md                    # 根清单 + 层索引
  logic/                      # 认知层 — 当前最优理解
    claims.md                 #   可证伪声明 + 证据指针
    experiments.md            #   实验计划
    problem.md                #   研究空白 + 关键洞察
    solution/
      architecture.md         #   系统设计
      algorithm.md            #   算法伪代码
      heuristics.md           #   关键启发式
      constraints.md          #   边界条件
    related_work.md           #   类型化依赖图
  src/                        # 物理层 — 可执行代码
    configs/                  #   超参 + 理由
    environment.md            #   依赖 + 硬件 + 种子
  trace/                      # 探索图 — 完整研究 DAG
    exploration_tree.yaml     #   五类节点 + 死胡同
  staging/                    # 暂存区 — 等待结晶
    observations.yaml         #   暂存观察
  evidence/                   # 证据层 — 原始输出
    tables/                   #   结果表
    figures/                  #   图表
```

---

## 使用示例

```
用户："记录研究进展"

Hermes 加载 ara-research-manager，扫描本 session：
→ 发现 1 个 experiment（对比了三种 embedding 模型）
→ 发现 1 个 decision（选用了 bge-large）
→ 发现 1 个 dead_end（openai embedding 成本过高放弃）
→ 暂存 1 个 claim（bge-large 在中文场景优于 openai）

写入 ara/trace/exploration_tree.yaml（新增 experiment/decision/dead_end 节点）
写入 ara/staging/observations.yaml（新增 claim 候选）

输出：
"已存档：1 实验 · 1 决策 · 1 死胡同 · 1 暂存声明
 ara/trace/exploration_tree.yaml 已更新
 暂存声明 O01 等待结晶信号"
```

---

## 工具适配

| 上游 (Claude Code) | Hermes |
|---------------------|--------|
| Read | read_file |
| Write | write_file |
| Edit | patch |
| Glob | search_files(target='files') |
| Grep | search_files(target='content') |

---

## 技术说明

- 上游：Orchestra-Research/Agent-Native-Research-Artifact (MIT)
- 本技能为上游 research-manager 的 Hermes 适配版
- 仅在论文研究场景触发，不增加常态化业务负担
