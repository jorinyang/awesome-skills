---
name: feishu-doc
description: 飞书文档创建与管理：将群内产出直接创建为飞书在线文档，归档至知识库，并主动推送变更通知
triggers:
  - 用户要求创建文档
  - 产出内容复杂度超出飞书消息承载范围
  - 用户要求修订已有文档
  - 讨论主题在知识库检索中被发现已存在
  - 用户要求同时产出「内部实施方案+对外宣传版本」（双轨交付）
  - 用户说「客户提了意见」「看看评论」「有修订意见」「帮我看下文档评论」
---

# Feishu Doc — 飞书文档创建与管理（v2）

## 功能概述

使用 `lark-cli docs` v2 API + **Lark XML 格式**创建/编辑飞书文档，支持 50+ 种 block 类型，彻底解决旧 REST API 仅支持 4 种 block 的限制。

## 核心能力

1. **知识库检索**：`docs +search` 全文搜索，判断主题是否已存在
2. **创建文档**：`docs +create --api-version v2 --doc-format xml` 一步创建并写入内容
3. **编辑文档**：`docs +update` 精准局部编辑（str_replace / block_insert_after / append 等）
4. **知识库归档**：`--parent-token` 直接创建到知识库指定分类下
5. **图片插入**：`docs +media-insert` 插入本地图片/文件
6. **图表支持**：`<whiteboard type="mermaid">` 内嵌 Mermaid/PlantUML/SVG 图表
7. **全 block 类型**：表格、列表、代码块、引用、分割线、高亮卡片、待办清单、分栏等
8. **评论驱动修订**：读取文档评论→AI 解析修改意图→精准编辑文档→回复评论告知结果 🔥
9. **文档推送**：新增/修订后主动推送变更摘要和链接

---

## 认证

CLI v2 已配置完成（`lark-cli config init --app-id cli_aa9ead14c2641cc3 --app-secret-stdin`），每次命令自动处理 token，无需手动刷新。

```bash
# 验证配置
lark-cli config show
```

**身份选择：**
- `--as bot`（默认）：应用身份，可创建文档/发消息
- `--as user`：用户身份，需 `lark-cli auth login`（可访问个人数据）

---

## 知识库信息

| 项目 | 值 |
|------|-----|
| space_id | `7643710721485753535` |
| 知识库首页 token | `NBW2wANDViY5BSkbVA1cnETfnEf` |

### 分类父节点（用于 --parent-token）

| 分类 | parent_node_token |
|------|-------------------|
| 企业文化 | `KqoZwqut8ilTSFk3SX4cOpQ9nZf` |
| 团队管理 | `PAVdwkNpNiedvfkPLIec1gK7nAU` |
| 业务规范 | `FB6DwZlXhijL38k0z6Jcy8gznhd` |
| 会议纪要 | `GI1cwlAUviHXIqk291vcjNxvnGb` |
| 方案计划 | `KVPTwrbOKiQMUkkUPlscaEKfnUd` |
| 汇报资料 | `MebBwjMDgiUH4YkNeEmcLhxFnrb` |
| 文案素材 | `J9h6wJgO4ij7NjkXNTCc6mNDnwf` |
| 产品研发 | `HrJXwlne7ioywnkDpAlc6p08ngV` |
| 运营策略 | `JIKCw1IXAi5ZYxkBKW0cYEuanGF` |

---

## Lark XML 格式速查

写入内容使用 XML（HTML 子集），以下是核心标签。

### 块级标签

