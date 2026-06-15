---
name: dingtalk-channel
description: "Configure Hermes Agent for DingTalk (钉钉) messaging channel — Stream Mode, AI Card streaming, display tuning, and troubleshooting. Covers the full setup: SDK deps, env vars, config.yaml, and known bugs."
version: "1.0.0"
author: jorinyang
tags: [dingtalk, messaging, streaming, ai-card, platform, 钉钉]
triggers:
  - dingtalk
  - 钉钉
  - "dingtalk stream"
  - "dingtalk streaming"
  - "dingtalk card"
  - "钉钉配置"
---

# DingTalk Channel for Hermes Agent

Configure Hermes Agent to work as a DingTalk (钉钉) chatbot via Stream Mode with AI Card streaming support.

## Prerequisites

- DingTalk Open Platform app with **Bot** capability enabled
- App Key (`DINGTALK_CLIENT_ID`) and App Secret (`DINGTALK_CLIENT_SECRET`)
- AI Card template ID (for streaming output)

## Step 1: Install Dependencies

```bash
# From hermes venv
pip install "dingtalk-stream>=0.20" httpx alibabacloud-dingtalk alibabacloud-tea-openapi
```

## Step 2: Environment Variables

Create `~/.hermes/env/dingtalk.env` (chmod 600):

```bash
DINGTALK_CLIENT_ID=your-app-key
DINGTALK_CLIENT_SECRET=your-app-secret
DINGTALK_CARD_TEMPLATE_ID=your-template-id.schema
```

> **Note**: The `.schema` suffix is required for AI Card template IDs.

## Step 3: config.yaml Configuration

### 3.1 Platform Layer — Connection

```yaml
platforms:
  dingtalk:
    extra:
      card_template_id: "${DINGTALK_CARD_TEMPLATE_ID}"
      # Optional: override robot_code (defaults to client_id)
      # robot_code: "your-robot-code"
      # Optional: group chat gating
      # require_mention: true
      # free_response_chats:
      #   - "cidABC=="
      # allowed_users:
      #   - "*"
```

### 3.2 Display Layer — Output Control

```yaml
display:
  platforms:
    dingtalk:
      # Hide thinking/reasoning process
      show_reasoning: false
      # Enable AI Card streaming (progressive content display)
      streaming: true
      # Suppress ALL tool call progress messages
      tool_progress: "off"
      # Suppress intermediate assistant messages ("正在分析...")
      interim_assistant_messages: false
      # Suppress long-running task notifications
      long_running_notifications: false
      # Suppress busy acknowledgment detail
      busy_ack_detail: false
```

### 3.3 Complete Example

```yaml
# In config.yaml, add both sections:
platforms:
  dingtalk:
    extra:
      card_template_id: "675cde2f-xxxx-xxxx-xxxx-xxxxxxxxxxxx.schema"

display:
  platforms:
    dingtalk:
      show_reasoning: false
      streaming: true
      tool_progress: "off"
      interim_assistant_messages: false
      long_running_notifications: false
      busy_ack_detail: false
```

## How It Works

### Stream Mode (dingtalk-stream SDK)

DingTalk adapter uses WebSocket-based Stream Mode — no webhook endpoint needed. The SDK maintains a persistent connection and receives messages via callback.

### AI Card Streaming

When `card_template_id` is set:
1. **Card SDK** initializes (`alibabacloud-dingtalk.card_1_0`)
2. `send()` creates an AI Card with `callback_type="STREAM"`
3. `edit_message()` updates card content via `streaming_update` API
4. Content appears progressively (token-by-token) in DingTalk

### Display Settings Resolution Order

```
display.platforms.dingtalk.<key>     ← Per-platform (highest priority)
display.tool_progress_overrides.<key> ← Legacy (tool_progress only)
display.<key>                         ← Global
_PLATFORM_DEFAULTS[dingtalk]           ← Built-in (TIER_LOW for dingtalk)
```

## Troubleshooting

### Card Content Disappears

**Symptom**: Streaming card shows content then becomes empty.

**Root Cause**: Double-finalize bug — `stream_consumer` sends `edit_message(finalize=True)` twice for `REQUIRES_EDIT_FINALIZE` adapters. The second call resets the card to empty template state.

**Fix**: In `gateway/platforms/dingtalk.py`, add finalize tracking:

```python
# In __init__:
self._finalized_cards: Set[str] = set()

# In edit_message, before streaming_update:
if finalize and message_id in self._finalized_cards:
    return SendResult(success=True, message_id=message_id)

# After successful finalize:
if finalize:
    self._finalized_cards.add(message_id)
```

### Tool Progress Still Showing

Check that `tool_progress` is a quoted string `"off"`, not YAML boolean `off` (YAML 1.1 treats bare `off` as `False`).

```yaml
# ✅ Correct
tool_progress: "off"

# ❌ Wrong (YAML 1.1 converts to False, normalized to "off" but inconsistent)
tool_progress: off
```

### Card SDK Not Initializing

```
[dingtalk] Card SDK initialized with template: None
```

**Check**: `card_template_id` must be in `platforms.dingtalk.extra.card_template_id`, NOT as an environment variable. The adapter reads from `config.yaml` extra, not from env.

### No Streaming (Content Appears All at Once)

1. Verify `display.platforms.dingtalk.streaming: true`
2. Verify `card_template_id` is set (streaming requires AI Cards)
3. Check `SUPPORTS_MESSAGE_EDITING` returns `True` in logs

## Reference

- Source: `gateway/platforms/dingtalk.py` (1505 lines)
- Display config: `gateway/display_config.py`
- Stream consumer: `gateway/stream_consumer.py`
- DingTalk Stream SDK: `dingtalk-stream>=0.20`
- DingTalk Card SDK: `alibabacloud-dingtalk.card_1_0`
