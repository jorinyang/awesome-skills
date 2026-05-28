# MiniMax CN — Vision API Failure Reference

## Symptom

Configuring `auxiliary.vision.provider = minimax-cn` with any MiniMax model results in silent failure: the API returns "no image provided" even with valid base64 image input. No error is raised — the image content is silently discarded.

## Root Cause

MiniMax CN API (`api.minimaxi.com/v1/chat/completions`) does not expose a vision-capable endpoint for the standard chat completions API. Available models confirmed via `GET /v1/models`:

```
MiniMax-M2.7, MiniMax-M2.7-highspeed, MiniMax-M2.5, MiniMax-M2.5-highspeed,
MiniMax-M2.1, MiniMax-M2.1-highspeed, MiniMax-M2
```

No separate vision model ID exists in the model list.

## What the token plan claims vs. API reality

| Feature | Token plan | API behavior |
|---------|-----------|-------------|
| 图像理解 (image understanding) | Listed | API silently drops image_url content |
| MCP / 联网搜索 | Listed | Requires separate MCP configuration |
| 4500 模型调用/月 | Listed | ✅ Works for text |

## Tested failure modes

All attempts with `image_url` content type return the same response:

```
"The user asks 'What is this image?' but no image was provided."
```

This occurs for:
- base64-encoded PNG/JPEG (inline `data:image/png;base64,...`)
- Public HTTPS image URLs
- All available MiniMax model IDs
- Both Chinese and English prompts about the image
- Anthropic-format `{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}}` sent to `/anthropic/v1/messages` (confirmed 2026-05-26 — same silent failure: `input_tokens` counted as text-only, no vision processing occurs)

## Workaround

Use a provider with actual vision capability for `auxiliary.vision`:

```bash
hermes config set auxiliary.vision.provider openrouter   # or anthropic / google
hermes config set auxiliary.vision.model gpt-4o            # or gemini-1.5-pro
```

MiniMax can remain as the main model provider.

## If the token plan genuinely includes vision

Escalate to MiniMax support. The capability may require:
1. A separate API endpoint not in the standard `/v1/` path
2. A separate model ID not returned by `/v1/models`
3. A separate service/quota pool

## Reproducer

```python
import subprocess, json, os, base64
from PIL import Image
import io

api_key = os.popen("grep MINIMAX_CN_API_KEY ~/.hermes-feishu/.env | cut -d= -f2").read().strip()

img = Image.new('RGB', (100, 100), color='red')
buf = io.BytesIO()
img.save(buf, format='PNG')
img_b64 = base64.b64encode(buf.getvalue()).decode()

result = subprocess.run([
    'curl', '-s', '--max-time', '30',
    'https://api.minimaxi.com/v1/chat/completions',
    '-H', f'Authorization: Bearer {api_key}',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps({
        "model": "MiniMax-M2.7-highspeed",
        "max_tokens": 50,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                {"type": "text", "text": "这张图片是什么？只回答颜色。"}
            ]
        }]
    })
], capture_output=True, text=True, timeout=35)

d = json.loads(result.stdout)
print(d.get('choices', [{}])[0].get('message', {}).get('content', ''))
# Bad outcome: "no image provided"
# Expected good: "红色" (red)
```

## Verdict

**INVALIDATED** — MiniMax CN API does not support image understanding via the standard chat completions endpoint with any currently available model. Token plan claim of 图像理解 support is either:
- Future capability not yet available via API
- Requires separate service/endpoint/account tier
- Marketing copy not yet backed by API capability
