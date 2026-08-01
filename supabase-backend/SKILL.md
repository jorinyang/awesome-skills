---
name: supabase-backend
description: Supabase 作为 SPA 后端数据层——项目初始化、建表、RLS 策略、前端 JS SDK 集成。适用于需要免费 PostgreSQL 后端的 Web 应用。
version: 1.4.1
triggers:
  - supabase
  - 后端方案
  - 数据库
  - postgresql 后端
  - 数据持久化
  - 多人共享数据
  - SPA 后端
related_skills: [feishu-html, trip-landing]
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
# 1. 显式 .env 文件（Linux/Mac）
cat ~/workspace/.env.supabase

# Windows 主机实际路径（实测，本会话验证可用）
cat /c/Users/<user>/.ClawShell/.env.supabase   # 主凭据库：URL/Key/PAT/DB_PASSWORD/Pooler 全套
cat /c/Users/<user>/workspace/.env.supabase    # 备用副本

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

**多应用共享一个 Supabase 项目时**，表名必须加应用前缀（如 `pm_users`、`quiz_questions`），避免与已有应用的表冲突或语义混淆。前缀即命名空间，前端 REST 路径同步带前缀，RLS 策略名也加前缀。

**凭据冲突处理**：用户口头提供的 DB password 可能与凭据文件不一致（用户记错）。两个都试一次，以能连通 Pooler 的为准——实测凭据文件中的密码优先级高于用户记忆。找到正确密码后不要追问，继续执行。

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

## 轻量级应用层认证（无 Supabase Auth）

内部工具/小团队应用**不必走 auth.users**。直接在业务表存用户名+哈希密码，前端校验——省掉 Auth 配置、email 伪装、RLS 角色判断的整套复杂度。适用：项目管理、看板等低敏感度内部协作工具（实测于 pm_ 前缀项目管理系统，4 用户场景）。

**建表 + 哈希函数**：

```sql
CREATE TABLE app_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  display_name TEXT NOT NULL,
  role TEXT DEFAULT 'member'
);

CREATE OR REPLACE FUNCTION app_hash_password(pw TEXT)
RETURNS TEXT AS $$
BEGIN
  RETURN encode(digest(pw || 'app_salt_constant', 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 种子用户
INSERT INTO app_users (username, password_hash, display_name)
VALUES ('admin', app_hash_password('admin123'), '管理员');
```

**前端登录**（Web Crypto API 复算哈希，与 DB 比对，零 SDK 依赖）：

```javascript
const rows = await fetch(API + '/app_users?username=eq.' + encodeURIComponent(username),
  { headers: { apikey: SB_KEY } }).then(r => r.json());
const buf = await crypto.subtle.digest('SHA-256',
  new TextEncoder().encode(password + 'app_salt_constant'));
const hex = [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
if (rows.length && hex === rows[0].password_hash) {
  // 登录成功：profile 存 localStorage，前端路由守卫控制权限
}
```

