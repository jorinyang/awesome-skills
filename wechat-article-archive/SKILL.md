---
name: wechat-article-archive
description: 微信公众号文章采集归档器——从公开文章链接出发，识别博主、采集最近N篇文章、保存为Markdown归档（含图片本地化）、生成文章清单CSV、按需调用 author-methodology-analysis 做方法论分析、默认生成HTML看板并同步飞书、最终打包ZIP。适用于"采集公众号最近N篇""公众号文章带图Markdown归档""归档后分析作者方法论""竞品公众号内容监控"等请求。不用于绕过登录、验证码、反爬或获取私密内容。
version: 1.0.0
author: Hermes Agent (adapted from freestylefly/wechat-article-archive-skill by 苍何)
license: MIT
source: https://github.com/freestylefly/wechat-article-archive-skill
metadata:
  hermes:
    tags: [wechat, archive, content-collection, markdown, intelligence, competitor-research]
    related_skills: [author-methodology-analysis, travel-intel, lark-doc, double-evolution]
    category: content
---

# 微信公众号文章归档器

> 来源：freestylefly/wechat-article-archive-skill（作者苍何），适配为 Hermes Skill 格式。
> 原始许可：MIT

## 概述

从用户提供的公开微信公众号文章链接出发，自动识别博主身份，采集可公开访问的文章正文与图片，按公众号隔离保存为本地 Markdown 归档，生成文章清单，并按需调用 `author-methodology-analysis` 生成方法论报告与文案框架。进入分析流程后默认自动生成 HTML 看板并同步飞书，最后校验并打包 ZIP。

## 触发条件

### 通用领域触发矩阵

覆盖 5 大领域、25 个子场景。自动识别触发。

#### AI 领域
| 场景 | 触发信号 |
|------|---------|
| AI产品竞品监控 | "采集XX AI公司的公众号文章""归档 OpenAI/Anthropic 公众号" |
| AI行业趋势追踪 | "抓一下AI行业KOL最近的文章""归档歸藏/宝玉的公众号" |
| AI博主方法论学习 | "采集XX的公众号，分析他的写作方法论" |
| AI训练语料收集 | "归档这些AI技术文章作为参考语料" |

#### 咨询领域
| 场景 | 触发信号 |
|------|---------|
| 客户行业快速研究 | "帮我采集XX行业的公众号文章做研究""快速建立XX行业的公众号内容档案" |
| 竞品情报交付 | "把竞品的公众号文章全部归档""采集XX公司的公众号历史文章" |
| 行业最佳实践采集 | "归档行业头部公司的公众号""采集行业协会的公众号内容" |
| 尽调辅助 | "做DD需要这个公司的公开公众号内容" |

#### 企业管理领域
| 场景 | 触发信号 |
|------|---------|
| 行业政策追踪 | "自动追踪XX部门的公众号""监控行业协会的公众号更新" |
| 知识管理基础设施 | "把内部公众号文章归档到知识库""建立公司公众号内容档案" |
| 品牌内容资产管理 | "归档我们自己的公众号历史文章""整理企业公众号内容库" |
| 竞品动态监控 | "持续监控竞品公众号""追踪XX公司的公众号更新" |

#### 数字化领域
| 场景 | 触发信号 |
|------|---------|
| 内容数字化转型 | "把公众号文章导出为Markdown""微信文章转本地归档" |
| 数据主权迁移 | "把微信平台的文章迁出来""公众号内容脱离微信保存" |
| 多平台内容聚合 | "把公众号文章同步到飞书知识库" |

#### 通用内容采集
| 场景 | 触发信号 |
|------|---------|
| 公众号文章归档 | "公众号文章归档""采集公众号最近N篇""公众号带图Markdown" |
| 博主内容采集 | "采集这个博主的所有文章""抓取XX公众号的内容" |
| 批量公众号处理 | "采集这几个公众号""批量归档公众号" |

### 手动触发关键词
采集公众号、公众号归档、公众号文章下载、微信文章转Markdown、公众号内容监控、归档公众号、抓取公众号、公众号图片本地化、公众号ZIP打包、wechat-article-archive、微信文章采集、公众号批量采集

### 不触发
- 需要登录/付费才能访问的私密内容
- 绕过验证码或反爬机制的请求
- 非微信公众号平台的内容

---

## 默认行为

- 只采集用户有权访问的公开内容，正文抓取不使用 Cookie
- 精确获取公众号历史列表时可由用户扫码登录微信公众平台，登录态仅保存在本地缓存
- 用户可自定义采集篇数；未指定时默认目标为最近 50 篇
- 默认生成文章归档、`<博主>-文章清单.csv` 和 ZIP
- 仅当用户要求分析作者方法论时，调用 `author-methodology-analysis`
- 进入方法论分析流程后，默认自动生成 HTML 看板并同步飞书
- 只有用户明确要求"不生成 HTML"或"不同步飞书"时才关闭对应产物
- 公开来源不足时交付实际数量，不伪造"最近 N 篇"或"完整历史"

