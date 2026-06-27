# 事后分拣工作流 — 一级分类 → 子分类批量移动

> **背景**：行业资讯 (`V0Lhwl7KYi`) 和竞品动态 (`EAMYw1CPoi`) 的 node_token 在 doc create 时返回 3380002，但 **Move API 不受影响**。新文档创建在咨询洞察一级 (`UF7Cw5w2Wi`) 下，需定期通过 Move API 分拣到子分类。

## 前提条件

- `FEISHU_APP_ID` / `FEISHU_APP_SECRET` 环境变量已设置
- curl + Python subprocess 可用

## 步骤

### Step 1: 列出待分拣文档

```python
import json, subprocess, os

r = subprocess.run(['curl','-s','-X','POST',
  'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
  '-H','Content-Type: application/json',
  '-d', json.dumps({'app_id': os.environ['FEISHU_APP_ID'],
                    'app_secret': os.environ['FEISHU_APP_SECRET']})],
  capture_output=True, text=True, timeout=15)
TOKEN = json.loads(r.stdout)['tenant_access_token']

space_id = '7643710721485753535'
parent_token = 'UF7Cw5w2WiHGfjkKVvBcxj8Hnib'

# 翻页获取所有子节点（含子分类节点本身）
def fetch_children(page_token=None):
    url = f'https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes?parent_node_token={parent_token}&page_size=50'
    if page_token:
        url += f'&page_token={page_token}'
    AUTH = 'Authorization: Bearer *** + TOKEN
    r = subprocess.run(['curl','-s', url, '-H', AUTH],
      capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)
```

> ⚠️ **不要用 `lark-cli wiki +node-list`** — 它不转发 `parent_node_token` query 参数，返回的是空间根节点而非实际子节点（静默失败）。

### Step 2: 分类

排除子分类节点（标题为「行业资讯」或「竞品动态」），对叶子文档按标题关键词分类：

| 目标 | 关键词 |
|------|--------|
| 竞品动态 | `竞品|新品|价格调整|营销` |
| 行业资讯 | 其余全部 |

> ⚠️ **避免宽泛关键词误判**：`价格`、`徒步` 等词在景区政策/促销新闻中常见，会误匹配竞品。严格按照上述竞品关键词匹配，不要扩展。

### Step 3: 批量移动

```python
target_parent = 'V0Lhwl7KYiWYDDk1vCncv2GhnYf'  # 行业资讯
# 或 'EAMYw1CPoipVWtkObbtcR2oDnNc'  # 竞品动态

import time

for i, doc in enumerate(docs_to_move):
    token = doc['token']
    url = f'https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes/{token}/move'
    body = json.dumps({'target_parent_token': target_parent})

    AUTH = 'Authorization: Bearer *** + TOKEN
    r = subprocess.run(['curl','-s','-X','POST', url,
      '-H', AUTH, '-H', 'Content-Type: application/json', '-d', body],
      capture_output=True, text=True, timeout=15)

    resp = json.loads(r.stdout)
    if resp.get('code') == 0:
        print(f'[{i+1}] OK: {doc["title"][:60]}')
    else:
        print(f'[{i+1}] FAIL {resp["code"]}: {doc["title"][:60]}')

    time.sleep(1)  # 每条间隔 1 秒

    # 每 10 条冷却 10 秒
    if (i + 1) % 10 == 0:
        time.sleep(10)
```

> ⚠️ **Token 过期风险**：tenant_access_token 有效期约 2 小时，但批量操作 >50 条时可能因为获取 token 到实际调用的时间差导致 99991668。**必须在开始移动前重新获取 token**，不要复用 listing 阶段的旧 token。

### Step 4: 验证

```python
# 验证父节点已无孤儿文档
# 咨询洞察一级下应只剩 2 个子分类节点
# 目标子分类的文档数应增加对应数量

# Spot check：get_node 确认 parent
r = subprocess.run(['curl','-s',
  f'https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={sample_token}',
  '-H', AUTH], capture_output=True, text=True, timeout=15)
node = json.loads(r.stdout)
assert node['data']['node']['parent_node_token'] == target_parent
```

## 2026-06-05 实测

- 70 篇待分拣文档（全部为 L2 采集的行业资讯，无竞品）
- 70/70 全部成功移入行业资讯，零失败
- 咨询洞察一级下从 72 个直接子节点缩减为 2 个（子分类节点）
- 行业资讯文档数：522 → 593
- 批参数：batch_size=10, 每条间隔 1s, 批次间冷却 10s
