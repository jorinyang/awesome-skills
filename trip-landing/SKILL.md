---
name: trip-landing
description: 客户行程落地页一键生成：从飞书方案文档提取行程+客户信息→5 TAB SPA（概览/行程/地图/须知/安全）→4色板个性化→PWA离线→手机验证→高德导航→实时天气→部署OSS→自动清理。触发：生成落地页/生成行程页/做成网页版/生成客户页/行程上线。
triggers:
  - 用户要求根据方案生成客户落地页
  - 用户说「生成行程页」「做成网页」「客户要看」
  - 用户说「把这个方案发布成线上页面」
dependencies:
  - feishu-doc (读取方案)
  - amap MCP (坐标/路线/天气)
  - feishu-html (页面生成/部署)
---

# Trip Landing · 客户行程落地页 v3

## Brief

> **问题陈述**：签约后，客户需要一份清晰、可随身携带、有温度的行程确认——不是 Word 文档，不是飞书链接，而是打开就能用的一站式行程页。页面需同时服务两种场景：出发前的行程准备（查看须知、确认酒店）+ 旅途中动态使用（天气、导航、紧急联系）。

### 核心原则

1. **"打开即用，不要学习"** — 客户只需输入手机号验证，无需注册、下载 App、或学习任何操作
2. **"客户看到的是TA的行程，不是我们的模板"** — 页面承载客户姓名、导游信息、个性化色彩方案，消除"模板感"
3. **"一次生成，全程陪伴"** — 签约后生成→出发前准备→旅途使用→出行后 10 天自动清理；页面陪跑完整生命周期

### 成功标准

- 客户打开率 > 80%（链接发送后 24h 内打开）
- 页面无需客服二次解释行程细节
- 导航按钮在微信内置浏览器中正常跳转高德 App
- PWA 离线模式下页面核心内容（行程+安全）可完整展示
- 行程结束后 10 天页面自动消失，不留隐私痕迹

### 不做什么

- ❌ 不做在线支付/预订功能
- ❌ 不做社交分享墙/游记/评价
- ❌ 不做实时位置追踪
- ❌ 不做多语言（目前仅中文）
- ❌ 不替代飞书方案文档（方案是内部工具，落地页是客户交付物）
- ❌ 不支持人工编辑页面内容（改行程 = 重新生成覆盖）

---

## 架构总览

```
                    ┌── 飞书方案文档 ──────────────┐
                    │ 含：行程 + 客户信息/导游/日期   │
                    │ + 安全/须知/费用等段落          │
                    └──────────────────────────────┘
                                    │
                    extract_trip.py --doc TOKEN
                                    │
                            trip_data.json
                    ┌── 含客户元数据 + 行程 + 坐标 ──┐
                    └──────────────────────────────┘
                                    │
                            build_page.py
                    ┌── 按 trip_type 选模板 ─┐
                    ├── individual: 山峦青    │
                    ├── family: 暖橙         │
                    ├── corporate: 深蓝      │
                    └── study: 竹绿          │
                                    │
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
              index.html        sw.js         manifest.json
              (含验证门禁)      (PWA缓存)       (PWA配置)
                    │
                    ↓
              OSS 部署 (feishu-html)
              https://gzzhike.cn/web-spa/{slug}/
                    │
        ┌───────────┴───────────┐
        ↓                       ↓
  每日 weather cron          清理 cron (或注册的一次性任务)
  fetch_weather.py           cleanup_pages.py
  拉取高德天气 → 更新          trip_end + 10d → 删除 OSS
  weather_{slug}.json          + 更新 registry
```

**关键设计决策**：
- 天气数据独立为 `weather_{slug}.json`，页面 JS 客户端 fetch。每日 cron 只更新 JSON，不重建 HTML。离线时用 SW 缓存的最后一份。
- 手机验证：页面 HTML 内嵌 SHA256(phone)，客户端输入后比对，通过后存 sessionStorage。同设备免重复验证。家人分享时输入同一手机号。
- 页面覆盖：行程变更时重新生成，覆盖同 URL。不需要版本管理。
- 生命周期：行程结束日期 + 10 天后自动清理。生成页面时注册一次性清理任务。

---

## 5 TAB 结构