---

## 唯一输出契约

先识别公众号名称和 `biz`，再确定：

```
author_root = <workspace>/output/<safe-author-name>/
```

若同名目录已属于其他 `biz`，使用 `<safe-author-name>-<biz-tail>`。

最终结构：

```
output/<safe-author-name>/
  <safe-author-name>-文章清单.csv
  articles/
    01-文章标题/
      <文章标题>.md
      images/
  <safe-author-name>-方法论报告.md          # 仅按需分析
  <safe-author-name>-文案框架.md            # 仅按需分析
  <safe-author-name>-分析数据.json           # 分析时生成
  <safe-author-name>-文章特征.csv            # 分析时生成
  <safe-author-name>-方法论看板.html          # 分析时默认生成
  <safe-author-name>-飞书同步.json            # 成功同步飞书后生成
  <safe-author-name>-文章归档.zip
```

---

## 工作流

### 1. 解析入口并锁定身份

🔴 CHECKPOINT — 入口解析前确认：提供的文章链接是否为公开的 `mp.weixin.qq.com` URL？是否可公开访问（无需登录/付费）？

从入口文章提取：标题（`#activity-name` / `msg_title`）、公众号名（`#js_name` / `nickname`）、`__biz` / `biz`、`mid` / `appmsgid`、`idx`、`sn`、发布时间、合集信息。

### 2. 锁定候选列表

🔴 CHECKPOINT — 候选列表生成前确认：是否需要扫码登录微信公众平台？扫码人是否就位（手机在身边）？采集篇数是否已指定（默认 50）？

候选字段至少包括：`title, url, publish_time, source_type, accessible, biz, mid, idx, sn`

来源优先级：
1. 用户扫码授权后的微信公众平台文章历史列表
2. 无需登录即可分页的公众号公开历史入口
3. 公开合集/专辑
4. 当前文章页显式内链
5. 最多两轮公开搜索补充
6. 经身份核验的本地既有归档

候选按 `biz + mid + idx + sn` 和规范化 URL 去重。

用户要求"最近 N 篇"时，优先使用确定性历史列表脚本：

```bash
python3 scripts/discover_account_articles.py \
  --account "<公众号精确名称>" \
  --limit <N> \
  --output "<workspace>/tmp/<safe-author-name>-candidates.csv"
```

首次运行会生成二维码，用户扫码确认后，登录态保存到 `~/.cache/wechat-article-archive/session.json`。

### 3. 抓取正文与图片

🔴 CHECKPOINT — 抓取启动前确认：候选列表是否已去重？是否只包含 `mp.weixin.qq.com` 公开 URL？`author_root` 目录是否已创建且不与已有公众号冲突？采集延迟和并发设置是否合理（串行 + 2s 延迟）？

```bash
python3 scripts/collect_articles.py \
  --author-root "<author_root>" \
  --candidate-csv "<candidate_csv>" \
  --limit <N> \
  --workers 1 \
  --image-workers 2 \
  --article-delay 2 \
  --resume
```

- 只接受 `mp.weixin.qq.com` 公开文章 URL
- 正文容器优先 `#js_content`，其次 `.rich_media_content`
- 图片按正文顺序下载到 `images/image-01.<ext>`
- 默认串行采集，请求间隔 2 秒
- 正文和图片请求默认失败重试 2 次并指数退避

Markdown 顶部元数据：

```markdown
# 文章标题

- 公众号：<名称>
- 原文链接：<url>
- 发布时间：<YYYY-MM-DD HH:mm:ss 或未知>
- 采集来源：<source_type>
---
```

### 4. 生成文章清单

`<博主>-文章清单.csv` 使用 UTF-8 BOM，至少包含：
`index, title, url, publish_time, error, author_name, article_dir, markdown_file`

### 5. 分析编排（可选）

🔴 CHECKPOINT — 方法论分析启动前确认：用户是否明确要求分析作者方法论？是否已归档 ≥3 篇文章（不足则跳过分析）？HTML 看板和飞书同步是否需关闭（默认开启）？

用户要求方法论分析时，调用 `author-methodology-analysis`，传入：
- `input_dir = <author_root>/articles`
- `output_dir = <author_root>`
- `author_name`
- `article_list = <author_root>/<safe-author-name>-文章清单.csv`
- `generate_html = true`（除非用户明确关闭）
- `sync_lark = true`（除非用户明确关闭）

### 6. 校验与打包

🔴 CHECKPOINT — 打包前确认：所有文章正文是否已抓取完成？图片是否已本地化且引用正确？CSV 是否 UTF-8 BOM 格式？是否已排除不可访问的候选？

