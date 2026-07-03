# 独立安装验证——已知坑

> github-absorb Phase 5C 参考。避免重蹈安装时的常见陷阱。

## 1. 端口与文档不一致

README 或文档中声明的默认端口可能与源码实际值不同。**必须从源码确认，而非盲信文档。**

**案例**：OpenPencil MCP HTTP Server
- 文档声称：`http://localhost:3100/mcp`
- 源码实际：`const port = Number.parseInt(process.env.PORT ?? "7600", 10);`

**检查方法**：
```bash
# 查看 dist 文件中的端口定义
grep -n 'port\|PORT\|listen' dist/index.mjs | head -5

# 或启动后查看监听端口
ss -tlnp | grep <进程名>
```

## 2. npm 包 shebang 与实际运行时不同

npm 全局安装的 CLI 包 shebang 写 `#!/usr/bin/env node`，但 dist 文件可能内嵌 Bun 专有 API（`Bun.file()`、`Bun.readFile()` 等）。

**症状**：
```
ERROR  Bun is not defined
    at loadDocument (.../dist/index.mjs:167:37)
```

**诊断**：
```bash
# 检查 dist 是否引用了 Bun API
grep -n 'Bun\.' dist/index.mjs | head -5

# 确认 Bun 是否可用
bun -e "console.log(typeof Bun)"
```

**修复**：
```bash
# 不通过 npm bin 的 node shebang，直接用 bun 运行 dist
bun /path/to/node_modules/@scope/pkg/dist/index.mjs <args>
```

## 3. MCP HTTP 传输协议细节

### Session 管理
- 首次 `initialize` 请求返回 `Mcp-Session-Id` 响应头
- 后续所有请求必须携带该 Session ID
- 必须在 `initialize` 后发送 `notifications/initialized` 才能调用工具

### 请求头
```
Content-Type: application/json
Accept: application/json, text/event-stream
Mcp-Session-Id: <session-id-from-initialize>
```

### 完整 MCP HTTP 交互序列
```bash
# 1. Initialize（捕获 Session ID）
SESSION=$(curl -s -v -X POST http://host:port/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{...}}' \
  2>&1 | grep -i 'mcp-session-id:' | awk '{print $3}' | tr -d '\r')

# 2. Send initialized notification
curl -s -X POST http://host:port/mcp \
  -H "Mcp-Session-Id: $SESSION" ... \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}'

# 3. Now tools/list and tools/call work
curl -s -X POST http://host:port/mcp \
  -H "Mcp-Session-Id: $SESSION" ... \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

### SSE 格式
HTTP MCP 响应使用 Server-Sent Events（`text/event-stream`）：
```
event: message
data: {"result":{...},"jsonrpc":"2.0","id":1}
```

解析时按行分割，匹配 `data: ` 前缀后提取 JSON。
