---
name: travel-knowledge
description: 贵州旅游资源知识库 — 查询飞书 Wiki 中已采集的旅游资讯（景点/酒店/交通/政策/活动），内置 24 类信息过期规则，为行程规划提供结构化背景知识。
triggers:
  - "查一下XX景点信息"
  - "知识库里有没有XX"
  - "贵州XX的最新消息"
  - "搜一下知识库"
  - "调用知识库"
tags: [travel, knowledge, search, expiry, 贵州之客]
category: travel
---

# travel-knowledge — 贵州旅游资源知识库

> **定位：** 旅游信息智能采集系统的查询接口。上游由 cronjob 定时填充，下游为 travel-itinerary / travel-marketing 等技能提供结构化背景知识。

## 知识库部署

| 存储节点 | Wiki Token | 内容类型 |
|----------|-----------|---------|
| 行业资讯 | `V0Lhwl7KYiWYDDk1vCncv2GhnYf` | 景点/酒店/交通/政策/活动/天气 |
| 竞品动态 | `EAMYw1CPoipVWtkObbtcR2oDnNc` | 竞品价格/新品/营销/社媒 |

父节点：`J4EewYIT2ieFuwkRWbxcgWbFnhe`（AI Native 工作流）

---

## 核心工作流

### 1. 关键词搜索知识库

```bash
# 全文搜索知识库文档
lark-cli docs +search --query "<关键词>" --as user
```

回退方案（--as user 未配置时）：
```bash
# 列出知识库节点，按标题匹配
lark-cli wiki +node-list --space-id 7643710721485753535 --parent-node-token V0Lhwl7KYiWYDDk1vCncv2GhnYf --as bot | python3 -c "
import sys, json
nodes = json.load(sys.stdin)['data']['nodes']
matches = [n for n in nodes if '<关键词>' in n.get('title','')]
print(json.dumps(matches, ensure_ascii=False, indent=2))
"
```

### 2. 读取匹配文档

```bash
lark-cli docs +fetch --api-version v2 --doc <obj_token> --as bot
```

### 3. 过期校验

**读取文档后，按文档标题中的日期前缀（`YYYY-MM-DD_类型_主题`）和内容类型，判断信息时效性。**

#### A. 旅游资源信息过期规则（16 种类型）

| 类型 | 有效期 | 过期处理 |
|------|--------|---------|
| 政策法规（国家级） | 12个月 | 仅标注，不降权 |
| 政策法规（地方/临时） | 3-6个月 | ⚠️ 可能已过期，降权 ↓30% |
| 景点基础信息 | 永久 | 标注最后核实日 |
| 门票/开放时间 | 3个月 | ⚠️ 请核实最新，降权 ↓50% |
| 酒店价格 | 1个月 | ❌ 已过期，降权 ↓80% |
| 酒店设施/房型 | 6个月 | ⚠️ 可能变动，降权 ↓30% |
| 交通时刻表 | 1个月 | ❌ 已过期，降权 ↓80% |
| 交通线路（常态） | 3个月 | ⚠️ 请核实，降权 ↓40% |
| 季节性信息 | 跨季过期 | ❌ 已过期，降权 ↓60% |
| 节庆/活动 | 活动后7天 | ❌ 活动已结束，降权 ↓90% |
| 天气/气候 | 2周 | ❌ 已过期，降权 ↓80% |
| 旅游攻略/游记 | 6个月 | ⚠️ 时效性降低，降权 ↓40% |
| 酒店评价/口碑 | 3个月 | ⚠️ 时效性降低，降权 ↓50% |
| 交通价格 | 1个月 | ❌ 已过期，降权 ↓80% |
| 景区公告 | 公告截止+3天 | ❌ 已失效，降权 ↓90% |
| 行业报告/白皮书 | 6个月 | ⚠️ 时效性降低，降权 ↓40% |

#### B. 竞品动态过期规则（8 种类型）

