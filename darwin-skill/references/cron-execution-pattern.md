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

---

> 日期：2026-06-29 | 执行：02:01 CST | 耗时：~268s（含 3 并行子 agent）

## 执行结果（8 skills）

| 技能 | 分组 | 基线 | 最终 | Δ | 轮次 | 状态 |
|------|:----:|:----:|:----:|:--:|:----:|------|
| wsl-docker-deploy | TODAY | 74 | 80.2 | +6.2 | 3 | ✅ 达 ≥80 |
| benchmark-generator | HISTORY | 62.7 | 70.1 | +7.4 | 3 | ✅ 达 ≥70 |
| skill-ab-test | HISTORY | 61.9 | 70.3 | +8.4 | 3 | ✅ 达 ≥70 |
| dynamic-workflow | HISTORY | 64.8 | 70.4 | +5.6 | 3 | ✅ 达 ≥70 |
| firecrawl-web | HISTORY | 53.1 | 66.7 | +13.6 | 3 | ⚠️ 未达70 |
| ocr-and-documents | HISTORY | 57.3 | 69.9 | +12.6 | 3 | ⚠️ 仅差0.1 |
| wechat-article-archive | HISTORY | 56.0 | 64.9 | +8.9 | 3 | ⚠️ 未达70 |
| author-methodology-analysis | HISTORY | 56.6 | 66.3 | +9.7 | 3 | ⚠️ 未达70 |

**已达阈值跳过（≥70）**：agent-tool-system(77.7), skill-evaluator(72.3), drawio-generation(74.0), blue-team(75.9), double-evolution(72.0), github-absorb(73.4), feishu-voice(77.0), darwin-skill(82.2)

## 子 agent 分配

| 子 agent | 技能数 | 状态 | 耗时 | 备注 |
|---------|:---:|------|------|------|
| 1 (TODAY) | 1 | ✅ 完成 | ~154s | 3 轮，达 ≥80 |
| 2 (HISTORY A) | 4 | ⚠️ 超限 | ~268s | 4 技能 × 3 轮 = 12 rounds，hit max_iterations；R3 编辑完成但未 git commit，父 agent 补提 |
| 3 (HISTORY B) | 3 | ✅ 完成 | ~172s | 3 技能 × 3 轮，全达 ≥70 |

## 新增教训

5. **子 agent batch 上限**：4 技能 × 3 轮超过 leaf 子 agent max_iterations（~50 tool calls）。每个子 agent 上限建议 ≤3 技能。症状：subagent 返回 `max_iterations`，文件已修改但未 git commit。修复：父 agent 在子 agent 返回后检查 `git status` 并补提未提交变更。
6. **体积天花板宽容**：firecrawl-web（87 行/3292B→4872B, 148%）和 ocr-and-documents（237 行/7492B→11189B, 149.3%）在 3 轮后逼近但未突破 150% 上限。R2 后应做预检预估 R3 体积。
7. **dry_run 评分一致性**：主 agent 手动评分经子 agent 验证后偏差 < 2 分，dry_run 模板可靠。

---

> 日期：2026-07-02 | 执行：02:01 CST | 耗时：~30s（**降级模式：仅评分**）

## Git 仓库不可用 → 降级为 Phase 1 only

`git rev-parse --is-inside-work-tree` 在 `~/.hermes-feishu/skills/` 顶层返回 `fatal: not a git repository`。

按 cron 任务约束「如 git 仓库不可用，跳过优化仅做评分报告」，本次执行降级。

### 执行结果（7 TODAY skills，无优化）

