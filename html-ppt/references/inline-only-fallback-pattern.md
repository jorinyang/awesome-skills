# Inline-Only Fallback Pattern (Zero Dependencies)

## When to Use
Assets directory missing or user explicitly requests a single self-contained HTML file.  
Proven at 47 slides / 147KB — scales to full corporate training decks with dense textbook content.

## Architecture

```
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>...</title>
  <style>/* ALL CSS HERE */</style>
</head>
<body>
  <div id="progress"></div>          <!-- top bar -->
  <nav id="navPrev">‹</nav>          <!-- optional arrow buttons -->
  <nav id="navNext">›</nav>
  <div id="deck">
    <section class="slide active">...</section>
    <section class="slide">...</section>
    ...
  </div>
  <div id="pagenum"></div>           <!-- bottom-right -->
  <div id="overview"></div>          <!-- overview mode container -->
  <script>/* ALL JS HERE */</script>
</body>
</html>
```

## CSS Slide Engine

```css
/* Slides stack via position:absolute, only .active is visible */
.slide {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 60px 80px;
  opacity: 0; visibility: hidden;
  transition: opacity .5s ease, transform .5s ease;
  transform: translateX(40px);       /* enter from right */
}
.slide.active { opacity: 1; visibility: visible; transform: translateX(0); }
.slide.exit-left { opacity: 0; visibility: visible; transform: translateX(-40px); }

/* Background variants via modifier classes */
.slide--dark { background: #1d1d1f; color: #fff; }
.slide--gray { background: #f5f5f7; }
.slide--gradient { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
```

## Stagger Animation (CSS-only, no JS library)

```css
.stagger > * {
  opacity: 0; transform: translateY(20px);
  transition: opacity .4s ease, transform .4s ease;
}
.slide.active .stagger > *:nth-child(1) { transition-delay: .1s; }
.slide.active .stagger > *:nth-child(2) { transition-delay: .2s; }
/* ... repeat up to :nth-child(8) at .1s increments */
.slide.active .stagger > * { opacity: 1; transform: translateY(0); }
```

Each direct child of `.stagger` fades up sequentially when its slide becomes active.
Wrap all slide content in `<div class="stagger">` for automatic entrance animation.

## JS Controller (minimal)

```javascript
(function() {
  const slides = document.querySelectorAll('.slide');
  const total = slides.length;
  let current = 0, isOverview = false;

  function update() {
    slides.forEach((s, i) => {
      s.classList.remove('active', 'exit-left');
      if (i < current) s.classList.add('exit-left');
    });
    slides[current].classList.add('active');
    progress.style.width = ((current + 1) / total * 100) + '%';
    pagenum.textContent = (current + 1) + ' / ' + total;
  }

  function go(n) { if (n >= 0 && n < total) { current = n; update(); } }
  function next() { go(current + 1); }
  function prev() { go(current - 1); }

  document.addEventListener('keydown', e => {
    switch (e.key) {
      case 'ArrowRight': case 'ArrowDown': case ' ': case 'PageDown':
        e.preventDefault(); next(); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp':
        e.preventDefault(); prev(); break;
      case 'f': case 'F': /* fullscreen toggle */ break;
      case 'o': case 'O': /* overview toggle */ break;
      case 'Home': e.preventDefault(); go(0); break;
      case 'End': e.preventDefault(); go(total - 1); break;
    }
  });

  // Touch swipe
  let startX;
  deck.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
  deck.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 50) { dx < 0 ? next() : prev(); }
  }, { passive: true });

  // Click: left 30% = prev, right 70% = next
  deck.addEventListener('click', e => {
    if (e.target.closest('button,a,input,textarea,select')) return;
    (e.clientX / window.innerWidth) > 0.3 ? next() : prev();
  });

  update();
})();
```

## Component Patterns (CSS-only)

### Comparison Blocks (✅ vs ❌)
```html
<div class="compare">
  <div class="compare-side compare-good">
    <h4>✅ 能做</h4>
    <ul><li>...</li></ul>
  </div>
  <div class="compare-side compare-bad">
    <h4>❌ 不做</h4>
    <ul><li>...</li></ul>
  </div>
</div>
```
```css
.compare { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.compare-good { background: rgba(52,199,89,.08); border-left: 4px solid #34c759; }
.compare-bad  { background: rgba(255,59,48,.08);  border-left: 4px solid #ff3b30; }
```