| TAB | 内容 | 展示方式 | 使用场景 |
|-----|------|---------|---------|
| 📋 **行程概览** | 行程简介、亮点标签云、目的地背景 | 文本卡片 + 标签云 | 出发前浏览 |
| 🗓️ **每日行程** | 逐日 Timeline + 实时天气栏 + 停止卡片（含导航按钮）+ 交通连接 + 酒店卡片 | 时间轴 + 卡片 | **双场景核心** |
| 🗺️ **地图导航** | 路线规划卡片 + Amap iframe + POI 列表 | 地图 + POI + 导航按钮 | 旅途中使用 |
| 📝 **行前须知** | 必备物品 checklist + 注意事项 + 费用说明 | Checklist + 警告卡片 | 出发前准备 |
| 🛡️ **安全保障** | 4 段折叠面板（防护/自救/灾害/处置）+ 紧急联系方式 | Accordion + 联系卡片 | 旅途中参考 |

**全局悬浮**：页面底部始终可见 → `👤 导游 {name} {phone} | 🚑 110 | 🏥 120`

---

## 4 色板 × 4 客户类型

| 类型 | 主色 | 色系 | 适用场景 |
|------|------|------|---------|
| `individual` 个人旅客 | `#1A4A3A` | 山峦青 | 自然探索、独立旅行 |
| `family` 亲子 | `#E8734A` | 暖橙 | 温暖安全感、亲子互动 |
| `corporate` 企业团建 | `#2C4A7C` | 深蓝 | 专业信任、团队协作 |
| `study` 研学 | `#4A8C5A` | 竹绿 | 成长学习、自然教育 |

`schema` 中定义完整 8 色调色板（主色/深色/浅色/强调色/表面色/次文字/危险色/背景色）。

`trip_type` 从飞书文档的「行程类型」段落自动提取，关键词模糊匹配：
- 亲子/家庭 → `family`
- 团建/企业/公司 → `corporate`
- 研学/学习/教育 → `study`
- 其他/个人/单人 → `individual`

---

## 核心流程

### Step 1: 提取行程 + 客户信息

```bash
python3 ~/.hermes-feishu/skills/productivity/trip-landing/scripts/extract_trip.py \
  --doc DOC_TOKEN \
  --output trip_data.json
```

从飞书文档智能解析：
- **行程**：支持 Day 1 / 第1天 / D1 / 第一天 四种格式变体
- **客户信息段落**（v3 新增）：姓名、手机号、行程类型、出行日期
- **导游信息段落**（v3 新增）：姓名、手机号
- **附加段落**：行程背景/亮点/必备物品/注意事项/安全须知/紧急联系/费用说明

自动调用高德 API 为每个 POI 填充坐标，计算每日停靠点之间的驾车路线（距离+时间）。

### Step 2: 生成页面

```bash
python3 ~/.hermes-feishu/skills/productivity/trip-landing/scripts/build_page.py \
  --trip trip_data.json \
  --output output/ \
  --slug zhang-20260715-qianxinan
```

生成输出目录内容：
```
output/
├── index.html      # 5-TAB SPA（含验证门禁+天气加载+PWA注册）
├── sw.js           # Service Worker（缓存策略：HTML cache-first，weather network-first）
└── manifest.json   # PWA manifest（主题色=对应色板主色）
```

**页面交互流**：
1. 客户打开 URL → 看到手机号验证门禁
2. 输入手机号 → SHA256 比对 → 通过后显示行程页
3. 同设备二次打开 → sessionStorage 命中 → 跳过验证
4. 分享给家人 → 家人输入同一手机号 → 看到相同内容
5. 注册 PWA Service Worker → 支持离线查看 + "添加到主屏幕"

### Step 3: 部署

按 `feishu-html` 技能流程，上传 `output/` 目录到 OSS：
- 路径：`web-spa/{slug}/`
- 访问：`https://gzzhike.cn/web-spa/{slug}/`
- 同时上传 `sw.js` 和 `manifest.json`

### Step 4: 注册维护任务

生成页面后，更新活跃行程注册表 + 注册清理任务：

```bash
# 注册到活跃行程表（供 weather cron 扫描）
echo '{"slug":"zhang-20260715-...","start_date":"2026-07-15","end_date":"2026-07-17",...}' \
  >> active_trips.json

# 注册一次性清理任务（D2：行程结束 + 10 天后自动清理）
python3 cleanup_pages.py \
  --slug zhang-20260715-qianxinan \
  --oss-path web-spa/zhang-20260715-qianxinan \
  --end-date 2026-07-17 \
  --registry active_trips.json
```

### Step 5: 持续维护（cron）

