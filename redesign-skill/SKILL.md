---
name: redesign-skill
description: 系统性页面升级方法论——对现有网页进行审计→诊断→修复的完整流程。覆盖排版/色彩/布局/交互/内容/组件/代码7大维度、60+检查项，含优先级排序。与hallmark互补：hallmark管生成后的质量门禁，本技能管已有页面的升级路径。适应自 Leonxlnx/taste-skill 的 redesign-skill (MIT)。
version: 1.0.0
license: MIT (adapted from Leonxlnx/taste-skill)
triggers:
  - redesign
  - 升级设计
  - 翻新页面
  - 设计审计
  - design audit
  - 页面改造
  - 视觉升级
  - 重构UI
  - 优化现有页面
  - 改善动画
  - 审计运动
  - improve animations
  - audit motion
  - 动画优化
  - 让这个感觉更好
  - make this feel better
  - 动画改进计划
metadata:
  hermes:
    tags: [redesign, audit, upgrade, quality, anti-slop]
    related_skills: [huashu-design, hallmark, taste-skill, apple-design, emil-design-eng, find-animation-opportunities]
    scope: interface-upgrade
  upstream: https://github.com/Leonxlnx/taste-skill/tree/main/skills/redesign-skill (MIT)
---

# Redesign Skill · 页面系统性升级

**定位**：对**已有**网页进行系统性的设计审计和阶梯式升级。不是从零设计，而是在现有基础上做手术式改进。

```
redesign-skill 🔧      → huashu-design 🎨       → hallmark 🛡️
（审计+诊断+优先级）       （执行升级改造）           （验证升级后质量）
```

## 与 hallmark 的关系

| | redesign-skill | hallmark |
|--|---------------|----------|
| 职责 | **升级路径**——发现什么问题、按什么顺序修 | **质量门禁**——通过/不通过 |
| 对象 | 已有页面（可跑的代码） | 新生成的页面或升级后的页面 |
| 输出 | 审计报告 + 优先级修复计划 | 58关卡 pass/fail 结果 |
| 触发时机 | 升级任务开始时 | 升级完成后、部署前 |

**两者互补，不重叠**。redesign-skill 管"怎么改"，hallmark 管"改完对不对"。

## 触发条件

| 触发词 | 场景 |
|--------|------|
| "redesign" / "翻新这个页面" / "升级设计" | 明确要求升级已有页面 |
| "设计审计" / "帮我看看这个页面有什么问题" | 只需要审计，不一定要改 |
| "优化UI" / "视觉升级" | 局部或全局视觉提升 |

**不触发**：从零做新页面（走 huashu-design）；只需要质量检查（走 hallmark）。

---

## 工作流

### 阶段一：Scan（读取代码库）

1. 读取目标页面的完整代码
2. 识别技术栈：框架（React/Vue/vanilla）、样式方案（Tailwind/vanilla CSS/styled-components）
3. 识别当前设计模式：使用的字体、色板、布局方式、组件结构

### 阶段二：Diagnose（审计清单）

按以下 7 大维度对照检查，列出每一项的问题：

#### 1. 排版（8项）

- 是否全用 Inter / 系统默认字体？→ 替换为有性格的字体（Geist / Outfit / 中文字体按场景）
- Headline 是否有存在感？→ 加大字号、收紧 letter-spacing、降低 line-height
- 正文是否过宽？→ 限制到 ~65字符宽度，增加 line-height
- 是否只用 400 + 700 字重？→ 引入 500/600 中间字重
- 数字是否用比例字体？→ 数据密集界面用等宽或 tabular-nums
- 是否有 orphaned words（末行孤词）？→ text-wrap: balance / pretty
- 大写标题是否到处滥用？→ 尝试小写斜体/句首大写/小型大写
- letter-spacing 是否需要调整？→ 大标题负 tracking，小标签正 tracking

#### 2. 色彩与表面（11项）

