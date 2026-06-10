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

## 与设计技能的配合

| 设计技能 | 定位 | design-md 角色 |
|----------|------|---------------|
| `claude-design` | 快速 HTML 原型、landing page | 提供品牌 token 作为风格参照 |
| `huashu-design` | 高保真原型、动画、幻灯片、品牌全案 | 作为其内置双轨体系（设计哲学+品牌Token）的品牌Token层 |
