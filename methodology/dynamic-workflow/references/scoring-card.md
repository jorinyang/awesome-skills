# 动态工作流计分卡速查

## 8 维度 × 4 级计分

| D# | 维度 | 驱动模式 | 0 分 | 1 分 | 2 分 | 3 分 |
|----|------|---------|------|------|------|------|
| D1 | 可并行度 | ② Fanout | 不可拆分 | 2 个子任务 | 3-5 个 | 6+ 批量 |
| D2 | 领域离散度 | ① Classify | 单一领域 | 2 个关联领域 | 3+ 不关联领域 | 边界模糊 |
| D3 | 风险等级 | ③ Adversarial | 无后果 | 用户可见 | 数据/发布 | 安全/合规 |
| D4 | 方案广度 | ④ Gen-Filter | 单一答案 | 2-3 方案 | 4-10 方案 | 11+ 探索 |
| D5 | 评价难度 | ⑤ Tournament | 明确指标 | 有主观成分 | 标准模糊 | 多利益方 |
| D6 | 探索深度 | ⑥ Loop | 一步到位 | 2-3 轮 | 深度未知 | 开放式 |
| D7 | 任务模糊度 | 先 Clarify | 规格完整 | 方向明确 | 目标模糊 | 一句话 |
| D8 | 依赖复杂度 | 限制并行 | 完全并行 | 简单 DAG | 复杂 DAG | 依赖未知 |

## 自动触发阈值

| 模式 | 触发条件 |
|------|---------|
| ① Classify | D2 ≥ 1 |
| ② Fanout | D1 ≥ 2 |
| ③ Adversarial | D3 ≥ 2（D3=3 强制，不可跳过） |
| ④ Gen-Filter | D4 ≥ 1 |
| ⑤ Tournament | D5 ≥ 2 AND D4 ≥ 1 |
| ⑥ Loop | D6 ≥ 2 |
| 先 Clarify | D7 ≥ 2 |

## 复杂度总分 → 行为

| 总分 | 行为 |
|------|------|
| 0-5 | 静默跳过，直接执行 |
| 6-9 | 构建工作流，单层 delegate_task |
| 10-14 | 构建工作流，多层 delegate_task + 质量门 |
| 15+ | 构建工作流 + 强制 ③ 验证 + 先 Clarify |

## 模式组合速查

| 任务类型 | 典型 D 分布 | 激活模式 | Agent 模板 |
|---------|-----------|---------|-----------|
| 代码审查 | D1=3 D3=3 | ②+③ | parallel reviewers + verifiers |
| 方案选型 | D4=2 D5=2 | ④+⑤ | generators × 3 + pairwise judges |
| 安全审计 | D1=2 D3=3 | ①+②+③ | classifier + reviewers + verifiers |
| 调研报告 | D1=2 D6=2 | ②+⑥ | parallel researchers + loop convergence |
| Bug 修复 | D6=2 D7=1 | ⑥ | loop until root cause |
| 竞品分析 | D1=3 D4=1 D6=1 | ②+④ | parallel analysts + gen+filter |
| 系统迁移 | D1=3 D3=2 D8=2 | ②+③(受限) | staged fanout + verification |
| 一句话需求 | D7=3 | 先 Clarify | clarify first, then re-score |
