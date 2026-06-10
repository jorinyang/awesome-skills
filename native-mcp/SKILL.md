---
name: native-mcp
description: "MCP client: connect servers, register tools (stdio/HTTP)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [MCP, Tools, Integrations]
    related_skills: [mcporter]
---

# Native MCP Client

Hermes Agent has a built-in MCP client that connects to MCP servers at startup, discovers their tools, and makes them available as first-class tools the agent can call directly. No bridge CLI needed -- tools from MCP servers appear alongside built-in tools like `terminal`, `read_file`, etc.

## When to Use

Use this whenever you want to:
- Connect to MCP servers and use their tools from within Hermes Agent
- Add external capabilities (filesystem access, GitHub, databases, APIs) via MCP
- Run local stdio-based MCP servers (npx, uvx, or any command)
- Connect to remote HTTP/StreamableHTTP MCP servers
- Have MCP tools auto-discovered and available in every conversation

For ad-hoc, one-off MCP tool calls from the terminal without configuring anything, see the `mcporter` skill instead.

## Prerequisites

- **uv** — package manager required for `uvx`-based MCP servers (Python-based servers). Install once:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  After install, `uvx` is available at `~/.local/bin/uvx`.

- **mcp Python package** — required. Must be installed into the hermes-agent venv specifically:
  ```bash
  /home/aorus/.hermes/hermes-agent/venv/bin/pip install mcp
  ```
  Installing to system Python does NOT make it available to hermes-agent.

> **Critical**: Hermes Agent runs in its own Python venv at `~/.hermes/hermes-agent/venv/bin/python3`. Installing `mcp` to the system Python does NOT make it available to hermes-agent. Always install into the hermes venv as shown above.

## Quick Start

Add MCP servers to `~/.hermes/config.yaml` under the `mcp_servers` key:

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

Restart Hermes Agent. On startup it will:
1. Connect to the server
2. Discover available tools
3. Register them with the prefix `mcp_time_*`
4. Inject them into all platform toolsets

You can then use the tools naturally -- just ask the agent to get the current time.

## Configuration Reference

Each entry under `mcp_servers` is a server name mapped to its config. There are two transport types: **stdio** (command-based) and **HTTP** (url-based).

### Stdio Transport (command + args)

```yaml
mcp_servers:
  server_name:
    command: "npx"             # (required) executable to run
    args: ["-y", "pkg-name"]   # (optional) command arguments, default: []
    env:                       # (optional) environment variables for the subprocess
      SOME_API_KEY: "value"
    timeout: 120               # (optional) per-tool-call timeout in seconds, default: 120
    connect_timeout: 60        # (optional) initial connection timeout in seconds, default: 60
```

### HTTP Transport (url)

```yaml
mcp_servers:
  server_name:
    url: "https://my-server.example.com/mcp"   # (required) server URL
    headers:                                     # (optional) HTTP headers
      Authorization: "Bearer sk-..."
    timeout: 180               # (optional) per-tool-call timeout in seconds, default: 120
    connect_timeout: 60        # (optional) initial connection timeout in seconds, default: 60
```

### All Config Options

| Option            | Type   | Default | Description                                       |
|-------------------|--------|---------|---------------------------------------------------|
| `command`         | string | --      | Executable to run (stdio transport, required)     |
| `args`            | list   | `[]`    | Arguments passed to the command                   |
| `env`             | dict   | `{}`    | Extra environment variables for the subprocess    |
| `url`             | string | --      | Server URL (HTTP transport, required)             |
| `headers`         | dict   | `{}`    | HTTP headers sent with every request              |
| `timeout`         | int    | `120`   | Per-tool-call timeout in seconds                  |
| `connect_timeout` | int    | `60`    | Timeout for initial connection and discovery      |

Note: A server config must have either `command` (stdio) or `url` (HTTP), not both.

## How It Works

### Startup Discovery

When Hermes Agent starts, `discover_mcp_tools()` is called during tool initialization:

1. Reads `mcp_servers` from `~/.hermes/config.yaml`
2. For each server, spawns a connection in a dedicated background event loop
3. Initializes the MCP session and calls `list_tools()` to discover available tools
4. Registers each tool in the Hermes tool registry

### Tool Naming Convention

MCP tools are registered with the naming pattern:

```
mcp_{server_name}_{tool_name}
```

Hyphens and dots in names are replaced with underscores for LLM API compatibility.

Examples:
- Server `filesystem`, tool `read_file` → `mcp_filesystem_read_file`
- Server `github`, tool `list-issues` → `mcp_github_list_issues`
- Server `my-api`, tool `fetch.data` → `mcp_my_api_fetch_data`

