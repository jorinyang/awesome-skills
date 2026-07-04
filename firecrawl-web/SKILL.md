---
name: firecrawl-web
description: "Firecrawl 自托管 web 搜索与抓取——搜索网页、抓取内容、爬取网站、提取结构化数据时自动使用。MCP 调用本地 Firecrawl (localhost:3002)，无限额度。触发：搜索/查资料/抓取/爬取/提取数据/web search/scrape/crawl/extract。"
version: 1.0.0
author: jorinyang
triggers:
  - 搜索
  - 查资料
  - 抓取
  - 爬取
  - 提取数据
  - web search
  - scrape
  - crawl
  - 帮我查一下
  - 找一下
  - 搜一下
---

# Firecrawl 自托管 Web 工具

> 自托管 Firecrawl 实例 (localhost:3002)，无限额度。

## 🔴 铁律：搜索路由优先级

```
firecrawl_search（优先，全文 markdown，策展索引）
    ↓ 不可用时降级
mcp_minimax_mcp_web_search（备选，摘要式）
    ↓
❌ web_search（永久禁用）
```

> **Firecrawl 自托管实例是自有策展索引，非 Google 套壳。支持 domain/time/location 过滤、github/research/pdf 专项分类。全文 markdown 信息密度远超摘要。MiniMax 仅作为 Firecrawl 挂掉时的后备通道。**

## 使用规则（按步骤执行）

| 步骤 | 动作 | 输入 | 输出 | 说明 |
|---|---|---|---|---|
| 1 | 搜索 | 用户查询（中文/英文关键词）、`limit`（默认 5） | Markdown 格式搜索结果列表 | 优先用 `firecrawl_search`，全文 markdown，策展索引 |
| 2 | 🔴 降级搜索 | 同上 | 摘要式搜索结果 | 仅 Firecrawl 不可用时，用 `mcp_minimax_mcp_web_search` |
| 3 | 🔴 抓取单页 | URL | Markdown 格式页面内容 | 用 `firecrawl_scrape`；确认 URL 公开可访问、需 JS 渲染 |
| 4 | 🔴 整站爬取 | URL + `limit`（默认 10，最大 50） | 多页面 Markdown 列表 | 用 `firecrawl_crawl`；确认 limit、robots.txt、深度限制 |
| 5 | 🔴 结构化提取 | URL 列表 + `prompt`（字段描述） | JSON 结构化数据 | 用 `firecrawl_extract`；确认 prompt 明确、URL 已去重 |
| 6 | 搜索优化 | 搜索反馈 | 优化后搜索结果 | 用 `firecrawl_search_feedback`，搜索结果不满意时 |

> ❌ `web_search` 永久禁用。🔴 = 执行前需用户确认 CHECKPOINT。

## 工具速查

> 自托管实例无 API key，搜索国内内容可能需要加中文关键词。

| 工具 | 用途 | 示例 |
|------|------|------|
| `firecrawl_search` | 搜索网络 | `{"query": "AI agent 最新进展", "limit": 5}` |
| `firecrawl_scrape` | 抓取单页（markdown） | `{"url": "https://example.com"}` |
| `firecrawl_scrape` (query) | 抓取单页（LLM 提取） | `{"url": "...", "formats": ["query"], "queryOptions": {"prompt": "..."}}` — SaaS 文档截断时首选 |
| `firecrawl_crawl` | 整站爬取 | `{"url": "https://docs.example.com", "limit": 20}` |
| `firecrawl_map` | 发现所有 URL | `{"url": "https://example.com"}` |
| `firecrawl_extract` | 结构化提取 | `{"urls": [...], "prompt": "提取产品名称和价格"}` |
| `firecrawl_agent` | 自主研究 | `{"prompt": "调研市场上最好的 AI 爬虫工具"}` |

## 失败模式与恢复

| 触发条件 | 症状 | 一线修复 | 仍失败兜底 |
|---|---|---|---|
| Firecrawl 实例未启动 | 连接拒绝/超时 | `docker ps \| grep firecrawl`，`docker start firecrawl` | 降级用 `mcp_minimax_mcp_web_search` |
| Firecrawl 实例未启动+Docker不可用 | 连接拒绝/超时+`docker ps` 超时 | **中文工商搜索降级**：用 `execute_code` 直接 HTTP 搜 Sogou（搜狗），再用正则提取公司名称/法人/注册资本等字段。Sogou 对国内企业信息命中率远好于 Bing。 | 让用户提供天眼查/企查查 URL，用 `web_extract` 直接提取 |
| 目标站点 robots.txt 禁止 | 403/禁止爬取 | 改用 `firecrawl_scrape` 单页抓取 | 向用户说明限制，请求替代 URL |
| JS 渲染不完整 | 返回内容为空 | 添加 `formats: ["markdown"]`，确认版本支持 | 降级用 `browser_navigate`（需交互时） |
| 搜索无结果 | 返回空列表 | 添加中文关键词，`firecrawl_search_feedback` | 降级用 `mcp_minimax_mcp_web_search` |
| 结构化提取失败 | 返回空 JSON | 检查 `prompt` 字段名，减少 URL 数量 | 单页抓取后手动解析 markdown |
| 触发站点限流 | 429 Too Many Requests | 增大延迟，降低 `limit`，暂停 5 分钟 | 分批爬取或换时段 |
| SaaS 文档截断 | 长文档 markdown 不完整，代码/表格被截（钉钉/飞书/Notion 等 SPA 文档） | **首选**：`firecrawl_scrape` + `formats: ["query"]` + 详细 `queryOptions.prompt`（见下方「query 格式提取」）；query 模式绕过 markdown 渲染截断，直接 LLM 提取结构化内容 | `waitFor` 10s 等 JS 完全渲染；`firecrawl_map` 定位子页面逐个抓取 |
| `firecrawl_agent` 报 Unauthorized | `API key is required when not using a self-hosted instance` | 自托管实例不提供 agent；改用 `firecrawl_search` → `firecrawl_scrape` 手动组合 | 或 Chrome CDP 直接提取（见下方） |

