---
name: github-absorb
description: >-
  GitHub 代码仓库全流程评估与吸收引擎。当用户给出 GitHub 仓库链接时自动触发：
  深度分析→业务价值评估→吸收策略分类→独立创建/吸收执行→网格化引用→
  单元测试+全业务链路测试→能力强化报告。触发信号：github.com 链接、
  "这个仓库怎么样"、"帮我看看这个项目"、"能不能用"、"吸收这个仓库"。
version: 1.1.1
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [github, absorption, evaluation, repository, meta-skill, code-review, business-value]
    related_skills:
      - external-skill-evaluation
      - codebase-inspection
      - cross-project-adaptation
      - skill-evaluator
      - darwin-skill
      - github-release-readme
triggers:
  - "https://github.com/"
  - "这个仓库怎么样"
  - "帮我看看这个项目"
  - "能不能用"
  - "吸收这个仓库"
  - "评估一下这个代码仓库"
  - "这个项目对我们有帮助吗"
  - "analyze this repo"
  - "evaluate repository"
---

# GitHub 代码仓库全流程评估与吸收引擎

> **定位**：不是"看看这个仓库"的信息检索——是从**业务价值判断→吸收执行→测试验证→网格化引用→能力报告**的完整闭环。覆盖 AI、数字化、咨询、企业管理、FDE 五大业务域。

## 设计哲学

1. **价值先行，不行即止** — 业务价值为负或无关 → 立即停止，不浪费后续步骤
2. **最小化可用** — 优先独立创建技能；只在强互补+高契合时才吸收到现有技能
3. **技能纯粹性** — 不把不同职责塞进同一个技能；代码仓库能力与现有技能边界清晰
4. **自动触发** — GitHub 链接出现即启动，不需用户重复说"评估一下"
5. **闭环交付** — 从评估到测试到报告，产出完整可追溯的强化记录

## 触发条件

### 自动触发（默认）

当消息中出现以下任一信号时自动启动 Phase 1：
- 包含 `github.com` 且看起来像仓库链接（`/owner/repo` 模式）
- 用户说"帮我看看这个仓库/项目"
- 用户说"这个项目怎么样/能不能用/值不值得"
- 用户说"吸收/引入/用这个仓库"

### 不触发场景

- Gist 链接（`gist.github.com`）
- GitHub 非仓库页面（Issues/PRs/Discussions/profile）
- 用户只是提了一嘴 GitHub 作为上下文但没要求评估
- 纯代码片段引用（如"参考 github.com/xxx/blob/main/src/yyy.py 的写法"）

## 全局工作流（八阶段）

```
Phase 1 → Phase 2 → Phase 3 (Gate) → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8
 触发      深度      价值判断       吸收策略    执行吸收   网格引用   测试验证   强化报告
 检测      分析      (停/续)        分类       创建技能   更新关联   双轨测试   最终交付
```

---

## Phase 1: 触发检测与仓库定位

### Step 1.1: 解析 GitHub URL

从用户消息中提取：
```
https://github.com/{owner}/{repo}
```

若用户给了非标准格式（如 `owner/repo`），补全为 `https://github.com/{owner}/{repo}`。

### Step 1.2: 确认评估意图

若 URL 出现但意图不明确（如"你看过 github.com/xxx 吗"），追问确认：
```
你是想让我评估这个仓库对当前业务的价值吗？还是只是想了解这个项目是做什么的？
```

### Step 1.3: 获取仓库元信息

```bash
# 仓库基本信息
curl -s https://api.github.com/repos/{owner}/{repo} | python3 -c "
import sys,json
r=json.load(sys.stdin)
print(f'Stars: {r.get(\"stargazers_count\",\"?\")}')
print(f'Forks: {r.get(\"forks_count\",\"?\")}')
print(f'Language: {r.get(\"language\",\"?\")}')
print(f'Topics: {\", \".join(r.get(\"topics\",[]))}')
print(f'Description: {r.get(\"description\",\"?\")}')
print(f'License: {r.get(\"license\",{}).get(\"spdx_id\",\"?\") if r.get(\"license\") else \"?\"}')
print(f'Last push: {r.get(\"pushed_at\",\"?\")}')
print(f'Archived: {r.get(\"archived\",False)}')
"
```

