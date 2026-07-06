---
name: image-analysis
description: Analyze images users send — MiniMax VLM, resize workarounds, common failures.
---

# Image Analysis

Analyze images that users send in chat. Covers vision API usage, large-image handling, and failure recovery.

## Trigger

User sends an image and you need to describe or extract information from it.

## Workflow

1. **Check image dimensions and size first:**
   ```bash
   file /path/to/image && ls -lh /path/to/image
   ```
   MiniMax VLM reliably rejects images >~10MB or >4000px. Pre-resize to avoid wasting turns on 1033 errors.

2. **Resize large images with PIL** (ImageMagick `convert` may not be installed):
   ```bash
   python3 -c "
   from PIL import Image
   img = Image.open('/path/to/image.jpg')
   img.thumbnail((1280, 1280))
   img.save('/path/to/image_sm.jpg', quality=85)
   "
   ```
   Target ~0.3MB, 1280px max dimension.

3. **Analyze with MiniMax VLM:**
   Use `mcp_minimax_mcp_understand_image` with the resized (`_sm`) version. Start with a simple prompt like "What is in this image?" — complex prompts can trigger 1033 errors when the service is under load.

4. **If 1033-system-error persists on small images:**
   The MiniMax VLM service is likely down. In that case, retry once with an even simpler prompt, then inform the user the vision service is unavailable.

## Pitfalls

- **Large images (>10MB, >4000px)** → persistent 1033-system-error from MiniMax VLM. Always resize first.
- **ImageMagick `convert`** may not be installed (common in WSL). Fall back to `python3 -c "from PIL import Image..."`.
- **`execute_code`** may be blocked in cron or restricted contexts. Use `terminal` with `python3 -c` directly.
- MiniMax VLM can have transient outages — 1033 errors even on small images. A retry with a minimal prompt often succeeds.
