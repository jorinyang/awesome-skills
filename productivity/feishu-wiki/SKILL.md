---
name: feishu-wiki
description: Feishu Wiki 知识库全面管理 — 目录探索、文档摘要、分类检测、变动追踪、变更日志
tags: [feishu, wiki, knowledge-base, directory, categorization, change-tracking]
category: productivity
---

# Feishu Wiki — 知识库全面管理 (v2)

## 功能概述

对飞书知识库进行全生命周期管理：目录结构探索与展示、文档分类检测、变动追踪、变更日志自动记录。

**核心设计原则：只读 + 写入 docx，不移动节点。**

## ⛔ 关键安全约束

### Move API 是危险的 — 绝对禁止使用

`POST /wiki/v2/spaces/{space_id}/nodes/{node_token}/move` 和 `lark-cli wiki +move` 在当前应用配置下会导致**知识库树结构级联损坏**。

**实测证据 (2026-05-28)**：
- 移动 1 个节点（企业文化→行业资讯）导致 15+ 个节点被随机重排到错误父级
- 每次后续移动触发更多级联损坏
- 节点从正确的父级凭空消失，出现在不相关的分类下
- 损坏不可逆 — 即使移回也无法恢复原始结构

**替代方案**：检测到分类错误时，**生成报告通知用户手动调整**，不自动移动。

---

## 认证

CLI v2 已配置完成：

```bash
# 验证配置
lark-cli config show
```

**身份选择：**
- `--as bot`（默认）：应用身份，可写文档
- `--as user`：用户身份，需 `lark-cli auth login`

**REST API Token 获取（需要时）：**
```bash
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$FEISHU_APP_ID\",\"app_secret\":\"$FEISHU_APP_SECRET\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")
```

---

## 知识库信息

| 项目 | 值 |
|------|-----|
| space_id | `7643710721485753535` |
| 知识库首页 URL | `https://acn3kz7weyc0.feishu.cn/wiki/NBW2wANDViY5BSkbVA1cnETfnEf` |
| 首页 doc_token (obj) | `Y4LYd1X8Yo1Du9x9WtNcYD51nte` |
| 最近更新 doc_token (obj) | `LJ7RdGzVVoUX6rxmzwpcH3L0npg` |

### 分类节点（用于 parent_node_token 查询）

| 分类 | parent_node_token |
|------|-------------------|
| 企业文化 | `KqoZwqut8ilTSFk3SX4cOpQ9nZf` |
| 团队管理 | `PAVdwkNpNiedvfkPLIec1gK7nAU` |
| 产品研发 | `HrJXwlne7ioywnkDpAlc6p08ngV` |
| 运营策略 | `JIKCw1IXAi5ZYxkBKW0cYEuanGF` |
| 业务规范 | `FB6DwZlXhijL38k0z6Jcy8gznhd` |
| 会议纪要 | `GI1cwlAUviHXIqk291vcjNxvnGb` |
| 方案计划 | `KVPTwrbOKiQMUkkUPlscaEKfnUd` |
| 行业资讯 | `V0Lhwl7KYiWYDDk1vCncv2GhnYf` |
| 竞品动态 | `EAMYw1CPoipVWtkObbtcR2oDnNc` |
| AI Native 工作流 | `J4EewYIT2ieFuwkRWbxcgWbFnhe` |
| 汇报资料 (leaf) | `MebBwjMDgiUH4YkNeEmcLhxFnrb` |
| 文案素材 (leaf) | `J9h6wJgO4ij7NjkXNTCc6mNDnwf` |

---

## 核心工作流

### 流程一：全面探索知识库目录

列出所有分类及其子文档，生成结构化的目录快照。

**API 调用**：
```bash
# 1. 列出根级节点
curl -s "https://open.feishu.cn/open-apis/wiki/v2/spaces/7643710721485753535/nodes?page_size=50" \
  -H "Authorization: Bearer $TOKEN"

# 2. 对每个 has_child=true 的节点，列出子节点
curl -s "https://open.feishu.cn/open-apis/wiki/v2/spaces/7643710721485753535/nodes?page_size=50&parent_node_token={node_token}" \
  -H "Authorization: Bearer $TOKEN"
```