| 标签 | 说明 | 示例 |
|------|------|------|
| `<title>` | 文档标题 | `<title>我的文档</title>` |
| `<h1>` ~ `<h9>` | 标题 | `<h1>一级标题</h1>` |
| `<p>` | 段落 | `<p>正文内容</p>` |
| `<ul><li>` | 无序列表 | `<ul><li>项目一</li><li>项目二</li></ul>` |
| `<ol><li seq="auto">` | 有序列表 | `<ol><li seq="auto">第一步</li></ol>` |
| `<pre lang="X"><code>` | 代码块（带语法高亮） | `<pre lang="python" caption="示例"><code>print("hi")</code></pre>` |
| `<table>` | 表格 | `<table><thead><tr><th>列A</th></tr></thead><tbody><tr><td>值</td></tr></tbody></table>` |
| `<blockquote>` | 引用块 | `<blockquote><p>引用内容</p></blockquote>` |
| `<hr/>` | 分割线 | `<hr/>` |
| `<callout>` | 高亮卡片 | `<callout emoji="💡" background-color="light-yellow" border-color="yellow"><p>提示</p></callout>` |
| `<checkbox done="true/false">` | 待办事项 | `<checkbox done="false">待完成</checkbox>` |
| `<grid>` + `<column>` | 分栏布局 | `<grid><column width-ratio="0.5"><p>左</p></column><column width-ratio="0.5"><p>右</p></column></grid>` |
| `<img>` | 图片 | `<img href="https://..." width="800" caption="说明"/>` |
| `<source>` | 文件附件 | `<source name="报告.pdf"/>` |
| `<whiteboard>` | 画板/图表 | `<whiteboard type="mermaid">graph TD; A-->B;</whiteboard>` |

### 行内标签

| 标签 | 说明 | 示例 |
|------|------|------|
| `<b>` | 加粗 | `<b>重点</b>` |
| `<em>` | 斜体 | `<em>强调</em>` |
| `<del>` | 删除线 | `<del>废弃</del>` |
| `<u>` | 下划线 | `<u>突出</u>` |
| `<code>` | 行内代码 | `<code>var x = 1</code>` |
| `<a href="...">` | 链接 | `<a href="https://...">文本</a>` |
| `<span text-color="red">` | 文字颜色 | `<span text-color="green">绿色</span>` |
| `<span background-color="light-yellow">` | 背景色 | `<span background-color="light-yellow">高亮</span>` |
| `<cite type="user" user-id="...">` | @人 | `<cite type="user" user-id="ou_xxx"></cite>` |
| `<cite type="doc" doc-id="...">` | @文档 | `<cite type="doc" doc-id="DOX_TOKEN"></cite>` |
| `<br/>` | 换行 | 文本内换行 |

**颜色参考**：red, orange, yellow, green, blue, purple, gray + `light-{色}` / `medium-{色}` 变体。

### 转义规则

- 标签本身**不转义** — `<p>内容</p>` ✅，`&lt;p&gt;内容&lt;/p&gt;` ❌
- 文本内容中：`&` → `&amp;`，`<` → `&lt;`，`>` → `&gt;`
- 文件传参时可绕过转义：`--content @path/to/file.xml`

---

## 核心工作流程

### 流程零：知识库检索（必须优先执行）

```bash
lark-cli docs +search --query "搜索关键词" --as user
```

- 命中 → 向用户确认："知识库中已存在相关文档《{标题}》，是否直接编辑？"
  - 确认编辑 → 流程二（更新已有文档）
  - 新建 → 流程一
- 未命中 → 流程一
- `--as user` 身份可能未配置（需 `lark-cli auth login`），此时回退为手动列出知识库节点匹配

### 流程一：创建新文档

1. **生成内容 XML 文件**（写入 `/tmp/doc_content.xml`）
2. **创建文档**：

```bash
cd /tmp && lark-cli docs +create \
  --api-version v2 \
  --doc-format xml \
  --content @doc_content.xml \
  --parent-token {{分类的 parent_node_token}} \
  --as bot
```

3. 从响应 JSON 提取 `document_id` 和 `url`
4. 如需插入图片，后续调用 `docs +media-insert`

> ⚠️ **`@file` 必须是相对路径**：先 `cd` 到文件所在目录，或用 `--content -` 从 stdin 传入。
>
> ⚠️ **标题创建后无法通过旧 API 修改**，但 CLI v2 支持 `+update --new-title`。

### 流程二：更新已有文档

**推荐模式：精准局部编辑**

