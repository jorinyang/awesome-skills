---
name: travel-itinerary
description: 贵州之客智能行程规划 — 输入目的地/天数/偏好/预算/日期，调用 weather + amap + minimax 三重 MCP，产出结构化行程 + 地图标注 + 费用预估，双版输出（客户版 + 地接版）。
triggers:
  - "规划行程/行程规划/行程设计"
  - "设计线路/线路规划"
  - "帮我排一个XX天的路线"
  - "定制XX之旅"
  - "XX天XX游"
  - "客户想XX，帮排行程"
  - "地接版/执行单"
  - "帮我看看这张图/这个景点/这个地方是哪里"
  - "识别景点/图片识别"
tags: [travel, itinerary, planning, guizhou, 贵州之客]
category: travel
---

# travel-itinerary — 智能行程规划

> **定位：** P1 技能。上游依赖 travel-knowledge（旅游资源知识库），下游交付 feishu-doc（飞书文档）。输入需求描述，产出完整行程方案。

## 触发条件

| 触发词 | 示例 |
|--------|------|
| 规划行程 / 行程规划 | "帮我规划一个3天2晚荔波行程" |
| 设计线路 | "设计一条黔东南5天自驾线路" |
| 排路线 / 定路线 | "帮我排一个贵阳出发2日游" |
| 地接版 / 执行单 | "转成地接版执行单" |

---

## 核心工作流（7 步）

### Step 0 — 图片识别（可选前置）

> 📌 2026-05-28 新增：minimax `understand_image` 已确认可用。

当用户发送景区/美食/路牌照片时，先调用图片理解：

```
mcp_minimax_mcp_understand_image(
  prompt="识别这张图片中的地点/景点/美食/标识，给出名称、位置、简要信息和游玩建议。如果是景区照片，请判断具体是哪个景点。",
  image_source="<图片URL或本地路径>"
)
```

识别结果注入 Step 3 的目的地信息池，用于后续行程规划。

### Step 1 — 解析需求 + CRM 画像查询

**子步骤 1a：从用户输入中提取结构化参数**

| 参数 | 示例 | 缺失时默认值 |
|------|------|-------------|
| `destination` | 荔波 / 黔东南 / 贵州全境 | 需用户明确 |
| `days` | 3天2晚 | 需用户明确 |
| `dates` | 2026-06-15 ~ 06-17 | 以当前日期为起点 |
| `group_size` | 4人 | 2人 |
| `budget` | 3000元/人 | 中等预算 |
| `preferences` | 自然/文化/探险/美食/亲子/摄影 | 综合型 |
| `travel_mode` | 自驾/包车/公共交通 | 包车（贵州推荐） |
| `departure_city` | 贵阳 | 贵阳 |

**偏好 → 行程风格映射：**

| 偏好标签 | 行程特征 |
|----------|---------|
| 自然风光 | 瀑布/峡谷/喀斯特地貌，徒步比重↑ |
| 民族文化 | 苗寨/侗寨/非遗体验，互动活动↑ |
| 户外探险 | 探洞/桨板/徒步/攀岩，体能要求↑ |
| 美食之旅 | 酸汤鱼/肠旺面/丝娃娃，餐饮点↑ |
| 亲子家庭 | 轻松节奏/互动体验/安全优先 |
| 摄影采风 | 黄金光线时段/观景台/慢节奏 |
| 休闲度假 | 高端住宿/少移动/深度体验 |

**子步骤 1b：查询 CRM 画像（如果用户提供了姓名）**

> 📌 2026-05-28 新增：对接「贵州之客 CRM 客户画像」多维表格。

当用户提到客户姓名时，查询 CRM 获取历史偏好：

```bash
lark-cli base +record-search --base-token Wi1HbLBJZa8oWSsUmakcM3k3n5e \
  --table-id tblloIwP9YAo64Dv \
  --json '{"filter":{"conjunction":"and","conditions":[{"field_name":"客户姓名","operator":"contains","value":["<客户姓名>"]}]}}' \
  --as bot
```

**CRM → 行程参数自动填充：**

