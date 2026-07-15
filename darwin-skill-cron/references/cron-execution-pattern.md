# Cron 执行模式 — 关键教训

> 综合 2026-06-28 + 2026-06-29 两日 cron 执行数据（共 13 技能优化）。

## 执行结果汇总

### 2026-06-28（5 技能）

| 技能 | 分组 | 基线 | 最终 | Δ | 轮次 | 状态 |
|------|:----:|:----:|:----:|:--:|:----:|------|
| feishu-voice | TODAY | 66 | 81 | +15 | 4 | ✅ 达 ≥80 |
| guide-exec | TODAY | 31 | 39 | +8 | 1 | ⚠️ 体积天花板 |
| double-evolution | TODAY | 81 | — | — | — | ✅ 已达阈值 |
| supply-check | HISTORY | 17 | 34 | +17 | 2 | ✅ |
| vendor-brief | HISTORY | 17 | 34 | +17 | 2 | ✅ |
| req-align-analysis | HISTORY | 55 | 72 | +17 | 2 | ✅ |

### 2026-06-29（8 技能）

| 技能 | 分组 | 基线 | 最终 | Δ | 轮次 | 状态 |
|------|:----:|:----:|:----:|:--:|:----:|------|
| wsl-docker-deploy | TODAY | 74 | 80.2 | +6.2 | 3 | ✅ |
| benchmark-generator | HISTORY | 62.7 | 70.1 | +7.4 | 3 | ✅ |
| skill-ab-test | HISTORY | 61.9 | 70.3 | +8.4 | 3 | ✅ |
| dynamic-workflow | HISTORY | 64.8 | 70.4 | +5.6 | 3 | ✅ |
| firecrawl-web | HISTORY | 53.1 | 66.7 | +13.6 | 3 | ⚠️ 未达70 |
| ocr-and-documents | HISTORY | 57.3 | 69.9 | +12.6 | 3 | ⚠️ 差0.1 |
| wechat-article-archive | HISTORY | 56.0 | 64.9 | +8.9 | 3 | ⚠️ |
| author-methodology-analysis | HISTORY | 56.6 | 66.3 | +9.7 | 3 | ⚠️ |

## 关键教训

1. **小技能（<100 行）不做多轮** — 1 轮即近体积上限。guide-exec: R1 135%, R2 175% ❌, R3 249% ❌
2. **子 agent batch 上限 = 3** — 4 技能 × 3 轮超 max_iterations（~50 tool calls），文件已改但未 commit
3. **并行子 agent context 必须显式传 rubric + 修复模板** — 否则子 agent 评分偏差大
4. **git reset --hard 在 cron 安全策略中被拦截** — 必须 `git revert`
5. **父 agent 在子 agent 返回后必须检查 git status** — 补提未提交变更
6. **体积天花板** — firecrawl-web (148%) 和 ocr-and-documents (149.3%) 逼近 150% 上限
7. **dry_run 评分一致性** — 主 agent 手动评分经子 agent 验证偏差 < 2 分
8. **收敛定律** — R3 起大部分 skill Δ<2，R4+ 仅标记补全。6 轮最多 4 轮有效改动

## 收敛数据

14 技能 6 轮实测（基线 44-75 → 最终 71-83）：
- R1: D3+D4+D6+D9 — 高杠杆基础建设
- R2: D1+D2+D5 — 工作流升级
- R3: D7 去冗余 — 5/14 无改动可 skip
- R4: 交叉引用修正 + ⛔ 标记补全
- R5-R6: Δ<2 收敛 + 低分 skill 体积超标 → 触发 Phase 2.5 回退

## 回滚案例

**guide-exec R2+R3**：D9 反例 + D3 失败模式 → 体积 1992→4964 字节（249%），超 150% 上限。
回退: `git revert 979cf87 --no-edit && git revert abf8489 --no-edit`，保留 R1（2683 字节, 135%）
