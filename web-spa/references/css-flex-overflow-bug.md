# CSS Flex 居中 + Overflow 剪切 Bug

## 复现条件

```html
<div style="display:flex;align-items:center;justify-content:center;height:100vh;overflow-y:auto">
  <div style="max-width:960px">
    <!-- 内容超过视口高度时 -->
  </div>
</div>
```

## 症状

内容超过视口高度时：
- **上半部分**被裁切且无法滚动到
- **下半部分**（含 D 选项、答案区）落在可视区外
- 滚动条存在但滚动不到顶部/底部

## 根因

`align-items: center` 让 flex 容器把子元素推到垂直正中。当子元素高度 > 容器高度时，子元素的中心仍在容器中心，导致子元素的顶部溢出到容器上方不可达区域。`overflow: auto` 无法滚动到溢出到容器上方的部分——这是 CSS flexbox 规范的已知道缺陷。

## 已验证的失败方案

| 方案 | 结果 |
|------|------|
| `align-items: center` + `overflow: auto` | ❌ 顶部裁切 |
| `justify-content: center` + `overflow: auto` | ❌ 顶部裁切 |
| `align-items: safe center` | ❌ 浏览器支持不一致 |
| CSS `margin: auto 0` on child | ⚠️ 部分可用，但受父容器 flex 属性干扰 |
| `display: table-cell` + `vertical-align: middle` | ❌ 同样裁切 |

## 唯一可靠方案：JS 动态居中

```javascript
function center() {
  setTimeout(function() {
    var card = document.getElementById('card');
    var main = document.getElementById('main');
    card.style.marginTop = '0';  // 先重置
    var ch = card.offsetHeight;
    var mh = main.clientHeight;
    if (ch < mh) {
      card.style.marginTop = Math.floor((mh - ch) / 2) + 'px';
    } else {
      card.style.marginTop = '16px';  // 内容过长时顶部留白即可
    }
  }, 50);  // 等 DOM 渲染完成
}
```

每次 `innerHTML` 更新后调用 `center()`。

## 触发条件

本 session 中触发此 bug 的页面特征：
- 全屏答题页，主区域 `flex: 1`
- 题目文字长（36px 字体）
- 选项 + 答案区总高度经常超过视口
- 必答题显示在屏投设备（1366×768 或 1024×768）
