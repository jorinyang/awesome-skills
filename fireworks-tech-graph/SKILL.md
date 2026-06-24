---
name: fireworks-tech-graph
description: >-
  NL→SVG+PNG 技术图表生成（渲染型）。自然语言描述需求，直接输出生产级 SVG/PNG 图表。
  触发词："SVG技术图" "程序化出图" "生成SVG图" "generate diagram" "visualize" "序列图" "状态机" "类图"。
  7种风格×14种图表类型×40+产品图标库。
  需要可编辑格式（Draw.io XML）→ drawio-generation；暗色主题架构图 → architecture-diagram。
metadata:
  hermes:
    related_skills: [drawio-generation, architecture-diagram]
---

# Fireworks Tech Graph (Hermes 适配版)

将自然语言描述转化为精美 SVG 技术图，通过 cairosvg 导出高分辨率 PNG。

原始仓库：https://github.com/yizhiyanhua-ai/fireworks-tech-graph
Stars: ~5,100 | License: MIT | 风格: 7+1 | 图表类型: 14

> **增强来源**：吸收 `deepjai-way/ai-viz` (MIT) — 五维质量控制 + 设计语言注入 + 轻量路由

## 首次使用：安装依赖

```bash
# 克隆仓库（获取脚本/模板/参考文档）
git clone --depth 1 https://github.com/yizhiyanhua-ai/fireworks-tech-graph.git ~/.hermes-feishu/fireworks-tech-graph

# 安装 PNG 导出依赖（推荐）
pip install cairosvg
```

后续使用时，仓库路径为 `~/.hermes-feishu/fireworks-tech-graph`。

---

## 工作流（严格按此顺序）

0. **加载设计语言** — 从 `~/.hermes-feishu/design-language.yaml` 或项目根目录同名文件加载配色/排版/布局参数（详见下方「设计语言注入」章节）
1. **分类** — 识别图表类型（见下方图表类型）
2. **提取结构** — 从用户描述中识别层次、节点、边、流、语义分组
3. **规划布局** — 应用对应图表类型的布局规则
4. **加载风格参考** — 默认风格 1 (Flat Icon)；加载对应 `references/style-N.md` 获取精确色值和 SVG 模式
5. **映射节点到形状** — 使用形状词汇表
6. **检查图标需求** — 加载 `references/icons.md` 获取已知产品图标
7. **生成 SVG** — 使用 Python 列表方法（见下方 SVG 生成策略）
8. **验证** — `python3 -c "import xml.etree.ElementTree as ET; ET.parse('file.svg')"` 
9. **导出 PNG** — 使用 cairosvg（推荐）
10. **报告** — 输出生成的文件路径

---

## 图表类型 & 布局规则

### 架构图 (Architecture)
节点 = 服务/组件。按**水平层**分组（上→下或左→右）。
- 典型层次：Client → Gateway/LB → Services → Data/Storage
- 用 `<rect>` 虚线容器分组同层相关服务
- 箭头方向跟随数据/请求流
- ViewBox: `0 0 960 600` 标准，`0 0 960 800` 高栈

### 数据流图 (Data Flow)
强调**什么数据移动到哪**，关注数据转换。
- 每条箭头上标注数据类型（如 "embeddings", "query", "context"）
- 主数据路径用粗箭头 (`stroke-width: 2.5`)
- 控制/触发流用虚线箭头
- 按数据类别给箭头上色

### 流程图 (Flowchart)
顺序决策/处理步骤。
- 首选上→下；宽的流用左→右
- 决策用菱形，处理用圆角矩形，I/O用平行四边形
- 节点标签短（≤3字），详细信息放子标签
- 网格对齐：x 间隔 120px，y 间隔 80px

### Agent 架构图 (Agent Architecture)
展示 AI Agent 如何推理、使用工具、管理记忆。
- 核心概念层：Input → Agent Core (LLM, reasoning loop) → Memory (Short/Long/Episodic) → Tools → Output
- 用循环箭头（弧线）表示迭代推理
- 不同记忆类型视觉上分开

### 记忆架构图 (Memory Architecture)
专注记忆操作，Mem0/MemGPT 风格。
- 分开显示记忆**写路径**和**读路径**（不同箭头颜色）
- 记忆层级：Working → Short-term → Long-term → External Store
- 标注记忆操作：`store()`, `retrieve()`, `forget()`, `consolidate()`

