# trip-archive — 团后归档器

> 原为独立技能，现作为 `travel-workflow` 管线的参考文档。脚本已移至 `scripts/trip_archive.py`。

## 执行

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
