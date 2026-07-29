---
name: web-spa
description: Web SPA 开发模式与陷阱——全屏演示/答题类单页应用的最佳实践。覆盖 CSS 居中+溢出的经典坑、数据加载方案选择、JS 作用域陷阱、选项格式化管道、倒计时音效、自动隐藏导航、流体排版、Apple 风格 UI。
version: 1.2.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [frontend, spa, css, layout, js, audio]
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
  - "倒计时音效"
  - "Web Audio beep"
  - "导航条自动隐藏"
---

# web-spa — Web SPA 开发模式与陷阱

## 1. 数据加载方案决策

| 方案 | 适用 | 坑 |
|------|------|-----|
| Supabase JS 客户端 `@supabase/supabase-js@2` | 需要实时写入 | `.select('*')` 不加 `.limit(1000)` 可能分页截断；JSONB 字段偶发返回字符串而非数组 |
| Supabase REST API `fetch()` 直调 | 只读、高性能 | 无自动重试，需手动 `limit=1000` |
| OSS 预生成 JSON → fetch | **最可靠**，零运行时风险 | 需 cron 定时同步，非实时 |

**分离原因**：题库是"慢数据"（数百题 x 完整选项），用预生成 JSON 最可靠；配置是"快数据"（几个数字），从 Supabase 直读实现零延迟同步。

**CDN 缓存陷阱**：OSS JSON 被 CDN 缓存后，即使设 `Cache-Control: no-cache`，浏览器仍可能用旧文件。修复：**JSON 文件名版本化** `quiz_data_{timestamp}.json`，每次同步生成新文件名，display.html 中引用新 URL。

```javascript
// 题库从 JSON → 配置从 Supabase REST
fetch('https://gzzhike.cn/funv-quiz/quiz_data_1784263695.json')  // 版本化文件名
  .then(r => r.json())
  .then(d => { pool = d.required; })
  .then(() => fetch(SUPABASE + '/rest/v1/exam_config?select=*&limit=1', { headers }))
  .then(r => r.json())
  .then(cfg => { config = cfg[0]; })
```

**分离原因**：题库是"慢数据"（数百题 x 完整选项），用预生成 JSON 最可靠；配置是"快数据"（几个数字），从 Supabase 直读实现零延迟同步。

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

### ✅ 推荐方案 A：`::before`/`::after` 伪元素（最可靠，纯 CSS）
```css
#main {
  display: flex; flex-direction: column; align-items: center;
  flex: 1; min-height: 0;          /* ← min-height:0 是关键 */
  overflow-y: auto; overflow-x: hidden;
}
#main::before, #main::after { content: ''; flex: 1; min-height: 0; }
#card { max-width: 960px; width: 100%; }
```
**原理**：`::before` 和 `::after` 是 flex 弹性占位符，`flex: 1` 平分剩余空间→居中。内容溢出时 `min-height: 0` 让占位符缩到零，所有内容可滚动。

**优点**：纯 CSS、缩放/窗口变化自动响应、不依赖 JS 计算。

### ✅ 方案 B：JS 动态居中
```javascript
function center() {
  var c = document.getElementById('card');
  var m = document.getElementById('main');
  var ch = c.offsetHeight, mh = m.clientHeight;
  c.style.marginTop = (ch < mh) ? Math.floor((mh - ch) / 2) + 'px' : '16px';
}
```
**注意**：页面缩放后不重新计算，可能导致导航被挤出视口。方案 A 更优。

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

## 4. LLM 生成结构化数据的铁律（题库导入核心教训）

**核心坑**：LLM 重排选项导致答案字母错位——补全缺失选项时改变了 ABCD 排列顺序，但 `correct_answer` 字母未更新，导致指向错误选项。一次 session 中发现 38 处此类错误。

### 规避策略（按优先级）

1. **System Prompt 强制声明**：
```
铁律：选项顺序与原文保持一致，不可重排！答案字母必须与选项位置对应。
选项固定4个，统一 "A.xxx" "B.xxx" "C.xxx" "D.xxx" 格式。
严禁使用 A、 A) A， 等分隔符。
```

2. **导入后自动校验**：每道题检查 `correct_answer` 指向的选项文本与原始文档是否一致。

