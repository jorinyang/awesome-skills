---
name: taste-skill
description: 设计方向指引——在huashu-design执行前，通过Brief推断+三旋钮(VARIANCE/MOTION/DENSITY)+风格预设，为设计提供量化的方向参数。定位为设计管线的第一环（方向→执行→验证）。适应自 Leonxlnx/taste-skill (MIT)。
metadata:
  hermes:
    tags: [design, direction, pre-generation, tuning, anti-slop]
    related_skills: [huashu-design, hallmark, design-md, double-evolution]
    scope: design-direction
    pipeline: brandkit(策略) → taste-skill(方向) → huashu-design(执行) → hallmark(门禁)
  upstream: https://github.com/Leonxlnx/taste-skill (MIT, by Leonxlnx)
version: 1.0.0
license: MIT (adapted from Leonxlnx/taste-skill)
triggers:
  - 设计方向
  - taste skill
  - 设计调参
  - 设计基调
  - 风格方向
  - 视觉方向
  - 帮我定设计方向
  - 这个页面应该什么风格
---

# Taste Skill · 设计方向指引

**定位**：设计管线第一环。在 `huashu-design`（执行）和 `hallmark`（验证）之前运行。

```
taste-skill 🔮          → huashu-design 🎨       → hallmark 🛡️
（方向指引+预检）          （创意执行）              （质量门禁）
    ↓                        ↓                        ↓
Brief推断+三旋钮            20种设计哲学              58道关卡
风格预设+Design Read        品牌资产协议              六轴自评
```

---

## ⚠️ 三技能边界（必读）

### taste-skill vs huashu-design

| 维度 | taste-skill（本技能） | huashu-design |
|------|----------------------|---------------|
| **职责** | 回答"**往哪个方向做**" | 回答"**怎么做好**" |
| **输出** | Design Read + 旋钮值 + 风格预设 | HTML原型/动画/幻灯片/品牌全案 |
| **粒度** | 可量化参数（7/6/4） | 设计执行（色板/字体/布局/动效） |
| **触发时机** | huashu 加载**之前** | taste 产出方向参数**之后** |
| **主导权** | taste 设定上限（如MOTION≤4则huashu不添加动效） | huashu 在taste设定的范围内自由创作 |

**冲突裁决**：当两者对同一设计决策有不同意见时，**taste 的方向参数是硬约束，huashu 在此约束内创作**。

### taste-skill vs hallmark

| 维度 | taste-skill（本技能） | hallmark |
|------|----------------------|----------|
| **职责** | **生成前**的方向指引 | **生成后**的质量门禁 |
| **时机** | 设计开始前 | 设计完成后、部署前 |
| **操作对象** | 设计意图（还没写代码） | 设计产出（已完成的HTML/CSS） |
| **典型动作** | "这个页面的MOTION设3，不要动效" | "检查这个页面有没有transition:all" |
| **主导权** | taste的预检在生成前；hallmark的关卡在生成后 | 两者不冲突——taste管"别往那个方向做"，hallmark管"做的结果对不对" |

**规则重叠处理**：当同一条反slop规则在taste和hallmark中都出现时：
- taste版本是**方向性约束**（"不要用Inter做display字体"=告诉huashu别选Inter）
- hallmark版本是**验证性检查**（"检查display字体是不是Inter"=验证huashu没选Inter）
- 如果taste说"本次允许Inter"（override），hallmark的对应关卡自动放行

---

## 触发条件

| 触发词 | 场景 |
|--------|------|
| "帮我定设计方向" / "这个页面应该什么风格" | 用户需要设计方向指引 |
| "taste skill" / "设计调参" / "设计基调" | 显式调用 |
| 在 huashu-design 加载前 | 自动触发（作为设计管线第一环） |

**不触发**：功能页面（SPA/后台/工具）的纯功能设计；已有明确品牌规范且不涉及新视觉方向。系统性页面（表格/表单/仪表盘）跳过 taste。

---

## 工作流

### Step 0: Brief 推断（读场景，不猜审美）

在触碰代码或旋钮之前，从用户需求中提取以下信号：

1. **页面类型** — landing(SaaS/消费/机构/活动)、portfolio(开发/设计/创意)、redesign(保留/翻新)、编辑/博客
2. **氛围词** — 用户说了什么？"极简""沉稳""Linear风""活泼""B2B严肃""编辑感""创意机构"
3. **参考信号** — 用户提供的链接/截图/品牌名/竞品
4. **受众** — B2B采购决策者 / 设计敏感的消费者 / 浏览portfolio的HR / 公众
5. **已有品牌资产** — Logo/色值/字体/产品图（redesign必须读取）
6. **隐式约束** — 无障碍优先/公共部门/合规行业/信任优先

**输出一句 "Design Read"**（在生成任何代码之前）：

> *"Reading this as: {页面类型} for {受众}, with a {氛围} language, leaning toward {设计系统或美学方向}."*

例：
- *"Reading this as: B2B SaaS landing for technical buyers, with a Linear-style minimalist language."*
- *"Reading this as: 文旅品牌 landing for 中产消费者, with a 自然系/留白 language."*

**如果brief模糊**：问**一个**问题，不多问。例：*"这个页面应该更接近Linear极简还是Awwwards创意实验？"* 能自信推断就不问。

---

### Step 1: 三旋钮调参

基于 Design Read 设定三个旋钮。这是传给 huashu-design 的核心参数。

