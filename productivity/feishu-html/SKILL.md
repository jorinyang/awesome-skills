---
name: feishu-html
description: 将飞书文档或用户提供的内容制作成功能完整、视觉精良的 WEB SPA 应用，部署至阿里云 OSS 并提供在线访问链接。触发：做个网页/做个页面/发布到线上/部署/做个展示页/做个方案页/做个功能页/做个后台/做一个web/在线访问/做个汇报页。
triggers:
  - 用户要求创建内部方案+对外宣传两个版本（双轨交付）
---

# Feishu HTML · 内容制作与 OSS 部署

## 必备信息

- **Bucket**：`clawshell-vault`
- **OSS Endpoint**：`https://oss-cn-hongkong.aliyuncs.com`
- **绑定域名**：`https://gzzhike.cn`
- **AccessKey ID**：`REDACTED`
- **AccessKey Secret**：`REDACTED`
- **部署目录前缀**：`web-spa/`
- **OSS SDK**：`oss2`（`pip install oss2`）

---

## 核心能力

1. **内容理解**：深度解析用户提供文档/文本，提取结构、逻辑、核心需求
2. **功能性设计**：拆解目标→制定规范→任务规划→逐步交付→校验验收
3. **展示性设计**：调用 `huashu-design` 技能进行页面规划与视觉设计
4. **WEB SPA 架构**：多 TAB 页面、响应式、移动端+桌面端分别优化
5. **校验**：完整性、功能有效性、页面可读性、内容一致性、关键信息呈现
6. **部署**：上传至 OSS WEB-SPA 目录，交付访问链接

---

## 页面设计与风格规范

### 风格来源优先级

1. **用户明确指定风格**：用户提供了参考网站/品牌规范/设计稿 → 严格遵循用户指定风格
2. **用户提供了品牌内容**：用户提供了 Logo/VI/色值/字体规范 → 以用户品牌为核心设计元素
3. **无明确风格说明**：默认参考旅游行业风格，融入山河/自然/在地文化元素
4. **贵州之客品牌调性**（无明确风格且内容涉及贵州之客时）：
   - 主色调：自然系（山峦青、水碧、石褐）
   - 辅助色：暖米/陶土/木色
   - 字体：中文衬线（思源宋体/Noto Serif SC）用于标题，中文无衬线用于正文
   - 视觉语言：克制、留白、有呼吸感，避免过度装饰

### 旅游行业通用风格特征

适用于无明确风格说明时的默认参考：

- **色彩**：自然色系（森林绿/岩石褐/天空蓝/日出橙），饱和度适中
- **版式**：大图留白，信息密度适中，避免信息过载
- **配图**：真实风景/在地人文摄影为主，不用通用 stock photo
- **排版**：层级清晰，标题突出，正文可快速扫读
- **交互**：轻量动效（如 fade-in、slide-up），强化阅读节奏而非炫技

---

## 执行流程

### 阶段一：内容理解

**目的**：充分理解原始文档/文本的结构、逻辑、核心需求，形成可执行的内容大纲。

**步骤**：

1. **获取原始内容**
   - ⚠️ **飞书文档优先用 REST API**：`feishu_doc_read` 工具仅在飞书评论上下文（comment context）中可用，普通对话中会报"Feishu client not available"。通用方法是用 Python + urllib 调用飞书 Open API：
     ```python
     import urllib.request, urllib.parse, json
     # 1. 获取 tenant_access_token
     req = urllib.request.Request(
         'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
         data=urllib.parse.urlencode({'app_id': 'cli_aa9ead14c2641cc3', 'app_secret': 'ZUUm7yI7HmfLi42ki8fPTgZzbj2AuTeM'}).encode(),
         headers={'Content-Type': 'application/x-www-form-urlencoded'}
     )
     with urllib.request.urlopen(req) as r:
         token = json.loads(r.read())['tenant_access_token']
     # 2. 读取文档 raw_content
     req2 = urllib.request.Request(
         f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/raw_content',
         headers={'Authorization': f'Bearer {token}'}
     )
     with urllib.request.urlopen(req2) as r:
         content = json.loads(r.read())['data']['content']
     ```
   - 飞书消息线程：GET `/im/v1/messages?container_id_type=thread&container_id={thread_id}`
   - 用户直接提供：直接使用