```bash
# 追加内容到末尾
lark-cli docs +update --api-version v2 --doc {{doc_id}} --command append \
  --content @追加内容.xml --as bot

# 替换特定文本
lark-cli docs +update --api-version v2 --doc {{doc_id}} --command str_replace \
  --pattern "旧文本" --content "新文本" --as bot

# 替换整个 block
lark-cli docs +update --api-version v2 --doc {{doc_id}} --command block_replace \
  --block-id "目标block_id" --content '<p>新内容</p>' --as bot

# 全文覆盖（谨慎使用，会丢失图片/评论）
lark-cli docs +update --api-version v2 --doc {{doc_id}} --command overwrite \
  --content @新内容.xml --as bot
```

**获取 block ID 用于精准操作：**

```bash
lark-cli docs +fetch --api-version v2 --doc {{doc_id}} --detail with-ids --as bot
```

### 流程三：图片插入

```bash
# 本地文件
cd /path/to/dir && lark-cli docs +media-insert \
  --doc {{doc_id}} \
  --file image.png \
  --caption "图片说明" \
  --align center \
  --as bot

# 网络图片（直接在 XML 中）
<img href="https://example.com/image.png" width="800" caption="说明"/>
```

### 流程四：图表插入（Mermaid / PlantUML）

**方式一：直接嵌入 XML（推荐）**

```xml
<whiteboard type="mermaid">
graph TD
    A[开始] --> B[处理]
    B --> C[结束]
</whiteboard>
```

**方式二：创建空白画板后通过 +whiteboard-update 写入**

先创建空白画板：
```xml
<whiteboard type="blank"></whiteboard>
```

再更新画板内容：
```bash
lark-cli docs +whiteboard-update \
  --whiteboard-token {{board_token}} \
  --input_format mermaid \
  --source 'graph TD; A-->B;' \
  --as bot
```

> 从 `docs +create` 或 `+update` 的返回值 `document.new_blocks` 中获取 `block_token` 作为 `--whiteboard-token`。

### 流程五：推送给用户

每次新增或修订文档后，发送通知：
- 文档链接
- 操作类型（新建/修订）
- 内容摘要（100字内）
- 主要修改点（修订时）

### 流程六：评论驱动修订（@hermes 自动触发）🔥

**核心理念**：用户/客户在飞书文档中添加评论，只要有一条评论包含 `@hermes`，Hermes 自动读取全部评论并处理——无需用户额外通知。

#### 6.1 触发机制

| 触发条件 | 行为 |
|---------|------|
| 评论含 `@hermes` | ✅ **自动**读取全部评论并处理（即使其他评论没有 @hermes）|
| 无 `@hermes` | ❌ 不处理，等待用户主动通知 |

> **关键变更**：当检测到任何评论中有 `@hermes`，Hermes 处理的是**该文档的全部未解决评论**，不是仅限 @hermes 那条。这样客户只需在一条评论 @hermes，所有意见都被处理。

#### 6.2 读取评论（注意嵌套结构）

评论文本不在 `rich_text` 字段，而在 `reply_list.replies[*].content.elements[*].text_run.text`：

```python
for item in api_response['data']['items']:
    cid = item['comment_id']
    # 🔑 文本在嵌套结构中，不在 flat rich_text
    replies = item.get('reply_list', {}).get('replies', [])
    if replies:
        elements = replies[0].get('content', {}).get('elements', [])
        text = ''.join(e.get('text_run', {}).get('text', '') for e in elements)
    else:
        text = ''
    
    has_hermes = '@hermes' in text
    unresolved = not item['is_solved']
```

#### 6.3 细颗粒度意图识别

不再笼统分类，精确到操作级别：

