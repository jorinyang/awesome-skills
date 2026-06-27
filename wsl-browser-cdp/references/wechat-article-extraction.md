# 微信文章提取

## 问题

`mp.weixin.qq.com` 文章页面有以下特点：
- `browser_navigate` 首次加载经常**超时**（微信服务器反爬/验证）
- 即使加载成功，`browser_snapshot(full=true)` 也**截断**长文（~2000 行限制）
- 文章正文在 `<div id="js_content">` 容器中

## 正确流程

### Step 1: 确保 CDP 已连接

```bash
# 按 wsl-browser-cdp 主文档启动 Windows Chrome + CDP
hermes config set browser.cdp_url "http://172.24.48.1:9222"
```

### Step 2: navigate + 等待加载

```bash
browser_navigate(url="https://mp.weixin.qq.com/s/XXXXX")
```

首次可能超时 — 重试一次通常成功。

### Step 3: 用 browser_console 直接提取全文

```js
// 方法 A: 微信文章专属（最精准）
document.querySelector('#js_content') ? 
  document.querySelector('#js_content').innerText : 
  document.body.innerText
```

`browser_console(expression=...)` 返回的文本**不会被截断**，不受 `browser_snapshot` 的行数限制。

### Step 4: 不回退到 browser_snapshot(full=true)

`browser_snapshot` 的截断是设计行为（防止 token 溢出），不适合长文章。

## 已知局限

- 微信文章可能包含**付费内容**或**需要登录**的部分 — 这些无法通过 CDP 获取
- 部分文章的图片/图表在 innerText 中不可见 — 如需图片内容，需额外调用 `browser_get_images` + `vision`
