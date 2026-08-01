# 票务验证 SPA — 多步查询到票根保存

## 场景

用户扫码 → 输入姓名+手机号/订单号 → 查询票根 → 多票时选择 → 显示票根 → 保存截图。

## 三步骤 SPA 架构

```
Step 1 (search) → Step 2 (select, 多票时) → Step 3 (stub + 保存)
```

### 步骤切换

```css
.step { display: none; }
.step.active { display: flex; flex-direction: column; }
```

```javascript
function showStep(name) {
  document.querySelectorAll('.step').forEach(s => s.classList.remove('active'))
  document.getElementById('step-' + name).classList.add('active')
}
```

### 单票直跳 vs 多票选择

**重要更新**：查询后应只显示当前日期及未来的有效票。已过期（`shows.date < today`）和已取消的票不应展示。

```javascript
const today = new Date().toISOString().slice(0, 10)
// 仅有效 + 未过期
const valid = data.filter(b => b.status === 'active' && b.seats?.shows?.date >= today)
if (valid.length === 0) { toast('暂无有效票根'); return }
if (valid.length === 1) { renderStub(valid[0]); showStep('stub') }
else { shownTickets = valid; renderSelect(valid); showStep('select') }
```

**旧版逻辑（已废弃）**：不再同时展示「有效+无效」混合列表，也不通过 `data.length` 判断是否有其它票。

## 截图保存（html2canvas + 微信长按保存）

**坑**：直接用 `a.click()` 下载文件在微信内置浏览器中不工作。微信必须「长按图片 → 保存到手机」。

**正确流程**：
1. html2canvas 只捕获票根卡片（`stub-card`），**不包含**下方的保存按钮
2. 将 canvas 转为 blob → `URL.createObjectURL()` → 插入 `<img>` 到 `.save-area`
3. 显示引导文字「长按上方图片即可保存到手机」

```javascript
async function saveStub() {
  const el = document.getElementById('stub-card')  // 只截卡片，不含按钮
  const canvas = await html2canvas(el, { backgroundColor: '#f5f5f5', scale: 2 })
  const blob = await new Promise(r => canvas.toBlob(r, 'image/png'))
  const url = URL.createObjectURL(blob)
  // 替换按钮区域为图片
  document.querySelector('.save-area').innerHTML =
    `<img src="${url}" style="width:100%;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,.15)">
     <p class="save-hint">👆 长按上方图片即可保存到手机</p>`
}
```

**HTML 结构**：保存按钮必须在 `stub-card` 之外，否则会被截进图里：

```html
<div class="stub-card" id="stub-card">
  <!-- 只有票根内容：姓名/场次/区/排/座/状态/警告 -->
</div>
<div class="save-area">
  <button onclick="saveStub()">📸 生成图片后长按保存</button>
  <p class="save-hint">微信扫码用户：点击按钮后长按图片即可保存</p>
</div>
```

## 票根卡片设计

移动端优先，使用 `100dvh` 替代 `100vh`（避免 iOS Safari 底部工具栏遮挡）：

```css
body { min-height: 100dvh; -webkit-tap-highlight-color: transparent; }
.stub-card { border-radius: 18px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,.12); }
.stub-top { background: linear-gradient(135deg, #c41e3a, #8b1028); color: #fff; padding: 24px 20px; }
```

### 响应式放大（移动端→大屏）

默认尺寸紧凑，420px 以上放大关键元素：

```css
.stub-seat .seat { font-size: 2.6rem; }           /* 移动端 */
@media (min-width: 420px) {
  .stub-seat .seat { font-size: 3.2rem; }         /* 大屏放大 */
  .stub-card { max-width: 420px; }
}
```

### 保存区域样式

保存按钮和引导文字在卡片外部，不被截图捕获：

```css
.save-area { padding: 16px 22px 22px; text-align: center; }
.save-hint { font-size: .7rem; color: var(--mut); margin-top: 10px; }
```

## 订单号生成

订座时生成短可读订单号：

```javascript
const orderNo = 'FK' + Date.now().toString(36).toUpperCase() + Math.random().toString(36).slice(2, 6).toUpperCase()
// 例: FKMB7NQ8XK4A
```

## 查询接口

同时支持手机号和订单号查询：

```javascript
// bookings 查询：customer_name 精确匹配 + (手机号 OR 订单号)
filters: `customer_name=eq.${name}&or=(customer_phone.eq.${input},order_number.eq.${input})`
```

## 安全提醒

有效票根页面必须显示明确警告：

```html
<div class="warn">⚠️ 请勿将此页面分享给他人</div>
```

无效/已退票不显示保存按钮和入场提示。

## 常见 JS 语法错误

### 模板字面量中多余的闭合括号

当 `renderStub` 用 `innerHTML = \`...\`` 生成 HTML，且内部包含条件表达式 `${active?'...':''}` 时，容易在字符串末尾多写一个 `}` 闭合函数体外的括号，导致后续函数（如 `saveStub`）失效。

**错误示例**：
```javascript
function renderStub(b) {
  document.getElementById('el').innerHTML =
  `${active?`<div>...</div>`:''}`
}  // ← renderStub 的 }
}  // ← 多余的 }，导致后续 saveStub 语法错误

async function saveStub() { ... }  // 此函数永不执行！
```

**修复**：检查 `innerHTML = \`...\`` 赋值行之后只有一个 `}`（来自 renderStub 函数体闭合），没有多余的闭合符。

### 微信浏览器 ES6 模板字符串不兼容

**症状**：Chrome DevTools 中一切正常，但微信扫码打开后按钮点击无响应、页面无任何 JS 执行。

**原因**：微信内置浏览器（Android WebView）可能不支持 ES6 模板字面量 `` `${expr}` ``。整个 `<script>` 块解析失败 = 所有函数全部不可用。

**修复**：**全部改用普通字符串拼接** `'text ' + var + ' more'`，不使用任何模板字面量。同时避免箭头函数、`const`/`let`（降级为 `function`/`var`）。**微信环境下必须实际扫码测试，不能仅靠 Chrome DevTools**。

### html2canvas 阻塞页面加载

**症状**：页面白屏，特别是在微信扫码环境下。

**原因**：html2canvas CDN `<script src>` 放在 `<head>` 中会阻塞 DOM 解析。jsDelivr 在国内/微信环境下可能加载极慢或被墙。

**修复**：**html2canvas 改为按需动态加载**，不在页面初始 HTML 中引入：

```javascript
async function saveStub() {
  // 运行时按需加载 html2canvas
  if (typeof html2canvas === 'undefined') {
    var s = document.createElement('script')
    s.src = 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js'
    await new Promise(function(resolve, reject) { s.onload = resolve; s.onerror = reject; document.head.appendChild(s) })
  }
  // 然后正常使用 html2canvas...
}
```

## 按钮反馈模式（重要用户偏好）

**规则**：按钮在操作中**永远不禁用**（`disabled` 不改）。仅通过 `textContent` 变化给用户反馈：

```javascript
// ✅ 正确
btn.textContent = '查询中...'
await doWork()
btn.textContent = '查 询'

// ❌ 禁止
btn.disabled = true  // 用户会困惑，不知道是否在处理中
```

这是用户的明确偏好——按钮应始终可点击，让用户有控制感。
