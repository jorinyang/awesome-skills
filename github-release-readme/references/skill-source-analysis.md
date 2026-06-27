# 技能来源判定方法论

当需要清理仓库或评估技能归属时，对每个技能从以下维度判定来源。

## 判定维度

| 维度 | 检查内容 | 工具/方法 |
|------|---------|----------|
| **SKILL.md frontmatter** | `author`, `license`, `version` 字段 | 直接读取 `---` 块 |
| **Git 提交历史** | 首次出现时间、提交信息中的关键词 | `git log --all --oneline --diff-filter=A -- <path>` |
| **README 分类标签** | 标注为"自建核心""三方吸收""方法论开发" | 搜索 README 中的技能详解段落 |
| **本地实例存在性** | 是否在 `~/.hermes/skills/` 中 | `ls ~/.hermes/skills/<name>/` |
| **SKILL.md 内容线索** | 吸收声明、版权声明、源仓库链接 | 搜索"吸收自""adapted from""吸收 ""fork""source:" |

## 四类归属判断

### 1. Hermes 系统自带 / 官方社区插件
**特征**：
- author 为 `SHL0MS`、`Hermes Agent`、`Hermes Agent (consolidated umbrella)` 等
- 标记 `adapted from obra/superpowers`、`adapted from gsd-build/get-shit-done`
- 存在于 `~/.hermes/skills/` 且来自 Hermes 发行版/插件系统
- README 中无"吸收自"标记
- **处理**：保留在本地 Hermes，不同步到 GitHub

### 2. 用户自建
**特征**：
- author 为 `杨瑒`、`月夜`、`jorinyang`
- 内容包含专有业务术语（如"贵州之客""之客"）
- 引用个人基础设施路径（`~/.hermes-feishu/`）
- **处理**：同步到 GitHub（自建核心资产）

### 3. 第三方吸收
**特征**：
- SKILL.md 明确写"吸收自 <repo>"或"adapted from <repo>"
- author 标记为 `杨瑒 (月夜)` 但内容有明确上游来源
- 包含 MIT/Apache 等第三方 license 声明
- **处理**：同步到 GitHub（注明来源和 license）

### 4. 自动生成
**特征**：
- author 为 `Hermes Agent`
- 无明确的第三方来源声明
- 无用户手动创建痕迹
- 功能单一、无业务关联
- **处理**：评估价值后决定保留或清理

## 实践案例：v5.1.0 清理判定

| 技能 | author | 归属 | 处置 |
|------|--------|------|------|
| creative-ideation | SHL0MS | Hermes 社区 | 移除 |
| kanban | Hermes Agent (consolidated) | Hermes 官方 | 移除 |
| plan | Hermes Agent (adapted from superpowers) | Hermes 吸收 | 移除 |
| spike | Hermes Agent (adapted from gsd-build) | Hermes 吸收 | 移除 |
| dingtalk-channel | jorinyang | 用户自建(但低价值) | 移除 |
| agent-tool-system | 杨瑒 (月夜) | 用户自建(吸收OpenPencil) | **保留** |
| shipinhao-cold-start | (none) | 用户自建(之客业务) | 移除 |
| codebase-inspection | Hermes Agent | 自动生成 | 移除 |
| ocr-and-documents | Hermes Agent | 自动生成 | 移除 |
