---
name: answer
description: AI Native'S Workflow(er) — 7 阶段结构化工作流编排器。适用于任何从零开始的复杂构建任务：新业务/新产品/新技能/新方案/新流程/新系统/调研分析/策略规划/项目启动/决策支持/汇报演示/预算规划/复盘总结/运营营销/品牌策划/架构设计/迭代优化。以 design-flow 编排范式为核心，串联 clarify → brief → architect → standards → decompose → build → review。触发：answer / 梳理思路 / 从零开始 / 帮我规划 / 设计方案 / 启动项目 / 拆解问题 / 写方案 / 做BP / SOP / 做复盘 / 运营方案 / 营销计划 / from scratch / plan this 等 100+ 关键词。
version: 1.6.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [workflow, design-flow, builder, orchestrator]
    related_skills: [advanced-elicitation, editorial-review-prose, editorial-review-structure, blue-team, huashu-design, feishu-html, feishu-doc, trip-landing, pm-prioritization-frameworks, stakeholder-mapping, opportunity-solution-tree]
triggers:
  # 显式调用
  - "answer"
  - "AI原生工作流"
  - "用answer"
  - "workflow this"
  # 规划/设计/构建类（高置信度）
  - "从零开始规划"
  - "从零开始建"
  - "从零开始做"
  - "从无到有"
  - "结构化规划"
  - "系统化设计"
  - "帮我规划一个"
  - "帮我设计一个"
  - "帮我搭建"
  - "帮我构建"
  - "帮我建一个"
  # 方案/提案/计划类
  - "写一个方案"
  - "做一个方案"
  - "设计方案"
  - "方案框架"
  - "方案规划"
  - "商业计划书"
  - "做一份BP"
  - "写BP"
  - "提案"
  - "建议书"
  - "立项"
  # 项目/产品启动类
  - "启动一个项目"
  - "启动新项目"
  - "做一个新产品"
  - "做一个新功能"
  - "开发一个"
  - "搭一个框架"
  - "搭框架"
  - "搭骨架"
  # 流程/SOP/标准化类
  - "设计一个流程"
  - "写SOP"
  - "做SOP"
  - "标准化"
  - "流程优化"
  - "流程设计"
  - "制度设计"
  # 分析/拆解/梳理类
  - "帮我梳理"
  - "帮我厘清"
  - "拆解这个问题"
  - "拆解一下"
  - "理一下逻辑"
  - "帮我分析一下"
  - "分析框架"
  # 策略/规划/调研类
  - "制定策略"
  - "做一个规划"
  - "做规划"
  - "年度规划"
  - "季度规划"
  - "调研方案"
  - "竞品分析"
  - "做一个调研"
  # 决策/评估类
  - "帮我做决策"
  - "几个方案怎么选"
  - "方案评估"
  - "可行性分析"
  - "评估方案"
  # 技能/工具创建类
  - "创建一个技能"
  - "建一个skill"
  - "写一个skill"
  - "做一个工具"
  - "设计一个技能"
  # 汇报/演示/PPT类
  - "做一个汇报"
  - "写汇报"
  - "汇报方案"
  - "做PPT"
  - "演示方案"
  - "汇报材料"
  # 预算/资源/成本类
  - "做预算"
  - "预算方案"
  - "资源规划"
  - "成本分析"
  - "做成本分析"
  # 复盘/总结/回顾类
  - "做一个复盘"
  - "复盘方案"
  - "总结分析"
  - "回顾分析"
  - "做复盘"
  # 运营/营销/活动类
  - "运营计划"
  - "运营方案"
  - "营销方案"
  - "营销计划"
  - "推广方案"
  - "活动方案"
  - "活动策划"
  - "品牌方案"
  - "品牌策划"
  # 迭代/优化/改进类
  - "优化方案"
  - "改进方案"
  - "迭代计划"
  - "做迭代"
  - "版本规划"
  # 架构/组织/体系类
  - "设计组织架构"
  - "组织架构设计"
  - "指标体系"
  - "KPI设计"
  - "设计指标体系"
  # 口语化变体（精准匹配）
  - "出个方案"
  - "出方案"
  - "盘一下"
  - "捋一下"
  - "理一理"
  - "过一遍"
  # 英文等价触发
  - "plan this"
  - "design this"
  - "architect this"
  - "blueprint this"
  - "think this through"
  - "structure this"
  - "map this out"
  - "from scratch"
  - "build a plan"
---

# answer — AI Native'S Workflow(er)

> **answer = AI Native'S Workflow(er)**
>
> 拆解这个名字：
> ```
> A I Native' S Workflow( ER )
> └─┘ └───┘└─┘ └────┘└───┘
> A N S W ER
> ```
>
> - **answer**（答案）—— 给你结构化找到答案的路径
> - **AI Native'S Workflow(er)**（AI 原生的 工作流者）—— 赋予 AI 结构化思考的能力
>
> 以 `design-flow` 编排范式为核心，将 grill-me / design-brief / information-architecture / design-tokens / brief-to-tasks / design-review 的**方法论内化**，适配到新业务构建、新技能创建、新方案规划等通用领域。

## 触发条件

### 通用领域触发矩阵

7阶段工作流覆盖9大业务领域，45个子场景。

#### AI / 技术产品
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| AI产品从零构建 | 用户要从零搭建AI产品 | "answer: 做一个AI客服产品" |
| Agent系统设计 | 用户需要设计Multi-Agent系统 | "从零开始设计一个Agent编排系统" |
| RAG系统搭建 | 用户需要搭建RAG系统 | "从零规划一个企业RAG知识库" |
| 模型选型决策 | 用户需要系统化模型选型 | "梳理一下我们应该用哪个模型" |
| AI应用商业化 | 用户需要AI产品的商业化方案 | "梳理一下这个AI工具的变现路径" |

#### 数字产品 / SaaS
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| SaaS产品启动 | 用户要启动SaaS产品 | "从零开始做一个SaaS工具" |
| 产品功能规划 | 用户需要系统化功能规划 | "梳理这个产品的MVP和roadmap" |
| 技术架构决策 | 用户需要架构方案设计 | "design this: 技术栈选型和架构方案" |
| 用户增长方案 | 用户需要系统化增长策略 | "answer: 用户增长策略" |
| 定价模式设计 | 用户需要定价方案设计 | "梳理一下这个SaaS的定价模式" |

#### 业务流程 / 运营
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| SOP流程设计 | 用户需要设计操作流程 | "设计一个客服SOP流程" |
| 运营方案策划 | 用户需要运营策划案 | "做一个暑期营销运营方案" |
| 数字化转型 | 用户需要数字化转型方案 | "梳理一下传统企业数字化转型路径" |
| 组织架构设计 | 用户需要组织架构方案 | "设计这个团队的OKR和架构" |
| 项目管理方案 | 用户需要项目管理系统 | "梳理一下多项目管理流程" |

#### 市场营销 / 品牌
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 营销方案策划 | 用户需要营销策划案 | "做一个新产品上市营销方案" |
| 品牌策略规划 | 用户需要品牌策略 | "从零梳理这个品牌的定位和策略" |
| 内容营销体系 | 用户需要内容营销规划 | "梳理一下内容营销的选题和分发" |
| 社交媒体策略 | 用户需要社媒运营方案 | "answer: 社交媒体运营策略" |
| 活动策划 | 用户需要活动方案 | "设计一个线上发布会活动方案" |

#### 商业策略 / 创业
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 商业模式设计 | 用户需要商业模式设计 | "梳理这个项目的商业模式" |
| 商业计划书 | 用户需要BP | "写一个BP" |
| 市场进入策略 | 用户需要市场进入方案 | "梳理一下进入这个市场的策略" |
| 竞品分析 | 用户需要系统化竞品分析 | "answer: 竞品深度分析" |
| 融资方案 | 用户需要融资规划 | "梳理一下A轮融资方案" |

#### 技能/工具创建
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| Skill创建 | 用户需要创建Hermes技能 | "创建一个skill" |
| 工具开发 | 用户需要开发新工具 | "从零做一个自动化脚本工具" |
| 工作流设计 | 用户需要设计自动化工作流 | "设计一个文档自动生成工作流" |
| 集成方案 | 用户需要系统集成方案 | "梳理一下飞书+GitHub集成方案" |

