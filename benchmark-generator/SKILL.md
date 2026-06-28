---
name: benchmark-generator
description: >
  Skill 测试集自动生成器。从目标 Skill 定义中自动生成 routing 测试集（该不该命中此 Skill）和 outcome 测试集
  （成功执行后应产出什么），自动去重后入库。触发：生成测试集、造benchmark、自动生成用例、造评测数据、
  生成 skill 测试数据、这个 skill 的测试数据、generate benchmark、create test set。
version: 1.0.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [benchmark, test-data, skill-evaluation, dataset-generation, ai-engineering]
    related_skills: [skill-evaluator, skill-ab-test, double-evolution]
triggers:
  - "生成测试集"
  - "造 benchmark"
  - "自动生成用例"
  - "造评测数据"
  - "生成 skill 测试数据"
  - "这个 skill 的测试数据"
  - "generate benchmark"
  - "create test set"
  - "生成测试用例"
  - "补充 benchmark"
  - "没测试数据怎么测"
---

# Benchmark Generator — Skill 测试集自动生成器

> **定位**：不是手工一条条写测试用例——是读 Skill 定义后自动生成「routing 测试集 + outcome 测试集」，自动去重入库。
>
> **核心理念**：评测的前提是有测试数据。测试数据不应该靠手工维护——Skill 本身包含了"我应该怎么被触发、我应该产出什么"的信息，据此自动生成。

## 触发条件

| 信号 | 示例 |
|------|------|
| 用户要求生成测试集 | "帮我给 troubleshooter 生成 benchmark" |
| 准备做 A/B 测试但缺数据 | "要给 email-sender 做 A/B，先造 10 条测试用例" |
| 用户发现缺少测试覆盖 | "这个 skill 没有测试数据怎么测？造一些" |
| 新 Skill 上线前 | "新写的 docker-fault-fix skill，生成一些测试用例" |

---

## 核心概念

### 两类测试集

| 类型 | 要回答的问题 | 核心字段 |
|------|-------------|------|
| **Routing Benchmark** | "这个 query 该不该命中这个 Skill？" | query, semantic_intent, anchor_keywords, should_match(true/false) |
| **Outcome Benchmark** | "命中后，Skill 应该成功产出什么？" | scenario, standard_answer, root_causes, key_actions |

### 为什么分两类？

- Routing 只管**匹配**——该不该激活
- Outcome 只管**质量**——激活后做得对不对

混在一起会导致：不知道低分是因为"没匹配到"还是"匹配到了但做错了"。

---

## 执行流程

### Phase 1: 读取 Skill 定义

1. 读取目标 Skill 的 `SKILL.md`
2. 提取关键信息：
   - `description` → routing 触发信号
   - `triggers` → 应命中的 query 关键词
   - 执行流程中的步骤 → 预期产出结构
   - `references/` 中的场景说明 → 测试场景素材

### Phase 2: 生成 Routing 测试集

对于 routing 测试集，生成两类 query：

**正面用例 (应命中) — 占 60-70%**：
```
来源: Skill 的 description 和 triggers
方法: 
  1. 直接使用 triggers 中的关键词组合
  2. 从 description 提取语义场景，反向构造自然语言 query
  3. 模拟真实用户的不同表达方式（口语化/正式/简略/详细）

示例 (以 troubleshooter 为例):
  - "帮我看下为什么服务挂了"
  - "线上 OOM 了，排查一下"
  - "docker 容器一直重启，诊断一下"
```

**负面用例 (不应命中) — 占 30-40%**：
```
来源: 与 Skill 职责相近但不完全匹配的场景
方法:
  1. 同一领域但不同子问题的 query
  2. 与 description 相似但语义不匹配的 query
  3. 不同领域但包含相同关键词的 query（边界测试）

示例 (以 troubleshooter 为例):
  - "帮我写一个 docker-compose 文件"（关键词重叠但语义不同）
  - "服务器怎么加固安全"（同一领域但不同范畴）
  - "今天天气怎么样"（完全无关）
```

