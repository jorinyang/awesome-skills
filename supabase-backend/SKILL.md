---
name: supabase-backend
description: Supabase 作为 SPA 后端数据层——项目初始化、建表、RLS 策略、前端 JS SDK 集成。适用于需要免费 PostgreSQL 后端的 Web 应用。
version: 1.3.0
triggers:
  - supabase
  - 后端方案
  - 数据库
  - postgresql 后端
  - 数据持久化
  - 多人共享数据
  - SPA 后端
related_skills: [feishu-html, trip-landing, double-evolution]
---

# Supabase Backend — SPA 数据层最佳实践

## 定位

Supabase 是零运维 PostgreSQL 后端，适合作为纯前端 SPA 的数据层——替代 localStorage、OSS JSON、自建代理等方案。

| 对比 | localStorage | OSS JSON + 代理 | Supabase |
|------|:-----------:|:-------------:|:--------:|
| 多人共享 | ❌ | ⚠️ 需代理 | ✅ 原生 |
| 部署复杂度 | 无 | 中 | 低 |
| 成本 | ¥0 | ¥0 | ¥0 (500MB) |
| 实时同步 | ❌ | ❌ | ✅ |

## 触发条件

- 需要 SPA 多人共享数据
- localStorage/OSS JSON 方案无法满足
- 用户提到 Supabase / PostgreSQL 后端
- 需要免费数据库后端的任何 Web 项目

## 凭据体系（必读）

Supabase 有 **四层凭据**，初学者最容易混淆：

| 凭据 | 格式 | 用途 | 安全级别 |
|------|------|------|---------|
| **Publishable Key** | `sb_publishable_...` | 前端 JS SDK 初始化 | 公开（可嵌入 HTML） |
| **Anon Key** (旧) | `eyJhbG...` (JWT) | 前端 JS SDK（旧格式） | 公开 |
| **Service Key** | `sb_secret_...` | 服务端 API 调用 | 保密 |
| **PAT** | `sbp_...` | Management API / CLI | 保密 |
| **DB Password** | 任意字符串 | 直连 PostgreSQL | 保密 |

### 关键误区

- **Publishable key ≠ Service key**：前者只能做 RLS 允许的操作，后者有管理员权限
- **PAT 不能替代 Service key**：PAT 用于管理项目，Service key 用于操作数据
- **PAT 有 scope 限制**：创建时选择 read/write/admin 范围，可能无法执行某些操作
- **`sb_secret_...` 不是 DB password**：它是 REST API key，不能用于 psycopg2 连接

## 项目发现

如果用户已有 Supabase 项目，按优先级查找凭据：

```bash
# 1. 显式 .env 文件
cat ~/workspace/.env.supabase

# 2. Supabase CLI 配置
cat ~/workspace/supabase/config.toml | grep project_id

# 3. 临时文件（项目引用）
cat ~/workspace/supabase/.temp/project-ref
cat ~/workspace/supabase/.temp/pooler-url

# 4. 自定义客户端文件
grep -r "supabase.co" ~/workspace/

# 5. 用 PAT + CLI 列出项目
SUPABASE_ACCESS_TOKEN=*** supabase projects list
```

## 建表：两条路径

### 路径 A：直连 PostgreSQL（推荐）

**适用**：有 DB password，可以做任何 DDL。

```python
import psycopg2

conn = psycopg2.connect(
    host="aws-0-us-west-2.pooler.supabase.com",
    port=6543,
    user="postgres.{project_ref}",
    password="{db_password}",
    dbname="postgres",
    connect_timeout=10
)
cur = conn.cursor()

# 建表
cur.execute("""CREATE TABLE IF NOT EXISTS workshops (
  id TEXT PRIMARY KEY,
  round_number INTEGER NOT NULL,
  date TEXT NOT NULL
)""")

# 必须做的三件事：
# ① 开启 RLS
cur.execute("ALTER TABLE workshops ENABLE ROW LEVEL SECURITY")
# ② 创建策略（公开读写）
cur.execute("CREATE POLICY all_workshops ON workshops FOR ALL USING (true) WITH CHECK (true)")
# ③ 授权 schema
cur.execute("GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role")
cur.execute("GRANT ALL ON workshops TO anon, authenticated, service_role")
conn.commit()
```

### 路径 B：Management API（需 PAT）

**适用**：没有 DB password，有 PAT。

