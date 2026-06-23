---
name: github-release-readme
description: >-
  同步技能→更新README→创建Release的一键流水线。自动扫描本地+GitHub双源，
  过滤官方/插件技能（仅同步自建+第三方吸收），更新README分类/计数/版本历史，
  提交并推送至 jorinyang/awesome-skills。
  触发：同步到仓库/更新awesome-skills/发release/迭代README/发布版本/同步技能/GitHub同步。
version: 2.0.0
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
| **官方/插件技能** | 来自 Hermes 内置/插件（superpowers/feishu-media 等），或 SKILL.md 含 plugin 标记 | lark-* (27个), coding-agents, kanban, memos-cloud |
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

```bash
cd /tmp && rm -rf awesome-skills
git clone --depth 1 https://github.com/jorinyang/awesome-skills.git

# 扫描本地 + GitHub 双源
python3 /tmp/scan_inventory.py
```

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
    
    # 1. 官方/插件标记（最高优先级）
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

```
技能名模式 → README 分类
─────────────────────────
advanced-elicitation, blue-team, book-deconstruct, darwin-skill,
deep-think, domain-decompose, edge-case-hunter, editorial-review-*,
github-absorb, external-skill-evaluation, ljg-*, qa-extract,
relationship-analysis, pm-prioritization-frameworks, stakeholder-mapping,
opportunity-solution-tree, author-methodology-analysis
  → 🧠 方法论

answer, answer-standalone, architecture-diagram, drawio-generation,
brandkit, claude-design, design-md, feishu-html, fireworks-tech-graph,
hallmark, html-ppt, huashu-design, humanizer, pretext, redesign-skill,
sketch, strategy-plan-writing, writing-plans, requirement-alignment-analysis,
dynamic-workflow, taste-skill
  → 🏗️ 构建与设计

agent-native-cli-design, coding-agents, cross-project-adaptation,
dingtalk-cli, kanban, plan, spike, subagent-driven-development,
supabase-backend, test-driven-development, systematic-debugging,
requesting-code-review, codebase-inspection, dogfood,
technical-documentation-production, windows-troubleshooting-from-wsl,
hermes-instance-sync, wsl-browser-cdp
  → 🔧 开发工程

skill-evaluator, skill-ab-test, benchmark-generator, agent-tool-system
  → 🤖 AI 工程

feishu-doc, feishu-table, feishu-wiki, project-kanban, zhike-task-hub,
yuanbao, github-release-readme
  → 📋 工具与集成

amap-lbs, travel-intel, travel-itinerary, trip-landing, trip-*,
travel-workflow, zhike-content-output, wechat-article-archive,
shipinhao-cold-start, jimeng-video
  → 🏔️ 贵州之客

ara-compiler, ara-research-manager, ara-rigor-reviewer
  → 🔬 研究

baoyu-*, youtube-content, image-analysis
  → 🎨 创意内容

ocr-and-documents, pdf-content-generation
  → 📄 文档生成
```

### Phase 5: 提交与推送

```bash
cd /tmp/awesome-skills
git add -A
git commit -m "v{M}.{m}.{p}: {变更摘要}"

# WSL 推送用后台模式（前台必超时）
git push origin main  # 在 terminal(background=true, notify_on_complete=true) 中执行
```

⚠️ **WSL push 铁律**：`git push` 在 WSL 前台模式下总是超时。必须使用 `terminal(background=true, notify_on_complete=true)`。

### Phase 6: 创建 Release（可选）

```bash
gh release create v{M}.{m}.{p} \
  --title "v{M}.{m}.{p} — {一句话总结}" \
  --notes-file /tmp/release_notes.md
```

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
- [ ] **Symlink 解析**：所有源路径已通过 `readlink -f` 解析
- [ ] 软链接已解除（`cp -rL` 而非 `cp -a`；GitHub 端 `find -type l` 必须为 0）
- [ ] `__pycache__/` 已删除
- [ ] README badge 计数已更新
- [ ] README 分类表计数已更新
- [ ] 版本历史已添加新行
- [ ] WSL push 使用后台模式

---

## 常见问题

### Q: 如何判断一个技能是否"官方"？
A: 检查 SKILL.md 中是否有 `plugin:` / `superpowers:` 标记，或来源是否为 Hermes 官方仓库。lark-cli/lark-* 系列虽然部分自建，但因含飞书内部 API 配置，也划为"仅本地"。

### Q: 遇到 symlink 怎么办？
A: 本地技能目录使用 `hermes-instance-sync` 创建了大量软链接（当前 212 个）。
- **读取前**：`readlink -f <path>` 解析到真实文件
- **复制时**：`cp -rL` 穿透所有层级 symlink，复制真实内容
- **验证**：`find /tmp/awesome-skills -type l` 必须为空
- **注意**：跨 profile 的 symlink（如 `~/.hermes/skills/ → ~/.hermes-feishu/skills/`）用 `readlink -f` 自动解析

### Q: unclassified 技能怎么处理？
A: 首次遇到时标记为 ⚠️，输出列表让用户确认分类。确认后更新该技能的 SKILL.md 添加分类标记。

### Q: 本地有但 GitHub 没有的 travel/* 技能？
A: travel 分类技能均为自建（贵州之客业务），应全部同步。GitHub-only 的残留技能（如 `cost-engine`, `customer-view`）已被 `travel-workflow` 吸收，保留在 GitHub 作为存档。

### Q: README 分类和 GitHub 目录结构不一致怎么办？
A: 以 GitHub 实际目录结构为准。README 中的分类表是面向读者的逻辑分组，可以与物理目录不同。

---

## 版本号规则

- **主版本**：技能总数跨越 10 的倍数（如 98→102）
- **次版本**：新增技能或重要联动更新
- **补丁版本**：纯文档/描述修正

当前：v4.9.0 (102 技能 — 自建+三方吸收)

---

## 反例（禁止）

- ❌ 不执行双源扫描就直接复制文件——遗漏差异
- ❌ 不先 `readlink -f` 解析 symlink 就访问——可能指到其他 profile 的过期版本
- ❌ 用 `cp -a` 保留软链接——GitHub 上变成死链接（120000 文件类型）
- ❌ 不排除 `__pycache__`——污染仓库
- ❌ WSL 用前台 push——100% 超时
- ❌ 同步后不更新 README badge/分类计数——版本号与内容不一致
- ❌ 把 lark-* 或其他平台专属技能推到 GitHub——泄露内部配置
- ❌ 不检查 git config 就 commit——author 信息混乱

---

## 吸收来源

> 本技能 v2.0.0 从"手动同步脚本"升级为"双源自动流水线"——
> 吸收 `hermes-instance-sync` 的双源对比方法论 + `github-absorb` 的分类引擎思想。
