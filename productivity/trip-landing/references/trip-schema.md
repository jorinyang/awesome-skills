# Trip Data JSON Schema v2

## 顶层结构

```json
{
  "title": "黔西南3日亲子游",
  "slug": "qianxinan-3day-family",
  "total_days": 3,
  "stops_count": 8,
  "overview": "行程简介/背景介绍文本...",
  "background": "目的地文化/地理背景介绍...",
  "highlights": ["亮点1", "亮点2", "亮点3"],
  "difficulty": "轻松 | 适中 | 挑战",
  "best_season": "全年 | 3-10月",
  "essentials": ["必备物品1", "必备物品2", "..."],
  "precautions": ["注意事项1", "注意事项2", "..."],
  "safety": {
    "protection": "户外防护措施说明...",
    "self_rescue": "自救知识说明...",
    "disaster": "灾害天气提醒...",
    "emergency_procedures": "意外事故处置流程..."
  },
  "emergency_contacts": [
    {"name": "贵州之客客服", "phone": "139xxxx", "icon": "service"},
    {"name": "紧急救援", "phone": "110 / 120", "icon": "emergency"},
    {"name": "景区救援", "phone": "0859-xxxx", "icon": "local"}
  ],
  "days": [...],
  "transport": [...],
  "pricing_note": "价格说明文本（可选）",
  "inclusions": ["包含项目1", "包含项目2"],
  "exclusions": ["不含项目1", "不含项目2"]
}
```

## Day 对象

```json
{
  "day": 1,
  "title": "兴义万峰林 + 马岭河峡谷",
  "stops": [
    {
      "name": "万峰林景区",
      "lng": 104.895503,
      "lat": 25.091960,
      "formatted_name": "贵州省黔西南布依族苗族自治州兴义市万峰林景区",
      "duration": "4小时",
      "activity_type": "观光 | 徒步 | 摄影 | 探险 | 亲子 | 美食",
      "description": "简短描述（可选）"
    }
  ],
  "hotel": "兴义富康国际酒店",
  "hotel_lng": 104.88,
  "hotel_lat": 25.08,
  "weather": {
    "date": "2026-07-15",
    "day_weather": "晴",
    "night_weather": "多云",
    "high": 28,
    "low": 20,
    "aqi": 35,
    "air_level": "优",
    "wind": "南风 2级",
    "humidity": "65%"
  }
}
```

## Transport 对象

```json
{
  "from": "万峰林景区",
  "to": "马岭河峡谷",
  "from_lng": 104.895503,
  "from_lat": 25.091960,
  "to_lng": 104.95,
  "to_lat": 25.12,
  "distance_km": 15.3,
  "duration_min": 30
}
```

## Safety 对象结构

```json
{
  "protection": "## 户外防护\n- 防晒：SPF50+ 防晒霜，每2小时补涂\n- 防蚊：携带驱蚊液，穿长袖长裤\n- 防滑：穿防滑登山鞋，雨天注意湿滑路段\n- 饮水：每人每天至少携带1.5L饮用水",
  "self_rescue": "## 基础自救\n- 迷路：保持冷静，原路返回或拨打景区救援电话\n- 扭伤：立即停止活动，冷敷患处，抬高受伤部位\n- 中暑：转移到阴凉处，补充水分和电解质\n- 蛇咬：记住蛇的特征，保持伤口低于心脏，立即就医",
  "disaster": "## 天气灾害提醒\n- 雨季（6-8月）：注意山洪、滑坡预警\n- 雷暴：远离高地、孤立大树、金属物体\n- 暴雨：立即撤离河道、峡谷等低洼地带\n- 关注当地气象预警（短信 / 微信公众号）",
  "emergency_procedures": "## 意外处置流程\n1. 保持冷静，评估现场安全\n2. 拨打紧急电话（见上方联系方式）\n3. 向领队/导游报告，启动应急预案\n4. 在安全地点等待救援，不要单独行动\n5. 配合救援人员，提供准确位置信息"
}
```

## 行程文档格式（支持的变体）

### 格式 A：英文 Day 标题
```
Day 1: 兴义万峰林 → 马岭河峡谷 → 宿兴义市区
Day 2: 兴义市区 → 安龙招堤 → 安龙古城 → 返程
```

### 格式 B：中文数字天
```
第一天：万峰林景区（4小时）、马岭河峡谷（3小时）、住宿兴义富康酒店
第二天：安龙招堤（2小时）、安龙古城（2小时）、返程兴义
```

### 格式 C：简写
```
D1 万峰林 / 马岭河 / 宿兴义
D2 安龙招堤 → 古城 → Return
```

### 格式 D：结构化文本
```
第1天 兴义万峰林景区
  建议游玩4小时
  下午：马岭河峡谷
  晚上入住兴义市区酒店

第2天 兴义→安龙
  上午：安龙招堤
  下午：安龙古城
  傍晚返程兴义
```

## 附加段落格式（文档中行程之后的部分）

提取器会识别以下段落标题并自动分类提取：

| 段落标题关键词 | 映射字段 |
|-------------|---------|
| 行程背景 / 目的地介绍 / 线路介绍 | `overview`, `background` |
| 行程亮点 / 特色体验 | `highlights` |
| 必备物品 / 行前准备 / 携带物品 | `essentials` |
| 注意事项 / 禁忌 / 温馨提示 | `precautions` |
| 安全须知 / 安全保障 / 户外安全 | `safety` |
| 紧急联系 / 联系方式 / 救援电话 | `emergency_contacts` |
| 费用说明 / 价格说明 / 包含费用 | `pricing_note`, `inclusions`, `exclusions` |
| 难度等级 / 适合人群 | `difficulty` |
| 最佳季节 / 推荐时间 | `best_season` |
