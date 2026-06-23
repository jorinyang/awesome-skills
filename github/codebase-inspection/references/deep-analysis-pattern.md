# Deep Codebase Architecture Analysis Pattern

Repeatable multi-phase workflow for comprehensive repository architecture analysis.

## Phase 1 — Discovery

Goal: Full file inventory + per-language line counts.

1. **Full file list**: `search_files(pattern=*, target=files, limit=200, offset=0)` — paginate until no more results.
2. **Per-language line counts**: Use `find ... -print | while read f; do wc -l "$f"; done | awk` — one invocation per extension type. This is more reliable than piping through xargs which has argument-length limits.
   - Extensions to check: `.py`, `.sh`, `.yaml/.yml`, `.md`, `.json`, `Dockerfile`, `.conf`, `.service`, `.j2`, `.example`, `.crt`, `.key`, `.txt`
3. **Directory tree**: `find . -path './.git' -prune -o -type d -print | sort`
4. **Top-level structure**: Read `.gitignore` and any `.editorconfig`/`pyproject.toml`/`package.json` to understand build system.

## Phase 2 — Read Documentation Layer

Read ALL top-level docs before touching source code:

1. `README.md` — project overview, architecture diagram, quick start, phase progress
2. `SPEC.md` — interface specs, data models, protocol definitions, port mappings
3. `PLANNING.md` — architecture philosophy, design principles, directory structure plan
4. `IMPLEMENTATION.md` — phased implementation tasks, dependency graph
5. `SYNTHESIS.md` — fusion/synthesis docs if merging multiple projects
6. Any `ARCHITECTURE.md` or `DESIGN.md`

These reveal the INTENT before the implementation, making code reading much faster.

## Phase 3 — Read Architecture Core (Top-Down Order)

**Order matters**: start at the outermost entry point and trace inward.

1. **Cloud entry point** (e.g., `cloud-hub/src/hub.py`) — the main class, its components, message types, event flow
2. **Edge entry point** (e.g., `gateway.py`) — main class, sub-module initialization, lifecycle
3. **Domain `__init__.py`** — reveals all domain handlers and exported symbols
4. **Key domains** (newest/most important first) — genome, adaptive, swarm, workflow
5. **EventStore `__init__.py`** — reveals storage layer modules
6. **EventBus core** (edge side) — pub/sub, schema, DLQ
7. **Adapters/Managers** — adapter manager, platform detectors, IDE bridges
8. **Config files** — config.yaml, requirements.txt, cloud.json templates
9. **Deployment layer** — Dockerfile, docker-compose.yml, nginx.conf, Ansible playbooks
10. **CI/GitHub** — .github/ workflows or skills

## Phase 4 — Synthesize Report

Produce a structured report with these sections:

### Code Metrics
- Per-language line counts with percentages
- Total files (excluding .git)
- Total lines

### Architecture Overview
- Overall positioning (what this project actually IS, not just what it's named)
- Architecture diagram (ASCII or description)
- Directory tree with role annotations

### Tech Stack
- Language, framework, async runtime, auth, storage, containerization, orchestration, proxy, protocols, LLM providers

### Component Responsibilities
- Per-module breakdown with file paths and line counts
- For large classes (1000+ lines), note the key methods and their roles

### Communication & Data Flow
- Edge→Cloud connection flow
- Event flow (emit → persist → broadcast)
- Offline/reconnect behavior
- Hermes brain integration (if applicable)

### Design Patterns
- Pattern name, location, what it achieves
- Common ones: Event Sourcing, CQRS, Pub/Sub, Adapter, Strategy, Orchestrator, Circuit Breaker, Outbox, Saga, DLQ, Knowledge Graph

### Differences from Related Projects
- When analyzing a "port" or "fusion" project, compare with the source

### Gaps & Missing Pieces
- Tests (or lack thereof)
- CI/CD
- GUI (or lack thereof for supposedly-UI projects)
- Deployment verification status

## Pitfalls

1. **Don't skip Phase 2**: reading docs first saves hours. The code makes sense only after understanding the intent.
2. **`xargs wc -l` silently truncates**: use the `while read; do wc -l` pattern instead.
3. **Don't read files in random order**: a domain handler's code is incomprehensible without knowing what CloudHub injects into it. Read entry points first.
4. **Check if the project name is misleading**: "ClawShell-MacOS" has no macOS native code. Always verify what the actual source files contain vs. what the name suggests.
5. **Note what's NOT there**: missing tests, missing CI, placeholder configs marked "待实施" (pending implementation) are as important as what IS there.
