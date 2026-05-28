---
name: travel-monitor
description: 竞品与行业监控 — 监控探洞/天坑/桨板竞品动态，采集价格变动、新品上线、营销动作，生成每日简报+周度分析并归档至飞书知识库。含RSS源管理、社交媒体监测、关键词周度动态调整。
triggers:
  - 定时每日简报（cron: 0 8,18 * * *）
  - 定时周度分析（cron: 0 9 * * 1）
  - 手动：travel-monitor query <竞品名>
  - 关键词周度调整（cron: 0 9 * * 1，与周报联动）
  - 信息过期校验（cron: 0 3 * * *）
toolsets: [terminal, web, feishu_doc, feishu_drive, feishu_wiki, browser]
dependencies:
  skills: [feishu-doc, feishu-wiki, blogwatcher]
  commands: [blogwatcher-cli, lark-cli, agent-browser]
---

# travel-monitor — 竞品与行业监控

## 核心身份

你是一个专注于**贵州户外旅游竞品与行业动态**的监控 Agent。你的任务是采集竞品（探洞、天坑、桨板）和行业动态，生成每日简报和周度分析，归档至飞书知识库竞品动态节点下。同时管理 RSS 源和动态关键词库。

---

## 存储结构

| 项目 | 值 |
|------|-----|
| **Space ID** | `7643710721485753535` |
| **父节点 token** | `EAMYw1CPoipVWtkObbtcR2oDnNc` |
| **父节点名称** | 竞品动态 |
| **文档命名规则** | 简报: `{YYYY-MM-DD}_竞品简报` / 周报: `{YYYY}_{WW}周_竞品分析` |

**目录结构：**
```
竞品动态 (EAMYw1CPoipVWtkObbtcR2oDnNc)
├── daily/
│   ├── 2026-05-28_竞品简报.md
│   └── 2026-05-29_竞品简报.md
├── weekly/
│   ├── 2026_22周_竞品分析.md
│   └── 2026_23周_竞品分析.md
├── keywords/
│   └── 关键词库_2026W22.md
└── config/
    └── RSS源配置.md
```

---

## 监控竞品与关键词

### 核心竞品

| # | 竞品方向 | 监测关键词（示例） |
|---|---------|------------------|
| 1 | **探洞** | 贵州探洞、洞穴探险、地下河探险、天窗探险、竖井挑战、绳降探洞 |
| 2 | **天坑** | 天坑探险、天坑速降、平塘天坑群、大石围天坑、天坑研学 |
| 3 | **桨板** | SUP桨板、桨板旅行、贵州桨板基地、红水河桨板、万峰湖桨板 |

### 动态关键词库（按周调整）

**关键词管理层级：**

```
活跃关键词（本周监测）
├── 核心业务词：探洞 天坑 桨板
├── 地域词：贵州户外 黔西南 黔南 罗甸 平塘 荔波 安顺
├── 竞品活动词：探洞体验 桨板培训 天坑研学 户外夏令营
├── 行业趋势词：山地旅游 体旅融合 户外运动 露营经济
├── 社交媒体热词：小红书爆款 抖音热门 B站探洞
└── 季节词（动态注入）：夏季玩水 避暑旅游 暑期亲子
```

**周度调整规则：**

每周一 09:00 执行关键词审计：
1. **提取热词**：统计过去一周所有采集内容的标题/摘要中的高频词（出现 ≥3 次）
2. **新增候选**：高频但不在活跃关键词库中的词 → 加入下周监测
3. **淘汰候选**：连续 2 周 0 命中的词 → 标记 `[休眠]`
4. **季节性注入**：每月 1 日根据当前月份注入季节词：
   - 3-5月：赏花、徒步、春游、清明
   - 6-8月：避暑、玩水、漂流、夏令营、暑期亲子
   - 9-11月：秋色、摄影、国庆黄金周、户外赛事
   - 12-2月：温泉、冰雪、春节旅游、冬令营

---

## 信息源配置

### RSS 源（blogwatcher 管理）

**已验证 RSS 源状态（2026-05-28）：**

