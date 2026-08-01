# 竞赛答题展示页 — fetch() 直连 Supabase 模式

## 场景

大屏投影的竞赛答题系统：后台管理题库 → 前端随机抽题 → 大屏展示 → 点击出答案。

## 架构选择

❌ **CDN SDK**：`@supabase/supabase-js@2` 在部分网络下 JSONB 解析异常 + 分页截断
✅ **原生 fetch()**：零依赖，`limit=1000` 确保全量，类型安全包装

## 核心代码

### 数据加载

```javascript
const API_BASE = 'https://{project_ref}.supabase.co/rest/v1';
const API_KEY = 'sb_publishable_...';
const HEADERS = { 'apikey': API_KEY, 'Authorization': 'Bearer ' + API_KEY, 'Accept': 'application/json' };

async function fetchTable(table) {
  var resp = await fetch(API_BASE + '/' + table + '?select=*&order=id&limit=1000', { headers: HEADERS });
  var data = await resp.json();
  // 关键：options 字段类型安全检查
  for (var i = 0; i < data.length; i++) {
    var opts = data[i].options;
    if (opts === null || opts === undefined) { data[i].options = null; continue; }
    if (Array.isArray(opts)) continue;
    if (typeof opts === 'string') {
      try { data[i].options = JSON.parse(opts); } catch(e) { data[i].options = null; }
    } else {
      data[i].options = null;
    }
  }
  return data;
}

// 并行加载
var results = await Promise.all([
  fetchTable('questions_required'),
  fetchTable('questions_quick'),
  fetchTable('questions_mediation'),
  fetch(API_BASE + '/exam_config?select=*&limit=1', { headers: HEADERS }).then(function(r) { return r.json(); })
]);
questionPool.required = results[0];
questionPool.quick = results[1];
questionPool.mediation = results[2];
```

### Option Rendering (simplest possible — rely on pre-standardized data)

```javascript
function renderOptsHTML(q) {
  // 判断题：显示 √/× 按钮
  if (q.question_type === '判断题') {
    return '<div class="judge-options">' +
      '<div class="judge-item" id="j-true">√</div>' +
      '<div class="judge-item" id="j-false">×</div>' +
      '</div>';
  }

  var opts = q.options;
  if (!opts || !Array.isArray(opts) || opts.length === 0) {
    return '<div class="opts"><div class="opt" style="color:#dc2626">' +
      '⚠️ 选项缺失 [' + q.id + ']</div></div>';
  }

  // 关键：字母从索引硬编码（String.fromCharCode(65+i)），不依赖正则匹配前缀
  // 前提：选项中已标准化为 "A.xxx" "B.xxx" 格式（数据库迁移确保）
  return '<div class="opts">' + opts.map(function(o, i) {
    return '<div class="opt" id="opt-' + String.fromCharCode(65 + i) + '">' +
      '<span class="o">' + String.fromCharCode(65 + i) + '</span>' +
      '<span>' + esc(String(o).replace(/^[A-D]\.\s*/, '')) + '</span>' +
      '</div>';
  }).join('') + '</div>';
}
```

### Option Standardization Script (run once after LLM import)

```python
import re, json, psycopg2

def normalize_option(opt, letter):
    """统一为 A.xxx 格式"""
    opt = str(opt).strip()
    # 去掉所有已知前缀变体
    stripped = re.sub(r'^[A-Da-d][.\u3001\uFF0C\s\)）．:：]+', '', opt).strip()
    return f'{letter}.{stripped}' if stripped else f'{letter}.{opt}'

for table in ['questions_required', 'questions_quick']:
    cur.execute(f"SELECT id, options FROM {table} WHERE question_type IN ('单选题','多选题')")
    for qid, opts in cur.fetchall():
        if not opts: continue
        new_opts = [normalize_option(o, chr(65+i)) for i, o in enumerate(opts)]
        if new_opts != opts:
            cur.execute(f'UPDATE {table} SET options = %s WHERE id = %s', (json.dumps(new_opts), qid))
```

**原则**：选项格式在数据库层标准化 → 前端代码极简。不要反向兼容所有格式。

## Common Pitfalls (by discovery order — most time-wasting first)