### 序列图 (Sequence)
参与者之间按时间排序的消息交换。
- 参与者作为垂直**生命线**（顶部标签 + 垂直虚线）
- 消息作为生命线之间的水平箭头，上→下时间序
- 激活框（生命线上的细填充矩形）显示活动处理
- 用 `<rect>` loop/alt 框架分组，标签在左上角
- ViewBox 高度 = 80 + (消息数 × 50)

### 对比矩阵 (Comparison Matrix)
系统/方案/组件并排对比。
- 列头 = 系统，行头 = 属性
- 行高: 40px；列宽: 最小 120px；表头行高: 50px
- 支持: 着色背景 + `✓`；不支持: `#f9fafb` 填充
- 交替行背景提高可读性
- 最大可读列数：5

### 时间线/甘特图 (Timeline)
水平时间轴显示持续时间、阶段、里程碑。
- X轴 = 时间；Y轴 = 项目/任务/阶段
- 条：圆角矩形，按类别着色，内部或旁边标签
- 里程碑标记：菱形或实心圆，上方标签
- ViewBox: `0 0 960 400` 典型

### 思维导图 (Mind Map)
从中心概念辐射状布局。
- 中心节点在 `cx=480, cy=280`
- 一级分支：围绕中心均匀分布 (360/N 度)
- 二级分支：从一级分支以 30-45° 偏移展开
- 用弯曲 `<path>` 三次贝塞尔曲线，不用直线

### 类图 (Class Diagram - UML)
展示类、属性、方法和关系的静态结构。
- **类框**: 3 格矩形 (名称/属性/方法)，最小宽 160px
- **关系**: 继承(实线+空心三角)、实现(虚线+空心三角)、关联(实线+开放箭头)、聚合(空心菱形)、组合(实心菱形)、依赖(虚线+开放箭头)
- 布局：父类在上，子类在下；接口在实现者左/右

### 用例图 (Use Case Diagram - UML)
从用户视角展示系统功能。
- **Actor**: 火柴人（圆形头+身体线），置于系统边界外
- **Use Case**: 椭圆，中心标签，最小 140×60px
- **系统边界**: 大矩形虚线边框 + 系统名左上角
- 关系：include (虚线 `<<include>>`)、extend (虚线 `<<extend>>`)、泛化 (实线+空心三角)

### 状态机图 (State Machine Diagram - UML)
实体的生命周期状态和转换。
- **状态**: 圆角矩形，最小 120×50px
- 初始状态：实心黑圆 (r=8)；终止状态：双圆
- **转换**: 带标签箭头 `event [guard] / action`
- 复合/嵌套状态：大矩形包含子状态

### ER 图 (Entity-Relationship)
数据库模式和实体关系。
- **实体**: 矩形，实体名粗体头部，属性下方
- 主键属性：下划线；外键：斜体或标 (FK)
- **关系**: 连接线上的菱形，标注基数 `1`, `N`, `0..1`
- 弱实体：双边框矩形

### 网络拓扑 (Network Topology)
物理或逻辑网络基础设施。
- 设备图标：路由器(圆+交叉箭头)、交换机(矩形+箭头网格)、服务器(堆叠矩形)、防火墙(砖纹/盾形)、负载均衡器(分割矩形+箭头)、云(重叠弧线)
- 连接：有线(实线)、无线(虚线+WiFi符号)、VPN(虚线+锁图标)
- 子网/区域：虚线矩形容器 + 区域标签
- 布局：分层上→下 (Internet → Edge → Core → Access → Endpoints)

---

## 形状词汇表

将语义概念映射为一致的形状：

