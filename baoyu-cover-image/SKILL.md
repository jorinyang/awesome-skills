---
name: baoyu-cover-image
description: "Article cover images: 5D dimension system (Type × Palette × Rendering × Text × Mood)."
version: 1.0.0
author: 宝玉 (JimLiu), adapted by Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cover-image, creative, image-generation, article]
    category: creative
    homepage: https://github.com/JimLiu/baoyu-skills#baoyu-cover-image
---

# Cover Image Generator

Adapted from [baoyu-cover-image](https://github.com/JimLiu/baoyu-skills) for Hermes Agent.

Generate elegant article cover images with **5-dimensional customization**: Type × Palette × Rendering × Text × Mood. Supports cinematic (2.35:1), widescreen (16:9), square (1:1), and custom aspect ratios.

## When to Use

Trigger when the user asks to "generate cover image", "create article cover", "make cover", "封面图", or provides an article and wants a cover. The user provides content (file, URL, or pasted text) and optionally specifies dimensions.

## Five Dimensions

| Dimension | Values | Default |
|-----------|--------|---------|
| **Type** | `hero`, `conceptual`, `typography`, `metaphor`, `scene`, `minimal` | auto |
| **Palette** | `warm`, `elegant`, `cool`, `dark`, `earth`, `vivid`, `pastel`, `mono`, `retro`, `duotone`, `macaron` | auto |
| **Rendering** | `flat-vector`, `hand-drawn`, `painterly`, `digital`, `pixel`, `chalk`, `screen-print` | auto |
| **Text** | `none`, `title-only`, `title-subtitle`, `text-rich` | `title-only` |
| **Mood** | `subtle`, `balanced`, `bold` | `balanced` |
| **Font** | `clean`, `handwritten`, `serif`, `display` | `clean` |

### Type (Visual Composition)

| Type | Description | Best For |
|------|-------------|----------|
| `hero` | Large focal visual (60-70% area), dramatic composition | Product launch, announcements |
| `conceptual` | Abstract shapes, information hierarchy, clean zones | Technical articles, architecture |
| `typography` | Title as primary element (40%+ area), minimal visuals | Opinion, quotes, insights |
| `metaphor` | Concrete object representing abstract idea | Philosophy, growth, reflection |
| `scene` | Atmospheric environment, narrative feel | Stories, travel, lifestyle |
| `minimal` | Single focal element, generous whitespace (60%+) | Zen, focus, core concepts |

### Palette (Color Scheme)

11 palettes: `warm` (personal/story), `elegant` (business/luxury), `cool` (tech/system), `dark` (cinematic/premium), `earth` (nature/wellness), `vivid` (launch/promotion), `pastel` (fantasy/gentle), `mono` (zen/focus), `retro` (history/vintage), `duotone` (movie poster/dramatic), `macaron` (education/tutorial).

### Rendering (Visual Style)

| Rendering | Line Quality | Best For |
|-----------|-------------|----------|
| `flat-vector` | Clean, geometric | Tech, WeChat, infographic |
| `hand-drawn` | Sketchy, organic | Personal, casual, doodle |
| `painterly` | Soft, watercolor | Art, dreamy, fantasy |
| `digital` | Polished, crisp | Data, SaaS, corporate |
| `pixel` | Blocky, 8-bit | Gaming, retro, nostalgic |
| `chalk` | Chalk-textured | Education, tutorial |
| `screen-print` | Bold, limited layers | Poster, movie, album |

### Text Level

| Level | Title | Subtitle | Tags | Visual Area |
|-------|:-----:|:--------:|:----:|:-----------:|
| `none` | - | - | - | 100% |
| `title-only` | ✓ | - | - | 85% |
| `title-subtitle` | ✓ | ✓ | - | 75% |
| `text-rich` | ✓ | ✓ | 2-4 tags | 60% |

### Mood (Emotional Intensity)

| Mood | Contrast | Saturation | Weight |
|------|:--------:|:----------:|:------:|
| `subtle` | Low (-20-30%) | Muted (-20-30%) | Light |
| `balanced` | Standard | Standard | Standard |
| `bold` | High (+20-30%) | Vivid (+20-30%) | Heavy |

### Style Presets (shortcuts)

`--style <name>` sets Palette + Rendering in one shot. Explicit `--palette`/`--rendering` overrides preset values.

| Preset | Palette | Rendering |
|--------|---------|-----------|
| `blueprint` | cool | digital |
| `chalkboard` | dark | chalk |
| `corporate` | elegant | digital |
| `minimal` | mono | flat-vector |
| `sketch-notes` | warm | hand-drawn |
| `warm` | warm | hand-drawn |
| `watercolor` | earth | painterly |
| `nature` | earth | hand-drawn |
| `notion` | mono | digital |
| `pixel-art` | vivid | pixel |
| `poster-art` | retro | screen-print |
| `vintage` | retro | hand-drawn |
| `cinematic` | duotone | screen-print |

## Auto-Selection

When dimensions are omitted, select based on content signals:

### Type
| Signals | Type |
|---------|------|
| Product, launch, announcement, release | `hero` |
| Architecture, framework, system, API, technical | `conceptual` |
| Quote, opinion, insight, headline | `typography` |
| Philosophy, growth, abstract, reflection | `metaphor` |
| Story, journey, travel, lifestyle | `scene` |
| Zen, focus, essential, simple | `minimal` |

### Palette
| Signals | Palette |
|---------|---------|
| Personal story, emotion, lifestyle | `warm` |
| Business, professional, luxury | `elegant` |
| Architecture, system, API, code | `cool` |
| Entertainment, cinematic, premium | `dark` |
| Nature, wellness, eco, organic | `earth` |
| Product launch, gaming, promotion | `vivid` |
| Fantasy, creative, whimsical | `pastel` |
| Zen, focus, pure, simple | `mono` |
| History, vintage, classic | `retro` |
| Movie poster, concert, dramatic | `duotone` |
| Education, tutorial, knowledge | `macaron` |

### Rendering
| Signals | Rendering |
|---------|-----------|
| Clean, modern, tech, infographic | `flat-vector` |
| Sketch, personal, casual, doodle | `hand-drawn` |
| Art, watercolor, dreamy, fantasy | `painterly` |
| Data, dashboard, SaaS, polished | `digital` |
| Gaming, retro, nostalgic | `pixel` |
| Education, tutorial, classroom | `chalk` |
| Poster, movie, album, silhouette | `screen-print` |

### Text
| Signals | Text |
|---------|------|
| Visual-only, photography, abstract | `none` |
| Article, blog, standard cover | `title-only` |
| Series, tutorial, technical with context | `title-subtitle` |
| Announcement, features, multiple points | `text-rich` |

### Mood
| Signals | Mood |
|---------|------|
| Professional, corporate, academic, luxury | `subtle` |
| General, educational, blog, documentation | `balanced` |
| Launch, promotion, event, gaming, entertainment | `bold` |

### Font
| Signals | Font |
|---------|------|
| Personal, lifestyle, warm, friendly | `handwritten` |
| Technical, professional, modern, clean | `clean` |
| Editorial, academic, luxury, classic | `serif` |
| Announcement, entertainment, bold, event | `display` |

## Output Structure

```
cover-image/{topic-slug}/
├── source-{slug}.md       # Saved source content
├── prompts/cover.md       # Generation prompt (reproducibility record)
└── cover.png              # Output image
```

Slug: 2-4 words kebab-case. Conflict: append `-YYYYMMDD-HHMMSS`.

## Workflow

```
- [ ] Step 1: Analyze content
- [ ] Step 2: Confirm options (clarify)
- [ ] Step 3: Create prompt → prompts/cover.md
- [ ] Step 4: Generate image → cover.png
- [ ] Step 5: Completion report
```

### Step 1: Analyze Content

1. Save source content (file → read_file, pasted text → write_file to `source-{slug}.md`)
2. Analyze: topic, tone, keywords, visual metaphors
3. Detect language (source, user input, or explicit `--lang`)
4. Determine output directory: `cover-image/{topic-slug}/`
5. **Strip secrets**: scan for API keys, tokens, credentials — never include in outputs

### Step 2: Confirm Options

Use the `clarify` tool. Ask at most 2-3 questions in sequence:

**Q1 — Type, Palette, Rendering**: Present 2-3 auto-recommended combinations with rationale. User picks one.
**Q2 — Text & Aspect**: Confirm text level and aspect ratio (16:9 default, or 2.35:1/4:3/3:2/1:1).
**Q3 — Language** (only if source ≠ user language): which language for title text?

Skip questions where user already specified values. Skip entirely if user said "quick" or "不用确认".

### Step 3: Create Prompt → `prompts/cover.md`

Write a structured prompt file with YAML frontmatter:

```yaml
---
type: cover
palette: [confirmed]
rendering: [confirmed]
---

# Content Context
Article title: [exact title from source]
Content summary: [2-3 sentences]
Keywords: [5-8 terms]

# Visual Design
Type: [confirmed] | Palette: [confirmed] | Rendering: [confirmed]
Font: [confirmed] | Text level: [confirmed] | Mood: [confirmed]
Aspect ratio: [confirmed] | Language: [confirmed]

# Text Elements
[Title/subtitle/tags per text level — use exact title from source; never invent]

# Composition
[Type-specific layout + visual metaphor from content + palette colors + rendering notes]
```

**Principles**:
- Title text: Use exact title from source/user. Do NOT invent.
- Visual metaphor: Derived from content meaning, not literal illustration
- Whitespace: 40-60% breathing room
- Characters: Simplified silhouettes; NO realistic humans
- Color constraint: hex values are rendering guidance — do NOT display as visible text in image
- Strip secrets from all output files

### Step 4: Generate Image

1. Write full prompt to `prompts/cover.md` (reproducibility record — MUST do before generation)
2. Call `image_generate(prompt=..., aspect_ratio=...)` with the prompt content
   - Map aspect: `16:9`/`4:3`→`landscape`, `9:16`/`3:4`→`portrait`, `1:1`→`square`
3. `image_generate` returns a URL — download via terminal:
   ```bash
   curl -sSL -o "/absolute/path/to/cover-image/{slug}/cover.png" "{url}"
   ```
4. Verify file exists and is non-empty
5. On failure, auto-retry once

**Prompt file requirement (hard)**: write `prompts/cover.md` BEFORE calling `image_generate`. The file is the reproducibility record.

### Step 5: Completion Report

```
Cover Generated!

Topic: [topic]
Type: [type] | Palette: [palette] | Rendering: [rendering]
Text: [text] | Mood: [mood] | Font: [font] | Aspect: [ratio]
Language: [lang]

Files:
✓ source-{slug}.md
✓ prompts/cover.md
✓ cover.png
```

## Composition Principles

- **Whitespace**: 40-60% breathing room; avoid clutter
- **Visual anchor**: Main element centered or offset left (right side for title)
- **Characters**: Simplified silhouettes only — NO realistic human faces
- **Title**: Use exact title from user/source; never invent
- **Icon vocabulary**: Simple recognizable icons (code window, lightbulb, gear, lock, etc.) rather than detailed illustrations

## Modification

| Action | Steps |
|--------|-------|
| Regenerate | Backup cover.png → Update prompt file → Regenerate |
| Change dimension | Backup → Confirm new value → Update prompt → Regenerate |

## Pitfalls

1. **Data integrity**: Use exact title from source — never invent or modify
2. **Strip secrets**: Scan for API keys, tokens, credentials before writing any file
3. **Prompt file first**: Write prompts/cover.md BEFORE image_generate — it's the reproducibility record
4. **image_generate returns URL not file**: Always download via `curl -sSL -o {absolute path} {url}`
5. **Aspect ratio mapping**: `16:9`→`landscape`, `9:16`→`portrait`, `1:1`→`square`; custom ratios→nearest
6. **No backend selection from agent**: `image_generate` uses user-configured backend; don't write model names into prompts
7. **Visualize concepts not metaphors**: If article says "电锯切西瓜", illustrate the underlying concept, not the literal image
8. **No text repair on bitmaps**: If title is garbled, regenerate from corrected prompt — never overlay/Photoshop
