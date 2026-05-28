# 通过消息链接（applink）获取完整消息内容

## 问题背景

飞书消息中的链接格式 `https://applink.feishu.cn/client/message/link/open?token=xxx` 是**消息分享链接**，不是文档链接，无法通过 docx API 直接读取。

但如果该消息在某个线程（thread）中，可以从 Feishu 消息上下文提取 `chat_id` 和 `thread_id`，然后调用 IM API 读取线程消息列表。

## 上下文来源

从当前会话中，Feishu 消息的 JSON 上下文包含：
- `chat_id`（或 `open_conversation_id`）：会话 ID，格式如 `oc_xxx`
- `thread_id`（或 `thread_id`）：主话题 ID，格式如 `omt_xxx`

这些信息在 Hermite 系统的消息 metadata 中可以直接获取（无需额外 API 调用）。

## API 调用

```
GET https://open.feishu.cn/open-apis/im/v1/messages?container_id_type=thread&container_id={thread_id}&page_size=20
Authorization: Bearer {token}
```

响应 body.content 是 JSON 字符串，需要再次解析：

```python
import urllib.request, json

# 获取 token（每个 execute_code 脚本都要重新获取）
req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=json.dumps({"app_id": "cli_aa9ead14c2641cc3", "app_secret": "ZUUm7yI7HmfLi42ki8fPTgZzbj2AuTeM"}).encode(),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read())['tenant_access_token']

# 获取线程消息
req2 = urllib.request.Request(
    f'https://open.feishu.cn/open-apis/im/v1/messages?container_id_type=thread&container_id={thread_id}&page_size=20',
    headers={'Authorization': f'Bearer {token}'}
)
with urllib.request.urlopen(req2) as resp:
    result = json.loads(resp.read())

items = result.get('data', {}).get('items', [])
for item in items:
    body = json.loads(item.get('body', {}).get('content', '{}'))
    print(body.get('text', ''))  # 消息纯文本内容
```

## 适用场景

- 群聊中的长文档/方案内容被飞书消息截断时
- 用户分享的是消息链接而非文档链接时
- 文档本身无法直接访问，但消息内容完整

## 限制

- `container_id_type=thread` 才能读取线程消息，`container_id_type=chat` 只能读普通会话消息
- page_size 默认 20，最大可调
- 只能读取有权限访问的线程消息

## 发送通知注意

读取消息内容后，如需向同一 thread 推送通知：
- ❌ `target=platform:chat_id:thread_id` → 报 `99992402 field validation failed`
- ✅ `target=platform:chat_id` → 消息自动进入主话题
- 原因：send_message 的 thread_id 参数仅支持 Telegram Topics 等少数平台，飞书 thread 通知走 chat_id 即可