2. **深度分析内容**
   - 梳理内容结构（总论→分论点→案例/数据→结论）
   - 识别核心信息模块（标题、段落、列表、数据、引用、图表）
   - 提取关键词、核心论点、业务逻辑、数据关系
   - 识别隐含需求（用户没明说但内容暗示的功能）

3. **需求具象化**
   - 明确最终交付物的使用场景（内部汇报/外部展示/客户演示/持续运营）
   - 确定目标受众（管理层/客户/内部团队/公众）
   - 提取功能需求（查询/筛选/交互/导出/多人协作等）
   - 提取展示需求（信息架构/可视化/导航结构/TAB分类等）

4. **需求确认**：将理解后的内容结构和功能规划一次性向用户确认，🛑 等用户回复再往下走

> **贵州之客例外**：用户（杨瑒/月夜，CTO）沟通风格极简直接，发现问题立即纠正。若用户指令已明确（如"用你修改之后的版本做个web展示"），且提供了文档链接，可直接进入阶段二—三，跳过需求确认步骤，以用户已确认的意图为准。

### 双轨交付模式（触发：内部方案+对外宣传同时需要）

当用户要求同时产出**内部实施方案**和**对外宣传版本**时，两轨并行执行：

| 轨道 | 产出 | 工具 |
|------|------|------|
| 内部执行版 | 飞书在线文档 → 归档至知识库「方案计划」分类 | `feishu-doc` 流程一 |
| 对客宣传版 | HTML 页面 → 部署至 OSS | `feishu-html` 本技能 |

**执行顺序**：先完成飞书文档（内部版固定信息），再基于同一内容框架转化为面向客户的对外版本。两版内容分开——内部版保留预算/KPI/排期等管理信息，对外版聚焦体验场景/价格/报名入口。

**参考案例**：暑假营销方案（2026-05-26），内部版归档于知识库，对外版部署于 `https://gzzhike.cn/web-spa/summer-campaign-2026/index.html`，报名表单页 `book.html` 承接受众报名行为。

**配套参考文件**：
- `references/summer-campaign-template.md` — 对外宣传页结构/配色规范
- `references/booking-form-template.md` — 报名表单页标准字段/样式/链接规范（派生时直接修改项目信息，无需从零构建）
- `references/solution-proposal-template.md` — B2B方案/系统建设提案的客户演示页结构（双轨交付：飞书文档+HTML）
- `references/interactive-demo-template.md` — 交互式功能Demo（客户可点击操作的 prototype，含mock数据/模态框CRUD/多步表单）

---

### 阶段二：功能性与展示性设计规划

#### 2.1 页面分类判断

根据内容判断页面类型：

| 类型 | 判断标准 | 核心特征 |
|------|---------|---------|
| **功能性页面** | 用户需执行操作（查询/填报/审批/配置/管理） | 表单/列表/看板/仪表盘/配置面板 |
| **展示性页面** | 用户仅需阅读/浏览/理解 | 方案介绍/报告/产品说明/数据展示 |
| **交互式Demo** | 客户演示用功能原型，需mock数据+可操作的所有功能模块 | JS数据驱动/搜索筛选/模态框CRUD/多步表单/后台管理面板 |
| **混合页面** | 同时包含以上两者 | 功能模块+展示模块共存 |

> **交互式Demo 与静态方案页的区别**：交互式Demo 用 JS mock 数据数组 + 运行时 CRUD，客户可真正点击体验系统流程。结构模板见 `references/interactive-demo-template.md`。

#### 2.2 功能性页面设计（阶段二-A）

**核心原则**：以终为始，倒推任务路径。

1. **明确最终目标**
   - 用户能做什么？（查询XX、配置XX、提交XX、管理XX）
   - 成功的衡量标准是什么？

2. **拆解功能模块**
   ```
   [最终目标]
       ↓
   [模块A：负责XX]  [模块B：负责XX]  [模块C：负责XX]
       ↓               ↓               ↓
   [子任务A1/A2]   [子任务B1/B2]   [子任务C1/C2]
   ```

