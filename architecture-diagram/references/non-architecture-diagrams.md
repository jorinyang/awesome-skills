# Beyond Architecture: Flowcharts, Sequence, and Structural Diagrams

Extend the Architecture Diagram skill's dark-themed SVG design system to cover additional diagram types. All types share the same color palette, typography (JetBrains Mono), and background grid — ensuring visual consistency across a documentation set.

Based on patterns from [baoyu-diagram](https://github.com/JimLiu/baoyu-skills#baoyu-diagram) (MIT).

---

## When to Use This Reference

Load this when the user requests a diagram type not covered by the core architecture-diagram skill:

| User Says | Diagram Type | Section |
|-----------|-------------|---------|
| "flowchart", "decision tree", "process", "workflow" | Flowchart | §1 |
| "sequence diagram", "UML sequence", "protocol flow", "handshake" | Sequence | §2 |
| "class diagram", "UML class", "ER diagram", "entity relationship", "org chart" | Structural | §3 |
| "mind map", "brainstorming", "topic exploration" | Mind Map | §4 |
| "timeline", "chronology", "history" | Timeline | §5 |
| "state machine", "state diagram", "lifecycle" | State Machine | §6 |
| "data flow", "DFD", "pipeline" | Data Flow | §7 |

---

## §1 Flowchart

### Shape Vocabulary

| Shape | Meaning | SVG |
|-------|---------|-----|
| Rounded rect (rx=25) | Start / End | `<rect rx="25">` |
| Rectangle (rx=6) | Process / Action | `<rect rx="6">` |
| Diamond | Decision | `<polygon points="CX,CY-35 CX+50,CY CX,CY+35 CX-50,CY">` |
| Parallelogram | Input / Output | `<polygon>` with skew(N) |
| Cylinder | Data store | Ellipse + rect pair |

### Flow Direction

Primary: **top to bottom**. Branch flows go right (or left).

### Layout Algorithm

1. Identify the **main path** (happy path) — runs straight down center
2. **Branch from decisions**: "Yes" continues down, "No" branches right
3. **Merge paths**: L-shaped connectors back to main path
4. **Loop-backs**: Route upward on far left/right with curved paths

### Spacing

- Step vertical gap: 60–80px
- Decision diamond: 70px height, 100px width (point-to-point)
- Branch offset: 200px from center
- Connector clearance: 20px from any box

### Decision Labels

Place "Yes"/"No" (or "是"/"否") directly on exit arrows, 10px from diamond edge:

```svg
<!-- Yes: downward -->
<line x1="CX" y1="CY+35" x2="CX" y2="CY+95" stroke="#64748b" marker-end="url(#arrow)"/>
<text x="CX+12" y="CY+60" fill="#34d399" font-size="8">Yes</text>

<!-- No: rightward -->
<line x1="CX+50" y1="CY" x2="CX+150" y2="CY" stroke="#64748b" marker-end="url(#arrow)"/>
<text x="CX+80" y="CY-7" fill="#fb7185" font-size="8">No</text>
```

### Coloring

| Element | Color |
|---------|-------|
| Start/End | Highlight (blue) |
| Process | Primary (cyan) or Secondary (emerald) |
| Decision | Accent (amber) |
| Error paths | Alert (rose), dashed arrows |
| Happy path arrows | Slightly brighter (`stroke-opacity="1"` vs `0.7`) |

### Complex Flowcharts (10+ steps)

Group into swim lanes (vertical columns with header bars), using the region boundary pattern.

---

## §2 Sequence Diagram

### Core Elements

| Element | Visual | Description |
|---------|--------|-------------|
| Actor box | Rect at top + dashed vertical lifeline | Each entity |
| Sync message | Solid arrow → | Request/call |
| Async message | Open arrowhead → | Fire-and-forget |
| Return message | Dashed arrow ← | Response |
| Activation bar | Narrow rect (10px) on lifeline | Entity is processing |
| Self-message | Arrow looping back | Internal call |
| Note | Rounded rect + folded corner | Annotation |
| Alt/Opt frame | Dashed boundary + label tab | Conditional block |
| Loop frame | Dashed boundary + "loop" tab | Repetition |

### Layout Algorithm

1. Place actors horizontally, 150–200px apart
2. Draw lifelines as vertical dashed lines downward
3. Place messages top-to-bottom in time order
4. Vertical gap between messages: 40–50px
5. Activation bars: 10px wide, centered on lifeline

### Actor Box

```svg
<rect x="X" y="20" width="130" height="45" rx="6" fill="#0f172a"/>
<rect x="X" y="20" width="130" height="45" rx="6" fill="rgba(8,51,68,0.4)" stroke="#22d3ee" stroke-width="1.5"/>
<text x="CX" y="47" fill="white" font-size="11" font-weight="600" text-anchor="middle">Actor</text>
<!-- Lifeline -->
<line x1="CX" y1="65" x2="CX" y2="BOTTOM" stroke="#334155" stroke-width="1" stroke-dasharray="6,4"/>
```

### Message Arrows

```svg
<!-- Sync (solid) -->
<line x1="FX" y1="Y" x2="TX" y2="Y" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arrow)"/>
<text x="MID" y="Y-8" fill="#e2e8f0" font-size="9" text-anchor="middle">methodCall()</text>

<!-- Return (dashed, reversed) -->
<line x1="TX" y1="Y" x2="FX" y2="Y" stroke="#64748b" stroke-width="1" stroke-dasharray="6,3" marker-end="url(#arrow)"/>
<text x="MID" y="Y-8" fill="#94a3b8" font-size="8" text-anchor="middle" font-style="italic">response</text>

<!-- Self-message -->
<path d="M CX,Y L CX+40,Y L CX+40,Y+25 L CX,Y+25" fill="none" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arrow)"/>
<text x="CX+45" y="Y+15" fill="#e2e8f0" font-size="8">process()</text>
```

### Activation Bar

```svg
<rect x="CX-5" y="START" width="10" height="H" rx="2" fill="rgba(8,51,68,0.6)" stroke="#22d3ee" stroke-width="1"/>
```

### Alt/Loop Frames

```svg
<!-- Frame -->
<rect x="X" y="Y" width="W" height="H" rx="4" fill="none" stroke="#64748b" stroke-width="1" stroke-dasharray="4,3"/>
<!-- Label tab -->
<rect x="X" y="Y" width="50" height="18" rx="4" fill="rgba(30,41,59,0.8)" stroke="#64748b" stroke-width="1"/>
<text x="X+25" y="Y+13" fill="#94a3b8" font-size="8" font-weight="600" text-anchor="middle">alt</text>
<text x="X+60" y="Y+13" fill="#94a3b8" font-size="8" font-style="italic">[condition]</text>
<!-- Else divider -->
<line x1="X" y1="MID" x2="X+W" y2="MID" stroke="#64748b" stroke-width="1" stroke-dasharray="4,3"/>
```

### Numbering (8+ messages)

```svg
<circle cx="FX-15" cy="Y" r="8" fill="rgba(59,130,246,0.3)" stroke="#60a5fa" stroke-width="1"/>
<text x="FX-15" y="Y+3" fill="#60a5fa" font-size="7" font-weight="600" text-anchor="middle">1</text>
```

### Color Assignment

Give each actor a distinct color. Use for: actor box stroke, activation bar, outgoing arrows.

---

## §3 Structural Diagrams

Covers: class diagrams, ER diagrams, org charts.

### §3.1 Class Diagram

#### Class Box (3-Compartment)

```svg
<g transform="translate(X, Y)">
  <rect width="180" height="120" rx="6" fill="#0f172a"/>
  <rect width="180" height="120" rx="6" fill="rgba(8,51,68,0.4)" stroke="#22d3ee" stroke-width="1.5"/>
  <!-- Name -->
  <text x="90" y="24" fill="white" font-size="11" font-weight="700" text-anchor="middle">ClassName</text>
  <line x1="0" y1="35" x2="180" y2="35" stroke="#22d3ee" stroke-width="0.5" stroke-opacity="0.5"/>
  <!-- Attributes -->
  <text x="10" y="52" fill="#94a3b8" font-size="8">- id: int</text>
  <text x="10" y="64" fill="#94a3b8" font-size="8">- name: string</text>
  <line x1="0" y1="75" x2="180" y2="75" stroke="#22d3ee" stroke-width="0.5" stroke-opacity="0.5"/>
  <!-- Methods -->
  <text x="10" y="92" fill="#94a3b8" font-size="8">+ getName(): string</text>
</g>
```

Abstract classes: italicize name. Interfaces: `«interface»` above name in smaller font.

#### Relationship Lines

| Relationship | Style | End Marker |
|-------------|-------|-----------|
| Inheritance | Solid | Empty triangle (▷) → parent |
| Implementation | Dashed | Empty triangle → interface |
| Composition | Solid | Filled diamond (◆) at owner |
| Aggregation | Solid | Empty diamond (◇) at owner |
| Dependency | Dashed | Open arrowhead → target |
| Association | Solid | Open arrowhead or none |

**Inheritance marker:**
```svg
<marker id="inherit" markerWidth="12" markerHeight="10" refX="12" refY="5" orient="auto">
  <polygon points="0 0, 12 5, 0 10" fill="#0f172a" stroke="#94a3b8" stroke-width="1.5"/>
</marker>
```

**Composition diamond:**
```svg
<marker id="composition" markerWidth="12" markerHeight="8" refX="0" refY="4" orient="auto">
  <polygon points="0 4, 6 0, 12 4, 6 8" fill="#94a3b8"/>
</marker>
```

**Aggregation diamond:**
```svg
<marker id="aggregation" markerWidth="12" markerHeight="8" refX="0" refY="4" orient="auto">
  <polygon points="0 4, 6 0, 12 4, 6 8" fill="#0f172a" stroke="#94a3b8" stroke-width="1.5"/>
</marker>
```

#### Cardinality

Place at each end, offset 5–8px from box edge:
```svg
<text x="X" y="Y" fill="#94a3b8" font-size="8">1..*</text>
```

### §3.2 ER Diagram

- 2-compartment boxes (entity name + attributes)
- `PK` prefix + bold for primary keys
- `FK` prefix for foreign keys
- Crow's foot notation for relationships:

```svg
<!-- One end -->
<line x1="X" y1="Y" x2="X+15" y2="Y" stroke="#94a3b8" stroke-width="1.5"/>
<!-- Many end (crow's foot) -->
<line x1="X-15" y1="Y-6" x2="X" y2="Y" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="X-15" y1="Y+6" x2="X" y2="Y" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="X-15" y1="Y" x2="X" y2="Y" stroke="#94a3b8" stroke-width="1.5"/>
```

### §3.3 Org Chart

- Top-down tree layout, root at top center
- Each level: 100–120px vertical gap
- Siblings evenly distributed horizontally
- Connection: vertical from parent bottom → horizontal bar → vertical to children
- Use color to distinguish departments/levels

---

## §4 Mind Map

- Central node: large rounded rect (120×60px), highlight color, centered
- Branches radiate outward with curved Bezier paths
- Child nodes: smaller rounded rects (rx=20)
- Color-code branches: each major branch a different palette color
- Font: 11px bold for central, 9px for children, 8px for grandchildren
- Organic layout: children spread ±45° from parent direction

---

## §5 Timeline

- Horizontal axis with tick marks, or vertical with event markers
- Event nodes: small circles (r=6) or rounded rects
- Period spans: semi-transparent rects spanning date ranges
- Axis line: solid, 2px, color #475569
- Date labels: 8px, #94a3b8, below (horizontal) or left (vertical) of axis
- Event descriptions: 9px, white, offset from axis

---

## §6 State Machine

- State nodes: rounded rects (rx=12)
- Initial state: filled circle (r=8)
- Final state: double circle (outer r=10, inner r=6, fill)
- Transitions: directed arrows with event labels
- Use semantic coloring: active=highlight, error=alert, normal=primary
- Guard conditions: `[condition]` on transition label

---

## §7 Data Flow Diagram (DFD)

- Process bubbles: circles or rounded rects, primary/emerald colors
- External entities: rects with neutral (slate) color
- Data stores: parallel horizontal lines or cylinder shapes
- Data flows: labeled arrows connecting processes
- Numbering: label each process (e.g., "1.0", "2.1") for hierarchy

---

## Shared Color Assignment

All types use the same semantic palette from the architecture-diagram design system:

| Role | Color |
|------|-------|
| Primary (frontend) | cyan `#22d3ee` |
| Secondary (backend) | emerald `#34d399` |
| Tertiary (database) | violet `#a78bfa` |
| Accent (cloud/infra) | amber `#fbbf24` |
| Alert (security) | rose `#fb7185` |
| Connector (bus) | orange `#fb923c` |
| Neutral (external) | slate `#94a3b8` |
| Highlight (active) | blue `#60a5fa` |

## Pitfalls

1. **Same double-rect masking** applies: draw opaque `#0f172a` bg rect first, then styled rect on top
2. **Arrow markers** must be defined in `<defs>` before use
3. **viewBox sizing**: calculate generously, then trim after layout is confirmed
4. **Text labels on paths**: for diagonal arrows, place text at midpoint with appropriate offset
5. **Don't use read_file→write_file for SVG edits**: use native Python `open()` or terminal `grep`/`sed`