| 概念 | 形状 | 备注 |
|------|------|------|
| User / Human | 圆形+身体路径 | 火柴人 |
| LLM / Model | 圆角矩形+渐变填充 | 用强调色 |
| Agent / Orchestrator | 六边形或双边框圆角矩形 | 表示"主动控制器" |
| Memory (short-term) | 圆角矩形，虚线边框 | 临时的=虚线 |
| Memory (long-term) | 圆柱体（数据库形状） | 持久的=实心圆柱 |
| Vector Store | 带内部网格线的圆柱体 | 加3条水平线 |
| Graph DB | 圆簇（3个重叠圆） | |
| Tool / Function | 齿轮状矩形 | |
| API / Gateway | 六边形（单边框） | |
| Queue / Stream | 水平管道 | |
| File / Document | 折角矩形 | |
| Browser / UI | 带3点标题栏的矩形 | |
| Decision | 菱形 | 仅流程图 |
| Process / Step | 圆角矩形 | 标准框 |
| External Service | 带云图标或虚线边框的矩形 | |
| Data / Artifact | 平行四边形 | 流程图 I/O |

---

## 箭头语义

始终赋予箭头含义，不仅是颜色：

| 流类型 | 颜色 | 描边 | 虚线 | 含义 |
|--------|------|------|------|------|
| 主数据流 | `#2563eb` 蓝 | 2px 实线 | 无 | 主请求/响应路径 |
| 控制/触发 | `#ea580c` 橙 | 1.5px 实线 | 无 | 系统间触发 |
| 记忆读取 | `#059669` 绿 | 1.5px 实线 | 无 | 从存储检索 |
| 记忆写入 | `#059669` 绿 | 1.5px | `5,3` | 写入/存储操作 |
| 异步/事件 | `#6b7280` 灰 | 1.5px | `4,2` | 非阻塞事件驱动 |
| 嵌入/转换 | `#7c3aed` 紫 | 1px 实线 | 无 | 数据转换 |
| 反馈/循环 | `#7c3aed` 紫 | 1.5px 曲线 | 无 | 迭代推理循环 |

使用 2+ 种箭头类型时必须包含**图例**。

---

## 8 种视觉风格

| # | 名称 | 背景 | 最适合 |
|---|------|------|--------|
| 1 | **Flat Icon** (默认) | White `#ffffff` | 博客、文档、演示 |
| 2 | **Dark Terminal** | `#0f0f1a` | GitHub、开发者文章 |
| 3 | **Blueprint** | `#0a1628` | 架构文档 |
| 4 | **Notion Clean** | White, minimal | Notion |
| 5 | **Glassmorphism** | Dark gradient | 产品页、主题演讲 |
| 6 | **Claude Official** | Warm cream `#f8f6f3` | Anthropic 风格 |
| 7 | **OpenAI Official** | Pure white `#ffffff` | OpenAI 风格 |
| 8 | **Dark Luxury** | `#0a0a0a` | 高级编辑排版 |

加载 `~/.hermes-feishu/fireworks-tech-graph/references/style-N.md` 获取精确色值和 SVG 模式。
加载 `~/.hermes-feishu/fireworks-tech-graph/references/style-diagram-matrix.md` 获取风格-图表类型适配建议。

---

## SVG 生成策略

### 强制：Python 列表方法

**始终使用此方法生成 SVG**，防止字符截断和语法错误：

```python
python3 << 'EOF'
lines = []
lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 700">')
lines.append('  <defs>')
# ... 每行独立添加
lines.append('</svg>')

with open('/path/to/output.svg', 'w') as f:
    f.write('\n'.join(lines))
print("SVG generated successfully")
EOF
```

### SVG 技术规则

- ViewBox: `0 0 960 600` 默认；`0 0 960 800` 高；`0 0 1200 600` 宽
- 字体：通过 `<style>font-family: ...</style>` 嵌入，不用外部 `@import`（cairosvg/rsvg 无法获取外部 URL）
- `<defs>`: 箭头标记、渐变、滤镜、裁剪路径
- 文字：最小 12px，标签 13-14px，子标签 11px，标题 16-18px
- 所有箭头：`<marker>` + `markerEnd`, `markerWidth="10" markerHeight="7"`
- 投影：`<feDropShadow>` in `<filter>`，谨慎使用（仅关键节点）
- Z-order（绘制顺序）：① 画布背景 ② 虚线容器/区域背景 ③ 箭头和连接线 ④ 节点形状 ⑤ 文字标签 ⑥ 图例和覆盖层

### 间距规则

- 同层节点：水平 80px，垂直层间 120px
- 画布边距：最小 40px
- 对齐 8px 网格：水平 120px 间隔，垂直 120px 间隔

