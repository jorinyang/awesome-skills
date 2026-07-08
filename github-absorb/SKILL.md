---
name: github-absorb
description: >-
  GitHub 代码仓库全流程评估与吸收引擎。当用户给出 GitHub 仓库链接时自动触发：
  深度分析→业务价值评估→吸收策略分类→独立创建/吸收执行→网格化引用→
  单元测试+全业务链路测试→能力强化报告。触发信号：github.com 链接、
  "这个仓库怎么样"、"帮我看看这个项目"、"能不能用"、"吸收这个仓库"。
version: 1.7.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [github, absorption, evaluation, repository, meta-skill, code-review, business-value]
    related_skills:
      - external-skill-evaluation
      - codebase-inspection
      - double-evolution
      - cross-project-adaptation
      - skill-evaluator
      - darwin-skill
      - github-release-readme
      - agent-tool-system
      - wsl-browser-cdp
triggers:
  - "https://github.com/"
  - "这个仓库怎么样"
  - "帮我看看这个项目"
  - "能不能用"
  - "吸收这个仓库"
  - "评估一下这个代码仓库"
  - "这个项目对我们有帮助吗"
  - "analyze this repo"
  - "evaluate repository"
---

# GitHub 代码仓库全流程评估与吸收引擎

> **定位**：不是"看看这个仓库"的信息检索——是从**业务价值判断→吸收执行→测试验证→网格化引用→能力报告**的完整闭环。覆盖 AI、数字化、咨询、企业管理、FDE 五大业务域。

## 设计哲学

1. **价值先行，不行即止** — 业务价值为负或无关 → 立即停止，不浪费后续步骤
2. **最小化可用** — 优先独立创建技能；只在强互补+高契合时才吸收到现有技能
3. **工具优先安装** — 仓库本身是完整可安装工具（CLI/桌面应用/MCP Server）时，优先独立安装使用，而非强行吸收为技能
4. **技能纯粹性** — 不把不同职责塞进同一个技能；代码仓库能力与现有技能边界清晰
4. **自动触发** — GitHub 链接出现即启动，不需用户重复说"评估一下"
5. **闭环交付** — 从评估到测试到报告，产出完整可追溯的强化记录

## 触发条件

### 自动触发（默认）

当消息中出现以下任一信号时自动启动 Phase 1：
- 包含 `github.com` 且看起来像仓库链接（`/owner/repo` 模式）
- 用户说"帮我看看这个仓库/项目"
- 用户说"这个项目怎么样/能不能用/值不值得"
- 用户说"吸收/引入/用这个仓库"

### 不触发场景

- Gist 链接（`gist.github.com`）
- GitHub 非仓库页面（Issues/PRs/Discussions/profile）
- 用户只是提了一嘴 GitHub 作为上下文但没要求评估
- 纯代码片段引用（如"参考 github.com/xxx/blob/main/src/yyy.py 的写法"）

## 全局工作流（八阶段）

```
Phase 1 → Phase 2 → Phase 3 (Gate) → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8
 触发      深度      价值判断       吸收策略    执行吸收   网格引用   测试验证   强化报告
 检测      分析      (停/续)        分类       创建技能   更新关联   双轨测试   最终交付
```

---

## Phase 1: 触发检测与仓库定位

### Step 1.1: 解析 GitHub URL

从用户消息中提取：
```
https://github.com/{owner}/{repo}
```

若用户给了非标准格式（如 `owner/repo`），补全为 `https://github.com/{owner}/{repo}`。

### Step 1.2: 确认评估意图

若 URL 出现但意图不明确（如"你看过 github.com/xxx 吗"），追问确认：
```
你是想让我评估这个仓库对当前业务的价值吗？还是只是想了解这个项目是做什么的？
```

### Step 1.3: 获取仓库元信息

```bash
# 仓库基本信息
curl -s https://api.github.com/repos/{owner}/{repo} | python3 -c "
import sys,json
r=json.load(sys.stdin)
print(f'Stars: {r.get(\"stargazers_count\",\"?\")}')
print(f'Forks: {r.get(\"forks_count\",\"?\")}')
print(f'Language: {r.get(\"language\",\"?\")}')
print(f'Topics: {\", \".join(r.get(\"topics\",[]))}')
print(f'Description: {r.get(\"description\",\"?\")}')
print(f'License: {r.get(\"license\",{}).get(\"spdx_id\",\"?\") if r.get(\"license\") else \"?\"}')
print(f'Last push: {r.get(\"pushed_at\",\"?\")}')
print(f'Archived: {r.get(\"archived\",False)}')
"
```

---

## Phase 2: 深度分析

### Step 2.1: 读取文档层

按优先级读取：

1. **README.md** — 项目定位、核心功能、快速开始
2. **CHANGELOG.md / RELEASE_NOTES** — 版本演进、稳定性判断
3. **CONTRIBUTING.md / ARCHITECTURE.md** — 架构设计、贡献指南
4. **docs/ 目录** — 详细文档
5. **examples/ 目录** — 使用示例

优先使用 `web_extract(urls=["https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"])` 或 `curl` 分块读取。

> ⚠️ **文档读取超时是常态**：`web_extract` 对大仓库 README 经常 60s 超时（如 AnythingLLM、LangChain 等 60K+ stars 项目），官方 docs 站点也常因 JS 渲染而超时。超时后**不要反复重试**同一工具——直接 `git clone --depth 1` 读本地文件（`read_file /tmp/{repo}/README.md`）。这个 fallback 对 README / CHANGELOG / docs / openapi.json 等所有文档读取都适用。

