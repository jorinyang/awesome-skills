# 网络搜索降级预案

> 当 Firecrawl 自托管实例 (localhost:3002) 不可用时的工作流。

## 故障诊断

```bash
# 1. 检查容器状态
docker ps -a --filter name=firecrawl --format "{{.Names}} {{.Status}}"

# 2. 检查 API 健康
curl -s http://localhost:3002/health

# 3. 如果容器存在但已退出，尝试通过 compose 重启
docker compose -p firecrawl ps        # 先查项目名
docker compose -p firecrawl up -d api # 启动 API
```

## 常见故障原因

| 原因 | 症状 | 方案 |
|------|------|------|
| WSL 已移除 | `wsl -d Ubuntu` 返回 `WSL_E_LOCAL_SYSTEM_NOT_SUPPORTED` | 直接走降级方案 |
| Docker compose 文件在 WSL 内 | `docker compose -p firecrawl` 找不到 config | 无法恢复，降级 |
| TUN 代理干扰 localhost | curl localhost:3002 超时 | 检查 `http_proxy` 环境变量 |
| API 容器因 Redis/RabbitMQ 连接失败而退出 | 日志显示 ECONNREFUSED | 用 compose 完整重启整个栈 |

## 降级方案：Sogou + Bing 直搜

当 Firecrawl 确认不可用时，通过 `execute_code` 直接请求搜索引擎：

```python
import urllib.request, ssl, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

query = "搜索关键词"
url = f"https://www.sogou.com/web?query={urllib.request.quote(query)}"
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10, context=ctx)
html = resp.read().decode('utf-8', errors='ignore')
text = re.sub(r'<[^>]+>', ' ', html)
text = re.sub(r'\s+', ' ', text)
# 用正则提取目标信息
```

### 搜索引擎选择

| 引擎 | 中文搜索 | 公司/工商信息 | 注意事项 |
|------|---------|-------------|---------|
| **Sogou** | ✅ 强 | ✅ 能搜到企查查/水滴信用数据 | 首选中文公司搜索 |
| **Bing** | 🟡 中 | 🟡 有时反爬 | 需 SSL 验证关闭 |
| **Baidu** | ✅ 强 | ❌ 反爬严格 | CSS class 不稳定 |

### 公司信息提取的专用模式

```python
# 从搜索结果文本中提取公司注册信息
patterns = {
    '公司全称': r'(?:公司名称|企业名称)[：:\s]+(\S{4,40}(?:有限公司|有限责任公司))',
    '法定代表人': r'法定代表人[：:\s]+(\S{2,6})',
    '注册资本': r'注册资本[：:\s]+(\S{2,20})',
    '成立日期': r'成立日期[：:\s]+(\S{5,15})',
    '统一社会信用代码': r'统一社会信用代码[：:\s]+([\dA-Z]{18})',
    '经营范围': r'经营范围[：:\s]+(.{5,200})',
}
```

### 直接提取天眼查 URL

如果已知天眼查公司链接，直接用 `web_extract` 获取结构化信息：

```python
web_extract(urls=["https://www.tianyancha.com/company/{company_id}"])
```
天眼查页面返回的 markdown 包含公司名、法人、注册资本、成立日期、股东信息等。
