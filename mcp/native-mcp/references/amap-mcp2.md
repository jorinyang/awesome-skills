# 高德 MCP 2.0 发布信息

来源：微信公众平台文章 `https://mp.weixin.qq.com/s/GflfPtWgN_q7q7oROYGLcg`
提取日期：2026-05-28

## MCP 版本演进

### MCP 1.0（2025年3月发布）
- 12 大核心地图服务：位置服务、地点信息搜索、路径规划、天气查询等
- 支持 SSE 协议
- 与阿里云百炼等大模型开发平台合作
- 上线 1 个月：数万开发者、数百万次 MCP 服务调用

### MCP 1.0 的痛点
生成出行指南后，实际导航需要 6 个步骤：
> 复制 → 切换 → 粘贴 → 搜索 → 启动导航 → 返回攻略

完成整个攻略需要几十甚至上百次机械化复制粘贴和 APP 切换。

### MCP 2.0（2025年4月发布）
核心改进：**与高德地图 APP 无缝打通**

新能力：
1. **专属地图 Tools**：生成专属地图导入高德地图 APP，支持打车、导航、酒店预订、门票预订、餐厅预订、加油充电等一站式服务
2. **唤端 Tools & 动态地图**：在出行计划中嵌入动态地图，支持一键导航、打车等功能

## MCP 2.0 接入方式

### SSE 端点（微信文章示例）
```json
{
  "mcpServers": {
    "amap-amap-sse": {
      "url": "https://mcp.amap.com/sse?key=***"
    }
  }
}
```

### Streamable HTTP 端点（官方 gettingstarted 推荐）
```json
{
  "mcpServers": {
    "amap-maps-streamableHTTP": {
      "url": "https://mcp.amap.com/mcp?key=***"
    }
  }
}
```

## 应用案例

### 案例1：寻找约会中间点
MCP 1.0 能找到双方最方便的约会地点；MCP 2.0 可以把约会地点导入高德 APP，分享给好友，看到双方实时位置。

### 案例2：制作旅游攻略
MCP 1.0 能做详细攻略；MCP 2.0 可在 Web 端生成可视化地图的同时，调用高德 APP 一键生成专属地图，每日行程结合实时路况。

### 案例3：昆明4天旅行攻略（文中示例）
- 使用 Cursor + AMAP MCP SSE 连接
- 大模型生成 HTML 旅行攻略页面（含天气、景点卡片、地图、打车链接）
- 效果预览：https://a.amap.com/jsapi_demo_show/static/feitian_data_view/kmTravel.html

## 官方文档参考
- 快速接入：https://lbs.amap.com/api/mcp-server/gettingstarted
- API Key 申请：https://console.amap.com/dev/key/app
- Node.js 要求：≥ v22.14.0（仅 npx 方式需要）
- npm registry：需为默认源 https://registry.npmjs.org（仅 npx 方式需要）

## MCP 2.0 完整工具列表（15 个工具）

来源：高德官方文档 `https://lbs.amap.com/api/mcp-server/summary`（2026-03-17 更新）

### MCP 2.0 专属工具（MCP 1.0 无）

| 工具 | 功能 | 输入 | 输出 |
|------|------|------|------|
| 生成专属地图 | 行程导入高德 APP，生成私有地图 | 行程名称、每日行程描述、途径点位 | 专属地图唤端链接 |
| 导航到目的地 | 一键启动高德导航 | 目的地经纬度 | 高德导航唤端链接 |
| 打车 | 一键发起高德打车 | origin + destination 经纬度 | 高德打车唤端链接 |

### 基础地理工具（MCP 1.0 和 2.0 均有）

| 工具 | 功能 |
|------|------|
| 地理编码 | 地址 → 经纬度 |
| 逆地理编码 | 经纬度 → 地址 |
| IP 定位 | IP → 位置信息 |
| 天气查询 | city/adcode → 天气预报 |
| 骑行路径规划 | ≤500km 骑行路线 |
| 步行路径规划 | ≤100km 步行路线 |
| 驾车路径规划 | 小客车/轿车通勤方案 |
| 公交路径规划 | 综合公共交通（火车/公交/地铁），跨城需传 city + cityd |
| 距离测量 | 两点距离+耗时 |
| 关键词搜索 | keywords → POI 列表 |
| 周边搜索 | location + radius → POI 列表 |
| 详情搜索 | POI ID → 详细信息 |

## 旅游规划应用案例

来源：高德官方文档 `https://lbs.amap.com/api/mcp-server/application-case/tourism-planning`（2026-03-17 更新）

### 案例：北京 3 天端午旅行攻略

使用高德 MCP 2.0 + 通义灵码编程智能体生成包含以下内容的 HTML 旅行攻略页面：
- 天气卡片（3 天天气详情 + 旅行小贴士）
- 每日行程计划（每天 3 个景点）
- 网页地图自定义绘制旅游路线和位置
- 简约美观页面风格，景区图片以卡片展示
- 行程可导入高德地图 APP 生成专属地图
- 同天行程景区间生成打车链接
- 输出文件名：`travel_tips.html`

示例效果预览：https://lbs.amap.com/fn/iframe?path=mcp-server/example/customization

### 关键能力流程

```
描述需求 → MCP 搜索景点/天气 → MCP 规划路线 → 
生成 HTML 页面（含地图 + 打车链接） → 导入高德 APP 专属地图
```
