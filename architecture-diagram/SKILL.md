---
name: architecture-diagram
description: "Dark-themed SVG architecture/cloud/infra diagrams as HTML."
version: 1.1.0
author: Cocoon AI (hello@cocoon-ai.com), ported by Hermes Agent
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [architecture, diagrams, SVG, HTML, visualization, infrastructure, cloud]
    related_skills: [drawio-generation, fireworks-tech-graph]
---

# Architecture Diagram Skill

Generate professional, dark-themed technical architecture diagrams as standalone HTML files with inline SVG graphics. No external tools, no API keys, no rendering libraries — just write the HTML file and open it in a browser.

## 触发条件

### 通用领域触发矩阵

架构图覆盖7大领域，25个子场景。

| 领域 | 场景 | 触发信号 | 示例 |
|------|------|---------|------|
| **AI/ML** | RAG架构图 | 用户需要RAG系统架构图 | "画一个RAG pipeline的架构图" |
| AI/ML | Agent系统图 | 用户需要Multi-Agent拓扑图 | "画这个Agent系统的架构图" |
| AI/ML | 模型服务架构 | 用户需要推理服务架构图 | "画LLM serving的架构图" |
| **Web/后端** | 微服务架构 | 用户需要微服务拓扑图 | "画这个微服务系统的架构图" |
| Web/后端 | API网关架构 | 用户需要API网关图 | "画API gateway的架构" |
| Web/后端 | 数据库架构 | 用户需要数据库拓扑图 | "画主从读写分离的架构" |
| Web/后端 | 事件驱动架构 | 用户需要消息系统架构图 | "画event-driven架构的消息流" |
| **前端** | 前端架构 | 用户需要前端技术栈图 | "画前端monorepo的架构" |
| 前端 | SSR/CSR架构 | 用户需要渲染策略图 | "画SSR hydration的架构" |
| 前端 | 组件系统 | 用户需要组件依赖图 | "画design system的依赖关系" |
| **云/基础设施** | VPC网络 | 用户需要云网络拓扑图 | "画AWS VPC的子网和路由" |
| 云/基础设施 | K8s集群 | 用户需要K8s架构图 | "画k8s集群的node/pod/service" |
| 云/基础设施 | CI/CD Pipeline | 用户需要CI/CD流程图 | "画CI/CD pipeline的stages" |
| 云/基础设施 | 灾备架构 | 用户需要DR架构图 | "画multi-region failover" |
| **数据工程** | 数据管道 | 用户需要ETL架构图 | "画data pipeline的数据流" |
| 数据工程 | 数据湖/仓 | 用户需要数据平台架构图 | "画lakehouse的分层架构" |
| 数据工程 | 实时流处理 | 用户需要流处理拓扑图 | "画Kafka Streams的topology" |
| **安全** | 安全架构 | 用户需要安全边界图 | "画零信任安全架构的信任域" |
| 安全 | 认证流程 | 用户需要OAuth/SSO流程图 | "画OAuth2的授权流程" |
| 安全 | 网络分段 | 用户需要网络隔离图 | "画DMZ/内网/管理网的分段" |
| **产品/商业** | 业务架构 | 用户需要业务系统架构图 | "画业务中台的系统架构" |
| 产品/商业 | 用户流程 | 用户需要用户旅程图 | "画用户注册→下单→支付的流程" |
| 产品/商业 | 技术方案 | 用户需要技术方案图 | "画这个技术方案的整体架构" |
| 产品/商业 | 决策流 | 用户需要决策流程图 | "画这个审批流程的决策树" |
| 产品/商业 | 对比架构 | 用户需要对比两个架构方案 | "画现架构vs目标架构的对比" |

### 手动触发
- "画架构图"
- "architecture diagram"
- "系统架构图"
- "画一个XX的图"
- "流程图"
- "拓扑图"
- "deployment diagram"

## Scope

**Best suited for:**
- Software system architecture (frontend / backend / database layers)
- Cloud infrastructure (VPC, regions, subnets, managed services)
- Microservice / service-mesh topology
- Database + API map, deployment diagrams
- **Flowcharts** — decision logic, process steps, workflows
- **Sequence diagrams** — time-ordered interactions, protocol handshakes
- **Structural diagrams** — class diagrams, ER diagrams, org charts, component diagrams
- **Mind maps, timelines, state machines, data flow diagrams**
- Anything with a tech-infra subject that fits a dark, grid-backed aesthetic

**For non-architecture diagram types**, load `references/non-architecture-diagrams.md` — it extends this skill's design system with shape vocabularies, layout algorithms, and SVG patterns for flowcharts, sequence diagrams, structural diagrams, mind maps, timelines, state machines, and data flow diagrams. All types share the same color palette, typography, and background grid.

**Look elsewhere first for:**
- Physics, chemistry, math, biology, or other scientific subjects
- Physical objects (vehicles, hardware, anatomy, cross-sections)
- Floor plans, narrative journeys, educational / textbook-style visuals
- Hand-drawn whiteboard sketches (consider `excalidraw`)
- Animated explainers (consider an animation skill)

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

### ⚠️ Pitfall: hermes read_file corrupts HTML/SVG files

**NEVER use `read_file` → `write_file` for HTML/SVG editing.** Hermes' `read_file` tool injects `LINE_NUM|` prefixes into the returned content. When that content is then passed to `write_file`, the line numbers become embedded in the output file, corrupting the HTML/SVG.

**Fix pattern:**
- Use native Python `open()` with `encoding="utf-8"` for reading/writing HTML
- Write a `.py` fix script with `write_file`, then execute via `terminal("python3 /tmp/fix.py")`
- Use `terminal` with `grep`/`sed` for simple targeted replacements
- Use `execute_code` to run Python that uses native `open()` for complex modifications