### 箭头标签（关键）

- **偏移优先**（默认）：标签距水平箭头 6-8px 上方，或垂直箭头 8px 左/右
- **背景兜底**：仅当偏移标签仍穿过其他视觉元素时添加 `<rect fill="canvas_bg" opacity="0.95"/>`
- 置于箭头中间，≤3 词，多箭头汇聚时错开 15-20px

### 箭头路由

- 优先正交（L 形）路径减少交叉
- 箭头锚定在组件边缘，非几何中心
- 绕开密集节点簇，平行箭头用不同 y 偏移
- 不可避免的交叉用跳弧（5px 半径）

### 质量控制（五维体系）

> 🔴 模式开关：简单图（≤8节点，内部使用）→ **轻量模式**（快速3项）。复杂图或对外交付 → **全量五维**。

#### 轻量模式（默认 — 快速检查，生成后自动执行）

- [ ] SVG 语法合法（`xml.etree.ElementTree` 可解析）
- [ ] 核心实体不遗漏（知识源中提到的关键组件全在图里）
- [ ] 配色符合设计语言（加载自 design-language.yaml）

#### 全量五维（对外交付 / 复杂图 / 正式场景 — 用户要求时触发）

##### 1. 结构正确性
- [ ] 知识源中的核心实体全部体现，无遗漏
- [ ] 实体间关系完整准确，无关键连接缺失
- [ ] 图种选择匹配知识源类型（DDL→ER图，不能画成流程图）

##### 2. 布局合理性
- [ ] 无元素重叠
- [ ] 布局方向一致（不混合从上到下和从左到右）
- [ ] 间距均匀，留白充分
- [ ] 分层/分组逻辑清晰

##### 3. 信息完整性
- [ ] 所有连线有标注（说明传递什么：HTTP请求？消息？数据？）
- [ ] 标签文字未截断，完整可读
- [ ] 节点命名一致（同一实体全图使用相同名称）

##### 4. 风格一致性
- [ ] 配色符合设计语言语义槽位映射（primary/secondary/accent/muted/danger）
- [ ] 字体大小层次分明（标题 18px > 正文 14px > 注释 10px）
- [ ] 同类型元素使用相同形状和尺寸

##### 5. 可交付性（格式专项）
- [ ] SVG 可被 xml.etree.ElementTree 正常解析
- [ ] 所有 marker 引用正确（marker-end url 指向已定义的 id）
- [ ] 字体用内嵌 `<style>font-family</style>`（不用 @import，cairosvg 无法获取外部 URL）
- [ ] `<defs>` 中定义的 id 在全文档唯一
- [ ] 特殊字符正确转义（`&` → `&amp;`，`<` 仅在标签内）

### 常见语法错误避免

- ❌ `yt-anchor` → ✅ `y="60" text-anchor="middle"`
- ❌ `fill=#fff` → ✅ `fill="#ffffff"`
- ❌ `marker-end=` → ✅ `marker-end="url(#arrow)"`
- ❌ `L 29450` → ✅ `L 290,220`
- ❌ 缺少 `</svg>` 结尾

---

## SVG → PNG 导出

### 推荐：cairosvg

```bash
# 单文件 (2x 分辨率)
python3 -c "import cairosvg; cairosvg.svg2png(url='input.svg', write_to='output.png', scale=2)"

# 批量转换
python3 -c "
import cairosvg, os, glob
for svg in sorted(glob.glob('*.svg')):
    png = svg.replace('.svg', '.png')
    cairosvg.svg2png(url=svg, write_to=png, scale=2)
"
```

### 备选：rsvg-convert（简单但可能丢失样式）

```bash
rsvg-convert -w 1920 file.svg -o file.png
```

### 注意

- cairosvg 可能无法渲染 CJK 字符和 emoji → 对中文图保留 SVG 为主格式，或换 Puppeteer
- rsvg-convert 对含 `<foreignObject>`、CSS `filter` 或复杂 `<style>` 的 SVG 渲染不完整

---

## 输出

- **默认**: `./[派生名].svg` 和 `./[派生名].png` 在当前目录
- **自定义**: 用户指定路径如 `输出到 /path/`
- **PNG 质量**: 默认 2x 分辨率（适合高清屏和文档嵌入）

