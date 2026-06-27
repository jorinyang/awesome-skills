# agent-browser 实操手册

> 基于 2026-05-30 L1+L3 多引擎/多平台采集实战。agent-browser 0.27.0 + Chromium 150。

## 环境

```bash
AGENT_BROWSER=~/.local/bin/agent-browser    # v0.27.0
CHROMIUM=~/.chromium/chrome-linux/chrome     # v150
CONFIG=~/.agent-browser/config.json
```

config.json:
```json
{
  "executablePath": "/home/aorus/.chromium/chrome-linux/chrome",
  "args": "--no-sandbox,--disable-gpu,--no-proxy-server"
}
```

## 核心铁律

### 1. 代理变量必须 unset

agent-browser 使用 Chromium 直接联网，不能经过代理：

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY
```

不 unset 会导致连接挂起/超时。

### 2. JSON 输出需双重解析

agent-browser `eval` 返回的 stdout 是 **外层引号包裹的 JSON 字符串**：

```
raw: "[{\"title\":\"...\",\"url\":\"...\"}]"
     ↑ 外层是 JSON string，不是 array
```

Python 解析方式：

```python
import json
raw = proc.stdout.strip()
parsed = json.loads(raw)       # → str (去掉外层引号)
if isinstance(parsed, str):
    parsed = json.loads(parsed) # → list (真正的数组)
```

### 3. 渲染等待

| 平台 | sleep | 备注 |
|------|:--:|------|
| 百度 | 4s | DOM 稳定 |
| 夸克 | 5s | AI 摘要+搜索结果渲染 |
| B站 | 6s | 视频卡片 + 异步渲染 |
| 头条 | 5s | 热榜 + 搜索结果，需滚动 |

### 4. 礼貌间隔

多关键词搜索之间 `sleep 2`，避免触发反爬。

### 5. 并行调用陷阱

agent-browser 维护**单一浏览器会话**。并行 `open` 会互相覆盖页面状态，导致 `eval`/`snapshot` 作用在错误页面。**必须串行调用。**

## 平台选择器 & 提取策略

### 百度 (baidu.com) — L1

```javascript
// ★ 多选择器兜底 (2026-06-13): 百度 DOM 随版本变化，按优先级尝试
// 优先级: .result h3 a → .c-container h3 a → h3.c-title a → h3.t a → h3 a
(() => {
  const sel = ['.result h3 a', '.c-container h3 a', 'h3.c-title a', 'h3.t a', 'h3 a'];
  for (const s of sel) {
    const els = document.querySelectorAll(s);
    if (els.length) return JSON.stringify(Array.from(els).slice(0, 8).map(a => ({
      title: a.textContent.trim(), url: a.href
    })));
  }
  return '[]';
})()
```

URL 为百度跳转链接（`baidu.com/link?url=...`），非真实目标 URL。

噪音过滤：`精选笔记` `百度图片` `百度百科` `买东西逛淘宝`、单字+括号标题。

**验证码绕过**：`open` 后先检测 `window.location.href` 是否跳转到 `wappass.baidu.com`，若是则直接返回空（不浪费重试时间）。

### 夸克 (quark.cn) — L1

```javascript
// 搜索结果 — 夸克是 AI 搜索，结果在 article 标签
document.querySelectorAll('article a[href]')
```

URL 为真实目标链接（非跳转）。同 URL 多次出现需去重。噪音：空标题、`X小时前`、`携程旅行`。

### B站 (bilibili.com) — L3

```javascript
// 视频卡片 — 提取标题/URL/UP主/元数据
document.querySelectorAll('.bili-video-card')
// 子元素:
//   a                          → href = BV号视频URL
//   .bili-video-card__info--tit    → 视频标题
//   .bili-video-card__info--author → UP主名
//   .bili-video-card__info--meta   → 播放/时长
```

搜索URL: `https://search.bilibili.com/all?keyword={query}&order=pubdate`

**关键:** `sleep 6` 以上，B站视频卡片异步渲染较慢。`order=pubdate` 按最新发布排序以获取时效内容。

### 头条 (toutiao.com) — L3 🆕

```javascript
// 搜索结果 — 需先 scroll 到内容区，再用关键字筛选
// 头条页面结构: 热榜(上) → 搜索过滤器 → 视频结果 → 资讯结果(下)
document.querySelectorAll('a')
  .filter(a => a.textContent.includes('贵州') || a.textContent.includes('探洞'))
// URL 格式: sou.toutiao.com/search/jump?url=<encoded_real_url>
// 需要双重 URL decode 才能拿到 toutiao.com/article/... 真链
```

