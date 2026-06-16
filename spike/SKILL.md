---
name: spike
description: "Throwaway experiments to validate an idea before build."
version: 1.0.0
author: Hermes Agent (adapted from gsd-build/get-shit-done)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [spike, prototype, experiment, feasibility, throwaway, exploration, research, planning, mvp, proof-of-concept]
    related_skills: [sketch, writing-plans, subagent-driven-development, plan]
---

# Spike

## 触发条件

### 通用领域触发矩阵

快速验证实验覆盖7大领域，21个子场景。

| 领域 | 场景 | 触发信号 | 示例 |
|------|------|---------|------|
| **AI/ML** | 模型推理测试 | 用户想在真实环境测试模型效果 | "spike一下这个embedding模型在我们的数据上效果怎么样" |
| AI/ML | Agent框架 | 用户想快速验证Agent框架可行性 | "试试CrewAI能不能处理我们的workflow" |
| AI/ML | Fine-tuning | 用户想测试微调方案的可行性 | "quick prototype一下LoRA在我们数据上的效果" |
| **Web/后端** | 新框架评估 | 用户想在用框架前先试试 | "before I commit to FastAPI, spike一个小接口" |
| Web/后端 | 性能对比 | 用户想对比两个方案的性能 | "compare Redis vs Dragonfly for our use case" |
| Web/后端 | 数据库选型 | 用户想测试数据库方案 | "spike PostgreSQL vs TimescaleDB for time-series" |
| **前端** | 组件方案 | 用户想测试组件库可行性 | "试试用Shadcn UI做我们的dashboard" |
| 前端 | 状态管理 | 用户想对比状态管理方案 | "spike Zustand vs Jotai for our form state" |
| 前端 | 动画/交互 | 用户想验证复杂交互可行性 | "is this animation even possible with Framer Motion" |
| **数据工程** | 数据处理方案 | 用户想测试ETL工具 | "试试用DuckDB代替Spark做我们这步计算" |
| 数据工程 | 流处理 | 用户想验证流式方案 | "spike一下Kafka Streams能不能处理我们的延迟要求" |
| 数据工程 | 可视化方案 | 用户想测试图表库 | "quick prototype用Observable Plot做我们的dashboard" |
| **基础设施** | 部署方案 | 用户想测试部署策略 | "spike用Fly.io部署我们的Next.js app" |
| 基础设施 | 容器化 | 用户想测试容器方案 | "try Docker Compose vs Podman for our stack" |
| 基础设施 | 监控配置 | 用户想测试监控方案 | "spike Prometheus + Grafana for our metrics pipeline" |
| **安全** | 认证方案 | 用户想测试auth方案 | "spike Clerk vs Auth0 for our multi-tenant app" |
| 安全 | 加密库 | 用户想对比加密实现 | "compare rust-crypto vs ring for our TLS termination" |
| 安全 | 渗透测试 | 用户想快速测试漏洞 | "quick test: is this endpoint vulnerable to SQL injection" |
| **移动** | 跨平台方案 | 用户想测试跨平台框架 | "spike React Native vs Flutter for our real-time chat" |
| 移动 | 推送方案 | 用户想测试推送服务 | "try OneSignal vs Firebase for push reliability" |
| 移动 | 离线方案 | 用户想测试离线存储 | "spike SQLite vs WatermelonDB for offline-first" |

### 手动触发
- "spike this out"
- "quick prototype"
- "试试看能不能work"
- "let me try this"
- "is this even possible?"
- "compare A vs B quickly"
- "quick test"
- "验证一下可行性"

Use this skill when the user wants to **feel out an idea** before committing to a real build — validating feasibility, comparing approaches, or surfacing unknowns that no amount of research will answer. Spikes are disposable by design. Throw them away once they've paid their debt.

Load this when the user says things like "let me try this", "I want to see if X works", "spike this out", "before I commit to Y", "quick prototype of Z", "is this even possible?", or "compare A vs B".