3. **制定每步产出标准**
   - 每步完成什么？
   - 如何校验这步是对的？
   - 什么情况下算"完成"？

4. **数据建模**（如涉及）
   - 核心数据实体有哪些？
   - 数据关系是什么？
   - 示例数据是什么？（用于展示）

5. **交互流程设计**
   - 用户操作路径（主路径+分支路径）
   - 异常情况处理（空状态/加载中/错误/权限不足）
   - 键盘快捷键（桌面端）

#### 2.3 展示性页面设计（阶段二-B）

调用 `huashu-design` 技能，执行其完整工作流，特别关注：

1. **内容结构化**
   - 核心论点提炼（不超过5个关键点）
   - 层级扁平化（≤3级标题）
   - 关键数据突出（数字放大/色彩强调）

2. **可视化图形规划**（按需使用）

   | 图形类型 | 适用场景 | 产出 |
   |---------|---------|------|
   | SVG架构全景图 | 产品架构/系统组成/组织结构 | 矢量可缩放图 |
   | 时间周期甘特图 | 项目计划/里程碑/版本规划 | 横向时间轴 |
   | 业务流程结构图 | 业务流转/决策流程/用户路径 | 节点+连线图 |
   | 分析框架图 | SWOT/PEST/波特五力/RFM等 | 矩阵/象限图 |
   | 时间周期趋势图 | 趋势数据/增长曲线/周期波动 | 折线/面积图 |
   | 地理信息图 | 地点分布/路线/区域对比 | 地图+标记 |
   | 占比对比图 | 分类对比/构成分析 | 饼图/环形图/堆叠柱状 |
   | 进度/漏斗图 | 转化漏斗/流程进度 | 漏斗/阶梯图 |

3. **TAB 结构设计**
   - 按逻辑模块分组（不是按原文顺序罗列）
   - 每个 TAB 有明确主题，命名简洁
   - TAB 之间有逻辑递进或并列关系
   - 典型结构：
     - 概览总览 → 详情/明细 → 分析/趋势
     - 背景 → 方案 → 实施 → 效果
     - 产品 → 运营 → 财务 → 团队

4. **内容呈现范式**
   - 标题区：主题 + 核心结论（一句话）
   - 关键指标卡：数字+标签+趋势箭头
   - 内容区：结构化正文 + 可视化辅助
   - 引用区：关键引语/金句独立展示
   - 交互区：可切换的详情面板

---

### 阶段三：WEB SPA 制作

#### 3.0 功能性页面的必检规范 ⚠️

在开始写 HTML 之前，先规划以下功能性要素，漏掉任何一项都是交付缺陷：

**按钮规范**
- 所有「立即预订」类按钮：href 指向报名页面（**不得使用 `#contact` + alert，必须有真实页面承接**）
- 「定制咨询」类按钮：href 指向添加客服微信（`weixin://contacts/profile/gzzhike2026`）或对应 IM 的跳转链接
- HTML 内禁止在行内元素（如 `<a>`、`<button>`）内部嵌入 `<!-- 注释 -->`
- **飞书群/钉钉群等社群跳转链接**：href 不得使用占位符（如 `code=***` 或 `code=XXXXX`），不得出现引号残缺。若暂时没有真实 code，先写完整 URL 结构（去除 code 参数），禁止留残缺引号打断 HTML 解析
- **「返回顶部」按钮**：必须使用 `href="#"`（真正返回页面顶部），禁止指向中间锚点（如 `#pricing`），否则用户从最底部点击会跳到错误位置
- **所有导航/CTA 按钮**：在页面交付前必须逐一验证 href 有效性——禁止任何按钮的 href 是 `#` + JS alert 的空跳转组合

