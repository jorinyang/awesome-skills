# cost-engine — 成本核算引擎

> 原为独立技能，现作为 `travel-workflow` 管线的参考文档。脚本已移至 `scripts/cost_engine.py`。

## 执行

```bash
python3 scripts/cost_engine.py <trip_json_path>
```

## 核心规则

- **成本底价与报价分离** — 成本核算输出不含利润的底价；报价由 trip-quote 生成
- **分类汇总** — 按活动/餐饮/交通/住宿/其他/保险六类统计占比
- **定价建议四档** — 团购(×1.15) / 标准(×1.25) / 小团(×1.40) / 定制(×1.60)
- **飞猪比价** — 从 trip.json 的 `pricing.market_reference` 读取市场参考价

## 输出

- 飞书 docx → 归档到 01-产品研发（token: XysVwyHOmiOOstkCjj9cXDBlnQb）
- 本地备份：`~/.hermes-feishu/cache/cost_engine_{团号}.md`