```python
# ⚠️ 部分 PAT 可能被 scope 限制，返回 403 error 1010
url = f"https://api.supabase.com/v1/projects/{ref}/query"
req = urllib.request.Request(url, data=json.dumps({"query": sql}).encode(), method='POST')
req.add_header('Authorization', f'Bearer {pat}')
```

**注意**：PAT 在 CLI 中可能正常工作（`supabase projects list`），但 Management API 返回 403。这是 scope 问题，不是 token 格式问题。

### RLS 策略模板

```sql
-- 公开读写（社区工具、内部应用）
CREATE POLICY "all_access" ON workshops FOR ALL USING (true) WITH CHECK (true);

-- 仅认证用户
CREATE POLICY "auth_access" ON workshops FOR ALL 
  USING (auth.role() = 'authenticated') 
  WITH CHECK (auth.role() = 'authenticated');

-- 仅拥有者（配合 auth.uid()）
CREATE POLICY "owner_access" ON topics FOR ALL 
  USING (auth.uid() = user_id) 
  WITH CHECK (auth.uid() = user_id);

-- 公开读 + 认证写
CREATE POLICY "public_read" ON topics FOR SELECT USING (true);
CREATE POLICY "auth_insert" ON topics FOR INSERT WITH CHECK (auth.role() = 'authenticated');
```

**容易漏掉的**：
- `GRANT USAGE ON SCHEMA public TO anon, authenticated` — 漏掉 → 401
- `GRANT ALL ON {table} TO anon, authenticated` — 漏掉 → 403
- 外键 `REFERENCES ... ON DELETE CASCADE` — 删父记录时自动清理子记录

## 种子用户创建（phone+password 模式）

当 Auth 方案是「手机号+密码」且不需要 SMS 验证码时，用直接 SQL 创建用户最快：

```python
import psycopg2, uuid, json

conn = psycopg2.connect(host=HOST, port=PORT, user=USER, password=PW, dbname='postgres')
cur = conn.cursor()

users = [
    ("张三", "13800000001", "supervisor", "dept_green"),
    ("李四", "13900000001", "worker", "dept_green"),
]

for name, phone, role, dept in users:
    uid = str(uuid.uuid4())
    email = f"{phone}@wf.internal"  # ← phone 转 email 的关键
    meta = json.dumps({"name": name, "role": role})
    dept_v = f"'{dept}'" if dept else 'NULL'

    # ① 写入 auth.users（pgcrypto 加密密码）
    cur.execute("""
        INSERT INTO auth.users (id, instance_id, email, phone, encrypted_password,
            email_confirmed_at, phone_confirmed_at, raw_app_meta_data, raw_user_meta_data,
            created_at, updated_at, aud, role)
        VALUES (%s, '00000000-0000-0000-0000-000000000000', %s, %s,
            crypt('88888888', gen_salt('bf', 6)), now(), now(),
            '{"provider":"phone","providers":["phone"]}', %s,
            now(), now(), 'authenticated', 'authenticated')
        ON CONFLICT DO NOTHING
    """, (uid, email, phone, meta))

    # ② 写入 app_users（业务用户表）
    cur.execute(f"""
        INSERT INTO app_users (id, name, phone, role, department_id)
        VALUES ('{uid}', '{name}', '{phone}', '{role}', {dept_v})
        ON CONFLICT (id) DO NOTHING
    """)

conn.commit()
```

**前端登录**（用户无感知 email 转换）：

```jsx
// AuthContext.jsx
async function login(phone, password) {
  const email = `${phone}@wf.internal`
  const { data, error } = await supabase.auth.signInWithPassword({ email, password })
  if (error) throw error
  // 加载 app_users profile
  const { data: profile } = await supabase.from('app_users')
    .select('*, departments:department_id(name)')
    .eq('id', data.user.id).single()
  return { ...data, profile }
}
```

**要点**：
- `{phone}@wf.internal` 的后缀任意，只要不冲突真实邮箱
- `encrypted_password` 必须用 `crypt()` + `gen_salt('bf', 6)` —— 实测 `gen_salt('bf', 10)` 的成本过高，Supabase Auth 验证时会报 `Invalid login credentials`。`bf,6` 兼容所有版本。`bf,10` 仅在使用 Admin API 创建的用户上可用
- `ON CONFLICT DO NOTHING` 防止 Admin API 和 SQL 双重创建时的重复键冲突
- 若 pgcrypto 扩展未安装：`CREATE EXTENSION IF NOT EXISTS pgcrypto`

