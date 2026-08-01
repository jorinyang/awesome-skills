# 动态座位生成模式

## 场景

票务/选座系统中，座位由后台管理页面动态配置（区域→排→号段），每次修改配置后需为所有场次重新生成座位。

## 表结构

```sql
-- 区域配置（后台可增删）
CREATE TABLE zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    floor INT DEFAULT 1,
    sort_order INT DEFAULT 0
);

-- 排配置（后台可增删，每行支持多段号段）
CREATE TABLE row_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id UUID REFERENCES zones(id) ON DELETE CASCADE,
    row_number INT NOT NULL,
    seat_start INT NOT NULL,
    seat_end INT NOT NULL
    -- ⚠️ 不要加 UNIQUE(zone_id, row_number)！一行可能有两段号段
);

-- 场次
CREATE TABLE shows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL UNIQUE,
    is_open BOOLEAN DEFAULT false
);

-- 座位（由 row_configs × shows 生成）
CREATE TABLE seats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    show_id UUID REFERENCES shows(id) ON DELETE CASCADE,
    zone_id UUID REFERENCES zones(id) ON DELETE CASCADE,
    zone_name TEXT NOT NULL,
    floor INT DEFAULT 1,
    row_number INT NOT NULL,
    seat_number INT NOT NULL,
    status TEXT DEFAULT 'available',
    UNIQUE(show_id, zone_id, row_number, seat_number)
);
```

## 批量生成座位（单条 SQL）

```sql
-- 为指定场次生成所有座位，利用 generate_series 展开号段
INSERT INTO seats(show_id, zone_id, zone_name, floor, row_number, seat_number)
SELECT $show_id, z.id, z.name, z.floor, rc.row_number, s.seat_num
FROM row_configs rc
JOIN zones z ON z.id = rc.zone_id
CROSS JOIN LATERAL generate_series(rc.seat_start, rc.seat_end) AS s(seat_num);
```

## psycopg2 执行

```python
c.autocommit = True  # ⚠️ 必须！否则 DELETE/INSERT 可能不生效

# 清空重建
cur.execute('DELETE FROM bookings')
cur.execute('DELETE FROM seats')
cur.execute('DELETE FROM shows')

for show in shows:
    cur.execute('INSERT INTO shows(...) VALUES(...) RETURNING id', ...)
    sid = cur.fetchone()[0]
    cur.execute('''
        INSERT INTO seats(show_id, zone_id, zone_name, floor, row_number, seat_number)
        SELECT %s, z.id, z.name, z.floor, rc.row_number, s.s
        FROM row_configs rc
        JOIN zones z ON z.id = rc.zone_id
        CROSS JOIN LATERAL generate_series(rc.seat_start, rc.seat_end) AS s(s)
    ''', (sid,))
```

## 踩坑记录

1. **UNIQUE(zone_id, row_number) 导致插入失败**：雅致区第3排有 1-9 和 21-29 两段号段 → 第二段插入违反唯一约束。解决：移除该约束或改为 `UNIQUE(zone_id, row_number, seat_start)`。

2. **autocommit 缺失导致 DELETE 无效**：`DELETE FROM seats` 后 `SELECT count(*)` 仍返回原数据 → 因为 psycopg2 在隐式事务中。解决：`c.autocommit = True`。

3. **批量 INSERT 性能**：448座 × 7天 = 3136行，单条 INSERT 需要 60s+。用 `CROSS JOIN LATERAL generate_series` 一次性生成（< 2s）。
