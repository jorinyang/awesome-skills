---
name: amap-lbs
description: "高德 LBS SKILL：POI搜索、路径规划、旅游规划、周边搜索、热力图、地图链接生成。通过REST API调用高德开放平台Web服务。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [AMap, LBS, POI, Route, Travel, API]
    related_skills: [amap-cli, maps]
---

# 高德 LBS 综合服务 SKILL

基于高德开放平台 REST API，提供开箱即用的地理信息服务。此技能是 `amap-mcp-server` MCP 工具的补充，提供更灵活的直接 API 调用模式和复合场景（旅游规划、热力图、地图链接生成等）。

## 前置条件

高德 Web 服务 API Key（已在配置中）：
```bash
AMAP_KEY=bdd24d613825549ee07b6c32c032c59b
```

> 此 Key 已在 `amap` MCP Server 中配置。本技能可直接使用，无需额外配置。

## API 基础信息

- 基础 URL：`https://restapi.amap.com/v3/`
- 所有请求需带参数：`key=bdd24d613825549ee07b6c32c032c59b`
- 返回格式：JSON

## 场景一：POI 搜索

### 1.1 关键词搜索

直接搜索类别或地点，生成高德地图搜索链接可视化查看。

```bash
# 城市内搜索
curl -s "https://restapi.amap.com/v3/place/text?key=$AMAP_KEY&keywords=美食&city=北京&offset=20" | python3 -m json.tool

# 生成地图链接（供用户在浏览器中打开）
echo "https://www.amap.com/search?query=美食"
```

**参数**：

| 参数 | 必填 | 说明 |
|------|------|------|
| `keywords` | ✅ | 查询关键词 |
| `city` | ❌ | 城市（不填则全国搜索） |
| `types` | ❌ | POI 分类 |
| `offset` | ❌ | 每页条数（默认 20，最大 25） |
| `page` | ❌ | 页码 |

### 1.2 周边搜索

```bash
# 先地理编码获取坐标
curl -s "https://restapi.amap.com/v3/geocode/geo?key=$AMAP_KEY&address=西直门" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['geocodes'][0]['location'])"

# 再拼接周边搜索链接
# location=116.353138,39.939385
echo "https://ditu.amap.com/search?query=美食&query_type=RQBXY&longitude=116.353138&latitude=39.939385&range=1000"
```

```bash
# 周边搜索 API
curl -s "https://restapi.amap.com/v3/place/around?key=$AMAP_KEY&location=116.353138,39.939385&radius=1000&keywords=美食" \
  | python3 -m json.tool | head -30
```

### 1.3 POI 详细搜索（脚本方式）

```bash
# 基础搜索
curl -s "https://restapi.amap.com/v3/place/text?key=$AMAP_KEY&keywords=肯德基&city=北京&offset=5" \
  | python3 -m json.tool

# 周边搜索
curl -s "https://restapi.amap.com/v3/place/around?key=$AMAP_KEY&location=116.397428,39.90923&radius=1000&keywords=酒店" \
  | python3 -m json.tool
```

## 场景二：路径规划

### 2.1 四种出行方式

```bash
# 驾车
curl -s "https://restapi.amap.com/v3/direction/driving?key=$AMAP_KEY&origin=116.434,39.909&destination=116.324,39.915" | python3 -m json.tool

# 步行
curl -s "https://restapi.amap.com/v3/direction/walking?key=$AMAP_KEY&origin=116.434,39.909&destination=116.324,39.915" | python3 -m json.tool

# 骑行
curl -s "https://restapi.amap.com/v4/direction/bicycling?key=$AMAP_KEY&origin=116.434,39.909&destination=116.324,39.915" | python3 -m json.tool

# 公交
curl -s "https://restapi.amap.com/v3/direction/transit/integrated?key=$AMAP_KEY&origin=116.434,39.909&destination=116.324,39.915&city=北京" | python3 -m json.tool
```

### 2.2 驾车策略

| 策略值 | 含义 |
|--------|------|
| `0` | 速度优先（默认） |
| `1` | 费用优先 |
| `2` | 距离优先 |
| `3` | 不走高速 |
| `4` | 躲避拥堵 |
| `5` | 多策略（同时返回以上多种） |

```bash
# 躲避拥堵
curl -s "https://restapi.amap.com/v3/direction/driving?key=$AMAP_KEY&origin=116.434,39.909&destination=116.324,39.915&strategy=4" | python3 -m json.tool
```

## 场景三：地理编码

### 3.1 地理编码（地址 → 坐标）

```bash
curl -s "https://restapi.amap.com/v3/geocode/geo?key=$AMAP_KEY&address=北京市朝阳区阜通东大街6号" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
for g in d.get('geocodes', []):
    print(f\"{g['formatted_address']} → {g['location']}\")
"
```

