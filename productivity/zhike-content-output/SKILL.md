---
name: zhike-content-output
description: Content output rules for 贵州之客 — how to produce result documents that don't mix ideology/methodology with outcomes. Core workflow skill for all document产出 tasks.
trigger: "Produce a document, write content, create output for 贵州之客; draft a product plan, SOP, strategy doc, or any written deliverable"
tags: [贵州之客, content-output, 价值观, 方法论, 产出准则]
category: productivity
---

# 贵州之客内容产出准则

## 核心区分：工具 vs 产物

> ⚠️ **这是贵州之客内容产出的第一核心原则，优先级高于一切写作技巧。**

| 概念 | 定义 | 出现位置 |
|------|------|---------|
| **价值观**：山河五则 | 思想指引/意识形态 | 仅用于内部推理和判断，**不出现**在输出文档中 |
| **方法论**：体验式工作法 | 行为动作的实施路径 | 仅用于内部推理和判断，**不出现**在输出文档中 |
| **输出文档** | 用户需求的结果性内容 | 纯净的结果，不含上述工具的原文或关键词 |

## 推理过程（内部，不输出）

当收到一个内容需求时：

1. **用价值观做 filter** — 这个设计/方案是否符合山河五则？哪几条在起作用？
2. **用方法论做路径** — 这个需求应该用「编剧·制片·主演」还是「破冰·沉浸·余响」来推导？
3. **输出结果** — 文档中只写结果：产品方案、SOP、时间表、定价表、话术文本

**推理过程不需要显式呈现。** 用户看到的是他们要的结果，不是你的推导过程。

## 错误示例

❌ **错误：把方法论文本写进产品文案**

```
产品设计理念：
采用「编剧·制片·主演」的方法论...
序曲→铺垫→高潮→尾声的情绪动线设计...
```

❌ **错误：在结果文档中复述价值观条目**

```
本产品体现了「山不让土，故能成其高」的开放连接精神...
```

✅ **正确：只输出结果性内容**

```
产品结构：Day1 晚风轻徒步（松弛入戏）→ Day2 上午 犀牛洞探险（核心高潮）→ Day2 下午 天坑绳索（突破瞬间）→ Day3 慢民宿+篝火（余响留存）
```

## 什么时候才需要在文档中写价值观/方法论？

**只有一种情况：** 用户明确要求「体现山河五则」或「用方法论包装」——这是特定的内容包装需求，不是默认行为。

默认行为 = 工具内化，结果外显。

## Feishu 输出格式规则

- **简单输出**（≤3点，纯文字）→ 直接发 Feishu 卡片，用纯文本
- **复杂输出**（含表格/多级标题/结构化内容）→ 创建 Feishu 在线文档，输出文档链接
- **禁止**：在卡片消息中用 Markdown 表格 `| |`、标题 `##`、引用 `>` — Feishu 不支持，会渲染为原始标签

> ⚠️ **飞书在线文档 API 约束**：实测支持 block_type 2/3/4/5/12/13/15/22（text、heading1~3、bullet、ordered、quote、divider）。表格/代码块等不支持，需降级处理。详见 `feishu-doc` 技能的 block_type 对照表。

## 相关记忆

核心记忆文件：`~/.hermes-feishu/memories/MEMORY.md`

- 意识形态最高准则（使命/愿景/价值观山河五则/方法论体验式工作法）
- 内容产出最高准则（第一性原理/批判性思维/苏格拉底模型/极简优先/外科手术式修改/目标驱动）
- 这些是**推理工具**，永远不在输出文档中显式出现

## 相关技能
- `feishu-doc`：飞书文档创建与知识库归档的完整工作流

### 贵州之客设计产出链路（2026-05-26 新增）

**链路**：`huashu-design` 生成 HTML 设计稿 → `feishu-html` 部署至 OSS

| 环节 | 工具 | 输出 |
|------|------|------|
| 高保真设计 | `huashu-design` | HTML 原型/动画/幻灯片 |
| 部署访问 | `feishu-html` | OSS 在线链接 |

**典型触发词**：做原型、设计Demo、交互原型、HTML演示、动画Demo、做个HTML页面、app原型、iOS原型、导出MP4

**OSS 配置（实测正确）**：
- Bucket: `clawshell-vault`
- Endpoint: `oss-cn-hongkong.aliyuncs.com`（香港节点，Guangzhou 会 403）
- 绑定域名: `https://gzzhike.cn`
- 访问格式: `https://gzzhike.cn/web-spa/{slug}/index.html`
