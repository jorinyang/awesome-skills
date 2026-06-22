---
name: pdf-content-generation
version: 1.0.0
description: "从结构化内容+图片生成排版精良的PDF文档（产品手册、宣传册、方案书等），支持中文排版、多章节布局、图片嵌入。触发：生成PDF/做个PDF/做成PDF/排版成PDF/输出PDF/产品手册/宣传册PDF。"
metadata:
  requires:
    bins: ["python3"]
    pkgs: ["fpdf2", "Pillow"]
---

# PDF 内容生成

从用户提供的结构化内容（文字+图片）生成排版精良的 PDF 文档。

## 快速决策

- 用户要编辑已有 PDF（改文字/标题/错字）→ [`nano-pdf`](../nano-pdf/SKILL.md)
- 用户要做网页版本 → [`feishu-html`](../feishu-html/SKILL.md)
- 用户要做 PPT → [`powerpoint`](../powerpoint/SKILL.md)
- 用户要从零生成新 PDF 文档 → **本 skill**

## 工作流

### 1. 理解内容结构
从用户消息中提取：标题、副标题、章节划分、正文、图片位置（`[Image]` 标记）、价格信息、注意事项等。

### 2. 安装依赖
```bash
pip3 install fpdf2 Pillow
```

### 3. 压缩图片（关键步骤）
原始图片通常过大（40MB+），必须先压缩：
```python
from PIL import Image
img = Image.open(src)
img.thumbnail((1280, 1280))  # 限制最大边长
img.save(dst, quality=85)
```
保存为 `_sm.jpg` 后缀版本供 PDF 使用。

### 4. 生成 PDF

#### 字体配置
```python
from fpdf import FPDF

class PDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        # 按优先级查找 CJK 字体
        font_paths = [
            '/usr/share/fonts/truetype/noto/NotoSansSC-Regular.ttf',
            '/usr/share/fonts/opentype/noto/NotoSansSC-Regular.otf',
            '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                self.add_font('CN', '', fp)
                # 尝试 Bold 变体
                bold = fp.replace('Regular','Bold').replace('-Regular','-Bold')
                if os.path.exists(bold):
                    self.add_font('CNB', '', bold)
                break
        # 兜底：搜索任意 noto *sc* 字体
        if not hasattr(self, 'cn_font'):
            for root, dirs, files in os.walk('/usr/share/fonts'):
                for f in files:
                    if 'noto' in f.lower() and 'sc' in f.lower():
                        self.add_font('CN', '', os.path.join(root, f))
                        break
```

#### 配色与尺寸
```python
GREEN = (27, 140, 62)   # #1B8C3E — 章节标题/价格
DARK  = (40, 40, 40)     # 正文
GRAY  = (120, 120, 120)  # 次要信息
MARGIN = 18  # 左右边距(mm)
```

#### 图片嵌入
```python
def add_image_centered(self, path, max_w=170, max_h=120):
    """居中嵌入图片，自动缩放适应页面"""
    img = Image.open(path)
    ratio = min(max_w/img.width, max_h/img.height)
    w, h = img.width*ratio, img.height*ratio
    x = self.l_margin + (self.w - self.l_margin - self.r_margin - w) / 2
    if self.get_y() + h > self.h - 20:
        self.add_page()
    self.image(path, x=x, w=w, h=h)
    self.ln(h + 3)
```

#### 章节标题
```python
def section_title(self, title):
    self.ln(3)
    self.set_font('CNB' or 'CN', '', 14)
    self.set_text_color(*GREEN)
    self.cell(0, 8, title)
    self.ln(10)
    # 绿色下划线分隔
    self.set_draw_color(*GREEN)
    self.set_line_width(0.6)
    self.line(self.l_margin, self.get_y(), self.w-self.r_margin, self.get_y())
    self.ln(5)
```

#### 价格突出显示
```python
# 绿色边框矩形框
self.set_fill_color(245, 250, 245)
self.set_draw_color(*GREEN)
y = self.get_y()
self.rect(self.l_margin, y, self.w-self.l_margin-self.r_margin, 28, style='DF')
self.set_xy(self.l_margin+5, y+4)
self.set_font('CNB' or 'CN', '', 18)
self.set_text_color(*GREEN)
self.cell(0, 8, '¥298 / 人')
```

### 5. 上传到飞书 Drive

```bash
cd /path/to/output && lark-cli drive +upload --file ./output.pdf --name "文档名.pdf" --as bot
```

> ⚠️ `--as bot` 必须用相对路径；`--as user` 无此限制但可能需要额外 scope

### 6. 返回链接

上传后返回飞书云空间文件链接供用户查看/下载。

## 典型页面结构

```
封面页：品牌图全幅 + 标题 + 副标题 + 一句话介绍
内容页：章节标题(绿色+下划线) + 正文 + 配图(居中自适应)
价格页：突出价格框 + 规则列表
尾页：收尾图片 + 品牌信息 + 地址
```

## 模板

可直接基于 [`templates/brochure_template.py`](templates/brochure_template.py) 修改内容生成 PDF，包含封面、章节、价格框、尾页等常用组件。

## 避坑

- 大图(>5MB)不压缩会导致 PDF 体积爆炸 — 必须用 PIL thumbnail 到 1280px
- fpdf2 不支持 emoji（如 ⚠ ▴）— 使用纯文本或 ASCII 替代
- WenQuanYi 字体缺少部分 Unicode 符号 — 优先用 Noto Sans SC
- 图片跨页时手动 `add_page()` 避免截断
- A4 可用高度约 277mm（297-20 底部边距）
