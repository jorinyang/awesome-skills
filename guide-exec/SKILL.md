---
name: guide-exec
description: 贵州之客导游执行单生成器。从行程方案 JSON 生成飞书 docx 导游执行单，含客户名单（身份证/保险）、行程明细、供应商对接、物资核对、财务、应急预案等12个模块。
category: travel
triggers:
  - 导游执行单
  - 执行单
  - guide-exec
  - 带团手册
version: 1.0.0
metadata:
  hermes:
    related_skills:
      - supply-check
---

# guide-exec — 导游执行单生成器

## 12 模块

1. 团基本信息 2. 客户名单（含身份证号/保险单号） 3. 行程明细
4. 景点对接 5. 餐饮安排 6. 住宿信息 7. 车辆信息
8. 物资核对清单 9. 财务信息 10. 应急预案
11. 天气预报 12. 行前确认清单

## 输出
- 飞书文档：在「03-出团执行」节点下创建
- 本地备份：`~/.hermes-feishu/cache/guide_exec_{团号}.md`
- 受众：导游、计调（内部文档）

## 执行流程

### Step 1: 验证输入

🔴 **CHECKPOINT** — 验证输入完整性：

- [ ] `trip_json_path` 文件存在且可读
- [ ] JSON 格式合法（`python3 -m json.tool` 不报错）
- [ ] 包含必填字段 `guide.name` / `guide.phone`
- [ ] `customers` 数组非空且每人有 `name` + `id_card`

如果任一检查失败 → 报错终止，提示缺失字段名。

### Step 2: 生成文档

```bash
python3 scripts/generate_guide_exec.py <trip_json_path> [--parent-token <wiki_node_token>]
```

### Step 3: 验证输出

🛑 **STOP — 生成后验证**：

- [ ] 飞书文档已创建（返回 token）
- [ ] 本地备份已写入 `~/.hermes-feishu/cache/guide_exec_{团号}.md`
- [ ] 12 模块逐项检查无空节

验证不通过 → 报告缺失模块，不继续下一步。

## 陷阱

### trip.json 必须字段

脚本强制要求以下字段，缺失会报 `KeyError`：

```json
"guide": {
  "name": "...",
  "phone": "...",
  "assistant_name": "",    ← 必须存在，可为空字符串
  "assistant_phone": ""    ← 必须存在，可为空字符串
}
```

如果新增 trip.json 不包含 `assistant_name` / `assistant_phone`，即使为空也必须写出。

## 常见陷阱

| 陷阱 | 症状 | 修复 |
|------|------|------|
| trip.json 缺少 `guide.assistant_name` / `assistant_phone` | `KeyError: 'assistant_name'` | 即使无助理也需提供空字符串 `"assistant_name": "", "assistant_phone": ""` |

---

## 关联技能指引

> 以下指引由 `github-absorb` Phase 6 自动生成

- **downstream → `supply-check`**：生成导游执行单后，加载 `supply-check` 逐项核对行程所需物资（第 8 模块「物资核对清单」）。两技能输出互补：执行单给导游看，物资单给仓库核。
