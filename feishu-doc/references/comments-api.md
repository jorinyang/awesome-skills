# 飞书文档评论 API 参考

## 可用工具

| 工具 | 用途 |
|------|------|
| `feishu_drive_list_comments` | 列出文档所有评论 |
| `feishu_drive_list_comment_replies` | 列出某条评论的所有回复 |
| `feishu_drive_reply_comment` | 回复一条评论 |
| `feishu_drive_add_comment` | 添加整篇文档评论 |

## 评论文本提取（关键）

⚠️ **文本不在 `rich_text` 字段！** 在嵌套 `reply_list` 结构中：

```python
# 正确提取方式
for item in api_response['data']['items']:
    cid = item['comment_id']
    replies = item.get('reply_list', {}).get('replies', [])
    if replies:
        elements = replies[0].get('content', {}).get('elements', [])
        text = ''.join(e.get('text_run', {}).get('text', '') for e in elements)
    else:
        text = ''
```

原始 API 返回结构：
```json
{
  "comment_id": "7644663286658518233",
  "is_solved": false,
  "is_whole": true,
  "reply_list": {
    "replies": [{
      "content": {
        "elements": [{
          "type": "text_run",
          "text_run": {"text": "@hermes 请修改这段内容"}
        }]
      }
    }]
  }
}
```

## 创建评论

⚠️ **必须同时传 `comment_content` 和 `reply_list`**，两者缺一不可。仅传 `reply_list` 会报 9499 `Missing required parameter: ReplyList`（误导读，实际是缺 `comment_content`）。

```python
body = {
    "comment_content": {
        "elements": [{"type": "text_run", "text_run": {"text": "评论正文"}}]
    },
    "reply_list": {
        "replies": [{
            "content": {
                "elements": [{"type": "text_run", "text_run": {"text": "首条回复（必填，可为简短标注）"}}]
            }
        }]
    }
}
# POST /open-apis/drive/v1/files/{doc_token}/comments?file_type=docx
```

注意：`file_type=docx` 是 URL 查询参数（不在 body 中），否则报 99992402。

## 回复评论

```python
body = {"reply_list": {"replies": [{
    "content": {"elements": [{"type": "text_run", "text_run": {"text": "回复内容"}}]}
}]}}
# POST /open-apis/drive/v1/files/{doc_token}/comments/{comment_id}/replies
```

## 权限要求

- `drive:comment:readonly` — 读取评论
- `drive:comment:writeonly` — 回复/添加评论

## 实测陷阱

1. **`text_run.text` 不是 `text_run.content`** — v2 API 字段名变了
2. **`rich_text` flat 字段为空** — 文本在嵌套 `reply_list.replies` 中
3. **回复 API 需要嵌套结构** — 不是简单的 `{"content": "text"}`
4. **评论类型** — `is_whole: true` = 整篇文档评论，`false` = 段落级评论
5. **创建评论必传 `?file_type=docx`** — 否则报 99992402
