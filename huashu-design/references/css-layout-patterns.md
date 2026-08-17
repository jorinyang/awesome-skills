# CSS Flexbox 垂直居中 + Overflow 滚动

## 致命问题：overflow:hidden 裁切内容

`overflow: hidden` 是选项消失的 #1 根因。当题目文字长、选项多、加上答案区，整个卡片高度超出 `.main-area` 可视范围时，**底部选项（尤其是 D）和答案区直接被裁掉**。

```
❌ overflow: hidden  → 长题目底部裁切
✅ overflow-y: auto  → 长题目可通过滚动查看全部内容
```

**诊断方法**：如果用户报告"有些题选项正常，有些题缺选项"，几乎100%是 overflow 问题——短题目刚好能显示完整，长题目被裁。

## 问题：flex centering + overflow 的经典 bug

`display: flex; align-items: center; justify-content: center; overflow-y: auto` 组合会导致内容顶部和底部被裁剪——这是 CSS flexbox 的经典 bug。

当子元素高度超过父容器时，`justify-content: center` 将子元素推到垂直中心，但其上半部分落在滚动区域上方（不可达），下半部分被裁剪。

JS 动态计算 `margin-top` 可以修复，但页面缩放（Ctrl+/-）后不重新计算，导航栏等固定元素会被挤出视口。

## 最终方案：::before/::after 伪元素

```css
#main {
  display: flex;
  flex-direction: column;
  align-items: center;      /* 水平居中 */
  flex: 1;
  min-height: 0;            /* 关键：允许 flex 子元素收缩 */
  overflow-y: auto;         /* 内容溢出时滚动 */
  overflow-x: hidden;
  padding: 0 24px;
}
#main::before,
#main::after {
  content: '';
  flex: 1;                  /* 上下伪元素平分剩余空间 → 居中 */
  min-height: 0;            /* 关键：溢出时收缩到0 */
}
#card {
  max-width: 960px;
  width: 100%;
  text-align: center;
}
```

**原理**：
- 内容短时：`::before` 和 `::after` 各占 `flex: 1`，平分空间，`#card` 居中
- 内容长时：`min-height: 0` 允许伪元素收缩到 0，`#card` 从顶部开始可完整滚动
- 缩放时：浏览器自动重新计算 flex 分配，无需 JS

**错误做法**（会导致裁剪）：
- `justify-content: center` + `overflow: auto`
- `align-items: center` 作垂直居中 + `overflow: auto`
- JS `marginTop` 计算（缩放后失效）

## 补充：JavaScript 变量/函数重名

```javascript
// ❌ 错误：var 和 function 同名
var sel = null;
function sel(t, el) { sel = t; }
// → sel() 执行后 sel 变成字符串 'required'，第二次调用 sel() 报 TypeError

// ✅ 正确：用不同名称
var selType = null;
function sel(t, el) { selType = t; }
```

## 响应式字体：clamp() 替代硬编码 + 媒体查询

硬编码 `font-size: 34px` + 多个 `@media` 断点无法处理连续缩放和 4K 屏。用 `clamp()` 一行替代：

```css
.qtext { font-size: clamp(22px, 2.5vw, 38px); }  /* 题目 */
.opt   { font-size: clamp(14px, 1.4vw, 22px); }  /* 选项 */
```

**原理**：`clamp(MIN, PREFERRED, MAX)` — 三个值自动适配：
- 大屏 4K：取 MAX（38px / 22px）
- 普通 1080p：取 PREFERRED 比例（~34px / ~20px）  
- 投影 720p：向 MIN 方向缩减（~25px / ~15px）
- UI 缩放 150%：等价缩小视口，字体等比下沉

**适用**：padding、margin、gap、border-radius 等所有尺寸属性。

## Supabase JS 客户端 JSONB 陷阱

```javascript
// ❌ 不设 limit — 可能分页截断
db.from('questions').select('*')           // 某些版本默认 100 行

// ❌ JSONB options 可能是字符串而非数组
q.options.length  // TypeError: options is string "[\"A.xx\",...]"

// ✅ 正确用法
db.from('questions').select('*').limit(1000)  // 显式设大 limit

// ✅ 防御归一化
function normOpts(opts) {
  if (Array.isArray(opts)) return opts;
  if (typeof opts === 'string') {
    try { return JSON.parse(opts); } catch(e) { return null; }
  }
  return null;
}
```

**注意**：题目数量不大时（<1000），用原生 `fetch()` 直调 REST API 比 supabase-js 更可控，完全避开 JSONB 序列化差异。
