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

### Connection keeps dropping

The client retries up to 5 times with exponential backoff (1s, 2s, 4s, 8s, 16s, capped at 60s). If the server is fundamentally unreachable, it gives up after 5 attempts. Check the server process and network connectivity.

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

**方式一：Streamable HTTP — MCP 2.0（官方推荐，无需本地安装）**
```yaml
mcp_servers:
  amap:
    url: "https://mcp.amap.com/mcp?key=your-amap-web-service-key"
    timeout: 30
```
对应 AMAP 官方 `gettingstarted` 文档推荐的接入方式。注册工具含 MCP 2.0 专属地图和唤端能力。

**方式二：SSE — MCP 2.0（微信文章示例）**
```yaml
mcp_servers:
  amap:
    url: "https://mcp.amap.com/sse?key=your-amap-web-service-key"
    timeout: 30
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