---

## 辅助脚本

仓库提供 4 个辅助脚本（位于 `~/.hermes-feishu/fireworks-tech-graph/scripts/`）：

1. `generate-diagram.sh` — 验证 SVG + 导出 PNG
2. `generate-from-template.py` — 从模板创建 SVG
3. `validate-svg.sh` — 验证 SVG 语法
4. `test-all-styles.sh` — 批量测试所有风格

复杂图表推荐使用脚本辅助生成。

---

## 轻量路由（知识源→图种自动推荐）

> 吸收自 ai-viz 的路由引擎思想，做简化版适配。

当用户给出知识源（代码/文档/DDL/API规范）而非直接描述时，自动推断图种：

| 知识源特征 | 推荐图种 | 置信度 |
|-----------|---------|:---:|
| 系统/服务设计文档，层次结构描述 | 架构图 | 高 |
| API 规范、调用链、接口定义 | 时序图 | 高 |
| 业务规则、流程描述（if-else、步骤） | 流程图 | 高 |
| DDL、实体描述、外键关系 | ER 图 | 高 |
| 类/接口/模块定义 | 类图 | 高 |
| 运维配置、K8s YAML、Docker Compose | 部署图 | 中 |
| 对比/并列分析描述 | 对比矩阵 | 中 |
| 状态描述、生命周期 | 状态机 | 中 |
| 演进/历史叙述 | 时间线 | 中 |

**主动触发信号**（对话中检测到以下信号时主动建议画图）：
- ≥3 个交互组件被描述 → 建议架构图
- 时序性描述（先…再…然后…）→ 建议时序图
- 条件分支（如果…否则…）→ 建议流程图
- 分层/层级结构描述 → 建议分层架构图

**置信度分级行动策略**：
- 高置信度 → 直接执行，附判断理由
- 中置信度 → 推荐主选图种 + 列出 1-2 个备选，等用户确认
- 低置信度 → 询问用户意图后再画

---

## 常见图表模式速查

**RAG Pipeline**: Query → Embed → VectorSearch → Retrieve → Augment → LLM → Response
**Agentic RAG**: 在 Query 和 LLM 之间添加 Agent loop + Tool use
**Agentic Search**: Query → Planner → [Search/Caculator/Code] → Synthesizer → Response
**Mem0 / Memory Layer**: Input → Memory Manager → [Write: VectorDB+GraphDB] / [Read: Retrieve+Rank] → Context
**Multi-Agent**: Orchestrator → [SubAgent A/B/C] → Aggregator → Output
**Tool Call Flow**: LLM → Tool Selector → Tool Execution → Result Parser → LLM (loop)

---

## 设计语言注入

生成的 SVG 遵循「三层设计语言」体系：

### 加载优先级

```
1. 项目级：$(pwd)/design-language.yaml      ← 项目特定配置
2. 用户级：~/.hermes-feishu/design-language.yaml ← 全局默认
3. 对话级：用户对话中指定的临时覆盖            ← 仅本次有效
```

未找到项目级配置时，用户级全局默认自动生效（**零摩擦**）。

### 默认配色映射（白底风格）

| 语义槽位 | fill | stroke | 适用场景 |
|---------|------|--------|---------|
| primary | #DBEAFE | #2563EB | 核心业务服务/节点 |
| secondary | #D1FAE5 | #059669 | 外部系统/接入层 |
| accent | #FEF3C7 | #D97706 | 网关/关键节点 |
| muted | #F3F4F6 | #6B7280 | 基础设施/支撑 |
| danger | #FEE2E2 | #DC2626 | 告警/注意（红强调） |

### 默认排版

- `font-family: "PingFang SC", "HarmonyOS Sans SC", "Microsoft YaHei", sans-serif`
- 标题 18px bold / 正文 14px / 副文本 12px / 注释 10px

### 默认布局参数（16:9 白底）

- viewBox: `0 0 1169 827`
- 最小边距: 40px
- 复杂度自适应间距：≤8 节点 → 紧凑，9-15 → 标准，16-20 → 宽松，>20 → 拆分

### 项目级覆盖

在项目根目录放置 `design-language.yaml`，覆盖以上默认值。模板参考 `~/.hermes-feishu/design-language.yaml`。