| 源名称 | URL | Feed URL | 文章/次 | 状态 | 说明 |
|--------|-----|----------|---------|------|------|
| 品橙旅游 | pinchain.com | `/feed` | 10 | ✅ | 中文旅游行业，唯一可用中文 RSS |
| Skift | skift.com | `/feed/` | 10 | ✅ | 全球旅游行业趋势（英文） |
| ExplorersWeb | explorersweb.com | `/feed/` | 63 | ✅ | 探险/极限运动（英文） |
| Outside-Online | outsideonline.com | `/feed?scope=anon` | 10 | ✅ | 户外运动/装备（英文） |
| 环球旅讯 | traveldaily.cn | — | — | ⚠️ 无RSS | 站内搜索 `/search?keyword=关键词` |
| 执惠旅游 | tripvivid.com | — | — | ⚠️ 无RSS | 首页直接抓取 |
| 8264户外 | 8264.com | — | — | ⚠️ 无RSS | 首页抓取，编码为 gbk |
| 贵州文旅厅 | whhly.guizhou.gov.cn | — | — | ⚠️ 无RSS | 首页抓取，政策/活动信息 |
| 中国旅游报 | ctnews.com.cn | — | — | ❌ 无扫描 | 无 RSS + 无首页抓取 |
| 多彩贵州网 | gog.cn | — | — | ❌ TLS错误 | 无法连接 |

> **探测结论**：国内旅游/户外行业 RSS 极度稀缺。探测了 35+ 个站点（B2B 门户、政府网、门户旅游频道、户外论坛），仅品橙旅游提供标准 RSS。3 个国际源作为行业趋势和极限运动动态的补充。其他 6 个站点需通过首页抓取或站内搜索补充。

### 社交媒体监测（web_search 补充）

| 平台 | 搜索方式 | 优先级 |
|------|---------|--------|
| **小红书** | `site:xiaohongshu.com 贵州探洞` | 高 |
| **B站** | `site:bilibili.com 贵州户外探险` | 高 |
| **抖音** | `site:douyin.com 贵州旅游` | 高 |
| **微博** | `site:weibo.com 贵州文旅` | 中 |
| **微信公众号** | 通用搜索（搜狗微信搜索） | 中 |

---

## 每日简报工作流（Cron：08:00 / 18:00）

### 早间简报（08:00）：RSS 扫描 + 竞品搜索

#### Step 1: 扫描 RSS 源

```bash
blogwatcher-cli scan
```

获取所有 RSS 源的新文章。

#### Step 2: 过滤相关文章

```bash
# 筛选包含竞品关键词的未读文章
blogwatcher-cli articles --all | grep -iE "探洞|天坑|桨板|贵州户外|山地旅游|体旅"
```

#### Step 3: 直接站点抓取补充

**L1 — 抓取5个行业媒体首页，提取标题：**

```python
import urllib.request, ssl, re
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

sites = [
    ("品橙旅游", "https://www.pinchain.com/"),
    ("执惠旅游", "https://www.tripvivid.com/"),
    ("环球旅讯", "https://www.traveldaily.cn/"),
    ("8264户外", "https://www.8264.com/"),
    ("贵州文旅厅", "https://whhly.guizhou.gov.cn/"),
]
FILTER_KW = "探洞|洞穴|溶洞|天坑|桨板|SUP|漂流|溯溪|户外|山地|体旅|营地|徒步|研学|贵州"

for name, url in sites:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    resp = urllib.request.urlopen(req, timeout=10, context=ssl_ctx)
    html = resp.read()
    enc = 'gbk' if '8264' in url else 'utf-8'
    text = html.decode(enc, errors='ignore')
    titles = re.findall(r'<a[^>]*>(.{8,100})</a>', text)
    for t in titles:
        t_clean = re.sub(r'<[^>]+>', '', t).strip()
        if re.search(FILTER_KW, t_clean):
            print(f"[{name}] {t_clean}")
```

**L2 — 站内搜索深入（品橙 + 环球旅讯）：**

```python
# 品橙旅游站内搜索"贵州"
req = urllib.request.Request("https://www.pinchain.com/?s=" + urllib.parse.quote("贵州"), headers=...)
# 环球旅讯站内搜索
req = urllib.request.Request("https://www.traveldaily.cn/search?keyword=" + urllib.parse.quote("贵州"), headers=...)
```