#### 调研分析
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 行业调研 | 用户需要系统化行业分析 | "梳理一下这个行业的竞争格局" |
| 用户研究 | 用户需要用户研究方案 | "从零规划用户访谈和调研" |
| 可行性分析 | 用户需要可行性研究 | "这个项目能不能做，梳理一下" |
| 技术调研 | 用户需要技术调研方案 | "梳理一下微服务vs单体的选型" |

#### 复盘/汇报
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 项目复盘 | 用户需要系统化复盘 | "做一个项目复盘" |
| 年度总结 | 用户需要年度总结 | "写一个年度总结报告" |
| 投资人汇报 | 用户需要投资人更新 | "做一个investor update" |
| 绩效回顾 | 用户需要绩效回顾方案 | "梳理一下团队的OKR回顾" |

#### 内容/创作
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| 内容策略 | 用户需要内容策略规划 | "梳理一下这个账号的内容策略" |
| 课程设计 | 用户需要课程体系设计 | "设计一个AI入门课程大纲" |
| 知识库搭建 | 用户需要知识库规划 | "梳理一下团队知识库的结构" |
| 视频系列 | 用户需要视频内容规划 | "规划一个技术视频系列" |

### 自动触发场景（按置信度分层）

**Tier 1 — 显式调用（100% 触发）**：
- "answer this" / "用 answer" / "workflow this"
- "AI 原生工作流" / "帮我厘清" / "结构化规划"

**Tier 2 — 高置信度场景（触发，并告知用户已加载 answer）**：

| 场景分类 | 信号示例 | 适配领域 |
|---------|---------|---------|
| 从零构建 | "从零开始做一个XX"、"从无到有建一个"、"搭一个框架" | 自动判断 |
| 方案设计 | "写一个方案"、"做一个提案"、"商业计划书"、"BP" | 📋 新方案 |
| 项目启动 | "启动一个项目"、"做一个新产品"、"开发一个新功能" | 🏢 新业务 |
| 流程标准 | "设计一个流程"、"写 SOP"、"流程优化"、"标准化" | 🔄 流程规范 |
| 策略规划 | "制定策略"、"怎么做规划"、"调研方案"、"竞品分析" | 🔍 分析调研 |
| 技能创建 | "创建一个技能"、"写一个 skill"、"做一个工具" | 🛠️ 新技能 |
| 汇报演示 | "做一个汇报"、"写汇报"、"做 PPT"、"演示方案" | 📋 新方案 |
| 复盘总结 | "做一个复盘"、"总结分析"、"回顾分析" | 🔍 分析调研 |
| 运营营销 | "运营方案"、"营销计划"、"活动策划"、"品牌方案" | 📋 新方案 |
| 架构体系 | "设计组织架构"、"指标体系"、"KPI 设计" | 🏢 新业务 |
| 迭代优化 | "优化方案"、"迭代计划"、"版本规划" | 自动判断 |

**Tier 3 — 上下文触发（结合复杂度判断）**：
- "帮我分析一下" — 如果话题涉及多步骤决策 → 触发 answer
- "帮我梳理" — 如果内容涉及多个模块/阶段 → 触发 answer
- "拆解" — 如果问题有多个子问题 → 触发 answer
- "评估" — 如果有多个方案需要对比 → 触发 answer
- "不知道怎么开始" — 任何不够清晰的任务 → 触发 answer
- "盘一下" / "捋一下" / "理一理" / "过一遍" — 口语化梳理请求 → 触发 answer
- "plan this" / "design this" / "think this through" — 英文等价请求 → 触发 answer

**不触发 answer 的场景**（直接处理，不走工作流）：
- 单一事实查询（"今天天气怎么样"）
- 已有明确答案的问题（"这段代码哪里错了"）
- 简单操作（"帮我发个消息"、"打开XX文件"）
- 已有成熟方案的重复性任务（"按上次的流程再做一次"）

### 领域自动识别（扩展版）

根据用户描述自动判断最佳匹配领域。判断优先级如下：

| 领域 | 关键词/模式 | 典型场景 | Brief 模板变体 |
|------|-----------|---------|---------------|
| 🛠️ **新技能** | skill、技能、Hermes、工具、CLI、命令、触发、API | 创建 trip-summary 技能、写一个天气查询 skill | 技能接口/I/O/依赖 |
| 🏢 **新业务/产品** | 商业模式、产品、市场、营收、用户、获客、增长、MVP、启动、功能、模块、系统 | 设计一个会员体系、做一个探洞小程序 | 商业意图/价值主张 |
| 📋 **新方案** | 计划、提案、策略、方案、BP、商业计划、汇报、建议书、立项 | 暑期营销方案、年度规划汇报 | 受众分析/方案逻辑链 |
| 🔄 **流程/SOP** | 流程、SOP、标准化、规范、制度、操作手册、SOP、优化流程 | 客户接待 SOP、内容发布流程 | 步骤序列/角色/规则 |
| 🔍 **分析/调研** | 分析、调研、研究、竞品、评估、可行性、拆解、梳理 | 竞品分析报告、市场调研方案 | 分析框架/假设/数据源 |
| 🎯 **决策支持** | 决策、对比、选择、权衡、几个方案、怎么选 | 选供应商、选技术方案 | 方案对比/评估标准 |

**匹配规则**：
1. 多个关键词命中时，取优先级最高的领域（技能 > 业务 > 方案 > 流程 > 分析 > 决策）
2. 无法明确判断时，默认使用「新方案」模板，并询问用户确认领域
3. 用户可随时覆盖自动判断（"不，这不是技能，是方案"）

🔴 **CHECKPOINT**：领域识别完成后，向用户确认——"识别为 {领域标签}，走对应的 7 阶段追问流程。正确吗？" 确认后再进入 Phase 1。

**领域覆盖后**：自动加载 `references/domain-mapping.md` 中对应领域的追问清单和模板变体。

---

## 7 阶段编排序列

```
1. Clarify    → 决策树遍历，追问到底（grill-me 方法论）
2. Brief      → 结构化简报，记录意图/目标/约束（design-brief 方法论）
3. Architect  → 定义结构/层次/关系/流程（information-architecture 方法论）
4. Standards  → 建立可复用标准/模式/规范（design-tokens 方法论）
5. Decompose  → 拆解为独立可验证的增量任务（brief-to-tasks 方法论）
6. Build      → 按任务逐步构建交付物
7. Review     → 对照简报逐项检查（design-review + blue-team 方法论）
```

### 编排规则

1. **开始前**：告知完整 7 阶段序列，询问是否跳过某些阶段（常见跳过的：已有清晰思路可跳过 Clarify；单一产出可跳过 Architect）
2. **每阶段前**：宣布进入哪个阶段、产出什么、确认是否继续
3. **每阶段后**：总结产出（文件名、关键决策、开放问题），询问「进入下一阶段？」
4. **阶段间检查**：前一阶段的输出是否影响下一阶段？（如 Brief 中的领域设定会影响 Standards 的规范模板）
5. **可随时暂停**：用户说"够了"即停止，总结当前进度和下一步
6. **活文档纪律**：`{answername}_工作流全记录` 是活文档（Living Document）——Phase 3 的关键架构决策、Phase 6 的意外发现和决策记录、Phase 7 的成果回顾，都必须持续更新到文档中。进度、决策、发现全在一处，确保跨会话中断后可从文档恢复。

### 产出目录

所有产出创建为飞书在线文档，归档到 Wiki 节点 `J4EewYIT2ieFuwkRWbxcgWbFnhe`（AI Native 工作流）下。

**默认模式：合并文档**（用户偏好）。Phase 1-5 合并为单一飞书文档 `{answername}_工作流全记录`，各阶段作为一级章节。Phase 6 Build 产出最终交付物（方案文档/报告等），Phase 7 Review 追加到工作流记录文档末尾。

