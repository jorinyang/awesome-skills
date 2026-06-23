---
name: github-release-readme
description: 同步技能→更新README→创建Release的一键流水线。当完成技能创建/更新后，触发将变更同步到 jorinyang/awesome-skills 仓库并创建 GitHub Release。触发：同步到仓库/更新awesome-skills/发release/迭代README/发布版本。
version: 1.0.0
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
metadata:
  hermes:
    tags: [github, release, readme, sync, pipeline]
    related_skills: []
    repo: jorinyang/awesome-skills
---

# GitHub Release & README · 一键同步流水线

当技能创建/更新后，执行以下流程同步到 `jorinyang/awesome-skills` 仓库。

## 流程

### Step 1: 识别变更

列出本次 session 中创建或修改的技能：

```bash
# 已创建（新技能）
# 已修改（patch过的技能）
```

### Step 2: 同步 SKILL.md

```bash
cd /tmp/awesome-skills
git pull origin main

# 新增技能：复制到仓库
cp ~/.hermes/skills/<category>/<skill>/SKILL.md <skill>/SKILL.md

# 更新技能：覆盖
cp ~/.hermes/skills/<category>/<skill>/SKILL.md <skill>/SKILL.md
```

**⚠️ TUN代理注意**：在 WSL 环境下，git push/pull/clone 可能超时。所有 git/gh 命令前需 `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY`。

### Step 3: 更新 README

1. **Badge 计数**：`Skills-{N}` → `Skills-{N+新增}`
2. **技能索引表**：在对应分类表中插入新行
3. **设计管线图**（如涉及设计技能）
4. **版本历史**：最上方新增一行
5. **安装脚本**：如新技能需新分类匹配规则

### Step 4: 提交并推送

```bash
cd /tmp/awesome-skills
git add -A
git commit -m "v{M}.{m}.{p}: {变更摘要}"
git push origin main
```

### Step 5: 创建 Release

```bash
gh release create v{M}.{m}.{p} \
  --title "v{M}.{m}.{p} — {一句话总结}" \
  --notes-file /tmp/release_notes.md
```

**release_notes.md 模板**：

```markdown
## 新增

### 🆕 {技能名} — {一句话描述}
{2-3句核心能力说明}

适应自 {upstream repo} ({license})。

## 更新

### {技能名}
- {变更1}
- {变更2}
```

## 版本号规则

`jorinyang/awesome-skills` 使用语义化版本：
- **主版本**：技能总数跨越 10 的倍数（如 48→50）
- **次版本**：新增技能或重要联动更新
- **补丁版本**：纯文档/描述修正

当前：v4.9.0 (102 技能)