**L3 — 对高价值线索抓取全文**（见上方 L3 模板）。

#### Step 4: 生成每日简报文档

使用 Lark XML 格式，模板如下：

```xml
<title>{YYYY-MM-DD}_竞品简报</title>

<callout emoji="📊" background-color="light-blue" border-color="blue">
  <p><b>采集时间：{YYYY-MM-DD HH:00} ｜ 简报类型：{早间/晚间}</b></p>
  <p>监测竞品：探洞 · 天坑 · 桨板 | 信息源：RSS + Web</p>
</callout>

<h1>📈 本日概览</h1>
<grid>
  <column width-ratio="0.33">
    <callout emoji="🕳️" background-color="light-green" border-color="green">
      <p><b>探洞</b></p>
      <p>{N} 条动态</p>
    </callout>
  </column>
  <column width-ratio="0.33">
    <callout emoji="⛰️" background-color="light-yellow" border-color="yellow">
      <p><b>天坑</b></p>
      <p>{N} 条动态</p>
    </callout>
  </column>
  <column width-ratio="0.33">
    <callout emoji="🏄" background-color="light-blue" border-color="blue">
      <p><b>桨板</b></p>
      <p>{N} 条动态</p>
    </callout>
  </column>
</grid>

<h1>🔴 重要动态（高优先级）</h1>

<h2>1. {标题}</h2>
<callout emoji="🔴" background-color="light-red" border-color="red">
  <p><b>类型：价格变动 / 新品上线 / 营销大动作</b></p>
  <p>来源：{来源} ｜ 日期：{日期} ｜ 竞品：{竞品名}</p>
  <p><a href="{URL}">查看原文</a></p>
</callout>
<p>{摘要}</p>
<ul>
  <li>影响评估：{对贵州之客的潜在影响}</li>
  <li>建议动作：{应对建议}</li>
</ul>
<hr/>

<h1>🟡 常规动态</h1>
<!-- 同上结构，callout 用 light-yellow/yellow -->

<h1>🟢 行业资讯</h1>
<!-- 非竞品但行业相关的政策/趋势信息 -->

<h1>🔍 新关键词发现</h1>
<callout emoji="💡" background-color="light-green" border-color="green">
  <p><b>本周新发现高频词：</b></p>
  <ul>
    <li>{新词1} — 出现 {N} 次</li>
    <li>{新词2} — 出现 {N} 次</li>
  </ul>
  <p>将在下周关键词审计中决定是否纳入监测。</p>
</callout>

<h2>后续行动</h2>
<checkbox done="false">高优先级动态同步到运营团队</checkbox>
<checkbox done="false">新关键词标记待审计</checkbox>
```

#### Step 5: 创建文档到知识库

```bash
cd /tmp
cat > monitor_daily.xml << 'XMLEOF'
[XML内容]
XMLEOF

lark-cli docs +create \
  --api-version v2 \
  --doc-format xml \
  --content @monitor_daily.xml \
  --parent-token EAMYw1CPoipVWtkObbtcR2oDnNc \
  --as bot
```

> **晚间简报（18:00）**：流程相同，但仅扫描 RSS（不重复执行 web_search），凌晨到 18:00 之间的 RSS 更新。

---

## 周度分析工作流（Cron：每周一 09:00）

### Step 1: 汇总过去一周的每日简报

```bash
# 读取 daily/ 目录下过去 7 天的简报
lark-cli wiki +node-list \
  --space-id 7643710721485753535 \
  --parent-node-token EAMYw1CPoipVWtkObbtcR2oDnNc \
  --as bot
```

提取 daily/ 下最近 7 个文档的内容摘要。

### Step 2: 统计与聚合

- 本周 {N} 条动态（高优 {N} / 常规 {N} / 行业 {N}）
- 各竞品活跃度排名
- 动态类型分布（价格变动 / 新品 / 营销 / 政策 / 其他）
- 对比上周变化趋势

### Step 3: 生成周度分析文档

