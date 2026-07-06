# 外部技能吸收方法论

吸收自 ljg-skills 项目的实践经验。当评估和吸收外部技能仓库时使用。

## 六阶段流程

### Phase 1: 深度读取

不是读 README 和 frontmatter。是读**完整 SKILL.md 内容**，包括所有 reference 文件和方法论细节。

关键：理解三层结构——
- 第 1 层：认知哲学（"灵魂"——最高法则、核心信条）
- 第 2 层：方法论框架（"骨架"——具体步骤、判据、取景框）
- 第 3 层：输出格式层（"皮肤"——工具依赖、文件格式、平台绑定）

第 1/2 层可吸收，第 3 层必须本地化替换。

### Phase 2: 冲突矩阵

四维分类每个技能：

| 判定 | 条件 | 动作 |
|------|------|------|
| 🟢 独立 | 无现有技能覆盖，方法论独特 | 创建新技能 |
| 🟡 吸收 | 与现有技能有交集但不完全重叠 | 提取方法论精华注入现有技能 |
| 🔴 冲突 | 生态/工具链/定位完全冲突 | 放弃 |
| ⚪ 无关 | 场景太窄、非业务域、低价值 | 跳过 |

### Phase 3: 三层适配

- **可直接安装**：方法论+工具都兼容 → 创建独立技能
- **吸收精华**：方法论有价值但工具冲突 → 提取框架，本地化重建
- **跳过**：完全冲突或低价值 → 记录理由，不创建

### Phase 4: Companion 技能模式

当目标技能是**系统内置技能**（如 humanizer/advanced-elicitation/baoyu-infographic），无法直接 patch 时：
- 创建 companion 技能（命名：`ljg-{domain}` 或 `{original}-extension`）
- 在 metadata 中声明 `companion_to` 和 `co_load_with`
- 作为增强层协同加载，不替代原技能

### Phase 5: 触发场景细化

触发条件必须细化到**业务场景矩阵**级别：
```
| 场景 | 触发信号 | 示例 |
|------|---------|------|
| {具体业务场景} | {用户话语中的信号} | {真实示例} |
```

不能停留在笼统关键词列表。每张矩阵覆盖一个业务域。

### Phase 6: 仓库同步

```
# 更新 awesome-skills
gh repo clone jorinyang/awesome-skills -- --depth 1
cp ~/.hermes-feishu/skills/*/SKILL.md awesome-skills/
# 更新 README: badge + 技能索引 + 版本历史
git commit && git push && gh release create
```

**注意事项**：
- WSL 下 `unset http_proxy https_proxy` 避免代理超时
- SSH clone 失败时用 `gh repo clone` 利用 HTTPS 认证
- 跨 10× 里程碑升级主版本号
