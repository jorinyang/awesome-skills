---
name: repo-source-deepread
description: >-
  大型远程源码仓库深读法——不克隆或浅交互下，对数千文件级仓库做"设计模式级"精读。
  用 git trees API 递归定位子系统，raw 拉取+AST 骨架提取（docstring/签名/常量），
  小文件整读、大文件骨架化，批量 execute_code 一次拉多文件防上下文爆炸。
  触发信号：精读源码/深入分析这个仓库的实现/看看XX怎么做的/竞品源码分析/
  这个项目的XX机制怎么实现的/从源码里学设计。
version: 1.0.0
author: 杨瑒 (ClawShell 沉淀)
metadata:
  hermes:
    tags: [github, source-reading, ast, code-comprehension, competitive-analysis, context-budget]
    related_skills: [github-absorb, codebase-inspection, external-skill-evaluation]
---

# 大型远程源码仓库深读法（AST 骨架提取）

> **定位**：介于"读 README 评估"（github-absorb Phase 2 文档层）和"克隆后全量静态分析"（codebase-inspection）之间的**源码设计模式精读**。目标不是数 LOC，而是从源码里提炼可借鉴的架构决策、机制设计、产品调参。
> 典型场景：竞品/同血缘产品的机制拆解（"N.E.K.O 的主动发起机制怎么实现的"）、向成熟仓库学设计、评估"能不能抄这个机制"。

## 核心约束：上下文预算

大仓库单文件可达 100KB~200KB（N.E.K.O `memory/facts.py` 192KB、豆包类项目主文件普遍 50KB+）。**整读进上下文 = 自杀**。本方法用 AST 骨架把每文件压到 30~70 行，20 个文件一轮精读控制在 ~15KB 输出。

## 四阶段工作流

### Phase 1 — 子系统定位（一次 API 调用）

```python
# execute_code 内执行
GET https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1
# 返回全仓文件路径列表 → 正则筛子系统
```

- 关键词正则定位：`re.search(r"cat|mind|proactive|memory", p)` 之类，直捣目标子系统目录
- **测试文件名即设计规格**：`test_proactive_unanswered_repeat.py`（有未应答重复策略）、`test_proactive_voice_backoff_static.py`（语音退避）、`test_proactive_intent_label_leak.py`（内部标签不泄漏给用户）——测试名清单是免费的设计意图文档，先读测试名再读源码
- 顺带点名校验 README 大小写（见坑 #1）

### Phase 2 — 批量骨架提取（核心）

用 `scripts/gh_ast_skeleton.py`，或等价的 execute_code 内联实现：

```bash
# 指定文件批量骨架
python scripts/gh_ast_skeleton.py {owner}/{repo} \
  main_logic/proactive_chat/service.py main_logic/proactive_chat/decisions.py

# 子树前缀+正则自动选文件
python scripts/gh_ast_skeleton.py {owner}/{repo} \
  --prefix main_logic/proactive_chat/ --regex "service|decisions|state"

# <8KB 的关键小文件整读
python scripts/gh_ast_skeleton.py {owner}/{repo} brain/agent_session.py --full
```

**骨架 = 每文件只取四样**：
1. **模块 docstring**（截 ~350 字符）——成熟项目的模块 docstring 常是架构宣言。案例：N.E.K.O `topic/pipeline.py` 开头 "Ordinary chat must never wait for topic screening" 一句话道出话题池后台化铁律；`activity/state_machine.py` "No LLM, no external calls, every decision is keyword/threshold driven" 道出零成本活动感知
2. **类+方法签名+docstring 首行**——机制链路从函数名就能读出来（`_decide_closed_activity_gate` → 有活动闸门；`_enter_proactive_phase2` → 两阶段架构）
3. **顶层函数签名**
4. **顶层常量**（≥3 个常量时打印）——**配置文件的黄金**：半衰期、冷却秒数、触发概率、阈值等产品打磨过的数值全在常量里（N.E.K.O `proactive_settings.py`：拒绝冷却 5h > 接受冷却 2h，尊重拒绝的细节直接可抄）

**纪律**：
- **一次 execute_code 拉 4~6 个文件**，不要一个文件一次工具调用（每轮往返都重发整个会话）
- 分批次推进：入口编排 → 决策/状态 → 感知/配置 → 执行/适配，每批一个主题
- 单文件失败不中断批量（try/except per file）

### Phase 3 — 选择性整读

只对 <8KB 的关键小文件整读全文（适配器入口、会话管理器、契约定义）。>50KB 的文件**永不整读**，需要细节时按需 `--prefix` 再钻一层或用 search_files 在克隆版里 grep。

### Phase 4 — 吸收笔记落盘

产出"源码精读笔记"文档，结构：精读范围与方法 → 按子系统提炼设计模式（带真实常量值/函数名证据）→ 对本项目的吸收清单（按 MVP 阶段排序）→ 明确不抄什么 → 遗留待读清单。**吸收清单必须分"立即吸收/中期吸收/深水区/明确不抄"四档**——防全盘照搬冲动。

## 坑位清单

1. **README 大小写**：`raw.githubusercontent.com/.../main/README.md` 404 时先试 `README.MD`（N.E.K.O 实测）。稳妥做法：先 `GET /repos/{owner}/{repo}/contents/` 列根目录确认实际文件名
2. **50KB+ 文件整读**：一次就能把上下文打穿，且 95% 是实现细节噪音——骨架先行，按需深钻
3. **逐文件逐调用**：20 个文件 = 20 次工具调用 = 上下文被会话历史重复发送撑爆。必须批量
4. **忽略测试目录**：测试文件名是规格说明书，忽略它等于丢掉免费的设计文档
5. **读完不落盘**：源码精读的发现（常量值、机制链路）不写成笔记文档，下次会话全部重来
6. **GitHub API 限流（429/403）**：不要重试，fallback 到 `git clone --depth 1` 后本地跑同样的 AST 提取（脚本改读本地路径即可）
7. **骨架 ≠ 理解全部**：骨架给出机制地图；涉及具体算法正确性（如衰减公式细节）时，承认"只读到签名级"，需要精确实现时回读该函数局部

## 与其他技能的关系

| 技能 | 关系 | 使用方式 |
|------|:---:|---------|
| `github-absorb` | upstream | 先做仓库级价值评估与文档层阅读；需要"机制怎么实现的"级别的答案时进入本技能 |
| `codebase-inspection` | sibling | 本技能回答"怎么设计的"，codebase-inspection 回答"多大/什么语言/什么结构" |
| `external-skill-evaluation` | sibling | 评估技能市场仓库时，知识层用评估框架，机制层用本方法深读 |

## 工具集

| 文件 | 用途 |
|------|------|
| `scripts/gh_ast_skeleton.py` | AST 骨架提取 CLI：支持指定文件列表、`--prefix`+`--regex` 子树选文件、`--full` 整读小文件、自动打印顶层常量 |
| `references/skeleton-signals.md` | 骨架信号判读指南——从签名/docstring/常量/测试名识别常见架构模式的速查 |

> 沉淀自 2026-07-31 N.E.K.O（Project-N-E-K-O/N.E.K.O，5014 文件）精读会话：20 文件 4 批次，产出竞品机制笔记 9.5KB，全程零上下文溢出。
