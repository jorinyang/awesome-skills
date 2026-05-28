---
name: trip-landing
description: 客户行程落地页一键生成：从飞书方案文档提取行程→5 TAB SPA（概览/行程/地图/须知/安全）→高德导航→天气预报→部署OSS。触发：生成落地页/生成行程页/做成网页版/生成客户页/行程上线。
triggers:
  - 用户要求根据方案生成客户落地页
  - 用户说「生成行程页」「做成网页」「客户要看」
  - 用户说「把这个方案发布成线上页面」
dependencies:
  - feishu-doc (读取方案)
  - amap MCP (坐标/路线)
  - weather MCP (天气预报)
  - feishu-html (页面生成/部署)
---

# Trip Landing · 客户行程落地页 v2

## 功能概述

从飞书方案文档自动提取行程数据，调用高德地图和天气 API，生成含 5 个 TAB 的客户落地页 SPA，部署至 OSS。

## 5 TAB 结构

| TAB | 内容 | 展示方式 |
|-----|------|---------|
| 📋 **行程概览** | 行程简介、行程亮点、目的地背景 | 文本卡片 + 亮点标签云 |
| 🗓️ **每日行程** | 逐日 Timeline 行程卡片、天气、导航按钮 | 时间轴 + 停止卡片 + 交通连接线 + 酒店卡片 |
| 🗺️ **地图导航** | 路线规划卡片 + Amap iframe + POI 列表 | 嵌入地图 + POI 导航卡片 + 路线规划面板 |
| 📝 **行前须知** | 必备物品清单、注意事项、费用说明 | Checklist + 警告卡片 |
| 🛡️ **安全保障** | 防护/自救/灾害/意外处置（折叠面板）+ 紧急联系方式 | Accordion + 紧急联系卡片 |

## 核心流程

```
飞书方案文档 → extract_trip.py 提取行程+段落解析 → Amap坐标/路线 → Weather天气 → build_page.py 生成5-TAB HTML → OSS部署
```

## 三步操作

### Step 1: 提取行程

```bash
python3 ~/.hermes-feishu/skills/productivity/trip-landing/scripts/extract_trip.py \
  --doc DOC_TOKEN
```

从飞书文档中智能解析行程 + 自动识别并提取以下段落：

| 段落关键词 | 提取到字段 |
|-----------|-----------|
| 行程背景 / 目的地介绍 / 线路介绍 | `overview`, `background` |
| 行程亮点 / 特色体验 | `highlights` |
| 必备物品 / 行前准备 | `essentials` |
| 注意事项 / 禁忌 / 温馨提示 | `precautions` |
| 安全须知 / 安全保障 / 户外安全 | `safety` (含子段: 防护/自救/灾害/处置) |
| 紧急联系 / 联系方式 / 救援电话 | `emergency_contacts` |
| 费用说明 / 价格说明 | `pricing_note`, `inclusions`, `exclusions` |
| 难度等级 / 最佳季节 | `difficulty`, `best_season` |

行程格式支持：`Day 1` / `第1天` / `第一天` / `D1`，地点列表（→ 顿号 换行分隔），酒店/住宿信息，时间安排。

### Step 2: 生成页面

```bash
python3 ~/.hermes-feishu/skills/productivity/trip-landing/scripts/build_page.py \
  --trip trip_data.json \
  --output output/
```

生成含 5 个 TAB 的完整 SPA：

- **TAB1 行程概览**：简介 + 亮点标签 + 目的地背景
- **TAB2 每日行程**：Timeline 时间轴 + Day 卡片 + 天气栏 + 停止卡片（含导航按钮）+ 交通连接线 + 酒店卡片
- **TAB3 地图导航**：隐藏路线规划卡片（从行程 TAB 点击导航时弹出）+ Amap 嵌入 iframe + 全局 POI 列表（含快速导航/规划按钮）
- **TAB4 行前须知**：必备物品 checklist + 注意事项警告列表 + 费用包含/不含
- **TAB5 安全保障**：4 段折叠面板（防护/自救/灾害/处置）+ 紧急联系方式卡片（可拨打）

### Step 3: 部署

按 `feishu-html` 技能流程，上传到 OSS：
- 路径：`web-spa/{slug}/index.html`
- 访问：`https://gzzhike.cn/web-spa/{slug}/`

## 地图导航增强

### 从行程点击导航 → 跳转地图 TAB

在每个行程停止卡片上点击"🗺️ 导航前往"，自动切换到地图 TAB，展示路线规划卡片：

```
┌─────────────────────────────────────────┐
│  📍 路线规划                            │
│  目的地：万峰林景区（建议游玩 4小时）      │
│  [🗺️ 打开高德地图导航]  [📍 使用我的位置] │
│  默认起点：兴义市区 · 点击获取实时定位     │
└─────────────────────────────────────────┘
```

- "打开高德地图导航" → `https://uri.amap.com/navigation?to=lng,lat,name&mode=car&callnative=1`
- "使用我的位置" → 调用浏览器 Geolocation API，获取当前位置作为起点
- 移动端在微信内置浏览器中均可正常打开，引导跳转高德 App

### 地图 TAB

- **桌面端**：Amap iframe 显示全局行程点位 + POI 列表（每项有"导航"和"规划"按钮）
- **移动端**：POI 列表为主，点击"导航"直接跳转高德，"规划"触发路线规划卡片

### 导航链接兼容性

- ✅ 微信内置浏览器：`https://uri.amap.com/navigation` + `callnative=1`
- ✅ 桌面浏览器降级：`https://uri.amap.com/marker`
- ❌ 禁用 `amapuri://` scheme（微信拦截）

## 配色方案 — 贵州之客品牌

| 色值 | 用途 | 名称 |
|------|------|------|
| `#1A4A3A` | 主色、标题、按钮 | 山峦青 |
| `#4A7C96` | 地图、路线规划区 | 水碧 |
| `#D4914A` | 强调按钮、路线规划 CTA | 陶土金 |
| `#F5ECE0` | 酒店卡片、交通 badge | 暖米 |
| `#8B6F5C` | 次要文字、badge | 石褐 |
| `#C9403B` | 紧急联系、安全警告 | 警示红 |

字体：标题用 Noto Serif SC（思源宋体），正文用系统无衬线。

## 响应式设计

- **移动端**（<768px）：单列布局，TAB 导航可横向滚动，底部固定 footer
- **桌面端**（≥768px）：最大宽度 780px 居中，双列 checklist/紧急联系网格

## 关键约束

- **微信兼容**：导航链接必须用 `https://uri.amap.com/navigation`，不能用 `amapuri://`
- **安全指南必含**：防护措施、自救知识、灾害提醒、意外处置流程 + 紧急联系方式
- **配色为贵州之客品牌规范**：自然色系（山峦青/水碧/陶土金/暖米/石褐）
- **响应式**：移动优先，卡片堆叠；桌面端居中
- **轻量**：单文件 SPA，内联样式+脚本，< 30KB
- **禁止 pattern**：无紫色渐变、无 emoji 作纯图标、无过度装饰（反 AI slop）
