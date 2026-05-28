# Interactive Demo SPA Template

适用场景：客户演示用的功能原型，非静态展示页。客户可在浏览器中点击操作，体验完整系统流程。

## 与 static proposal 的关键区别

| 维度 | 静态方案页 | 交互式Demo |
|------|-----------|-----------|
| 数据 | 写死的HTML内容 | JS mock数据数组，可运行时增删改 |
| 交互 | 锚点跳转、hover效果 | 搜索筛选、表单提交、模态框CRUD、步骤流 |
| 目标 | 展示方案内容 | 让客户"操作一遍"感受系统 |

## 标准模块结构

用户常要求5-6个模块的交互式Demo：

```
├─ 首页 (Home)        — 数据仪表盘 + 快捷入口 + 业务流程
├─ 核心业务模块1      — 列表+搜索筛选+详情弹窗+操作按钮
├─ 核心业务模块2      — 同上模式，根据实际业务定制
├─ 表单注册模块       — 多步骤表单 + 验证 + 提交确认
├─ 后台管理 (Admin)   — 子Tab切换 + 数据CRUD + 状态管理
└─ 可选: 公示/报表等   — 表格+筛选+查看详情
```

## 技术模式

### 数据层（全部 JS mock）

```javascript
// 所有数据用 JS 数组存储，运行时可变
let items = [
  { id:'XX-001', name:'示例项目', status:'进行中', ... },
];

// 搜索筛选：前端 filter
function renderTable() {
  const search = document.getElementById('search').value.toLowerCase();
  let data = items.filter(i => i.name.toLowerCase().includes(search));
  // render to table body
}
```

### 导航系统

```javascript
// 顶层Tab：页面级切换
function switchToPage(pageName) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + pageName).classList.add('active');
  // 激活对应导航链接，滚动到顶部
}

// 子Tab：页面内切换（如后台管理的子模块）
function switchAdminTab(tab, el) {
  document.querySelectorAll('#page-admin .sub-tab').forEach(t => /* deactivate */);
  el.classList.add('active');
  // 显示/隐藏对应的子面板
}
```

### 模态框模式

```html
<!-- 模态框骨架：overlay + modal + header/body/footer -->
<div class="modal-overlay" id="modalFoo">
  <div class="modal">
    <div class="modal-header"><h3>标题</h3><button class="modal-close">✕</button></div>
    <div class="modal-body"><!-- 动态填充 --></div>
    <div class="modal-footer"><!-- 操作按钮 --></div>
  </div>
</div>
```

关键交互：
- `modal-overlay.show` 类控制显示/隐藏
- 点击遮罩层关闭：`overlay.addEventListener('click', e => { if (e.target === overlay) close(); })`
- ESC键关闭：`document.addEventListener('keydown', e => { if (e.key === 'Escape') closeAll(); })`

### 多步骤表单

```javascript
let currentStep = 1;

function goToStep(n) {
  // 前进时验证当前步骤
  if (n > currentStep && !validateCurrentStep()) return;
  currentStep = n;
  // 隐藏所有步骤卡片，显示目标步骤
  // 更新步骤指示器（done / active 状态）
}
```

### Toast 通知

```javascript
// 简单的顶部滑入通知
function showToast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast ' + (type || ''); // type: 'success' 绿色
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}
```

## 设计规范

- **配色**：商务蓝 `#1a56db` 为主色，配合绿/橙/红用于状态标签
- **卡片**：白底 + 1px border + 12px圆角，hover轻微上浮
- **表格**：灰色表头 + hover行高亮
- **Badge**：圆角徽章，用颜色区分状态
- **按钮**：primary/success/danger/outline 四类
- **响应式**：mobile 时隐藏导航链接、grid 改为单列

## 验收清单

部署前逐项检查：

- [ ] 5个页面模块均已实现且有内容
- [ ] 搜索筛选功能可正常使用
- [ ] 模态框可打开/关闭（按钮+遮罩+ESC）
- [ ] 多步表单可走完全流程（含验证拦截）
- [ ] 后台管理CRUD操作可执行且有反馈
- [ ] Toast通知正常弹出和消失
- [ ] 所有按钮有视觉反馈（颜色/光标变化）
- [ ] 移动端布局不断裂
- [ ] 无 `#contact` + alert 空跳转
- [ ] 无行内注释打断 HTML 标签

## 本模板来源

基于「采购招标系统」交互Demo实战（2026-05-27）。5模块：首页、招标公告、招采公示、供应商注册、后台管理。49KB 单文件 SPA，部署于 OSS。