---

## Phase 2: 深度分析

### Step 2.1: 读取文档层

按优先级读取：

1. **README.md** — 项目定位、核心功能、快速开始
2. **CHANGELOG.md / RELEASE_NOTES** — 版本演进、稳定性判断
3. **CONTRIBUTING.md / ARCHITECTURE.md** — 架构设计、贡献指南
4. **docs/ 目录** — 详细文档
5. **examples/ 目录** — 使用示例

使用 `curl -s 'https://raw.githubusercontent.com/{owner}/{repo}/main/README.md' | head -500` 分块读取。

### Step 2.2: 分析目录结构

```bash
curl -s https://api.github.com/repos/{owner}/{repo}/contents/ | python3 -c "
import sys,json
for i in json.load(sys.stdin):
    print(f'{i[\"type\"]:5s} {i[\"name\"]}')
"

# 若为 monorepo，深入探索关键子目录
```

### Step 2.3: 代码规模与语言分析

使用 `codebase-inspection` 技能的方法：

```bash
# 浅克隆（加速）
git clone --depth 1 https://github.com/{owner}/{repo}.git /tmp/{repo} 2>&1

# 语言/规模分析
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,dist,build" \
  /tmp/{repo} 2>/dev/null
```

若仓库过大（>100MB 或 clone 超时 60s），跳过全量代码分析，仅基于文档层判断。

### Step 2.4: 代码文档质量评估

检查以下信号：
- 是否有 docstring/注释（搜索 `def ` + 下一行是否含 `"""`）
- 是否有类型标注（Python `.py` 文件搜索 `: str` / `->` 等模式）
- 是否有测试文件（`test_*.py` / `*_test.go` / `*.spec.ts` 等）
- 是否有 CI/CD 配置（`.github/workflows/` / `.gitlab-ci.yml` 等）

### Step 2.5: 业务域映射

**核心判断**：这个仓库解决什么问题？与当前五大业务域的关系？

| 业务域 | 映射信号 | 示例 |
|--------|---------|------|
| **AI** | LLM/Agent/RAG/MLOps/Prompt/NLP/CV | LangChain、vLLM、Agent框架 |
| **数字化** | ERP/CRM/WMS/低代码/流程自动化/数据中台 | 企业管理系统、工作流引擎 |
| **咨询** | 方法论框架/战略工具/分析模型/MECE | SWOT分析、BCG矩阵、OKR工具 |
| **企业管理** | 组织架构/绩效/财务/HR/协同 | 人事系统、预算管理、项目看板 |
| **FDE** | 前端/后端/数据/DevOps基础设施 | 微服务框架、数据库工具、CI/CD |

每个域打分（0-5）：
- **0**：完全无关
- **1-2**：有弱关联，但不能直接用于业务
- **3**：中等关联，可借鉴思想或部分组件
- **4**：强关联，可直接用于核心业务场景
- **5**：极强关联，填补关键能力空白

---

## Phase 3: 价值判断门禁（Gate）

### 决策逻辑

```
if max(业务域评分) < 2:
    → 🛑 停止。输出"业务相关性不足"简要报告，不进入后续阶段。

if max(业务域评分) >= 3:
    → ✅ 继续。进入 Phase 4 吸收策略。
```

### 门禁判断需考虑的负面信号

| 信号 | 含义 | 处理 |
|------|------|------|
| 仓库已归档（Archived） | 不再维护 | 标注但不自动否决——老旧方法论仍可能有价值 |
| 最后更新 > 2年 | 可能过时 | 减 1 分，提示技术债风险 |
| 无 License 或非宽松许可证 | 法律风险 | 标注，用户决策 |
| 纯 Demo/Toy 项目 | 无生产价值 | 直接否决（除非方法论创新极强） |
| README 质量极低 | 项目不成熟 | 减 0.5-1 分 |

