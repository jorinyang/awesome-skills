---
name: trip-archive
description: 贵州之客团后归档器——每日扫描出团缓存，自动归档到飞书知识库对应节点，生成归档报告。
trigger:
  - cron
  - keywords: ["归档", "归档报告", "团后归档"]
toolset_requirements:
  - terminal
  - file
  - feishu_doc
---

# trip-archive — 团后归档器

每日自动扫描出团缓存目录，识别待归档文档，按类型归档到飞书知识库对应节点，生成归档报告。

## 流水线

### Phase 1: 扫描缓存

```bash
ls ~/.hermes-feishu/cache/ | grep -E '^(quote_|briefing_|guide_exec_|supply_check_|vendor_|cost_|route_)'
```

### Phase 2: 去重判断

- 检查是否已有 `archive_<团号>.md` 文件
- 已有 → 跳过该团（已归档）
- 没有 → 进入 Phase 3

### Phase 3: 按团分组识别

从文件名提取团号（格式如 `GZ-2026-0710-001`），将同一团号的所有文档归为一组。

### Phase 4: 执行归档

对每个待归档的团，运行：

```bash
# 找到对应的 trip JSON 文件
python3 ~/.hermes-feishu/skills/travel/travel-workflow/scripts/trip_archive.py <trip_json_path>
```

如无对应 trip JSON（仅有产出文件），手动按前缀匹配归档：

| 文件前缀 | 文档类型 | 知识库节点 | token |
|---------|---------|-----------|-------|
| `quote_*` | 报价单 | 02-销售转化 | Rcdow4tcRiYL88kwCZDcjNw8nBf |
| `briefing_*` | 出团通知书 | 03-出团执行 | HmnBwlKhsixk45kjNa9cmCRDndb |
| `guide_exec_*` | 导游执行单 | 03-出团执行 | HmnBwlKhsixk45kjNa9cmCRDndb |
| `supply_check_*` | 物资核对 | 03-出团执行 | HmnBwlKhsixk45kjNa9cmCRDndb |
| `vendor_hotel_*` | 酒店对接 | 04-供应商对接 | HbYIw1R93ihXRFkwgZ5cPmWnneb |
| `vendor_transport_*` | 车辆对接 | 04-供应商对接 | HbYIw1R93ihXRFkwgZ5cPmWnneb |
| `vendor_guide_*` | 地接对接 | 04-供应商对接 | HbYIw1R93ihXRFkwgZ5cPmWnneb |
| `cost_*` | 成本核算 | 01-产品研发 | XysVwyHOmiOOstkCjj9cXDBlnQb |
| `route_*` | 路线方案 | 01-产品研发 | XysVwyHOmiOOstkCjj9cXDBlnQb |

### Phase 5: 飞书知识库归档

使用 `feishu-wiki` 技能将归档文档移动到对应知识库节点：

1. `docs +create --parent-token <节点token>` 创建文档
2. `wiki +move` 移动到目标知识库节点
3. 生成归档报告存入 `05-归档结算` 节点（token: KuyvwJWGki1D7vkBslWchymWn2f）

### Phase 6: 清理

```bash
# 已归档的 .html 文件可删除（.pdf 已生成）
rm ~/.hermes-feishu/cache/*_<团号>*.html
```

## 输出

### 无待归档 → 静默

```
[SILENT]
```

### 有待归档 → 报告

```
📦 团后归档报告 — YYYY-MM-DD

| 团号 | 文档数 | 归档节点 | 状态 |
|------|--------|---------|:--:|
| GZ-2026-xxxx-xxx | 3 | 02-销售转化/03-出团执行 | ✅ |

归档报告：[飞书链接]
```

## 去重规则

- 同一团号只归档一次（检查 `archive_<团号>.md` 是否存在）
- 同一文档类型的 .html 和 .pdf 同时存在时，仅保留 .pdf
- 归档报告不可重复跑——每次执行都创建新飞书文档

## 陷阱

- **文件命名必须遵守前缀约定**：`quote_`、`briefing_`、`guide_exec_` 等
- **归档脚本依赖**：`trip_archive.py` 位于 `travel-workflow/scripts/`
- **知识库节点 token 硬编码在脚本中**：如需更改知识库结构，需同步更新 `trip_archive.py` 中的 `KB_NODES` 字典

### Skill 加载失败会静默伪装成功

如果 cron 输出中出现 `⚠️ Skill(s) not found and skipped: trip-archive`，说明 skill 未被正确加载。此时 LLM 可能仍能从 prompt 推断逻辑并输出 `[SILENT]`，**表面上运行成功但实际已降级运行**。必须修复 skill 发现机制。

**常见原因**：lark-cli 版本过旧导致 skills 注册表不同步。运行 `lark-cli update` 更新 lark-cli 及 skills。

### 凌晨 cron 批量失败（Connection error）

每日 03:00 是 cron 密集触发时段。若模型 API（DeepSeek）瞬时不可达，多个 cron job 可能同时报 `Connection error`。此为瞬态故障，通常下一轮自动恢复。手动 `cronjob action=run` 可验证。

## 故障排查

当 cron 报告 `failed: Connection error` 时：

```bash
# 1. 检查最近的 cron 输出
ls -lt ~/.hermes-feishu/cron/output/<job_id>/

# 2. 搜索 agent 日志中的调度事件
grep 'Running job.*trip-auto-archive\|a6e7885c2cf7' ~/.hermes-feishu/logs/agent.log

# 3. 手动触发一次验证
# (通过 Hermes: cronjob action=run job_id=<id>)

# 4. 确认 lark-cli 和 skills 是否最新
lark-cli update && lark-cli auth status
```

确认修复后，cron 输出中应不再出现 `Skill(s) not found` 警告。详见 `references/cron-debug-2026-07-01.md`。
