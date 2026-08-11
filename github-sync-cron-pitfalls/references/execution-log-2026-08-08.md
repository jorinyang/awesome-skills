# Sync run 2026-08-08: stale release tag collision and CRLF-safe commit

本轮实际验证的可复用经验：

1. codeload ZIP 工作目录没有 `.git`，必须先 `git init -b main`，设置作者和 `core.autocrlf=false`，再添加 SSH origin、fetch、`reset --soft origin/main`、`reset HEAD`。
2. 本地与 GitHub 比对后，只有明确判定为 self-built/third-party 且方向证据充分的变更才复制；本轮唯一明确同步项为 `github-sync-cron-pitfalls`。
3. 本地 Windows 工作树中的 CRLF 会让 `git diff --check` 把整文件报告为 trailing whitespace。对已确认需要提交的文本文件逐文件按实际格式归一化为 LF 后再 `git add`，并用 `git diff --cached --stat` 复核真实变更量。
4. 推送前必须重新 fetch；本轮 `33c16fb..e101b58 main -> main` 推送成功。
5. 不能从本地常量盲目生成 Release 版本。本轮 `v5.4.37` 已存在且指向历史提交，`gh release create` 返回 `HTTP 422: Release.tag_name already exists`。后续应从远端 tags 动态计算下一个 PATCH，并在创建前检查 tag/release 是否已存在；若已有同名 tag 指向别的提交，默认不要覆盖历史发布，改用下一个版本号。
6. `gh auth status` 可能同时显示一个有效账号和一个失效账号；应以目标账号/仓库操作实际结果为准，不要因失效的非 active 账号阻断 L1 路径。

真实产物：commit `e101b58` 已推送到 `jorinyang/awesome-skills/main`；本轮 Release 未创建，因为 `v5.4.37` 已存在。