## 前端集成

### 标准初始化

```html
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"></script>
<script>
// ⚠️ 必须等待 SDK 加载：CDN 脚本可能比 inline script 慢
(function waitForSupabase(){
  if(!window.supabase){setTimeout(waitForSupabase,100);return}
  
  const sb = window.supabase.createClient(
    'https://{project_ref}.supabase.co',
    'sb_publishable_...'  // ← 用 publishable key，不是 secret key
  );
  
  // 查询
  const {data, error} = await sb.from('workshops').select('*').order('date', {ascending: false});
  
  // 插入
  await sb.from('workshops').insert({id: uid(), round_number: 1, date: '2026-08-01'});
  
  // 更新
  await sb.from('workshops').update({date: '2026-09-01'}).eq('id', workshopId);
  
  // 删除
  await sb.from('workshops').delete().eq('id', workshopId);
})();
</script>
```

### 前端陷阱

| 陷阱 | 症状 | 修复 |
|------|------|------|
| CDN 加载时序 | `window.supabase is undefined` | IIFE 轮询等待 `window.supabase` |
| 用错 key | `Invalid API key` (401) | 前端用 publishable key，不是 secret key |
| 漏掉 RLS | 查询返回空 `[]` | `ENABLE ROW LEVEL SECURITY` + `CREATE POLICY` |
| 漏掉 GRANT | 401/403 | `GRANT USAGE` + `GRANT ALL` |

### 多用户投票模式

```javascript
// 每个浏览器唯一 ID
let voterId = localStorage.getItem('voter_id');
if(!voterId) { voterId = 'v_' + Math.random().toString(36).slice(2,10); localStorage.setItem('voter_id', voterId); }

// 投票 toggle：检查 voterId 避免重复
const existing = votes.find(v => v.topic_id === topicId && v.voter_id === voterId);
if(existing) await sb.from('votes').delete().eq('id', existing.id);
else await sb.from('votes').insert({topic_id: topicId, voter_id: voterId});
```

### 实时同步

```javascript
// 简单轮询（15 秒间隔即可）
setInterval(loadAll, 15000);

// 或 Supabase Realtime（WebSocket，更省资源）
sb.channel('public:workshops')
  .on('postgres_changes', {event:'*', schema:'public'}, payload => loadAll())
  .subscribe();
```

## 完整工作流（从零到上线）

```
1. 注册/登录 supabase.com
2. 创建项目 → 获取 URL + publishable key
3. 建表：直连 PG 或 Management API
4. 配 RLS 策略 + GRANT 权限
5. 前端集成：init → select → insert → update → delete
6. 部署 HTML 到 OSS（调用 feishu-html 技能，或直接参考 `references/oss-deploy.md`）
```

### 重建/清空数据库

当用户说「删除重建，不保留数据」时：

```python
import psycopg2

conn = psycopg2.connect(
    host=env['SUPABASE_DB_HOST'],
    port=env['SUPABASE_DB_PORT'],
    user=env['SUPABASE_DB_USER'],
    password=env['SUPABASE_DB_PASSWORD'],
    dbname='postgres',
    connect_timeout=10
)
cur = conn.cursor()

# 1. 删除所有自定义表（CASCADE 处理外键依赖）
cur.execute("""
    DO $$ DECLARE r RECORD;
    BEGIN
        FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname='public') LOOP
            EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(r.tablename) || ' CASCADE';
        END LOOP;
    END $$;
""")

# 2. 清空 auth.users（如有测试用户）
cur.execute("DELETE FROM auth.users")

# 3. 清除 Storage 桶（如有）
cur.execute("DELETE FROM storage.objects")

conn.commit()
cur.close()
conn.close()
```

**注意**：`DROP ... CASCADE` 会连带删除依赖该表的所有 RLS 策略、触发器、索引。重建后必须重新 `ENABLE ROW LEVEL SECURITY` + `CREATE POLICY` + `GRANT`。

## 与已有技能配合

```
feishu-html（部署管道）
  └── 可选后端：supabase-backend（推荐）或 OSS JSON
        └── supabase-backend（本技能）提供数据层
  
trip-landing（行程落地页）
  └── 报名表单 → supabase-backend 收集数据
```

---