| 意图级别 | 特征词/句式 | Hermes 操作 | 示例 |
|---------|-----------|------------|------|
| **数值替换-价格** | 调整为X元/人、改为X元/人、价格更新 | `str_replace` 定位旧价格→替换为新价格 | "标准套餐调整为3280元/人" |
| **数值替换-预算** | 预算.*调整为X万、改成X万 | `str_replace` 定位预算数字→替换 | "KOL预算调整为15万" |
| **数值替换-数据** | 数据.*更新、预测.*X万、同比增长X% | `str_replace` 定位统计数据→替换 | "预测900万人次，增长15%" |
| **数值替换-数量** | 改成X位、改为X个、数量调整 | `str_replace` 定位数量→替换 | "改成15位亲子+5位户外" |
| **追加-段落** | 加一段、增加、补充、后面加/追加 | `lark-cli +update append` 追加内容 | "在渠道策略后面加一段小程序" |
| **追加-列表项** | 再加一个、补充一点、新增一项 | `append` 追加到已有列表末尾 | "补充：微信视频号同步宣传" |
| **删除-文本** | 删除、去掉、取消、移除、删掉X | `str_replace` X→空字符串 `""` | "删除黔西南全景自驾7日" |
| **删除-段落** | 整段删掉、这章不要、整个部分删除 | 定位 block → 删除整个 block | "第四章整个删掉" |
| **替换-文本** | 改成"X"、改为Y、将A替换为B | `str_replace` A→B | "亲子类博主改成15位" |
| **替换-措辞** | 措辞优化、换个说法、建议改成 | `str_replace` 精准替换措辞 | "建议改用更积极的说法" |
| **结构-移动** | 放到前面、移到X前、调整顺序 | `block_insert_after` 移动 block | "把价格部分放到产品前面" |
| **结构-合并** | 合并、放到一起、并到一章 | 提取两个 block → 合并 → 删除原 block | "把一二章合并" |
| **格式-加粗/高亮** | 加粗、高亮、突出、标红 | `str_replace` 添加 `<b>`/`<callout>` 标签 | "这句话加粗突出" |
| **格式-标题级别** | 改成H2、标题级别不对、这是小标题 | 修改 block 类型或包裹内容 | "这个应该改成三级标题" |
| **格式-列表化** | 改成列表、改成要点、用 bullets | 将文本拆分 → 写入 `<ul><li>` | "这段改成列表" |

#### 6.4 执行修订 + 回复评论

```
1. feishu_drive_list_comments → 获取评论，提取文本（注意嵌套结构）
2. 检测 @hermes 触发器 → 若存在，处理全部未解决评论
3. 逐条解析评论 → 精确匹配意图（用上表）
4. lark-cli docs +update → 精准 str_replace/append
5. 回复评论：feishu_drive_reply_comment → 告知修改结果
```

**回复评论格式（注意 reply API 需要嵌套结构）**：

```python
# 回复评论的正确结构
reply_body = {"reply_list": {"replies": [{
    "content": {"elements": [{"type": "text_run", "text_run": {"text": "回复内容"}}]}
}]}}
# POST /open-apis/drive/v1/files/{doc_token}/comments/{comment_id}/replies
```

**回复模板**：
- ✅ "已修改：KOL预算从20万调整为15万，物料制作增加至15万"
- ⚠️ "已按理解为'删除整段XX内容'执行，如有误请告知"
- 🤔 "您的意思是[理解]，请确认后修改"
- ❌ "此修改需人工处理：[原因]"

#### 6.5 批量处理策略

```python
comments = list_comments(file_token=DOC)
if not any("@hermes" in c.text for c in comments):
    return  # 无 @hermes 触发器，跳过

for c in comments:
    if c.is_solved:
        continue
    
    intent = parse_intent(c.text)  # 用 6.3 细颗粒度匹配
    if intent.confidence == "high":
        execute_revision(DOC, intent)
        reply_comment(c.id, f"✅ 已修改：{intent.summary}")
    elif intent.confidence == "medium":
        execute_revision(DOC, intent)
        reply_comment(c.id, f"⚠️ 已按理解修改：{intent.summary}，请确认")
        notify_user(f"可能需要确认：{c.summary}")
    else:
        reply_comment(c.id, f"🤔 需要更多信息才能修改：{intent.reason}")
        notify_user(f"评论需人工处理：{c.summary}")
```

#### 6.6 关键约束

