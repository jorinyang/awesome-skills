# Awesome Skills

> 精心筛选的 Agent Skill 集合 — 为 Hermes Agent 设计，兼容任何支持 SKILL.md 格式的 Agent 框架。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-73-blue)](.)

---

## 📖 目录

- [什么是 Agent Skill](#-什么是-agent-skill)
- [技能索引](#-技能索引)
- [技能详解](#-技能详解)
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

### 🧠 方法论 (8)

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [advanced-elicitation](advanced-elicitation/SKILL.md) | 深度审视/换个角度/red team | 69种追问方法，产出后自动触发多维审视 |
| [blue-team](blue-team/SKILL.md) | 帮我看看这个方案/challenge一下 | 6阶段破坏性逻辑审查，模拟最挑剔的挑战者 |
| [creative-ideation](creative-ideation/SKILL.md) | 帮我想个idea/创意生成 | 创意约束生成器——随机约束激发项目创意 |
| [darwin-skill](darwin-skill/SKILL.md) | 优化技能/技能质量评估 | Agent 技能质量评估与进化——评估/诊断/优化 |
| [editorial-review-prose](editorial-review-prose/SKILL.md) | 审一下文案/文本审查/edit this | 微软基线 × 7维审查 × 三列表格修订 |
| [editorial-review-structure](editorial-review-structure/SKILL.md) | 结构审查/逻辑重排 | 5种结构模型 × 6类重组建议 |
| [edge-case-hunter](edge-case-hunter/SKILL.md) | 边界检查/edge case/穷举测试 | 穷举7维边界条件，纯JSON输出 |
| [systematic-debugging](systematic-debugging/SKILL.md) | 帮我debug/排查这个bug | 4阶段根因调试——方法论驱动非直觉驱动 |

### 🏗️ 构建与设计 (16)

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [answer](answer/SKILL.md) | answer/从零开始/帮我规划 | 7阶段工作流编排器（澄清→简报→架构→标准→拆解→构建→审查） |
| [answer-standalone](answer-standalone/SKILL.md) | answer/从零开始/帮我规划 | 同上，独立部署版本（非Wiki集成） |
| [architecture-diagram](architecture-diagram/SKILL.md) | 架构图/系统架构/云架构 | 白底黑字+蓝红强调 SVG 架构图 16:9 |
| [claude-design](claude-design/SKILL.md) | 做个页面/设计一个landing | 一次性 HTML 制品设计（landing/deck/prototype） |
| [design-md](design-md/SKILL.md) | 参考Apple/Stripe/Linear风格 | 71个品牌 DESIGN.md token 参考库 |
| [feishu-html](feishu-html/SKILL.md) | 做个网页/发布到线上/部署 | 飞书文档 → WEB SPA 制作 + OSS 部署 |
| [fireworks-tech-graph](fireworks-tech-graph/SKILL.md) | AI技术图/Agent架构/UML | AI/Agent 技术图 + UML + 系统架构可视化 |
| [hallmark](hallmark/SKILL.md) | 审查AI味/audit设计/发射前检查 | Anti-AI-slop 58道关卡质量门禁 |
| [html-ppt](html-ppt/SKILL.md) | 做幻灯片/PPT/演示文稿 | HTML 幻灯片工厂——交互式演示 |
| [huashu-design](huashu-design/SKILL.md) | 做原型/设计Demo/高保真UI | HTML高保真原型/动画/幻灯片/变体探索/品牌设计 |
| [humanizer](humanizer/SKILL.md) | 去AI味/润色文案/更像人写的 | 文案去AI味——29种文本模式 |
| [pretext](pretext/SKILL.md) | 创意浏览器demo/交互实验 | @chenglou/pretext 浏览器创意 Demo 构建 |
| [requesting-code-review](requesting-code-review/SKILL.md) | 帮我review/代码审查 | 预提交审查——安全扫描/质量门禁/自动修复 |
| [sketch](sketch/SKILL.md) | 快速mockup/设计变体对比 | 一次性 HTML mockup——2-3变体快速对比 |
| [spike](spike/SKILL.md) | 快速验证/做个实验/try一下 | 一次性验证实验——验证想法可行性 |
| [writing-plans](writing-plans/SKILL.md) | 写个计划/实施方案/规划 | 实现计划撰写——bite-sized任务/路径/代码 |

### 🔧 开发工程 (13)

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [agent-native-cli-design](agent-native-cli-design/SKILL.md) | 设计CLI/agent-native工具 | Agent-Native CLI 设计方法论——四范式决策树 |
| [coding-agents](coding-agents/SKILL.md) | 派Agent干活/并行开发 | 自主AI编码Agent编排与多Agent工作流 |
| [debugging-hermes-tui-commands](debugging-hermes-tui-commands/SKILL.md) | 调试TUI/斜杠命令 | Hermes TUI 斜杠命令调试 |
| [dingtalk-cli](dingtalk-cli/SKILL.md) | 钉钉/dingtalk/dws | 钉钉 CLI (dws)——19服务+PAT授权 |
| [hermes-agent](hermes-agent/SKILL.md) | 配置Hermes/安装插件/设置模型 | Hermes Agent 配置/扩展/贡献指南 |
| [kanban](kanban/SKILL.md) | 看板/任务分解/并行工作 | Hermes Kanban——任务分解+并行worker编排 |
| [node-inspect-debugger](node-inspect-debugger/SKILL.md) | 调试Node/Chrome DevTools | Node.js --inspect + CDP CLI 调试 |
| [opencli](opencli/SKILL.md) | 浏览器操作/opencli | OpenCLI——基于浏览器的59+平台CLI |
| [python-debugpy](python-debugpy/SKILL.md) | 调试Python/pdb/断点 | Python pdb REPL + debugpy 远程 (DAP) |
| [reverse-tunnel-deploy](reverse-tunnel-deploy/SKILL.md) | SSH隧道/内网穿透/deploy | SSH反向隧道部署——localhost→公网 |
| [subagent-driven-development](subagent-driven-development/SKILL.md) | 按计划执行/派子Agent | 子Agent驱动开发——并行执行+两阶段review |
| [supabase-backend](supabase-backend/SKILL.md) | 数据库/后端/Supabase | Supabase 后端——REST API + RLS + 数据建模 |
| [test-driven-development](test-driven-development/SKILL.md) | TDD/测试先行/RED-GREEN | TDD强制实施——红灯→绿灯→重构 |

### 📋 飞书系列 (6)

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [feishu-doc](feishu-doc/SKILL.md) | 创建飞书文档/归档到知识库 | 飞书文档创建、修改、评论管理、归档 |
| [feishu-table](feishu-table/SKILL.md) | 新建多维表格/查询记录 | 飞书多维表格 + 电子表格 CRUD |
| [feishu-wiki](feishu-wiki/SKILL.md) | 知识库巡检/目录更新/文档归类 | 知识库全生命周期管理（扫描→总结→分类→变更日志） |
| [project-kanban](project-kanban/SKILL.md) | 看板状态/项目进度/任务分配 | 飞书多维表格 + 日历 + 任务三引擎项目跟踪 |
| [teams-meeting-pipeline](teams-meeting-pipeline/SKILL.md) | 会议纪要/Teams总结 | Teams 会议纪要流水线——转录→总结→归档 |
| [webhook-subscriptions](webhook-subscriptions/SKILL.md) | webhook/事件驱动/订阅 | Webhook 订阅管理——事件驱动的 Agent 运行 |

### 🏔️ 贵州之客 (11)

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [dingtalk-cli](dingtalk-cli/SKILL.md) | 钉钉/dingtalk/dws | 企业内外协作工具链 |
| [huashu-design](huashu-design/SKILL.md) | 做原型/设计Demo | B2B海报/方案页/品牌视觉 |
| [jimeng-video](jimeng-video/SKILL.md) | 生成视频/即梦/CapCut | 即梦/CapCut AI 视频与图片生成 |
| [project-kanban](project-kanban/SKILL.md) | 看板状态/项目进度 | 飞书三引擎项目跟踪 |
| [supabase-backend](supabase-backend/SKILL.md) | 数据库/后端/Supabase | 数据底座——REST API + RLS |
| [travel-intel](travel-intel/SKILL.md) | 搜一下知识库/行业动态 | 4通道采集→入库→过期校验→分级报告 |
| [travel-itinerary](travel-itinerary/SKILL.md) | 规划行程/去XX玩几天 | 7步智能行程规划（天气→搜索→POI→费用→双版文档） |
| [trip-landing](trip-landing/SKILL.md) | 生成落地页/生成行程页 | 一键生成5 TAB SPA → PWA离线 → OSS部署 |
| [zhike-content-output](zhike-content-output/SKILL.md) | 产出文档/对客文案/写公众号 | 对客写作铁律 + 叙事声音规范 + 内容审核 |
| [zhike-task-hub](zhike-task-hub/SKILL.md) | 今天做了什么/本周总结 | Todo存档 + 早晚周月报 + 对话查询 |
| [amap-lbs](amap-lbs/SKILL.md) | 搜索景点/路径规划/周边 | 高德 LBS——POI/路径/旅游/热力图 |

### 🔬 研究 (8)

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [ara-compiler](ara-compiler/SKILL.md) | 编译论文/结构化论文 | PDF论文→四层ARA可导航格式 |
| [ara-research-manager](ara-research-manager/SKILL.md) | 记录研究进展/ara capture | 研究过程捕获——三阶段流水线 |
| [ara-rigor-reviewer](ara-rigor-reviewer/SKILL.md) | 审查论文/审稿/提交前检查 | 六维认识论审查——评分报告+修改建议 |
| [blogwatcher](blogwatcher/SKILL.md) | 监控博客/RSS订阅 | 博客/RSS/Atom 订阅监控 |
| [codebase-inspection](codebase-inspection/SKILL.md) | 代码统计/项目分析 | pygount LOC/语言/比率分析 |
| [llm-wiki](llm-wiki/SKILL.md) | LLM知识库/关联笔记 | Karpathy LLM Wiki——关联markdown知识库 |
| [polymarket](polymarket/SKILL.md) | 预测市场/Polymarket | Polymarket——市场/价格/订单簿查询 |
| [research-paper-writing](research-paper-writing/SKILL.md) | 写论文/学术写作 | 学术论文写作工作流 |

### 🎨 创意内容 (8)

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [baoyu-article-illustrator](baoyu-article-illustrator/SKILL.md) | 文章配图/插图生成 | 文章插图——类型×风格×调色板一致性 |
| [baoyu-comic](baoyu-comic/SKILL.md) | 知识漫画/科普漫画 | 知识漫画（科普/教育/传记/教程） |
| [baoyu-infographic](baoyu-infographic/SKILL.md) | 信息图/可视化/数据图 | 信息图——21布局×21风格 |
| [gif-search](gif-search/SKILL.md) | 搜GIF/动图搜索 | Tenor GIF 搜索/下载 |
| [heartmula](heartmula/SKILL.md) | AI音乐/歌曲生成 | HeartMuLa——类Suno 歌曲生成 |
| [songsee](songsee/SKILL.md) | 音频分析/频谱图 | 音频频谱/特征——mel/chroma/MFCC |
| [songwriting-and-ai-music](songwriting-and-ai-music/SKILL.md) | 写歌/AI音乐/Suno | 歌曲创作 + Suno AI 音乐提示词 |
| [youtube-content](youtube-content/SKILL.md) | YouTube字幕/视频总结 | YouTube 字幕→摘要/线索/博客 |

### 🗺️ 地图位置 (3)

| 技能 | 触发词 | 核心能力 |
|------|--------|---------|
| [amap-cli](amap-cli/SKILL.md) | 地图可视化/POI控制 | 高德 CLI (amap-gui)——精确地图状态控制 |
| [amap-lbs](amap-lbs/SKILL.md) | 搜索景点/路径规划/周边 | 高德 LBS REST API——POI/路径/热力图 |
| [maps](maps/SKILL.md) | 地址查询/路线规划/POI | OpenStreetMap/OSRM——地理编码/POI/路线 |

---

## 📖 技能详解

### 🧠 方法论

#### 1. advanced-elicitation — 结构化深度追问

> **触发**：深度审视 / 换个角度 / Push deeper / Red team

产出不是终点——深度审视是质量的门禁。

**能力**：69种追问方法 × 9大类 × 智能选择5种最匹配方法 × 迭代审视

**联动**：可被 `answer` / `travel-intel` / `feishu-html` 调用

---

#### 2. blue-team — 业务蓝军内容审核

> **触发**：帮我看看这个方案 / challenge一下 / 压力测试

模拟最挑剔的挑战者，通过6阶段审查逼迫方案暴露逻辑断层。

**能力**：本质还原 / 死亡假设 / 苏格拉底追问 / 逻辑遍历 / 竞争替代

---

#### 3. darwin-skill — Agent 技能质量评估

> **触发**：优化技能 / 评估技能质量 / 技能进化

评估 SKILL.md 质量（触发/步骤/产出/完整性），输出诊断+优化方案。支持方法论吸收冲突矩阵分析。

---

#### 4. editorial-review-prose — 临床级文本编辑

> **触发**：审一下文案 / review the prose / 文本审查

审查文案的沟通问题，输出三列表格修订建议。基于微软写作风格指南。

**与 zhike-content-output 搭档**：铁律（写什么）+ ER-P审查（写得怎样）

---

#### 5. editorial-review-structure — 文档结构编辑

> **触发**：结构审查 / 逻辑重排 / 信息架构优化

审查文档结构并提出实质性重组建议。**在文案编辑前运行。** 5种结构模型 × 6类建议。

---

#### 6. edge-case-hunter — 边界条件穷举审查

> **触发**：边界检查 / edge case / 穷举测试

纯路径追踪器——机械式走查每条分支路径，报告未处理的。7维穷举 × 纯JSON输出。

---

#### 7. systematic-debugging — 系统化调试

> **触发**：帮我debug / 排查这个bug

4阶段根因调试：理解bug→定位根因→修复→验证。方法论驱动非直觉驱动。

---

### 🏗️ 构建与设计

#### 8. answer — AI Native's Workflow(er)

> **触发**：answer / 从零开始 / 帮我规划 / 设计方案

7阶段结构化工作流编排器，将模糊想法转化为可执行的完整方案。

**7阶段管线**：Clarify → Brief → Architect → Standards → Decompose → Build → Review

**能力**：6大领域适配 | 100+ 触发词 | 飞书 Wiki 全链路产出 | 活文档纪律 | AE/ER/blue-team 增强审查

---

#### 9. huashu-design — 花叔Design

> **触发**：做原型 / 设计Demo / 交互原型 / HTML演示 / UI mockup

用HTML做高保真原型、交互Demo、幻灯片、动画、设计变体探索+设计方向顾问的一体化设计能力。

**能力**：iOS/Android原型 | 20种设计哲学 | 品牌资产协议 | B2B海报 | 动画导出 | 专家评审

---

#### 10. hallmark — Anti-AI-Slop 质量门禁

> **触发**：审查AI味 / audit设计 / 提取设计DNA / 发射前检查

58道反AI-slop关卡 + 六轴预发射自评（P/H/E/S/R/V）。从 Nutlope/hallmark (MIT) 适配。

**能力**：视觉反模式 | 排版纪律 | 交互动效 | 内容诚信 | 移动端硬地板

**联动**：已集成到 `feishu-html` 阶段五和 `huashu-design` 反AI slop章节

---

#### 11. design-md — 品牌设计Token参考库

> **触发**：参考Apple/Stripe/Linear风格 / 品牌设计

71个品牌的 DESIGN.md token 规范文件。作为 `claude-design` 和 `huashu-design` 的品牌Token补充参考层。

---

#### 12. feishu-html — WEB SPA 制作与部署

> **触发**：做个网页 / 发布到线上 / 部署 / 做个展示页

将飞书文档或用户内容制作为功能完整的 WEB SPA 应用，部署至阿里云 OSS。

**能力**：7阶段全链路 | Playwright CDP 7项验证 | 多TAB SPA + 响应式 | 双轨交付 | Hallmark 质量门禁集成

---

#### 13. humanizer — 文案反AI味

> **触发**：去AI味 / 润色文案 / 更像人写的

29种文本模式去除AI写作痕迹——与 `hallmark`（UI反AI味）形成文案+视觉双重防线。

---

### 🔧 开发工程

#### 14. subagent-driven-development — 子Agent驱动开发

> **触发**：按计划执行 / 派子Agent / 并行开发

按 `writing-plans` 产出的计划，通过 delegate_task 并行派发子Agent，两阶段review。

---

#### 15. test-driven-development — TDD强制执行

> **触发**：TDD / 测试先行 / RED-GREEN-REFACTOR

严格实施 TDD 循环：先写失败测试→最小实现→重构。测试不过不写功能代码。

---

#### 16. supabase-backend — Supabase 后端

> **触发**：数据库 / 后端 / Supabase / 数据建模

Supabase 数据底座——REST API + Row Level Security + 数据建模 + 迁移脚本。

---

### 🔬 研究

#### 17. ara-research-manager — 研究过程捕获

> **触发**：记录研究进展 / ara capture / 研究session结束

三阶段流水线（Harvester→Router→Maturity Tracker）自动扫描研究session，将决策/实验/死胡同/声明写入 ARA 四层结构。适应自 Orchestra-Research/Agent-Native-Research-Artifact (MIT)。

**能力**：渐进结晶 | 来源标记 | 死胡同追踪 | 五类DAG节点

---

#### 18. ara-compiler — 文献结构化编译器

> **触发**：编译论文 / 结构化这篇论文 / 把论文转成ARA

将PDF论文/代码仓库转化为四层 ARA 可导航格式，消除叙事税和工程税。

---

#### 19. ara-rigor-reviewer — 论文质量审查

> **触发**：审查论文 / 审稿 / 提交前检查

六维认识论审查（证据相关性/可证伪性/范围校准/论证连贯性/探索完整性/方法论严谨性），产出评分报告。

---

### 🏔️ 贵州之客系列

#### 20. zhike-content-output — 内容产出准则

> **触发**：产出文档 / 对客文案 / 写公众号 / 脚本创作

贵州之客品牌的内容产出第一核心原则：工具内化，结果外显。

**能力**：对客写作铁律 | 叙事声音6大特征 | 评论回复7条铁律 | 视频脚本框架

---

#### 21. travel-intel — 旅游情报系统

> **触发**：搜一下知识库 / 查XX景点信息 / 行业动态

4通道采集 → 入库 → 过期校验 → 分级报告。5个 cron job 自动化运行。

---

#### 22. travel-itinerary — 智能行程规划

> **触发**：规划行程 / 做个行程 / 去XX玩几天

7步工作流：解析需求 → 天气 → 搜索 → POI → LLM规划 → 费用 → 双版文档。

---

#### 23. trip-landing — 行程落地页

> **触发**：生成落地页 / 生成行程页 / 做成网页版

一键生成5 TAB SPA（概览/行程/地图/须知/安全）→ PWA离线 → OSS部署 → 10天自动清理。

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
→ huashu-design（设计视觉方向）
→ 撰写文案 + 设计
→ hallmark audit（反AI-slop检查）
→ editorial-review-prose（铁律为 style_guide，三列表格审查）
→ feishu-html（部署上线）
```

### 场景3：学术论文研究

```
ara-compiler（结构化相关文献）
→ 进行研究工作（实验/分析/写作）
→ ara-research-manager（每session存档）
→ ara-rigor-reviewer（提交前六维审查）
→ 修复Critical → 提交
```

### 场景4：代码 PR 审查

```
requesting-code-review
├── 清单式审查（安全/质量/性能/测试）
└── edge-case-hunter（穷举边界条件 JSON）
→ 合并报告 → 提交 Review
```

### 场景5：旅游行业情报监控

```
travel-intel（每日自动采集）
├── L1a 百度+夸克 (06:30)
├── L1b 微博+知乎 (06:35)
├── L2 站点直抓 (07:00)
└── L3 Bitable深度 (每5分钟)
→ 每日简报 (09:00) → 周度分析 → 综合洞察
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
    advanced-elicitation|edge-case-hunter|systematic-debugging|darwin-skill|creative-ideation) category="methodology" ;;
    editorial-review-prose|editorial-review-structure) category="productivity" ;;
    answer|answer-standalone|blue-team) category="productivity" ;;
    feishu-*|zhike-*|project-kanban|teams-meeting-pipeline) category="productivity" ;;
    travel-*|trip-landing) category="travel" ;;
    huashu-design|claude-design|hallmark|architecture-diagram|design-md|fireworks-tech-graph|html-ppt|humanizer|pretext|sketch) category="creative" ;;
    ara-*|blogwatcher|llm-wiki|polymarket|codebase-inspection|research-paper-writing) category="research" ;;
    subagent-driven-development|test-driven-development|coding-agents|agent-native-cli-design|writing-plans|spike) category="software-development" ;;
    supabase-backend|dingtalk-cli|reverse-tunnel-deploy|kanban|webhook-subscriptions|hermes-agent) category="devops" ;;
    maps|amap-*|jimeng-video) category="mapping" ;;
    opencli|xurl|himalaya) category="social-media" ;;
    *) continue ;;
  esac
  mkdir -p "$HOME/.hermes/skills/$category/$name"
  cp "$name/SKILL.md" "$HOME/.hermes/skills/$category/$name/"
  echo "✅ $name → $category"
done
```

### 方式三：IDE 中使用

| IDE | 路径 |
|-----|------|
| Claude Code | `.claude/skills/<name>/SKILL.md` |
| Cursor | `.cursor/skills/<name>/SKILL.md` |
| Windsurf | `.windsurf/skills/<name>/SKILL.md` |

---

## 🤝 贡献指南

1. 每个技能一个文件夹，包含 `SKILL.md`
2. SKILL.md 必须包含 frontmatter（name / description / version / author / license）
3. 触发条件明确——不要泛泛的"使用时触发"
4. 步骤可执行——新手 Agent 仅凭此文档即可独立完成任务
5. 提交 PR 前验证：`python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"`

---

## 📝 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.0.0 | 2026-06-11 | 73技能（+57新增：ARA三件套/Hallmark门禁/花叔Design/品牌Token库/开发方法论/创意内容/地图位置） |
| v1.0.0 | 2026-06-05 | 首次发布：16技能 |

详见 [Releases](https://github.com/jorinyang/awesome-skills/releases)

---

## 📄 License

MIT — 详见各 SKILL.md 中的作者归属。

---

**Made with ❤️ by Hermes Agent + 杨瑒 (月夜)**
