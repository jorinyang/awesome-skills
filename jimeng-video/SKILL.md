---
name: jimeng-video
description: 即梦/CapCut AI视频与图片生成 — CLI安装、token管理、文生视频/图生视频/omni_reference。内置情绪导演 Prompt 工程核心方法论（物理优先、六段式结构、情绪→生理转化），接入AI Native Workflow
triggers:
  - 生成视频/制作视频/AI视频
  - 即梦/jimeng/dreamina/CapCut 相关
  - 视频素材自动生成
  - prompt工程/视频提示词/分镜脚本/情绪导演
  - 写prompt/优化prompt/视频prompt
related_skills: [double-evolution]
tags: [jimeng, video-generation, image-generation, ai-native, capcut, dreamina, prompt-engineering, emotion-director]
category: travel
---

# Jimeng Video — 即梦 CLI 视频/图片生成

## 概述

即梦 CLI（`jimeng-cli`）是字节跳动官方提供的 Agent 工具包，让 AI Agent 通过命令行调用即梦（Dreamina）/CapCut 的图像和视频生成能力。

- **npm 包**: `jimeng-cli@0.3.9`
- **作者**: Jimeng CLI Team (ByteDance)
- **许可证**: GPL-3.0
- **发布时间**: 2026-05-01
- **官方文档**: https://bytedance.larkoffice.com/wiki/FVTwwm0bGiishxkKOoScdHR2nsg

### 当前环境状态

| 项目 | 值 |
|------|-----|
| 安装状态 | ✅ 已安装 |
| Token | ✅ 已配置 (cn, credits: 2,238) |
| 图片生成 | ✅ 已验证 (jimeng-4.5, 2560×1440) |
| 视频 3.0-fast | ✅ 可用 |
| 视频 3.0-pro | ✅ 可用 |
| 视频 3.5-pro | ✅ 可用 (原报 1006 已恢复) |
| **Seedance 2.0** | **❌ 账户不可用** — `models list` 中无此模型，omni_reference 模式不可用 |
| 默认视频模型 | ❌ jimeng-video-3.0 已下线 (错误码 2061) |

## 安装

```bash
npm install -g jimeng-cli
```

三个可执行文件：
- `jimeng-cli` — CLI 入口
- `jimeng` — 别名（推荐使用）
- `jimeng-mcp` — MCP 服务器入口

**环境要求**：
- Node.js
- Python 3（浏览器自动登录需要）
- Chrome/Chromium（浏览器自动登录需要）

## 认证（登录）

### 方式一：sessionid 注入（推荐，免浏览器）

```bash
# 1. 从浏览器获取 sessionid
#    打开 https://jimeng.jianying.com/ai-tool/home/ → 登录
#    F12 → Application → Cookies → jimeng.jianying.com → sessionid

# 2. 注入 token
jimeng login --sessionid <your_sessionid> --region cn
```

### 方式二：浏览器自动登录

```bash
jimeng login --region cn
# 自动打开 Chrome，扫码登录
# WSL 环境需确保 Chrome 在 PATH 中
```

### 方式三：官方一键安装脚本

```bash
curl -s https://jimeng.jianying.com/cli | bash
```

### Token 管理

```bash
jimeng token list          # 列出所有 token
jimeng token check         # 验证 token
jimeng token points        # 查询积分
jimeng token pool          # 查看 token 池状态
jimeng token add ...       # 添加 token
jimeng token remove ...    # 移除 token
```

配置目录：`~/.dreamina_cli/`
日志目录：`~/.dreamina_cli/logs/`

## 核心命令

### 模型查询

```bash
jimeng models list          # 列出可用模型
jimeng models refresh       # 刷新模型列表
```

### 图片生成

```bash
# 文生图
jimeng image generate \
  --prompt "贵州万峰林日出，云雾缭绕，航拍视角" \
  --model jimeng-4.5 \
  --ratio 16:9 \
  --resolution 2k

# 图编辑
jimeng image edit --prompt "..." --image-file ./input.png

# 超分
jimeng image upscale --image-file ./input.png
```

**默认模型**: `jimeng-4.5`，默认分辨率 `2k`，默认比例 `1:1`

