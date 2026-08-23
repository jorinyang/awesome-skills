# Awesome Skills



> 精选 Agent Skill 集合 — 自建核心 + 三方吸收 + 方法论开发。为 Hermes Agent 设计，兼容任何支持 SKILL.md 格式的 Agent 框架。



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[![Skills](https://img.shields.io/badge/Skills-117-blue)](.)



---



## 📖 目录



- [什么是 Agent Skill](#-什么是-agent-skill)

- [技能索引](#-技能索引)

- [技能详解](#-技能详解)

- [使用场景](#-使用场景)

- [安装方法](#-安装方法)

- [贡献指南](#-贡献指南)



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



### 🧠 方法论 (26)



| 技能 | 触发词 | 核心能力 |

|------|------|----------|

| [advanced-elicitation](advanced-elicitation/SKILL.md) | 深度审视/换个角度/red team | 69+3种追问方法，产出后自动触发多维审视 |

| [author-methodology-analysis](author-methodology-analysis/SKILL.md) | 分析博主方法论/拆解公众号套路/提炼写作框架/内容方法论 | 21维度作者内容方法论分析→报告+文案框架+HTML看板+飞书同步 |
| [batch-course-delivery](batch-course-delivery/SKILL.md) 🆕 | 批量培训/批量交付/一门课讲很多场/场次配置单 | 冻结框架+适配规则书+场次配置单——一门课对多客户批量交付，AI工作流派生PPT/手册/题库/工具包 |

| [blue-team](blue-team/SKILL.md) | 帮我看看这个方案/challenge一下 | 6阶段破坏性逻辑审查 |

| [book-deconstruct](book-deconstruct/SKILL.md) | 拆书/拆这本/这本书在讲什么 | 五件事拆书法——问题→基线→delta→落点→内核 |

| [darwin-skill](darwin-skill/SKILL.md) | 优化技能/技能质量评估 | Agent 技能质量评估与进化 |

| [deep-think](deep-think/SKILL.md) | 想透/追本/本质是什么/深挖 | 追本之箭——纵向深钻思维，一路钻到不可再分的本质 |

| [domain-decompose](domain-decompose/SKILL.md) | 降秩/找秩/背后是什么/底层逻辑 | 降秩引擎——找不可约独立生成器，配9种取景框 |

| [edge-case-hunter](edge-case-hunter/SKILL.md) | 边界检查/edge case/穷举测试 | 穷举7维边界条件，纯JSON输出 |

| [editorial-review-prose](editorial-review-prose/SKILL.md) | 审一下文案/文本审查 | 微软基线 × 7维审查 × 三列表格修订 |

| [editorial-review-structure](editorial-review-structure/SKILL.md) | 结构审查/逻辑重排 | 5种结构模型 × 6类重组建议 |

| [github-absorb](github-absorb/SKILL.md) 🆕 | 评估仓库/这个项目怎么样/吸收仓库 | GitHub仓库全流程评估→吸收——代码分析/业务价值/吸收策略/测试验证 |

| [ljg-elicitation-modes](ljg-elicitation-modes/SKILL.md) | 解剖概念/圆桌讨论/降秩审视 | advanced-elicitation增强——八维解剖+圆桌+降秩审视三种模式 |

| [ljg-infographic-design](ljg-infographic-design/SKILL.md) | 信息图设计判断 | baoyu-infographic增强——密度×结构×情绪三维诊断 |

| [ljg-writing-voice](ljg-writing-voice/SKILL.md) | 写作声音/写作哲学 | humanizer增强——ljg-writes最高法则+语言铁律 |

| [qa-extract](qa-extract/SKILL.md) | 问答/Q&A/QA/抽取问题 | 信息提问机——核心观点抽成Q-A链，Q切要害A有形式化收口 |

| [relationship-analysis](relationship-analysis/SKILL.md) | 关系分析/分析关系/为什么总是 | 五层结构诊断+精神分析，不给建议只提问 |

| [pm-prioritization-frameworks](pm-prioritization-frameworks/SKILL.md) 🆕 | 优先级排序/怎么排优先级/RICE还是ICE | 9种优先级框架速查——Opportunity Score/ICE/RICE/Kano/MoSCoW等 |

| [stakeholder-mapping](stakeholder-mapping/SKILL.md) 🆕 | 干系人分析/stakeholder map/谁会影响这个项目 | Power×Interest矩阵定位+四象限沟通策略+冲突识别 |

| [opportunity-solution-tree](opportunity-solution-tree/SKILL.md) 🆕 | 机会方案树/OST/产品发现/从问题到方案 | Teresa Torres四层发现树——Outcome→Opportunity→Solution→Experiment |

| [external-skill-evaluation](external-skill-evaluation/SKILL.md) 🆕 | 评估外部技能/这个skill对我们有用吗 | 能力扫描→深度阅读→业务映射→风险识别→优先级排序→吸收策略 |

| [writing-skills](writing-skills/SKILL.md) 🆕 | 创建技能/写skill/技能测试/技能验证/技能质量 | TDD驱动的技能工程——压力测试→基线失败→写技能→封堵漏洞 |

| [verification-before-completion](verification-before-completion/SKILL.md) 🆕 | 完成了/修好了/通过了/发布/deploy/验证 | Iron Law门禁——证据先于声明，未验证不声称完成 |

| [darwin-skill-cron](darwin-skill-cron/SKILL.md) 🆕 | darwin cron/技能自动巡检/skill nightly optimize | Darwin Skill Cron自动化模式——9维评分+棘轮机制+并行子agent+自包含prompt模板

| [double-evolution](double-evolution/SKILL.md) 🆕 | 技能进化/双速进化/MOMO CODE/Pioneer | 双速技能进化引擎——吸收MOMO CODE/Pioneer Agent方法论，技能自优化 |

| [repo-source-deepread](repo-source-deepread/SKILL.md) 🆕 | 精读源码/深入分析这个仓库的实现/看看XX怎么做的/这个项目的XX机制怎么实现的/从源码里学设计 | 大型远程源码仓库深读法——git trees API 定位子系统 + AST 骨架提取（docstring/签名/常量），批量 execute_code 防上下文爆炸 |

### 🏗️ 构建与设计 (26)



| 技能 | 触发词 | 核心能力 |

|------|--------|---------|

| [answer](answer/SKILL.md) | answer/从零开始/帮我规划 | 7阶段工作流编排器 |

| [answer-standalone](answer-standalone/SKILL.md) | answer/从零开始 | 同上，独立部署版（非Wiki集成） |

| [dynamic-workflow](dynamic-workflow/SKILL.md) | 编排多Agent/并行工作流 | 自动构建并执行动态多Agent工作流 |

| [architecture-diagram](architecture-diagram/SKILL.md) | 架构图/系统架构/云架构 | 暗色主题 SVG 架构图 16:9 |

| [drawio-generation](drawio-generation/SKILL.md) 🆕 | drawio/可编辑图表/专业架构图/客户方案图 | Draw.io XML 专业图表生成→PNG/SVG/PDF导出，五维质控 |

| [brandkit](brandkit/SKILL.md) | 品牌设计/Logo设计/品牌视觉 | 品牌策略+5种Logo手法+8种视觉模式——设计决策层 |

| [claude-design](claude-design/SKILL.md) | 做个页面/设计一个landing | 一次性 HTML 制品设计 |

| [design-md](design-md/SKILL.md) | 参考Apple/Stripe风格 | 71品牌 DESIGN.md token 参考库 |

| [feishu-html](feishu-html/SKILL.md) | 做个网页/发布到线上/部署 | 飞书文档 → WEB SPA 制作 + OSS 部署 |

| [fireworks-tech-graph](fireworks-tech-graph/SKILL.md) | 画图/架构图/流程图/可视化 | NL→SVG+PNG 技术图表，五维质控+轻量路由+设计语言注入 |

| [hallmark](hallmark/SKILL.md) | 审查AI味/audit/发射前检查 | Anti-AI-slop 58道关卡质量门禁 |

| [html-ppt](html-ppt/SKILL.md) | 做幻灯片/PPT/演示文稿 | HTML 幻灯片工厂 |

| [huashu-design](huashu-design/SKILL.md) | 做原型/设计Demo/高保真UI | HTML高保真原型/动画/幻灯片/品牌设计 |

| [humanizer](humanizer/SKILL.md) | 去AI味/润色文案 | 29种文本模式去除AI写作痕迹 |

| [pretext](pretext/SKILL.md) | 创意浏览器demo | @chenglou/pretext 创意 Demo |

| [redesign-skill](redesign-skill/SKILL.md) | redesign/升级设计/翻新页面 | 7维60+项审计→诊断→修复——页面系统性升级 |

| [requesting-code-review](requesting-code-review/SKILL.md) | 帮我review/代码审查 | 预提交审查——安全/质量/自动修复 |

| [sketch](sketch/SKILL.md) | 快速mockup/设计变体对比 | 一次性 HTML——2-3变体对比 |

| [strategy-plan-writing](strategy-plan-writing/SKILL.md) | 写战略/写方案/商业计划 | 商业战略、运营规划、市场分析方案写作 |

| [taste-skill](taste-skill/SKILL.md) | 设计方向/设计调参/风格方向 | 三旋钮(V/M/D)+Brief推断+风格预设——设计管线第一环 |

| [writing-plans](writing-plans/SKILL.md) | 写个计划/实施方案 | 实现计划——bite-sized任务/路径/代码 |

| [web-spa](web-spa/SKILL.md) 🆕 | 写Web SPA/前端陷阱/全屏演示 | CSS居中+溢出坑、数据加载、JS作用域、选项格式化管道 |

| [requirement-alignment-analysis](requirement-alignment-analysis/SKILL.md) 🆕 | 需求对齐差异分析/PRD对比/需求变更分析 | 多轮需求对齐后逐项对比——原有/差异/新增/待确定状态 |

| [dashiai-ppt-hermes](dashiai-ppt-hermes/SKILL.md) 🆕 | 做PPT/生成PPT/DashiAI PPT/大师PPT/网页PPT/汇报材料 | DashiAI PPT生成器——12套视觉主题+1020个版式，浏览器编辑+导出PPTX/PDF

| [diagram-cjk-rendering](diagram-cjk-rendering/SKILL.md) 🆕 | CJK图表/中文SVG/口字/兜底字体 | cairosvg CJK字体渲染兜底——「口」字检测→修复→验证流程 |
| [training-content-restructure](training-content-restructure/SKILL.md) 🆕 | 培训材料全局调整/整库重构/移除模块/学练比重构 | 培训资料全链路重构——级联同步+一致性治理+HTML产物验证 |


### 🔧 开发工程 (25)



| 技能 | 触发词 | 核心能力 |

|------|--------|---------|

| [agent-native-cli-design](agent-native-cli-design/SKILL.md) | 设计CLI/agent-native工具 | Agent-Native CLI 四范式决策树 |

| [cross-project-adaptation](cross-project-adaptation/SKILL.md) | 跨项目借鉴/模式迁移 | 跨项目适配——概念/模式/算法迁移 |

| [coding-agents](coding-agents/SKILL.md) | 派Agent干活/并行开发 | 自主AI编码Agent编排 |

| [dingtalk-cli](dingtalk-cli/SKILL.md) | 钉钉/dingtalk/dws | 钉钉 CLI——19服务+PAT授权 |

| [subagent-driven-development](subagent-driven-development/SKILL.md) | 按计划执行/派子Agent | 子Agent驱动——并行执行+两阶段review |

| [executing-plans](executing-plans/SKILL.md) 🆕 | 执行计划/实现/按计划构建/跑任务清单 | 加载计划→批判审查→逐步执行→完成报告（无子代理回退方案） |

| [finishing-a-development-branch](finishing-a-development-branch/SKILL.md) 🆕 | 开发完成/合并分支/创建PR/收尾/发布 | 结构化4选项——合并/PR/保留/丢弃+工作区清理 |

| [receiving-code-review](receiving-code-review/SKILL.md) 🆕 | code review/审查意见/PR反馈/review feedback | 技术严谨回应——验证后实现，不盲从不表演 |

| [supabase-backend](supabase-backend/SKILL.md) | 数据库/后端/Supabase | Supabase 数据底座——REST API + RLS |

| [test-driven-development](test-driven-development/SKILL.md) | TDD/测试先行 | TDD强制实施——红灯→绿灯→重构 |

| [wsl-browser-cdp](wsl-browser-cdp/SKILL.md) ⚠️仅WSL | WSL连Chrome/浏览器CDP | ⚠️仅WSL环境适用——通过CDP连接Windows Chrome（Windows原生环境Chrome直连，无需此技能） |

| [hermes-instance-sync](hermes-instance-sync/SKILL.md) 🆕 | 同步技能/实例间同步/技能对齐 | Hermes实例间Skill同步——双源对比+分类+备份+软链接 |

| [technical-documentation-production](technical-documentation-production/SKILL.md) 🆕 | 产出技术文档/PRD/ER图/架构图 | 技术文档套件——PRD+ER图+架构图+流程图+交叉校验 |

| [windows-troubleshooting-from-wsl](windows-troubleshooting-from-wsl/SKILL.md) ⚠️仅WSL | Windows修复/服务诊断 | ⚠️仅WSL环境适用——bash→PowerShell桥接诊断修复（Windows原生环境直接使用PowerShell） |

| [wsl-docker-deploy](wsl-docker-deploy/SKILL.md) 🆕 | 部署docker/自托管/docker pull超时/拉取镜像失败 | WSL2 Docker Desktop代理部署——crane代理拉取→docker load→compose up |

| [firecrawl-web](firecrawl-web/SKILL.md) 🆕 | 搜索/查资料/抓取/爬取/提取数据 | Firecrawl自托管MCP——搜索网页/抓取内容/爬取网站/结构化数据提取 |

| [github-release-readme](github-release-readme/SKILL.md) 🆕 | 同步技能/更新awesome-skills/发release | GitHub同步→README更新→Release创建流水线 |

| [alicloud-fc-deploy](alicloud-fc-deploy/SKILL.md) 🆕 | 部署FC/函数计算/阿里云FC/Serverless部署/fcapp.run | 阿里云FC部署Python函数——OpenAPI创建服务/函数/HTTP触发器+ACS3-HMAC-SHA256签名+WSGI模板

| [hermes-performance-diagnosis](hermes-performance-diagnosis/SKILL.md) 🆕 | 执行慢/很慢/卡住了/性能/优化/诊断 | Hermes性能瓶颈诊断——文件搜索/网络搜索/LLM推理三大根因+优先级修复

| [hermes-windows-native](hermes-windows-native/SKILL.md) 🆕 | Windows原生/Hermes Windows配置 | Hermes Agent Windows原生配置+故障排查（post-WSL迁移）

| [question-bank-pipeline](question-bank-pipeline/SKILL.md) 🆕 | 题库/quiz system/知识竞答/试卷/题目导入/大比武 | 题库全栈开发管线——docx/xlsx/md解析→Supabase JSONB→Web SPA大屏→OSS部署

| [wukong-skill-center](wukong-skill-center/SKILL.md) 🆕 | 悟空技能中心/企业技能中心/Wukong Skill Hub/技能路由/ExclusiveSkillHub | 钉钉悟空企业技能中心集成——SkillBridge iframe+FC路由服务两种模式 |

| [github-sync-cron-pitfalls](github-sync-cron-pitfalls/SKILL.md) 🆕 | GitHub skill-repo sync cron troubleshooting/class-level pitfalls | 日常 sync cron 踩过的类级坑——codeload 429 fallback、reset --soft race、CRLF 归一化、unclassified 三子桶、bytes ratio 截获精简版 |
| [github-skill-repo-cron](github-skill-repo-cron/SKILL.md) | 类级 cron 规范/github仓库自动同步/sync cron/七阶段闭环 | 七阶段抽象——双源扫描+symlink穿透+CRLF归一+方向验证+bytes ratio+unclassified三子桶；会话级细节留给 github-release-readme |
| [dingtalk-minutes-extraction](dingtalk-minutes-extraction/SKILL.md) 🆕 | 听记/会议记录/会议摘要/AI听记/会议转写 | 钉钉AI听记提取——会议转写+AI摘要+待办拉取 |


### 🤖 AI 工程 (4) 🆕



| 技能 | 触发词 | 核心能力 |

|------|--------|---------|

| [skill-evaluator](skill-evaluator/SKILL.md) 🆕 | 评测skill/技能质量 | 三维评测(精准度×时效×成本)+LLM法官+过程追溯+靶向归因+自动触发 |

| [skill-ab-test](skill-ab-test/SKILL.md) 🆕 | AB测试/对比skill | A/B对比测试——对照组vs实验组自动评测+三维决策(能力/成本/稳定性) |

| [benchmark-generator](benchmark-generator/SKILL.md) 🆕 | 生成测试集/造benchmark | 从Skill定义自动生成routing+outcome测试集+去重入库 |

| [agent-tool-system](agent-tool-system/SKILL.md) 🆕 | Agent工具/工具系统/defineTool/toolsToAI | defineTool→registry→toolsToAI三层架构+ToolLog调试+StepBudget步数预算 |



### 📋 飞书系列 (7)



| 技能 | 触发词 | 核心能力 |

|------|--------|---------|

| [feishu-doc](feishu-doc/SKILL.md) | 创建飞书文档/归档 | 飞书文档创建/修改/评论/归档 |

| [feishu-table](feishu-table/SKILL.md) | 新建多维表格/查询 | 飞书多维表格 + 电子表格 CRUD |

| [feishu-wiki](feishu-wiki/SKILL.md) | 知识库巡检/首页更新 | 每日巡检+文档总结+分类检测+变更日志（space=7643710721485753535） |

| [feishu-voice](feishu-voice/SKILL.md) 🆕 | 飞书语音/语音消息/转录语音 | 飞书语音消息转录——OGG→ASR秒级识别/妙记回落，自动返回逐字稿 |

| [feishu-wiki-file-routing](feishu-wiki-file-routing/SKILL.md) 🆕 | 飞书wiki降级/file类型/wiki节点不是文档/wiki路由降级 | 飞书知识库 /wiki/ URL 路由降级——当 lark-doc 无法处理 file 类型节点时的发现→下载→提取流程；与 lark-doc/lark-wiki/lark-drive 协同 |

| [project-kanban](project-kanban/SKILL.md) | 看板状态/项目进度 | 表格+日历+任务三引擎跟踪 |

| [zhike-task-hub](zhike-task-hub/SKILL.md) | 今天做了什么/本周总结 | Todo存档 + 早晚周月报 |



### 🏔️ 贵州之客 · 旅行社全链路 (16)



| 技能 | 触发词 | 核心能力 |

|------|--------|---------|

| [amap-lbs](amap-lbs/SKILL.md) | 搜索景点/路径规划/周边 | 高德 LBS——POI/路径/旅游/热力图 |

| [jimeng-video](jimeng-video/SKILL.md) | 生成视频/即梦/CapCut | AI视频与图片生成 |

| [travel-intel](travel-intel/SKILL.md) | 搜一下知识库/行业动态 | 4通道采集→入库→分级报告 |

| [travel-itinerary](travel-itinerary/SKILL.md) | 规划行程/去XX玩几天 | 7步智能行程规划 |

| [travel-workflow](travel-workflow/SKILL.md) 🆕 | 旅行社工作流/一键出团 | 一条 trip.json → 8技能全链路（报价→通知书→执行单→归档） |

| [trip-landing](trip-landing/SKILL.md) | 生成落地页/生成行程页 | 一键5 TAB SPA → PWA → OSS部署 |

| [wechat-article-archive](wechat-article-archive/SKILL.md) | 采集公众号/公众号归档/微信文章转Markdown | 公众号文章采集→Markdown归档→ZIP打包→飞书同步 |

| [zhike-content-output](zhike-content-output/SKILL.md) | 产出文档/对客文案 | 对客写作铁律 + 叙事声音规范 |

| [trip-quote](trip-quote/SKILL.md) | 生成报价单/做报价 | 报价单→PDF（团建/私人定制/研学/散客4风格） |

| [trip-briefing](trip-briefing/SKILL.md) | 出团通知书 | 对客PDF→行程/住宿/餐饮/交通/安全/天气 |

| [guide-exec](guide-exec/SKILL.md) | 导游执行单/执行单 | 12章飞书docx→名单(身份证/保险)/行程/对接/物资/应急 |

| [supply-check](supply-check/SKILL.md) | 物资清单/核对物资 | 行程物资逐项核对→飞书docx勾选表 |

| [vendor-brief](vendor-brief/SKILL.md) | 供应商对接/对接单 | 酒店/车辆/地接 ×3 PDF对接单 |

| [cost-engine](cost-engine/SKILL.md) | 成本核算/市场比价 | 成本分项+OTA实时比价→定价建议 |

| [trip-archive](trip-archive/SKILL.md) | 团后归档 | 全部出团文档→知识库5节点自动归档 |

| [customer-view](customer-view/SKILL.md) | 客户打包/客户文档包 | 报价单+通知书+须知→单PDF打包 |



### 🔬 研究 (4)



| 技能 | 触发词 | 核心能力 |

|------|--------|---------|

| [ara-compiler](ara-compiler/SKILL.md) | 编译论文/结构化论文 | PDF论文→四层ARA可导航格式 |

| [ara-research-manager](ara-research-manager/SKILL.md) | 记录研究进展/ara capture | 研究过程捕获——三阶段流水线 |

| [ara-rigor-reviewer](ara-rigor-reviewer/SKILL.md) | 审查论文/审稿 | 六维认识论审查 |

| [systematic-debugging](systematic-debugging/SKILL.md) | 帮我debug/排查bug | 4阶段根因调试 |



### 🎨 创意内容 (9)



| 技能 | 触发词 | 核心能力 |

|------|--------|---------|

| [baoyu-article-illustrator](baoyu-article-illustrator/SKILL.md) | 文章配图/插图生成 | 文章插图——类型×风格×调色板 |

| [baoyu-comic](baoyu-comic/SKILL.md) | 知识漫画/科普漫画 | 知识漫画（科普/教育/传记） |

| [baoyu-cover-image](baoyu-cover-image/SKILL.md) | 封面图/文章封面 | 5D封面图系统——类型×配色×渲染×文字×情绪 |

| [baoyu-infographic](baoyu-infographic/SKILL.md) | 信息图/可视化 | 信息图——21布局×21风格 |

| [baoyu-translate](baoyu-translate/SKILL.md) | 翻译/精翻/快翻 | 三模式翻译——快翻/标准/精翻 + 受众×风格参数化 |

| [image-analysis](image-analysis/SKILL.md) 🆕 | 分析图片/图片内容识别 | MiniMax VLM 图片分析——JPEG/PNG/WebP，URL或本地文件 |

| [apple-design](apple-design/SKILL.md) | Apple风格/流体交互/spring动画 | Apple设计原则与流体交互（17条原则） |

| [emil-design-eng](emil-design-eng/SKILL.md) | 设计工程/动画决策/UI打磨 | Emil Kowalski的设计工程哲学 |

| [find-animation-opportunities](find-animation-opportunities/SKILL.md) | 动画机会/哪里加动画 | 动画机会发现与过滤 |



---



## 📖 技能详解



### 🧠 方法论



#### 🆕 方法论引擎（吸收 ljg-skills）



吸收 [lijigang/ljg-skills](https://github.com/lijigang/ljg-skills) 认知哲学和方法论框架，本地化适配 Hermes + 飞书生态。



**核心引擎（5个）**：

```

domain-decompose (P0) ← ljg-rank    降秩引擎

book-deconstruct (P1) ← ljg-book    拆书

deep-think (P1)        ← ljg-think  追本之箭

qa-extract (P2)        ← ljg-qa     Q-A链提取

relationship-analysis (P3) ← ljg-relationship  关系诊断

```



**系统增强层（3个companion技能）**：

```

ljg-writing-voice      ← ljg-writes  humanizer增强：最高法则+语言铁律

ljg-elicitation-modes  ← ljg-learn+roundtable+rank  advanced-elicitation增强：+3种模式

ljg-infographic-design ← ljg-card    baoyu-infographic增强：密度×结构×情绪

```



**跨技能调用网络**：

```

domain-decompose → deep-think, qa-extract

book-deconstruct → deep-think, domain-decompose, qa-extract

deep-think       → domain-decompose

qa-extract       → deep-think

relationship-analysis → deep-think

```



**吸收的核心认知哲学**：差量即贡献(book) · 好解释一动就塌(rank/Deutsch) · 你会这样跟聪明的朋友说话吗(writes) · 不给建议只提问(relationship) · 样式为思想服务(card)。



#### advanced-elicitation — 结构化深度追问



> **触发**：深度审视 / 换个角度 / Push deeper / Red team



69种追问方法 × 9大类 × 智能选择5种最匹配方法 × 迭代审视。产出后自动触发多维审视。



**联动**：可被 `answer` / `travel-intel` / `feishu-html` 调用



---



#### blue-team — 业务蓝军内容审核



> **触发**：帮我看看这个方案 / challenge一下 / 压力测试



模拟最挑剔的挑战者，通过6阶段审查逼迫方案暴露逻辑断层：本质还原 → 死亡假设 → 苏格拉底追问 → 逻辑遍历 → 竞争替代。



---



#### darwin-skill — Agent 技能质量评估



> **触发**：优化技能 / 评估技能质量 / 技能进化



评估 SKILL.md 质量（触发条件/执行步骤/产出标准/方法论完整性），输出诊断+优化方案。支持方法论吸收冲突矩阵分析。



---



#### editorial-review-prose — 临床级文本编辑



> **触发**：审一下文案 / review the prose / 文本审查



审查文案的沟通问题，输出三列表格修订建议。基于微软写作风格指南。



**与 zhike-content-output 搭档**：铁律（写什么）+ ER-P审查（写得怎样）



---



#### editorial-review-structure — 文档结构编辑



> **触发**：结构审查 / 逻辑重排 / 信息架构优化**



审查文档结构并提出实质性重组建议。**在文案编辑前运行。** 5种结构模型 × 6类建议（CUT/MERGE/MOVE/CONDENSE/QUESTION/PRESERVE）。



---



#### edge-case-hunter — 边界条件穷举审查



> **触发**：边界检查 / edge case / 穷举测试



纯路径追踪器——机械式走查每条分支路径，报告未处理的。7维穷举 × 纯JSON输出。与对抗性审查正交。



---



### 🏗️ 构建与设计



#### repo-source-deepread — 大型远程源码仓库深读法 🆕



> **触发**：精读源码 / 深入分析这个仓库的实现 / 看看XX怎么做的 / 竞品源码分析 / 这个项目的XX机制怎么实现的 / 从源码里学设计



介于"读 README 评估"（github-absorb）与"克隆后全量静态分析"（codebase-inspection）之间的**源码设计模式精读**。用 git trees API 递归定位子系统，raw 拉取 + AST 骨架提取（docstring/签名/常量），单文件压到 30~70 行，20 文件一轮精读控制在 ~15KB 输出。



**四阶段工作流**：

1. **子系统定位** — `GET /repos/{owner}/{repo}/git/trees/main?recursive=1` 一次拿全仓文件路径，正则筛子系统

2. **批量骨架提取** — `scripts/gh_ast_skeleton.py`，每文件只取：模块 docstring（截 350 字符）+ 类/方法签名 + 顶层函数签名 + 顶层常量（≥3 个时）

3. **选择性整读** — 只对 <8KB 的关键小文件（适配器入口、会话管理器、契约定义）整读全文；>50KB 的永不整读

4. **吸收笔记落盘** — 产出"源码精读笔记"文档：精读范围 → 按子系统提炼设计模式 → 对本项目的吸收清单（立即/中期/深水区/明确不抄四档）→ 遗留待读清单



**核心纪律**：

- 一次 `execute_code` 拉 4~6 个文件，不要一个文件一次调用（每轮重发整个会话）

- 50KB+ 单文件不整读——骨架先行 + 按需深钻

- 测试文件名即设计规格（`test_proactive_unanswered_repeat.py` → 有未应答重复策略），先读测试名再读源码

- 配置文件的常量是黄金：半衰期/冷却秒数/触发概率/阈值（产品打磨过的数值全在这里）

- 429 限流 fallback：`git clone --depth 1` + 本地跑同一 AST 脚本



**联动**：上游 `github-absorb`（先做文档层评估）→ 本技能（机制深读）→ 互补 `codebase-inspection`（结构盘点）/ `external-skill-evaluation`（评估决策）



**工具集**：`scripts/gh_ast_skeleton.py`（AST 骨架 CLI，支持指定文件/`--prefix`+`--regex` 子树选文件/`--full` 整读）+ `references/skeleton-signals.md`（架构模式信号速查）



> 沉淀自 2026-07-31 N.E.K.O（Project-N-E-K-O/N.E.K-O，5014 文件）精读：20 文件 4 批次，产出竞品机制笔记 9.5KB，零上下文溢出。



---



#### answer — AI Native's Workflow(er)



> **触发**：answer / 从零开始 / 帮我规划 / 设计方案



7阶段结构化工作流编排器，将模糊想法转化为可执行的完整方案。



**7阶段管线**：Clarify → Brief → Architect → Standards → Decompose → Build → Review



**能力**：6大领域适配 | 100+ 触发词 | 飞书 Wiki 全链路产出 | 活文档纪律 | AE/ER/blue-team 增强审查



---



#### huashu-design — 花叔Design



> **触发**：做原型 / 设计Demo / 交互原型 / HTML演示 / UI mockup



用HTML做高保真原型、交互Demo、幻灯片、动画、设计变体探索+设计方向顾问的一体化设计能力。



**能力**：iOS/Android原型 | 20种设计哲学 | 品牌资产协议 | B2B海报 | 动画导出 | 专家评审



---



#### hallmark — Anti-AI-Slop 质量门禁



> **触发**：审查AI味 / audit设计 / 提取设计DNA / 发射前检查



58道反AI-slop关卡 + 六轴预发射自评（P/H/E/S/R/V）。从 Nutlope/hallmark (MIT) 适配。在 huashu-design 和 feishu-html 之间作为质量门禁层运行。



**能力**：视觉反模式 | 排版纪律 | 交互动效 | 内容诚信 | 移动端硬地板



---



#### design-md — 品牌设计Token参考库



71个品牌的 DESIGN.md token 规范文件（色板/字体/间距/阴影/组件规范）。作为 `claude-design` 和 `huashu-design` 的品牌Token补充参考层。



---



#### feishu-html — WEB SPA 制作与部署



> **触发**：做个网页 / 发布到线上 / 部署 / 做个展示页



将飞书文档或用户内容制作为功能完整的 WEB SPA 应用，部署至阿里云 OSS。



**能力**：7阶段全链路 | Playwright CDP 验证 | 多TAB SPA + 响应式 | 双轨交付 | Hallmark 质量门禁



---



#### humanizer — 文案反AI味



29种文本模式去除AI写作痕迹。与 `hallmark`（UI反AI味）形成文案+视觉双重防线。



---



### 🔬 研究（ARA三件套）



#### ara-compiler — 文献结构化编译器



> **触发**：编译论文 / 结构化这篇论文 / 把论文转成ARA



将PDF论文/代码仓库转化为四层 ARA 可导航格式，消除叙事税和工程税。适应自 Orchestra-Research/Agent-Native-Research-Artifact (MIT)。



---



#### ara-research-manager — 研究过程捕获



> **触发**：记录研究进展 / ara capture / 研究session结束



三阶段流水线（Harvester→Router→Maturity Tracker）自动扫描研究session，将决策/实验/死胡同/声明写入 ARA 四层结构。



**能力**：渐进结晶 | 来源标记 | 死胡同追踪 | 五类DAG节点



---



#### ara-rigor-reviewer — 论文质量审查



> **触发**：审查论文 / 审稿 / 提交前检查



六维认识论审查（证据相关性/可证伪性/范围校准/论证连贯性/探索完整性/方法论严谨性），产出评分报告。



---



### 🤖 AI 工程 🆕



> **来源**：吸收 [openEuler/agent-insight](https://atomgit.com/openeuler/witty-skill-insight) (MIT) — Agent 技能全生命周期工程化方法论，本地化适配 Hermes 生态。



**吸收核心思想**：数据驱动的闭环飞轮——「生成→执行→评测→归因→优化」共享同一套执行数据；过程追溯而非只问结果；靶向归因区分「Skill错了」还是「模型歪了」。



#### skill-evaluator — Agent 技能三维评测引擎



> **触发**：评测skill / 技能质量 / 这个skill怎么样



执行精准度 × 端到端时效 × 计算成本 三维量化评测 + LLM-as-Judge 自动打分 + Mermaid 过程追溯图 + 靶向归因(技能/模型/环境) + **自动触发**(每次Skill使用后自动评分)。



**能力**：三维评测 | LLM法官 | 过程追溯 | 靶向归因 | 自动触发 | 历史趋势 | CPSR成本量化



**调用链**：skill-evaluator → benchmark-generator（无benchmark时先生成测试集）



---



#### skill-ab-test — Skill A/B 对比测试



> **触发**：AB测试 / 对比skill / 这个改动有没有提升



同一套用例下对照组(A) vs 实验组(B)自动对比——能力(精准度) × 成本(Token) × 稳定性(标准差) 三维评估 + 统计显著性检验 + 通过/打回决策。



**调用链**：skill-ab-test → benchmark-generator（生成测试数据） → skill-evaluator（逐run打分）



---



#### benchmark-generator — 测试集自动生成



> **触发**：生成测试集 / 造benchmark / 这个skill的测试数据



从 Skill 定义自动生成 routing 测试集(该不该命中) + outcome 测试集(命中后应产出什么)，语义去重后入库。支撑 skill-evaluator 和 skill-ab-test 的测试数据需求。



---



#### agent-tool-system — Agent 工具系统设计方法论 🆕



> **触发**：Agent 工具 / 工具系统 / defineTool / toolsToAI / MCP tools 设计

> **来源**：吸收 [open-pencil/open-pencil](https://github.com/open-pencil/open-pencil) (MIT) — AI-Native 设计编辑器的 100+ 工具三层架构。



defineTool → registry → toolsToAI 三层架构 + ToolLog 调试基建（before/after 快照、重复检测、noop 检测）+ StepBudget 步数预算。一份工具定义同时驱动 AI Chat（Vercel AI SDK）、CLI（citty）、MCP Server（JSON Schema），零重复定义。



**能力**：Schema层(defineTool泛型工厂) | Registry层(CORE/EXTENDED分级) | Adapter层(toolsToAI/MCP/CLI) | ToolLog调试 | StepBudget | 参数类型系统



**调用链**：github-absorb → agent-tool-system（从源码仓库提取工具系统架构） → cross-project-adaptation（迁移到不同业务域）



---



### 🏔️ 贵州之客系列



#### zhike-content-output — 内容产出准则



> **触发**：产出文档 / 对客文案 / 写公众号 / 脚本创作



贵州之客品牌的内容产出第一核心原则。**能力**：对客写作铁律 | 叙事声音6大特征 | 评论回复7条铁律 | 视频脚本框架



---



#### wechat-article-archive — 公众号文章采集归档器 🆕



> **触发**：采集公众号 / 公众号归档 / 微信文章转Markdown / 竞品公众号监控



从公开公众号文章链接出发，识别博主、采集最近N篇文章（默认50）、保存为Markdown归档（含图片本地化）、生成文章清单CSV、按需调用 author-methodology-analysis 做方法论分析、HTML看板+飞书同步、ZIP打包。适应自 freestylefly/wechat-article-archive-skill by 苍何 (MIT)。



**能力**：扫码登录微信公众平台 | 5源候选列表 | 串行采集+图片本地化 | 校验+打包 | 飞书同步



---



#### author-methodology-analysis — 作者内容方法论深度分析器 🆕



> **触发**：分析博主方法论 / 拆解公众号套路 / 提炼写作框架 / 内容方法论分析



21维度全面数据分析（样本质量/发布节奏/篇幅密度/主题分类/关键词体系/标题策略/开头模式/篇章结构/论证方式/证据体系/实体网络/判断立场/语言风格/读者收益/CTA/图片使用/时间演化/交叉关联/异常检测），提炼作者定位、选题系统、表达模板、金句风格、写作SOP。适应自 freestylefly/author-methodology-analysis-skill by 苍何 (MIT)。



**能力**：21维数据分析 | 13模块方法论报告 | 独立文案框架（选题脚手架+标题公式+开头模板） | HTML看板（十章节学习者视角） | 飞书同步



**联动**：可被 `wechat-article-archive` 调用 | 与 `zhike-content-output` 形成规范↔分析闭环 | `advanced-elicitation` 审视 | `humanizer` 后处理



---



#### travel-intel — 旅游情报系统



> **触发**：搜一下知识库 / 查XX景点信息 / 行业动态



4通道采集 → 入库 → 过期校验 → 分级报告。5个 cron job 自动化运行。



---



#### travel-itinerary — 智能行程规划



> **触发**：规划行程 / 做个行程 / 去XX玩几天



7步工作流：解析需求 → 天气 → 搜索 → POI → LLM规划 → 费用 → 双版文档。



---



#### trip-landing — 行程落地页



> **触发**：生成落地页 / 生成行程页 / 做成网页版



一键生成5 TAB SPA（概览/行程/地图/须知/安全）→ PWA离线 → OSS部署 → 10天自动清理。



---



---



## 🎨 设计管线（五环联动）



```

brandkit 🔮              → taste-skill 🔮          → redesign-skill 🔧

（品牌策略+Logo方法论）      （方向指引+预检）           （页面升级审计）



        ↓                        ↓                        ↓

        ↓               huashu-design 🎨           hallmark 🛡️

        ↓               （创意执行）                （质量门禁）

        ↓                        ↓                        ↓

  委派jimeng/ComfyUI        20种设计哲学              58道关卡

  生成品牌视觉              品牌资产协议              六轴自评

```



| 技能 | 环节 | 回答的问题 |

|------|:--:|------|

| [brandkit](brandkit/SKILL.md) | 品牌策略 | "品牌为什么存在？Logo如何表达？" |

| [taste-skill](taste-skill/SKILL.md) | 方向指引 | "往哪个方向做？" |

| [redesign-skill](redesign-skill/SKILL.md) | 升级审计 | "现有页面怎么系统性升级？" |

| [huashu-design](huashu-design/SKILL.md) | 创意执行 | "怎么做好？" |

| [hallmark](hallmark/SKILL.md) | 质量门禁 | "做得对不对？" |



**边界协议**：taste 的 V/M/D 旋钮是 huashu 的硬约束，brandkit 的策略决定 taste 的方向参数（如文旅品牌→Dark Nature模式→V6/M4/D3），redesign-skill 的审计报告可被 taste 读取来决定升级方向。



---



## 🔗 使用场景



### 场景1：从零构建新业务方案



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

→ editorial-review-prose（三列表格审查）

→ feishu-html（部署上线）

```



### 场景3：学术论文研究



```

ara-compiler（结构化相关文献）

→ 进行研究工作（实验/分析/写作）

→ ara-research-manager（每session存档）

→ ara-rigor-reviewer（提交前六维审查）

```



### 场景4：代码 PR 审查



```

requesting-code-review

├── 清单式审查（安全/质量/性能/测试）

└── edge-case-hunter（穷举边界条件 JSON）

→ 合并报告 → 提交 Review

```



### 场景5：旅游情报监控



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



for dir in */; do

  name=$(basename "$dir")

  case "$name" in

    # 🧠 方法论 (26)

    advanced-elicitation|author-methodology-analysis|batch-course-delivery|blue-team|book-deconstruct|darwin-skill|darwin-skill-cron|deep-think|domain-decompose|double-evolution|edge-case-hunter|editorial-review-prose|editorial-review-structure|external-skill-evaluation|github-absorb|ljg-elicitation-modes|ljg-infographic-design|ljg-writing-voice|opportunity-solution-tree|pm-prioritization-frameworks|qa-extract|relationship-analysis|stakeholder-mapping|repo-source-deepread|verification-before-completion|writing-skills) category="methodology" ;;

    # 🏗️ 构建与设计 (26)

    answer|answer-standalone|architecture-diagram|brandkit|claude-design|dashiai-ppt-hermes|design-md|diagram-cjk-rendering|drawio-generation|dynamic-workflow|feishu-html|fireworks-tech-graph|hallmark|html-ppt|huashu-design|humanizer|pretext|redesign-skill|requesting-code-review|requirement-alignment-analysis|sketch|strategy-plan-writing|taste-skill|training-content-restructure|web-spa|writing-plans) category="build-design" ;;

    # 🔧 开发工程 (25)

    agent-native-cli-design|alicloud-fc-deploy|coding-agents|cross-project-adaptation|dingtalk-cli|dingtalk-minutes-extraction|executing-plans|finishing-a-development-branch|firecrawl-web|github-release-readme|github-skill-repo-cron|github-sync-cron-pitfalls|hermes-instance-sync|hermes-performance-diagnosis|hermes-windows-native|question-bank-pipeline|receiving-code-review|subagent-driven-development|supabase-backend|technical-documentation-production|test-driven-development|windows-troubleshooting-from-wsl|wsl-browser-cdp|wsl-docker-deploy|wukong-skill-center) category="dev-engineering" ;;

    # 🤖 AI 工程 (4)

    agent-tool-system|benchmark-generator|skill-ab-test|skill-evaluator) category="ai-engineering" ;;

    # 📋 飞书系列 (7)

    feishu-doc|feishu-table|feishu-voice|feishu-wiki|feishu-wiki-file-routing|project-kanban|zhike-task-hub) category="feishu" ;;

    # 🏔️ 贵州之客 · 旅行社全链路 (16)

    amap-lbs|cost-engine|customer-view|guide-exec|jimeng-video|supply-check|travel-intel|travel-itinerary|travel-workflow|trip-archive|trip-briefing|trip-landing|trip-quote|vendor-brief|wechat-article-archive|zhike-content-output) category="travel" ;;

    # 🔬 研究 (4)

    ara-compiler|ara-research-manager|ara-rigor-reviewer|systematic-debugging) category="research" ;;

    # 🎨 创意内容 (9)

    apple-design|baoyu-article-illustrator|baoyu-comic|baoyu-cover-image|baoyu-infographic|baoyu-translate|emil-design-eng|find-animation-opportunities|image-analysis) category="creative" ;;

    *) category="misc" ;;

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



---



## 🤝 贡献指南



1. 每个技能一个文件夹，包含 `SKILL.md`

2. 必须包含 frontmatter（name / description / version / author / license）

3. 触发条件明确——新手 Agent 仅凭此文档即可独立完成任务

4. 提交 PR 前验证：`python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"`



---



---



## 📝 版本历史



| 版本 | 日期 | 变更 |
|------|------|
| v5.4.45 | 2026-08-23 | 117技能 — 0 新增 + 1 内容同步（batch-course-delivery v0.2.0→v0.3.0：生产阶段改两棒制——课程大纲为第一棒生产门禁、确认后派生四件套；PPT 生成通道定为 qwen-image-ppt 技能；related_skills 加 qwen-image-ppt；references/rulebook-example.md §7 同步）；badge 保持 117。 |
| v5.4.44 | 2026-08-23 | 117技能（+1 新增 batch-course-delivery v0.2.0：一门课对多客户批量交付——冻结框架+适配规则书+场次配置单+AI工作流派生四件套（PPT/手册/题库/工具包），含 references/rulebook-example.md 与 templates/client-intake-and-session-config.md；🧠 方法论 25→26）；badge 116→117。 |
| v5.4.43 | 2026-08-19 | 0 新增 + 1 内容同步（wechat-article-archive）；18 SKIP（含 14 永久排除/官方 + 4 GH 版本更新 + 1 cron-slim ratio<0.7）；1 unclassified REPORT（claude-design 本地 v1.1.0 > GH v1.0.0 但 author: BadTechBandit 非自建/非三方标记 → 等用户补 author）；badge 计数保持 116（无新增技能）；skill-evaluator GH 比本地多 35 行验证（GH 含 5 references + 36 行 A/B 双部署 + no_agent 静默原则 + provider timeout 红鲱鱼诊断是完整版，本地 17842b 是 cron 精简分叉）→ SKIP 避免倒退。 |

| v5.4.42 | 2026-08-18 | 0 新增 + 6 内容扩展（apple-design / baoyu-infographic / firecrawl-web / huashu-design / web-spa / wsl-docker-deploy）：补充本地新增 references、scripts 与 Windows/WSL 部署恢复实践；3 个 unclassified 差异继续 REPORT，不自动覆盖。 |

| v5.4.41 | 2026-08-16 | 0 新增 + 3 内容同步（skill-evaluator/wechat-article-archive/wsl-docker-deploy）；2 unclassified REPORT；skill-evaluator 同版本 + ratio 0.92 经方向验证真实新增（cron A/B 部署方式更新 + 36 行）；wechat-article-archive 5 行 CHECKPOINT 改写；wsl-docker-deploy 1 行 EOF 修复表格 |

| v5.4.41 | 2026-08-13 | 116技能 — 0 新增 + 0 内容同步 → 静默同步周期；badge 计数修正 117→116（v5.4.39 提交遗留的 off-by-one：磁盘目录 116 / 索引唯一引用 116 / 分类表求和 116 三方一致，仅 badge 多计 1）；scanner Phase 1B 改为通用 1 级子目录枚举（此前硬编码子目录列表漏扫 creative/ppt/education，导致 apple-design/dashiai-ppt-hermes/emil-design-eng/find-animation-opportunities/training-content-restructure 5 个技能被误报为 GH-only，修复后 GH-only 归零）；17 content_diff → 0 SYNC + 16 SKIP + 1 REPORT；darwin-skill 本地 v2.1.2 (2271b) vs GH v2.1.1 (19626b) ratio=0.116 被 bytes ratio < 0.7 规则第五次截获（cron 精简版分叉，勿覆盖）；external-skill-evaluation 本地 v1.3.0 < GH v1.4.0 → SKIP；claude-design 本地 v1.1.0 > GH v1.0.0 但 author: BadTechBandit 非自建/非三方标记 → unclassified REPORT，按 cron policy 仅报告不推送。 |

| v5.4.39 | 2026-08-12 | 115→117技能 — 新增 2 自建技能：dingtalk-minutes-extraction v1.0.0（钉钉AI听记提取：会议转写+AI摘要+待办，🔧 开发工程 24→25）、training-content-restructure v1.0.0（培训资料全链路重构+一致性治理，含 references/html-artifact-verification.md，🏗️ 构建与设计 25→26）；更新 github-sync-cron-pitfalls v1.2.0→v1.4.0（+8 行 v-number 派生自远端 tag / codeload worktree 验证序列 / gh 账号有效性辨析，新增 references/execution-log-2026-08-08.md）；23 content_diff → 2 SYNC + 19 SKIP + 2 REPORT；skill-evaluator 经行级 diff 判定为 scanner symlink 歧义假阳性（.hermes-feishu/ai-engineering/ 19455b 与 .hermes/ 17842b 为两个真实分叉，GH 已是 mtime 最新版）→ 不同步。 |

| v5.4.38 | 2026-08-08 | 114→115技能 — github-sync-cron-pitfalls v1.2.0 内容同步（local v1.2.0 > gh v1.1.0，bytes ratio 0.71，+110 行实战：v5.4.36 tag collision + gh L1 TTL 缓存 + v-number 派生；新增 references/v5.4.36-tag-collision-and-gh-l1.md）；github-skill-repo-cron 顺手补录（orphan cleanup，🔧 开发工程 23→24）；badge 113→115。 |
| v5.4.37 | 2026-08-05 | 113技能 — question-bank-pipeline v1.2.0 内容同步（本地 17972b/335行 vs GH 17419b/331行，本地新增 4 行 md-json-bank-maintenance 表行+对应 references/md-json-bank-maintenance.md 文件，按 v5.4.23 行级 diff 方向验证判定为本地新版本）；其余 18 content_diff 全部归类：14 OFFICIAL 跳过（feishu-doc/feishu-html/feishu-wiki/hermes-instance-sync/project-kanban/travel-intel/travel-itinerary/travel-workflow/zhike-task-hub/trip-archive/supply-check/vendor-brief/design-md）+ 1 CRON-SLIM ratio=0.116 跳过（darwin-skill 本地 v2.1.2 2271b < GH v2.1.1 19626b） + 3 unclassified REPORT（external-skill-evaluation 本地 v1.3.0 < GH v1.4.0 + claude-design 本地 v1.1.0 > GH v1.0.0 + dashiai-ppt-hermes 本地 0b vs GH v1.0.0 10645b）按 cron policy 仅报告不推送，等待用户补 author; local_only 250 个全部归类为 official 或 unclassified/bak/cycle-addendum，无 self-built/third-party 待同步。 |
| v5.4.36 | 2026-08-04 | web-spa v1.2.0 内容更新（HEAD = v5.4.36 提交于 2026-08-04）。 |
| v5.4.35 | 2026-08-02 | 113技能（+1 新增 repo-source-deepread：大型远程源码仓库深读法——git trees API 递归定位 + AST 骨架提取 + 批量 execute_code 防上下文爆炸，方法论 24→25；+7 内容更新 html-ppt 加 references 目录 + humanizer v2.5.1 真实新增 + pretext v1.0.0 references + requirement-alignment-analysis v1 + ref file + sketch v1.0.0→v1.0.1 移除永久排除 spike 引用 + skill-evaluator v1.2.0 真实新增 + strategy-plan-writing v + references + supabase-backend v1.3.0→v1.4.1 + 7 references）；16 SKIP（24 content_diff - 8 SYNC = 16 SKIP：6 PERMANENTLY_EXCLUDED feishu-doc/feishu-html/feishu-wiki/hermes-instance-sync/project-kanban/zhike-task-hub + 5 cron 精简版 darwin-skill 0.116/design-md 0.615/external-skill-evaluation 本地 v1.3.0 < GH v1.4.0 + travel-intel/travel-itinerary/travel-workflow 永久排除 + supply-check/vendor-brief/trip-archive 永久排除 + github-release-readme 自身排除）；HEAD = v5.4.34 = origin/main 无 race condition。|

| v5.4.34 | 2026-07-31 | 112技能 — web-spa v1.2.0 内容更新 (3 行新增：演讲者备注 div.notes + F 键全屏 + 对客红线扫描 multi-doc-consistency Workflow C)；skill-evaluator v1.2.0 跳过（GH 含方式A/B双部署 36行更完整，本地是方式B only 简化版，按 v5.4.21 方向验证规则 SKIP 勿降级）；4 unclassified REPORT (claude-design/external-skill-evaluation/html-ppt/requirement-alignment-analysis/strategy-plan-writing) 按 cron policy 跳过，等待补 author 触发自动归类。 |

| v5.4.33 | 2026-07-30 | 112技能 — web-spa v1.2.0 内容更新：新增 PPT 式横向翻页 Pager 配方与无头验收脚本（弹簧物理/手势状态机/橡皮筋/reduced-motion/错峰入场）；4 个 unclassified REPORT（external-skill-evaluation/html-ppt/strategy-plan-writing/supabase-backend）按 cron policy 跳过，等待补 author 或人工决策。|

| v5.4.31 | 2026-07-24 | 2技能内容更新：web-spa v1.2.0 完整版；sketch 清理永久排除 spike 引用。5个共享技能保持 unclassified，仅报告不推送。 |

| v5.4.32 | 2026-07-27 | 112技能 — skill-evaluator v1.2.0 references 目录新增2文件(hermes-hook-setup.md + hermes-session-format.md 部署双方式 A/B)，SKILL.md 字节级一致；其余21个 content_diff 经方向验证全部归类为：6个 PERMANENTLY_EXCLUDED 已跳过(feishu-doc/feishu-html/feishu-wiki/hermes-instance-sync/project-kanban/trip-archive/github-release-readme)、6个官方类已跳过(travel-intel/travel-itinerary/travel-workflow/supply-check/vendor-brief/zhike-task-hub)、5个真正 IDENTICAL 无需同步(humanizer/requirement-alignment-analysis/supply-check/vendor-brief/skill-evaluator)、3个 bytes ratio<0.5 疑似 cron 精简版已SKIP(darwin-skill 0.116/html-ppt 0.464)；unclassified REPORT 1项(supabase-backend v1.3.0→v1.4.1 大版本更新+7 references 待用户加 author 后下次 cron 自动归 self-built 推送) |

| v5.4.30 | 2026-07-23 | 112技能（+1 新增 github-sync-cron-pitfalls: GitHub skill-repo sync cron troubleshooting 实战踩坑分类与防御；开发工程 22→23）+5 内容更新(apple-design v1.0.0 新增::before 多层级伪元素继承坑、huashu-design v0.0.0 新增 HTML Slide 维护+主题迁移 references、question-bank-pipeline v1.2.0 新增考试系统/评分系统触发词、sketch v1.0.0 移除永久排除 spike 引用、skill-evaluator v1.2.0 新增 cron script 部署双方式 A/B）；5 SKIP(DO NOT OVERWRITE: firecrawl-web本地精简版 vs GH完整版、test-driven-development/wechat-article-archive/wsl-docker-deploy/systematic-debugging本地内容少于GH保留GH完整度)；76 unclassified REPORT 待用户决策分类 |

| v5.4.26 | 2026-07-17 | 111技能 — 9技能内容同步(answer v1.6.0+docx-quiz-extraction reference升级、apple-design v1.0.0细化原则、hallmark v1.0.0扩充58关卡+review-animations专项、huashu-design v0.0.0路由表+related_skills、question-bank-pipeline v1.2.0管线优化、redesign-skill v1.0.0升级7维审计、sketch v1.0.0+disposable mode、wechat-article-archive v1.0.0+🛑 STOP验证项、writing-skills v1.0.1)；2跳过(darwin-skill本地v2.1.2 Cron精简版2271b < GH v2.1.1完整版20072b、web-spa本地v1.2.0精简版10009b < GH v1.0.0基础版4673b，按v5.4.22 bytes ratio < 0.7 疑似精简版规则跳过)；4 unclassified REPORT(external-skill-evaluation/requirement-alignment-analysis/strategy-plan-writing/supabase-backend)；版本号继续PATCH(111技能数未变) |

| v5.4.25 | 2026-07-16 | 111技能 — +3 新增(apple-design/emil-design-eng/find-animation-opportunities: 吸收自 emilkowalski/skills 的Apple设计原则/动画决策框架/动画机会发现，创意分类 6→9)；hallmark 融入 review-animations 动画专项审查能力；redesign-skill 融入 improve-animations 动画审计优化能力；huashu-design 更新路由表和 related_skills；完整技能引用网络已建立 |

| v5.4.22 | 2026-07-14 | 102技能 — 5技能内容同步(executing-plans/finishing-a-development-branch/receiving-code-review/verification-before-completion/writing-skills v1.0.0→v1.0.1)；3技能unclassified REPORT待用户决策(external-skill-evaluation/strategy-plan-writing/supabase-backend)；darwin-skill本地v2.1.2为Cron精简版(2271字节)，GH HEAD v2.1.1为完整版(20072字节)，按v5.4.21方向验证规则跳过避免倒退 |

| v5.4.11 | 2026-07-04 | 96技能 — 11技能内容更新(drawio-generation/external-skill-evaluation/feishu-wiki/github-absorb/github-release-readme/hermes-instance-sync/ppt-structure-parser/ppt-template-filler/skill-evaluator/travel-intel/trip-archive) |

| v5.4.10 | 2026-07-04 | 96技能（+2 新增 ppt-structure-parser + ppt-template-filler：PPT模板拆解→页面库 + 跨模板拼装生成，回归 v5.4.9 误删的两技能；构建与设计 22→24）+ 20技能内容更新(answer/ara-compiler/darwin-skill/dingtalk-cli/external-skill-evaluation/feishu-doc/feishu-table/feishu-wiki/firecrawl-web/github-absorb/github-release-readme/hermes-instance-sync/jimeng-video/sketch/strategy-plan-writing/supabase-backend/test-driven-development/travel-intel/trip-archive/windows-troubleshooting-from-wsl) |

| v5.4.9 | 2026-07-03 | 94技能（-2 移除：ppt-structure-parser + ppt-template-filler 迁移至独立仓库 jorinyang/ppt-engine-ref refactor；构建与设计 24→22；修复 badge 计数 96→94 + 移除遗留引用 + 安装脚本清理） |

| v5.4.8 | 2026-07-02 | 96技能 — 11技能内容更新：external-skill-evaluation v1.3.0→v1.4.0(新增借鉴思想吸收轻量模式)；github-release-readme classify_skill顺序修正(author优先)；hermes-instance-sync 新增Phase -1 broken symlink清理；trip-archive 格式规范化+内容扩展；travel-intel 采集层标记修正；wsl-browser-cdp/wsl-docker-deploy 移除WSL-only警告标记；github-absorb/firecrawl-web/image-analysis/ppt-structure-parser 微调 |

| v5.4.6 | 2026-07-01 | 96技能 — WSL适配：3个WSL技能标记为仅WSL环境适用 + 10个技能移除WSL特定引用(travel-intel/github-release-readme/github-absorb/jimeng-video/feishu-doc/image-analysis/firecrawl-web/dingtalk-cli/strategy-plan-writing/double-evolution) |

| v5.4.5 | 2026-07-01 | 96技能 — +1 新增(feishu-wiki-file-routing: 飞书知识库 /wiki/ URL 路由降级——当 lark-doc 无法处理 file 类型节点时的发现→下载→提取流程；与 lark-doc/lark-wiki/lark-drive 协同)；飞书系列 6→7 |

| v5.4.4 | 2026-07-01 | 95技能 — +2 新增(ppt-structure-parser + ppt-template-filler: PPT模板拆解→三级标签入库 + 页面库→跨模板拼装生成，四阶段流水线)；构建与设计 22→24 |

| v5.4.1 | 2026-06-28 | 91技能 — 移除4个非核心技能(plan/spike/dingtalk-channel/ocr-and-documents v5.1.0已清但v5.4.0误加回)，永久排除；构建与设计24→22、开发工程13→12、创意内容7→6；清理4处交叉引用 |

| v5.2.1 | 2026-06-25 | 89技能 — 解决功能重复(answer/answer-standalone区分飞书集成版vs独立版、fireworks/drawio/architecture-diagram触发词去冲突) + 建立11对互补技能双向引用网络(brandkit↔taste-skill↔huashu-design↔hallmark设计管线等) + taste-skill metadata去重 |

| v5.1.0 | 2026-06-25 | 89技能 — 清理12个非核心技能(creative-ideation/kanban/plan/spike/dogfood/youtube-content/yuanbao/dingtalk-channel/shipinhao-cold-start/pdf-content-generation/codebase-inspection/ocr-and-documents)；工具与集成4→1、开发工程17→11、方法论21→20、贵州之客9→8、创意内容7→6 |

| v5.0.0 | 2026-06-24 | 102技能 — README重构：去重7跨类技能(brandkit/huashu-design等)→每技能唯一分类；+12缺失条目补全(codebase-inspection/dingtalk-channel/dogfood/hermes-instance-sync/technical-documentation-production/windows-troubleshooting-from-wsl/github-release-readme/yuanbao/ocr-and-documents/pdf-content-generation/image-analysis/travel-workflow)；新增📋工具与集成分类；贵州之客12→9、创意内容6→7、开发工程12→17、构建与设计23→22；github-release-readme v2.0.1 symlink穿透规则 |

| v4.8.1 | 2026-06-23 | agent-tool-system v1.0→v1.1.0：升级为规范+工具——新增3个脚本(scaffold/validate/mcp-schema导出)+CI管线+GitHub Actions模板；18个触发词全生命周期覆盖 |

| v4.8.0 | 2026-06-23 | 89技能（+1 agent-tool-system：defineTool→registry→toolsToAI三层架构+ToolLog+StepBudget，吸收自 open-pencil/open-pencil；AI工程3→4；+1更新 github-absorb v1.3.0 新增📦独立安装分类+Phase 5C安装验证） |

| v4.7.0 | 2026-06-22 | 88技能（+8 旅行社工作流系统：trip-quote/trip-briefing/guide-exec/supply-check/vendor-brief/cost-engine/trip-archive/customer-view；报价单4风格+出团通知书+导游执行单12章+物资核对+供应商对接×3+成本比价+客户打包+归档；新增 travel 分类） |

| v4.6.0 | 2026-06-22 | 80技能（+4 新增：external-skill-evaluation/shipinhao-cold-start/wsl-browser-cdp/requirement-alignment-analysis；方法论19→20；贵州之客11→12；飞书系列5→6；开发工程10→11；+6 更新：skill-evaluator v1.2 B-2 Hook架构/wechat-article-archive QR登录工作流/travel-intel v1.5.6 迈点降级监控/feishu-wiki 精简定制化/blue-team/author-methodology-analysis） |

| v4.5.0 | 2026-06-21 | 76技能（+3 吸收 openEuler/agent-insight AI工程方法论：skill-evaluator/skill-ab-test/benchmark-generator；Skill三维评测+A/B对比+测试集自动生成；新增 ai-engineering 分类；skill-evaluator 支持 cron 自动触发评测） |

| v4.4.0 | 2026-06-18 | 73技能（+3 吸收 pm-skills PM方法论：pm-prioritization-frameworks/stakeholder-mapping/opportunity-solution-tree；9种优先级框架速查+干系人矩阵+四层发现树；answer v1.5.0→v1.6.0 注入红队攻击+JTBD价值主张+产品战略画布+死亡假设Tiger分级；方法论 16→19） |

| v4.3.0 | 2026-06-18 | 70技能（+2 吸收 canghe-skills：wechat-article-archive/author-methodology-analysis；公众号采集归档 + 21维作者方法论分析；方法论 16→16，贵州之客 11→11） |

| v4.2.0 | 2026-06-17 | 68技能（+4 新增：dynamic-workflow/cross-project-adaptation/plan/strategy-plan-writing；15技能触发场景全面扩展为通用领域覆盖） |

| v4.1.0 | 2026-06-16 | 63技能（+3 ljg增强companion技能：writing-voice/elicitation-modes/infographic-design；5核心技能触发场景全面细化；方法论12→15） |

| v4.0.0 | 2026-06-16 | 60技能（+5 吸收 ljg-skills 方法论引擎：domain-decompose/book-deconstruct/deep-think/qa-extract/relationship-analysis；方法论 7→12，跨技能调用网络） |

| v3.1.0 | 2026-06-14 | 55技能（+3 baoyu-cover-image/baoyu-translate/youtube-content；architecture-diagram v1.1 扩展7种图表类型） |

| v3.0.0 | 2026-06-14 | 52技能（+2 brandkit/redesign-skill；+5 huashu-design reference吸收；design-md反模式扩展；设计管线三环→五环） |

| v2.1.0 | 2026-06-13 | 49技能（+1 taste-skill 设计方向指引；huashu-design/hallmark 三环联动协议） |

| v2.0.0 | 2026-06-11 | 48技能（自建核心+三方吸收+方法论开发） |

| v1.0.0 | 2026-06-05 | 首次发布：16技能 |



---



## 📄 License



MIT — 详见各 SKILL.md 中的作者归属。



---



**Made with ❤️ by Hermes Agent + 杨瑒 (月夜)**

