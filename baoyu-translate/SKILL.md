---
name: baoyu-translate
description: "Three-mode translation (quick/normal/refined) with audience × style parameterization."
version: 1.0.0
author: 宝玉 (JimLiu), adapted by Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [translation, localization, content, writing]
    category: creative
    homepage: https://github.com/JimLiu/baoyu-skills#baoyu-translate
---

# Translator — Three-Mode Translation

Adapted from [baoyu-translate](https://github.com/JimLiu/baoyu-skills) for Hermes Agent.

Three-mode translation skill: **quick** for direct translation, **normal** for analysis-informed translation, **refined** for full publication-quality workflow with review and polish. All translation is performed by the LLM directly — no external scripts required.

## When to Use

Trigger when the user asks to "translate", "翻译", "精翻", "translate to Chinese/English", "localize", "这篇文章翻译一下", or provides a URL/file with translation intent.

## Modes

| Mode | Trigger Words | Steps | Use Case |
|------|--------------|-------|----------|
| **Quick** | "快翻", "quick", "直接翻译" | Translate | Short texts, informal, quick tasks |
| **Normal** (default) | (default) | Analyze → Translate | Articles, blog posts, general content |
| **Refined** | "精翻", "refined", "publication quality" | Analyze → Translate → Review → Polish | Publication-quality, important docs |

**Auto-detection**: "快翻"/"quick"/"直接翻译" → quick; "精翻"/"refined"/"proofread" → refined; otherwise → normal.

**Upgrade prompt**: After normal mode completes, display:
> Translation saved. To further review and polish, reply **继续润色** or **refine**.

If user responds, continue with review → polish (same as refined mode Steps 4-6).

## Parameterization

### Audience (target reader profile)

| Value | Description | Effect |
|-------|-------------|--------|
| `general` | General readers (default) | Plain language, more translator's notes for jargon |
| `technical` | Developers / engineers | Less annotation on common tech terms |
| `academic` | Researchers / scholars | Formal register, precise terminology |
| `business` | Business professionals | Business-friendly tone, explain tech concepts |

Custom audience descriptions accepted: `--audience "AI感兴趣的普通读者"`.

### Style (translation voice)

| Value | Description | Effect |
|-------|-------------|--------|
| `storytelling` | Engaging narrative flow (default) | Smooth transitions, vivid phrasing |
| `formal` | Professional, structured | Neutral tone, no colloquialisms |
| `technical` | Precise, documentation-style | Concise, terminology-heavy |
| `literal` | Close to original structure | Minimal restructuring |
| `academic` | Scholarly, rigorous | Formal register, citation-aware |
| `business` | Concise, results-focused | Action-oriented, executive-friendly |
| `humorous` | Preserves and adapts humor | Witty, recreates comedic effect |
| `conversational` | Casual, spoken-like | Friendly, approachable |
| `elegant` | Literary, polished prose | Aesthetically refined, rhythmic |

Custom style descriptions accepted: `--style "poetic and lyrical"`.

## Output Directory

```
{source-dir}/{source-basename}-{target-lang}/
├── translation.md          # Final translation (always this name)
├── 01-analysis.md          # Content analysis (normal, refined)
├── 02-prompt.md            # Assembled translation prompt (normal, refined)
├── 03-draft.md             # Initial draft (refined only)
├── 04-critique.md          # Critical review findings (refined only)
├── 05-revision.md          # Revised translation (refined only)
└── chunks/                 # Source + translated chunks (long content only)
```

## Translation Principles (Apply to All Modes)

- **Rewrite, not translate**: Rewrite content into natural, engaging target language as if a skilled native writer composed it from scratch. Quality test: "Does this read like it was originally written in the target language?"
- **Accuracy first**: Facts, data, and logic must match the original exactly
- **Natural flow**: Use idiomatic target language word order. Break long source sentences into shorter, natural ones. Interpret metaphors and idioms by intended meaning, not word-for-word
- **Terminology**: Use standard translations consistently. First occurrence of specialized terms: annotate with original in parentheses
- **Preserve format**: Keep all markdown formatting (headings, bold, italic, images, links, code blocks)
- **Proactive interpretation**: For jargon or concepts the target audience may lack context for, add concise explanations in **bold parentheses** `（**解释**）`. Keep annotations few — only where genuinely needed
- **Frontmatter**: If source has YAML frontmatter, rename source-metadata fields with `source` prefix (camelCase: `url`→`sourceUrl`, `title`→`sourceTitle`), add translated values as new top-level fields, keep other fields as-is
- **Strip secrets**: Scan source for API keys, tokens, credentials before writing any output file

## Workflow

### Quick Mode

1. Translate directly → save to `translation.md`
2. Apply all translation principles above
3. Report: "Translation saved to {output-dir}/translation.md"

### Normal Mode

```
- [ ] Step 1: Analyze → 01-analysis.md
- [ ] Step 2: Assemble prompt → 02-prompt.md
- [ ] Step 3: Translate → translation.md
- [ ] Prompt user: "Reply 继续润色 to refine further"
```

#### Step 1: Analyze → `01-analysis.md`

Load source (file → read_file, URL → browser/fetch, pasted text → write_file). Analyze:

```markdown
# Translation Analysis

## Source Metadata
- File: [path] | Language: [detected] | Word count: [N]
- Domain: [tech/business/academic/general]
- Tone: [formal/casual/technical/narrative]

## Terminology Map
| Source Term | Target Translation | Notes |
|-------------|-------------------|-------|
| ... | ... | ... |

## Translation Challenges
- [Cultural references needing adaptation]
- [Idioms/phrasal verbs needing interpretation]
- [Domain-specific jargon needing annotation]
```

#### Step 2: Assemble Prompt → `02-prompt.md`

Combine: audience profile + style instructions + terminology map + translation principles + source content. Save as the translation instruction file.

#### Step 3: Translate → `translation.md`

Translate following `02-prompt.md`. For long content (>4000 words):

1. **Extract terminology**: Scan entire document for proper nouns, technical terms
2. **Split into chunks** at markdown block boundaries (headings, paragraphs). Max ~5000 words per chunk
3. **Translate chunks** sequentially, maintaining terminology consistency via the shared terminology map
4. **Merge** translated chunks in order → `translation.md`

After completion, prompt user to optionally continue to refined mode.

### Refined Mode

```
- [ ] Step 1: Analyze → 01-analysis.md
- [ ] Step 2: Assemble prompt → 02-prompt.md
- [ ] Step 3: Draft → 03-draft.md
- [ ] Step 4: Critical review → 04-critique.md
- [ ] Step 5: Revision → 05-revision.md
- [ ] Step 6: Polish → translation.md
```

Steps 1-2 same as Normal mode.

#### Step 3: Draft → `03-draft.md`

Translate following `02-prompt.md`. For long content, chunk as described in Normal mode Step 3. Include translator's notes inline for ambiguous passages.

#### Step 4: Critical Review → `04-critique.md`

Review `03-draft.md` systematically for:

```markdown
# Translation Critique

## Accuracy Issues
- [Mistranslations — meaning differs from source]
- [Omissions — content dropped]
- [Additions — content not in source]

## Europeanized Language (for EN→ZH)
- [Word-for-word sentence structures that sound unnatural in Chinese]
- [Overuse of passive voice / 被字句]
- [Long modifier chains before nouns]

## Style Execution
- [Does the translation match the requested style?]
- [Are metaphors/idioms interpreted by meaning?]
- [Is the voice consistent throughout?]

## Expression Issues
- [Awkward phrasing]
- [Repetitive vocabulary]
- [Register inconsistencies]
```

**⚠️ Diagnosis only — do NOT propose fixes in this step.** The critique identifies problems; revision solves them.

#### Step 5: Revision → `05-revision.md`

Apply ALL critique findings to produce a revised translation:

1. Fix accuracy issues (mistranslations, omissions, additions)
2. Restructure Europeanized sentences into natural target language patterns
3. Align voice with requested style
4. Improve expression (varied vocabulary, consistent register)
5. Verify terminology consistency
6. Preserve all markdown formatting

#### Step 6: Polish → `translation.md`

Final publication-quality pass:

1. Read `05-revision.md` aloud (mentally) — flag anything that sounds unnatural
2. Tighten prose: remove filler words, redundant phrases
3. Ensure paragraph transitions are smooth
4. Verify title is compelling in target language
5. Check for consistent formatting
6. Save as `translation.md`

## Step 5: Output

Final translation always at `translation.md` in output directory.

After final translation, do a lightweight image-language check:
1. Collect image references from the translated article
2. Identify likely text-heavy images (covers, screenshots, diagrams, charts)
3. If any image likely contains text in source language while article is now in target language, warn user:

```
Possible image localization needed:
- ![cover](attachments/cover.png): likely still contains source-language text
- ![diagram](attachments/diagram.png): text-heavy graphic, check labels
```

Display summary:
```
**Translation complete** ({mode} mode)
Source: {source-path}
Languages: {from} → {to}
Output: {output-dir}/translation.md
```

## Pitfalls

1. **Accuracy first**: Never sacrifice factual correctness for style. Verify data, numbers, names.
2. **Strip secrets**: Scan source for API keys, tokens, credentials before writing any file
3. **Rewrite, not transliterate**: The goal is natural target-language writing, not word-for-word conversion
4. **Idioms by meaning**: "It's raining cats and dogs" → "大雨倾盆" (heavy rain), not literal animals
5. **Terminology consistency**: Same source term → same target term throughout
6. **Markdown preservation**: Code blocks, links, images, tables must survive translation intact
7. **Frontmatter handling**: Don't lose YAML metadata; prefix source fields with `source`
8. **Critique before fix**: In refined mode Step 4, diagnose only — don't mix critique with revision
