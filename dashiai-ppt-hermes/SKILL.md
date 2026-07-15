---
name: dashiai-ppt-hermes
description: >-
  DashiAI PPT 生成器（Hermes 封装）—— 12套视觉主题、1020个版式的 AI PPT 技能。
  从文档/大纲/需求描述生成 HTML 演示文稿，浏览器内编辑，支持导出 PPTX/PDF。
  触发词：做PPT、生成PPT、制作演示文稿、DashiAI PPT、大师PPT、网页PPT、
  汇报材料、路演PPT、分析报告PPT、make slides、create presentation。
version: 1.0.0
author: 杨瑒 (月夜)
category: ppt
metadata:
  hermes:
    tags: [ppt, presentation, dashiai, html-deck, slides, ai-ppt]
    related_skills:
      - html-ppt
triggers:
  - "做PPT"
  - "生成PPT"
  - "制作演示文稿"
  - "DashiAI PPT"
  - "大师PPT"
  - "网页PPT"
  - "汇报材料"
  - "路演PPT"
  - "分析报告PPT"
  - "用DashiAI做"
  - "make slides"
  - "create presentation"
  - "html ppt"
  - "帮我做个汇报"
  - "做个路演"
  - "做份演示"
---

# DashiAI PPT（Hermes 封装）

