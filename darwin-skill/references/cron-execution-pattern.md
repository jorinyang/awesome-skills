# Cron 执行模式 — 实战案例

> 日期：2026-06-28 | 执行：02:01 CST | 耗时：~5min（含 3 并行子 agent 147s）

## 分组策略

| 分组 | 条件 | 阈值 | 优化深度 |
|------|------|:---:|---------|
| TODAY | mtime = 今天 | < 80 | 最多 4 轮，目标 ≥80 或 Δ<2 收敛 |
| HISTORY | mtime < 今天 | < 70 | 2-3 轮；≥70 跳过 |

## 执行结果（5 skills）

| 技能 | 分组 | 基线 | 最终 | Δ | 轮次 | 状态 |
|------|:----:|:----:|:----:|:--:|:----:|------|
| feishu-voice | TODAY | 66 | 81 | +15 | 4 | ✅ |
| guide-exec | TODAY | 31 | 39 | +8 | 1 | ⚠️ 体积天花板 |
| double-evolution | TODAY | 81 | — | — | — | ✅ 已达阈值 |
| supply-check | HISTORY | 17 | 34 | +17 | 2 | ✅ |
| vendor-brief | HISTORY | 17 | 34 | +17 | 2 | ✅ |
| req-align-analysis | HISTORY | 55 | 72 | +17 | 2 | ✅ |

## 回滚：guide-exec R2+R3

D9 反例 + D3 失败模式 → 体积 1992→4964 字节（249%），超 150% 上限。
回退链：`git revert 979cf87 --no-edit && git revert abf8489 --no-edit`
最终保留 R1（2683 字节，135%），score 31→39。

## 并行优化性能

3 HISTORY skill 通过 `delegate_task tasks[]` 并行：
- 总耗时 147s，单 skill 均 49s
- toolsets: `["terminal", "file"]`
- 子 agent context 必须传递 rubric 速查 + D4/D6/D9 修复模板

## 体积天花板实证

**guide-exec**（65 行 / 1992B 基线）：
- R1 D4：+3 Checkpoints → 2683B (135%) ✅
- R2 D9：+6 反例 → 3478B (175%) ❌
- R3 D3：+8 失败模式 → 4964B (249%) ❌

**结论**：<100 行 baseline 的技能，1 轮即近体积上限。策略：接受天花板（~40-50）或先精简冗余再优化。

## 关键教训

1. 小技能（<100 行）不做多轮优化 — 1 轮可能触上限
2. 并行子 agent 需在 context 显式传 rubric + 修复模板
3. `git reset --hard` 在 cron 安全策略中被拦截 → 必须 `git revert`
4. results.tsv 路径：实际为 `methodology/darwin-skill/results.tsv`

## 日报模板

```markdown
# 技能优化日报 {YYYY-MM-DD}

## 总览
扫描{N} | TODAY{N}需优化{N} | HISTORY{N}需优化{N} | 实际{N}技能{N}轮 | 保留{N}回滚{N}

## 优化详情
### {skill} ⭐ → {old}→{new}(+{delta}) {rounds}轮
- R1 D4: ...
- R2 D3: ...

## 已达阈值
## 质量验证矩阵（5标记）
## 仍需关注
```