搜索URL: `https://so.toutiao.com/search?dvpf=pc&source=input&keyword={query}`

**关键:** 搜索结果在热榜下方，需 `agent-browser scroll down 800` 后才能看到。URL 经过 `sou.toutiao.com/search/jump?url=...` 跳转封装，需 Python 端解码。

## 平台兼容性矩阵

| 平台 | 状态 | 用途 | 反爬类型 | 绕过方法 |
|------|:--:|------|------|------|
| **百度** | ⚠️ 间歇验证码 | L1 通用搜索 | 验证码重定向 (wappass.baidu.com) | 检测+单次跳过 → 夸克兜底 |
| **夸克** | ✅ | L1 AI搜索 | 偶发验证码 | 间隔≥2s |
| **B站** | ✅ | L3 视频 | 无 | — |
| **头条** | ✅ 🆕 | L3 资讯+视频 | 无 | 需scroll+decode URL |
| 微博 | ❌ | — | 登录墙 | CDP webdriver spoof 无效 |
| 知乎 | ❌ | — | 40362(页面前侦测) | CDP注入太晚 |
| 小红书 | ❌ | — | IP风控300012 | 需住宅代理 |
| 搜狗微信 | ❌ | — | 反爬重定向 | — |
| 8264 | ❌ | — | 503/CDP超时 | 已从L2退役 |

### 百度验证码 (2026-06-13 发现) ★

百度会对 headless Chrome 触发验证码重定向（`wappass.baidu.com`），导致搜索结果提取为 0。**这是会话级别的拦截**——首个关键词触发后，后续全部被拦。

**对策**：`search_baidu()` 检测 `window.location.href` 是否含 `wappass.baidu.com`，命中则跳过当前关键词（重试无意义）。夸克作为主力兜底引擎。

### CDP anti-detection 限制

`Object.defineProperty(navigator,"webdriver",{get:()=>false})` 注入对知乎/微博无效——这些平台在页面加载**前**就完成侦测。agent-browser 的 `open` 命令=导航+页面加载原子操作，无法在加载前注入脚本。这是 headless Chromium 的固有限制。

## 端到端耗时

| 阶段 | L1单引擎 | L3单平台 | 全量 L1+L3 |
|------|:--:|:--:|:--:|
| 单关键词搜索 | 6-7s | 8-11s | — |
| 关键词×引擎数 | ~80s (10kw×2) | ~55s (6kw) | ~135s |
| lark-cli 推送 | — | — | ~2min (1.5s/条) |
| **完整一轮** | — | — | **~4.5min** |

## lark-cli 推送

```bash
lark-cli docs +create \
  --wiki-node "EAMYw1CPoipVWtkObbtcR2oDnNc" \
  --title "文档标题" \
  --markdown "**通道:** L1 | **来源:** baidu\n\n**原文链接:** https://..." \
  --as bot
```

- `--wiki-node` 和 `--wiki-space` **互斥**，只用 `--wiki-node`
- 限流：连续创建需间隔 ≥1.5s
- bot 创建后不会自动授权当前用户（不影响访问）

## 长期运行维护 ★ (2026-06-13 发现)

### Chrome 进程僵死问题

agent-browser 的 headless Chrome 进程连续运行 10+ 天后会逐渐僵死：所有 `open`/`eval` 调用均超时。

**诊断**：
```bash
# 进程 uptime 是首要指标
ps aux | grep "agent-browser$"
# 健康探测
agent-browser eval "1+1"  # 应返回 "2"（裸值，非 JSON 字符串）
```

**自动修复**（已嵌入 `l3_cron.sh`）：
```bash
# 采集前健康检查，失败则自动重启
RESULT=$(timeout 10 agent-browser eval "1+1" 2>&1)
if [ "$RESULT" != "2" ]; then
    pkill -f agent-browser
    pkill -f agent-browser-chrome
    sleep 3
    agent-browser &
    sleep 5
fi
```

**手动恢复**：
```bash
pkill -f agent-browser; pkill -f agent-browser-chrome; sleep 3
agent-browser &
sleep 5
agent-browser eval "1+1"  # 验证
```

**注意**：可能存在多 agent-browser 实例同时运行（端口冲突），清理时需全部 kill。
