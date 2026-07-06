# 批量同步 double-evolution 追踪网络

当 `double-evolution` 的"已关联技能"列表与 `jorinyang/awesome-skills` 仓库实际技能数脱节时，用此脚本一键对齐。

## 前置条件

```bash
git clone https://github.com/jorinyang/awesome-skills.git /tmp/awesome-skills
```

## 批量添加 `related_skills: [double-evolution]`

仓库中 SKILL.md 的 frontmatter 存在 3 种格式，需分段处理：

### 格式 1：含 `metadata.hermes.related_skills` 字段

匹配 `related_skills: [...]` 正则，直接在列表末尾追加 `, double-evolution`。约占 70%。

```python
related_match = re.search(r'related_skills:\s*\[([^\]]*)\]', content)
new = f"related_skills: [{items}, double-evolution]"
```

### 格式 2：有 frontmatter 但无 `related_skills`

锚定 `version:` / `tags:` / `triggers:` / `category:` 字段，插入 `related_skills: [double-evolution]` 到其上方。约占 20%。

```python
if '\nversion:':
    content = content.replace('\nversion:', '\nrelated_skills: [double-evolution]\nversion:')
elif '\ntags:':
    ...
```

### 格式 3：极简 frontmatter（仅 `name` + `description`）

仅有 `name:` 和 `description:` 两个字段，无其他锚点。用 `---` 分隔符定位 frontmatter 结束位置插入。

```python
parts = content.split('---', 2)
new_fm = parts[1].rstrip() + '\nrelated_skills: [double-evolution]\n'
content = '---' + new_fm + '---' + parts[2]
```

### 验证

```bash
cd /tmp/awesome-skills
grep -rl "double-evolution" --include="SKILL.md" | wc -l
# 期望输出 = 仓库技能总数
```

## 同步 double-evolution 自身 SKILL.md

批量添加完成后，还必须更新 `double-evolution/SKILL.md` 中的"已关联技能"列表，按分类列出全部技能名。

参考：`~/.hermes-feishu/skills/methodology/double-evolution/SKILL.md` 的"已关联技能"章节格式。

## 提交

```bash
cd /tmp/awesome-skills
git add -A
git commit -m "feat(tracking): 全量技能纳入 double-evolution 追踪网络"
git push origin main
```
