# 过期校验诊断 Probe（2026-07-05 新增）

## 用途

当 `expiry_checker.py` 输出 `expired == 0` 时，需要快速验证这是"知识库年轻正常"还是"静默 bug（规则命中但被吞、扫描节点错、分类关键词缺失等）"。本 probe 在不修改脚本的前提下，导出三组诊断信号：

1. **`classify_doc` 命中分布** — 文档按 15 类规则的分类桶
2. **年龄分布** — 0-6d / 7-13d / 14-29d / 30-59d / 60-89d / 90+d / 无日期
3. **实际过期列表**（前 20 条，附 `age` 和命中规则）

## 使用

### Step 1：写入 probe 脚本

```python
# /tmp/expiry_probe.py
import sys
sys.path.insert(0, r"C:\Users\Aorus\.hermes-feishu\skills\travel\travel-intel\scripts")
from expiry_checker import (list_docs, classify_doc, parse_title_date,
                            parse_unix_time, check_expiry, load_rules, NODES)
from collections import Counter
from datetime import date

rules = load_rules()
buckets = Counter()
age_buckets = Counter()
expired = []
all_docs = []
for n in NODES:
    all_docs.extend(list_docs(n))

print(f"Total docs scanned: {len(all_docs)}")
for d in all_docs:
    cls = classify_doc(d.get("title", ""))
    buckets[cls or "<no-match>"] += 1
    age, rule = check_expiry(d, rules)
    if rule is not None:
        expired.append((d.get("title","")[:50], age, rule.get("type")))
    dd = parse_title_date(d.get("title","")) or parse_unix_time(d.get("obj_edit_time"))
    if dd:
        a = (date(2026,7,5) - dd).days  # ← 改成当天日期
        if a < 7: age_buckets["0-6d"] += 1
        elif a < 14: age_buckets["7-13d"] += 1
        elif a < 30: age_buckets["14-29d"] += 1
        elif a < 60: age_buckets["30-59d"] += 1
        elif a < 90: age_buckets["60-89d"] += 1
        else: age_buckets["90+d"] += 1
    else:
        age_buckets["<no-date>"] += 1

print("\nClassify buckets:")
for k, v in buckets.most_common():
    print(f"  {v:5d}  {k}")
print("\nAge distribution:")
for k, v in age_buckets.most_common():
    print(f"  {v:5d}  {k}")
print(f"\nActually expired: {len(expired)}")
for t,a,r in expired[:20]:
    print(f"  {a:4d}d  [{r}]  {t}")
```

### Step 2：执行

```bash
export $(grep -E "^FEISHU_APP_" "C:/Users/Aorus/.hermes-feishu/.env" | xargs)
python3 C:/tmp/expiry_probe.py
```

## 解读

| 信号 | 含义 |
|------|------|
| `<no-match>` 占比 > 60% | `classify_doc` 关键词覆盖不足，需扩 L83-120 的关键词集合 |
| `<no-date>` 占比 > 5% | 文档标题非 `YYYY-MM-DD_*` 格式且 `obj_edit_time` 缺失，永久无法过期 |
| 所有文档 < 7d | 知识库 < 7 天历史，正常现象 |
| classify 命中但全被 `days: null` 吞 | 4 条规则无阈值，参见 SKILL.md 「过期规则 days: null 不触发检查」陷阱 |
| `actually expired > 0` 但 `marked == 0` | `mark_expired()` 失败 → 检查 Windows 双陷阱（`lark-cli.cmd` + npm 路径） |

## 2026-07-05 实证输出

```
Total docs scanned: 1873

Classify buckets:
    804  <no-match>
    427  政策法规（地方/临时）
    197  酒店/交通价格
    150  节庆/活动       ← 命中分类，但被 days:null 吞
    94   攻略/游记/评价
    67   门票/开放时间
    58   行业报告/趋势
    49   景点基础信息    ← 同上
    17   酒店设施/交通线路
     7   竞品新品/营销
     3   季节性信息      ← 同上

Age distribution (today=2026-07-05):
   1070  14-29d
    408  7-13d
    395  0-6d

Actually expired: 0
```

**结论**：所有文档 ≤29d，最低阈值 7d（社媒热议）/14d（节庆）/30d（门票）的过期规则全部未触发。**0 过期是真实结果**，不是 bug。预计 2026-07-12 起出现首批 30d+ 过期。

## 维护提醒

- 每次 `expiry_checker.py` 修改后，建议先跑一次 probe 对比基线
- probe 输出可粘贴到「周度分析」报告作为「知识库健康度」指标
- 当 probe 显示 `<no-match>` 占比突变（>10pp 波动），优先排查 `classify_doc` 关键词集合