---

## Phase 4: 吸收策略分类

基于 Phase 2 的深度分析，对仓库进行**能力拆解**和**分类标注**。

### 能力拆解

不是整个仓库作为一个整体吸收。先拆成独立的能力单元：

```
仓库 {owner}/{repo}
├── 能力单元 1: [核心算法/方法]
├── 能力单元 2: [工具/CLI]
├── 能力单元 3: [框架/库]
├── 能力单元 4: [设计模式/架构]
└── 能力单元 N: [文档/知识]
```

### 五类分类法

逐能力单元标注吸收类别：

| 分类 | 图标 | 含义 | 操作 |
|------|:---:|------|------|
| **独立创建** | 🟢 | 独特能力，现有技能库缺失 | 创建独立 Hermes 技能 |
| **吸收增强** | 🔵 | 与现有技能强互补且契合 | 注入到现有技能的特定阶段/字段 |
| **参考借鉴** | 🟡 | 有启发性但暂不吸收 | 记录为参考，不创建技能 |
| **冲突/重复** | 🔴 | 直接冲突或完全被覆盖 | 记录冲突原因，不操作 |
| **无关** | ⚪ | 与业务场景无关 | 跳过 |

### 吸收优先级

| 优先级 | 条件 | 行动 |
|:---:|------|------|
| **P0** | 🟢 独立创建 + 业务评分 ≥ 4 | 立即执行 |
| **P1** | 🔵 吸收增强 + 业务评分 ≥ 3 | 立即执行 |
| **P2** | 🟢 独立创建 + 业务评分 3 | 可选执行 |
| **P3** | 🟡 参考借鉴 | 仅记录 |

### 用户决策点 🔴 CHECKPOINT

展示吸收策略矩阵，**等待用户确认**后才进入 Phase 5：

```
┌──────────────────────────────────────────────────────────┐
│              吸收策略决策矩阵                               │
├────────────────┬──────┬──────┬──────────┬─────────────────┤
│ 能力单元        │ 分类  │ 优先级 │ 吸收方式   │ 目标技能         │
├────────────────┼──────┼──────┼──────────┼─────────────────┤
│ 核心算法        │ 🟢   │ P0   │ 独立创建   │ [新技能名]       │
│ 工具CLI        │ 🔵   │ P1   │ 吸收增强   │ [现有技能名]     │
│ 设计模式        │ 🟡   │ P3   │ 仅记录    │ —               │
└────────────────┴──────┴──────┴──────────┴─────────────────┘

是否按以上策略执行吸收？（可选择调整分类/优先级）
```

---

## Phase 5: 执行吸收

### 5A: 独立创建技能

根据以下标准创建 Hermes 技能：

#### 技能结构要求

```
~/.hermes-feishu/skills/{category}/{skill-name}/
├── SKILL.md              # 核心：触发条件 + 执行流程 + 反例
├── references/           # 参考文件（方法论、模板、案例）
├── scripts/              # 可执行脚本
└── templates/            # 输出模板
```

#### SKILL.md 写作标准

- **name**: 英文小写+连字符，≤64字符
- **description**: 必须包含"做什么 + 何时用 + 触发词"，≤1024字符
- **triggers**: 至少 3 个中文触发词
- **执行流程**: 编号步骤，每步有明确输入/输出
- **失败模式**: 显式编码 if-失败-→ fallback
- **检查点**: 关键决策前用 🔴 CHECKPOINT
- **反例**: "不要做什么"的独立章节

#### 触发机制设计

确保技能可通过以下方式触发：
1. **关键词自动触发** — 在 description 中声明 ≥ 3 个中文触发词
2. **上下文语义触发** — 触发词覆盖核心场景的不同表述
3. **关联触发** — 若该技能与现有技能强相关，在 existing skill 的 related_skills 中添加