- **文本提取**：评论在 `reply_list.replies[0].content.elements[*].text_run.text`，不在 `rich_text`
- **@hermes 触发范围**：检测到任意 @hermes → 处理文档**全部**未解决评论
- **不用 overwrite**：会丢失图片/图表/未处理评论
- **str_replace 精确匹配**：pattern 必须与 raw_content 中的文本完全一致
- **评论回复 API**：需要嵌套 `reply_list.replies[*].content.elements` 结构
- **去重**：同一位置的多次 str_replace 可能冲突，按评论顺序执行
- **清理测试**：测试后删除测试文档

---

## Markdown → Lark XML 转换规则

当用户提供 Markdown 格式的内容时，按以下规则转换为 Lark XML：

| Markdown | Lark XML |
|----------|----------|
| `# 标题` | `<h1>标题</h1>` |
| `## 标题` | `<h2>标题</h2>` |
| `### 标题` | `<h3>标题</h3>` |
| 普通段落 | `<p>段落</p>` |
| `**加粗**` | `<b>加粗</b>` |
| `*斜体*` | `<em>斜体</em>` |
| `` `代码` `` | `<code>代码</code>` |
| `- 项目` | `<ul><li>项目</li></ul>` |
| `1. 项目` | `<ol><li seq="auto">项目</li></ol>` |
| `> 引用` | `<blockquote><p>引用</p></blockquote>` |
| `---` | `<hr/>` |
| ` ```lang ` 代码块 | `<pre lang="lang"><code>代码</code></pre>` |
| `| 表头 |` | `<table>`（标准 HTML table 结构） |
| `![alt](url)` | `<img href="url" name="alt"/>` |
| `- [ ] 待办` | `<checkbox done="false">待办</checkbox>` |
| `- [x] 完成` | `<checkbox done="true">完成</checkbox>` |

> ⚠️ **不再需要降级处理**。旧版中表格→文本行、代码块→普通文本、列表→文本等降级策略全部废弃。

---

## 文档创作规范（CRITICAL — 每次生成内容前必读）

### 核心原则

1. **格式一致**：所有生成的内容必须使用 Lark XML 原生标签，与飞书渲染格式完全一致。不得使用 Markdown 语法写在 `<p>` 内（如 `<p>**加粗**</p>` ❌，应写 `<p><b>加粗</b></p>` ✅）。
2. **类型多样**：每篇文档必须使用 ≥4 种不同的 block 类型（标题不计入），禁止纯文本堆砌。
3. **读者优先**：结构清晰、层次分明，关键信息在 3 秒内可定位。

### 强制多样性规则

| 规则 | 要求 |
|------|------|
| **最低 block 种类** | 每篇 ≥4 种（h1-h9 不计入） |
| **每章节结构** | 每个 h2 章节至少包含 1 个非 `<p>` 的 block |
| **表格化数据** | 3 列以上的对比数据**必须**用 `<table>`，禁止用文本行拼接 |
| **三级以上步骤** | **必须**用 `<ol><li seq="auto">` 或 `<whiteboard type="mermaid">` 流程图 |
| **警告/重要提示** | **必须**用 `<callout>` 包裹，禁止用普通 `<p>` 加 emoji |
| **任务/待办** | **必须**用 `<checkbox>`，禁止用 `<ul>` 模拟 |
| **外部链接** | **必须**用 `<bookmark>` 而非 `<a>`，以获得富媒体卡片渲染 |

### 文档骨架模板

每篇文档必须包含以下结构元素：

```xml
<title>精准概括文档主题</title>

<!-- 1. 开篇摘要 — callout 高亮 -->
<callout emoji="📌" background-color="light-blue" border-color="blue">
  <p><b>一句话概述本文档的核心内容和目标读者。</b></p>
</callout>

<!-- 2. 正文章节 — 每章必须混合多种 block -->
<h1>章节标题</h1>
<h2>子标题</h2>
<!-- 段落 + 列表 + 表格/图表/高亮 交替出现 -->
<p>段落内容</p>
<ul><li>要点</li></ul>
<table>...</table>