```xml
<title>{YYYY}_{WW}周_竞品分析</title>

<callout emoji="📊" background-color="light-blue" border-color="blue">
  <p><b>分析周期：{YYYY-MM-DD} ~ {YYYY-MM-DD} ｜ 第 {WW} 周</b></p>
</callout>

<h1>📈 本周数据看板</h1>
<table>
  <thead><tr><th>指标</th><th>本周</th><th>上周</th><th>变化</th></tr></thead>
  <tbody>
    <tr><td>动态总数</td><td>{N}</td><td>{N}</td><td>{trend}</td></tr>
    <tr><td>高优动态</td><td>{N}</td><td>{N}</td><td>{trend}</td></tr>
    <tr><td>竞品活跃度</td><td>探洞{N} 天坑{N} 桨板{N}</td><td>...</td><td>...</td></tr>
  </tbody>
</table>

<whiteboard type="mermaid">
graph LR
    A[本周动态 {N}条] --> B[高优 {N}条]
    A --> C[常规 {N}条]
    A --> D[行业 {N}条]
    B --> E[价格变动 {N}]
    B --> F[新品上线 {N}]
    B --> G[营销动作 {N}]
</whiteboard>

<h1>🔴 本周重点分析</h1>
<!-- 逐条深度分析本周最重要的 3-5 条动态 -->

<h1>📊 竞品横向对比</h1>
<table>
  <thead><tr><th>竞品</th><th>本周动态</th><th>活跃度</th><th>主要方向</th><th>威胁等级</th></tr></thead>
  <tbody>
    <tr><td>探洞类</td><td>{N}</td><td>{high|medium|low}</td><td>{方向}</td><td>{🟢🟡🔴}</td></tr>
    <tr><td>天坑类</td><td>{N}</td><td>{high|medium|low}</td><td>{方向}</td><td>{}</td></tr>
    <tr><td>桨板类</td><td>{N}</td><td>{high|medium|low}</td><td>{方向}</td><td>{}</td></tr>
  </tbody>
</table>

<h1>🏷️ 关键词审计</h1>
<!-- 周度关键词调整结果 -->

<h1>🎯 建议与行动</h1>
<callout emoji="🎯" background-color="light-green" border-color="green">
  <p><b>本周关键建议</b></p>
  <ol><li seq="auto">{建议1}</li><li seq="auto">{建议2}</li><li seq="auto">{建议3}</li></ol>
</callout>

<h2>后续行动</h2>
<checkbox done="false">周报同步到管理团队</checkbox>
<checkbox done="false">更新关键词库</checkbox>
<checkbox done="false">高威胁竞品制定应对方案</checkbox>
```

### Step 4: 创建周报文档 + 推送

```bash
cd /tmp
cat > monitor_weekly.xml << 'XMLEOF'
[XML内容]
XMLEOF

lark-cli docs +create \
  --api-version v2 \
  --doc-format xml \
  --content @monitor_weekly.xml \
  --parent-token EAMYw1CPoipVWtkObbtcR2oDnNc \
  --as bot
```

### 补充：综合洞察分析（跨节点交叉分析）

> 与上述竞品周报不同，**综合洞察分析**横跨行业资讯 + 竞品动态两个知识库节点，执行 6 维度 LLM 交叉分析（行业趋势/竞品态势/政策窗口/供需缺口/风险预警/采集建议），面向管理层战略决策。完整 prompt 模板和 XML 报告格式见 `references/weekly-comprehensive-insight.md`。

---

## 竞品动态过期规则

| # | 内容类型 | 有效期 | 过期操作 | 权重降幅 |
|---|---------|--------|---------|---------|
| 1 | 竞品价格变动 | 1个月 | 标注 `❌ 价格信息已过期` | ↓70% |
| 2 | 竞品新品上线 | 3个月 | 标注 `⚠️ 上线已超过3个月` | ↓50% |
| 3 | 竞品营销活动 | 活动结束后1周 | 标注 `❌ 活动已结束` | ↓70% |
| 4 | 竞品社交媒体动态 | 2周 | 标注 `❌ 信息已过期` | ↓90% |
| 5 | 行业政策/法规 | 6个月 | 标注 `⚠️ 政策可能更新` | ↓30% |
| 6 | 行业趋势报告 | 3个月 | 标注 `⚠️ 趋势时效性降低` | ↓40% |
| 7 | 文旅厅通知 | 通知截止日后3天 | 标注 `❌ 通知已失效` | ↓90% |
| 8 | 社交媒体热议话题 | 1周 | 标注 `❌ 话题热度已过` | ↓90% |

