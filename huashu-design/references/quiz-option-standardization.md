# 题库选项标准化流水线

从 docx/pdf/md 导入题库时，选项格式可能混乱（`A.`、`A、`、`A)`、选项合并、缺 D 等）。以下流水线确保所有选项统一为 `A.xxx` `B.xxx` `C.xxx` `D.xxx`。

## 1. LLM 导入 Prompt 模板

```text
你是题库生成专家。从给定内容中提取题目，输出严格 JSON 数组。

每道题格式：
{"question_type":"单选题/多选题/判断题","question_text":"题目正文","options":["A.选项1","B.选项2","C.选项3","D.选项4"],"correct_answer":"A"}
- 判断题 options 填 null，correct_answer 填 "√" 或 "×"
- 选项统一 A. B. C. D. 格式，不用其他分隔符
- 去掉题目中的编号前缀（如 B1-1、Q1-1）
- 只输出 JSON 数组，不要其他文字
```

## 2. 数据库标准化

导入后运行标准化脚本，将 `A、A) A． A，` 等统一为 `A.`：

```python
import re, json

def normalize_option(opt, letter):
    opt = str(opt).strip()
    stripped = re.sub(r'^[A-Da-d][.\u3001\uFF0C\s\)）．:：]+', '', opt).strip()
    return f'{letter}.{stripped}' if stripped else f'{letter}.{opt}'

for q in questions:
    for i, o in enumerate(q['options']):
        q['options'][i] = normalize_option(o, chr(65+i))
```

## 3. 导入后自动校验项

| 检查项 | 条件 | 修复 |
|--------|------|------|
| 选项缺 D | `len(options) < 4` | LLM 批量补全第 4 选项 |
| 选项合并 | 一个选项含多个前缀（如 `C.xxxD.xxx`） | 正则拆分 |
| 题号污染 | 选项含 `B1-1`/`Q1-1` 等 | 正则截断 |
| 选项过短 | 剥离前缀后 <2 字符 | 标记人工审核 |
| 选项过⻓ | 剥离前缀后 >200 字符 | 标记异常 |
| JSON 非法字符 | 题目中引号未转义 | 用 `json.loads` 前先修复 |
| 答案匹配 | 答案字母不在 A-D 范围 | 对比原文修正 |

## 4. 端到端审计脚本

```python
# 加载 quiz_data.json 全面审计
for q in questions:
    assert q['question_type'] in ('单选题','多选题','判断题')
    if q['question_type'] == '判断题':
        assert q['correct_answer'] in ('√','×')
        assert q['options'] is None
    else:
        opts = q['options']
        assert len(opts) == 4, f"Expected 4 options, got {len(opts)}"
        for i, lt in enumerate('ABCD'):
            assert opts[i].startswith(lt+'.'), f"Bad prefix: {opts[i][:20]}"
            assert not re.search(r'[BQ]\d+-\d+', opts[i]), "题号污染"
        if q['question_type'] == '单选题':
            assert re.match(r'^[A-D]$', q['correct_answer'])
        else:
            assert re.match(r'^[A-D]{2,4}$', q['correct_answer'])
```

## 5. 常见错误记实录

| 错误类型 | 典型表现 | 根因 |
|----------|---------|------|
| 缺 D 选项 | 58/354 题只有 ABC | docx 解析时选项不全，LLM 生成时遗漏 |
| 选项合并 | `C.双方自愿结婚的D.闪婚` | docx 原文 C/D 同行未拆分 |
| 题号污染 | D 选项含 `Q17-11（判断题）...` | docx 两个段落拼接在同一行 |
| JSONB 字符串 | `options` 字段为字符串 `"[\"A\",...]"` | Supabase JS 客户端序列化异常 |
| 重复题型 | 同题在 4 套中出现 | 原始题库跨套复用，去重保留 |
| 答案不一致 | LLM 生成的选项改变了正确选项的字母位置 | LLM 重新排列选项顺序后，原 docx 的答案字母失效 |
| 近似重复 | `"一个月内"` vs `"1个月内"` 共存 | 中文数字/阿拉伯数字混用，Levenshtein ≤ 2 但内容相同 |

## 6. 答案一致性验证

**答案对比不能只看字母——LLM 生成选项后会重排顺序，导致原始 docx 的答案字母失效。**

正确做法：
1. 从原始 docx 提取 (题目文本 → 正确答案字母) 映射
2. 与数据库按「完整题目文本」精确匹配（非前 N 字模糊匹配）
3. 多行题目需收集完整 block 再提取答案（答案可能在后续行）
4. 修复时直接覆写 `correct_answer` 字段

```python
# 正确：完整文本精确匹配
key = qtext  # 用完整题目文本
if key in docx_answers:
    fix_answer(db_id, docx_answers[key])

# 错误：前 N 字模糊匹配（会错配相似题）
key = qtext[:60]  # ❌ 可能匹配到另一个问题
```

## 7. 配置实时同步

display 页从预生成 JSON 加载题库，但 **exam_config（各题型数量）必须从 Supabase 实时读取**：

```
题库数据 (354题) → quiz_data.json (OSS, 定时同步)
配置数据 (4字段) → Supabase REST API (实时, fetch 即取)
```

原因：admin 改配置后如果不能立即反映到 display，用户体验断裂。JSON 同步有延迟（cron/手动），但配置变更必须实时。

## 6. 前端渲染 — 剥离前缀

标准化后前端只需简单正则：

```javascript
// 所有选项已统一为 A.xxx 格式，简化剥离
var text = String(opt).replace(/^[A-D]\\.\\s*/, '');
```

## 7. 答案一致性验证

**答案对比不能只看字母——LLM 生成选项后会重排顺序，导致原始 docx 的答案字母失效。**

正确做法：
1. 从原始 docx 提取 (题目文本 → 正确答案字母) 映射 — 用完整文本作 key
2. 多行题目需收集完整 block 再提取答案（答案可能在后续行，不在题目行）
3. 与数据库按「完整题目文本」精确匹配后覆写 `correct_answer`

```python
# 正确：完整文本精确匹配 + 多行 block 收集
if full_qtext in docx_answers:
    cur.execute('UPDATE questions SET correct_answer = %s WHERE id = %s',
               (docx_answers[full_qtext], qid))

# 错误1：前 N 字模糊匹配 → 错配相似题
# 错误2：单行提取答案 → 多行题目漏答案
```

## 8. 近似重复去重

同表内题目文本 Levenshtein 距离 ≤ 2 且答案相同 → 去重保留其一。

```
"人民调解委员会调解纠纷，一般应当在一个月内调解终结。"  (一)
"人民调解委员会调解纠纷，一般应当在1个月内调解终结。"  (1)
→ 删除后者，保留前者
```

**注意**：`","属于"` vs `"不属于"` 距离也是1，但答案相反 → 不能去重，这类是合法不同题。
