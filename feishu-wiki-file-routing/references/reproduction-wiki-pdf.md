# 完整复现案例：Wiki PDF 读取全流程

## 场景

用户给出飞书知识库 PDF 链接，需要读取内容后生成图表。

## 完整命令序列

```bash
# Step 0: 发现需要授权 wiki:node:retrieve
lark-cli wiki +node-get --node-token T0niwkAxVitLWmkd9oGc7u7Gnyd --as user --format json
# → missing scope: wiki:node:retrieve

# Step 0a: 获取授权 (--no-wait + QR码模式)
lark-cli auth login --scope "wiki:node:retrieve" --no-wait --json
# → 拿到 device_code + verification_url

# Step 0b: 生成二维码给用户扫描
lark-cli auth qrcode --output ./lark-auth-qr.png "<verification_url>"
# 用户扫描授权后继续

# Step 0c: 完成授权轮询
lark-cli auth login --device-code "<device_code>"
# → OK: 授权成功

# Step 1: 尝试 doc 读取 → 失败（file 类型）
lark-cli wiki +node-get --node-token T0niwkAxVitLWmkd9oGc7u7Gnyd --obj-type docx --as user --format json
# → "not found: document not found" (不是 docx 类型)

lark-cli docs +fetch --api-version v2 --doc "https://acn3k7zweyc0.feishu.cn/wiki/T0niwkAxVitLWmkd9oGc7u7Gnyd" --scope outline --max-depth 4 --format json
# → "Unsupported document type 'file'. Only docx is supported"

# Step 2: 发现真实类型
lark-cli wiki spaces get_node --params '{"token":"T0niwkAxVitLWmkd9oGc7u7Gnyd"}' --as user --format json
# → obj_type: "file", obj_token: "Adzxb9uGYo6IywxAsyOcMUfUntf", title: "Agentic AI工程师路线图2026.pdf"

# Step 3: 下载文件
lark-cli drive +download --file-token Adzxb9uGYo6IywxAsyOcMUfUntf --output ./Agentic_AI_Engineer_Roadmap_2026.pdf
# → saved_path: C:/Users/Aorus/Agentic_AI_Engineer_Roadmap_2026.pdf, size: 1038680 bytes

# Step 4: 提取 PDF 文本
python3 -c "import pymupdf; doc=pymupdf.open('./Agentic_AI_Engineer_Roadmap_2026.pdf'); [print(page.get_text()) for page in doc]"
# → 15 pages extracted successfully
```

## 关键教训

1. `/wiki/` URL 不能假设是 docx 类型 —— 必须先探测
2. `wiki +node-get --obj-type docx` 对 file 类型返回 "not found"，不是明确说"这是 file"
3. `docs +fetch` 对 file 类型返回明确的 "Unsupported document type 'file'"
4. `wiki spaces get_node` 是唯一能稳定发现 obj_type 的方式
5. `--output` 只接受相对路径（lark-cli 安全限制）