```
J4EewYIT2ieFuwkRWbxcgWbFnhe (AI Native 工作流)
└── {answername}_工作流全记录        ← Phase 1-5 合并 + Phase 7 Review 追加
    ├── # Phase 1: Clarify
    ├── # Phase 2: Brief
    ├── # Phase 3: Architect
    ├── # Phase 4: Standards
    ├── # Phase 5: Decompose
    └── # Phase 7: Review
└── {最终交付物}                     ← Phase 6 Build 产出（方案文档/报告等）
```

**分文档模式**（仅在用户明确要求时使用）——每阶段独立文档：

```
J4EewYIT2ieFuwkRWbxcgWbFnhe (AI Native 工作流)
└── {answername}/
    ├── CLARIFY_{answername}
    ├── BRIEF_{answername}
    ├── ARCHITECTURE_{answername}
    ├── STANDARDS_{answername}
    ├── TASKS_{answername}
    ├── BUILD_LOG_{answername}
    └── REVIEW_{answername}
```

**注意**：Phase 1-5 产出完成后，如果用户要求合并已有文档，使用 `lark-cli wiki +node-delete --node-token TOKEN --obj-type wiki --yes` 删除分散文档（注意 `--obj-type wiki` 而非 `docx`），创建合并文档后重新写入。

**创建文档方法**：必须使用 v2 API 一步法。**禁止两步法**（Wiki API 建节点 + docs update 写内容）——该模式在 lark-cli v1.0.40–v1.0.44 上返回 `ok:true` 但文档永远为空。

```bash
# ✅ 一步法（唯一可靠方式）
cd /tmp
cat > doc.md << 'EOF'
# {标题}

{markdown 内容}
EOF

lark-cli docs +create --api-version v2 --doc-format markdown \
  --title "{文档标题}" --content @doc.md \
  --parent-token {parent_node_token} --as bot
```

**写入后校验**：
```bash
lark-cli docs +fetch --api-version v2 --doc {document_id} --as bot
# 确认 revision_id > 1 且 blocks 数 > 0
```
---

## 阶段详情

### Phase 1: Clarify（决策树遍历）

**来源**：grill-me — 无死角追问，逼出所有设计决策

**目标**：在动手之前，遍历决策树的每一个分支，确保所有前提假设都被显式化。

**方法**：
1. 从用户初始描述中提取关键决策点，展开为决策树
2. 逐分支追问，每个追问提供推荐答案
3. 用代码库/数据源探索替代提问（能查到的不要问）
4. 追问维度（按领域适配）：

| 追问维度 | 新业务 | 新技能 | 新方案 |
|---------|--------|--------|--------|
| 核心对象 | 用户是谁？JTBD？ | 用户是谁？什么场景触发？ | 受众是谁？决策标准？ |
| 成功定义 | 什么算成功？（量化） | 什么算"这个技能好用"？ | 什么算方案通过？ |
| 边界约束 | 预算/时间/团队/合规 | 依赖的技能/工具/平台 | 截止日期/形式/篇幅 |
| 核心假设 | 最不确定的假设是什么？ | 能力边界的最大未知？ | 最薄弱的逻辑环节？ |
| 反目标 | 明确不做什么？ | 明确不覆盖哪些场景？ | 明确不涉及哪些内容？ |

> 完整的 6 领域追问清单（含 🔄流程/SOP、🔍分析/调研、🎯决策支持）见 `references/domain-mapping.md`，Clarify 阶段会自动加载对应领域的追问模板。

**产出**：`CLARIFY_{answername}.md` — 决策树记录、关键决策、开放问题

**模板**：
```markdown
# Clarify: {answername}

## 决策树
### Q1: {核心问题}
- 推荐答案：{recommendation}
- 用户选择：{answer}
- 影响的分支：{downstream decisions}

### Q2: ...
...

## 关键决策摘要
1. {decision 1}
2. {decision 2}

## 仍开放的追问
- {open question 1}（将在 Phase 2 Brief 中作为假设记录，或在后续阶段回答）

**处理开放问题**：无法在此阶段回答的开放问题，记录到 Brief 的「待验证假设」字段中，供后续阶段引用。

🔴 **CHECKPOINT**：确认决策树已遍历完毕、关键决策已记录，再进入 Phase 2。
```

**过渡语**："我们已遍历核心决策树。下面把结论沉淀为结构化简报。继续？"

---

### Phase 2: Brief（结构化简报）

**来源**：design-brief — 交互式访谈 + 代码库探索

**目标**：将所有澄清结果结构化，产出可被后续阶段引用的单一真源。

**方法**：
1. 基于 Phase 1 的决策树结果，填充简报模板
2. 探索已有资源（对于技能创建：已有技能文件；对于业务：已有飞书文档/数据）
3. 为每个决策项提供推荐答案

**产出**：`BRIEF_{answername}.md` — 结构化简报

**模板**（领域适配）：

```markdown
# {领域标签} Brief: {answername}

## 问题定义
{从用户/受众角度描述核心问题，不是技术描述，不是商业指标}

## 目标方案
{这个方案做什么，描述为体验/流程，而非功能列表}

## 核心原则（最多 3 条）
1. **{原则名}** — {实践中的含义，应解决一个张力}
2. ...
3. ...

## 价值主张（JTBD 6-part — 数字产品/服务类项目必填）

> 🆕 借鉴 pm-skills `value-proposition`——用 JTBD 框架定义价值主张，替代空泛的「我们提供XX」。

对每个目标用户群：

| 维度 | 说明 | 示例 |
|------|------|------|
| **Who（谁）** | 目标用户的具体画像 | 「中型企业 IT 经理，每天处理 50+ 审批」 |
| **Why（为什么）** | 他们的痛点/未满足需求 | 「现有工具审批慢、追溯难、跨部门协调靠微信」 |
| **What before（现状）** | 他们现在怎么做的 | 「Excel + 微信 + 邮件三件套，平均每单 3 天」 |
| **How（我们怎么做）** | 我们的解决方式 | 「一站式审批：自动路由 + 移动端秒批 + 全程留痕」 |
| **What after（改善后）** | 使用后的改善结果 | 「审批时间从 3 天 → 2 小时，合规审计秒级响应」 |
| **Alternatives（替代方案）** | 他们现在用什么替代 | 「钉钉审批（但缺乏定制化）、自研系统（维护成本高）」 |

## 产品战略画布（数字产品/SaaS/AI方案类可选）

> 🆕 如果产出是数字产品/SaaS/AI 产品的战略方案，可用 9-section Product Strategy Canvas 替代或补充上面的通用 Brief 模板。
> 
> 9-section: Vision → Market Segments → Relative Costs → Value Propositions → Trade-offs → Key Metrics → Growth → Capabilities → Can't/Won't (Defensibility)
> 
> 详见 `references/product-strategy-canvas.md`。

## 领域约束
- 平台/环境：{已有技能、工具、平台限制}
- 时间/资源：{截止日期、预算、团队}
- 合规/品牌：{必须遵守的规范}

## 成功标准

每条标准必须是可观测的、人类可验证的。格式：「条件 → 操作 → 预期结果」

- **SC-1**：{描述}。验证方法：{具体操作}，预期结果：{可观测输出}
- **SC-2**：{描述}。验证方法：{具体操作}，预期结果：{可观测输出}

> **示例（方案类）**：
> - **SC-1**：方案逻辑无断层。验证方法：蓝军审查 Phase 2 死亡假设全部有应对，预期结果：蓝军报告无 Must Fix
> - **SC-2**：交付物可在 10 分钟内被目标受众理解。验证方法：找 1 名未参与项目的人阅读后复述核心观点，预期结果：复述准确率 ≥ 80%
>
> **示例（技能类）**：
> - **SC-1**：技能可从空状态触发。验证方法：在干净 Hermes 环境中说「触发词」，预期结果：Hermes 加载该技能并开始执行 Phase 1

> 此格式借鉴 execplan 的 Observable Outcomes 方法论——验收标准必须是人类可感知的行为，而非内部属性。

## 已有资产
{可以复用的技能、文档、代码、数据}

## 产出物清单
| 产出物 | 类型 | 接收方 |
|--------|------|--------|
| {output 1} | {doc/deck/skill/html} | {audience} |

## 不做什么
{明确排除的内容，防止范围蔓延}
```

**过渡语**："简报已结构化。下面我们定义架构——结构、层次、流程。继续？"