---

## 搜索方法

### 主方案：RSS + 站点首页抓取（双通道）

**通道 1 — RSS（4 源，blogwatcher 管理）**

| 源 | Feed URL | 文章/次 | 语言 |
|----|----------|---------|------|
| 品橙旅游 | https://www.pinchain.com/feed | 10 | 中文 |
| Skift | https://skift.com/feed/ | 10 | 英文 |
| ExplorersWeb | https://explorersweb.com/feed/ | 63 | 英文 |
| Outside-Online | https://www.outsideonline.com/feed?scope=anon | 10 | 英文 |

```bash
# 逐个扫描（批量扫描遇首个失败即全部中止）
for name in "品橙旅游" "Skift" "ExplorersWeb" "Outside-Online"; do
  blogwatcher-cli scan "$name" || true
done
# 筛选相关文章
blogwatcher-cli articles --all | grep -iE "探洞|天坑|桨板|贵州|户外"
```

**通道 2 — 站点首页抓取（5 站，Python urllib）**

> 脚本：参见 `scripts/site_scraper.py`（travel-knowledge 技能目录）。调用：`python3 site_scraper.py --output json`

| 站点 | 抓取方式 | 编码 | 平均产出 |
|------|---------|------|---------|
| 环球旅讯 | 首页 + 站内搜索「贵州」「户外」 | utf-8 | 1-3 篇/次 |
| 执惠旅游 | 首页 `/N.html` 模式 | utf-8 | 5-8 篇/次 |
| 8264户外 | 首页 `/viewnews-N.html` 模式 | **gbk** | 2-5 篇/次 |
| 贵州文旅厅 | 首页 `title=` 属性提取 | utf-8 | 8-12 篇/次 |
| 中国旅游报 | 首页 `/content-N.html` 模式 | utf-8 | 10-15 篇/次 |

> ⚠️ 8264 编码为 gbk，直接 decode('utf-8') 会乱码。

**环境要求**：Chromium 150 @ `~/.chromium/chrome-linux/`，agent-browser 0.27.0，配置 `~/.agent-browser/config.json`。使用前 `unset` 所有代理环境变量。

| 平台 | 方式 | 适用场景 |
|------|------|---------|
| **Bing 通用** | agent-browser 直搜 + eval 提取 | 竞品动态、行业新闻 |
| **Bing site:** 聚合 | `site:weibo.com OR site:zhihu.com OR ...` | 社交媒体全平台覆盖 |
| **B站** | agent-browser 直搜 `search.bilibili.com` | 户外视频/探洞垂直内容 |
| **品橙旅游** | blogwatcher RSS | 行业综合资讯 |
| **web_search** | Hermes 内置（云端 Cron 降级） | 自动采集 |

#### 搜索模板
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY

# Bing 通用搜索
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('关键词'))")
~/.local/bin/agent-browser open "https://www.bing.com/search?q=$ENCODED&setlang=zh-Hans"
sleep 3
~/.local/bin/agent-browser eval "
Array.from(document.querySelectorAll('#b_results .b_algo')).slice(0,8).map(el => {
  const link = el.querySelector('h2 a');
  const snippet = el.querySelector('.b_caption p, .b_lineclamp2');
  return {title:(link?.textContent||'').trim(), url:link?.href||'', snippet:(snippet?.textContent||'').trim().substring(0,200)};
}).filter(x=>x.title&&x.url)
"
```

> ⚠️ 微博/知乎/小红书直搜被反爬拦截，使用 Bing `site:` 聚合搜索替代。

### 竞品搜索关键词模板
---

### 主力采集：直接站点抓取（Python urllib）

按优先级分3层：

**L1 — 首页直接抓取（最快，覆盖当日头条）：**

```python
import urllib.request, ssl, re
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

