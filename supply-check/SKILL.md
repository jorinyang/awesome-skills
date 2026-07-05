---
name: supply-check
description: 行程JSON→飞书docx逐项勾选
category: travel
triggers: [物资清单,核对物资,supply-check]
version: 1.0.0
---
# supply-check — 物资核对清单
🔴 IN: trip.json存在|合法|含行程字段。失败→终止。
```bash
python3 scripts/generate_supply_check.py <trip.json>
```
🛑 OUT: docx非空，项数=天数。
## ⛔ 反模式
❌ 跳过校验|MD替docx|手改docx
## 失败模式
| 触发 | 症状 | 修复 |
|------|------|------|
| JSON缺失/非法 | Error/DecodeError | 校验 |
| 缺字段 | KeyError | 补全 |
