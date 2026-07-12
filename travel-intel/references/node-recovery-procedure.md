# Wiki 节点失效恢复流程

> 适用场景：飞书 Wiki 子分类节点永久删除（131005）导致采集/报告管道中断。

## 恢复流程

### Step 1: 创建新节点

```bash
export PATH="/c/Users/Aorus/AppData/Roaming/npm:$PATH"

# 在父节点下创建新子节点
lark-cli wiki +node-create \
  --space-id 7643710721485753535 \
  --parent-node-token <PARENT_TOKEN> \
  --title "<节点名称>" \
  --node-type origin \
  --as bot
```

记录返回的 `node_token`。

### Step 2: 全局搜索旧 token 引用

```bash
grep -rn "OLD_TOKEN" /c/Users/Aorus/.hermes-feishu/ \
  --include="*.py" --include="*.md" --include="*.yaml" --include="*.sh" \
  > /tmp/token_refs.txt
```

按文件类型分类：
- **`.py` 脚本** → 必须全部替换
- **`.md` 文档** → 区分活跃指令 vs 历史记录
- **`cron/output/`** → 历史日志，不修改
- **`__pycache__/*.pyc`** → 删除重建

### Step 3: 批量替换脚本中的 token

```bash
OLD="dead_token_here"
NEW="new_token_here"

for f in $(grep -rl "$OLD" /c/Users/Aorus/.hermes-feishu/scripts/ /c/Users/Aorus/.hermes-feishu/skills/ --include="*.py"); do
  sed -i "s/$OLD/$NEW/g" "$f"
done
```

### Step 4: 手动修复 sed 无法处理的文件

⚠️ **陷阱：sed 会破坏 raw string 中的反斜杠**

```python
# ❌ sed 后变成乱码
r"C:\Users\Aorus\AppData\Roaming\npm\agent-browser.cmd"

# ✅ 用 patch 工具逐个修复
```

使用 `patch` 工具 + `old_string` / `new_string` 精确替换。

### Step 5: 清理 pycache

```bash
find /c/Users/Aorus/.hermes-feishu -name "__pycache__" -type d \
  -exec rm -rf {} + 2>/dev/null
```

### Step 6: 验证

```bash
# 确认无残留
grep -rn "OLD_TOKEN" /c/Users/Aorus/.hermes-feishu/skills/ /c/Users/Aorus/.hermes-feishu/scripts/ \
  --include="*.py" || echo "SCRIPTS: CLEAN"

# 测试写入新节点
lark-cli docs +create --api-version v2 --doc-format markdown \
  --parent-token NEW_TOKEN \
  --content "# test_$(date +%Y-%m-%d)" --as bot
```

### Step 7: 更新 SKILL.md 存储节点表

标记旧节点为删除，添加新节点信息。

## 2026-07-04 案例

| 旧节点 | Error | 新节点 |
|--------|-------|--------|
| `V0Lhwl7KYi` (行业资讯) | 131005 | `MYQtwtPEOiu4nZkma9NcEEQ3n6V` |
| `EAMYw1CPoi` (竞品动态) | 131005 | `E7xyw9pSfibEEckZVEIcU5AynJs` |

影响范围：9 个 .py 脚本 + 7 个 .md 文档 + feishu-wiki skill。
