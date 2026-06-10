---
name: architecture-diagram
description: "Dark-themed SVG architecture/cloud/infra diagrams as HTML."
version: 1.0.0
author: Cocoon AI (hello@cocoon-ai.com), ported by Hermes Agent
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [architecture, diagrams, SVG, HTML, visualization, infrastructure, cloud]
    related_skills: [concept-diagrams, excalidraw]
---

# Architecture Diagram Skill

Generate professional, dark-themed technical architecture diagrams as standalone HTML files with inline SVG graphics. No external tools, no API keys, no rendering libraries — just write the HTML file and open it in a browser.

## ⚠️ CRITICAL: Style Priority — Match Content, Not Template

When the user provides BOTH a reference template AND content:
1. If the content document has its own established visual style (colors, fonts, layout), **match the content document's style**, NOT the reference template's style.
2. The template is for **structural inspiration** (two-column, SVG inline, card summaries) — not for blind visual cloning.
3. The user chose the content document's style for a reason; overriding it with this skill's dark-tech default will result in corrections.

**Decision tree:**
- Tech/infra subject + no content style → use dark theme (JetBrains Mono, `#020617` bg)
- Chinese business/industry subject → use light theme (PingFang SC, `#FAFBFD` bg, see below)
- Content doc has explicit CSS → extract its color palette and typography, use those

## Scope

**Best suited for:**
- Software system architecture (frontend / backend / database layers)
- Cloud infrastructure (VPC, regions, subnets, managed services)
- Microservice / service-mesh topology
- Database + API map, deployment diagrams
- Anything with a tech-infra subject that fits a dark, grid-backed aesthetic

**Alternative — Chinese Corporate Light Variant:**
For Chinese business architecture / maturity model / transformation roadmap diagrams where the user wants a white background with Chinese fonts, blue labels, and red emphasis (common in 企业架构图 / 业务全景图 / 成熟度模型), see `references/chinese-corporate-light.md`. Load it with `skill_view(name="architecture-diagram", file_path="references/chinese-corporate-light.md")`.

**Look elsewhere first for:**
**Look elsewhere first for:**
- Physics, chemistry, math, biology, or other scientific subjects
- Physical objects (vehicles, hardware, anatomy, cross-sections)
- Floor plans, narrative journeys, educational / textbook-style visuals
- Hand-drawn whiteboard sketches (consider `excalidraw`)
- Animated explainers (consider an animation skill)

If a more specialized skill is available for the subject, prefer that. If none fits, this skill can also serve as a general SVG diagram fallback — choose dark or light theme based on context.