### Step 2.1b: 读取配套文章/博客（如有）

当用户同时提供了仓库的配套文章链接（微信公众号 `mp.weixin.qq.com`、Medium、博客等），这些文章通常包含作者的完整设计思路和哲学背景，是评估仓库价值的**高信号信息源**。

**微信文章访问**：`browser_navigate` 直接访问微信文章通常超时或返回空白。必须使用 CDP 浏览器：

1. 确保 Windows Chrome CDP 已连接（加载 `wsl-browser-cdp` 按流程启动）
2. `browser_navigate(url="微信文章URL")` 打开页面
3. 页面加载后，用 `browser_console` 提取正文：

```js
// 微信文章正文在 #js_content 容器中
document.querySelector('#js_content') ? 
  document.querySelector('#js_content').innerText : 
  document.body.innerText
```

> `browser_snapshot` 会截断长文（~2000行），优先用 `browser_console` 直接提取全文。

提取后，将文章内容作为 Phase 2 分析的一部分，重点关注：
- 作者的设计哲学和核心洞察
- 与 README 互补的实现细节
- 无法从代码中直接读出的决策背景

### Step 2.2: 分析目录结构 → API 限流检测

```bash
curl -s https://api.github.com/repos/{owner}/{repo}/contents/ | python3 -c "
import sys,json
for i in json.load(sys.stdin):
    print(f'{i[\"type\"]:5s} {i[\"name\"]}')
"
```

**⚠️ API Rate Limit 降级**：如果 GitHub API 或 `raw.githubusercontent.com` 返回 429/403，**不要反复重试**。立即 fallback 到浅克隆：

```bash
cd /tmp && rm -rf {repo} && git clone --depth 1 https://github.com/{owner}/{repo}.git 2>&1
```

克隆后所有文件读取改用 `read_file` 直接读本地文件（`/tmp/{repo}/...`）。这比等待 rate limit 恢复更快、更可靠。

### Step 2.2b: 技能市场仓库检测

当目录结构分析发现 `skills/` 目录包含多个以技能命名的子目录（如 `brainstorming/`、`test-driven-development/`），且每个子目录包含 `SKILL.md` 文件时，该仓库是 **Agent 技能市场/方法论仓库**。此时切换评估模式：

**检测命令**（克隆后在本地执行）：
```bash
ls /tmp/{repo}/skills/ | head -20  # 子目录列表
grep -l '^name:' /tmp/{repo}/skills/*/SKILL.md  # 验证技能文件
```

**切换后：**
1. **跳过** Step 2.3（pygount 代码分析）——仓库主体是 Markdown，非代码
2. **跳过** Step 2.4（代码文档质量评估）——技能仓库的文档标准不同
3. **替代分析**：逐技能读取 SKILL.md，按 `name:` / `description:` frontmatter 提取核心能力清单
4. **检查插件架构**：阅读 `.claude-plugin/`、`.codex-plugin/`、`hooks/` 等目录了解跨平台分发机制
5. **优先读取元技能**：读取 `skills/using-{repo-name}/SKILL.md`（如 `using-superpowers/SKILL.md`）——这是技能体系的引导入口，揭示了其设计哲学和技能间编排逻辑

> **案例**：`obra/superpowers` 即典型的技能市场仓库（14 个技能 + 多平台插件架构）。评估重点从"代码质量"转向"方法论完整度"和"技能间协同编排"。

### Step 2.2b: 技能仓库检测

当目录结构分析发现 `skills/` 目录包含多个以技能命名的子目录（如 `brainstorming/`、`test-driven-development/`），且每个子目录包含 `SKILL.md` 文件时，该仓库是 **Agent 技能市场/方法论仓库**，而非传统代码仓库。此时需要切换评估模式：

**检测信号：**
```bash
# 列出 skills/ 下的技能目录
curl -s https://api.github.com/repos/{owner}/{repo}/contents/skills | python3 -c "
import sys,json
items=json.load(sys.stdin)
skills=[i['name'] for i in items if i['type']=='dir']
print(f'Skills count: {len(skills)}')
for s in skills: print(f'  - {s}')
"
```

**切换到技能仓库评估模式后：**
1. **跳过** Step 2.3（pygount 代码分析）——无意义（仓库主体是 Markdown）
2. **跳过** Step 2.4（代码文档质量）——技能仓库的文档标准不同
3. **替代分析**：逐技能读取 SKILL.md，按 `name:` / `description:` frontmatter 提取核心能力清单
4. **检查插件架构**：阅读 `.claude-plugin/`、`.codex-plugin/`、`hooks/` 等目录，了解跨平台分发机制
5. **读取元技能**：优先读取 `using-{repo-name}/SKILL.md`（如 `using-superpowers/SKILL.md`）——这是技能体系的引导入口

> **案例**：`obra/superpowers` 即典型的技能市场仓库（14 个技能 + 插件架构）。评估重点从"代码质量"转向"方法论完整度"和"技能间协同关系"。

### Step 2.3: 代码规模与语言分析

使用 `codebase-inspection` 技能的方法：

```bash
# 浅克隆（加速）
git clone --depth 1 https://github.com/{owner}/{repo}.git /tmp/{repo} 2>&1

# 语言/规模分析
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,dist,build" \
  /tmp/{repo} 2>/dev/null
```

