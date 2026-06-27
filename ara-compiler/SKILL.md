---
name: ara-compiler
description: 文献结构化编译器——将 PDF 论文/代码仓库/实验日志转化为四层 ARA 可导航格式（logic/src/trace/evidence），消除叙事税和工程税。仅论文研究场景触发。
version: 1.0.0
license: MIT (adapted from AmberLJC/Agent-Native-Research-Artifact)
triggers:
  - 编译论文
  - 结构化这篇论文
  - 把论文转成 ARA
  - ara compile
  - /compiler
metadata:
  hermes:
    tags: [research, compiler, paper-to-ara]
    related_skills: [ara-research-manager, ara-rigor-reviewer, double-evolution]
    scope: research-only
  upstream: https://github.com/AmberLJC/Agent-Native-Research-Artifact
---

# ARA Compiler · 文献结构化编译器

**仅论文研究场景触发。** 常态化业务对话不加载此技能。

## 何时触发

| 触发词 | 场景 |
|--------|------|
| "编译这篇论文" / "结构化这篇论文" | 用户提供 PDF 路径或 arXiv URL |
| "把论文转成 ARA" | 显式要求 ARA 格式输出 |
| "ara compile <path>" | CLI 风格调用 |
| "/compiler <path>" | 显式调用 |

**不触发**：常规文献阅读、写飞书文档总结（除非用户明确要求 ARA 格式）。

---

## 核心目标

将传统论文（PDF）消除两项结构性税收后转化为 ARA 协议：

1. **叙事税** — 论文把树状探索压缩为线性叙事，丢失失败实验、被否假设
2. **工程税** — 论文只为审稿人满意而写，缺配置/环境/技巧等 Agent 复现所需信息

编译器输入：PDF 论文 + 可选 代码仓库/数据集/评测 Rubric
编译器输出：标准四层 ARA 目录

---

## 四阶段编译流水线

### 阶段 1：语义解构

**动作**：
1. 读取 PDF 文本内容（用 `python3 -c "import fitz;..."` 或已有文本文件）
2. 剥离叙事框架，提取**信息密集的核心事实**
3. 以电报体重写关键段落——

**提取清单**（对照论文逐项检查）：

| 提取项 | 来源段落 | 输出目标 |
|--------|---------|---------|
| 研究空白 (Gap) | Introduction 末段 | logic/problem.md |
| 关键洞察 (Insight) | Method 开头 | logic/problem.md |
| 可证伪声明 (Claims) | Abstract + Conclusion | logic/claims.md (暂存) |
| 实验设计 (Experiments) | Experimental Setup | logic/experiments.md |
| 架构描述 | Method/Architecture | logic/solution/architecture.md |
| 算法伪代码 | Method | logic/solution/algorithm.md |
| 超参数 + 搜索空间 | Implementation Details | src/configs/ |
| 环境依赖 | Implementation Details | src/environment.md |
| 基线 + 消融 | Experiments | evidence/tables/ |
| 相关信息 | Related Work | logic/related_work.md |

**提取原则**（重要）：
- 论文中**没有**的信息标注 `[missing — not in source]`，不编造
- 论文中**隐含/implicit**的信息标注 `[inferred — confirm with authors]`
- 论文中**明确**的信息直接写入，标注来源（章节/段落）

### 阶段 2：认知映射

将阶段 1 提取的原始信息，填入 ARA 的结构化格式：

**logic/claims.md** — 每条 Claim 格式：
```
## C{NN}: {一句话标题}
- Statement: {精确陈述}
- Status: proposed | confirmed | refuted
- Falsification: {如何证伪此声明}
- Proof: [E{NN}, E{MM}]  (实验 ID)
- Dependencies: [C{NN}]   (依赖的其他声明)
- Tags: [causal|generalization|improvement|descriptive|scoping]
- Provenance: ai-inferred | human-confirmed
```

