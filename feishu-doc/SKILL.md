---
name: feishu-doc
description: 飞书文档创建与管理：将群内产出直接创建为飞书在线文档，归档至知识库，并主动推送变更通知
triggers:
  - 用户要求创建文档
  - 产出内容复杂度超出飞书消息承载范围
  - 用户要求修订已有文档
  - 用户要求删除文档
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
9. **文档推送**：用户文档先发审阅再归档（两步流程）；自动化采集产出可直接推送变更摘要
10. **PRD 需求对齐分析**：原始 PRD + 会议转写/纪要 → 结构化差异对照文档（已对齐/差异/新增）— 详见 `references/prd-diff-methodology.md`
11. **非 docx 文件访问**：Wiki 节点包裹的 PDF/MD/TXT 文件通过 Drive API 下载读取 — 详见 `references/wiki-file-access.md`

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

> 知识库已于 2026-06-01 重组为 4 一级分类 + 21 子类。一级分类用于 `--parent-token`，子分类 node_token 用于精确定位。

| 一级分类 | parent_node_token | 子分类 |
|----------|-------------------|--------|
| 运营管理 | `W57jwRHJYimFRskVK2VcCQjfnXf` | 企业文化、团队管理、产品研发、运营策略、业务规范、任务复盘 |
| 内容素材 | `XMVrw88PsijL6Ek4S2sc1B5enuh` | 会议纪要、方案计划、汇报资料、文案素材、落地页模板 |
| 咨询洞察 | `UF7Cw5w2WiHGfjkKVvBcxj8Hnib` | 行业资讯、竞品动态 |
| AI Native 工作流 | `J4EewYIT2ieFuwkRWbxcgWbFnhe` | 8 个文档节点 |

**子分类 node_token（用于精确创建）：**

| 子分类 | node_token | 所属一级 |
|--------|-----------|---------|
| 企业文化 | `KqoZwqut8ilTSFk3SX4cOpQ9nZf` | 运营管理 |
| 团队管理 | `PAVdwkNpNiedvfkPLIec1gK7nAU` | 运营管理 |
| 产品研发 | `HrJXwlne7ioywnkDpAlc6p08ngV` | 运营管理 |
| 运营策略 | `JIKCw1IXAi5ZYxkBKW0cYEuanGF` | 运营管理 |
| 业务规范 | `FB6DwZlXhijL38k0z6Jcy8gznhd` | 运营管理 |
| 任务复盘 | `NHaQwmHNliUnSekHDOmcPPGfn8f` | 运营管理 |
| 会议纪要 | `GI1cwlAUviHXIqk291vcjNxvnGb` | 内容素材 |
| 方案计划 | `KVPTwrbOKiQMUkkUPlscaEKfnUd` | 内容素材 |
| 汇报资料 | `MebBwjMDgiUH4YkNeEmcLhxFnrb` | 内容素材 |
| 文案素材 | `J9h6wJgO4ij7NjkXNTCc6mNDnwf` | 内容素材 |
| 落地页模板 | `DqdVwu8U5i8UwWkkMMXcAl0HnFf` | 内容素材 |
| 行业资讯 | `V0Lhwl7KYiWYDDk1vCncv2GhnYf` | 咨询洞察 |
| 竞品动态 | `EAMYw1CPoipVWtkObbtcR2oDnNc` | 咨询洞察 |

### 特殊文档 token

| 文档 | obj_token |
|------|-----------|
| 知识库首页 | `Y4LYd1X8Yo1Du9x9WtNcYD51nte` |
| 最近更新（变更日志） | `LJ7RdGzVVoUX6rxmzwpcH3L0npg` |

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

## Markdown 模式（v2 轻量替代）

当文档以文本为主、不需要 `callout`/`grid`/`checkbox`/`whiteboard` 等高级 block 时，可以直接用 Markdown 写入，跳过 XML 转换。**支持创建和更新两种场景：**

**创建文档（含知识库归档）：**

```bash
# ⚠️ --title is DEPRECATED (lark-cli v1.0.53+). Title goes in first line of markdown content.
# Markdown content must start with: <title>文档标题</title>
# @file must be relative path from CWD — cd to file dir first
cd /tmp && lark-cli docs +create --api-version v2 --doc-format markdown \
  --content @file.md \
  --parent-token KVPTwrbOKiQMUkkUPlscaEKfnUd \
  --as bot
```

**更新已有文档：**

```bash
cd /tmp && lark-cli docs +update --api-version v2 --doc DOC_ID \
  --command overwrite --doc-format markdown \
  --content @file.md --as bot
```

lark-cli 自动完成 Markdown → Lark XML 转换。适用场景：工作流阶段文档（Clarify/Brief/Architect）、纯文本方案、会议纪要。

