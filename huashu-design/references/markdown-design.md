# Huashu-Design for Markdown

When applying huashu-design principles to **pure Markdown documents** (READMEs, proposals, docs rendered on GitHub/Feishu), use **light integration** mode — the design paradigm transfers, the HTML tooling doesn't.

## Core Adaptation

| Huashu-Design Principle | Markdown Equivalent |
|------------------------|---------------------|
| Swiss typography grid | Strict H1→H2→H3 hierarchy, no level skipping |
| Information hierarchy | Top-down scanning layers: Hero(5s)→Claim(15s)→Depth(3min) |
| Anti-AI slop (visual) | No `<p align>` HTML, no `<table>` for layout, no `<center>` |
| Anti-AI slop (content) | No emoji as heading prefixes, no badge walls (cap at 2) |
| Visual temperature | Expressed through sentence structure, not color |
| Capacity estimation | 5 GitHub scrolls ≈ 3-5 min read |

## The 4 Questions Adapted

1. **Narrative role**: README is a mix of hero (first impression) + reference (return visits)
2. **Viewing distance**: Desktop monitor, GitHub renderer (~1m, ~1200px wide max)
3. **Visual temperature**: Clean, structured, confident. Not flashy, not cold.
4. **Capacity**: Top ~800px is the "above-fold" for GitHub. Full document: 200-250 lines.

## Anti-Slop Rules for Markdown

### Forbidden Patterns
- `<p align="center">` wrapping (use plain markdown, centered text isn't a design tool)
- `<table>` used for layout (markdown tables for data only)
- HTML `align` attributes on any element
- Badge rows longer than 2 items (badge walls are visual noise)
- Emoji-only section headings (emoji is decoration, not structure)
- More than 3 consecutive lines of badge/link decoration

### Emoji Discipline
- **Allowed**: Domain/section identifiers with semantic meaning (🏢 product, 🛠️ skill, 📋 plan)
- **Forbidden**: Pure decoration emoji (🚀✨🎯💡), emoji as heading prefixes, emoji in CTA
- Rule of thumb: if removing the emoji changes the information, keep it. Otherwise, cut it.

### Clean Markdown Patterns
```markdown
# Title (H1 only once)

**Subtitle** (bold for emphasis, not HTML)

> Blockquote for design philosophy or key insight — not for ordinary paragraphs.

## Section (H2 — no emoji prefix, no horizontal rule before it unless separating major parts)

### Sub-section (H3 — only when H2 content justifies subdivision)

| Table header | Table header |
|-------------|-------------|
| Data only    | Not layout   |
```

## Quality Baseline (DoD)

- [ ] GitHub renders without broken/misaligned HTML
- [ ] Reader understands core proposition within 30s of scanning
- [ ] No `<p align>`, `<center>`, or `<table>` layout tags
- [ ] Badge count ≤ 2
- [ ] Emoji count ≤ 10 total, each justified by semantic role
- [ ] All links resolve (no 404s)
- [ ] Line count between 200-300 (long enough to be thorough, short enough to scan)
