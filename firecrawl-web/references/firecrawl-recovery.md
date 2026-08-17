# Firecrawl 恢复流程

## 检测 Firecrawl 是否可用

```bash
# 可靠检测：POST 搜索探针（/health 端点返回 404，不可用于检测）
curl -sf --connect-timeout 5 --max-time 20 \
  -X POST http://localhost:3002/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"h","limit":1}' \
  -o /dev/null || echo "DOWN"
```

## 守护进程（自动恢复）

已部署 `firecrawl-health-watchdog` cron job（`no_agent=true`），每 5 分钟执行：

```
策略:
  1. curl 健康检查 (POST /v1/search) → 健康则静默退出
  2. 异常 → docker compose restart (快速重启进程)
  3. restart 无效 → docker compose up -d --no-recreate (完整重建)
  4. 仍无效 → 输出告警（Docker不可用则告知需手动启动）
```

脚本：`~/.hermes/scripts/firecrawl-watchdog.py`
Cron job ID：`2aec4e07396d`
调度：`*/5 * * * *`

守护在健康时零输出，仅在异常修复/告警时产生日志。Agent 无需手动管理——守护会自动恢复。

## 诊断链路

```
curl localhost:3002/v1/search → 超时/非200？
  ├─ YES → docker ps（检查容器状态）
  │   ├─ docker 不可用 → Docker Desktop 未启动
  │   │   ├─ Agent 是 SYSTEM 用户？→ 无法自动恢复，通知用户手动启动
  │   │   └─ Agent 是普通用户？→ 启动 Docker Desktop + 等待 VM
  │   ├─ firecrawl 容器 Exited → docker compose up -d
  │   ├─ firecrawl 容器 Running 但无响应 → docker compose restart（先快恢复）
  │   │   └─ restart 无效 → docker compose up -d --no-recreate
  │   └─ docker compose up -d 报 validation error → 检查 compose YAML（见下方 pitfall）
  └─ NO → Firecrawl 正常
```

## ⚠️ compose YAML pitfall

`docker-compose.windows.yaml` 中 `services.api` 的 `ulimits:` 键值为空（锚点引用错误：`ulimits: *id002` 实际指向了 `networks`），导致 `docker compose up -d` 失败：
```
validating docker-compose.windows.yaml: services.api.ulimits must be a mapping
```

**修复**：删除 `api` 服务中空的 `ulimits:` 行。注意 `docker compose up -d`（不带 `-f`）会自动合并 `docker-compose.yaml` + `docker-compose.windows.yaml`，此时从基础文件继承正确的 ulimits 配置。

## 降级方案（Firecrawl 不可恢复时）

1. **配置文件降级**（Agent 自动执行）：
   ```bash
   cd ~/.hermes
   cp config.yaml config.yaml.bak
   sed -i 's/backend: firecrawl/backend: '\'''\''/g' config.yaml
   ```
   效果：Hermes 原生 `web_search` 恢复工作（DuckDuckGo 后端）。

2. **恢复 Firecrawl 后**（Agent 自动执行）：
   ```bash
   cd ~/.hermes
   sed -i 's/backend: '\'''\''/backend: firecrawl/g' config.yaml
   ```

## 用户手动恢复

1. 双击 `C:\Users\Aorus\tmp\firecrawl-selfhost\start-firecrawl.bat`
2. 等待提示 "Firecrawl 启动完成!"
3. Agent 会话中执行 `curl http://localhost:3002/health` 验证
