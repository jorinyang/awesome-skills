# 考试系统架构参考

## 技术栈

| 层 | 技术 | 说明 |
|---|------|------|
| 前端 | 纯 HTML SPA (vanilla JS) | 无框架依赖，Apple Design 风格 |
| 后端 | Supabase (PostgreSQL + REST API) | RLS 控制权限，anon key 前端调用 |
| LLM | MiniMax API (MiniMax-Text-01) | 主观题评分 + 错题解析生成 |
| 部署 | 阿里云 OSS (clawshell-vault) | gzzhike.cn 域名，静态托管 |

## 关键设计决策

### 1. 客户端随机抽取 vs 数据库随机

选择**客户端随机**（fetch all → shuffle → slice）：
- 简单可靠，不依赖数据库函数
- Supabase REST API 没有原生 RANDOM() 支持
- 180题全量加载性能可接受（<50KB JSON）

### 2. Anon key + RLS vs Service key

选择**anon key + 宽松 RLS**：
- Service key 浏览器端被 CORS 拦截（HTTP 401）
- Admin 页面自身有密码保护层
- RLS 策略允许 anon 对题库/配置的完整 CRUD

### 3. LLM 评分 vs 关键词匹配

选择 **LLM 评分**：
- 简答题答案多样化，关键词匹配误判率高
- MiniMax API 响应快（<2s），成本低
- 提供评分理由，可作为错题解析

### 4. 学员认证

姓名 + 手机号匹配（非严格认证）：
- 允许重考（按 max_retakes 配置）
- 同姓名+手机号视为同一学员
- 适合内部培训场景，无需复杂账号系统

## 前端页面结构

### 学员端 (index.html) ~25KB

```
┌─ screen-login ─────────────────────┐
│  📝 AI培训考核                       │
│  姓名 [________]  手机 [________]  │
│  考试时间 60 分钟 · 共 28 题       │
│         [ 开始考试 ]               │
├─ screen-exam ──────────────────────┤
│  1/28  58:32   ●●●○○○ (导航点)    │
│  ┌─────────────────────────┐      │
│  │ 题目内容...              │      │
│  │ ○ A. 选项1              │      │
│  │ ● B. 选项2 (已选)       │      │
│  │ ○ C. 选项3              │      │
│  │ ○ D. 选项4              │      │
│  └─────────────────────────┘      │
│  [上一题]  [下一题]  [交卷]        │
├─ screen-loading ───────────────────┤
│  正在评分...                       │
├─ screen-result ────────────────────┤
│  🎉 85分 / 100分 (通过)           │
│  [查看错题解析]                    │
└────────────────────────────────────┘
```

### 后台管理 (admin.html) ~30KB

```
┌─ 登录弹窗 ─┐
│ 密码: ****  │
│ [登录]      │
├─────────────┴──────────────────────┤
│ 📝 考试管理      │  📊 数据概览     │
│ ├ 📊 数据概览    │  0 考试人次      │
│ ├ 📋 考试记录    │  0 平均分        │
│ ├ ❓ 题库管理    │  0% 通过率       │
│ └ ⚙️ 考试设置    │  181 题库总量    │
│                  │  [成绩分布图]    │
│                  │  [最近记录表]    │
└──────────────────┴─────────────────┘
```

## Supabase 凭证配置

前端 SPA 中硬编码（或从环境变量注入）：
```javascript
var SB_URL = 'https://mqsqcpkcmcgwbzcsmrlm.supabase.co';
var SB_KEY = 'sb_publishable_3pQRAq-R_5Ux9DS8bWHt3A_Kr0v4Dd0';  // anon key!
```

凭证完整信息：`~/.ClawShell/.env.supabase`

## LLM 评分 Prompt 模板

```
你是一位专业的企业培训考试评分专家。

【参考答案】{reference_answer}
【评分要点】{key_points}
【学员答案】{student_answer}

请根据参考答案和评分要点，对学员答案进行评分（0-100分）。
评分标准：
- 核心要点覆盖度（60%）
- 表述准确性（20%）
- 逻辑完整性（20%）

返回JSON格式：{"score": 分数, "feedback": "评语"}
```

Temperature: 0.3（低随机性，评分一致性优先）
