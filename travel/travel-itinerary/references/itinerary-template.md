# 行程文档 Lark XML 模板

> 用途：生成飞书文档时的 XML 骨架。Agent 将规划结果填充到占位符后，通过 feishu-doc 技能创建。
> 占位符格式：`{{VARIABLE}}` — Agent 替换为实际内容。

## A. 客户版模板

```xml
<title>贵州之客_行程方案_{{destination}}_{{days}}天{{dates}}</title>

<callout emoji="📌" background-color="light-blue" border-color="blue">
  <grid>
    <column width-ratio="0.25"><p><b>目的地</b><br/>{{destination_full}}</p></column>
    <column width-ratio="0.25"><p><b>行程天数</b><br/>{{days}}天{{nights}}晚</p></column>
    <column width-ratio="0.25"><p><b>出行日期</b><br/>{{date_range}}</p></column>
    <column width-ratio="0.25"><p><b>人数</b><br/>{{group_size}}人</p></column>
  </grid>
</callout>

<h1>🌤️ 天气预报</h1>
<table>
  <thead><tr><th>日期</th><th>天气</th><th>温度</th><th>风力</th><th>AQI</th><th>出行建议</th></tr></thead>
  <tbody>
    {{WEATHER_ROWS}}
  </tbody>
</table>

<callout emoji="⚠️" background-color="light-yellow" border-color="yellow">
  <p><b>特别提醒：</b>{{weather_alert}}</p>
</callout>

<h1>🗺️ 每日行程</h1>
{{DAILY_ITINERARY}}

<h1>🍜 美食推荐</h1>
{{FOOD_RECOMMENDATIONS}}

<h1>💰 费用明细</h1>
<table>
  <thead><tr><th>费用项</th><th>明细</th><th>人均（元）</th></tr></thead>
  <tbody>
    {{COST_ROWS}}
  </tbody>
</table>

<callout emoji="💡" background-color="light-green" border-color="green">
  <p><b>费用总计：¥{{total_cost}}/人</b>（{{group_size}}人团，共 ¥{{group_total}}）</p>
</callout>

<h1>🎒 行前准备清单</h1>
<grid>
  <column width-ratio="0.5">
    <h3>证件类</h3>
    <checkbox done="false">身份证/护照</checkbox>
    <checkbox done="false">驾驶证（自驾）</checkbox>
    <h3>衣物类</h3>
    {{CLOTHING_CHECKLIST}}
  </column>
  <column width-ratio="0.5">
    <h3>装备类</h3>
    {{GEAR_CHECKLIST}}
    <h3>药品类</h3>
    <checkbox done="false">晕车药</checkbox>
    <checkbox done="false">肠胃药</checkbox>
    <checkbox done="false">创可贴</checkbox>
  </column>
</grid>

<h1>📞 实用贴士</h1>
<callout emoji="📞" background-color="light-blue" border-color="blue">
  <p><b>紧急联系：</b></p>
  <ul>
    <li>导游：待填写</li>
    <li>车队：待填写</li>
    <li>报警：110 | 急救：120 | 交通事故：122</li>
    <li>旅游投诉：12301</li>
  </ul>
</callout>
<ul>
  {{TIPS}}
</ul>
```

## B. 每日行程 XML 模板（填充到 `{{DAILY_ITINERARY}}`）

```xml
<h2>Day {{N}} — {{date}}（{{weekday}}）{{weather_emoji}} {{weather_summary}}</h2>

<callout emoji="🌅" background-color="light-orange" border-color="orange">
  <p><b>主题：{{day_theme}}</b> | 移动距离约 {{day_distance}}km | {{day_play_hours}}小时游玩</p>
</callout>

<h3>上午</h3>
<table>
  <thead><tr><th>时间</th><th>活动</th><th>地点</th><th>备注</th></tr></thead>
  <tbody>
    {{MORNING_ROWS}}
  </tbody>
</table>

<h3>午餐</h3>
<p>🍽️ 推荐：<b>{{lunch_spot}}</b> | 人均约 ¥{{lunch_cost}} | {{lunch_signature}}</p>

<h3>下午</h3>
<table>
  <thead><tr><th>时间</th><th>活动</th><th>地点</th><th>备注</th></tr></thead>
  <tbody>
    {{AFTERNOON_ROWS}}
  </tbody>
</table>

<h3>晚餐 + 住宿</h3>
<p>🍽️ <b>{{dinner_spot}}</b> | 人均约 ¥{{dinner_cost}}</p>
<p>🏨 <b>{{hotel_name}}</b> | {{hotel_area}} | 约 ¥{{hotel_cost}}/晚</p>

<callout emoji="🚗" background-color="light-blue" border-color="blue">
  <p><b>今日交通：</b></p>
  <ul>
    {{TRAFFIC_ROWS}}
  </ul>
</callout>

<callout emoji="🌧️" background-color="light-yellow" border-color="yellow">
  <p><b>雨天备选方案：</b>{{rain_plan}}</p>
</callout>
<hr/>
```

