# 知识库 9 分类读写验证（2026-05-26）

## 验证结论
9 个分类全部通过写入+读取验证，链路完整。

## 测试结果

| 分类 | node_token | obj_token | 写入 | 读取 |
|------|-----------|-----------|------|------|
| 企业文化 | Spwkw7TeqiJdmvk8WzdckRW8nmf | SLVKdVzqGobhLKxUIjCc6zmCnje | ✅ | ✅ |
| 团队管理 | Nraswhxksi0RSAk9WF1ckESjnKd | FSZ7dpCSMoGnsuxhd4qcfCb0nwf | ✅ | ✅ |
| 业务规范 | YCfjw4lvAiJhiwkbDH2cLP4CnSf | LstadCRDRoFIBDx0l3vckmdYnKZ | ✅ | ✅ |
| 会议纪要 | JEdfw6wcYixmbmkxOK2cMaWanAh | JlBydWPIuoOxYoxwmEtcDXrwn3c | ✅ | ✅ |
| 方案计划 | DJpjwa1boigv9Ika67uc9bCTnBd | WanCdIfQPog6fXxTOOPcTVHyn1c | ✅ | ✅ |
| 汇报资料 | BXxbwUH14iGKFrkwydscbbWEnCg | SdGpdRlJBos4eqxNgJccmQCGnxh | ✅ | ✅ |
| 文案素材 | PgvmwUltji9DRVk0uMJc02YCnkB | Cu9BdNrTeoRvWfxNtckcA2qCnVO | ✅ | ✅ |
| 产品研发 | KTPFw37BkimJKck32dGcyeZNnjf | GRwHdViiUoFRH5xoq9Ec9IcInqd | ✅ | ✅ |
| 运营策略 | RqAZw2tR0iC1Q9kyUauc4TjhnNg | F4n1dJ31BoTMljxBSjRcKONwnyh | ✅ | ✅ |

## 关键调试发现

### 发现一：写入响应 items=[] 但内容实际已写入
调用 `POST /docx/v1/documents/{obj_token}/blocks/{obj_token}/children` 返回 `code=0, items=[]` 是正常行为，不代表写入失败。需读回 `/blocks/{obj_token}/children` 验证。

### 发现二：读取内容块必须用 /children 路径
`GET /docx/v1/documents/{doc_id}/blocks` 只返回 page 根块（block_type=1），包含 `children` 数组。直接读内容要加 `/children`。

### 发现三：Wiki 节点创建响应数据在 data.node 内层
解析响应时用 `d['data']['node']['node_token']`，不能用 `d['node_token']`。

## 验证脚本
`/home/aorus/test_kb_write.py` — 批量创建节点并写入  
`/home/aorus/test_kb_read.py` — 批量读取验证内容