| 类型 | 有效期 | 过期处理 |
|------|--------|---------|
| 竞品价格变动 | 1个月 | ❌ 已过期，降权 ↓70% |
| 竞品新品上线 | 3个月 | ⚠️ 上线超3月，降权 ↓50% |
| 竞品营销活动 | 活动后1周 | ❌ 已结束，降权 ↓70% |
| 竞品社媒动态 | 2周 | ❌ 已过期，降权 ↓90% |
| 行业政策/法规 | 6个月 | ⚠️ 可能更新，降权 ↓30% |
| 行业趋势报告 | 3个月 | ⚠️ 时效性降低，降权 ↓40% |
| 文旅厅通知 | 截止+3天 | ❌ 已失效，降权 ↓90% |
| 社媒热议话题 | 1周 | ❌ 热度已过，降权 ↓90% |

### 4. 输出格式

对每个命中的文档，返回：

```
📄 文档标题
  类型：<信息类型>
  采集日期：YYYY-MM-DD
  有效期至：YYYY-MM-DD（或"永久"）
  状态：✅ 有效 / ⚠️ 即将过期 / ❌ 已过期
  权重：100% → 经降权后 XX%
  摘要：<核心内容 100 字>
  链接：<飞书文档链接>
```

**对 travel-itinerary 调用方，只返回权重 ≥ 30% 的结果。**

---

## 信息采集周期（cronjob 填充节奏）

| 周期日 | 采集类别 | 关键词示例 |
|:------:|---------|-----------|
| Day 1 | 景点 | 贵州5A景区、黄果树瀑布、荔波小七孔 |
| Day 2 | 酒店 | 贵阳五星级酒店、贵州民宿、黔东南特色客栈 |
| Day 3 | 交通 | 贵阳荔波动车、贵州自驾游、支线机场航班 |
| Day 4 | 政策 | 贵州文旅厅政策、旅游优惠、旅游条例 |
| Day 5 | 活动 | 贵州节庆、山地旅游大会、户外运动赛事 |
| Day 6 | 综合 | 轮空或补采集上周热点 |

---

## 周度综合洞察分析 (Insight Layer)

> **定位**：在采集层之上，对本周所有文档进行 LLM 多维度交叉分析，生成可执行的战略洞察报告。

### Insight Cron

| Job ID | 调度 | 输出 |
|--------|------|------|
| `84cabcfe3d10` | 每周六 10:00 | 综合洞察报告 → 贵州之客群 |

### 分析维度（6 维）

1. **行业趋势信号** — 识别 3-5 个趋势，每个含：描述 + 证据来源（引用文档标题）+ 影响评估
2. **竞品态势图谱** — 四方向（探洞/天坑/桨板/坝盘）活跃度热力 + 威胁等级标注 + 新动作识别
3. **政策与合规窗口** — 政策变化汇总 + 红利窗口期 + 合规风险
4. **供需缺口与机会** — 2-3 个具体可操作的产品/运营建议
5. **风险与预警** — 按紧急度排序（本周/本月/趋势性）
6. **下周采集建议** — 基于本周发现的重点方向 + 关键词优化

### 报告输出

- **完整报告**：飞书文档 → 行业资讯节点 (V0Lhwl7KYiWYDDk1vCncv2GhnYf)，命名 `{YYYY}_{WW}周_综合洞察分析`
- **群摘要**：≤3000 字符纯文本，含核心发现 + 趋势 + 竞品 + 风险 + 机会 + 文档链接

### 已验证案例

2026 年第 22 周洞察分析识别出：
1. 马蜂窝安顺三大探洞项目（直接威胁）⚠️
2. 桨板 SUP 蓝海窗口（零竞品动态）
3. 采集管道噪音问题（Bing 通用搜索 vs 行业垂直情报）

---

## 与 travel-itinerary 的集成点

在 travel-itinerary Step 3a 中：

1. 调用本技能搜索目的地相关存量文档
2. 获取未过期的景点信息、住宿建议、交通提示
3. 标注"来自知识库（采集日期：YYYY-MM-DD）"
4. 过期但仍可参考的信息标注"⚠️ 信息可能已过期，建议交叉验证"
5. 知识库未覆盖的信息 → 触发 web_search 补充

---

## 搜索方法

### 主方案：Chromium `--dump-dom` + 站点首页抓取（WSL 本地 cron 使用）

**这是当前生产环境中实际运行的方案**。双通道采集：
1. Bing 搜索：Chromium `--dump-dom` 直搜（task_poller.py）
2. 站点抓取：Python urllib 抓取 5 个行业站首页（site_scraper.py）

