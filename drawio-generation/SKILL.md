---
name: drawio-generation
description: >-
  生成可编辑的 Draw.io (.drawio) 格式专业图表。支持架构图/流程图/ER图/部署图/网络拓扑等，
  导出 PNG/SVG/PDF。适用于客户提案、正式文档、PPT 嵌入等需要专业外观的场景。
  触发词："drawio" "画drawio" "生成drawio" "导出drawio" "可编辑图表"
  "专业架构图" "正式图表" "客户方案图" "PPT用图"。
version: 1.0.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [drawio, diagram, architecture, professional, export, XML]
    related_skills: [fireworks-tech-graph, architecture-diagram, double-evolution]
source: 吸收自 deepjai-way/ai-viz (MIT) — 提取 + 适配为 Hermes 原生技能
---

# Draw.io 专业图表生成

生成可编辑的 Draw.io XML 格式图表。不同于 SVGO（一次性静态图），Draw.io 文件可被 Draw.io Desktop / VS Code 插件 / app.diagrams.net 打开编辑，支持导出 PNG/SVG/PDF。

**定位**：`fireworks-tech-graph` 做快速 SVG 可视化，`drawio-generation` 做正式可交付图表。选择规则见下方的「格式选择指南」。

---

## 触发条件

### 自动触发

当用户消息中出现以下任一信号时自动触发：

- "drawio" / "画 drawio" / "用 drawio"
- "可编辑的图" / "专业图表" / "正式图表"
- "客户方案图" / "PPT 用图" / "对外展示图"
- 用户明确说"不要 SVG，要能改的图"
- 上下文是「对外交付/提案/正式评审」场景

### 格式选择指南（与 fireworks-tech-graph 的分工）

| 场景 | 推荐技能 |
|------|---------|
| 内部讨论 / 快速草图 | `fireworks-tech-graph` (SVG) |
| README / 技术文档 | `fireworks-tech-graph` (SVG+Mermaid) |
| 客户提案 / 投标方案 | **本技能** (Draw.io → PNG导出) |
| PPT 嵌入 / 正式汇报 | **本技能** (Draw.io → SVG/PNG导出) |
| 需要后续编辑协作 | **本技能** (Draw.io 可编辑) |
| 白底黑字+蓝红风格 | `fireworks-tech-graph` (SVG) 或本技能均可 |

---

## 工作流

### Step 1: 知识源提取

```
- 若用户指定了文档/代码路径 → 读取文件，提取结构
- 若自然语言描述 → 从描述中提取实体、关系、层次
- 不凭空创造结构——所有节点和连线必须有来源
```

### Step 2: 图种确认

```
高置信度（DDL → ER图，Swagger → 时序图，K8s → 部署图）
  → 直接执行，附理由
低置信度（一份设计文档可能画架构图也可能画数据流图）
  → 推荐主选 + 备选，等确认
```

### Step 3: 结构提取

```
- 识别节点（实体/服务/参与者）
- 识别关系（调用/依赖/数据流）
- 识别层次（分层/分组/泳道）
- 识别复杂度等级（节点数 ≤8 / 9-15 / 16-20 / >20）
```

### Step 4: 布局规划

```
- 加载设计语言配色（见下方设计语言注入）
- 应用渲染规格（见下方布局规范）
- 计算坐标网格（全部最小单位 10px 对齐）
- 复杂度分级策略：
  ┌──────────┬─────────────┬──────────────────────┐
  │ 节点数    │ 间距策略     │ 处理                  │
  ├──────────┼─────────────┼──────────────────────┤
  │ ≤ 8      │ 紧凑 (h=200, v=150) │ 单区域          │
  │ 9-15     │ 标准 (h=250, v=180) │ 2-3 逻辑分组     │
  │ 16-20    │ 宽松 (h=300, v=200) │ 分层+路由走廊    │
  │ > 20     │ —           │ 建议拆分为多张图       │
  └──────────┴─────────────┴──────────────────────┘
```

### Step 5: 生成 Draw.io XML

```
- 按照 XML Schema 生成 .drawio 文件
- 节点用 mxCell+mxGeometry
- 连线用 edge + source/target
- 容器用 parent 引用
- 所有 HTML 值用 html=1 属性
```

### Step 6: 质量自检（强制）

生成后逐项检查（详见下方「质量控制」）：