> ⚠️ Markdown 模式的 block 类型有限（h1-h6、p、ul/ol、table、hr、code、img），需要高级 block 时仍需 XML。
>
> ⚠️ **v1 `docs +create --markdown` 不支持 `--parent-token`**，文档只能创建在云空间。要归档到知识库必须用 v2 + `--parent-token`。
>
> ⚠️ **`--title` 被 markdown `# Title` 覆盖 (2026-06-02):** 当 markdown 内容以 `# 标题` 开头时，lark-cli 自动将文档标题设为该 heading 文本，**忽略 `--title` 参数**。后果：自动化采集场景中 `YYYY-MM-DD_source_topic` 格式标题被原始文章标题取代，丢失日期/来源前缀。**对策**：若需精确控制标题（如 travel-intel 自动化命名），使用 XML 格式或在 markdown 中省略 `#` 开头行，改用 `--title` 传标题。

### ⛔ 两步法陷阱（2026-06-01 定位根因 + 验证方法）

**不要先用 Wiki API 创建节点，再用 `docs +update` 写入内容。** 这是静默失败模式：

```bash
# ❌ 两步法 — 返回 ok:true 但文档内容可能为空
Step 1: lark-cli api POST /open-apis/wiki/v2/spaces/{id}/nodes → 创建节点
Step 2: lark-cli docs +update --api-version v2 --doc OBJ_TOKEN \
          --command overwrite --doc-format markdown --content @file.md --as bot
# → 返回 {"ok": true, "revision_id": N} 但实际内容写入不稳定
```

**根因**：Wiki API 创建的 docx 节点与 `docs +update` 的内容写入路径存在不兼容。此问题在 lark-cli v1.0.40–v1.0.44 上均存在。

**正确做法**：必须用一步法 — `docs +create --api-version v2 --doc-format markdown` 同时创建文档和写入内容：

```bash
# ✅ 一步法
cd /tmp && lark-cli docs +create --api-version v2 --doc-format markdown \
  --title "文档标题" --content @file.md \
  --parent-token PARENT_TOKEN --as bot
```

> 已验证：一步法创建的文档内容可正常回读（blocks > 0, text 完整）。

### ⚠️ `docs +fetch` 无法可靠验证文档内容（2026-06-01, updated 2026-06-06）

`lark-cli docs +fetch --api-version v2` **在 Wiki 节点和云空间文档上均不可靠**——即使内容已成功写入（REST API 确认 blocks 存在），`fetch` 仍显示 `Outline items: 0, Blocks: 0`。2026-06-06 确认云空间文档 (`docs +create` 不带 `--parent-token`) 同样受影响，回退到 `Outline items: 0`。

| 验证方式 | 可靠性 |
|----------|:--:|
| `lark-cli docs +fetch --api-version v2` | ❌ 不可靠（Wiki + 云空间 docs 均可能显示 blocks=0 误报） |
| `GET /docx/v1/documents/{id}/blocks/{id}/children` | ✅ 可靠（返回真实 blocks 数量） |

**验证命令**：
```bash
# ✅ 可靠验证（Wiki + 云空间均适用）
lark-cli api GET "/open-apis/docx/v1/documents/{obj_token}/blocks/{obj_token}/children?page_size=500" --as bot 2>&1 | head -50
# 确认返回 items 数组非空即可，不依赖 fetch 的 blocks 计数
```

---

## ⚠️ 读取文档：工具优先级

当需要读取飞书文档内容时，按优先级尝试：

| 优先级 | 工具 | 可靠性 |
|:--:|------|:--:|
| 1 | `lark-cli docs +fetch --api-version v2 --doc <token>` | ⚠️ 可能显示 blocks=0（见下文 pitfall），用 REST API 二次验证 |
| 2 | `GET /docx/v1/documents/{id}/blocks/{id}/children` | ✅ 可靠验证（返回真实 blocks） |
| 3 | `feishu_doc_read(doc_token=...)` | ⚠️ 仅飞书评论上下文中可用 |
| 4 | `curl` / 浏览器 | ❌ 需要登录，返回登录页 |

**关键 pitfall 1**：`feishu_doc_read` 在非飞书评论上下文中（如群聊、私聊）报 `"Feishu client not available (not in a Feishu comment context)"`。**永远不要依赖它**。
**关键 pitfall 2**：`docs +fetch` 对 Wiki 和云空间文档均可能返回 `blocks=0` 误报（见实测陷阱）。读取后如 blocks=0，**不要断言文档为空**——立即用 REST API `blocks/children` 二次验证。

```bash
# 读取（可能不可靠）
lark-cli docs +fetch --api-version v2 --doc <doc_token> --as bot

# 验证（可靠 — fetch 返回 blocks=0 时必做）
lark-cli api GET "/open-apis/docx/v1/documents/{doc_token}/blocks/{doc_token}/children?page_size=500" --as bot
```

> ⚠️ 用户不希望你让他们"补全内容"或"重新说一遍"已经在文档里的东西。先读文档，再行动。

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

> ⚠️ **`docs +search` 仅支持 `--as user`**（`--as bot` 报错 `not supported`）。在 cron/自动化环境中不可用。替代方案：`lark-cli wiki +node-list --parent-node-token TOKEN --page-all --as bot` 列出节点后本地过滤匹配。

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
# 本地文件（必须 cd 到文件所在目录，传相对路径）
cd /path/to/dir && lark-cli docs +media-insert \
  --doc {{doc_id}} \
  --file image.png \
  --caption "图片说明" \
  --align center \
  --as bot