若仓库过大（>100MB 或 clone 超时 60s），跳过全量代码分析，仅基于文档层判断。

### Step 2.4: 代码文档质量评估

检查以下信号：
- 是否有 docstring/注释（搜索 `def ` + 下一行是否含 `"""`）
- 是否有类型标注（Python `.py` 文件搜索 `: str` / `->` 等模式）
- 是否有测试文件（`test_*.py` / `*_test.go` / `*.spec.ts` 等）
- 是否有 CI/CD 配置（`.github/workflows/` / `.gitlab-ci.yml` 等）

### Step 2.5: 业务域映射

**核心判断**：这个仓库解决什么问题？与当前五大业务域的关系？

| 业务域 | 映射信号 | 示例 |
|--------|---------|------|
| **AI** | LLM/Agent/RAG/MLOps/Prompt/NLP/CV | LangChain、vLLM、Agent框架 |
| **数字化** | ERP/CRM/WMS/低代码/流程自动化/数据中台 | 企业管理系统、工作流引擎 |
| **咨询** | 方法论框架/战略工具/分析模型/MECE | SWOT分析、BCG矩阵、OKR工具 |
| **企业管理** | 组织架构/绩效/财务/HR/协同 | 人事系统、预算管理、项目看板 |
| **FDE** | 前端/后端/数据/DevOps基础设施 | 微服务框架、数据库工具、CI/CD |

每个域打分（0-5）：
- **0**：完全无关
- **1-2**：有弱关联，但不能直接用于业务
- **3**：中等关联，可借鉴思想或部分组件
- **4**：强关联，可直接用于核心业务场景
- **5**：极强关联，填补关键能力空白

---

## Phase 3: 价值判断门禁（Gate）

### 决策逻辑

```
if max(业务域评分) < 2:
    → 🛑 停止。输出"业务相关性不足"简要报告，不进入后续阶段。

if max(业务域评分) >= 3:
    → ✅ 继续。进入 Phase 4 吸收策略。

# 特殊：工具本身可作为独立软件安装使用（非吸收到技能库）
if 仓库是完整可安装工具（CLI/桌面应用/MCP Server/库）且 max(业务域评分) >= 2:
    → ✅ 继续。标记 📦 独立安装，不因低技能吸收价值而跳过。
```

### 门禁判断需考虑的负面信号

| 信号 | 含义 | 处理 |
|------|------|------|
| 仓库已归档（Archived） | 不再维护 | 标注但不自动否决——老旧方法论仍可能有价值 |
| 最后更新 > 2年 | 可能过时 | 减 1 分，提示技术债风险 |
| 无 License 或非宽松许可证 | 法律风险 | 标注，用户决策 |
| 纯 Demo/Toy 项目 | 无生产价值 | 直接否决（除非方法论创新极强） |
| README 质量极低 | 项目不成熟 | 减 0.5-1 分 |

### Phase 3 后高频追问（正面评估的延续）

当 Phase 3 门禁通过且用户给出正面信号后，用户常会追问以下三类问题而不等 Phase 4 吸收流程。这些追问**不需重跑整个评估管线**，直接基于已收集的信息回答：

| 追问类型 | 典型问法 | 处理方式 |
|---------|---------|---------|
| **部署可行性** | "能部署到我当前设备吗？""怎么装？" | 检查 Docker/Node 环境 → 给出具体命令；同时查 Release 页面有无桌面版安装包 |
| **集成协作** | "能和 Hermes/n8n/ComfyUI 协作吗？" | 查 API 端点（openapi.json）、MCP 端点、webhook 支持 → 绘制集成拓扑图 |
| **算力需求** | "需要云端 GPU 吗？""能离线跑吗？" | 查 LLM 提供商列表 + 默认内置模型 → 判断是否支持纯本地/气隙部署 |

回答风格：**直接给结论 + 具体命令 + 集成拓扑**，不套用 Phased 工作流模板。这些是实操问题，不是方法论评估。

---

## Phase 4: 吸收策略分类

基于 Phase 2 的深度分析，对仓库进行**能力拆解**和**分类标注**。

### Step 4.0: 现有技能重叠检查 🔴 CHECKPOINT

在拆解能力单元之前，**必须先检查**源仓库的技能与 Hermes 现有技能的命名重叠和功能重叠：

```bash
# 扫描源仓库技能名列表
for d in /tmp/{repo}/skills/*/; do
  name=$(grep '^name:' "$d/SKILL.md" 2>/dev/null | head -1 | sed 's/name: *//')
  [ -n "$name" ] && echo "$name"
done | sort > /tmp/source-skills.txt

# 与 Hermes 现有技能逐个比对
while read skill; do
  found=$(find ~/.hermes/skills -maxdepth 3 -name "SKILL.md" -exec grep -l "name: $skill" {} \; 2>/dev/null)
  if [ -n "$found" ]; then
    echo "✅ OVERLAP: $skill → $(echo "$found" | head -1)"
  else
    echo "❌ NEW: $skill (not in Hermes)"
  fi
done < /tmp/source-skills.txt
```

**重叠分类：**
| 重叠类型 | 含义 | 处理 |
|---------|------|------|
| ✅ 同名技能 | Hermes 已有同名实现 | 在能力拆解中标注 🔵，吸收策略为"增强现有" |
| ✅ 功能等价 | 名称不同但功能覆盖 | 标注 🟡 参考借鉴，不重复创建 |
| ❌ 完全缺失 | Hermes 无此能力 | 标注 🟢，考虑独立创建 |