创建完成后立即用 `darwin-skill` 的 L1 静态检查验证：
```bash
# 基本结构检查
grep -c "^## " SKILL.md  # 至少 3 个二级标题
grep -c "🔴 CHECKPOINT" SKILL.md  # 至少 1 个检查点
grep -c "❌" SKILL.md  # 至少 1 个反例
```

### 5B: 吸收增强现有技能

对 🔵 类能力单元，执行以下操作：

1. **定位注入点** — 确定目标技能的哪个 Phase/步骤可以增强
2. **提取核心方法论** — 从源仓库提取算法、模式、检查项
3. **本地化适配** — 转换为 Hermes 原生措辞和工具调用
4. **注入** — 用 `skill_manage(action='patch')` 精确插入新内容
5. **记录来源** — 在目标技能中添加 `> 吸收自: {repo_url}` 的引用标注

注入原则：
- 只加内容，不改原有核心逻辑
- 新增内容放在对应 Phase 的末尾（不打断现有流程）
- 保持原有技能的结构和命名风格

---

## Phase 6: 网格化引用网络

每次独立创建 / 吸收增强后，必须更新技能间的引用关系。

> **审计工具**：`references/skill-network-audit.py` 可随时对全库执行引用网络健康检查，发现反向引用缺失、孤立技能和引用断裂。用法见底部「工具集」。

### 6A: 双向引用

```yaml
# 新技能 → 关联技能
metadata:
  hermes:
    related_skills: [skill-a, skill-b, skill-c]

# 关联技能 → 新技能（反向引用）
# 在 skill-a 的 related_skills 中添加新技能名
```

### 6B: 引用指引生成与注入

`related_skills` 元数据只是索引——技能加载时并不会自动知道"什么时候该用"关联技能。必须为每个关联技能生成**引用指引段落**并注入到其 SKILL.md 正文中，实现"技能知道何时加载另一技能"。

#### 引用指引格式

根据引用维度，为每个关联技能生成一段具体的指引：

| 引用类型 | 指引模板 |
|---------|---------|
| **downstream** | `当需要 [具体场景] 时，先加载 \`{target-skill}\` 获取 [输出类型]，再继续本流程的 [阶段/步骤]。` |
| **upstream** | `本技能的 [产出类型] 可由 \`{target-skill}\` 进一步处理：[衔接场景说明]。` |
| **sibling** | `当面对 [复合场景] 时，与 \`{target-skill}\` 协同使用：[协同方式说明]。` |
| **alternative** | `当 [条件差异] 时，可选 \`{target-skill}\` 替代本技能的 [阶段/步骤]，因为 [理由]。` |

#### 指引编写要求

- **必须具体**：不是"与 X 协同使用"，而是"当需要将评测结果转换为业务报告时，与 X 协同使用"
- **必须给出触发条件**：让技能能自行判断"现在我该不该加载 X"
- **必须说明衔接方式**：输入什么、期望得到什么、结果用在哪一步

#### 注入位置

在目标技能的 SKILL.md 中查找以下章节（按优先级）：

1. `## 与其他技能的关系` → 在该章节末尾追加指引
2. `## 关联技能` → 在该章节末尾追加指引
3. 以上都不存在 → 在技能末尾新增 `## 关联技能指引` 章节

#### 注入方式

使用 `skill_manage(action='patch', file_path='SKILL.md')` 精确插入指引行，只追加、不改写。

#### 注入内容示例

假设在 Phase 5A 独立创建了 `skill-evaluator-extended` 技能，它与 `skill-evaluator` 形成 upstream 关系（skill-evaluator 的输出可由新技能进一步处理）。对 `skill-evaluator` 注入：

```markdown
## 关联技能指引

> 以下指引由 `github-absorb` Phase 6 自动生成，来源于 {repo_url}

- **upstream → `skill-evaluator-extended`**：本技能的三维评测结果可由 `skill-evaluator-extended` 进一步扩展为包含「业务适配度」的四维评测。当需要面向业务决策层输出评测报告时，先加载 `skill-evaluator-extended` 追加第四维度。
```