```
- [ ] XML 标签正确闭合
- [ ] 所有 mxCell id 唯一
- [ ] 连线均有标注（说明传递内容）
- [ ] source/target 引用存在
- [ ] 布局方向一致
- [ ] 配色符合设计语言
- [ ] 核心节点 ≤ 20
- [ ] 无元素重叠
- [ ] 特殊字符转义（& → &amp;，< → &lt;，> → &gt;）
- [ ] 含 HTML 值的节点 style 有 html=1
```

### Step 7: 输出

```
1. .drawio 文件
2. 摘要：图种 + 节点数 + 关键结构说明
3. 打开方式提示：
   - VS Code + Draw.io Integration 插件
   - Draw.io Desktop（双击打开）
   - app.diagrams.net（在线导入）
4. 若为对外场景 → 主动询问是否需要导出 PNG/SVG
```

---

## 设计语言注入

### 用户级默认配色

**遵循用户全局偏好**（来自 `~/.hermes-feishu/design-language.yaml`）：

| 语义槽位 | 白底风格 drawio 颜色 | 用途 |
|---------|---------------------|------|
| primary | fillColor=#DBEAFE, strokeColor=#2563EB | 核心业务服务 |
| secondary | fillColor=#D1FAE5, strokeColor=#059669 | 外部系统/接入层 |
| accent | fillColor=#FEF3C7, strokeColor=#D97706 | 网关/关键节点 |
| muted | fillColor=#F3F4F6, strokeColor=#6B7280 | 基础设施/支撑 |
| danger | fillColor=#FEE2E2, strokeColor=#DC2626 | 告警/注意（红） |
| text | fontColor=#111827 | 主文字 |
| stroke | strokeColor=#111827 | 默认边框 |

### 项目级覆盖

```
若当前工作目录存在 design-language.yaml → 覆盖全局默认
若不存在 → 使用全局默认（零摩擦）
```

---

## XML 技术规范

### 文件骨架

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="hermes" agent="drawio-generation">
  <diagram name="Diagram Name" id="diagram-001">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10"
                  guides="1" tooltips="1" connect="1"
                  arrows="1" fold="1" page="1"
                  pageScale="1" pageWidth="1169" pageHeight="827">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- 所有图表元素以此 parent="1" -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 节点（圆角矩形）

```xml
<mxCell id="svc-order" value="&lt;b&gt;订单服务&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size:11px&quot;&gt;订单创建/支付/退款&lt;/font&gt;"
        style="rounded=1;fillColor=#DBEAFE;strokeColor=#2563EB;fontColor=#111827;fontSize=14;fontStyle=1;whiteSpace=wrap;html=1;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="200" height="60" as="geometry"/>
</mxCell>
```

> **关键**：value 含 HTML 标签时，style 必须包含 `html=1;`

### 连线（箭头）

```xml
<mxCell id="edge-order2pay" value="创建支付"
        style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#111827;fontSize=11;endArrow=blockThin;endFill=1;"
        edge="1" source="svc-order" target="svc-pay" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

### 分层容器

```xml
<mxCell id="layer-service" value="服务层"
        style="rounded=1;fillColor=#F3F4F6;strokeColor=#6B7280;dashed=1;fontSize=12;fontStyle=2;verticalAlign=top;align=left;spacingLeft=10;spacingTop=5;"
        vertex="1" parent="1">
  <mxGeometry x="50" y="200" width="900" height="140" as="geometry"/>
</mxCell>
<!-- 子节点引用容器：parent="layer-service"，坐标相对于容器左上角 -->
```

### 数据库形状

```xml
<mxCell id="db-mysql" value="MySQL"
        style="shape=cylinder3;size=15;fillColor=#F3F4F6;strokeColor=#6B7280;fontSize=12;whiteSpace=wrap;html=1;"
        vertex="1" parent="1">
  <mxGeometry x="200" y="400" width="80" height="60" as="geometry"/>