### Auto-Injection

After discovery, MCP tools are automatically injected into all `hermes-*` platform toolsets (CLI, Discord, Telegram, etc.). This means MCP tools are available in every conversation without any additional configuration.

### Connection Lifecycle

- Each server runs as a long-lived asyncio Task in a background daemon thread
- Connections persist for the lifetime of the agent process
- If a connection drops, automatic reconnection with exponential backoff kicks in (up to 5 retries, max 60s backoff)
- On agent shutdown, all connections are gracefully closed

### Idempotency

`discover_mcp_tools()` is idempotent -- calling it multiple times only connects to servers that aren't already connected. Failed servers are retried on subsequent calls.

## Transport Types

### Stdio Transport

The most common transport. Hermes launches the MCP server as a subprocess and communicates over stdin/stdout.

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

The subprocess inherits a **filtered** environment (see Security section below) plus any variables you specify in `env`.

### HTTP / StreamableHTTP Transport

For remote or shared MCP servers. Requires the `mcp` package to include HTTP client support (`mcp.client.streamable_http`).

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer sk-..."
```

If HTTP support is not available in your installed `mcp` version, the server will fail with an ImportError and other servers will continue normally.

## Security

### Environment Variable Filtering

For stdio servers, Hermes does NOT pass your full shell environment to MCP subprocesses. Only safe baseline variables are inherited:

- `PATH`, `HOME`, `USER`, `LANG`, `LC_ALL`, `TERM`, `SHELL`, `TMPDIR`
- Any `XDG_*` variables

All other environment variables (API keys, tokens, secrets) are excluded unless you explicitly add them via the `env` config key. This prevents accidental credential leakage to untrusted MCP servers.

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      # Only this token is passed to the subprocess
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."
```

### Credential Stripping in Error Messages

If an MCP tool call fails, any credential-like patterns in the error message are automatically redacted before being shown to the LLM. This covers:

- GitHub PATs (`ghp_...`)
- OpenAI-style keys (`sk-...`)
- Bearer tokens
- Generic `token=`, `key=`, `API_KEY=`, `password=`, `secret=` patterns

## Troubleshooting

### "MCP SDK not available -- skipping MCP tool discovery"

The `mcp` Python package is not installed. Install it:

```bash
pip install mcp
```

### "No MCP servers configured"

No `mcp_servers` key in `~/.hermes/config.yaml`, or it's empty. Add at least one server.

### "Failed to connect to MCP server 'X'"

Common causes:
- **Command not found**: The `command` binary isn't on PATH. Ensure `npx`, `uvx`, or the relevant command is installed.
- **Package not found**: For npx servers, the npm package may not exist or may need `-y` in args to auto-install.
- **Timeout**: The server took too long to start. Increase `connect_timeout`.
- **Port conflict**: For HTTP servers, the URL may be unreachable.

### "MCP server 'X' requires HTTP transport but mcp.client.streamable_http is not available"

Your `mcp` package version doesn't include HTTP client support. Upgrade:

```bash
pip install --upgrade mcp
```

### Tools not appearing

- Check that the server is listed under `mcp_servers` (not `mcp` or `servers`)
- Ensure the YAML indentation is correct
- Look at Hermes Agent startup logs for connection messages
- Tool names are prefixed with `mcp_{server}_{tool}` -- look for that pattern

### Stdio `uvx` command not found — filtered PATH

MCP stdio subprocesses inherit a **filtered PATH** (only safe baseline: `PATH`, `HOME`, `USER`, `LANG`, `LC_ALL`, `TERM`, `SHELL`, `TMPDIR`, `XDG_*`). If `uvx` is at `~/.local/bin/uvx`, the subprocess won't find it because `~/.local/bin` isn't in the baseline PATH.

**Fix**: Use the absolute path in the `command` field:

```yaml
# ❌ Broken — MCP subprocess can't find uvx
command: uvx

# ✅ Correct — absolute path bypasses PATH filtering
command: /home/aorus/.local/bin/uvx
```

Same applies to any binary outside `/usr/bin` or `/usr/local/bin` (e.g., `node` from nvm, `npx` from non-system location). Verify the path with `which <binary>` and use the absolute result.

### HTTP 406 / 500 from StreamableHTTP servers — Accept header requirement

**Some MCP 2.0 StreamableHTTP servers require a specific `Accept` header** to function. The amap MCP server (`https://mcp.amap.com/mcp`) returns 406 or 500 when the client doesn't send `Accept: application/json, text/event-stream`. The `mcp` Python SDK (v1.27.0) may not send this header by default, causing persistent connection failures.

