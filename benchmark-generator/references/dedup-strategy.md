# 去重策略详解

## Routing 测试集去重

### 语义去重方法

1. **关键词重叠率**：两条 query 的 anchor_keywords 交集 / 并集 > 70% → 标记为疑似重复
2. **语义向量相似度**：将 query 文本转换为向量，cosine similarity > 0.85 → 标记为重复
3. **意图等价判断**：两条 query 的 semantic_intent 相同 且 关键实体一致 → 直接去重

### 去重规则

```
if should_match 不同:
  保留两条（一条正面、一条负面，即使语义相似也不去重）
elif cosine_sim(query_a, query_b) > 0.85:
  skip（保留先入库的那条）
elif keyword_overlap > 0.70 and semantic_intent 相同:
  标记 potential_duplicate_of，保留但可供人工审核
else:
  keep（独立用例）
```

## Outcome 测试集去重

### 去重维度

| 维度 | 权重 | 方法 |
|------|:---:|------|
| scenario 相似度 | 40% | 文本相似度 |
| standard_answer 相似度 | 30% | 关键事实匹配 |
| root_causes 重叠率 | 20% | 集合 Jaccard |
| key_actions 重叠率 | 10% | 集合 Jaccard |

### 去重规则

```
综合相似度 = 0.4 × scenario_sim + 0.3 × answer_sim + 0.2 × cause_sim + 0.1 × action_sim

if 综合相似度 > 0.80:
  skip（保留先入库的那条）
elif 综合相似度 > 0.60:
  标记 potential_duplicate_of，降低权重
else:
  keep（独立用例）
```

## 特殊情况

1. **同一语义的不同表达**：如 "docker 容器挂了" 和 "docker container crashed" → 检测到中英混合时降低相似度阈值到 0.75
2. **同一场景的不同难点**：if difficulty 不同 → 即使 scenario 相同也保留（hard 版本通常包含更多边界条件）
3. **信息完整度差异**：if 新用例的 input_context 比旧用例丰富 > 30% → 替换旧用例（更完整的用例往往质量更高）