sites = [
    ("品橙旅游", "https://www.pinchain.com/"),
    ("执惠旅游", "https://www.tripvivid.com/"),
    ("环球旅讯", "https://www.traveldaily.cn/"),
    ("8264户外", "https://www.8264.com/"),       # encoding: gbk
    ("贵州文旅厅", "https://whhly.guizhou.gov.cn/"),
]
for name, url in sites:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    resp = urllib.request.urlopen(req, timeout=10, context=ssl_ctx)
    html = resp.read()
    # 8264 uses gbk, others utf-8
    text = html.decode('gbk' if '8264' in url else 'utf-8', errors='ignore')
    # Extract titles
    titles = re.findall(r'<a[^>]*>(.{8,80})</a>', text)
    # Filter for Guizhou/outdoor keywords
    ...
```

**L2 — 站内搜索（深入挖掘）：**

| 站点 | 搜索 URL 模板 |
|------|-------------|
| 品橙旅游 | `https://www.pinchain.com/?s={urlencode(关键词)}` |
| 环球旅讯 | `https://www.traveldaily.cn/search?keyword={urlencode(关键词)}` |

**L3 — 文章详情抓取（获取全文）：**

```python
req = urllib.request.Request(article_url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=15, context=ssl_ctx)
html = resp.read().decode('utf-8', errors='ignore')
# Strip scripts/styles, extract text
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '\n', text)
```

### 辅助通道：RSS（品橙旅游唯一可靠源）

```bash
# 逐个扫描（批量扫描遇首个失败即全部中止）
blogwatcher-cli scan "品橙旅游"
```

### 云端降级（Cron 环境 agent-browser 不可用）
| 优先级 | 方法 |
|--------|------|
| 1 | Python urllib 直接抓取行业媒体首页 + 站内搜索 |
| 2 | `web_search` 工具（Hermes 内置） |
| 3 | `curl` Bing/DuckDuckGo |

### 竞品搜索关键词模板（用于站内搜索 + RSS 过滤）

对每个竞品方向，在站点抓取结果中过滤：

| 竞品方向 | 过滤关键词 |
|---------|-----------|
| 探洞 | 探洞\|洞穴\|溶洞\|绳降\|地心\|飞拉达 |
| 天坑 | 天坑\|速降\|平塘\|大石围\|研学 |
| 桨板 | 桨板\|SUP\|水上\|漂流\|溯溪 |

---

## 定时采集工作流（Cron：每日 07:00）

与 travel-knowledge 共用校验逻辑：

1. 列出 `EAMYw1CPoipVWtkObbtcR2oDnNc` 下所有 daily/ 子文档
2. 提取标题日期，与当前日期比较
3. 按上表过期规则标记
4. 对过期文档顶部插入过期 callout 标记

---

## RSS 源维护

### 初始安装 blogwatcher

```bash
# 安装
curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | sudo tar xz -C /usr/local/bin blogwatcher-cli

# 添加源（逐条验证 RSS 可用性）
blogwatcher-cli add "贵州文旅厅" https://whhly.guizhou.gov.cn/
blogwatcher-cli add "品橙旅游" https://www.pinchain.com/
blogwatcher-cli add "环球旅讯" https://www.traveldaily.cn/
```

### 每周维护

每周一执行：
```bash
# 检查 RSS 源健康状态
blogwatcher-cli blogs
# 对失效源标记并尝试修复
```

---

## Cron 任务推送配置

> 详细格式参考和 prompt 模板见 travel-knowledge 技能的 `references/cron-delivery-format.md`。

### 推送格式（不可定制）

所有 cron 任务的消息在群内的格式固定为：

```
Cronjob Response: {任务名} (job_id: {job_id})
<-- cron agent 的最终回复内容 -->
To stop or manage this job, send me a new message (e.g. "stop reminder {任务名}")
```

**头尾是系统包装，不可去除**。群成员可通过头部识别任务来源，通过尾部指令管理任务。

### 推送目标

`deliver` 参数决定消息去向：

| 值 | 效果 |
|----|------|
| `origin` | 推送到 cron 创建时的对话（DM） |
| `feishu:oc_XXXX` | 推送到指定群聊（推荐用于团队可见） |
| `all` | 推送到所有连接的频道 |

**团队汇报场景必须用群 chat_id**（如 `feishu:oc_40570cc921ca1f645f8667151c1e85e6`），不要用 `origin`（会只发到 DM）。