**Fix**: Add the `headers` field to the server config:

```yaml
mcp_servers:
  amap:
    url: "https://mcp.amap.com/mcp?key=your-key"
    headers:
      Accept: "application/json, text/event-stream"
    timeout: 30
```

**How to diagnose**: Test the server with curl:
```bash
# This will fail (no Accept header):
curl -X POST "https://mcp.amap.com/mcp?key=YOUR_KEY" -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{}},"id":1}'

# This works:
curl -X POST "https://mcp.amap.com/mcp?key=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{}},"id":1}'
```

If curl works (returns 200 with server capabilities) but the gateway fails, the Accept header is likely the culprit.

### HTTP MCP connection fails — first check for `***` placeholder key

The most common silent failure: the API key in the URL is a literal `***` (placeholder, never filled in). This is easy to miss because `read_file` redacts real keys to `***`, so both a real key and a literal placeholder look identical in the output.

**Diagnosis** — check raw bytes to distinguish placeholder from redacted real key:

```bash
python3 -c "
with open('config.yaml', 'rb') as f:
    content = f.read()
idx = content.find(b'amap')  # or your server name
# Check hex dump — '2a 2a 2a' = literal ***, any other hex = real key
print(content[idx:idx+200].hex(' '))
"
```

If the hex shows `2a 2a 2a` (ASCII `***`), it's a placeholder. If it shows a long hex string (like `62 64 64 32...`), it's a real key being redacted by `read_file`.

**⚠️ `patch` tool pitfall**: `read_file` may display lines differently from actual disk bytes (line reflow, key redaction). When `patch`'s `old_string` is copied from `read_file` output, it may not match the actual file content. Always verify with raw byte inspection (`python3 -c "open(...)"`) before and after patching config files.

### MCP servers not configured in profile config

Hermes Agent supports multiple profiles. Each profile uses its own `config.yaml`:
- Default: `~/.hermes/config.yaml`
- Feishu: `~/.hermes-feishu/config.yaml`
- Custom: set via `HERMES_HOME` env var

**`mcp_servers` must be configured in the profile-specific config file**, not just the default one. If you switch to a different profile (e.g., for Feishu), copy the `mcp_servers` block to that profile's config. The profiles do NOT merge or inherit MCP configurations from each other.

### MiniMax web_search returns "login fail" — API key expired

When `mcp_minimax_mcp_web_search` returns `API Error: login fail: Please carry the API secret key in the 'Authorization' field`:

```json
{"result": "Failed to perform search: API Error: login fail: ... status_code: 1004"}
```

**Root cause**: The MiniMax API key (`MINIMAX_API_KEY` in the server config) has expired or been revoked. The MCP server itself is registered and connected fine — the error comes from the MiniMax upstream API rejecting the credential.

**Diagnosis** — test the key directly against MiniMax API:
```bash
curl -s -X POST "https://api.minimaxi.com/v1/text/chatcompletion_v2" \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-M2.7","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
# status_code: 1004 = key invalid/expired
```

**Fix**: Get a new API key from https://platform.minimaxi.com and update the `MINIMAX_API_KEY` in the server config. Restart gateway.

### Connection keeps dropping

The client retries up to 5 times with exponential backoff (1s, 2s, 4s, 8s, 16s, capped at 60s). If the server is fundamentally unreachable, it gives up after 5 attempts. After giving up, it does NOT retry automatically — a gateway restart is required to reconnect. Check the server process and network connectivity.

## Examples

### Time Server (uvx)

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

Registers tools like `mcp_time_get_current_time`.

### Filesystem Server (npx)

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/documents"]
    timeout: 30
```

Registers tools like `mcp_filesystem_read_file`, `mcp_filesystem_write_file`, `mcp_filesystem_list_directory`.

### GitHub Server with Authentication

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"
    timeout: 60
```

Registers tools like `mcp_github_list_issues`, `mcp_github_create_pull_request`, etc.

### Remote HTTP Server

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.mycompany.com/v1/mcp"
    headers:
      Authorization: "Bearer sk-xxxxxxxxxxxxxxxxxxxx"
      X-Team-Id: "engineering"
    timeout: 180
    connect_timeout: 30
```

### Multiple Servers

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]

  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]

  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"

  company_api:
    url: "https://mcp.internal.company.com/mcp"
    headers:
      Authorization: "Bearer sk-xxxxxxxxxxxxxxxxxxxx"
    timeout: 300
```

All tools from all servers are registered and available simultaneously. Each server's tools are prefixed with its name to avoid collisions.

