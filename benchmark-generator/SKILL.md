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
    related_skills: [skill-evaluator, skill-ab-test]
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

## 反例（禁止）

- ❌ 生成与 Skill 定义无关的测试数据 — 必须基于 SKILL.md 内容
- ❌ routing 和 outcome 混在一起 — 必须分开生成
- ❌ 不检查去重就直接入库 — 重复数据污染评测结果
- ❌ standardAnswer 空泛 — 必须足够具体才能评测
- ❌ 只生成正面用例 — 必须包含边界和负面用例

---

## 参考文件

- `references/case-template.md` — 测试用例模板
- `references/dedup-strategy.md` — 去重策略详解
