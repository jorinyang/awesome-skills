---
name: trip-archive
description: 贵州之客团后归档器。扫描缓存目录，按文档类型自动归档到知识库对应节点，生成归档报告。
category: travel
triggers:
  - 归档
  - trip-archive
  - 团后归档
  - 存档
  - 整理团档
version: 1.0.0
---

# trip-archive — 团后归档器

## 使用

```bash
python3 scripts/trip_archive.py <trip_json_path>
```

## 归档映射

| 缓存文件匹配 | → 知识库节点 |
|-------------|------------|
| quote_* / 报价 | 01-产品研发 |
| briefing_* / 出团 | 03-出团执行 |
| guide_exec_* / 执行单 | 03-出团执行 |
| supply_check_* / 物资 | 03-出团执行 |
| vendor_* / 供应商 | 04-供应商对接 |
| archive_* / 归档报告 | 05-归档结算 |

## 输出

- 飞书 docx 归档报告 → 05-归档结算