- 是否纯黑 `#000000` 背景？→ 替换为 off-black `#0a0a0a` / `#121212`
- accent 是否过饱和？→ 饱和度降到 80% 以下
- 是否超过1个 accent 色？→ 选一个，删其余的
- 是否暖冷灰混用？→ 统一个灰色家族
- 是否有紫蓝 "AI渐变" 审美？→ 换成中性底色 + 单一经过考量的 accent
- box-shadow 是否通用黑色？→ 给阴影着色，匹配背景色调
- 是否平面无纹理？→ 添加微噪点/颗粒/微图案
- 渐变是否完美均匀？→ 用径向渐变/噪点覆盖/mesh渐变打破均匀
- 光照方向是否不一致？→ 审计所有阴影确保单一光源
- 浅色页面中间是否突兀出现深色 section？→ 统一背景调性
- 空白 section 是否无视觉深度？→ 添加高质量背景图/环境渐变

#### 3. 布局（13项）

- 是否一切居中对称？→ 用偏置边距/混合比例/左对齐标题打破
- 是否三列等宽卡片作为 feature row？→ AI最通用的布局，替换为 zig-zag/非对称/横向滚动
- 是否用 `height: 100vh`？→ 替换为 `min-height: 100dvh`（iOS Safari 跳变）
- 是否复杂 flexbox 百分比计算？→ 换 CSS Grid
- 是否无 max-width 容器？→ 添加 1200-1440px 约束
- 卡片是否强制等高？→ 允许变化高度或 masonry
- 圆角是否全统一？→ 内部元素紧、容器软
- 是否无层叠/深度？→ 负 margin 制造层次
- padding 是否对称？→ 视觉微调，底部通常需要稍大
- Dashboard 是否总是左侧栏？→ 尝试顶导/浮动命令菜单
- 是否缺少留白？→ 翻倍间距
- 按钮在卡片组中是否不底对齐？→ 固定CTA于卡片底部
- side-by-side 元素基线是否对齐？→ 统一标题/描述/价格/按钮的垂直位置

#### 4. 交互与状态（11项）

- 按钮是否无 hover 态？→ 添加背景色变化/微缩放/位移
- 是否无 active/pressed 反馈？→ scale(0.98) 或 translateY(1px)
- 过渡是否瞬间？→ 200-300ms 平滑过渡
- 是否缺 focus ring？→ 可见的键盘导航焦点指示器
- 是否无 loading 态？→ 骨架屏替代圆形 spinner
- 是否无 empty 态？→ 设计 "getting started" 引导视图
- 是否无 error 态？→ 行内清晰的错误消息
- 是否有死链接（href="#"）？→ 链接到真实目标或视觉禁用
- 导航是否缺当前页指示？→ 激活态样式区分
- 锚点是否跳变？→ scroll-behavior: smooth
- 动画是否用 top/left/width/height？→ 换 transform + opacity

#### 5. 内容（11项）

- 是否有 "John Doe" / "Jane Smith"？→ 多样、真实感的姓名
- 是否有假整数数据（99.99% / $100.00）？→ 有机不规则数据
- 是否有占位公司名（Acme Corp / Nexus / SmartFlow）？→ 上下文可信的品牌名
- 是否有 AI 文案 cliché？→ 禁止："Elevate" "Seamless" "Unleash" "Next-Gen" "Game-changer" "Delve" "Tapestry" "In the world of..."
- 成功消息是否有感叹号？→ 去掉，要自信不要喧哗
- 错误消息是否有 "Oops!"？→ 直接："连接失败，请重试"
- 是否被动语态？→ 主动语态
- 博客日期是否全相同？→ 随机化
- 多人是否用同一头像？→ 每人独立资产
- 是否有 Lorem Ipsum？→ 写真实草稿文案
- 是否每个标题都用 Title Case？→ 用 sentence case

#### 6. 组件模式（10项）