```bash
# 每日天气更新
python3 fetch_weather.py --registry active_trips.json --output ./weather_out/
# → 将 weather_out/*.json 上传到对应 OSS 路径

# 每日清理扫描（兜底，防止一次性任务失败）
python3 cleanup_pages.py --registry active_trips.json --oss-bucket gzzhike
```

---

## 页面功能细节

### 手机号验证门禁

- 页面 HTML 内嵌 `SHA256(customer_phone)`
- 客户端使用 Web Crypto API (`crypto.subtle.digest`) 计算 SHA256
- 验证通过后存入 `sessionStorage`（关闭标签页即清除）
- 手机号作为共享密码：家人输入同一手机号即可查看

### PWA 离线策略

- `sw.js` 缓存策略：
  - HTML/静态资源：Cache-first（安装时预缓存，后续从缓存加载）
  - `weather_*.json`：Network-first（优先网络，失败时回退缓存）
- 支持 `beforeinstallprompt`：显示"添加到主屏幕"横幅
- manifest.json 主题色匹配客户类型色板

### 天气实时更新

- 页面加载时 fetch `weather_{slug}.json`（与 HTML 同目录）
- 成功时动态替换各 Day 卡片的天气栏
- 失败时保留 HTML 内嵌的初始天气数据（首次生成时的快照）
- 每日 cron 更新 JSON 文件，客户端下次加载自动获取最新数据

### 导航链接兼容性

- ✅ 微信内置浏览器：`https://uri.amap.com/navigation` + `callnative=1`
- ✅ 桌面浏览器降级：`https://uri.amap.com/marker`
- ❌ 禁用 `amapuri://` scheme（微信拦截）
- 支持浏览器 Geolocation API 获取当前位置作为起点

### 紧急联系方式

- 安全保障 TAB 内：完整紧急联系人卡片网格（可点击拨号）
- 页面底部悬浮条（始终可见）：导游 + 110 + 120
- 设计原则：紧急场景下不需要切换 TAB 就能拨号

---

## 关键约束

- **微信兼容**：导航链接必须用 `https://uri.amap.com/navigation`，不能用 `amapuri://`
- **安全指南必含**：防护措施、自救知识、灾害提醒、意外处置流程 + 紧急联系方式
- **配色为贵州之客品牌规范**：4 套自然色系，按客户类型自动匹配
- **响应式**：移动优先，卡片堆叠；桌面端居中
- **轻量**：单文件 SPA，内联样式+脚本，< 40KB（含验证和 PWA 注册）
- **隐私**：手机号仅以 SHA256 形式嵌入页面，页面过期自动删除
- **离线**：PWA Service Worker 缓存核心内容
- **禁止 pattern**：无紫色渐变、无 emoji 作纯图标、无过度装饰（反 AI slop）

---

## 维护脚本

| 脚本 | 用途 | 触发器 |
|------|------|--------|
| `scripts/extract_trip.py` | 从飞书文档提取行程+客户信息，缺失字段从知识库模板兜底 | 生成页面时 |
| `scripts/build_page.py` | 生成 5-TAB SPA 页面 | 生成页面时 |
| `scripts/fetch_weather.py` | 每日拉取天气数据 | cron：每天凌晨 |
| `scripts/cleanup_pages.py` | 清理过期页面 | 一次性注册 / cron 兜底扫描 |

## 知识库模板 (Wiki)

落地页模板存放在知识库「落地页模板」节点下（node_token: `DqdVwu8U5i8UwWkkMMXcAl0HnFf`）：

```
落地页模板/
├── 安全须知模板                  ← safety.* 缺失时兜底
├── 紧急联系方式模板              ← emergency_contacts 缺失时兜底
├── 必备物品模板/
│   ├── 个人旅客                  ← essentials 缺失 + trip_type=individual
│   ├── 亲子                      ← essentials 缺失 + trip_type=family
│   ├── 企业团建                  ← essentials 缺失 + trip_type=corporate
│   └── 研学                      ← essentials 缺失 + trip_type=study
└── 目的地背景模板/
    ├── 兴义                      ← background 缺失 + 行程含"兴义"
    ├── 安龙                      ← background 缺失 + 行程含"安龙"
    ├── 贞丰 / 晴隆 / 册亨 / 望谟
```

**兜底策略 (B+)**：`extract_trip.py` 先从方案文档提取，文档中缺失的字段自动从知识库对应模板读取。用 `--no-kb` 可禁用此行为。

## 数据格式参考

详见 `references/trip-schema.md` — 完整 JSON schema 含 v3 客户元数据字段和 trip_type 枚举。
