---
name: github-release-readme
description: >-
  同步技能→更新README→创建Release的一键流水线。自动扫描本地+GitHub双源，
  过滤官方/插件技能（仅同步自建+第三方吸收），更新README分类/计数/版本历史，
  提交并推送至 jorinyang/awesome-skills。
  触发：同步到仓库/更新awesome-skills/发release/迭代README/发布版本/同步技能/GitHub同步。
version: 2.1.0
author: 杨瑒 (月夜)
triggers:
  - 同步到仓库
  - 同步到 github
  - 更新 awesome-skills
  - 发 release
  - 更新 release
  - 创建新 release
  - 迭代 README
  - 发布版本
  - 创建 release
  - 同步技能
  - GitHub同步
metadata:
  hermes:
    tags: [github, release, readme, sync, pipeline, dual-source]
    related_skills: [github-absorb, hermes-instance-sync]
    repo: jorinyang/awesome-skills
---

# GitHub Release & README · 自动同步流水线

> **定位**：从"手动复制文件"升级为"双源扫描→分类过滤→自动同步→README生成→Release创建"的全自动闭环。

---

## 同步策略

### 纳入范围（GitHub 收录）

| 类型 | 识别方式 | 示例 |
|------|---------|------|
| **自建技能** | author=杨瑒/月夜/jorinyang，或 SKILL.md 含"自建"标记 | answer, fireworks-tech-graph, zhike-* |
| **第三方吸收** | SKILL.md 含"吸收自/adapted from"标记 + 非官方上游 | brandkit, architecture-diagram, github-absorb |

### 排除范围（仅本地，不上传）

| 类型 | 识别方式 | 示例 |
|------|---------|------|
| **官方/插件技能** | 来自 Hermes 内置/插件，或 SKILL.md 含 plugin/superpowers 标记。**同步时强制过滤，绝不推送到 GitHub。** | lark-* (27个), coding-agents, creative-ideation, kanban, dogfood, yuanbao, youtube-content, model-comparison, memos-cloud |
| **永久排除（用户指定）** | 用户明确要求从 GitHub 仓库移除且永不加入。即使后续本地有更新也不同步。 | plan, spike, dingtalk-channel, ocr-and-documents |
| **平台专属技能** | 含飞书内部 API token/space_id 等敏感信息 | feishu-wiki (含 space_id), clawshell-cloud-brain |

> 🔴 原则：GitHub 仓库 = 公开可复用的技能资产。平台绑定/含密钥/纯执行工具的技能留在本地。

---

## 全自动流水线

### Phase 0: 前置检查

```bash
# 确保 Git 已配置
git config user.name "jorinyang"
git config user.email "jorinyang@users.noreply.github.com"

# WSL TUN 代理处理
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
```

### Phase 1: 双源扫描

**🔴 Windows 原生环境关键差异**：当前 Hermes 运行在 Windows 原生（不再是 WSL）。`readlink -f` / `cp -rL` / `cd /tmp` 等 WSL 风格命令在 PowerShell 或沙箱 Python 中**不工作**或行为不同。Phase 1 必须改用 Windows 路径 + codeload ZIP。

#### Phase 1A: 用 codeload ZIP 下载（绕过 GFW）

```bash
# HTTPS git clone 在沙箱被屏蔽；用 codeload.github.com ZIP 镜像
python3 << 'PYEOF'
import urllib.request, zipfile, shutil
url = 'https://codeload.github.com/jorinyang/awesome-skills/zip/refs/heads/main'
urllib.request.urlretrieve(url, r'C:\tmp\awesome-skills.zip')
shutil.rmtree(r'C:\tmp\awesome-skills-main', ignore_errors=True)
with zipfile.ZipFile(r'C:\tmp\awesome-skills.zip') as z:
    z.extractall(r'C:\tmp\')
PYEOF
```

> GitHub API 端点（`api.github.com`）也可访问，但 ZIP 端点（`codeload.github.com`）在 GFW 下更稳定。

