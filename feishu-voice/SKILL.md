---
name: feishu-voice
description: >-
  飞书语音消息转录——收到 .ogg 语音文件或用户说"飞书语音/语音消息/听听这个"时自动触发，
  通过飞书妙记将语音转为逐字稿并返回文本内容。
  三步管线：drive上传 → minutes生成妙记 → vc读取逐字稿。
  触发词：飞书语音、语音消息、听听这个、转录语音、转文字、voice、transcribe。
version: 1.0.0
author: 杨瑒 (月夜)
metadata:
  hermes:
    tags: [feishu, voice, transcription, media]
    related_skills: [lark-minutes, double-evolution]
triggers:
  # 显式命令
  - "飞书语音"
  - "语音消息"
  - "听听这个"
  - "转录语音"
  - "转文字"
  - "voice"
  - "transcribe"
  # 收到音频附件时自动触发
  - ".ogg"
  - "audio_cache"
---

# feishu-voice — 飞书语音转录

> 将飞书语音消息（.ogg）转为文字。优先使用飞书原生 ASR API，秒级返回；超时/失败时回落妙记方案。

## 触发条件

### 自动触发
- 用户发送 `.ogg` 音频附件
- 消息中包含 `/audio_cache/` 路径的音频文件

### 手动触发
- "飞书语音" / "语音消息" / "转文字"
- "听听这个" / "转录语音"
- "voice" / "transcribe"

---

## 执行流程

### 决策：路径选择

🛑 **STOP — 路径决策前检查**：

1. 音频文件格式是否为 `.ogg`？→ 是，继续
2. 音频时长是否 ≤ 60 秒？→ 是，走路径 A；否，走路径 B
3. 飞书 ASR API scope 是否已授权？→ 检查 `lark-cli auth status | grep speech_to_text`

**规则**：优先路径 A（原生 API，2-3 秒出结果），失败自动切路径 B。不要问用户选哪个。

**音频时长检测**：
```bash
# 检查时长（秒），用于路径选择决策
ffprobe -v error -show_entries format=duration -of csv=p=0 {input.ogg}
```

### 路径 A：原生 ASR API（首选，≤60秒音频）

飞书开放平台提供原生语音识别 API，一步到位，比妙记方案快 5-10 倍。

**步骤**：

1. **转码**：`ffmpeg -i {input.ogg} -f s16le -acodec pcm_s16le -ar 16000 -ac 1 /tmp/audio.pcm`

   → 如果 ffmpeg 不可用：`sudo apt install ffmpeg -y`

2. **Base64 编码**：`base64 -w0 /tmp/audio.pcm > /tmp/audio.b64`

3. **调用 API**：
```bash
lark-cli api POST /open-apis/speech_to_text/v1/speech/file_recognize \
  --data '{"speech":{"speech":"'$(cat /tmp/audio.b64 | tr -d '\n')'"}, \
    "config":{"file_id":"'$(uuidgen | tr -d '-' | cut -c1-16)'", \
    "format":"pcm","engine_type":"16k_auto"}}' \
  --as user
```

4. 提取 `data.recognition_text` 返回给用户

   **响应解析示例**：
   ```json
   // API 成功响应结构
   {"code":0, "data":{"recognition_text":"转录出的文字内容"}}
   ```
   提取：`jq -r '.data.recognition_text'` 或 python3 `json.loads(resp)['data']['recognition_text']`

🔴 **CHECKPOINT — API 返回验证**：
- [ ] HTTP 200 → 提取文本
- [ ] `missing_scope` → 提示授权 `speech_to_text:speech`
- [ ] 超时/4xx/5xx → 自动切路径 B
- [ ] `recognition_text` 为空 → "未检测到有效语音内容"

**限制**：仅支持 PCM 格式，≤60 秒，需要 scope `speech_to_text:speech`，20 QPS。

### 路径 B：妙记转录（回落，>60秒或路径 A 失败时）

三步管线，适合长音频或非 PCM 格式。

1. `drive +upload` 上传文件获取 `file_token`
2. `minutes +upload` 生成妙记获取 `minute_token`

🛑 **STOP — 妙记未就绪**：
- `vc +notes` 可能返回 `"minute not ready, try later"`
- → 等待 8 秒后重试，最多重试 2 次
- → 2 次仍失败：报告 "妙记生成超时，请稍后重试"

