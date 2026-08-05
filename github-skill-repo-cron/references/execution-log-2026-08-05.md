# 2026-08-05 同步执行日志 (v5.4.37)

## 摘要
- **同步成功**：1 技能内容更新（question-bank-pipeline v1.2.0）
- **跳过**：18 个 content_diffs（14 OFFICIAL + 1 CRON-SLIM + 3 unclassified REPORT）
- **HEAD**: v5.4.37 (commit 85ea0a6)
- **Release**: https://github.com/jorinyang/awesome-skills/releases/tag/v5.4.37

## 流水线执行

### Phase 1A: 工作目录
- 复用 `C:\tmp\awesome-skills-20`（v5.4.36 已 init，git 状态干净，SSH origin 已配）
- 跳过 codeload ZIP 下载（节省 90 秒）
- ⚠️ **新坑修复**：`glob(r'C:\tmp\awesome-skills-*')` 遇到 `awesome-skills-prev-backup` 备份目录时 `int(p.split('-')[-1])` 报 ValueError。修复：filter `if p.split('-')[-1].isdigit()`。

### Phase 1B: 双源扫描
- 本地 400 技能（双 profile: hermes-feishu + hermes）
- GitHub 113 技能
- 共享 113 | 真正相同 94 | content_diffs 19 | local_only 287 | gh_only_real 0

### Phase 1C: README 一致性
- 索引与磁盘 100% 一致
- Badge 113 = 实际 113（无变化）
- v5.4.36 已 commit 但 README 未插入 changelog 行 — 本次顺手补上

### Phase 2: 分类过滤
- v5.4.21+ 完整分类器（PERMANENTLY_EXCLUDED → prefix → NAME_OFFICIAL_HINTS → official fingerprints → adapted-from → author self-built → Hermes Agent fallback）
- 19 个 content_diffs 分类结果：
  - 14 OFFICIAL 跳过
  - 1 SELF-BUILT CRON-SLIM 跳过 (darwin-skill)
  - 1 SELF-BUILT SYNC (question-bank-pipeline v1.2.0)
  - 3 UNCLASSIFIED REPORT
- 250 个 local_only 全部归类为 OFFICIAL / UNCLASSIFIED / .bak / cycle-addendum

### Phase 3: 同步
- 复制 question-bank-pipeline 完整目录（symlink 穿透 + __pycache__ 清理）
- 4 个 references 新增文件全部带过去
- ⚠️ **新坑记录**：`shutil.copytree(real_local, GH_DIR, symlinks=False)` 执行后 Python 报 `UnicodeDecodeError` 来自 `subprocess.run(['find', ...])` 线程 reader——次要问题（subprocess 输出不是 UTF-8），不影响实际文件复制成功。

### Phase 4: README 更新
- PATCH 版本：v5.4.36 → v5.4.37
- v5.4.24 lesson: 用 str.replace 而非 re.sub 插入版本行
- HEAD=CRLF 保留一致
- ⚠️ **新坑记录**：`read_file` 工具对 CRLF 文件报告 "Binary file - cannot display as text"——实际上是 UTF-8 with CRLF terminators，不是真正二进制。绕过方式：用 Python `open(path, 'rb').read()` 读取、显示 `has_crlf` 标志后再用 `'\r\n'` 切分行。

### Phase 5: 提交推送
- HEAD = v5.4.37 (85ea0a6)
- 推送至 origin/main (e69376b..85ea0a6)
- SSH 直连成功，无 race condition
- ⚠️ **新坑记录**：`git diff --shortstat` 显示 `README.md: 1366 (+/-)` 实际上 99% 是 CRLF 噪声。**永远用 `git diff --shortstat -w` 验证真实行变更**——本轮真实只有 2 行新增（v5.4.37 + v5.4.36 changelog）。
- ⚠️ **patch 着陆原则**: HEAD 已是 CRLF 编码，`git config core.autocrlf false` 已配，但 `git diff` 仍按行统计数量而非字节差异 → 误报「readme 改动 1366 行」。

### Phase 6: Release
- gh auth L1 路径已认证直通过
- Release: https://github.com/jorinyang/awesome-skills/releases/tag/v5.4.37

## 关键决策
- **v5.4.23 行级 diff 验证规则第三轮实战**：question-bank-pipeline 同版本 v1.2.0 + ratio=0.969 → 行级 diff 发现本地多 4 行 + 1 references → 判定本地新版本，覆盖 GH
- **v5.4.22 bytes ratio < 0.7 规则**：darwin-skill ratio=0.116 再次正确截获 cron-slim 分叉
- **大版本差异报告**：3 项 unclassified (external-skill-evaluation / claude-design / dashiai-ppt-hermes) 等待用户补 `author:` 触发自动归类推送

## 下一轮关注
- external-skill-evaluation: GH v1.4.0 > 本地 v1.3.0 (skip)
- claude-design: 本地 v1.1.0 > GH v1.0.0 (等 author)
- dashiai-ppt-hermes: 本地 0b vs GH v1.0.0 10645b (本地缺失，等 author)
- 持续积累 250+ local_only unclassified 等待用户批量补 author 标记

## 时间线改进建议
- **本轮仅 1 技能同步**：建议未来 cron 在周日/周一（用户操作密集期）路径上加一道 filter：若 `local_only_total > 100` → 大概率没有新增自建技能 → 倾向静默退出 + scan-only 报告，避免无意义消耗 token。
- **本地-远端最近 36 小时内无新增 commit 时**：明确跳过 push 验证，直接进入 content_diff 模式。