| 技能 | 分组 | 评分 | 状态 |
|------|:----:|:----:|------|
| skill-evaluator | TODAY | **82.7** | ✅ 已达 ≥80 阈值 |
| hermes-webui-lifecycle | TODAY | **77.4** | ⚠️ 跳过优化（git 不可用） |
| clawshell-cloud-brain | TODAY | **75.6** | ⚠️ 跳过优化（git 不可用） |
| clawshell-optimization-engine | TODAY | **73.4** | ⚠️ 跳过优化（git 不可用） |
| hermes-windows-native | TODAY | **71.8** | ⚠️ 跳过优化（git 不可用） |
| clawshell-deep-architecture-review | TODAY | **70.9** | ⚠️ 跳过优化（git 不可用） |
| search-fallback | TODAY | **52.7** | ⚠️ 跳过优化（git 不可用），**结构严重缺失** |

### 关键发现

- **search-fallback** 是本次最大风险（52.7 分）：无 workflow 结构、无 CHECKPOINT、无失败模式，仅 76 行代码片段。cron 触发时大概率退化为「一次性脚本执行」而非按 skill 设计的多步协调。
- **6 个待优化技能全部卡在 D4（CHECKPOINT）**：darwin-skill 实测 HL-1「🔴 4 行改动撬动 +3 分」，优化 D4 是最高 ROI。
- **skill-evaluator 与 hermes-webui-lifecycle 接近阈值**：下次有 git 后，1 轮优化即可触达。

### 关键教训（新增）

8. **降级工作流的核心是「不要 git init」**：cron 应静默降级而非自作主张初始化仓库。仓库初始化涉及 `.gitignore` 策略、远程仓库、首次 commit message，是用户决策。
9. **scoring-only cron 仍有价值**：基线评分是发现严重缺失技能（如 search-fallback 类无 workflow 结构）的唯一手段。`results.tsv` 仍要写入（commit 字段填 `nogit-<date>` 占位），保留历史趋势。
10. **darwin-skill 双位置歧义**：cron 路径应使用 `methodology/darwin-skill`（slim 1.7KB 版本含 Cron 模式），避免根目录 19.6KB 主版本的 `skill_view` 模糊匹配。

### 恢复策略（建议用户在桌面时段执行）

```bash
cd ~/.hermes-feishu/skills/
git init
git add -A
git commit -m "snapshot: pre-darwin baseline 2026-07-02"
```

建议 `.gitignore` 至少包含：`__pycache__/`、`*.pyc`、`data/`、`*.log`。

### 后续 cron 的优先目标（git 恢复后）

1. **search-fallback**（52.7）：补 workflow 4 步结构 + 失败模式表（D2/D3/D4 同时涨）
2. **6 个 ClawShell 系 + hermes-windows-native** 走 D4 CHECKPOINT 增量（HL-1 杠杆）
3. **hermes-webui-lifecycle**（77.4）：距 80 阈值 2.6 分，1 轮可达

---

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

---

## Cron 模式常见 Pitfalls（汇总）

| # | 陷阱 | 后果 | 修复 |
|---|------|------|------|
| 1 | git 仓库缺失 → 跳过优化 | 当次 cron 零改进 | 用户在桌面时段 `git init`，见 2026-07-02 案例 |
| 2 | cron 中自作主张 `git init` | 仓库策略未与用户对齐 | 静默降级，标 ⚠️ 提示用户 |
| 3 | `git reset --hard` 被安全策略拦截 | 回滚失败 | 用 `git revert HEAD` 或 `git revert <hash> --no-edit` |
| 4 | 子 agent batch 超 4×3 rounds | `max_iterations` 截断，未 commit | 每个子 agent ≤3 技能，父 agent 补提 `git status` |
| 5 | 体积超 150% | 该轮 score 不入账 | R2 后预检体积，>140% 即 skip R3 |
| 6 | darwin-skill 双位置歧义 | `skill_view` 报 ambiguous | cron 路径用 `methodology/darwin-skill`（slim 版本含 Cron 模式） |
| 7 | dry_run 比例 > 30% | dim8 形同虚设 | 至少 1 个真实 full_test（如 dogfood、yuanbao） |
| 8 | 不写 results.tsv | 历史趋势断档 | 即使无优化也要写 baseline 行（commit 字段填 `nogit`） |