**注意**：同名不代表质量相同。Phase 2 已读取双方 SKILL.md，此时应对比：
- 行数/字节量 → 初步判断内容丰富度
- references/ 配套文件数 → 判断支撑材料密度
- 是否有 Iron Law / HARD-GATE 模式 → 判断方法论成熟度

若源仓库的技能显著更丰富（配套文件 3+ 个 / SKILL.md 行数高出 50%+），即使同名也标注 🔵 吸收增强。

### Step 4.0: 现有技能重叠检查 🔴 CHECKPOINT

在拆解能力单元之前，**必须先检查**源仓库的技能与 Hermes 现有技能的命名重叠和功能重叠。这在技能市场仓库评估中尤其重要——你可能已经有同名技能了：

```bash
# 扫描源仓库技能名清单（克隆后在本地执行）
for d in /tmp/{repo}/skills/*/; do
  name=$(grep '^name:' "$d/SKILL.md" 2>/dev/null | head -1 | sed 's/name: *//')
  [ -n "$name" ] && echo "$name"
done | sort > /tmp/source-skills.txt

# 与 Hermes 现有技能逐个比对
while read skill; do
  found=$(find ~/.hermes/skills -maxdepth 3 -name "SKILL.md" -exec grep -l "name: $skill" {} \; 2>/dev/null)
  if [ -n "$found" ]; then
    echo "✅ OVERLAP: $skill → $(echo "$found" | head -1)"
  else
    echo "❌ NEW: $skill (not in Hermes)"
  fi
done < /tmp/source-skills.txt
```

**重叠分类与处理：**

| 重叠类型 | 含义 | 处理 |
|---------|------|------|
| ✅ 同名技能 | Hermes 已有同名实现 | 标注 🔵，吸收策略为"增强现有" |
| ✅ 功能等价 | 名称不同但功能覆盖 | 标注 🟡 参考借鉴，不重复创建 |
| ❌ 完全缺失 | Hermes 无此能力 | 标注 🟢，考虑独立创建 |

**注意**：同名不代表同质。Phase 2 已读取双方 SKILL.md，此时应做**质量对比**：
- 行数/字节量对比 → 初步判断内容丰富度
- `references/` 配套文件数对比 → 判断支撑材料密度  
- 是否有 Iron Law / HARD-GATE / Red Flags 模式 → 判断方法论成熟度
- 是否有跨技能引用和编排逻辑 → 判断体系完整度

若源仓库的技能**显著更丰富**（配套文件 3+ 个，或 SKILL.md 行数高出 50%+），即使同名也标注 🔵 吸收增强，而非 🟡 跳过。

> **案例**：超级力量仓库的 `subagent-driven-development` 在 Hermes 中已有同名技能（379 行 vs 418 行 + 2 个 reviewer prompt），差距不足以触发替换，但配套 prompts 值得迁移——标注 🔵 增强。

### 能力拆解

不是整个仓库作为一个整体吸收。先拆成独立的能力单元：

```
仓库 {owner}/{repo}
├── 能力单元 1: [核心算法/方法]
├── 能力单元 2: [工具/CLI]
├── 能力单元 3: [框架/库]
├── 能力单元 4: [设计模式/架构]
└── 能力单元 N: [文档/知识]
```

### 五类分类法

逐能力单元标注吸收类别：

| 分类 | 图标 | 含义 | 操作 |
|------|:---:|------|------|
| **独立安装** | 📦 | 可独立安装使用的完整工具（CLI/桌面应用/MCP Server/库） | 安装到本地环境并验证可用性 |
| **独立创建** | 🟢 | 独特能力，现有技能库缺失 | 创建独立 Hermes 技能 |
| **吸收增强** | 🔵 | 与现有技能强互补且契合 | 注入到现有技能的特定阶段/字段 |
| **参考借鉴** | 🟡 | 有启发性但暂不吸收 | 记录为参考，不创建技能 |
| **冲突/重复** | 🔴 | 直接冲突或完全被覆盖 | 记录冲突原因，不操作 |
| **无关** | ⚪ | 与业务场景无关 | 跳过 |

### 吸收优先级

| 优先级 | 条件 | 行动 |
|:---:|------|------|
| **P0** | 🟢 独立创建 + 业务评分 ≥ 4 | 立即执行 |
| **P0** | 📦 独立安装 + 业务评分 ≥ 3 | 立即执行：安装到本地 + 验证可用性 |
| **P1** | 🔵 吸收增强 + 业务评分 ≥ 3 | 立即执行 |
| **P2** | 🟢 独立创建 + 业务评分 3 | 可选执行 |
| **P3** | 🟡 参考借鉴 | 仅记录 |

### 用户决策点 🔴 CHECKPOINT

展示吸收策略矩阵，**等待用户确认**后才进入 Phase 5：

```
┌──────────────────────────────────────────────────────────┐
│              吸收策略决策矩阵                               │
├────────────────┬──────┬──────┬──────────┬─────────────────┤
│ 能力单元        │ 分类  │ 优先级 │ 吸收方式   │ 目标技能         │
├────────────────┼──────┼──────┼──────────┼─────────────────┤
│ 工具CLI        │ 📦   │ P0   │ 独立安装   │ brew/npm install  │
│ 核心算法        │ 🟢   │ P0   │ 独立创建   │ [新技能名]       │
│ 工具CLI        │ 🔵   │ P1   │ 吸收增强   │ [现有技能名]     │
│ 设计模式        │ 🟡   │ P3   │ 仅记录    │ —               │
└────────────────┴──────┴──────┴──────────┴─────────────────┘

是否按以上策略执行吸收？（可选择调整分类/优先级）
```

