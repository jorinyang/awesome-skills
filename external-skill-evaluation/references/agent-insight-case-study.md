# Agent-Insight 吸收案例 — B+A 两阶段模式

> 2026-06-21 | 项目: openEuler/agent-insight (MIT) | 规模: ~168K LOC, 1000 文件

## 项目特征

- **类型**: 平台+技能混合（Next.js 全栈 Web 应用 + 9 个 Agent Skill）
- **平台层**: Next.js 16 + Prisma + OTel + Web 看板 — 不可直接吸收为 Hermes 技能
- **方法论层**: 三维评测体系、四模式优化引擎、去冗余三步法 — 可独立吸收
- **Hermes 适配状态**: `hermesAdapter` 为 stub，需开发 OTel 适配器才能接入平台

## B 方案执行记录

### 吸收的技能 (3 个, ai-engineering 分类)

| Hermes 技能 | 来源 | 吸收内容 |
|------|------|------|
| `skill-evaluator` | `skills/skill-optimizer` + `lib/engine/evaluation` | 三维评测指标、LLM-as-Judge 六维打分、过程追溯、靶向归因、CPSR |
| `skill-ab-test` | `docs/design/ab-testing/` + `lib/engine/evaluation` | 对照组/实验组自动对比、三维决策矩阵、统计显著性 |
| `benchmark-generator` | `skills/skill-benchmark-generator` + `skills/outcome-benchmark-generator` | routing/outcome 双类型测试集、语义去重、难度分层 |

### 关键设计决策

1. **自动触发优先**: skill-evaluator 内置 `auto_trigger` 机制（cron job 每 30 分钟自动评测）
2. **自包含**: 所有技能不依赖 Agent-Insight 平台，可在 Hermes 本地独立运行
3. **评测结果本地持久化**: `~/.hermes-feishu/eval_results/` 目录，JSON 格式

### 测试修复

测试发现并修复了 4 个问题：
- `static_check.sh` JSON 输出格式错误（pass_rate 字段多余引号）
- `static_check.sh` 引用检测正则匹配了 backtick 内的引用
- `static_check.sh` 高危指令扫描误匹配自身
- `benchmark-generator` 缺少 `references/dedup-strategy.md`

## A 方案适配计划

### 关键数据
- 适配器开发量: 2 Waves / ~11 任务组 / 1-3 天
- 客户端: 复用开源 `briancaffey/hermes-otel` 插件（零代码）
- 服务端: 新增 `ingest/otel/hermes-mapper.ts` + 填充 `adapters/hermes.ts`
- 保护区域: `buildAgentCallTree` / `deriveSubagentExecutions` / `prisma/schema.prisma` 禁改

### 触发条件（等待）
1. Skill 数量 > 30
2. 生产事故暴露 Skill 问题
3. 需要量化 AI 投入产出
4. Agent-Insight 进入 1.0+ 稳定版

## 方法论提取

### 可复用的吸收模式

```
平台+技能项目 → B+A 两阶段
  B 阶段: 读 SKILL.md + 读关键引擎代码 → 
           提取方法论 → 创建自包含 Hermes 技能 → 
           自动触发设计 → 测试修复 → GitHub 同步
  A 阶段: 评估适配成本 → 输出 Waves 计划 → 
           等待触发条件 → 开发适配器 → 部署平台
```

### GitHub 同步清单
- [x] 更新 badge (73→76)
- [x] 添加索引行 (ai-engineering 分类)
- [x] 添加详细技能介绍段
- [x] 更新安装脚本（category 映射）
- [x] 更新版本历史
- [x] commit + tag v4.5.0
- [ ] push (网络延迟)