| CRM 字段 | → | 行程参数 |
|----------|---|---------|
| 偏好类型 | → | `preferences` |
| 预算级别 | → | `budget` |
| 出行方式偏好 | → | `travel_mode` |
| 历史目的地 | → | 推荐相似线路或新目的地 |
| 意向人数 | → | `group_size` |
| 意向日期 | → | `dates` |
| 特殊需求 | → | 纳入 Step 5 LLM 优化约束 |

**如果 CRM 中无此客户** → 跳过此步骤，使用默认参数。规划完成后提示"是否存入 CRM"。

### Step 2 — 并行查询天气（weather + amap MCP）

**BEFORE 规划具体路线，必须先拉取气象数据。** 按日期间隔选择工具：

| 时间范围 | 工具 | 获取信息 |
|----------|------|---------|
| 近 7 天 | weather 七日天气 / 15日逐小时 | 温度、湿度、天气现象、风力、AQI |
| 7-15 天 | weather 15日预报 | 趋势判断 |
| 当前 | weather 实况 / 降水分钟级 | 出行当日参考 |
| 景区 | weather 景区天气 | 目的地景区专属预报 |

**天气影响规则（自动应用）：**

| 天气条件 | 行程调整策略 |
|----------|-------------|
| 暴雨/雷电预警 | 当天户外活动→室内备选；峡谷/漂流→取消 |
| 中雨 | 户外活动移至上午，下午安排室内/交通 |
| 小雨 | 不影响，增加雨具提醒 |
| 高温 ≥35°C | 午间避开户外，早晚活动为主 |
| AQI > 100 | 提醒敏感人群戴口罩 |
| 晴天 | 优先安排观景台/摄影点位 |

### Step 3 — 搜索目的地信息 + 查询知识库（minimax + travel-knowledge）

**子步骤 3a：先查知识库存量**

```
调用 travel-knowledge 技能 → 搜索已有攻略/景点信息
  如命中 → 直接使用，标注"来自知识库（采集日期：YYYY-MM-DD）"
  如未命中或过期 → 进入 web_search
```

**子步骤 3b：minimax web_search（交叉验证）**

```
第1轮：景点基础信息
  → "{destination} 旅游攻略 2026 必去景点 门票价格"
  → "{destination} 最新开放时间 注意事项"

第2轮：时效性信息（交叉验证）
  → "{destination} 近期景区公告 道路状况"
  → "{destination} 游玩攻略 避坑指南"

第3轮（可选）：深度内容
  → "{destination} 当地美食推荐 特色体验"
  → "{destination} 民族文化 非遗体验"
```

**提取结构化信息：**
- 景点名称、评级（5A/4A）、参考游玩时长
- 门票价格、开放时间、最佳游览时段
- 特色体验项目（探洞/桨板/民俗表演）
- 餐饮推荐（本地人常去、人均消费）
- 住宿区域建议
- ⚠️ 近期注意事项（修路/闭园/限制）

### Step 4 — POI 定位 + 路线规划（amap MCP）

**子步骤 4a：地理编码**

```
对每个景点/酒店执行：
  mcp_amap_maps_geo（地址 → 经纬度）
```

**子步骤 4b：周边搜索**

```
对每个核心景点执行：
  mcp_amap_maps_search_around
    - 附近餐厅（type=餐饮）
    - 附近酒店（type=酒店）
    - 附近停车场、卫生间、加油站
```

**子步骤 4c：路线规划**

```
Day N 内移动：
  景点A → 景点B：mcp_amap_maps_direction_driving（包车/自驾）
  或 mcp_amap_maps_direction_transit_integrated（公交方案）
  或 mcp_amap_maps_direction_walking（景区内步行）
```

**记录每段：**
- 距离（km）、预估耗时（分钟）
- 路线摘要（途经主要道路）
- 同时提供备选方案（更快 / 风景更好）

**子步骤 4d：查询实时路况（Amap 交通 API）**

> 📌 2026-05-28 新增：高德交通路况 API 已开通。

