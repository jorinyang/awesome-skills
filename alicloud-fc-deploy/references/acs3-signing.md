# ACS3-HMAC-SHA256 签名算法

阿里云 OpenAPI V3 签名机制，用于所有 FC API 调用。

## Python 实现

```python
import json, time, hashlib, hmac, base64, urllib.request, ssl

AK = "YOUR_ACCESS_KEY"
SK = "YOUR_SECRET_KEY"
ENDPOINT = "fc.cn-hangzhou.aliyuncs.com"  # 注意: fc.{region}.aliyuncs.com

def sha256_hex(s):
    return hashlib.sha256(s.encode() if isinstance(s, str) else s).hexdigest()

def api(method, path, action, body=None):
    url = f"https://{ENDPOINT}{path}"
    
    # 构造请求头
    headers = {
        "host": ENDPOINT,
        "content-type": "application/json",
        "accept": "application/json",
        "x-acs-action": action,
        "x-acs-version": "2021-04-06",
        "x-acs-date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "x-acs-signature-nonce": hashlib.md5(str(time.time()).encode()).hexdigest(),
    }
    
    # 1. 计算 body hash
    body_str = json.dumps(body) if body else ""
    body_hash = sha256_hex(body_str)
    
    # 2. 构建 canonical headers（按 key 字母排序）
    signed_keys = sorted([
        "host", "content-type", "accept",
        "x-acs-action", "x-acs-version",
        "x-acs-date", "x-acs-signature-nonce"
    ])
    canonical_headers = "\n".join(
        f"{k}:{headers[k]}" for k in signed_keys
    )
    signed_headers_str = ";".join(signed_keys)
    
    # 3. 解析 URI
    if "?" in path:
        uri, query = path.split("?", 1)
    else:
        uri, query = path, ""
    
    # 4. 构建 canonical request
    canonical_request = (
        f"{method}\n{uri}\n{query}\n"
        f"{canonical_headers}\n\n"
        f"{signed_headers_str}\n{body_hash}"
    )
    
    # 5. 计算签名
    hashed_cr = sha256_hex(canonical_request)
    string_to_sign = f"ACS3-HMAC-SHA256\n{hashed_cr}"
    sig = hmac.new(
        SK.encode(),
        string_to_sign.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # 6. 设置 Authorization header
    headers["authorization"] = (
        f"ACS3-HMAC-SHA256 "
        f"Credential={AK},"
        f"SignedHeaders={signed_headers_str},"
        f"Signature={sig}"
    )
    
    # 7. 发送请求
    data = body_str.encode() if body_str else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    ctx = ssl.create_default_context()
    
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, (json.loads(raw) if raw else {"error": str(e)})
        except:
            return e.code, {"error": str(e)[:200]}
```

## 签名校验（调试用）

如果签名失败，错误消息格式：
```
Specified signature does not match our calculation.
server StringToSign is [ACS3-HMAC-SHA256\n<hex>]
server CanonicalRequest is [<method>\n<uri>\n...]
```

对比 server 和 client 的 canonical request 找出差异。

## Body Hash 注意

- 空 body：`sha256("")` = `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- JSON body：用 `json.dumps(body)` 的字符串（无空格、ensure_ascii 默认 True）
