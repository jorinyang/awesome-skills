# Docker 工具安装故障排查模式

> 吸收自多次独立安装实践（ShadowBroker 等），记录 Docker Desktop Windows 上的常见陷阱和已验证的绕过方案。

## 1. 镜像源全部失效 → 代理直连

**症状**：`docker pull` / `docker compose build` 在 `FROM` 阶段报 EOF 或 TLS handshake timeout，所有 registry-mirrors 均不可达。

**已验证的绕过方案**：

```bash
# Step 1: 从 daemon.json 移除失效镜像源
# 编辑 %USERPROFILE%\.docker\daemon.json，删除 registry-mirrors 数组
# 重启 Docker Desktop

# Step 2: 预拉取基础镜像（客户端 env var 对 pull 有效）
export HTTP_PROXY=http://127.0.0.1:7890 HTTPS_PROXY=http://127.0.0.1:7890
docker pull python:3.11-slim-bookworm
docker pull rust:1.88-slim-bookworm

# Step 3: 在 Dockerfile 中注入代理环境变量（build 容器内部用 host.docker.internal）
sed -i '/^FROM/a ENV HTTP_PROXY=http://host.docker.internal:7890\nENV HTTPS_PROXY=http://host.docker.internal:7890' Dockerfile
# 对每个 FROM stage 重复

# Step 4: 构建
docker compose build backend
```

**原理**：
- `docker pull` 走客户端环境的代理变量 → 基础镜像可拉取
- `docker build` 的 RUN/ADD 命令在容器内执行，127.0.0.1 指向容器自身 → 需用 `host.docker.internal`
- `daemon.json` 的 `proxies` 配置在 Docker Desktop Windows 上**不生效** → 必须走 Dockerfile 注入

## 2. Admin Key 长度要求

**症状**：设置 `ADMIN_KEY=mykey` 后容器启动失败，日志显示 `_validate_admin_startup` → `SystemExit: 1`。

**原因**：ShadowBroker（及类似工具）要求 admin key ≥ 32 字符，短 key 会被拒绝。

```bash
# 生成符合要求的 key
python3 -c "import secrets; print(secrets.token_hex(32))"  # 64 字符 hex
echo "ADMIN_KEY=<generated>" >> .env
echo "MESH_DEBUG_MODE=true" >> .env  # 调试模式下短 key 会被警告但不会拒绝
docker compose up -d --force-recreate backend
```

## 3. OpenClaw HMAC 客户端适配陷阱

**症状**：HMAC 客户端调用 `GET /api/ai/channel/status` 返回 403，但 `POST /api/ai/channel/command` 正常。

**原因**：不同端点的认证依赖不同：
- `channel/status` → `require_local_operator`（只认 loopback IP / admin key，不认 HMAC）
- `channel/command` / `channel/batch` → `require_openclaw_or_local`（认 HMAC + loopback + admin key）

**修复**：HMAC 模式下用 `send_command("channel_status")` 替代直接 GET：

```python
async def channel_status(self):
    if self._hmac_secret:
        resp = await self.send_command("channel_status", {})
        inner = resp.get("result", {})
        if isinstance(inner, dict) and inner.get("ok"):
            return {"ok": True, "tier": resp.get("tier", 1), "transport": "http+hmac"}
        # Fallback
        resp2 = await self.send_command("get_summary", {"compact": True})
        return {"ok": bool(resp2.get("ok")), "tier": resp2.get("tier"),
                "transport": "http+hmac", "probe": "get_summary"}
```

## 4. GitHub Release 下载慢 / 国内加速

**症状**：`curl` 下载 GitHub Release 附件（如 `.exe`、`.dmg`）速度极慢（<50KB/s），或超时。

**已验证的绕过方案**：