#### 引用指引质量自检

每条指引注入前自问：

- [ ] 是否说明了**什么场景**下需要加载关联技能？（不能泛泛说"需要时使用"）
- [ ] 是否说明了**衔接方式**？（输入什么、期望输出什么）
- [ ] 是否使用了具体的技能名和阶段名？（不能只说"相关技能"）
- [ ] 技能是否**无需上下文就能判断**触发条件？（按 "if 用户说 X / 当前处于 Y 阶段" 来写）

### 6C: 执行清单

对每个新创建或增强的技能，逐项执行并确认：

- [ ] 新技能自身的 `related_skills` 元数据已填写（6A）
- [ ] 对每个关联技能，确定了引用类型（6B 维度）
- [ ] 对每个关联技能，编写了引用指引段落（6B 格式）
- [ ] 已将引用指引注入到每个关联技能的正文中（6B 注入）
- [ ] 对注入后的关联技能执行 L1 结构检查（结构未损坏）
- [ ] GitHub `awesome-skills` README 索引标记 TODO

---

## Phase 7: 测试验证

### 7A: 单元测试（能力和功能）

对每个新创建或增强的技能：

#### L1 静态合规（自动）

```bash
# SKILL.md 结构完整性
- [ ] name/description/version 完整
- [ ] trigger 列表 ≥ 3 个
- [ ] 执行流程有编号步骤
- [ ] 至少 1 个 🔴 CHECKPOINT
- [ ] 至少 1 个反例章节
- [ ] references/ 中引用的文件全部存在
- [ ] scripts/ 中 .py/.sh 文件语法正确
```

#### L2 功能测试（手动/AI驱动）

```bash
# 对每个 trigger 信号，测试技能是否能正确触发
测试集:
  1. 典型触发场景（happy path）
  2. 边界场景（模糊/不全的触发信号）
  3. 负样本（不应触发的场景）
```

#### L3 吸收完整性检查

```bash
- [ ] 源仓库的核心能力是否完整提取
- [ ] 吸收后的技能是否可独立运行（不依赖源仓库）
- [ ] 是否有遗漏的关键方法/算法
- [ ] 文档中是否标注了原始来源
```

### 7B: 全业务链路测试

基于当前系统的**实际功能**与**历史会话/记忆中的主要业务场景**，构建端到端测试链：

#### 链路定义

```
需求 → 转换 → 洞察 → 分析 → 校验 → 输出
```

#### 测试场景生成

从以下来源提取测试场景：

1. **当前任务地图**（从 SOUL.md 和当前会话）
   - 当前身份和业务域
   - 正在进行的项目
   - 记忆中的主要业务场景

2. **历史高频任务**（从 session_search）
   - 搜索最近 1 个月的高频操作类型
   - 提取 3-5 个典型端到端场景

3. **技能依赖链**（从技能 related_skills 图）
   - 找出涉及新技能的最长调用链
   - 测试链上每个节点的输入输出兼容性

#### 测试执行示例

假设新技能为 `{new-skill}`，测试链为：

```
场景: AI Agent 应用探讨
  demand  → 用户提出"帮我设计一个 Agent 架构"
  convert → {new-skill} 从 GitHub 仓库中提取 Agent 设计模式
  insight → {new-skill} 映射到当前业务（数字化/企业管理系统）
  analyze → cross-project-adaptation 分析适配成本
  verify  → skill-evaluator 验证产出质量
  output  → 生成架构方案文档
```

每个环节检查：
- [ ] 输入格式是否兼容下游
- [ ] 输出是否满足上游预期
- [ ] 是否有信息丢失或格式断裂
- [ ] 端到端耗时是否合理

#### 多业务体系适配验证

确保新技能在以下业务体系中均可正常工作：

