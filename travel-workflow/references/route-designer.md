# route-designer — 行程路线设计器

> 原为独立技能，现作为 `travel-workflow` 管线的参考文档。脚本执行路径保持不变。

**职责：** 输入原始活动价目表 + 客户需求 → 输出飞书 docx 行程方案。是 9 技能管线的前置设计阶段，产出物为 `trip.json` 上游。

## 触发条件

用户提供活动项目价目表（Excel/docx/飞书文档）+ 明确人数/天数/主题需求时触发。

## 工作流（5 阶段）

### Stage 1 — 解析活动目录

从 Excel/docx/飞书文档中提取所有项目：名称、类型（理疗/文化/手作/户外）、时长、单价、团队价、备注（人数下限/场地费等）。

```bash
# Excel
python3 -c "import openpyxl; ..."  # 直接读取

# docx
python3 -c "import zipfile, xml.etree.ElementTree as ET; ..."
```

按类型分组为：中医理疗、文化讲座、手作体验（扎染/香囊/永生花）、布依文化活动、其他。

### Stage 2 — 设计方案骨架

根据客户需求确定：
- **总天数** × **晚间数**（=天数−1，首晚可能有欢迎活动）
- **住宿基地**（默认纳具和园，可替换为云屯/其他）
- **日间景区穿插**（黔西南核心资源：万峰林、马岭河、万峰湖+吉隆堡、峰林布依、贞丰双乳峰、安龙招堤、二十四道拐、花江世界大桥、贞丰古城、放马坪、阿妹戚托小镇）
- **轻户外资源**（栖水谷自有：马鞭田桨板、犀牛洞探洞+天坑）
- **每日结构**：晨练→上午景区→午餐→下午活动/理疗→晚餐→晚间疗愈
- **分组**：≥60 人分 4 组轮转

### Stage 3 — 匹配晚间项目

从活动目录中精选 10 个晚间项目（如果天数≥10），按以下原则：
- 类型交替：文化之夜 / 理疗 / 手作 / 讲座轮换
- 强度匹配：户外日→设备理疗/熏蒸解乏，文化日→讲座/手作
- 高潮节点：首晚篝火+八音座唱，末晚告别晚宴

### Stage 4 — 编排每日行程

逐日填充：时间槽 → 活动 → 详情描述。格式规范：

```xml
<h2>Day N — 标题·副标题</h2>
<callout emoji="🎯" background-color="light-green" border-color="green">
  <p><b>主题：</b>...</p>
</callout>
<table>
  <colgroup><col width="80"/><col width="120"/><col width="360"/></colgroup>
  <thead>
    <tr><th background-color="light-gray">时段</th><th background-color="light-gray">活动</th><th background-color="light-gray">详情</th></tr>
  </thead>
  <tbody>
    <tr><td>HH:MM-HH:MM</td><td>活动名</td><td><b>亮点粗体</b>——详细描述</td></tr>
    <tr><td background-color="light-yellow">20:00-21:00</td><td background-color="light-yellow"><b>🌙 晚间疗愈N</b></td><td background-color="light-yellow"><b>项目名</b>（价格·时长）——说明</td></tr>
  </tbody>
</table>
```

晚间行用 `light-yellow` 底色区分。

### Stage 5 — 费用估算 + 输出

- 汇总晚间疗愈费用（单价×人数）、日间项目费用（含场地费/教学费）
- 产出费用汇总表（人均 + 合计），标注待确认项
- 整体输出：`lark-cli docs +create --api-version v2 --as user --content @file.xml`

## 文档撰写规则

- 所有内容用 XML 格式（非 markdown），统一 `<table>` 结构
- 每个 `h2` 章节之间用 `<hr/>` 分隔
- 价格数字加粗 `<b>368元</b>`
- 金额汇总用 `<callout emoji="💰" background-color="light-yellow">` 高亮
- 备注/限制条件用 `<callout emoji="📝" background-color="light-gray">`
- 无发票项目用 `<span text-color="red">` 标注

## lark-cli 操作技巧

- `docs +create` + `@file` 须用 cwd 相对路径：`cd /tmp && lark-cli docs +create ... --content @file.xml`
- 创建后编辑优先 `str_replace --doc-format markdown --pattern "前缀...后缀"` 做跨 block 整节替换
- 避免 `append`——可能返回 `ok: true` 但 `result: failed`（权限 4030004），需检查 `result` 字段
- 写权限缺失时用 split-flow auth：`lark-cli auth login --scope "docx:document:write_only" --no-wait --json` → 生成 QR → 用户授权 → `--device-code <code>` 完成
- 两个身份都失败时回退：新 `+create` 完整文档

## 住宿替换变体

当用户要求"换住宿基地 + 剔除康养项目做二次消费"时：
1. 全局替换住宿名
2. 剔除所有晚间疗愈/理疗/手作/讲座行
3. 空出的康养日替换为周边探索（古镇/城市漫游/骑行等）
4. 将所有剔除项目汇总为「二次消费总览」章节，按类别分表列出
5. 底部添加费用结构说明（基础团费 vs 二次消费 vs 轻户外）

## 与下游管线衔接

本阶段产出物为飞书 docx 行程方案。后续进入 `travel-workflow` 管线时，需将行程方案结构化抽取为 `trip.json`，再由下游脚本生成交付物。
