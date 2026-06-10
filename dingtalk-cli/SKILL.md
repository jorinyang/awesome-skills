---
name: dingtalk-cli
description: DingTalk Workspace CLI (dws) — 安装、配置、20项MCP服务全能力边界（ai表格/审批/日历/文档/通讯录/邮箱/考勤等）。适用于钉钉生态内的自动化操作。
version: 1.3.0
triggers:
  - 钉钉CLI
  - dws
  - dingtalk-cli
  - dingtalk-workspace
  - 钉钉AI表格
  - 钉钉审批
  - 宜搭
related_skills: [feishu-table, supabase-backend]
---

# DingTalk Workspace CLI (dws)

## 安装

> 详细绕过方案见 `references/install-workaround.md`

```bash
npm install -g dingtalk-workspace-cli
```

### 安装陷阱：unzip 缺失

如果系统没有 `unzip`（如 WSL 精简环境），postinstall 会失败。绕过方法：

```bash
# 1. 跳过 postinstall
npm install -g dingtalk-workspace-cli --ignore-scripts

# 2. 手动提取平台二进制（不需要 unzip，用 tar）
cd $(npm config get prefix)/lib/node_modules/dingtalk-workspace-cli

# 3. 提取 Linux x64 二进制
node -e "
const {execFileSync} = require('child_process');
const tmp = require('fs').mkdtempSync('/tmp/dws-');
execFileSync('tar', ['-xzf', 'assets/dws-linux-amd64.tar.gz', '-C', tmp]);
const dws = require('fs').readdirSync(tmp, {recursive:true}).find(f=>f.endsWith('dws'));
require('fs').copyFileSync(tmp+'/'+dws, 'vendor/dws');
require('fs').chmodSync('vendor/dws', 0o755);
"

# 4. 验证
dws --help
```

### 平台包清单

`assets/` 目录包含所有平台的预编译 Go 二进制：

| 文件 | 平台 |
|------|------|
| `dws-linux-amd64.tar.gz` | Linux x64 |
| `dws-linux-arm64.tar.gz` | Linux ARM |
| `dws-darwin-amd64.tar.gz` | macOS Intel |
| `dws-darwin-arm64.tar.gz` | macOS Apple Silicon |
| `dws-windows-amd64.zip` | Windows x64 |

## MCP 服务全景

`dws` 启动后自动发现以下 20 项 MCP 服务。详细边界测试结果见 `references/boundary-test-20260608.md`。

| 服务 | 能力 |
|------|------|
| `aitable` | **AI表格** — Base/数据表/字段/记录/视图/仪表盘/导入导出/附件/模板 |
| `oa` | **OA审批** — 发起/同意/拒绝/撤销 |
| `calendar` | 日历日程/会议室/闲忙 |
| `contact` | 通讯录/用户/部门搜索 |
| `todo` | 待办任务管理 |
| `ding` | DING消息发送/撤回 |
| `doc` | 钉钉文档读写/块级编辑/评论 |
| `sheet` | 钉钉表格管理 |
| `wiki` | 知识库管理 |
| `drive` | 云盘文件/上传/下载 |
| `attendance` | 考勤打卡/排班/统计 |
| `report` | 日志（OA周报）提交/统计 |
| `minutes` | AI听记 — 摘要/待办/文字稿/思维导图 |
| `mail` | 邮箱收发 |
| `aisearch` | AI搜人 — person/enterprise/behavior 三维搜索 |
| `chat` | IM扩展命令 — 置顶会话/单聊/群聊信息 |
| `devdoc` | 开放平台文档搜索 |
| `live` | 直播列表/流管理 |
| `hrmregister` | HR花名册 — 10个字段组(系统/基本/工作/个人/学历/银行卡/合同/紧急联系人/家庭/材料) |
| `pat` | 行为授权管理 |
| `doc-comment` | 文档评论 (子 server，由 doc 调用) |

## PAT（个人行为授权）安全模型

dws 内置零信任安全：**读操作无需授权，写操作分层管控**。

| 风险等级 | 示例操作 | 是否需要 PAT |
|----------|---------|:--:|
| 低风险（读） | `list`, `get`, `search` | ❌ |
| 低风险（创建） | calendar `event create`, doc `create` | ❌ |
| 中风险（修改） | calendar `event update` | ⚠️ 部分需要 |
| 中风险 | aitable `record update` | ❌ |
| 高风险（删除） | calendar `event delete` | ✅ `calendar.event:delete` |

当操作需要 PAT 时，dws 返回：
```json
{"code": "PAT_MEDIUM_RISK_NO_PERMISSION", "data": {"authorizationUrl": "https://open-dev.dingtalk.com/fe/old?hash=...", "userCode": "XXXX-XXXX", "requiredScopes": [{"scope": "calendar.event:delete"}]}}
```

