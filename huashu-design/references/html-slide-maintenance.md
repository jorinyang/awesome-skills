# HTML Slide 维护与迁移规范

维护已有的 HTML 幻灯片（主题迁移、嵌入图片修复、浏览器验证）时的规范和陷阱。

---

## 1. Dark→White 主题迁移（深色→浅色）

### 核心陷阱：内联样式优先级高于 CSS class

深色主题 slide 有两类白色文字来源：
1. **CSS class 规则**：如 `.slide--dark p { color: rgba(255,255,255,.92) }`
2. **内联 style**：如 `<h3 style="color:#fff">`

改 `.slide--dark { background: #fff }` **只解决了第 1 类**。内联 `color:#fff` 的元素仍然是白字白底——**视觉上完全不可见**。

### 迁移清单

| 步骤 | 操作 | 必须性 |
|------|------|--------|
| 1. CSS class 背景 | `.slide--dark { background: #fff }` | 必须 |
| 2. CSS class 文字色 | `.slide--dark p, li { color: rgba(0,0,0,.82) }` | 必须 |
| 3. **扫描全部内联白色文字** | grep `color:#fff` / `color:rgba(255,255,255` | **必须** |
| 4. 区分深色容器 vs 白色容器 | 深色卡片/代码块内的白色文字应保留 | 必须检查 |
| 5. 渐变/蓝色背景页 | `slide--gradient` / `slide--blue` / Q&A 页白色文字保留 | 必须检查 |
| 6. 信息卡片背景 | `background:rgba(255,255,255,.08)` → `#f5f5f7` | 推荐 |
| 7. KBD/快捷键提示 | `background:rgba(255,255,255,.1)` → `rgba(0,0,0,.06)` | 推荐 |

### 扫描命令

```bash
grep -n 'color:#fff\|color:rgba(255,255,255\|color:#FFF\|color: white' file.html \
  | grep -v 'slide--gradient\|slide--blue\|Q & A'
```

### 判断逻辑

对每个匹配项，判断其**父容器背景**：
- 父容器白色/浅灰 → **需改深色文字**
- 父容器深色/蓝色/渐变 → **保留白色文字**
- 父容器彩色徽章（蓝/绿/橙/红） → **保留白色文字**

---

## 2. 嵌入式 Base64 图片操作规范

### Patch 工具会截断 Base64 数据

当文件包含大型 base64 编码图片（>5KB）时，**不要在该图片附近使用 patch 工具**。patch 的 diff 生成算法会截断 base64 数据，导致 `<img>` 标签损坏。

**正确做法**：用 `execute_code` 内的 Python 脚本完成全部操作（读文件 → 字符串替换 → 写文件），一个脚本搞定。

### read_file 无法处理超长单行

base64 data URI 是单行超长字符串（可能 >18,000 字符）。`read_file` 的行格式化会截断输出。**用 terminal + Python 的 `open().read()` 读取。**

### PNG→JPEG 转换陷阱

```python
# ❌ 直接保存会报 KeyError: 'RGBA'（PNG 有 alpha 通道）
img.save(buf, format='JPEG', quality=75)

# ✅ 先转 RGB
img = img.convert('RGB')
img.save(buf, format='JPEG', quality=75, optimize=True)
```

### 全流程模板（execute_code 内执行）

```python
from hermes_tools import terminal

result = terminal(r"""python3 -c "
import base64
from PIL import Image
import io

# 1. 生成 data URI
img = Image.open(r'path\\to\\image.png')
img = img.resize((480, 576), Image.LANCZOS)
img = img.convert('RGB')  # PNG→JPEG 必须
buf = io.BytesIO()
img.save(buf, format='JPEG', quality=75, optimize=True)
data_uri = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

# 2. 读 HTML
with open(r'path\\to\\file.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 3. 替换
old = 'broken img tag text'
new = '<img src=\"' + data_uri + '\" alt=\"...\" style=\"...\">'
content = content.replace(old, new)

# 4. 写回
with open(r'path\\to\\file.html', 'w', encoding='utf-8') as f:
    f.write(content)
" """, timeout=60)
```

---

## 3. 浏览器验证技巧

### 闭包内 JS 函数的导航方法

很多 HTML 幻灯片的导航函数在 IIFE 闭包内，console 无法直接调用。

**可靠替代方案**：