## C. 地接版追加模板（拼接到客户版后）

```xml
<h1>🚌 交通执行明细（地接版）</h1>
<table>
  <thead><tr><th>日期</th><th>出发</th><th>抵达</th><th>距离</th><th>预估耗时</th><th>备选路线</th><th>备注</th></tr></thead>
  <tbody>
    {{GROUND_TRAFFIC_ROWS}}
  </tbody>
</table>

<h1>📞 供应商联系清单</h1>
<table>
  <thead><tr><th>类型</th><th>名称</th><th>联系人</th><th>电话</th><th>地址</th><th>确认状态</th></tr></thead>
  <tbody>
    <tr><td>酒店</td><td>{{hotel_name_day1}}</td><td>待填写</td><td>待填写</td><td>{{hotel_addr_day1}}</td><td>⬜</td></tr>
    <tr><td>酒店</td><td>{{hotel_name_day2}}</td><td>待填写</td><td>待填写</td><td>{{hotel_addr_day2}}</td><td>⬜</td></tr>
    <tr><td>餐厅</td><td>{{restaurant_1}}</td><td>待填写</td><td>待填写</td><td>{{restaurant_addr_1}}</td><td>⬜</td></tr>
    <tr><td>车队</td><td>{{fleet_name}}</td><td>待填写</td><td>待填写</td><td>—</td><td>⬜</td></tr>
    <tr><td>景区</td><td>各景区管理处</td><td>—</td><td>—</td><td>—</td><td>⬜</td></tr>
  </tbody>
</table>

<h1>🧾 物资清单</h1>
<grid>
  <column width-ratio="0.33">
    <h3>团队物资</h3>
    <checkbox done="false">手持喇叭</checkbox>
    <checkbox done="false">队旗/标识</checkbox>
    <checkbox done="false">急救包</checkbox>
    <checkbox done="false">备用雨衣 ×{{group_size}}</checkbox>
    <checkbox done="false">饮用水 每人 2 瓶/天</checkbox>
  </column>
  <column width-ratio="0.33">
    <h3>客户物资</h3>
    <checkbox done="false">行程单/地图</checkbox>
    <checkbox done="false">欢迎卡片/小礼品</checkbox>
    <checkbox done="false">充电宝</checkbox>
  </column>
  <column width-ratio="0.33">
    <h3>应急物资</h3>
    <checkbox done="false">晕车贴</checkbox>
    <checkbox done="false">腹泻药</checkbox>
    <checkbox done="false">创可贴/纱布</checkbox>
    <checkbox done="false">登山杖（如有徒步）</checkbox>
  </column>
</grid>

<h1>⚠️ 风险点位标注</h1>
<table>
  <thead><tr><th>点位</th><th>风险类型</th><th>风险等级</th><th>应对措施</th></tr></thead>
  <tbody>
    {{RISK_ROWS}}
  </tbody>
</table>

<h1>⏱️ 时间缓冲表</h1>
<table>
  <thead><tr><th>日</th><th>计划时间</th><th>缓冲（+min）</th><th>雨天备选</th></tr></thead>
  <tbody>
    {{BUFFER_ROWS}}
  </tbody>
</table>
```

## D. 关键占位符说明

| 占位符 | 数据类型 | 来源 | 示例 |
|--------|---------|------|------|
| `{{WEATHER_ROWS}}` | HTML `<tr>` × N | weather MCP | `<tr><td>6/15</td><td>☀️晴</td><td>22-30°C</td>...</tr>` |
| `{{DAILY_ITINERARY}}` | HTML block × N | LLM 编排 | 每日行程的完整 HTML |
| `{{COST_ROWS}}` | HTML `<tr>` × N | LLM 汇总 | `<tr><td>住宿</td><td>3晚×300元</td><td>900</td></tr>` |
| `{{GROUND_TRAFFIC_ROWS}}` | HTML `<tr>` × N | amap 路线 | 含主选+备选双行 |
| `{{RISK_ROWS}}` | HTML `<tr>` × N | 天气+路况分析 | 暴雨/山路/体能 |
| `{{BUFFER_ROWS}}` | HTML `<tr>` × N | LLM 计算 | 每段 +20-30% 时间 |
