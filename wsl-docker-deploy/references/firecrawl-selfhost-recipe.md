# Firecrawl 自托管部署配方

## 镜像清单

| 镜像 | 大小 | crane 拉取命令 |
|------|------|---------------|
| `ghcr.io/firecrawl/firecrawl:latest` | 307MB | `crane pull ghcr.io/firecrawl/firecrawl:latest` |
| `ghcr.io/firecrawl/playwright-service:latest` | 520MB | `crane pull ghcr.io/firecrawl/playwright-service:latest` |
| `docker.io/library/postgres:17` | 154MB | `crane pull docker.io/library/postgres:17` |

> 注意：compose 中 `nuq-postgres` 有 Dockerfile（`FROM postgres:17` + pg_cron），需预拉 postgres:17 否则 build 阶段超时。

## docker-compose 修改

两个关键改动（从源码 build → 预构建 image）：

```yaml
# API 服务
services:
  api:
    image: ghcr.io/firecrawl/firecrawl:latest   # 加上 tag
    # build: apps/api                             # 注释掉

  playwright-service:
    image: ghcr.io/firecrawl/playwright-service:latest
    # build: apps/playwright-service-ts
```

## .env 最小配置

```env
PORT=3002
HOST=0.0.0.0
PROXY_SERVER=http://host.docker.internal:7890
BULL_AUTH_KEY=<random-string>
```

## Hermes MCP 接入

```bash
# 非交互式添加（需要 pipe Y 绕过 TUI 确认）
echo "Y" | hermes mcp add firecrawl --command npx --args -y firecrawl-mcp --env FIRECRAWL_API_URL=http://localhost:3002
```

接入后 Hermes 获得 26 个工具：`firecrawl_search`、`firecrawl_scrape`、`firecrawl_crawl`、`firecrawl_map`、`firecrawl_extract`、`firecrawl_agent` 等。

## 验证

```bash
# 健康检查
curl http://localhost:3002/v1/scrape -H 'Content-Type: application/json' -d '{"url":"https://example.com"}'

# 搜索（自托管版可用，云端免费版不可用）
curl http://localhost:3002/v1/search -H 'Content-Type: application/json' -d '{"query":"test","limit":2}'

# 国际站点（通过代理）
curl http://localhost:3002/v1/scrape -H 'Content-Type: application/json' -d '{"url":"https://news.ycombinator.com"}'
```

## 与云端版对比

| | 免费云端 | 自托管 |
|---|:---:|:---:|
| Credits | 500/月 | ∞ |
| Search | ❌ | ✅ |
| Crawl | ❌ | ✅ |
| 代理出国 | ❌ | ✅（通过 PROXY_SERVER） |
| 额度焦虑 | 有 | 无 |

## docker-compose YAML 坑位

`docker-compose.windows.yaml` 中 `services.api` 有一个空 `ulimits:` 行（无值），导致 `docker compose -f docker-compose.windows.yaml up -d` 报错 `ulimits must be a mapping`。

**修复**：删除 `api` 服务下的空 `ulimits:` 行。merge 模式（`docker-compose.yaml` + `docker-compose.windows.yaml`）下 base yaml 已提供 ulimits 定义。

`docker compose restart` 不受影响（不验证 config），watchdog 优先用 restart。

## 一键启动脚本

`start-firecrawl.bat`（位于 compose 目录）：自动启动 Docker Desktop → 等待就绪 → `docker compose up -d` → 验证 health。

## 健康守护（Watchdog）

由 Hermes cron job `firecrawl-health-watchdog` 自动管理，脚本位于 `firecrawl-web` 技能的 `scripts/firecrawl-watchdog.py`。

- 频率：每 5 分钟
- 方式：`no_agent=true`（纯脚本，零 LLM 开销）
- 策略：健康时静默 → 异常时 `restart` → 不成就 `up -d` → 仍失败告警
- SYSTEM 账户限制：WSL2 不支持 SYSTEM 上下文，Docker Desktop 崩溃后 watchdog 无法重启 Daemon（只能修复容器层问题）。此时需用户在 Aorus 桌面运行 `start-firecrawl.bat`。
