# L3 Bitable 分发架构

> 2026-05-30 实现。解决云端 cron 无法使用 agent-browser 的问题，通过 Bitable 队列桥接云端分发与本地执行。

## 架构

```
Cloud cron (travel-intel-collect, 07:00)
  ├─ L1: browser_collector.py 百度+夸克 → Wiki (WSL本地 06:30 独立运行)
  ├─ L2: urllib 站点直抓 → Wiki
  └─ L3: 写 4-6 个关键词到 Bitable 队列
       ↓
WSL crontab (*/5 * * * *) → l3_poller.py
  ├─ 读取 Bitable pending tasks
  ├─ agent-browser 搜索 (百度/B站/头条)
  ├─ 创建 Wiki 文档 (MYQtwtPE / E7xyw9pS)
  └─ 更新 Bitable 状态
```

## Bitable 配置

| 项目 | 值 |
|------|-----|
| base_token | `TDYYwZ0T0ifLtdkK9iOcp2HTnwf` |
| table_id | `tblVKG82oOl3UaNW` |
| Wiki 节点 | 行业资讯 (在行业资讯分类下) |

## 字段

| 字段 | field_id | 类型 | 说明 |
|------|----------|------|------|
| Text | fldvtLgrUo | text | 任务名称，含"竞品"→路由到竞品动态节点 |
| 搜索关键词 | fldQLYRyV0 | text | agent-browser 搜索词 |
| 平台 | fldqZJK4dC | select | 百度/B站/头条/综合 |
| 结果摘要 | fldnEcMm15 | text | pending→processing→done/failed |

## 写入任务 (云端 cron)

```bash
lark-cli api POST "/open-apis/bitable/v1/apps/TDYYwZ0T0ifLtdkK9iOcp2HTnwf/tables/tblVKG82oOl3UaNW/records" \
  --as bot \
  --data '{"fields":{"Text":"竞品_探洞行业动态","搜索关键词":"贵州 探洞 洞穴探险 2026","平台":"综合","结果摘要":"pending"}}'
```

## 轮询器 (Hermes cron, no_agent 脚本模式)

```bash
# Hermes cron: travel-intel-l3-poller (e92c1aeeb70e)
# 调度: */5 * * * *, no_agent=true
# 脚本: l3_poller.py
```

Cron job 详情（Hermes）:
| 字段 | 值 |
|------|-----|
| job_id | `e92c1aeeb70e` |
| 调度 | `*/5 * * * *` |
| 脚本 | `l3_poller.py` (→ `~/.hermes-feishu/scripts/l3_poller.py`) |
| 模式 | `no_agent=true` (纯脚本，不消耗 LLM token) |
| 日志 | `~/.hermes-feishu/logs/l3_poller.log` |

## 平台选择建议

| 场景 | 推荐平台 |
|------|----------|
| 竞品深度研究 (探洞/桨板/天坑) | 综合 (百度+B站+头条) |
| 政策法规 | 百度 |
| 视频攻略 | B站 |
| 资讯动态 | 头条 |

## Wiki 入库流程

l3_poller.py 使用两步法创建文档：
1. `POST /wiki/v2/spaces/{space_id}/nodes` — 创建空 Wiki 节点
2. `lark-cli docs +update --api-version v2 --command overwrite` — 填充内容

注意：`lark-cli docs +create --wiki-node` 不会将文档添加到 Wiki 树，已废弃此方式。
