---
name: ppt-structure-parser
description: >
  PPT结构解析器 —— 将多套PPT模板拆解为独立页面，三级标签分类，入库为可检索的页面数据列表。
  触发词：解析PPT模板、拆PPT、拆模板、PPT组件化、建页面库、导入模板、分析PPT结构、
  模板拆解、parse ppt template、deconstruct ppt、split ppt into pages。
version: 1.0.0
author: 杨瑒 (月夜)
category: ppt
metadata:
  hermes:
    tags: [ppt, template, parser, component, library, structure]
    related_skills:
      - ppt-template-filler
triggers:
  # 中文 — 解析/拆解类
  - "解析PPT模板"
  - "解析模板"
  - "拆PPT模板"
  - "拆解PPT模板"
  - "拆模板"
  - "拆PPT"
  - "PPT拆解"
  - "模板拆解"
  - "分析PPT结构"
  - "分析模板结构"
  # 中文 — 入库/组件化类
  - "PPT组件化"
  - "建PPT页面库"
  - "建页面库"
  - "PPT入库"
  - "页面库初始化"
  - "导入PPT模板"
  - "导入模板"
  - "把模板拆成页面"
  - "把PPT拆成组件"
  # 中文 — 母版/幻灯片类
  - "解析幻灯片"
  - "解析母版"
  - "幻灯片拆解"
  - "分析幻灯片布局"
  # English
  - "parse ppt template"
  - "parse pptx"
  - "deconstruct ppt"
  - "deconstruct template"
  - "ppt component library"
  - "build page library"
  - "import ppt template"
  - "analyze ppt structure"
  - "split ppt into pages"
  - "template deconstruction"
  - "ppt page extraction"
---

# PPT 结构解析器

> 定位：将多套复杂PPT模板拆解为原子页面，三级标签分类，入库为可检索的页面数据列表。

## 设计哲学

每张幻灯片独立存储为一条 `PageEntry` 记录（JSON），携带完整的：
- 元数据（来源模板、模板族、页面索引）
- 三级标签（模板族 → 页面类型 → 布局变体）
- 设计令牌（颜色/字体/间距）
- 元素统图（文本框/图片/图表/形状数量）
- 文本结构（标题/副标题/正文的角色和位置）
- 内容约束（最大标题字符、最大正文行数等）

不依赖单个模板的母版完整性。每页独立，可被跨模板组合。

## 前置条件

```bash
# Python 依赖
pip install python-pptx

# 引擎路径
PYTHONPATH="/home/aorus/.hermes-feishu:$PYTHONPATH"
```

> 📄 核心技术验证报告见 `references/cloning-technique.md`（跨模板形状克隆、背景提取、已知陷阱）

## 执行流程

### Step 1: 接收模板文件

用户提供 .pptx 文件路径和模板族名称。

```
用户: 把这个模板解析入库，命名为 "business_dark_v2"
→ 获取 pptx_path + family_name
```

🔴 CHECKPOINT 1: 文件合法性验证
   
   - [ ] 文件路径非空且以 `.pptx` 结尾
   - [ ] `os.path.exists(pptx_path)` 返回 True
   - [ ] `python-pptx` 可打开文件（try `Presentation(pptx_path)`）
   - [ ] 幻灯片数量 ≥ 1（`len(pres.slides) > 0`）
   - [ ] 模板族名称非空且不含特殊字符
   
   → 不通过则 STOP，提示用户提供正确文件路径。

### Step 2: 逐页拆解

```python
from ppt_engine import PPTEngine

engine = PPTEngine()  # 使用默认页面库路径
entries = engine.parse_template(pptx_path, family_name)
```

每页输出摘要：
```
[00] cover          | single-column             | 2T
[01] section-header | single-column             | 1T    
[02] content-2col   | image-left-text-right     | 3T 1I
```

格式：`[索引] 页面类型 | 布局变体 | 元素统计(T=文本,I=图片,C=图表)`

### Step 3: 查看入库结果

```python
stats = engine.stats()
# → {'total_pages': 24, 'template_families': 3, ...}
```

### Step 4: 批量处理

