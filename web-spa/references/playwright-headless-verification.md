# Playwright 无头验证全屏 HTML 交付物（deck / SPA / landing）

实测来源：60 页培训 deck（195KB 单文件、hash 深链 `#/N`、O 总览、N notes 抽屉）全量验证通过。脚本可直接抄改。

## 陷阱 1：同文档 hash 跳转不触发重载（最高优先级）

页面已在 `file:///deck.html`（任意 hash）时，`page.goto(URL + "#/N")` 是 same-document navigation——**页面不重载**，deck 初始化时的 hash 解析不会执行，深链测试和截图会静默拍到**错误的页面**且难以察觉（测试报"深链失败"但 deck 没病，先怀疑测试写法）。

修复：每次 hash 导航前插入 `about:blank` 强制真实加载：

```python
pg.goto("about:blank"); pg.goto(URL + f"#/{i}", wait_until="load"); pg.wait_for_timeout(400)
```

## 陷阱 2：evaluate() 返回值不是元素句柄

`page.evaluate("document.querySelectorAll('.ovt')[34]").click()` → `AttributeError: 'str' object has no attribute 'click'`。evaluate 把返回值序列化回 Python（str/dict/list），不是 ElementHandle。点击用 locator：

```python
page.locator(".ovt").nth(34).click()
```

## 功能验证清单脚本（骨架，按需增删断言）

```python
from playwright.sync_api import sync_playwright
URL = "file:///C:/path/deck.html"
errors = []
with sync_playwright() as p:
    pg = p.chromium.launch(headless=True).new_page(viewport={"width":1600,"height":900})
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(URL, wait_until="load"); pg.wait_for_timeout(600)
    total  = pg.evaluate("document.querySelectorAll('.slide').length")         # 页数
    active = pg.evaluate("document.querySelectorAll('.slide.active').length") # 应==1
    pg.keyboard.press("ArrowRight"); pg.keyboard.press("End"); pg.keyboard.press("Home")
    pg.keyboard.press("o")                                                   # 总览
    thumbs = pg.evaluate("document.querySelectorAll('.ovt').length")
    pg.locator(".ovt").nth(30).click()                                       # 缩略图跳转
    pg.keyboard.press("n")                                                   # notes 抽屉
    body = pg.text_content("#ndbody")                                        # 应有内容且随翻页刷新
    pg.keyboard.press("Escape")
    pg.goto("about:blank"); pg.goto(URL + "#/42")                            # 深链（强制重载）
    pg.wait_for_timeout(400)
    assert "42 /" in pg.text_content("#pagenum")
assert not errors, errors   # 控制台零报错
```

## DOM 对比度审计（WCAG 算法；比抽 5 页目视强，能抓像素统计漏掉的浅色底+白字）

在页面上下文跑 IIFE：对每个文本元素向上找第一个非透明背景算有效背景色，算相对亮度比，低于 3.2 报警：

```javascript
(() => {
  const parse = s => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x)); return [p[0],p[1],p[2], p.length>3?p[3]:1]; };
  const lum = ([r,g,b]) => { const f = c => { c/=255; return c<=0.03928 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4); };
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b); };
  const effBg = el => { let e = el; while (e && e !== document.body) {
    const c = parse(getComputedStyle(e).backgroundColor);
    if (c && c[3] > 0.9) return c.slice(0,3); e = e.parentElement; } return [255,255,255]; };
  const bad = [];
  document.querySelectorAll('.slide.active p,.slide.active li,.slide.active td,.slide.active th,.slide.active h1,.slide.active h2,.slide.active h3,.slide.active h4')
    .forEach(el => { if (!el.textContent.trim()) return;
      const fg = parse(getComputedStyle(el).color); if (!fg) return;
      const L1 = lum(fg.slice(0,3)), L2 = lum(effBg(el));
      const r = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
      if (r < 3.2) bad.push({ r: +r.toFixed(2), txt: el.textContent.trim().slice(0,30) });
    });
  return bad;
})()
```

每页跑一遍（`about:blank` + hash 翻页），汇总。实测战果：60 页扫出梯级图浅蓝 `#5ac8fa` 底白字 ratio=1.9。

## 溢出审计

```python
ov = pg.evaluate("(()=>{const s=document.querySelector('.slide.active');return {sh:s.scrollHeight,ch:s.clientHeight}})()")
# ov["sh"] > ov["ch"] + 4 → 该页在目标视口溢出
```

密集教材级 deck 目标是**不溢出**；`overflow-y:auto` + 美化滚动条是安全网不是目标（等高居中的正确写法见本技能 §2）。

## 无 VLM 时的渲染健全性检查（PIL 像素统计）

环境里没有视觉模型时的替代：截图转灰度，算均值/标准差。Apple 白底 deck：**mean>200 且 std>20** = 白底且有内容渲染；空白页/渲染失败必挂其一。

```python
from PIL import Image
import statistics
px = list(Image.open("shot.png").convert("L").getdata())
mean, std = sum(px)/len(px), statistics.pstdev(px)
ok = mean > 200 and std > 20
```

## 颜色规则（血泪教训）

**浅色强调色（#5ac8fa 类，亮度≈0.5）只做装饰**（进度条、渐变底、键帽），**绝不做白字背景**（对比度 1.9 不可读）。白字彩块背景亮度需 ≤0.28 才过 3.2 线：

| 颜色 | 白字对比度 | 结论 |
|---|---|---|
| #5ac8fa | 1.9 | ❌ 装饰专用 |
| #3d8fd1 | 3.47 | ✅ 浅阶梯/浅彩块可用 |
| #0071e3 / #0a54b8 / #1d1d1f | >4.5 | ✅ 安全 |

## 超大单文件的分块构建模式（50+ 页 deck）

单次 write_file 写 200KB+ 有截断风险。已验证模式（60 页 / 195KB 零截断）：

1. `write_file` 写基座：head + 全部 CSS + 前 3–5 页 + chrome（进度条/页码/抽屉/总览容器）+ 完整 JS 控制器，并在 `#deck` 收尾前放唯一标记 `<!--APPEND-->`。
2. 每个模块一次 `patch(mode=replace)`：`old_string='<!--APPEND-->'`，`new_string='<该模块 7–9 页>\n<!--APPEND-->'`。
3. 最后一批把标记换成末批 slides（不带标记）。

唯一标记保证 patch 模糊匹配零歧义，永远不碰已写内容。
