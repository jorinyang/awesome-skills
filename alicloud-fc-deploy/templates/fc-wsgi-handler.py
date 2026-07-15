# -*- coding: utf-8 -*-
"""
FC WSGI Handler 模板 — 复制此文件为 index.py 直接部署

Handler 签名: handler(environ, start_response)
Runtime: python3.10
Handler: index.handler
"""
import json


def handler(environ, start_response):
    """FC HTTP 触发器 WSGI handler"""
    
    # ── 解析请求 ──
    method = environ.get("REQUEST_METHOD", "GET")
    content_type = environ.get("CONTENT_TYPE", "")
    
    # 读 body
    body_str = ""
    try:
        length = int(environ.get("CONTENT_LENGTH", "0"))
        if length > 0:
            body_str = environ["wsgi.input"].read(length).decode("utf-8")
    except:
        body_str = ""
    
    # 解析 JSON
    try:
        body = json.loads(body_str) if body_str else {}
    except json.JSONDecodeError:
        body = {}
    
    # ── 业务逻辑 ──
    # TODO: 替换为你的业务处理
    result = {"message": "Hello from FC", "method": method, "received": body}
    
    # ── 返回响应 ──
    result_json = json.dumps(result, ensure_ascii=False)
    
    status = "200 OK"
    response_headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
    ]
    start_response(status, response_headers)
    return [result_json.encode("utf-8")]