#### Phase 1B: 扫描本地 vs GitHub

扫描脚本**必须用 Windows 路径**（Python 不识别 `/c/Users/...`）：

```python
# ❌ 错误：Python 找不到 /c/Users/...
LOCAL_DIRS = ['/c/Users/Aorus/.hermes-feishu/skills']

# ✅ 正确：使用原始 Windows 路径
LOCAL_DIRS = [
    r'C:\Users\Aorus\.hermes-feishu\skills',
    r'C:\Users\Aorus\.hermes\skills',
]
GH_DIR = r'C:\tmp\awesome-skills-main'
```

#### Phase 1C: README vs 实际文件一致性检查

> 🔴 **新增检查项**：每次扫描必须对比 README 引用的 `SKILL.md` 路径与 GitHub 实际目录，发现不一致要报告（不要自动修复——这是用户决策）。

```python
import re
readme = open(r'C:\tmp\awesome-skills-main\README.md', encoding='utf-8').read()
referenced = set(re.findall(r'\[([\w-]+)\]\(([\w-]+)/SKILL\.md\)', readme))
actual = {d for d in os.listdir(GH_DIR) if os.path.isdir(os.path.join(GH_DIR, d))}
# README 引用但实际不存在 → 待修复
missing = referenced - actual
# README badge 数字 vs 实际目录数
badge_match = re.search(r'Skills-(\d+)', readme)
if badge_match:
    badge_count = int(badge_match.group(1))
    actual_count = len([d for d in os.listdir(GH_DIR) if os.path.isdir(os.path.join(GH_DIR, d)) and not d.startswith('.')])
    if badge_count != actual_count:
        print(f'⚠ badge {badge_count} vs actual {actual_count}')
```

#### Phase 1D: 反例（踩过的坑）

| ❌ 反例 | ✅ 正例 |
|---------|---------|
| `git clone https://github.com/.../awesome-skills.git` | `codeload.github.com` ZIP |
| `cd /tmp/awesome-skills` | `cd C:/tmp/awesome-skills-main` |
| `LOCAL_DIRS = ['/c/Users/...']` | `LOCAL_DIRS = [r'C:\Users\...']` |
| 信任 README 引用与实际目录一致 | Phase 1C 显式验证 |
| 同步完成后立即 push | Phase 5D push 前必须 rebase |

**扫描输出示例**：
```
本地: 124 技能 | GitHub: 102 技能
  共享: 87 | 仅本地: 37 | 仅GitHub: 6
  本地独有-应同步(自建+三方): 8
  本地独有-官方/插件(排除): 29
  内容差异: 12
```

### Phase 2: 技能分类

对每个技能判断归属：

```python
def classify_skill(skill_md_path):
    """
    返回: 'self-built' | 'third-party' | 'official' | 'unclassified'
    """
    content = read(skill_md_path)
    
    # 0. 永久排除（用户指定，最高优先级）
    # 这些技能即使满足后续条件，也绝不纳入 GitHub 同步
    PERMANENTLY_EXCLUDED = [
        'plan', 'spike', 'dingtalk-channel', 'ocr-and-documents'
    ]
    for skill_name in PERMANENTLY_EXCLUDED:
        if f'/skills/{skill_name}/' in skill_md_path or skill_md_path.endswith(f'/{skill_name}/SKILL.md'):
            return 'official'  # 作为官方/插件类排除
    
    # 1. 官方/插件标记
    if any(m in content for m in [
        'plugin:', 'superpowers:', 'hermes builtin',
        'hermes官方', 'from hermes core'
    ]):
        return 'official'
    
    # 2. 自建标记
    if any(m in content.lower() for m in [
        'author: 杨瑒', 'author: 月夜', 'author: jorinyang'
    ]):
        return 'self-built'
    
    # 3. 第三方吸收标记
    if any(m in content.lower() for m in [
        '吸收自', 'adapted from', 'adapted from leonxlnx',
        'adapted from cocoon', 'adapted from nutlope',
        'adapted from vercel', 'adapted from chenglou',
        'adapted from agents365', 'adapted from coleam00',
        'adapted from helloianneo', 'adapted from yizhiyanhua',
        'adapted from freestylefly', 'adapted from open-pencil',
        'adapted from openeuler', 'adapted from lijigang',
        'adapted from orchestra', 'adapted from deepjai',
    ]):
        return 'third-party'
    
    return 'unclassified'  # 需人工判断
```

