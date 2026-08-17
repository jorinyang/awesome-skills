# 拖拽·手势·转场 — Web 实现配方（看板系统实测）

> 来源：多用户项目管理 SPA（Supabase + 单文件 HTML）交互升级 session，2026-07。全部配方经浏览器实测（合成 PointerEvent 序列验证跨列拖拽、sheet 下滑关闭、快速完成动效全链路）。

## 1. Pointer Events 替代 HTML5 Drag & Drop

HTML5 DnD（draggable + dragstart/dragover/drop）在需要「Apple 级」跟手体验时不合格：移动端基本不支持、拖拽视觉由浏览器接管不可控、不可中断/反转、dragover 触发频率怪异。**任何需要 1:1 跟手、FLIP 让位、弹簧归位的拖拽都用 Pointer Events 手写。**

卡片基础 CSS：`touch-action: pan-y`（垂直滚动留给页面，水平拖动和长按归手势）+ `user-select: none`。

## 2. 激活阈值（防误触）

- 鼠标：按下后移动距离 > 8px 即开始拖拽
- 触摸：长按 240ms 激活；激活前若移动 > 10px 判定为滚动意图，`clearTimeout` + 移除监听取消手势

## 3. 1:1 跟手（尊重抓取偏移）

```js
const rect = card.getBoundingClientRect();
const grabOffsetX = e.clientX - rect.left, grabOffsetY = e.clientY - rect.top;
// 拖拽中（fixed 定位下用 transform 偏移，scale/rotate 营造"提起"感）：
card.style.transform = `translate(${x - grabOffsetX - rect.left}px, ${y - grabOffsetY - rect.top}px) scale(1.04) rotate(1.5deg)`;
```

提起时：卡片改 `position: fixed` + 原 left/top/width + `z-index: 500` + `pointer-events: none` + 深阴影；原位置插入同高 `.task-placeholder`（2px 虚线边框 + 半透明底色）。拖拽期间 `document.body.style.overflow='hidden'` 防页面滚动。

## 4. 落点判定 + FLIP 让位动画

目标列：指针坐标 vs 每列 `getBoundingClientRect()`（外扩约 12px 容差提升容错）。插入位置：指针 Y 与列内兄弟卡片中线比较。

兄弟卡片让位用 FLIP（记录旧位置 → 移动占位符 → 反向补偿 → 播放）：

```js
const items = [...document.querySelectorAll('.kanban-tasks .task-card')].filter(el => el !== ghost);
const oldTops = new Map(items.map(el => [el, el.getBoundingClientRect().top]));
targetList.insertBefore(placeholder, insertBeforeEl);
items.forEach(el => {
  const dy = oldTops.get(el) - el.getBoundingClientRect().top;
  if (!dy) return;
  el.style.transition = 'none';
  el.style.transform = `translateY(${dy}px)`;
  requestAnimationFrame(() => {
    el.style.transition = 'transform .28s cubic-bezier(.32,.72,0,1)';
    el.style.transform = '';
  });
});
```

## 5. 释放：弹簧归位 + 乐观持久化

- 维护最近 6 个 `{x, y, t}` 采样算释放速度（可作过冲/动量投射依据）
- 归位：`card.style.transition='transform .32s cubic-bezier(.32,.72,0,1)'`，transform 目标 = placeholder 屏幕位置——**从呈现值出发，无跳变**（可中断性原则）
- ~300ms 后：移除 ghost + placeholder → 按占位符顺序计算列内新 position（idx*10 留间隙便于后续插入）→ 乐观更新本地 state → 局部重渲染 → 后台 `Promise.all` PATCH（状态 + 各卡片 position），失败 toast 并回滚
- 局部重渲染只重建列内容 + 计数，不重新拉数据；计数变化播 `scale 1→1.35→1` bump 动画

## 6. 拖拽后抑制 click

拖拽卡片本身有 onclick（打开详情）。拖拽结束时 `suppressNextClick = true`，100ms 后复位；onclick 首行检查该标志并 return。否则 drop 后立即触发详情弹窗。

## 7. iOS Sheet drag-to-dismiss

- 手势只绑在顶部 handle 条 + header 区（body 滚动区不绑，避免与内容滚动冲突）；modal-body 加 `overscroll-behavior: contain`
- 拖拽中：sheet 关 transition（`.dragging` 类），下拉 `translateY(dy)`，**上拉橡皮筋 `dy/3`**
- 释放判定：位移 > 120px 或速度 > 0.6px/ms → `translateY(105%)` 携带动量关闭（0.28s spring curve）；否则弹簧回弹 `cubic-bezier(.34,1.25,.4,1)`
- 速度从最近 5 个采样的首尾两点计算

## 8. SPA 视图转场（无框架）

- 容器 `.view-stack { display: grid }`，所有 `.view-pane { grid-area: 1/1 }` 同格叠放，天然支持双 pane 并存转场
- 前进：新 pane 初始 `translateX(56px); opacity: 0` → reflow（`void el.offsetHeight`）→ 移除初始类播 transition；旧 pane 加 `translateX(-56px); opacity: 0`，420ms 后 `remove()`。返回方向完全镜像（空间一致性原则）
- **竞态守卫**：`const seq = ++viewSeq`；异步数据回来后 `if (seq !== viewSeq) return`——快速连点切换时旧请求不覆盖新视图
- 骨架屏在新 pane 创建的第一帧就渲染（响应优先），数据到位后同 pane 就地替换——转场与加载并行，无白屏等待

## 9. 实测有效的微交互清单

| 交互 | 配方 |
|------|------|
| 数字入场 | count-up：rAF + cubic-out easing，`Math.round(target * (1-(1-p)^3))` |
| 卡片入场 | stagger：`animation-delay: idx*60ms`，from `translateY(26px) scale(.96)` |
| 快速完成 | hover 浮现圆形勾选钮 → SVG 描边动画（stroke-dasharray/offset）→ 卡片脉冲 → **延迟 ~380ms 再移列**（先让用户看到完成反馈） |
| 删除 | 退场类 `translateX(30px) scale(.92) opacity 0`，~280ms 后重渲染 |
| 表单错误 | shake 关键帧 + 红框；重启动画技巧：先 remove 类 → `void el.offsetWidth` → add 类 |
| 头像组 | 默认 `margin-left: -8px` 堆叠，容器 hover 时 `-2px` 散开（transition margin） |
| 确认对话框 | 用 Apple 风格模态（danger 按钮 + 说明文案）替代原生 `confirm()` |

## 10. 无头验证方法

用 browser_console 注入合成 PointerEvent 序列（pointerdown → 多个 pointermove 过阈值 → pointerup）可无头验证整个拖拽链路：断言 `.drag-lift` 类存在、placeholder 数量、目标列 `drag-over` 高亮、释放后各列卡片数与 state 一致。求值表达式写单行 + `var` + 普通函数最稳妥。
