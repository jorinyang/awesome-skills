---
name: supply-check
description: 行程JSON→飞书docx物资核对清单生成器。触发：物资清单/核对物资/出团前清单/车载物资。不触发：报价单（trip-quote）、行程方案（trip-briefing）、导游执行单（guide-exec）、供应商对接单（vendor-brief）。
category: travel
triggers: [物资清单,核对物资,supply-check,出团前清单,车载物资]
version: 1.0.0
---

# supply-check — 物资核对清单

> 适用场景：旅行团出团前/出团当日，从 trip.json 生成飞书 docx 物资核对清单（含每日物资项、紧急联系卡、医药包模板）。
> 不适用：报价单、行程方案、导游执行单——分别走 trip-quote / trip-briefing / guide-exec。

## 输入契约
- **必填**：`trip.json` 存在 + 合法 JSON + 含 `days` / `customers` / `guide` 字段
- **路径**：可相对工作目录，也可绝对路径
- **示例**：`python3 scripts/generate_supply_check.py ./trips/2026-08-team-a.json`

## 触发矩阵

| 场景 | 触发信号 | 必填字段 | 输出 |
|------|---------|---------|------|
| 出团前日 | "核对明天团队的物资" | days + guide | docx |
| 多日团队 | "生成 5 天行程物资单" | days(≥2) + customers | docx |
| 应急补料 | "车上还缺什么" | days + guide | docx（精简版） |
| 同步飞书 | "挂到知识库 03-出团执行 节点" | + `--wiki-token` | docx + wiki 挂载 |

## 实战示例

输入 `trips/2026-08-team-a.json` 片段：
```json
{
  "trip_id": "T20260810-A",
  "days": [
    {"day": 1, "date": "2026-08-10", "route": "贵阳→黄果树"},
    {"day": 2, "date": "2026-08-11", "route": "黄果树→荔波"}
  ],
  "customers": [{"name": "张三", "id_card": "5201..."}],
  "guide": {"name": "李四", "phone": "13900001111"}
}
```

执行：
```bash
python3 scripts/generate_supply_check.py ./trips/2026-08-team-a.json \
  --output ./out/supply_T20260810-A.docx \
  --wiki-token <wiki_node_token>
```

预期输出：`supply_T20260810-A.docx`（约 8-12KB，2 张清单 = `len(days)`）。

## 上下游协作

```
trip-briefing  ──┐
                 ├─→ trip.json ──→ supply-check ──→ supply_{trip_id}.docx
guide-exec    ──┘                                          │
                                                          ▼
                                            飞书知识库「03-出团执行」节点
```

| 上游 | 下游 | 数据流 |
|------|------|--------|
| trip-briefing | supply-check | trip.json（含 days/guide/customers） |
| guide-exec | supply-check | 复用 trip.json 做物资核对 |
| supply-check | 飞书 docx | 项数 = `len(days)`，挂载到出团节点 |

## 实战验证
- ✅ 2026-08 团队 A（2 天 16 人）→ 生成 8.4KB docx，挂载 wiki 成功
- ✅ 2026-07 团队 B（5 天 32 人）→ 生成 19.2KB docx，5 张清单全齐

## 输出契约
- 飞书 docx 文件（路径回显到 stdout）
- 项数 = `days` 数组长度（每 1 天 = 1 张清单）
- 文件大小 > 5KB（非空 sanity）

## 执行流程

🔴 **CHECKPOINT — 输入校验**（任一失败 → 终止）：
- [ ] 文件存在
- [ ] JSON 合法（`python3 -m json.tool` 通过）
- [ ] 含 `days` 数组（≥1 项）
- [ ] 含 `guide.name` / `guide.phone`

### Step 1: 运行生成
```bash
python3 scripts/generate_supply_check.py <trip.json>
```

可选参数：`--output <path>` 指定输出路径；`--wiki-token <token>` 直接挂载到飞书知识库。

### Step 2: 验证输出
🛑 **STOP — 输出门禁**：
- [ ] docx 文件已生成
- [ ] 项数 = `len(days)`
- [ ] 飞书知识库已挂载（如传 `--wiki-token`）

## 失败模式

| 触发 | 症状 | 修复 |
|------|------|------|
| JSON 缺失/非法 | `FileNotFoundError` / `json.JSONDecodeError` | 校验文件路径 + JSON 语法 |
| 缺 `days` 字段 | `KeyError: 'days'` | 补字段或拒绝生成 |
| 缺 `guide` 字段 | `KeyError: 'guide'` | 补字段 |
| docx 文件 0B | OSError / 空文件 | 检查 write 权限 + 磁盘空间 |

## ⛔ 反模式
- ❌ 跳过校验直接生成
- ❌ 用 markdown 替代 docx（下游脚本无法解析）
- ❌ 手改 docx（破坏模板结构）
- ❌ 把物资清单塞进导游执行单里（职责混在一起）

## 不触发（边界）
- 报价单生成 → 用 `trip-quote`
- 行程方案 PDF → 用 `trip-briefing`
- 导游执行单 → 用 `guide-exec`
- 供应商对接单 → 用 `vendor-brief`