---
name: opencli
description: OpenCLI — browser-based CLI for 59+ web platforms. Use for xiaohongshu/zhihu/weibo/bilibili etc. that normal browser tools cannot access (anti-bot sites). Requires Chrome + extension bridge setup. WSL2 verified working with portproxy.
tags: [opencli, browser, xiaohongshu, zhihu, weibo, bilibili, anti-bot, social-media]
category: social-media
version: 1.1.0
dependencies:
  commands: [node, npm, chrome]
---

# OpenCLI — 浏览器驱动的反爬站点 CLI

> **定位**：补位 Hermes browser 工具链盲区——小红书/知乎/微博等反爬严格、Hermes browser 无法访问。
> **原理**：Chrome CDP 驱动真实浏览器，复用登录态和指纹。
> **安装**：`npm install -g @jackwener/opencli`

## 核心差异化能力

| 平台 | Hermes browser | OpenCLI | 命令数 |
|------|:--:|:--:|:--:|
| 小红书 | ❌ IP风控 300012 | ✅ | 15 |
| 知乎 | ❌ 反爬 40362 | ✅ | 13 |
| 微博 | ❌ 强制登录跳转 | ✅ | 11 |
| B站 | 🟡 部分可用 | ✅ | 14 |

## 架构

```
opencli CLI → Daemon (WSL 127.0.0.1:19825)
       ↕ Python relay (WSL_IP:19826)
       ↕ portproxy v4tov4 (Windows 127.0.0.1:19825→WSL_IP:19826)
Chrome Extension ↔ Chrome CDP ([::1]:9222)
       ↕ portproxy v4tov6 (0.0.0.0:9222→[::1]:9222)
WSL curl → WIN_IP:9222
```

## WSL2 已验证配置（2026-06-01）

### 关键发现

1. **IP Helper 服务默认禁用**——portproxy 依赖它
2. **Chrome 只绑定 IPv6 `[::1]:9222`**——需 `v4tov6` 转发
3. **Daemon 只绑定 `127.0.0.1`**——需 TCP relay + 反向 portproxy
4. **Extension 需手动安装一次**——Chrome 安全策略禁止命令行加载

### Step 1 — 启用 IP Helper

```bash
/mnt/c/Windows/System32/sc.exe config iphlpsvc start=auto
/mnt/c/Windows/System32/sc.exe start iphlpsvc
```

### Step 2 — 防火墙

```bash
/mnt/c/Windows/System32/netsh.exe advfirewall firewall add rule name="Chrome CDP 9222" dir=in action=allow protocol=TCP localport=9222
```

### Step 3 — 端口转发

```bash
WIN_IP=$(ip route show default | awk '{print $3}')
WSL_IP=$(ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1)

# WSL→Windows: CDP (v4tov6)
/mnt/c/Windows/System32/netsh.exe interface portproxy add v4tov6 listenport=9222 listenaddress=0.0.0.0 connectport=9222 connectaddress=::1

# Windows→WSL: Daemon (v4tov4)
/mnt/c/Windows/System32/netsh.exe interface portproxy add v4tov4 listenport=19825 listenaddress=127.0.0.1 connectport=19826 connectaddress=${WSL_IP}

# 启动 Python TCP relay (后台)
python3 -c "
import socket,threading
L=('${WSL_IP}',19826);T=('127.0.0.1',19825)
def r(a,b):
 try:
  while 1:
   d=a.recv(4096)
   if not d:break
   b.sendall(d)
 except:pass
s=socket.socket();s.setsockopt(1,2,1);s.bind(L);s.listen(10)
while 1:
 c,_=s.accept();t=socket.socket();t.connect(T)
 threading.Thread(target=r,args=(c,t),daemon=1).start()
 threading.Thread(target=r,args=(t,c),daemon=1).start()
" &
```

### Step 4 — 启动 Chrome

```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command \
  "Start-Process 'C:\Program Files\Google\Chrome\Application\chrome.exe' \
   -ArgumentList '--remote-debugging-port=9222','--user-data-dir=C:\temp_chrome_debug5','--no-first-run','--no-default-browser-check','about:blank'"
```

### Step 5 — 手动安装 Extension

1. 下载：`curl -sLo /tmp/ext.zip https://github.com/jackwener/OpenCLI/releases/download/v1.8.1/opencli-extension-v1.0.17.zip`
2. 解压：`python3 -c "import zipfile;zipfile.ZipFile('/tmp/ext.zip').extractall('/mnt/c/temp_opencli_ext')"`
3. Chrome 中打开 `chrome://extensions` → 开发者模式 → 加载已解压 → 选 `C:\temp_opencli_ext`

### Step 6 — 验证

```bash
curl -s http://${WIN_IP}:9222/json/version | grep Chrome  # CDP ✅
opencli doctor  # 应显示 [OK] Extension
opencli zhihu hot -f json --limit 3  # 端到端测试
```

## 常用命令

```bash
# 小红书
opencli xiaohongshu search "贵州探洞" -f json
opencli xiaohongshu note --url "https://..." -f json

# 知乎
opencli zhihu hot -f json --limit 10
opencli zhihu search "AI Agent" -f json

# 微博
opencli weibo hot -f json
opencli weibo search "关键词" -f json

# B站
opencli bilibili hot -f json
opencli bilibili video --url "https://..." -f json
```

## 关键约束

1. **Chrome 真实浏览器**——不可 headless
2. **登录态**——`[cookie]` 命令需在 Chrome 中登录目标网站（知乎搜索、小红书等）
3. **Extension 手动安装**——一次性
4. **WSL IP 可能变化**——重启后需更新 portproxy/relay 中的 IP

## 显式不支持的平台

这些平台没有公开 web 接口，OpenCLI 无法访问，且无已知的第三方适配方案：

| 平台 | 原因 | 替代方案 |
|------|------|---------|
| **视频号** | 微信生态内完全封闭——无公开 web 端、无搜索收录（中小账号）、`channels.weixin.qq.com` 需扫码登录 SPA 后台 | 截图/录屏 → 视觉分析；或登录视频号助手导出数据 |

> 视频号审查唯一可行路径：用户截图关键帧发来 → `understand_image` 逐帧分析 → 汇总产出竞品审视文档。不要浪费时间尝试 web_search 或 browser_navigate。

## 已知适配器变更

| 命令 | 数据源 | 说明 |
|------|--------|------|
| `zhihu hot` | tophub.today | 知乎 API v3 改为强制登录(401)，切换至公开聚合器 |
| `zhihu search` | 知乎 API v4 | 需 Chrome 登录知乎后可用 |
| `weibo hot` | 微博 `/ajax/statuses/hot_band` | 偶发加载时序 404，重试即可 |

> ⚠️ **npm 升级会覆盖适配器修复**：修改在 `$(npm root -g)/@jackwener/opencli/clis/` 中的文件会在 `npm update -g` 时被覆盖。如需持久化，将修复后的适配器复制到 `~/.opencli/clis/<site>/<command>.js`（用户目录优先加载）。

## 参考文件

- `references/wsl2-cdp-debug.md` — WSL2 CDP 完整排障实录
- `references/adapter-debugging.md` — 适配器调试与修复方法论
