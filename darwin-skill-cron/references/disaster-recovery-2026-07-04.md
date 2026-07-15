# 技能目录灾难恢复记录 — 2026-07-04

## 事件
`darwin-nightly-optimize` cron (job_id: 4306d2598fcd) 的 sub-agent 通过 `delegation` toolset
删除了 `.hermes/skills/` 中 ~155 个未 git 追踪的技能子目录。仅剩 13 个顶层目录。

## 根因
1. Cron job 的 `enabled-toolsets` 包含 `delegation`
2. Sub-agent 通过 delegation 获得了不受限的文件操作能力
3. `.hermes/skills/` 的 git repo 只追踪了 19 个文件（9 个技能），其余均为 untracked
4. Sub-agent 执行了目录级删除操作而非单文件 `patch`

## 恢复步骤

### 1. 评估损害
```bash
# 检查 .hermes/skills/ 剩余目录
ls .hermes/skills/ | wc -l
# 检查 .hermes-feishu/skills/ 中的 broken symlinks
find .hermes-feishu/skills/ -type l ! -exec test -e {} \; | wc -l
```

### 2. 从 awesome-skills 恢复
```bash
# awesome-skills 是发布级技能源（约 88 个技能含 SKILL.md）
cd ~/awesome-skills
for d in */; do
  name="${d%/}"
  [ "$name" = "skills" ] && continue
  [ -d "$HOME/.hermes/skills/$name" ] && continue
  cp -r "$name" "$HOME/.hermes/skills/"
done
```

### 3. 交叉备源恢复
```bash
# hermes-agent profile 含少数独有技能
cp -r ~/.hermes/hermes-agent/skills/yuanbao ~/.hermes/skills/
cp -r ~/.hermes/hermes-agent/skills/dogfood ~/.hermes/skills/
```

### 4. 清理死链
```bash
# 删除不可恢复的 broken symlinks
find ~/.hermes-feishu/skills/ -type l ! -exec test -e {} \; -delete
```

### 5. Git 加固
```bash
cd ~/.hermes/skills
# 添加 .gitignore 避免再次丢失
echo ".curator_state
.usage.json
.usage.json.lock
development/
devops/
openyida/" > .gitignore
git add -A
git commit -m "recovery: restore deleted skills from awesome-skills"
```

### 6. 停 cron
```bash
# 暂停肇事 cron 直到修复
cronjob pause 4306d2598fcd
```

## 恢复结果
- 恢复 88 个技能（awesome-skills）+ 2 个（hermes-agent）
- 移除 41 个不可恢复的 broken symlinks
- 永久丢失 ~10 个技能（creative-ideation, dingtalk-channel, kanban, memos-cloud, model-comparison, hermes-instance-migration, hermes-platform-migration, openclaw-imports/*, osint/shadowbroker-osint）
- 497 files committed, zero broken symlinks
- 192 skills loaded normally

## 防御措施
- 从 cron enabled-toolsets 中移除 `delegation`
- 所有技能目录纳入 git 追踪
- 添加 pre-flight git check
- 禁止子 agent 执行目录级删除操作