**价格卡片等高规范**（底部对齐 + 顶部对齐）
```css
/* 父级：横向排列 + 等高 */
.price-grid {
  display: flex;
  align-items: stretch;          /* ← 关键：强制整行卡片等高，取最高那张 */
  gap: 24px;
}
/* 每张卡：flex column 布局 */
.price-card {
  display: flex;
  flex-direction: column;
  flex: 1;                       /* 等宽 */
  min-height: 520px;             /* 统一起跑线，内容不满时自然撑高 */
}
/* 内容区：自动填满剩余空间 → 底部按钮永远在同一高度 */
.price-features {
  flex: 1;
  align-self: stretch;
}
```
多行价格卡时，每行必须有独立的 flex 容器，不能跨行直接等高（跨行 grid 的 align-items:stretch 只对单行生效）。每行用一个 `div.price-grid` 包裹该行的所有卡片，确保每行各自顶部对齐、底部对齐。

**联系/CTA 区域设计规范**（展示性页面均有）
当页面含「联系我们」区块时，需要提供以下社群入口：
```
微信社群  →  二维码占位图（120×120 SVG placeholder） + weixin:// 协议跳转
飞书群    →  二维码占位图 + applink 跳转链接（飞书开放平台获取 code 参数）
钉钉群    →  二维码占位图 + dingtalk:// 协议跳转
```
按钮文字统一：非特殊场景，一律「立即预订」；不混用「咨询详情」「定制咨询」

#### 3.1 架构选型

**默认**：多 TAB 单文件 SPA（所有 TAB 内联，通过 JS 切换）

```html
<!-- SPA 骨架 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${页面标题}</title>
  <style>/* 内联全部样式 */</style>
</head>
<body>
  <header class="spa-header">...</header>
  <nav class="spa-tabs" id="tabNav">...</nav>
  <main class="spa-content" id="tabContent">...</main>
  <script>/* 内联全部逻辑 */</script>
</body>
</html>
```

**例外**：多文件包（>2000行/多子页面/需独立分享某一页） → `index.html` + 每页独立 HTML，iframe 聚合

#### 3.2 响应式框架

**断点策略**：
- Mobile：`< 768px`（手机竖屏）
- Tablet：`768px - 1024px`（平板）
- Desktop：`> 1024px`（桌面）

**移动端优化**：
- 底部 TAB 导航栏（手机操作拇指区）
- 触控滑动切换 TAB（touch swipe）
- 触控点击切换 TAB
- 大按钮/大触控区域
- 简化信息密度（桌面端信息全量，移动端按需展开）

**桌面端优化**：
- 顶部/侧边 TAB 导航栏
- 键盘导航：
  - `←` `→` 或 `Tab` 切换 TAB
  - `Enter` 确认/进入
  - `Escape` 退出弹窗/回到概览
- 悬停态（hover）显示更多信息
- 鼠标滚轮/触摸板横向滚动长列表

#### 3.3 交互规范

| 交互元素 | 桌面端 | 移动端 |
|---------|-------|-------|
| TAB 切换 | 键盘←→/点击/hover | 点击/左右滑动 |
| 详情展开 | 点击/hover展开 | 点击展开 |
| 表单提交 | 键盘回车/点击 | 点击 |
| 弹窗关闭 | 点击X/ESC键/点击遮罩 | 点击X/点击遮罩 |
| 滚动 | 滚轮/触摸板 | 手指滑动 |
| 图表交互 | hover显示tooltip | 点击显示tooltip |

---

### 阶段四：OSS Bucket 权限确认

**⚠️ 必做第一步**：确认目标 Bucket ACL 为「公共读」，否则 URL 无法公开访问。

```python
import oss2
auth = oss2.Auth('REDACTED', 'REDACTED')
bucket = oss2.Bucket(auth, 'oss-cn-hongkong.aliyuncs.com', 'clawshell-vault')
acl = bucket.get_bucket_acl()
print('Bucket ACL:', acl.acl)
# private → 无法公开访问，需改 ACL
# 改法：OSS 控制台 → 基础设置 → Bucket 权限管理 → 改为「公共读」
```

**如果 Bucket 是 private**：CDP 访问测试会得到 `<Error><Code>AccessDenied</Code>...` 的 XML 页面，而不是目标 HTML。可选方案：
- 方案A（推荐）：OSS 控制台改 Bucket ACL 为「公共读」
- 方案B：改完 ACL 之前跳过 CDP 验证，改为 `curl -I` 检查文件是否存在 + 上传成功即视为通过
- 方案C：使用签名 URL（有效期内的临时访问链接）供 CDP 测试

