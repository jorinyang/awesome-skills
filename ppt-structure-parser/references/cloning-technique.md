# 跨模板形状克隆技术验证

> 验证日期: 2026-07-01 | 引擎版本: v1.0.0

## 核心发现

**形状克隆完全可行，无需母版合并。**

### 已验证的技术点

| 技术点 | 方法 | 结果 |
|--------|------|:---:|
| 文本框克隆 | `deepcopy(shape._element)` → `target.spTree.append()` | ✅ 文本+格式完整保留 |
| 自动形状克隆 | 同上，含圆角矩形等 | ✅ 形状类型+填充保留 |
| 跨模板克隆 | 不同母版的 PPT 之间 | ✅ 形状独立于母版 |
| 背景色提取 | `layout._element.find('.//a:srgbClr', ns)` | ✅ 从 layout 提取颜色值 |
| 背景应用到目标 | `target_slide.background.fill.solid()` + `RGBColor` | ✅ 直接填充成功 |

### 不可克隆的形状类型

| 类型 | 原因 | 替代方案 |
|------|------|---------|
| SmartArt | 复杂的多元素依赖 | 渲染为图片后再插入 |
| 图表 (Chart) | XML 引用外部数据 | 需重建图表对象 |
| 组合形状内的子形状 | deepcopy 可能丢失部分属性 | 拆分后逐元素克隆 |

### Python 环境要求

```bash
# PEP 668 环境必须用 venv
python3 -m venv .venv-ppt
source .venv-ppt/bin/activate
pip install python-pptx
```

## 已知陷阱

### PageStore truthiness

`PageStore` 定义了 `__len__` 返回页面数。Python 中当 `__len__` 返回 0 时，`__bool__` 返回 `False`。这导致空库时 `if page_store:` 判断失败。

**修复**: 显式添加 `__bool__` 返回 `True`，并将 `if page_store:` 改为 `if page_store is not None:`。

### features['shapes'] 是 dict 列表

`extract_shape_features()` 返回的 `features['shapes']` 是字典列表，不是 Shape 对象。访问属性需用 `s.get('text', '')` 而非 `s.shape.text`。

### 字体属性可能为 None

新建文本框的 `run.font.size`、`run.font.bold` 等可能为 `None`（继承自段落/母版）。提取时需检查 `None`。

### 颜色属性访问

`run.font.color.rgb` 在颜色为继承时抛出 `AttributeError: no .rgb property on color type '_NoneColor'`。需 try/except 包裹。
