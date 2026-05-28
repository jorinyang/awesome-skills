# MiniMax CN API — Vision Capability Reference

## What the token plan claims

| Feature | Claimed |
|---------|---------|
| Image understanding (图像理解) | ✅ Listed |
| MCP / 联网搜索 | ✅ Listed |
| Model calls | 4500/mo |
| Model | MiniMax-M2.7-highspeed |

## What the API actually does

### Endpoint tested
`POST https://api.minimaxi.com/v1/chat/completions`

### Models available (via `GET /v1/models`)
```
MiniMax-M2.7, MiniMax-M2.7-highspeed, MiniMax-M2.5, MiniMax-M2.5-highspeed,
MiniMax-M2.1, MiniMax-M2.1-highspeed, MiniMax-M2
```
No separate vision-capable model ID is listed.

### Vision test results

| Format | Model | API Response |
|--------|-------|-------------|
| base64 PNG | MiniMax-M2.7-highspeed | "no image provided" |
| base64 PNG | MiniMax-M2.7 | "no image provided" |
| base64 PNG | MiniMax-M2.5 | "no image provided" |
| public HTTPS URL | MiniMax-M2.7-highspeed | "no image provided" |
| Chinese prompt "只回答颜色" | all | same — image data is silently discarded |

### Other endpoints tested (all 404)
- `/v1/mvisions`
- `/v1/vision`
- `/v1/chat/completions_vision`
- `/v1/mvision/chat`
- `api.minimax.cn/v1/models` (no response)

## Conclusion

**MiniMax CN API does not support image understanding** via the standard `/v1/chat/completions` endpoint. The `image_url` message content is accepted without error but silently dropped — the model has no visual capability.

If the token plan includes image understanding, it likely requires:
1. A separate API endpoint not documented in the public API
2. A separate model ID not shown in `/v1/models`
3. A separate service/quota from MiniMax

## Verdict template for future vision spikes

```
## MiniMax Vision Capability

**Token plan says:** image understanding included
**API says:** no vision-capable model, image_url content dropped silently

→ Spike outcome: INVALIDATED (for standard API path)
→ Next step: escalate to MiniMax support to confirm separate endpoint/model
```

## Reproduce

```python
import subprocess, json, os, base64
from PIL import Image
import io

api_key = os.popen("grep MINIMAX_CN_API_KEY ~/.hermes-feishu/.env | cut -d= -f2").read().strip()

# Create test image
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
# Expected (bad): model claims no image was provided
# Expected (good): model answers the color
```
