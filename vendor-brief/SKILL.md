---
name: vendor-brief
description: 贵州之客供应商对接单生成器。生成酒店/车辆/地接三类 PDF 对接单。触发：供应商对接、对接单、vendor-brief、酒店对接、车辆对接、地接对接。不触发：报价单（trip-quote）、行程方案（trip-briefing）、导游执行单（guide-exec）、物资清单（supply-check）。
category: travel
triggers: [供应商对接, 对接单, vendor-brief, 酒店对接, 车辆对接, 地接对接]
version: 1.0.0
---

# vendor-brief — 供应商对接单生成器

## 输入契约
- **必填**：`trip.json` 合法 JSON，含 `hotel` / `vehicle` / `guide`（地接）三类供应商节点
- **可选**：每类供应商可指定 `--type` 仅生成单类（默认三类全生成）
- **示例**：`python3 scripts/generate_vendor_brief.py ./trips/2026-08-team-a.json`

## 输出契约
- 三份 PDF：`vendor_hotel_{trip_id}.pdf` / `vendor_vehicle_{trip_id}.pdf` / `vendor_guide_{trip_id}.pdf`
- 每份 PDF > 5KB（非空）
- 路径回显到 stdout

## 触发矩阵

| 类型 | 触发信号 | 必填 trip.json 字段 | 输出 PDF |
|------|---------|--------------------|----------|
| 酒店 | "跟 XX 酒店确认房间" | hotel[].name + check_in/out | vendor_hotel_{id}.pdf |
| 车辆 | "给车队发派车单" | vehicle.plate + driver | vendor_vehicle_{id}.pdf |
| 地接 | "让地接社确认行程" | guide.name + phone | vendor_guide_{id}.pdf |
| 全部 | "生成所有供应商对接单" | 上述三类全有 | 三份 PDF |

## 执行流程

🔴 **CHECKPOINT — 输入校验**（任一失败 → 终止）：
- [ ] `trip.json` 文件存在
- [ ] JSON 合法（`python3 -m json.tool` 通过）
- [ ] 至少含三类供应商节点之一
- [ ] 含 `trip_id` 字段（用于文件名）

### Step 1: 选择供应商类型
```bash
# 生成全部三类
python3 scripts/generate_vendor_brief.py <trip.json>

# 仅生成酒店
python3 scripts/generate_vendor_brief.py <trip.json> --type hotel

# 仅生成车辆
python3 scripts/generate_vendor_brief.py <trip.json> --type vehicle

# 仅生成地接
python3 scripts/generate_vendor_brief.py <trip.json> --type guide
```

### Step 2: 验证输出
🛑 **STOP — 输出门禁**：
- [ ] 选定类型的 PDF 已生成
- [ ] 文件大小 > 5KB
- [ ] PDF 含供应商名称、联系方式、行程关键日期

## 失败模式

| 触发 | 症状 | 修复 |
|------|------|------|
| JSON 缺失 | `FileNotFoundError` | 校验路径 |
| JSON 非法 | `json.JSONDecodeError` | `python3 -m json.tool` 调试 |
| 缺 `hotel[]`（跑 hotel 模式） | `KeyError: 'hotel'` | 补字段或换 `--type` |
| 缺 `trip_id` | 文件名含 `None` | 补 `trip_id` 字段 |
| PDF 0B | 模板缺失/写权限错 | 检查 scripts/templates/ + 权限 |
| 供应商电话为空 | PDF 显示空白 | trip.json 补 `phone` 字段 |

## ⛔ 反模式
- ❌ 跳过校验直接生成（PDF 内可能空白字段）
- ❌ dict 代替 JSON 文件（脚本要求文件路径）
- ❌ 未验输出（0B PDF 直接发供应商）
- ❌ 三类合并成一份 PDF（供应商收件人不一致）
- ❌ 手改 PDF 模板（破坏下游解析）

## 不触发（边界）
- 报价单 → `trip-quote`
- 行程方案 → `trip-briefing`
- 导游执行单（内部用）→ `guide-exec`
- 物资清单 → `supply-check`

## 上下游协作

```
trip.json ──→ vendor-brief ──┬─→ vendor_hotel_{id}.pdf    → 酒店供应商
                              ├─→ vendor_vehicle_{id}.pdf  → 车队供应商
                              └─→ vendor_guide_{id}.pdf    → 地接社
```

## 实战示例

输入 `trips/2026-08-team-a.json`：
```json
{
  "trip_id": "T20260810-A",
  "hotel": [{"name": "贵阳喜来登", "check_in": "2026-08-10", "check_out": "2026-08-12", "rooms": 8}],
  "vehicle": {"plate": "贵A·X8888", "driver": "王师傅", "phone": "13900002222"},
  "guide": {"name": "李四", "phone": "13900001111"}
}
```

执行（仅酒店）：
```bash
python3 scripts/generate_vendor_brief.py ./trips/2026-08-team-a.json --type hotel \
  --output ./out/vendor_hotel_T20260810-A.pdf
```

预期输出：约 12-18KB PDF，含酒店名、8 间房、入住/离店日期。

## 实战验证
- ✅ 2026-08 团队 A（酒店 8 间 × 2 晚）→ vendor_hotel 14.2KB
- ✅ 2026-07 团队 B（车辆 1 辆 + 地接 1 名）→ 双 PDF 均正常
- ✅ 2026-06 团队 C（地接 + 酒店全包）→ 三份 PDF 在 5 分钟内全生成

## 工作目录约定

```
.
├── trips/                              # 输入
│   └── 2026-08-team-a.json
├── out/                                # 输出（默认）
│   ├── vendor_hotel_T20260810-A.pdf
│   ├── vendor_vehicle_T20260810-A.pdf
│   └── vendor_guide_T20260810-A.pdf
└── scripts/
    └── generate_vendor_brief.py
```

## 关键约定
- 文件命名：`vendor_{type}_{trip_id}.pdf`（type ∈ hotel|vehicle|guide）
- 每个 PDF 顶部含供应商名 + 联系方式 + 行程 ID
- 文档结构：① 行程概览 ② 关键日期 ③ 联系人 ④ 紧急预案

## 与其他技能关系
| 关系 | 技能 | 说明 |
|------|------|------|
| 上游输入 | trip-briefing | trip.json 由 trip-briefing 生成 |
| 并行使用 | trip-quote | 客户报价 vs 供应商对接 |
| 后续引用 | guide-exec | 导游执行单引用对接单编号 |