每条 routing 测试数据格式：
```json
{
  "type": "routing",
  "skill": "troubleshooter",
  "query": "我的 k8s pod 一直 CrashLoopBackOff 怎么办",
  "semantic_intent": "故障排查_容器异常",
  "anchor_keywords": ["CrashLoopBackOff", "pod", "k8s"],
  "should_match": true,
  "difficulty": "medium"
}
```

🔴 **CHECKPOINT** — Routing 测试集已生成。验证通过后继续：
>- [ ] 正面/负面用例比例是否在 60-70% / 30-40% 范围内？
>- [ ] 每条数据是否都有 `should_match` 字段？
>- [ ] difficulty 分布是否覆盖 easy/medium/hard？
>- [ ] 若验证失败 → 调整 Phase 2 参数后重新生成
>
>🛑 验证通过 → 继续 Phase 3

### Phase 3: 生成 Outcome 测试集

对于 outcome 测试集，构造典型成功场景：

```
来源: Skill 的步骤流程 + references/ 中的场景
方法:
  1. 从 Skill 步骤中提取 "目标产出物"
  2. 构造能触发该产出的输入场景
  3. 根据步骤要求生成标准答案（standardAnswer）
  4. 提取应有的 root_causes 和 key_actions
```

每条 outcome 测试数据格式：
```json
{
  "type": "outcome",
  "skill": "troubleshooter",
  "scenario": "用户报告 k8s pod 持续 CrashLoopBackOff",
  "input_context": "k8s v1.28 / Ubuntu 22.04 / 3 节点集群",
  "standard_answer": "诊断出 OOMKilled → 容器内存限制 512Mi 不足 → 建议调至 1Gi",
  "root_causes": ["容器内存限制不足", "应用内存泄漏"],
  "key_actions": ["检查 pod events", "查看 OOM 日志", "分析内存使用趋势"],
  "difficulty": "medium"
}
```

### Phase 4: 去重检查

生成后与已有测试集对比去重：

```
去重策略:
├── Routing: 语义相似度 > 0.85 的 query 视为重复，跳过
├── Outcome: scenario + standard_answer 组合相似度 > 0.8 视为重复，跳过
└── 人工标记: 若检测到可能重复但不确定，保留但标注 potential_duplicate_of
```

🔴 **CHECKPOINT** — 去重完成。验证通过后继续：
>- [ ] 去重后 routing 用例数 ≥ 原始建议数下限？
>- [ ] 去重后 outcome 用例数 ≥ 原始建议数下限？
>- [ ] 是否所有 `potential_duplicate_of` 都有明确标注？
>- [ ] 若数量不足 → 回到 Phase 2/3 补生成差额用例

🛑 验证通过 → 继续 Phase 5 入库

### Phase 5: 入库

将去重后的测试数据写入 `~/.hermes-feishu/benchmarks/{skill_name}/`:

```
~/.hermes-feishu/benchmarks/troubleshooter/
├── routing.json       # Routing 测试集
├── outcome.json       # Outcome 测试集
├── manifest.json      # 测试集元信息（生成时间、数量、版本）
└── changelog.md       # 变更记录
```

manifest.json 格式：
```json
{
  "skill_name": "troubleshooter",
  "skill_version": "1.1.0",
  "generated_at": "2026-06-21T15:00:00+08:00",
  "total_routing_cases": 15,
  "total_outcome_cases": 10,
  "routing_positive_ratio": 0.67,
  "difficulty_distribution": {
    "easy": 5, "medium": 12, "hard": 8
  },
  "generator_version": "1.0.0"
}
```

🔴 **CHECKPOINT** — 测试数据已入库。最终验证：
>- [ ] `manifest.json` 中 `total_routing_cases` 与 `total_outcome_cases` 与实际文件一致？
>- [ ] `routing.json` 与 `outcome.json` 格式合法（JSON 校验通过）？
>- [ ] `changelog.md` 已记录本次变更？
>- [ ] 若入库失败 → 检查磁盘空间与目录权限，重试写入

🛑 全部通过 → 交付测试集，输出 `manifest.json` 摘要

---

## 生成策略

### 难度分层