> **每 prompt 产出 4 张变体**：`jimeng-4.5` 一次生成返回 4 个不同结果的 URL。`--no-wait` 模式下 `task get` 会列出全部 4 个 URL。批量生成用 `--no-wait` + 轮询 + curl 下载，详见 `references/batch-image-generation.md`。

### 视频生成（4种模式）

| 模式 | 命令 flag | 输入要求 | 默认模型 | 可用？ |
|------|----------|---------|---------|--------|
| 文生视频 | `--mode text_to_video` | 仅 prompt | jimeng-video-3.0 | ✅ |
| 图生视频 | `--mode image_to_video` | 1张图 + prompt | jimeng-video-3.0 | ✅ |
| 首尾帧 | `--mode first_last_frames` | 1-2张图 + prompt | jimeng-video-3.0 | ✅ |
| 全能参考 | `--mode omni_reference` | 1-9张图 + 0-3视频 + prompt | seedance-2.0-fast | ❌ 账户无此模型 |

> **⚠️ omni_reference 不可用时的替代方案**：使用 `image_to_video` 模式，所有镜头共用**同一张**参考图（建议选最具代表性的基地全景图），通过 prompt 分别描述每个镜头的独特内容。一致性靠共享的参考图锚定，细节靠 prompt 引导。详见 `references/multi-shot-without-seedance.md`。

> ⚠️ **omni_reference 不可用**：该模式强制要求 `jimeng-video-seedance-2.0` 或 `jimeng-video-seedance-2.0-fast`，这两个模型不在当前账户的 `models list` 中。尝试使用会报错：`region 已匹配，但无 token 支持模型 jimeng-video-seedance-2.0-fast`。
>
> **多镜头一致性降级方案**：用 `image_to_video` 替代，选一张最能代表整体场景的参考图（如基地航拍全景），所有镜头共用同一张图作为视觉锚定。每个镜头用不同的 prompt 描述具体画面、运镜和动作。一致性不如 omni_reference，但在无 seedance 的条件下是最佳方案。

```bash
# 文生视频
jimeng video generate \
  --mode text_to_video \
  --prompt "万峰林日落延时，云雾从山谷升起，金色光线穿过山峰" \
  --ratio 16:9 \
  --duration 5 \
  --resolution 720p

# 图生视频（从静态图生成动态视频）
jimeng video generate \
  --mode image_to_video \
  --prompt "Camera slowly pushes in, mist flowing" \
  --image-file ./wanfenglin.png \
  --duration 5

# 首尾帧过渡
jimeng video generate \
  --mode first_last_frames \
  --prompt "Day to night transition over karst mountains" \
  --image-file ./day.png \
  --image-file ./night.png

# 全能参考（多素材混合）— 注意：omni_reference 使用编号参数！
jimeng video generate \
  --mode omni_reference \
  --model jimeng-video-seedance-2.0-fast \
  --prompt "Use @image_file_1 as character reference, @image_file_2 as location, @video_file_1 for motion style" \
  --image-file-1 ./char_ref.png \
  --image-file-2 ./bg.png \
  --image-file-3 ./style.png \
  --video-file-1 ./motion_ref.mp4 \
  --duration 5 \
  --ratio 16:9
```

**默认参数**: 分辨率 `720p`，时长 `5s`，比例 `1:1`

### 任务管理

```bash
jimeng task get <task_id>     # 查询任务状态
jimeng task wait <task_id>    # 等待任务完成
jimeng task list              # 查看历史任务
```

**异步模式**：加 `--no-wait` 立即返回 task_id，后续用 `task wait` 轮询。

## AI Native Workflow 集成点

### 1. 行程视频预览（trip-landing 增强）

```
用户行程方案 → trip-landing 提取景点 → mmx search query 搜索景点参考图
→ mmx vision describe 分析参考图 → jimeng text_to_video 生成预览视频
→ 嵌入落地页 → OSS 部署
```

### 2. 营销素材自动生成

```
travel-monitor 采集竞品 → mmx vision describe 分析竞品视觉
→ 提取差异化卖点 → jimeng image generate 海报图
→ jimeng video generate 短视频 → 归档至文案素材
```

