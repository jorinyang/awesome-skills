# 专属技能中心（ExclusiveSkillHub）接入指南 摘要

> 来源：钉钉文档 `NZQYprEoWoxKPoqwCDx9KyymV1waOeDk`
> 对应组件：`packages/skills-ui/src/components/ExclusiveSkillHub.tsx`

## 入口逻辑

`SkillsPage` 调用 `host.useExclusiveSkillHubUrl()` 拉取后端配置。当 `skill_hub_url` 存在时渲染 `ExclusiveSkillHub`（iframe 模式），否则降级到默认 `SkillsTab`。

## 架构

```
SkillsPage (能力中心页)
└── ExclusiveSkillHub (专属模式入口)
    ├── <iframe src={resolvedUrl}> ← 企业技能中心 Web 页
    └── useSkillBridge ← 双向通信桥
        ├── postMessage 监听 (iframe → Host 请求)
        ├── postMessage 推送 (Host → iframe 事件)
        └── Tauri 事件转发 (skills:changed)
```

## SkillBridge 协议（TypeScript 类型）

```typescript
// packages/skills-ui/src/services/exclusive/skillBridge.types.ts

export type SkillBridgeMessage<T = any> = { action: string; payload: T };

export type SkillInfo = {
  skill_id: string; name: string; description: string;
  icon: string; is_installed: boolean; is_enabled: boolean;
};

export type SkillBridgeActions = {
  query_skills:      { request: { system_id: string; tenant_id: string }; response: { skills: SkillInfo[] } };
  install_skill:     { request: { skill_id: string }; response: { success: boolean; message: string } };
  enable_skill:      { request: { skill_id: string }; response: { success: boolean; message: string } };
  disable_skill:     { request: { skill_id: string }; response: { success: boolean; message: string } };
  open_task_create:  { request: { skill_id: string; task_id: string }; response: { success: boolean; message: string } };
  get_user_info:     { request: {}; response: { user_id: string; name: string; avatar: string } };
  open_url:          { request: { url: string }; response: { success: boolean; message: string } };
};
```

## 企业免登

`get_user_info` action 无需参数，宿主自动注入当前登录用户信息。iframe 页内无需实现登录逻辑。

## 关键约束

- iframe URL 通过 `resolvedUrl` 处理（支持模板变量注入，如 tenant_id）
- 通信实现见 `packages/skills-ui/src/hooks/useSkillBridge.ts`
- 宿主端技能变更通过 `skills:changed` Tauri 事件推送到 iframe