```bash
python3 scripts/validate_archive.py "<author_root>"
python3 scripts/package_archive.py "<author_root>"
python3 scripts/validate_archive.py "<author_root>" --zip "<zip_path>"
```

---

## 失败边界

- 微信公众平台历史列表会话失效：删除本地缓存并提示重新扫码
- 搜狗或其他跳转触发验证码：立即停止该路径
- 入口文章不可公开访问：说明限制并请求可访问链接
- 不可访问的搜索结果不得进入最终包
- 转载内容不得标记为公众号原文

## 失败模式与恢复

| 触发条件 | 症状 | 一线修复 | 仍失败兜底 |
|---|---|---|---|
| QR 扫码超时 | `discover_account_articles.py` 超时退出（exit≠0） | 删除 `wechat-login-qr.jpg` 和本地缓存，用 `--login-timeout 300` 重新运行 | 改用公开搜索/合集/内链等无需扫码的来源 |
| Session 缓存被 kill 丢失 | 进程被 kill 后 `~/.cache/wechat-article-archive/session.json` 不存在 | 确认进程正常 exit 0 退出（非 kill），session 只在正常退出时写入 | 重新扫码获取新 session |
| 文章页面触发验证码 | `collect_articles.py` 返回空正文或验证码页面 | 立即停止该 URL 的请求，标记为不可访问 | 跳过该文章，继续采集其他可访问文章 |
| 公众号名称精确匹配失败 | `discover` 脚本输出 "未找到匹配的公众号" | 用 `--fakeid` 精确选择（从候选列表中获取） | 让用户提供该公众号的 `biz` 或直接文章链接 |
| 图片下载失败 | `images/` 目录下图片缺失或 404 | 重试 2 次（脚本默认），检查图片 URL 是否过期 | 标记图片失败数，正文中用 `[图片获取失败]` 占位 |
| 候选列表为空 | `collect_articles.py` 收到空 CSV | 检查 `discover` 脚本是否正常完成，尝试不同来源优先级 | 让用户提供更多公开文章链接，手动构建候选列表 |
| 微信改版导致选择器失效 | `#js_content` / `.rich_media_content` 均无匹配 | 检查页面源码是否变更，尝试通用内容选择器 | 用 `firecrawl_scrape` 替代直接抓取，等待脚本更新 |

## 最终回复

简要报告：实际归档数与失败数、来源范围、发布时间未知数、图片失败数、校验结果、方法论/HTML/飞书完成情况、ZIP 本地绝对路径。

---

## 资源

## 资源

> ⚠️ Python 脚本需从上游仓库安装到技能 scripts/ 目录：`git clone https://github.com/freestylefly/wechat-article-archive-skill.git /tmp/waa && cp /tmp/waa/scripts/*.py <skill_dir>/scripts/`。依赖 `requests` + `lxml`，需在 venv 中可用。

本技能 Python 脚本源自 `freestylefly/wechat-article-archive-skill`：
- `scripts/discover_account_articles.py` — 扫码登录微信公众平台，生成候选列表
- `scripts/collect_articles.py` — 抓取正文、转换 Markdown、本地化图片
- `scripts/validate_archive.py` — 校验目录、CSV、Markdown、图片引用和 ZIP
- `scripts/package_archive.py` — 以 UTF-8 文件名创建 ZIP
- `scripts/archive_common.py` — 共享 CSV Schema、安全路径规则

## QR 码登录工作流 ★ (2026-06-18 实战验证)

首次采集某个公众号必须扫码。**不能在 foreground 直接跑**（用户看不到终端 stdout 里的 QR 码文本），必须按以下流程操作（已验证四次后成功）：

```
1. 用 --login-timeout 300 后台启动（默认 180s 不够）
   terminal(background=true, notify_on_complete=true,
     "python3 -u scripts/discover_account_articles.py
      --account \"<名称>\" --limit <N> --login-timeout 300
      --output <csv_path>")

2. 等 3 秒让 QR 文件写入磁盘
   sleep 3 && ls <skill_dir>/wechat-login-qr.jpg

3. 立刻将 QR 码文件发到飞书（用户手机在飞书里可以直接长按识别）
   send_message("📱 微信扫码（5分钟内有效）
                 MEDIA:<skill_dir>/wechat-login-qr.jpg", target="feishu")

4. 等用户扫码 → 监听 notify_on_complete 通知
```

**关键约束**：
- QR 文件由脚本写入磁盘（`<cwd>/wechat-login-qr.jpg`），与 stdout 输出独立——所以即使 background 缓冲了 stdout，QR 文件仍然可读
- Session 缓存路径：`~/.cache/wechat-article-archive/session.json`（权限 0600）
- 进程被 kill 时 session 不会保存。正常 exit code 0 退出后 session 自动缓存
- 缓存后同号下次不再需要扫码，直接复用

