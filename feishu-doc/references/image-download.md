# 飞书图片处理（v2）

## 插入图片到文档（推荐）

使用 `lark-cli docs +media-insert`，一步完成上传+插入：

```bash
# 本地图片
cd /path/to/dir && lark-cli docs +media-insert \
  --doc {{doc_id}} \
  --file image.png \
  --caption "图片说明" \
  --align center \
  --as bot

# 网络图片（在 XML 中直接嵌入）
<img href="https://example.com/image.png" width="800" caption="说明"/>
```

## 文件插入

```bash
lark-cli docs +media-insert \
  --doc {{doc_id}} \
  --file report.pdf \
  --type file \
  --as bot
```

## 从 Feishu CDN 下载图片

Feishu 消息/文档中的图片托管在 `sf3-cn.feishucdn.com`，可直接通过 curl 下载：

```bash
curl -sL -o /tmp/feishu_image.png \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://sf3-cn.feishucdn.com/obj/open-platform-opendoc/..." \
  -w "\nHTTP_CODE:%{http_code} SIZE:%{size_download}"
```

下载后可通过 `+media-insert` 插入文档。

## 通过 IM API 获取消息中的图片

```
GET https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/resources/{file_key}?type=image
Authorization: Bearer {{TOKEN}}
```

**完整流程**：
1. 列出消息：`GET /im/v1/messages?container_id_type=chat&container_id={chat_id}`
2. 从响应中找 `msg_type=image` 的消息，记录 `message_id` 和 `image_key`
3. 下载后通过 `+media-insert` 插入文档

**已知群聊**：

| 群名 | chat_id |
|------|---------|
| 贵州之客 | `oc_40570cc921ca1f645f8667151c1e85e6` |
