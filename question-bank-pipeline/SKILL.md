---
name: question-bank-pipeline
description: 题库系统全栈开发 — 从文档解析→数据库入库→Web SPA展示的完整管线。覆盖 docx/xlsx/md 题目提取、Supabase JSONB 存储、前端大屏展示、考试系统（登录/答题/评分/错题分析/后台管理）、LLM 主观题评分、OSS 部署。
version: 1.2.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [development, quiz, supabase, spa]
triggers:
  - "题库"
  - "题库维护"
  - "题库改版/升级"
  - "quiz system"
  - "question bank"
  - "知识竞答"
  - "试卷"
  - "题目导入"
  - "大比武"
  - "抢答"
  - "必答题"
  - "考试系统"
  - "exam system"
  - "在线考试"
  - "评分系统"
  - "错题分析"
---

# question-bank-pipeline — 题库系统全栈开发

## 适用场景

从文档（docx/xlsx/md）中提取题目，入库到 Supabase，并通过 Web SPA 展示（大屏投影/主持人操作）。

## 核心管线

```
文档 → 解析提取 → 结构化 JSON → 去重验证 → Supabase 入库 → 前端展示 → OSS 部署
```

## Phase 1: 文档解析

### 解析策略选择

| 文档格式 | 推荐方案 | 原因 |
|---------|---------|------|
| docx（规范格式） | python-docx + 正则 | 快速、准确、零成本 |
| docx（不规范格式） | python-docx + LLM 分段提取 | 正则无法覆盖所有格式变体 |
| xlsx | openpyxl/xlsx → CSV | 结构化数据，直接映射 |
| md/txt | 正则分块 | 格式最可控 |

### docx 解析关键技巧

1. **预处理合并行**：docx 中 "第X轮：" 和题目ID可能在同一段落，需先拆分
   ```python
   m = re.match(r'^(第[一二三]轮[：:]?\s*)([BQ]\d+-\d+[（(])', raw)
   if m:
       lines.append(m.group(1).strip())
       lines.append(m.group(2) + raw[m.end():])
   ```

2. **选项两种格式**：
   - 独立成行：`A.选项1` / `B.选项2`（正则逐行匹配）
   - 内联同行：`A.协议离婚B.诉讼离婚C.两者都适用D.两者都不适用`（需用正则 `([A-D])[.、．]\s*([^A-D\n].*?)(?=\s+[A-D][.、．]|$)` 提取）

3. **答案提取**：答案通常在题目末尾 `（A）` 或 `（√）` 格式，注意全角/半角括号

### LLM 辅助提取（当正则不够时）

- 按"套"分块发送，每块 ~3000 字
- 严格要求 JSON 输出
- **PITFALL**: LLM 输出的 JSON 常因题目中的引号而损坏 → 用 `re.search(r'\{[\s\S]*\}', content)` 提取，或改用 JSONL 格式

## Phase 2: 数据模型

### Supabase 表结构

```sql
-- 必答题/抢答题（结构相同，分表存储）
CREATE TABLE questions_required (
  id BIGSERIAL PRIMARY KEY,
  question_type TEXT NOT NULL CHECK (question_type IN ('单选题', '多选题', '判断题')),
  question_text TEXT NOT NULL,
  options JSONB,  -- ["A.xx", "B.xx", ...] 或 null(判断题)
  correct_answer TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 模拟调解题
CREATE TABLE questions_mediation (
  id BIGSERIAL PRIMARY KEY,
  background_text TEXT NOT NULL,
  task_text TEXT NOT NULL DEFAULT '现场模拟调解。',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 考试配置
CREATE TABLE exam_config (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL DEFAULT '默认配置',
  required_count INT NOT NULL DEFAULT 15,
  quick_count INT NOT NULL DEFAULT 20,
  mediation_count INT NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### RLS 策略（公开题库）

```sql
ALTER TABLE questions_required ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_all" ON questions_required FOR ALL USING (true) WITH CHECK (true);
-- 其他表同理
```

## Phase 3: 去重与验证

### 去重策略

**PITFALL**: 不能用题目文本前缀截取去重！大量题目开头相似（如"根据《民法典》规定，下列哪项..."），前60-100字符碰撞严重。

正确做法：用题目全文+选项的 MD5 哈希去重：
```python
import hashlib
def make_key(q):
    parts = [q['question_text']]
    if q.get('options'): parts.extend(q['options'])
    return hashlib.md5('|'.join(parts).encode()).hexdigest()