### MiniMax Coding Plan MCP (Vision + Web Search)

```yaml
mcp_servers:
  minimax:
    command: "/home/aorus/.local/bin/uvx"
    args: ["minimax-coding-plan-mcp", "-y"]
    env:
      MINIMAX_API_KEY: "${MINIMAX_CN_API_KEY}"
      MINIMAX_API_HOST: "https://api.minimaxi.com"
    timeout: 120
    connect_timeout: 60
```
`${MINIMAX_CN_API_KEY}` is interpolated from the profile's `.env` file at startup. On Feishu profile (`~/.hermes-feishu/`), the `.env` is `~/.hermes-feishu/.env`. On default profile, it is `~/.hermes/.env`. Restart Hermes Agent after adding this config.
Exposes `understand_image` (vision) and `web_search` tools. Requires `uvx` on PATH and the `minimax-coding-plan-mcp` package (auto-installed by uvx). On first run, uvx caches the package; subsequent starts are near-instant.

### Amap Maps MCP (China Mapping — Geocoding, Routing, POI, Weather)

高德地图 MCP Server 有两个代际版本：

| 版本 | 发布时间 | 接入方式 | 工具数量 | 特色能力 |
|------|----------|----------|----------|----------|
| **MCP 1.0** | 2025年3月 | npx stdio | ~7个基础工具 | 地理编码/路径规划/POI/天气 |
| **MCP 2.0** | 2025年4月 | Streamable HTTP / SSE | 基础+专属地图+唤端 | 生成专属地图导入高德APP、一键导航/打车 |

**MCP 2.0 新能力**：将大模型产出的攻略一键生成为高德地图 APP 内的专属私有地图，支持打车/导航/酒店预订/门票/加油等一站式出行服务。

#### 接入方式

**方式二：SSE — MCP 2.0（已废弃，端点返回 404）**
```yaml
# ❌ 此端点已不可用 (2026-05-30 实测 404)，请使用方式一
# url: "https://mcp.amap.com/sse?key=your-amap-web-service-key"
```

**方式一：Streamable HTTP — MCP 2.0（当前推荐，但网关有已知 bug）**

```yaml
mcp_servers:
  amap:
    url: "https://mcp.amap.com/mcp?key=your-amap-web-service-key"
    headers:
      Accept: "application/json, text/event-stream"   # ⚠️ 必须！否则返回 500
    timeout: 30
```

**⚠️ 已知问题 (2026-06-02)**：amap MCP 2.0 HTTP 端点通过 mcp Python SDK 直连完全正常（15 工具，协议 2025-03-26），但在 Hermes 网关中 `streamable_http_client` 持续抛出 `unhandled errors in a TaskGroup (1 sub-exception)` → `500 Internal Server Error`。

**根因已确认**：amap 服务器不是完整 Streamable HTTP 实现——POST JSON-RPC 正常（200），但不支持 GET SSE（返回 405）。SDK 在 `initialized` 通知后自动打开 GET SSE 流，该任务失败后被 `anyio.TaskGroup` 包装为 `ExceptionGroup`。**升级到 v2026.5.29（含 preflight 修复 64f7f3671）不会修复此问题**，因为 preflight 只检测非 MCP 端点（HTML），amap 返回合法的 `application/json` 能通过 preflight，后续 GET SSE 阶段才失败。

所有替代假设已被排除：httpx 配置、event_hooks、后台线程 event loop、message_handler、协议版本头、SDK 版本均不是原因。详见 `references/amap-gateway-500-debug.md`。

**临时方案**：使用方式三（npx stdio）作为降级，仅失去 3 个 MCP 2.0 专属工具（schema_personal_map / schema_navi / schema_take_taxi）。如需同时获得两套工具，参见 `references/dual-server-degradation.md`。

**诊断方法**：
```bash
# 1. 确认端点可达（应返回 200 + protocolVersion: 2025-03-26）
curl -s -X POST "https://mcp.amap.com/mcp?key=KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{}},"id":1}'

# 2. 确认 SDK 直连正常（应注册 15 工具）
/home/aorus/.hermes/hermes-agent/venv/bin/python3 -c "
import asyncio, httpx
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession
async def test():
    async with httpx.AsyncClient(timeout=httpx.Timeout(30), headers={'Accept': 'application/json, text/event-stream'}) as c:
        async with streamable_http_client('URL', http_client=c) as (r,w,s):
            async with ClientSession(r,w) as sess:
                result = await sess.initialize()
                print(f'protocol={result.protocolVersion}')
                tools = await sess.list_tools()
                print(f'tools={len(tools.tools)}')
asyncio.run(test())
"

# 3. 如果 SDK 直连正常但网关仍报 500 → 属于网关级 bug，降级到 npx
```