**Recovery**: If corrupted, restore from git: `git checkout -- path/to/file.html`.

### ⚠️ Pitfall: Unicode em dash in SVG comments

SVG comments in ClawShell diagrams use Unicode em dashes `─` (U+2500), not ASCII hyphens. Example: `<!-- ── Cloud: Services ── -->`. String replacements like `.replace('<!-- Cloud: Services -->', ...)` **silently fail** because the dashes don't match.

**Fix**: Use `re.search()` for pattern-based insertion:
```python
import re
match = re.search(r'<!--[^>]*Cloud: Services[^>]*-->', html)
pos = match.start()
html = html[:pos] + new_section + html[pos:]
```

### ⚠️ Pitfall: Y-coordinate shift must be systematic

When inserting new sections and shifting downstream content:
1. Shift the container rect (y=)
2. Shift the header text (y=)
3. Shift EVERY child rect (y=)
4. Shift EVERY child text label (y=)
5. Shift the bottom description text (y=)
6. Expand region background rect heights
7. Expand viewBox

**Test pattern**: Use a loop for batch shifts:
```python
for old_y, new_y in [('y="645"','y="790"'), ('y="667"','y="812"'), ...]:
    html = html.replace(old_y, new_y)
```

### ⚠️ Pitfall: terminal tool blocks heredoc

`terminal("python3 << 'EOF' ...")` is blocked by the security filter. Write scripts to temp files instead:
```bash
write_file("/tmp/_fix.py", script)
terminal("python3 /tmp/_fix.py", timeout=10)
```

When a diagram contains multiple regions (e.g., Cloud Hub + Edge Brain side-by-side) with bottom sections (persistence, external services, principles) spanning both, it's easy for the bottom layers to overlap the lower content of the regions above.

**The user will catch this** — they explicitly flagged "持久层覆盖到了其他信息" and requested a fresh diagram. Fix pattern:

1. **Calculate all Y boundaries before writing.** Sum the total height of each region's content. The bottom layer must start below the DEEPER of the two region bottoms.
2. **Increase viewBox height** to accommodate all sections. Start generous (1350px) then compress after verifying no overlaps.
3. **Extend region background boxes** to match the chosen height.
4. **Do NOT sed-patch complex SVGs.** If the user reports layout issues, regenerate the entire SVG with corrected coordinates. Sed-based fixes to SVG coordinates are fragile (miss nested elements, text labels, sub-rectangles). Use Python re.sub for simple global shifts, or rewrite the SVG from scratch for structural changes.
5. **Verify** by checking no bottom-layer elements share Y ranges with region content.

### Compact Vertical Stack Pattern

When the user asks for persistence/external sections to be placed "directly below" the main regions and principles+legend to be side-by-side, use this proven Y layout:

```
y=60-640:  Cloud Hub (left x=20-720) + Edge Brain (right x=755-1480)
           Data Flow arrows in the center gap (x=720-755), vertical
y=645-745: Persistence Layer (full width, 100px)
y=750-820: External Services (full width, 70px)
y=830-905: Design Philosophy (left 1080px) + Legend (right 360px)
           These two sections are side-by-side on the same row
viewBox:   1500 x 980  (or adjust after verifying)
```

This pattern avoids the common mistake of placing persistence/principles far below with large gaps, which the user will flag as wasted space. Every section should be tightly stacked with minimal gaps (5-15px between sections).

### Side-by-side Row Alignment

When aligning two sections horizontally (e.g., Principles + Legend):
- Calculate total width needed: left_section_width + right_section_width = ~1460px (viewBox - 40px margins)
- Use the same Y and height for both rects
- Legend should be compact (360px wide) showing only essential color mappings
- Principles text should be concise (2-3 lines max), not a full paragraph

### Middle-Gap Data Flow Pattern

When placing bidirectional data flow arrows in the gap between two side-by-side regions (e.g., Cloud Hub ↔ Edge Brain):

**Borderless by default.** The data flow section should NOT have a background rect or border — just the vertical label text and arrows. The user will explicitly ask to remove the border if you add one.

**Even distribution.** Calculate arrow positions mathematically:
```python
# 12 arrows (6 Cloud→Edge + 6 Edge→Cloud), 35px step
step = 35
base = 135  # start Y after DATA FLOW label
for i in range(6):
    cloud_y = base + (i * step * 2)      # right-pointing arrows
    edge_y  = base + step + (i * step * 2)  # left-pointing arrows
```

**Interleaved directions.** Cloud→Edge (right) and Edge→Cloud (left) arrows must alternate. Never group all right arrows together then all left arrows — the user will notice uneven visual density.

**Arrows per row:**
| Y | Cloud→Edge (right) | Edge→Cloud (left) |
|---|---------------------|-------------------|
| ~135 | REST | — |
| ~170 | — | Health |
| ~205 | WSS | — |
| ~240 | — | Events |
| ~275 | Tasks | — |
| ~310 | — | Register |
| … | (continue interleaved) | … |

**Label positioning:** Right-arrow labels go at `x=arrow_x - 2, y=arrow_y - 5, text-anchor=end`. Left-arrow labels go at `x=arrow_x + 2, y=arrow_y - 2, text-anchor=start`.

### Section Height Matching

When two sections appear at the same vertical position in different regions (e.g., Cloud Deployment at y=570 and Edge Adapters at y=564), match their heights for visual alignment. The user will notice and flag height mismatches. Use the taller height for both.

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
- **Compatibility:** Must render correctly in any modern web browser

## References

- `references/architecture-diagram-pitfalls.md` — Layout conventions, common mistakes, font sizing, arrow spacing, GitHub rendering issues
- `templates/template.html` — Full HTML template with CSS, SVG, and working examples of every component type
