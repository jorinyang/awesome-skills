---
name: alicloud-fc-deploy
description: 阿里云函数计算(FC)部署 Python 函数——通过 OpenAPI 创建服务/函数/HTTP触发器，含 ACS3-HMAC-SHA256 签名算法、WSGI handler 模板、常见坑位。触发：部署FC/函数计算/阿里云函数/Serverless部署/fcapp.run/CreateFunction。
version: 1.0.0
author: jorinyang
triggers:
  - "部署到FC"
  - "函数计算部署"
  - "阿里云FC"
  - "创建FC函数"
  - "Serverless部署"
  - "fcapp.run"
  - "CreateFunction"
  - "HTTP触发器"
---

# Alibaba Cloud FC Deployment

> 通过 FC OpenAPI 部署 Python 函数，含签名、handler、触发器全流程。

## 核心铁律

1. **端点格式**：`fc.{region}.aliyuncs.com`（NOT `{region}.fc.aliyuncs.com`）——后者 DNS 不解析
2. **签名算法**：ACS3-HMAC-SHA256，参考 `references/acs3-signing.md`
3. **HTTP 触发器 handler**：必须用 **WSGI 格式** `(environ, start_response)` 才能获得正确 `Content-Type: application/json`
4. **Runtime 选 `python3.10`**，不用 `python3`（后者是 python3.9 别名，HTTP 响应行为不稳定）

## 部署流程（5 步）

### Step 1：创建服务

```python
api("POST", "/2021-04-06/services", "CreateService", {
    "serviceName": "my-service",
    "description": "...",
    "internetAccess": True,
})
```

### Step 2：打包代码

```python
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write("index.py", "index.py")  # 第二个参数是 zip 内路径
code_b64 = base64.b64encode(buf.getvalue()).decode()
```

### Step 3：创建函数

```python
api("POST", "/2021-04-06/services/{svc}/functions", "CreateFunction", {
    "functionName": "my-func",
    "runtime": "python3.10",
    "handler": "index.handler",
    "memorySize": 256,
    "timeout": 30,
    "code": {"zipFile": code_b64},
    "environmentVariables": {"KEY": "value"},
})
```

### Step 4：创建 HTTP 触发器

```python
api("POST", f"/2021-04-06/services/{svc}/functions/{fn}/triggers", "CreateTrigger", {
    "triggerName": "http-trigger",
    "triggerType": "http",
    "triggerConfig": json.dumps({
        "authType": "anonymous",
        "methods": ["POST", "GET"]
    }),
})
```

### Step 5：获取公网 URL

```python
s, r = api("GET", f"/.../{fn}/triggers/http-trigger", "GetTrigger")
url = r["urlInternet"]  # fcapp.run 域名
```

## WSGI Handler 模板

参考 `templates/fc-wsgi-handler.py`。关键：**必须用 WSGI 格式**，FC python3.10 的 HTTP 触发器走 WSGI 协议。

```python
def handler(environ, start_response):
    # 读 body
    length = int(environ.get("CONTENT_LENGTH", "0"))
    body_str = environ["wsgi.input"].read(length) if length else b""
    
    # 处理逻辑...
    result = {"skills": [...]}
    
    # 显式设置 Content-Type
    status = "200 OK"
    headers = [("Content-Type", "application/json; charset=utf-8")]
    start_response(status, headers)
    return [json.dumps(result, ensure_ascii=False).encode("utf-8")]
```

## 常见坑位

### ❌ 返回 dict 而非 string
FC 直接用 `str()` 转 → 输出 `statusCodeheadersbody`（字典 key 拼接）。

### ❌ 返回 string 但非 WSGI
FC 不设置 Content-Type → `application/octet-stream`，被下游拒绝。

### ❌ 端点用 `{region}.fc.aliyuncs.com`
DNS 不解析（sandbox 环境），但 `fc.{region}.aliyuncs.com` 可用。

### ❌ DELETE 返回 204 空 body
`json.loads()` 会崩，需处理空响应：`json.loads(raw) if raw else {}`。

### ❌ UpdateFunction API 不 work
PUT/POST UpdateFunction 都返回 404 "api not found"。唯一可靠方式：删函数 → 重建。

## 签名算法

详见 `references/acs3-signing.md`。核心：

```
canonical_request = f"{method}\n{uri}\n{query}\n{canonical_headers}\n\n{signed_headers}\n{body_hash}"
string_to_sign = f"ACS3-HMAC-SHA256\n{sha256(canonical_request)}"
signature = HMAC-SHA256(SK, string_to_sign)
```

## 相关

- `references/acs3-signing.md`：完整签名算法 + Python 实现
- `templates/fc-wsgi-handler.py`：可复制的 WSGI handler 模板
- DingTalk Wukong 路由服务对接文档见阿里钉钉文档
