---
name: wukong-skill-center
description: 钉钉悟空企业技能中心集成——从技能仓库到 FC 路由服务的完整搭建管线。覆盖专属技能中心(SkillBridge iframe)和技能路由服务(HTTP API)两种模式。触发：悟空技能中心/企业技能中心/Wukong Skill Hub/技能路由/ExclusiveSkillHub/SkillBridge。
version: 1.0.0
author: 杨瑒 (月夜)
triggers:
  - 悟空技能中心
  - 企业技能中心
  - Wukong Skill Hub
  - 技能路由
  - 技能路由服务
  - ExclusiveSkillHub
  - SkillBridge
  - 钉钉悟空技能
  - 专属技能中心
tags: [wukong, dingtalk, skill-center, fc, oss, alibaba-cloud, agent-skill]
---

# Wukong 企业技能中心集成

> 将 Agent 技能（SKILL.md）接入钉钉悟空客户端的完整方案。两种模式：SkillBridge iframe（嵌入 Web 页）和 HTTP 路由服务（推荐）。

## 架构

```
钉钉悟空客户端
    │
    ├── 模式A: ExclusiveSkillHub ── iframe + postMessage ──▶ 企业技能中心 Web 页
    │
    └── 模式B: 技能路由服务 ── HTTP POST ──▶ FC 函数 ──▶ OSS (技能索引+zip包)
                                                    │
                                                    ▼
                                             GitHub (技能源码)
```

## 模式B：HTTP 路由服务（推荐）

### 悟空请求格式

```json
POST https://你的FC域名/skill-discover
{
  "keywords": ["周报"],
  "domain": null,
  "contextSummary": null
}
```

### 响应格式

```json
{
  "skills": [{
    "id": "weekly-report",
    "name": "weekly-report",
    "display_name": "周报助手",
    "description": "按周汇总项目进展并生成周报",
    "install_locicator": {
      "type": "remote_url",
      "url": "https://clawshell.online/wukong-skills/zips/weekly-report-v1.0.0.zip"
    }
  }]
}
```

### 搭建步骤（5 步）

1. **解析技能** — 扫描 GitHub 仓库中所有 `SKILL.md` → 提取 name/description/triggers/tags/version → 生成 `skills-index.json`
2. **打包上传** — 每个技能目录打为 .zip → OSS 公开可读 + 索引文件
3. **编写 FC 函数** — Python 3，纯标准库（urllib+json+re），从 OSS 加载索引，关键词匹配打分
4. **部署 FC** — 阿里云 FC (cn-hongkong, 256MB, Python 3, 30s timeout)，HTTP 触发器匿名访问
5. **配置钉钉** — 管理后台「技能中心配置」填入 FC 公网 URL

### 关键词匹配算法

多字段加权评分：
- 技能名精确匹配 → 30 分
- 技能名分词匹配 → 20 分
- display_name 匹配 → 15 分
- description 匹配 → 4-8 分
- triggers 匹配 → 6 分
- tags 匹配 → 5 分
- category 匹配 → 3 分

阈值 MIN_SCORE=0.2，最多返回 MAX_RESULTS=10 个技能。

### pitfalls

- **🔴 SkillBridge 消息格式（严格对齐协议，二次修正）**：
  - 协议类型 `SkillBridgeMessage = {action, payload}`——**不要**添加 `source`/`request_id` 等顶层字段
  - Host 通过 `event.source`（iframe.contentWindow）和 `event.origin` 过滤消息，**不看** `msg.source` 字段
  - ❌ 错误格式：`{source:'exclusive-skill-hub', request_id:1, action, payload}` → Host 拒绝
  - ✅ 正确格式：`{action, payload}` → Host 正常接收
  - 响应追踪：把 `_rid` 嵌入 payload 内，Host 回传时带回来：`payload._rid`
  - 监听 Host 消息：`if (!msg || !msg.action) return`，不要用 `msg.source === 'wukong-host'` 过滤
- **🔴 install_skill 安装失败根因**：
  - iframe 的 `install_skill` 只能安装悟空**已注册**的技能，企业自建技能不在注册表中 → 静默失败
  - 路由服务返回的技能通过 `install_locator.url` 安装，**与 iframe 的 `install_skill` 是两条独立链路**
  - 当前状态：iframe 安装对企业自建技能不可用，需要在悟空管理后台检查是否有「技能注册/上传技能包」入口
  - install_skill payload 建议附带 `install_locator`、`display_name`、`description` 作为协议扩展（Host 忽略多余字段不报错，但若支持则可直接安装）
  - 症状：响应体变成字面字符串 `"statusCodeheadersbody"`（Python dict 的 key 拼接），Content-Type 变成 `application/octet-stream`
  - 根因：`python3` runtime 下，返回 dict → FC 调用 `str(dict)` → 输出 dict key 拼接字符串
  - **第一次尝试**（失败）：直接返回 dict `{"skills": [...]}` → FC 仍把 dict 转成 key 拼接字符串
  - **第二次尝试**（失败）：返回 `json.dumps(result)` 字符串 → 函数正常，但 Content-Type 不是 `application/json`
  - **最终正确方案**：使用 `python3.10` runtime + **WSGI handler**，显式设置 Content-Type：
    ```python
    def handler(environ, start_response):
        result_json = json.dumps({"skills": matched}, ensure_ascii=False)
        status = "200 OK"
        headers = [("Content-Type", "application/json; charset=utf-8")]
        start_response(status, headers)
        return [result_json.encode("utf-8")]
    ```
  - **最终方案**：`python3.10` runtime + WSGI handler，显式 Content-Type；空查询返回示例技能防连通性测试失败