---

### Phase 3: Architect（结构设计）

**来源**：information-architecture — 导航/内容层级/用户流

**目标**：定义产出物的骨架：模块划分、层级关系、信息流、关键路径。

**方法**：
1. 基于 Brief 中的产出物清单，逐项设计结构
2. 对于复杂产出（多页面、多子技能、多阶段方案），先画结构树
3. 定义模块间依赖关系
4. 定义关键路径（用户/受众如何使用这个产出）

**产出**：`ARCHITECTURE_{answername}.md` — 结构设计文档

**模板**：

```markdown
# Architecture: {answername}

## 结构总览

{层级树，缩进表示嵌套}

- 模块 A
  - 子模块 A1
  - 子模块 A2
- 模块 B
  - 子模块 B1

## 模块关系与依赖

| 模块 | 依赖 | 被依赖 | 备注 |
|------|------|--------|------|
| A | — | B | 基础模块 |
| B | A | — | 依赖 A 的数据 |

## 关键路径（用户流）

### 路径 1: {路径名}
1. 受众/用户进入 {入口}
2. 看到 {内容/提示}
3. 采取行动：{action}
   - 若 {条件A} → {结果}
   - 若 {条件B} → {结果}
4. 到达 {终点}

## 信息层级

### {模块名}
1. **最高优先级**：{内容} — 理由：{why}
2. **次优先级**：{内容} — 理由：{why}
3. **第三优先级**：{内容} — 理由：{why}

## 增长适配
{哪些部分会随时间扩展？如何处理？（分类/分页/归档）}

## 接口规格（技术类项目时使用）

> 借鉴 execplan 的 Interface Specs 方法论——对技术类项目显式定义模块接口。

| 模块 | 输入 | 输出 | 依赖 |
|------|------|------|------|
| {模块A} | {类型 / 格式 / 示例} | {类型 / 格式 / 示例} | {外部服务的 API 版本 / 认证方式} |
| {模块B} | {类型} | {类型} | — |

### {模块名} 错误处理
- 失败时回退行为：{描述}。
```

**注意**：如果产出是单一文件/简单结构（如单篇方案文档），此阶段可快速通过——仅需确认内容大纲和层级（创建一个简化的 ARCHITECTURE 文档，只包含「结构总览」和「信息层级」两节，跳过模块关系和增长适配）。

### Architect 视觉增强（精装修模式）

当用户对 Phase 3 结构表达"看上去不够丰富"时，在不增加内容的条件下添加视觉层：

1. **ASCII 架构全景图** — 用框图展示 Days × Modules 嵌套关系，标注子模块核心动作
2. **三层能力映射表** — 认知层/操作层/创造层，每层标注覆盖模块和学员获得
3. **时间配比** — Day 1/Day 2 实操/讲解/茶歇百分比分布

原则：**内容一个不改，穿上视觉外衣**。不改变 Brief/Standards 中定义的任何设计决策。

**过渡语**："架构已定义。下面建立标准和规范——复用模式、命名约定、质量基线。加载 domain-mapping 获取领域特定的规范模板。继续？"

---

### Phase 4: Standards（标准规范）

**来源**：design-tokens — 建立可复用模式

**目标**：定义可复用的标准、模式、命名约定、质量基线，确保产出的一致性。

**方法**：
1. 识别可复用的模式（技能创建时的命名约定、方案文档的段落模板）
2. 加载 `references/domain-mapping.md`，根据当前领域加载对应的 Standards 模板变体
3. 定义标准（格式、命名、结构）
4. 定义质量基线（什么算"完成"）

**产出**：`STANDARDS_{answername}.md` — 标准规范文档

**模板**：

```markdown
# Standards: {answername}

## 命名约定

| 概念 | 命名 | 规则 |
|------|------|------|
| {concept 1} | {name} | {rule} |

## 格式规范
- 文件格式：{markdown/html/json/...}
- 编码：UTF-8
- 换行：LF

## 复用模式

### 模式 1: {模式名}
- **何时使用**：{trigger}
- **模板**：\`\`\`{示例}\`\`\`
- **已有参考**：{链接到已有实例}

## 质量基线（DoD）

每个产出物必须满足：

| # | 检查项 | 通过标准 |
|---|--------|---------|
| 1 | {item} | {standard} |
| 2 | {item} | {standard} |

## 反模式（禁止）

| # | 反模式 | 原因 |
|---|--------|------|
| 1 | {anti-pattern} | {why bad} |
```

**过渡语**："标准已建立。下面将简报拆解为可独立构建的增量任务。继续？"

---

### Phase 5: Decompose（任务拆解）

**来源**：brief-to-tasks — 垂直切片式拆解

**目标**：将 Brief 中的所有产出物拆解为独立、可验证、可增量交付的任务列表。

**方法**：
1. 每个任务是一个垂直切片——包含结构+内容+验证
2. 任务可独立构建、独立验证
3. 按依赖排序：基础 → 核心 → 润色
4. 每个任务标注：是新创建/复用/修改

**产出**：`TASKS_{answername}.md` — 任务清单

**模板**：

```markdown
# Build Tasks: {answername}

Generated from: BRIEF_{answername}.md
Date: {date}

## Spike（可行性验证）

> 借鉴 execplan 的 Prototyping Milestones 方法论——先验证关键假设，再投入完整构建。

- [ ] **{尖刺任务名}**: {要验证的假设}。_{通过标准：{可观测结果}}。_{若通过 → 进入 Core Task N；若不通过 → 记录到决策日志}。_

## Foundation（基础）
- [ ] **{任务名}**: {一句话描述什么是"完成"}。_{状态：新建 / 复用 / 修改}。_

## Core（核心构建）
- [ ] **{任务名}**: {描述}。_{依赖：{前置任务}}。_
- [ ] **{任务名}**: {描述}。

## Polish（润色与验证）
- [ ] **{任务名}**: {描述}。覆盖：{状态/边界情况}。
- [ ] **Review：运行 answer Phase 7 审查**。

## 执行顺序

```
Task 1 → Task 2 → Task 3 (可与 4 并行)
                    ↘ Task 4 ↗ Task 5
```
```

**任务设计规则**：
- 不允许"创建项目结构"/"初始化仓库"类纯搭建任务
- 每个任务包含内容+验证
- 高风险/不确定的任务排在前面
- 视觉/用户感知优先级高的排在前面

**过渡语**："任务已拆解。下面按顺序逐步构建。是否现在开始构建？"

🔴 **CHECKPOINT**：
1. 任务清单完整（Spike + Foundation + Core + Polish 四组齐全） ✓
2. 每个任务是垂直切片（含内容+验证） ✓
3. **自包含检查**：随机抽取 1 个任务，假设自己是"从没见过这个项目的人"——只看该任务的描述和上下文，能否独立完成？如果不能，缺少什么信息？ ✗
4. 确认后进入 Build。Build 阶段不可逆——开始后按任务顺序执行，不跳回重排。

---

### Phase 6: Build（逐步构建）

**目标**：按 TASKS.md 的顺序，逐个完成任务并在每个任务后验证。

**方法**：
1. 从 Foundation 第一个任务开始
2. 完成后立即验证（对照 Standards 中的 DoD）
3. 🔴 **文档写入后强制校验**：每次用 `lark-cli docs +update --command overwrite` 写入飞书文档后，立刻 `lark-cli docs +fetch` 确认 `revision_id > 1` 且文本内容存在。创建时 revision_id=1 且无文本 = 写入失败。不跳过此步。
4. 打勾 ✅ 标记完成，输出该任务的交付物
5. 确认后进入下一个任务
6. 所有任务完成后，记录构建日志

**产出**：`BUILD_LOG_{answername}.md` + 各任务的交付物

**构建日志模板**：

```markdown
# Build Log: {answername}

## Task 1: {任务名}
- 状态：✅ 完成
- 时间：{开始时间} ~ {结束时间} (UTC+8)，耗时约 {分钟} min
- 产出：{链接/文件路径}
- 调用的技能/工具：{skill_manage / feishu-doc / feishu-html / ...}
- 参数：{关键参数摘要}
- 验证结果：{通过/失败 + 详情}

### 💡 意外发现（如有）
- {实施中发现的非预期行为 / 工具坑 / 边界情况}。_{证据：{复现步骤或输出摘要}}。_

### 🔄 决策记录（如有）
- 决策：{中途改了什么}
- 理由：{为什么}
- 替代方案：{曾考虑但放弃的选项 + 放弃原因}

## Task 2: {任务名}
...
```

