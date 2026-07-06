---
name: agent-native-cli-design
description: Use when designing or evaluating agent-native CLI tools, creating skill harnesses, or deciding which bridge pattern to use for accessing a service/app from Hermes.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [agent-native, cli-design, bridge-patterns, methodology, reference]
    related_skills: [opencli, hermes-agent-skill-authoring, comfyui, obsidian]
---

# Agent-Native CLI 设计原则

> **定位**：为 Hermes Agent 技能开发提供统一的 CLI 设计方法论和桥接范式决策框架。
> **来源**：综合 CLI-Anything Hub（HKUDS, 41.5K⭐）、OpenCLI（jackwener, 23K⭐）、微信工具链（wx-cli 3.1K⭐）三大生态的最佳实践。

## 概述

Agent-Native CLI 是指**为 AI Agent 消费而设计**的命令行工具，而不是为人类交互优化。核心理念：AI Agent 通过 CLI 操作一切软件——GUI 应用、Web SaaS、本地桌面应用、Electron 应用。

一个合格的 Agent-Native CLI 满足四个硬约束：
1. **结构化输出**：`--json` 始终可用，Agent 不做 HTML/text 解析
2. **机器可发现**：提供 registry / agent-card / SKILL.md 供 Agent 自主发现
3. **幂等操作**：一 shot 命令，可重复执行不产生副作用
4. **错误自描述**：失败返回结构化错误对象，Agent 可据此决策重试或降级

## 四种桥接范式

选择正确的桥接模式，取决于目标系统的接口特征和反爬/安全约束。

### 范式一：直接藩篱（Direct Harness）

**来源**：CLI-Anything Hub（Python harness 模式）

**适用**：目标软件已有 CLI 或 REST API，只需做 Agent 友好的封装。

```
Agent → harness CLI → 原生 CLI/API → 软件
```

**设计模板**：
```bash
# 安装
cli-hub install <name>   # 或 pip install / npm install

# 使用
<entry-point> --json <command> [args]
<entry-point> repl        # 多步骤交互
```

**关键约束**：
- 输出统一为 `{"ok": true/false, "data": ..., "error": {"code": ..., "message": ...}}`
- 一 shot 命令 ≤ 30s 超时
- REPL 模式支持会话上下文保持

**Hermes 中已有案例**：ComfyUI skill（本地 API 藩篱）、Obsidian skill（本地应用藩篱）、Feishu 系列技能（REST API 藩篱）

**何时采用**：目标有 CLI/API → 直接封装，不要绕路

---

### 范式二：浏览器桥接（Browser Bridge）

**来源**：OpenCLI（Chrome CDP + Extension + Daemon）

**适用**：目标为反爬严格的 Web SaaS，无公开 API，但可通过浏览器登录访问。

```
Agent → opencli <site> <cmd> → Daemon → Extension → Chrome CDP → 网站
```

**设计模板**：
```bash
# 安装 bridge
opencli doctor                    # 验证连通性

# 使用内置 adapter
opencli <site> <command> --json

# 驱动浏览器 ad-hoc
opencli browser <session> open <url>
opencli browser <session> snapshot
opencli browser <session> click @e5
```

**关键约束**：
- Chrome 必须真实运行，不可 headless（反爬检测）
- 登录态由 Chrome 自身维护，不额外传递 cookie
- Session 有 TTL（默认 5 分钟闲置回收）
- 每个 adapter 声明 auth 模式：`PUBLIC` / `COOKIE` / `INTERCEPT` / `UI` / `LOCAL`

**Hermes 中已有案例**：OpenCLI skill（小红书/知乎/微博/B站/公众号后台）

**何时采用**：Web SaaS ∧ 无 API ∧ 有反爬 → 浏览器桥接

---

### 范式三：内存扫描（Memory Scan）

**来源**：wx-cli（Rust daemon + memory scan + encrypted DB）

**适用**：目标为本地桌面应用，数据库加密且无 API，但进程内存中可获取密钥/数据。

```
Agent → wx-cli → Daemon → Memory scan → 解密数据库 → 结构化输出
```

**设计模板**：
```bash
# 初始化（一次性，macOS 需 ad-hoc 签名）
wx init

# 使用（daemon 自动管理）
wx sessions --json          # 会话列表
wx history <session> --json # 聊天记录
wx search <keyword> --json  # 全文搜索
```

**关键约束**：
- 完全本地，数据不出机
- Daemon 持久化解密缓存，mtime 不变则复用
- macOS 需 `codesign --force --deep --sign -` 重签微信（或 TCC 授权 Terminal）
- 每次微信更新后需重新签名
- `--json` 输出包含 `meta` 字段（freshness、source 信息）供 Agent 判断数据时效

**返回值格式**：
```json
{"ok": true, "data": [...], "meta": {"source": "memory-scan", "freshness": "realtime", "contact_count": 42}}
```

**Hermes 中潜在案例**：微信私域数据查询（客户对话回溯）、钉钉本地数据

**何时采用**：本地桌面应用 ∧ 无 API ∧ 数据在本地加密存储 → 内存扫描

---

### 范式四：CDP 直连（CDP Direct）

**来源**：OpenCLI Desktop adapters

**适用**：目标为 Electron 应用，可通过 `--remote-debugging-port` 暴露 CDP。

```
Agent → CDP client → Electron app CDP endpoint → 应用内部
```

**设计模板**：
```bash
# 启动 Electron 应用并暴露 CDP
cursor --remote-debugging-port=9222

# CDP 直连（不走 Extension）
opencli --cdp-endpoint http://127.0.0.1:9222 <adapter> <command>
```