- **🔴 SkillBridge 消息格式（严格对齐协议）**：协议 `{action, payload}`，不加 `source`/`request_id`。Host 用 `event.source`/`event.origin` 过滤。响应追踪用 payload 内嵌 `_rid`
- **🔴 install_skill 失效根因**：iframe 只安装已注册技能，企业自建技能走路由服务的 `install_locator` 安装——两条独立链路
- **FC 更新 = 删光重建**：`DeleteTrigger`(204空body)→`DeleteFunction`(204空body)→`CreateFunction`→`CreateTrigger`
- **ACS3 签名 + FC 端点**: `fc.{region}.aliyuncs.com`
- **详情弹窗 ≠ 下载**：详情=modal 展示完整信息；安装=触发 install。卡片点击=详情
- **非 iframe fallback**: `window.open(url)`，`isInIframe = window.parent !== window`
- **执行原则**：不问直接做，遇凭证才停

### 管理后台配置项（管理员操作，非开发者）

| 配置项 | 位置 | 说明 |
|--------|------|------|
| HTTP 服务地址 | 企业技能路由服务 | FC 函数的公网 URL |
| 鉴权方式 | 鉴权配置 | 悟空自动附带鉴权信息 |
| 关闭默认推荐 | 开关 | 开启后只用企业技能 |
| 携带用户本地技能 | 开关 | 请求附用户已安装技能列表 |

## 模式A：SkillBridge iframe（进阶）

### 协议概述

悟空客户端通过 `<iframe>` 嵌入企业 Web 页，基于 `postMessage` 双向通信。

### 7 个 Action

| Action | 方向 | 参数 | 响应 |
|--------|------|------|------|
| `query_skills` | web→宿主 | `system_id`, `tenant_id` | `{skills: [{skill_id, name, description, icon, is_installed, is_enabled}]}` |
| `install_skill` | web→宿主 | `skill_id` | `{success, message}` |
| `enable_skill` | web→宿主 | `skill_id` | `{success, message}` |
| `disable_skill` | web→宿主 | `skill_id` | `{success, message}` |
| `open_task_create` | web→宿主 | `skill_id`, `task_id` | `{success, message}` |
| `get_user_info` | web→宿主 | 无 | `{user_id, name, avatar}` |
| `open_url` | web→宿主 | `url` | `{success, message}` |

### 宿主→iframe 事件

- `skills:changed` — 技能安装/启用/禁用状态变更时推送

### pitfalls

- **企业 Web 页必须 HTTPS**：iframe 嵌入要求安全上下文
- **postMessage origin 校验**：iframe 内需验证 `event.origin` 防止跨域攻击
- **技能中心 Web 页可托管 OSS**：静态 SPA，绑定自定义域名即可
- **🔴 安装/详情按钮无响应（非 iframe 环境静默失败）**：`hostCall()` 中 `window.parent === window` 判断后直接 `return false`，调用方未检查返回值 → 点击按钮无任何反馈。修复：启动时检测 `isInIframe = window.parent !== window`，非 iframe 时 `window.open(url)` fallback
- **install_skill payload 增强**：协议只有 `skill_id`，但 Host 可能无法定位安装源。附加 `install_locator` + `display_name` + `description` 字段——Host 忽略多余字段不影响，但若支持则可直接下载
- **企业免登**：收到 `host_ready` 事件后调用 `hostCallAsync('get_user_info')` 获取用户身份
- **钉钉管理后台验证**：后台"测试"按钮发 GET 请求，空查询需返回至少一个非空 skill（否则报"请检查服务地址是否正确"）。WSGI handler + python3.10 runtime 是唯一经验证能正确返回 `Content-Type: application/json` 的组合

## references

- `references/dd-docs-exclusive-skill-hub.md` — 钉钉官方文档：专属技能中心（ExclusiveSkillHub）接入指南摘要
- `references/dd-docs-skill-routing.md` — 钉钉官方文档：企业技能路由服务 HTTP 接入指南摘要
- `references/acs3-signing.py` — FC OpenAPI ACS3-HMAC-SHA256 签名客户端（FCClient 类，含 retry 逻辑）
- `references/category-mapping.md` — 技能分类映射表（96 技能 → 8 分类，对齐 GitHub README）
- `templates/fc-handler.py` — FC 路由服务 WSGI handler 模板（可直接部署）
- `scripts/build-and-upload.py` — 技能索引生成 + zip 打包 + OSS 上传脚本
