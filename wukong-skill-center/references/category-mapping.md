# Awesome Skills 分类映射

从 GitHub README (jorinyang/awesome-skills) 提取的 8 大分类，用于补全 `skills-index.json` 中缺失的 category 字段。

生成命令：
```python
# 在 skills-index.json 中应用此映射
with open('skills-index.json') as f: skills = json.load(f)
for s in skills:
    if s['id'] in CATEGORY_MAP:
        s['category'] = CATEGORY_MAP[s['id']]
```

## 🧠 方法论 (21)

```
advanced-elicitation, author-methodology-analysis, blue-team, book-deconstruct,
darwin-skill, deep-think, domain-decompose, edge-case-hunter,
editorial-review-prose, editorial-review-structure, github-absorb,
ljg-elicitation-modes, ljg-infographic-design, ljg-writing-voice,
qa-extract, relationship-analysis, pm-prioritization-frameworks,
stakeholder-mapping, opportunity-solution-tree, external-skill-evaluation,
double-evolution
```

## 🏗️ 构建与设计 (24)

```
answer, answer-standalone, dynamic-workflow, architecture-diagram,
drawio-generation, brandkit, claude-design, design-md, feishu-html,
fireworks-tech-graph, hallmark, html-ppt, ppt-structure-parser,
ppt-template-filler, huashu-design, humanizer, pretext, redesign-skill,
requesting-code-review, sketch, strategy-plan-writing, taste-skill,
writing-plans, requirement-alignment-analysis, spike
```

## 🔧 开发工程 (14)

```
agent-native-cli-design, cross-project-adaptation, coding-agents,
dingtalk-cli, subagent-driven-development, supabase-backend,
test-driven-development, wsl-browser-cdp, hermes-instance-sync,
technical-documentation-production, windows-troubleshooting-from-wsl,
wsl-docker-deploy, firecrawl-web, github-release-readme, openyida
```

## 🤖 AI 工程 (4)

```
skill-evaluator, skill-ab-test, benchmark-generator, agent-tool-system
```

## 📋 飞书系列 (7)

```
feishu-doc, feishu-table, feishu-wiki, feishu-voice,
feishu-wiki-file-routing, project-kanban, zhike-task-hub
```

## 🏔️ 贵州之客 (16)

```
amap-lbs, jimeng-video, travel-intel, travel-itinerary, travel-workflow,
trip-landing, wechat-article-archive, zhike-content-output, trip-quote,
trip-briefing, guide-exec, supply-check, vendor-brief, cost-engine,
trip-archive, customer-view
```

## 🔬 研究 (4)

```
ara-compiler, ara-research-manager, ara-rigor-reviewer, systematic-debugging
```

## 🎨 创意内容 (6)

```
baoyu-article-illustrator, baoyu-comic, baoyu-cover-image,
baoyu-infographic, baoyu-translate, image-analysis
```