```python
import subprocess, os, re, urllib.parse

# 清理代理环境变量
for k in list(os.environ.keys()):
    if 'proxy' in k.lower():
        del os.environ[k]

CHROME = os.path.expanduser("~/.chromium/chrome-linux/chrome")
keyword = "搜索关键词"
url = f"https://www.bing.com/search?q={urllib.parse.quote(keyword)}&setlang=zh-Hans"

proc = subprocess.run(
    [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
     "--no-first-run", "--no-proxy-server", "--dump-dom", url],
    capture_output=True, text=True, timeout=30
)

html = proc.stdout
# 正则提取标题 + URL + 摘要
titles = re.findall(r'<h2[^>]*>.*?<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
snippets = re.findall(r'<p[^>]*class="[^"]*b_lineclamp[^"]*"[^>]*>(.*?)</p>', html, re.DOTALL)

results = []
seen = set()
for url, title_raw in titles:
    url = url.strip()
    if url in seen or 'bing.com' in url or 'microsoft.com' in url:
        continue
    title = re.sub(r'<[^>]+>', '', title_raw).strip()
    if len(title) < 8:
        continue
    seen.add(url)
    results.append({"title": title, "url": url, "snippet": ""})
```

> 完整实现见 `scripts/task_poller.py`（WSL crontab 轮询器）+ `scripts/site_scraper.py`（行业站点抓取器）。

### 行业站点直抓（补充 RSS 盲区）

国内旅游行业 RSS 极度稀缺（35+ 站点探测仅品橙旅游有 RSS）。`site_scraper.py` 通过 Python urllib 首页抓取补充 5 个站点：

| 站点 | 编码 | 平均产出 |
|------|------|---------|
| 环球旅讯 traveldaily.cn | utf-8 | 1-3 篇 |
| 执惠旅游 tripvivid.com | utf-8 | 5-8 篇 |
| 8264户外 8264.com | **gbk** | 2-5 篇 |
| 贵州文旅厅 whhly.guizhou.gov.cn | utf-8 | 8-12 篇 |
| 中国旅游报 ctnews.com.cn | utf-8 | 10-15 篇 |

```bash
cd ~/.hermes-feishu/scripts && python3 site_scraper.py --output json
```

### 备选方案：agent-browser daemon（交互式/手动查询）

#### 环境要求

- Chromium 150 @ `~/.chromium/chrome-linux/chrome`
- agent-browser 0.27.0 @ `~/.local/bin/agent-browser`
- ⚠️ 使用前必须 `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY`

#### 可用平台

| 平台 | 方式 | 状态 |
|------|------|:--:|
| **Bing 通用** | 直搜 + eval 提取 | ✅ |
| **B站** | 直搜 `search.bilibili.com` | ✅ |
| **微博/知乎/小红书/抖音/头条/公众号** | Bing `site:` 聚合 | ✅ |

> ⚠️ 微博/知乎/小红书直搜被反爬拦截，必须走 Bing `site:` 路由。

#### 通用搜索（Bing）
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY
QUERY="关键词"
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUERY'))")
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

### 云端降级（Cron 环境 agent-browser/Chromium 不可用）
| 优先级 | 方法 |
|--------|------|
| 1 | `web_search` 工具（Hermes 内置） |
| 2 | `curl` Bing/DuckDuckGo |

### 搜索结果处理

1. 过滤：剔除广告、无关内容、低质量来源
2. 可信度分级：gov.cn/官方=high，知名OTA/媒体=medium，个人/论坛=low
3. 按 16 种过期规则标注每条信息的有效期
4. 生成 Lark XML 文档（≥4 种 block 类型）

### 云端→本地任务队列

> 详细架构见 `references/cloud-local-task-queue.md`。轮询器脚本见 `scripts/task_poller.py`。

Bitable 任务队列路由规则：任务名以 `竞品_` 开头 → 文档存入竞品动态节点 `EAMYw1CPoipVWtkObbtcR2oDnNc`；其余 → 行业资讯节点 `V0Lhwl7KYiWYDDk1vCncv2GhnYf`。

品橙旅游 RSS 为唯一可用的标准 RSS 源（`blogwatcher-cli scan "品橙旅游"`）。

## Cron 任务推送配置

