---
name: agent-tool-system
description: >-
  AI Agent 工具系统设计方法论——defineTool→registry→toolsToAI 三层架构。
  当需要为 Agent 系统设计工具集、构建 MCP Server 工具注册表、
  或评估 Agent 工具架构时触发。触发词：Agent 工具/工具系统/tool system/
  defineTool/工具注册表/工具适配器/tool adapter/MCP tools。
version: 1.0.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [agent, tools, architecture, mcp, ai-sdk, design-pattern]
    related_skills:
      - github-absorb
      - cross-project-adaptation
      - skill-evaluator
  source: https://github.com/open-pencil/open-pencil (packages/core/src/tools/)
triggers:
  - "Agent 工具"
  - "工具系统"
  - "tool system"
  - "defineTool"
  - "工具注册表"
  - "工具适配器"
  - "tool registry"
  - "toolsToAI"
  - "MCP tools 设计"
  - "Agent 工具箱"
---

# Agent 工具系统设计方法论

> 吸收自 [OpenPencil](https://github.com/open-pencil/open-pencil) `packages/core/src/tools/` 的三层工具架构。
> 核心思想：**一个工具定义，多处消费**——同一份 ToolDef 同时驱动 AI Chat、CLI、MCP Server，零重复定义。

## 设计哲学

1. **Schema-driven** — 工具定义是单一数据源，消费者（AI SDK / CLI / MCP）是适配器
2. **Layer separation** — Schema（类型）→ Registry（组织）→ Adapter（消费），每层独立演进
3. **Minimal core** — 核心工具集 < 30 个，覆盖 90%+ 场景；扩展工具按需加载
4. **Observability built-in** — 每个工具调用自动记录 before/after 快照、重复检测、noop 检测
5. **Budget awareness** — 步数预算内置于执行管道，防止 Agent 无限循环

## 三层架构

```
┌─────────────────────────────────────────────────────┐
│                  Consumer Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ AI Chat  │  │   CLI    │  │MCP Server│          │
│  │(Vercel AI│  │ (citty)  │  │(JSON Sch)│          │
│  │  +valibot│  │          │  │          │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│       │             │             │                  │
│       ▼             ▼             ▼                  │
│  ┌─────────────────────────────────────┐            │
│  │         Adapter Layer                │            │
│  │  toolsToAI()  cliAdapter()  mcpToJSON()          │
│  └────────────────┬────────────────────┘            │
│                   │                                  │
├───────────────────┼──────────────────────────────────┤
│                   ▼                                  │
│  ┌─────────────────────────────────────┐            │
│  │         Registry Layer               │            │
│  │  CORE_TOOLS    EXTENDED_TOOLS         │            │
│  │  (~30 tools)   (~80 tools)           │            │
│  └────────────────┬────────────────────┘            │
│                   │                                  │
│                   ▼                                  │
│  ┌─────────────────────────────────────┐            │
│  │          Schema Layer                │            │
│  │  ToolDef  defineTool()  ParamDef     │            │
│  └─────────────────────────────────────┘            │
└─────────────────────────────────────────────────────┘
```

---

## Phase 1: Schema Layer — 工具定义

### 1A: 参数类型系统

```typescript
// 五种基础参数类型，覆盖 Agent 工具所有常见输入
type ParamType = 'string' | 'number' | 'boolean' | 'color' | 'string[]'

interface ParamDef {
  type: ParamType
  description: string      // 给 AI 看的，必须写清楚用途
  required?: boolean       // 默认 false
  default?: unknown
  enum?: string[]           // 约束可选值
  min?: number              // 数值范围
  max?: number
}
```

**设计要点**：
- 类型要少而精。5 种够用，不引入 `object`/`array` ——复杂输入拆成多个简单参数
- `description` 是最重要的字段——它是 AI 理解工具意图的唯一入口
- `enum` 比 `min`/`max` 更受 AI 欢迎——枚举值直接出现在 schema JSON 中

### 1B: 工具定义接口

```typescript
interface ToolDef {
  name: string             // snake_case，AI 友好
  description: string      // 一句话说清楚做什么、返回什么
  mutates?: boolean        // true = 会修改状态，触发 before/after 快照
  params: Record<string, ParamDef>
  execute: (api: DomainAPI, args: Record<string, unknown>) => unknown
}
```

**领域 API 模式**：`execute` 的第一个参数是领域 API 对象（如 `FigmaAPI`），不是裸状态。这样：
- 工具不直接依赖全局状态
- 测试时可以注入 mock API
- 同一工具可用于不同上下文

### 1C: 泛型工厂函数

```typescript
function defineTool<P extends Record<string, ParamDef>>(def: {
  name: string
  description: string
  mutates?: boolean
  params: P
  execute: (api: DomainAPI, args: ResolvedParams<P>) => unknown
}): ToolDef {
  return def as ToolDef
}
```

**核心价值**：`defineTool` 不是简单的 identity function——它通过 TypeScript 条件类型 (`ResolvedParams<P>`) 让 `args` 的类型自动推导为参数定义的精确类型。这意味着：
- 写工具时 `args.fontSize` 自动推断为 `number`（因为 ParamDef 里 type 是 'number'）
- `args.color` 自动推断为 `string`
- 编译期保证参数类型正确

### 1D: 工具编写示例

```typescript
// ✅ 正确：参数扁平化，每个参数有 description
export const setFont = defineTool({
  name: 'set_font',
  description: 'Set font family, weight, and style on a text node',
  mutates: true,
  params: {
    id: { type: 'string', required: true, description: 'Node ID to modify' },
    font: { type: 'string', required: true, description: 'Font family name (e.g. Inter, JetBrains Mono)' },
    weight: {
      type: 'number',
      required: true,
      enum: [100, 200, 300, 400, 500, 600, 700, 800, 900],
      description: 'Font weight (100-900)'
    },
    italic: { type: 'boolean', description: 'Enable italic style' }
  },
  execute: (api, args) => {
    const node = requireNode(api, args.id)
    api.setTextProperties(node, {
      fontName: { family: args.font, style: args.italic ? 'Italic' : 'Regular' },
      fontWeight: args.weight
    })
    return nodeSummary(node)
  }
})

// ❌ 错误：参数太复杂
// params: { config: { type: 'object', ... } }  // 不要用 object 类型！
// AI 无法理解嵌套对象的结构
```

### 1E: 辅助工具

```typescript
// 必用工具函数
function requireNode(api: DomainAPI, id: string): Node {
  const node = api.getNodeById(id)
  if (!node) throw new NodeNotFoundError(id)
  return node
}

function nodeSummary(node: Node): { id: string; name: string; type: string } {
  return { id: node.id, name: node.name, type: node.type }
}

// 可选：错误时返回结构化错误给 AI（比抛异常更友好）
function nodeNotFound(id: string): { error: string } {
  return { error: `Node "${id}" not found` }
}
```

**🔴 CHECKPOINT**：每个工具定义完成后自检：
- [ ] `name` 是 snake_case？
- [ ] 每个参数有 `description`？
- [ ] 复杂操作拆成了多个工具？（一个工具只做一件事）
- [ ] `execute` 的返回值是 AI 可理解的结构？

---

## Phase 2: Registry Layer — 工具组织

### 2A: 分层注册

```typescript
// registry-core.ts — 高频工具（~30 个，~3K schema tokens）
export const CORE_TOOLS: ToolDef[] = [
  // Read (5-8)
  getSelection, getNode, findNodes, getJsx,
  // Create (2-3)
  render, createShape,
  // Modify (8-12)
  updateNode, setLayout, setFill, setStroke, setText, setFont, setRadius, setEffects,
  // Structure (4-5)
  deleteNode, reparentNode, nodeResize, batchUpdate,
  // Utility (3-4)
  describe, calc, evalCode, viewportZoomToFit
]

// registry-extended.ts — 低频/特定场景（~80 个）
export const EXTENDED_TOOLS: ToolDef[] = [
  // Vector ops
  booleanUnion, pathGet, pathSet, pathScale,
  // Analysis
  analyzeColors, analyzeTypography, analyzeSpacing, analyzeClusters,
  // Codegen
  designToTokens, designToComponentMap,
  // Export
  exportSvg, exportPdf, exportImage,
  // Stock photos
  stockPhoto,
  // Variables
  createVariable, bindVariable, readVariables,
  // ...
]

// registry.ts — 统一导出
export const ALL_TOOLS: ToolDef[] = [...CORE_TOOLS, ...EXTENDED_TOOLS]
```

### 2B: 分级策略

| 级别 | 工具数 | Schema Tokens | 使用场景 | 何时提供 |
|:---|:---:|:---:|---|---|
| **Core** | ~30 | ~3K | 90%+ sessions | 每次 AI 请求默认提供 |
| **Extended** | ~80 | ~8K | 特定操作 | AI 显式请求或特定 context 注入 |
| **All** | ~110 | ~11K | MCP/CLI | 非 AI 消费者全量提供 |

**核心原则**：Core 工具集是"AI 最可能用的"，不是"所有基础工具"。选择标准：
1. 此工具在最近的 100 次 AI 会话中出现过 > 5 次 → Core
2. 此工具是实现用户意图的必经之路 → Core
3. 其余 → Extended

### 2C: 按领域组织文件

```
tools/
├── schema.ts              # ToolDef + defineTool + helpers
├── registry-core.ts       # CORE_TOOLS
├── registry-extended.ts   # EXTENDED_TOOLS
├── registry.ts            # ALL_TOOLS = [...CORE, ...EXTENDED]
├── ai-adapter.ts          # toolsToAI()
├── read/                  # 读取类工具
│   ├── nodes.ts           # getNode, findNodes
│   ├── selection.ts       # getSelection
│   └── query.ts           # queryNodes (XPath)
├── create/                # 创建类工具
│   ├── basic.ts           # createShape
│   ├── components.ts      # createComponent
│   └── render.ts          # render
├── modify/                # 修改类工具
│   ├── paint.ts           # setFill, setStroke
│   ├── layout.ts          # setLayout
│   ├── text.ts            # setText, setFont
│   └── geometry.ts        # setRotation, setOpacity
├── analyze/               # 分析类工具
│   ├── colors.ts
│   ├── typography.ts
│   └── clusters.ts
├── structure/             # 结构类工具
│   ├── basic.ts           # deleteNode, reparentNode
│   └── hierarchy.ts       # groupNodes, arrangeNodes
├── vector/                # 矢量工具
│   ├── boolean.ts
│   └── path.ts
└── codegen/               # 代码生成工具
    ├── tokens.ts
    └── component-map.ts
```

---

## Phase 3: Adapter Layer — 工具消费

### 3A: AI SDK 适配器 (toolsToAI)

将 `ToolDef[]` 转换为 Vercel AI SDK 的 `ToolSet`：

```typescript
function toolsToAI(
  tools: ToolDef[],
  options: AIAdapterOptions,
  deps: { v: typeof valibot; valibotSchema: typeof createValibotSchema; tool: typeof createTool }
): ToolSet {
  const result: ToolSet = {}
  for (const def of tools) {
    const shape: Record<string, unknown> = {}
    for (const [key, param] of Object.entries(def.params)) {
      shape[key] = paramToValibot(v, param)  // ParamDef → valibot schema
    }
    result[def.name] = tool({
      description: def.description,
      inputSchema: valibotSchema(v.object(shape)),
      execute: async (args) => {
        // 包裹生命周期：before snapshot → execute → after snapshot → log
        const figma = options.getFigma()
        options.onBeforeExecute?.(def)
        try {
          const result = await def.execute(figma, args)
          options.onToolLog?.({ ... })  // 记录执行日志
          return result
        } finally {
          await options.onAfterExecute?.(def)
        }
      }
    })
  }
  return result
}
```

### 3B: AIAdapterOptions — 生命周期钩子

```typescript
interface AIAdapterOptions {
  getFigma: () => DomainAPI                    // 领域 API 工厂
  onBeforeExecute?: (def: ToolDef) => void     // 执行前（UI 反馈）
  onAfterExecute?: (def: ToolDef) => void      // 执行后（刷新视图）
  onFlashNodes?: (nodeIds: string[]) => void   // 高亮受影响的节点
  onToolLog?: (entry: ToolLogEntry) => void    // 记录执行日志
  getStepBudget?: () => StepBudget             // 步数预算
}
```

**设计要点**：
- 通过回调注入 UI 行为，适配器本身不依赖 UI 框架
- `getStepBudget` 是函数而非值——因为步数在执行期间会变化
- `onFlashNodes` 提供即时视觉反馈（"AI 改了这三个按钮"）

### 3B-1: 步数预算

```typescript
interface StepBudget {
  current: number   // 当前已用步数
  max: number       // 最大步数
}

// 当剩余步数 ≤ 5 时，工具返回值上附加警告
const STEP_WARNING_THRESHOLD = 5

function appendStepWarning(result: unknown, budget: StepBudget): unknown {
  const remaining = budget.max - budget.current
  if (remaining > STEP_WARNING_THRESHOLD) return result
  return { ...result, _warning: `⚠ ${remaining} steps remaining. Wrap up.` }
}
```

**为什么需要步数预算**：
- 防止 Agent 在单个任务上无限循环（"再调一下" → "还是不对" → "再调"）
- AI 收到 `_warning` 后会调整行为——停止 polish、给出最终结果
- 用户可随时 "continue" 追加步数

### 3C: 执行日志 (ToolLogEntry)

每次工具调用自动记录结构化的执行日志：

```typescript
interface ToolLogEntry {
  tool: string
  args: Record<string, unknown>
  result: unknown
  error?: string
  timestamp: number
  durationMs: number
  mutates: boolean
  nodeBefore?: Record<string, unknown>    // 修改前快照
  nodeAfter?: Record<string, unknown>     // 修改后快照
  unchangedProps?: string[]                // 声称修改了但实际未变的属性
  isDuplicate?: boolean                    // 是否与之前的调用完全相同
}
```

**聚合分析** (`buildDebugLog`):
- **duplicates**: 检测完全相同的 tool+args 重复调用（Agent 陷入循环的信号）
- **noopMutations**: 工具声称成功但节点属性未变（工具执行逻辑有问题）
- **totalResultBytes**: 粗略的 token 消耗估算

---

## 反例（禁止）

- ❌ 工具定义和 AI 适配混在一起 — Schema 层必须独立于消费层
- ❌ 工具返回值不结构化 — AI 需要 `{ id, name, type }` 而非裸字符串
- ❌ 工具执行直接修改全局状态 — 必须通过注入的 DomainAPI 操作
- ❌ 所有工具放一个 Core 注册表 — Core 超过 30 个时 AI 的 tool choice 准确率下降
- ❌ 参数类型用 `object` 或 `any` — AI 无法理解嵌套结构的 schema
- ❌ 工具名不用 snake_case — `setFont` 不是 `setFont` 或 `SetFont`
- ❌ 没有步数预算 — Agent 可能在一个任务上消耗 50+ 次工具调用
- ❌ 忽略执行日志 — 没有日志就无法发现 Agent 的浪费行为

## 与现有技能的关系

| 技能 | 关系 | 使用场景 |
|------|:---:|---|
| `github-absorb` | 来源 | 本技能通过 github-absorb 从 open-pencil 仓库吸收 |
| `cross-project-adaptation` | downstream | 将此工具架构迁移到不同业务域（仓储/采购/咨询）时使用 |
| `skill-evaluator` | downstream | 评估生成的新工具集质量时使用 |

## 迁移清单

将三层架构应用到你的 Agent 项目时：

- [ ] 定义 DomainAPI 接口（你的 Agent 操作的领域对象）
- [ ] 编写 `ParamDef` / `ToolDef` / `defineTool` 基类
- [ ] 列出核心操作 → 映射为 Core 工具（≤ 30 个）
- [ ] 列出扩展操作 → Extended 工具
- [ ] 实现 `toolsToAI` 适配器（或 MCP/CLI 适配器）
- [ ] 设计 AIAdapterOptions（生命周期钩子）
- [ ] 实现 ToolLogEntry + buildDebugLog
- [ ] 添加步数预算
- [ ] 编写至少 3 个工具的单元测试（验证 execute + schema 正确性）

---

> 吸收自: https://github.com/open-pencil/open-pencil (MIT License)
> 源文件: packages/core/src/tools/schema.ts, registry-core.ts, registry-extended.ts, ai-adapter.ts