### Phase 3: 同步执行

> 🔴 **Symlink 穿透规则**：本地技能目录大量使用软链接（当前 212 个）。访问任何技能前必须先解析 symlink 到真实路径，复制时必须使用 `cp -rL` 穿透链接。

#### Symlink 解析

```bash
# 读取 SKILL.md 前先解析 symlink
REAL_PATH=$(readlink -f ~/.hermes-feishu/skills/<category>/<skill-name>/SKILL.md)
# 或整个目录
REAL_DIR=$(readlink -f ~/.hermes-feishu/skills/<category>/<skill-name>)
```

#### 复制到 GitHub（穿透 + 排除）

```bash
# 新增技能：穿透所有 symlink → 复制真实文件
SRC=$(readlink -f ~/.hermes-feishu/skills/<category>/<skill-name>)
DST=/tmp/awesome-skills/<skill-name>
cp -rL "$SRC" "$DST"

# 更新技能：覆盖 SKILL.md
cp "$(readlink -f ~/.hermes-feishu/skills/<category>/<skill-name>/SKILL.md)" "$DST/SKILL.md"

# 清理 __pycache__
find "$DST" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
```

| 命令 | 作用 | 错误做法 |
|------|------|---------|
| `readlink -f` | 解析 symlink 到真实路径 | 直接 `cat` symlink 路径（可能指到别的 profile） |
| `cp -rL` | 递归复制 + 穿透所有层级 symlink | `cp -a`（保留 symlink → GitHub 死链接） |
| `cp -rL` 而非 `cp -r` | 穿透目录级和文件级 symlink | `cp -r` 只处理文件，目录 symlink 仍保留 |

### Phase 4: README 自动更新

基于 GitHub 实际技能清单，更新以下内容：

1. **Badge 计数**：`Skills-{N}` → 精确计数
2. **分类表计数**：每类精确计数（方法论/构建与设计/开发工程/...）
3. **新增/更新条目**：在对应分类表中插入或更新行
4. **版本历史**：最上方新增一行
5. **安装脚本**：如新增分类需更新 case 匹配规则

#### 分类映射表

> ⚠️ 此映射随 README 实际分类变化。最近清理(v5.2.0)展平目录+合并分类。以下为当前映射。

```
技能名模式 → README 分类 (v5.2.0, 89技能，全根目录)
─────────────────────────────────────────
advanced-elicitation, author-methodology-analysis, blue-team,
book-deconstruct, darwin-skill, deep-think, domain-decompose,
edge-case-hunter, editorial-review-*, github-absorb,
external-skill-evaluation, ljg-*, qa-extract, relationship-analysis,
pm-prioritization-frameworks, stakeholder-mapping,
opportunity-solution-tree
  → 🧠 方法论 (20)

answer, answer-standalone, dynamic-workflow, architecture-diagram,
drawio-generation, brandkit, claude-design, design-md, feishu-html,
fireworks-tech-graph, hallmark, html-ppt, huashu-design, humanizer,
pretext, redesign-skill, requesting-code-review, sketch,
strategy-plan-writing, taste-skill, writing-plans,
requirement-alignment-analysis
  → 🏗️ 构建与设计 (22)

agent-native-cli-design, coding-agents, cross-project-adaptation,
dingtalk-cli, subagent-driven-development, supabase-backend,
test-driven-development, wsl-browser-cdp, hermes-instance-sync,
technical-documentation-production, windows-troubleshooting-from-wsl,
github-release-readme, wsl-docker-deploy, firecrawl-web
  → 🔧 开发工程 (14)

skill-evaluator, skill-ab-test, benchmark-generator, agent-tool-system
  → 🤖 AI 工程 (4)

feishu-doc, feishu-table, feishu-wiki, project-kanban, zhike-task-hub
  → 📋 飞书系列 (5)

amap-lbs, jimeng-video, travel-intel, travel-itinerary,
travel-workflow, trip-landing, wechat-article-archive,
zhike-content-output, trip-quote, trip-briefing, guide-exec,
supply-check, vendor-brief, cost-engine, trip-archive, customer-view
  → 🏔️ 贵州之客 · 旅行社全链路 (16)

ara-compiler, ara-research-manager, ara-rigor-reviewer,
systematic-debugging
  → 🔬 研究 (4)

baoyu-article-illustrator, baoyu-comic, baoyu-cover-image,
baoyu-infographic, baoyu-translate, image-analysis
  → 🎨 创意内容 (6)
```

