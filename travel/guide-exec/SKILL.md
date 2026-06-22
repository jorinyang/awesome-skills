---
name: guide-exec
description: 贵州之客导游执行单生成器。从行程方案 JSON 生成飞书 docx 导游执行单，含客户名单（身份证/保险）、行程明细、供应商对接、物资核对、财务、应急预案等12个模块。
category: travel
triggers:
  - 导游执行单
  - 执行单
  - guide-exec
  - 带团手册
version: 1.0.0
---

# guide-exec — 导游执行单生成器

## 12 模块

1. 团基本信息 2. 客户名单（含身份证号/保险单号） 3. 行程明细
4. 景点对接 5. 餐饮安排 6. 住宿信息 7. 车辆信息
8. 物资核对清单 9. 财务信息 10. 应急预案
11. 天气预报 12. 行前确认清单

## 输出
- 飞书文档：在「03-出团执行」节点下创建
- 本地备份：`~/.hermes-feishu/cache/guide_exec_{团号}.md`
- 受众：导游、计调（内部文档）

## 使用
```bash
python3 scripts/generate_guide_exec.py <trip_json_path> [--parent-token <wiki_node_token>]
```