### Flow Chart (CSS flex + arrows)
```html
<div class="flow">
  <div class="flow-step">Step 1</div>
  <div class="flow-arrow">→</div>
  <div class="flow-step">Step 2</div>
</div>
```
```css
.flow { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; justify-content: center; }
.flow-step { background: var(--blue); color: #fff; padding: 10px 20px; border-radius: 10px; }
```

### Inline Progress Bars (percentage visualization)
```html
<div style="display:flex;align-items:center;gap:16px">
  <span style="font-weight:700;min-width:80px">25%</span>
  <div style="flex:1;height:8px;background:var(--gray);border-radius:4px;overflow:hidden">
    <div style="width:25%;height:100%;background:var(--blue);border-radius:4px"></div>
  </div>
  <span>Feature Name</span>
</div>
```

### Section Tag (chapter label)
```html
<span class="section-tag">第1章 · 章节名</span>
```
```css
.section-tag {
  display: inline-block; font-size: .8rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: .1em; color: var(--blue);
  background: rgba(0,113,227,.08); padding: 4px 12px; border-radius: 6px;
}
```

### Numbered Step List
```html
<div class="card" style="display:flex;align-items:center;gap:12px">
  <span style="background:var(--blue);color:#fff;width:28px;height:28px;
    border-radius:50%;display:flex;align-items:center;justify-content:center;
    font-size:.85rem;font-weight:600;flex-shrink:0">1</span>
  <span>Step description here</span>
</div>
```

## Overview Mode (O key)

Clone each slide scaled to thumbnail size, click to navigate:

```javascript
function toggleOverview() {
  isOverview = !isOverview;
  if (isOverview) {
    overview.classList.add('show');
    slides.forEach((s, i) => {
      const thumb = document.createElement('div');
      thumb.className = 'overview-thumb' + (i === current ? ' active' : '');
      const clone = s.cloneNode(true);
      clone.style.cssText = `position:absolute;inset:0;transform:scale(0.22);
        transform-origin:top left;width:${innerWidth}px;height:${innerHeight}px;
        opacity:1;visibility:visible`;
      thumb.appendChild(clone);
      thumb.addEventListener('click', () => { go(i); toggleOverview(); });
      overview.appendChild(thumb);
    });
  } else {
    overview.classList.remove('show');
    overview.innerHTML = '';
  }
}
```

## Performance Notes

- 47 slides at 147KB total → ~3.1KB/slide average (dense textbook content with code blocks, tables, SVG)
- 38 slides at 68KB total → ~1.8KB/slide average (standard presentation content)
- No external fonts needed: `-apple-system, 'SF Pro Display', 'PingFang SC', sans-serif` covers macOS/iOS/Windows/Android
- Stagger animation uses CSS transitions (GPU-accelerated), not JS requestAnimationFrame
- Overview mode clones DOM on demand, clears on close — no persistent memory cost

## Click Zone Navigation (three-zone, safer for content-dense slides)

For slides with tables, code blocks, and inline links, split click zones into thirds to prevent accidental page turns when users click content:

```javascript
deck.addEventListener('click', e => {
  if (e.target.closest('button,a,input,textarea,select,.overview-thumb')) return;
  const x = e.clientX / window.innerWidth;
  if (x < 0.33) prev();       // left 1/3 = previous
  else if (x > 0.67) next();  // right 1/3 = next
  // middle 1/3 = no action (safe zone for content interaction)
});
```

Use this instead of the simple `x > 0.3` split when slides contain dense interactive content.

## Bottom Progress Bar with Page Number Overlay

When user requests bottom progress bar (instead of top), use a wrapper with the page number overlaid:

```html
<div id="progress-wrap">
  <div id="progress"></div>
  <div id="pagenum"></div>
</div>
```

```css
#progress-wrap {
  position: fixed; bottom: 0; left: 0; right: 0; height: 20px;
  background: rgba(0,0,0,.08); z-index: 1000;
}
#progress {
  position: absolute; bottom: 0; left: 0; height: 100%;
  background: linear-gradient(90deg, var(--blue), #5ac8fa);
  transition: width .4s cubic-bezier(.4,0,.2,1); width: 0;
  border-radius: 0 10px 10px 0;
}
#pagenum {
  position: absolute; bottom: 0; left: 0; right: 0; height: 20px;
  display: flex; align-items: center; justify-content: center;
  font-size: .72rem; color: #fff; font-weight: 600; z-index: 1001;
  text-shadow: 0 1px 2px rgba(0,0,0,.3);
  font-variant-numeric: tabular-nums; letter-spacing: .02em;
}
```