**重要**：Build 阶段可能调用其他技能来完成具体交付：
- 需要做 HTML 页面 → 调用 `feishu-html`
- 需要写飞书文档 → 调用 `feishu-doc`
- 需要画架构图 → 调用 `architecture-diagram`
- 需要做行程页 → 调用 `trip-landing`
- 需要创建技能 → 调用 `skill_manage`

### 幂等性要求

> 借鉴 execplan 的 Idempotence 方法论——步骤可安全重复执行，不产生副作用。

- 创建类操作：先检查是否已存在，已存在则跳过（不覆盖）
- 写入类操作：使用 overwrite 模式（重复执行结果一致）
- 部署类操作：重复部署不产生重复资源（OSS 同名文件覆盖）
- 如果某步骤不可幂等（如发送通知），在 BUILD_LOG 中显式标注 ⚠️ 非幂等

### 全局决策日志

> 借鉴 execplan 的 Decision Log 方法论——贯穿 Phase 3 和 Phase 6，记录所有关键决策。

在工作流记录文档末尾维护「## 决策日志」章节：

```markdown
## 决策日志

### D-001: {决策标题}
- 阶段：Phase {3 Architect / 6 Build}
- 决策：{选择了什么方案}
- 理由：{为什么选这个}
- 替代方案：{曾考虑的选项 + 放弃原因}
- 日期/作者：{YYYY-MM-DD} / {作者}
```

**过渡语**："构建完成。现在运行审查——对照简报逐项检查质量。继续？"

---

### Phase 7: Review（质量审查）

**来源**：design-review（对照性审查）+ blue-team（压力测试）+ strategy-red-team（红队攻击）+ pre-mortem（风险分级）

**目标**：对照 Brief 和 Standards，检查所有产出物的质量，暴露逻辑断层和实现偏差。

**方法**：

#### 7.1 对照性审查（design-review 方法论）

逐项检查产出物 vs. Brief：

| 审查维度 | 检查项 |
|---------|--------|
| **完整性** | 所有计划产出物是否全部完成？有无遗漏？ |
| **一致性** | 产出是否与 Brief 中的核心原则一致？ |
| **标准合规** | 是否遵守 Standards 中定义的命名/格式/质量基线？ |
| **依赖闭合** | Architect 中定义的依赖关系是否全部满足？ |
| **受众适配** | 产出物对目标受众是否可用/可理解？ |

#### 7.2 压力测试（blue-team 方法论）

调用 `blue-team` 技能对方案本身进行逻辑审查：
- 本质还原：核心价值主张是什么？
- 死亡假设：如果失败，最可能的死因？
- 苏格拉底追问：未被验证的前提假设？

#### 7.2a 红队攻击（strategy-red-team 方法论 — 战略级方案必用）

> 🆕 借鉴 pm-skills `strategy-red-team` —— 攻击 Load-bearing Assumptions，不是泛泛的风险列表。

适用于：战略方案、PRD、商业计划书、架构决策等**关键决策**文档。对日常方案（活动策划、简单流程 SOP）可选。

**红队审查规则**（与 blue-team 的差异化定位）：

| 维度 | blue-team | strategy-red-team |
|------|-----------|-------------------|
| **审查对象** | 方案整体逻辑 | **Load-bearing Assumptions**（承受性假设） |
| **方法** | 死亡假设 + 苏格拉底追问 | **Steelman-then-Attack**（先建钢人再攻击） |
| **输出** | 问题分级（Must/Should/Could Fix） | **Fail-if + Cheapest Test + Kill Criterion** |
| **目标** | 提升方案质量 | **防止自信地押错注**——找到最便宜的证据来验证或推翻核心假设 |

**红队流程**：

1. **提取每个 claim**：列出方案断言为真的每件事——关于用户、市场、约束、机制、时间线。区分 **Load-bearing claims**（如果假，方案崩溃）和装饰性 claims。只攻击 Load-bearing 的。

2. **Steelman, then Attack**：对每个 Load-bearing claim，先陈述它为真的最强版本，然后攻击那个版本——不是稻草人。攻击弱版本毫无价值。

3. **每个失效模式写成「Fails if ___」**：具体、可证伪。「Fails if 激活率不是真正的瓶颈」优于「执行风险」。

4. **按 (Impact if wrong) × (Likelihood wrong) × (Cheapness to test) 排序**：列表顶部是本周就该测的——高影响、可能出错、测试便宜。

5. **自我反驳，不编造**：默认「这个风险是真的」，除非方案已引用证据反驳。但如果一个 claim 确实有理有据，直接说——红队编造疑虑和橡皮图章一样没用。

6. **每个存活下来的 kill-assumption 给三个动作**：
   - **Fails if**：精确地，什么条件会让方案崩溃
   - **Evidence to get this week**：本周能拿到的具体数据/查询/对话
   - **Kill criterion**：到什么阈值你该停下来或改变方向
   - **Cheapest test**：最小的验证实验

**红队输出模板**：

```
## 红队审查: {方案名}

### Top Kill-Assumptions（按测试便宜度排序，最多5条）
对每条：
- **Claim**: {承受性断言}
- **Fails if**: {具体、可证伪的崩溃条件}
- **Evidence to get this week**: {具体数据来源}
- **Kill criterion**: {停止/转向阈值}
- **Cheapest test**: {最小验证实验}

### 什么站得住脚
{明确说哪些部分理由充分——不编造疑虑}

### 无法评估的部分
{方案未给出足够信息的盲区}
```

**红队纪律**：
- 不稻草人——攻击钢人或别攻击。
- 不泛化风险列表——每一条都针对**这个**方案。
- 不编造——如果站得住，就说站得住。
- 无情排序——最便宜的、影响最大的测试才是整个红队的意义。

#### 7.2b 死亡假设风险分级（pre-mortem Tiger 分级）

> 🆕 对 blue-team 的死亡假设增加 Tigers / Paper Tigers / Elephants 三级分类。

| 级别 | 含义 | 应对 |
|------|------|------|
| **🐯 Tiger** | 高概率 + 高影响 = 真老虎。必须直接应对。 | 缓解方案 + 监控指标 |
| **📄 Paper Tiger** | 看起来吓人但经不起推敲 = 纸老虎。深入分析后发现没那么危险。 | 记录理由，不投入资源 |
| **🐘 Elephant** | 低概率 + 高影响 = 房间里的大象。大家都知道但没人提。 | 明确承认 + if-then 预案 |

**使用方式**：在 blue-team 审查完成后，将每个死亡假设标注 Tiger/Paper Tiger/Elephant 级别。Tiger 项写入 Must Fix，Elephant 写入 Should Fix 并附 if-then 预案。Paper Tiger 记录在「什么站得住脚」中。

#### 7.2b 深度审视（Advanced Elicitation — 可选增强层）

> 🆕 调用 `advanced-elicitation` 技能对产出做多视角审视。

对 Review 中发现的 Must Fix / Should Fix 项，建议运行 2-3 种方法做深度审视：

```
加载 advanced-elicitation，对 Review 中的关键发现运行：
- 方案/决策类 → Pre-mortem + First Principles + Inversion
- 代码/技术类 → Boundary Sweep + 5 Whys + Red Team
- 文案/内容类 → Critique & Refine + Socratic + Steelmanning
```

AE 不会自动运行——Phase 7 结束后提示用户"是否需要对关键发现运行深度审视？"

#### 7.2c 文案质量门禁（Editorial Review — 可选增强层）

> 🆕 调用 `editorial-review-prose` 技能对产出文案做临床级审查。

如果最终交付物包含面向客户的文案：

```
加载 editorial-review-prose（如需贵州之客铁律，同时加载 zhike-content-output 作为 style_guide）
→ 三列表格审查（原文/修订/变更理由）
→ 用户逐条确认是否采用
```

