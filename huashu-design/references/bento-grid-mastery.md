# Bento 网格精通 · Bento Grid Mastery

> 吸收自 upstream taste-skill/gpt-tasteskill 的 gapless bento grid + 2-line hero rule
> 用于 huashu-design 的网格布局质量规则

## 无缝 Bento 网格（Gapless Bento Grid）

AI 生成的 Bento 网格常留下空白死格。以下规则防止这一点：

### 规则
1. **必须使用 `grid-auto-flow: dense`**——让浏览器自动填充空隙
2. **数学验证 `col-span` 和 `row-span` 互锁**——在写代码前人工验证行列总和
3. **禁止空白角/空洞**——每个网格位置都必须有内容

### 验证公式
```
总列数 × 总行数 = 期望总单元格数
实际所有卡片的 (col-span × row-span) 之和 必须 ≈ 期望总单元格数
```

### 反模式
```
❌ 4列3行网格，放了三个 col-span-2 卡片 = 有6个空位
✅ 4列3行，一个 col-span-2 row-span-2 + 四个 col-span-1 + 若干填满
```

## 2行 Hero 铁律

Hero 的 H1 绝对不允许超过 2-3 行。4、5、6 行是灾难性失败。

### 防止手段
1. **用超宽容器**：`max-w-5xl` / `max-w-6xl` / `w-full`——让文字横向流动
2. **降低字号**：`clamp(3rem, 5vw, 5.5rem)` 而非 `clamp(4rem, 8vw, 8rem)`
3. **缩短文案**：如果文案本身太长，改文案——不改字号、不缩容器

### Hero 禁止清单
- 禁止在 Hero 中放浮动 stamp/badge 图标
- 禁止 Hero 下接药丸标签
- 禁止在 Hero 中堆原始数据/统计数字
- 禁止 Hero 中出现"Scroll to explore" "Swipe down" 或滚动箭头

## AIDA 页面结构（gpt-tasteskill 吸收）

每一页都应遵循 AIDA：

| 阶段 | 内容 | 技术 |
|------|------|------|
| **Attention** (Hero) | 电影感、干净、宽布局 | 2行铁律 + 9变体构图 |
| **Interest** (Features/Bento) | 高密度、数学完美的网格 | 无缝 Bento 规则 |
| **Desire** (GSAP/Motion) | 固定 section、横向滚动、文字揭露 | GSAP ScrollTrigger |
| **Action** (Footer/CTA) | 大对比 CTA + 干净链接 | 简洁 Footer |