Key differences from top bar: `height: 20px` (vs 3px), page number centered inside the bar, `text-shadow` for readability over the gradient.

## SVG Architecture Diagram Pattern

For system architecture diagrams (e.g., ecosystem overviews). Two validated variants:

### Dark variant (when slide background is dark)
- Background: `#0d1117` (GitHub dark)
- Text: `#e6edf3` titles, `#8b949e` descriptions
- Blue: `#58a6ff`, Purple: `#a78bfa`

### White variant (when slide background is white)
- Background: `#ffffff` + `stroke="#e8e8ed" stroke-width="1"`
- Text: `#1d1d1f` titles, `#6e6e73` descriptions
- Blue: `#0071e3`, Purple: `#7c3aed`
- Badge text (colored badge backgrounds): keep `#ffffff`

Conversion mapping table (dark → white):

| Dark | White | Role |
|------|-------|------|
| `#0d1117` bg rect | `#ffffff` + `#e8e8ed` stroke | background |
| `#e6edf3` | `#1d1d1f` | node titles |
| `#8b949e` | `#6e6e73` | descriptions |
| `#58a6ff` | `#0071e3` | blue accents |
| `#a78bfa` | `#7c3aed` | purple accents |

**Scope limit**: Only replace colors inside the SVG block. `.code-block` uses `#e6edf3` text on dark `#1d1d1f` background — that is intentional code styling, do NOT change it.

## Slide Scrollbar Styling

When slide content overflows viewport, browser default scrollbar looks jarring on white background. Add:

```css
.slide::-webkit-scrollbar{width:6px}
.slide::-webkit-scrollbar-track{background:transparent}
.slide::-webkit-scrollbar-thumb{background:#c1c1c1;border-radius:3px}
.slide::-webkit-scrollbar-thumb:hover{background:#a8a8a8}
```

6px width, rounded light-gray thumb, transparent track, darker on hover. Scoped to `.slide` only.

## Keyboard: add Enter to next-page keys

```javascript
case 'ArrowRight': case 'ArrowDown': case ' ': case 'PageDown': case 'Enter':
  e.preventDefault(); next(); break;
```

Also add `Escape` handling: exit fullscreen if active, else exit overview.

## Dense Content Patterns (corporate training decks from textbooks)

When source material is a dense textbook (e.g., 1600-line markdown), the slide deck must match that information density — not just keywords. Use these patterns:

1. **Full-sentence cards**: Each card has a complete sentence, not just a label. Include examples, comparisons, and specific numbers.
2. **Code blocks for examples**: Use `<pre>` inside `.code-block` for verbatim textbook examples (system prompts, naming conventions, Q-A pairs, decision trees).
3. **Comparison tables**: Use `.data-table` for structured comparisons (DEAP vs 悟空， good vs bad examples, decision matrices).
4. **Callout boxes**: Use `.callout` for key insights, warnings, and company-specific examples.
5. **Max width 1200px**: Content area wider than default (800-900px) to accommodate dense layouts.
6. **Font sizes**: h2 at 2.2rem, body at 1.05rem, small at .88rem — denser than presentation defaults.
7. **Multi-column card grids**: `cols-2`, `cols-3`, `cols-4` for parallel information display.
8. **Scrollable slides**: Add `overflow-y: auto` to `.slide` for content that exceeds viewport height.

## Verification Checklist for HTML Decks

After writing the file, verify in browser before claiming completion:

1. `grep -c '<section class="slide"' file.html` — count matches expected slide count
2. `grep -c '</section>' file.html` — closing tags match opening tags
3. Open in browser → `document.querySelectorAll('.slide').length` — confirm count
4. Check `document.querySelectorAll('.slide.active').length === 1` — only one active
5. Test keyboard: `ArrowRight` → page number increments, progress bar width updates
6. Test click zones: click left 1/3 → prev, right 1/3 → next, middle → no action
7. Test F (fullscreen), O (overview), ESC (exit)
8. Visual check: take screenshot of key slides (cover, SVG diagram, dense content slide)
9. Reset to slide 1 before finishing: remove `.active` from all, add to first, update progress

## Instructor Intro Slide (inserted after cover)

Corporate training decks need an instructor credibility slide after the cover. Layout: photo left, info right.