#### 7.3 可视化验证（如产出是 HTML 页面）

对部署后的页面运行 `feishu-html` 阶段五的 Playwright 验证协议（6 项必检）。

**产出**：`REVIEW_{answername}.md` — 审查报告

**模板**：

```markdown
# Review: {answername}

Review against: BRIEF_{answername}.md
Date: {date}

## 对照审查

| # | 检查项 | 结果 | 证据/备注 |
|---|--------|------|----------|
| 1 | 完整性 | ✅/❌ | {detail} |
| 2 | 一致性 | ✅/❌ | {detail} |
| 3 | 标准合规 | ✅/❌ | {detail} |
| 4 | 依赖闭合 | ✅/❌ | {detail} |
| 5 | 受众适配 | ✅/❌ | {detail} |

## Must Fix（必须修复）
1. **[问题]**：{具体描述}。_修复方案：{建议}。_

## Should Fix（应该修复）
1. **[问题]**：{描述}。_修复方案：{建议}。_

## Could Improve（可以优化）
1. **[问题]**：{描述}。_建议：{idea}。_

## 蓝军审查摘要
{调用 blue-team 的结果摘要或完整嵌入}

## 红队审查摘要（战略级方案）
{如有运行 7.2a 红队攻击，嵌入 Top Kill-Assumptions + Cheapest Test}

## 总体评分
{score}/100 — {一句话总结}

## 成果与回顾 (Outcomes & Retrospective)

> 借鉴 execplan 的 Outcomes & Retrospective 方法论——对照 Brief 的成功标准，总结实际达成。

### 对照 Brief 成功标准

| Brief 中的成功标准 | 实际达成 | 差距 |
|-------------------|---------|------|
| {SC-1} | {实际结果} | {✅ 达标 / ⚠️ 部分 / ❌ 未达成} |
| {SC-2} | {实际结果} | ... |

### 未达成的目标（如有）

- **{目标}**：未达成原因 → {原因}，建议：{后续行动}

### 经验教训

1. **{关键学习}**：{描述} — {对未来项目的启示}
2. **{改进建议}**：{描述}

### 可复用资产

- 决策日志中的关键决策（D-001, D-002...）
- 意外发现中可跨项目复用的发现（S-001...）
```

---

## 领域适配参考

详见 `references/domain-mapping.md` — 不同领域到 7 阶段的参数化模板。

### 快速适配表

| 阶段 | 🏢 新业务/产品 | 🛠️ 新技能 | 📋 新方案 | 🔄 流程/SOP | 🔍 分析/调研 | 🎯 决策支持 |
|------|----------|----------|----------|----------|----------|----------|
| Clarify | 市场/用户/模式 | 触发/边界/依赖 | 受众/标准/约束 | 目标/痛点/例外 | 目的/数据源/框架 | 选项/标准/后果 |
| Brief | 商业意图/价值 | 技能接口/I/O | 方案目标/范围 | 流程目标/范围 | 分析目标/数据源 | 决策问题/候选 |
| Architect | 业务流程/角色 | 工作流/子模块 | 模块/逻辑链 | 流程图/角色/异常 | 框架/报告结构 | 决策树/评估矩阵 |
| Standards | 业务规则/质量 | 命名/风格/文档 | 格式/内容规范 | 编号/格式/SLA | 引用/结论质量 | 评分/权重规范 |
| Decompose | 里程碑/阶段 | 子技能/测试 | 章节/证据 | 步骤/表单/模板 | 维度/洞察/可视化 | 评估/敏感度 |
| Build | MVP/迭代 | 写 SKILL.md | 写方案文档 | 写 SOP 文档 | 写分析报告 | 写决策备忘录 |
| Review | BP检查/蓝军 | 端到端验证 | 审核/蓝军 | 模拟走查 | 数据/逻辑检查 | 反面意见检查 |

---

## 约束与陷阱

### 约束
1. **Phase 2 核心原则 ≤ 3 条** — 超过即失去聚焦
2. **Phase 5 每个任务必须是垂直切片** — 不含纯搭建任务
3. **Phase 7 审查必须具体** — 每条发现指向具体产出物的具体位置
4. **产出全进飞书 Wiki** — 不在本地留散落文件
5. **每阶段必须等用户确认** — 不自动跳下一阶段

### 常见陷阱

| # | 陷阱 | 后果 | 正确做法 |
|---|------|------|---------|
| 0 | **用两步法创建文档（Wiki API 建节点 + v2 update 写内容）** | 返回 `ok:true` revision_id 递增但 blocks=0，文档永远为空。lark-cli v1.0.40–v1.0.44 均存在此 bug | 必须用一步法：`docs +create --api-version v2 --doc-format markdown --title \"标题\" --content @file.md --parent-token TOKEN --as bot`。详见 feishu-doc 技能「两步法陷阱」 |
| 1 | 跳过 Clarify 直接写 Brief | 后续阶段基于未验证假设 | 至少确认 3 个核心假设 |
| 2 | Brief 写成功能列表 | 失去方向一致性 | 用"体验/流程"语言描述，不用"功能"语言 |
| 3 | Architect 过于抽象 | 拆解时无法落地 | 每个模块必须有具体的内容描述 |
| 4 | Standards 写了不用 | Build 产出与 Standards 矛盾——最典型的是 Standards 写"以内容需求为准"但 Build 产出写了具体数字（如"8-45s""8-15s"），用户一眼发现。定性标准被 Build 偷换成定量捷径 | Build 每完成一个任务对照 Standards 逐条检查，尤其警惕"数值化改写"——Standards 说"以内容为准"就不能在产出里写任何时长范围 |
| 4a | **训练/教学类文档的 Standards 写成"讲师备课用的提词器/教学备注"** | 用户会说"内容的规范应当是讲师面对学员要表达的内容"。Standards 定义了全文档的写作基调，写错则全篇语气偏离 | Standards 的「内容规范」必须写"讲师口吻，面向学员——文档=讲师张嘴就能念的逐字稿"，禁止写"此处讲师引导""讲师应在此处强调"等幕后备注。详见 `references/training-proposal-template.md` 常见陷阱第二条 |
| 5 | Review 只挑问题不说不好的 | 团队不知道自己什么做对了 | 必须包含 "What Works Well" |

### ⛔ 反例与禁止操作

以下操作在任何情况下都**禁止**——不是"不建议"，是**不允许**：

| # | 禁止操作 | 为什么禁止 | 正确做法 |
|---|---------|-----------|---------|
| 1 | **跳过 Phase 1 Clarify 直接写方案** | 未验证的假设会导致全链条崩塌 | 强制至少确认 3 个核心假设后再进 Phase 2 |
| 2 | **在 Phase 5 创建"搭建项目骨架"/"初始化目录"类任务** | 纯搭建任务不是垂直切片，不可验证 | 第一个任务必须是可产出用户可见结果的垂直切片 |
| 3 | **Phase 6 Build 时跳过任务验证直接标记完成** | 未验证的 build 产出在 Phase 7 Review 中会全部暴露 | 每个任务完成后对照 Standards DoD 逐项验证 |
| 4 | **用"视情况而定"/"灵活把握"/"根据情况判断"等措辞替代具体标准** | 软化措辞让标准失去可执行性 | 给出具体阈值（如"≤ 3 条"、"≥ 44px"、"重试 2 次"） |
| 5 | **Review 评分用"大概 80 分"/"还不错"等主观表述** | 无量化评分不可复现、不可对比 | 对照审查表的 5 个维度逐项打分，计算加权总分 |
| 6 | **Wiki API 失败时静默跳过，用户不知道产出丢失** | 静默失败是最危险的失败模式 | 降级到本地文件并明确告知用户 |
| 7 | **领域识别错误时强行继续而不纠正** | 用错误的追问模板走完全程 = 全篇作废 | 任何阶段发现领域不匹配，立即回退到 Clarify 重新确认 |
| 8 | **用 answer 子方法论裸拼替代完整 7 阶段** | 用户说"用 answer 方法论"，但 Agent 只调用了 grill-me/design-brief/information-architecture 等子方法独立拼凑，跳过 7 阶段的交互确认流。产出看似用了设计方法论，实则完全脱离了 answer 的编排逻辑。用户会发现你根本没走 answer | answer 的 7 阶段是**强制管线**——Phase 1 到 Phase 7 必须按序执行，每阶段有用户确认检查点。用子方法论碎片≠用了 answer。触发器："用 answer 方法论"/"请使用answer的方法论" → 必须从 Phase 1 Clarify 开始完整走 7 阶段交互 |
| 9 | **把"重构 README"误解为"做网页"** | 用户说"用 answer + huashu-design 重构 GitHub README"，Agent 创建了一个 HTML SPA 页面而不是 markdown 文件。GitHub README 是纯文本，不是 Web 应用 | README 重构 = 重写 markdown 文件。huashu-design 在此场景中为轻量注入（信息层级 + 反 AI slop），不是做 HTML 页面。详见 `references/readme-design-paradigm.md` |