### Phase 5: 提交与推送

**🔴 SSH 优先于 HTTPS**（GFW 屏蔽 HTTPS，但 SSH + 个人 key 可用）：

```bash
# 1. 在解压目录初始化 git（不是从 clone 来的）
cd /c/tmp/awesome-skills-main

# 2. 设置作者
git config user.name "jorinyang"
git config user.email "jorinyang@users.noreply.github.com"

# 3. 用 SSH fetch 拿到真实 origin/main（含全部历史）
git remote add origin git@github.com:jorinyang/awesome-skills.git
export HOME=/c/Users/Aorus
export GIT_SSH_COMMAND="ssh -o ConnectTimeout=30 -i /c/Users/Aorus/.ssh/id_rsa"
git fetch --depth=10 origin main

# 4. 🔴 关键：基于 origin/main 建立可 fast-forward 的本地分支
#    不要用 `git checkout origin/main -- .` + 空 commit —— 会产生 orphan commit 需要 rebase
#    用 reset --soft 让 origin/main 成为本地分支的父提交
git checkout -b main origin/main

# 5. 复制新文件 + 修改 SKILL.md（Phase 3 已拷贝到此目录）

# 6. ⚠️ push 前再次 fetch 确认远端未变（防止 race condition）
git fetch --depth=10 origin main
LOCAL_SHA=$(git rev-parse HEAD)
REMOTE_SHA=$(git rev-parse origin/main)
if [ "$LOCAL_SHA" != "$REMOTE_SHA" ]; then
  echo "⚠️ origin/main 已 ahead —— race condition，需要 rebase"
  git rebase origin/main
fi

# 7. commit + push
git add -A
git commit -m "vX.Y.Z: 描述"
git push origin main
```

#### Phase 5D: Push 失败恢复

> 🔴 **必读**：origin/main 可能在同步过程中被抢先更新（GitHub Actions / 其他 contributor）。每次 push 失败时**不要重试**——先 `git fetch` 然后判断：

| 现象 | 原因 | 处理 |
|------|------|------|
| `non-fast-forward` | origin/main 已 ahead | `git fetch` → 比对 → rebase 或重新基于新 origin/main |
| `non-fast-forward` (no common ancestor) | `checkout origin/main -- .` 产生 orphan commit | 改用 `git checkout -b main origin/main`（已修复，见 Phase 5 步骤4） |
| `Permission denied (publickey)` | SSH key 未被 git 找到 | 确认 `~/.ssh/id_rsa` 存在 + 设置 `GIT_SSH_COMMAND` |
| `Connection timed out` | HTTPS 走代理失败 | 强制走 SSH URL `git@github.com:...` |
| `Could not read from remote` | 同上 | 同上 |

#### Phase 5E: Race Condition 缓解

> 🔴 **观察到的现象**：长会话（5+ 分钟）期间 origin/main 可能被自动 commit 抢先。本次会话累计触发 3 次 push 拒绝。
>
> **缓解策略**：
> 1. Push 之前**最后一次** `git fetch` 对比 origin/main
> 2. 如果 race 发生：放弃本地 commit，重新基于最新 origin/main，cherry-pick 本地变更
> 3. 整个流程压缩到 < 3 分钟（减少 race 窗口）

