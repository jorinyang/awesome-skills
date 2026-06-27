---
name: double-evolution
description: >-
  双速技能进化引擎——吸收 MOMO CODE / Pioneer Agent 方法论，实现 Hermes 技能的自动观测→蒸馏→注入→固化闭环。
  Fast Loop（/evolve 手动触发，秒-分级）：扫描信号→蒸馏候选 patch→Thompson 采样选择→注入预览→人工确认。
  Slow Loop（Cron 30min 自动，时-日级）：聚合信号→skill-evaluator 对比→Ratchet Gate 只保留提升版本→飞书提案。
  触发词：/evolve / 技能进化 / 进化技能 / 优化技能 / 看看哪些技能该优化了 / 技能自进化
version: 1.0.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [evolution, skill-optimization, self-improvement, meta-skill]
    related_skills: [skill-evaluator, darwin-skill, github-absorb]
triggers:
  - "/evolve"
  - "/evolve observe"
  - "/evolve distill"
  - "/evolve inject"
  - "/evolve solidify"
  - "/evolve status"
  - "技能进化"
  - "进化技能"
  - "优化技能"
  - "看看哪些技能该优化了"
  - "技能自进化"
  - "自动优化技能"
---

# double-evolution — 双速技能进化引擎

> 吸收自：[MOMO CODE](https://github.com/momozi1996/momo-code) × [Pioneer Agent](https://arxiv.org/abs/2604.09791)（§2.1-§2.8, §21.4）
>
> **核心范式**：将 LLM 权重级的双速进化（KEP + MCGS + LoRA）适配到 Hermes 技能的 prompt/procedure 级进化。

## 架构

```
┌──────────────────────────────────────────────────────────┐
│                  双速技能进化引擎                          │
│                                                          │
│  Fast Loop (/evolve，手动触发)                             │
│  ┌────────────────────────────────────────────┐          │
│  │ observe → distill → inject → solidify      │          │
│  │  扫描      蒸馏      注入      固化         │          │
│  │  signals  →tactics →patches →feedback      │          │
│  └────────────────────────────────────────────┘          │
│                      │ Bridge                            │
│                      ↓                                   │
│  Slow Loop (Cron 30min，自动)                             │
│  ┌────────────────────────────────────────────┐          │
│  │ mine → evaluate → gate → report            │          │
│  │ 聚合    三维评测   Ratchet  飞书提案        │          │
│  └────────────────────────────────────────────┘          │
│                                                          │
│  数据层: ~/.hermes-feishu/evolution/                      │
│  ├── signals.jsonl    ← 原始信号（append-only）           │
│  ├── tactics.jsonl    ← 蒸馏出的策略卡片                  │
│  ├── patches.jsonl    ← 候选/已应用 patch                │
│  └── ledger.jsonl     ← 审计日志                         │
└──────────────────────────────────────────────────────────┘
```

## 触发条件

### 命令触发

| 命令 | 作用 |
|------|------|
| `/evolve` 或 `/evolve status` | 显示进化状态仪表盘 |
| `/evolve observe` | 扫描 signals.jsonl，聚类失败模式 |
| `/evolve distill` | 对高频失败模式蒸馏候选 patch |
| `/evolve inject` | Thompson 采样选择最优 patch，生成预览 |
| `/evolve solidify` | 反馈最近注入的 patch（好用/不好用） |

### 上下文触发

当用户说以下内容时自动加载本技能：
- "技能进化" / "进化技能" / "优化技能"
- "看看哪些技能该优化了" / "技能自进化"

---

## 命令详细流程

### 1. `/evolve status` — 进化状态仪表盘

**目标**：展示所有已追踪技能的健康状态。

**流程**：
1. 读取 `~/.hermes-feishu/evolution/tactics.jsonl`
2. 读取 `~/.hermes-feishu/evolution/patches.jsonl`
3. 按技能聚合统计：
   - 信号总数（近 7 天 / 近 30 天）
   - 成功率（pass / total）
   - 候选 tactic 数
   - 已注入 patch 数
   - 已固化 patch 数

**输出格式**：

```markdown
## 技能进化仪表盘

| 技能 | 7天信号 | 成功率 | 候选tactic | 已注入 | 已固化 |
|------|:------:|:------:|:----------:|:------:|:------:|
| feishu-doc | 23 | 78% | 3 | 1 | 0 |
| answer | 15 | 87% | 1 | 0 | 0 |
| github-absorb | 8 | 75% | 2 | 1 | 0 |

### 需要关注的技能
- **feishu-doc**: 成功率 < 80%，3 个候选 tactic 待注入 → 建议 `/evolve inject`
- **github-absorb**: 有 1 个已注入 patch 待 solidify → 建议 `/evolve solidify`
```

### 2. `/evolve observe` — 扫描信号

**目标**：从 signals.jsonl 中提取近期失败模式。

**流程**：
1. 读取 `signals.jsonl`，筛选近 7 天的信号
2. 按 `skill + outcome` 分组
3. 识别高频失败模式（同一组 ≥ 3 条）
4. 对每次失败，加载原始 session 上下文（`session_search`）
5. 输出聚类报告

**输出格式**：

```markdown
## 信号扫描报告 ({日期})

### 发现的失败模式

#### feishu-doc
- **user_corrected × 5**: 创建文档时标题格式错误
  - s_001: "标题应包含日期" → 触发词"创建文档"不够精确
  - s_012: "缺少 --parent-token" → 未在上下文中提供 Wiki 节点
  - ...

#### github-absorb
- **rejected × 3**: Phase 4 吸收策略矩阵与用户预期不一致
  - s_008: 用户选了"只记录参考"但技能继续推进 Phase 5
  - ...

### 聚类摘要
- 总计: 42 条信号，识别 4 个失败模式
- feishu-doc (2) / github-absorb (1) / answer (1)
```

### 3. `/evolve distill` — 蒸馏候选 patch

**目标**：对 observe 识别的失败模式，生成可执行的 patch 建议。

**流程**：
1. 对每个高频失败模式（≥ 3 条信号）
2. 读取对应技能 SKILL.md 全文
3. 分析根因：是触发词问题？流程缺失？输出去向不明？
4. 调用 LLM 生成候选 patch（old_string → new_string）
5. 检查去重：相同 old_string 的 patch 是否已存在于 tactics.jsonl
6. 写入 tactics.jsonl（status=candidate，alpha=1，beta=1）

🔴 **CHECKPOINT**：生成的 patch 必须满足——
- [ ] old_string 在技能文件中唯一存在
- [ ] new_string 保留原有功能，只增加/调整
- [ ] 不改变技能的核心架构

**输出格式**：

```markdown
## 蒸馏结果 ({日期})

### 新候选 tactic

| # | 技能 | 类型 | 标题 | 成功率预估 |
|---|------|------|------|:--------:|
| t_001 | feishu-doc | trigger_addition | 添加"新建飞书文档"触发词 | — |
| t_002 | github-absorb | checkpoint_add | Phase 3 后加用户确认检查点 | — |
| t_003 | answer | flow_reorder | Clarify 跳过逻辑前置 | — |

### 去重命中
- t_004 (answer trigger_addition) 与已有 t_a1b2c3d4 重复 → 已跳过
```

### 4. `/evolve inject` — 注入 patch

**目标**：Thompson 采样选择最优候选 tactic，生成 patch 预览，人工确认后执行。

**流程**：
1. 读取 tactics.jsonl，筛选 status=candidate 的 tactic
2. 对每个 tactic，计算 Beta(α, β) 随机采样值
3. 选择采样值最高的 tactic
4. 展示 patch 预览（diff 格式）
5. 等待用户确认

🔴 **CHECKPOINT**：应用前必须展示预览并等待确认。

5. 用户确认后：
   - 执行 `skill_manage(action='patch', name='{skill}', old_string='...', new_string='...')`
   - 写入 patches.jsonl（action=applied）
   - 更新 tactics.jsonl（status=injected）
   - 写入 ledger.jsonl（kind=inject）

**输出格式**：

```markdown
## 注入预览 — t_{id}

**技能**: feishu-doc
**类型**: trigger_addition
**标题**: 添加"新建飞书文档"触发词
**Thompson 采样**: Beta(α=3, β=1) → sample=0.81
**胜率预估**: 75%

### 变更预览

```diff
 triggers:
   - "创建飞书文档"
   - "写飞书文档"
   - "创建文档"
+  - "新建飞书文档"
```

> 确认注入？(y/n)
```

### 5. `/evolve solidify` — 固化反馈

**目标**：收集注入后 patch 的表现反馈，更新 Beta 分布。

**流程**：
1. 读取 patches.jsonl，筛选 status=injected 且未 solidify 的 patch
2. 读取对应 tactic 的后续信号（注入后的 signals）
3. 展示每个 injected patch 注入前后对比
4. 询问用户评价

**用户评价选项**：
- `好用` → tactic.alpha += 1，记录信号
- `不好用` → tactic.beta += 1，记录信号
- `没感觉` → tactic.alpha += 0.5，tactic.beta += 0.5

**门禁规则**：
- alpha + beta ≥ 5 且 alpha/(alpha+beta) ≥ 0.7 → status = solidified
- alpha + beta ≥ 5 且 alpha/(alpha+beta) < 0.5 → status = rejected（触发自动回滚）
- 否则保持 injected

**自动回滚**：当 tactic 被 rejected 时——
- 读取对应 patch，执行 `skill_manage(action='patch')` 反向回滚
- 写入 patches.jsonl（reverted=true）
- 写入 ledger.jsonl（kind=rollback）

**输出格式**：

```markdown
## 固化反馈

| # | 技能 | Tactic | 注入时间 | 注入后信号 | 当前胜率 | 状态 |
|---|------|--------|---------|:--------:|:--------:|------|
| 1 | feishu-doc | trigger_addition | 3h前 | 4 pass, 1 fail | 80% | → solidified |

### 待评价
| # | 技能 | Tactic | 操作 |
|---|------|--------|------|
| 2 | github-absorb | checkpoint_add | 好用 / 不好用 / 没感觉 |
```

---

## Slow Loop（Cron 30min）

Slow Loop 由独立的 cron job 驱动，不依赖本技能的手动触发。

### 流水线

```
每 30 分钟执行:
  ① Mine:
     - 读取 signals.jsonl（自上次运行后的新信号）
     - 按 skill 聚合，识别高频失败模式（≥5 次）
  
  ② Evaluate:
     - 对每个 solidifiable tactic：
       - 创建技能副本 ~/.hermes-feishu/skills/_eval/{skill}_v{n}/
       - 应用 patch
       - 调用 skill-evaluator 三维对比
         · 执行精准度 (precision)
         · 端到端时效 (timeliness)
         · 计算成本 (cost)
  
  ③ Gate (Ratchet):
     - 只保留三维评分全部 ≥ 原版的 patch
     - 任一维度退化 → 标记 rejected + 自动回滚
     - 通过 → 标记 promoted + 发送飞书通知
  
  ④ Report:
     - 生成飞书文档《技能进化提案 {日期}》
     - 每个提案：
       · 技能名 / 问题描述 / 建议 patch / 预期改善 / 风险
     - 发送到当前 DM
```

### Cron 创建命令

⚠️ **重要**：`cronjob` API 的 `repeat` 默认为 `once`（只跑一次）。创建持续循环的 Slow Loop 时**必须**显式传 `repeat=0`（= forever）或后续用 `update` 修正。

```bash
# 首次初始化时执行（技能加载后自动触发）
cronjob create \
  --name "hermes-evolution-slow-loop" \
  --schedule "30m" \
  --repeat 0 \
  --skills "double-evolution,skill-evaluator" \
  --prompt "加载 double-evolution 技能，执行 Slow Loop 流水线：Mine→Distill→Evaluate→Gate→Report"
```

验证创建成功：
```bash
cronjob list | grep evolution
# 确认 repeat=forever，非 once
```

> 如已创建为 `once`，用 `cronjob update --job-id <id> --repeat 0` 修正。

---

## 技能间关系

| 技能 | 关系 | 使用方式 |
|------|:---:|---------|
| `skill-evaluator` | downstream | Slow Loop 第②步：三维对比新旧技能版本 |
| `darwin-skill` | downstream | L1 静态检查：patch 后的技能结构是否完整 |
| `github-absorb` | upstream | 方法论文档：记录吸收自 MOMO CODE 的范式 |

---

## 数据文件位置

| 文件 | 路径 |
|------|------|
| signals.jsonl | `~/.hermes-feishu/evolution/signals.jsonl` |
| tactics.jsonl | `~/.hermes-feishu/evolution/tactics.jsonl` |
| patches.jsonl | `~/.hermes-feishu/evolution/patches.jsonl` |
| ledger.jsonl | `~/.hermes-feishu/evolution/ledger.jsonl` |
| schema.md | `~/.hermes-feishu/evolution/schema.md` |

---

## 信号采集（通过技能引用）

本技能**不要求**在其他技能 SKILL.md 中嵌入信号采集代码。改为更轻量的引用模式：

### 方式：技能引用 + Agent 自主记录

1. **核心技能声明关联**：在目标技能的 `related_skills` 中添加 `double-evolution`。当 Agent 加载该技能时，会同时知道此技能被进化系统追踪。

2. **Agent 自主记录**：当 Agent 在会话中使用被追踪的技能时，根据以下 schema 在 `~/.hermes-feishu/evolution/signals.jsonl` 追加一行记录：

```json
{"id":"s_{uuid8}","ts":"{ISO8601}","session_id":"{chat_id}","skill":"{skill_name}","trigger":"hit|miss|false_trigger","outcome":"pass|multi_iteration|user_corrected|rejected|not_used","iterations":{N},"corrections":{N},"user_feedback":"","duration_s":{秒},"context":{"task_summary":"{一句话总结}"}}
```

### 记录时机

Agent 在以下时刻隐性记录信号（不打断对话、不向用户展示）：
- 技能产出被直接使用，无修改 → outcome=pass → 会话结束或切换技能时记录
- 用户要求修改 ≥2 次 → outcome=multi_iteration → 最终产出被接受时记录
- 用户明确指出错误 → outcome=user_corrected → 修正完成后记录
- 用户否定方向 → outcome=rejected → 切换策略时记录
- 技能触发但产出未被使用 → outcome=not_used → 会话结束或超时记录

### 已关联技能

以下技能已声明 `double-evolution` 关联（共 11 个）：

**自建 (7)**：`agent-tool-system`、`benchmark-generator`、`blue-team`、`drawio-generation`、`github-absorb`、`skill-ab-test`、`skill-evaluator`

**三方吸收 (4)**：`author-methodology-analysis`、`dynamic-workflow`、`ocr-and-documents`、`wechat-article-archive`

> 新增需要追踪的技能时，只需在其 `related_skills` 中添加 `double-evolution` 即可。

---

## 反例（禁止）

- ❌ 跳过 observe 直接 distill — 没有信号基础的蒸馏是瞎猜
- ❌ 注入 patch 时不展示预览 — 用户必须有确认机会
- ❌ solidify 时只看 pass/fail 计数不看语义 — 需要分析失败的具体原因
- ❌ Slow Loop 自动 promote 不通知用户 — 所有 promote 必须经过飞书提案
- ❌ 对同一技能同时注入 ≥2 个未 solidify 的 patch — 无法归因哪个有效
- ❌ 手动修改 signals.jsonl / ledger.jsonl — 破坏审计完整性
- ❌ 把本技能用于非技能文件的修改 — 进化范围严格限定在 SKILL.md
- ❌ 创建 Slow Loop Cron 时不检查 `repeat` 参数 — 默认 `once` 只跑一次，必须显式 `repeat=0` 设为 forever

---

## 异常与边界条件

| 场景 | 处理 |
|------|------|
| signals.jsonl 为空 | observe → 输出"无信号记录，请先使用技能积累数据" |
| tactics.jsonl 为空 | inject → 输出"无候选 tactic，请先 /evolve distill" |
| 蒸馏出的 patch old_string 在技能中不存在 | 标记为 invalid，写入 ledger |
| 注入后 24h 内没有新信号 | solidify 提示"数据不足，继续积累" |
| 技能文件已被外部修改，patch 无法应用 | 标记 stale，提示用户手动检查 |
| 多个 cron tick 同时运行 | 文件锁（flock）防并发写入 |
| cron job 被创建为 once 而非 forever | `cronjob update --repeat 0` 修正。创建时 `repeat` 默认为 `once`，持续循环必须显式传 `repeat=0` |
