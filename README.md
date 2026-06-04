# Awesome Skills

Curated collection of Agent Skills — designed for Hermes Agent but compatible with any agent framework that supports SKILL.md format.

## Skills Index

### 🧠 Methodology

| Skill | Description |
|-------|-------------|
| [advanced-elicitation](advanced-elicitation/SKILL.md) | 结构化深度追问 — 69种方法（Pre-mortem/First Principles/Red Team/Socratic等） |
| [blue-team](blue-team/SKILL.md) | 业务蓝军内容审核官 — 6阶段破坏性逻辑审查 |

### 🏗️ Builder

| Skill | Description |
|-------|-------------|
| [answer](answer/SKILL.md) | AI Native'S Workflow(er) — 7阶段结构化工作流编排器 |

### 🔍 Quality

| Skill | Description |
|-------|-------------|
| [edge-case-hunter](edge-case-hunter/SKILL.md) | 穷举边界遍历 — 机械式走查所有分支路径和边界条件 |
| [editorial-review-prose](editorial-review-prose/SKILL.md) | 临床级文本编辑 — 微软基线 × 三列表格审查 |
| [editorial-review-structure](editorial-review-structure/SKILL.md) | 结构编辑 — 5种结构模型 × 6类重组建议 |

### 📋 Feishu (飞书)

| Skill | Description |
|-------|-------------|
| [feishu-html](feishu-html/SKILL.md) | 飞书文档 → WEB SPA 制作与 OSS 部署 |
| [feishu-doc](feishu-doc/SKILL.md) | 飞书文档创建与管理 |
| [feishu-wiki](feishu-wiki/SKILL.md) | 飞书知识库全面管理 — 巡检/总结/分类/变更 |
| [feishu-table](feishu-table/SKILL.md) | 飞书多维表格与电子表格管理 |

### 🏔️ 贵州之客 (Zhike)

| Skill | Description |
|-------|-------------|
| [zhike-content-output](zhike-content-output/SKILL.md) | 内容产出准则 — 对客写作铁律/叙事声音规范 |
| [zhike-task-hub](zhike-task-hub/SKILL.md) | 任务中枢 — Todo存档 + 早晚周月报 |
| [project-kanban](project-kanban/SKILL.md) | 项目看板 — 飞书多维表格/日历/任务三引擎 |

### 🗺️ Travel

| Skill | Description |
|-------|-------------|
| [travel-intel](travel-intel/SKILL.md) | 旅游情报系统 — 4通道采集 → 入库 → 过期校验 → 分级报告 |
| [travel-itinerary](travel-itinerary/SKILL.md) | 智能行程规划 — 7步工作流 |
| [trip-landing](trip-landing/SKILL.md) | 客户行程落地页 — 一键生成 5 TAB SPA |

## Usage

Each skill is a self-contained SKILL.md file in its own folder. Load into Hermes Agent via:

```bash
hermes -s advanced-elicitation
```

Or for any agent framework that reads SKILL.md format, reference the file directly.

## License

MIT — See individual SKILL.md files for author attribution.