```

### 验证清单

- [ ] 无缺答案（correct_answer 非空）
- [ ] 单选题答案为单个 A-D 字母
- [ ] 多选题答案为 2-4 个 A-D 字母
- [ ] 判断题答案为 √ 或 ×
- [ ] 单选/多选题 options 数组长度 ≥ 2
- [ ] 题目文本去重后无重复
- [ ] 多选题 question_type 标记正确（LENGTH(correct_answer) > 1 应为多选题）

## Phase 4: 前端展示

### 大屏展示页核心要求

1. **白底主题**（投影仪友好）：`--bg: #ffffff; --surface: #f8fafc; --text: #1e293b`
2. **字号大**：题目 ≥ 36px，选项 ≥ 22px
3. **点击出答案**：先显示题目，点击后高亮正确选项
4. **键盘快捷键**：空格/回车=翻页，←→=上下题，Esc=返回

### JSONB 字段前端处理

**PITFALL**: Supabase JSONB 字段可能返回字符串而非数组，必须做类型检查：
```javascript
function ensureOptionsArray(opts) {
  if (!opts) return null;
  if (Array.isArray(opts) && opts.length > 0) return opts;
  if (typeof opts === 'string') {
    try { var parsed = JSON.parse(opts); if (Array.isArray(parsed) && parsed.length > 0) return parsed; } catch(e) {}
  }
  return null;
}
```

## Phase 5: OSS 部署

```python
import oss2
auth = oss2.Auth(AK, SK)
bucket = oss2.Bucket(auth, 'https://oss-cn-hongkong.aliyuncs.com', BUCKET)
bucket.put_object_from_file(key, local, headers={
    'Content-Type': 'text/html; charset=utf-8',
    'x-oss-object-acl': 'public-read',
    'Cache-Control': 'no-cache'  # 开发阶段禁缓存
})
```

## Phase 6: 前端数据加载策略（关键）\n\n### 方案对比\n\n| 方案 | 优点 | 缺点 | 适用场景 |\n|------|------|------|---------|\n| Supabase JS 客户端 | 实时性、支持 CRUD | JSONB 可能返回字符串、分页默认值不确定 | 管理后台（admin） |\n| 静态 JSON 文件 | 100% 可靠、零中间层、性能好 | 修改后需重新导出 | 展示页（display） |\n\n### 静态 JSON 加载模式\n\n**当展示页出现数据不完整（如选项丢失）且排查无果时，直接切换到静态 JSON 模式。**\n\n1. Python 从 PostgreSQL 导出完整数据（含 JSON 序列化验证）\n2. 上传 JSON 到 OSS（`x-oss-object-acl: public-read`）\n3. 前端通过 `fetch(DATA_URL)` 加载\n\n```javascript\nvar resp = await fetch('https://domain.com/quiz_data.json');\nvar allData = await resp.json();\nquestionPool.required = allData.required || [];\nconfig = allData.config;\n```\n\n导出脚本示例（含逐题验证）：\n```python\ncur.execute('SELECT * FROM questions_required ORDER BY id')\ncols = [d[0] for d in cur.description]\nfor row in cur.fetchall():\n    item = dict(zip(cols, row))\n    opts = item.get('options')\n    if isinstance(opts, str): item['options'] = json.loads(opts)\n    # 验证\n    assert item['question_type'] != '单选题' or (isinstance(item['options'], list) and len(item['options']) >= 2)\n    all_data['required'].append(item)\n```\n\n### Supabase JS 客户端分页问题\n\n**PITFALL**: `db.from('table').select('*')` 不加 `.limit(1000)` 时，某些版本的 Supabase JS v2 可能使用低默认分页值（如 100），导致数据截断。\n\n```javascript\n// ❌ 可能丢失数据\ndb.from('questions_required').select('*')\n\n// ✅ 显式设置\ndb.from('questions_required').select('*').limit(1000)\n```\n\n## Phase 7: 考试系统架构（完整考试场景）