# 插入到指定位置（在匹配文本之前插入）
cd /path/to/dir && lark-cli docs +media-insert \
  --doc {{doc_id}} \
  --file image.png \
  --type image \
  --width 1920 \
  --align center \
  --selection-with-ellipsis "目标段落中的唯一文本" \
  --before \
  --as bot

# 网络图片（直接在 XML 中）
<img href="https://example.com/image.png" width="800" caption="说明"/>
```

#### SVG 转 PNG 嵌入飞书文档

飞书 markdown 和 Lark XML 均不支持内嵌 `<svg>` 标签。如需在飞书文档中嵌入 SVG 图，必须先转为 PNG：

```bash
# 步骤 1：在 venv 中安装 cairosvg（PEP 668 环境必须用 venv）
python3 -m venv /tmp/svg2png
/tmp/svg2png/bin/pip install cairosvg

# 步骤 2：转换 SVG → PNG（1920×1080 适配飞书全宽）
/tmp/svg2png/bin/python3 -c "
import cairosvg
cairosvg.svg2png(url='file.svg', write_to='output.png', output_width=1920, output_height=1080)
"

# 步骤 3：用 +media-insert 插入 PNG 到文档
cd /tmp && lark-cli docs +media-insert \
  --doc DOC_ID \
  --file output.png \
  --type image \
  --width 1920 \
  --align center \
  --as bot
```

> **注意**：`+media-insert` 的 `--file` **必须是相对路径**（在当前目录下），不能用绝对路径如 `/tmp/file.png`。务必先 `cd` 到文件所在目录。

#### SVG 转 PNG 中文字体坑

cairosvg 渲染 SVG 时，如果 SVG 中引用的字体（如 `PingFang SC`）在服务器上不存在，中文会变成方框（□□□）。

**修复步骤**：

```bash
# 1. 检查系统可用的中文字体
fc-list :lang=zh | head -5

# 2. 修改 SVG 中的 font-family 为可用字体
sed -i 's/PingFang SC, HarmonyOS Sans SC, sans-serif/Noto Sans SC, SimSun, sans-serif/g' file.svg

# 3. 移除 emoji 字符（也可能渲染为方框）
sed -i 's/🏗️ //g' file.svg

# 4. 重新转换
/tmp/svg2png/bin/python3 -c "
import cairosvg
cairosvg.svg2png(url='file.svg', write_to='output.png', output_width=1920, output_height=1080)
"
```

> **验证**：转换后 PNG 文件大小显著增加（从 ~47KB 跳到 ~230KB）意味着字体正确渲染。方框渲染时文件很小因为只有空框路径。也可用 `understand_image` 工具目视检查。

#### 替换已存在的图片块

`lark-cli docs +media-upload` 只上传文件获取 token，**不会更新已有的图片块**。要替换文档中已有图片：

```bash
# 步骤 1：上传新图片获取 file_token
cd /tmp && lark-cli docs +media-upload \
  --doc-id DOC_ID \
  --parent-node BLOCK_ID \
  --parent-type docx_image \
  --file new_image.png \
  --as bot
# 返回 {"file_token": "NEW_TOKEN_xxx"}

# 步骤 2：用 PATCH API 替换图片块中的 token
lark-cli api PATCH "/open-apis/docx/v1/documents/DOC_ID/blocks/BLOCK_ID" \
  --data '{"replace_image":{"token":"NEW_TOKEN_xxx"}}' \
  --as bot
