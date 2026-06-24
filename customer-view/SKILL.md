---
name: customer-view
description: 贵州之客客户视角文档包。将报价单+行程+住宿+餐饮+安全须知合并为单一 PDF，一键发给客户。
category: travel
triggers: [客户打包, 客户文档, customer-view, 全套文档]
version: 1.0.0
---

# customer-view — 客户视角文档包

## 使用
```bash
python3 ~/.hermes-feishu/skills/travel/customer-view/scripts/customer_view.py <trip.json>
```

## 产出
- 单一 PDF：封面 + 行程概览 + 费用说明 + 住宿交通 + 安全须知
- 可直接微信发送客户
