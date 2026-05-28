# 天气查询 MCP（阿里云 API 网关 · cmapi00072158）

Streamable HTTP MCP 服务，提供 7 个天气查询工具。零依赖，通过 URL 直连。

## 配置

```yaml
mcp_servers:
  weather:
    url: "http://mcpservergateway.market.alicloudapi.com/mcpnacos/cmapi00072158/eyJhcHBDb2RlIjoiNGY0MjM1Y2I0ODc5NGNmYjhhZDQwYmMzOTA0MDViZmYiLCJzIjoiQ2xvdWRfTWFya2V0In0="
    timeout: 30
```

网关认证信息（备用）：
- AppKey: `205000351`
- AppSecret: `eqNqO4IHasW57MfI9atie6fmNHJNLhEP`
- AppCode: `4f4235cb48794cfb8ad40bc390405bff`

## 工具列表（7个）

| 工具 | 功能 | 参数 |
|------|------|------|
| `七日天气极速版` | 未来7天逐日天气 | `city`/`lat+lng`/`ip`/`adcode`/`cityid`（任选其一） |
| `未来15日天气情况极速版` | 未来15天逐小时 | 同上 |
| `24小时实况天气极速版` | 当前实况（温/湿/风/能见度/紫外线） | 同上 |
| `实时降水降雨量极速版` | 实时降水数据 | `lat` + `lng`（必填） |
| `景区天气查询` | 特定景区天气 | `adcode` 或 `cityid` |
| `历史天气专业版` | 历史数据查询 | `cityid` + `year`/`month`/`date` |
| `城市空气质量极速版` | AQI 空气质量 | `citycode` |

## 关键使用规范

### 城市名称参数（`city`）
- **不带「市」「区」后缀** — 正确: `"兴义"`，错误: `"兴义市"`
- 字母城市名正常使用: `"北京"`, `"青岛"`, `"铁西"`
- 如有重名风险，加 `province` 参数: `"山东"`, `"上海"`（也不带省/市后缀）

### 经纬度参数（`lat`/`lng`）
```json
{"lat": "25.09", "lng": "104.89"}
```
字符串格式，可从 amap `maps_geo` 获取。

### 支持的查询方式
所有方式互斥，一次只传一种:
1. `city` — 最常用
2. `lat` + `lng` — 精确位置
3. `ip` — 按 IP 定位
4. `adcode` — 统计局区划代码
5. `cityid` — 服务商城市 ID 表

## 返回数据亮点

- 七日天气包含：日期、天气、风力(m/s)、湿度、AQI、日出日落、**预警信息**（雷电/暴雨/大风等）
- 15日天气包含：逐小时温度、体感温度、湿度、风力风向、云量、紫外线、降水概率、能见度
- 历史天气支持：按日/月/年回查

## 实测示例（2026-05-27）

兴义查询返回：
```json
{
  "date": "2026-05-28",
  "wea": "多云", "wea_day": "晴", "wea_night": "中雨",
  "air": "34", "air_level": "优",
  "humidity": "86%",
  "alarm": {
    "alarm_type": "雷电",
    "alarm_level": "黄色",
    "alarm_title": "贵州省黔西南布依族苗族自治州兴义市发布雷电黄色预警信号",
    "alarm_content": "兴义市气象台5月27日18时44分发布雷电黄色预警信号..."
  }
}
```

⚠️ **预警信息是旅游行程规划的关键输入** — 智能行程技能应据此自动调整户外活动安排。

## 与 amap 的天气工具对比

amap MCP 也有 `maps_weather` 工具，但功能较基础。此天气 MCP 服务更专业：
- 15日超长预报 vs amap 基础天气
- 逐小时精度（温度/降水/紫外线）
- 历史天气回查
- 实时降水雷达级数据

推荐**行程规划类场景优先使用本 weather MCP**，简单当前天气用 amap 即可。