### 3. 客户方案视频化

```
feishu-doc 行程方案 → 提取关键帧描述 → mmx vision describe 分析目的地参考图
→ jimeng first_last_frames / omni_reference 生成过渡视频
→ 嵌入方案文档
```

### 4. 定时批量生成

```
cron: 每周一 9:00 → 读取文案素材库最新行程
→ jimeng image generate --prompt 批量生成宣传图
→ 输出至 OSS → 更新素材库
```

## 与现有技能的关系

| 技能 | 集成方式 |
|------|---------|
| `trip-landing` | 落地页嵌入 AI 生成视频 |
| `travel-monitor` | 竞品分析 → 自动生成对比视频 |
| `feishu-doc` | 方案文档嵌入视频素材 |
| `huashu-design` | 设计原型嵌入 AI 图片 |

## 多镜头视频生成

需要按分镜脚本生成多个镜头后拼接成片？见 `references/seedance-multi-shot-workflow.md`。核心要点：各镜头共用同一组 `--image-file-N` 参考图维持一致性，用 ffmpeg 拼接。

**Seedance 不可用时** → 见 `references/multi-shot-without-seedance.md`：用 `image_to_video` + 单张锚定图替代，所有镜头共用同一参考图。

**完整生产线（含配音+配乐+ffmpeg组装）** → 见 `references/video-production-pipeline.md`。

需要将完整宣传片脚本（10+ 分镜）分解为 6-8 个 Seedance 生成任务？见 `references/script-to-seedance-decomposition.md`。方法论：分类→合并同类镜→标注不可生成→写 prompt→汇编。

ffmpeg 精剪拼接模板（trim/slow/montage/logo）见 `references/ffmpeg-assembly-pattern.md`。

## ⚠️ 铁律（违反即返工）

### 铁律 1：单次视频生成 ≤ 15 秒

即梦长视频（>15s）质量急剧下降，画面崩坏、抖动、形变。**任何视频生成任务，单次 --duration 不得超过 15 秒。**

如需更长成片，拆分为多个 ≤15s 镜头分别生成后 ffmpeg 拼接。

### 铁律 2：每个镜头必须有参考主体图（推荐 image_to_video）

所有视频镜头**必须有至少一张参考图控制视觉方向**，禁止纯 `text_to_video`（无图控制、结果随机）。

推荐模式（按优先级）：
1. **`image_to_video`**（首选，生产最常用）：一张高质量参考图 + 详细 prompt。单图足够锚定场景色调、构图和主体。
2. **`first_last_frames`**（需要精确过渡时使用）：首帧图 + 尾帧图，控制起始和结束画面。仅当需要精确的场景转换时使用。

> `video-production-pipeline.md` 使用 `image_to_video` 作为生产工作流，已验证效果可靠。

首尾帧图来源：
1. 用户提供的参考图（优先）
2. 即梦图片生成先产出关键帧（`jimeng image generate`）
3. 从现有视频截取代表性帧（`ffmpeg -i input.mp4 -ss 2 -vframes 1 frame.png`）

### 铁律 3：多镜头任务先拆后拼

多镜头视频 → 逐镜头独立生成（每镜 ≤15s、带首尾帧）→ ffmpeg concat 拼接。

---

## 🎬 Prompt 工程核心：情绪导演方法论

> 完整方法论见 [`references/emotion-director-prompt-engineering.md`](references/emotion-director-prompt-engineering.md)。本方法论吸收自 Seedance 2.0 情绪导演 SKILL v2.1，已适配所有 jimeng 视频模型。

### 核心铁律（prompt 书写层面）

1. **禁止文学化修辞**：无比喻、拟人、象征、夸张 → 全部替换为物理世界直接描述
2. **物理优先**：光线/动作/表情/声音/空间全部用 AI 可理解的相对化描述（光源位置、身体参照、明暗对比、色温倾向）
3. **时间轴精确到秒**：逐秒拆分，景别+动作+神态+台词
4. **字数 ≤ 1900 字**：含标点，超限按优先级压缩

