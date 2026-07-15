"""
阿里云 FC OpenAPI — ACS3-HMAC-SHA256 签名 + 完整部署客户端
===========================================================
纯标准库实现，可直接在 FC Python 3 运行时或任何 Python 3.6+ 环境使用。

端点: fc.{region}.aliyuncs.com（NOT {region}.fc.aliyuncs.com — DNS 不可达）
⚠️  DELETE 返回 204 No Content，响应体为空 — json.loads(b"") 抛异常，需 try/except 兜底
⚠️  x-acs-action 必须精确匹配（CreateService/GetFunction/DeleteTrigger…），不能从 URL path 推导

用法:
    from acs3_signing import FCClient
    client = FCClient(ak, sk, "cn-hangzhou")
    client.ensure_service("my-service")
    url = client.ensure_http_trigger("my-service", "my-func")
"""
import json, time, hashlib, hmac, base64, urllib.request, ssl


class FCClient:
    """阿里云 FC OpenAPI 客户端 (v2021-04-06)"""

    def __init__(self, ak, sk, region="cn-hangzhou"):
        self.ak = ak
        self.sk = sk
        self.endpoint = f"fc.{region}.aliyuncs.com"
        self.api_version = "2021-04-06"

    def _sha256_hex(self, s):
        if isinstance(s, str): s = s.encode()
        return hashlib.sha256(s).hexdigest()

    def _sign(self, method, path, body_str):
        """ACS3-HMAC-SHA256 签名 — body hash 包含在 canonical request 中"""
        headers = {
            "host": self.endpoint,
            "content-type": "application/json",
            "accept": "application/json",
            "x-acs-action": self._get_action(method, path),
            "x-acs-version": self.api_version,
            "x-acs-date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "x-acs-signature-nonce": hashlib.md5(str(time.time()).encode()).hexdigest(),
        }

        body_hash = self._sha256_hex(body_str)
        signed_keys = sorted(["host", "content-type", "accept",
                              "x-acs-action", "x-acs-version",
                              "x-acs-date", "x-acs-signature-nonce"])
        canonical_headers = "\n".join(f"{k}:{headers[k]}" for k in signed_keys)
        signed_headers_str = ";".join(signed_keys)

        uri, query = (path.split("?", 1) + [""])[:2]

        canonical_request = (
            f"{method}\n{uri}\n{query}\n"
            f"{canonical_headers}\n\n{signed_headers_str}\n{body_hash}"
        )

        string_to_sign = f"ACS3-HMAC-SHA256\n{self._sha256_hex(canonical_request)}"
        sig = hmac.new(self.sk.encode(), string_to_sign.encode(), hashlib.sha256).hexdigest()

        headers["authorization"] = (
            f"ACS3-HMAC-SHA256 Credential={self.ak},"
            f"SignedHeaders={signed_headers_str},Signature={sig}"
        )
        return headers

    def _get_action(self, method, path):
        if method == "GET":
            if "/triggers/" in path: return "GetTrigger"
            if "/functions/" in path: return "GetFunction"
            if "/services/" in path: return "GetService"
            return "ListServices"
        if method == "POST":
            if "/triggers" in path: return "CreateTrigger"
            if "/functions" in path: return "CreateFunction"
            if "/services" in path: return "CreateService"
        if method == "DELETE":
            if "/triggers" in path: return "DeleteTrigger"
            if "/functions" in path: return "DeleteFunction"
        if method == "PUT":
            if "/functions" in path: return "UpdateFunction"
        return path.split("/")[-1]

    def api(self, method, path, body=None):
        url = f"https://{self.endpoint}{path}"
        body_str = json.dumps(body) if body else ""
        headers = self._sign(method, path, body_str)
        data = body_str.encode() if body_str else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        ctx = ssl.create_default_context()
        try:
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                raw = resp.read()
                return resp.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raw = e.read()
            try: return e.code, json.loads(raw) if raw else {}
            except: return e.code, {"error": str(e)[:300]}

    # ── 便捷方法 ──

    def ensure_service(self, name):
        s, _ = self.api("GET", f"/{self.api_version}/services/{name}")
        if s != 200:
            s, _ = self.api("POST", f"/{self.api_version}/services", {
                "serviceName": name, "description": name, "internetAccess": True
            })
        return s in (200, 201)

    def deploy_function(self, svc, fn, code_b64, env=None, runtime="python3",
                        handler="index.handler", memory=256, timeout=30):
        """部署函数。PUT 更新优先，失败则 DELETE → POST 重建"""
        body = {"functionName": fn, "runtime": runtime, "handler": handler,
                "memorySize": memory, "timeout": timeout, "code": {"zipFile": code_b64}}
        if env:
            body["environmentVariables"] = env

        # Try PUT first
        s, _ = self.api("PUT", f"/{self.api_version}/services/{svc}/functions/{fn}", body)
        if s in (200, 201): return True

        # DELETE → POST rebuild
        for sub in [f"/triggers/http-trigger", ""]:
            self.api("DELETE", f"/{self.api_version}/services/{svc}/functions/{fn}{sub}")
        s, _ = self.api("POST", f"/{self.api_version}/services/{svc}/functions", body)
        return s in (200, 201)

    def ensure_http_trigger(self, svc, fn):
        """确保 HTTP 触发器存在，返回 urlInternet"""
        tpath = f"/{self.api_version}/services/{svc}/functions/{fn}/triggers/http-trigger"
        s, r = self.api("GET", tpath)
        if s != 200:
            self.api("POST", f"/{self.api_version}/services/{svc}/functions/{fn}/triggers", {
                "triggerName": "http-trigger", "triggerType": "http",
                "triggerConfig": json.dumps({"authType": "anonymous", "methods": ["POST", "GET"]})
            })
            s, r = self.api("GET", tpath)
        return r.get("urlInternet") if s == 200 else None
