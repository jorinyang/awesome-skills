# 座位段合并算法

## 场景

票务系统中，同一区域同一排可能有多个不连续的座位段（如 VIP区 1排 1-9号 + 27-29号）。当管理员在同一排新增座位段时，需要自动检测并合并重叠或相邻的段。

## 算法

```javascript
async function addRowWithMerge(zoneId, rowNum, newStart, newEnd) {
  // 1. 拉取该排所有现有段
  const existing = await api('get','row_configs',{
    filters:`zone_id=eq.${zoneId}&row_number=eq.${rowNum}`, limit:'50'
  })
  
  // 2. 收集所有段（现有 + 新增）
  let ranges = (existing||[]).map(r => ({ start: r.seat_start, end: r.seat_end, id: r.id }))
  ranges.push({ start: newStart, end: newEnd, id: null })
  
  // 3. 按起始号排序
  ranges.sort((a, b) => a.start - b.start)
  
  // 4. 合并重叠/相邻段
  const merged = []
  let cur = null
  for (const r of ranges) {
    if (!cur) { cur = {...r}; continue }
    if (r.start <= cur.end + 1) {
      // 重叠或相邻 → 扩展当前段
      cur.end = Math.max(cur.end, r.end)
    } else {
      // 有间隔 → 保存当前段，开始新段
      merged.push(cur)
      cur = {...r}
    }
  }
  if (cur) merged.push(cur)
  
  // 5. 删除旧段 + 写入合并后的段
  if (existing) for (const r of existing) {
    await api('delete','row_configs',{filters:`id=eq.${r.id}`})
  }
  for (const m of merged) {
    await api('post','row_configs',{body:{
      zone_id: zoneId, row_number: rowNum,
      seat_start: m.start, seat_end: m.end
    }})
  }
}
```

## 合并规则

| 场景 | 输入 | 输出 |
|------|------|------|
| 重叠 | 已有 1-5, 新增 3-8 | → 1-8 |
| 相邻 | 已有 1-3, 新增 4-6 | → 1-6 |
| 分离 | 已有 1-3, 新增 27-29 | → 两条独立保留 |
| 包含 | 已有 1-10, 新增 3-7 | → 1-10 |
