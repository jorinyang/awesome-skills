# 暑假营销方案 HTML 参考模板

## 基本信息
- 项目：黔山秀水·探秘之夏 暑假旅游营销
- 日期：2026-05-26
- 产出：对外宣传单页 HTML
- URL：https://gzzhike.cn/web-spa/summer-campaign-2026/index.html

---

## 页面结构

### 导航栏（固定顶部）
- Logo + 锚点链接（体验项目 / 路线行程 / 价格方案 / 联系我们）+ CTA 按钮

### 首屏 Hero
- 大标题 + 副标题 + 双按钮（立即预订 / 探索项目）
- 背景：渐变色 + 几何纹理 SVG

### 核心体验区（3卡片）
- 卡片结构：图标区（emoji + 渐变背景）/ 标题 / 地点 / 描述 / 标签
- 三张卡片：桨板 / 犀牛洞 / 天坑群
- 交互：hover 上浮 + 阴影加深

### 行程路线（D1-D3 时间轴）
- 左侧圆形日期标记 + 右侧内容
- 每节点：标题 + 描述 + 标签组

### 价格方案（3栏）
- 三栏卡片，居中卡片突出（scale 1.05 + 边框强调）
- 结构：标题 / 价格大数字 / 备注 / 特性列表 / CTA 按钮

### 联系我们 / CTA（最终版）
- 手机号展示区 + 微信号展示
- **社群入口三卡片**：微信 / 飞书 / 钉钉（含占位二维码 + 协议跳转链接）
- 主按钮：「查看价格方案」（非 alert 弹窗）
- 备按钮：「返回顶部」

### 页脚
- 品牌名 + 三个据点地址 + 版权

---

## 技术要点

### 色彩系统
```
--primary: #2d6a4f        /* 山峦青 */
--primary-light: #40916c
--primary-dark: #1b4332
--accent: #e76f51         /* 日出橙 */
--accent-warm: #f4a261
--stone: #8b7355
--cream: #fefae0          /* 暖米背景 */
--cream-dark: #f5e6c8
--ink: #1a1a1a
--ink-light: #4a4a4a
```

### 字体
- 标题：Noto Serif SC（衬线，传达山河沉稳感）
- 正文：Noto Sans SC（无衬线，清晰易读）

### 响应式断点
- Desktop: > 1024px（三栏布局）
- Tablet: 768px-1024px（两栏）
- Mobile: < 768px（单栏，隐藏导航链接，仅保留 CTA）

### 关键 CSS 技巧
- `clamp()` 用于响应式字号：`font-size: clamp(48px, 8vw, 88px)`
- Hero 背景叠加：渐变层 + SVG 点阵纹理层
- 卡片 hover：`transform: translateY(-8px)` + 阴影过渡
- 居中卡片突出：`transform: scale(1.05)`，移动端 reset 为 none

### 部署
- 目录：`web-spa/summer-campaign-2026/`
- 单文件上传（index.html 内联全部 CSS/JS）
- Bucket ACL 验证：`clawshell-vault` 已是 `public-read`，直接上传即可

---

## 交付后 QA 必查清单

每张卡片自检三件事（2026-05-26 修复记录）：
- [ ] **按钮可点击**：`href` 不能是 `#contact` + alert()，也不能是行内 `<!-- 注释 -->` 打断的标签
- [ ] **卡片等高**：父级 `.price-card` 加 `display:flex; flex-direction:column`，子级 `.price-features` 加 `flex:1`
- [ ] **CTA 社群入口**：联系区必须包含微信/飞书/钉钉三社群卡片，即使二维码暂缺也要留结构

## 贵州之客品牌调性（本次沉淀）
- 主色：山峦青 + 暖米背景，对照强烈但不刺眼
- 强调色：日出橙（#e76f51），用于价格/CTA/标签
- 风格：克制、留白、呼吸感，不堆砌装饰元素
- 体验文案写法：情绪价值先行（「朋友圈最特别的夏天」），景点信息辅助
