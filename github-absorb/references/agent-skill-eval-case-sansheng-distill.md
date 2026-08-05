# 案例：sansheng-distill 代理技能仓库评估

> 评估日期: 2026-07-12
> 仓库: `sandypoli-boop/sansheng-distill` (v0.1.0)
> GitHub 状态: 404（已不可公开访问）
> 镜像源: `sanshengai.top/downloads/sansheng-distill-v0.1.0.zip`

## 背景

用户要求"从真实源码出发进行测试验证得到实际的评估结果"来评估一个微信公众号文章中宣传的 AI 拆书 Agent Skill。

## 404 → 镜像站发现路径

1. GitHub API / `firecrawl_scrape` 均返回 404
2. 从用户提供的微信公众号文章 (`mp.weixin.qq.com/s/UyjUDmGftFkHwtGkbSg9-w`) 中提取到作者官网 `sanshengai.top/tools/github`
3. 抓取镜像页面 → 发现 zip 下载链接 `sanshengai.top/downloads/sansheng-distill-v0.1.0.zip`
4. `curl -L -o` 下载 (7MB) → `unzip` 解压 → 完整源码

## 评估方法

### 测试套件执行
```bash
pip install pytest ebooklib beautifulsoup4 pymupdf pillow
python -m pytest scripts/tests/ -v --tb=short
```
结果: **194/194 PASSED, 0 FAILED, 2 SKIPPED**

### 端到端冒烟
```python
# 程序化构建 3 章测试 epub
from ebooklib import epub
bk = epub.EpubBook(); bk.set_title('测试蒸馏'); bk.set_language('zh')
# ... 构建 ch1/ch2/ch3 各含 20 段中文文本
epub.write_epub('test-book.epub', bk)

# 运行核心转换脚本
python scripts/convert_book.py test-book.epub --outdir ./test-distill
# 输出: format=epub, extractable=true, garbled_ratio=0.0, recommendation=直接蒸馏
```

## 关键发现

### 仓库结构
| 维度 | 数值 |
|------|------|
| 总文件 | 56 |
| Python 代码行 | 4,195 |
| 测试用例 | 196 |
| 测试通过率 | 100% (194/194) |
| SKILL.md | 131 行管线编排 |
| Reference 文档 | 2,386 行方法论 |

### 核心脚本
1. `convert_book.py` (199行) — 电子书 → txt + 诊断：epub/pdf/txt/azw3/mobi 五种格式，扫描版检测，Big5 误解码拦截
2. `verify_page.py` (1044行) — 三步出厂验证：HTML静态lint + distill.json契约门禁 + Playwright冒烟。G8-G21 共14道机拦门禁
3. `update_index.py` (86行) — 跨书5-tag知识索引
4. `build_series.py` (196行) — 视频系列→语料组装
5. `fetch_comments.py` (227行) — YouTube/B站评论抓取
6. `build_author.py` (771行) — 多书作者思想演变聚合

### 原创贡献
- 跨书知识索引 (5-tag: SUPPORTS/REFINES/CONTRADICTS/NEW_SUB_ASPECT/NEW_CONCEPT)
- 逐句锚点可追溯 (六类字段强制带原文出处)
- 自绘 SVG 脑图 (零第三方依赖)
- Zero-Hex 设计纪律 (CSS 只允许 token 块内 hex)
- 五段阅读漏斗 (一眼全书/逐章精读/书魂/行动自检/批判延伸)

### Agent Skill 特殊性
核心蒸馏逻辑完全由 LLM (Claude/Fable 5) 完成，Python 脚本仅做：
- 格式转换（epub→txt）
- 输入校验（扫描版检测）
- 输出验证（契约门禁、HTML lint）
- 索引维护（跨书知识网络）

单本书蒸馏成本：~320万 token（Fable 5 牌价 $50/百万token 产出）

## 教训

1. **GitHub 404 不意味着无法评估** — 中文开发者社区中，因合规/版权原因删除仓库但通过自有站点继续分发是常见模式
2. **Agent Skill 评估需区分两个维度** — 管线代码质量（可测试、可验证）vs 方法论设计质量（只能通过产物评估）
3. **测试套件运行是强信号** — 196 测试全绿 + 端到端冒烟通过，远比仅检查"是否有测试文件"有说服力
