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