**注意**：① anon key 下 `password_hash` 列可被读——内部低敏感工具可接受，敏感系统仍需 Supabase Auth；② 权限控制在应用层做（role 字段 + 前端守卫），RLS 用 `USING (true)` 即可；③ salt 常量在 SQL 函数和前端 JS 中必须完全一致；④ 密码 hash 验证可离线比对——先 `crypto.subtle.digest` 复算再与查询结果比对，无需调 Auth API。

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
| 28 | **Pooler 连接下单条 INSERT 极慢** | 448 条数据插入耗时 60s+ | 单条 INSERT 经 Pooler 延迟 ~100ms/条 | 用 `execute_values` 批量插入，448 条 → <2s |
| 29 | **DELETE 后 INSERT 仍报 UNIQUE 冲突** | `UniqueViolation: duplicate key` 但确认已 DELETE | Pooler 连接下 `c.commit()` 可能静默不提交 DELETE | `c.autocommit = True`；DELETE 后立即 `SELECT count(*)` 验证 |
| 30 | **CDN SDK 全局变量不可用** | 页面空白/登录失败，`window.supabase` 始终 undefined | jsDelivr CDN 在某些网络环境下加载失败，或 UMD build 没有正确暴露全局变量 | 完全绕过 SDK，用原生 `fetch()` 直接调 Supabase REST API（见下文「无 CDN SDK 的 fetch 模式」） |
| 31 | **一行多段座位号 UNIQUE 冲突** | 同一排有 1-9 和 21-29 两段 → UNIQUE 约束报错 | row_configs 表 UNIQUE(zone_id, row_number) 不允许同一排号出现两次 | 移除该 UNIQUE 约束；用 `DELETE + INSERT` 替换 UPDATE（非 idempotent） |
| 32 | **前端 COUNT 查询 limit 截断** | 统计数据不准（6272 行只读了 5000） | `select`+`limit` 取回行数不足 | 用 `Prefer: count=exact` 请求头 + `limit=0`，解析 `content-range` 头获取精确行数，不拉取任何数据行 |
| 33 | **bookings 按演出日期过滤需做两次查询** | bookings → seats → shows 跨三层关系，REST API 不能直接在 bookings 上加 `seats.shows.date=eq.X` 过滤 | Supabase REST API 的嵌入式过滤不支持跨三层关系 | 先查 `shows.date=X` 获取 show_id → 查 seats 获取 seat_ids → 用 `seat_id=in.(...)` 过滤 bookings。对数据量小的场景可用 `select=*,seats(*,shows(*))` 取回后在 JS 端过滤 |
| 34 | **FK 列传错 UUID 类型（如 bookings FK 传了 seat UUID）** | PATCH 操作无错误提示但数据未更新，页面假死/无响应 | `rescheduled_from UUID REFERENCES bookings(id)` 但代码传入的是 seat_id（另一个表的 UUID），外键校验静默拒绝 → API 返回错误但前端未 catch → 后续状态不一致 | ① 严格区分 FK 列引用的目标表；② PATCH 操作必须 try-catch 并显示错误；③ 如果 FK 列在当前业务中不必须，不要传该字段（而非传错误值）

## 通知触发器

业务事件驱动的站内通知可以用 PostgreSQL 触发器零成本实现——状态变更时自动 INSERT 到 `notifications` 表，前端 30s 轮询。详见 `references/notification-triggers.md`。

如果通知需要**同时推送到外部平台**（钉钉/飞书），使用 `pg_net` 扩展的 `net.http_post()` 在同一个触发器内完成。详见 `references/pg-net-webhook.md`。

**⚠️ 单一数据源原则**：工单/申领/盘点状态变更通知由 DB 触发器统一管理，前端只做 CRUD。DB 触发器内先调用 `send_webhook()` 一次再插按用户通知行，避免 N×webhook 爆炸。详见 `references/notification-architecture.md` 和 `references/send-webhook-helper.md`。

每条通知应包含该环节的关键业务信息（地点、接单人、类别、评分等）。完整模板映射见 `references/notification-templates.md`。

修改 webhook 格式后务必全量验证。完整测试方法和 14 种模板清单见 `references/testing-webhook-templates.md`。

批量修复多张表 `id` 列无 DEFAULT 的问题，使用 `references/batch-fix-id-defaults.md` 中的检测与一键修复脚本。

## 前端：无 CDN SDK 的原生 fetch 模式

当 CDN 加载的 Supabase JS SDK 无法正常工作（`window.supabase` 始终 undefined、网络环境限制）时，**完全绕过 SDK**，直接用原生 `fetch()` 调用 Supabase REST API。零外部依赖，可靠性最高。

```javascript
const SB_URL = 'https://{project_ref}.supabase.co'
const SB_KEY = 'sb_publishable_...'
const API = SB_URL + '/rest/v1'

async function api(method, table, params = {}) {
  let url = `${API}/${table}`
  const opts = {
    method: method.toUpperCase(),
    headers: { 'apikey': SB_KEY, 'Content-Type': 'application/json', 'Prefer': 'return=representation' }
  }
  if (params.select) url += `?select=${encodeURIComponent(params.select)}`
  if (params.filters) url += (url.includes('?') ? '&' : '?') + params.filters
  if (params.order) url += (url.includes('?') ? '&' : '?') + `order=${params.order}`
  if (params.limit) url += (url.includes('?') ? '&' : '?') + `limit=${params.limit}`
  if (params.body) opts.body = JSON.stringify(params.body)

  const r = await fetch(url, opts)
  if (!r.ok) { const e = await r.text(); throw new Error(e) }
  const txt = await r.text()
  return txt ? JSON.parse(txt) : null
}
```

**COUNT 查询（不拉取数据）**：

```javascript
async function apiCount(table, filter) {
  let url = `${API}/${table}?limit=0`
  if (filter) url += `&${filter}`
  const r = await fetch(url, { headers: { 'apikey': SB_KEY, 'Prefer': 'count=exact' } })
  const range = r.headers.get('content-range')
  if (range) { const m = range.match(/\d+$/); if (m) return parseInt(m[0]) }
  return 0
}
```