- 通用卡片样式（border+shadow+白底）→ 去掉 border，或只用背景色，或只用间距
- 总是一填一虚两个按钮 → 增加 text link 或三级样式
- 药丸 "New"/"Beta" 徽章 → 试方形徽章/旗标/纯文字标签
- Accordion FAQ → 换并排列表/可搜索帮助/行内渐进展开
- 3-card 轮播 + 点 → 换 masonry 墙/嵌入社交帖子/单条旋转引语
- 3-tower 定价表 → 用颜色和强调突出推荐 tier
- 什么都是 Modal → 行内编辑/滑出面板/展开区域
- 全是圆头像 → 试 squircle 或圆角方形
- 亮暗切换总是太阳/月亮 → 下拉/系统偏好检测/集成到设置
- Footer 4列链接农场 → 简化，聚焦主导航和法律必需链接

#### 7. 代码质量（9项）

- div soup → 语义 HTML：nav / main / article / aside / section
- 行内样式混 CSS 类 → 统一到样式系统
- 硬编码 px → 相对单位（% / rem / em / max-width）
- 缺 alt text → 描述图片内容
- 随意 z-index（9999）→ 建立主题变量中的清晰层级
- 注释掉的死代码 → 发布前删除
- import 幻觉 → 检查 package.json 实际依赖
- 缺 meta tags → title / description / og:image / social sharing

#### 战略遗漏（AI 经常忘的）

- 缺法律链接 → footer 加隐私政策/服务条款
- 缺返回导航 → 每页要有返回路径
- 缺 404 页面 → 设计有帮助的品牌化 "page not found"
- 缺表单验证 → 客户端验证 email/必填字段/格式
- 缺 skip-to-content → 键盘用户必需
- 缺 cookie consent → 如需，加合规横幅

### 阶段三：Fix（按优先级执行）

**修复优先级**（最大视觉冲击 + 最小风险）：

| 优先级 | 范围 | 理由 |
|:--:|------|------|
| 1 | **字体替换** | 瞬间最大改善，最低风险 |
| 2 | **调色板清理** | 清除冲突或过饱和颜色 |
| 3 | **hover/active 态** | 让界面活起来 |
| 4 | **布局和间距** | 统一网格/max-width/padding |
| 5 | **替换通用组件** | 换掉 cliché 模式 |
| 6 | **添加 loading/empty/error 态** | 让页面感觉完成 |
| 7 | **排版精修** | 字重层级/行距/letter-spacing——锦上添花 |

---

## 规则

- **不动现有技术栈**——不迁移框架或样式库
- **不破坏现有功能**——每次改动后验证
- 引入任何新库前先检查项目依赖
- 如果项目用 Tailwind，检查版本（v3 vs v4）
- 如果项目无框架，用 vanilla CSS
- 改动可控、可审查——小步定向改进，不大拆大建

## 动画审计与优化（融合自 improve-animations）

当用户要求"改善动画"、"审计运动"、"让这个app感觉更好"时，执行以下动画审计与优化流程：

### 定位

使用高级模型完成判断复合的部分——理解代码库的运动、决定什么值得修复、编写规范——然后将执行交给任何代理，包括更便宜的模型。它**只做一件事**：调查动画和运动代码，然后生成优先级发现和实施计划。它不审查单个diff（那是 hallmark 的动画审查），也不自己实施修复。

### 硬规则

1. **永远不修改源代码。** 你创建或编辑的唯一文件在 `plans/`（或 `animation-plans/`）下。如果被要求"直接修复"，拒绝并指向执行计划。
2. **没有变更操作。** 没有安装、没有副作用的构建、没有提交、没有格式化。只读分析。
3. **计划必须完全自包含。** 执行者没有这个对话的上下文和品味。永远不要写"使用上面讨论的缓动"——内联确切的三次贝塞尔、确切的持续时间、确切的文件路径和代码摘录。

### 工作流

#### 阶段一——侦察（始终先做）