## When NOT to use this

- The answer is knowable from docs or reading code — just do research, don't build
- The work is production path — use `writing-plans` / `plan` instead
- The idea is already validated — jump straight to implementation

## If the user has the full GSD system installed

If `gsd-spike` shows up as a sibling skill (installed via `npx get-shit-done-cc --hermes`), prefer **`gsd-spike`** when the user wants the full GSD workflow: persistent `.planning/spikes/` state, MANIFEST tracking across sessions, Given/When/Then verdict format, and commit patterns that integrate with the rest of GSD. This skill is the lightweight standalone version for users who don't have (or don't want) the full system.

## Core method

Regardless of scale, every spike follows this loop:

```
decompose  →  research  →  build  →  verdict
   ↑__________________________________________↓
                  iterate on findings
```

### 1. Decompose

Break the user's idea into **2-5 independent feasibility questions**. Each question is one spike. Present them as a table with Given/When/Then framing:

| # | Spike | Validates (Given/When/Then) | Risk |
|---|-------|----------------------------|------|
| 001 | websocket-streaming | Given a WS connection, when LLM streams tokens, then client receives chunks < 100ms | High |
| 002a | pdf-parse-pdfjs | Given a multi-page PDF, when parsed with pdfjs, then structured text is extractable | Medium |
| 002b | pdf-parse-camelot | Given a multi-page PDF, when parsed with camelot, then structured text is extractable | Medium |

**Spike types:**
- **standard** — one approach answering one question
- **comparison** — same question, different approaches (shared number, letter suffix `a`/`b`/`c`)

**Good spike questions:** specific feasibility with observable output.
**Bad spike questions:** too broad, no observable output, or just "read the docs about X".

**Order by risk.** The spike most likely to kill the idea runs first. No point prototyping the easy parts if the hard part doesn't work.

**Skip decomposition** only if the user already knows exactly what they want to spike and says so. Then take their idea as a single spike.

### 2. Align (for multi-spike ideas)

Present the spike table. Ask: "Build all in this order, or adjust?" Let the user drop, reorder, or re-frame before you write any code.

### 3. Research (per spike, before building)

Spikes are not research-free — you research enough to pick the right approach, then you build. Per spike:

1. **Brief it.** 2-3 sentences: what this spike is, why it matters, key risk.
2. **Surface competing approaches** if there's real choice:

   | Approach | Tool/Library | Pros | Cons | Status |
   |----------|-------------|------|------|--------|
   | ... | ... | ... | ... | maintained / abandoned / beta |

3. **Pick one.** State why. If 2+ are credible, build quick variants within the spike.
4. **Skip research** for pure logic with no external dependencies.

Use Hermes tools for the research step:

- `web_search("python websocket streaming libraries 2025")` — find candidates
- `web_extract(urls=["https://websockets.readthedocs.io/..."])` — read the actual docs (returns markdown)
- `terminal("pip show websockets | grep Version")` — check what's installed in the project's venv

For libraries without docs pages, clone and read their `README.md` / `examples/` via `read_file`. Context7 MCP (if the user has it configured) is also a good source — `mcp_*_resolve-library-id` then `mcp_*_query-docs`.

### 4. Build

One directory per spike. Keep it standalone.

```
spikes/
├── 001-websocket-streaming/
│   ├── README.md
│   └── main.py
├── 002a-pdf-parse-pdfjs/
│   ├── README.md
│   └── parse.js
└── 002b-pdf-parse-camelot/
    ├── README.md
    └── parse.py
```

**Bias toward something the user can interact with.** Spikes fail when the only output is a log line that says "it works." The user wants to *feel* the spike working. Default choices, in order of preference:

1. A runnable CLI that takes input and prints observable output
2. A minimal HTML page that demonstrates the behavior
3. A small web server with one endpoint
4. A unit test that exercises the question with recognizable assertions

**Depth over speed.** Never declare "it works" after one happy-path run. Test edge cases. Follow surprising findings. The verdict is only trustworthy when the investigation was honest.