## 踩坑记录

| # | 陷阱 | 症状 | 根因 | 正确做法 |
|---|------|------|------|---------|
| 1 | PAT + Management API 403 | `error code: 1010` | PAT scope 不足 | 用 DB password 直连 PG |
| 2 | PAT CLI 可用但 API 不可用 | `projects list` 正常，API 403 | CLI 和 API 认证路径不同 | 优先用 DB password |
| 3 | `.env` 文件凭据被截断 | `sb_sec...inwW` | 文件内写了 `...` 省略 | 从 Supabase Dashboard 重新获取 |
| 4 | `sb_secret_...` 当 DB password 用 | `FATAL: password authentication failed` | Service key ≠ DB password | 在 Dashboard 看 Database 密码 |
| 5 | CDN 脚本未加载完就调用 | `window.supabase is undefined` | inline script 先于 CDN 执行 | IIFE 轮询等待 |
| 6 | Publishable key 写成 Service key | `Invalid API key` (401) | 前端用了 secret key | 前端只用 publishable key |
| 7 | RLS 开启但未建策略 | 查询返回空数组 `[]` | 默认拒绝所有访问 | `CREATE POLICY ... USING (true)` |
| 8 | 建表后未 GRANT | 401/403 | anon 角色无 schema 权限 | `GRANT USAGE` + `GRANT ALL` |
| 9 | Supabase CLI 版本过旧 | 部分命令不可用 | v2.15.8 → v2.105.0 | `supabase update` 或 `npm update -g supabase` |
| 10 | `supabase db push` 交互式密码 | 脚本中无法自动输入 | 命令行交互 prompt | 用 psycopg2 直连 PG 替代 |
| 11 | 发现已有表（上次会话残留） | 建表 SQL 报 `relation already exists` | 之前会话或手动操作留下部分 schema | 先用 `information_schema.tables` 摸底，确认 schema 差异后问用户：删除重建/保留改造/只增不改 |
| 12 | RLS 策略冲突：INSERT 被 SELECT 策略阻塞 | `new row violates row-level security policy`，即使 INSERT 策略 `WITH CHECK (true)` | `get_user_role()` 函数中 `auth.uid()::text` 在匿名用户时为 NULL，虽然 `COALESCE` 兜底但 SECURITY DEFINER 上下文中可能抛异常。且 `FOR SELECT USING(get_user_role()=...)` 策略的 `USING` 子句在 INSERT 时也会被评估 | **修复函数**：`CASE WHEN auth.uid() IS NULL THEN 'anon' ELSE COALESCE(...) END`。**修复策略**：INSERT 策略显式 `FOR INSERT TO anon, authenticated`，不使用 `roles=['public']`。SELECT/UPDATE 策略的 USING 中先判断 `auth.uid() IS NOT NULL` |
| 13 | Supabase Admin API 批量创建用户超时 | `urllib.request.urlopen` 30s 无响应 | `/auth/v1/admin/users` 对网络延迟敏感，批量请求可能半途中断（部分用户创建成功，app_users 未写入） | 优先用 **直接 SQL 插入 auth.users**：`INSERT INTO auth.users (...) VALUES (..., crypt('password', gen_salt('bf',10)), ...)` 配合 pgcrypto。API 只作为备选。批量创建后务必检查 `auth.users` 和 `app_users` 行数是否一致 |
| 14 | 手机号+密码登录：Supabase Auth 不支持原生 phone+password | `signInWithPassword` 要求 email 字段，直接用 phone 报错 | Supabase JS SDK `signInWithPassword({ phone, password })` 在 v2 未完全支持 phone 标识符 | 用 `{phone}@wf.internal` 作为 email 注册。前端登录时自动拼接 `@wf.internal` 后缀。用户完全无感知——只输入手机号 |
| 15 | DDL: `text NOT NULL` 列无 DEFAULT，REST API INSERT 报错 | PostgREST 不自动生成 UUID，显式传 NULL 覆盖 DEFAULT → `null value in column "id" violates not-null constraint` | TEXT PRIMARY KEY 列没有 `DEFAULT gen_random_uuid()::text` | **建表时必须** `ALTER TABLE x ALTER COLUMN id SET DEFAULT gen_random_uuid()::text`。或前端插入时手动 `crypto.randomUUID()`。⚠️ 与之相关的坑 #23 是 JS SDK 端的静默失败表现 |
| 16 | 触发器从 REST API 无法写入通知表 | 触发器函数默认 SECURITY INVOKER，继承 anon/authenticated 的权限，无 INSERT 权限 | 函数未声明 `SECURITY DEFINER`，notifications 表也未 GRANT INSERT | ① `ALTER FUNCTION notify_xxx() SECURITY DEFINER` ② 或 `GRANT INSERT ON notifications TO anon, authenticated`。推荐两者都做 |
| 17 | pg_net 扩展未安装导致 `net.http_post` 不可用 | `function net.http_post() does not exist` | Supabase 项目默认不启用 pg_net | `CREATE EXTENSION IF NOT EXISTS pg_net`。若权限不足，用 psycopg2 直连 PG（pooler 端口 6543）执行。安装后即可从触发器内调用 HTTP API |
| 18 | React: 派单时工人列表为空（跨部门） | 主管打开其他部门的工单，派单下拉无工人可选 | `loadWorkers()` 用 `useAuth().departmentId`（主管自己的部门）而非 `order.department_id`（工单的部门）筛选 | ① `loadWorkers()` 在 `loadOrder()` 内部调用，用 fetch 返回的 `data.department_id` 而非 React state 中的 `order?.department_id`。② 不要将 `loadWorkers()` 放在与 `loadOrder()` 并行的 useEffect 中——state 尚未更新时 `order` 为 null。详见 `references/react-dispatch-pitfall.md` |
| 19 | 匿名工单(无部门ID)导致派单按钮不显示 + 工人列表为空 | 部分 pending 工单有派单按钮，部分没有；或管理员也选不了工人 | `department_id IS NULL` → `null === deptId` = false → `isMyDept` 失败；工人列表过滤 `eq('department_id', null)` 返回空 | `const isMyDept = !order.department_id \|\| order.department_id === departmentId`；工人列表无部门时加载全部。详见 `references/react-dispatch-pitfall.md#扩展` |
| 20 | pg_net 触发器中 HTTP 异常回滚整个事务 | INSERT 报 404，错误信息显示 `function net.http_post does not exist`，且业务数据（工单/通知）也未写入 | `net.http_post()` 抛异常未被捕获 → 触发器事务回滚 → PostgREST 返回 404 + 数据未写入 | ① `CREATE EXTENSION IF NOT EXISTS pg_net` ② 触发器内用 `BEGIN...EXCEPTION WHEN OTHERS THEN` 包裹 HTTP 调用 ③ 设 `timeout_milliseconds := 8000`。详见 `references/pg-net-webhook.md` |
| 21 | Management API SQL 端点返回 Cloudflare 1010 | `POST /v1/projects/{ref}/query` → 403 error 1010；但 CLI `projects list` 正常 | Cloudflare WAF 根据 TLS fingerprint 区分 CLI (Go) 和脚本 (Python/curl) 流量，对后者返回 1010 拦截 | **用 psycopg2 直连 Pooler**（IPv4 解析 → port 6543）。Go CLI 因 SASL 不兼容特殊字符密码也不可用。详见 `references/cli-sql-execution.md` |
| 22 | DB 主机仅 IPv6，服务器仅 IPv4 | `db.{ref}.supabase.co` 解析无 IPv4 记录 → `dial error: network is unreachable` | Supabase 直连 PG 使用 IPv6-only 地址 | 必须通过 Pooler 连接（`aws-0-{region}.pooler.supabase.com:6543`），Pooler 有 IPv4。详见 `references/cli-sql-execution.md` 踩坑 #3 |
| 23 | Supabase JS SDK: `text NOT NULL` 列无 DEFAULT，insert 静默失败 | 前端 insert 不报错但数据未写入；通知/webhook 未触发 | ① `id` 列类型为 `text`（非 `uuid`），JS SDK 不会自动生成 text 类型的主键值 ② insert 对象中未包含 `id` 字段 ③ Postgres 拒绝 NULL 值 ④ 前端 try-catch 或 fire-and-forget 调用吞掉了错误 | **建表后必须** `ALTER TABLE x ALTER COLUMN id SET DEFAULT gen_random_uuid()`。批量检测和修复脚本见 `references/batch-fix-id-defaults.md`。诊断时直连 PG 做无 id 的测试 INSERT 验证。注意：此 bug 对下游影响严重——无通知 → webhook 触发器永不触发 → 外部平台收不到推送 |
| 24 | **pg_net v0.19.5 `body` 参数类型不匹配** | 触发器不报错但 webhook 未发送；pg_net 队列为空；`SELECT net.http_post(...)` 直接调用能工作但触发器内不行 | 旧版 pg_net 的 `http_post(body text)` 已改为 `http_post(body jsonb)`。触发器函数中 `payload TEXT` + `body := payload` 编译为 `body => text`，PG 找不到匹配签名 → 被 EXCEPTION 静默吞掉 | **声明 `payload JSONB`，用 `::jsonb` 转换。** 诊断：临时删除 EXCEPTION 块，看真实错误 `function net.http_post(body => text) does not exist`。详见 `references/pg-net-webhook.md` |
| 25 | **通知重复推送：三层重复** | 一次工单操作收到 3~N 条钉钉消息（N=管理员数） | ① **重复触发器**：`trg_wo_notify` + `trg_notify_wo_change` 调用同一函数（同理 `trg_mr_notify` + `trg_notify_mr_change`） ② **前端重复**：Detail.jsx/Report.jsx/MaterialRequests.jsx/CheckList.jsx 的 `createNotification()` 与 DB 触发器重复插入 ③ **N×扩展**：DB 触发器按用户循环 `INSERT INTO notifications`，`trg_push_webhook` 监听每行 → 每个管理员一条 webhook | ① 删重复触发器 → 每表保留 1 个 ② 前端移除所有工作流通知调用 → 只保留非业务事件（inventory_alert/inspection_repair/inspection_damage） ③ DB 触发器内先调 `send_webhook()` 一次，再插按用户通知行 ④ `push_to_webhook()` 跳过 already-handled 类型。详见 `references/notification-architecture.md` |
| 26 | **localStorage 分类与页面未同步** | 管理员后台新增分类后，库存页面的分类标签/下拉仍是旧的硬编码列表 | Admin Config 页将分类写入 `localStorage`（如 key=`material_categories`），但功能页面（库存）有独立的硬编码常量数组，不读 localStorage | **单一数据源**：功能页每次渲染直接从 localStorage 读取同一 key（`loadMaterialCats()`），不声明模块级常量。方案：`const cats = loadMaterialCats()` 放在组件体内（非 `useMemo(()=>loadMaterialCats(),[])` 否则只会读取一次）。硬编码列表作为 fallback 即可 |
| 27 | **pg_net queue 中 body 列为 memoryview** | `json.loads(body)` 报 `the JSON object must be str, bytes or bytearray, not memoryview` | `net.http_request_queue.body` 列类型为 `bytea`，psycopg2 返回 `memoryview` 对象 | `raw = bytes(body).decode('utf-8')` 先转为 bytes 再 decode。也可用 `body::text` 但 bytea→text 转义会破坏 JSON |