---

## Phase 5: 执行吸收

### 5A: 独立创建技能

根据以下标准创建 Hermes 技能：

#### 技能结构要求

```
~/.hermes-feishu/skills/{category}/{skill-name}/
├── SKILL.md              # 核心：触发条件 + 执行流程 + 反例
├── references/           # 参考文件（方法论、模板、案例）
├── scripts/              # 可执行脚本
└── templates/            # 输出模板
```

#### SKILL.md 写作标准

- **name**: 英文小写+连字符，≤64字符
- **description**: 必须包含"做什么 + 何时用 + 触发词"，≤1024字符
- **triggers**: 至少 3 个中文触发词
- **执行流程**: 编号步骤，每步有明确输入/输出
- **失败模式**: 显式编码 if-失败-→ fallback
- **检查点**: 关键决策前用 🔴 CHECKPOINT
- **反例**: "不要做什么"的独立章节

#### 触发机制设计

确保技能可通过以下方式触发：
1. **关键词自动触发** — 在 description 中声明 ≥ 3 个中文触发词
2. **上下文语义触发** — 触发词覆盖核心场景的不同表述
3. **关联触发** — 若该技能与现有技能强相关，在 existing skill 的 related_skills 中添加

创建完成后立即用 `darwin-skill` 的 L1 静态检查验证：
```bash
# 基本结构检查
grep -c "^## " SKILL.md  # 至少 3 个二级标题
grep -c "🔴 CHECKPOINT" SKILL.md  # 至少 1 个检查点
grep -c "❌" SKILL.md  # 至少 1 个反例
```

### 吸收策略用户级 vs 项目级设计模式

当吸收的工具/方法论设计为「项目级安装」（如 `npx ai-viz init` 每个项目独立配置），但用户场景是多项目 + 统一偏好时，应遵循以下模式：

**模式**：用户级全局默认 + 项目级可选覆盖

```
Layer 1: 用户级默认（~/.hermes-feishu/）
  · 全局配置文件（如 design-language.yaml）
  · 所有技能共享此默认
  · 零摩擦——不需要任何项目级 setup

Layer 2: 项目级覆盖（可选）
  · 项目根目录放置同名配置文件
  · 技能检测到项目级配置 → 覆盖全局默认
  · 未检测到 → 使用全局默认

Layer 3: 对话级临时覆盖
  · 用户口头指定（如"配色用暗色主题"）
  · 仅本次对话有效，不污染文件
```

**何时应用**：
- 工具要求每个项目手动 init
- 用户的项目太多，手动 init 不现实
- 用户有稳定的全局偏好

**反模式**：为每个项目写适配器——适配器模式（Adapter Pattern）适用于不同接口的标准化，不适用于「同一接口的不同配置」。区别在于：适配器解决**格式差异**，本模式解决**配置差异**。

对 🔵 类能力单元，执行以下操作：

1. **定位注入点** — 确定目标技能的哪个 Phase/步骤可以增强
2. **提取核心方法论** — 从源仓库提取算法、模式、检查项
3. **本地化适配** — 转换为 Hermes 原生措辞和工具调用
4. **注入** — 用 `skill_manage(action='patch')` 精确插入新内容到 SKILL.md
5. **迁移配套文件** — 将源仓库技能目录中的支持文件复制到目标 Hermes 技能的 `references/` 下
6. **更新元数据** — 在目标技能的 frontmatter 中：bump `version`、添加 `source:` 字段标注吸收来源
7. **记录来源** — 在目标技能正文末尾添加 `> 吸收自: {repo_url}` 引用标注

#### 5B.1: SKILL.md 注入

用 `skill_manage(action='patch', file_path='SKILL.md')` 精确插入新内容。原则：
- 只加内容，不改原有核心逻辑
- 新增内容放在对应 Phase 的末尾（不打断现有流程）
- 保持原有技能的结构和命名风格

#### 5B.2: References 文件迁移（模式）

当源仓库技能包含**独立的支持文件**（如 reviewer prompts、anti-patterns 文档、技术参考手册），将其复制到目标 Hermes 技能的 `references/` 目录：

```bash
# 批量迁移 references 文件
SRC=/tmp/{repo}/skills/{source-skill}
DST=~/.hermes/skills/{target-skill}/references
mkdir -p "$DST"

# 复制所有非 SKILL.md 的支持文件
for f in "$SRC"/*.md "$SRC"/references/*.md; do
  [ -f "$f" ] && cp "$f" "$DST/$(basename "$f")"
done
```

**适用场景**：
- `implementer-prompt.md` / `task-reviewer-prompt.md` → 子代理调用的独立 prompt 模板
- `code-reviewer.md` → 代码审查的详细检查清单
- `testing-anti-patterns.md` → TDD 反模式参考手册
- `root-cause-tracing.md` / `defense-in-depth.md` → 调试技术深度文档
- `plan-document-reviewer-prompt.md` → 计划文档审查标准

**迁移后验证**：确认目标 SKILL.md 中已有或新增对 references 文件的引用句（一句即可）：
```markdown
详见 `references/{filename}.md`。
```

**不要迁移**：
- ❌ 脚本文件（`scripts/`）——除非经过 Hermes 环境适配
- ❌ 测试文件——源仓库的测试框架与 Hermes 不兼容
- ❌ 平台特定配置（`plugin.json`, `hooks.json`）——Hermes 有独立触发机制