</mxCell>
```

### HTML 转义规则

| 字符 | 转义 |
|------|------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `&` | `&amp;` |

---

## 布局规范（适配用户偏好）

### 画布

- 比例：**16:9**（viewBox 等效，A4 横向 1169×827）
- 方向：自上而下（top-to-bottom）为主，宽流程图可左→右
- 字体：等价于 PingFang SC / HarmonyOS Sans SC（Draw.io 默认 sans-serif）
- 边距：最小 40px

### 分层架构图

```
- 层间距：150-200px
- 同层节点间距：200-280px
- 配色：外部/接入层 → secondary（绿系），网关/核心 → accent（黄系），业务服务 → primary（蓝系），基础设施 → muted（灰系），数据库 → muted+圆柱
- 节点尺寸：宽 200-350px，高 65-80px
```

### 连线规范

| 关系 | 样式 | 标注要求 |
|------|------|---------|
| 同步调用 | 实线 + 箭头 | 标注协议/传递内容（如 "HTTPS"、"Feign"） |
| 异步消息 | 虚线 + 箭头 | 标注消息类型（如 "MQ"、"Event"） |
| 数据流 | 实线 + 箭头（略粗） | 标注数据类型 |

### 标注规则

- 每个节点：主标签（粗体服务名）+ 副标签（一句话职责）
- 每条箭头：必须标注传递内容
- 右侧可加步骤注解（① ② ③）

---

## 质量控制（五维，轻量模式）

> 🔴 区分轻重：简单图（≤8 节点 + 无对外交付需求）→ 快速检查 3 项。复杂图或对外交付 → 全量五维。

### 轻量模式（默认）

快速检查 3 项：
- [ ] XML 语法合法（标签闭合 + id 唯一）
- [ ] 核心实体不遗漏
- [ ] 配色符合设计语言

### 全量五维（对外交付/复杂图）

#### 1. 结构正确性
- [ ] 知识源中的核心实体全部体现
- [ ] 实体间关系完整准确
- [ ] 图种选择匹配知识源类型

#### 2. 布局合理性
- [ ] 无元素重叠
- [ ] 布局方向一致
- [ ] 间距均匀，留白充分
- [ ] 分层/分组逻辑清晰

#### 3. 信息完整性
- [ ] 所有连线有标注
- [ ] 标签文字未截断
- [ ] 节点命名一致

#### 4. 风格一致性
- [ ] 配色符合设计语言
- [ ] 字体大小层次分明
- [ ] 同类型元素形状尺寸一致

#### 5. 可交付性
- [ ] XML 标签正确闭合，id 唯一
- [ ] source/target 引用存在
- [ ] 特殊字符正确转义
- [ ] html=1 与 HTML value 匹配

---

## 导出

### Draw.io Desktop CLI（推荐）

```bash
# macOS
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -o output.png input.drawio

# Linux
drawio -x -f png -o output.png input.drawio

# 指定缩放
drawio -x -f png --scale 2 -o output@2x.png input.drawio
```

### npx ai-viz export（自动检测平台 + drawio 安装路径）

```bash
npx ai-viz export input.drawio -f png
npx ai-viz export input.drawio -f svg
npx ai-viz export input.drawio -f pdf
```

---

## 迭代协议

- 用户反馈 → Edit 模式：读取现有 XML，定向修改 mxCell
- 保留已有布局，只改涉及部分
- 同一图最多 5 轮迭代
- 需求变更 > 50% 或图种变更 → 建议切回 Create 模式重生成

---

## 反例（禁止）

- ❌ 把 Draw.io 文件当 SVG 输出——格式完全不同
- ❌ 生成 XML 时不加 `html=1`——含 HTML 标签的 value 会显示原始标签
- ❌ 跳过质量自检直接交付——XML 语法错误导致文件打不开
- ❌ 对外交付场景不主动建议导出 PNG——客户可能没有 Draw.io
- ❌ 简单图（≤8 节点）跑全量五维检查——拖慢响应，用轻量模式
- ❌ 用 drawio 替代 fireworks-tech-graph 做快速内部草图——Draw.io 生成成本更高

---

## 与其他技能的关系

| 技能 | 关系 | 说明 |
|------|:---:|------|
| `fireworks-tech-graph` | sibling | 快速 SVG vs 正式 Draw.io，根据场景选择 |
| `architecture-diagram` | sibling | 暗色 HTML SVG vs 白底 Draw.io，不同受众 |
| `baoyu-article-illustrator` | alternative | 文章配图用 illustrator，技术图用 drawio |
| `design-language.yaml` | upstream | 全局设计语言配置，提供配色/字体默认值 |

---

## 吸收来源

> 本技能核心方法论吸收自 `deepjai-way/ai-viz` (MIT)，包括：
> - Draw.io XML Schema 和 mxCell 节点规范
> - 复杂度分级布局策略
> - 五维质量控制清单
> - 设计语言注入机制
>
> 本地化适配：Hermes 原生技能触发体系 + 用户白底黑字蓝红偏好 + 轻量/全量双模式质控。
