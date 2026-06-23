# 四维度文档校验脚本模板

## 使用说明

将以下模板复制到 `execute_code` 中，修改文档路径和检查项后运行。
校验脚本输出四维度检查报告。

## 模板

```python
from hermes_tools import read_file

# 1. 读取所有文档
docs = {}
for name, path in [("PRD", "/workspace/xxx_PRD.md"),
                    ("流程图", "/workspace/xxx_flow.md"),
                    ("ER图", "/workspace/xxx_ER.md"),
                    ("架构图", "/workspace/xxx_arch.md")]:
    docs[name] = read_file(path, limit=2000)['content']

# 2. 维度1: 需求一致性 —— 关键需求检查清单
requirements = {
    "需求项名称": "关键字符串" in docs["PRD"],
}

# 3. 维度2: 跨文档一致性 —— 同一概念是否在多文档一致出现
cross_checks = [
    ("概念名称", "term" in docs["PRD"] and "term" in docs["流程图"]),
]

# 4. 维度3: 信息密度 —— 统计行数/图表块数
for name, content in docs.items():
    lines = len(content.split('\n'))
    mermaid_count = content.count('```mermaid')
    print(f"  {name}: {lines}行, {mermaid_count}个Mermaid块")

# 5. 维度4: 逻辑正确性 —— 链路闭环检查
logic_checks = {
    "链路名": "起点关键词" in docs["PRD"] and "终点关键词" in docs["PRD"],
}

# 6. 汇总
for cat, checks in [("需求一致性", requirements), 
                      ("跨文档一致性", dict(enumerate(cross_checks))),
                      ("逻辑正确性", logic_checks)]:
    ok = sum(1 for v in checks.values() if v)
    print(f"  {cat}: {ok}/{len(checks)}")
```

## 常见检查项

### 需求一致性 (示例)
- 销售价格基准是否已解耦
- 编码规则是ABC还是ABCD
- 退货规则是否收紧
- 精度是几位小数

### 跨文档一致性 (示例)
- 同一实体名称是否一致（如"缺货中间表"）
- 术语是否统一（如"动态加权平均"vs"加权平均"）
- 角色名称是否一致

### 逻辑闭环 (示例)
- 采购链路: 缺货→中间表→申请→订单→入库→库存→应付
- 销售链路: 订单→锁定→出库→结算→应收
- 退货链路: 退货→C类→通知采购→换货→A类入库