### 3.2 逆地理编码（坐标 → 地址）

```bash
curl -s "https://restapi.amap.com/v3/geocode/regeo?key=$AMAP_KEY&location=116.310,39.982" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
r = d.get('regeocode', {})
print(r.get('formatted_address', 'N/A'))
"
```

## 场景四：天气查询

```bash
# 基础天气
curl -s "https://restapi.amap.com/v3/weather/weatherInfo?key=$AMAP_KEY&city=110000&extensions=base" \
  | python3 -m json.tool

# 预报天气
curl -s "https://restapi.amap.com/v3/weather/weatherInfo?key=$AMAP_KEY&city=110000&extensions=all" \
  | python3 -m json.tool
```

## 场景五：智能旅游规划

自动搜索兴趣点并规划游览路线。

```bash
# 北京一日游
AMAP_KEY="bdd24d613825549ee07b6c32c032c59b"
CITY="北京"
INTERESTS=("景点" "美食" "酒店")

for interest in "${INTERESTS[@]}"; do
  echo "=== 搜索 $CITY $interest ==="
  curl -s "https://restapi.amap.com/v3/place/text?key=$AMAP_KEY&keywords=$interest&city=$CITY&offset=5" \
    | python3 -c "
import sys, json
d = json.load(sys.stdin)
for p in d.get('pois', [])[:5]:
    print(f\"  {p['name']} | {p['location']} | {p.get('address','')} | ⭐{p.get('biz_ext',{}).get('rating','N/A')}\")
"
  echo ""
done
```

## 场景六：地图链接生成

一键生成高德地图链接，方便用户在浏览器/APP 中打开。

```bash
# 搜索链接
echo "https://www.amap.com/search?query=星巴克"

# 导航链接（从A到B）
echo "https://ditu.amap.com/dir?from[name]=西直门&to[name]=天安门&type=car"

# 周边搜索链接
echo "https://ditu.amap.com/search?query=美食&query_type=RQBXY&longitude=116.353138&latitude=39.939385&range=1000"

# 地点详情链接
echo "https://ditu.amap.com/place/B000A7BD6C"
```

## 场景七：行政区划查询

```bash
# 查询省份列表
curl -s "https://restapi.amap.com/v3/config/district?key=$AMAP_KEY&keywords=中国&subdistrict=1" \
  | python3 -m json.tool | head -30

# 查询城市区县
curl -s "https://restapi.amap.com/v3/config/district?key=$AMAP_KEY&keywords=北京&subdistrict=2" \
  | python3 -m json.tool | head -40
```

## 场景八：IP 定位

```bash
curl -s "https://restapi.amap.com/v3/ip?key=$AMAP_KEY" | python3 -m json.tool
```

## 常用 POI 分类代码

| 大类 | 代码 | 说明 |
|------|------|------|
| 餐饮 | `050000` | 餐饮服务 |
| 购物 | `060000` | 购物服务 |
| 住宿 | `100000` | 住宿服务 |
| 景点 | `110000` | 风景名胜 |
| 交通 | `150000` | 交通设施 |
| 金融 | `160000` | 金融保险 |
| 医疗 | `090000` | 医疗保健 |
| 教育 | `140000` | 科教文化 |

```bash
# 按分类搜索
curl -s "https://restapi.amap.com/v3/place/text?key=$AMAP_KEY&keywords=&types=110000&city=北京" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(p['name'],p['location']) for p in d.get('pois',[])]"
```

## 与其他工具的互补

| 工具 | 适用场景 | MCP 版本 |
|------|----------|----------|
| `amap-lbs` (本技能) | 需要灵活自定义 API 调用、复合场景编排 | — |
| `amap` MCP Server (Streamable HTTP) | 官方 MCP 2.0 推荐方式：基础地理服务 + **专属地图/唤端**（旅游规划首选） | MCP 2.0 |
| `amap` MCP Server (npx stdio) | MCP 1.0：仅基础地理服务，无专属地图/唤端能力 | MCP 1.0 |
| `amap-cli` (amap-gui) | 需要可视化地图交互（GUI 环境） | — |
| `maps` 技能 | 通用地图（OSM/OSRM），国际场景 | — |

> ⚠️ **旅游规划场景**：务必使用 MCP 2.0（Streamable HTTP，`url: "https://mcp.amap.com/mcp?key=..."`）。仅 MCP 2.0 支持将行程一键导入高德 APP 生成专属地图、一键导航/打车唤端。MCP 1.0（npx 或社区 uvx）仅有 geocode/search/direction/weather 基础工具。