### SaaS 文档截断主力方案：query 格式提取

当 `firecrawl_scrape` 的 markdown 格式对 SaaS 文档（钉钉 alidocs / 飞书 / Notion）返回截断内容时，**不要立即跳到 Chrome CDP**。先用 `query` 格式：

```json
{
  "url": "https://alidocs.dingtalk.com/i/nodes/...",
  "formats": ["query"],
  "waitFor": 8000,
  "queryOptions": {
    "mode": "freeform",
    "prompt": "提取 XXX 的完整定义，包括所有字段、类型、代码示例和协议细节。"
  }
}
```

**为什么有效**：query 模式让 Firecrawl 的后端 LLM 直接理解和提取页面内容，绕过 markdown 渲染层的截断。对长文档的效果远好于 markdown。

**成功案例**：钉钉 alidocs（共享文档，无需登录）的 ExclusiveSkillHub 接入指南（1443 词）和技能路由对接说明（3040 词），markdown 格式在 ~3000 字符处截断，但 query 格式准确提取了全部 7 个 SkillBridge action 的完整 TypeScript 类型定义、请求/响应 JSON Schema、协议细节。钉钉 alidocs 的文档内容内嵌在页面 HTML 中，Firecrawl 可直接抓取——不需要 Chrome 登录。

**prompt 编写原则**：
- 明确列出要提取的具体内容（字段名、类型、枚举值）
- 使用"完整"、"所有"、"全部"等词确保 LLM 不会省略
- 对技术文档，指定要提取的代码示例、协议细节、Schema 定义

### Chrome CDP 提取（备用，仅限已登录场景）

当 query 格式也返回不完整，且 Chrome 实例**已登录**该 SaaS 平台时：

```bash
# 启动带远程调试的 Chrome（--remote-allow-origins=* 必须）
chrome.exe --remote-debugging-port=9223 --remote-allow-origins="*" ^
  --user-data-dir="%USERPROFILE%\.chrome-debug-profile" ^
  --no-first-run --no-default-browser-check "URL1" "URL2"

# 获取页面列表 → 找到目标页面的 webSocketDebuggerUrl
# 通过 CDP Runtime.evaluate 执行 JS 提取 document.body.innerText
```

**前提**：Chrome 实例必须已登录该 SaaS 平台（否则只能拿到登录页，`body.innerText` 为空）。端口冲突换其他端口。

**已知限制（已验证）**：未登录钉钉的 Chrome 实例（`--user-data-dir` 新 profile）访问 alidocs → `document.body.innerText` 返回空，`loginBtn` 为 true。必须用已登录的 default profile 或先手动扫码登录。此方案仅适用于用户已有登录态的场景——未登录时回退到 query 格式。

## 部署与接入

> 部署配方见 `wsl-docker-deploy` 技能 `references/firecrawl-selfhost-recipe.md`。

### MCP 添加（非交互）

`hermes mcp add` 默认是 TUI，非交互环境下用 `echo "Y" |` 管道自动确认：

```bash
echo "Y" | hermes mcp add firecrawl --command npx --args -y firecrawl-mcp --env FIRECRAWL_API_URL=http://localhost:3002
```

添加完成后需要 `/new` 重启会话，MCP 工具才会生效。

## ⛔ 反例与禁止

- ❌ **使用 `web_search`** — 永久禁用，始终用 `firecrawl_search`，降级用 `mcp_minimax_mcp_web_search`
- ❌ **爬取登录/付费/验证码内容** — Firecrawl 只处理公开页面
- ❌ **同域名并发 >5 请求** — 尊重 robots.txt 和目标站点
- ❌ **Firecrawl 可用时用 `browser_navigate` 抓取静态页** — Firecrawl 自动 JS 渲染，返回更干净 markdown
- ❌ **跳过 `firecrawl_search` 直接用 `mcp_minimax`** — 除非 Firecrawl 确实不可用（连接拒绝/超时）
- ❌ **`limit` 超过 50** — 避免过度爬取触发风控
- ❌ **传 `apiKey` 参数** — 自托管实例不需要
