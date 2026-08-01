# Supabase Pooler 批量操作与连接陷阱

## 批量插入性能

单条 INSERT 通过 Supabase Pooler 延迟极高（~100ms/条）。448 条需 60s+。必须用 `execute_values` 批量：

```python
from psycopg2.extras import execute_values

batch = [(sid, zone, rl, sn) for ...]
execute_values(cur, 'INSERT INTO seats(show_id,zone,row_label,seat_number) VALUES %s', batch)
```

448 条从 60s → <2s。

## autocommit 陷阱

Supabase Pooler 连接下，手动 `c.commit()` 可能**静默不提交** DELETE 操作，导致后续 INSERT 遇到 UNIQUE 冲突报重复键。

```python
c = psycopg2.connect(...)
c.autocommit = True  # 强制每条语句立即提交
cur = c.cursor()
cur.execute('DELETE FROM seats')  # 立即生效，无需 commit()
```

**诊断方法**：TRUNCATE/DELETE 后立即 `SELECT count(*)` 验证实际已删除。如发现数据仍在，切换为 `autocommit=True`。

## generate_series 动态生成座位

当座位的排号段存储在 row_configs 表时，用 `CROSS JOIN LATERAL generate_series()` 批量生成，避免 Python 循环逐条 INSERT：

```sql
INSERT INTO seats(show_id, zone_id, zone_name, floor, row_number, seat_number)
SELECT $1, z.id, z.name, z.floor, rc.row_number, s.seat_num
FROM row_configs rc
JOIN zones z ON z.id = rc.zone_id
CROSS JOIN LATERAL generate_series(rc.seat_start, rc.seat_end) AS s(seat_num)
```

## 一行多段号处理

座位布局中常见同一排有多个不连续号段（如 VIP 区第 1 排：10-20号 + 雅致区第 1 排：1-9号 + 21-29号）。不要对排配置表加 `UNIQUE(zone_id, row_number)` 约束——用 `DELETE + INSERT` 替换更新，或直接允许多条同排记录。

## 排查步骤

当遇到 `UniqueViolation: duplicate key` 但确信已 DELETE 时：

1. `c.autocommit = True`
2. `cur.execute('SELECT count(*) FROM {table}')` — 确认当前行数
3. `cur.execute('DELETE FROM {table}')`
4. 再次 `SELECT count(*)` — 应为 0
5. 确认后再执行 INSERT
