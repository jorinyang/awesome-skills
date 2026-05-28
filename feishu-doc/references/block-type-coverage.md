# 飞书文档 Block 类型覆盖率验证报告

> 验证时间：2026-05-27 | 验证方式：`lark-cli docs +create --api-version v2 --doc-format xml` + `lark-cli wiki +node-create`

## Docx XML 直接支持（24 种）

| # | 类型 | 标签 | 说明 |
|---|------|------|------|
| 1 | 标题 H1-H9 | `h1` ~ `h9` | 九级标题 |
| 2 | 正文段落 | `p` | 支持 `<b>` `<em>` `<del>` `<u>` `<code>` `<span text-color>` `<span background-color>` `<br/>` |
| 3 | 无序列表 | `ul` / `li` | 支持嵌套 |
| 4 | 有序列表 | `ol` / `li seq="auto"` | 自动编号 |
| 5 | 代码块 | `pre lang="X"` / `code` | 语法高亮 + `caption` 标题 |
| 6 | 待办事项 | `checkbox done="bool"` | 勾选状态 |
| 7 | 引用块 | `blockquote` | 标准引用 |
| 8 | 分割线 | `hr/` | 视觉分隔 |
| 9 | 高亮卡片 | `callout` | `emoji` + `background-color` + `border-color` + `text-color`，子块支持文本/标题/列表/待办/引用 |
| 10 | 分栏布局 | `grid` / `column` | 2-5 栏，`width-ratio` 控制比例 |
| 11 | 表格 | `table` / `thead` / `tbody` / `tr` / `th` / `td` | 含 `colgroup`/`col` 列宽、`background-color`、`vertical-align`、`colspan`/`rowspan` |
| 12 | 网络图片 | `img href="..."` | 支持 `width` `height` `caption` `name`，URL 自动下载 |
| 13 | 文件附件 | `source name="..."` | ⚠️ 需通过 `+media-insert` 上传后获得 token |
| 14 | Mermaid 图表 | `whiteboard type="mermaid"` | 自动创建 whiteboard block |
| 15 | PlantUML 图表 | `whiteboard type="plantuml"` | 自动创建 whiteboard block |
| 16 | SVG 画板 | `whiteboard type="svg"` | 直接嵌入自包含 SVG |
| 17 | 空白画板 | `whiteboard type="blank"` | 后续用 `+whiteboard-update` 写入 |
| 18 | 电子表格 | `sheet type="blank"` | 自动创建嵌入式 sheet |
| 19 | 会话卡片 | `chat_card chat-id="..."` | 嵌入群聊卡片 |
| 20 | @用户 | `cite type="user" user-id="..."` | 解析为真实姓名 |
| 21 | @文档 | `cite type="doc" doc-id="..."` | 含文档标题 |
| 22 | 行内公式 | `latex` | LaTeX 渲染 |
| 23 | 书签卡片 | `bookmark name="..." href="..."` | 富媒体链接卡片（地图/视频/抖音等） |
| 24 | 按钮 | `button action="OpenLink" src="..."` | 可点击按钮 |
| 25 | 时间提醒 | `time expire-time="..." notify-time="..." should-notify="bool"` | 文档内提醒 |
| 26 | 引文 | `cite type="citation"` | ⚠️ 独立块可能不渲染，建议行内使用 |
| 27 | 链接 | `a href="..."` | ⚠️ 普通链接，富媒体卡片请用 `bookmark` |

> ⚠️ `<a type="url-preview">` 在 XML 中会被降级为普通 `<a>` 链接。富媒体卡片绑定用 `<bookmark>`。

## wiki +node-create 独立节点（5 种）

| # | 类型 | obj_type | 说明 |
|---|------|----------|------|
| 28 | 飞书文档 | `docx` | `lark-cli wiki +node-create --obj-type docx` |
| 29 | 多维表格 | `bitable` | `lark-cli wiki +node-create --obj-type bitable` |
| 30 | 思维导图 | `mindnote` | `lark-cli wiki +node-create --obj-type mindnote` |
| 31 | 电子表格 | `sheet` | `lark-cli wiki +node-create --obj-type sheet` |
| 32 | 幻灯片 | `slides` | `lark-cli wiki +node-create --obj-type slides` |

## 不支持 / 需替代方案（6 种）

| 类型 | 原因 | 替代方案 |
|------|------|----------|
| 议程 (agenda) | API 不支持创建 | `<time>` + `<checkbox>` 组合 |
| UML 图 (diagram) | API 不支持创建 | `<whiteboard type="mermaid">` |
| 折叠块 (toggle) | CLI XML 未暴露 | 用 `<callout>` + h2 分区替代 |
| 任务 (task) | 需已有 GUID | `lark-cli wiki +node-create` 的 task 需单独管理 |
| OKR | 需 user_token + 已有 OKR ID | 通过飞书 OKR 功能手动添加 |
| 内嵌网页 (iframe) | 需 component type + URL 编码 | `<bookmark>` 替代 |
| 日历 | 需独立日历 API | 通过日历 API 单独创建 |

## 外部平台嵌入方案

| 平台 | 最佳方式 | 示例 |
|------|----------|------|
| 高德/百度地图 | `<bookmark>` | `<bookmark name="贵阳" href="https://uri.amap.com/marker?position=..."/>` |
| B站/视频 | `<bookmark>` | `<bookmark name="视频" href="https://www.bilibili.com/video/..."/>` |
| 抖音 | `<bookmark>` | `<bookmark name="抖音" href="https://www.douyin.com/video/..."/>` |
| 小红书 | `<bookmark>` | `<bookmark name="小红书" href="https://www.xiaohongshu.com/..."/>` |
| GitHub | `<bookmark>` | `<bookmark name="仓库" href="https://github.com/..."/>` |
| Figma | `<bookmark>` | `<bookmark name="设计稿" href="https://www.figma.com/..."/>` |

## 总覆盖率

**33/40 = 82.5%** 的 block 类型可通过 CLI v2 直接或间接实现。