#### Phase 5F: 推送命令模板（WSL/Windows 通用）

```bash
export HOME=/c/Users/Aorus
export GIT_SSH_COMMAND="ssh -o ConnectTimeout=30 -i /c/Users/Aorus/.ssh/id_rsa"
timeout 90 git push origin main 2>&1 | tail -10
```

> `timeout 90` 防止挂起；`tail -10` 防止输出过多。

### Phase 6: 创建 Release

### Phase 6: 创建 Release（必做 🔴）

> 🔴 **铁律：每次同步必须创建 Release。** 这是全自动闭环的最后一步，不可跳过。
> 历史教训：v5.0.0~v5.2.2 期间 README 版本号一路涨，但 Release 停在 4.8.1——
> 因为 Phase 6 被当作"可选"跳过了 5 个版本。

```bash
# 1. 写 release notes
cat > /tmp/release_notes.md << 'RNEOF'
## 🆕 新增 / 🔄 更新
...（变更摘要，与 README 版本历史行一致）
RNEOF

# 2. 创建 tag（如果 Phase 5 未创建）
git tag -a "v{M}.{m}.{p}" -m "v{M}.{m}.{p} — {一句话总结}"
git push origin "v{M}.{m}.{p}"

# 3. 创建 Release
gh release create "v{M}.{m}.{p}" \
  --title "v{M}.{m}.{p} — {一句话总结}" \
  --notes-file /tmp/release_notes.md

# 4. 验证
gh release view "v{M}.{m}.{p}" --repo jorinyang/awesome-skills
```

> ⚠️ **gh 未登录时的回退**：沙箱/cron 环境通常没有 `gh auth`。check：`gh auth status`。
> - 如果 `gh` 未登录：跳过 Phase 6，将 release notes 缓存到 `/tmp/release_notes.md`，提示用户手动创建。
> - 手动创建命令会一并输出，用户复制粘贴即可。
> - **tag 仍然推送**（`git push origin "vX.Y.Z"`），只是 Release 页面需要手动补。

**release_notes.md 模板**：

```markdown
## 🆕 新增

### {技能名} — {一句话描述}
{2-3句核心能力说明}
> 吸收自 {upstream} ({license})。

## 🔄 更新

### {技能名}
- {变更1}
- {变更2}

## 📊 统计
- 技能总数: {N}（自建 {A} + 三方吸收 {B}）
- 排除官方/插件: {C} 个
```

---

## 🔴 同步检查清单

每次同步前确认：

- [ ] 双源扫描已完成（本地 vs GitHub）
- [ ] 官方/插件技能已过滤（不在同步列表中）
- [ ] **永久排除技能检查**：plan/spike/dingtalk-channel/ocr-and-documents 确认不在同步列表中（classify_skill 第0步强制拦截）
- [ ] **Symlink 解析**：所有源路径已通过 `readlink -f` 解析
- [ ] 软链接已解除（`cp -rL` 而非 `cp -a`；GitHub 端 `find -type l` 必须为 0）
- [ ] `__pycache__/` 已删除
- [ ] README badge 计数已更新
- [ ] README 分类表计数已更新
- [ ] 版本历史已添加新行
- [ ] Push 使用后台模式（网络不稳定时）
- [ ] **Release 已创建**（`gh release view` 验证成功）

---

## 📎 相关文档

- `references/execution-log-2026-07-03.md` — 本次 v5.4.9 同步的实际执行日志（含踩坑清单）
- `references/skill-source-analysis.md` — 技能来源四维判定方法论
- `references/wsl-adaptation-checklist.md` — WSL 适配标记清单
- `scripts/scan_inventory.py` — 双源扫描脚本

## 常见问题

