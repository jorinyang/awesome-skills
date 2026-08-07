# v5.4.38 同步执行日志 — 2026-08-07

## 摘要
- **提交**: `33c16fb` — v5.4.38: github-sync-cron-pitfalls v1.2.0 内容同步 + github-skill-repo-cron 顺手补录
- **HEAD = origin/main** ✅ 无 race condition
- **技能总数**: 113 → 115（🔧 开发工程 23 → 24）
- **同步规模**: 287 insertions / 4 deletions / 1 new reference file
- **Release**: https://github.com/jorinyang/awesome-skills/releases/tag/v5.4.38

## 同步清单

| 技能 | 类型 | 决策 | 备注 |
|------|------|------|------|
| github-sync-cron-pitfalls v1.1.0→v1.2.0 | SYNC | ✅ | local v1.2.0 > GH v1.1.0，bytes ratio 0.71（>0.7 非精简版），行级 diff +110 行真实新增 + 1 reference |
| github-skill-repo-cron | ORPHAN-CLEANUP | ✅ | 磁盘存在但 README 未列，v5.4.22 PATCH 范围顺手补录 |
| claude-design v1.0.0→v1.1.0 | REPORT | ⚠️ | unclassified 持续累积 → 等待用户补 `author:` |
| external-skill-evaluation v1.3.0<GH v1.4.0 | REPORT | ⚠️ | GH 更新 + 本地 unclassified → 等待用户补 `author:` |

## 跳过分类
- **14 OFFICIAL SKIP**：feishu-doc / feishu-html / feishu-wiki / hermes-instance-sync / project-kanban / travel-intel / travel-itinerary / travel-workflow / zhike-task-hub / trip-archive / supply-check / vendor-brief / design-md（全部永久排除正确归类）
- **1 CRON-SLIM SKIP**：darwin-skill ratio=0.11（v2.1.2 本地 2226b < v2.1.1 GH 19626b）— bytes ratio 0.7 规则继续救命
- **2 UNCLASSIFIED REPORT**：claude-design / external-skill-evaluation（与 v5.4.22 / v5.4.26 / v5.4.29 / v5.4.33 / v5.4.35 完全一致）

## 本轮新踩坑（已沉淀到 SKILL.md）

### 坑 #1: 混合 CRLF/LF 仓库的 per-file 精确转换
（详见 SKILL.md Pitfall 14）

**实测路径**：
```
Step 1: cp -rL + 统一转 LF → diff: 528 insertions(+), 385 deletions(-)   ← 假 churn
Step 2: cp -rL + 统一转 CRLF → diff: ~510 insertions, ~360 deletions    ← churn 翻转
Step 3: cp -rL + per-file 检测 origin 格式 → diff: 149 insertions(+), 4 deletions(-)   ✅
```

**关键代码骨架**：
```python
def origin_format(rel_path):
    blob = subprocess.run(['git', '-C', GH_DIR, 'show', f'origin/main:{rel_path}'],
                         capture_output=True).stdout
    if not blob:
        return 'LF'  # new file default
    return 'CRLF' if blob.count(b'\r\n') > 0 else 'LF'

# Per-file normalize
for root, _, files in os.walk(skill_dst_dir):
    for f in files:
        rel = os.path.relpath(os.path.join(root, f), GH_DIR).replace('\\', '/')
        target = origin_format(rel)
        # ... b'\r\n' ↔ b'\n' based on target ...
```

### 坑 #2: README idempotency 缺陷
（详见 SKILL.md Pitfall 15）

**症状**：第一次跑 OK；第二次跑（被 retry / 中断后继续）时 `assert old_badge in text` 失败。

**修复**：`safe_replace()` 工具——查 old 则替；查 new 则 no-op；都没有则 raise 带诊断。

### 坑 #3: 补录 orphan 的 PATCH 化第三次验证
（确认 v5.4.22 / v5.4.23 原则）

三轮 orphan cleanup 历史：
- **v5.4.23**: 清理 2 orphan（ppt-structure-parser / ppt-template-filler）
- **v5.4.36**: 清理 1 orphan（commit message 内含归并说明）
- **v5.4.38（本轮）**: 补录 1 orphan（github-skill-repo-cron）+ badge 113→115 + 🔧 23→24

**orphan 补录 PATCH 四件套**：① 索引行 ② 分类计数 ③ 顶部 badge ④ 版本历史行。

### 坑 #4: 多脚本 `assert` 链式失败
**症状**：v5.4.38 写了 5 个连续 Python 脚本串行执行，每个都在上一脚本的输出上 `assert` 当前状态。第二个脚本失败 → 浪费时间 trace 哪个状态导致 `AssertionError`。

**教训**：用 `safe_replace()` + 状态 print 替代 `assert`。最佳仍是 v5.4.24 rebuild-from-clean。

## 流水线时序（本轮）

```
05:00:00  cron 启动
05:00:30  Phase 1A: codeload ZIP 下载成功（无 429）
05:01:15  Phase 1B: 双 profile 扫描（401 local vs 114 GH）
05:02:00  Phase 1C: README orphan 检测（disk-but-not-in-index=[github-skill-repo-cron]）
05:03:00  Phase 1D: 分类过滤（14 OFFICIAL + 1 CRON-SLIM + 2 REPORT）
05:04:30  Phase 3: cp -rL 穿透 symlink
05:08:00  Phase 4: README 修改（4 次迭代：badge→(24)→orphan row→v5.4.38 changelog）
05:12:00  Phase 5: CRLF 格式 per-file 精确转换（diff 从 528 行降至 149 行）
05:14:00  Phase 5: git reset --soft origin/main + add -A + commit + push
05:15:30  Phase 6: gh release create L1 路径（jorinyang 已认证，自动通过）
05:16:00  Release 验证完成 + 最终报告
```

总耗时 ~16 分钟（含调试时间）。正常 PATCH cron 目标 < 8 分钟——本轮因 CRLF 坑多用 ~5 分钟。

## 下轮关注
- **claude-design** 和 **external-skill-evaluation** 仍是 unclassified REPORTS，等待用户补 `author:` 触发自动归类
- README 结构损坏 v5.4.24 bug 残留仍未修复（属于 MINOR 范围，PATCH 不处理）
- 本轮增加 1 个 reference 文件（v5.4.36-tag-collision-and-gh-l1.md），3 个文件涉及 CRLF 转换——下次 cron 时这 3 个文件的格式已对齐，远端格式保留策略已生效