```bash
# 方案 A：通过本地代理直连（最快，如果代理已运行）
curl -L -o output.exe \
  --proxy http://127.0.0.1:7890 \
  --connect-timeout 30 --max-time 1200 \
  "https://github.com/{owner}/{repo}/releases/download/{tag}/{asset}"

# 方案 B：ghproxy 镜像（无需代理，但速度不稳定）
curl -L -o output.exe \
  "https://ghproxy.net/https://github.com/{owner}/{repo}/releases/download/{tag}/{asset}"
```

> **优先级**：代理可达时方案 A 最优（本 session 实测 376MB 14s 完成 vs ghproxy <30KB/s）。

## 5. Windows Desktop GUI 安装器限制

**症状**：`.exe` 安装器已下载，但 `start` / `cmd //c` 启动后卡住不安装。进程存在但无安装产物。

**根因分析**（三层）：
1. **会话隔离**：Hermes 终端运行在 SYSTEM Session 0，用户桌面在 Session ≥1。`start` 启动的子进程留在 Session 0，无法在用户会话中创建可见窗口。
2. **UAC 安全桌面**：安装器需要管理员权限时会弹出 UAC 安全桌面弹窗，该弹窗在隔离的安全桌面中，任何自动化工具（包括 cua-driver）都无法与之交互。
3. **安装器 GUI 交互**：即使绕过 UAC（如免管理员安装），安装器本身仍是 GUI 向导，需要在用户会话中有可见窗口才能点击"下一步"。

**可做的事 vs 不能做的事**：
- ✅ 下载安装包到用户可访问路径
- ✅ 预配置环境（创建目录、写配置文件）
- ❌ 点击 UAC 弹窗
- ❌ 在用户桌面创建可见窗口并进行 GUI 交互

**SOP**：下载完成后告知用户安装包路径，让用户手动双击完成安装，再回到自动化流程做后续配置。

---

## 6. Docker Desktop 管道权限错误

**症状**：重启 Docker Desktop 报 "Cannot start server... Access is denied. open \\.\pipe\dockerBackendApiServer: Access is denied."

**原因**：残留的 Docker Desktop.exe / com.docker.backend.exe 进程占用命名管道。

```bash
# 强制清理所有残留进程
taskkill //F //IM "Docker Desktop.exe" 2>/dev/null
taskkill //F //IM "com.docker.backend.exe" 2>/dev/null
sleep 2

# 重启服务
net stop com.docker.service && net start com.docker.service
```

服务启动后，从开始菜单启动 Docker Desktop 即可重连。

## 7. Docker Hub 被墙——终极降级策略

**症状**：即使 `HTTP_PROXY` 环境变量 + `daemon.json` proxy 都配了，`docker pull hello-world` 仍然返回 `EOF` 或 `TLS handshake timeout`。代理本身可达（`curl` 通过代理正常），Docker 就是不行。

**根因**：Docker Desktop Windows 的 WSL2 后端运行在独立 VM 中，其网络栈与 Windows 宿主机的代理不完全兼容。某些网络环境下（如中国大陆），即使宿主代理正常，WSL2 内的 Docker daemon 也无法通过代理访问 Docker Hub。

**判断信号**：`curl --proxy http://127.0.0.1:7890 https://registry-1.docker.io/v2/` 返回 200/401（可达），但 `docker pull` 仍然 EOF → 立即停止折腾 Docker。

**终极方案——跳过 Docker**：
1. 检查仓库是否提供**非 Docker 部署方式**：裸金属（BARE_METAL.md）、桌面安装器（Release 页 .exe/.dmg）、源码构建
2. 对桌面安装器：下载到用户路径 → 告知用户手动安装
3. 对源码项目：`git clone` + 本地开发命令（`yarn dev`/`npm start`/`pip install`）
4. 都不行 → 仅做代码层评估（`git clone --depth 1` + 读源码），不部署

> **记住**：放弃 Docker 不是失败，是成本最优决策。一个 300MB 的桌面安装器通过代理 14 秒就能下完，比调 Docker 网络快得多。