3. `vc +notes --minute-tokens` 获取逐字稿
4. 读取 `transcript.txt`

### 输出

以引用格式展示转录文本。如转录为空 → "未检测到有效语音内容"。

### 完整示例

> 用户发送 30 秒 `.ogg` 语音 → 自动触发本技能

```
# 1. 检测时长
$ ffprobe -v error -show_entries format=duration -of csv=p=0 voice.ogg
30.5

# 2. ≤60秒 → 走路径 A
$ ffmpeg -i voice.ogg -f s16le -acodec pcm_s16le -ar 16000 -ac 1 /tmp/audio.pcm
$ base64 -w0 /tmp/audio.pcm > /tmp/audio.b64

# 3. 调用 ASR API
$ lark-cli api POST /open-apis/speech_to_text/v1/speech/file_recognize \
  --data '{"speech":{"speech":"...base64..."},"config":{...}}' --as user

# 4. 响应: {"code":0, "data":{"recognition_text":"今天天气真好"}}
# 输出: > 今天天气真好
```

---

## 失败模式

| 触发条件 | 症状 | 一线修复 | 仍失败兜底 |
|---------|------|---------|-----------|
| ffmpeg 未安装 | `command not found: ffmpeg` | `sudo apt install ffmpeg -y` | 路径 A 不可用，自动切路径 B |
| 音频非 `.ogg` 格式 | ffmpeg 解码失败 | 尝试 `ffmpeg -i {input}` 自动检测格式转 PCM | 报告 "不支持的音频格式，请发送 .ogg 文件" |
| 路径 A API 返回 `missing_scope` | API error 400 | 提示：`lark-cli auth login --scope speech_to_text:speech` | 自动切路径 B |
| 路径 A API 超时/5xx | 无响应或 HTTP 5xx | 自动切路径 B | — |
| `recognition_text` 字段为空 | API 200 但 text 为空 | → "未检测到有效语音内容" | — |
| 妙记返回 `minute not ready` | 转录未完成 | 等待 8 秒后重试，最多 2 次 | 报告 "妙记生成超时，请稍后重试" |
| `drive +upload` 失败 | 文件上传报错 | 检查 `.ogg` 文件是否损坏（`ffprobe {file}`） | 报告 "文件上传失败，请重新发送语音" |
| lark-cli 未登录 | `unauthorized` 或 token 过期 | `lark-cli auth login` | 报告 "飞书未授权，请先登录" |

## 所需权限

| 路径 | scope | 说明 |
|------|------|------|
| A (原生ASR) | `speech_to_text:speech` | 首次使用需扫码授权 |
| B (妙记) | `minutes:minutes.upload:write` | 上传音频生成妙记 |
| B (妙记) | `vc:note:read` | 读取妙记逐字稿 |
| B (妙记) | `minutes:minutes:readonly` | 读取妙记基本信息 |
| B (妙记) | `minutes:minutes.artifacts:read` | 读取 AI 转录产物 |

路径 B 批量授权：
```bash
lark-cli auth login --scope "minutes:minutes.upload:write vc:note:read minutes:minutes:readonly minutes:minutes.artifacts:read"
```

如果转录时返回 `missing_scope` 错误，对照上表补授权。

## 约束

- 优先走路径 A（原生 API，2-3秒），失败再走路径 B
- 如转录为空 → "未检测到有效语音内容"
- 不要问"要我转录吗"——收到语音直接转录
- 不缓存 file_token/minute_token 复用

## 参考

- [飞书原生 ASR API 速查](references/native-asr-api.md) — 端点/参数/错误码

## ⛔ 反例与禁止

- ❌ **不要用 ffmpeg/whisper 本地做完整语音识别** — ffmpeg 仅做 PCM 转码，识别必须走飞书 API（路径 A 或 B）
- ❌ **不要跳过路径 A 直接走路径 B** — 路径 A 快 10 倍且节省妙记配额
- ❌ **不要问用户选哪个路径** — 自动优先 A，失败自动切 B
- ❌ **不要在转录过程中展示中间步骤** — 只输出最终转录文本
- ❌ **不要缓存 file_token/minute_token 复用** — 每次转录重新生成
- ❌ **不要忽略 `missing_scope` 错误** — 必须提示用户补授权或自动切路径 B