### 阶段五：页面校验

对阶段二、阶段三产出的**所有 HTML 页面**（功能性页面 + 展示性页面）逐一进行校验，不通过则修复后再继续：

#### 功能性页面交付前必查清单 ⚠️

**所有按钮必须通过以下校验方可交付：**

| # | 检查项 | 通过标准 |
|---|--------|---------|
| 1 | 英雄区「立即预订」按钮 | href 指向真实报名页（`.html` 页面或飞书表单 URL），禁止 `#contact` + alert |
| 2 | 导航栏「立即预订」CTA | 同上，禁止空跳转 |
| 3 | 价格卡片「立即预订」按钮 | 同上 |
| 4 | 社群入口按钮（微信/飞书/钉钉） | `weixin://` / `applink.feishu.cn/...` / `dingtalk://` 协议链接完整，无引号残缺 |
| 5 | 「返回顶部」按钮 | `href="#"` |
| 6 | HTML 内无行内注释打断标签 | 无 `<!--` 出现在 `<a>` 或 `<button>` 标签内部 |
| 7 | 所有 href 值已填写 | 无 `href=""` 空值，无 `href="#"` + 无 JS 跳转的静默失效按钮 |

**验证方法（每次交付前必做）：**
```python
# 第一步：Python 正则检查所有链接
import re
with open('output/index.html') as f:
    html = f.read()
links = re.findall(r'<a[^>]+href="([^"]+)"', html)
for href in links:
    assert href != '', f"空 href: {href}"
    assert not (href == '#contact' and 'alert' in html), f"禁止 #contact+alert"
print(f"共 {len(links)} 个链接，全部通过校验")
```

**⚠️ 必须用 Playwright 做真实浏览器 CDP 验证（功能性页面的最后一道关）**

> **执行环境注意**：Playwright 只能通过 `terminal()` 调用（系统级 Python），不能通过 `execute_code` sandbox（独立 venv 无 playwright 包）。验证脚本必须用 `terminal` 工具执行。

所有功能性页面在部署后，必须用 Playwright headless 模式验证以下 7 项，有一项不通过则修复后重新验证：

```python
from playwright.sync_api import sync_playwright

def full_verify(url):
    """功能性页面完整验证协议"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # ① 页面能加载且有内容
        page.goto(url, timeout=15000)
        assert len(page.content()) > 1000, "页面内容为空"

        # ② 检查 hero::before 没有拦截点击（高频根因）
        hero_before_ptr = page.evaluate(
            "getComputedStyle(document.querySelector('.hero'),'::before').pointerEvents"
        )
        assert hero_before_ptr == 'none', f"hero::before pointer-events={hero_before_ptr}，会拦截按钮点击"

        # ③ 所有 CTA 按钮 href 有效
        ctas = page.query_selector_all('.btn-primary, .nav-cta, .cta-button')
        for btn in ctas:
            href = btn.get_attribute('href')
            assert href and href != '#', f"按钮 href 无效: {href}"
            assert not (href == '#contact'), "禁止 #contact 空跳转"

        # ④ 返回顶部按钮
        back_top = page.query_selector('.back-to-top, [href="#"]')
        assert back_top, "缺少返回顶部按钮"

        # ⑤ 锚点跳转 hash 保留（如果有锚点区块）
        if page.query_selector('#experience, #pricing, #contact'):
            page.click('a[href="#experience"]')
            page.wait_for_timeout(800)
            hash_val = page.evaluate("window.location.hash")
            assert hash_val == '#experience', f"锚点hash丢失，当前: {hash_val}"
            # 验证 scroll-margin-top 生效
            section_top = page.evaluate(
                "document.querySelector('#experience').getBoundingClientRect().top"
            )
            assert 60 <= section_top <= 90, f"#experience 距顶 {section_top}px，应在60-90px（导航栏下方）"

        # ⑥ 控制台零错误
        errors = []
        page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
        page.reload()
        page.wait_for_timeout(1500)
        assert len(errors) == 0, f"控制台错误: {errors}"

        # ⑦ 报名/社群按钮跳转验证（通过 URL 变化判断，不真正跳转）
        if page.query_selector('a[href*="book.html"]'):
            with page.expect_navigation(timeout=5000):
                page.click('a[href*="book.html"]')
            assert 'book.html' in page.url, f"报名页跳转失败: {page.url}"

        browser.close()
        print("✅ Playwright 完整验证通过")
        return True
```