**方式三：npx stdio — MCP 1.0（npm 包 v0.0.8，需 Node.js ≥ v22.14.0）**
```yaml
mcp_servers:
  amap:
    command: "npx"
    args: ["-y", "@amap/amap-maps-mcp-server"]
    env:
      AMAP_MAPS_API_KEY: "your-amap-web-service-key"
    timeout: 30
```
npx 方式要求 npm registry 为默认源 `https://registry.npmjs.org`（用 `npm config get registry` 检查）。若设置了 npmmirror 镜像，npx 会从镜像拉取同名包（可用但可能有版本滞后风险）。仅提供 MCP 1.0 的 ~7 个基础工具：`mcp_amap_maps_geo`、`mcp_amap_maps_direction_driving`、`mcp_amap_maps_direction_walking`、`mcp_amap_maps_direction_bicycling`、`mcp_amap_maps_direction_transit_integrated`、`mcp_amap_maps_search_around`、`mcp_amap_maps_weather`。

**方式四：Python uvx（社区版本，PyPI `amap-mcp-server` v0.1.11）**
```yaml
mcp_servers:
  amap:
    command: "uvx"
    args: ["amap-mcp-server"]
    env:
      AMAP_MAPS_API_KEY: "your-amap-web-service-key"
    timeout: 30
```
社区维护版本，工具集与 MCP 1.0 类似。

#### 升级建议

如果当前使用 npx 方式（MCP 1.0），建议切到 Streamable HTTP 方式（方式一）以获得 MCP 2.0 的专属地图和高德 APP 联动功能。只需将 `command`+`args` 替换为 `url` 字段，重启 Hermes 即可。

**China coverage is drastically better than OSM/OSRM** — POI search works for county-level cities, walking/cycling modes are real (not degraded), and public transit routing is available for major cities. Get an API key at https://console.amap.com/dev/key/app (choose "Web服务" type). Free tier: 5,000 calls/day.

See also: `amap-lbs` skill (direct REST API calls), `amap-cli` skill (GUI-based map control).

Reference: `references/amap-mcp2.md` — 高德 MCP 2.0 微信文章原文及 MCP 版本演进信息。
Reference: `references/amap-mcp-response-formats.md` — 实测 15 个工具的响应格式差异表（2026-05-28），含 JSON 结构差异与 Schema 唤端纯文本返回说明。
Reference: `references/amap-gateway-500-debug.md` — amap MCP 2.0 HTTP 网关 500 问题完整 debug trace（2026-06-02），含根因确认、升级无效说明、排除假设表。
Reference: `references/amap-api-key-verification.md` — API key 占位符检测：hex 原始字节检查区分 `read_file` 脱敏 vs 真正未填的 `***`。
Reference: `references/dual-server-degradation.md` — 双条目降级模式：stdio 主力 + HTTP 增强，同一服务两种传输并存。

## Sampling (Server-Initiated LLM Requests)

Hermes supports MCP's `sampling/createMessage` capability — MCP servers can request LLM completions through the agent during tool execution. This enables agent-in-the-loop workflows (data analysis, content generation, decision-making).

Sampling is **enabled by default**. Configure per server:

```yaml
mcp_servers:
  my_server:
    command: "npx"
    args: ["-y", "my-mcp-server"]
    sampling:
      enabled: true           # default: true
      model: "gemini-3-flash" # model override (optional)
      max_tokens_cap: 4096    # max tokens per request
      timeout: 30             # LLM call timeout (seconds)
      max_rpm: 10             # max requests per minute
      allowed_models: []      # model whitelist (empty = all)
      max_tool_rounds: 5      # tool loop limit (0 = disable)
      log_level: "info"       # audit verbosity
```

Servers can also include `tools` in sampling requests for multi-turn tool-augmented workflows. The `max_tool_rounds` config prevents infinite tool loops. Per-server audit metrics (requests, errors, tokens, tool use count) are tracked via `get_mcp_status()`.

Disable sampling for untrusted servers with `sampling: { enabled: false }`.

## Notes

- MCP tools are called synchronously from the agent's perspective but run asynchronously on a dedicated background event loop
- Tool results are returned as JSON with either `{"result": "..."}` or `{"error": "..."}`
- The native MCP client is independent of `mcporter` -- you can use both simultaneously
- Server connections are persistent and shared across all conversations in the same agent process
- Adding or removing servers requires restarting the agent (no hot-reload currently)
