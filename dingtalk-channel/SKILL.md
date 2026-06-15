---
name: dingtalk-channel
description: "Configure Hermes Agent for DingTalk (钉钉) messaging channel — Stream Mode, display tuning (hide tool calls / reasoning / intermediate messages), and troubleshooting."
version: "1.1.0"
author: jorinyang
tags: [dingtalk, messaging, platform, 钉钉, display]
triggers:
  - dingtalk
  - 钉钉
  - "dingtalk stream"
  - "dingtalk config"
  - "钉钉配置"
  - "钉钉隐藏工具"
---

# DingTalk Channel for Hermes Agent

Configure Hermes Agent to work as a DingTalk (钉钉) chatbot via Stream Mode.

## Prerequisites

- DingTalk Open Platform app with **Bot** capability enabled
- App Key (`DINGTALK_CLIENT_ID`) and App Secret (`DINGTALK_CLIENT_SECRET`)

## Step 1: Install Dependencies

```bash
pip install "dingtalk-stream>=0.20" httpx
```

## Step 2: Environment Variables

Set in shell or `~/.hermes/.env`:

```bash
DINGTALK_CLIENT_ID=your-app-key
DINGTALK_CLIENT_SECRET=your-app-secret
```

## Step 3: config.yaml — Minimal Working Config

```yaml
platforms:
  dingtalk:
    extra: {}
    # Optional group-chat gating:
    # require_mention: true
    # free_response_chats:
    #   - "cidABC=="
    # allowed_users:
    #   - "*"
```

No `extra` keys required for basic operation. The adapter reads `DINGTALK_CLIENT_ID` and `DINGTALK_CLIENT_SECRET` from env.

## Step 4: Hide Tool Calls, Reasoning, and Intermediate Messages

This is the key config that makes DingTalk output clean — only showing the final response:

```yaml
display:
  platforms:
    dingtalk:
      # Hide LLM thinking/reasoning chain
      show_reasoning: false
      # Suppress ALL tool call progress (terminal, search, read, etc.)
      tool_progress: "off"
      # Suppress intermediate assistant messages ("正在分析...")
      interim_assistant_messages: false
      # Suppress long-running task notifications ("⏳ Working — 3 min")
      long_running_notifications: false
      # Suppress busy acknowledgment detail
      busy_ack_detail: false
```

### Why Each Setting Matters

| Setting | Without | With `"off"` / `false` |
|---------|---------|----------------------|
| `tool_progress` | `terminal: "grep..."` lines flood chat | Only final response shown |
| `show_reasoning` | LLM thinking chain visible | Hidden |
| `interim_assistant_messages` | "正在分析..." status messages | Hidden |
| `long_running_notifications` | "⏳ Working — 3 min" heartbeats | Hidden |
| `busy_ack_detail` | Iteration/tool state detail | Hidden |

### Common Mistake

`tool_progress` must be the **quoted string** `"off"`, not bare `off`:

```yaml
# ✅ Correct — quoted string
tool_progress: "off"

# ❌ Wrong — YAML 1.1 converts bare `off` to boolean False
tool_progress: off
```

## How It Works

### Stream Mode (dingtalk-stream SDK)

DingTalk adapter uses WebSocket-based Stream Mode — no webhook endpoint needed. The SDK maintains a persistent connection and receives messages via callback.

### Display Settings Resolution Order

```
display.platforms.dingtalk.<key>      ← Per-platform (highest)
display.tool_progress_overrides.<key> ← Legacy fallback
display.<key>                          ← Global
_PLATFORM_DEFAULTS[dingtalk]           ← Built-in (TIER_LOW)
```

DingTalk defaults to `TIER_LOW` (tool_progress off, no interim messages). The explicit config above is belt-and-suspenders — ensures the behavior even if defaults change.

## Optional: AI Card Streaming

> ⚠️ **Known issue**: AI Card streaming has a double-finalize bug where card content may disappear. Use at your own risk until the upstream fix lands.

To enable progressive content display (token-by-token), you need an AI Card template:

1. Create a card template in DingTalk Open Platform with a `content` field
2. Add to config:

```yaml
platforms:
  dingtalk:
    extra:
      card_template_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.schema"
```

3. Install Card SDK:

```bash
pip install alibabacloud-dingtalk alibabacloud-tea-openapi
```

4. Enable streaming display:

```yaml
display:
  platforms:
    dingtalk:
      streaming: true
```

### Double-Finalize Bug (Card Streaming)

When card streaming is enabled, `stream_consumer` may call `edit_message(finalize=True)` twice. The second call resets the card to empty template state. Workaround in `gateway/platforms/dingtalk.py`:

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

## Troubleshooting

### Tool progress still showing

Check `tool_progress: "off"` is a **quoted string**, not bare YAML boolean.

### No messages received

1. Verify `DINGTALK_CLIENT_ID` and `DINGTALK_CLIENT_SECRET` are set
2. Check gateway logs: `tail -f ~/.hermes/logs/gateway.log`
3. Ensure the DingTalk app has Bot capability enabled

### Messages sent but not received by user

Check session webhook expiry. The adapter caches webhooks per chat_id with a 5-minute safety margin before expiry.

## Reference

- Source: `gateway/platforms/dingtalk.py`
- Display config: `gateway/display_config.py`
- DingTalk Stream SDK: `dingtalk-stream>=0.20`