**关键约束**：
- 仅 Electron/Chromium 内核应用可用
- 端口配置需与应用启动参数一致
- 比浏览器桥接轻量（不需要 Extension），但应用覆盖面窄

**Hermes 中潜在案例**：Claude Desktop、Cursor 自动化

**何时采用**：Electron 应用 ∧ 可配置 CDP 端口 → CDP 直连

---

## 范式决策树

```
目标系统
├─ 有 CLI/API？
│  └─ YES → 范式一：直接藩篱
│     例：ComfyUI API → 写 harness CLI
│          飞书 REST API → feishu-* 技能
│
├─ 是 Web SaaS？（网页操作）
│  ├─ 有公开 API？→ 范式一
│  ├─ 无反爬，Hermes browser 可访问？→ Hermes browser 工具
│  └─ 有反爬（小红书/公众号/微博）？→ 范式二：浏览器桥接
│
├─ 是本地桌面应用？
│  ├─ 是 Electron 应用？
│  │  ├─ 可配置 CDP？→ 范式四：CDP 直连
│  │  └─ 不可配置？→ 范式二（走 Chrome + Extension）
│  └─ 原生桌面应用（数据库加密）？
│     └─ 可内存扫描？→ 范式三：内存扫描
│        不可？→ 范式二（如果有 Web 版）或放弃
│
└─ 以上都不适用？
   └─ 评估 ROI，可能需要自定义桥接方案
```

## 通用设计原则

无论采用哪种范式，Agent-Native CLI 都应遵循：

### 1. 结构化输出优先
```
✅ GOOD: {"ok": true, "data": [...], "total": 42}
❌ BAD: "Found 42 results:\n1. foo\n2. bar"
```

### 2. 机器可发现
- 提供 `SKILL.md`（Agent 自动读取）
- 提供 `llms.txt` 或 registry entry
- 命令列表可通过 `<tool> list --json` 获取

### 3. 幂等操作
- 查询命令（search/list/get）必须幂等
- 写操作（create/update/delete）返回操作 ID 供状态查询
- 避免「切换/切换回」式的状态修改

### 4. 错误自描述
```json
{
  "ok": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "检测到频率限制，建议等待 60 秒后重试",
    "retry_after": 60
  }
}
```

### 5. Session 管理
- 长连接/持久状态用 daemon 模式（wx-cli 风格）
- 短连接/无状态用一 shot 模式（CLI-Anything 风格）
- 浏览器桥接用 session TTL 回收（OpenCLI 风格）

### 6. Skill 即文档即接口
- 每个 CLI 配套一个 SKILL.md
- SKILL.md 同时是人类文档和 Agent 操作手册
- 包含：安装步骤、命令列表、输出格式、常见陷阱、验证清单

## 反爬生存策略（范式二专有）

针对浏览器桥接的反爬对抗：

1. **真实浏览器**：绝不 headless，Chrome 必须 GUI 运行
2. **登录态复用**：不传递 cookie，让 Chrome 自身维护 session
3. **人类行为模拟**：随机延迟（200-800ms）、自然滚动轨迹
4. **限速检测**：返回 `meta.rate_limit`，Agent 据此调整频率
5. **降级策略**：IP 被风控 → 提示用户手动解除 → 恢复后继续

## 实施清单

设计一个新的 Agent-Native CLI 接入时，按以下顺序评估：

- [ ] 确定目标系统的接口特征（CLI/API/Web/Desktop/Electron？）
- [ ] 按决策树选择正确的桥接范式
- [ ] 确认是否有现有 skill 可复用（搜索 skills_list 和 CLI-Anything registry）
- [ ] 设计 CLI 命令结构（search/list/get/create/update/delete + --json）
- [ ] 定义结构化输出 schema（ok/data/error/meta）
- [ ] 确认错误码枚举（NETWORK_ERROR / RATE_LIMITED / AUTH_EXPIRED / NOT_FOUND / PERMISSION_DENIED）
- [ ] 编写 SKILL.md（安装 + 命令 + 输出格式 + 陷阱 + 验证）
- [ ] 端到端验证（`skill_view` → 按文档执行 → 确认输出符合 schema）
- [ ] 记录已知局限（OS 限制、版本依赖、风控风险）

## 常见陷阱

1. **过度封装**：目标已有良好的 CLI/API，不要再包一层浏览器桥接
2. **忽略反爬**：以为 `curl` 能搞定，被 IP 封禁后才改用浏览器桥接
3. **输出格式不统一**：有的命令返回 JSON，有的返回纯文本——Agent 无法可靠消费
4. **缺少 SKILL.md**：技能写了但 Agent 不知道怎么用
5. **Daemon 不自动启动**：依赖后台进程但没做健康检查和自动拉起
6. **不处理登录态过期**：浏览器桥接的 cookie/session 过期后静默失败

## 参考生态

| 系统 | 范式 | GitHub | 用途 |
|------|------|--------|------|
| CLI-Anything Hub | 直接藩篱 | HKUDS/CLI-Anything (41.5K⭐) | 注册表 + 包管理器 |
| OpenCLI | 浏览器桥接 | jackwener/OpenCLI (23K⭐) | 反爬站点 CLI |
| wx-cli | 内存扫描 | jackwener/wx-cli (3.1K⭐) | 微信本地数据 |
| ComfyUI (Hermes) | 直接藩篱 | — | AI 图像/视频生成 |
| Obsidian (Hermes) | 直接藩篱 | — | 笔记管理 |
| Feishu 系列 (Hermes) | 直接藩篱 | — | 飞书 REST API |
| OpenCLI (Hermes) | 浏览器桥接 | — | 小红书/知乎/微博/B站 |

---

*本文档是活的参考——每次接触到新的桥接模式或发现陷阱，用 `skill_manage(action='patch')` 更新。*
