# agent-browser WSL 环境配置（已验证可用）

> 2026-05-28 验证通过。TUN VPN + WSL2 下 Chromium 可靠工作。

## 安装 Chromium

TUN 模式 VPN 开启时 Google 直连，但 puppeteer Node.js 下载器 TLS Reset。手动下载：

```bash
LATEST=$(curl -s "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2FLAST_CHANGE?alt=media")
curl -L -o /tmp/chromium.zip \
  "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F${LATEST}%2Fchrome-linux.zip?alt=media"
python3 -c "import zipfile,os; os.makedirs(os.path.expanduser('~/.chromium'),exist_ok=True); zipfile.ZipFile('/tmp/chromium.zip').extractall(os.path.expanduser('~/.chromium/'))"
chmod +x ~/.chromium/chrome-linux/chrome ~/.chromium/chrome-linux/chrome_crashpad_handler
```

## agent-browser 配置

```bash
mkdir -p ~/.agent-browser
cat > ~/.agent-browser/config.json << 'EOF'
{
  "executablePath": "/home/aorus/.chromium/chrome-linux/chrome",
  "args": "--no-sandbox,--disable-gpu,--no-proxy-server"
}
EOF
```

⚠️ args 是逗号分隔字符串，不是 JSON 数组。

## 致命陷阱：代理环境变量

WSL 中 `http_proxy`/`https_proxy` 指向 `127.0.0.1:7890`（IPv4），但代理只监听 `::7890`（IPv6）。Chromium 读到这些会导致 `ERR_CONNECTION_CLOSED`。

**每次使用 agent-browser 前必须执行：**
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY
```

## 验证

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY
~/.local/bin/agent-browser open "https://www.bing.com"
~/.local/bin/agent-browser get title
# → "Search - Microsoft Bing"
```

## 可用平台

| 平台 | 方式 | 状态 |
|------|------|:--:|
| Bing 通用 | agent-browser 直搜 + eval | ✅ 首选 |
| B站 | agent-browser 直搜 search.bilibili.com | ✅ |
| 微博/知乎/小红书/抖音/头条/公众号 | Bing `site:` 聚合 | ✅ |

## 子进程调用

agent-browser daemon 从 subprocess 调用不稳定。脚本中使用 **Chromium 直连 `--dump-dom`**：

```python
proc = subprocess.run(
    [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
     "--no-first-run", "--no-proxy-server", "--dump-dom", url],
    capture_output=True, text=True, timeout=30
)
```

比 agent-browser daemon 更可靠（已验证 97KB 搜索结果页）。