> ⚠️ PATCH 和 DELETE 必须在 URL filter 中指定条件（如 `?id=eq.xxx`），否则操作全表。

## 动态座位生成模式

适用于票务/选座等需要从行配置批量生成座位的场景。

**表结构**：`zones`(区域) → `row_configs`(排号段) → `seats`(具体座位 × 每场次)

**关键规则**：
- 一行可能有**多个不连续号段**（如 1-9号 + 21-29号）→ 不要对 `(zone_id, row_number)` 加 UNIQUE，同一排允许多条 row_configs 记录
- 前端渲染座位图时，对同一排的多段号段要合并展示在同一行（按 seat_number 排序后渲染）
- 用 `CROSS JOIN LATERAL generate_series(seat_start, seat_end)` 批量生成
- admin 后台提供「重新生成座位」按钮，修改区域排配置后一键重建

```sql
INSERT INTO seats(show_id, zone_id, zone_name, floor, row_number, seat_number)
SELECT $1, z.id, z.name, z.floor, rc.row_number, s.seat_num
FROM row_configs rc
JOIN zones z ON z.id = rc.zone_id
CROSS JOIN LATERAL generate_series(rc.seat_start, rc.seat_end) AS s(seat_num)
```

### 座位模板复用模式

当不同演出日期使用不同的座位布局时，**不要直接修改 seats 表**。引入 `seat_templates` + `template_rows` 两层：

- `seat_templates`(id, name) — 模板名称（如 "默认448座"、"VIP专场"）
- `template_rows`(template_id, zone_id, zone_name, floor, row_number, seat_start, seat_end) — 模板内的排配置
- `shows.template_id` — 每个场次关联一个模板

**流程**：
1. 在 `row_configs` 中编辑当前布局 → 确认后「保存为模板」→ 复制到 `template_rows`
2. 新建演出日期 → 选择模板 → 从模板批量生成该日期的 seats
3. 「重生成」按钮只操作单日：清除该日 seats + bookings → 从模板重新生成
4. 不同日期可关联不同模板，各自独立，互不影响

**前端并行加载模式**：日期和区域数据独立，登录后并行加载再自动渲染第一个区域：

```javascript
Promise.all([loadDates(), loadZones()]).then(() => {
  loadSeats()  // 此时 curShow + curZone 均已设置
  loadStats()
  loadBookings()
})
```

## 批量操作与 Pooler 连接

通过 Pooler 连接时两个核心坑和最佳实践：

- **批量插入**：逐条 INSERT 经 Pooler 延迟 ~100ms/条，448 条 → 60s+。用 `execute_values` 后 448 条 → <2s（性能 100×）
- **autocommit**：`c.commit()` 对 DELETE 可能静默不提交 → 设置 `c.autocommit = True`
- **验证**：DELETE/TRUNCATE 后立即 `SELECT count(*)` 确认行数为 0 再继续 INSERT

## 环境依赖

- `psycopg2-binary` + `psycopg2.extras.execute_values` — 直连 PostgreSQL + 批量插入
- `supabase` CLI — 项目管理（可选）
- 前端：Supabase JS SDK（CDN）或 **原生 fetch()（推荐，零依赖）**

## 凭据文件

项目凭据（URL、Key、PAT、OSS 等）集中在 `references/credentials.md`。新项目启动时先从该文件获取凭据。

