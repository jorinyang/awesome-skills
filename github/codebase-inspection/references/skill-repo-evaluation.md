# Agent Skill Repository Evaluation Methodology

Use this when the user asks to evaluate an external AI agent skill repository
(e.g., a GitHub repo of Claude Code / Codex / Cursor skills) for Hermes
adaptation. Trigger phrases: "评估一下对你是否有帮助", "evaluate this skill
repo", "should I install this", "能不能吸收", "borrow from this skill repo".

## Core Principle

**Absorb design systems and workflow patterns, not execution scripts.**
AI agent skill repos typically bundle SKILL.md (knowledge) with platform-specific
execution scripts (TypeScript/Bun, Python, shell). The knowledge layer is
language-agnostic and portable; the execution layer is tightly coupled to the
source platform. Separate them in your analysis.

## Phase 1: Structural Reconnaissance

1. Clone the repo shallow: `git clone --depth 1 <url>`
2. Count skill directories: `ls skills/` or equivalent
3. Read README.md and CLAUDE.md (or equivalent agent config) for intent
4. Extract frontmatter from each skill's SKILL.md (name, description, version, metadata)
5. Identify runtime dependencies (Bun, Node.js, Chrome, Python, specific APIs)
6. Count LOC per language, total files, shared packages

Output: a structural summary (skill count, runtime, dependency tree, LOC).

## Phase 2: Overlap Analysis (Per-Skill Matrix)

For each skill in the external repo, compare against Hermes existing capabilities:

| Overlap Level | Criteria | Action |
|--------------|----------|--------|
| **Full overlap** | Hermes has a skill or built-in tool that covers the same function | Skip adaptation |
| **Partial overlap** | Some sub-capabilities overlap, but skill has unique dimensions | Absorb the unique parts as concepts or reference material |
| **No overlap** | No Hermes capability matches this function | Evaluate adaptation value |

Check against:
- Hermes built-in tools (image_generate, browser, terminal, clarify, etc.)
- Hermes skills (check `skills_list` for all categories)
- LLM-native capabilities (tasks the agent can do with just its language model)

## Phase 3: Concept Absorption Value Rating

Rate each skill 1-5 ⭐ for its **design ideas**, independent of code portability:

| Rating | Meaning | Example |
|--------|---------|---------|
| ⭐⭐⭐⭐⭐ | Design system with broad applicability; reusable by multiple skills | Style×Layout matrix for image generation |
| ⭐⭐⭐⭐ | Well-structured workflow with parameterized dimensions | 5D cover-image system, refined translation pipeline |
| ⭐⭐⭐ | Useful pattern but narrow scope or already partially covered | Diagram type taxonomy |
| ⭐⭐ | Minor patterns or edge-case handling | Caching strategy, site-specific parsers |
| ⭐ | No transferable ideas; pure execution glue | Platform-specific Chrome CDP scripts |

## Phase 4: Five-Category Positioning

Classify the repository into one or more of these relationships:

| Category | When | Example |
|----------|------|---------|
| **独立应用** (Standalone app) | The repo IS an application, not a library of components | ❌ Rare for skill repos |
| **基础设施/标准模版** (Infra/template) | The repo provides a framework or template system others build on | Plugin marketplace format, design system catalogs |
| **吸收思想/架构** (Absorb ideas) | The design patterns, taxonomies, and workflows are the high-value artifact | Style×Layout matrices, prompt engineering patterns |
| **已有重复能力** (Duplicate) | Hermes already covers these functions via tools or existing skills | Image generation backends, URL fetching, markdown formatting |
| **存在冲突** (Conflict) | The repo's approach conflicts with Hermes architecture | Different execution models, incompatible runtime dependencies |

A repo can span multiple categories for different parts. Be specific per skill group.

## Phase 5: Adaptation Difficulty Rating

| Rating | Criteria | Action |
|--------|----------|--------|
| 🟢 Low | Pure SKILL.md knowledge; no external scripts or APIs needed | Adapt directly as a new Hermes skill |
| 🟡 Medium | Has TypeScript scripts but the logic can be replicated via Hermes tools | Extract the design system and workflow; discard scripts |
| 🔴 High | Requires Chrome CDP, specific native binaries, platform-locked APIs, or reverse-engineered endpoints | Do not adapt; possibly absorb isolated ideas |

## Phase 6: Decision Matrix Output

Produce a per-skill table:

```
| Skill | Overlap | Adapt? | Concept Value | Difficulty | Key Absorbable Ideas |
|-------|---------|--------|---------------|------------|----------------------|
```

Followed by a **prioritized action plan**:

1. **Already adapted** (maintain)
2. **Worth adapting** (high concept value + low difficulty)
3. **Concept absorption only** (high concept value + high difficulty)
4. **Skip** (full overlap, platform-locked, or low value)

## Pitfalls

1. **Don't confuse version number drift with feature gap.** Upstream repos often
   have rapid version bumps (1.117.x) from independent per-skill release cycles.
   An adapted Hermes skill at 1.56.x may have the same design system — compare
   content, not numbers.
2. **Metadata is not functionality.** baoyu-skills uses `openclaw` metadata;
   Hermes uses `hermes` metadata. The metadata difference is cosmetic; the
   SKILL.md body is what matters.
3. **"Already covered" means functionally covered, not identically covered.**
   Hermes `browser` tool + LLM can replace a dedicated URL→Markdown Chrome CDP
   script even if the output format differs slightly.
4. **Platform-locked skills are not portable.** WeChat publishing (requires
   Chinese social media auth + Chrome CDP), WeChat summary (macOS only +
   wx-cli), Electron ASAR extraction — these have zero portability regardless
   of how well-designed the workflow is.
5. **Script count is noise.** A skill with 5,000 lines of TypeScript
   orchestration code may have less transferable value than a skill with 200
   lines of SKILL.md containing a novel design taxonomy.
