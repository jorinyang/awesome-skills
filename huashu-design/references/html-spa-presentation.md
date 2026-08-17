# HTML SPA Presentation Pattern（单文件幻灯片SPA）

> 与 `deck_stage.js` web component 和多文件架构不同的第三种模式。适用于：培训课件、企业内部演示、需要单文件交付的场景。

## 与 deck_stage.js 的区别

| 维度 | deck_stage.js | SPA Pattern |
|------|--------------|-------------|
| 依赖 | 需要 `deck_stage.js` 外部文件 | 零依赖，全内联 |
| 架构 | Web Component (`<deck-stage>`) | 原生 JS + CSS class 切换 |
| CSS作用域 | Shadow DOM | 全局（单文件天然无冲突） |
| 总览模式 | 无 | 内置（按O键缩略图总览） |
| 触控支持 | 无 | 内置touch swipe |
| 点击翻页 | 无 | 左1/3=上页，右1/3=下页 |
| 适用规模 | ≤10页 | 实测48页可用 |

**选型建议**：需要跨页共享状态/React交互 → deck_stage.js；培训课件/企业演示/单文件交付 → SPA Pattern。

## 完整骨架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>演示标题</title>
<style>
/* ===== Reset & Variables ===== */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --blue:#0071e3;
  --dark:#1d1d1f;
  --gray:#fafafa;
  --green:#34c759;
  --orange:#ff9500;
  --red:#ff3b30;
  --purple:#7c3aed;
  --radius:12px;
  --shadow:0 2px 12px rgba(0,0,0,.08);
  --font:system-ui,-apple-system,'PingFang SC','Helvetica Neue',Arial,sans-serif;
}
html,body{width:100%;height:100%;overflow:hidden;font-family:var(--font);color:var(--dark);background:#fff;-webkit-font-smoothing:antialiased}

/* ===== Progress Bar ===== */
#progress-wrap{position:fixed;bottom:0;left:0;right:0;height:20px;background:rgba(0,0,0,.08);z-index:1000}
#progress{position:absolute;bottom:0;left:0;height:100%;background:linear-gradient(90deg,var(--blue),#5ac8fa);transition:width .4s cubic-bezier(.4,0,.2,1);width:0;border-radius:0 10px 10px 0}
#pagenum{position:absolute;bottom:0;left:0;right:0;height:20px;display:flex;align-items:center;justify-content:center;font-size:.72rem;color:#fff;font-weight:600;z-index:1001;text-shadow:0 1px 2px rgba(0,0,0,.3);font-variant-numeric:tabular-nums}

/* ===== Slide Container ===== */
#deck{position:relative;width:100vw;height:100vh;overflow:hidden}
.slide{
  position:absolute;inset:0;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:60px 80px 40px;
  opacity:0;visibility:hidden;
  transition:opacity .5s cubic-bezier(.4,0,.2,1),transform .5s cubic-bezier(.4,0,.2,1);
  transform:translateX(40px);
  background:#fff;overflow-y:auto;
}
.slide.active{opacity:1;visibility:visible;transform:translateX(0)}
.slide.exit-left{opacity:0;visibility:visible;transform:translateX(-40px)}

/* ===== Backgrounds ===== */
.slide--gray{background:#fafafa}
.slide--blue{background:linear-gradient(135deg,var(--blue) 0%,#5ac8fa 100%);color:#fff}

/* ===== Typography ===== */
.slide h1{font-size:2.8rem;font-weight:700;letter-spacing:-.02em;line-height:1.2;margin-bottom:.4em;text-align:center}
.slide h2{font-size:2.4rem;font-weight:600;letter-spacing:-.01em;line-height:1.3;margin-bottom:.3em;text-align:center}
.slide h3{font-size:1.3rem;font-weight:600;margin-bottom:.3em}
.slide p,.slide li{font-size:1.1rem;line-height:1.7}
.slide .subtitle{font-size:1.15rem;color:#555;margin-bottom:.8em}
.small{font-size:.88rem;color:#555}
.tiny{font-size:.78rem;color:#666}
.content{width:100%;max-width:1200px;display:flex;flex-direction:column;align-items:center}

/* ===== Stagger Animation ===== */
.stagger>*{opacity:0;transform:translateY(16px);transition:opacity .4s ease,transform .4s ease}
.slide.active .stagger>*:nth-child(1){transition-delay:.08s}
.slide.active .stagger>*:nth-child(2){transition-delay:.16s}
.slide.active .stagger>*:nth-child(3){transition-delay:.24s}
.slide.active .stagger>*:nth-child(4){transition-delay:.32s}
.slide.active .stagger>*:nth-child(5){transition-delay:.40s}
.slide.active .stagger>*:nth-child(6){transition-delay:.48s}
.slide.active .stagger>*{opacity:1;transform:translateY(0)}

/* ===== Components ===== */
.card{background:#fff;border-radius:var(--radius);padding:24px 28px;box-shadow:var(--shadow)}
.card-grid{display:grid;gap:16px;width:100%;max-width:1100px}
.card-grid.cols-2{grid-template-columns:1fr 1fr}
.card-grid.cols-3{grid-template-columns:1fr 1fr 1fr}
.card-grid.cols-4{grid-template-columns:1fr 1fr 1fr 1fr}
.section-tag{display:inline-block;font-size:.78rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--blue);margin-bottom:10px;background:rgba(0,113,227,.08);padding:4px 12px;border-radius:6px}
.flow{display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:center}
.flow-step{background:var(--blue);color:#fff;padding:10px 18px;border-radius:10px;font-size:.88rem;font-weight:500}
.flow-arrow{color:var(--blue);font-size:1.3rem}
.callout{padding:14px 18px;border-radius:var(--radius);margin:12px 0;font-size:.9rem}
.callout-blue{background:rgba(0,113,227,.06);border-left:3px solid var(--blue)}

/* ===== Overview Mode ===== */
#overview{position:fixed;inset:0;background:rgba(0,0,0,.92);z-index:2000;display:none;overflow:auto;padding:40px}
#overview.show{display:flex;flex-wrap:wrap;gap:14px;justify-content:center;align-items:flex-start}
.overview-thumb{width:200px;height:120px;border-radius:8px;overflow:hidden;cursor:pointer;border:3px solid transparent;transition:border-color .2s,transform .2s;position:relative;flex-shrink:0}
.overview-thumb:hover,.overview-thumb.active{border-color:var(--blue);transform:scale(1.05)}
.overview-thumb .thumb-num{position:absolute;bottom:4px;right:8px;font-size:.7rem;color:#fff;background:rgba(0,0,0,.5);padding:2px 6px;border-radius:4px}

/* ===== Nav Arrows ===== */
.nav-arrow{position:fixed;top:50%;transform:translateY(-50%);z-index:500;width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.9);box-shadow:var(--shadow);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:opacity .2s,transform .2s;opacity:0}
.nav-arrow svg{width:18px;height:18px;color:var(--dark)}
#navPrev{left:16px}
#navNext{right:16px}
body:hover .nav-arrow{opacity:1}
.nav-arrow:hover{transform:translateY(-50%) scale(1.1)}

/* ===== Responsive ===== */
.slide::-webkit-scrollbar{width:6px}
.slide::-webkit-scrollbar-thumb{background:#c1c1c1;border-radius:3px}
@media(max-width:768px){
  .slide{padding:24px 16px 30px}
  .slide h1{font-size:1.8rem}
  .slide h2{font-size:1.5rem}
  .card-grid.cols-3,.card-grid.cols-4{grid-template-columns:1fr}
  .card-grid.cols-2{grid-template-columns:1fr}
}
</style>
</head>
<body>

<!-- Progress Bar -->
<div id="progress-wrap"><div id="progress"></div><div id="pagenum"></div></div>

<!-- Nav Arrows -->
<button id="navPrev" class="nav-arrow" aria-label="上一页"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg></button>
<button id="navNext" class="nav-arrow" aria-label="下一页"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></button>

<div id="deck">
  <!-- Slide 1 -->
  <section class="slide active">
    <div class="stagger content">
      <h1>标题</h1>
      <p class="subtitle">副标题</p>
    </div>
  </section>
  <!-- Slide 2 ... -->
</div>

<div id="overview"></div>

<script>
(function(){
  const slides=document.querySelectorAll('.slide');
  const total=slides.length;
  let current=0,isOverview=false,touchStartX=0,touchStartY=0;
  const progress=document.getElementById('progress');
  const pagenum=document.getElementById('pagenum');
  const overview=document.getElementById('overview');
  const deck=document.getElementById('deck');

  function update(){
    slides.forEach((s,i)=>{s.classList.remove('active','exit-left');if(i<current)s.classList.add('exit-left')});
    slides[current].classList.add('active');
    progress.style.width=((current+1)/total*100)+'%';
    pagenum.textContent=(current+1)+' / '+total;
    if(isOverview)highlightThumb();
  }
  function go(n){if(n<0||n>=total)return;current=n;update()}
  function next(){go(current+1)}
  function prev(){go(current-1)}

  // Keyboard
  document.addEventListener('keydown',e=>{
    if(isOverview){if(e.key==='Escape'||e.key==='o'||e.key==='O'){toggleOverview()}return}
    switch(e.key){
      case'ArrowRight':case'ArrowDown':case' ':case'PageDown':case'Enter':e.preventDefault();next();break;
      case'ArrowLeft':case'ArrowUp':case'PageUp':e.preventDefault();prev();break;
      case'o':case'O':toggleOverview();break;
      case'Home':e.preventDefault();go(0);break;
      case'End':e.preventDefault();go(total-1);break;
    }
  });

  // Touch
  deck.addEventListener('touchstart',e=>{touchStartX=e.touches[0].clientX;touchStartY=e.touches[0].clientY},{passive:true});
  deck.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-touchStartX;const dy=e.changedTouches[0].clientY-touchStartY;if(Math.abs(dx)>Math.abs(dy)&&Math.abs(dx)>50){dx<0?next():prev()}},{passive:true});

  // Nav buttons
  document.getElementById('navPrev').addEventListener('click',prev);
  document.getElementById('navNext').addEventListener('click',next);

  // Click zones: left 1/3 = prev, right 1/3 = next
  deck.addEventListener('click',e=>{
    if(e.target.closest('button,a,input,textarea,select,.overview-thumb'))return;
    const x=e.clientX/window.innerWidth;
    if(x<0.33)prev();else if(x>0.67)next();
  });

  // Overview
  function toggleOverview(){
    isOverview=!isOverview;
    if(isOverview){
      overview.classList.add('show');overview.innerHTML='';
      slides.forEach((s,i)=>{
        const thumb=document.createElement('div');
        thumb.className='overview-thumb'+(i===current?' active':'');
        const clone=s.cloneNode(true);
        clone.style.cssText='position:absolute;inset:0;transform:scale(0.22);transform-origin:top left;width:'+window.innerWidth+'px;height:'+window.innerHeight+'px;opacity:1;visibility:visible;overflow:hidden';
        thumb.style.width='200px';
        thumb.style.height=(window.innerHeight/window.innerWidth*200)+'px';
        thumb.appendChild(clone);
        const num=document.createElement('div');num.className='thumb-num';num.textContent=i+1;thumb.appendChild(num);
        thumb.addEventListener('click',()=>{go(i);toggleOverview()});
        overview.appendChild(thumb);
      });
    }else{overview.classList.remove('show');overview.innerHTML=''}
  }
  function highlightThumb(){overview.querySelectorAll('.overview-thumb').forEach((t,i)=>{t.classList.toggle('active',i===current)})}

  update();
})();
</script>
</body>
</html>
```

## 关键交互特性

| 功能 | 实现方式 |
|------|---------|
| 键盘翻页 | ←/→/Space/Enter/PageUp/PageDown/Home/End |
| 触控翻页 | touchstart→touchend 检测水平滑动>50px |
| 点击翻页 | 左1/3区域=上页，右1/3=下页，中间1/3=无操作 |
| 悬停导航按钮 | body:hover .nav-arrow{opacity:1} |
| 总览模式 | 按O键，缩略图网格，点击跳转 |
| 进度条 | 底部20px高，渐变蓝色，页码居中 |
| 入场动画 | .stagger子元素逐个延迟出现(80ms间隔) |
| 页面切换 | opacity+translateX(40px)过渡，已翻过的页面exit-left |

## 48页性能验证

实测48页（~106KB HTML）在Chrome/Edge中流畅运行，无卡顿。总览模式克隆48个缩略图也无性能问题。

## Pitfalls

1. **第一个slide必须有class="active"**，否则所有页都不可见
2. **stagger动画依赖.slide.active**，子元素必须在.slide内
3. **总览模式克隆了整个slide DOM**，超过50页时考虑虚拟化
4. **移动端padding需要调小**，默认60px 80px在手机上会溢出
5. **点击区域在button/a/input上不触发翻页**，通过e.target.closest检查
