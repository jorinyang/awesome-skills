#!/usr/bin/env python3
"""PDF brochure generator template — customize content, sections, and image paths.
Dependencies: pip3 install fpdf2 Pillow
"""
from fpdf import FPDF
from PIL import Image
import os

CACHE = os.path.expanduser("~/.hermes-feishu/image_cache")

class BrochurePDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        # ---- CJK font discovery ----
        font_paths = [
            '/usr/share/fonts/truetype/noto/NotoSansSC-Regular.ttf',
            '/usr/share/fonts/opentype/noto/NotoSansSC-Regular.otf',
            '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                self.add_font('CN', '', fp)
                bold = fp.replace('Regular','Bold').replace('-Regular','-Bold')
                if os.path.exists(bold):
                    self.add_font('CNB', '', bold)
                break
        # Fallback: search for any Noto SC font
        if 'CN' not in self.fonts:
            for root, dirs, files in os.walk('/usr/share/fonts'):
                for f in files:
                    if 'noto' in f.lower() and 'sc' in f.lower() and f.endswith(('.ttf','.otf','.ttc')):
                        self.add_font('CN', '', os.path.join(root, f))
                        break
                if 'CN' in self.fonts:
                    break

    # ---- helpers ----
    GREEN = (27, 140, 62)
    DARK  = (40, 40, 40)
    GRAY  = (120, 120, 120)
    LIGHT_GREEN_BG = (245, 250, 245)

    def heading(self, title):
        self.ln(3)
        font = 'CNB' if 'CNB' in self.fonts else 'CN'
        self.set_font(font, '', 14)
        self.set_text_color(*self.GREEN)
        self.cell(0, 8, title)
        self.ln(10)
        self.set_draw_color(*self.GREEN)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)

    def para(self, text, size=9):
        self.set_font('CN', '', size)
        self.set_text_color(*self.DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def kv(self, key, value, key_w=52):
        """Key-value pair line"""
        font_b = 'CNB' if 'CNB' in self.fonts else 'CN'
        self.set_font(font_b, '', 9)
        self.set_text_color(*self.DARK)
        self.cell(key_w, 7, key)
        self.set_font('CN', '', 9)
        self.cell(0, 7, value)
        self.ln(8)

    def add_img(self, path, max_w=170, max_h=120):
        """Center image, auto-page-break if needed"""
        if not os.path.exists(path):
            sm = path.replace('.jpg', '_sm.jpg')
            if os.path.exists(sm):
                path = sm
            else:
                return False
        img = Image.open(path)
        ratio = min(max_w / img.width, max_h / img.height)
        w, h = img.width * ratio, img.height * ratio
        x = self.l_margin + (self.w - self.l_margin - self.r_margin - w) / 2
        if self.get_y() + h > self.h - 20:
            self.add_page()
        self.image(path, x=x, w=w, h=h)
        self.ln(h + 3)
        return True

    def price_box(self, text, sub_text, box_h=28):
        """Highlighted price rectangle"""
        y = self.get_y()
        self.set_fill_color(*self.LIGHT_GREEN_BG)
        self.set_draw_color(*self.GREEN)
        self.rect(self.l_margin, y, self.w - self.l_margin - self.r_margin, box_h, style='DF')
        font_b = 'CNB' if 'CNB' in self.fonts else 'CN'
        self.set_xy(self.l_margin + 5, y + 4)
        self.set_font(font_b, '', 18)
        self.set_text_color(*self.GREEN)
        self.cell(0, 8, text)
        self.set_xy(self.l_margin + 5, y + 15)
        self.set_font('CN', '', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, sub_text)
        self.set_y(y + box_h + 4)

    # ---- header/footer ----
    def header(self):
        if self.page_no() > 1:
            self.set_font('CN', '', 7)
            self.set_text_color(150, 150, 150)
            self.cell(0, 4, '', align='R')  # override with doc title
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('CN', '', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, str(self.page_no()), align='C')


# ============================================================
# USAGE EXAMPLE — replace content below
# ============================================================
if __name__ == '__main__':
    pdf = BrochurePDF()
    pdf.set_auto_page_break(True, 20)
    pdf.set_left_margin(18)
    pdf.set_right_margin(18)

    # --- Cover ---
    pdf.add_page()
    pdf.ln(30)
    font_b = 'CNB' if 'CNB' in pdf.fonts else 'CN'
    pdf.set_font(font_b, '', 26)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 12, '产品标题', align='C')
    pdf.ln(16)
    pdf.set_font(font_b, '', 20)
    pdf.cell(0, 10, '副标题', align='C')
    pdf.ln(14)
    pdf.set_font('CN', '', 13)
    pdf.set_text_color(*pdf.GREEN)
    pdf.cell(0, 8, '一句话描述', align='C')
    pdf.ln(25)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font('CN', '', 10)
    pdf.multi_cell(0, 7, '介绍段落内容...', align='C')

    # --- Section 1 ---
    pdf.add_page()
    pdf.heading('一、章节标题')
    pdf.para('正文内容...')

    # --- Price section ---
    pdf.add_page()
    pdf.heading('费用')
    pdf.price_box('¥XXX / 人', '补充说明信息')
    pdf.para('详细规则...', size=8)

    # --- Back cover ---
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font('CN', '', 12)
    pdf.set_text_color(*pdf.GREEN)
    pdf.cell(0, 8, '品牌名称', align='C')
    pdf.ln(10)
    pdf.set_font('CN', '', 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, '地址信息', align='C')

    # Save
    output = os.path.expanduser('~/output.pdf')
    pdf.output(output)
    print(f'Done: {output}  ({os.path.getsize(output)/1024:.0f} KB, {pdf.page_no()} pages)')