| 44 | **`select('*')` 不指定 `.limit()` 导致数据截断** | 题库 187 条记录但页面显示不全，选项字段缺失 | Supabase JS SDK 默认不分页但 PostgREST 的 `max-rows` 配置可能被调低；部分行因超出限制未被返回 | **所有 `select('*')` 必须显式加 `.limit(1000)`**。即使数据量在默认限制内，这是防御性实践 |
| 45 | **JSONB `options` 字段在 Supabase JS Client 中类型不稳定** | 单选题无选项显示（空白区域），但数据库内 options 为正常 JSON 数组 | SDK v2 对 JSONB 列的解析可能因网络/缓存返回 JSON 字符串而非已解析数组 | **前端必须用 `ensureOptionsArray()` 包装函数**：检查 `Array.isArray()` → 尝试 `JSON.parse()` → 降级处理。不能假设 `q.options` 总是数组 |
| 46 | **Dedup 用前缀截取而非完整文本 hash** | 去重逻辑用 `question_text[:60]` 作为 key，导致 110+252 道合法题目被误删 | 后缀不同的题目（"根据《民法典》规定，下列哪项..."）前缀相同被当作重复 | **去重必须用完整内容 hash**：`hashlib.md5(question_text + '|'.join(options)).hexdigest()`，而非前缀截取 |
| 47 | **LLM 生成选项后答案字母错位** | 38 道题显示错误答案——正确选项被 LLM 移到了其他字母位置 | LLM 补全缺失选项（如补 D）时重排了选项顺序，但 `correct_answer` 字母未更新。例如原答案为 B，但选项重排后正确内容移到了 A | **必须交叉验证答案内容而非字母**：用原始 docx 中正确选项的**文本内容**去匹配当前 DB 选项文本，重新映射答案字母。不能假设字母不变 |
| 48 | **多选题被误标为单选题** | 题型列显示"单选题"但正确答案为 "ABC" | docx 解析器未识别多选题标记，或 LLM 补全选项后未回头修正 `question_type` | **入库后做 constraint 校验**：`LENGTH(correct_answer) > 1` → `question_type` 必须为 '多选题'，自动批量修正 |
| 49 | **选项渲染正则不稳定 + 分隔符不统一** | 部分单选题选项不显示，或个别字母（A/B/C/D）消失 | 选项分隔符有 `. 、 ， ) ） ． : ：` 等 8+ 种格式，正则疲于兼容 | **① 入库前标准化所有选项为 `A.xxx` 格式**（数据库迁移脚本）；② 前端只用 `replace(/^[A-D]\.\s*/, '')`；③ 字母用 `String.fromCharCode(65+i)` 硬编码，不依赖正则匹配 |
| 50 | **fetch() 直调 Supabase REST API 比 CDN SDK 更可靠** | `select('*')` 缺数据、JSONB 解析异常、CDN 加载失败 | supabase-js v2 CDN 在全球不同网络下表现不一致；JSONB 字段类型可能因版本返回 string 而非 array | **前端完全绕过 SDK，用原生 `fetch()` + `limit=1000` + 类型安全包装函数**。参考 `references/quiz-display-fetch.md` |

| 35 | **apiCount 加 `_t` 时间戳参数导致 COUNT 全返回 0** | 统计四栏全是 0，但数据存在 | 给 REST API URL 追加 `&_t=${Date.now()}` 意图破缓存，但 Supabase REST API 将其视为有效查询参数，干扰 `count=exact` 的 `content-range` 响应头解析 | apiCount 的 URL 只保留 `limit=0` + 业务 filter，不追加任何额外参数。REST API 默认无缓存，无需手动破缓存 |
| 36 | **apiCount 加 Cache-Control 头导致 COUNT 返回 0** | 同 #35，统计全显示 0 | `fetch(...,{headers:{'Cache-Control':'no-cache'}})` 在 Supabase REST API 中干扰 count=exact 响应 | apiCount 的 fetch headers 只保留 `apikey` + `Prefer: count=exact`，不额外加任何缓存控制头 |
| 37 | **PostgreSQL `NOT IN (NULL, ...)` 不匹配任何行** | `WHERE col NOT IN (SELECT col FROM t)` 预期删除孤儿行但 0 row affected，而子查询返回了 NULL | SQL 标准：`NOT IN` 子查询含 NULL 时，对所有外行返回 UNKNOWN，WHERE 当作 FALSE 执行 | 避免 `NOT IN (subquery)` 当子查询可能返回 NULL。改用 `NOT EXISTS (SELECT 1 FROM t WHERE t.col = outer.col)` 或在子查询中加 `WHERE col IS NOT NULL` |
| 38 | **PostgREST 嵌入资源别名不作用于 FK 列** | `shows(date,template:seat_templates(name))` 返回的 `shows.template` 为 null | PostgREST 中 `alias:table(cols)` 别名仅适用于自定义 join，FK 列的嵌入资源键名是**引用表名**而非别名 | FK 嵌入用实际表名：`shows(date,seat_templates(name))` → 前端取 `b.seats?.shows?.seat_templates?.name` |
| 39 | **座位排号段合并覆盖问题** | 同一排添加第二段时第一段被覆盖 | 前端 `DELETE FROM row_configs WHERE zone_id=X AND row_number=Y` 清空同排旧记录再 INSERT 新记录 | 合并算法：收集同排所有现有段 + 新段 → 按 start 排序 → 相邻/重叠段合并（`end+1>=next.start`）→ DELETE 旧记录 → INSERT 合并后的段。详见 `references/seat-range-merge.md` |
| 40 | **区域名不统一导致三端不一致** | 订座页/后台/票根页显示不同区域名 | 数据库 zone.name 被多轮操作覆盖，但 seats.zone_name 是生成时快照的旧值 | 修改 zone.name 后**必须同步更新** `seats.zone_name` 和 `template_rows.zone_name`（三条 UPDATE）。后台「重新生成座位」会重建 seats，但 template_rows 和已有 bookings 不会自动刷新。zone_name 改为数字标识（如 168/128/108）后确认三端显示统一再继续 |
| 41 | **ES6 模板字符串在微信浏览器中不解析** | 页面按钮点击无响应，JS 完全不执行 | 微信内置浏览器（特别是 Android 端）的 WebView 内核可能不支持 ES6 模板字面量 `` `${}` ``，导致脚本解析失败，整个页面的 JS 停摆 | **全部改用普通字符串拼接 `'text ' + var + ' more'`**，不使用模板字面量。同时检查箭头函数兼容性，必要时降级为 `function(){}`。验证时在微信中实际扫码测试，不能仅依赖 Chrome DevTools |
| 42 | **html2canvas CDN 脚本阻塞页面加载** | 页面空白或长时间 loading，特别是微信扫码环境下 | html2canvas CDN（jsDelivr）在部分网络环境下加载极慢或被墙，`<script src>` 在 `<head>` 或页面顶部时会**阻塞 DOM 解析**，导致整个页面白屏 | **改为按需动态加载**：在 `saveStub()` 函数内部先检查 `typeof html2canvas === 'undefined'`，不存在时用 `document.createElement('script')` 动态插入 `<head>` 并 `await onload`。页面首屏不再依赖 html2canvas CDN |
| 43 | **按钮在操作中 disabled 导致用户困惑** | 用户反馈「按钮点不了」「没有反馈」 | 按钮 `disabled=true` 后变灰且不可再点击，用户不知道操作是否在进行中，也无法取消或重试 | **按钮永远不禁用**。操作中仅修改 `btn.textContent`（如「查询中...」「生成中...」），完成后恢复原文。按钮始终可点击让用户有主动控制感。这是用户的明确偏好——不得违反 |

