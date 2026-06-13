# 粗野主义双亚型 · Brutalist Dual Archetypes

> 吸收自 upstream taste-skill/brutalist-skill（粗野UI风格预设）
> 用于 huashu-design 的 brutalist 方向。二选一，不混用。

## 亚型一：Swiss Industrial Print（瑞士工业印刷）

**特征**：1960年代企业识别系统 + 重工业蓝图
**模式**：高对比浅色（新闻纸/米白底材）

### 色彩
```
Background:  #F4F4F0 或 #EAE8E3（哑光未漂白文档纸）
Foreground:  #050505 到 #111111（碳墨）
Accent:      #E61919 或 #FF2A2A（航空/危险红）——这是唯一的 accent
```

### 排版
```
Macro-Type（结构性标题）：
  分类：Neo-Grotesque / Heavy Sans
  字体：Neue Haas Grotesk (Black), Inter (Extra Bold/Black), Archivo Black
  比例：clamp(4rem, 10vw, 15rem)
  tracking：-0.03em 到 -0.06em（极度紧凑）
  leading：0.85 到 0.95（极度压缩）
  大小写：全部大写

Micro-Type（数据/遥测）：
  分类：Monospace / Technical Sans
  字体：JetBrains Mono, IBM Plex Mono, Space Mono
  比例：10px-14px（0.7rem-0.875rem）
  tracking：0.05em-0.1em（打字机间距）
  大小写：全部大写
```

### 关键视觉手法
- 可见的结构分割线
- 激进的非对称负空间
- 溢出视口的超大数字或字母
- 红色删除线——穿过标题的粗红横线

---

## 亚型二：Tactical Telemetry CRT（战术遥测终端）

**特征**：军事数据库/遗留大型机/航天HUD
**模式**：深度暗色 + CRT 荧光感

### 色彩
```
Background:  #0A0A0A 或 #121212（消活的 CRT，避免纯黑 #000）
Foreground:  #C8C8C8 或 #BEBEBE（磷光文本）
Accent:      #00FF41（经典CRT绿）或 #FF6B35（军用琥珀）
```

### 排版
同上 Swiss Print，但：
- 必须是深色模式（暗底亮字）
- Monospace 占绝对主导地位
- 引入 ASCII 框架装置（方括号、十字准线）

### 关键视觉手法
- 高密度表格数据
- ASCII 框架：[ TARGET ACQUIRED ] / +---[ SYS ]---+
- 扫描线覆盖（CSS：repeating-linear-gradient 模拟 CRT 行）
- 半色调/抖动效果
- 磷光 glow（text-shadow 模拟 CRT 余辉）

### CRT 特效 CSS 片段
```css
/* 扫描线 */
.crt-scanlines {
  background: repeating-linear-gradient(
    0deg,
    rgba(0,0,0,0.15) 0px,
    rgba(0,0,0,0.15) 1px,
    transparent 1px,
    transparent 2px
  );
}
/* 文本发光 */
.crt-glow {
  text-shadow: 0 0 5px rgba(0,255,65,0.5),
               0 0 10px rgba(0,255,65,0.2);
}
```

## 选择指南

| 场景 | 选 |
|------|------|
| 数据密集仪表盘、系统监控 | CRT Terminal |
| 品牌宣言页、编辑特稿、设计 studio portfolio | Swiss Print |
| 两者都要（错误） | ⛔ 选一个，全文统一 |

## 文本对比层（艺术性破坏）

两种亚型都可引入一个"对比层"：高对比衬线字体（Playfair Display / EB Garamond）→ 但必须经过半色调滤镜或 1-bit 抖动处理，以破坏矢量完美——制造纹理对比。