**logic/experiments.md** — 每条实验格式：
```
## E{NN}: {实验标题}
- Verifies: [C{NN}]  (验证哪些声明)
- Setup: {实验配置}
- Metrics: {评估指标}
- Baselines: {基线方法}
- Expected: {预期结果}
- Dependencies: [E{NN}]
```

**logic/related_work.md** — 不再是一段段文字综述，而是类型化依赖图：
```
| 论文 | 关系 | 类型 | 注入内容 |
|------|------|------|---------|
| Smith 2023 | import  | 先验定义 | 公式 (3)-(5) 的定义 |
| Chen 2024 | bound   | 约束传播 | 超参搜索空间上界 |
| Li 2025    | baseline| 回归检测 | 自动触发性能对比 |
```

### 阶段 3：物理落地

**如果有代码仓库**：
1. 对照论文中的方法描述与代码实现，交叉核对
2. 挖掘论文中未文档化的隐性知识（未提及的参数、数据预处理 trick）
3. 为 src/configs/ 中每个超参附注**理由**（不是只写值，写为什么是这个值）
4. 生成 src/environment.md（Python 版本、关键库版本、CUDA、随机种子）

**如果仅有论文无代码**：
1. 从论文实现细节提取所有可恢复的配置
2. 为无法确定的值标注 `[unknown — author confirmation needed]`
3. 生成最小可执行存根（不编造完整实现，只写接口签名）

### 阶段 4：探索图重建

**目标**：从论文的线性叙事中反推研究 DAG。

**方法**：
1. 阅读论文的 "Ablation Studies" → 推断哪些是事后验证、
   哪些是开发过程中真正推动决策的实验（前者常在 ablation，后者常被省略）
2. 阅读论文的 "Limitations" → 推断死胡同节点
3. "We tried X but found Y" 类句子 → 标注为 dead_end 节点

**trace/exploration_tree.yaml 节点类型**：
- `decision` — "我们在 A/B/C 中选了 A，因为…"
- `dead_end` — "尝试了 X，失败，学到 Y"
- `pivot` — "因为发现 Z，从 A 方向转向 B 方向"
- `question` — 论文提出的开放问题

**关键原则**：论文省略的信息用 `[inferred — low confidence]` 标注，不用 `[missing]`（后者暗示论文本应有但没写）。

---

## 校验：ARA Seal Level 1

编译完成后运行结构校验：
- 所有文件存在且格式正确
- 所有跨层引用可解析（C{NN} → E{NN} → evidence/ 路径）
- PAPER.md 索引完整

---

## 使用示例

```
用户："编译这篇论文 /home/aorus/papers/attention.pdf"

Hermes 加载 ara-compiler：
→ 阶段 1：提取 3 个 Gap、5 个 Claims、2 个 Experiments、12 个超参
→ 阶段 2：填充 logic/ claims.md + experiments.md + related_work.md
→ 阶段 3：生成 src/configs/ + src/environment.md
→ 阶段 4：推断 1 个 decision、2 个 dead_end
→ ARA Seal Level 1 校验：引用全解析 ✓

输出：ara/attention/ 已生成，共 12 个文件
      PAPER.md 索引已更新
      2 个 claimed 值标注为 [inferred — confirm with authors]
```

---

## 工具适配

| 操作 | Hermes 工具 |
|------|------------|
| 读取 PDF 文本 | terminal: `python3 -c "import fitz;..."` 或 `pdftotext` |
| 搜索论文中的关键词 | search_files(target='content') |
| 创建目录文件 | write_file |
| 读取代码仓库 | read_file + search_files |
| 结构校验 | search_files(target='files') 检查所有必需文件存在 |

---

## 技术说明

- 上游：Orchestra-Research/Agent-Native-Research-Artifact (MIT)
- 本技能为上游 compiler 的 Hermes 适配版
- 仅在论文研究场景触发，不涉及任何网络请求
- 编译质量取决于源 PDF 信息完整度，显式标注不确定性
