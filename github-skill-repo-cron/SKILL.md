---
name: github-skill-repo-cron
description: 类级 cron 同步规范：双源扫描→分类过滤→symlink 穿透→README→push→Release 七阶段闭环。
metadata:
  hermes:
    tags: [github, cron, sync, pipeline, dual-source]
    related_skills: [github-release-readme, github-absorb, hermes-instance-sync]
---

# GitHub Skill Repo · Cron 同步流水线

> **类级抽象**：把"自动同步 Hermes 技能到 GitHub 发布仓库"这一类工作收口为一个可独立维护、可在 cron 中调用的流水线规范。
>
> **与 `github-release-readme` 的关系**：本技能只保留**类级原则**（跨 profile 扫描、symlink 穿透、CRLF 归一化、方向验证、bytes ratio 校验、unclassified 三子桶、Author 字段前缀启发式、永久排除四类）；会话级执行细节（v5.4.21~v5.4.37 各轮踩坑、scanner 脚本、release notes 模板）继续在 `github-release-readme` 中维护。

---

## 0. 参考资料

- `references/execution-log-2026-08-05.md` — v5.4.37 同步执行日志（含新坑：glob backup 目录过滤 / read_file "Binary file" 误判 / `git diff -w` 验证真实行变更）

---

## 1. 七阶段闭环

```
Phase 1 双源扫描（双 profile mtime 仲裁）
  ↓
Phase 2 分类过滤（prefix → author → adapted-from → OFFICIAL 自报）
  ↓
Phase 3 方向验证（version 对比 + bytes ratio + 行级 diff + references 增量）
  ↓
Phase 4 symlink 穿透 + 全量复制
  ↓
Phase 5 README 更新（str.replace + 双向索引校验）
  ↓
Phase 6 commit + push（SSH 优先 + reset --soft + race condition 守护）
  ↓
Phase 7 Release（L1 gh auth → L2 API token → L3 手动 URL）
```

---

## 2. 铁律（不会随 cron 周期变化）

### 2.1 永久排除 vs 用户主动删除 = 两套集合
- `PERMANENTLY_EXCLUDED`（检测到 name 命中即 SKIP，不报告）
- `USER_EXPLICITLY_REMOVED`（即使 classify_skill 返回 self-built，也绝不复活——尊重历史 commit 决策）

### 2.2 静默退出三条件（全部满足才不推送）
1. `local_only` 经 `classify_skill` 后为空（无新增自建/三方）
2. `content_diffs` 经分类 + 方向验证后为空（无覆盖需求）
3. `git status --porcelain` 为空（工作树与 origin/main 已同步）

### 2.3 方向验证四件套
- **version 字段对比**（local_v > gh_v 强烈暗示本地新）
- **mtime 对比**（用 `git log --follow -- <path>` 取 GH 上次同步时间）
- **CRLF 归一化**（`bytes.replace(b'\r\n', b'\n')` → identical = 假阳性）
- **references/ 目录增量**（新增 refs 文件强烈暗示本地新）

### 2.4 bytes ratio < 0.7 规则
- 同 version + ratio < 0.7 → 高度疑似本地 cron-slim 分叉 → **SKIP**
- v5.4.22 实测至今已 4 次救命（darwin-skill / web-spa / skill-evaluator / 多 skill 三轮）

### 2.5 行级 diff 兜底
- 同 version + ratio > 0.99 → 不能盲信 ratio
- 必做行级 diff：`extra_in_local = [l for l in local_lines if l not in gh_lines]`
- v5.4.23 实测：answer v1.6.0 ratio=0.996 实际有 2 行真实新增

---

## 3. 跨 profile 扫描原则

```python
LOCAL_DIRS = [
    r'C:\Users\Aorus\.hermes-feishu\skills',
    r'C:\Users\Aorus\.hermes\skills',
]
PROFILE_SUBDIRS = ['', 'content', 'methodology', 'productivity', 'creative',
                   'development', 'ai-engineering', 'devops', 'github',
                   'media', 'travel', 'data-processing', 'data-science',
                   'mlops', 'research', 'note-taking', 'web', 'platform',
                   'software-development', 'strategy-plan-writing', 'design',
                   'education', 'content-production', 'tools', 'automation']
```

**多 profile 仲裁规则**：
- 同一技能可能在两个 profile 各有一份（symlink 链）
- 取 `os.path.getmtime()` 最新者作为权威本地源
- v5.4.23 实测：wechat-article-archive 若取错 profile 会得到 false positive

---

## 4. 分类器四层顺序（v5.4.21 v2 版）

