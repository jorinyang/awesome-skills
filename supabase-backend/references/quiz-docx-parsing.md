# Docx 题库解析 — 婚调大比武案例

## 问题

从 20 套 × 36 题的 docx 文件中提取结构化题库。原始 docx 格式极不规范：
- 题目 ID 和题型在同行 `B1-1（单选题）：题目...（A）A.选项1`
- 选项可能内联（同一行）或隔行
- 答案可能嵌入选项行中 `（B）` `（√）` `（×）`
- "第X轮：" 和题号在同一段落（需要预处理拆分）
- 不同套之间有重复题

## 核心技巧

### 1. 预处理：「第X轮：」与题号同行拆分

```python
for raw in lines:
    m = re.match(r'^(第[一二三]轮[：:]?\s*)([BQ]\d+-\d+[（(])', raw)
    if m:
        lines.append(m.group(1).strip())  # 轮次标题
        lines.append(m.group(2) + raw[m.end():])  # 题目行
    else:
        lines.append(raw)
```

### 2. 状态机解析（section 驱动）

```
检测 → [一二三]、必答题 → section='required'
检测 → [一二三]、抢答题 → section='quick'  
检测 → [一二三]、模拟调解题 → section='mediation'
跳过 → 第\d+套 / 第[一二三]轮
在 required: 匹配 B\d+-\d+ → parse_block
在 quick:    匹配 Q\d+-\d+ → parse_block
在 mediation: 匹配 背景： → 收集背景+任务
```

### 3. 题目块解析（parse_block）

- **判断题**：从块末尾提取 `√` 或 `×`，其余为题目文本
- **单选题**：提取 `A-D` 选项（支持 `A.` `A、` `A）` 等前缀），从末尾提取 `（A-D）` 答案
- **多选题**：同上，但答案可能为 `ABCD` 多字母组合
- **内联选项**：`re.findall(r'([A-D])[.、．]\s*([^A-D\n].*?)(?=\s+[A-D][.、．]|$)', line)`

### 4. 答案答案提取（逐行反向搜索）

```python
for line in reversed(block_lines):
    m = re.search(r'[（(]([A-D]{1,4})[）)]\s*$', line)
    if m: answer = m.group(1); break
# 判断题：
    m = re.search(r'[（(]([×√])[）)]\s*$', line)
    if m: answer = m.group(1); break
```

### 5. 去重：全文 hash，不用前缀截取

❌ 错误：`q['question_text'][:60]` — 不同题目前 60 字相同会被误删
✅ 正确：
```python
key = hashlib.md5(
    (q['question_text'] + '|'.join(q['options'] or [])).encode()
).hexdigest()
```

## 完整流程

```
docx → 预处理(拆分同行) → 状态机区块解析 → JSON → 
去重(hash) → 入库 Supabase → 交叉验证答案 → 
LLM 补全缺失选项 → 修正多选题类型标记
```

## 答案交叉验证

入库后必须对比数据库答案与 docx 原文答案：

```sql
-- 找问答不一致的题目
SELECT q.id, q.question_text, q.correct_answer as db_ans,
       -- 通过 API 或离线比对得出 docx_ans
FROM questions_required q
WHERE q.correct_answer != expected_docx_answer
```

本案例发现 17 道不一致（12 道多选误标为单选 + 5 道答案偏差），全部修正。

## 入库后的标准化脚本

解析完成后，执行选项格式统一化——所有选项强制为 `A.xxx` 格式：

```python
import re, json

def normalize_option(opt, letter):
    opt = str(opt).strip()
    stripped = re.sub(r'^[A-Da-d][.\u3001\uFF0C\s\)）．:：]+', '', opt).strip()
    return f'{letter}.{stripped}' if stripped else f'{letter}.{opt}'

for table in ['questions_required', 'questions_quick']:
    cur.execute(f"SELECT id, options FROM {table} WHERE question_type IN ('单选题','多选题')")
    for qid, opts in cur.fetchall():
        new_opts = [normalize_option(o, chr(65+i)) for i, o in enumerate(opts)]
        if new_opts != opts:
            cur.execute(f'UPDATE {table} SET options = %s WHERE id = %s', (json.dumps(new_opts), qid))
```

此步骤消除 `.` `、` `，` `)` `．` `:` `：` 等 8 种分隔符差异，前端只需 `replace(/^[A-D]\.\s*/, '')`。