```python
engine.parse_templates([
    ("/path/to/template_a.pptx", "business_dark"),
    ("/path/to/template_b.pptx", "modern_light"),
    ("/path/to/template_c.pptx", "creative_color"),
])
```

## 三级标签体系

| Level | 名称 | 说明 | 示例 |
|-------|------|------|------|
| L1 | 模板族 | 来源模板 + 设计系统 | `business_dark`, `modern_light` |
| L2 | 页面类型 | 功能分类（18种） | `cover`, `content-2col`, `chart` |
| L3 | 布局变体 | 具体排列差异 | `image-left-text-right`, `multi-column` |

完整 L2 枚举：`cover`, `toc`, `section-header`, `content-1col`, `content-2col`, `content-3col`, `image-full`, `image-left`, `image-right`, `chart`, `table`, `quote`, `team`, `timeline`, `comparison`, `numbered-list`, `ending`, `blank`, `unknown`

## 提取的特征

| 特征 | 字段 | 说明 |
|------|------|------|
| 元素统计 | `element_map` | text_boxes / image_placeholders / chart_placeholders / auto_shapes |
| 文本角色 | `text_structure` | 每个文本槽的 role / position / font_size / max_chars |
| 设计令牌 | `design_tokens` | primary_color / font_title / body_size_pt / spacing |
| 内容约束 | `content_constraints` | max_title_chars / max_body_lines / requires_image |

## 数据存储

页面数据存储为 JSON 文件：`~/.hermes-feishu/ppt_engine/page_library.json`

```json
{
  "version": "1.0",
  "total_pages": 24,
  "pages": [
    {
      "page_id": "business_dark_page_00",
      "source_template": "template_a.pptx",
      "template_family": "business_dark",
      "page_type": "cover",
      "layout_variant": {"arrangement": "single-column", ...},
      "element_map": {"text_boxes": 2, "image_placeholders": 0, ...},
      "text_structure": [{"role": "title", "position": "center", ...}],
      "design_tokens": {"primary_color": "#1A1A2E", ...},
      "content_constraints": {"max_title_chars": 40, ...}
    }
  ]
}
```

## 分类规则

### 封面检测
- 第 1 页 + 文本框 ≤ 4 个 → `cover`

### 尾页检测
- 最后一页 + 文本框 ≤ 3 个 → `ending`

### 目录检测
- 前 3 页 + 含 "目录/CONTENTS/AGENDA" → `toc`

### 图片页检测
- 含 1 个图片位 + 0-1 个文本框 → `image-full`
- 图片位在左侧 → `image-left`
- 图片位在右侧 → `image-right`

### 图表/表格检测
- 含图表占位符 → `chart`
- 含表格占位符 → `table`

### 多栏检测
- 文本框 ≥ 7 个 → `content-3col`
- 文本框 ≥ 5 个 → `content-2col`

### 章节页检测
- 非首页 + 文本框 ≤ 3 个 + 有标题槽 + 极少正文 → `section-header`

## 反例（禁止）

- ❌ 不检查文件是否存在就直接解析 — 会抛出不易理解的错误
- ❌ 大量模板不先建设计令牌就入库 — 后续匹配缺少关键信息
- ❌ 用 PPTEngine 的默认库路径替代用户指定的路径 — 用户可能要多库管理
- ❌ 忽略解析错误 — 某页失败不应阻塞整批处理

## 失败模式

| 场景 | 原因 | 处理 |
|------|------|------|
| 文件不存在 | 路径错误 | 提示用户检查路径 |
| 非 .pptx 格式 | 旧版 .ppt | 提示需转换为 .pptx |
| 幻灯片无内容 | 空模板 | 跳过该页，标注 quality_score=0 |
| 字体/颜色提取失败 | 缺少字体信息 | 设计令牌字段留空，标记 incomplete |
| 分类不准确 | 规则覆盖不足 | 标记为 PageType.UNKNOWN，后续可人工修正 |
| JSON 序列化失败 | 特殊字符 | 捕获异常，跳过该字段 |

## 关联技能

- **downstream → `ppt-template-filler`**：解析入库后，由 template-filler 查询页面库并组装新 PPT
