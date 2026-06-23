---
name: codebase-inspection
description: "Inspect codebases w/ pygount: LOC, languages, ratios."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [LOC, Code Analysis, pygount, Codebase, Metrics, Repository]
    related_skills: [github-repo-management]
prerequisites:
  commands: [pygount]
---

# Codebase Inspection with pygount

Analyze repositories for lines of code, language breakdown, file counts, and code-vs-comment ratios using `pygount`.

## When to Use

- User asks for LOC (lines of code) count
- User wants a language breakdown of a repo
- User asks about codebase size or composition
- User wants code-vs-comment ratios
- General "how big is this repo" questions
- User asks to evaluate an external AI agent skill repository for Hermes adaptation ("评估一下", "能不能吸收", "borrow from", "should I install this skill repo")
- Cross-platform skill repo comparison and overlap analysis

## Prerequisites

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

## 1. Basic Summary (Most Common)

Get a full language breakdown with file counts, code lines, and comment lines:

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**IMPORTANT:** Always use `--folders-to-skip` to exclude dependency/build directories, otherwise pygount will crawl them and take a very long time or hang.

## 2. Common Folder Exclusions

Adjust based on the project type:

```bash
# Python projects
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript projects
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# General catch-all
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. Filter by Specific Language

```bash
# Only count Python files
pygount --suffix=py --format=summary .

# Only count Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. Detailed File-by-File Output

```bash
# Default format shows per-file breakdown
pygount --folders-to-skip=".git,node_modules,venv" .

# Sort by code lines (pipe through sort)
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. Output Formats

```bash
# Summary table (default recommendation)
pygount --format=summary .

# JSON output for programmatic use
pygount --format=json .

# Pipe-friendly: Language, file count, code, docs, empty, string
pygount --format=summary . 2>/dev/null
```

## 6. Interpreting Results

The summary table columns:
- **Language** — detected programming language
- **Files** — number of files of that language
- **Code** — lines of actual code (executable/declarative)
- **Comment** — lines that are comments or documentation
- **%** — percentage of total

Special pseudo-languages:
- `__empty__` — empty files
- `__binary__` — binary files (images, compiled, etc.)
- `__generated__` — auto-generated files (detected heuristically)
- `__duplicate__` — files with identical content
- `__unknown__` — unrecognized file types

## 7. Deep Architecture Analysis (Full Codebase Deep-Dive)

When the user asks for a comprehensive architectural analysis (not just LOC counts), use this multi-phase approach. Reference: `references/deep-analysis-pattern.md`

**Phase 1 — Discovery**: use `search_files` with `pattern=*` and `target=files` to get the full file tree. Count lines per language:

```bash
find . -path './.git' -prune -o -name '*.py' -print | while read f; do wc -l "$f"; done | awk '{s+=$1} END {print "Python:", s}'
```

Repeat for each relevant extension (.sh, .yaml, .yml, .md, Dockerfile, .conf, .service, .j2, .json, etc.). Also get the directory tree with:

```bash
find . -path './.git' -prune -o -type d -print | sort
```

**Phase 2 — Read Documentation Layer**: Read README.md, SPEC.md, PLANNING.md, IMPLEMENTATION.md, SYNTHESIS.md, and any architecture docs first. These give high-level intent before diving into code.

**Phase 3 — Read Architecture Core**: Read entry points (main.py, hub.py, gateway.py), then domain/module __init__.py files, then key handlers/engines, then adapters/bridges, then config/deployment files. Order matters: start from the top and work down.

**Phase 4 — Synthesize**: Produce a structured report covering:
- Code metrics (per-language line counts, percentages)
- Architecture overview (cloud/edge split, event flow, component relationships)
- Directory tree with annotations
- Full tech stack
- Component responsibilities (per module, with line counts)
- Communication protocols and data flow
- Design patterns used (with locations)
- Differences from related projects (if applicable)
- Missing pieces (tests, CI, docs, etc.)

## Parallel Subagent Decomposition (Performance Optimization)

For large repos (50+ files), parallelize Phases 1-3 using `delegate_task` with 3 simultaneous subagents:

**Round 1 — Static Analysis (parallel)**:
1. **Codebase mapper**: AST-parse all .py files, extract classes/functions/imports, check syntax, find duplicates, map import graph
2. **Docs/test auditor**: read all test files + docs, check coverage gaps, version consistency, TODO/FIXME/HACK comments
3. **API surface mapper**: read entry points + routers + CLI, map all endpoints/tools/commands, check implementations vs stubs

**Round 2 — Dynamic Testing (parallel, after Round 1)**:
1. **Unit test runner**: run all test files individually + via pytest, count assertions pass/fail, identify fixture issues
2. **Live integration tester**: curl all production endpoints, check status codes, response bodies, timing, WebSocket upgrade
3. **Component tester**: import+instantiate key modules, run CLI commands, test detectors/bridges

**Final**: Synthesize all 6 reports into a single comprehensive report with scoring.

**Speedup**: ~2-3x faster than sequential analysis. Each subagent writes its report to `/tmp/`, then the orchestrator reads all reports and compiles the final output.

**When to use**: User asks for "comprehensive audit", "full testing", "validate everything", or "check all capabilities". NOT for simple LOC counts or single-module analysis.

## 8. Systematic Repository Testing (Full Audit)

When the user asks for "comprehensive testing", "full audit", "validate all functionality", or "test everything", follow this phased methodology. Reference: `references/testing-methodology.md`

### Phase 1 — Run Existing Tests First

```bash
cd /path/to/repo
# Install deps
pip install -e ".[dev,test]" 2>/dev/null || pip install -r requirements.txt pytest

