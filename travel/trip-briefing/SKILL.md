---
name: trip-briefing
description: 贵州之客出团通知书生成器。从行程方案 JSON 生成对客 PDF 出团通知书，含行程、住宿、餐饮、交通、物品、安全等全部出行信息。
category: travel
triggers:
  - 出团通知书
  - 出行通知
  - trip-briefing
  - 生成通知书
version: 1.0.0
---

# trip-briefing — 出团通知书生成器

## 输出
- 文件：`~/.hermes-feishu/cache/briefing_{团号}.pdf`
- 格式：A4 竖版 PDF，可打印和微信发送
- 受众：客户（对客文档）

## 使用
```bash
python3 scripts/generate_briefing.py <trip_json_path>
```