```python
def classify_skill_v2(name, skill_md_path):
    # 0. PERMANENTLY_EXCLUDED → 'official'
    # 1. 名称前缀启发式（lark-*/yida-*/clawshell-*/baoyu-非收录前缀）
    # 2. 名称白名单（computer-use/dogfood/mcp/auth-flow-diagram）
    # 3. 官方指纹（不含 'author: Hermes Agent'——可能附 adapted from）
    # 4. 第三方吸收（adapted-from 必须在 author 检测之前）
    # 5. 自建（regex 整行 author 兼容括号变体）
    # 6. fallback: author: Hermes Agent
    # 7. unclassified
```

**反向引用检查（v5.4.29 lesson）**：基础名在 `PERMANENTLY_EXCLUDED` 时，**必须**同步给 cron scanner 的 prefix 启发式加一行——否则 addendum 子变体会泄漏为 unclassified noise。

---

## 5. README 更新反模式（v5.4.23/v5.4.24/v5.4.37）

| ❌ 反模式 | ✅ 正例 |
|---|---|
| `re.sub(pattern, new_line_with_'\n', readme)` | `readme = readme.replace(old, new, 1)` |
| `HEADER_NEW[key].replace('(', r'\(')` 再 re.sub | `str.replace` 直接匹配字面字符串 |
| `read_file` 报 "Binary file" 就放弃 | Python `open(path, 'rb').read()` 直接绕开 |
| `git diff --shortstat` 报 1366 行改动 | `git diff --shortstat -w` 验证真实行变更 |
| `glob(r'C:\tmp\awesome-skills-*')` 拿尾部 | `if p.split('-')[-1].isdigit()` 过滤 backup 目录 |

---

## 6. push 守护（v5.4.23 race condition）

```bash
# 推送前必做
git fetch --depth=10 origin main
LOCAL_SHA=$(git rev-parse HEAD)
REMOTE_SHA=$(git rev-parse origin/main)
if [ "$LOCAL_SHA" != "$REMOTE_SHA" ]; then
  git reset --soft origin/main
  git reset HEAD
fi
# ⚠️ reset --soft 后必须重新 git add -A，否则 commit 失败
git add -A
```

---

## 7. Release 三级回退

| 层级 | 触发条件 | 动作 |
|---|---|---|
| L1 | `gh auth status` 显示已登录 | `gh release create` |
| L2 | gh 未登录 + 有 `$GITHUB_TOKEN` | `curl -X POST ... api.github.com/repos/.../releases` |
| L3 | 两者都失败 | 写入 `/c/tmp/release_notes_vX.Y.Z.md` + 给手工 URL |

**铁律**：先穷尽 L1/L2 再给 L3。v5.4.26 后的 cron 几乎都走 L1 路径。

---

## 8. 共享踩坑清单（与 `github-release-readme` 同步）

- v5.4.18 fallback 多目录探测：429 时不要直接用 `tail -1` 目录，按版本号降序逐个探测 `.git/` + `git remote -v` 是否含 SSH origin
- v5.4.21 方向验证矩阵：content_diff 不等于「应该本地覆盖」
- v5.4.22 bytes ratio < 0.7 规则第三次实战救命
- v5.4.23 行级 diff 兜底 + 双向引用修复 + scanner mtime 仲裁
- v5.4.24 README header `re.sub` 双重转义破坏 + rebuild-from-clean
- v5.4.29 addendum 子前缀泄漏 → prefix 启发式直接归 official
- v5.4.36-v5.4.37 cron 静默退出稳定 + 行级 diff 第三轮实战 + git diff -w 验证

---

## 9. cron 触发器分类（用户决策影响）

| cron 类型 | 时机 | 期望动作 |
|---|---|---|
| 每日 05:00 同步 | 静默退出 | 仅 REPORT 或 PATCH |
| 用户手动触发 | 主动确认 | 走完整流水线 |
| 检测到 race | 推送被拒 | 立即回退 + 重新基于 origin/main |
| gh auth 失效 | 推送失败 | 升级到 L2 → L3，无声失败不可取 |

---

## 📎 与同类技能的关系

- `github-release-readme`（USER-OWNED）：会话级执行记录 + 流水脚本
- `github-absorb`：评估外部仓库价值并吸收
- `hermes-instance-sync`：profile 间同步（同机不同 profile）
- `cron-job-optimization`：cron 任务本身健康度审计

**本技能不重复 `github-release-readme` 的执行细节**，仅保留类级原则，让任何人在不同 cron session 都能复用。