⚠️ **重要**：在没有 Node.js 环境的机器上，可以用 Python `subprocess` 调用系统 Playwright CLI；也可以用 Python `playwright` 包（`pip install playwright && playwright install chromium`）。禁止跳过此验证步骤。

#### 在线页面验证（必须执行）

**⚠️ 部署后必须用 Playwright 验证页面可正常加载**：

```python
from playwright.sync_api import sync_playwright

def verify_online_page(url):
    """验证在线页面可访问且结构正确"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=15000)
        title = page.title()
        content = page.content()
        print(f'Title: {title}')
        print(f'Content length: {len(content)}')
        # 检查TAB/导航元素
        tabs = page.query_selector_all('.tab-btn, [role=tab], nav a, .spa-tab')
        print(f'Tabs found: {len(tabs)}')
        page.wait_for_timeout(2000)
        browser.close()
        return len(content) > 1000  # 内容非空即通过
```

**Bucket ACL 预检（防止部署后无法访问）**：
```python
import oss2
auth = oss2.Auth('REDACTED', 'REDACTED')
bucket = oss2.Bucket(auth, 'oss-cn-hongkong.aliyuncs.com', 'clawshell-vault')
acl = bucket.get_bucket_acl()
if acl.acl == 'private':
    print('⚠️ Bucket是私有！部署后URL无法公开访问，需先在OSS控制台改为「公共读」')
```

#### 通用校验（所有页面必须通过）

| 校验维度 | 检查项 | 通过标准 |
|---------|-------|---------|
| **完整性** | 所有计划 TAB 页面均已实现，无遗漏 | 每个 TAB 都有对应内容区块 |
| **功能有效性** | 按钮/链接/表单/TAB切换等均有响应 | 点击/触发有视觉或逻辑反馈 |
| **页面可读性** | 文字清晰、层级分明、图文比例合理 | 无文字重叠/溢出/截断 |
| **内容一致性** | 与原始文档信息一致 | 关键数据/结论/名称与原始内容一致 |
| **信息呈现** | 关键信息有视觉突出 | 核心数字/结论/标题在首屏或视觉焦点区一眼可见 |
| **响应式布局** | 桌面端+移动端均可正常浏览 | 三断点（<768px/768-1024px/>1024px）均不断裂、不错位 |
| **交互体验** | 所有声明的交互逻辑均已实现并可响应 | 桌面键盘+移动触控均有对应响应 |
| **代码质量** | HTML 结构语义化、无死链、内联样式不污染 | 可用浏览器 DevTools 检查 |

#### 功能性页面附加校验

| 校验维度 | 检查项 | 通过标准 |
|---------|-------|---------|
| **数据完整性** | 表单/列表/看板等的数据结构与设计一致 | 数据字段齐全，示例数据真实 |
| **操作路径** | 主操作路径（增删改查/提交/审批）无断点 | 每步操作有明确下一步指引 |
| **状态覆盖** | 空状态、加载中、错误、权限不足等异常情况均已处理 | 页面不出现空白崩溃 |
| **键盘交互** | 桌面端键盘可完成核心操作 | Tab/Enter/Esc 符合预期 |

#### 展示性页面附加校验

| 校验维度 | 检查项 | 通过标准 |
|---------|-------|---------|
| **可视化有效性** | 甘特图/架构图/趋势图等图形元素渲染正确 | 图形可读、标注清晰 |
| **信息密度** | 桌面端全量信息，移动端按需展开 | 不因信息过载导致可读性下降 |
| **视觉一致性** | 多 TAB 视觉风格统一（色彩/字体/间距/动效） | 无跳脱感 |
| **导出兼容性** | 嵌入的 PDF/视频 在主流浏览器可查看 | 不依赖特定插件 |

