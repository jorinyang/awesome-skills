# MiniMax Vision + MCP — Setup Guide

## Status (2026-05-26)

Standard `/v1/chat/completions` API does NOT support image understanding — confirmed silent failure on all tested models and input formats.

**Vision capability DOES exist via `minimax-coding-plan-mcp` MCP server** — the token plan's "图像理解" refers to this MCP path.

## Setup

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After install: `uvx` lives at `~/.local/bin/uvx`.

### 2. Install mcp into hermes-agent venv

```bash
/home/aorus/.hermes/hermes-agent/venv/bin/pip install mcp
```

> Must install into hermes-agent's venv, not system Python. Hermes runs in `~/.hermes/hermes-agent/venv/`.

### 3. Add to `~/.hermes/config.yaml` (NOT `~/.hermes-feishu/config.yaml`)

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

`${MINIMAX_CN_API_KEY}` is interpolated from `~/.hermes/.env` (not `~/.hermes-feishu/.env`) at startup via `_interpolate_env_vars()`.

### 4. Restart Hermes Agent

New tools `understand_image` and `web_search` will be registered.

## Verified Working Tools

| Tool | Description | Latency |
|------|-------------|---------|
| `understand_image` | Image understanding (URL or local path) | ~20-90s |
| `web_search` | Real-time web search | ~5s |

## Key Files

- Config: `~/.hermes/config.yaml` (not feishu profile config)
- hermes venv pip: `/home/aorus/.hermes/hermes-agent/venv/bin/pip`
- MCP SDK: `/home/aorus/.hermes/hermes-agent/venv/lib/python3.11/site-packages/mcp/`
- MCP package cache: `~/.cache/uv/archive-v0/`
