# 高德地图 MCP — 中国地图完整方案

> 更新于 2026-05-28：MCP 2.0（Streamable HTTP）已取代 MCP 1.0（npx stdio），15 个工具全部实测通过。

OSM/OSRM 在中国三四线城市存在严重数据稀疏问题（POI 为空、步行/骑行退化、无公交路线）。

## 推荐接入方式：MCP 2.0 Streamable HTTP

```yaml
mcp_servers:
  amap:
    url: "https://mcp.amap.com/mcp?key=你的高德Web服务Key"
    timeout: 30
```

**优势**：零本地安装、自动更新、含 MCP 2.0 独家能力（专属地图/导航唤端/打车唤端）。

## MCP 1.0 接入方式（已过时，仅供兼容参考）

```yaml
# npx stdio (Node.js ≥ v22.14.0)
mcp_servers:
  amap:
    command: "npx"
    args: ["-y", "@amap/amap-maps-mcp-server"]
    env:
      AMAP_MAPS_API_KEY: "你的Key"
    timeout: 30
```
仅提供 ~7 个基础工具，无专属地图/唤端能力。

## 高德 API Key 获取

1. 访问 https://console.amap.com/dev/key/app
2. 创建应用 → 添加 Key
3. 服务平台选择「Web服务」
4. 免费额度：每日 5000 次

## MCP 2.0 完整工具列表（15个）

| 工具 | 功能 | 对比 OSM/OSRM |
|------|------|:--:|
| `maps_geo` | 地址→坐标 | ✅ 优于 Nominatim |
| `maps_regeocode` | 坐标→地址 | ❌ OSM 无此能力 |
| `maps_ip_location` | IP 定位 | ❌ OSM 无此能力 |
| `maps_weather` | 天气查询 | ❌ OSM 无此能力 |
| `maps_text_search` | 关键词 POI 搜索 | ❌ OSM 在中国返回空 |
| `maps_around_search` | 周边 POI 搜索 | ❌ OSM 在中国返回空 |
| `maps_search_detail` | POI 详情（电话/评分/照片） | ❌ OSM 无此能力 |
| `maps_direction_driving` | 驾车路线规划 | ✅ 路网数据完整 |
| `maps_direction_walking` | 步行路线 | ❌ OSM 在中国退化 |
| `maps_direction_bicycling` | 骑行路线 | ❌ OSM 不支持 |
| `maps_direction_transit_integrated` | 公共交通 | ❌ OSM 完全不支持 |
| `maps_distance` | 距离测量 | ✅ |
| `maps_schema_personal_map` | 🆕 行程导入高德 APP 生成私有地图 | ❌ OSM 无此能力 |
| `maps_schema_navi` | 🆕 一键导航唤端 amapuri:// | ❌ OSM 无此能力 |
| `maps_schema_take_taxi` | 🆕 一键打车唤端 amapuri:// | ❌ OSM 无此能力 |

> ⚠️ Schema 唤端工具返回**纯文本 URI**（非 JSON），详见 `native-mcp` 技能 `references/amap-mcp-response-formats.md`。

## 实测数据（兴义→安龙，2026-05-27）

| 模式 | OSM/OSRM | 高德 MCP |
|------|----------|----------|
| 驾车 | 61.2km / 56min | **69.3km / 63min / 过路费32元** |
| 步行 | 61.2km（退化=驾车） | **61.9km / 825min（真实步行）** |
| 骑行 | 61.2km（退化=驾车） | 不可用（SERVICE_NOT_AVAILABLE） |
| 公共交通 | 不支持 | 兴义→安龙无公交路线（县级市间数据有限） |
| POI 搜索 | 0结果 | ✅ 安龙周边5个火车站 |

**结论：驾车距离+过路费准确，POI 覆盖碾压 OSM，步行真实可用。公共交通在小城市间有限是数据问题（大城市全覆盖）。**

## 限制

- 骑行路线部分区域不可用（`SERVICE_NOT_AVAILABLE`）
- 公共交通在县级市之间覆盖有限（同城公交/地铁完整）
- 高德 Key 免费额度：每日 5000 次（Web服务）