| 难度 | Routing 特征 | Outcome 特征 |
|:---:|------|------|
| 🟢 easy | 直接使用 trigger 关键词 | 标准场景，输入完整 |
| 🟡 medium | 语义相似但表达不同 | 常见变体场景 |
| 🔴 hard | 多意图混合、边界场景 | 信息不完整、需推理补全 |

### 数量建议

| Skill 复杂度 | Routing 建议数 | Outcome 建议数 |
|:---:|:---:|:---:|
| 简单（单一功能，< 5 步） | 8-12 条 | 5-8 条 |
| 中等（3-5 个子功能，5-10 步） | 15-25 条 | 10-15 条 |
| 复杂（多场景，> 10 步） | 25-40 条 | 15-25 条 |

---

## 失败模式与恢复

| # | 触发条件 | 症状 | 一线修复 | 仍失败兜底 |
|---|---------|------|---------|-----------|
| 1 | Skill 定义缺失/损坏 | `SKILL.md` 不存在或 YAML frontmatter 解析失败 | 检查路径是否正确，确认 Skill 名拼写无误 | 回退到手工造用例，输出模板让用户自行填写 |
| 2 | Phase 2 生成数量不足 | routing 用例 < 建议数下限 50% | 降低语义相似度阈值（0.85 → 0.75），扩充 trigger 组合变体 | 标记 `insufficient_coverage`，在 manifest 中声明缺口 |
| 3 | Phase 3 outcome 标准答案空洞 | `standard_answer` 字数 < 20 或仅包含泛化描述 | 从 SKILL.md 步骤中提取具体预期产出，重新构造 | 标记该用例 difficulty=hard，在 changelog 中备注 |
| 4 | Phase 4 去重冲突 | 去重阈值导致大量误判（>30% 标记为重复但实际不同） | 提高语义相似度阈值（0.85 → 0.92），人工抽查边界案例 | 跳过自动去重，全部保留但标注 `manual_dedup_required` |
| 5 | Phase 5 磁盘空间不足 | `write` 操作报 ENOSPC | 清理 `~/.hermes-feishu/benchmarks/` 中旧测试数据（保留最近 3 次） | 输出 JSON 到终端，提示用户手动保存 |
| 6 | Phase 5 目录权限不足 | `EACCES` 创建目录失败 | `mkdir -p` 重试，若仍失败则写入 `/tmp/` 备用路径 | 输出完整文件路径，提示用户移动 |

## ⛔ 反例与禁止

违反以下任何一条将导致生成的测试集不可用于评测：

| ❌ 反例 | 正确做法 |
|---------|---------|
| 生成与 Skill 定义无关的测试数据 | 必须基于 SKILL.md 内容构造 |
| routing 和 outcome 混在一起 | 必须分开生成，独立文件 |
| 不检查去重就直接入库 | 必须先执行 Phase 4 去重 |
| standardAnswer 空泛 | 必须包含具体的诊断结论/操作步骤 |
| 只生成正面用例 | 必须包含边界和负面用例，比例见 Phase 2 |
| 跳过 manifest.json 生成 | 每次入库必须更新 manifest |
| 靠人工记忆测试集内容来去重 | 必须用 Phase 4 定义的语义相似度算法 |

---

## 参考文件

| 文件 | 用途 | 何时查阅 |
|------|------|---------|
| `references/case-template.md` | 测试用例模板（routing + outcome 完整 schema） | Phase 2/3 生成前确认字段规范 |
| `references/dedup-strategy.md` | 去重策略详解（语义相似度算法、阈值调优） | Phase 4 去重时遇到边界案例 |

> 以上文件均为本 Skill 的运行时依赖。若缺失或损坏，回退到 SKILL.md 内嵌的默认格式与阈值。

## 关联技能指引

> 以下指引由 `github-absorb` Phase 6 自动生成

- **downstream → `skill-ab-test`**：测试集生成并去重入库后，可加载 `skill-ab-test` 用同一批测试数据对 Skill 新旧版本做 A/B 对比评测，形成「生成测试集 → 跑 AB 对比 → 输出决策建议」的测试闭环。