## 通知触发器

业务事件驱动的站内通知可以用 PostgreSQL 触发器零成本实现——状态变更时自动 INSERT 到 `notifications` 表，前端 30s 轮询。详见 `references/notification-triggers.md`。

如果通知需要**同时推送到外部平台**（钉钉/飞书），使用 `pg_net` 扩展的 `net.http_post()` 在同一个触发器内完成。详见 `references/pg-net-webhook.md`。

**⚠️ 单一数据源原则**：工单/申领/盘点状态变更通知由 DB 触发器统一管理，前端只做 CRUD。DB 触发器内先调用 `send_webhook()` 一次再插按用户通知行，避免 N×webhook 爆炸。详见 `references/notification-architecture.md` 和 `references/send-webhook-helper.md`。

每条通知应包含该环节的关键业务信息（地点、接单人、类别、评分等）。完整模板映射见 `references/notification-templates.md`。

修改 webhook 格式后务必全量验证。完整测试方法和 14 种模板清单见 `references/testing-webhook-templates.md`。

批量修复多张表 `id` 列无 DEFAULT 的问题，使用 `references/batch-fix-id-defaults.md` 中的检测与一键修复脚本。

## 环境依赖

- `psycopg2-binary` — 直连 PostgreSQL
- `supabase` CLI — 项目管理（可选）
- Supabase JS SDK — 前端（CDN 引入，无需安装）

## 凭据文件

项目凭据（URL、Key、PAT、OSS 等）集中在 `references/credentials.md`。新项目启动时先从该文件获取凭据。
