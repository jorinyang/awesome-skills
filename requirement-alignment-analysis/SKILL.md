---
name: requirement-alignment-analysis
description: 多轮需求对齐差异分析。将PRD及多轮会议对齐结果以需求项为核心逐项对比，标注原有/差异/新增/待确定状态。适用于系统开发中与客户进行多次信息同步后产出差异分析文档。触发：需求对齐差异分析/PRD对比/需求变更分析/需求项追踪/需求对齐结果对比。
---

# 需求对齐差异分析

## 触发条件

用户需要基于PRD和多轮会议对齐结果，产出以需求项为核心的逐项对比分析文档时使用。

## 核心原则

**以需求项为核心，逐项追踪多轮状态变化。** 不使用散落的分类列表，每个需求项作为一行，在统一表格中展示 PRD → 第一次对齐 → 第二次对齐 的完整演变。

## 文档格式

### 表格结构

每个模块一张表，列结构：

```
| 序号 | 需求项 | 状态 | PRD v2.0 | 第一次对齐 (日期) | 第二次对齐 (日期) |
```

### 状态标注（中文+emoji）

- 🟢 **原有/已对齐** — 三轮均一致，或PRD提出后后续对齐确认无变化
- 🟡 **差异/调整** — 与PRD或前次对齐结果不一致，需说明原设计、变更后、变更原因
- 🔵 **新增** — PRD及前次对齐均未涉及，本次新提出
- 🔴 **待确定** — 已提出但尚未最终确定

### 文档结构

```
标题: <系统名> - 第X次需求对齐差异分析
版本/日期/编制人 + 对照基线说明 + 状态标注图例

一、主数据管理     （表格）
二、采购管理       （表格）
三、销售管理       （表格）
四、仓库管理       （表格）
五、[新增模块]    （表格，标注"新增模块"）
...
N、待确定事项汇总  （表格：事项|责任方|期望时间）
N+1、关键决策与共识（列表）
```

### 反例（禁止）

❌ 先列"已对齐"再列"差异"再列"新增" — 无法看出需求项演变轨迹
❌ 不标注状态 — 无法快速识别确认/变化/新增
❌ 英文状态标注 — 中文语境应使用中文标注

## 工作流

1. 并行读取所有源材料（PRD + 所有轮次的录音转写 + 会议纪要）
   ## 工作流

   ### 第一步：读取源材料

   源材料可能是飞书原生文档（docx）或 wiki 上传文件（PDF/txt/md）。按以下优先级尝试：

   1. 首选 `lark-cli docs +fetch --api-version v2 --doc "<URL>" --as user`
   2. ⚠️ 若返回 `3380002: Unsupported document type 'file'` → 节点是上传文件，改走 wiki 下载路径：
      - `lark-cli wiki +node-get --as user --node-token "<URL>" --format json` 获取 `obj_token`
      - `lark-cli drive +download --file-token "<obj_token>" --output "./filename.ext" --as user`
      - ⚠️ `wiki +node-get` 需要 `wiki:node:retrieve` scope，缺失时报 `missing_scope` → 走 split-flow 授权：
        ```bash
        lark-cli auth login --scope "wiki:node:retrieve" --no-wait --json
        # → 用 verification_url 生成 QR code 发给用户
        # → 用户确认后执行 lark-cli auth login --device-code <code>
        ```
      - 下载路径仅接受相对路径，建议 `cd /tmp` 后下载
   3. PDF 文件用 PyPDF2 提取文本：`python3 -c "import PyPDF2; ..."`
   4. 优先读纪要（含结构化结论），转写用于补充细节和确认语境

   ### 第二步：交叉对比

   逐模块梳理需求项，追踪 PRD → 每轮对齐的状态变化。

   ### 第三步：标注状态

   "差异"项必须写清：原设计 → 变更后 → 变更原因。

   ### 第四步：产出飞书文档

   - 先写本地 Markdown 文件
   - 再 `lark-cli docs +create --api-version v2 --doc-format markdown --content @文件路径 --as user`
   - 对于长文档（>10KB），直接全量传入 Markdown（`@file`）即可，飞书 API 支持

   ### 第五步：验证

   `lark-cli docs +fetch --api-version v2 --doc "<新文档URL>" --as user` 检查所有表格和章节完整渲染