| 业务体系 | 测试问题 | 检查点 |
|---------|---------|--------|
| **AI 技术** | Agent/LLM/RAG 相关的仓库评估 | 能否识别技术栈并映射到业务 |
| **数字化** | ERP/WMS/低代码 相关仓库 | 能否识别企业管理价值 |
| **咨询** | 方法论框架/分析工具 | 能否提取可复用的思维模型 |
| **企业管理** | 组织/流程/绩效工具 | 能否映射到实际管理场景 |
| **FDE** | 基础设施/DevOps 工具 | 能否评估技术栈适配性 |

---

## Phase 8: 能力强化报告

生成最终的结构化报告，包含以下全部内容：

### 报告模板

完整报告模板见 `references/report-template.md`。使用时替换所有 `{placeholder}` 为实际内容。报告包含七个章节：

1. **仓库概览** — 基本信息表
2. **业务价值评估** — 五大业务域评分
3. **吸收执行摘要** — 能力单元×分类矩阵
4. **创建/增强的技能** — 新技能详情 + 增强注入点
5. **引用网格** — ASCII 图 + 维度明细表
6. **测试结果** — 单元测试 + 全链路测试 + 多业务适配
7. **后续行动** — Checklist

---

## 反例（禁止）

- ❌ 不读完 README 就下结论 — 仓库价值在文档细节中
- ❌ 跳过业务域评分直接分类 — 业务价值是吸收决策的锚
- ❌ 把整个仓库作为一个整体吸收 — 必须拆成能力单元逐项评估
- ❌ 创建技能后不更新引用网格 — 孤立的技能就是死技能
- ❌ 跳过 Phase 7 测试 — 未测试的技能不可信
- ❌ 用户没有确认就执行 Phase 5 吸收 — 吸收决策必须人审
- ❌ 对低价值仓库继续执行后续阶段 — Phase 3 门禁必须严格执行
- ❌ 吸收时破坏原有技能结构 — 注入内容必须放在对应 Phase 末尾

---

## 与其他技能的关系

| 技能 | 关系 | 使用方式 |
|------|:---:|---------|
| `external-skill-evaluation` | sibling | github-absorb 走完全流程时，若仓库含 agent skill，可委托给 external-skill-evaluation 做技能层评估 |
| `codebase-inspection` | downstream | Phase 2.3 使用其 pygount 分析和仓库探索方法 |
| `cross-project-adaptation` | downstream | Phase 5B 吸收增强时使用其架构映射方法 |
| `skill-evaluator` | downstream | Phase 7 测试时调用其三维评测框架 |
| `darwin-skill` | downstream | Phase 5A 创建技能后使用其 L1 静态检查 |
| `github-release-readme` | downstream | Phase 8 报告产出后可同步到 GitHub |

---

## 异常与边界条件

| 场景 | 触发条件 | 处理 |
|------|---------|------|
| 仓库过大 clone 超时 | `git clone --depth 1` > 60s | 跳过代码分析，仅基于文档层评估 |
| 私有仓库 | API 返回 404 | 提示用户提供 access token 或手动描述 |
| 仓库只有 README 无代码 | pygount 结果为空 | 按纯知识/方法论仓库处理，评分默认保守 |
| 多语言混合仓库 | pygount 返回 5+ 种语言 | 只分析主要语言（>20% 占比） |
| 仓库是 Fork | `fork: true` | 标注 Fork 来源，评估与原版的差异 |
| API rate limit | 403 返回 | 等待 60s 重试一次；仍失败则用 `web_search` 获取信息 |
| 用户中途改变需求 | 任意阶段 | 记录当前进度后调整方向 |

## 工具集（references/）

| 文件 | 用途 | 场景 |
|------|------|------|
| `references/report-template.md` | Phase 8 能力强化报告模板 | 每次吸收完成后生成报告 |
| `references/skill-network-audit.py` | 技能引用网络全量审计脚本 | 扫描本地+GitHub 技能库，输出反向引用缺失/孤立技能/聚类报告 |

运行审计脚本：
```bash
python3 references/skill-network-audit.py /path/to/awesome-skills ~/.hermes-feishu/skills
```