| 10 | **每个阶段单独创建飞书文档** | 用户明确偏好合并输出，拆散文档增加管理负担。Phase 1-5 应合并为单一工作流记录文档 | 默认合并：`{answername}_工作流全记录`。Phase 1-5 为章节，Phase 6 产出独立交付物文档，Phase 7 Review 追加到工作流记录末尾 |
| 11 | **用 `wiki +node-delete --obj-type docx` 删 Wiki 节点** | Wiki 节点的 obj_type 是 `wiki` 而非 `docx`。用错会报 131005 not found | 使用 `lark-cli wiki +node-delete --node-token TOKEN --obj-type wiki --yes --as bot`
| 12 | **创建文档后不验证 title** | 飞书 API 偶发静默回退 title 为 "Untitled"——创建返回成功但文档名是默认值 | 创建后立即 `lark-cli api GET /open-apis/wiki/v2/spaces/get_node` 检查 `title != "Untitled"` |
| 14 | **培训文档写成了给讲师的元注释而非逐字稿** | 用户纠正"内容规范应当是讲师面对学员要表达的内容"。Agent 在 Standards 中写"讲师视角""一句话核心——讲师用"等元注释方向，但应该直接写出讲师对学员要说的话，不是给讲师看的备注。用户一眼发现方向错误 | 培训/授课类文档的 Standards 内容规范必须声明"面向学员的逐字稿，不是给讲师的备注"。判断标准：文档中的每一句话，讲师能否直接念给学员听？不能念的=不该写。结构骨架可以有控制标记（⏱/🖐️），但正文内容必须是可念出口的话 |
| 15 | **SVG 架构图转 PNG 嵌入飞书文档时中文变方框** | cairosvg 在 Linux 服务器端渲染 SVG 为 PNG 时，PingFang SC / HarmonyOS Sans SC 字体不可用，所有中文字符渲染为空心方框 □。用户看到的架构图全是方框和 X | (1) SVG 中 font-family 必须使用 Linux 系统可用的中文字体：`"Noto Sans SC", "SimSun", sans-serif`。(2) SVG 中禁止使用 emoji（🏗️🔭🔴🟠🔵 等），cairosvg 无法渲染 emoji 字形，会变成方框或 X。使用 HTML 实体替代：▶ `&#9654;`、→ `&#8594;`、◆ `&#9670;`。(3) 生成 PNG 后必须用 vision 工具验证中文正常显示再嵌入飞书 |
| 16 | **飞书文档覆盖写入后架构图丢失** | `docs +update --command overwrite` 会清空文档所有 block 并重新写入，之前通过 `+media-insert` 插入的图片块被一并清除。用户发现架构图不见了 | 每次 overwrite 后必须重新插入图片：`docs +media-insert --doc ID --file ./image.png --type image --width 1920 --align center --selection-with-ellipsis "文档开头...唯一文本" --before --as bot`。注意 `+media-insert` 要求相对路径，必须先 cd 到图片所在目录 |
| 17 | **飞书图片块替换用 `+media-upload` 不生效** | `docs +media-upload` 只上传文件到飞书存储并返回 file_token，但不会将新 token 绑定到已有的图片块上。文档中显示的仍是旧图片 | 正确做法：先 `docs +media-upload` 获取新 file_token，然后用 `lark-cli api PATCH "/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}" --data '{"replace_image":{"token":"新token"}}' --as bot` 直接替换图片块中的 token |
| 14 | **用完整培训提案模板（training-proposal-template.md）套轻量大纲需求** | 用户只想要课程日程表，Agent 却加载了含报价/场景诊断/公司介绍的 6 章模板，产出冗余章节。用户说"保持模板结构"指的是 .docx 的物理结构，不是让你加预算页 | 先判断文档类型：含报价+商务论证 → 用 `training-proposal-template.md`；纯课程内容不含商务 → 用 `training-outline-lite.md`。不确定时问用户"这份文档需要包含预算/报价吗？" |

### 错误处理

每个可预见的失败场景必须有明确的 if-then 响应路径。**禁止静默失败**——任何异常都必须向用户通报并提供下一步选项。

| 触发条件 (IF) | 一线修复 (THEN) | 仍失败时 (FALLBACK) |
|------|---------|------|
| Wiki API 创建文档失败（99992402） | 检查请求体 node_type 字段；重试 2 次（间隔 2s） | 降级为本地 .md 文件写入 ~/.hermes-feishu/answer/ |
| **创建成功但 title 为 Untitled** | 删除原节点，3s 间隔重试创建 | 仍失败则用 API 单独 PATCH 更新 title |
| Wiki API 返回其他错误码 | 打印完整 error response | 同上降级 |
| lark-cli 写入失败 | 检查 lark-cli 配置（`lark-cli config show`），确认 `--as bot` 可用 | 改用 curl 直接调飞书 Open API（`docx/v1/documents/{id}/blocks` 批量写入） |
| token 过期（99991663） | 重新调用 `auth/v3/tenant_access_token/internal` 获取新 token | 若连续 3 次获取失败，告知用户检查飞书应用凭证 |
| 用户在阶段间 5 分钟不回复 | 不催促；保留已完成的 Wiki 文档作为检查点 | 不主动关闭；用户返回时从中断恢复流程继续 |
| 领域无法自动识别 | 默认使用「新方案」模板；向用户展示候选领域，让用户选择 | 用户不选时以「新方案」开始 |
| 用户输入过于模糊无法展开决策树 | 输出 1 个具体追问（如"你能举一个具体的使用场景吗？"），不强行还原 | 缩小追问范围到最核心的 1 个问题 |
| Build 阶段某任务失败 | 标记该任务为 ❌，记录错误详情到 BUILD_LOG | 跳过该任务继续下一个；Phase 7 Review 时汇总所有失败任务 |
| execute_code 脚本语法错误导致终端调用静默跳过 | 脚本中的 f-string 反斜杠等语法错误会使整个 execute_code 提前终止，后续 terminal() 调用全部不执行 | ① 写完文档后用 `docs +fetch` 验证 revision_id 递增且文本存在 ② 复杂脚本拆为多个 execute_code 调用，降低单点失败影响面 ③ f-string 中的引号检查用变量替代（`ok = '"ok": true' in output`） |
| docs +update overwrite 返回成功但文档为空 | 创建时用的 `wiki +node-create` 生成空 docx，如果 overwrite 的 execute_code 脚本静默失败，revision_id 仍为 1 且无文本 | 每次 overwrite 后立刻 `docs +fetch` 检查 `revision_id > 1` 且有文本内容 |
| 产出目录 `{answername}/` 下已有同名项目 | 追加时间戳后缀（`{answername}-{HHmm}`）避免覆盖 | 告知用户已有同名项目，询问是覆盖还是新建 |

### 中断恢复

当用户说"暂停"/"够了"/"之后继续"，或对话中断后用户返回：

1. **检查 Wiki 节点**：列出 `J4EewYIT2ieFuwkRWbxcgWbFnhe` 下的已有文档
2. **判断进度**：根据已存在的文档判断当前在哪个阶段：
   - `{answername}_工作流全记录` 存在 → 读取内容，判断最后完成的阶段
   - 各阶段独立文档存在（旧模式）→ 按文档名判断
