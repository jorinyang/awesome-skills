---
name: ppt-template-filler
description: >
  PPT模板填充器 —— 从页面库查询匹配页面，跨模板拼装新PPT，四阶段流水线（匹配→分析→组装→校验）。
  触发词：组装PPT、做PPT、生成PPT、填充模板、套模板、大纲转PPT、内容转PPT、
  create ppt、make slides、generate ppt、ppt from outline。
version: 1.0.0
author: 杨瑒 (月夜)
category: ppt
metadata:
  hermes:
    tags: [ppt, template, filler, assembly, composition, content]
    related_skills:
      - ppt-structure-parser
triggers:
  # 中文 — 组装/生成类
  - "组装PPT"
  - "拼PPT"
  - "做PPT"
  - "生成PPT"
  - "制作PPT"
  - "做演示文稿"
  - "做slides"
  - "生成演示文稿"
  - "PPT生成"
  - "PPT组装"
  # 中文 — 填充/模板类
  - "填充PPT模板"
  - "填充模板"
  - "用模板生成PPT"
  - "套模板"
  - "套PPT模板"
  # 中文 — 大纲/内容转PPT类
  - "从大纲生成PPT"
  - "从内容做PPT"
  - "根据内容生成PPT"
  - "把大纲变成PPT"
  - "内容转PPT"
  - "大纲转PPT"
  - "根据大纲做PPT"
  # 中文 — 页面拼装类
  - "拼PPT页面"
  - "跨模板组装"
  - "PPT页面拼装"
  # English
  - "create ppt"
  - "make ppt"
  - "generate ppt"
  - "assemble ppt"
  - "build ppt"
  - "fill ppt template"
  - "ppt generation"
  - "make slides"
  - "create presentation"
  - "generate presentation"
  - "ppt from outline"
  - "content to ppt"
  - "outline to ppt"
---

# PPT 模板填充器

> 定位：从页面库查询匹配最佳模板页 → 内容分析确认适配 → 跨模板形状克隆组装 → 校验输出质量。四阶段非破坏性流水线，源模板文件零修改。

## 前置条件

```bash
# 依赖
pip install python-pptx

# 引擎路径
PYTHONPATH="$HOME/.hermes-feishu/skills/ppt:$PYTHONPATH"

# 确保页面库已建立
python3 -c "from ppt_engine import PPTEngine; print(PPTEngine().stats())"
```

> 📄 跨模板形状克隆技术细节见 `ppt-structure-parser` 的 `references/cloning-technique.md`

## 执行流程

### Phase 1: 页面匹配 🔍

输入：内容大纲 → 输出：组装计划 `AssemblyPlan`

```python
from ppt_engine import PPTEngine

engine = PPTEngine()

# 内容大纲定义
outline = [
    {"page_type": "cover", "content": {"title": "2026年度战略报告", "subtitle": "技术创新部"}},
    {"page_type": "section-header", "content": {"title": "核心成果"}},
    {"page_type": "content-2col", "content": {
        "title": "重点项目进展",
        "body": "项目A: 已完成90%\n项目B: 进入验收阶段\n项目C: 启动筹备",
        "has_image": True
    }},
    {"page_type": "chart", "content": {"title": "营收趋势"}},
    {"page_type": "ending", "content": {"title": "感谢聆听"}},
]

result = engine.fill(outline, output_path="/tmp/report.pptx")
```

**匹配策略**：
1. 优先 `preferred_family`（指定模板族）
2. 同页面类型查询 → 内容结构评分 → 质量分加成
3. 无精确匹配时降级（放宽类型限制）

**匹配分数计算**：
- 模板族偏好: +20
- 类型匹配: +10
- 标题适配: ±5（过长扣分）
- 图片需求匹配: +5
- 正文容量适配: ±3
- 质量分加成: +0-5

### Phase 2: 内容分析 📊

对每一页做内容→模板结构适配度分析：

```python
analyzer = ContentAnalyzer()
analysis = analyzer.analyze(entry, content)
# → {"score": 0.85, "issues": [...], "fit_map": {"title": "Title Box 3", ...}}
```

**检查项**：
- 标题长度是否超出页面容量
- 正文行数是否超出页面容量
- 图片需求 vs 模板图片位
- 图表需求 vs 模板图表位

**风险等级**：
- `score ≥ 0.8`: ✅ 适配良好
- `0.5 ≤ score < 0.8`: ⚠️ 有轻微不匹配
- `score < 0.5`: ❌ 严重不匹配，建议更换页面

### Phase 3: 幻灯片组装 🔧

非破坏性操作——源文件零修改：