#### 5B.3: 版本与来源标注

每次 🔵 吸收增强后，更新目标技能的 frontmatter：

```yaml
# Before
name: systematic-debugging
version: 1.0.0
description: "..."

# After (bump MINOR version + add source)
name: systematic-debugging
version: 1.1.0
metadata:
  hermes:
    related_skills: [newly-discovered-deps]
  source: 增强自 https://github.com/{owner}/{repo} (v{X.Y.Z})
```

#### 5B.4: 批量执行策略

当多个 🔵 增强涉及"纯文件复制 + 元数据更新"（无 SKILL.md 内容注入），可使用 `terminal` 批量操作；涉及 SKILL.md 内容改变时必须逐个 `patch`。典型执行顺序：

```bash
# Step 1: 批量复制 references 文件（terminal）
# Step 2: 逐个 patch frontmatter（skill_manage patch）
# Step 3: 如有 SKILL.md 正文注入，逐个 patch
```

> **案例**：在超级力量吸收中，5 个 🔵 增强全部是"references 迁移 + frontmatter 更新"模式（无正文注入），仅 1 个（answer 设计门禁）需要实际内容注入。

---

## Phase 6: 网格化引用网络

每次独立创建 / 吸收增强后，必须更新技能间的引用关系。

> **⚠️ 重要**：不是所有反向引用都值得补。通用工具被调用、格式引用、方法论启发等场景不需要反向引用——盲目补全会制造假耦合。引用过滤标准见 `references/filtering-criteria.md`。

> **审计工具**：`scripts/audit-reference-network.py` 可随时对本地+GitHub 双源执行全库引用网络健康检查。用法见底部「工具集」。

### 6A: 双向引用

```yaml
# 新技能 → 关联技能
metadata:
  hermes:
    related_skills: [skill-a, skill-b, skill-c]

# 关联技能 → 新技能（反向引用）
# 在 skill-a 的 related_skills 中添加新技能名
```

### 6B: 引用指引生成与注入

`related_skills` 元数据只是索引——技能加载时并不会自动知道"什么时候该用"关联技能。必须为每个关联技能生成**引用指引段落**并注入到其 SKILL.md 正文中，实现"技能知道何时加载另一技能"。

#### 引用指引格式

根据引用维度，为每个关联技能生成一段具体的指引：

| 引用类型 | 指引模板 |
|---------|---------|
| **downstream** | `当需要 [具体场景] 时，先加载 \`{target-skill}\` 获取 [输出类型]，再继续本流程的 [阶段/步骤]。` |
| **upstream** | `本技能的 [产出类型] 可由 \`{target-skill}\` 进一步处理：[衔接场景说明]。` |
| **sibling** | `当面对 [复合场景] 时，与 \`{target-skill}\` 协同使用：[协同方式说明]。` |
| **alternative** | `当 [条件差异] 时，可选 \`{target-skill}\` 替代本技能的 [阶段/步骤]，因为 [理由]。` |

#### 指引编写要求

- **必须具体**：不是"与 X 协同使用"，而是"当需要将评测结果转换为业务报告时，与 X 协同使用"
- **必须给出触发条件**：让技能能自行判断"现在我该不该加载 X"
- **必须说明衔接方式**：输入什么、期望得到什么、结果用在哪一步

#### 注入位置

在目标技能的 SKILL.md 中查找以下章节（按优先级）：

1. `## 与其他技能的关系` → 在该章节末尾追加指引
2. `## 关联技能` → 在该章节末尾追加指引
3. 以上都不存在 → 在技能末尾新增 `## 关联技能指引` 章节

#### 注入方式

使用 `skill_manage(action='patch', file_path='SKILL.md')` 精确插入指引行，只追加、不改写。

#### 注入内容示例

假设在 Phase 5A 独立创建了 `skill-evaluator-extended` 技能，它与 `skill-evaluator` 形成 upstream 关系（skill-evaluator 的输出可由新技能进一步处理）。对 `skill-evaluator` 注入：

```markdown
## 关联技能指引

> 以下指引由 `github-absorb` Phase 6 自动生成，来源于 {repo_url}

- **upstream → `skill-evaluator-extended`**：本技能的三维评测结果可由 `skill-evaluator-extended` 进一步扩展为包含「业务适配度」的四维评测。当需要面向业务决策层输出评测报告时，先加载 `skill-evaluator-extended` 追加第四维度。
```

#### 引用指引质量自检

每条指引注入前自问：

- [ ] 是否说明了**什么场景**下需要加载关联技能？（不能泛泛说"需要时使用"）
- [ ] 是否说明了**衔接方式**？（输入什么、期望输出什么）
- [ ] 是否使用了具体的技能名和阶段名？（不能只说"相关技能"）
- [ ] 技能是否**无需上下文就能判断**触发条件？（按 "if 用户说 X / 当前处于 Y 阶段" 来写）

### 6C: 执行清单

对每个新创建或增强的技能，逐项执行并确认：

- [ ] 新技能自身的 `related_skills` 元数据已填写（6A）
- [ ] 对每个关联技能，确定了引用类型（6B 维度）
- [ ] 对每个关联技能，编写了引用指引段落（6B 格式）
- [ ] 已将引用指引注入到每个关联技能的正文中（6B 注入）
- [ ] 对注入后的关联技能执行 L1 结构检查（结构未损坏）
- [ ] GitHub `awesome-skills` README 索引标记 TODO

