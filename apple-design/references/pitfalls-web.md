# Web 实现常见坑与还原方案

## 1. CSS Flex 居中 + Overflow 裁剪 bug

**现象**：`align-items: center` + `overflow: auto` 时，内容过长被从顶部裁切，不可滚动到。

**根因**：Flex 居中时溢出的顶部内容被推出视口外，且不可访问。

**修复**：用 `::before`/`::after` 伪元素代替 `justify-content: center`：

```css
.container{
  display:flex; flex-direction:column; align-items:center;
  flex:1; min-height:0; overflow-y:auto;
}
.container::before, .container::after{content:''; flex:1; min-height:0}
```

伪元素作为弹性占位符，内容短时自动居中，内容长时缩为 0 可滚动。`min-height:0` 是关键——否则 flex 子元素无法收缩。

## 2. `clamp()` 大屏适配

**需求**：同一页面在 720p 投影仪和 4K 屏幕都要正常显示。

**方案**：所有字号/间距/宽度用 `clamp(最小值, 视口比例, 最大值)`：

```css
.qtext{font-size:clamp(22px,2.5vw,38px)}   /* 题目：22-38px */
.opt{font-size:clamp(14px,1.4vw,22px)}     /* 选项：14-22px */
```

1080p 取中值，4K 取上限，720p 取下限，缩放自然。

## 3. 毛玻璃导航 Auto-hide

```css
#topbar{opacity:0; transform:translateY(-100%); transition:opacity .35s,transform .35s}
#topbar:hover{opacity:1; transform:translateY(0)}
/* 触发区：透明固定层，不占布局流 */
.top-zone{position:fixed; top:0; left:0; right:0; height:44px; z-index:21}
```

## 4. Web Audio 嘀嘀声（无外部文件）

```js
function beep(n){
  var ctx=new AudioContext();
  for(var k=0;k<n;k++) setTimeout(function(){
    var o=ctx.createOscillator(),g=ctx.createGain();
    o.type='square'; o.frequency.value=880; g.gain.value=.08;
    o.connect(g); g.connect(ctx.destination);
    o.start(); o.stop(ctx.currentTime+.12);
  },k*300);
}
```

## 5. 卡片转场弹簧动画

```css
@keyframes cardIn{
  from{opacity:0; transform:translateY(24px) scale(.98)}
  to{opacity:1; transform:translateY(0) scale(1)}
}
.card-anim{animation:cardIn .45s cubic-bezier(0.32,0.72,0,1) both}
```
重新触发：`el.classList.remove('card-anim'); void el.offsetWidth; el.classList.add('card-anim')`

## 6. Supabase JSONB 字段防御

Supabase JS 客户端 v2 中，JSONB 字段有时返回 JSON 字符串而非数组：

```js
function normalizeOptions(opts){
  if(Array.isArray(opts)&&opts.length>0) return opts;
  if(typeof opts==='string'){try{return JSON.parse(opts)}catch(e){}}
  return null;
}
```

## 8. CSS `::before` 多层级伪元素继承坑

**场景**：用 `::before` 伪元素实现自定义列表符号（Apple风格三级圆点），多层嵌套 `<ul>` 时符号不显示。

**根因链**（三个独立问题，常同时出现）：

1. **`content` 不继承**：`::before` 伪元素的 `content` 属性不从祖先元素的 `::before` 继承。每个嵌套层级必须显式设置 `content: ''`，否则默认 `none`，伪元素不生成。

2. **`position: relative` 不继承**：`position` 不是继承属性。父级 `li` 的 `position: relative` 不传递给子级 `li`——必须每层都设，否则 `::before` 的绝对定位参考系错误。

3. **`position: absolute` + `left`/`top` 不继承**：每层 `::before` 需要独立的定位属性。

**正确写法**：

```css
ul { list-style: none; padding-left: 0; }

/* 一级：实心蓝点 */
ul > li {
  position: relative;
  padding-left: 1.5rem;
}
ul > li::before {
  content: '';              /* 必须 */
  position: absolute;       /* 必须 */
  left: 0; top: 0.6em;    /* 必须 */
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--blue);
}

/* 二级：空心圆环 — 每个属性都要重新声明 */
ul > li > ul > li {
  position: relative;       /* 不继承 */
}
ul > li > ul > li::before {
  content: '';              /* 不继承 */
  position: absolute;       /* 不继承 */
  left: 0; top: 0.55em;
  width: 5px; height: 5px;
  border-radius: 50%;
  background: transparent;
  border: 1.5px solid var(--blue);
}
```

**检查清单**（`::before` 符号不显示时）：
- [ ] 每层 `li` 有 `position: relative`？
- [ ] 每层 `::before` 有 `content: ''`？
- [ ] 每层 `::before` 有 `position: absolute` + `left` + `top`？
- [ ] 父级 `ul` 的 `list-style: none`？

## 9. OSS 缓存爆破

```javascript
// 部署时设 no-cache
bucket.put_object_from_file(key, path, {
  headers:{'Cache-Control':'no-cache, no-store, must-revalidate, max-age=0'}
});

// 请求时加时间戳
fetch(url+'?t='+Date.now())
```