```bash
# 矩形区域路况查询
curl -s "https://restapi.amap.com/v3/traffic/status/rectangle?key=bdd24d613825549ee07b6c32c032c59b&rectangle=<左下经纬度>;<右上经纬度>&extensions=all"
```

路况数据用于：
- 修正 Step 4c 的预估耗时（畅通/缓行/拥堵 × 时间系数）
- Step 5 LLM 优化中避开拥堵路段
- 地接版「风险点位标注」中标注常堵路段

**子步骤 4e：MCP 2.0 专属工具（高德 APP 联动）**

> ⚠️ 仅 MCP 2.0（Streamable HTTP）可用。MCP 1.0 无此能力。

完成路线规划后，针对每个 POI 和每段行程生成高德 APP 唤端链接：

**专属地图生成：** 将整日行程（POI 列表 + 时段描述）导入高德 APP 生成私有地图。
**导航唤端：** 每个目的地生成 `amapuri://` 一键导航链接。
**打车唤端：** 景点间生成高德打车唤端链接（origin → destination）。

这些链接嵌入 Step 7 客户版文档，游客在手机端点击即可跳转高德 APP。

### Step 5 — LLM 智能规划与优化

> 📌 用户批注要求：**"考虑采用 LLM 进行规划或者优化"**，而非引入 OR-Tools。

将 Step 2-4 的所有数据（天气、景点、路线）传入 LLM 推理，产出优化后的日程：

**LLM 优化目标：**
1. **天气适配** — 雨天日安排室内/交通；晴天抓紧户外观景
2. **时间合理** — 每天游玩时间 6-8 小时，含午餐休息
3. **空间聚合** — 同方向景点归到同一天，减少绕路
4. **节奏控制** — 高强度日（多景点/长距离）与放松日交替
5. **偏好满足** — 根据用户偏好标签优先安排对应活动类型

**⚠️ 不依赖 OR-Tools，由 LLM 在语义层面完成排序优化。**

### Step 6 — 费用预估

| 费用项 | 计算方式 | 说明 |
|--------|---------|------|
| 住宿 | 天数 × 人均标准 | 根据目的地酒店均价估算 |
| 交通 | 包车日均 + 路线里程费用 | 贵州包车参考：600-800元/天 |
| 门票 | Σ(各景点门票) | 从 Step 3 搜索结果提取 |
| 餐饮 | 天数 × 人均餐标 | 正餐 50-80元/人/顿 |
| 体验项目 | Σ(各项目费用) | 探洞/桨板/民俗体验等 |
| 保险 | 固定 N 元/人 | 旅游意外险 |

**输出费用汇总表：** 明细 + 小计 + 总计（元/人）

### Step 7 — 生成双版文档

使用 `feishu-doc` 技能创建飞书文档，归档至知识库「方案计划」节点。

#### A. 客户版（面向游客）

结构：
1. 📌 行程概览卡片（目的地/天数/人数/日期/预算）
2. 🌤️ 天气预报总览（每日图标+温度+AQI）
3. 🗺️ 每日详细行程（时间轴格式：08:30 出发 → 09:00 抵达 → 12:00 午餐 → ...）
4. 🍜 美食推荐（每天 2-3 家）
5. 💰 费用明细表
6. 🎒 行前准备清单（证件/衣物/装备/药品）
7. 📞 紧急联系与实用贴士

#### B. 地接版（面向导游/地接团队）

在客户版基础上追加：
1. 🚌 交通执行明细（每段路线+距离+预估时间+备选方案对照表）
2. 📞 供应商联系清单（酒店/餐厅/车队/景区 — 由地接团队填写）
3. 🧾 物资清单（团队物资+客户物资+应急物资）
4. ⚠️ 风险点位标注（天气风险/路况风险/体能要求）
5. ⏱️ 时间缓冲表（每段预留缓冲时间 + 雨天备选方案）

---

## MCP 工具调用映射