用户在浏览器打开 `authorizationUrl` 授权一次后永久有效。`dws pat` 命令管理已授权项。

**各服务 PAT 边界**（已验证，含已授权和 API 限制）：

| 服务 | 操作 | PAT 需求 | 备注 |
|------|------|:--:|------|
| calendar | event create/update | ❌ 免 PAT | 自动附带钉钉视频会议 |
| calendar | event delete | ✅ `calendar.event:delete` | 已授权，完整闭环 |
| aitable | record CRUD | ❌ 免 PAT | Base 创建也免 PAT |
| aitable | base delete | ✅ `aitable.base:delete` | 已授权；可用 `doc delete` 桥接绕过 PAT |
| todo | task create/done | ❌ 免 PAT | 创建需 `--executors` |
| todo | task delete | ⚠️ PAT 通过但 API 不支持 | **钉钉 API 返回 false，只能标记完成无法真删** |
| ding | message send | ✅ `ding.message:send` + **需 `--robot-code`** | PAT 授权后还需机器人应用 code |
| chat | message send | ❌ 免 PAT | 单聊/群聊均可直接发，推荐用于通知 |
| report | create | ❌ 免 PAT | 创建后 **不可 API 删除**（无 delete 子命令） |
| mail | draft create | ❌ 免 PAT | **草稿不可彻底删除**（batch-delete 只移回收站） |
| drive | upload/delete | ❌ 免 PAT | 三步上传自动完成 |

### 钉钉 API 原生限制（非 dws 问题）

- **待办不可删除**：`todo.task:delete` PAT scope 存在，但 API 返回 `{"success": false}`。只能标记完成 (`task done --task-id ... --status true`)
- **日志不可删除**：`dws report` 无 `delete` 子命令。创建后残留数据只能去钉钉客户端手动删除
- **草稿不可彻底删除**：`dws mail` 无 `draft delete`，`batch-delete` 只移到回收站
- **DING 需机器人**：`ding.message:send` 需要 `--robot-code`（即使 PAT 已授权），用户发消息用 `chat message send` 代替（免 PAT，直接发单聊/群聊）
- **PAT 无 list 命令**：`dws pat` 无法查看已有授权列表，只能通过触发需要授权的操作来获取 authorizationUrl

### PAT 全授权后完整边界（2026-06-08 验证）

用户（月夜/杨瑒，组织主管理员）已完成全部 PAT scope 授权后的最终边界：

| 能力 | 状态 | 验证方式 |
|------|:--:|------|
| contact 通讯录 | ✅ 只读 | `user get-self`, `dept list-children` |
| calendar 日历 CRUD | ✅ 完整 | create→get→update→delete 闭环 |
| todo 待办创建/标记 | ✅ | `create --executors` + `done --status true` |
| todo 待办删除 | ❌ API限制 | PAT 通过但 API 返回 false |
| chat 消息收发 | ✅ | `message send` 免 PAT，`recall` 可撤回 |
| ding DING 发送 | ⚠️ | PAT 已授权但需 `--robot-code` |
| doc 文档 CRUD | ✅ 完整 | 20+命令，块级编辑完善 |
| wiki 知识库 | ✅ | 创建/删除通过 doc 桥接 |
| sheet 表格 | ✅ | `list --node` 必填 |
| aitable AI表格 CRUD | ✅ 完整 | Base/Table/Field/Record 全闭环 |
| drive 云盘 | ✅ 完整 | upload→list→delete |
| oa 审批读 | ✅ | `list-forms` 报 200002 但 list-pending/list-submitted 正常 |
| attendance 考勤 | ✅ | summary/record get 正常 |
| report 日志创建 | ✅ | 创建成功但不可删 |
| mail 邮箱 | ✅ | 搜索/草稿创建正常 |
| minutes 听记 | ✅ | `list mine` |
| aisearch 搜索 | ✅ | person/enterprise/behavior 三维 |
| hrmregister 花名册 | ✅ | 10字段组 + 离职列表 |
| pat 管理 | ❌ | 无 list 命令 |

## 与飞书 CLI 对比

| 能力 | 飞书 (lark-cli) | 钉钉 (dws) |
|------|:--:|:--:|
| 多维表格/Base | `base +table-*` | `aitable` |
| 审批 | 无内置 | `oa` |
| 文档 | `docs +create` | `doc` |
| 日历 | 无 | `calendar` |
| 通讯录 | 无 | `contact` |
| 考勤 | 无 | `attendance` |
| 待办 | 无 | `todo` |
| AI听记 | 无 | `minutes` |
| 知识库 | `wiki +node-*` | `wiki` |

## 认证

两种登录方式。**Agent/无头/SSH 环境必须用 `--device`。**

### 设备流（推荐：无头/远程/Agent 环境）

```bash
dws auth login --device
```