## 多渠道用户模式（多对多）

当账号需要绑定多个渠道时，用 junction table 而非单列外键：

```sql
CREATE TABLE user_channels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES admin_users(id) ON DELETE CASCADE,
  channel_id UUID REFERENCES channels(id) ON DELETE CASCADE,
  UNIQUE(user_id, channel_id)
);
```

**查询**：`admin_users?select=*,channel:channels(name),user_channels:user_channels(channel_id,channel:channels(name))`

| 50 | **fetch() 直调 Supabase REST API 比 CDN SDK 更可靠** | `select('*')` 缺数据、JSONB 解析异常、CDN 加载失败 | supabase-js v2 CDN 在全球不同网络下表现不一致；JSONB 字段类型可能因版本返回 string 而非 array | **前端完全绕过 SDK，用原生 `fetch()` + `limit=1000` + 类型安全包装函数**。参考 `references/quiz-display-fetch.md` |
| 51 | **DDL: `CREATE POLICY IF NOT EXISTS` 语法错误** | 整批 DDL 执行中断报 `syntax error at or near "NOT"`，后续建表语句全部未执行 | PostgreSQL 的 `CREATE POLICY` 不支持 `IF NOT EXISTS`（截至 PG17） | 先 `DROP POLICY IF EXISTS xxx ON tbl;` 再 `CREATE POLICY xxx ...`。幂等且可重复执行 |
| 52 | **多应用共享项目时表名冲突** | 新建 `users`/`projects` 等通用表名与已有应用表冲突或语义混淆 | 同一 Supabase 项目承载多个应用，通用表名互相覆盖 | 表名加应用前缀（`pm_users`、`quiz_questions`），RLS 策略名同步加前缀 |

## 关联工具

- **Playwright HTML-to-PDF**：当文档需导出为排版精良的 PDF 时，参考 `references/playwright-pdf.md`
- **票务验证 SPA**：扫码→查询→多票选择→票根→截图保存，参考 `references/ticket-verify-spa.md`
- **座位排号段合并算法**：参考 `references/seat-range-merge.md`
- **Docx 题库解析**：从多套 docx 提取结构化数据，参考 `references/quiz-docx-parsing.md`
- **竞赛答题展示页**：fetch() + options 渲染 + 白底大屏投影，参考 `references/quiz-display-fetch.md`