# Run with verbose output
python -m pytest tests/ -v --tb=long 2>&1 | head -200
```

Capture: which files pytest collects, which pass/fail, fixture errors, collection errors.

### Phase 2 — Inspect Actual API Signatures BEFORE Writing Tests

**CRITICAL**: Never assume API names. Always inspect first:

```python
import inspect
from some_module import SomeClass

# Constructor
print(inspect.signature(SomeClass.__init__))

# All public methods with signatures
for name in sorted(dir(SomeClass)):
    if not name.startswith('_'):
        attr = getattr(SomeClass, name)
        if callable(attr):
            print(f"  {name}{inspect.signature(attr)}")
        elif isinstance(attr, property):
            print(f"  {name} [property]")
```

### Phase 3 — Write and Run Unit Tests Iteratively

Use `execute_code` (not delegate_task) for test execution — subagents timeout at 600s on test-heavy tasks.

Pattern:
1. Write test assumptions based on Phase 2 signatures
2. Run with `execute_code`
3. Fix failures by re-inspecting signatures
4. Repeat until stable pass rate

### Phase 4 — Scenario and Boundary Tests

After unit tests stabilize, test:
- Full lifecycle flows (create→use→complete)
- State machine transitions (valid + invalid)
- Concurrent access (threading)
- Edge cases (empty data, unicode, long strings, XSS)

### Phase 5 — Generate Report

Structure: Executive Summary → Existing Tests Analysis → Unit Results → Scenario Results → Boundary Results → Issues → Recommendations

### Version Consistency Check

Always check for version mismatches across:
- `VERSION` / `*_VERSION` files
- `pyproject.toml` / `setup.py` / `package.json`
- `MANIFEST.json` / `CHANGELOG.md`
- `__init__.py` / `__version__` variables

### Duplicate File Detection

Check if top-level files duplicate package-internal files (common legacy pattern):

```bash
# Find files that exist both at root and inside packages
for f in *.py; do
  find . -path "./$f" -prune -o -name "$f" -print 2>/dev/null | grep -q . && echo "DUPLICATE: $f"
done
```

## 9. Portability & Borrowing Evaluation (Assess External Repos)

When the user asks "can we port X?" or "should we borrow from X?", extend the deep analysis with:

### Evaluation Matrix

Rate each dimension: 🟢 Low difficulty / 🟡 Medium / 🔴 High

| Dimension | Assess |
|-----------|--------|
| Language migration | Same language vs rewrite required, LOC count |
| Dependency decoupling | How tightly coupled to its host platform |
| Platform/WASM dependencies | Native binaries, browser-specific APIs |
| Protocol compatibility | Does it use standards we already support (MCP, REST, gRPC) |
| Architecture mapping | How well do its concepts map to our system |

### Borrowing Strategy

When full port is impractical (🔴 on 2+ dimensions), identify **individually portable modules**:
1. Read type definitions (`types.ts`, `models.py`, interfaces) — these define the conceptual vocabulary
2. For each module, rate: ⭐ value to our system × 🟢 extraction difficulty
3. Prioritize: high-value + low-extraction-cost first
4. Note Python/TypeScript equivalents for any native dependencies (e.g., `hnswlib` for HNSW, `faiss` for vector search)

### Output Template

```markdown
## Portability Assessment: [Repo Name]

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Language | 🟢/🟡/🔴 | ... |
| Dependencies | 🟢/🟡/🔴 | ... |
| Platform | 🟢/🟡/🔴 | ... |
| Protocol | 🟢/🟡/🔴 | ... |
| Architecture | 🟢/🟡/🔴 | ... |