Based on [Cocoon AI's architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) (MIT).

## Workflow

1. User describes their system architecture (components, connections, technologies)
2. Generate the HTML file following the design system below
3. Save with `write_file` to a `.html` file (e.g. `~/architecture-diagram.html`)
4. User opens in any browser — works offline, no dependencies

### Output Location

Save diagrams to a user-specified path, or default to the current working directory:
```
./[project-name]-architecture.html
```

### Preview

After saving, suggest the user open it:
```bash
# macOS
open ./my-architecture.html
# Linux
xdg-open ./my-architecture.html
```

## Design System & Visual Language

### Color Palette (Semantic Mapping)

Use specific `rgba` fills and hex strokes to categorize components:

| Component Type | Fill (rgba) | Stroke (Hex) |
| :--- | :--- | :--- |
| **Frontend** | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (cyan-400) |
| **Backend** | `rgba(6, 78, 59, 0.4)` | `#34d399` (emerald-400) |
| **Database** | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (violet-400) |
| **AWS/Cloud** | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (amber-400) |
| **Security** | `rgba(136, 19, 55, 0.4)` | `#fb7185` (rose-400) |
| **Message Bus** | `rgba(251, 146, 60, 0.3)` | `#fb923c` (orange-400) |
| **External** | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (slate-400) |

### Typography & Background
- **Font:** JetBrains Mono (Monospace), loaded from Google Fonts
- **Sizes:** 12px (Names), 9px (Sublabels), 8px (Annotations), 7px (Tiny labels)
- **Background:** Slate-950 (`#020617`) with a subtle 40px grid pattern

```svg
<!-- Background Grid Pattern -->
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
</pattern>
```

## Technical Implementation Details

### Component Rendering
Components are rounded rectangles (`rx="6"`) with 1.5px strokes. To prevent arrows from showing through semi-transparent fills, use a **double-rect masking technique**:
1. Draw an opaque background rect (`#0f172a`)
2. Draw the semi-transparent styled rect on top

### Connection Rules
- **Z-Order:** Draw arrows *early* in the SVG (after the grid) so they render behind component boxes
- **Arrowheads:** Defined via SVG markers
- **Security Flows:** Use dashed lines in rose color (`#fb7185`)
- **Boundaries:**
  - *Security Groups:* Dashed (`4,4`), rose color
  - *Regions:* Large dashed (`8,4`), amber color, `rx="12"`

### Spacing & Layout Logic
- **Standard Height:** 60px (Services); 80-120px (Large components)
- **Vertical Gap:** Minimum 40px between components
- **Message Buses:** Must be placed *in the gap* between services, not overlapping them
- **Legend Placement:** **CRITICAL.** Must be placed outside all boundary boxes. Calculate the lowest Y-coordinate of all boundaries and place the legend at least 20px below it.

## Document Structure

The generated HTML file follows a four-part layout:
1. **Header:** Title with a pulsing dot indicator and subtitle
2. **Main SVG:** The diagram contained within a rounded border card
3. **Summary Cards:** A grid of three cards below the diagram for high-level details
4. **Footer:** Minimal metadata

### Info Card Pattern
```html
<div class="card">
  <div class="card-header">
    <div class="card-dot cyan"></div>
    <h3>Title</h3>
  </div>
  <ul>
    <li>• Item one</li>
    <li>• Item two</li>
  </ul>
</div>
```

## Output Requirements
- **Single File:** One self-contained `.html` file
- **No External Dependencies:** All CSS and SVG must be inline (except Google Fonts)
- **No JavaScript:** Use pure CSS for any animations (like pulsing dots)
- **Legend**: horizontal flex row below the SVG, not inside it

### 16:9 Full-Page Requirement (applies to both themes)
When the user requests 16:9, the ENTIRE page must be 16:9 — not just SVG viewBox. Move ALL content (summary cards, legend, footer) inside `<svg viewBox="0 0 1920 1080">`. CSS: `html,body{width:100%;height:100%;overflow:hidden} svg{width:100vw;height:100vh}`. No HTML outside the SVG.

> See `references/chinese-business-diagram.md` for: progressive font enlargement, content fusion, grid cell centering, layout compression, enterprise pills sizing, cell height multipliers, centered vs horizontal layout preference, version management (V1/V2/V3).

Load the quick-reference palette:
```
skill_view(name="architecture-diagram", file_path="references/chinese-business-palette.md")
```

## Alternative: Chinese Enterprise Light Theme

When the user asks for "白底黑字", "蓝字标注，红字强调", or explicitly wants a Chinese business diagram rather than dark tech aesthetic, load the light-theme variant:

```
skill_view(name="architecture-diagram", file_path="references/chinese-enterprise-light-theme.md")
```

This variant uses white backgrounds, PingFang SC fonts, blue annotations (#3B5BDB), red emphasis (#DC2626), and is optimized for 16:9 enterprise business architecture diagrams.

## Alternative: Engineering Blueprint Theme

When the user asks for "工程蓝图风格" or wants a dark navy/grid-based professional look with white/cyan lines and corner measurement ticks:

```
skill_view(name="architecture-diagram", file_path="references/engineering-blueprint-theme.md")
```

This variant uses deep navy backgrounds (#0A1628), 40+160px grid patterns, cyan/white high-contrast text, and corner tick marks for an authentic engineering drawing aesthetic. See the reference for full color palette, tag/stage colors adapted for dark backgrounds, and cell background patterns.

Load the full HTML template for the exact structure, CSS, and SVG component examples:

```
skill_view(name="architecture-diagram", file_path="templates/template.html")
```

The template contains working examples of every component type (frontend, backend, database, cloud, security), arrow styles (standard, dashed, curved), security groups, region boundaries, and the legend — use it as your structural reference when generating diagrams.

## Light Theme Variant: Chinese Business / Industry Context

For Chinese business architecture diagrams (industry maps, maturity models, transformation roadmaps, capability matrices), override the dark-tech defaults:

### Color System
| Role | Color | Usage |
|------|-------|-------|
| Background | `#FAFBFD` (page), `#FFFFFF` (cards) | Clean white |
| Text (primary) | `#0F172A` | Body, headings |
| Text (secondary) | `#475569` | Descriptions |
| Text (muted) | `#64748B` / `#94A3B8` | Metadata, hints |
| **Blue annotation** | `#1F3A8A` / `#3B5BDB` / `#1D4ED8` | Labels, key actions ▸, stage L1, CTAs |
| **Red emphasis** | `#DC2626` / `#B91C1C` | ⚠ Risks, warnings, deadlines, key metrics |
| Green (positive) | `#15803D` / `#10B981` | Business value, growth, success metrics |
| Amber (leadership) | `#92400E` (#FFFDF5 bg) | Boss/leader action items |
| Purple (advanced) | `#4F46E5` / `#7C3AED` | L2 stage, advanced capabilities |
| Cyan (cutting-edge) | `#0E7490` / `#06B6D4` | L3 stage, AI-native, future state |

### Typography
- **Font:** `"PingFang SC", "HarmonyOS Sans SC", "Source Han Sans SC", "Microsoft YaHei", sans-serif`
- **Sizes:** 13px headings, 10-11px body, 9px labels, 8px tags

### Stage/Cell Borders
- Each stage column gets a **colored top border** (2-2.5px) matching its stage color
- Cells within a stage use a lighter version of that stage color for borders
- Tag pills: rounded rects with light fill + matching border

### Key Patterns
- **Continuous rows** (maturity, value): full-width band with gradient track + dots
- **Risk rows**: `#FFF5F5` background with red-tinted cells
- **Boss/leader rows**: `#FFFDF5` amber background, diamond ◆ prefix
- **Legend**: horizontal flex row below the SVG, not inside it

### 16:9 Full-Page Requirement (applies to both themes)
When the user requests 16:9, the ENTIRE page must be 16:9 — not just SVG viewBox. Move ALL content (summary cards, legend, footer) inside `<svg viewBox="0 0 1920 1080">`. CSS: `html,body{width:100%;height:100%;overflow:hidden} svg{width:100vw;height:100vh}`. No HTML outside the SVG.

> See `references/chinese-business-diagram.md` for: progressive font enlargement, content fusion, grid cell centering, layout compression, enterprise pills sizing, cell height multipliers, centered vs horizontal layout preference, version management (V1/V2/V3).
