---
name: hermes-performance-diagnosis
description: "Hermes 任务执行慢的系统性能诊断——排查文件搜索、网络搜索、LLM 推理三大瓶颈，按优先级输出根因和修复方案。触发：执行慢/很慢/太久了/卡住了/性能/performance/优化/诊断。"
version: 1.0.0
author: jorinyang
triggers:
  - 执行慢
  - 很慢
  - 太久了
  - 卡住了
  - 性能
  - performance
  - 优化
  - 诊断
  - 为什么这么慢
  - 慢在哪里
---

# Hermes 性能诊断

当用户报告 Hermes 任务执行过慢时，按此流程系统诊断并输出根因报告。

## 诊断框架：三通道并行检测

```
用户反馈"太慢了"
  ├─ [通道1] 文件搜索瓶颈
  │   └─ node_modules 黑洞 / .rgignore 缺失 / 目录深度
  ├─ [通道2] 网络搜索瓶颈
  │   └─ Firecrawl 本地服务 / API 延迟 / 后端降级
  └─ [通道3] LLM 推理瓶颈
      └─ reasoning_effort / streaming / skills 注入量 / context 压缩
```

## 通道1：文件搜索诊断

### 步骤

```bash
# 1. 工作区文件数
find /c/Users/Aorus/workspace -type f 2>/dev/null | wc -l

# 2. node_modules 数量与大小
find /c/Users/Aorus/workspace -name "node_modules" -type d 2>/dev/null | wc -l
du -sh /c/Users/Aorus/workspace/*/node_modules 2>/dev/null | sort -rh | head -10

# 3. 基准测试（有/无排除）
time find /c/Users/Aorus/workspace -name "*.py" -type f 2>/dev/null | wc -l
time find /c/Users/Aorus/workspace -not -path "*/node_modules/*" -name "*.py" -type f 2>/dev/null | wc -l

# 4. .rgignore 是否存在
cat /c/Users/Aorus/.rgignore 2>/dev/null || echo "MISSING"
```

### 判定标准

| 指标 | 正常 | 警告 | 需要修复 |
|------|------|------|----------|
| 工作区文件数 | < 5万 | 5-15万 | > 15万 |
| node_modules 数量 | < 5 | 5-20 | > 20 |
| 单次文件搜索耗时 | < 0.5s | 0.5-2s | > 2s |
| .rgignore | 存在且有排除规则 | 存在但规则少 | 不存在 |

### 修复

1. **删除不活跃项目的 node_modules**：`rm -rf <project>/node_modules`
2. **创建 .rgignore**：排除 `node_modules/` `.git/` `dist/` `build/` `__pycache__/` `.next/` `target/` `*.pyc`
3. Hermes 的 `search_files`（ripgrep 后端）自动读取 `.rgignore`

## 通道2：网络搜索诊断

### 步骤

```bash
# 1. API 延迟基线
for host in api.deepseek.com api.minimaxi.com openrouter.ai; do
  echo -n "$host: "; curl -s -o /dev/null -w "%{time_total}s" --connect-timeout 5 "https://$host"
done

# 2. Firecrawl 本地服务
curl -s --connect-timeout 3 http://localhost:3002/health || echo "DOWN"

# 3. 当前 web.backend 配置
grep -A3 "^web:" ~/.hermes/config.yaml

# 4. Firecrawl MCP 配置
grep -A8 "firecrawl:" ~/.hermes/config.yaml
```

### 判定标准

| 服务 | 正常延迟 | 警告 | 故障 |
|------|----------|------|------|
| deepseek API | < 0.5s | 0.5-2s | > 2s 或超时 |
| minimax API | < 4s | 4-8s | > 8s |
| openrouter | < 5s | 5-10s | > 10s |
| firecrawl :3002 | < 0.5s | 0.5-2s | 超时/拒绝 |

### Firecrawl 降级链路

```
firecrawl_search（MCP localhost:3002）
  ↓ 不可用 → 检查 Docker
    ├─ Docker 可恢复 → docker compose restart → (无效则) docker compose up -d
    └─ Docker 不可恢复（SYSTEM 账户/WSL2限制）→ 降级
        ↓
      mcp_minimax_mcp_web_search
        ↓ 也不可用 →
          web_search（Hermes 原生 DuckDuckGo）
            需临时：sed -i 's/backend: firecrawl/backend: '\\'''\\''/g' ~/.hermes/config.yaml
```

> **已部署守护**：`firecrawl-health-watchdog` cron（`no_agent=true`，每 5 分钟）自动执行上述 Docker 恢复流程。详见 `firecrawl-web` 技能 `references/firecrawl-recovery.md`。

## 通道3：LLM 推理诊断

### 步骤

```bash
# 1. reasoning_effort（最大单一因素）
grep "reasoning_effort" ~/.hermes/config.yaml

# 2. streaming
grep "enabled:" ~/.hermes/config.yaml | head -3  # streaming section

# 3. skills 注入量
find ~/.hermes/skills -name "SKILL.md" -type f | wc -l
du -sh ~/.hermes/skills

# 4. api_max_retries
grep "api_max_retries" ~/.hermes/config.yaml

# 5. show_reasoning
grep "show_reasoning" ~/.hermes/config.yaml
```

### 判定标准

| 配置 | 推荐值 | 当前值 | 影响 |
|------|--------|--------|------|
| `reasoning_effort` | `high` | `xhigh` | xhigh 延迟比 high 多 40-60% |
| `streaming.enabled` | `true` | `false` | 用户感知等待时间差 3-5x |
| 技能数量 | < 80 | > 100 | 每次注入 ~200-500KB 上下文 |
| `api_max_retries` | 2 | 3 | 每多一次重试 = +100% 最坏延迟 |
| `show_reasoning` | `true` | `false` | 关了看不到思考过程，体感"卡住" |

## 复合任务耗时精算模型

以"搜索本地文件 + 网页搜索 + 信息总结"为例：

| 环节 | 最短 | 最长 | 瓶颈 |
|------|------|------|------|
| LLM Turn 1（规划工具调用） | 5s | 15s | reasoning_effort |
| 文件搜索（有 node_modules） | 0.14s | 4.4s | node_modules 黑洞 |
| 网页搜索（Firecrawl 超时） | 超时 | 10s+ | 本地服务宕机 |
| 上下文压缩 | 0s | 3s | context 过大 |
| LLM Turn 2（分析+生成） | 5s | 20s | reasoning_effort |
| 响应输出（streaming=false） | 0.5s | 2s | 非流式 |

**总量**：正常 15-30s，故障状态 40-90s。

## 输出格式

诊断完成后，以表格形式输出：

```
## 诊断结果

| 通道 | 状态 | 根因 | 修复 |
|------|------|------|------|
| 文件搜索 | ✅/⚠️/❌ | ... | ... |
| 网络搜索 | ✅/⚠️/❌ | ... | ... |
| LLM 推理 | ✅/⚠️/❌ | ... | ... |

### 优先级建议
P0: ...
P1: ...
P2: ...
```

## ⛔ 反例

- ❌ 不检查硬件（磁盘 IO/内存/CPU）就直接归因于"模型慢"
- ❌ 跳过 node_modules 排查就直接优化文件搜索
- ❌ xhigh reasoning 时反复重试——不是网络问题，是模型在思考
- ❌ 在 SYSTEM 账户下反复尝试启动 Docker Desktop
