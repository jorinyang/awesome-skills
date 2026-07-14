# DOCX 题库提取技术参考

> 从 Word 文档中提取结构化题目数据（题型/题目/选项/答案）的实战方法论。

## 适用场景

- 从 .docx 格式的考试题库提取为 JSON/Excel/数据库
- 题目格式：`编号（题型）：题目内容（答案）` + 选项行
- 多套题合并去重

## 核心陷阱

### 1. python-docx 段落合并

Word 的段落(paragraph)可能把"第X轮："和题目ID合并到同一个段落中。必须预处理拆分：

```python
import re
processed = []
for raw in [p.text.strip() for p in doc.paragraphs]:
    m = re.match(r'^(第[一二三]轮[：:]?\s*)([BQ]\d+-\d+[（(])', raw)
    if m:
        processed.append(m.group(1).strip())  # 轮次标题单独一行
        processed.append(m.group(2) + raw[m.end():])  # 题目单独一行
    else:
        processed.append(raw)
```

### 2. 去重 key 长度

❌ `q['question_text'][:60]` — 太短，"根据《民法典》规定，下列哪项..."开头的题目几十道，全部被误判为重复。

❌ `q['question_text'][:100]` — 仍然不够，相似题目在100字符内无法区分。

✅ 用题目全文+选项的 MD5 hash：

```python
import hashlib
def make_key(q):
    parts = [q['question_text']]
    if q.get('options'):
        parts.extend(q['options'])
    return hashlib.md5('|'.join(parts).encode()).hexdigest()
```

### 3. LLM JSON 提取的脆弱性

当题目内容包含引号、括号等特殊字符时，LLM 输出的 JSON 经常解析失败（"Expecting ',' delimiter"）。

**正则优先**：对于格式规范的文档（编号+题型标记清晰），正则解析比 LLM 更可靠。
**LLM 补位**：只在正则失败时（格式混乱、无规律）使用 LLM，且需要：
- 分块处理（每套/每章单独请求）
- JSON 修复（尝试 `json5` 或正则修复常见错误）
- 重试机制（3次）

### 4. 状态机解析优于全文切割

按"第X套"→"一、必答题"→"二、抢答题"→"三、模拟调解题"的状态机逐行解析，优于先全文切割再解析。

关键：状态机切换时要正确处理"当前行属于哪个section"，避免在 section 切换时丢失第一道题。

## 完整解析流程

```
1. python-docx 读取所有段落
2. 预处理拆分合并段落
3. 状态机逐行解析：
   - 检测套号/节标题/轮次 → 切换状态
   - 检测题目ID (B{set}-{num}/Q{set}-{num}) → 收集题目块
   - 收集到下一个ID/节标题为止
4. parse_block() 解析每个题目块：
   - 判断题：找末尾（√/×）
   - 单选/多选：提取选项行 + 答案标记
5. MD5 hash 去重
6. 输出 JSON
```

## 输出格式

```json
[
  {
    "question_type": "单选题",
    "question_text": "根据《民法典》规定，下列哪项属于夫妻一方的个人财产？",
    "options": ["A.婚后工资奖金", "B.婚前购买且登记在个人名下的房产", "C.婚后经营收益", "D.婚后继承的遗产"],
    "correct_answer": "B"
  }
]
```

判断题 options 为 null，correct_answer 为 "√" 或 "×"。
