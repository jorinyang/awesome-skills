---
name: web-spa
description: Web SPA 开发模式与陷阱——全屏演示/答题类单页应用的最佳实践。覆盖 CSS 居中+溢出的经典坑、数据加载方案选择、JS 作用域陷阱、选项格式化管道。
version: 1.0.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [frontend, spa, css, layout, js]
triggers:
  - "做个web SPA"
  - "单页应用"
  - "大屏展示页"
  - "全屏答题"
  - "前端页面开发"
  - "做问答系统"
  - "选项不显示"
  - "CSS 居中问题"
  - "flex overflow bug"
---

# web-spa — Web SPA 开发模式与陷阱

## 1. 数据加载方案决策

| 方案 | 适用 | 坑 |
|------|------|-----|
| Supabase JS 客户端 `@supabase/supabase-js@2` | 需要实时写入 | `.select('*')` 不加 `.limit(1000)` 可能分页截断；JSONB 字段偶发返回字符串而非数组 |
| Supabase REST API `fetch()` 直调 | 只读、高性能 | 无自动重试，需手动 `limit=1000` |
| OSS 预生成 JSON → fetch | **最可靠**，零运行时风险 | 需 cron 定时同步，非实时 |

**推荐**：答题/展示类 SPA → OSS JSON，admin 操作通过 cron 自动同步。

**Supabase JS 客户端正确用法**（当必须使用时）：
```javascript
// ① 显式 limit(1000) 防止分页截断
db.from('questions').select('*').order('id').limit(1000)

// ② 防御性 JSONB 归一化
function normalizeOptions(opts) {
  if (Array.isArray(opts) && opts.length > 0) return opts;
  if (typeof opts === 'string') {
    try { return JSON.parse(opts); } catch(e) {}
  }
  return null;
}
```

## 2. CSS 全屏居中 + 滚动的经典坑

### ❌ 绝对不能用的组合
```css
.container {
  display: flex;
  align-items: center;      /* ← 居中 + overflow = bug */
  justify-content: center;
  overflow-y: auto;
}
```
**症状**：内容超出视口时，顶部被裁切不可滚动，底部选项消失。

### ✅ JS 动态居中（最可靠）
```css
#main { flex: 1; overflow-y: auto; padding: 0 32px 60px; }
#card { max-width: 960px; margin: 0 auto; }
```
```javascript
function center() {
  setTimeout(function() {
    var c = document.getElementById('card');
    var m = document.getElementById('main');
    c.style.marginTop = '0';
    var ch = c.offsetHeight, mh = m.clientHeight;
    if (ch < mh) c.style.marginTop = Math.floor((mh - ch) / 2) + 'px';
    else c.style.marginTop = '16px';
  }, 50);
}
```

### ✅ `margin:auto` 方案（次选）
```css
.container {
  flex: 1; display: flex; flex-direction: column;
  overflow-y: auto;
  /* 不用 align-items:center; 不用 justify-content:center; */
}
.card { margin: auto 0; align-self: center; }
```
`margin: auto 0` 在内容短时居中，长时塌缩为 0 允许滚动。**但不能用 `align-items: center`**，否则 auto margin 失效。

## 3. JS 变量名与函数名冲突

**JavaScript 函数声明提升优先级问题**：
```javascript
// ❌ 同名碰撞
var sel = null;           // 全局变量
function sel(t, el) {     // 函数声明
  sel = t;               // 首次执行后 sel 变成字符串，函数身份丢失
}
sel('required', el);      // ✅ 第一次 OK
sel('quick', el);         // ❌ TypeError: sel is not a function
```

**修复**：变量名与函数名必须不同。
```javascript
var selType = null;
function sel(t, el) { selType = t; }
```

## 4. 选项标准化管道

当选项来源不统一（原始文档/LLM 生成/手动录入）时：

```
原始数据 ──→ 归一化脚本 ──→ DB 统一格式 ──→ JSON 导出 ──→ 前端简单渲染
              ↓
         strip all prefixes
         replace with "A.xxx" format
```

**归一化正则**（Python）：
```python
def normalize_option(opt, letter):
    stripped = re.sub(r'^[A-Da-d][.\u3001\uFF0C\s\)）．:：]+', '', str(opt)).strip()
    return f'{letter}.{stripped}'
```

**前端渲染**（JS，所有格式已统一后最简单）：
```javascript
String(o).replace(/^[A-D]\.\s*/, '')  // 只处理 "A." 前缀
```

## 5. 全屏演示 SPA 的 CSS 基线

```css
/* 防裁切 */
#main {
  overflow-y: auto;        /* NOT hidden */
  overflow-x: hidden;
}
.opt {
  overflow: hidden;        /* 单选项文字过长隐藏，非整题隐藏 */
  word-break: break-word;
  min-height: 52px;        /* 保证空内容也可见 */
}
```

## 6. 调试技巧

无法看到实际渲染问题时，给页面加调试面板：
```javascript
window.onerror = function(msg, src, line) {
  // 显示在固定底部面板
};
```
或关键渲染处打印 `console.log` 输出数据结构和类型。

## 参考文件

- `references/css-flex-overflow-bug.md` — CSS flex 居中+overflow bug 详细复现与解决方案
