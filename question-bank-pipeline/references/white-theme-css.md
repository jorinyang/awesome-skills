# 题库展示页白底配色方案

> 用于大屏投影展示，白底高对比度，支持三种题型颜色区分。

## CSS 变量

```css
:root {
  --bg: #ffffff;
  --surface: #f8fafc;
  --surface2: #f1f5f9;
  --border: #e2e8f0;
  --text: #1e293b;
  --text2: #64748b;
  --primary: #4f46e5;
  --primary-light: rgba(79,70,229,.08);
  --accent-required: #4f46e5;    /* 必答题：靛蓝 */
  --accent-quick: #d97706;       /* 抢答题：琥珀 */
  --accent-mediation: #db2777;   /* 调解题：玫红 */
  --success: #16a34a;
  --success-light: rgba(22,163,74,.08);
  --danger: #dc2626;
  --danger-light: rgba(220,38,38,.08);
}
```

## 组件配色

| 组件 | 背景 | 文字颜色 | 边框 |
|------|------|---------|------|
| 页面底色 | `var(--bg)` `#fff` | `var(--text)` `#1e293b` | — |
| 顶部/底部栏 | `var(--surface)` `#f8fafc` | — | `var(--border)` `#e2e8f0` |
| 卡片/选项框 | `var(--surface)` `#f8fafc` | `var(--text)` | `2px solid var(--border)` |
| 题型徽章 | 对应题型 10% 透明度 | 对应题型纯色 | — |
| 正确选项高亮 | `var(--success-light)` | `var(--success)` | `var(--success)` |
| 错误选项高亮 | `var(--danger-light)` | `var(--danger)` | `var(--danger)` |
| 答案区域 | `var(--success-light)` | `var(--text2)`/`var(--success)` | `rgba(22,163,74,.2)` |

## 字号规范（大屏投影）

| 元素 | 字号 |
|------|------|
| 主标题（开始页） | 48px / 800 |
| 题目文本 | 36px / 700 |
| 选项文字 | 22px |
| 题型徽章 | 16px |
| 答案显示 | 32px / 800 |
| 判断题按钮 | 48px / 800 |
| 导航按钮 | 16px |
| 顶部计数器 | 16px |

## 题型颜色映射

```javascript
var typeBg = q.question_type === '单选题' ? 'rgba(79,70,229,.1)'
  : q.question_type === '多选题' ? 'rgba(22,163,74,.1)' 
  : 'rgba(217,119,6,.1)';

var typeColor = q.question_type === '单选题' ? '#4f46e5'
  : q.question_type === '多选题' ? '#16a34a' 
  : '#d97706';
```