```html
<section class="slide">
  <div class="stagger content" style="display:flex;align-items:center;justify-content:center;gap:56px;max-width:1000px;margin:0 auto">
    <div style="flex-shrink:0">
      <img src="instructor-photo.png" alt="Name" style="width:280px;height:340px;object-fit:cover;border-radius:20px;box-shadow:0 20px 60px rgba(0,0,0,.15)">
    </div>
    <div style="text-align:left;max-width:520px">
      <span class="section-tag">讲师介绍</span>
      <h2>Name（Alias）</h2>
      <p style="font-size:1.1rem;color:var(--blue);font-weight:600">Title · Specialty</p>
      <!-- Certification block -->
      <div style="margin-top:24px;display:flex;flex-direction:column;gap:16px">
        <div>
          <p style="font-size:.82rem;color:#86868b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">专业认证</p>
          <p style="font-size:.92rem;line-height:1.6">Cert 1 / Cert 2 / Cert 3</p>
        </div>
        <!-- Experience tags -->
        <div>
          <p style="font-size:.82rem;color:#86868b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">从业经验</p>
          <div style="display:flex;gap:16px;flex-wrap:wrap">
            <span style="background:#f0f7ff;color:#0071e3;padding:6px 14px;border-radius:8px;font-size:.85rem;font-weight:600">N年从业</span>
            <!-- more tags -->
          </div>
        </div>
        <!-- Industry background -->
        <div>
          <p style="font-size:.82rem;color:#86868b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">行业背景</p>
          <p style="font-size:.92rem;line-height:1.6">Industry description</p>
        </div>
      </div>
    </div>
  </div>
</section>
```

Key design decisions:
- Photo: `object-fit:cover` + `border-radius:20px` + large shadow for depth
- Info sections use small uppercase gray labels (`.82rem`, `#86868b`) as section dividers
- Experience numbers as blue pill tags (`.85rem`, `#f0f7ff` bg) — scannable
- `max-width:1000px` centers the two-column layout; `flex-shrink:0` prevents photo compression

## Textbook → PPT Rebuild Methodology

When rebuilding a slide deck from a dense source textbook (e.g., 1600-line markdown), the key is **content preservation, not summarization**. Users reject keyword-list slides when the source material has complete examples, comparisons, and specific numbers.

### Process

1. **Read the full textbook first** — identify every section that has: code examples, comparison tables, decision matrices, step-by-step procedures, specific numbers/thresholds
2. **Map sections to slides** — one major textbook section → 1-2 slides. Don't force one-to-one; some sections deserve 3 slides (e.g., a case study with setup/implementation/results)
3. **Preserve complete examples** — if the textbook has a full "good vs bad" system prompt comparison, put both verbatim on the slide in a two-column layout
4. **Keep specific numbers** — "约1000-2000个智能体" not "大量智能体"; "25%" not "一些"
5. **Add company-specific callouts** — use `.callout` blocks for company-context examples that make abstract concepts concrete

### Density targets

| Source density | Slide treatment | Example |
|---|---|---|
| Code examples (system prompts, configs) | `<pre>` block, verbatim, both good+bad versions | 角色描述设计页 |
| Comparison tables (5+ rows) | `.data-table` with alternating row colors | DEAP vs 悟空对比表 |
| Step procedures (5+ steps) | Numbered cards with full descriptions | 创建智能体5步流程 |
| Decision matrices | Full table with all scenarios | 场景决策矩阵7行 |
| Anti-patterns | ❌→✅ with reason and company example | 常见反模式5条 |

### Common failure mode

Generating "outline-style" slides with only headings and bullet points when the source has rich detail. Fix: re-read the source section, extract the **most specific** example or comparison, and put it on the slide verbatim.

## Instructor Photo Handling

When user uploads a photo for the deck:
1. Copy to project directory: `cp /path/to/upload "项目目录/讲师照片.png"`
2. Reference as relative path in HTML: `<img src="讲师照片.png">`
3. For OSS deployment: upload photo alongside HTML, use same relative path
4. Photo size: 280×340px works well for side-by-side layout; `object-fit:cover` handles aspect ratio differences

## Checklist for New Inline Decks

1. All `<section class="slide">` inside `#deck`
2. First slide has `class="slide active"`, rest have `class="slide"` only
3. Wrap each slide's content in `<div class="stagger">` for entrance animation
4. Top: `#progress` bar. Bottom-right: `#pagenum` counter
5. Test: ← → keys, F fullscreen, O overview, touch swipe, click-to-advance
6. Target: < 100KB for 40 slides