1. 创建空白目标 PPT
2. 打开源模板 → 定位目标幻灯片
3. 用 `copy.deepcopy()` 克隆形状 XML 元素到目标幻灯片
4. 克隆版面背景色（如果源页有背景填充）
5. 按 `fit_map` 填充文本内容到对应形状槽

```python
# 核心克隆逻辑（自动执行）
for shape in source_slide.shapes:
    if not shape.is_placeholder:
        new_element = deepcopy(shape._element)
        target_slide.shapes._spTree.append(new_element)
```

**背景处理**：优先从 layout 提取 `srgbClr` 值，直接应用到目标 slide 的 `background.fill`。

### Phase 4: 内容校验 ✔️

逐页逐形状验证：

- 页数匹配检查
- 形状数量合理性（不低于源页面 50%）
- 文本是否成功填充
- 内容适配警告是否已处理

```python
# 校验结果
result.passed  # True/False
result.summary # "校验完成: 0 错误, 2 警告"
result.issues  # [ValidationIssue(...), ...]
```

## 内容大纲格式

### 完整格式

```json
[
  {
    "page_type": "cover",
    "content": {
      "title": "演示文稿标题",
      "subtitle": "副标题或日期",
      "has_image": false
    }
  },
  {
    "page_type": "content-2col",
    "content": {
      "title": "页面标题",
      "body": "正文内容\n可以多行",
      "has_image": true,
      "image_description": "产品架构图"
    }
  },
  {
    "page_type": "chart",
    "content": {
      "title": "图表标题",
      "chart_type": "bar",
      "has_chart": true
    }
  }
]
```

### 简化格式（仅类型，无内容）

```python
from ppt_engine.template_filler import ContentOutline

outline = ContentOutline.from_simple_list([
    "cover", "toc", "content-2col", "content-2col", "ending"
])
```

## 可用页面类型

| 类型 | 用途 | 建议 |
|------|------|------|
| `cover` | 封面 | 标题+副标题 |
| `toc` | 目录 | 列表式结构 |
| `section-header` | 章节过渡页 | 大标题+装饰 |
| `content-1col` | 单栏正文 | 纯文本内容 |
| `content-2col` | 双栏正文 | 对比/并列内容 |
| `content-3col` | 三栏正文 | 三要素展示 |
| `image-full` | 全图页 | 大图+极少文字 |
| `image-left` | 左图右文 | 图片在左侧 |
| `image-right` | 左文右图 | 图片在右侧 |
| `chart` | 图表页 | 数据可视化 |
| `table` | 表格页 | 表格数据 |
| `quote` | 引用页 | 金句/引言 |
| `team` | 团队/人物 | 人物介绍 |
| `timeline` | 时间线 | 里程碑 |
| `comparison` | 对比页 | A vs B |
| `numbered-list` | 编号列表 | 步骤/要点 |
| `ending` | 尾页 | 致谢/Q&A |

## 和谐化策略

跨模板组装时的设计一致性处理：

| 模式 | `harmony_color_mode` | 行为 |
|------|---------------------|------|
| 保持源设计 | `keep_source` | 每页保留各自模板的设计令牌 |
| 统一主色 | `unify_all` | 所有页统一为目标族的设计令牌 |
| 自适应 | `adaptive` | 同族页面保持，跨族页面做有限和谐化 |

## 反例（禁止）

- ❌ 不经内容分析就直接组装 — 可能出现标题溢出正文截断
- ❌ 源文件被修改 — 克隆操作目标是新 PPT，源文件零写入
- ❌ 母版合并操作 — 不在同一 PPT 中混合多个母版
- ❌ 用 `prs.slides.add_slide(source_layout)` 跨模板添加幻灯片 — 母版不兼容
- ❌ 跳过校验步骤 — 表面看起来正常的 PPT 可能有隐藏问题

## 失败模式

| 场景 | 原因 | 处理 |
|------|------|------|
| 页面库为空 | 未先执行 structure-parser | 提示先建库 |
| 无匹配页面 | 页面类型库中不存在 | 降级到 content-1col 或提示补充模板 |
| 形状克隆失败 | 特殊形状类型（SmartArt） | 跳过该形状，记录警告 |
| 背景克隆失败 | 源页无背景信息 | 使用白色背景，不影响组装 |
| 文本填充错位 | 形状名不匹配 | 按角色降级填充到第一个文本框 |
| 输出 PPT 无法打开 | XML 结构破坏 | 回退到上一步，逐形状检查 |

## 关联技能

- **upstream ← `ppt-structure-parser`**：填充器依赖结构解析器建立的页面库。页面库为空时无法工作。