### Q: WSL 迁移后终端 bash 损坏怎么办？
A: Hermes 从 WSL 迁移到 Windows 原生环境后，`terminal` 工具的 bash 层可能持续返回 `WSL_E_LOCAL_SYSTEM_NOT_SUPPORTED`。解决方案：
1. **用 `execute_code` 代替 `terminal`** 执行 git 操作（clone/commit）——沙箱环境可直接运行 Windows git
2. **git push 从沙箱超时**是沙箱 HTTPS 限制，不是网络问题。提交在沙箱环境完成，push 由用户在本地终端手动执行
3. **`~` 路径在沙箱中不指向用户目录**——始终用 `C:\Users\Aorus` 绝对路径
4. **ZIP 下载代替 git clone**：沙箱无法访问 WSL 的 `/tmp/` 路径，用 `urllib.request.urlretrieve` 从 GitHub API 下载 ZIP

### Q: HTTPS git clone 被 GFW 屏蔽怎么办？
A: **不要用 `git clone https://github.com/...`**。改用：
1. **`codeload.github.com` ZIP 镜像**：`https://codeload.github.com/jorinyang/awesome-skills/zip/refs/heads/main` —— urllib 下载后解压，**这是 Phase 1 的首选**
2. **SSH fetch**：解压后用 SSH 从 origin fetch 拿到真实的 git 历史（`git fetch --depth=10 origin main` + `GIT_SSH_COMMAND`）
3. **gh CLI**：需先 `gh auth login`，不推荐用于 cron 自动化

### Q: SSH 推送报 "Permission denied (publickey)" 怎么办？
A: 三步检查：
1. `~/.ssh/id_rsa` 必须存在（路径：`/c/Users/Aorus/.ssh/id_rsa`）
2. `export GIT_SSH_COMMAND="ssh -o ConnectTimeout=30 -i /c/Users/Aorus/.ssh/id_rsa"` —— **必须显式指定 key 路径**，Git 不会自动找
3. `export HOME=/c/Users/Aorus` —— 必须设置 HOME，否则 SSH 找不到 config

### Q: push 反复失败报 "non-fast-forward" 怎么办？
A: **origin/main 在同步期间被抢先更新**。处理：
1. **不要盲目重试 push**——可能覆盖他人提交
2. `git fetch origin main` → 对比 `git log origin/main --oneline -5`
3. 如果 origin/main 是他人的提交 → 联系用户确认是否要 rebase
4. 如果 origin/main 是自动 commit（GitHub Actions）→ 等几分钟后重新 fetch + 重新基于新 HEAD
5. **整个流程压缩到 < 3 分钟**减少 race 窗口

### Q: 发现 README 引用了 GitHub 上已不存在的技能（如 refactor 后）怎么办？
A: **不要自动修复**——这是用户决策点：
1. Phase 1C 输出 `missing = referenced - actual` 列表
2. 在执行报告中标记 ⚠️ 提示用户
3. README 修改超出本次同步范围（涉及 badge 计数 + 分类行删除 + 安装脚本 case 更新 + 指向新仓库）
4. 用户确认后再单独发一个 README 修复版本（MINOR 版本号）

### Q: 本地有但 GitHub 没有的 travel/* 技能？
A: 检查 SKILL.md 中是否有 `plugin:` / `superpowers:` 标记，或来源是否为 Hermes 官方仓库。详见 `references/skill-source-analysis.md` 四维判定方法论。lark-cli/lark-* 系列虽然部分自建，但因含飞书内部 API 配置，也划为"仅本地"。

### Q: 遇到 symlink 怎么办？
A: 本地技能目录使用 `hermes-instance-sync` 创建了大量软链接（当前 212 个）。
- **读取前**：`readlink -f <path>` 解析到真实文件
- **复制时**：`cp -rL` 穿透所有层级 symlink，复制真实内容
- **验证**：`find /tmp/awesome-skills -type l` 必须为空
- **注意**：跨 profile 的 symlink（如 `~/.hermes/skills/ → ~/.hermes-feishu/skills/`）用 `readlink -f` 自动解析