**Verdict**: Port ✅ / Borrow selectively ❌ port / Not viable ❌

### Borrowable Modules (priority-ordered)
1. [Module] — Value ⭐⭐⭐⭐⭐ / Difficulty 🟢 / Path: ...
2. ...
```

### Pitfall

Don't confuse "the code exists in a different language" with "it's hard to borrow." The **ideas** (type definitions, algorithms, trust formulas, topology patterns) are language-agnostic and often the most valuable part. Code is implementation; architecture is knowledge.

## 10. Agent Skill Repository Evaluation

When the user asks to evaluate an external AI agent skill repository
(e.g., a GitHub repo of Claude Code / Codex / Cursor / OpenClaw skills) for
Hermes adaptation — phrases like "评估一下对你是否有帮助", "evaluate this skill
repo", "能不能吸收", or "should I install this" — load and follow the full
methodology in `references/skill-repo-evaluation.md`.

The methodology covers:

| Phase | Purpose |
|-------|---------|
| Structural Reconnaissance | Clone, count skills, read docs, identify runtime deps |
| Overlap Analysis | Per-skill matrix: full/partial/none overlap with Hermes |
| Concept Absorption Rating | ⭐1-5 value of design ideas independent of code |
| Five-Category Positioning | 独立应用 / 基础设施 / 吸收思想 / 已有重复 / 存在冲突 |
| Adaptation Difficulty | 🟢 Low / 🟡 Medium / 🔴 High |
| Decision Matrix | Per-skill table + prioritized action plan |

Key principle: **absorb design systems and workflow patterns, not execution
scripts.** The SKILL.md knowledge layer is portable; the TypeScript/Bun/Chrome
CDP execution layer is tightly coupled to the source platform.

## Pitfalls

1. **Always exclude .git, node_modules, venv** — without `--folders-to-skip`, pygount will crawl everything and may take minutes or hang on large dependency trees.
2. **Markdown shows 0 code lines** — pygount classifies all Markdown content as comments, not code. This is expected behavior.
3. **JSON files show low code counts** — pygount may count JSON lines conservatively. For accurate JSON line counts, use `wc -l` directly.
4. **Large monorepos** — for very large repos, consider using `--suffix` to target specific languages rather than scanning everything.
5. **pytest fixture lookup on parameters** — if a function `test_handler(event)` exists, pytest interprets `event` as a fixture request. Rename to `_test_handler` or add `@pytest.fixture`. This blocks the ENTIRE file from being collected.
6. **Don't assume API names** — class constructors and method signatures vary wildly between projects. Always `inspect.signature()` before writing tests. In this session, ~50% of initial API assumptions were wrong (e.g., `data` vs `payload`, `assigned_edge` vs `assigned_to`, `name` vs `node_name`).
7. **Subagents timeout on test-heavy work** — `delegate_task` with 3 parallel test tasks all hit 600s timeout. Use `execute_code` directly for running tests — it's faster and doesn't timeout.
8. **Stats/dict key naming inconsistency** — many engines use different naming conventions for stats keys (`total_hashes` vs `deduplicated`, `total_dead` vs `total`, `registered_nodes` vs `total_nodes`). Always check actual keys before asserting.
9. **Script count is noise in skill repos** — a skill with 5,000 lines of TypeScript orchestration code may have less transferable value than a skill with 200 lines of SKILL.md containing a novel design taxonomy. When evaluating external AI agent skill repos for Hermes, focus on the knowledge layer (SKILL.md design systems, workflow patterns, prompt templates), not the execution layer (scripts, SDK wrappers, CDP automation).
10. **Version number drift ≠ feature gap** — upstream skill repos often have rapid version bumps (1.117.x) from independent per-skill release cycles. An adapted Hermes skill at 1.56.x may have the same design system — compare content, not version numbers.