### 5C: 独立安装与验证

对 📦 类能力单元，执行以下操作：

**0. 安装类型识别**（先判断再行动）：
- **CLI / 库 / Docker 镜像** → 走步骤 1-5，全自动完成。
- **Desktop GUI 安装器**（`.exe` / `.dmg` / `.AppImage`）→ 下载到用户路径后**停止自动化**。告知用户手动完成 GUI 安装向导，原因：
  - SYSTEM 会话无法在用户桌面会话中创建可见窗口（Session 0 隔离）
  - UAC / 管理员密码弹窗运行在隔离的安全桌面，任何自动化工具（含 cua-driver）均无法交互
  - 安装器本身的 GUI 向导（"下一步"/"我同意"/"选择路径"）需要人类点击
  - 用户安装完成后回到自动化流程做后续配置（环境变量、LLM 接入、工作区创建等）

1. **确定安装方式** — 从 README/文档提取安装命令（brew/npm/pip/cargo/docker/二进制下载）
2. **执行安装** — 在本地环境执行安装（仅 CLI/Docker 类型）
3. **验证可用性** — 至少执行 3 项验证（仅 CLI/Docker 类型）：
 - 版本号检查（`--version` 或等效）
 - 基础命令验证（CLI `--help` 或 API 健康检查）
 - 端到端功能验证（使用实际数据执行一个完整操作）
4. **记录环境约束** — 运行时依赖（Node/Bun/Python 版本）、平台限制、已知问题
5. **创建速查卡** — 记录到最终报告的工具信息表中

> **常见问题**：运行时不匹配、端口不一致、MCP Accept 头、国内下载慢需代理直连、Docker Hub 被墙需镜像/代理、GUI 安装器无法自动化——详见 `references/tool-install-pitfalls.md`。

---

## Phase 7: 测试验证

### 7A: 单元测试（能力和功能）

对每个新创建或增强的技能：

#### L1 静态合规（自动）

```bash
# SKILL.md 结构完整性
- [ ] name/description/version 完整
- [ ] trigger 列表 ≥ 3 个
- [ ] 执行流程有编号步骤
- [ ] 至少 1 个 🔴 CHECKPOINT
- [ ] 至少 1 个反例章节
- [ ] references/ 中引用的文件全部存在
- [ ] scripts/ 中 .py/.sh 文件语法正确
```

#### L2 功能测试（手动/AI驱动）

```bash
# 对每个 trigger 信号，测试技能是否能正确触发
测试集:
  1. 典型触发场景（happy path）
  2. 边界场景（模糊/不全的触发信号）
  3. 负样本（不应触发的场景）
```

#### L3 吸收完整性检查

```bash
- [ ] 源仓库的核心能力是否完整提取
- [ ] 吸收后的技能是否可独立运行（不依赖源仓库）
- [ ] 是否有遗漏的关键方法/算法
- [ ] 文档中是否标注了原始来源
```

### 7B: 全业务链路测试

基于当前系统的**实际功能**与**历史会话/记忆中的主要业务场景**，构建端到端测试链：

#### 链路定义

```
需求 → 转换 → 洞察 → 分析 → 校验 → 输出
```

#### 测试场景生成

从以下来源提取测试场景：

1. **当前任务地图**（从 SOUL.md 和当前会话）
   - 当前身份和业务域
   - 正在进行的项目
   - 记忆中的主要业务场景

2. **历史高频任务**（从 session_search）
   - 搜索最近 1 个月的高频操作类型
   - 提取 3-5 个典型端到端场景

3. **技能依赖链**（从技能 related_skills 图）
   - 找出涉及新技能的最长调用链
   - 测试链上每个节点的输入输出兼容性

#### 测试执行示例

假设新技能为 `{new-skill}`，测试链为：

```
场景: AI Agent 应用探讨
  demand  → 用户提出"帮我设计一个 Agent 架构"
  convert → {new-skill} 从 GitHub 仓库中提取 Agent 设计模式
  insight → {new-skill} 映射到当前业务（数字化/企业管理系统）
  analyze → cross-project-adaptation 分析适配成本
  verify  → skill-evaluator 验证产出质量
  output  → 生成架构方案文档
```

每个环节检查：
- [ ] 输入格式是否兼容下游
- [ ] 输出是否满足上游预期
- [ ] 是否有信息丢失或格式断裂
- [ ] 端到端耗时是否合理

#### 多业务体系适配验证

确保新技能在以下业务体系中均可正常工作：

| 业务体系 | 测试问题 | 检查点 |
|---------|---------|--------|
| **AI 技术** | Agent/LLM/RAG 相关的仓库评估 | 能否识别技术栈并映射到业务 |
| **数字化** | ERP/WMS/低代码 相关仓库 | 能否识别企业管理价值 |
| **咨询** | 方法论框架/分析工具 | 能否提取可复用的思维模型 |
| **企业管理** | 组织/流程/绩效工具 | 能否映射到实际管理场景 |
| **FDE** | 基础设施/DevOps 工具 | 能否评估技术栈适配性 |

---

## Phase 8: 能力强化报告

生成最终的结构化报告，包含以下全部内容：

### 报告模板

完整报告模板见 `references/report-template.md`。使用时替换所有 `{placeholder}` 为实际内容。报告包含七个章节：