### Q: unclassified 技能怎么处理？
A: 首次遇到时标记为 ⚠️，输出列表让用户确认分类。确认后更新该技能的 SKILL.md 添加分类标记。

### Q: related_skills 双向引用有必要吗？
A: 绝大多数不需要。`related_skills` 的实用价值是声明**数据流/调用方向**——上游技能声明它需要下游技能。反向引用是冗余的。
- **保留双向**：仅当两个技能真正互相调用（如 deep-think ↔ domain-decompose，深钻后需降秩、降秩后需深钻）
- **使用单向**：上游声明下游（brandkit → taste-skill、travel-intel → travel-itinerary、ara-compiler → ara-research-manager）
- **删除无关引用**：独立使用的技能不互相引用（claude-design / huashu-design / sketch）

### Q: 本地有但 GitHub 没有的 travel/* 技能？
A: travel 分类技能均为自建（贵州之客业务），应全部同步。GitHub-only 的残留技能（如 `cost-engine`, `customer-view`）已被 `travel-workflow` 吸收，保留在 GitHub 作为存档。

### Q: README 分类和 GitHub 目录结构不一致怎么办？
A: 以 GitHub 实际目录结构为准。README 中的分类表是面向读者的逻辑分组，可以与物理目录不同。

---

## 版本号规则

使用语义化版本 MAJOR.MINOR.PATCH：
- **PATCH (x.y.Z)**: 技能内容修订、交叉引用修复、触发词调整、metadata去重、配置变更。默认选择。
- **MINOR (x.Y.z)**: 新增/删除技能、目录结构变更、分类重构、READEME重大重写。
- **MAJOR (X.y.z)**: 技能总数跨越 10 的倍数（如 98→102），或全功能生产验证后。

> 原则：从最小版本开始更新。不必要时不要跳版本号。
- **补丁版本 (PATCH)**：每次更新默认版本 —— 维护性变更、1-2 技能调整、描述修正、引用补全、README 微调等

> 🔴 **铁律：默认 PATCH。** 每次同步若无特殊声明，一律升级 PATCH（x.y.Z）。
> 只有「≥3 技能新增/删除」或「分类/目录重构」才升级 MINOR。
> MAJOR 不自行决定，必须用户明确要求。

当前：v5.4.9 (94 技能 — 全根目录，8 分类)

---

## 🔗 技能引用网络规则

> **铁律：`related_skills` 使用单向引用，按数据流/调用方向建立。**
> 仅真正互相调用的技能对保留双向引用。

### 单向规则
- **管线上下游**：上游 → 下游（brandkit → taste-skill → huashu-design）
- **调用方向**：调用者 → 被调用者（blue-team → advanced-elicitation）
- **数据流向**：数据生产者 → 数据消费者（travel-intel → travel-itinerary）
- **独立工具**：不互引（claude-design, huashu-design, sketch 分别独立使用）

### 双向例外（仅此一对）
- deep-think ↔ domain-decompose：深钻后需要降秩，降秩后需要深钻，形成闭环

### 检查方法
```bash
# 验证引用方向一致性
for f in */SKILL.md; do
  name=$(basename $(dirname $f))
  grep "related_skills.*$name" */SKILL.md && echo "⚠️ $name 被反向引用"
done
```

---

## 🔴 清理规则（最高优先级）

> ⚠️ **清理技能仅从 GitHub 仓库移除，绝不动本地 `~/.hermes/skills/`。**
> 本地 Hermes 实例中的技能（含官方/社区/平台专属）是运行依赖，清理操作的目标仅限于 `jorinyang/awesome-skills` 仓库。
>
> ⚠️ **同步时强制过滤官方/社区插件技能。** 同步操作（Phase 2 classify_skill）会在双源扫描后自动排除 `official` 类技能，确保它们只存在于本地而不会出现在 GitHub 仓库中。当用户要求"同步到仓库"时，不要反问"是否包含官方技能"——直接执行过滤。

