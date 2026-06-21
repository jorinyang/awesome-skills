# Known Skill Ecosystems: Research Paper Writing

> Domain notes on the ML research paper writing skill landscape. Compiled from a full evaluation of the `research-paper-writing` skill.

## Upstream Source

**Orchestra-Research/AI-Research-SKILLs** (GitHub)
- Maintains `research-paper-writing` (v1.1.0, MIT) — the canonical version in the Hermes skills library
- The skill supersedes the older `ml-paper-writing` skill by the same org
- Installed via `agentskills.io` ecosystem
- 57 open issues, active maintenance but no public members
- NPX distributable: `npx @orchestra-research/ai-research-skills`

## Skill Profile

| Dimension | Detail |
|-----------|--------|
| **Size** | SKILL.md: 2,377 lines / 103KB |
| **Support files** | 50+ files: 6 conference LaTeX templates (NeurIPS/ICML/ICLR/ACL/AAAI/COLM) + 9 reference docs |
| **Phases** | 0: Setup → 1: Lit Review → 2: Experiment Design → 3: Execution & Monitoring → 4: Analysis → 5: Drafting → 6: Self-Review → 7: Submission → 8: Post-Acceptance |
| **Dependencies** | semanticscholar, arxiv, habanero, requests, scipy, numpy, matplotlib, SciencePlots |
| **Hermes integration** | Native — uses `terminal`, `process`, `execute_code`, `cronjob`, `delegate_task`, `todo`, `memory`, `clarify`, `send_message` |

## Writing Philosophy Sources

The skill synthesizes methodology from top ML researchers:
- **Neel Nanda** (Google DeepMind): The Narrative Principle, What/Why/So What
- **Sebastian Farquhar** (DeepMind): 5-sentence abstract formula
- **Gopen & Swan**: 7 principles of reader expectations
- **Zachary Lipton**: Word choice, eliminating hedging
- **Jacob Steinhardt** (UC Berkeley): Precision, consistent terminology
- **Ethan Perez** (Anthropic): Micro-level clarity tips

## Community Forks

| Fork | Commits | Target Audience | Link |
|------|---------|-----------------|------|
| **Master-cai/Research-Paper-Writing-Skills** | 4 | ML/CV/NLP researchers, based on 彭思达's notes | github.com/Master-cai/Research-Paper-Writing-Skills |
| **Norman-bury/research-writing-skill** | 11 | Undergraduates/grad students, multi-platform (Claude Code/Codex/Cursor/OpenCode) | github.com/Norman-bury/research-writing-skill |
| **Ar9av/PaperOrchestra** | 35 | Google PaperOrchestra implementation as pluggable skill pack | github.com/Ar9av/PaperOrchestra |

## Business Relevance Assessment

**For 贵州之客 (outdoor travel company): zero relevance.** The skill targets ML conference paper writing (NeurIPS/ICML/ICLR/ACL/AAAI/COLM). Every phase — experiment design, model training, LaTeX compilation, conference submission — is orthogonal to travel operations.

**The skill is retained as a dormant asset** in the library. It serves no business function but costs nothing to keep.

## Evaluation Anti-Pattern

When evaluating a skill of this size (~100KB+), `skill_view()` will truncate the output (107,729 char limit). The truncation marker is subtle — a `[Truncated: ...]` note at the end of the returned content. Always fall back to `read_file` with chunked offsets to read the complete SKILL.md.