3. **从中断阶段继续**：告知用户「上次进行到 Phase {N}，从 Phase {N+1} 继续？」
4. **如果 Wiki 中无记录**：检查 `~/.hermes-feishu/answer/` 本地降级目录

### 与现有技能互动规则

| 场景 | 互动方式 |
|------|---------|
| Phase 6 Build 生成 HTML 页面 | 加载 `feishu-html` 技能，使用其阶段三—六流程。answer 的 Standards 中定义的品牌/风格规范传给 feishu-html |
| Phase 6 Build 生成飞书文档 | 加载 `feishu-doc` 技能，使用其创建流程 |
| Phase 6 Build 重构/优化 README 或文档 | 加载 `huashu-design` 技能，轻量注入信息层级和反 AI slop 原则（注意：README 是 markdown，不是 HTML 页面） |
| Phase 6 Build 创建技能 | 使用 `skill_manage(action='create')` |
| Phase 7 Review HTML 产出 | 加载 `feishu-html` 技能，使用其增强版阶段五（含 design-review 设计质量审查） |
| Phase 7 Review 方案文档 | 加载 `blue-team` 技能，对方案逻辑进行压力测试。如果方案级别为战略级（非日常流程/活动），额外运行本技能内置的 7.2a 红队攻击流程 |
| Phase 7 Review 文档/README 产出 | 使用 answer 自身的 5 维度对照审查表（完整性/一致性/标准合规/依赖闭合/受众适配），不需要 blue-team |
| 所有阶段 Wiki 操作 | 使用本技能内置的 Feishu API 封装；不依赖 feishu-wiki 技能（避免循环依赖） |

---

## 快速启动（省略模式）

当用户只需要快速规划而不要完整 7 阶段时，支持精简模式：

- `answer quick {topic}`：Clarify(精简) → Brief(模板) → Decompose(5 条任务)，跳 Architect/Standards/Build/Review
- `answer brief {topic}`：只跑 Clarify + Brief，产出结构化简报
- `answer review {project}`：只跑 Phase 7 审查已完成的产出

---

## 端到端示例：创建一个"行程总结"技能

以真实案例展示 7 阶段如何运作：

```
用户: "answer this: 创建一个 trip-summary 技能，输入方案文档自动生成客户总结页"

🔴 CHECKPOINT → 识别为 🛠️ 新技能领域。确认。

Phase 1 CLARIFY → 追问 5 轮：
  Q1: 谁在什么场景触发？→ 运营人员，客户要出行前生成
  Q2: 输入输出？→ 输入 doc_token，输出 HTML 页面
  Q3: 依赖？→ trip-landing(页面结构) + feishu-html(部署)
  Q4: 不覆盖什么？→ 不修改方案、不与已有 trip-landing 功能重叠
  Q5: 最不确定？→ 文档内容提取的准确性
→ 产出: CLARIFY_trip-summary.md ✓

Phase 2 BRIEF → 结构化：
  核心原则: 一键交付 > 灵活配置; 客户体验优先; 品牌一致性
  产出物: SKILL.md + extract.py + build_page.py
→ 产出: BRIEF_trip-summary.md ✓

Phase 3 ARCHITECT → 结构树：
  触发 → 提取行程(extract.py) → 生成页面(build_page.py) → 部署OSS
→ 产出: ARCHITECTURE_trip-summary.md ✓

Phase 4 STANDARDS → 规范：
  命名: trip-summary (kebab-case)
  DoD: 从方案链接输入→3步内生成可访问URL
→ 产出: STANDARDS_trip-summary.md ✓

Phase 5 DECOMPOSE → 任务清单：
  Foundation: [ ] 创建 SKILL.md 骨架
  Core: [ ] 实现 extract.py [ ] 实现 build_page.py
  Polish: [ ] 端到端测试 [ ] Review
→ 产出: TASKS_trip-summary.md ✓

🔴 CHECKPOINT → 任务清单完整，确认进入 Build。

Phase 6 BUILD → 逐步构建：
  Task 1 ✅ SKILL.md → 调 skill_manage 创建
  Task 2 ✅ extract.py → 写入 scripts/
  Task 3 ✅ build_page.py → 写入 scripts/
  Task 4 ✅ 端到端测试 → 测试用例通过
→ 产出: BUILD_LOG_trip-summary.md ✓

Phase 7 REVIEW → 对照审查 + blue-team 压力测试：
  完整性 ✅ | 一致性 ✅ | 标准合规 ✅ | 依赖闭合 ✅ | 受众适配 ✅
  评分: 88/100
→ 产出: REVIEW_trip-summary.md ✓

总计: 7 个 Wiki 文档, 1 个技能上线, 耗时 ≈ 15 分钟
```

---

## 验证清单

- [ ] 工作流记录文档已创建并写入飞书 Wiki（Phase 1-5 合并为单文档，Phase 7 追加）
- [ ] Phase 2 Brief 包含 ≤ 3 条核心原则
- [ ] Phase 5 任务全是垂直切片，无纯搭建任务
- [ ] Phase 6 Build 交付物已独立写入飞书 Wiki
- [ ] Phase 7 Review 包含对照审查 + 蓝军审查
- [ ] Review 中有具体评分

---

## 开源仓库

GitHub: **[jorinyang/answer](https://github.com/jorinyang/answer)** — SKILL.md + domain-mapping + README + CHANGELOG，含 v1.0.0 / v1.1.0 / v1.1.1 三个 Release。

> **非飞书环境？** 使用 `answer-standalone` 技能（v2.0.0），纯本地 markdown 输出，零外部依赖。与原版 answer 共享相同的 7 阶段方法论和 6 领域模板。

**独立封装文档**: [Answer 方法论完全指南](https://acn3kz7weyc0.feishu.cn/wiki/JYK4wJTEdiA3TPkN8R3ceMJCnfd) — 脱离 Hermes 技能系统的 18 章独立参考文档，归档于 AI Native 工作流节点下。

---

## 📚 引用文件索引

| 文件 | 路径 | 用途 |
|------|------|------|
| SKILL.md | `~/.hermes-feishu/skills/productivity/answer/SKILL.md` | 主技能文件（本文件） |
| domain-mapping.md | `references/domain-mapping.md` | 6 领域 × 7 阶段完整追问清单和模板变体 |
| readme-design-paradigm.md | `references/readme-design-paradigm.md` | README 设计范式：designer-skills 6 层结构（Hero→问题→Flow→原则→细节→收尾） |
| dingtalk-deap.md | `references/dingtalk-deap.md` | 钉钉DEAP企业AI平台模块矩阵与费用参考 |
| skill-audit-pattern.md | `references/skill-audit-pattern.md` | 技能审计模式：用 answer 逆向审计已有技能/方案的 4 步流程 |
| training-proposal-template.md | `references/training-proposal-template.md` | 培训/工作坊方案模板：6章+附录结构，场景筛选→课程设计→担忧回应→映射表（企业AI部署/DEAP工作坊类） |
| training-outline-lite.md | `references/training-outline-lite.md` | 轻量培训大纲模板：纯课程内容，不含报价/场景诊断/公司介绍（已有合作关系、仅需课程设计的场景） |
| internal-onboarding-training.md | `references/internal-onboarding-training.md` | 内部工具上手培训模式：三层目标框架+手机端实操+逐字稿内容规范（与上一条是两种培训类型） |
| `pricing-estimation.md` | `references/pricing-estimation.md` | 软件功能报价方法论：Fibonacci+RICE 双因子定价，双 Sheet Excel 输出 |
| `distribution.md` | `references/distribution.md` | 分发包指南：tar.gz 打包、目标安装、GitHub Token 推送陷阱 |
| `lark-cli-v2-quickref.md` | `references/lark-cli-v2-quickref.md` | lark-cli v2 API 命令速查：创建/写入/删除/验证 Wiki 文档的正确 flags |
| marketing-funnel-template.md | `references/marketing-funnel-template.md` | 运营营销方案漏斗数学模板：GMV反推、渠道矩阵、内容复用流、私域承接时间线、预算分配参考 |
| CHANGELOG.md | GitHub 仓库 | 版本变更记录（v1.0 → v1.1.1） |
| LICENSE | GitHub 仓库 | MIT 开源许可 |