当需求从"题目展示"升级为"在线考试"时，需要以下额外组件：

### 考试系统数据模型

```sql
-- 题库（含多题型）
CREATE TABLE exam_questions (
  id BIGSERIAL PRIMARY KEY,
  type TEXT NOT NULL CHECK (type IN ('choice','truefalse','shortanswer')),
  question TEXT NOT NULL,
  options JSONB,            -- choice题: {"A":"...","B":"..."}
  answer TEXT NOT NULL,     -- choice/truefalse: 标准答案; shortanswer: 参考答案
  reference_answer TEXT,    -- shortanswer题的参考答案
  key_points JSONB,         -- shortanswer题的评分要点
  category TEXT DEFAULT '', -- 知识分类标签
  difficulty TEXT DEFAULT 'medium' CHECK (difficulty IN ('easy','medium','hard')),
  explanation TEXT DEFAULT ''
);

-- 考试配置（单行）
CREATE TABLE exam_configs (
  id BIGSERIAL PRIMARY KEY,
  num_choice INT DEFAULT 15,
  num_truefalse INT DEFAULT 10,
  num_shortanswer INT DEFAULT 3,
  time_limit_minutes INT DEFAULT 60,
  max_retakes INT DEFAULT 3,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 答卷记录
CREATE TABLE exam_records (
  id BIGSERIAL PRIMARY KEY,
  student_name TEXT NOT NULL,
  phone TEXT NOT NULL,
  score NUMERIC,
  total INT,
  details JSONB,           -- 每题得分/答案/解析
  answers JSONB,           -- 学员原始答案
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS: anon 可读题库和配置，可插入答卷
ALTER TABLE exam_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_records ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read" ON exam_questions FOR SELECT USING (true);
CREATE POLICY "anon_read" ON exam_configs FOR SELECT USING (true);
CREATE POLICY "anon_insert" ON exam_records FOR INSERT WITH CHECK (true);
-- 写操作（题库管理）
CREATE POLICY "anon_write_q" ON exam_questions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "anon_write_c" ON exam_configs FOR UPDATE USING (true);
```

### 考试系统前端架构

两个独立 SPA，均部署到 OSS：

| 页面 | 文件 | 功能 | 认证 |
|------|------|------|------|
| 学员端 | index.html | 登录→答题→评分→错题解析 | 姓名+手机号 |
| 后台管理 | admin.html | 成绩查询/题库CRUD/参数配置 | 管理密码 |

### 学员端核心流程

```
登录(姓名+手机) → 加载配置 → 从题库随机抽取N题 → 答题(计时/逐题导航)
→ 交卷 → 客观题自动评分 → 主观题LLM评分 → 展示结果 → 错题解析(LLM生成)
```

**随机抽取**：客户端从 Supabase 加载全量题库 → 按类型分组 → `shuffle()` → 按配置数量 `slice()`。不依赖数据库随机函数。

### 后台管理核心功能

- **数据概览**：考试人次/平均分/通过率/成绩分布/错误率最高题目
- **考试记录**：搜索/筛选/排序/导出CSV
- **题库管理**：CRUD + 按类型/分类/难度筛选
- **考试设置**：题量/时间/重考次数

### LLM 主观题评分（MiniMax 示例）

