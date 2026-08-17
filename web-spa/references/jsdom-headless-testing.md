# jsdom 无头验收 SPA（单文件 HTML 的逻辑级测试）

适用：需要断言**逻辑态**（判分对错、localStorage 内容、抽题配比、倒计时递减、DOM 状态机）而非像素/手势。托管 browser 工具拒绝 file:// 与 localhost（`browser_navigate` 报 "Blocked: URL targets a private or internal address"）时，这是比 playwright-core 更轻的备选；视觉/手势/橡皮筋物理仍走 `scripts/verify-pager.js` 的 playwright 路径。

来源于 OPT-FDE 练习系统 session（2026-08）：86 条断言全 PASS，覆盖练习判分→错题写入→测验抽题→倒计时→成绩环→错题连对移除→file:// 降级全链路。

## 最小骨架

```javascript
const { JSDOM } = require('jsdom');
const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  pretendToBeVisual: true,          // 提供 requestAnimationFrame（测动画 class/环）
  url: 'https://localhost/'         // 关键：让 localStorage 可用
});
const { window } = dom;
const $  = s => window.document.querySelector(s);
const ev = expr => window.eval(expr);        // 读顶层 let/const（见坑 2）
window.confirm = () => true;                  // 所有 native confirm 自动接受
await new Promise(r => setTimeout(r, 300));   // 等脚本执行
$('#start-btn').click();                       // onclick 绑定直接 .click() 驱动
```

## 七个坑（按踩坑顺序）

1. **`url` 必须给 http(s) 源**。file:// 在 jsdom 是 opaque origin，`localStorage` 抛 `SecurityError`。反过来利用：第二个 dom 用 `url:'file:///C:/test.html'` 专测降级路径——断言 `store.ok===false` 且提示条渲染、答题不崩。
2. **顶层 `let/const` 不在 `window` 上**（全局词法环境）。从 Node 侧读写用 `window.eval('session.items.length')` / `window.eval('session.idx = 4')`；函数声明同样可经 eval 调用（`window.eval('renderExam()')`）。
3. **native `confirm()`/`alert()` 会卡住测试**——开局 `window.confirm = () => true`（或按需返回 false 测取消分支）。
4. **jsdom 没有 `matchMedia` / `scrollIntoView` / `scrollTo`**。应用代码必须防御式调用（这本就是好实践）：
   `if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;`
   `const el=$('.fb'); if (el && el.scrollIntoView) el.scrollIntoView(...);`
5. **定时器是真实时钟**：倒计时断言 `await sleep(1300)` 后查 `left < 1800`；异步反馈（如 `setTimeout(confetti, 350)`）要等够再断言元素存在，别 150ms 就查。
6. **视图导航类断言注意循环尾部副作用**：测试循环里"答完题→点下一题"是固定尾动作，中途插入的跳题/回退探针必须把状态恢复到"尾动作执行后等于下一迭代期望"的位置——恢复错一格，后面级联 FAIL。
7. **断言计数前先枚举所有写入路径**：多个流程写同一个 store 时（练习答错、测验答错、多选专项测试都写错题本），漏算一个流程，计数断言必然 FAIL。先在心里跑一遍"当前 localStorage 里应该有几条、分别来自哪一步"。

## 驱动答题的通用助手

```javascript
function answerCorrectly(){
  const t = ev('session.items[session.idx].q.type');
  if (t === 'judge') $(`.jbtn[data-v="${ev('session.items[session.idx].q.answer')}"]`).click();
  else if (t === 'single') $$('.opt')[ev('session.items[session.idx].prepared.findIndex(o=>o.isCorrect)')].click();
  else { ev('session.items[session.idx].prepared.map((o,i)=>o.isCorrect?i:-1).filter(i=>i>=0)')
           .forEach(i => $$('.opt')[i].click()); $('#sub-multi').click(); }
}
// 答错版本：findIndex(o=>!o.isCorrect)；多选选"全部错误项"或"少选一个正确项"（验集合相等判分）
```

## 顺带可验的静态项

- 抽 `<script>` 内容 → `node --check`（内联 80KB JSON 也一并校验）
- 标签平衡：对每个结构标签计数 `<tag(\s|>)` vs `</tag>`
- 零外部依赖：grep `src|href="http`、`@import`、`url(http`、`\bfetch\(` 应全空

## 已知噪音（可忽略）

`Not implemented: Window's scrollTo() method` —— jsdom 警告，不影响断言；grep 过滤即可。