| 旋钮 | 范围 | 含义 |
|------|:--:|------|
| **VARIANCE** | 1-10 | 1=完美对称 10=艺术性混乱 |
| **MOTION** | 1-10 | 1=静态 10=电影级动效 |
| **DENSITY** | 1-10 | 1=美术馆留白 10=驾驶舱数据密度 |

**默认值**: `V8 / M6 / D4`。以下信号会覆盖：

| 用户信号 | VARIANCE | MOTION | DENSITY |
|----------|:--:|:--:|:--:|
| "极简/干净/沉稳/编辑感/Linear风" | 5-6 | 3-4 | 2-3 |
| "高端消费/Apple感/奢侈品/品牌" | 7-8 | 5-7 | 3-4 |
| "活泼/创意/Dribbble/Awwwards/实验" | 9-10 | 8-10 | 3-4 |
| "landing/portfolio/营销站(默认)" | 7-9 | 6-8 | 3-5 |
| "信任优先/公共部门/合规/无障碍" | 3-4 | 2-3 | 4-5 |
| "redesign-保留" | 匹配现状 | +1 | 匹配现状 |
| "redesign-翻新" | +2 | +2 | 匹配现状 |

**传递方式**：设定后写入 Design Read，huashu-design 在加载时读取。

---

### Step 2: 风格预设映射

taste-skill 的三个前端风格预设与 huashu-design 的 20 种设计哲学存在映射关系。**不在 taste 中重复定义 huashu 已有的内容，而是提供选择速查表**：

| taste 预设 | huashu 对应哲学 | 核心特征 | 何时选 |
|-----------|----------------|---------|--------|
| **soft-skill** (高端UI) | atmospheric / premium-consumer | 柔对比、大量留白、品牌字体、弹性动效(M5-7) | 高端消费品牌、奢侈、艺术 |
| **minimalist-skill** (极简UI) | editorial / modern-minimal | 克制调色板、清晰结构、Notion/Linear风格 | B2B SaaS、编辑内容、工具产品 |
| **brutalist-skill** (粗野UI) | brutalist | 硬机械语言、Swiss字体、强对比、实验布局 | 创意机构、设计studio、宣言页 |

**最佳实践**：
- taste 产出"选哪个风格" → huashu 加载对应设计哲学执行
- 不在 taste 中展开具体配色/字体规则（那是 huashu + design-md 的职责）
- taste 只负责**选方向**，不负责**做设计**

---

### Step 3: 预检（Pre-Flight Check）

在 huashu-design 开始执行前，跑以下机械检查。这是 taste 和 hallmark 的分界线——taste 预检在**生成前**，hallmark 关卡在**生成后**。

| # | 检查项 | 不通过则 |
|---|--------|---------|
| 1 | Design Read 是否已输出？ | 回到 Step 0 |
| 2 | 三个旋钮值是否已设定？ | 回到 Step 1 |
| 3 | 风格预设是否已选择？ | 回到 Step 2 |
| 4 | 页面类型是否匹配风格预设？（如公共部门不应选 brutalist） | 重新选 |
| 5 | MOTION > 4 是否在非营销/非品牌页面？（弱动效场景设了高动效） | 降 MOTION |
| 6 | 有无明确的品牌资产未读取？（logo/色值/字体未被读取） | 读取后再继续 |

**通过预检** → 将 Design Read + 旋钮值 + 风格预设传给 huashu-design，进入执行阶段。

---

## 与 huashu-design 的交互协议

```
用户需求
    │
    ▼
taste-skill  ← 本技能
    │ 输出: Design Read + V/M/D 旋钮值 + 风格预设
    │ 传给: huashu-design（通过对话上下文）
    ▼
huashu-design
    │ 读取 taste 的方向参数
    │ 在 taste 设定的 V/M/D 范围内执行设计
    │   VARIANCE → 影响布局不对称度
    │   MOTION   → 影响动效强度和类型选择
    │   DENSITY  → 影响信息密度和留白比例
    │ 加载 design-md 获取品牌 token
    │ 产出 HTML
    ▼
hallmark
    │ 验证产出是否符合 taste 的方向约束
    │ 如果 taste 允许了某项（如Inter字体），
    │   hallmark 对应关卡自动放行
    │ 58道关卡检查
    ▼
feishu-html（部署）
```

---

## 技术说明

- **上游**：https://github.com/Leonxlnx/taste-skill (MIT, 42.7K stars)
- **本技能** 吸收上游的核心方法论（三旋钮 + Brief推断 + 预检 + 风格预设映射），但排除：
  - ❌ 具体CSS/Tailwind/React实现规则 → 那是huashu-design的职责
  - ❌ GSAP动效代码骨架 → huashu-design已有完整动画系统
  - ❌ 设计系统安装指令（Fluent/Carbon/Material等）→ 与Hermes场景无关
  - ❌ 图片生成技能（imagegen-*）→ jimeng-video已覆盖
  - ❌ image-to-code管线 → 暂不吸收，Hermes以文本→代码为主
- **与 hallmark 的规则重叠**：taste 的规则是"方向性约束"，hallmark 的规则是"验证性检查"。taste 的 override 对 hallmark 生效。
- **与 huashu-design 的风格重叠**：taste 的三个风格预设映射到 huashu 的 20 种设计哲学。taste 选方向，huashu 做执行。