```javascript
async function gradeShortAnswer(studentAnswer, referenceAnswer, keyPoints) {
  var prompt = '你是一位专业的企业培训考试评分专家。\\n\\n' +
    '参考答案：' + referenceAnswer + '\\n\\n' +
    '评分要点：' + (keyPoints || '无') + '\\n\\n' +
    '学员答案：' + studentAnswer + '\\n\\n' +
    '请根据参考答案和评分要点，对学员答案进行评分（0-100分）。\\n' +
    '返回JSON格式：{"score": 分数, "feedback": "评语"}';
  
  var resp = await fetch('https://api.minimax.chat/v1/text/chatcompletion_v2', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + MINIMAX_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'MiniMax-Text-01',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.3
    })
  });
  // Parse score from response...
}
```

**错题解析生成**：将题目+学员答案+正确答案发给 LLM，要求生成针对性解析。

### OSS 部署（Python oss2）

```python
import oss2
auth = oss2.Auth(AK, SK)
bucket = oss2.Bucket(auth, 'https://oss-cn-hongkong.aliyuncs.com', 'clawshell-vault')
bucket.put_object('exam/index.html', open('index.html','rb'), headers={
    'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-cache'
})
```

**Bucket 名**：`clawshell-vault`（对应 gzzhike.cn 域名）。凭证在 `~/.ossutilconfig`。

## Pitfalls

1. **Supabase service key 浏览器 CORS 拦截**：`sb_secret_*` service key 从浏览器 fetch 调用会被 CORS 策略拦截（HTTP 401），即使 key 正确。**解决方案**：前端 SPA（包括 admin 后台）必须使用 `sb_publishable_*` anon key。需要写操作时，为 anon 角色添加 RLS INSERT/UPDATE/DELETE 策略。service key 仅用于服务端（Python/Node.js/Edge Functions）。这不影响安全——admin 页面已有自己的密码认证层。

1. **docx 选项内联**：同一行 `A.xx B.xx C.xx D.xx` 格式，正则需处理空格分隔
2. **去重用前缀截取**：题目开头高度相似，必须用全文+选项哈希
3. **多选题被标记为单选**：`LENGTH(correct_answer) > 1` 的应批量修正为多选题
4. **LLM JSON 损坏**：题目中的引号/特殊字符导致 JSON 解析失败 → 分块+重试+正则提取
5. **匿名 key 无 DDL 权限**：建表需用 service_role key 或直接连 PostgreSQL
6. **前端 JSONB 字段**：永远做类型检查，不要假设返回类型
7. **Supabase `select('*')` 默认分页**：不加 `.limit(1000)` 可能只返回部分数据 → 展示页可选静态 JSON 兜底
8. **选项前缀正则**：使用 `[.\u3001\uFF0C\s\)）]+` 覆盖 A. / A、/ A) / A ）等多种分隔符，而非仅 `[\.\、]`
9. **Supabase 凭证位置**：完整凭证（含 service_key/DB密码/PAT）在 `.ClawShell/.env.supabase`，建表/批量导入用 DB 直连 psycopg2
10. **白底配色方案**：投影展示用 `--bg:#fff; --surface:#f8fafc; --text:#1e293b; --text2:#64748b`，题型用靛蓝/琥珀/玫红区分
11. **CSS flex居中+overflow裁剪**：`align-items:center` + `overflow-y:auto` 导致长内容顶端不可达。修复：`#main::before,#main::after{content:'';flex:1;min-height:0}` + `#card{margin:auto 0}`，用伪元素做弹性占位而非 flex 居中
12. **LLM 选项重排导致答案错位**：LLM 补全缺失选项时可能改变原选项顺序，但 `correct_answer` 字母未更新。修复方案：① System Prompt 明确"选项顺序与原文一致，不可重排"；② 导入后用 docx 正确答案文本匹配 DB 选项内容，重新计算正确字母
13. **选项格式标准化**：数据库中所有选项统一为 `A.xxx` 格式（禁止 A、/A)/A，），LLM 生成的选项必须归一化
14. **JS 变量/函数重名**：全局 `var sel=null` 和 `function sel()` 冲突，首次调用后变量覆盖函数导致后续 TypeError。修复：重命名变量为 `selType`
15. **近似重复检测**：`一个月内` vs `1个月内`（数字格式差异）→ 同表内 Levenshtein ≤ 2 且答案相同的视为重复并去重；跨表（必答/抢答）不删
16. **答案验证应比较选项内容而非字母**：对比 docx 的正确答案选项文本与 DB 对应位置的选项文本是否一致，而非仅比字母。LLM 重排选项后字母不变但内容错位

