---
name: brandkit
description: 品牌策略与Logo设计方法论——品牌策略推导、5种Logo概念手法、8种视觉模式、面板组合DNA。设计决策层，图片生成委派jimeng-video/ComfyUI执行。适应自 Leonxlnx/taste-skill 的 brandkit (MIT)。
version: 1.0.0
license: MIT (adapted from Leonxlnx/taste-skill)
triggers:
  - 品牌设计
  - Logo设计
  - 品牌视觉
  - brand kit
  - 品牌标识
  - 视觉系统
  - 品牌策略
  - 品牌形象
  - 做个Logo
  - 设计品牌
metadata:
  hermes:
    tags: [brand, identity, logo, design-strategy, visual-system]
    related_skills: [huashu-design, design-md, jimeng-video, taste-skill]
    scope: brand-identity-design
  upstream: https://github.com/Leonxlnx/taste-skill/tree/main/skills/brandkit (MIT)
---

# Brandkit · 品牌策略与Logo设计

**定位**：品牌设计的**决策层**——做品牌策略推导、Logo概念设计、视觉系统规划。图片生成委派给 `jimeng-video`（即梦）或 `ComfyUI` 执行。

```
brandkit 🔮              → jimeng-video / ComfyUI 🎨
（品牌策略+Logo方法论）       （图片生成执行）
```

## 触发条件

| 触发词 | 场景 |
|--------|------|
| "品牌设计" / "做个Logo" / "品牌视觉" | 从零设计品牌标识 |
| "brand kit" / "视觉系统" / "品牌形象" | 完整品牌系统规划 |
| 贵州之客子品牌 / 新业务线命名 | 内部品牌孵化 |

**不触发**：仅需要一张图片（走 jimeng-video 直调）、已有成熟品牌规范不涉及新视觉方向。

---

## 工作流

### Step 0: 品牌策略推导（先想，不画）

从用户需求中提取以下信号，回答五个核心问题：

| 问题 | 提取内容 |
|------|---------|
| 品类 | 开发者工具/AI助手/安全/游戏/语音/合规/无人机/奢侈/生产力/文旅 |
| 受众 | B2B采购决策者/设计敏感消费者/HR/公众/开发者 |
| 情感承诺 | 信任/速度/精准/创造力/保护/自由/专注 |
| 核心隐喻 | cursor→构建 frame→脚手架 shield→边界 spark→灵感 path→方向 |
| 品牌禁区 | 不能像什么、不能用什么颜色、不能表达什么情绪 |

**输出一句 Brand Strategy Read**：

> *"This is a {品类} brand for {受众}. Its emotional promise is {情感承诺}. The core metaphor is {隐喻}. It should feel {形容词}, never {反面形容词}."*

例：
- *"This is a developer tool brand for builders. Its emotional promise is speed and control. The core metaphor is a scaffold — structured growth. It should feel sharp and precise, never playful or decorative."*

### Step 1: 选择Logo概念手法（5选1-2）

基于品牌策略，从以下5种手法中选用1-2种：

| 手法 | 逻辑 | 适用 |
|------|------|------|
| **Monogram + 意义** | 品牌首字母融合隐喻（K+风筝、N+路径、S+声波） | 有明确首字母的品牌 |
| **产品动作** | 把核心功能变成符号（构建→框架、保护→盾牌、转换→箭头） | 功能明确的工具产品 |
| **隐喻融合** | 两个有意义的概念合成为一个精简标记（猫头鹰+无人机视觉、盾牌+山） | 需要多层次含义的品牌 |
| **负空间** | 用空白创造智慧感（隐藏箭头、保护中心、剪切首字母） | 追求巧妙和深度的品牌 |
| **几何构造** | 从网格/圆/对角线/模块出发构建（圆形切割、网格系统、轨道路径） | 技术/工程/系统感品牌 |

**规则**：
- Logo必须：简单、可记忆、有象征意义、可缩放、可拥有
- 禁止：通用闪电（除非强理由）、随机动物、伪奢侈徽章、复刻知名标记、过度复杂符号、clip-art风格图标
- 最多组合两种手法——三合一必崩

### Step 2: 选择视觉模式（8选1）

