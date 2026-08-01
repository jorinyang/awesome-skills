# 骨架信号判读指南——从 AST 骨架识别架构模式

> 骨架只有签名/docstring/常量，但成熟项目的设计决策全藏在这三样里。本指南是"看到什么 → 说明什么"的速查表，沉淀自 N.E.K.O 精读（2026-07）。

## 1. 函数名前缀/动词 → 机制角色

| 签名模式 | 读出的机制 |
|---|---|
| `_decide_*_gate` / `*_entry_guard` | 守卫链（fail-closed 入口检查），如 `_decide_closed_activity_gate` → 活动感知闸门 |
| `_enter_*_phase2` / `phase1`/`phase2` | 两阶段架构（便宜筛选→昂贵生成），常带竞态复查 |
| `_should_skip_*` / `*_skip_probability` | 概率性跳过（反机械感/防打扰） |
| `*_half_life` / `*_decay` | 半衰期衰减（防重复/新鲜度权重） |
| `_is_similar_to_*` / `*_fingerprint` / `*_dedup` | 相似度/指纹去重（防复读） |
| `pause_dispatch` / `resume_dispatch` / `arbiter` | 队列仲裁器；若含"退回不消耗配额"语义注释 → 打断不罚设计 |
| `render_*_block` / `*_prompt_block` | 注入 system prompt 的渲染器（记忆/指令进入 LLM 的通道） |
| `check_feedback` / `confirm_*` / `reject_*` / `suppress*` | 反馈闭环（用户确认/否认驱动状态机） |
| `get_or_create` / `touch` / `expire` / `TTL` | 惰性过期会话管理 |
| `note_*` / `mark_*` / `record_*` | 事件埋点流（行为追踪→状态机输入） |

## 2. 模块 docstring → 架构宣言

成熟项目把设计铁律写在模块 docstring 第一句，精读时**先抄这些句子**：

- "No LLM, no external calls, every decision is keyword/threshold driven" → 该模块是纯规则引擎，零推理成本（可整套照搬的低成本方案）
- "Ordinary chat must never wait for X" → 主路径零等待铁律，X 全后台化
- "two-phase architecture" → 便宜模型筛选 + 昂贵模型生成的成本分层
- "fail closed" → 不确定时拒绝服务的安全姿态
- "Sync twin / async twin" → 生产热路径全异步化，同步版仅兼容

## 3. 顶层常量 → 产品调参（可直接作初始值）

配置/设置文件的常量是**被真实用户打磨过的数值**，比自己拍脑袋的初值可靠：

```python
# N.E.K.O proactive_settings.py 实例——每条都是产品决策：
MINI_GAME_INVITE_TRIGGER_PROBABILITY = 0.12        # 触发概率
MINI_GAME_INVITE_COOLDOWN_AFTER_ACCEPT_SECONDS = 2 * 3600   # 接受冷却 2h
MINI_GAME_INVITE_COOLDOWN_AFTER_DECLINE_SECONDS = 5 * 3600  # 拒绝冷却 5h
PROACTIVE_SOURCE_HALF_LIFE_DEFAULT = 3 * 86400.0   # 信源半衰期 3 天
EMOTION_ANALYSIS_MAX_TOKENS = 40                   # 情绪分析限 40 token
```

**判读要点**：
- **不对称冷却**（拒绝冷却 > 接受冷却）→ 尊重用户拒绝的产品哲学
- **半衰期默认值** → 内容新鲜度管理的量级参考
- **token 上限常量** → 成本控制的具体手法
- 状态机阈值常量（驻留秒数、GPU 百分比、切换次数）→ 行为判定的初始参数表

## 4. 测试文件名 → 设计规格

`tests/` 目录只做一件事：列出全部文件名。测试名是被验证过的需求清单：

| 测试名 | 规格 |
|---|---|
| `test_proactive_unanswered_repeat` | 主动消息未获应答时有重复策略 |
| `test_proactive_intent_label_leak` | 内部意图标签不得泄漏到用户可见文本 |
| `test_proactive_state_persistence` | 主动聊天状态需持久化（重启不丢） |
| `test_proactive_interval_20s_rollback` | 调度间隔曾改到 20s 后回滚——有节奏事故史 |
| `test_*_does_not_dehumanize` | 有人格一致性守门 |

 rollback/regress 类测试名尤其值钱——它们标记了**前人踩过的坑**。

## 5. 目录结构 → 子系统边界

- `contracts.py` / `types.py` → 该子系统有显式契约层（接口定义先读它）
- `_shared.py` / `_infra.py` → 私有共享层，说明模块是拆出来的（原是大文件重构）
- `workers/`（每 provider 一文件）→ 适配器矩阵，支持哪些 provider 一目了然
- `manager.py` + 多个 `mixin` 文件 → Mixin 组装模式，单一管理类多职责拆分
- `pipeline.py` / `service.py` / `delivery.py` 三件套 → 生产-编排-投递分层

## 6. 批量精读节奏建议

每批次一个主题、4~6 个文件，主题顺序：**入口编排 → 决策/状态 → 感知/配置 → 执行/适配 → 记忆/渲染**。每批结束立刻用自己的话写 3~5 条"机制提炼"再进下一批——防止骨架在眼前流过但没沉淀。