输出授权码 + 短链接，用户在任意设备浏览器打开并输入码即可，无需本地浏览器。

```
▶ Step 1: Requesting device authorization code...
  link: https://login.dingtalk.com/oauth2/device/verify.htm
  authorization code: XXXX-XXXX
  直达链接: https://login.dingtalk.com/oauth2/device/verify.htm?user_code=XXXX-XXXX
  (900 秒内有效)

▶ Step 2: Waiting for user authorization...  (每 5 秒轮询)
```

**Agent 场景下提取授权码的陷阱：** 设备流先输出码，然后进入轮询等待。后台运行时输出被缓冲，无法实时读取。解决：

```bash
# 让 dws 同时输出到终端和临时文件
dws auth login --device 2>&1 | tee /tmp/dws_login.txt &

# 延迟后读取码
sleep 3 && cat /tmp/dws_login.txt
```

拿到码后展示给用户，用户授权后轮询进程自动检测并退出。验证：`dws auth status`

### Loopback 流（仅本地有浏览器时）

```bash
dws auth login
```

1. 命令启动本地回调服务器（随机端口，如 `127.0.0.1:33205`）
2. 自动打开浏览器或输出授权 URL
3. 浏览器完成钉钉登录/扫码 → 回调到 localhost → 完成

> ⚠️ 终端不显示二维码。是打开浏览器链接完成授权，不是终端扫码。
> ⚠️ SSH/远程/Agent 环境不可用 — 127.0.0.1 回调不可达。

### PATH 配置

安装后 `dws` 可能在 `~/.hermes/node/bin/` 下，不自动在 PATH 中。

```bash
# 一次性
export PATH="$HOME/.hermes/node/bin:$PATH"

# 持久化
echo 'export PATH="$HOME/.hermes/node/bin:$PATH"' >> ~/.bashrc
```

### 状态检查

```bash
dws auth status    # {"authenticated": true/false}
dws auth logout    # 清除凭证
dws auth login --force  # 强制重新登录
```

**内置凭证：** `DWS_CLIENT_ID` / `DWS_CLIENT_SECRET` 已内置钉钉官方默认值，无需自建应用。

### 前置条件：组织管理员开启 CLI 数据访问

即便认证流程完成，如果组织未开启 CLI 数据访问，会收到错误：

```
⚠️ CLI data access is not enabled for this organization
   组织主管理员：<admin_name>
   device authorization failed: CLI data access is not enabled...
```

#### 方案 A：组织级开关

组织主管理员登录 https://open-dev.dingtalk.com → 左侧 **"基本信息"** → **"开发者设置"**：

1. **CLI 管理** → 开启「允许成员通过 CLI 访问个人数据」（若未开启报错 `CLI data access is not enabled`）
2. **使用范围管理** → 点击编辑，选择「全员可用」（若选「全员禁止使用」则 dws 报错 `该组织已禁止所有成员使用 CLI`；若选「指定人员范围可用」，确保当前用户在范围内）

设置后重新 `dws auth login --device`。

#### 方案 B：自建应用绕过（推荐，无需组织开关）

当组织级 CLI 访问管理入口不可见时，创建自有钉钉应用替代内置默认凭证：

1. 打开 https://open-dev.dingtalk.com/fe/app#/corp/app
2. 创建**企业内部应用**（任意命名）
3. 记录 **AppKey**（Client ID）和 **AppSecret**（Client Secret）
4. 应用详情 → 安全设置 → 重定向 URL 添加：`http://127.0.0.1`
5. 版本管理与发布 → 发布应用
6. 使用自有凭证登录：

```bash
dws auth login --client-id <AppKey> --client-secret <AppSecret>
```

自建应用走独立 OAuth 通道，不经过组织级 CLI 访问校验。

## 附：GB/T 17775-2024 标准

2025年10月30日，中国旅游景区协会主办、万峰林旅游集团承办、大华股份协办的
"《旅游景区质量等级划分》实操解读专题培训"以此标准为基础。
标准全文组装技术及来源见 `references/gbt17775-2024-standard.md`。

两个 CLI 互不冲突，可在同一项目中使用：

```
lark-cli base +record-list ...  --as bot    # 飞书多维表格
dws aitable record list ...                  # 钉钉AI表格
```

建议在 answer 工作流中同时提供两个技术路径的方案对比。

## 常见陷阱

