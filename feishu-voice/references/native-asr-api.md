# 飞书原生语音识别 API（替代妙记方案）

> 飞书开放平台 `speech_to_text/v1` 提供原生 ASR API，比 upload→minutes→vc 三步妙记方案快 5-10 倍。

## 接口

```
POST /open-apis/speech_to_text/v1/speech/file_recognize
```

## 权限

`speech_to_text:speech`（仅 1 个 scope，vs 妙记方案需 4 个）

## 限制

- 音频格式：仅 PCM，16k 采样率，单声道
- 时长：≤60 秒
- 频控：20 QPS/租户
- 引擎：16k_auto（中英混合）
- 免费版不支持

## 请求体

```json
{
  "speech": { "speech": "<base64-encoded PCM>" },
  "config": {
    "file_id": "<16位字母数字_下划线>",
    "format": "pcm",
    "engine_type": "16k_auto"
  }
}
```

## 响应

```json
{
  "code": 0,
  "data": { "recognition_text": "你好，使用飞书吧" }
}
```

## 完整流程

```bash
# 1. ogg → PCM
ffmpeg -i audio.ogg -f s16le -acodec pcm_s16le -ar 16000 -ac 1 audio.pcm

# 2. base64
B64=$(base64 -w0 audio.pcm)

# 3. 调用
lark-cli api POST /open-apis/speech_to_text/v1/speech/file_recognize \
  --data "{\"speech\":{\"speech\":\"$B64\"},\"config\":{\"file_id\":\"$(uuidgen | tr -d '-' | cut -c1-16)\",\"format\":\"pcm\",\"engine_type\":\"16k_auto\"}}" \
  --as user
```

## 对比妙记方案

| | 原生 ASR | 妙记 |
|--|---------|------|
| 步数 | 1 步 | 3 步（drive→minutes→vc） |
| 延迟 | ~2-3s | ~10-15s |
| 权限 | 1 scope | 4 scopes |
| 时长限制 | ≤60s | 无限制 |
| 依赖 | ffmpeg 转码 | 无 |

## 权限授权记录

飞书语音转录相关 scope 及用途：

| scope | 用途 | 状态 |
|-------|------|:--:|
| `minutes:minutes.upload:write` | 上传音频生成妙记 | ✅ 已授权 |
| `vc:note:read` | 读取妙记逐字稿 | ✅ 已授权 |
| `minutes:minutes:readonly` | 读取妙记基本信息 | ✅ 已授权 |
| `minutes:minutes.artifacts:read` | 读取妙记 AI 产物 | ✅ 已授权 |
| `speech_to_text:speech` | 原生 ASR API | ⬜ 待授权 |
| `docx:document:write_only` | 覆盖更新飞书文档 | ⬜ 待授权 |

## 来源

- 飞书开放平台：https://open.feishu.cn/document/server-docs/ai/speech_to_text-v1/file_recognize.md
- 发现于：2026-06-27，用户质疑"飞书真的没有语音转写 API 吗？"→ 确有，且比妙记简洁
