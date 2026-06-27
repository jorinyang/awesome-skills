---
name: trip-quote
description: 贵州之客报价单生成器。从行程方案 JSON 生成对客 PDF 报价单，支持团建/私人定制/研学/散客四种风格，不含利润仅展示项目费用。搭配 cost-engine 做成本核算。
category: travel
triggers:
  - 生成报价单
  - 做报价
  - 报价单
  - trip-quote
  - 客户报价
  - 出报价
  - 散客报价
  - 团建报价
  - 研学报价
  - 定制报价
version: 1.1.0
metadata:
  hermes:
    related_skills:
      - cost-engine
---

# trip-quote — 报价单生成器

从行程方案 JSON 生成对客 PDF 报价单。

## 核心规则

- **不含利润** — 报价单只展示服务项目及费用，利润在内部成本核算（cost-engine）中管理
- **四种风格** — 团建/私人定制/研学/散客，根据 `group.type` 自动匹配，也可 `--style` 手动指定
- **市场参考** — 可展示飞猪同类产品市场价作为锚定（可选列，来自 pricing.market_reference）
- **输出 PDF** — 对外文档，HTML→Playwright page.pdf()，可直接微信发送客户
- **成本基线与报价分离** — 报价单展示含加价后的对客价格；成本底价在 cost-engine 中独立核算

## 四种风格

| 风格 | 团类型 | 色调 | 特点 |
|------|--------|------|------|
| 团建 | 团建 | 蓝+白 专业感 | 突出团队规模、人均价、企业感 |
| 私人定制 | 私人定制 | 金+墨绿 高端感 | 突出个性化、品质、专属服务 |
| 研学 | 研学 | 橙+白 活力感 | 突出课程结构、学习目标、安全保障 |
| 散客 | 散客 / 通用 | 蓝绿旅行感 | 突出体验、性价比、出发日期、预订须知 |

## 模板文件

| 风格 | 模板 |
|------|------|
| 团建 | `templates/quote_团建.html` |
| 私人定制 | `templates/quote_私人定制.html` |
| 研学 | `templates/quote_研学.html` |
| 散客 | `templates/quote_散客.html` |

## 使用

```bash
python3 scripts/generate_quote.py <trip_json_path>
```

## 依赖

- Playwright (Chromium) — HTML → PDF 渲染
- Python stdlib json/pathlib

## 关联技能指引

> 以下指引由 `github-absorb` Phase 6 自动生成

- **downstream → `cost-engine`**：生成报价单前，必须先加载 `cost-engine` 获取各项成本明细（交通/住宿/餐饮/景点/物资）。成本数据作为报价的输入底价，本技能在此基础上生成不含利润的对客报价。
