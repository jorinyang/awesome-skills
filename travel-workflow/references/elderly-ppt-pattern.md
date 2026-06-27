# 老年友好 PPT 模式

> 用于 travel-workflow 场景中生成长辈演示文稿。不依赖 html-ppt 预置模板，手写内联 HTML。

## 触发条件

- 行程受众含 65+ 岁老人
- 用户明确说"给父母/长辈看的PPT"
- 家庭聚会方案需要演示

## 字号基线

| 元素 | 最小字号 | 建议 |
|------|:------:|------|
| 封面标题 | 2.5rem | clamp(2.5rem, 5vw, 4rem) |
| 页面标题 | 1.8rem | clamp(1.8rem, 3.5vw, 2.5rem) |
| 卡片标题 | 1.5rem | 加粗 |
| 时间标签 | 1.5rem | 加粗 + 暖色调 |
| 正文说明 | 1.3rem | 行距 1.8 |
| 辅助文字 | 1.1rem | 加粗，不用 0.95rem |

## 配色

米白底暖金调——温馨庄重，不刺眼：

```css
--gold: #C8A96E;        /* 时间/强调 */
--gold-light: #F5EDE0;  /* 背景渐变 */
--ink: #2C2C2C;         /* 主文字 */
--warm-white: #FFFBF5;  /* 页面底色 */
--soft-gray: #6B6B6B;   /* 说明文字 */
--accent: #A0522D;      /* 标题强调 */
```

## 内容密度

- 每页 ≤ 6 个时间线项
- 总览页用卡片网格（2×3）
- 详情页用左侧时间 + 右侧内容卡布局

## 翻页

键盘 ← → Space PgUp PgDn Home End，移动端 touch swipe。

## 部署

生成后部署到 OSS `web-spa/{slug}/index.html`，参考 feishu-html 阶段六。
