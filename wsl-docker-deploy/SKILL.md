---
name: wsl-docker-deploy
description: >-
  WSL2 Docker Desktop 代理部署工作流。解决 Docker daemon 无法直接拉取镜像的问题：
  crane 代理拉取→docker load→docker compose up。适用于 ghcr.io/Docker Hub 等
  被墙或超时的 registry。触发：部署docker/自托管/self-host/docker pull超时/
  拉取镜像失败/Docker Desktop WSL。
version: 1.0.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [docker, wsl, proxy, deployment, self-host, crane]
    related_skills: [windows-troubleshooting-from-wsl]
---

# WSL Docker Desktop Proxy Deployment

当在 WSL2 中通过 Docker Desktop（Windows 端）部署容器化服务时，
Docker daemon 往往无法直接拉取 ghcr.io/Docker Hub 镜像，
即使配置了国内镜像源也经常超时。

## 三步工作流

### Step 1: 定位 Windows 宿主 IP

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}')
# 验证代理可达
HTTP_CODE=$(curl -s --proxy http://$WINDOWS_HOST:7890 --connect-timeout 5 https://www.google.com -o /dev/null -w "%{http_code}")
echo "代理状态码: $HTTP_CODE"
```

🔴 **CHECKPOINT**: `HTTP_CODE` 必须为 `200`（非 200 则代理不可用，检查 Windows 端代理软件是否运行、端口 7890 是否正确）。确认代理可达后再继续。

### Step 2: crane 代理拉取 → docker load

```bash
# 安装 crane（单二进制，无依赖）
curl -sL --proxy http://$WINDOWS_HOST:7890 \
  https://github.com/google/go-containerregistry/releases/latest/download/go-containerregistry_Linux_x86_64.tar.gz \
  -o /tmp/crane.tar.gz
tar xzf /tmp/crane.tar.gz -C /tmp/ crane && chmod +x /tmp/crane

# 拉取 + 加载（对每个需要的镜像重复）
export HTTP_PROXY=http://$WINDOWS_HOST:7890 HTTPS_PROXY=http://$WINDOWS_HOST:7890
/tmp/crane pull ghcr.io/owner/image:tag /tmp/out.tar
docker load -i /tmp/out.tar
# 验证镜像已加载
docker images | grep "ghcr.io/owner/image" | grep "tag"
```

🔴 **CHECKPOINT**: 确认 `docker images` 输出包含目标镜像且 tag 正确。若加载失败（exit code ≠ 0），检查 `/tmp` 磁盘空间（`df -h /tmp`）、crane 版本兼容性。所有镜像全部加载成功后再进入 Step 3。

### Step 3: docker compose up

docker-compose 需两处修改：

**A. 用预构建镜像，不编译源码：**
```yaml
services:
  api:
    image: ghcr.io/owner/image:latest   # ✅
    # build: apps/api                    # ❌ 注释掉
```

**B. 容器内代理指向 Windows 宿主：**
```env
PROXY_SERVER=http://host.docker.internal:7890
```

`host.docker.internal` 在 Docker Desktop + `extra_hosts: host-gateway` 下自动解析到 Windows 宿主 IP。

## WSL2 网络核心事实

| 事实 | 含义 |
|------|------|
| WSL2 和 Windows 是独立网络命名空间 | `127.0.0.1:7890` 从 WSL 不通 Windows |
| `ip route show default` 拿到的 IP | 就是 Windows 宿主网关地址 |
| Docker daemon 跑在 Windows 上 | WSL 的环境变量不影响 daemon |
| crane 走 WSL 的网络栈 | 不受 Docker daemon 网络限制 |

## Docker Desktop 可用性检测

在 WSL 中执行任何 `docker` 命令前，务必先验证 Docker Desktop 是否在 Windows 端运行：

```bash
# 快速检测
docker ps 2>/dev/null || echo "Docker Desktop 未运行或 WSL 集成未启用"
```

🛑 **STOP — 前置条件**：`docker ps` 必须成功执行（exit code 0）。若失败，所有后续 `docker` 命令均不可用。必须先启动 Docker Desktop（Windows 端），等待 10-15 秒挂载点恢复后重新检测，通过后再执行任何 docker 操作。

**症状**：`docker: command not found` 或 `/mnt/wsl/docker-desktop/cli-tools/...: No such file or directory`

**根因**：WSL 中的 `docker` 是符号链接 → `/mnt/wsl/docker-desktop/cli-tools/usr/bin/docker`，该挂载点仅在 Docker Desktop 运行且启用 WSL 集成时才存在。Docker Desktop 关闭后，挂载点消失，docker CLI 不可用，**所有容器同时退出**（exit code 255）。

**恢复**：启动 Docker Desktop（Windows 端）→ `docker start <容器名>` 恢复容器。

## 失败模式速查表

| 触发条件 | 症状 | 一线修复 | 仍失败则 |
|----------|------|----------|----------|
| `docker pull` 超时/EOF（被墙 registry） | `dial tcp: i/o timeout` / `EOF` | 换 crane 代理拉取 → `docker load`（按 Step 2） | 检查代理端口（默认 7890），确认 `HTTP_PROXY` 已 export |
| `docker ps` 返回 `command not found` | `docker: command not found` / 挂载点缺失 | 启动 Docker Desktop（Windows 端），等待 15 秒 | 检查 Docker Desktop Settings → Resources → WSL Integration → 当前发行版已勾选 |
| `curl --proxy` 返回非 200 | HTTP_CODE ≠ 200 | 确认 Windows 端代理软件（Clash/V2Ray）正在运行，端口 7890 监听 | 检查 Windows 防火墙是否拦截入站连接；尝试 `ping $WINDOWS_HOST` 验证 WSL→Windows 网络通 |
| `docker load` 失败 | `no space left on device` / `invalid tar` | `df -h /tmp` 检查空间；重下 crane 最新版 | 换路径（如 `/var/tmp`）存储 tar 文件 |
| `docker build` 第一步就 EOF/超时 | `EOF` / `context deadline exceeded` | 先 `docker pull <base-image>` 绕过 build metadata 测试 mirror | pull 也失败 → registry mirror 不可用，切 crane 路径预拉所有 base image 再 docker load 后 build |
| `docker pull` 在配置了多个 mirror 后仍报 EOF（非超时） | `Head ... EOF`（非 `i/o timeout`），`docker info` 显示多个 mirror | **移除 `daemon.json` 中的 `registry-mirrors` 字段**，仅靠 proxy 直连 Docker Hub。重启 Docker Desktop 后重试 | mirror 全失效是常见现象（USTC/163/百度同时挂），此时 proxy 直连反而可用。`daemon.json` 位置：WSL 下 `~/.docker/daemon.json`，Windows 原生 Docker Desktop 下 `C:\Users\<user>\.docker\daemon.json` |
| Docker Desktop 关闭后容器消失 | `docker ps` 无容器 | 启动 Docker Desktop → `docker start <容器名>` | 容器 exit code 255 表示被 Docker Desktop 关闭信号终止，`docker start` 即可恢复（数据在 volume 中不丢失） |

## ⛔ 反例与禁止

- ❌ 反复重试 `docker pull` — 超时不会自愈，换 crane（详见速查表）
- ❌ 用 `127.0.0.1` 当代理地址 — WSL2 不通
- ❌ 在 daemon.json 加 proxy 后不重启 Docker Desktop — 不生效
- ❌ 从源码 `build:` 而不是用 `image:` — 编译耗时且需要完整工具链
- ❌ compose 里有 `build:` 的 Dockerfile 不预拉 base image — `FROM postgres:17` 等也会走 daemon 拉取超时。用 crane 预拉所有 base image 后 docker load
- ❌ `docker build` 第一步 EOF/超时就放弃 — 先 `docker pull <base-image>` 测 mirror（详见速查表）
- ❌ Docker Desktop 关闭后以为 `docker start` 能恢复容器 — `docker` 命令本身不可用（详见速查表）

## 参考资源

### 本地参考
- `references/firecrawl-selfhost-recipe.md`

### 外部参考
- [crane 文档](https://github.com/google/go-containerregistry/blob/main/cmd/crane/README.md)
- [Docker Desktop WSL 集成](https://docs.docker.com/desktop/wsl/)

## 清理

```bash
rm -f /tmp/crane.tar.gz /tmp/crane /tmp/out*.tar
```
