# Supabase REST API 嵌入式资源查询

## 表名 vs 别名

Supabase 的 JS SDK 支持 `template:seat_templates(name)` 别名语法，
但 **REST API (PostgREST) 不支持别名**，必须使用实际的数据库表名：

```javascript
// ❌ REST API 不支持 - 返回的嵌套对象中没有 template 字段
select: '*,shows:shows(date,template:seat_templates(name))'
// b.seats.shows.template → undefined

// ✅ 正确 - 用实际表名
select: '*,shows:shows(date,seat_templates(name))'
// b.seats.shows.seat_templates → { name: "万峰大会堂" }
```

## Count 查询

```javascript
async function apiCount(table, filter) {
  let url = `${API}/${table}?limit=0`
  if (filter && filter.length > 0) url += '&' + filter
  const r = await fetch(url, {
    headers: {
      'apikey': KEY,
      'Prefer': 'count=exact'
      // ⚠️ 不要加 Cache-Control: no-cache，会干扰响应头
    }
  })
  const range = r.headers.get('content-range')
  if (range) { const m = range.match(/\d+$/); if (m) return parseInt(m[0]) }
  return 0
}
```

**踩坑**：
- `_t=${Date.now()}` 参数会干扰 Supabase 的 `count=exact` → 返回空
- `Cache-Control: no-cache` 头可能导致 content-range 丢失
- 不需要这些防缓存手段——直接查即可

## 数据一致性

当表中有 denormalized 字段（如 `seats.zone_name`），修改源数据时必须同步更新：

```sql
UPDATE zones SET name='新名称' WHERE id='zone-uuid';
UPDATE seats SET zone_name='新名称' WHERE zone_id='zone-uuid';      -- 同步
UPDATE template_rows SET zone_name='新名称' WHERE zone_id='zone-uuid'; -- 同步
```

## 外键约束与插入顺序

```sql
-- bookings.rescheduled_from 引用 bookings(id)
-- 不能传入 seat_id 作为 rescheduled_from 值（类型不匹配 → FK 错误）
-- 解决方案：改签后 booking 保持 status='active'，仅更新 seat_id
```