## QR 码登录工作流 ★

首次采集新公众号必须扫码。正确流程（已验证）：

```
1. 后台启动 discover 脚本（300s 超时）
   terminal(background=true, notify_on_complete=true,
     "python3 -u scripts/discover_account_articles.py
      --account \"<名称>\" --limit <N> --login-timeout 300
      --output <path>")

2. 等 3 秒让 QR 文件生成
   sleep 3 && ls wechat-login-qr.jpg

3. 立刻将 QR 码发到飞书
   send_message("📱 微信扫码（5分钟内有效）
                 MEDIA:<skill_dir>/wechat-login-qr.jpg", target="feishu")

4. 等用户扫码 → process poll 或等 notify_on_complete
```

**为什么不能 foreground 直接跑**：foreground 模式下 QR 码打印到终端 stdout，但用户看不到终端输出。必须发到飞书。

**为什么不能后台跑完再发 QR**：后台 Python 输出被缓冲，`process poll` 始终返回空。QR 文件是独立写入磁盘的，可以检测到。

**关键参数**：`--login-timeout 300`（默认 180s 不够——从发 QR 到用户看到并扫码，180s 很紧）

## 常见陷阱

1. **扫码人未就位** — 首次采集新公众号需要手机扫码。跑脚本前确认扫码人可用
2. **QR 码超时（最高频陷阱）** — 默认 `--login-timeout 180` 偏紧。从生成 QR → 发飞书 → 用户打开飞书 → 长按识别，180s 经常不够。**必须用 `--login-timeout 300`**
3. **Foreground 跑 QR 登录** — 脚本在 foreground 会打印 QR 文本到 stdout 然后阻塞等待。用户看不到终端输出。**必须用 background 模式 + 检测 QR 文件写入 + 发飞书**
4. **Background Python 缓冲导致空 output** — `process poll` 对 background Python 进程始终返回空。不要依赖 poll 来判断 QR 是否生成——用 `ls wechat-login-qr.jpg` 检测文件
5. **Session 缓存被 kill 丢失** — 如果进程被 kill（非正常 exit 0），session 不会写入 `~/.cache/wechat-article-archive/session.json`。必须等进程正常退出后 session 才持久化
6. **微信改版导致脚本失效** — 脚本有降级策略（公开搜索/合集），非完全依赖后台接口
7. **高频采集触发风控** — 默认串行+2s延迟，不建议调高并发
8. **公众号名称精确匹配失败** — 用 `--fakeid` 精确选择（从候选列表中获取）+ 检测 QR 文件写入 + 发飞书**
4. **Background Python 缓冲导致空 output** — `process poll` 对 background Python 进程始终返回空。不要依赖 poll 来判断 QR 是否生成——用 `ls wechat-login-qr.jpg` 检测文件
5. **Session 缓存被 kill 丢失** — 如果进程被 kill（非正常 exit 0），session 不会写入 `~/.cache/wechat-article-archive/session.json`。必须等进程正常退出后 session 才持久化
6. **微信改版导致脚本失效** — 脚本有降级策略（公开搜索/合集），非完全依赖后台接口
7. **高频采集触发风控** — 默认串行+2s延迟，不建议调高并发
8. **公众号名称精确匹配失败** — 用 `--fakeid` 精确选择（从候选列表中获取）

## 验证清单

- [ ] 入口文章可公开访问
- [ ] 公众号名称和 biz 已确认
- [ ] 输出目录结构符合契约
- [ ] 文章清单 CSV UTF-8 BOM 格式正确
- [ ] Markdown 元数据完整
- [ ] 图片本地化无失效引用
- [ ] ZIP 二次校验通过
- [ ] 若分析：方法论报告/HTML/飞书均存在

## ⛔ 反例与禁止

- ❌ **采集需要登录/付费/验证码的内容** — 只采集公开可访问文章，遇到验证码立即停止
- ❌ **在 foreground 跑 QR 登录** — 用户看不到终端 stdout，必须用 background 模式 + 发飞书 QR
- ❌ **QR 扫码用默认 180s 超时** — 从发 QR 到用户扫码经常超过 180s，必须用 `--login-timeout 300`
- ❌ **并发采集或缩短延迟** — 默认串行 + 2s 延迟，调高并发或缩短延迟会触发风控
- ❌ **依赖 `process poll` 判断 QR 是否生成** — background Python 输出被缓冲，用 `ls wechat-login-qr.jpg` 检测文件
- ❌ **kill 进程后期望 session 可用** — session 只在正常 exit 0 时写入，kill 会导致缓存丢失
- ❌ **伪造\"最近 N 篇\"或\"完整历史\"** — 公开来源不足时交付实际数量，不虚构