| 步骤 | MCP 工具 | 调用时机 |
|------|---------|---------|
| 图片识别 | `mcp_minimax_mcp_understand_image` | Step 0 — 用户发图片时 |
| CRM 查询 | `lark-cli base +record-search` | Step 1b — 用户提供客户姓名时 |
| 天气查询 | `weather` 全系列 / `mcp_amap_maps_weather` | Step 2 — 规划前必须 |
| 知识库查询 | `travel-knowledge` 技能 | Step 3a — 优先查存量 |
| 目的地搜索 | `web_search`（minimax） | Step 3b — 至少 2 轮交叉验证 |
| 地理编码 | `mcp_amap_maps_geo` | Step 4a |
| POI 搜索 | `mcp_amap_maps_search_around` | Step 4b |
| 路线规划 | `mcp_amap_maps_direction_*` | Step 4c |
| 实时路况 | Amap REST API `traffic/status/rectangle` | Step 4d |
| 专属地图生成 | `mcp_amap_*` MCP 2.0 exclusive | Step 4e — 行程输出时 |
| 导航唤端链接 | `mcp_amap_*` MCP 2.0 exclusive | Step 4e — 每段移动 |
| 打车唤端链接 | `mcp_amap_*` MCP 2.0 exclusive | Step 4e — 景点间 |
| 文档生成 | `feishu-doc` 技能 | Step 7 |

> ⚠️ **MCP 版本要求**：专属地图生成、导航唤端、打车唤端三项能力仅在高德 MCP 2.0（Streamable HTTP 方式，`url: "https://mcp.amap.com/mcp?key=..."`）中可用。MCP 1.0（npx stdio 或社区 uvx 方式）仅有基础地理服务工具。详见 `native-mcp` 技能 references/amap-mcp2.md。

## 输出规范

### 文档命名规则
```
贵州之客_行程方案_{destination}_{days}天{dates}_v{version}
```
示例：`贵州之客_行程方案_荔波_3天0615-0617_v1`

### 知识库归档
- 分类：方案计划（`KVPTwrbOKiQMUkkUPlscaEKfnUd`）
- 每次规划产出独立文档
- 修订时在原文档上 `+update --command append`

### 质量检查清单
- [ ] 天气数据已拉取且日期匹配？
- [ ] 搜索信息已交叉验证（≥2 次搜索）？
- [ ] 每段路线有距离和预估耗时？
- [ ] 每日游玩时间 ≤ 8 小时？
- [ ] 雨天方案已标注备选？
- [ ] 费用表有明细+小计+总计？
- [ ] 客户版和地接版均已生成？
- [ ] 文档已归档至知识库？

---

## 已实现的能力（来自 MCP 矩阵）

| 能力 | 实现方式 |
|------|---------|
| ✅ 天气+路线联动 | LLM 编排 weather + amap |
| ✅ 多模式出行 | amap 驾车/步行/骑行/公交 |
| ✅ 资讯搜索 | minimax web_search（交叉验证） |
| ✅ 地图标注 | amap geo + POI |
| ✅ 双版输出 | feishu-doc 客户版 + 地接版 |
| ✅ 费用预估 | LLM 汇总 class 级估算 |
| ✅ 图片→景点识别 | minimax understand_image（2026-05-28） |
| ✅ CRM 偏好填充 | 飞书 Bitable「贵州之客 CRM 客户画像」（2026-05-28） |
| ✅ 实时路况修正 | Amap 交通 API（2026-05-28） |
| ✅ 知识库存量查询 | travel-knowledge 技能（2026-05-28） |
| ✅ 专属地图导入 | MCP 2.0 exclusive（高德 APP 私有地图） |
| ✅ 一键导航/打车唤端 | MCP 2.0 exclusive（amapuri:// 唤端链接） |

## 待完善的能力（用户批注 + P0 建议）

| 能力 | 状态 | 备注 |
|------|:----:|------|
| ~~实时交通路况~~ | ✅ 已接入 | Amap 交通 API → Step 4d |
| ~~用户画像/偏好记忆~~ | ✅ 已接入 | CRM Bitable → Step 1b |
| ~~图片理解~~ | ✅ 已接入 | minimax understand_image → Step 0 |
| ~~知识库存量查询~~ | ✅ 已接入 | travel-knowledge → Step 3a |
| 多目的地 TSP 优化 | 🟡 P1 | 当前 LLM 语义优化替代 OR-Tools |
| 景区实时客流 | 🟡 P1 | 待数据源接入 |

