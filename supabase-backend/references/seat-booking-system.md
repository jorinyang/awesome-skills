# 选座订票系统 Web SPA 开发笔记

## 架构

三页面 SPA，纯前端 + Supabase 后端，部署在阿里云 OSS：

| 页面 | 路径 | 用途 |
|------|------|------|
| book.html | /fenglin-seat/book.html | 登录 → 选日期 → 选区 → 座位图 → 订座 / 改签 / 退订 / 数据统计 |
| admin.html | /fenglin-seat/admin.html | 四 Tab 后台：日期管理、区域与座位模板、账号管理、渠道管理 |
| verify.html | /fenglin-seat/verify.html | 三步骤票根查询：输入信息 → 选票（多张时）→ 票根展示 → 长按保存 |

## 数据模型（Supabase / PostgreSQL）

```
shows (id, date, is_open, template_id → seat_templates)
zones (id, name, floor, sort_order)
row_configs (id, zone_id → zones, row_number, seat_start, seat_end)
seats (id, show_id → shows, zone_id → zones, zone_name, row_number, seat_number, status)
bookings (id, seat_id → seats, customer_name, customer_phone, ticket_source, status, order_number)
seat_templates (id, name)
template_rows (id, template_id → seat_templates, zone_id, zone_name, row_number, seat_start, seat_end)
admin_users (id, username, password_hash, role, channel_id → channels)
channels (id, name, contact_person, contact_phone)
user_channels (id, user_id → admin_users, channel_id → channels)  -- 多对多
```

## 座位模板工作流

1. 在「区域与排配置」中调整 row_configs
2. 点击「保存当前布局为新模板」→ 复制 row_configs 到模板
3. 新建日期时选择模板 → 自动从模板生成 seats
4. 每个日期可独立 🔄重生成（仅影响该日）

## 改签规则

- 仅同区域改签（前端限制，zone_id 过滤）
- 仅可改至**明天及之后**（系统时间 +1 天）
- 改签后 booking 保持 `status='active'`，只更新 `seat_id`
- 管理员可改所有渠道订单；普通用户仅可改同渠道订单

## 票根查询过滤规则

- 仅显示 `status='active'` 的有效订单
- 仅显示 `shows.date >= 今天` 的场次（过期票不显示）
- 已退/已改签/已过期全部过滤掉

## 区名数据一致性

`seats.zone_name` 和 `template_rows.zone_name` 是 denormalized 字段。
修改 `zones.name` 时必须同步更新这三张表。

## OSS 部署命令

```bash
python -c "
import oss2, pathlib
auth = oss2.Auth(AK, SK)
bucket = oss2.Bucket(auth, 'oss-cn-hongkong.aliyuncs.com', 'clawshell-vault')
base = pathlib.Path(r'C:\Users\Aorus\workspace\峰林文旅体-票务系统\seat-system')
for f in ['book.html', 'admin.html', 'verify.html']:
    bucket.put_object(f'web-spa/fenglin-seat/{f}', open(str(base/f), 'rb'),
        headers={'Content-Type':'text/html; charset=utf-8', 'Cache-Control':'no-store'})
    bucket.put_object_acl(f'web-spa/fenglin-seat/{f}', oss2.OBJECT_ACL_PUBLIC_READ)
"
```
