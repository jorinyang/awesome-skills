---
name: amap-cli
description: "高德开放平台 CLI (amap-gui)：精确控制地图状态、POI搜索、路线规划的命令行工具。用于需要地图可视化交互的场景。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [AMap, CLI, Map, GUI]
    related_skills: [amap-lbs]
---

# 高德开放平台 CLI (`amap-gui`)

高德开放平台提供标准化的命令行工具 `amap-gui`，使 AI Agent 能够精确控制地图状态、搜索兴趣点 (POI) 和进行路线规划。

> **注意**：`amap-gui` 是一个 GUI 工具，需要图形显示环境（X11/Wayland）。在无头环境中无法直接使用。对于无头场景，请使用 `amap-lbs` 技能（REST API）或 AMAP MCP Server。

## 前置条件

### 1. 安装

最新稳定版 `@amap-lbs/amap-gui` v1.0.3（依赖 Electron，安装时会下载 Electron 二进制 ~100MB）。

**标准安装**（npm 官方源）：
```bash
npm install -g @amap-lbs/amap-gui
```

**中国网络安装**（npm 镜像 + Electron 镜像双管齐下）：
```bash
# 方案A: 切换 npm 源后安装
npm config set registry https://registry.npmmirror.com
ELECTRON_MIRROR="https://npmmirror.com/mirrors/electron/" npm install -g @amap-lbs/amap-gui

# 方案B: 单次命令不修改全局配置
ELECTRON_MIRROR="https://npmmirror.com/mirrors/electron/" \
  npm install -g --registry=https://registry.npmmirror.com @amap-lbs/amap-gui
```

> ⚠️ **常见安装失败**：`Client network socket disconnected before secure TLS connection was established` — Electron 二进制从 GitHub Releases 下载被墙。必须设置 `ELECTRON_MIRROR` 环境变量指向 npmmirror 镜像。

### 2. 获取 API Key

注册成为高德开放平台开发者，申请 **Web 平台（JS API）** 的 Key 和安全密钥：
- 控制台：https://console.amap.com/dev/key/app
- 选择「Web服务」或「Web端(JS API)」类型

### 3. 设置环境变量

```bash
export AMAP_KEY=your_amap_web_js_key
export AMAP_SECURITY_KEY=your_amap_security_key
```

## 核心命令

### 地图生命周期

```bash
# 启动地图容器（阻塞直到就绪）
amap-gui start

# 查看地图容器状态
amap-gui status

# 关闭地图容器
amap-gui stop

# 获取最后一次用户交互事件
amap-gui getLastEvent
```

### 地图状态控制 `mapState`

```bash
# 获取当前地图状态
amap-gui mapState

# 设置地图状态
amap-gui mapState --action set \
  --center 116.397,39.909 \
  --zoom 15 \
  --style dark

# 参数说明
# --action      get|set    操作类型（默认 get）
# --center      lng,lat    中心点坐标
# --zoom        3-20       缩放级别
# --rotation    0-360      旋转角度
# --pitch       0-83       俯仰角度
# --style       name       地图样式
```

**可用样式**：`normal` | `dark` | `light` | `whitesmoke` | `fresh` | `grey` | `graffiti` | `macaron` | `blue` | `darkblue` | `wine`

**返回示例**：
```json
{
  "success": true,
  "data": {
    "center": [116.397428, 39.90923],
    "zoom": 15,
    "rotation": 0,
    "pitch": 0,
    "style": "dark",
    "bounds": {
      "southWest": [116.384258, 39.902195],
      "northEast": [116.410598, 39.916265]
    }
  }
}
```

### 路径规划 `route`

```bash
# 驾车路线
amap-gui route --from 北京南站 --to 天安门 --type driving

# 步行路线
amap-gui route --from 西直门 --to 动物园 --type walking

# 骑行路线
amap-gui route --from 朝阳公园 --to 国贸 --type riding

# 公交路线（必填 --city）
amap-gui route --from 北京南站 --to 颐和园 --type transit --city 北京

# 驾车（含途经点，最多16个）
amap-gui route --from 北京 --to 上海 --type driving --waypoints 济南,南京

# 驾车策略
amap-gui route --from A --to B --type driving --policy avoid_jam

# JSON 模式（优先）
amap-gui route --json '{"from":"北京南站","to":"天安门","type":"driving"}'
```

**参数说明**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--from` | 地名\|lng,lat | ✅ | 起点 |
| `--to` | 地名\|lng,lat | ✅ | 终点 |
| `--type` | driving\|walking\|riding\|transit | ✅ | 出行方式 |
| `--from-name` | string | ❌ | 起点显示名称 |
| `--to-name` | string | ❌ | 终点显示名称 |
| `--waypoints` | p1+p2+... | ❌ | 途经点（仅 driving） |
| `--policy` | 策略 | ❌ | 驾车策略 |
| `--strategy` | 策略 | ❌ | 公交策略 |
| `--city` | string | transit必填 | 城市名 |

**驾车策略**：`fastest` | `least_fee` | `shortest` | `no_highway` | `avoid_jam`

**公交策略**：`fastest` | `least_cost` | `least_walk` | `most_comfort` | `no_subway`

### POI 搜索 `searchPOI`

```bash
# 城市内搜索
amap-gui searchPOI --keyword 星巴克 --city 北京

# 周边搜索
amap-gui searchPOI --keyword 咖啡 --center 120.15,30.28 --radius 1000

# 分页
amap-gui searchPOI --keyword 酒店 --city 上海 --pageSize 20 --pageIndex 1

# JSON 模式
amap-gui searchPOI --json '{"keyword":"餐厅","city":"北京","pageSize":10}'
```

**参数说明**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--keyword` | string | ✅ | 搜索关键词 |
| `--city` | string | 二选一 | 城市名 |
| `--center` | lng,lat | 二选一 | 周边搜索中心 |
| `--radius` | meters | ❌ | 搜索半径（默认 3000） |
| `--pageSize` | n | ❌ | 每页条数（默认 10） |
| `--pageIndex` | n | ❌ | 页码（默认 1） |

## 使用示例

```bash
# 场景：在北京搜索咖啡馆并查看路线
amap-gui start
amap-gui mapState --action set --center 116.397,39.909 --zoom 13
amap-gui searchPOI --keyword 咖啡馆 --city 北京
amap-gui route --from 当前位置 --to 国贸 --type driving --policy avoid_jam

# 完成后
amap-gui stop
```

## 注意事项

1. `amap-gui start` 会阻塞直到地图窗口就绪
2. 需要有效的图形显示环境（Windows/Linux with GUI）
3. Key 必须是 **Web 端(JS API)** 类型，不是 Web 服务类型
4. `--json` 参数优先于其他参数
5. 公交模式必须指定 `--city`

## 与其他工具的互补关系

| 工具 | 适用场景 |
|------|----------|
| `amap-gui` CLI | 需要可视化地图交互 |
| AMAP MCP Server | API 级别的地理服务（无头可用） |
| `amap-lbs` Skill | REST API 直接调用（灵活封装） |