```

> `BLOCK_ID` 可通过 `lark-cli docs +fetch --api-version v2 --doc DOC_ID --detail with-ids --as bot` 获取，或从 `+media-insert` 的返回值中提取。替换后 `document_revision_id` 会递增。

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

### 流程五：推送给用户（★ 先发再审，不要急着归档）

**用户文档（非自动化产物）的两步流程：**

1. **创建文档** — 正常 `docs +create --parent-token` 创建到知识库
2. **发链接给用户审阅** — 用 `send_message` 把文档链接发给用户，**不要**在此时宣称"已归档"或"已完成"。文案示例：「模版已生成，你看看结构有没有要调整的：[链接]」
3. **等用户确认** — 用户审阅后可能要求修改（改结构、增减字段、换分类等）。修改完再等待确认
4. **用户认可后才视为定稿** — 此时可以正常推送变更摘要

> ⚠️ **禁止行为**：不要在用户审阅前就推送「文档已创建到知识库 XX 分类」——用户反馈"不要着急入库，你先发给我"。先发链接，等审阅通过再说归档的事。

**自动化情报采集（cron 产出）的推送流程：**

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

### 文档命名规范 ★

**两类场景，两套规则：**

| 场景 | 触发方 | 命名规则 | 示例 |
|------|:--:|------|------|
| **用户对话产出** | 用户直接要求创建 | **纯主题命名**，无日期/来源前缀 | `贵州之客户外安全操作规范` |
| **自动化情报采集** | cron 定时任务 | `YYYY-MM-DD_[source]_简短主题` | `2026-06-01_baidu_贵州探洞新发现` |

**原则**：用户对话中产出的文档是给人看的——干净、直接、一眼知道内容。自动化采集的文档是给系统追溯的——需要时间戳和来源标记方便排序和审计。不可混淆：不要把机器格式强加给用户文档，也不要把无日期标题用于审计流。

### 自动化标题生成规则

当文档属于自动化情报采集（如 travel-intel L1a/L1b/L2/L3），使用以下规则生成标题：

1. 前缀 `日期_来源_`（约 18-22 字符），主题片段 ≤ 40 字符，总长 ≤ 60 字符
2. 去除控制字符/换行/emoji，保留中英文/数字/基本标点
3. 在自然断点截断（句号/逗号/空格），不断在词中
4. 兜底：标题为空/过短时使用搜索关键词替代
5. 过长/含特殊字符的标题会被飞书 API 静默拒绝→回退默认名"无标题"

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

### 集成文档模式（可视化仪表盘 + 详细内容）

当文档需要同时服务"决策者快速扫读"和"执行者深度参考"时，使用双区结构：上半部分 6 模块可视化仪表盘（callout + table），下半部分完整细节。模板和约束见 `references/integrated-doc-pattern.md`。

---

### 钉钉文档 CP 提取

当 `browser_navigate` 无法渲染钉钉在线文档（SPA页面）时，可通过底层 CP 协议 JSON 直接提取文本内容。
详见 `references/dingtalk-cp-extraction.md`。

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
│ 读取文档内容 | `docs +fetch --api-version v2` |
│ 获取 block ID | `docs +fetch --detail with-ids` |

### ⛔ 用户说"有现成文档"时，先搜本地再搜Wiki

当用户提到已有文档/方案/报价时，**不要**直接创建新文档。按以下顺序搜寻：

1. **本地文件** — 用户指定路径（如 `/tmp/xxx/`、`~/workspace/`）或搜索 `/mnt/c/Users/*/Desktop|Documents|Downloads/`
2. **Feishu Wiki 节点** — `lark-cli wiki +node-list` 搜索知识库
3. **Feishu 云空间** — 用户可能分享过文档链接（`feishu.cn/docx/` token）

用户反馈：「本地电脑里有的文档，不要从零开始写」——先从本地 docx/xlsx 读取原始数据，再在此基础上修订。
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
| 读取 slides 内容 | `docs +fetch` 仅支持 docx；图片型幻灯片需导出 PPTX → 图片提取 → 视觉识别，详见 `references/reading-picture-slides.md` |

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
| `node: not found` | Node.js 不在 PATH | `export PATH="C:/Users/Aorus/.local/bin:$PATH"` |
| `3380002 Parent node not found` | 子分类 node_token 已失效 | 回退到一级分类 token（见上文陷阱）。该 token 可能因知识库重组而失效 |
| `1069302` comment reply failed | 评论类型不匹配 | 普通评论用 `feishu_drive_reply_comment`，整篇评论用 `feishu_drive_add_comment` |
| `1069307` comment not exist | 文档 ID 错误或权限不足 | 确认 doc_token 正确 + 应用有 `drive:comment:readonly` 权限 |
| 评论内容含特殊字符 | JSON 转义问题 | 评论内容必为纯文本，XML/Markdown 语法在评论中不渲染 |
| 回复评论 HTTP 400 | reply 结构不对 | 需要用嵌套结构 `reply_list.replies[*].content.elements[*].text_run.text` |
| `rich_text` 字段为空 | 文本在嵌套结构中 | 从 `reply_list.replies[0].content.elements` 提取文本，不用 flat `rich_text` |
| 评论列表为空但实际有评论 | `is_whole` 过滤 | 评论有两种类型（local/whole），不传 `is_whole` 参数获取全部 |

---

## 实测陷阱（2026-05-27 全量验证）

### XML 多表格渲染为 callout（2026-06-10 实测）

- **触发条件**：用 `--doc-format xml` 创建含 ≥3 个 `<table>` 块的文档
- **后果**：部分表格被错误渲染为 `callout`（type 31），而非 `table`（type 22）。5 个表格中 3 个变成 callout，仅 2 个正确。文档视觉结构被破坏
- **根因**：lark-cli v1.0.40 XML tokenizer 在处理连续表格块时存在 bug，callout 和 table 混淆
- **正确做法**：表格密集的文档**必须用 `--doc-format markdown`** 创建，Markdown 模式可正确渲染所有表格
- **规则**：文档含 ≥3 个表格 → 用 Markdown；≤2 个表格且需要 callout/whiteboard/grid 等高级 block → 用 XML

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

### `str_replace` 插入 XML block（callout 等）会被扁平化为纯文本 (2026-06-03)

- **触发条件**：通过 stdin 管道用 `str_replace` 插入 `<callout>`、`<ol>`、`<whiteboard>` 等 XML block，lark-cli 的 `str_replace` 命令将 `--content` **作为纯文本而非 XML 解析**
- **后果**：XML 标签被剥离/扁平化——`<callout emoji="✅"><p>内容</p></callout>` 变成 `<h3><b>内容</b></h3>`（被包裹到当前所在 block 的标签中），callout 的视觉结构完全丢失
- **根因**：`str_replace` 是文本级替换，不对 content 做 XML tokenization。即使通过 stdin 传入完整 XML，它也只做字符串替换，不创建新的 XML block 结构
- **正确做法**：如需在文档中插入新 XML block（callout、列表、图表等），使用以下优先级：
  1. **首选** `overwrite`：fetch 全文 → Python 修复所有问题 → overwrite 回写（参见下方「多变更级联修复」）
  2. **次选** `append`：如果只是追加到文档末尾，`append` 正确处理 XML
  3. **不推荐** `str_replace`：仅适用于纯文本替换（单行/单段），不适用于插入 XML block
- **检测**：`fetch` 后检查目标 block 的标签结构是否完整（是否出现 `<callout>` 而非 `<h3>`）；关键标记计数是否为 1（确保无重复残留）
- 完整案例和修复脚本见 `references/overwrite-rescue-pattern.md`

### 多变更级联修复工作流 (2026-06-03)

当需要对文档做 ≥3 处分散修改，或前序 `str_replace` 已造成内容损坏时：

```
1. fetch 全文 → Python 提取 JSON 中的 document.content
2. Python 中一次性完成所有修复：
   - str.replace() 做文本级替换
   - 字符串拼接插入新 XML block
   - 正则清理重复/残留内容
3. 检查 <title> 标签——如有则移除（避免 overwrite 产生幽灵节点）
4. 写入 /tmp/fixed.xml → overwrite 回写
5. fetch 验证：检查关键标记存在且唯一
```

**为什么不用多次 str_replace 逐个修**：
- 每次 str_replace 修改 revision，前后文位置漂移
- 单次失败会留下半修复状态，后续修复更难定位
- XML block 插入会被扁平化（见上一陷阱）
- 一个 str_replace 的残留内容可能干扰下一个 str_replace 的 pattern 匹配

**overwrite 安全检查**：
- overwrite 前移除 `<title>` 标签（防止幽灵节点）
- 确认文档无内部图片（`<img src="...">`），否则会被截断
- 检查 `result: "success"` + 无 `warnings`
- 立即 fetch 验证关键内容完整性

### `str_replace` 对大段文本静默失败 (2026-05-29, updated 2026-06-01)

- **触发条件**：`--pattern` 或 `--content` 字符串过长（实测 ≥3700 chars 的 pattern 会失败），lark-cli 可能因命令行参数长度限制而静默失败或行为异常
- **后果**：`str_replace` 返回 success 但文档内容未变化，或仅部分替换
- **检测方法**：`fetch` 对比替换前后内容；若未生效，改用 `overwrite`（需处理 img 标签风险）
- **适用范围**：`str_replace` 适合小范围文本替换（单行/单段/单个 block），不适合整章节替换。章节级别替换参见下方 overwrite 安全策略

#### stdin 管道绕过 @file XML 校验失败 (2026-06-01)

- **触发条件**：`str_replace --content @file.xml` 且文件包含大量 XML 标签（如整个章节的逐帧脚本表格）。lark-cli 将 `--content @file` 的内容当作 Lark XML 解析校验，报 `degrade_code=3001`（XML tokenization error），`result: "failed"`，revision 不变。
- **根因**：`str_replace --content` 在 `@file` 模式下仍然走 XML tokenizer，大量嵌套标签可能触发校验失败
- **正确做法**：通过 stdin 管道传入，绕过文件级别的 XML 校验：

```bash
cat /tmp/content.txt | lark-cli docs +update --api-version v2 --doc DOC \
  --command str_replace --pattern "目标文本" --content - --as bot
```

- 文件扩展名用 `.txt` 而非 `.xml` 可进一步避免触发 XML 解析路径
- 此方法实测成功：~15KB 的脚本 XML 内容通过 stdin 管道一次性 str_replace 成功

#### str_replace 插入式替换会吃掉 pattern 前缀 (2026-06-01)

- **场景**：想在「脚本10」之前插入「脚本1-9」，用 `--pattern '<hr/><h2>脚本10'` 匹配脚本10的起始标记，`--content` 放脚本1-9的全部内容
- **陷阱**：`str_replace` 是**完全替换**——pattern 匹配的文本 `<hr/><h2>脚本10` 会被整个替换为 content，不会保留。结果脚本10的开头标签消失了，只剩残缺的 `｜「桨板上的朋友」｜15秒</h2>`
- **检测**：替换后 `grep` 检查所有关键标题是否完整出现
- **修复**：再用一次 `str_replace` 把残缺标题补全。或**从一开始就在 replacement 末尾包含原 pattern**：

```bash
# ❌ 错误：content 不含 pattern，会丢失脚本10标题
--pattern '<hr/><h2>脚本10' --content @scripts_1_9.txt

# ✅ 正确：在 content 末尾把 pattern 原文加回去
# scripts_1_9.txt 末尾应包含 '<hr/><h2>脚本10' 作为衔接
cat scripts_with_s10_header.txt | lark-cli ... --content -
```

- **通用规则**：任何「在 X 之前插入 Y」的场景，replacement 必须是 `Y + X`，不能只有 Y

### `overwrite` 遇到内部 `<img src>` 标签导致内容截断 (2026-05-29)

- **触发条件**：文档中包含 Feishu 内部图片引用 `<img name="..." href="https://internal-api-drive-stream.feishu.cn/..." mime="image/png" scale="1.000000" src="DfdjbqxhJoTYypxCjMBcnk3fn2f"/>`（带 `src` 属性的内部文件 token），执行 `overwrite` 时 lark-cli XML tokenizer 报 `degrade_code=3001`（"XML tokenization error"）
- **后果**：①所有带 `src` 的内部 `<img>` 标签被剥离 ②第一个问题 `<img>` 之后的**全部内容被截断丢失**（静默失败，revision 仍递增）
- **检测方法**：`overwrite` 响应中 `"result": "partial_success"` + `"warnings": ["degrade_code=3001..."]`；随后 `fetch` 比对内容长度和关键章节
- **修复方法**：`fetch` 定位截断位置 → 构造丢失内容 XML（跳过问题 img 标签，用 `<p><em>（照片需手动重新上传）</em></p>` 占位）→ `append` 补回
- **预防策略**：替换文档中某一章节时，优先用多个小范围 `str_replace` 而非一次大段 `overwrite`。若必须 `overwrite`，提前从 preserve 内容中**移除所有带 `src` 属性的 `<img>` 标签**。完整操作流程见 `references/safe-section-replacement.md`。

### `overwrite` 含 `<title>` 导致 Wiki 节点幽灵残留 (2026-05-30)

- **触发条件**：`docs +update --command overwrite --content @file.xml` 且 XML 包含 `<title>新标题</title>`
- **后果**：lark-cli 自动重命名文档，但 Wiki 节点树中**保留旧名称的幽灵条目**——该条目仍显示旧标题，点开为空内容。用户看到旧标题节点以为是空文档，误判"文档未生成"
- **检测方法**：`wiki +node-list --parent-node-token <project>` 后发现有标题相似但不同 node_token 的重复条目
- **幽灵节点特征**：`wiki +node-delete` 对该节点报 `131005 not found`（底层文档已不存在，只剩树形引用）
- **正确做法**：
  - **推荐**：不写 `<title>` 标签，用 `--new-title` 单独设置标题
  - **备选**：如需在 XML 中写 `<title>`，write 后立即 `wiki +node-list` 检查是否出现幽灵条目
- **防混淆向用户交付**：提供文档直链 `https://acn3kz7weyc0.feishu.cn/docx/{obj_token}` 而非 Wiki 节点链接 `https://acn3kz7weyc0.feishu.cn/wiki/{node_token}`

### feishu-wiki 联动（v4）

- **全量巡检**：每日 5:00 自动扫描知识库 → 检测变动 → **自动移动**分类错误文档 → 级联验证
- **AI 文档总结**：LLM Agent 读取文档内容 → 生成 200 字中文总结 → 缓存到 `wiki_summaries.json`
- **首页同步**：骨架 XML（含 `##SUMMARY##` 占位符）→ Agent 填充总结 → overwrite 写入首页
- **变更日志**：每次变动（新增/删除/移动/更新）自动写入变更日志 docx，最新条目在最上方
- **首页 token**：`Y4LYd1X8Yo1Du9x9WtNcYD51nte`
- **变更日志 token**：`LJ7RdGzVVoUX6rxmzwpcH3L0npg`
- 详细操作 → 加载 `feishu-wiki` 技能

### `lark-cli api DELETE` 查询参数必须用 `--params` 而非 URL query string (2026-06-06)

- **触发条件**：`lark-cli api DELETE "/path?type=docx"` — 在 URL 中附加 `?type=docx` 查询参数
- **后果**：返回 `99992402: field validation failed, "type is required"`。lark-cli 在 DELETE 请求中不自动将 URL query string 传参
- **正确做法**：使用 `--params '{"type":"docx"}'` 显式传递查询参数：
  ```bash
  # ✅ 正确
  lark-cli api DELETE "/open-apis/drive/v1/files/{doc_token}" --params '{"type":"docx"}' --as bot
  ```
- **验证**：删除后 `docs +fetch` 返回 `3380003: Document page has been deleted` 确认成功

### 多实例文本替换（≥3 处）：用源 XML + overwrite

`str_replace` 仅替换首次匹配，无法处理批量同名替换（如"于袁天"出现 9 次需 9 次 API 调用）。高效方案：

```bash
# 1. 保留文档的原始 XML 源文件（创建时用的 .xml）
# 2. sed 一次性替换所有实例
sed -i 's/旧文本/新文本/g' /tmp/doc_source.xml
# 3. overwrite 回写
cd /tmp && lark-cli docs +update --api-version v2 --doc DOC_ID \
  --command overwrite --content @doc_source.xml --as bot
```

**前提**：必须有原始 XML 源文件。如果丢失，`docs +fetch` 不可靠（Wiki 文档 blocks=0），需用 REST API 逐 block 重建 XML，代价大。

### `docs +fetch` 云空间文档同样 blocks=0 (2026-06-06)

此前已记录 Wiki 文档的 `docs +fetch` blocks=0 误报。2026-06-06 确认：**不带 `--parent-token` 创建的云空间文档同样受影响**，`fetch` 返回 `Outline items: 0, Blocks: 0` 但 REST API 确认内容存在（callout、heading1、divider 等 block 正常）。

**对策不变**：始终用 `GET /docx/v1/documents/{id}/blocks/{id}/children` 做内容验证，不依赖 fetch。

### 保留源 XML 时的批量文本替换：sed + overwrite (2026-06-06)

当需要对文档做全量文本替换（如人名/术语统一修正），且**仍持有创建时的源 XML 文件**时，最快路径：

```bash
# 1. 直接在源 XML 上替换
sed -i 's/旧文本/新文本/g' /tmp/source.xml

# 2. overwrite 回写
cd /tmp && lark-cli docs +update --api-version v2 --doc DOC_ID \
  --command overwrite --content @source.xml --as bot
```

**优势**：绕过了 `docs +fetch` blocks=0 的不可靠问题，也绕过了 `str_replace` 每次只替换一个匹配的限制。本次会话中用此法一次性替换了 3 篇文档共 20 处"于袁天→夏与"，每篇仅 1 次 API 调用。

**前提**：源 XML 没有 `<img src="...">` 内部图片标签（否则 overwrite 会截断，见 overwrite 陷阱）。会议纪要、审议文档等纯文本+callout+table 的文档完全安全。

**对比 `str_replace`**：`str_replace` 每次只替换一个匹配，20 处需 20 次调用，且中间可能因 revision 变化导致定位偏移。sed+overwrite 是一步完成的原子操作。

- **触发条件**：先用 v1 `docs +create` 创建文档到云空间，再试图通过 `POST /open-apis/wiki/v2/spaces/{space_id}/nodes` 的 `origin_node_token` 将已有文档挂载到知识库
- **后果**：API 返回成功 `code:0`，但在知识库中创建的是一个**全新的空文档**（`obj_token` 与原始文档不同），不是对已有文档的引用。原始文档仍在云空间中，内容未迁移
- **检测方法**：用新 `obj_token` 执行 `docs +fetch` → outline 为空
- **正确做法**：创建时直接用 v2 `--api-version v2 --doc-format markdown --parent-token TOKEN`，一步到位写入知识库。如果已经在云空间创建了文档，用 `docs +fetch` 取回内容后 `overwrite` 到知识库文档中
- **清理**：空节点需用 `lark-cli wiki +node-delete --node-token <NODE> --obj-type wiki --yes` 删除

### 知识库 `nodes` API 对所有 parent 返回相同根节点列表 (2026-06-01)

- **触发条件**：`GET /nodes?parent_node_token=<ANY_CLASSIFICATION_SUBNODE>` — 无论传哪个子分类的 `node_token`，API 始终返回相同的 6 个根级节点（首页、最近更新、运营管理、内容素材、咨询洞察、AI Native 工作流）
- **影响**：无法通过 REST API 验证文档是否出现在正确的子分类下
- **根因**：此知识库在 2026-06-01 重组过分类结构，API 的父子关系映射可能未同步更新。飞书 UI 中的树形结构正常，仅 API 查询异常
- **对策**：创建时直接指定正确的 `--parent-token`（CLI v2 已验证可正确归档到子分类），信任创建行为，不依赖 API `node-list` 做归档验证

### 批量文本替换 → `overwrite` 优于多次 `str_replace`

当需要对文档做多处相同文本替换时（如全文替换人名、地名），逐次 `str_replace` 需要 N 次 API 调用且容易遗漏。**更高效的方式：**

```bash
# 前提：你有创建该文档时使用的原始 XML 文件
sed -i 's/旧文本/新文本/g' original.xml
lark-cli docs +update --api-version v2 --doc DOC_ID --command overwrite --content @original.xml --as bot
```

一次 overwrite 替代 N 次 str_replace。适用于：全文人名替换、地名修正、统一术语等场景。注意 overwrite 会丢失图片/评论，仅当文档无图片时使用。

### 子分类 node_token 可能失效，须做回退 (2026-06-03)

- **触发条件**：创建文档时使用子分类 node_token（如 `FB6DwZlXhijL38kz0J6cy8gznhd` 业务规范）作为 `--parent-token`，返回 `3380002: Parent node not found`
- **根因**：知识库 2026-06-01 重组后，子分类 token 可能已变化。表中列出的子分类 token 是重组前记录的值，部分已失效。飞书 API 的 `nodes` 端点无法返回子节点列表（见上一陷阱），无法通过 API 发现新 token
- **已确认有效的 token**（2026-06-03 验证）：
  - ✅ `W57jwRHJYimFRskVK2VcCQjfnXf` — 运营管理（一级分类）
  - ✅ `XMVrw88PsijL6Ek4S2sc1B5enuh` — 内容素材（一级分类）
  - ✅ `UF7Cw5w2WiHGfjkKVvBcxj8Hnib` — 咨询洞察（一级分类）
  - ✅ `J4EewYIT2ieFuwkRWbxcgWbFnhe` — AI Native 工作流（一级分类）
- ✅ `GI1cwlAUviHXIqk291vcjNxvnGb` — 会议纪要（子分类）— **已确认有效 (2026-06-06)**，连续两次创建成功
- ✅ `J9h6wJgO4ij7NjkXNTCc6mNDnwf` — 文案素材（子分类）— **已确认有效 (2026-06-09)**\n- ✅ `HrJXwlne7ioywnkDpAlc6p08ngV` — 产品研发（子分类）— **已确认有效 (2026-06-08)**
- ✅ `J9h6wJgO4ij7NjkXNTCc6mNDnwf` — 文案素材（子分类）— **已确认有效 (2026-06-09)**
- ✅ `PAVdwkNpNiedvfkPLIec1gK7nAU` — 团队管理（子分类）— **已确认有效 (2026-06-08)**
- ✅ `JIKCw1IXAi5ZYxkBKW0cYEuanGF` — 运营策略（子分类）— **已确认有效 (2026-06-08)**
- ✅ `NHaQwmHNliUnSekHDOmcPPGfn8f` — 任务复盘（子分类）— **已确认有效 (2026-06-08)**
- ✅ `J9h6wJgO4ij7NjkXNTCc6mNDnwf` — 文案素材（子分类）— **已确认有效 (2026-06-09)**
- ❌ `FB6DwZlXhijL38kz0J6cy8gznhd` — 业务规范（子分类）— 3380002 失效
- ❌ `V0Lhwl7KYiWYDDk1vCncv2GhnYf` — 行业资讯（子分类）— 3380002 **已确认失效 (2026-06-04)**
- ❌ `EAMYw1CPoipVWtkObbtcR2oDnNc` — 竞品动态（子分类）— 3380002 **已确认失效 (2026-06-04)**
- ✅ `KVPTwrbOKiQMUkkUPlscaEKfnUd` — 方案计划（子分类）— **已确认有效 (2026-06-10)**，本次会话成功创建文档
- ⚠️ 其余子分类 token — 未逐一验证，可能部分失效
- **回退策略**：
  1. 优先尝试子分类 token → 如返回 3380002，立即回退到对应的一级分类 token
  2. 一级分类 token（上述 4 个）已确认稳定有效，文档会创建在对应大类下
  3. 事后通知用户文档在一级分类下，需手动移至子分类（或等待 feishu-wiki 自动巡检移动）
- **不必浪费时间逐个验证子分类 token**：直接尝试目标子分类，失败即回退一级分类。此策略不会阻塞文档产出

---

## 常用命令速查

| 操作 | 命令 |
|------|------|
| 创建文档（应用云空间） | `lark-cli docs +create --api-version v2 --doc-format xml --content @file.xml --as bot` |
| 创建文档（知识库，XML） | `lark-cli docs +create --api-version v2 --doc-format xml --content @file.xml --parent-token TOKEN --as bot` |
| 创建文档（知识库，Markdown） | `cd /tmp && lark-cli docs +create --api-version v2 --doc-format markdown --content @file.md --parent-token TOKEN --as bot`（标题以 `<title>标题</title>` 写在内容首行，`--title` 已废弃） |
| 读取文档 | `lark-cli docs +fetch --api-version v2 --doc DOC --as bot` |
| 读取文档（含 block ID） | `lark-cli docs +fetch --api-version v2 --doc DOC --detail with-ids --as bot` |
| 追加内容 | `lark-cli docs +update --api-version v2 --doc DOC --command append --content @file.xml --as bot` |
| 文本替换 | `lark-cli docs +update --api-version v2 --doc DOC --command str_replace --pattern "旧" --content "新" --as bot` |
| 文本替换（大段内容，stdin） | `cat /tmp/content.txt \| lark-cli docs +update --api-version v2 --doc DOC --command str_replace --pattern "旧" --content - --as bot` |
| 全文覆盖 | `lark-cli docs +update --api-version v2 --doc DOC --command overwrite --content @file.xml --as bot` |
| 插入图片 | `lark-cli docs +media-insert --doc DOC --file img.png --caption "说明" --as bot` |
| 搜索知识库 | `lark-cli docs +search --query "关键词" --as user` | ⚠️ 仅 `--as user`，cron不可用 |
| 列出知识库节点（根） | `lark-cli wiki +node-list --space-id 7643710721485753535 --page-all --as bot` |
| 列出分类子节点 | `lark-cli wiki +node-list --space-id 7643710721485753535 --parent-node-token TOKEN --page-all --as bot` |
| 删除知识库节点 | `lark-cli wiki +node-delete --node-token TOKEN --obj-type wiki --yes` |
| 删除云空间文档 | `lark-cli api DELETE "/open-apis/drive/v1/files/{doc_token}" --params '{"type":"docx"}' --as bot` | ⚠️ 必须用 `--params`，URL 中 `?type=docx` 无效 |
| 通用 API 调用 | `lark-cli api GET /open-apis/wiki/v2/spaces/7643710721485753535/nodes` |
| 列出评论 | `feishu_drive_list_comments(file_token=DOC)` |
| 回复评论 | `feishu_drive_reply_comment(file_token=DOC, comment_id=ID, content="...")` |
