# Supabase 凭证文件格式 (.ClawShell/.env.supabase)

## 文件位置
```
C:\Users\<user>\.ClawShell\.env.supabase
```

## 完整格式
```env
# Supabase Project: <project-ref>
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_PROJECT_REF=<project-ref>
SUPABASE_PUBLISHABLE_KEY=sb_publishable_xxx
SUPABASE_SERVICE_KEY=sb_secret_xxx
SUPABASE_PAT=sbp_xxx
SUPABASE_DB_PASSWORD=<password>
SUPABASE_DB_USER=postgres.<project-ref>
SUPABASE_DB_HOST=aws-0-us-west-2.pooler.supabase.com
SUPABASE_DB_PORT=6543
```

## 各字段用途

| 字段 | 用途 | 使用场景 |
|------|------|---------|
| `PUBLISHABLE_KEY` | 匿名访问 | 前端 JS 客户端、REST API |
| `SERVICE_KEY` | 绕过 RLS | 后端批量操作 |
| `PAT` | Management API | 建表/项目管理 |
| `DB_PASSWORD` / `DB_HOST` | PostgreSQL 直连 | 批量导入/DDL/数据验证 |

## Python 直连示例
```python
import psycopg2
conn = psycopg2.connect(
    host='aws-0-us-west-2.pooler.supabase.com',
    port=6543,
    dbname='postgres',
    user='postgres.<project-ref>',
    password='<password>'
)
conn.autocommit = True
```

## JSON 导出+验证模板
```python
import psycopg2, json
from datetime import datetime

def make_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj

cur.execute('SELECT * FROM questions_required ORDER BY id')
cols = [d[0] for d in cur.description]
for row in cur.fetchall():
    item = dict(zip(cols, row))
    opts = item.get('options')
    if isinstance(opts, str): item['options'] = json.loads(opts)
    all_data[key].append(make_serializable(item))
```
