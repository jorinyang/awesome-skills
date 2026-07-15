# DashiAI PPT 方法论参考笔记

> 🟡 参考借鉴：以下内容不直接吸收，作为方法论参考供未来 PPT 技能演进时查阅。

## 1. 版式查询系统

```
layout:query --theme X --role cover --limit 8
layout:query --theme X --role chart --needs-media --limit 8
```

**设计亮点**：
- 按「主题+角色」二维查询，而非遍历所有页面
- 支持 `--needs-media`、`--planned-images N`、`--provided-images N`、`--image-gen` 精确控制媒体槽需求
- 每次查询结果随机排序（seed 可控），避免 Agent 总选第一条

**可借鉴**：我们现有 `PageLibrary` 只按 `page_type` 查询，缺少「媒体需求」维度和随机化。未来可加。

## 2. props:safe 安全写入

在填充 JSON props 前运行契约校验：
- `copyKeys`: 可安全改写的字段白名单
- `copyBudgets`: 文案长度预算（超长会被 `validate:goal-spec` 拦截）
- `propShapes`: 对象/数组字段的内部形状约束
- `contentLocked: true`: 页面内容由组件固定，不可改写

**设计哲学**：「锁模板填文案」——默认不改任何非文案 props。这与我们的 `PPTEngine.fill()` 的「填内容不破坏结构」理念一致，但 DashiAI 的实现更严格（白名单制而非角色推断）。

**可借鉴**：未来可在 `ContentAnalyzer` 中引入 `copyBudget` 检查（当前只检查标题/行数容量，不检查字段级字数上限）。

## 3. 三层校验体系

| 校验 | 阶段 | 检查内容 |
|------|------|---------|
| `validate:goal-spec` | 渲染前 | JSON 结构合规、字段长度、必填项 |
| `validate:swiss` | 渲染后 | HTML 完整性、页面数、资源引用 |
| `validate:goal-copy` | 渲染后 | 确认所有 `copyKeys` 文案已覆盖模板默认值 |

**设计亮点**：第三层 `goal-copy` 专门检查「是否残留模板默认文案」——这是 PPT 生成中最常见的质量问题（用户收到带「AI Capital」「SoundWave」等占位文案的页面）。

**可借鉴**：我们的 `TemplateFiller` Phase 4 校验只检查页数/形状/文本填充，缺少「占位文案残留检查」。这是一个现实的改进点。

## 4. 分析模型版式

内置以下分析模型的专用版式：
- SWOT 分析
- 波特五力
- PEST 分析
- 商业模式画布 (BMC)
- 双钻模型
- 甘特图、桑基图、漏斗图、热力图

**价值**：咨询场景下不需要手动画分析框架，直接选页填数据即可。

**局限**：这些是固定版式，不是通用绘图引擎。客户有自定义分析框架时无法适配。

## 5. 浏览器内编辑控制台

生成后每页自带控制台，可实时调节：
- 模块数量（slider）
- 布局切换
- 图表类型切换
- 配色切换
- 翻页动画
- 明暗模式

**设计哲学**：「生成后如何编辑，比生成本身更重要」——这个理念我们的 PPT 管线完全缺失。我们的 `TemplateFiller` 输出的是静态 PPTX，用户只能手工编辑。DashiAI 的 HTML-first 方案天然支持交互编辑。

**启示**：我们的 PPTX-native 路径无法做到浏览器内编辑（PPTX 不可在浏览器内交互操作）。但在「交互编辑」和「PPTX 原生保真度」之间，存在一个权衡：如果我们未来需要交互编辑能力，考虑 HTML 中间态方案。

## 6. 12 主题设计令牌系统

每套主题是独立的设计系统（配色、字体、间距、装饰元素统一），而非松散的颜色变量集合。

**与我们的对比**：
- 我们：解析真实 PPTX 模板的设计令牌（`primary_color`、`font_title`、`body_size_pt`、`spacing`）
- DashiAI：预置 12 套完整设计令牌，捆绑在组件库中

**优劣**：我们的方法更灵活（任何 PPTX 都可解析），DashiAI 的方法更稳定（12 套经过人工验收的设计系统）。本质上不是竞争关系——我们的 pipeline 做「模板即设计系统」，DashiAI 做「预验收设计系统」。

---

> 来源：https://github.com/chuspeeism/dashiAI-ppt-skill | 记录日期 2026-07-12