### 数值替换对照（强制）

| 禁止 ❌ | 替换 ✅ |
|---------|--------|
| X厘米/秒、X米、X毫米 | 身体参照（一臂距离/一拳之隔）或画面比例（人物占画面一半） |
| X度、X:X 受光比 | 低/高角度、面部半明半暗/几乎无阴影 |
| X次/秒 | 频繁/间隔变长/几乎不 |

### 情绪→生理转化表（最常用）

| 情绪 | 可拍摄的生理表现 |
|------|-----------------|
| 恐惧 | 瞳孔扩大，胸口快速起伏，手指轻颤，身体后缩 |
| 愤怒 | 下颌肌肉隆起，颈部青筋可见，拳头紧握指节发白 |
| 悲伤 | 眼睑下垂，嘴角下拉，肩膀内收，头部低垂 |
| 喜悦 | 嘴角上扬，眼角出现皱纹，身体舒展 |
| 绝望 | 瞳孔涣散失焦，头部无力下垂，双手垂落 |

### 六段式 Prompt 结构

**所有视频 prompt 严格按此结构输出**：

```
一、视听限制 —— 无BGM/纯环境音/禁止字幕水印
二、语言台词 —— 语种、语速、音量、音质标注
三、运镜手法 —— 方式、运动轨迹、镜头是否移动、与角色关系
四、风格色调与光景 —— 视觉风格、色彩调性、光源位置+色温
五、角色与场景设定 —— 外貌（相对描述）、服装、地点、时间、环境要素
六、时间轴详细叙事 —— 按秒拆分：[0-5s] 景别/动作(起点→过程→终点)/神态(肌肉运动)/台词(音量标注)/声音设计
```

### 动作四层次（防止 AI 木偶化）

| 层次 | 定义 | 示例 |
|------|------|------|
| 微动作 | 无意识小动作 | 指尖轻颤、脚尖点地 |
| 惯性动作 | 情绪驱动习惯 | 紧张摸耳垂、焦虑搓手指 |
| 神经反应 | 突发本能反应 | 瞳孔震动、吞咽、重心失衡 |
| 失控反应 | 情绪峰值失控 | 肩膀剧烈抖动、膝盖发软 |

### 降级适配说明（Seedance 不可用时）

本方法论原为 Seedance 2.0 设计，当前环境 Seedance 不可用。适配 jimeng-video-3.5-pro 时：
- 六段式结构和物理优先原则**完全适用**，保持不变
- 单镜头 ≤ 5s（3.5-pro 的实际输出上限），多镜头拼接
- 多镜头一致性靠**共享参考图**锚定（`image_to_video` + 同一张 `--image-file`），详见 [`references/multi-shot-without-seedance.md`](references/multi-shot-without-seedance.md)
- `omni_reference` 的多素材融合能力不可用，所有视觉控制靠单图 + prompt

---

## 宣传片制作：脚本优先工作流

用户要求制作宣传视频时，**先交付可执行的制作脚本，不要直接消耗积分生成**。用户偏好自己审查脚本后决定是否执行。

流程：
1. 设计分镜脚本（时间轴 + 钩子文案）
2. 写出完整 bash 脚本（图片→视频→ffmpeg拼接→文字叠加→BGM）
3. 先交付脚本，确认后再执行

脚本模板见 `templates/promo-video.sh`。

## 常见问题

### WSL 环境登录
自动浏览器登录在 WSL 中可能失败（Chrome 路径问题）。
→ 使用 sessionid 注入方式：手动从浏览器复制 sessionid → `jimeng login --sessionid <值>`

### Token 过期
```bash
jimeng token check    # 检查所有 token 状态
jimeng login ...      # 重新登录添加新 token
```

### 任务超时
生成任务默认等待，可能超时（尤其是视频）。
→ 使用 `--no-wait` + `task wait <id> --wait-timeout-seconds 600`

## 实测陷阱（2026-05-28 全流程验证）

详见 `references/verification-20260528.md` — 完整安装/登录/图片/视频/3.5-pro 批量生成记录。