> 封装自 [chuspeeism/dashiAI-ppt-skill](https://github.com/chuspeeism/dashiAI-ppt-skill) v0.3.0
> 吸收日期：2026-07-12 | AGPL-3.0

DashiAI PPT 基于 12 套预置视觉主题 + 1020 个版式页面生成 HTML 演示文稿。产物可在浏览器中打开编辑（翻页、改文字、换图、调布局），支持导出 PPTX / PDF。

## 前置条件

```bash
# 环境要求
Node.js 20+, npm, Chrome/Chromium/Edge（导出 PPTX/PDF 需要）
```

### 安装

首次使用需安装（一键，已装则原地更新）：

```bash
npx dashiai-ppt-skill@latest
# 国内镜像
npx --registry=https://registry.npmmirror.com dashiai-ppt-skill@latest
```

安装后 Skill 位于：`~/.claude/skills/dashiai-ppt/`（Windows 为 `%USERPROFILE%/.claude/skills/dashiai-ppt/`）

## 12 套主题速查

| 主题 | 风格 | 适合场景 |
|------|------|---------|
| `theme01` | 轻拟态风 | 产品介绍 / 企业汇报 |
| `theme02` | 炫光紫绿风 | 科技发布会 / AI主题 |
| `theme03` | 深浅代码风 | 技术方案 / 开发者大会 |
| `theme04` | 玻璃糖果风 | 年轻化品牌 / 消费产品 |
| `theme05` | 色谱图表风 | 数据报告 / 市场分析 |
| `theme06` | 深色图谱风 | 高密度数据 / 战略分析 |
| `theme07` | 冷白调研风 | 调研报告 / 白皮书 |
| `theme08` | 黑金实验风 | 高端发布 / 品牌提案 |
| `theme09` | 深蓝杂志风 | 品牌故事 / 人物访谈 |
| `theme10` | 金色指数风 | 金融数据 / 投资报告 |
| `theme11` | 高能增长风 | 增长复盘 / 商业计划 |
| `theme12` | 声波霓虹风 | 音乐娱乐 / 潮流活动 |

> ⚠️ `theme10` 不自动选用，仅用户明确指定或金融投资强相关时使用。

## 执行流程

### Phase 1: 需求提炼 🔍

从用户输入中提取：

- **title**: 演示标题
- **goal**: 一句话目标（面向谁、讲什么、达成什么）
- **audience**: 受众
- **owner**: 汇报人/团队
- **pageCount**: 页数（默认 10 页，最少 8 页）
- **format**: 交付格式（HTML 默认 / PPTX 明确指定时）

🔴 CHECKPOINT：确认主题风格和图片需求后才进入 Phase 2。

**委托模式**：仅当用户说"都你来定/不用问直接干"时才自选主题。否则必须展示主题预览后等待确认。

### Phase 2: 风格确认 🎨

🔴 必须展示主题预览图：回复中嵌入 `{SKILL_ROOT}/assets/skill/theme-style-grid.png`（展开为绝对路径）。

列出可选主题和「适合场景/人群」后等待用户选择。

同时确认：是否需要图片/视频素材？用户有本地素材先 `media:stage`。

### Phase 3: 选页 📋

```bash
SKILL_ROOT="$HOME/.claude/skills/dashiai-ppt"

# 查询候选页面
node "$SKILL_ROOT/project/scripts/layout-query.mjs" \
  --theme {themePack} --role {role} --limit 8

# 需要媒体槽时
node "$SKILL_ROOT/project/scripts/layout-query.mjs" \
  --theme {themePack} --role {role} --needs-media --limit 8

# 查看页面契约
npm --prefix "$SKILL_ROOT/project" run inspect:layout -- --compact {layout...}
```

**选页原则**：
- 封面从当前主题前 5 页（`themeXX_page001`~`page005`）中选 1 页
- 正文从第 6 页以后选
- 同一 deck 中 `layout` 必须唯一，不重复使用
- `contentLocked: true` 的页换一页

### Phase 4: 组装 goal.json 📝

```json
{
  "title": "标题",
  "goal": "一句话目标",
  "audience": "受众",
  "owner": "汇报人",
  "randomSeed": "{主题}-{日期}-{3位随机词}",
  "pageCount": 10,
  "themePack": "theme01",
  "slides": [
    {"layout": "theme01_page001", "props": {"kicker": "眉题", "titleTop": "主标上", "titleBottom": "主标下", "lead": "导语"}},
    {"layout": "theme01_page006", "props": {"kicker": "核心数字", "value": "970", "unit": "亿美元"}}
  ]
}
```

**填写规则**：
- 只填 `copyKeys` 和可见数组字段，不改样式/结构
- `display` / `metric` 字段只写短词短句或数字
- Html 字段只用 `<br>` + `<b>` / `<em>`，禁止 `<span>`
- 数组按 `fillPlan.arrays[].visibleCount` 填满可见项
- `decorativeKeys` 装饰位不填
- 图表页填数据后，页内 insight/读图文案一并改写

### Phase 5: 安全写入与校验 ✅

```bash
SKILL_ROOT="$HOME/.claude/skills/dashiai-ppt"
OUT_DIR="output/{deck-name}"

# 安全写入 props
npm --prefix "$SKILL_ROOT/project" run props:safe -- \
  --goal "$OUT_DIR/goal.json" --write

# 校验 goal spec
npm --prefix "$SKILL_ROOT/project" run validate:goal-spec -- \
  "$OUT_DIR/goal.json"
```

### Phase 6: 渲染 🚀

```bash
SKILL_ROOT="$HOME/.claude/skills/dashiai-ppt"
OUT_DIR="output/{deck-name}"

# 渲染 HTML
"$SKILL_ROOT/scripts/render_goal_deck.sh" \
  "$OUT_DIR/goal.json" \
  "$OUT_DIR/ppt/index.html"
```

脚本会自动启动本机预览服务，输出 `http://127.0.0.1:{port}/`。

> ⚠️ 只能用该脚本启动的预览服务（有导出和自动保存接口），不能用 `python -m http.server` 等静态服务器替代。

### Phase 7: 输出校验 ✅

```bash
SKILL_ROOT="$HOME/.claude/skills/dashiai-ppt"
OUT_DIR="output/{deck-name}"

npm --prefix "$SKILL_ROOT/project" run validate:swiss -- "$OUT_DIR/ppt/index.html"
npm --prefix "$SKILL_ROOT/project" run validate:goal-copy -- \
  "$OUT_DIR/goal.json" "$OUT_DIR/ppt/index.html"
```

### Phase 8: 交付 📦

**HTML 交付**（默认）：给用户 `http://127.0.0.1:{port}/`

**PPTX 交付**（用户明确要求时）：
```bash
# 方式 A：通过预览服务 API（需要预览服务运行中）
curl -X POST http://127.0.0.1:{port}/api/export-editable-pptx \
  -H "Content-Type: application/json" \
  -d '{"exportKind":"pptx"}' -o output.pptx

# 方式 B：命令行导出（无浏览器会话时）
npm --prefix "$SKILL_ROOT/project" run export:pptx -- \
  "$OUT_DIR/ppt" "output.pptx"
```

### Phase 9: 版本检查（静默）

```bash
node "$SKILL_ROOT/scripts/check_latest_version.mjs"
```

有输出时在回复末尾提醒用户更新；无输出则静默。

---

## 工具命令速查

所有路径均基于 `SKILL_ROOT="$HOME/.claude/skills/dashiai-ppt"`：

| 命令 | 用途 |
|------|------|
| `node $SKILL_ROOT/project/scripts/layout-query.mjs --theme X --role Y --limit N` | 查询候选页面 |
| `npm --prefix $SKILL_ROOT/project run inspect:layout -- --compact {layout}` | 查看页面契约 |
| `npm --prefix $SKILL_ROOT/project run props:safe -- --goal X --write` | 安全写入 props |
| `npm --prefix $SKILL_ROOT/project run validate:goal-spec -- X` | 校验 goal.json |
| `$SKILL_ROOT/scripts/render_goal_deck.sh {goal} {out}` | 渲染 HTML |
| `npm --prefix $SKILL_ROOT/project run validate:swiss -- X` | 校验输出完整性 |
| `npm --prefix $SKILL_ROOT/project run validate:goal-copy -- {goal} {html}` | 校验文案覆盖 |
| `npm --prefix $SKILL_ROOT/project run media:stage -- {dir} {files...}` | 素材导入 |
| `node $SKILL_ROOT/scripts/check_latest_version.mjs` | 版本检查 |

---

## 媒体工作流

1. 用户提供本地素材：先 `media:stage` 到 deck 目录
2. 需要生图：Codex 环境用 image-gen 并行生成（≥2 张时 subagent 并行）
3. 素材路径只引用 deck 内相对路径，不引用临时目录或外部绝对路径

---

## 返工与修复

只在以下情况返工：
- 渲染失败
- `validate:swiss` / `validate:goal-copy` 失败
- 输出中出现与用户主题无关的模板文案
- 用户明确指出某页有问题

默认最多修复 2 轮。仍失败时说明阻塞原因。

---

## 设计定位

本技能是 Hermes 的**默认 PPT 生成方案**。之前探索过的「解析 PPTX 模板 → 页面库 → 填充组装」路径因模型和模态能力达不到实用要求已废弃，但其方法论精华（内容分析/模板匹配/和谐化策略）已记录在 `references/methodology-insights.md` 供参考。

| 技能 | 关系 | 说明 |
|------|:---:|------|
| `html-ppt` | sibling | 同属 HTML PPT 生成，dashiai 独有：12 主题+浏览器内编辑控制台+分析模型版式 |

---

## 反例（禁止）

- ❌ 不确认主题就开工 — 风格必须用户选定
- ❌ 在 `goal.json` 中引用 `file://` 或远程 URL — 只允许 deck 内相对路径
- ❌ 用 `python -m http.server` 替代预览服务 — 导出和自动保存不可用
- ❌ 交付空媒体槽或伪造路径 — 交付前必须写入真实素材
- ❌ 修改页面样式/CSS/结构来填内容 — 只改 `props` 内文案
- ❌ 复用旧 `goal.json` 或旧 HTML — 每次新建独立输出目录
- ❌ 交付包含模板默认文案的页面 — 渲染前必须全部覆盖为用户内容
- ❌ 技术方案产出差却硬撑 — 之前「解析 PPTX 模板→页面库→填充」路径技术架构优雅但产出质量不过关，果断废弃。方法论保留（`references/methodology-insights.md`），不因沉没成本死守。

## 失败模式

| 场景 | 原因 | 处理 |
|------|------|------|
| `layout:query` 无结果 | 主题/角色组合不存在 | 换角色/主题重试 |
| 渲染失败 | goal.json 格式错误 | 先跑 `validate:goal-spec` |
| 导出 PPTX 失败 | Chrome 不可用 | 设置 `CHROME_PATH` 或确认已装 Chrome |
| 预览端口冲突 | 端口被占 | 设 `DASHI_PPT_PREVIEW_PORT=5200-5999` |
| 文案覆盖不全 | `copyKeys` 未完整覆盖 | 用 `inspect:layout` 查全量字段 |

---

> 源仓库：https://github.com/chuspeeism/dashiAI-ppt-skill | AGPL-3.0 | 导出引擎专有组件