**输出格式**（用于快照存储和比较）：
```json
{
  "scanned_at": "2026-05-28T17:00:00+08:00",
  "categories": {
    "行业资讯": {
      "node_token": "V0Lhwl7KYiWYDDk1vCncv2GhnYf",
      "children": [
        {"title": "2026-05-28_酒店_xxx", "node_token": "WsXv...", "obj_type": "docx"}
      ]
    }
  }
}
```

### 流程二：生成文档摘要

对每篇文档获取内容摘要（取 raw_content 前 200 字符）。

```bash
curl -s "https://open.feishu.cn/open-apis/docx/v1/documents/{obj_token}/raw_content" \
  -H "Authorization: Bearer $TOKEN"
```

> 注意：使用 `obj_token`（非 `node_token`）。`obj_token` 从节点列表 API 的 `obj_token` 字段获取。

### 流程三：写入知识库首页目录

使用 `lark-cli docs +update --command overwrite` 全量覆盖首页内容。

**目录结构 XML 模板**：
```xml
<title>首页</title>
<p>🕐 最后更新：{timestamp} CST</p>
<hr/>
<h2>📂 知识库目录</h2>
<p>共 <b>{category_count}</b> 个分类，<b>{doc_count}</b> 篇文档</p>
<hr/>

<!-- 每个分类一节 -->
<h3>📁 {分类名} ({N}篇)</h3>
<p><em>收录范围：{范围说明}</em></p>
<ul>
  <li><a href="https://acn3kz7weyc0.feishu.cn/wiki/{node_token}">{文档标题}</a></li>
</ul>
<hr/>
```

**执行命令**：
```bash
cd /tmp && lark-cli docs +update --api-version v2 \
  --doc Y4LYd1X8Yo1Du9x9WtNcYD51nte \
  --command overwrite \
  --content @wiki_directory.xml \
  --as bot
```

> ⚠️ 必须先 `cd /tmp`，因为 `--content @file` 只接受相对路径。

### 流程四：写入变更日志

每次检测到知识库变动时，将变动摘要**插入到最上方**（最新在上）。

**读取当前内容**：
```bash
lark-cli docs +fetch --api-version v2 --doc LJ7RdGzVVoUX6rxmzwpcH3L0npg --as bot
```

**构建新内容**（当前内容前插入新条目）：
```xml
<title>最近更新</title>

<!-- 新条目：插入到最上方 -->
<h2>{YYYY-MM-DD} 知识库变动</h2>
<p><em>🕐 检测时间：{timestamp}</em></p>
<ul>
  <li>📂 新增文档：{title} → {category}</li>
  <li>🗑️ 删除文档：{title}（原{category}）</li>
  <li>⚠️ 分类建议：{title} 当前在「{current}」，建议移至「{suggested}」</li>
  <li>📝 内容更新：{title}（修订时间 {time}）</li>
</ul>
<hr/>

<!-- 保留的历史条目（从当前读取的内容中提取） -->
{h2}...{/h2}
...
```

**执行命令**：
```bash
cd /tmp && lark-cli docs +update --api-version v2 \
  --doc LJ7RdGzVVoUX6rxmzwpcH3L0npg \
  --command overwrite \
  --content @recent_changes.xml \
  --as bot
```

### 流程五：分类检测与建议

基于文档命名规范判断分类是否正确，生成错位报告。

**命名规范**（行业资讯类）：
| 前缀模式 | 应属分类 |
|----------|---------|
| `YYYY-MM-DD_酒店_` | 行业资讯 |
| `YYYY-MM-DD_交通_` | 行业资讯 |
| `YYYY-MM-DD_政策_` | 行业资讯 |
| `YYYY-MM-DD_活动_` | 行业资讯 |
| `YYYY-MM-DD_景点_` | 行业资讯 |
| `YYYY-MM-DD_竞品_` | 行业资讯 |
| `竞品简报` | 竞品动态 |
| `竞品分析` | 竞品动态 |
| `纪要_` | 会议纪要 |
| `方案` | 方案计划 或 运营策略 |
| `营销` | 运营策略 |
| `SOP` | 业务规范 或 产品研发 |

**检测逻辑**：
1. 遍历所有子文档
2. 按命名规则匹配应属分类
3. 若当前父级 ≠ 应属分类 → 标记为错位
4. 生成错位报告（不自动移动！）