- **npm 全局安装后 bin 可能不在 PATH**：使用 `node $(npm root -g)/jimeng-cli/dist/cli/index.js` 直接调用
- **`jimeng-cli` 命令可能不可用**：bin 链接在 WSL 中未正确创建，使用 `node` 直接执行
- **WSL 浏览器登录失败**：CLI 的 Python 自动化登录脚本在 WSL 中可能无法找到 Chrome。使用 `--sessionid` 手动注入
- **sessionid 来源**：即梦域名 `jimeng.jianying.com`，用 `jimeng login --sessionid <值> --region cn` 注入
- **region 默认 cn**：国内用户无需指定，国外需 `--region us/hk/jp/sg`
- **视频生成耗时**：5s 视频通常 2-5 分钟，建议 `--no-wait` + `task wait`
- **默认视频模型不可用**：`jimeng-video-3.0` 已下线（错误码 2061），必须指定 `--model jimeng-video-3.0-fast` 或 `jimeng-video-3.0-pro`
- **`--duration` 实际输出上限 5s**：`jimeng-video-3.5-pro` 的 `--duration 8` / `--duration 7` 均输出 5s。`--duration` 参数被静默忽略，实际按 5s 生成。需要更长的片段用 `setpts` 慢放（`setpts=1.6*PTS` + `atempo=0.625` 可拉伸 5s→8s），或生成多个 5s 片段拼接
- **`--no-wait` 不下载文件**：`--no-wait` 模式下文件不会保存到 `--output-dir`。必须用 `task get --task-id <id>` 获取云端 URL，然后 curl 手动下载
- **`task get` 输出不是纯 JSON**：输出是带格式的人类可读文本（含 Status/Data/URL），用 grep 提取 URL，**不要**用 python json.load — 会抛 JSONDecodeError
- **任务状态码**：20=PROCESSING, 45=UNKNOWN（仍在处理中，可能卡住需重试）, 50=COMPLETED。45 并非错误，多数 2-3 分钟后转 50。若长时间 45 且无 URL，直接 resubmit — 重试通常立即完成
- **每 prompt 4 变体**：`jimeng-4.5` 图片生成每次返回 4 个不同结果的 URL，非 1 个
- **批量生成模式**：并行 `--no-wait` 提交 → shell 轮询 `task get` → `curl` 下载。详见 `references/batch-image-generation.md`

## 图片理解（MiniMax CLI `mmx-cli`）

用于分析参考图 → 提取视觉描述 → 嵌入 jimeng prompt 的工作流。这是 `mmx-cli` 在此项目中的核心用途。

> ℹ️ `mmx-cli` 还支持视频/图片/音乐/语音生成、网络搜索、文本对话等能力。完整命令参考见 [`references/minimax-cli-reference.md`](references/minimax-cli-reference.md)。

### 安装与配置

```bash
npm install -g mmx-cli
# WSL 环境 bin 不可用，使用 node 直接执行
MMX="node $(npm root -g)/mmx-cli/dist/mmx.mjs"
$MMX auth login --api-key <minimax-api-key>  # 自动检测 region cn
$MMX quota  # 查看配额
```

### 图片描述

```bash
$MMX vision describe --image ./ref.jpg --prompt "详细描述人物外观、服饰、场景色调"
# 输出 JSON：{"content": "...", "base_resp": {"status_code": 0}}
```

- 消耗 `coding-plan-vlm` 配额
- 支持本地路径和 URL
- 默认 prompt "Describe the image."，建议自定义中文 prompt 获得更精准描述

### 与 jimeng 集成

```
参考图 → mmx vision describe → 文字描述 → 嵌入 jimeng video generate --prompt
（无需切换视觉模型，无需人工描述）
```
- **积分限制**：`jimeng-video-3.5-pro` 需要更高额度，确认积分 > 2000 后可用
- **--wait 模式可能挂起**：图片生成使用 `--wait` 时，CLI 的轮询机制在完成后可能不退出，建议使用 `--no-wait` + 手动 `task get`
- **输出文件**: 图片 PNG、视频 MP4，默认输出到 `--output-dir` 指定的目录
- **--task-id 参数名**：`task get` 需要 `--task-id`（不是位置参数）