---

### 阶段六：OSS 上传与部署

**Python 部署脚本**：

```python
import oss2, os, glob, time, hashlib

auth = oss2.Auth('REDACTED', 'REDACTED')
bucket = oss2.Bucket(auth, 'https://oss-cn-hongkong.aliyuncs.com', 'clawshell-vault')

def slugify(name):
    """生成 URL 友好的目录名"""
    import re
    s = name.strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[-\s]+', '-', s)
    return s[:40]  # 限制长度

def deploy_spa(local_dir, project_name):
    """
    部署 SPA 应用到 OSS WEB-SPA 目录
    返回: (main_url, all_urls)
    """
    slug = slugify(project_name)
    prefix = f'web-spa/{slug}/'

    # 上传所有文件
    files = glob.glob(os.path.join(local_dir, '**', '*'), recursive=True)
    uploaded = []
    for filepath in files:
        if os.path.isfile(filepath):
            rel = os.path.relpath(filepath, local_dir).replace('\\', '/')
            oss_key = f'{prefix}{rel}'.lstrip('/')
            bucket.put_object_from_file(oss_key, filepath)
            uploaded.append(oss_key)

    # 找主文件
    main_files = ['index.html', 'main.html', 'default.html']
    main_url = None
    for mf in main_files:
        if mf in [os.path.basename(f) for f in uploaded]:
            main_url = f'https://gzzhike.cn/{prefix}{mf}'
            break

    return main_url, uploaded

def deploy_static_package(local_file, project_name):
    """
    部署单个静态文件（如 PDF、视频直接上传）
    返回: url
    """
    slug = slugify(project_name)
    fname = os.path.basename(local_file)
    oss_key = f'web-spa/{slug}/{fname}'
    bucket.put_object_from_file(oss_key, local_file)
    return f'https://gzzhike.cn/{oss_key}'
```

**目录命名规则**：

| 场景 | OSS 路径 |
|------|---------|
| SPA 应用 | `web-spa/{项目名-slug}/index.html` |
| 多文件包 | `web-spa/{项目名-slug}/`（含所有文件） |
| 嵌入型内容包 | `web-spa/{项目名-slug}/index.html`（含 embed 页面） |
| 单独 PDF/视频 | `web-spa/{项目名-slug}/{文件名}` |

**访问地址格式**：
- 主页面：`https://gzzhike.cn/web-spa/{slug}/index.html`
- 多页包主文件：由部署函数返回的具体 URL

---

### 阶段七：交付清单

向用户交付：

1. **访问链接**：`https://gzzhike.cn/web-spa/{slug}/index.html`
2. **功能说明**：页面支持哪些交互操作
3. **移动端适配**：在手机浏览器打开体验是否正常
4. **如有多 TAB**：说明各 TAB 的内容和切换方式
5. **如含嵌入内容**：说明 PDF/视频 等的查看方式
6. **如有多页面包**：提供主页面链接，各子页面从主页面进入

---

## 复盘：暑假营销活动项目（2026-05-26）最佳实践

### 项目背景
同时交付内部执行手册（飞书文档）和对外宣传页（HTML SPA），双轨并行。

### 沉淀下来的关键规范

**① 功能性页面必须先规划按钮承接，再写 HTML**
- 「立即预订」→ 报名表单页（`book.html`），表单提交后跳转飞书群
- 不能用 `#contact` + `alert('请联系客服')` 敷衍，这是用户立刻能发现的功能性缺陷
- 报名页字段：姓名、手机、项目、日期、人数、备注

**② hero::before 伪元素会拦截按钮点击**
- 症状：按钮视觉正常，但 Playwright 报错 `<section> intercepts pointer events`
- 根因：hero 背景的 `::before { position:absolute; inset:0; pointer-events:auto }` 透明纹理层覆盖在按钮之上
- 修复：在 `::before` 末尾加 `pointer-events: none`