1. **仓库概览** — 基本信息表
2. **业务价值评估** — 五大业务域评分
3. **吸收执行摘要** — 能力单元×分类矩阵
4. **创建/增强的技能** — 新技能详情 + 增强注入点
5. **引用网格** — ASCII 图 + 维度明细表
6. **测试结果** — 单元测试 + 全链路测试 + 多业务适配
7. **后续行动** — Checklist

---

## 反例（禁止）

- ❌ 不读完 README 就下结论 — 仓库价值在文档细节中
- ❌ 跳过业务域评分直接分类 — 业务价值是吸收决策的锚
- ❌ 把整个仓库作为一个整体吸收 — 必须拆成能力单元逐项评估
- ❌ 创建技能后不更新引用网格 — 孤立的技能就是死技能
- ❌ 跳过 Phase 7 测试 — 未测试的技能不可信
- ❌ 用户没有确认就执行 Phase 5 吸收 — 吸收决策必须人审
- ❌ 对低价值仓库继续执行后续阶段 — Phase 3 门禁必须严格执行
- ❌ 吸收时破坏原有技能结构 — 注入内容必须放在对应 Phase 末尾
- ❌ 不加判断地补全所有反向引用 — 通用工具被调用/格式引用/方法论启发等不需要反向引用，补了制造噪音和假耦合。过滤标准见 `references/filtering-criteria.md`
- ❌ 用户提出"更高维度评估"时仍用原策略矩阵回答 — 用户问"能不能改成Hermes""吸收后正负面影响""用户级vs项目级最优方案"等问题时，说明原策略矩阵不够，需要重新从范式/架构/能力边界三个维度审视。案例见 `references/ai-viz-absorption-case.md`

---

## 与其他技能的关系

| 技能 | 关系 | 使用方式 |
|------|:---:|---------|
| `external-skill-evaluation` | sibling | github-absorb 走完全流程时，若仓库含 agent skill，可委托给 external-skill-evaluation 做技能层评估 |
| `codebase-inspection` | downstream | Phase 2.3 使用其 pygount 分析和仓库探索方法 |
| `cross-project-adaptation` | downstream | Phase 5B 吸收增强时使用其架构映射方法 |
| `skill-evaluator` | downstream | Phase 7 测试时调用其三维评测框架 |
| `darwin-skill` | downstream | Phase 5A 创建技能后使用其 L1 静态检查 |
| `github-release-readme` | downstream | Phase 8 报告产出后可同步到 GitHub |
| `agent-tool-system` | downstream | Phase 5 独立创建——从源码仓库提取 defineTool→registry→toolsToAI 三层工具架构时使用 |
| `wsl-browser-cdp` | downstream | Phase 2.1b 访问配套微信/博客文章时使用 CDP 浏览器 |

- ❌ 不加判断地补全所有反向引用 — 通用工具被调用/格式引用/方法论启发等不需要反向引用，补了制造噪音和假耦合。过滤标准见 `references/filtering-criteria.md`

---

## 工具集

| 文件 | 用途 | 场景 |
|------|------|------|
| `references/report-template.md` | Phase 8 能力强化报告模板 | 每次吸收完成后生成报告 |
| `references/filtering-criteria.md` | Phase 6B 引用过滤标准 | 判断哪些反向引用值得补、哪些应跳过 |
| `scripts/audit-reference-network.py` | 技能引用网络双源审计脚本 | 扫描本地+GitHub 全库，输出反向缺口/孤立技能/连通聚类 |
| `references/tool-install-pitfalls.md` | Phase 5C 独立安装故障排查模式（Docker 镜像源失效/代理直连/Admin Key 长度/OpenClaw HMAC 端点适配/Docker Desktop 管道权限/GitHub Release 下载加速/Desktop GUI 安装器限制） | 安装 Docker/CLI/MCP/GUI 工具遇到网络、认证或会话隔离问题时查阅 |

运行审计脚本：
```bash
python3 ~/.hermes-feishu/skills/methodology/github-absorb/scripts/audit-reference-network.py \
  /path/to/awesome-skills ~/.hermes-feishu/skills
```

---

## 异常与边界条件

| 场景 | 触发条件 | 处理 |
|------|---------|------|
| 仓库过大 clone 超时 | `git clone --depth 1` > 60s | 跳过代码分析，仅基于文档层评估 |
| 私有仓库 | API 返回 404 | 提示用户提供 access token 或手动描述 |
| 仓库只有 README 无代码 | pygount 结果为空 | 按纯知识/方法论仓库处理，评分默认保守 |
| 多语言混合仓库 | pygount 返回 5+ 种语言 | 只分析主要语言（>20% 占比） |
| 仓库是 Fork | `fork: true` | 标注 Fork 来源，评估与原版的差异 |
| API rate limit | 429 返回或 `raw.githubusercontent.com` 限流 | **不要反复重试 API**。立即 fallback 到 `git clone --depth 1 https://github.com/{owner}/{repo}.git /tmp/{repo}` 浅克隆到本地，之后所有文件读取改用 `read_file` / `cat` 直接读本地文件。clone 超时 120s 内通常可完成（仓库 <100MB）。若 clone 也失败，用 `web_search` 获取信息。 |
| 用户中途改变需求 | 任意阶段 | 记录当前进度后调整方向 |
| 配套微信文章无法直接访问 | `browser_navigate` 超时或返回空白 | 使用 CDP 浏览器 + `browser_console` 提取 `#js_content`（见 Phase 2.1b）。若 CDP 也不可用，仅基于代码分析评估 |