**Avoid** unless the spike specifically requires it: complex package management, build tools/bundlers, Docker, env files, config systems. Hardcode everything — it's a spike.

**Building one spike** — a typical tool sequence:

```
terminal("mkdir -p spikes/001-websocket-streaming")
write_file("spikes/001-websocket-streaming/README.md", "# 001: websocket-streaming\n\n...")
write_file("spikes/001-websocket-streaming/main.py", "...")
terminal("cd spikes/001-websocket-streaming && python3 main.py")
# Observe output, iterate.
```

**Parallel comparison spikes (002a / 002b) — delegate.** When two approaches can run in parallel and both need real engineering (not 10-line prototypes), fan out with `delegate_task`:

```
delegate_task(tasks=[
    {"goal": "Build 002a-pdf-parse-pdfjs: ...", "toolsets": ["terminal", "file", "web"]},
    {"goal": "Build 002b-pdf-parse-camelot: ...", "toolsets": ["terminal", "file", "web"]},
])
```

Each subagent returns its own verdict; you write the head-to-head.

### 5. Verdict

Each spike's `README.md` closes with:

```markdown
## Verdict: VALIDATED | PARTIAL | INVALIDATED

### What worked
- ...

### What didn't
- ...

### Surprises
- ...

### Recommendation for the real build
- ...
```

**VALIDATED** = the core question was answered yes, with evidence.
**PARTIAL** = it works under constraints X, Y, Z — document them.
**INVALIDATED** = doesn't work, for this reason. This is a successful spike.

## Comparison spikes

When two approaches answer the same question (002a / 002b), build them **back to back**, then do a head-to-head comparison at the end:

```markdown
## Head-to-head: pdfjs vs camelot

| Dimension | pdfjs (002a) | camelot (002b) |
|-----------|--------------|----------------|
| Extraction quality | 9/10 structured | 7/10 table-only |
| Setup complexity | npm install, 1 line | pip + ghostscript |
| Perf on 100-page PDF | 3s | 18s |
| Handles rotated text | no | yes |

**Winner:** pdfjs for our use case. Camelot if we need table-first extraction later.
```

## Frontier mode (picking what to spike next)

If spikes already exist and the user says "what should I spike next?", walk the existing directories and look for:

- **Integration risks** — two validated spikes that touch the same resource but were tested independently
- **Data handoffs** — spike A's output was assumed compatible with spike B's input; never proven
- **Gaps in the vision** — capabilities assumed but unproven
- **Alternative approaches** — different angles for PARTIAL or INVALIDATED spikes

Propose 2-4 candidates as Given/When/Then. Let the user pick.

## Output

- Create `spikes/` (or `.planning/spikes/` if the user is using GSD conventions) in the repo root
- One dir per spike: `NNN-descriptive-name/`
- `README.md` per spike captures question, approach, results, verdict
- Keep the code throwaway — a spike that takes 2 days to "clean up for production" was a bad spike

## Pitfalls

1. **Declaring victory after one happy-path run.** Spikes fail when you only test the easy case. Follow surprising findings. An honest verdict requires testing edge cases.
2. **Over-engineering a throwaway.** A spike that takes 2 days to "clean up for production" was a bad spike. Hardcode everything.
3. **Patch stacking in the spike file.** If you iterate on the spike HTML/JS across multiple patch calls, check for duplicate `const VAR` declarations — same failure mode as production HTML SPA development. See `html-spa-development` skill for the surgical cleanup recipe.
4. **Research-free spikes.** Spikes are not research-free — research enough to pick the right approach, then build. Spikes that take the first library without surveying alternatives often produce misleading verdicts.

## Attribution

Adapted from the GSD (Get Shit Done) project's `/gsd-spike` workflow — MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)). The full GSD system offers persistent spike state, MANIFEST tracking, and integration with a broader spec-driven development pipeline; install with `npx get-shit-done-cc --hermes --global`.
