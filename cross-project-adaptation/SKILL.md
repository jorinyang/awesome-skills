---
name: cross-project-adaptation
description: "Adapt concepts, patterns, and algorithms from one project/language to another. Not code copying — architectural concept transfer with native idioms."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [architecture, adaptation, patterns, refactoring]
    related_skills: [writing-plans, double-evolution]
---

# Cross-Project Adaptation

## 触发条件

### 通用领域触发矩阵

跨项目架构概念迁移覆盖7大领域，21个子场景。

| 领域 | 场景 | 触发信号 | 示例 |
|------|------|---------|------|
| **AI/ML** | 模型服务架构 | 用户想从项目A的模型部署方案迁移到B | "把vLLM的continuous batching搬到我们自己的server" |
| AI/ML | Agent编排 | 用户想从开源Agent框架迁移编排模式 | "把LangGraph的checkpoint机制搬到我们的Agent系统" |
| AI/ML | RAG Pipeline | 用户想从论文实现迁移检索架构 | "把ColBERT的late interaction改到我们已有的pipeline" |
| **Web/后端** | API设计模式 | 用户想从项目A的API设计迁移到B | "Stripe的API版本策略搬到我们的项目" |
| Web/后端 | 数据库设计 | 用户想从Postgres方案适配到MongoDB | "把SQL schema的partition策略迁移到Mongo sharding" |
| Web/后端 | 缓存架构 | 用户想从Redis方案迁移到替代方案 | "把Redis pub/sub的event模式适配到Kafka" |
| **前端** | 组件库迁移 | 用户想从React组件库迁移到Vue | "把Radix UI的accessibility模式搬到Vue组件" |
| 前端 | 状态管理 | 用户想从Redux迁移到Zustand | "把Redux中间件的副作用管理搬到Zustand" |
| 前端 | 路由架构 | 用户想从Next.js迁移到其他框架 | "把Next.js的SSR策略适配到Nuxt" |
| **数据工程** | 数据处理管道 | 用户想从Spark方案适配到Python | "把Spark的window function逻辑用Pandas重写" |
| 数据工程 | 流处理 | 用户想从Flink迁移到RisingWave | "把Flink的时间窗口语义适配到RisingWave" |
| 数据工程 | 数据湖/仓库 | 用户想从Delta Lake迁移到Iceberg | "把Delta Lake的ACID事务模式适配到Iceberg" |
| **基础设施** | CI/CD | 用户想从GitHub Actions迁移到GitLab | "把GHA的matrix build搬到GitLab CI" |
| 基础设施 | 容器编排 | 用户想从Docker Compose迁移到K8s | "把compose的网络拓扑适配到K8s Service" |
| 基础设施 | 监控告警 | 用户想从Datadog迁移到Prometheus | "把Datadog的复合告警逻辑适配到PromQL" |
| **安全** | 认证授权 | 用户想从OAuth迁移到SAML | "把OAuth2的token刷新机制适配到SAML" |
| 安全 | 加密方案 | 用户想从AES迁移到ChaCha20 | "把AES-GCM的认证加密模式适配为ChaCha20-Poly1305" |
| 安全 | 审计日志 | 用户想从ELK迁移到Loki | "把ELK的结构化审计日志适配到Loki label" |
| **移动/IoT** | 推送通知 | 用户想从FCM迁移到APNs | "把FCM的topic订阅模式适配为APNs的channel" |
| 移动/IoT | 离线存储 | 用户想从SQLite迁移到Realm | "把SQLite的migration策略适配到Realm schema" |
| 移动/IoT | 蓝牙/WiFi | 用户想从BLE迁移到WiFi Direct | "把BLE的GATT profile映射到WiFi Direct服务发现" |

### 手动触发
- "把这个项目里的X搬到我们的项目"
- "adapt X from Y to Z"
- "把A的架构模式迁到B"
- "cross-project adaptation"
- "从XX项目学它的YY实现"

## When to Use

Borrowing capabilities from project A (source) to enhance project B (target), especially when:
- Different languages (TypeScript → Python)
- Different architectures (plugin system → monolith)
- Different protocols (MCP → REST)

## Methodology

### Phase 1: Deep Source Analysis

Don't just read READMEs. Examine:
1. **Core interfaces/types** — What contracts does the module define?
2. **Algorithms** — What's the actual computation? (formulas, data structures)
3. **Integration points** — How does it connect to the rest of the system?
4. **Dependencies** — What does it need from the host environment?

### Phase 2: Target Architecture Mapping

Map source concepts to target equivalents:

| Source Concept | Target Equivalent | Adaptation Needed |
|---------------|-------------------|-------------------|
| TypeScript interface | Python Protocol/dataclass | Type system translation |
| npm package | pip package or stdlib | Dependency evaluation |
| MCP tool | REST endpoint or MCP tool | Protocol adaptation |
| EventEmitter | threading + callback | Concurrency model |
| async/await | threading or asyncio | Execution model |

### Phase 3: Selective Import

Don't transplant entire frameworks. Extract:
- **Algorithms** (formulas, scoring, search) — usually portable
- **Data models** (types, enums, interfaces) — translate to target idioms
- **Patterns** (lifecycle, state machines) — reimplement natively
- **Integrations** — rewrite for target's plugin/extension system

### Phase 4: Integration Verification

**Critical**: After implementing modules, verify they're wired into the actual system.
See `references/integration-gap-audit.md` in `clawshell-development` skill for methodology.

## Example: Ruflo → ClawShell

Ruflo (TypeScript) concepts adapted to ClawShell (Python):

| Ruflo Module | ClawShell Adaptation | Key Decision |
|-------------|---------------------|--------------|
| HNSW index (custom TS) | `hnswlib` library | Use battle-tested C++ binding |
| Trust evaluator formula | Direct port | Formula is language-agnostic |
| Swarm topology types | Python Enum + manager | Native dataclasses |
| Hook system (EventEmitter) | threading + priority chain | Sync, not async |
| Plugin lifecycle (IPlugin) | Protocol + state machine | Python typing.Protocol |
| SONA learning (MicroLoRA) | Not ported | Too complex, defer |

## Pitfalls

- **Don't copy code verbatim** — different language idioms, error handling, concurrency models
- **Don't port everything** — YAGNI applies; port what you need now
- **Don't assume API compatibility** — source's API may not fit target's patterns
- **Always verify integration** — unit tests passing ≠ feature working; check call chains
- **Check for existing equivalents** — target may already have something similar under a different name

## Reference Files

- `references/ruflo-adaptation-results.md` — Actual results of Ruflo (TypeScript) → ClawShell (Python) adaptation: 6 modules ported, 398 tests, integration gap findings
