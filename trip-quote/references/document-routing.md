# 贵州之客文档路由规则

> 建立于 2026-06-22 工作流骨架构建会话。所有 travel 技能必须遵守。

## 核心规则

| 受众 | 格式 | 技术路径 | 分发 |
|------|------|---------|------|
| **客户** | PDF | HTML 模板 → Playwright `page.pdf()` | 微信/企微发送 |
| **供应商**（酒店/车辆/地接） | PDF | HTML 模板 → Playwright `page.pdf()` | 微信发送 |
| **内部**（计调/导游/运营） | 飞书 docx | Markdown → `lark-cli docs +create --doc-format markdown` | 链接分享 |

## 不做什么

- 不对客发飞书链接 — 客户不是飞书用户
- 不对内发 PDF — 内部需要协作编辑
- 不在报价单显示利润 — 利润在 cost-engine 中管理

## 产出清单

| 技能 | 产出 | 路由 |
|------|------|------|
| trip-quote | 报价单 | → PDF → 客户 |
| trip-briefing | 出团通知书 | → PDF → 客户 |
| guide-exec | 导游执行单 | → 飞书 docx → 03-出团执行 |
| supply-check | 物资核对 | → 飞书 docx → 03-出团执行 |
| vendor-brief | 供应商对接×3 | → PDF → 酒店/车辆/地接 |
| cost-engine | 成本核算 | → 飞书 docx → 01-产品研发 |
| trip-archive | 归档报告 | → 飞书 docx → 05-归档结算 |

## 飞书文档创建模式

```bash
# 必须使用相对路径（cd 到文件所在目录）
cd /tmp
lark-cli docs +create --api-version v2 --doc-format markdown \
  --content @file.md --parent-token <wiki_node_token> --as bot
```

### 陷阱

- `--content` 只接受相对路径，传绝对路径报 `unsafe file path`
- 标题写在 markdown 第一行 `# Title`，不用 `--title`（v2 已废弃）
- `--as bot` 创建后自动授予当前用户 full_access
- 创建后验证：`docs +fetch` 确认 `revision_id > 1`
- Wiki 节点创建用 `--as bot` 当 user 缺少 `wiki:node:create` scope

## 知识库节点映射

| 节点 | token | 归档内容 |
|------|-------|---------|
| 01-产品研发 | XysVwyHOmiOOstkCjj9cXDBlnQb | 成本核算、路线方案 |
| 02-销售转化 | Rcdow4tcRiYL88kwCZDcjNw8nBf | 报价单、合同 |
| 03-出团执行 | HmnBwlKhsixk45kjNa9cmCRDndb | 导游执行单、物资核对 |
| 04-供应商对接 | HbYIw1R93ihXRFkwgZ5cPmWnneb | 酒店/车辆/地接对接单 |
| 05-归档结算 | KuyvwJWGki1D7vkBslWchymWn2f | 团后总结、财务结算 |