**错位报告输出格式**：
```
⚠️ 分类错误检测 (2026-05-28)
- 「2026-05-28_景点_xxx」当前在「企业文化」，建议移至「行业资讯」
- 「竞品简报（测试运行）」当前在「产品研发」，建议移至「竞品动态」
```

### 流程六：变动检测

通过比较当前快照与上次快照检测变动。

**快照存储位置**：`~/.hermes-feishu/cron/wiki_snapshot.json`

**比较逻辑**：
1. 读取上次快照
2. 获取当前目录结构
3. 比较：
   - **新增文档**：当前有、上次无
   - **删除文档**：上次有、当前无
   - **移动文档**：node_token 相同但 parent 不同
   - **更新文档**：obj_edit_time 变化
4. 保存新快照

---

## 定时任务配置

### 每日 5:00 AM 知识库巡检

```python
# cronjob create 时的 prompt 内容：
"""
执行飞书知识库每日巡检：

1. 全面扫描知识库目录结构（spaces/nodes API）
2. 比较上次快照（~/.hermes-feishu/cron/wiki_snapshot.json）
3. 检测变动：
   - 新增/删除/移动的文档
   - 内容更新的文档（obj_edit_time 变化）
4. 分类检测：
   - 按命名规范检查所有文档当前分类是否正确
   - 生成错位报告
5. 更新首页：
   - 生成新的目录结构 XML
   - 用 lark-cli docs +update --command overwrite 写入首页
6. 写入变更日志：
   - 读取当前「最近更新」内容
   - 将今日变动 + 错位建议插入到最上方
   - 用 lark-cli docs +update --command overwrite 写入
7. 若有错位文档或重大变动，发送通知到群
8. 保存新快照
"""
```

**cron 配置**：
- schedule: `0 5 * * *`（每日 5:00 AM）
- skills: `feishu-wiki`, `feishu-doc`
- deliver: `feishu`（发送到 Home 群）

---

## API 参考

### 可用 API（已验证安全）

| API | 方法 | 说明 |
|-----|------|------|
| 列出空间节点 | `GET /wiki/v2/spaces/{id}/nodes` | 列出根级或子节点 |
| 获取节点详情 | `GET /wiki/v2/spaces/get_node?token=` | 获取单个节点信息 |
| 读取文档内容 | `GET /docx/v1/documents/{id}/raw_content` | 获取纯文本内容 |
| 读取文档 blocks | `GET /docx/v1/documents/{id}/blocks` | 获取块结构 |
| 创建文档 | `lark-cli docs +create` | 创建新文档 |
| 更新文档 | `lark-cli docs +update` | overwrite/append/str_replace |
| 读取文档 | `lark-cli docs +fetch` | 获取文档 XML |

### ⛔ 禁止使用的 API

| API | 原因 |
|-----|------|
| `POST /wiki/v2/spaces/{id}/nodes/{nt}/move` | **级联损坏知识库树结构** |
| `lark-cli wiki +move` | **同上，使用相同的底层 API** |

---

## 常见错误

### 99991672 — Missing Scope
重新发布应用版本后重新获取 token。

### lark-cli 输出不是纯 JSON
`lark-cli wiki +node-list` 在 JSON 前输出状态行，需 `tail -n +2` 处理。

### `@file` 必须是相对路径
先 `cd` 到文件所在目录再执行 lark-cli 命令。

### 131002 — param err
`obj_type=wiki` 无效，使用 `obj_type=4`（整数）。

---

## 实测陷阱 (2026-05-28)

### Move API 级联损坏
移动 1 个节点导致 15+ 个节点随机重排到其他父级下。每次后续移动触发更多损坏。**绝对不要调用 move API。**

### 首页和最近更新为 leaf 节点
这两个特殊节点 `has_child=false`，不会出现在分类遍历中。写入时通过 obj_token 直接定位。

### 竞品动态 与 行业资讯/竞品 的区别
- 「行业资讯」下的「竞品_探洞/天坑/桨板/坝盘」：**按行业分类的竞品专题研究**
- 「竞品动态」下的「竞品简报/分析」：**竞品动态汇总报告**
- 不要将两者混淆

---

## 引用文件

- `scripts/wiki_explorer.py` — 全量目录探索 + 快照生成脚本
- `scripts/wiki_monitor.py` — 每日巡检主脚本（目录比较、分类检测、变更日志）