3. **答案字母错位修复脚本**（比内容文本，非字母）：
```python
# 38 处字母错位 → 修复脚本：对每道题，匹配 docx 正确答案文本到 DB 选项位置
for q in db_questions:
    dx_text = docx_correct_answer_text.get(q['question_text'][:80])
    for idx, opt in enumerate(q['options']):
        opt_clean = re.sub(r'^[A-D]\\.\\s*', '', str(opt)).strip()
        if prefix_match(opt_clean, dx_text) > 0.5:
            if chr(65+idx) != q['correct_answer']:
                update_db(q['id'], chr(65+idx))
```

### 其他常见错误（本项目实际踩坑）

| 错误类型 | 现象 | 修复 |
|----------|------|------|
| 选项合并 | "C.xxxD.xxx" 被当成一个选项 | 正则 `([A-D])\\\\.` 拆分 |
| 缺 D 选项(58题) | 只有 3 个选项 | LLM 补全但保持前 3 个顺序不变 |
| 答案字母错位(38题) | 补选项后答案字母未更新 | 修复脚本比内容文本重新匹配位置 |
| 题号污染 | 选项文本中含 "B1-1 (√)" | `re.sub(r'[BQ]\\\\d+-\\\\d+.*', '', opt)` |
| 跨套重复 | 不同套同名题目 | 按 question_text 去重 |
| 近似重复 | "一个月内"/"1个月内" | Levenshtein ≤2 且答案相同→删一条 |
| JSON 非法 | 题目中引号未转义 | 导入前 `json.dumps` 校验 |
| 配置不实时 | admin 改完配置 display 页不变 | 配置从 Supabase 直读，不用 JSON 同步 |

## 5. 选项标准化管道

归一化所有选项为 `A.xxx` 格式，让前端渲染只需最简单正则：

**后端归一化（Python）**：
```python
def normalize_option(opt, letter):
    stripped = re.sub(r'^[A-Da-d][.\u3001\uFF0C\s\））．:：]+', '', str(opt)).strip()
    return f'{letter}.{stripped}'
```

**前端渲染（JS，格式统一后）**：
```javascript
String(o).replace(/^[A-D]\.\s*/, '')  // 只需处理 "A." 前缀
```

## 6. 响应式流体排版

用 `clamp()` 替代固定 `px` 和手动 `@media`：

```css
.qtext { font-size: clamp(22px, 2.5vw, 38px); }  /* 题目 */
.opt   { font-size: clamp(14px, 1.4vw, 22px); }  /* 选项 */
#card  { max-width: clamp(600px, 70vw, 960px); }  /* 卡牌 */
```

**效果**：一个声明覆盖 720p→4K 所有分辨率，UI 缩放 150% 时字体等比缩小。比手动 `@media(max-height:800px)` 更平滑。

## 7. 倒计时 + Web Audio 音效

**场景**：答题/竞赛类 SPA 需要在指定时间点发出音频提示。

**Web Audio API 合成嘟声（无需外部音频文件）**：
```javascript
var _actx = null;
function beep(n) {
  try {
    if (!_actx) _actx = new (window.AudioContext || window.webkitAudioContext)();
    for (var k = 0; k < n; k++) {
      (function(d) { setTimeout(function() {
        var o = _actx.createOscillator(), g = _actx.createGain();
        o.type = 'square'; o.frequency.value = 880; g.gain.value = 0.06;
        o.connect(g); g.connect(_actx.destination);
        o.start(); o.stop(_actx.currentTime + 0.1);
      }, d); })(k * 350);
    }
  } catch(e) {}
}

// 高频警报"滴滴滴滴"（8声，两两分组）
function beepAlert() {
  var count = 0;
  var id = setInterval(function() {
    if (count >= 8) { clearInterval(id); return; }
    var o = _actx.createOscillator(), g = _actx.createGain();
    o.type = 'square'; o.frequency.value = 1200; g.gain.value = 0.12;
    o.connect(g); g.connect(_actx.destination);
    o.start(); o.stop(_actx.currentTime + 0.15);
    count++;
  }, 300);
}
```

**时间点触发模式**：
```javascript
// 1分钟时：2声嘟
if (left === 60 && lastAlert > 60) { beep(2); }
// 10→1秒：红色脉冲（可配合每秒 beep(1)）
if (left >= 1 && left <= 10) { el.classList.add('warn'); }
// 归零
if (left <= 0) { stopTimer(); beepAlert(); }
```

