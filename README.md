# Awesome Skills

> 精心筛选的 Agent Skill 集合 — 为 Hermes Agent 设计，兼容任何支持 SKILL.md 格式的 Agent 框架。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-16-blue)](.)

---

## 📖 目录

- [什么是 Agent Skill](#-什么是-agent-skill)
- [技能索引](#-技能索引)
- [快速开始](#-快速开始)
- [技能详解](#-技能详解)
  - [🧠 方法论技能](#-方法论技能)
  - [🏗️ 构建技能](#️-构建技能)
  - [🔍 质量审查技能](#-质量审查技能)
  - [📋 飞书系列](#-飞书系列)
  - [🏔️ 贵州之客系列](#️-贵州之客系列)
  - [🗺️ 旅行系列](#️-旅行系列)
- [使用场景](#-使用场景)
- [安装方法](#-安装方法)
- [贡献指南](#-贡献指南)
- [版本历史](#-版本历史)

---

## 🤔 什么是 Agent Skill

Agent Skill 是一种自包含的知识模块——一个 `SKILL.md` 文件定义了一个完整的技能：何时触发、如何执行、产出什么、如何验证。

**一份好的 Skill：**
- ✅ 让一个不了解上下文的新手 Agent 也能独立完成任务
- ✅ 包含精确的触发条件、执行步骤、验证标准
- ✅ 自包含——所有知识内嵌，不依赖外部引用
- ✅ 可以独立加载，也可以被其他技能调用

---

## 📚 技能索引

### 🧠 方法论

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [advanced-elicitation](advanced-elicitation/SKILL.md) | 深度审视/换个角度/red team/Push deeper | 69种追问方法，产出后自动触发多维审视 |
| [blue-team](blue-team/SKILL.md) | 帮我看看这个方案/challenge一下/压力测试 | 6阶段破坏性逻辑审查，模拟最挑剔的挑战者 |

### 🏗️ 构建

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [answer](answer/SKILL.md) | answer/从零开始/帮我规划/设计方案 | 7阶段工作流编排器（澄清→简报→架构→标准→拆解→构建→审查） |

### 🔍 质量审查

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [edge-case-hunter](edge-case-hunter/SKILL.md) | 边界检查/edge case/穷举测试/所有情况都覆盖了吗 | 穷举7维边界条件，纯JSON输出 |
| [editorial-review-prose](editorial-review-prose/SKILL.md) | 审一下文案/文本审查/edit this/润色 | 微软基线 × 7维审查 × 三列表格修订 |
| [editorial-review-structure](editorial-review-structure/SKILL.md) | 结构审查/逻辑重排/信息架构优化 | 5种结构模型 × 6类重组建议 |

### 📋 飞书

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [feishu-html](feishu-html/SKILL.md) | 做个网页/发布到线上/做个展示页/部署 | 飞书文档 → WEB SPA 制作 + OSS 部署 |
| [feishu-doc](feishu-doc/SKILL.md) | 创建飞书文档/写个文档/归档到知识库 | 飞书文档创建、修改、评论管理、归档 |
| [feishu-wiki](feishu-wiki/SKILL.md) | 知识库巡检/目录更新/文档归类 | 知识库全生命周期管理（扫描→总结→分类→变更日志） |
| [feishu-table](feishu-table/SKILL.md) | 新建多维表格/查询记录/批量导入 | 飞书多维表格 + 电子表格 CRUD |

### 🏔️ 贵州之客

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [zhike-content-output](zhike-content-output/SKILL.md) | 产出文档/对客文案/写公众号/脚本创作 | 对客写作铁律 + 叙事声音规范 + 内容审核 |
| [zhike-task-hub](zhike-task-hub/SKILL.md) | 今天做了什么/本周总结/任务同步 | Todo存档 + 早晚报 + 周月报 + 对话查询 |
| [project-kanban](project-kanban/SKILL.md) | 看板状态/项目进度/任务分配 | 飞书多维表格 + 日历 + 任务三引擎项目跟踪 |

### 🗺️ 旅行

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [travel-intel](travel-intel/SKILL.md) | 搜一下知识库/查XX景点信息/行业动态 | 4通道采集→入库→过期校验→分级报告 |
| [travel-itinerary](travel-itinerary/SKILL.md) | 规划行程/做个行程/去XX玩几天 | 7步智能行程规划（天气→搜索→POI→费用→双版文档） |
| [trip-landing](trip-landing/SKILL.md) | 生成落地页/生成行程页/做成网页版 | 一键生成5 TAB SPA → PWA离线 → OSS部署 → 自动清理 |

---

## 🚀 快速开始

### 安装到 Hermes Agent

```bash
# 方式一：直接加载
hermes -s advanced-elicitation

# 方式二：安装到技能目录
cp advanced-elicitation/SKILL.md ~/.hermes/skills/methodology/advanced-elicitation/
```

### 独立使用

每个 `SKILL.md` 文件都是自包含的——任何支持 SKILL.md 格式的 Agent 框架都可以直接加载。

```bash
# 在 Claude Code / Cursor / Windsurf 等 IDE 中
# 将 SKILL.md 内容粘贴到 .claude/skills/ 或 .cursorrules 中
```

---

## 📖 技能详解

### 🧠 方法论技能

#### 1. advanced-elicitation — 结构化深度追问

> **触发**：深度审视 / 换个角度 / Push deeper / Red team / 第二意见

产出不是终点——深度审视是质量的门禁。

**能力**：
- **69种追问方法**，按9大类别组织（高级推理8种、核心方法11种、风险分析7种、协作模式11种、创造性7种、框架重构3种、竞争对抗3种、技术审查5种、其他14种）
- 智能选择：根据内容类型（方案/代码/文档/决策/架构）自动推荐5种最匹配方法
- 迭代审视：每次执行一种方法 → 展示发现 → 返回菜单 → 用户选择下一种或退出

**适用场景**：
- answer Phase 7 审查完成 → 对关键发现运行 2-3 种方法深度审视
- 复杂方案交付前 → Pre-mortem + First Principles + Inversion
- 竞品分析报告 → Stakeholder Lens + Red Team + 5 Whys
- 架构设计评审 → Architecture Decision Records + Assumption Audit

**联动**：可被 `answer` / `travel-intel` / `feishu-html` 调用

---

#### 2. blue-team — 业务蓝军内容审核

> **触发**：帮我看看这个方案 / challenge一下 / 压力测试 / 破坏性审议

模拟最挑剔的挑战者，通过6阶段审查逼迫方案暴露逻辑断层。

**能力**：
- 本质还原：这个方案到底在说什么？
- 死亡假设：如果失败，最可能的死因？
- 苏格拉底追问：未被验证的前提假设？
- 逻辑遍历：从结论倒推，每一步是否必然导出下一步？
- 竞争替代：不这么做，还有哪些更好的方式？

**适用场景**：方案评审、BP审查、策略文档自检、脚本审核、运营方案压力测试

---

### 🏗️ 构建技能

#### 3. answer — AI Native's Workflow(er)

> **触发**：answer / 从零开始 / 帮我规划 / 设计方案 / 拆解问题 / from scratch

7阶段结构化工作流编排器，将模糊想法转化为可执行的完整方案。

**7阶段管线**：
1. **Clarify** — 决策树遍历，追问到底
2. **Brief** — 结构化简报（目标/约束/成功标准）
3. **Architect** — 定义结构/层次/关系/流程
4. **Standards** — 建立可复用标准/模式/规范
5. **Decompose** — 拆解为独立可验证的增量任务
6. **Build** — 按任务逐步构建交付物
7. **Review** — 对照简报逐项检查 + blue-team压力测试

**能力**：
- 6大领域适配（技能/业务/方案/流程/分析/决策）
- 100+ 触发词
- 飞书 Wiki 全链路产出
- 活文档纪律——中断后可恢复
- 可调用 AE/ER/blue-team 作为增强审查层

**适用场景**：从零构建任何复杂任务——新业务、新技能、新方案、SOP、调研报告、决策分析、营销计划

---

### 🔍 质量审查技能

#### 4. edge-case-hunter — 边界条件穷举审查

> **触发**：边界检查 / edge case / 穷举测试 / 所有情况都覆盖了吗

纯路径追踪器——不判断代码好坏，只机械式走查每条分支路径，报告未处理的。

**能力**：
- **7维穷举**：控制流 / 数据边界 / 状态边界 / 时间边界 / 资源边界 / 用户边界 / 隐式边界
- 纯 JSON 输出：`[{location, trigger_condition, guard_snippet, potential_consequence}]`
- 方法论驱动非直觉驱动——机械式遍历，不遗漏

**适用场景**：
- PR diff 审查 → 合并到 github-code-review 的 Critical/Warnings
- HTML SPA 部署前 → 检查所有交互状态（空/加载/错误/权限）
- Bug 修复验证 → 确认修复覆盖全部边界而非仅当前触发的那一个

**联动**：可被 `github-code-review` / `feishu-html` / `systematic-debugging` 调用

---

#### 5. editorial-review-prose — 临床级文本编辑

> **触发**：审一下文案 / review the prose / 文本审查 / edit this

审查文案的沟通问题，输出三列表格修订建议。基于微软写作风格指南。

**能力**：
- **7维审查**：语法准确性 / 简洁性 / 清晰度 / 一致性 / 可读性 / 准确性 / 语调
- **三列表格输出**：原文 | 修订后 | 变更说明
- **最小干预原则**：应用最小改动实现清晰，尊重作者声音
- **内容神圣不可侵犯**：永远不挑战观点——只优化表达方式

**与 zhike-content-output 搭档**：
```
营销文案产出后 → zhike-content-output 提供铁律（写什么）
→ ER-P 将铁律作为 style_guide 传入 → 逐条检查是否符合铁律（写得怎样）
→ 三列表格输出修订建议
```

**适用场景**：对客文案审查、公众号推文润色、方案文档质量门禁、企业简介优化

---

#### 6. editorial-review-structure — 文档结构编辑

> **触发**：结构审查 / 逻辑重排 / 信息架构优化

审查文档结构并提出实质性重组建议。**在文案编辑前运行。**

**能力**：
- **5种结构模型**：线性教程 / 参考数据库 / 概念解释 / 任务定义 / 战略金字塔
- **6类建议**：CUT（删除）/ MERGE（合并）/ MOVE（重排）/ CONDENSE（缩短）/ QUESTION（询问）/ PRESERVE（保留）
- 字数影响估计 + 理解权衡标记
- 人类读者 vs LLM读者 两种优化模式

**适用场景**：
- feishu-html 页面设计前审查 TAB 结构和信息层级
- answer Phase 3 架构文档结构优化
- 知识库首页目录结构定期审查

---

### 📋 飞书系列

#### 7. feishu-html — WEB SPA 制作与部署

> **触发**：做个网页 / 发布到线上 / 部署

将飞书文档或用户内容制作为功能完整的 WEB SPA 应用，部署至阿里云 OSS。

**能力**：
- 7阶段全链路：内容理解→设计规划→制作→权限确认→校验→部署→交付
- Playwright CDP 7项浏览器验证
- 多TAB SPA + 响应式（移动端/桌面端）
- 阿里云 OSS 自动上传 + 绑定域名访问
- 双轨交付：内部飞书文档 + 对外 HTML SPA

---

#### 8. feishu-doc — 飞书文档管理

> **触发**：创建飞书文档 / 归档到知识库

飞书文档的完整生命周期管理——创建、更新、评论、归档。

**能力**：
- 一步法创建（docs+create v2）——避免两步法静默失败陷阱
- 写入后自动校验（revision_id + blocks 验证）
- 评论管理（添加/列表/回复）
- 知识库节点管理（移动/删除/重命名）

---

#### 9. feishu-wiki — 知识库全面管理

> **触发**：知识库巡检 / 目录更新 / 文档归类

飞书知识库的全生命周期自动化管理。

**能力**：
- 递归目录扫描 → 骨架XML生成
- AI文档总结生成（≤200字中文，批量并行处理）
- 分类检测 + 自动移动 + 级联验证
- 变更日志自动记录（最新在上）
- 首页每日5:00自动巡检更新

---

#### 10. feishu-table — 多维表格管理

飞书多维表格（Bitable）和电子表格（Sheet）的完整操作接口。78个 lark-cli 命令 + REST API。

---

### 🏔️ 贵州之客系列

#### 11. zhike-content-output — 内容产出准则

> **触发**：产出文档 / 对客文案 / 写公众号 / 脚本创作

贵州之客品牌的内容产出第一核心原则：工具内化，结果外显。

**能力**：
- 核心区分：价值观/方法论（推理工具，不输出）vs 输出文档（纯净结果）
- 对客写作铁律：不绝对化、不诋毁同行、感官沉浸、文学性语言
- 叙事声音规范：6大特征（第一人称/感官细节/完整句子/不用感叹号/每句值其位置/不给结论给画面）
- 评论回复写作：7条铁律 + 称呼+问句结尾原则
- 视频脚本框架：抖音/视频号/小红书分平台策略
- 搭档 `editorial-review-prose`：铁律（写什么）+ ER-P审查（写得怎样）

---

#### 12. zhike-task-hub — 任务中枢

Todo存档 + 早晚报 + 周月报 + 对话查询。基于飞书 Task v2 API。

#### 13. project-kanban — 项目看板

飞书多维表格（看板）+ 日历（日程）+ 任务（分配）三引擎一站式项目跟踪。

---

### 🗺️ 旅行系列

#### 14. travel-intel — 旅游情报系统

4通道采集 → 入库 → 过期校验 → 分级报告。5个 cron job 自动化运行。

**通道**：L1a百度+夸克 / L1b微博+知乎 / L2站点直抓 / L3 Bitable深度

#### 15. travel-itinerary — 智能行程规划

7步工作流：解析需求 → 天气 → 搜索 → POI → LLM规划 → 费用 → 双版文档。

#### 16. trip-landing — 行程落地页

一键生成5 TAB SPA（概览/行程/地图/须知/安全）→ PWA离线 → 4色板个性化 → OSS部署 → 10天自动清理。

---

## 🔗 使用场景

### 场景1：从零构建一个新业务方案

```
answer → Phase 1-5（澄清→简报→架构→标准→拆解）
→ Phase 6 Build（方案文档 + 落地页）
→ Phase 7 Review
    ├── blue-team（破坏性逻辑审查）
    ├── advanced-elicitation（多视角深度审视）
    └── editorial-review-prose（文案质量门禁）
```

### 场景2：对客营销文案产出

```
zhike-content-output（加载铁律）
→ 撰写文案
→ editorial-review-prose（铁律为 style_guide，三列表格审查）
→ 确认修订
```

### 场景3：代码 PR 审查

```
github-code-review
├── 清单式审查（安全/质量/性能/测试）
└── edge-case-hunter（穷举边界条件 JSON）
→ 合并报告 → 提交 Review
```

### 场景4：制作对客 HTML 展示页

```
feishu-html 7阶段
├── 阶段一B：grill-me 设计决策
├── 阶段二B：editorial-review-structure 审查 TAB 结构
├── 阶段五：Playwright CDP 7项 + edge-case-hunter 交互边界
└── 阶段七：交付链接
```

### 场景5：旅游行业情报监控

```
travel-intel（每日自动采集）
├── L1a 百度+夸克 (06:30)
├── L1b 微博+知乎 (06:35)
├── L2 站点直抓 (07:00)
└── L3 Bitable深度 (每5分钟)
→ 每日简报 (09:00)
→ 周度分析 (周一)
→ 综合洞察 (周六)
```

---

## 📦 安装方法

### 方式一：直接加载

```bash
hermes -s answer -s advanced-elicitation
```

### 方式二：安装到 Hermes 技能目录

```bash
git clone https://github.com/jorinyang/awesome-skills.git
cd awesome-skills

# 安装所有技能
for dir in */; do
  name=$(basename "$dir")
  case "$name" in
    advanced-elicitation|edge-case-hunter) category="methodology" ;;
    editorial-review-prose|editorial-review-structure) category="productivity" ;;
    answer|blue-team) category="productivity" ;;
    feishu-*) category="productivity" ;;
    zhike-*|project-kanban) category="productivity" ;;
    travel-*|trip-landing) category="travel" ;;
    *) continue ;;
  esac
  mkdir -p "$HOME/.hermes/skills/$category/$name"
  cp "$name/SKILL.md" "$HOME/.hermes/skills/$category/$name/"
  echo "✅ $name → $category"
done
```

### 方式三：IDE 中使用

将 SKILL.md 复制到对应 IDE 的技能目录：

| IDE | 路径 |
|-----|------|
| Claude Code | `.claude/skills/<name>/SKILL.md` |
| Cursor | `.cursor/skills/<name>/SKILL.md` |
| Windsurf | `.windsurf/skills/<name>/SKILL.md` |

---

## 🤝 贡献指南

1. 每个技能一个文件夹，包含 `SKILL.md`
2. SKILL.md 必须包含 frontmatter（name / description / version / author）
3. 触发条件明确——不要泛泛的"使用时触发"
4. 步骤可执行——新手 Agent 仅凭此文档即可独立完成任务
5. 提交 PR 前验证：`python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"`

---

## 📝 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | 2026-06-05 | 首次发布：16技能（4新建 + 12精选） |

详见 [Releases](https://github.com/jorinyang/awesome-skills/releases)

---

## 📄 License

MIT — 详见各 SKILL.md 中的作者归属。

---

**Made with ❤️ by Hermes Agent + 杨瑒 (月夜)**
