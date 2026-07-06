---
name: design-md
description: "Use alongside claude-design or huashu-design when creating UI in a specific brand/product-inspired style. Loads brand design token references from 71 companies (Apple, Stripe, Linear, Vercel, Airbnb, Notion, etc.). 品牌设计规范参考库：71个品牌的 DESIGN.md token 文件。"
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, brand, tokens, design-system, reference, ui]
    related_skills: [claude-design, huashu-design, popular-web-designs]
---

# Design MD — 品牌风格参考库

**这不是一个独立使用的技能。** 它是 `claude-design` 和 `huashu-design` 的补充参考库。

## 何时加载

当用户要求按照某个品牌/产品的视觉风格进行设计时，**同时加载本技能和 `claude-design` 或 `huashu-design`**。

- 用 **claude-design** 做快速原型、landing page、一次性 HTML 产物
- 用 **huashu-design** 做高保真交互原型、幻灯片、动画、品牌风格探索（huashu-design 内置了双轨参考体系：设计哲学 + 品牌Token）

本技能提供 71 个品牌的 DESIGN.md token 规范文件，每个文件包含该品牌的：
- 色彩体系（主色、辅助色、语义色）
- 字体方案（字体族、字重、层级）
- 间距与圆角规范
- 阴影与深度系统
- 组件样式指南
- 设计原则与反模式

## 使用方式

1. 确定目标品牌风格
2. 读取 `references/<brand>/DESIGN.md` 获取该品牌的完整设计 token
3. 将这些 token 应用到 `claude-design` 或 `huashu-design` 的设计流程中
4. 生成匹配品牌调性的 HTML 产物

## 可用品牌（71个）

### AI / 开发者工具
`claude` `cursor` `vercel` `supabase` `raycast` `warp` `voltagent` `ollama` `replicate` `together-ai` `opencode-ai` `mistral-ai` `cohere` `x-ai` `minimax` `runwayml` `elevenlabs` `lovable` `composio`

### 金融 / 加密 / 支付
`stripe` `coinbase` `binance` `kraken` `revolut` `wise` `mastercard`

### 消费品 / 电商
`apple` `nike` `shopify` `airbnb` `starbucks` `spotify` `tesla`

### 汽车 / 奢侈
`bmw` `bmw-m` `ferrari` `lamborghini` `bugatti` `renault`

### 生产力 / SaaS / 文档
`linear-app` `notion` `airtable` `mintlify` `cal` `intercom` `slack` `zapier` `figma` `framer` `miro` `clay` `sanity` `webflow` `expo` `sentry` `posthog` `clickhouse` `hashicorp` `mongodb` `ibm` `resend` `superhuman`

### 媒体 / 编辑
`wired` `theverge` `pinterest` `meta` `playstation` `nvidia` `spacex` `uber` `vodafone`

## 品牌选择指南

| 场景 | 推荐品牌 |
|---|---|
| AI SaaS 落地页 | `vercel` `claude` `cursor` |
| 支付/金融界面 | `stripe` `coinbase` `wise` |
| 极简产品页 | `apple` `linear-app` `raycast` |
| 暗色科技风 | `nvidia` `spacex` `warp` |
| 创意工具 | `figma` `framer` `miro` |
| 企业级产品 | `ibm` `hashicorp` `mongodb` |
| 消费品牌 | `nike` `spotify` `airbnb` |
| 汽车/工业 | `tesla` `bmw` `ferrari` |

## 输出规范

- 注明参考的品牌风格
- 总结应用的关键设计特征
- 保持可访问性和响应式
- 不复制受保护的品牌资产（logo、商标）
- 标注「品牌风格启发设计，非官方关联」

## 反 AI-Slop 通用规则（吸收自 taste-skill/stitch-skill）

以下规则应在所有品牌设计中默认执行，不仅是 design-md 参考场景：

### 禁止项（NEVER DO）
- ❌ 不使用 emoji（图标用 SVG/图标库）
- ❌ 不使用 Inter 字体（高级/创意场景）
- ❌ 不使用纯黑 `#000000`
- ❌ 不使用霓虹/外发光阴影
- ❌ 不使用过饱和 accent（饱和度<80%）
- ❌ 不用于大标题使用过度渐变文字
- ❌ 不使用自定义鼠标光标
- ❌ 不使用重叠元素——每个元素占据自己清晰的空间区域
- ❌ 不使用 3 列等宽卡片布局
- ❌ 不使用通用占位名（"John Doe" "Acme" "Nexus"）
- ❌ 不使用假整数数据（99.99%、50%）
- ❌ 不使用 AI 文案 cliché（"Elevate" "Seamless" "Unleash" "Next-Gen"）
- ❌ 不使用填充文本："Scroll to explore" "Swipe down" 滚动箭头
- ❌ 不使用死图片链接——用 picsum.photos 或 SVG avatars
- ❌ 高 VARIANCE 项目不使用居中 Hero section

### 必须项（ALWAYS DO）
- ✅ 所有交互元素 hover + active 反馈
- ✅ 骨架屏 loading 态（不用圆形 spinner）
- ✅ 移动端全部塌缩为单列（< 768px）
- ✅ 所有交互元素最小 44px 触摸目标
- ✅ `min-h-[100dvh]` 代替 `h-screen`
- ✅ 动画只用 `transform` + `opacity`

## 与设计技能的配合

| 设计技能 | 定位 | design-md 角色 |
|----------|------|---------------|
| `claude-design` | 快速 HTML 原型、landing page | 提供品牌 token 作为风格参照 |
| `huashu-design` | 高保真原型、动画、幻灯片、品牌全案 | 作为其内置双轨体系（设计哲学+品牌Token）的品牌Token层 |
| `brandkit` | 品牌策略+Logo设计方法论 | 品牌 token 参考库——做新品牌时加载参考竞品 |
| `redesign-skill` | 页面系统性升级 | 升级后验证品牌 token 一致性 |