```javascript
// 方法 1：通过 overview 模式跳转（最可靠）
// 先按 'o' 打开总览，然后：
document.querySelectorAll('.overview-thumb')[N].click()  // N = 0-based index

// 方法 2：直接操作 DOM（快速验证）
const slides = document.querySelectorAll('.slide');
slides.forEach((s, i) => {
  s.classList.remove('active', 'exit-left');
  if (i < targetIndex) s.classList.add('exit-left');
});
slides[targetIndex].classList.add('active');
```

### Flex 布局溢出时改用 Grid

当 flex 布局在窄视口导致子元素堆叠（本应并排）：

```css
/* ❌ flex 在窄视口会折叠 */
display: flex; gap: 56px; align-items: center;

/* ✅ grid 保证两列并排 */
display: grid; grid-template-columns: 240px 1fr; gap: 40px; align-items: center;
```

---

## 5. 彩色背景上的文字颜色陷阱

### 代码块/预格式化文本的颜色问题

HTML 幻灯片中的代码块常用 `color:#e6edf3`（浅灰蓝色，专为深色代码块设计）。当代码块被放入**浅色背景容器**时，这个颜色几乎不可见。

**典型问题模式**：

```html
<!-- ❌ 浅红底 + #e6edf3 浅色字 = 看不到 -->
<div style="background:rgba(255,59,48,.1)">
  <pre style="color:#e6edf3">文字内容</pre>
</div>

<!-- ✅ 浅红底 + 深色字 = 清晰可读 -->
<div style="background:rgba(255,59,48,.1)">
  <pre style="color:#1d1d1f">文字内容</pre>
</div>
```

### 排查方法

```bash
# 找出所有 #e6edf3（深色背景专用浅色字）在浅色容器中的使用
grep -n '#e6edf3' file.html
```

对每个匹配项，检查其**祖先容器的背景色**：
- 容器 `background:rgba(r,g,b,.1)` 或 `.06` → 浅色背景，**必须改深色字**
- 容器 `background:#1d1d1f` 或 `var(--dark)` → 深色背景，**保留 #e6edf3**

### 速查：安全的文字颜色

| 背景类型 | 安全文字色 | 避免 |
|----------|-----------|------|
| 白色/浅灰 `#fff` / `#f5f5f7` | `#1d1d1f` / `rgba(0,0,0,.82)` | `#e6edf3` / `#fff` |
| 浅彩色 `rgba(r,g,b,.06-.15)` | `#1d1d1f` / `rgba(0,0,0,.7)` | `#e6edf3` / `#fff` |
| 深色 `#1d1d1f` / `#0d1117` | `#e6edf3` / `rgba(255,255,255,.92)` | `#1d1d1f` |
| 彩色实底（蓝/绿/橙徽章） | `#fff` | `#1d1d1f` |

---

## 6. PNG 透明度保留与体积控制

### JPEG 不支持透明通道

当用户要求"保留背景透明"时，**不能用 JPEG**：

```python
# ❌ JPEG 丢弃 alpha 通道，背景变白
img.save(buf, format='JPEG')

# ✅ PNG 保留透明度
img.save(buf, format='PNG', optimize=True)
```

### 体积控制：PNG quantize

原图 PNG 可能很大（148KB base64）。用 `quantize` 减色压缩：

```python
# 128 色量化：体积降至 ~1/5，视觉差异极小
img = img.quantize(colors=128, method=2)
buf = io.BytesIO()
img.save(buf, format='PNG', optimize=True)
```

### 体积参考

| 处理方式 | 典型大小 | 适用场景 |
|----------|---------|---------|
| 原图 PNG 直接内嵌 | ~150KB base64 | 用户要求不压缩 |
| PNG 480px + quantize(128) | ~35KB base64 | 标准 PPT 头像 |
| JPEG 480px q=75 | ~18KB base64 | 不需要透明度时首选 |

### RGBA→JPEG 转换必须先转 RGB

```python
img = img.convert('RGB')  # 必须，否则 KeyError: 'RGBA'
```

---

## 7. 常见维护场景速查

| 场景 | 关键步骤 |
|------|----------|
| 改主题色（深→浅） | CSS背景 + CSS文字色 + **扫描全部内联白色文字** + 信息卡片底色 |
| 改主题色（浅→深） | 反向操作，同时检查深色背景上原有深色文字需变白 |
| 替换内嵌图片 | 用 Python read/write（不用 patch），PIL 先 convert('RGB') |
| 修复溢出布局 | flex→grid（固定列宽），或缩小子元素尺寸 |
| 验证某一页 | overview 模式 + `.overview-thumb[N].click()` |
| 批量同步副本 | `cp source.html dest.html`，确认文件大小一致 |