**③ 锚点跳转用 `scrollIntoView` + `pushState`，不要用 `scrollTo`**
- `window.scrollTo({ top: offset })` 在某些浏览器 smooth scroll 完成后会丢失 URL hash
- 正确做法：`target.scrollIntoView({ behavior: 'smooth', block: 'start' })` + `history.pushState(null, '', href)`
- 锚点目标 section 必须加 `scroll-margin-top: 72px`（导航栏高度 64px，留 8px 缓冲）

**④ 价格卡片多行时每行独立 flex 容器**
- 跨行 grid 的 `align-items: stretch` 只对单行生效，多行价格卡每行需单独 `div.price-grid`
- 卡片内部用 `flex-direction: column` + `flex: 1` 让内容区自动填满，底部按钮永远在同一行

**⑤ 飞书群链接不能有引号残缺**
- `href="https://applink.feishu.cn/client/minimalist/h5?code=*** target="` 这种引号残缺会打断整个 DOM
- 没有真实 code 时，先写完整 URL 结构（去除 code 参数），禁止留残缺引号

**⑥ 部署后必须用 Playwright 真实浏览器验证**
- Python re 检查只能验证链接格式，无法发现 `::before` 拦截、hash 丢失等运行时问题
- Playwright CDP 验证 7 项（页面加载、::before 拦截、CTA href、返回顶部、锚点 hash 保留、控制台错误、报名跳转）
- 没有 Node.js 时用 `pip install playwright && playwright install chromium` 的 Python 版

---

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| 页面按钮点击无响应（英雄区/价格卡） | 排查：① href 是不是 `#contact` + JS alert ② 标签内是否有 `<!-- 注释 -->` 打断 HTML 解析；两个都是高频低级错误 |
| 社群跳转链接引号残缺（如 `code=*** target="`） | href 引号不闭合是 HTML 解析致命错误，会打断整个 DOM；出现此问题整页按钮失效；用 `patch` 工具精确定位修复，不要用全局替换 |
| 「返回顶部」按钮跳到中间锚点 | 必须用 `href="#"`，JS 已处理 scroll-to-top；不能用 `#pricing` 等中间锚点 |
| 按钮层被 `::before` / `::after` 伪元素拦截 | hero 或卡片背景的 `::before` 使用 `position:absolute; inset:0` 时，即使透明也会拦截点击；必须显式加 `pointer-events: none`，Playwright 报错 `<section> intercepts pointer events` 即为此因 |
| 锚点跳转后 URL hash 丢失 | 原生 `scrollTo` + offset 计算会在某些浏览器丢失 hash；改用 `target.scrollIntoView()` + `history.pushState(null,'',href)` 保留 hash；锚点目标 section 需加 `scroll-margin-top: 72px` 防止被固定导航栏遮挡 |
| 访问 URL 返回 `<Error><Code>AccessDenied</Code>` XML | Bucket ACL 是 private，需改为「公共读」；或改前用签名 URL 测试 |
| 部署后页面 URL 返回 `200 text/html` 但内容为空/只有框架 | 用 Playwright 打开页面，检查 title/content length/TAB 元素数量，缺一不可 |
| 部署后页面空白/JS 报错 | 用 `browser_console` 检查控制台错误；检查是否有跨域/CDN 缓存/资源路径问题 |
| 飞书文档读取失败（工具报错 "Feishu client not available"） | 改用 Python REST API 调用（见阶段一步骤1），不要终止流程 |
| 内容为空/无效 | 终止流程，请用户补充内容 |
| OSS 上传失败 | 检查网络，3次重试，失败则提供本地文件供用户手动上传 |
| 嵌入资源（PDF/视频）无法访问 | 降级为下载链接，在页面提供"点击下载" |
| 响应式断点判断失误 | 优先保证移动端可用，桌面端在窄窗口手动测试 |
| 内容理解偏差 | 在需求确认阶段向用户重述理解，等用户纠正 |

---

## 内容产出原则

- **内容 = 结果性信息**，不含推导过程
- **HTML 自包含**：样式和脚本全部内联，单文件即可运行
- **代码即文档**：HTML 结构命名语义化（`<nav>`/`<section>`/`<article>`）
- **关键数据视觉化**：数字用大字号/对比色突出
- **渐进增强**：基础内容在低版本浏览器也能看，交互在支持环境增强
