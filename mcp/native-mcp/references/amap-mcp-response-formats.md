# 高德 MCP 2.0 响应格式差异表

> 实测于 2026-05-28，端点 `https://mcp.amap.com/mcp`，15 个工具全部可用。

## 核心发现

MCP 2.0 的 `tools/call` 返回格式**不统一**。不同工具返回的 JSON 结构差异很大，不能假设统一包含 `results` 包装。

## 各工具响应格式

### 地理编码类

| 工具 | 响应顶层键 | 数据结构 | 示例路径 |
|------|-----------|---------|---------|
| `maps_geo` | `results` | `[{province, city, district, location, ...}]` | `d['results'][0]['location']` |
| `maps_regeocode` | 扁平 | `{province, city, district}` (无 results 包装) | `d['province']` |
| `maps_ip_location` | `results` | `[{province, city, adcode}]` | `d['results'][0]['province']` |

### 搜索类

| 工具 | 响应顶层键 | 数据结构 | 注意事项 |
|------|-----------|---------|---------|
| `maps_text_search` | `suggestion` + `pois` | `{suggestion: {...}, pois: [{id, name, address, typecode, photo}]}` | ⚠️ 用 `pois` 不是 `results`；poi 对象不含 `location` 字段 |
| `maps_around_search` | `pois` | `[{id, name, address, typecode, photo, location}]` | ⚠️ 用 `pois` 不是 `results` |
| `maps_search_detail` | `results` | `[{id, name, address, location, tel, biz_ext: {rating}, photos}]` | 标准的 results 包装 |

### 路线规划类

| 工具 | 响应顶层键 | paths 路径 | 注意事项 |
|------|-----------|-----------|---------|
| `maps_direction_driving` | 扁平 `{origin, destination, paths}` | `d['paths'][0]` | ⚠️ 无 route/results 包装 |
| `maps_direction_walking` | `route` | `d['route']['paths'][0]` | ⚠️ 嵌套在 `route` 下 |
| `maps_direction_bicycling` | 扁平 `{origin, destination, paths}` | `d['paths'][0]` | 与驾车相同 |
| `maps_direction_transit_integrated` | `results` | `d['results'][0]['transits']` | 标准 results 包装 |

### 其他

| 工具 | 响应格式 | 说明 |
|------|---------|------|
| `maps_weather` | `{city, forecasts: [{date, dayweather, nightweather, daytemp, nighttemp, ...}]}` | ⚠️ 用 `forecasts` 不是 `casts`；无 results 包装 |
| `maps_distance` | `results` | `d['results'][0]['distance']` |

### Schema 唤端类（MCP 2.0 独家）

| 工具 | 响应格式 | 说明 |
|------|---------|------|
| `maps_schema_navi` | **纯文本** `amapuri://navi?...` | ⚠️ 不是 JSON！直接是 URI 字符串 |
| `maps_schema_take_taxi` | **纯文本** `amapuri://drive/takeTaxi?...` | ⚠️ 不是 JSON！ |
| `maps_schema_personal_map` | **纯文本** URI 或错误文本 | ⚠️ 不是 JSON！参数需 `{orgName, lineList: [{title, pointInfoList: [{name, lon, lat, poiId}]}]}` |

## Agent 调用建议

```python
def call_amap_mcp(name, args):
    """通用 amap MCP 调用 + 响应解析"""
    # ... MCP initialize + tools/call ...
    text = result['result']['content'][0]['text']
    
    # Schema 类返回纯文本 URI → 直接返回
    if 'schema' in name:
        return text  # amapuri://...
    
    # JSON 响应
    data = json.loads(text)
    
    # 统一提取路径信息
    paths = None
    if isinstance(data, dict):
        if 'paths' in data:
            paths = data['paths']
        elif 'route' in data and 'paths' in data['route']:
            paths = data['route']['paths']
        elif 'results' in data:
            r = data['results']
            if isinstance(r, list) and r and 'paths' in r[0]:
                paths = r[0]['paths']
    
    return data, paths
```
