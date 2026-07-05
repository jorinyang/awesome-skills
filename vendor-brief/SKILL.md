---
name: vendor-brief
description: 贵州之客供应商对接单生成器。生成酒店/车辆/地接三类 PDF 对接单。
category: travel
triggers: [供应商对接, 对接单, vendor-brief, 酒店对接, 车辆对接]
version: 1.0.0
---

# vendor-brief — 供应商对接单生成器

## 使用
```bash
python3 ~/.hermes-feishu/skills/travel/vendor-brief/scripts/generate_vendor_brief.py <trip.json>
```

## ⚡ CHECKPOINT
✅ 输入: trip.json 合法 JSON
✅ 输出: PDF 已生成, >0B

## ⛔ 反模式
- 跳过校验
- dict 代替 JSON
- 未验输出

|症|解|
|---|---|
|JSON|校验|
|PDF空|查|