在判断之前映射运动表面：
- **技术栈**：框架、运动库（Framer Motion/Motion、React Spring、GSAP、纯CSS、WAAPI）、组件库
- **运动在哪**：全局CSS/tokens、Tailwind配置、关键帧定义、transition/animate props、手势处理器
- **惯例**：现有的缓动tokens、持续时间尺度、弹簧配置
- **个性**：这是俏皮的消费者应用还是清脆的仪表盘？
- **频率图**：哪些动画元素每天被命中100+次 vs 偶尔 vs 稀少

有用的扫描：grep `transition`、`animation`、`@keyframes`、`ease-in`、`transition: all`、`scale(0)`、`prefers-reduced-motion`、`transform-origin`

#### 阶段二——审计

按以下8个类别审计：
1. 目的与频率
2. 缓动与持续时间
3. 物理性与起源
4. 可中断性
5. 性能
6. 无障碍
7. 内聚力与tokens
8. 错过的机会

#### 阶段三——审查、优先级、确认

对每个发现重新阅读引用的代码。拒绝任何设计好的、误归因的、重复的或豁免的。

呈现审查后的发现为一个表，按杠杆（影响÷努力）排序：

| # | 严重性 | 类别 | 位置 | 发现 | 修复摘要 |
|---|--------|------|------|------|---------|

严重性：**高** = 感觉破坏（UI上错误缓动、键盘/高频操作上的动画、掉帧、`scale(0)`）；**中** = 明显偏离（错误起源、不可中断的动态UI、缺少减弱动效）；**低** = 打磨（错开、模糊遮罩交叉淡入、token整合）

#### 阶段四——编写计划

每个选定发现一个计划，写入 `plans/` 为 `NNN-short-slug.md`。

每个计划包含：
- 确切的文件路径和当前代码摘录
- 确切的目标值（三次贝塞尔、持续时间、弹簧配置）
- 有序步骤
- 硬范围边界
- 验证部分（如何*感觉检查*结果：慢动作、逐帧、真实设备）

### 优先级修复偏好层级

1. **删除动画**（高频/无目的/键盘触发）
2. **减少它** — 更短持续时间、更小变换、更少动画属性
3. **修复缓动** — `ease-in`→`ease-out`/自定义曲线
4. **修复起源/物理性** — 纠正 `transform-origin`；替换 `scale(0)`
5. **使其可中断** — 关键帧→transitions或弹簧
6. **移到GPU** — 布局属性→`transform`/`opacity`
7. **非对称计时** — 慢故意阶段，快速响应
8. **打磨** — 模糊遮罩交叉淡入、错开、`@starting-style`
9. **无障碍与内聚力** — 添加减弱动效+悬停门控

### 调用变体

| 调用 | 行为 |
|------|------|
| 裸调用 | 完整工作流：侦察→审计所有类别→审查→确认→计划 |
| `quick` / `deep` | 调整审计努力 |
| 类别焦点 | 侦察+仅审计该类别 |
| `plan <描述>` | 跳过审计；侦察刚好足够指定，然后写一个计划 |
| `reconcile` | 重新检查 `plans/` 对当前代码：标记完成计划，刷新过时引用 |

---

## 与设计管线的关系

```
taste-skill 🔮     →  redesign-skill 🔧  →  huashu-design 🎨  →  hallmark 🛡️
（定升级方向）         （审计+诊断+优先级）    （执行升级改造）       （验证升级后质量）
```

redesign-skill 可以用 taste-skill 的方向参数来约束升级方向——比如 V/M/D 旋钮告诉 huashu 在执行升级时往哪个方向偏。

## 技术说明

- **上游**：https://github.com/Leonxlnx/taste-skill/tree/main/skills/redesign-skill (MIT)
- **本技能** 吸收上游的完整审计+诊断+修复方法论，但排除：
  - ❌ Tailwind 特定类名引用 → 改为框架无关描述
  - ❌ Codex/Cursor 特定执行指令 → 改为 Hermes 通用的 CSS 语义描述
  - ❌ 图片相关替换规则（Unsplash/picsum 等）→ Hermes 有自己的图片生成管线
- **新增**：与 hallmark 的集成点——升级完成后自动触发 hallmark 验证
