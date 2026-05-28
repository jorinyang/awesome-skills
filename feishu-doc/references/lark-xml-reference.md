# Lark XML 完整格式参考

基于 HTML 子集的 XML 格式，用于 `docs +create --api-version v2 --doc-format xml` 和 `docs +update --api-version v2 --command ... --content`。

## 一、标准 HTML 标签

p, h1-h9, ul, ol, li, table, thead, tbody, tr, th, td, blockquote, pre, code, hr, img, b, em, u, del, a, br, span 语义不变。

## 二、扩展标签速查

### 块级标签

| 标签 | 说明 | 关键属性 |
|------|------|----------|
| `<title>` | 文档标题（每篇唯一） | `align` |
| `<checkbox>` | 待办项 | `done="true"\|"false"` |

### 容器标签

| 标签 | 说明 | 关键属性 |
|------|------|----------|
| `<callout>` | 高亮框 | `emoji`(默认 bulb), `background-color`, `border-color`, `text-color` |
| `<grid>` + `<column>` | 分栏布局 | `width-ratio`（各列之和为 1） |
| `<whiteboard>` | 嵌入画板 | `type`: `blank` \| `mermaid` \| `plantuml` \| `svg` |
| `<pre>` | 代码块（内含 `code`） | `lang`, `caption` |
| `<figure>` | 视图容器 | `view-type` |
| `<bookmark>` | 书签链接 | `name`, `href`（均必传） |

### 行内组件

| 标签 | 说明 | 关键属性 |
|------|------|----------|
| `<cite type="user">` | @人 | `user-id="userID"` |
| `<cite type="doc">` | @文档 | `doc-id="docx_token"` |
| `<latex>` | 行内公式 | `<latex>E = mc^2</latex>` |
| `<img>` | 图片 | `href`(URL), `width`, `height`, `caption`, `name` |
| `<source>` | 文件附件 | `name="文件名.pdf"` |
| `<a type="url-preview">` | 预览卡片 | `href` |
| `<button>` | 操作按钮 | `action=OpenLink\|DuplicatePage\|FollowPage`, `background-color`, `src` |
| `<time>` | 提醒 | `expire-time`, `notify-time`(毫秒时间戳), `should-notify=true\|false` |

### 文本块通用属性

- `align` — `"left"`|`"center"`|`"right"`（适用于 p / h1-h9 / li / checkbox）
- 有序列表项用 `seq="auto"` 自动编号

## 三、资源块

| 标签 | 说明 | 示例 |
|------|------|------|
| `<img>` | 网络图片 | `<img href="https://..."/>` |
| `<whiteboard>` | 图表 | `<whiteboard type="mermaid">graph TD; A-->B;</whiteboard>` |
| `<sheet>` | 电子表格 | `<sheet type="blank"></sheet>` |
| `<task>` | 任务 | `<task task-id="GUID"></task>` |
| `<chat_card>` | 会话卡片 | `<chat_card chat-id="CHAT_ID"></chat_card>` |

## 四、富文本样式嵌套顺序

行内样式标签必须按以下顺序嵌套（外→内），关闭顺序严格反转：

`<a> → <b> → <em> → <del> → <u> → <code> → <span> → 文本内容`

## 五、列表规则

- 连续同类型列表项自动合并为一个 `<ul>` 或 `<ol>`
- 嵌套子列表放在 `<li>` 内部
- 新增列表项必须包在 `<ul>` 或 `<ol>` 内

## 六、表格扩展

- `<colgroup>` / `<col>` 定义列宽：`<col span="2" width="120"/>`
- `<th>` / `<td>` 增加 `background-color` 和 `vertical-align`（top | middle | bottom）
- 合并单元格用 `colspan` / `rowspan`

## 七、颜色系统

### 基础色（7 色）
red, orange, yellow, green, blue, purple, gray

### 适用场景

| 属性 | 支持的命名色 |
|------|-------------|
| 文字颜色 `<span text-color>` | 基础色 |
| 高亮框字色 `<callout text-color>` | 基础色 |
| 高亮框边框 `<callout border-color>` | 基础色 |
| 文字背景 `<span background-color>` | 基础色 + `light-{色}` + `medium-gray` |
| 高亮框填充 `<callout background-color>` | `gray` + `light-{色}` + `medium-{色}` |
| 单元格背景 `<th/td background-color>` | 同文字背景 |
| 按钮背景 `<button background-color>` | 同文字背景 |

### 常用 emoji
💡(默认) ✅ ❌ ⚠️ 📝 ❓ ❗ 👍 ❤️ 📌 🏁 ⭐ 🎯 🚀 📊

## 八、转义规则

> **标签本身禁止转义**，只有标签内部的文本内容才需要转义。

- ❌ `&lt;p&gt;内容&lt;/p&gt;`（把标签也转义了）
- ✅ `<p>A &amp; B 的对比：1 &lt; 2</p>`（标签保持原样，文本中的 `&` 和 `<` 才转义）

转义字符：
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`

## 九、完整示例

```xml
<title>文档标题</title>

<h1>一级标题</h1>
<h2>二级标题</h2>
<h3>三级标题</h3>

<p><b>加粗文本</b>，<em>斜体</em>，<span text-color="green">绿色文字</span></p>

<callout emoji="💡" background-color="light-yellow" border-color="yellow">
  <p>高亮框内容</p>
</callout>

<checkbox done="true">已完成事项</checkbox>
<checkbox done="false">未完成事项</checkbox>

<grid>
  <column width-ratio="0.5">
    <p>左栏</p>
  </column>
  <column width-ratio="0.5">
    <p>右栏</p>
  </column>
</grid>

<table>
  <thead><tr><th>表头</th><th>表头</th></tr></thead>
  <tbody><tr><td>单元格</td><td>单元格</td></tr></tbody>
</table>

<ul><li>无序列表项</li></ul>
<ol><li seq="auto">有序第一步</li><li seq="auto">有序第二步</li></ol>

<blockquote><p>引用内容</p></blockquote>

<hr/>

<pre lang="python" caption="示例"><code>print("hello")</code></pre>

<img href="https://example.com/photo.png" width="800" caption="说明"/>

<a type="url-preview" href="https://example.com">链接标题</a>

<source name="文件名.pdf"/>

<whiteboard type="mermaid">
graph TD
    A[开始] --> B[处理]
    B --> C[结束]
</whiteboard>

<p><cite type="user" user-id="USER_ID"></cite></p>
<p><cite type="doc" doc-id="DOC_TOKEN"></cite></p>
```
