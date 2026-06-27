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
metadata:
  hermes:
      related_skills: [double-evolution]
    related_skills:
      - trip-quote
      - cost-engine
      - trip-briefing
      - customer-view
      - guide-exec
      - supply-check
      - vendor-brief
      - trip-archive
      - travel-itinerary
      - trip-landing
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

## 关联技能指引

> 以下指引由 `github-absorb` Phase 6 自动生成

当用户给出 trip.json 或行程方案，进入以下任一场景时加载对应子技能：

- **生成对客报价** → 加载 `trip-quote`，传入行程 JSON，选择团建/私人定制/研学/散客四种风格之一
- **核算成本** → 先加载 `cost-engine` 获取各项成本明细（交通/住宿/餐饮/景点/物资），再将成本数据传给 `trip-quote`
- **生成出团通知书** → 加载 `trip-briefing`，先加载 `customer-view` 获取客户姓名/身份证/联系电话
- **提取客户信息** → 加载 `customer-view`，获取客户名单、身份证号、保险单号
- **生成导游执行单** → 加载 `guide-exec`，同步加载 `supply-check` 获取物资核对清单
- **核对物资** → 加载 `supply-check`，逐项勾选行程所需物资
- **生成供应商对接单** → 加载 `vendor-brief`，按酒店/车辆/地接分包生成 PDF
- **行程归档** → 加载 `trip-archive`，将全部执行文档归档至飞书知识库 05-归档结算
- **调整行程方案** → 加载 `travel-itinerary`，生成/修改每日行程明细
- **生成行程落地页** → 加载 `trip-landing`，生成客户侧行程展示页