| # | 现象 | 原因 | 修复 |
|---|------|------|------|
| 1 | **部分题目有选项、部分没有**（间歇性，最难定位） | **`overflow: hidden` 裁剪了超出可视区的长内容**。题文 36px 多行 + 4 选项 + 答案区 → 总高超视口 → 底部选项被切掉 | 主区域 `overflow-y: auto` + 卡片 `margin: auto 0`。**排查顺序**：先查数据库 → API → JS → CSS 颜色/可见性 → 最后才想到 overflow。花了几小时绕圈子 |
| 2 | 单选题无选项显示 | `q.options` 在 fetch 响应中为 JSON string 而非 array | `ensureOptionsArray()` 做类型检查 + JSON.parse 降级 |
| 3 | 某个选项字母消失（如只有 BCD 三项） | **正则匹配选项前缀失败**：选项分隔符有 `.  、  ，  )  ）  ．  :  ：` 等多种格式 | ① 入库前**标准化所有选项为 `A.xxx` 格式**（数据库迁移脚本 + LLM 导入后自动规范）② 前端剥离正则简化为 `replace(/^[A-D]\.\s*/, '')`。不要试图在渲染层兼容所有分隔符 |
| 4 | 数据不全 | `select('*')` 未指定 limit | 所有 select 加 `.limit(1000)` |
| 5 | 去重误删大量合法题目 | `question_text[:60]` 前缀截取 —— 不同题目末尾不同但前缀相同 | 用 `hashlib.md5(question_text + '|'.join(options)).hexdigest()` 完整 hash |
| 6 | LLM 补全选项后答案错位 | 多选题在 docx 中答案为 "BCD"，LLM 重排选项后答案变成 "A" | LLM 补全后**必须逐题交叉验证**：数据库答案 vs 原始 docx 答案 |
| 7 | 多选题被误标为单选题 | `question_type` 未随答案修正 | 入库后做 `LENGTH(correct_answer) > 1` → 自动修正 `question_type` |
| 8 | 判断题显示"无选项" | `renderOptions` 在判断题分支后仍调用 ensureOptionsArray(null) | 判断题分支必须 return 在最前面 |
| 9 | **无法复现用户反馈的 bug** | CDP/computer-use 连接不上，看不到用户浏览器实际状态 | 嵌入可见调试面板（见下文） |

## 前端调试面板（无 CDP 时的诊断手段）

当 remote debugging 不可用时，在页面内嵌调试面板是唯一的诊断方式。核心思路：

### 1. 全局错误捕获 + 数据校验输出

```javascript
window.onerror = function(msg, src, line) {
  updateDebug(msg + ' @ ' + src + ':' + line, 'err');
};

// 初始化时输出校验信息
var badCount = 0;
questionPool.required.forEach(function(q) {
  if ((q.question_type === '单选题' || q.question_type === '多选题') && 
      (!q.options || !Array.isArray(q.options) || q.options.length < 2)) {
    badCount++;
    updateDebug('BAD options id=' + q.id + ' type=' + q.question_type, 'err');
  }
});
updateDebug(badCount === 0 ? '所有选项验证通过' : badCount + ' 题选项异常');
```

### 2. 选项缺失时可见标记（用户可截图反馈）

```javascript
function renderOptsHTML(q) {
  var opts = q.options;
  if (!opts || !Array.isArray(opts) || opts.length === 0) {
    // 红色警告而非空白——用户能截图反馈具体 ID
    return '<div class="option-item" style="color:#dc2626;font-weight:700;grid-column:1/-1">'
      + '选项缺失 (ID=' + q.id + ' type=' + q.question_type + ')</div>';
  }
  // ... 正常渲染
}
```

### 3. 键盘快捷键切换

```javascript
// D 键切换调试面板
document.addEventListener('keydown', function(e) {
  if (e.key === 'd' || e.key === 'D') {
    var dp = document.getElementById('debug-panel');
    dp.style.display = dp.style.display === 'none' ? 'block' : 'none';
  }
});
```

```html
<!-- 底部红色调试面板，初始化后自动隐藏 -->
<div id="debug-panel" style="position:fixed;bottom:0;left:0;right:0;background:#fef2f2;
  border-top:2px solid #dc2626;padding:8px 16px;font-size:12px;font-family:monospace;
  max-height:100px;overflow-y:auto;z-index:999;display:none"></div>
```

### 设计原则

1. 初始化完成 + 无异常时自动隐藏
2. 检测到异常保持显示并标红
3. 按 D 键随时切换
4. 选项缺失用**红色警告 + 题目 ID**，用户可截图精准反馈
5. 调试信息用 monospace 字体，可滚动

## CSS 白底大屏投影模式

```css
:root {
  --bg: #ffffff;       /* 白底 */
  --text: #1e293b;     /* 深色文字 */
  --text2: #64748b;    /* 次要文字 */
  --border: #e2e8f0;   /* 浅灰边框 */
  --primary: #4f46e5;  /* 靛蓝主色 */
  --success: #16a34a;  /* 绿色正确答案 */
}
option-item {
  background: #f8fafc;  /* 浅灰卡片 */
  border: 2px solid #e2e8f0;
  font-size: 22px;
}
question-text {
  font-size: 36px;   /* 大字号适合投影 */
  font-weight: 700;
}
```