---

## 预设参数（贵州之客默认值）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 出发城市 | 贵阳 | 贵州省会，主要集散地 |
| 交通方式 | 包车 | 贵州景点分散，包车最灵活 |
| 住宿标准 | 中档 | 300-500元/晚 |
| 餐标 | 60元/人/正餐 | 含特色餐饮预算 |
| 保险 | 10元/人/天 | 基础旅游意外险 |
| 导游 | 含 | 本地导游服务 |
| 每天游玩时间 | 8:00-17:00 | 含午餐休息 1 小时 |

---

## 已知 MCP 工具名称（供 Agent 直接调用）

```
天气查询：
  weather MCP 工具名随 provider 暴露（7日/15日/实况/降水/历史/景区/空气质量）
  备选：mcp_amap_maps_weather

地理服务（amap MCP 2.0，15个工具）：
  mcp_amap_maps_geo              — 地址→经纬度
  mcp_amap_maps_regeocode        — 坐标→地址
  mcp_amap_maps_text_search      — 关键词 POI 搜索（返回 pois 键，非 results）
  mcp_amap_maps_search_around    — 周边 POI 搜索（返回 pois 键，非 results）
  mcp_amap_maps_search_detail    — POI 详情（电话/评分/照片）
  mcp_amap_maps_direction_driving        — 驾车路线
  mcp_amap_maps_direction_walking        — 步行路线（响应嵌套在 route 下）
  mcp_amap_maps_direction_bicycling      — 骑行路线
  mcp_amap_maps_direction_transit_integrated — 公交路线
  mcp_amap_maps_distance          — 距离测量
  mcp_amap_maps_schema_personal_map — 🆕 专属地图（返回纯文本 amapuri://）
  mcp_amap_maps_schema_navi       — 🆕 导航唤端（返回纯文本 amapuri://）
  mcp_amap_maps_schema_take_taxi  — 🆕 打车唤端（返回纯文本 amapuri://）

资讯搜索（minimax）：
  mcp_minimax_mcp_web_search  — 联网搜索

文档生成（feishu-doc 技能）：
  加载 feishu-doc 技能 → 使用 lark-cli docs +create
```

---

## 陷阱与注意事项

1. **天气必须在规划前拉取** — 不能先排路线再看天气，会导致晴天安排室内、雨天安排户外的逻辑错误
2. **搜索必须交叉验证** — 单一搜索结果可能存在过时信息，至少 2 次搜索比对
3. **amap POI 类型参数** — 中文类型名（"餐饮"/"酒店"/"景点"），非英文
4. **路线距离 ≠ 实际耗时** — 贵州山路多，预留 20-30% 缓冲
5. **门票价格会变动** — 搜索结果注明年份/季节，避免使用淡季价格作为旺季参考
6. **地接版需要供应商信息** — 酒店电话/车队联系人等需地接团队后续填写，LLM 仅生成空白模板
7. **跨天行程注意住宿连续性** — 避免 Day N 住宿点离 Day N+1 第一站太远
8. **专属地图/唤端链接仅 MCP 2.0 可用** — 如果 amap MCP 配置为 npx stdio（MCP 1.0）或社区 uvx 方式，无法生成专属地图和唤端链接。旅游规划场景必须使用 Streamable HTTP 方式（`url: "https://mcp.amap.com/mcp?key=..."`），详见 `native-mcp` 技能。
9. **MCP 2.0 响应格式不统一** — `maps_text_search` 和 `maps_around_search` 用 `pois` 键（非 `results`）；`maps_regeocode` 和 `maps_weather` 是扁平结构（无 `results` 包装）；`maps_direction_walking` 嵌套在 `route` 下；Schema 唤端工具返回纯文本 URI（非 JSON）。详见 `native-mcp` 技能 `references/amap-mcp-response-formats.md`。