**显示**：大号 `MM:SS` 格式 + 缩放适配：
```javascript
function fmtTime(s) {
  var m = Math.floor(s / 60), sec = s % 60;
  return (m < 10 ? '0' : '') + m + ':' + (sec < 10 ? '0' : '') + sec;
}
```

## 8. 导航条自动隐藏（沉浸式全屏）

**场景**：大屏投影答题时，顶栏和底栏默认隐藏，鼠标移到触发区时淡入。

**CSS 实现**：
```css
/* 导航条：默认滑出隐藏 */
#topbar {
  opacity: 0; transform: translateY(-100%);
  transition: opacity .35s ease, transform .35s ease;
  backdrop-filter: blur(20px); /* Apple 毛玻璃 */
}
#topbar:hover, #topbar.show { opacity: 1; transform: translateY(0); }

/* 透明触发区（扩大 hover 范围） */
.top-zone { position: fixed; top: 0; left: 0; right: 0; height: 44px; z-index: 21; }
```

底栏同理，用 `translateY(100%)`。首次进入时给导航条加 `.show` class 亮相 3 秒后自动移除作为提示。

## 9. Apple 风格 UI（关联技能）

需要 Apple 设计语言时加载 `apple-design` 技能。在实际项目中应用的组件：
- 毛玻璃：`backdrop-filter: blur(20px) saturate(180%)`
- 弹簧动画：`cubic-bezier(0.32,0.72,0,1)` / `cubic-bezier(0.34,1.56,0.64,1)`
- 胶囊按钮 + `:active { transform: scale(0.96) }` 按压反馈
- SF 风格字体：`letter-spacing: -0.022em`（大标题收紧）

## 10. PPT 式横向翻页 Pager（单文件手册/课件）

做「横向翻页单文件 HTML」（学员手册、课件 deck、landing 翻页页）时，直接套用 `references/pager-carousel.md` 的完整配方：

- **物理**：damping-ratio/response 双参数弹簧（response 0.4s），释放速度直接作弹簧初速；`project()` 动量投射（d=0.998）定落页；甩动 |v|>600px/s 才用 damping 0.8，默认 1.0 无过冲；飞行中 pointerdown 即 `cancelAnimationFrame` 可中断。
- **手势**：viewport `touch-action: pan-y`（纵滚交给原生），10px 阈值横向优先判定，判定后才 `setPointerCapture`；首末页橡皮筋（c=0.55）；拖拽 >10px 后 suppress 一次 click。
- **UI**：进度条从弹簧实时 x 渲染（非 idx）；入场 `.rv` 元素 `--d` 错峰 + `page:not(.active)` 无过渡即隐 → 重进重播；目录从 `data-g`/`data-t` 属性两处生成（浮层 + 内嵌目录页）。
- **reduced-motion**：track 交叉淡入 + 瞬时吸附，CSS 强制 `.rv` 全可见。
- **验收**：`scripts/verify-pager.js`（playwright-core + 系统 Chrome）——页数/键盘/目录跳页/拖拽/reduced-motion/移动端 resize/控制台零报错，一条命令出 PASS/FAIL。托管 browser 工具拒绝 file:// 与 localhost 时走此路径。

## 11. 调试技巧

```javascript
// 全局错误捕获
window.onerror = function(msg, src, line) { /* 显示在固定底部面板 */ };

// 渲染关键节点打印数据结构
console.log('q:', q[i], 'opts type:', typeof q[i].options, 'len:', q[i].options?.length);
```

在页面底部放红色调试面板，按 `D` 键切换显示。加载完成后自动隐藏。

## 参考文件

- `references/css-flex-overflow-bug.md` — CSS flex 居中+overflow bug 详细复现与解决方案
- `references/llm-import-guardrails.md` — LLM 批量生成题库的导入规范、System Prompt 模板、校验清单
- `references/pager-carousel.md` — PPT 式横向翻页 Pager 完整配方：弹簧物理/手势状态机/橡皮筋/reduced-motion 交叉淡入/入场错峰
- `scripts/verify-pager.js` — 翻页 deck 无头验收探针（playwright-core + 系统 Chrome），交付前跑 PASS/FAIL
- `web-quiz-system` — 问答系统专用技能：Supabase题库+大屏展示+LLM导入+OSS部署（本项目实际应用）