<!-- 3. 关键结论 — callout 强调 -->
<callout emoji="🎯" background-color="light-green" border-color="green">
  <p><b>核心结论</b></p>
  <ul><li>结论一</li><li>结论二</li></ul>
</callout>

<!-- 4. 待办清单 — checkbox -->
<h2>后续行动</h2>
<checkbox done="false">待办事项一</checkbox>
<checkbox done="false">待办事项二</checkbox>
</ol>
```

### 常见内容类型 → 最佳 block 映射

| 你要表达什么 | ❌ 错误做法 | ✅ 正确做法 |
|-------------|------------|-----------|
| 对比几个方案 | `<p>A: xxx B: yyy</p>` | `<table>` 含表头 |
| 操作步骤 | `<p>1. xxx 2. yyy</p>` | `<ol><li seq="auto">` |
| 重要提醒 | `<p>⚠️ 注意...</p>` | `<callout emoji="⚠️" background-color="light-red">` |
| 数据指标 | `<p>营收: 100万</p>` | `<grid>` + `<callout>` 分栏卡片 |
| 多级关系 | 嵌套 `<p>` 段落 | `<ul><li>含嵌套 <ul>` |
| 进度状态 | `<p>✅ done ❌ todo</p>` | `<checkbox done="true/false">` |
| 外部参考 | `<a href="...">链接</a>` | `<bookmark name="..." href="..."/>` |
| 代码/配置 | `<p>npm install xxx</p>` | `<pre lang="bash"><code>` |
| 架构/流程 | 纯文字描述 | `<whiteboard type="mermaid">` 图表 |
| 地图/视频 | `<a href="...">查看</a>` | `<bookmark>` 富媒体卡片 |

### 易读性检查清单

生成 XML 后自查：
- [ ] 能在 5 秒内扫到所有 h2 标题？
- [ ] 每段 `<p>` 不超过 4 行（超长则拆分或用列表）？
- [ ] 关键数字/结论是否在 `<callout>` 或 `<b>` 中突出？
- [ ] 同类信息是否已聚合为 `<table>` / `<ul>` / `<ol>`？
- [ ] 外部链接是否用 `<bookmark>` 而非 `<a>`？
- [ ] 是否使用了 ≥4 种 block 类型？

---

## API 能力总结

### ✅ 可通过 CLI v2 完成

| 能力 | 命令/方式 |
|------|----------|
| 创建文档（全 block 类型） | `docs +create --api-version v2 --doc-format xml` |
| 更新文档（精准编辑） | `docs +update --command str_replace/block_insert_after/...` |
| 追加内容 | `docs +update --command append` |
| 全文覆盖 | `docs +update --command overwrite` |
| 更新标题 | `docs +update --new-title` |
| 插入图片 | `docs +media-insert` |
| 插入本地文件 | `docs +media-insert --type file` |
| 创建 Mermaid/PlantUML 图表 | `<whiteboard type="mermaid">` |
| 搜索知识库 | `docs +search --query` |
| 读取文档内容 | `docs +fetch --api-version v2` |
| 获取 block ID | `docs +fetch --detail with-ids` |
| 读取/回复评论 | `lark-cli api GET/POST .../comments`（详见 `references/comments-api.md`）|
| 创建 Bitable 节点 | `--parent-token PARENT` + 后续 Bitable API |
| 列出文档评论 | `feishu_drive_list_comments(file_token=DOC, file_type="docx")` |
| 查看评论回复 | `feishu_drive_list_comment_replies(file_token=DOC, comment_id=ID)` |
| 回复评论 | `feishu_drive_reply_comment(file_token=DOC, comment_id=ID, content="回复内容")` |
| 添加评论 | `feishu_drive_add_comment(file_token=DOC, content="评论内容")` |

### ❌ 仍不可通过 API 完成

| 能力 | 说明 |
|------|------|
| 日历 | 需单独使用日历 API |
| 折叠块 (Toggle) | CLI v2 XML 暂未暴露 |
| 议程块 (Agenda) | API 不支持创建，用 `<time>` + `<checkbox>` 替代 |

### ✅ 通过 wiki +node-create 独立创建（知识库节点）

| obj_type | 说明 | 命令 |
|----------|------|------|
| `docx` | 飞书文档 | `lark-cli wiki +node-create --obj-type docx` |
| `bitable` | 多维表格 | `lark-cli wiki +node-create --obj-type bitable` |
| `mindnote` | 思维导图 | `lark-cli wiki +node-create --obj-type mindnote` |
| `sheet` | 电子表格 | `lark-cli wiki +node-create --obj-type sheet` |
| `slides` | 幻灯片 | `lark-cli wiki +node-create --obj-type slides` |

> 以上 5 种类型均可作为知识库独立节点创建。其中 `sheet` 还可通过 XML `<sheet type="blank">` 嵌入 docx。

### ✅ 外部内容嵌入

| 内容类型 | 推荐方式 | 示例 |
|----------|----------|------|
| 地图链接 | `<bookmark>` 书签 | `<bookmark name="贵阳" href="https://uri.amap.com/..."/>` |
| 视频链接 | `<bookmark>` 书签 | `<bookmark name="视频" href="https://www.bilibili.com/video/..."/>` |
| 抖音/小红书 | `<bookmark>` 书签 | `<bookmark name="抖音" href="https://www.douyin.com/..."/>` |
| GitHub/Figma | `<bookmark>` 书签 | `<bookmark name="仓库" href="https://github.com/..."/>` |

> ⚠️ `<a type="url-preview">` 在 XML 中会被降级为普通链接。使用 `<bookmark>` 实现富媒体卡片嵌入。

---

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| `not configured` | CLI 未初始化 | 运行 `echo "SECRET" \| lark-cli config init --app-id cli_aa9ead14c2641cc3 --app-secret-stdin --force-init` |
| `--content: invalid file path` | `@file` 用了绝对路径 | `cd` 到文件目录，传相对路径 |
| `permission denied` | Wiki 权限不足 | 确认应用已开通 `wiki:space:write_only` 并**重新发布** |
| `node: not found` | Node.js 不在 PATH | `export PATH="/home/aorus/.local/bin:$PATH"` |
| `resource created but auto-grant skipped` | 用户未登录 CLI | 文档创建成功但无法自动授权；运行 `lark-cli auth login` 或手动授权 |
| `1069302` comment reply failed | 评论类型不匹配 | 普通评论用 `feishu_drive_reply_comment`，整篇评论用 `feishu_drive_add_comment` |
| `1069307` comment not exist | 文档 ID 错误或权限不足 | 确认 doc_token 正确 + 应用有 `drive:comment:readonly` 权限 |
| 评论内容含特殊字符 | JSON 转义问题 | 评论内容必为纯文本，XML/Markdown 语法在评论中不渲染 |
| 回复评论 HTTP 400 | reply 结构不对 | 需要用嵌套结构 `reply_list.replies[*].content.elements[*].text_run.text` |
| `rich_text` 字段为空 | 文本在嵌套结构中 | 从 `reply_list.replies[0].content.elements` 提取文本，不用 flat `rich_text` |
| 评论列表为空但实际有评论 | `is_whole` 过滤 | 评论有两种类型（local/whole），不传 `is_whole` 参数获取全部 |

---

## 实测陷阱（2026-05-27 全量验证）

### `<source>` 文件附件
- **不能用 `name` 属性凭空创建**。`<source name="报告.pdf"/>` 作为独立块会报 `too big file size` 错误，因为缺少实际文件 token
- **正确做法**：用 `docs +media-insert --type file` 上传本地文件；或仅在 XML 中 `+update` 已有 source 块时保留其 `token`

### `<img>` 网络图片
- `<img href="https://..." width="800" caption="说明"/>` ✅ 可用
- `<img>` 不传 `href` 无法创建（需要图片 token）。本地图片用 `+media-insert`

### `<cite type="citation">` 引文
- 作为独立块时可能不渲染。建议放在 `<p>` 内行内使用

### 颜色标签回读
- `docs +fetch` 回读时 `<span text-color="...">` 和 `<callout background-color="...">` 的颜色属性可能被剥离。这是正常的 — 颜色已写入文档，仅在回读 XML 中丢失

### 嵌入资源自动创建
- `<whiteboard type="mermaid">` → 自动创建 whiteboard block（`new_blocks` 中返回 `block_token`）
- `<sheet type="blank">` → 自动创建嵌入式电子表格（`new_blocks` 中返回 `token` + `sheet-id`）
- 响应中的 `block_token` / `token` 可用于后续 `+whiteboard-update` 或 Sheets API

### `@file` 相对路径
- `--content @/tmp/file.xml` ❌ 报错 `invalid file path`
- 必须先 `cd /tmp && lark-cli ... --content @file.xml` ✅
- 或用 stdin：`cat /tmp/file.xml | lark-cli ... --content -`

### `--as user` 依赖 auth login
- `docs +search --as user` 需要先 `lark-cli auth login`（OAuth 设备流）
- 未登录时回退到 Bot 身份或手动 `lark-cli wiki +node-list`

### Shell heredoc 写入 XML 会截断内容 (2026-05-28)
- `cat > /tmp/file.xml << 'XMLEOF'` 写入 XML 内容时，XML 中的 `<hr/>` 等自闭合标签会触发 heredoc 截断，导致文件内容不完整
- **正确做法**：使用 Python `write_file` 或 `open().write()` 写入 XML 文件
- 示例：`with open("/tmp/file.xml", "w") as f: f.write(xml_content)`
- 此问题在 shell 中静默失败，lark-cli 不会报错但文档内容为空或截断

### `docs +fetch` 输出解析
- 输出包含状态行（如 "Running docs fetch..."）后才跟 JSON
- Python 解析时找第一个以 `{` 开头的行获取 JSON 体：
```python
lines = result["output"].split("\n")
json_start = next(i for i, l in enumerate(lines) if l.strip().startswith("{"))
data = json.loads("\n".join(lines[json_start:]))
```

### feishu-wiki 联动
- 知识库目录扫描、变动检测、分类建议 → 加载 `feishu-wiki` 技能
- 首页目录写入和变更日志记录在 feishu-wiki 中管理

---

## 常用命令速查

| 操作 | 命令 |
|------|------|
| 创建文档（应用云空间） | `lark-cli docs +create --api-version v2 --doc-format xml --content @file.xml --as bot` |
| 创建文档（知识库） | `lark-cli docs +create --api-version v2 --doc-format xml --content @file.xml --parent-token TOKEN --as bot` |
| 读取文档 | `lark-cli docs +fetch --api-version v2 --doc DOC --as bot` |
| 读取文档（含 block ID） | `lark-cli docs +fetch --api-version v2 --doc DOC --detail with-ids --as bot` |
| 追加内容 | `lark-cli docs +update --api-version v2 --doc DOC --command append --content @file.xml --as bot` |
| 文本替换 | `lark-cli docs +update --api-version v2 --doc DOC --command str_replace --pattern "旧" --content "新" --as bot` |
| 全文覆盖 | `lark-cli docs +update --api-version v2 --doc DOC --command overwrite --content @file.xml --as bot` |
| 插入图片 | `lark-cli docs +media-insert --doc DOC --file img.png --caption "说明" --as bot` |
| 搜索知识库 | `lark-cli docs +search --query "关键词" --as user` |
| 列出知识库节点 | `lark-cli wiki +node-list --space-id 7643710721485753535` |
| 删除知识库节点 | `lark-cli wiki +node-delete --node-token TOKEN --obj-type wiki --yes` |
| 通用 API 调用 | `lark-cli api GET /open-apis/wiki/v2/spaces/7643710721485753535/nodes` |
| 列出评论 | `feishu_drive_list_comments(file_token=DOC)` |
| 回复评论 | `feishu_drive_reply_comment(file_token=DOC, comment_id=ID, content="...")` |
