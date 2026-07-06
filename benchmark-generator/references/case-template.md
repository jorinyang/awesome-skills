# 测试用例模板

## Routing 测试用例

```json
{
  "type": "routing",
  "skill": "{skill_name}",
  "skill_version": "{version}",
  "query": "{用户可能的输入 query}",
  "semantic_intent": "{query 表达的语义意图}",
  "anchor_keywords": ["{关键词1}", "{关键词2}"],
  "should_match": true,
  "match_reason": "{为什么应该匹配这个 Skill}",
  "difficulty": "easy|medium|hard",
  "source": "auto-generated",
  "generated_at": "{timestamp}"
}
```

### Routing 示例

```json
[
  {
    "type": "routing",
    "skill": "docker-fault-fix",
    "skill_version": "1.0.0",
    "query": "docker 容器启动后马上退出，怎么排查",
    "semantic_intent": "故障排查_Docker容器异常退出",
    "anchor_keywords": ["docker", "容器", "退出", "排查"],
    "should_match": true,
    "match_reason": "Query 包含 Docker 故障排查语义，与 Skill 的故障诊断职责匹配",
    "difficulty": "easy",
    "source": "auto-generated",
    "generated_at": "2026-06-21T15:00:00+08:00"
  },
  {
    "type": "routing",
    "skill": "docker-fault-fix",
    "skill_version": "1.0.0",
    "query": "帮我用 docker 部署一个 nginx",
    "semantic_intent": "部署_Web服务器",
    "anchor_keywords": ["docker", "部署", "nginx"],
    "should_match": false,
    "match_reason": "部署类请求不属于故障排查范畴，虽然含 docker 关键词",
    "difficulty": "medium",
    "source": "auto-generated",
    "generated_at": "2026-06-21T15:00:00+08:00"
  }
]
```

## Outcome 测试用例

```json
{
  "type": "outcome",
  "skill": "{skill_name}",
  "skill_version": "{version}",
  "scenario": "{测试场景描述}",
  "input_context": "{输入上下文信息}",
  "standard_answer": "{Skill 成功执行后应产出的标准答案}",
  "root_causes": ["{根因1}", "{根因2}"],
  "key_actions": ["{应执行的关键动作1}", "{应执行的关键动作2}"],
  "difficulty": "easy|medium|hard",
  "source_scenario": "{来源场景（可选）}",
  "source": "auto-generated",
  "generated_at": "{timestamp}"
}
```

### Outcome 示例

```json
{
  "type": "outcome",
  "skill": "docker-fault-fix",
  "skill_version": "1.0.0",
  "scenario": "用户报告的 docker 容器频繁 OOM 重启",
  "input_context": "Docker 20.10 / Ubuntu 22.04 / 容器内存限制 256Mi / 运行 Node.js 应用",
  "standard_answer": "诊断出容器内存不足（256Mi）→ Node.js 应用运行时内存峰值约 400Mi → 建议调整内存限制至 512Mi 并排查应用内存泄漏",
  "root_causes": ["容器内存限制过低", "Node.js 应用可能的内存泄漏"],
  "key_actions": ["查看容器 OOM 日志", "检查容器内存限制配置", "分析应用内存使用趋势", "计算合理的内存限制值"],
  "difficulty": "medium",
  "source_scenario": "运维故障案例库 #42",
  "source": "auto-generated",
  "generated_at": "2026-06-21T15:00:00+08:00"
}
```
