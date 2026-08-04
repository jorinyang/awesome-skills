# 大屏展示页 CSS 布局模式

## 1. 垂直居中 + 溢出滚动（关键）

**错误做法**（导致内容顶部裁切）：
```css
#main {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;  /* ❌ 长内容顶端不可达 */
}
```

**正确做法**（伪元素弹性占位）：
```css
#main {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  min-height: 0;  /* 必须！否则 flex 子元素无法收缩 */
  overflow-y: auto;
}
#main::before, #main::after {
  content: '';
  flex: 1;
  min-height: 0;  /* 内容溢出时缩为0，正常时均分空间居中 */
}
#card {
  width: 100%;
  max-width: 960px;
}
```

**原理**：`::before`/`::after` 伪元素各占 `flex:1` 空间，内容短时居中，内容长时 `min-height:0` 允许缩为 0，完整内容可滚动。

## 2. 响应式 clamp() 字号

**意义**：替代固定 px + 多个 media query，一行代码适配所有分辨率。

```css
.qtext { font-size: clamp(22px, 2.5vw, 38px); }  /* 1920px→34px, 1024px→25px */
.opt   { font-size: clamp(14px, 1.4vw, 22px); }  /* 1920px→20px, 1024px→16px */
#card  { max-width: clamp(600px, 70vw, 960px); }
```

## 3. 白底投影配色方案

```css
:root {
  --bg: #ffffff;
  --surface: #f8fafc;
  --border: #e2e8f0;
  --text: #1e293b;
  --text2: #64748b;
  --primary: #4f46e5;
  --accent-quick: #d97706;
  --accent-mediation: #db2777;
  --success: #16a34a;
}
```

## 4. `overflow: hidden` 陷阱

**不要用** `overflow: hidden` 在展示区域！题目文字长时选项底部被裁切。
**用** `overflow-y: auto` 允许滚动，配合上面的伪元素居中方案。

## 5. JS 变量/函数重名

```javascript
// ❌ 变量 sel 和函数 sel() 冲突，首次调用后 sel 被覆盖为字符串
var sel = null;
function sel(t, el) { sel = t; }

// ✅ 重命名变量避免冲突
var selType = null;
function sel(t, el) { selType = t; }
```