获取群 chat_id：`send_message(action='list')` 查找目标群名。

### Prompt 设计铁律

cron agent 在独立会话中运行，**只会把最终回复推送到群**。如果 prompt 只要求「创建文档」而不要求「输出摘要」，群内只会看到空泛的 "任务完成"。

**每个 cron prompt 必须包含显式的摘要输出指令**，格式如下：

```
**关键：在你的最终回复中输出可见摘要，包括：**
- {具体要包含的信息项 1}
- {具体要包含的信息项 2}
- 创建的文档链接
```

### 已部署的 Cron 任务

| Job ID | 名称 | 调度 | deliver |
|--------|------|------|---------|
| `22fc10b1731c` | travel-knowledge-collect | 每日 07:00 | 贵州之客群 |
| `7bb67e31398b` | travel-monitor-morning | 每日 08:00 | 贵州之客群 |
| `d9e08267c622` | travel-monitor-evening | 每日 18:00 | 贵州之客群 |
| `7304faf4af71` | travel-monitor-weekly | 每周一 09:00 | 贵州之客群 |
| `ca0accd38ac8` | travel-expire-check | 每日 03:00 | 贵州之客群 |

---

## 关键陷阱

| # | 陷阱 | 正确做法 |
|---|------|----------|
| 1 | 大部分中文网站无 RSS，blogwatcher 批量扫描遇首个失败即中止 | 逐个源扫描 `for b in $(...); do blogwatcher-cli scan "$b" || true; done`；主力采集用 web_search |
| 2 | 社交媒体（小红书/B站/抖音）无 RSS | 使用 `site:` 搜索语法或 agent-browser，不依赖 blogwatcher |
| 3 | 竞品信息敏感度不一 | 价格变动标记高优🔴；普通内容标记🟡；行业新闻🟢 |
| 4 | 周报数据量大 | 只摘要关键指标，不逐条搬运；详细数据引用每日简报 |
| 5 | 关键词膨胀 | 休眠关键词定期清理（4周0命中 → 移出活跃库） |
| 6 | web_search 可能返回昨天的结果 | 按时间过滤，标注采集时间精确到小时 |
| 7 | 飞书文档分栏渲染问题 | grid/column 布局可能在某些客户端不显示，用 callout 替代测试后决定 |
| 8 | **搜索引擎受限于云端环境** | 云端 Cron 环境无 Chromium，Bing/Google curl 可能被反爬。使用 Python urllib 直抓行业媒体 + web_search 降级。本地 WSL 可用 Chromium --dump-dom |
| 9 | 过期标记用 append 不可见 | 用 `docs +update --command str_replace` 在 title 后插入 callout |
| 10 | **cron deliver 不用 origin** | 团队汇报必须指定群 chat_id，`deliver: "origin"` 只发到 DM |
| 11 | **cron prompt 缺少摘要指令** | 每个 prompt 必须包含「关键：最终回复输出摘要」段落，否则群内只看到空泛内容 |
| 12 | **cron 消息有固定包装** | 头部 "Cronjob Response: {name}" 和尾部管理指令不可去除，提前告知团队此格式 |
| 13 | **Feishu 消息长度限制 (99992402)** | agent 输出过长或含复杂格式时推送静默失败。强制约束：≤3000 字符纯文本。详见 travel-knowledge 技能 `references/cron-delivery-format.md` |
| 15 | **8264户外 编码为 GBK** | 直接 `decode('utf-8')` 会乱码。用 `html.decode('gbk', errors='ignore')` 或先检测编码再解码 |

---

## 验证清单

每次简报完成后检查：
- [ ] 3 个竞品方向（探洞/天坑/桨板）都有覆盖
- [ ] 高优动态正确标记和处理
- [ ] 文档创建到 `EAMYw1CPoipVWtkObbtcR2oDnNc` 下
- [ ] ≥4 种 block 类型
- [ ] 新关键词已记录

每周报完成后检查：
- [ ] 本周/上周数据对比完整
- [ ] 竞品横向对比表清晰
- [ ] 关键词审计已执行
- [ ] 威胁评估和建议已生成
