# 横向翻页 Pager 实现配方（PPT 式单文件 HTML 手册/幻灯片）

> 场景：PPT 式单文件 HTML（学员手册、课件、landing deck），要求 Apple 流体翻页手势。
> 本配方在「OPT 学员手册 32 页」实战验证（Playwright 无头全测通过）。配套探针：`scripts/verify-pager.js`。

## 1. 物理核心（px 单位，直接速度交接，无需归一化）

```js
const RESPONSE = 0.4; // Apple move 类交互 0.3–0.4s
function springConsts(damping){ const om = 2*Math.PI/RESPONSE; return { k: om*om, c: 2*damping*om }; }
// 半隐式欧拉积分，dt clamp 32ms；|x-target|<0.4 且 |v|<10 时 settle
// goTo: animateTo(-i*W, velocity, |v|>600 ? 0.8 : 1.0)  ← 甩动才欠阻尼，默认临界阻尼
function project(v, d=0.998){ return (v/1000)*d/(1-d); }              // 动量投射定落页
function rubberband(o, dim){ return (o*dim*0.55)/(dim+0.55*Math.abs(o)); } // 软边界，o 带符号
```

- 速度估计：只取 pointerup 前**最近 100ms** 的 move 采样（保留最近 ~10 个 {t,px}），`v = Δpx/Δt`，dt<5ms 时置 0。
- 落页：`ni = clamp(round(-(x + project(v)) / W))`——从投射点吸附，不是从释放点。
- 中断：pointerdown 第一动作 `cancelAnimationFrame(raf)`，从当前渲染 x 重新 baseline——**永不从逻辑目标值重启动画**。

## 2. 手势状态机（横向优先 + 页内纵滚共存）

```
viewport: touch-action: pan-y   ← 纵向滚动全部交给浏览器原生，JS 只管横向
pointerdown  → killSpring(); 记录 sx/sy/baseX; decided=false
pointermove  → 未决时: |dx|>10 且 |dx|>|dy|*1.15 → 横向：setPointerCapture + body.drag(user-select:none)
               |dy|>10 → 纵向：放弃本次手势（页内 overflow-y:auto + overscroll-behavior:contain 原生滚）
               横向后: x = baseX+dx；越界套 rubberband（首页/末页橡皮筋）
pointerup    → 拖拽>10px 则 suppressClick=true（capture 阶段 click 拦截一次，防误触内容链接/按钮）
```

坑：pointer capture 必须在意图判定**之后**再做，否则纵向滚动被抢走；热区/目录按钮要在 pointerdown 里 `e.target.closest(...)` 排除。

## 3. 导航 UI 与入场动效

- 进度条用**弹簧实时 x** 渲染（`-x/(W*(N-1))`），不是 idx——翻页中进度丝滑推进。
- 页码/模块标签在 `round(-x/W)` 变化时更新（飞行中途即刷新）。
- 入场错峰：JS 为每页 `.rv` 元素设 `--d: i*65ms`；CSS：
  `.rv{opacity:0;transform:translateY(20px)} .page.active .rv{opacity:1;transform:none;transition:…;transition-delay:var(--d)} .page:not(.active) .rv{transition:none}`
  离页立即隐藏且无过渡 → 再次进入动画重播。
- 目录跳页：pages 带 `data-g`(分组)/`data-t`(标题)，JS 生成浮层目录 + 内嵌目录页，两处同一 build 函数。

## 4. prefers-reduced-motion（交叉淡入替代滑动）

```js
if (REDUCED){ killSpring(); track.classList.add('fadeout'); // opacity→0 (.18s)
  setTimeout(()=>{ x=-i*W; render(); track.classList.remove('fadeout'); }, 90); return; }
```
CSS 配套：`@media (prefers-reduced-motion:reduce){ .rv{opacity:1!important;transform:none!important;transition:none!important} }`——内容必须瞬时全可见，不能只禁动画。

## 5. resize

`killSpring(); x=-idx*W; v=0; render()`——直接吸附当前页，禁用弹簧（否则窗口拖动时轨道追着手腕跑）。

## 6. 验收清单（scripts/verify-pager.js 已自动化）

页数与 #total 一致 · 键盘 ←/→/空格/Home/End · 目录打开+跳页 · 拖拽翻页 · reduced-motion 瞬时到位（transform 精确=-W·idx，无弹簧行程） · 移动端 resize 后正确吸附 · **控制台零报错**。

## 7. 无头验证路径

Hermes 托管 browser 工具可能拒绝 file:// 与 127.0.0.1 目标；备用路径：`npm i playwright-core`（不下载浏览器）+ `chromium.launch({channel:'chrome'})` 复用系统 Chrome，配合 `reducedMotion:'reduce'` 与 `setViewportSize` 覆盖 §6 全部用例。
