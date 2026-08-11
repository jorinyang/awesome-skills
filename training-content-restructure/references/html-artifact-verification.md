# HTML 制品自动化验证——选择器陷阱与断言模式

验证 HTML PPT/手册/练习系统（Playwright 或脚本断言）时，**先探测页面容器结构再写断言**，不要假设统一 class。以下陷阱全部来自实测（培训 PPT 59 页 / 学员手册 34 页 / 练习系统 80 题内联）。

## 1. 页数统计选择器

```python
# ❌ 精确匹配漏掉激活页
slides = html.count('class="slide"')   # PPT 实际 58+1 个 'class="slide active"'

# ✅ 先探测再定选择器
import re
sections = re.findall(r'<section[^>]*>', html)     # 学员手册用 <section> 标记页（34 个）
slides = re.findall(r'class="slide', html)         # PPT 用 class="slide"（含 active）
```

- 学员手册类制品可能用 `<section>` 而非 `.slide`；PPT 的激活页是 `class="slide active"`。
- 浏览器侧用 `document.querySelectorAll('.slide')` 会同时匹配两者，脚本侧字符串统计必须包含前缀匹配。

## 2. 页码元素

- 页码常是**静态容器**：`<div id="pagenum">1 / 59</div>`，文本由 JS 翻页时更新。
- 验证"页码动态"：翻 3 页后比较 `textContent`（`'1 / 59' → '4 / 59' → End → '59 / 59'`）。
- 选择器按实际实现命名（`#pagenum` vs `.slide-number` vs `.page-num`）——先 `re.finditer(r'id="page|class="[^"]*page', html)` 查实现，别按惯例猜。

## 3. transform 隐藏的抽屉（notes/面板）

```css
#ndrawer { transform: translateY(106%); transition: transform .35s ease; }
#ndrawer.show { transform: none; }
```

- `offsetHeight` 恒非零（transform 不改变布局高度）——"关闭后 offsetHeight===0"的判断**必然误报**。
- 正确断言：
  - 类判定：`classList.contains('show')`
  - 或样式判定：`getComputedStyle(el).transform === 'none'`（显示）vs `matrix(1, 0, 0, 1, 0, Y)`（隐藏中）
- CSS transition 0.3-0.5s：开合检测之间 `page.wait_for_timeout(400+)`，否则读到过渡中间态。

## 4. 控制台零报错

```python
errors = []
page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
page.on("pageerror", lambda e: errors.append(str(e)))
```

只监听 `console` 的 error 类型会漏掉未捕获异常（`pageerror`），必须双监听。

## 5. 内联数据校验（练习系统类单文件）

- `node _build.js` 生成后验证：BANK 内联（`'const BANK' in html`）、题目数（统计 `"type":"single"|"multi"|"judge"` 出现次数=80）、黑名单残留（`'M6'`、模块 chip 数组 `MODULES=[...]` 是否含已删模块）。
- **改模板源再重建**：直接改生成物会被下次 build 覆盖；`_build.js` 的 `dest` 文件名写死时，改模板 + 改 `_build.js` 目标名 + 重建 + 重部署四步一起做。
- OSS 一致性：本地 md5 vs `urllib.request.urlopen(URL).read()` 的 md5，确认部署无漂移。

## 6. 验证脚本自身

- f-string 拼正则：`rf"### M{m}[^\n]*"` 中 `{m}` 若已是 `"M2"` 会变 `MM2`——模板变量传裸值（`"2"`）。
- 豁免判断：修订说明不一定在文件头（HTML 单行结构可能在第 400+ 行）——用上下文窗口含关键词（修订说明/变更记录/移除 M6/已删除）判定，或人工逐条确认。