### 技能清理七步管线

当用户要求清理/移除仓库中的技能时，执行以下标准化管线：

#### Step 1: 来源分析
对目标技能逐一判定来源（四维分类）：
- 🔵 Hermes 系统自带/官方插件 — author 为 SHL0MS/Hermes Agent 或含 plugin 标记
- 🟢 用户自建 — author 为 杨瑒/月夜/jorinyang
- 🟡 自动创建/系统生成 — author=Hermes Agent 且无明确第三方来源
- 🟣 第三方吸收 — SKILL.md 含"吸收自/adapted from"标记

检查维度：author, license, git log 首次出现, README 分类标签, ~/.hermes/skills/ 中是否存在。

#### Step 2: 用户筛选
呈现分析结果，让用户选择保留/移除。同时确认：
- 是否有功能重复需要先解决再删除
- 是否有交叉引用需要后续修复

#### Step 3: 删除目录
```bash
cd /tmp/awesome-skills
git rm -r <skill-dir>
```
注意：部分技能在子目录中（如 `productivity/shipinhao-cold-start/`），需精确路径。
**model-comparison 等仅存于本地 ~/.hermes/skills/ 的技能不需要 GitHub 操作。**

#### Step 4: README 同步更新
四项必须更新：
1. Badge 计数 `Skills-{N}` → 新值
2. 分类表：移除对应行 + 更新分类计数 `(N→N-1)`
3. case 语句：移除安装脚本中的匹配规则
4. 版本历史：新增 PATCH 版本行

#### Step 5: 交叉引用修复
搜索剩余 SKILL.md 中的已删除技能引用：
- `related_skills` 字段 — 移除已删除项
- `called_by` / 管线引用 — 更新或泛化
- 正文中的 `\`skill-name\`` 调用 — 改为通用描述

过滤规则：排除作为通用词汇出现的匹配（如 "plan" 作为名词、"kanban" 作为视图类型）。

#### Step 6: 目录展平（如需要）
若删除暴露出空子目录或存在嵌套结构：
```bash
git mv <subdir>/<skill> <skill>   # 提升到根目录
```
合并重复技能（如 github-release-readme v1 vs v2）。
删除空目录：`ai-engineering/`, `devops/`, `github/`, `media/`, `methodology/`, `productivity/`, `travel/`

#### Step 7: 建立引用网络
清理后为互补技能添加 `related_skills`：
- **单向引用**：按数据流/调用方向（上游→下游，调用者→被调用者）
- **双向例外**：仅 deep-think ↔ domain-decompose
- **独立工具**：不互引（如 claude-design/huashu-design/sketch）
- metadata 去重合并
- 管线上下游在 description 中注明替代方案指向

完成后使用 PATCH 版本号提交。

### 反例（禁止）

- ❌ 不执行双源扫描就直接复制文件——遗漏差异
- ❌ 不先 `readlink -f` 解析 symlink 就访问——可能指到其他 profile 的过期版本
- ❌ 用 `cp -a` 保留软链接——GitHub 上变成死链接（120000 文件类型）
- ❌ 不排除 `__pycache__`——污染仓库
- ❌ WSL 用前台 push——100% 超时
- ❌ 同步后不更新 README badge/分类计数——版本号与内容不一致
- ❌ 把 lark-* 或其他平台专属技能推到 GitHub——泄露内部配置
- ❌ 不检查 git config 就 commit——author 信息混乱
- ❌ 清理技能时删除本地 `~/.hermes/skills/` 中的副本——只操作 GitHub 仓库
- ❌ 同步时反问用户"是否包含官方技能"——直接按分类过滤执行
- ❌ 同步后不创建 Release——README 版本号与 Release 列表脱节（v5.0.0~v5.2.2 历史教训）

---

## 吸收来源

> 本技能 v2.0.0 从"手动同步脚本"升级为"双源自动流水线"——
> 吸收 `hermes-instance-sync` 的双源对比方法论 + `github-absorb` 的分类引擎思想。
