# 云端触发 → 本地执行 任务队列架构

> 2026-05-28 实现。解决 Hermes 云端 cron 无法使用 agent-browser 的问题。

## 架构

```
Hermes 云端 cron (travel-task-dispatcher)
    │  每天 07:00
    │  写任务记录到 Bitable
    ▼
飞书 Bitable "任务队列"
  base_token: DhZcbnof3aj5d6siC1UcgyXtnvb
  table: tblVKG82oOl3UaNW
  字段: Text(任务名), 搜索关键词, 结果摘要
    │
    │  WSL crontab 每2分钟轮询
    ▼
WSL 本地 poller (~/.hermes-feishu/scripts/task_poller.py)
    │  Chromium --dump-dom Bing 搜索
    │  创建飞书文档
    │  更新 Bitable 状态
    │  推送群消息
    ▼
贵州之客群
```

## 关键组件

| 组件 | 位置 | 说明 |
|------|------|------|
| 云端触发器 | cron job `6f194036f3ae` | 每天 07:00 向 Bitable 写任务 |
| 任务队列 Bitable | 知识库行业资讯节点下 | 云端写、本地读 |
| 本地轮询器 | `~/.hermes-feishu/scripts/task_poller.py` | WSL crontab `*/2 * * * *` |
| 搜索执行 | Chromium `--dump-dom` | 比 agent-browser daemon 可靠 |

## Bitable API 注意事项

- 创建记录用 `PUT`（`PATCH` 返回 404）
- lark-cli api 用 `--data` 标志传 JSON，**不用 stdin**
- 输出在 `stderr` 而不是 `stdout`
- `结果摘要` 为空字符串时 API 不返回该字段

## 轮询器工作流

1. `GET /records` 列出所有记录
2. 筛选 `结果摘要` 为空或 "pending" 且 `搜索关键词` 非空的记录
3. Chromium `--dump-dom` 搜索 → 正则提取标题+URL+摘要
4. `lark-cli docs +create` 创建飞书文档
5. `PUT /records/{id}` 更新状态 → "done: 采集N条"
6. `POST /im/v1/messages` 推送群通知

## 已验证的端到端测试

### 单任务测试（2026-05-28 首轮）

```
1. Bitable 写入任务 → recvkTriTpNeMk: "贵州 溶洞 探洞 新发现 2026"
2. WSL poller 拾取 → Chromium --dump-dom Bing 搜索
3. 正则提取 6 条结果（标题+URL+摘要）
4. lark-cli docs +create 创建文档《2026-05-28_test_probe_caves_2026》
5. Bitable 更新: "done: 采集 6 条"
6. 群消息推送: "🤖 自动采集完成"
```

### 9任务批量测试（2026-05-28 二轮）

覆盖 knowledge 5类（景点/酒店/交通/政策/活动）+ monitor 4竞品（探洞/天坑/桨板/坝盘）：

| # | 任务 | 类型 | 结果 |
|---|------|------|------|
| 1 | 景点_贵州2026夏季新开户外项目 | knowledge | ✅ 6条 |
| 2 | 酒店_贵州新开业民宿2026 | knowledge | ✅ 6条 |
| 3 | 交通_贵州旅游交通新变化2026 | knowledge | ✅ 6条 |
| 4 | 政策_贵州文旅最新政策2026 | knowledge | ✅ 6条 |
| 5 | 活动_贵州户外赛事节庆2026 | knowledge | ✅ 6条 |
| 6 | 竞品_探洞行业动态 | monitor | ✅ 6条 |
| 7 | 竞品_天坑旅游动态 | monitor | ✅ 6条 |
| 8 | 竞品_桨板SUP动态 | monitor | ✅ 6条 |
| 9 | 竞品_坝盘区域动态 | monitor | ✅ 6条 |

**54条结果，13份文档全部入库。Bitable 全标记 done。**

### 修复的关键 Bug

1. **`lark-cli docs +create --content @file` 必须用相对路径。** 使用绝对路径 `/tmp/task_doc.xml` 时命令静默失败（exit code 2），但 `capture_output=True` + 未检查 `returncode` 导致文档从未创建。
   **修复**: 文件写至 `$SCRIPT_DIR/tmp/task_doc.xml`，`cwd=SCRIPT_DIR`，`--content @tmp/task_doc.xml`。

2. **Monitor 任务误存入行业资讯节点。** 任务名前缀 `竞品_` 的任务应路由到竞品动态父节点 `EAMYw1CPoipVWtkObbtcR2oDnNc`。
   **修复**: `get_pending_tasks()` 中根据 `task_name.startswith("竞品_")` 设置 `task_type`，`create_feishu_doc()` 根据 `task_type` 选择父节点。

## 环境要求

- WSL 必须运行（cron service active）
- Chromium 150 @ `~/.chromium/chrome-linux/`
- lark-cli 已配置 bot 身份
- 搜索前 `unset` 所有 proxy 环境变量