- **组织管理员未开启 CLI 数据访问**：设备授权成功但最终被拒，提示 "CLI data access is not enabled"。项目处于共创阶段，"CLI 访问管理"入口可能仅对受邀组织可见。管理员开启路径：open-dev.dingtalk.com → 基本信息 → 开发者设置 → CLI管理（开启「允许成员通过 CLI 访问个人数据」）+ 使用范围管理 → 全员可用。如找不到入口，用自建应用方案绕过：创建企业内部应用 → 获取 AppKey/AppSecret → `dws auth login --client-id <key> --client-secret <secret>`。
- **PAT 安全门理解**：读操作免 PAT，创建操作大多免 PAT，删除操作必需要 PAT。当操作需要 PAT 时，dws 返回 authorizationUrl + userCode，用户浏览器打开授权一次后永久有效。全 PAT 授权后，calendar/aitable/drive/chat 均可完整 CRUD。但有三项钉钉 API 原生限制：待办不可删除（只能标记完成）、日志不可删除（无 delete 子命令）、邮件草稿不可彻底删除（batch-delete 只移回收站）。
- **DING 消息发送需机器人**：即使 PAT 已授权 `ding.message:send`，仍需 `--robot-code`（钉钉机器人应用 code）。做通知推送优先用 `chat message send`（免 PAT，直接发单聊/群聊）。
- **每轮 `--device` 生成新码**：每次执行 `dws auth login --device` 都生成全新授权码，旧码作废。必须先拿到码展示给用户，然后保持同一进程轮询直到用户完成授权。不能先跑一次拿码，再跑第二次等授权。
- **后台模式输出缓冲**：`dws auth login --device` 在后台运行时输出被完全缓冲，`process poll` 读到空内容。必须用 `tee` 写到文件，再从另一终端调用读文件（见认证→设备流章节）。
- **Loopback 流程不可用于远程**：loopback 的 `127.0.0.1:<port>/callback` 只在 dws 所在本机可达。Agent 在远程跑 dws、用户在本地浏览器授权时，回调必定失败。始终用 `--device`。
- **安装路径不在 PATH**：npm 全局安装后 `dws` 落在 `~/.hermes/node/bin/`，不会自动加入 PATH。每次新会话需 export 或加入 `.bashrc`。

## 各服务命令模式与边界

参考 `references/boundary-test-20260608.md` 获取 20 服务的逐项测试报告，`references/boundary-test-20260609.md` 获取 PAT 全授权后最终验证结果。以下是核心边界速查：

| 服务 | 关键命令 | 边界/坑点 |
|------|---------|----------|
| contact | `user get-self`, `dept list-children --id 1` | 纯只读 |
| todo | `task list --status false`, `task create --title ... --executors ...`, `task done --task-id ... --status true` | **不可 API 删除**（只能标记完成）；创建必填 `--executors` |
| aitable | `base list/create`, `table list`, `record list/insert/update/get` | **完整 CRUD**，最推荐做工单系统。`base:delete` 需 PAT（可用 `doc delete` 桥接绕过） |
| doc | `list`, `search`, `create`, `block insert`, `update`, `delete` | 20+子命令，最完整。块级编辑、评论、上传下载全覆盖 |
| wiki | `space list`, `node list` | 创建/删除通过 doc 命令桥接 |
| oa | `list-submitted`, `list-pending` | `list-forms` 可能报 `200002` 权限不足 |
| mail | `mailbox list`, `message search --query "..." --size 5`, `draft create` | 362封邮件可搜。**草稿不可彻底删除** |
| sheet | `list --node <docId>`, `range`, `create`, `delete` | **必须 --node**，不能裸调 |
| minutes | `list mine` | `list` 是命令组，需子命令 `mine/all/shared` |
| hrmregister | `list-authorized-roster-fields`, `query-dismission-employee-list` | **无分页参数**，使用默认分页 |
| live | `stream list` | 需 `stream` 子命令 |
| devdoc | `article search --query "..." --size N` | 分页用 `--size`（非 `--page-size`） |
| ding | `message send --robot-code ... --users ...` | **只写**，无 list/get。需 PAT + `--robot-code`；通知优先用 `chat message send`（免 PAT） |
| drive | `list --limit 10`, `upload --file ...`, `delete --file-id ... -y` | 完整 CRUD，分页用 `--limit` |
| calendar | `event create/update/delete`, `event list/get`, `respond` | **完整 CRUD**，create/update 免 PAT，delete 需 PAT。支持循环日程、会议室 |
| attendance | `summary`, `record get` | `checkin records` 工具可能未开通 |
| report | `template list`, `create` | 创建可，**不可 API 删除**。8个模板 |
| aisearch | `person --query "..."`, `enterprise --query "..."` | person/enterprise/behavior 三维搜索 |
| chat | `list-top-conversations`, `message send --user ... --title ... --text ...` | **推荐做通知**：免 PAT，直接发单聊/群聊 |

### 分页参数不一致（核心坑点）

不同服务用不同分页参数名，需查阅 `--help` 确认：

| 参数 | 使用此参数的服务 |
|------|----------------|
| `--page-size` | doc、wiki、calendar |
| `--size` | devdoc、mail |
| `--limit` | drive |
| `--page` + `--size` | oa |
| 无分页参数 | hrmregister、minutes list（默认分页） |
