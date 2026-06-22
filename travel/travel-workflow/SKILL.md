---
name: travel-workflow
description: 贵州之客旅行社工作流系统总纲。一条 trip.json 入 → 8 技能全链路产出。含数据模型、管线架构、PDF生成模式、飞书文档创建模式、lark-cli v2 陷阱速查。
category: travel
triggers:
  - 旅游工作流
  - 出团文档
  - 行程方案转文档
  - travel-workflow
  - trip pipeline
version: 1.0.0
---

# travel-workflow — 贵州之客工作流系统

> 一键生成完整出团文档链路

## 架构

```
活动价目表(Excel/docx) + 客户需求
    │
    ├─ S0 route-designer → 行程方案设计 → 飞书 docx (行程路线) [ref: references/route-designer.md]
    │
trip.json (共享数据模型)
    │
    ├─ S6 cost-engine   → 成本核算     → 飞书 docx (01-产品研发) [script: scripts/cost_engine.py]
    ├─ S1 trip-quote    → 报价单       → PDF (客户)
    ├─ S2 trip-briefing → 出团通知书   → PDF (客户)
    ├─ S8 customer-view → 客户打包     → PDF (客户) [script: scripts/customer_view.py]
    ├─ S3 guide-exec    → 导游执行单   → 飞书 docx (03-出团执行)
    ├─ S4 supply-check  → 物资核对     → 飞书 docx (03-出团执行)
    ├─ S5 vendor-brief  → 供应商对接   → PDF×3 (酒店/车辆/地接)
    └─ S7 trip-archive  → 团后归档     → 飞书 docx (05-归档结算) [script: scripts/trip_archive.py]
```

## 子技能

| 技能 | 路径 | 产出格式 | 接收方 |
|------|------|---------|--------|
| `route-designer` | references/route-designer.md | 飞书 docx | 计调/客户 |
| `cost-engine` | scripts/cost_engine.py | 飞书 docx | 计调 |
| `trip-quote` | trip-quote/ | PDF (4风格) | 客户 |
| `trip-briefing` | trip-briefing/ | PDF | 客户 |
| `customer-view` | scripts/customer_view.py | PDF (全套) | 客户 |
| `guide-exec` | guide-exec/ | 飞书 docx (12章) | 导游 |
| `supply-check` | supply-check/ | 飞书 docx | 仓库 |
| `vendor-brief` | vendor-brief/ | PDF×3 | 供应商 |
| `trip-archive` | scripts/trip_archive.py | 飞书 docx | 存档 |

## 共享数据模型

样本：`trip-quote/templates/sample_trip.json`

核心结构：
- `group` — 团基本信息（类型决定报价单风格：团建/私人定制/研学/散客）
- `itinerary` — 每日行程（时间/地点/活动/详情）
- `pricing` — 费用明细 + 市场参考
- `suppliers` — 供应商（交通/酒店/餐饮/景点）
- `supplies` — 物资清单
- `customers` — 客户名单（含身份证号/保险单号）

## PDF 生成模式

HTML 模板 → Python script 填充 → Playwright (Chromium headless) → PDF

安装：`pip install playwright && python3 -m playwright install chromium`

## 飞书文档创建模式

```bash
cd /tmp
lark-cli docs +create --api-version v2 --doc-format markdown \
  --content @file.md --parent-token <wiki_node_token> --as bot
```

关键约束见 `references/lark-cli-v2-patterns.md`

## 使用

```bash
python3 ~/.hermes-feishu/skills/travel/pipeline.py trip.json
```

## 知识库归档结构

```
业务记录/
├── 01-产品研发/  ← cost-engine
├── 02-销售转化/  ← 报价单/合同模板
├── 03-出团执行/  ← guide-exec + supply-check
├── 04-供应商对接/ ← vendor-brief 模板
└── 05-归档结算/  ← trip-archive
```
