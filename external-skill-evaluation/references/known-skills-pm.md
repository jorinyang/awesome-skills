# Known Skills Ecosystem: PM / Product Management

> 已知的外部 Product Management 技能生态。用于快速识别重复评估和复用已有分析。

## phuryn/pm-skills

- **仓库**: https://github.com/phuryn/pm-skills
- **作者**: Paweł Huryn (The Product Compass Newsletter)
- **类型**: Claude Code Plugin Marketplace (9 plugins, 68 skills, 42 commands)
- **方法论基础**: Teresa Torres, Marty Cagan, Alberto Savoia, Dan Olsen, Strategyzer
- **评估日期**: 2026-06-18
- **评估结论**: 5 个 🟢 独立吸收 + 4 个 🔵 借鉴注入 + 59 个 🔴/⚪ 放弃

### 插件清单

| # | 插件 | 技能数 | 核心域 | 评估 |
|---|------|:---:|------|:---:|
| 1 | pm-product-strategy | 12 | 战略/愿景/商业模式/定价 | 🟢 product-strategy |
| 2 | pm-product-discovery | 13 | 发现/假设/实验/OST | 🟢 opportunity-solution-tree |
| 3 | pm-execution | 16 | PRD/OKR/路线图/干系人 | 🟢 prioritization-frameworks, stakeholder-map, strategy-red-team |
| 4 | pm-go-to-market | 6 | GTM/滩头/ICP/增长 | 🟡 与 strategy-plan-writing 重叠 |
| 5 | pm-market-research | 7 | 画像/细分/旅程图 | ⚪ 无关 |
| 6 | pm-marketing-growth | 5 | 营销/定位/North Star | ⚪ 无关 |
| 7 | pm-data-analytics | 3 | SQL/留存/A/B测试 | ⚪ 无关 |
| 8 | pm-ai-shipping | 2 | AI代码审计 | ⚪ 无关 |
| 9 | pm-toolkit | 4 | 简历/NDA/语法 | ⚪ 无关 |

### 关键吸收清单

| 来源技能 | 目标 | 分类 | 详情 |
|---------|------|:---:|------|
| prioritization-frameworks | 新建 pm-prioritization-frameworks | 🟢 P0 | 9种框架速查（ICE/RICE/Opportunity Score/Kano/MoSCoW等） |
| stakeholder-map | 新建 stakeholder-mapping | 🟢 P0 | Power×Interest矩阵 + 沟通计划 |
| opportunity-solution-tree | 新建 opportunity-solution-tree | 🟢 P0 | Teresa Torres 四层发现树 |
| product-strategy | 新建 product-strategy-canvas | 🟢 P1 | 9-section 产品战略画布 |
| strategy-red-team | 注入 answer Phase 7 | 🔵 P0 | 攻击钢人方法论增强红队审查 |
| value-proposition | 注入 answer Phase 2 Brief | 🔵 P1 | 6-part JTBD 价值主张 |
| business-model/lean-canvas | 注入 answer Phase 2 | 🔵 P1 | 商业模式画布三合一 |
| pre-mortem (Tiger分级) | 注入 blue-team | 🔵 P1 | 风险分级增强 |
| strategy-red-team | 注入 answer Phase 7 | 🔵 P0 | 攻击钢人方法论 |

### 格式兼容性

- Claude Code plugin 格式，需全部转写为 Hermes SKILL.md
- `$ARGUMENTS` 语法不兼容 Hermes → 改为自然语言触发
- Commands (`/discover`, `/strategy` 等) 不可用 → 纯 skills
- 所有 Google Slides/Sheets 模板链接不可直接访问 → 作为参考链接保留
