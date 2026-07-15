# 企业技能路由服务 HTTP 接入指南 摘要

> 来源：钉钉文档 `EpGBa2Lm8aZxe5myCEYl0K72WgN7R35y`

## 概述

专属悟空允许企业自建 HTTP 服务接管技能搜索与推荐。用户输入 query 时，悟空将请求转发到企业配置的 HTTP 地址。

## 开发者职责 vs 管理员职责

| 开发者需要做 | 管理员在后台配置 |
|-------------|----------------|
| 开发 HTTP POST 接口（接收 + 返回） | HTTP 服务地址填入 |
| 处理请求中的 keywords/domain/contextSummary | 鉴权方式选择 |
| 返回匹配的技能列表 | 关闭默认推荐技能 |
| — | 携带用户本地技能信息 |

## 请求格式

```json
POST /skill-discover
Content-Type: application/json

{
  "keywords": ["周报"],           // string[]  用户输入关键词
  "domain": null,                 // string|null  领域标识
  "contextSummary": null          // string|null  上下文摘要
}
```

## 响应格式

```json
{
  "skills": [{
    "id": "weekly-report",                    // string  唯一标识
    "name": "weekly-report",                  // string  技能名
    "display_name": "周报助手",               // string  展示名
    "description": "按周汇总项目进展并生成周报",  // string  描述
    "install_locator": {                      // object  安装定位器
      "type": "remote_url",                   // 目前仅 remote_url
      "url": "https://example.com/skills/weekly-report.zip"
    }
  }]
}
```

### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 技能唯一标识 |
| name | string | 技能内部名称 |
| display_name | string | 用户可见展示名 |
| description | string | 技能功能描述 |
| install_locator | object | `{type: "remote_url", url: "https://..."}` |

### install_locator

当前仅支持 `type: "remote_url"`，`url` 指向可公开下载的 .zip 包。
未来可能扩展 `marketplace` 等类型。

## 鉴权

- 开发者**不需要**在接口中实现鉴权
- 管理员在「鉴权配置」中选择方案（如签名验证）
- 悟空会自动在 HTTP 请求头中附带鉴权信息

## 部署要求（文档未明确规定，建议值）

| 参数 | 建议值 |
|------|--------|
| 超时 | 10-30s |
| 并发 | 按 FC 自动弹性 |
| 错误处理 | 返回 `{"skills": []}` 而非 5xx |
| 协议 | HTTPS（必须） |