| 模式 | 适用 | 视觉线索 |
|------|------|---------|
| **Dark Developer** | 开发者工具、infra、自动化 | 近黑面板、等宽字体、命令行感、cyan/blue/coral accent |
| **Dark Product** | 商业工具、增长工具、销售 | 黑/深红/琥珀、发光UI芯片、卡片系统、进度/奖励 motif |
| **Dark Nature** | 策略、旅行、健康、低调SaaS | 深绿+lime accent、雾景、圆形图像UI、软叠加、编辑网格 |
| **Dark Security** | 安全、合规、监控、网络 | 黑/navy、盾形、雷达线、红/蓝警戒芯片 |
| **Light Editorial** | 法律、隐私、合规、文档 | 暖象牙白、纸纹、小衬线标签、印章/徽章、深蓝/红/金 |
| **Luxury** | 美容、时尚、酒店、高端服务 | 象牙/石材/咖啡、衬线文字标记、优雅字母组合、纸张颗粒 |
| **Voice** | 语音AI、聊天、助手、音频 | 深靛蓝+lilac辉光、波形、麦克风 motif、脉冲环 |
| **Cultural** | 音乐、创意工具、活动、文化产品 | 半色调、CRT纹理、模拟印刷、大胆 accent、海报风格 |

**选择一个模式并全文统一。不混用。**

### Step 3: 面板组合DNA

品牌板不是装饰——是对"品牌为什么存在"的视觉论证。

**3×3 经典面板系统（默认）**：

| 位置 | 内容 | 节奏 |
|------|------|------|
| 1 | Logo封面——大Logo+文字标记，强负空间 | 安静 |
| 2 | Logo构造——符号分解、网格、几何逻辑 | 技术 |
| 3 | 数字应用——浏览器chrome/app header/终端 | 功能 |
| 4 | 品牌本质——一条简短标语，大字 | 安静 |
| 5 | 色彩系统——色板、渐变条、色盘 | 技术 |
| 6 | 字体排印——大字样本、字母行、主/辅字体配对 | 技术 |
| 7 | 物理应用——卡片/文件夹/徽章/海报/标签/封条 | 功能 |
| 8 | 图像方向——电影感景观/产品特写/半色调海报 | 情绪 |
| 9 | 系统细节——UI chips/输入栏/命令行/图标行 | 细节 |

**2×3 迷你面板（简洁版）**：1.Logo → 2.浏览器/产品界面 → 3.命令行/功能面板 → 4.氛围图 → 5.符号/构造 → 6.标语

### Step 4: 色彩纪律

- **最多1个accent色**，饱和度<80%
- 禁止紫蓝"AI辉光"
- 禁止纯黑 `#000000`——用 off-black/charcoal
- accent 必须在所有面板重复出现
- 一个 accent 可以承载整个系统

### Step 5: 执行——委派图片生成

品牌策略和Logo设计决策完成后，将执行委派给：

**首选：jimeng-video（即梦）**
```bash
jimeng image generate \
  --prompt "Premium brand-kit overview for [BRAND NAME]. [Mode] visual mode.
  [Palette]. 3x3 grid on dark/light presentation canvas with strong gutters.
  Panels: logo cover / logo construction / digital app / tagline / color system /
  typography / physical mockup / image direction / system detail.
  Style: premium, sparse, cinematic, brand-guidelines deck, no clutter.
  Logo: [logo concept description — symbolic, simple, ownable]." \
  --model jimeng-4.5 \
  --ratio 4:3 \
  --resolution 2k
```

**备选：ComfyUI**（需要更精细控制时）

---

## 反通用品牌规则

禁止产出：
- 随机漂浮图标
- 通用创业渐变
- 过度设计的Logo
- 无意义的 blob
- 混乱的拼贴布局
- 假的小UI元素
- 不一致的Logo变体
- 过多颜色
- 廉价霓虹
- stock模板品牌板
- 企业PPT风格的品牌页

---

## 与现有技能的关系

| 技能 | 关系 |
|------|------|
| `taste-skill` | 品牌也需要方向指引——先跑 taste 定 V/M/D 旋钮，再跑 brandkit |
| `huashu-design` | brandkit 产出品牌方向后，huashu 做具体页面/落地页设计 |
| `design-md` | 品牌 token 参考库——做品牌时加载参考竞品 |
| `jimeng-video` | 执行端——brandkit 做决策，jimeng 生成图片 |
| `hallmark` | 品牌产出的反 slop 质量门禁 |

## 技术说明

- **上游**：https://github.com/Leonxlnx/taste-skill/tree/main/skills/brandkit (MIT)
- **本技能** 吸收上游的品牌策略+Logo设计+视觉系统方法论，但排除：
  - ❌ 图片生成指令（原版针对 DALL-E/Midjourney）→ 替换为 jimeng-video 委派
  - ❌ Tailwind 特定类名引用
  - ❌ ChatGPT Images 特定集成
- **Hermes 适配**：品牌决策层留 Hermes，像素执行层委派 jimeng-video 或 ComfyUI