## 📚 引用文件索引

| 文件 | 路径 | 用途 |
|------|------|------|
| supabase-credentials.md | `references/supabase-credentials.md` | Supabase 凭证文件格式、DB直连模板、JSON导出验证模板 |
| white-theme-css.md | `references/white-theme-css.md` | 白底配色方案CSS变量、字号规范、题型颜色映射 |
| llm-import-prompt.md | `references/llm-import-prompt.md` | LLM 导入 System Prompt 模板、常见错误、校验清单 |
| css-display-patterns.md | `references/css-display-patterns.md` | 大屏展示 CSS 布局模式：伪元素居中、clamp()响应式、白底配色 |
| md-json-bank-maintenance.md | `references/md-json-bank-maintenance.md` | 题库 MD↔JSON 双工件维护/升级：schema 约定、JSON 单一事实源生成 MD、独立五项校验、黑名单豁免、原地覆盖恢复、中文路径读文件坑 |\n\n1. **docx 选项内联**：同一行 `A.xx B.xx C.xx D.xx` 格式，正则需处理空格分隔\n2. **去重用前缀截取**：题目开头高度相似，必须用全文+选项哈希\n3. **多选题被标记为单选**：`LENGTH(correct_answer) > 1` 的应批量修正为多选题\n4. **LLM JSON 损坏**：题目中的引号/特殊字符导致 JSON 解析失败 → 分块+重试+正则提取\n5. **匿名 key 无 DDL 权限**：建表需用 service_role key 或直接连 PostgreSQL\n6. **前端 JSONB 字段**：永远做类型检查，不要假设返回类型\n7. **Supabase `select('*')` 默认分页**：不加 `.limit(1000)` 可能只返回部分数据 → 展示页可选静态 JSON 兜底\n8. **选项前缀正则**：使用 `[.\\u3001\\uFF0C\\s\\)）]+` 覆盖 A. / A、/ A) / A ）等多种分隔符，而非仅 `[\\.\\、]`\n9. **Supabase 凭证位置**：完整凭证（含 service_key/DB密码/PAT）在 `.ClawShell/.env.supabase`，建表/批量导入用 DB 直连 psycopg2\n10. **白底配色方案**：投影展示用 `--bg:#fff; --surface:#f8fafc; --text:#1e293b; --text2:#64748b`，题型用靛蓝/琥珀/玫红区分

## 📚 引用文件索引

| 文件 | 路径 | 用途 |
|------|------|------|
| supabase-credentials.md | `references/supabase-credentials.md` | Supabase 凭证文件格式、DB直连模板、JSON导出验证模板 |
| white-theme-css.md | `references/white-theme-css.md` | 白底配色方案CSS变量、字号规范、题型颜色映射 |
| llm-import-prompt.md | `references/llm-import-prompt.md` | LLM 导入 System Prompt 模板、常见错误、校验清单 |
| css-display-patterns.md | `references/css-display-patterns.md` | 大屏展示 CSS 布局模式：伪元素居中、clamp()响应式、白底配色 |
| md-json-bank-maintenance.md | `references/md-json-bank-maintenance.md` | 题库 MD↔JSON 双工件维护/升级：schema 约定、JSON 单一事实源生成 MD、独立五项校验、黑名单豁免、原地覆盖恢复、中文路径读文件坑 |
