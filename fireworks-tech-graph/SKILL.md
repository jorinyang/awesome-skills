---
name: fireworks-tech-graph
description: >-
  NL→SVG+PNG 技术图表生成。自然语言描述需求，直接输出生产级技术图表。
  触发词："画图" "架构图" "流程图" "序列图" "类图" "ER图" "状态机"
  "可视化" "出图" "generate diagram" "draw" "visualize"。
  7种风格×14种图表类型×40+产品图标库。
---

# Fireworks Tech Graph (Hermes 适配版)

将自然语言描述转化为精美 SVG 技术图，通过 cairosvg 导出高分辨率 PNG。

原始仓库：https://github.com/yizhiyanhua-ai/fireworks-tech-graph
Stars: ~5,100 | License: MIT | 风格: 7+1 | 图表类型: 14

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

### 验证清单（最终确定前）

1. **箭头-组件碰撞**: 箭头不得穿过组件内部
2. **文字溢出**: 所有文字需适配 8px 内边距
3. **箭头-文字对齐**: 箭头端点需连接形状边缘；箭头标签不重叠箭头线
4. **容器规范**: 箭头优先通过组件间空隙进出容器
5. **滤镜边界安全**: 滤镜元素距离 viewBox 边缘 ≥ max(元素尺寸20%, 阴影模糊半径×3)
6. **箭头-标题碰撞**: 箭头不得穿过区域/容器标题文字

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

## 常见图表模式速查

**RAG Pipeline**: Query → Embed → VectorSearch → Retrieve → Augment → LLM → Response
**Agentic RAG**: 在 Query 和 LLM 之间添加 Agent loop + Tool use
**Agentic Search**: Query → Planner → [Search/Caculator/Code] → Synthesizer → Response
**Mem0 / Memory Layer**: Input → Memory Manager → [Write: VectorDB+GraphDB] / [Read: Retrieve+Rank] → Context
**Multi-Agent**: Orchestrator → [SubAgent A/B/C] → Aggregator → Output
**Tool Call Flow**: LLM → Tool Selector → Tool Execution → Result Parser → LLM (loop)
