# 单文件练习/考试 SPA 配方（零依赖 + 内联题库）

适用：把一份本地题库 JSON 变成一个**双击就能打开**的单文件 HTML 练习系统（练习模式/模拟测验/错题本），无 Supabase、无 OSS、无 CDN、无字体、无图片。来源于 OPT-FDE 80 题培训练习系统 session（2026-08）。

## 1. 构建管线：模板 + 内联脚本

不要让 HTML 手抄题库。维护两个文件：

```
_build_template.html   # 完整 SPA，脚本里只有一行占位：const BANK = /*__BANK_JSON__*/;
_build.js              # Node 构建脚本（见下）
```

```javascript
// _build.js
const fs = require('fs');
const src = JSON.parse(fs.readFileSync('_practice_bank.json', 'utf8'));
const out = {
  meta: src.meta,
  questions: src.questions.map(q => ({
    id: q.id, type: q.type, module: q.module, question: q.question,
    // 剥掉 "A." 前缀——运行时按 {text,isCorrect} 重排，标签按新位置重新分配
    options: q.options ? q.options.map(o => o.replace(/^[A-Z]\.\s*/, '')) : null,
    answer: q.answer, analysis: q.analysis
  }))
};
let json = JSON.stringify(out);
json = json.replace(/</g, '\\u003c');          // 防题目文本中的 "</" 提前闭合 <script>
const html = fs.readFileSync('_build_template.html', 'utf8')
  .replace('/*__BANK_JSON__*/', json);
fs.writeFileSync('04-练习系统.html', html, 'utf8');
```

构建前先跑数据校验（count/类型分布/答案格式/选项前缀完整性），比生成后调试便宜得多。

## 2. 选项乱序：对象级重映射（判分正确性的核心）

```javascript
function prepare(q){
  if (q.type === 'judge') return null;                 // 判断题不参与
  const opts = q.options.map((t, i) => ({
    text: t, isCorrect: q.answer.indexOf('ABCDEFGH'[i]) >= 0
  }));
  shuffle(opts);                                       // 对象整体洗牌
  return opts.map((o, i) => { o.label = 'ABCDEFGH'[i]; return o; }); // 标签按新位置重分配
}
function gradeItem(it, sel){                            // sel = 新下标数组
  if (it.q.type === 'judge') return sel[0] === it.q.answer;
  const ci = it.prepared.map((o,i)=>o.isCorrect?i:-1).filter(i=>i>=0);
  return sel.length === ci.length && ci.every(i => sel.includes(i));  // 多选=集合相等
}
```

**铁律**：判分只查 `isCorrect` 标志，绝不记录"用户选了字母 C"再与原答案字母比——重排后字母已错位（与 SKILL.md §4 LLM 重排坑同源，一个是数据期一个是运行期）。解析/回顾里的"正确答案：B D"也从 prepared 的 isCorrect 重新生成。

## 3. localStorage 在 file:// 下的降级

`file://` 在部分浏览器是 opaque origin，`localStorage.setItem` 直接抛异常。不处理则整个 SPA 白屏。

```javascript
const store = (function(){
  let ok = false; const mem = {};
  try { localStorage.setItem('__t','1'); localStorage.removeItem('__t'); ok = true; } catch(e){}
  return {
    ok,
    get(k, def){ try { if(ok){ const v=localStorage.getItem(k); return v?JSON.parse(v):def; } return (k in mem)?mem[k]:def; } catch(e){ return def; } },
    set(k, v){ mem[k]=v; if(ok){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} } }
  };
})();
// 首页 + 错题本页：if(!store.ok) 显示"本次数据仅会话内有效"提示条
```

错题本 key 按项目加前缀（`opt_fde_wrong`），统计另存一个 key（`opt_fde_stats`）。错题条目结构 `{streak:0, ts}` —— 答错入册/重置 streak，重练答对 streak+1，≥2 自动删除（"连对 2 次才算掌握"闭环）。练习与测验的错题都入册。

## 4. 测验模式抽题与状态

```javascript
const byType = t => BANK.questions.filter(q => q.type === t);
const pick   = (arr,n) => shuffle(arr.slice()).slice(0, Math.min(n, arr.length)); // 不足则全取
const all = shuffle([...pick(byType('single'),12), ...pick(byType('multi'),3), ...pick(byType('judge'),10)]);
session = { mode:'exam', items: all.map(q => ({q, prepared: prepare(q)})), idx:0, answers:{}, marks:{}, left:1800 };
```

- **选项在抽题时一次 prepare 存进 session**——翻题导航回去不能重洗，否则用户已选下标指向别的选项。
- 倒计时 `setInterval(1s)`，`left<=60` 加红色脉冲 class，归零 clearInterval + 自动交卷；交卷前 `confirm('还有 N 题未作答')`。
- 题号网格 25 格：已答(filled)/未答(gray)/当前(ring)/标记(⚑角标)，点格跳题。
- 成绩：每题 4 分（25×4=100），≥70 通过；SVG 双 circle 环 `stroke-dashoffset` 动画；通过才生成 confetti（CSS `@keyframes` translateY+rotate，`prefers-reduced-motion` 时跳过生成）。

## 5. 四视图状态机

home → practice-setup → quiz（practice/wrong 共用渲染器，mode 区分）→ quizDone；home → exam → result；home → wrongbook → quiz(wrong)。单 `#app` 容器 innerHTML 重渲染 + `.view{animation}` 弹簧入场（仅 transform/opacity）。顶栏 frosted glass 随视图换 title/back/进度 chip。

## 6. 验收

- `node --check` 抽出的内联脚本 + 结构标签平衡脚本（开放/闭合计数）。
- jsdom 无头功能测：判分/localStorage/抽题配比/倒计时/错题闭环/file:// 降级——配方见 `references/jsdom-headless-testing.md`。