> 详细格式参考和 prompt 模板见 `references/cron-delivery-format.md`。
> 云端→本地任务队列架构见 `references/cloud-local-task-queue.md`。
> agent-browser 环境配置见 `references/agent-browser-setup.md`。
> 生产环境轮询器脚本见 `scripts/task_poller.py`。
> 行业站点抓取器见 `scripts/site_scraper.py`。

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

| Job ID | 名称 | 调度 | 说明 |
|--------|------|------|------|
| `22fc10b1731c` | travel-knowledge-collect | 每日 07:00 | 云端采集 + Bitable 任务队列 |
| `7bb67e31398b` | travel-monitor-morning | 每日 08:00 | 竞品早间简报 |
| `d9e08267c622` | travel-monitor-evening | 每日 18:00 | 竞品晚间简报 |
| `7304faf4af71` | travel-monitor-weekly | 每周一 09:00 | 竞品周度分析 |
| `ca0accd38ac8` | travel-expire-check | 每日 03:00 | 信息过期校验 |
| `6f194036f3ae` | travel-task-dispatcher | 每日 07:00 | 写入 Bitable 任务队列（云端→本地桥） |
| `84cabcfe3d10` | travel-insight-weekly | 每周六 10:00 | ⭐ 综合洞察分析（6维LLM分析） |

全部 deliver 到：`feishu:oc_40570cc921ca1f645f8667151c1e85e6`（贵州之客群），dispatcher 为 `local`。

### 完整信息流水线

```
采集层              校验层           分析层
───────            ───────         ───────
每日 03:00          每日 03:00      每周六 10:00
expire-check ────── 过期标记
                    降权标注
每日 07:00
dispatcher ──┐
             ├─→ Bitable 队列
WSL poller ──┘    ↓
              Chromium Bing 搜索
              ↓
              飞书文档入库 ──────────→ insight-weekly
                                         ↓
                                      6维LLM分析
                                         ↓
                                      洞察报告 + 群推送
```

---

## 文档链接格式（强制遵守）

| URL 类型 | 正确格式 |
|---------|---------|
| Wiki 节点页面 | `https://acn3kz7weyc0.feishu.cn/wiki/<node_token>` |
| 文档直链 | `https://acn3kz7weyc0.feishu.cn/docx/<obj_token>` |

⚠️ **禁止使用 `bytedance.feishu.cn` 域名**，该域名返回 404。
⚠️ **禁止用 `obj_token` 拼 `/wiki/` 路径**，会导致链接不存在。

正确示例：
```
https://acn3kz7weyc0.feishu.cn/wiki/HgnhwdbK4iqVFgkttIbcGrS1nXc
https://acn3kz7weyc0.feishu.cn/docx/AcbPdlYy4owB8JxiDeecriXxnnh
```

## 陷阱

1. **文档日期从标题提取** — 命名规范为 `YYYY-MM-DD_类别_主题`，如果标题不规范则无法自动计算过期
2. **过期校验在查询时进行** — 不在 cronjob expire-check 中修改文档内容，而是在知识查询时标注状态
3. **禁止修改 Wiki 节点标题** — 飞书 App 权限不支持 API 重命名，标题污染后只能手动修复。过期标记用 `feishu_drive_add_comment`，不要改标题
4. **竞品动态与行业资讯分开查询** — 两个 Wiki 节点独立，根据调用方需求选择
4. **`docs +search` 需要 --as user** — 如果用户未登录 CLI（`lark-cli auth login`），回退到 `wiki +node-list` + 标题匹配
5. **本地搜索用 agent-browser** — Bing+B站直搜可用，微博/知乎/小红书走 Bing site: 聚合。云端 Cron 用 web_search+curl 降级
6. **cron 消息有固定包装** — 头部 "Cronjob Response: {name}" 和尾部管理指令是系统格式，不可去除。确保 prompt 有显式摘要输出指令
7. **cron deliver 不用 origin** — 团队汇报必须指定群 chat_id
8. **Feishu 消息长度限制 (99992402)** — agent 输出过长或含复杂格式时推送静默失败。强制约束：≤3000 字符，纯文本 + 基础 markdown。详细内容放文档，消息只含摘要+链接。详见 `references/cron-delivery-format.md`
