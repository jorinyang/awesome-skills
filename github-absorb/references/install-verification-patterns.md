# 独立安装验证模式库

> 吸收自 open-pencil/open-pencil 安装验证过程（2026-06-23）。
> 当 Phase 5C 遇到安装问题时，逐一对照这些模式。

## 模式 1：运行时不匹配（shebang vs dist 依赖）

**症状**：`npm install -g` 成功，但运行时报 `Bun is not defined` 或类似运行时 API 缺失。

**根因**：npm 包 dist 文件使用了 Bun 全局对象（`Bun.file()` / `Bun.readFile()` 等），但 bin 入口的 shebang 是 `#!/usr/bin/env node`，导致 Node.js 执行时找不到 `Bun`。

**检测方法**：
```bash
# 1. 检查 shebang
head -1 $(which <command>)
# 如果是 #!/usr/bin/env node，但 dist 用了 Bun API → 不匹配

# 2. 验证 Bun 全局是否可用
bun -e "console.log(typeof Bun)"
# → "object" 表示 Bun 运行时正常
```

**修复**：
```bash
# 方案 A：直接用 Bun 运行 dist 文件
bun /path/to/node_modules/<package>/dist/index.mjs <args>

# 方案 B：安装真正的 Bun 二进制（brew install bun / curl bun.sh/install）
# 然后 bun add -g <package> 重装（Bun 全局安装的 shebang 指向 bun）
```

**注意**：`npm install -g bun` 安装的是 bun npm 包（内含 ELF 二进制，~92MB），但需要验证它是否提供完整 Bun 运行时（`bun -e "console.log(typeof Bun)"`）。

---

## 模式 2：端口与文档不一致

**症状**：按 README 写的端口（如 3100）访问，连接被拒绝。

**根因**：README 示例端口与实际代码默认值不同。很多时候 README 写的是"建议端口"，代码里是另一个默认值。

**检测方法**：
```bash
# 1. 别信 README，直接读 dist 源码
grep -n 'port\|PORT\|listen' /path/to/dist/index.mjs | head -10

# 2. 或用 ss/netstat 看实际监听端口
ss -tlnp | grep <进程名>
```

**本例**：OpenPencil MCP HTTP README 写 `localhost:3100/mcp`，实际代码默认 `PORT ?? "7600"`。

---

## 模式 3：MCP HTTP 需要双 Accept 头

**症状**：MCP HTTP POST 请求返回 `-32000 "Not Acceptable: Client must accept both application/json and text/event-stream"`。

**根因**：MCP HTTP 传输使用 SSE（Server-Sent Events），服务端要求客户端同时声明支持 `application/json`（请求体）和 `text/event-stream`（响应流）。

**正确请求**：
```bash
curl -s -X POST http://localhost:7600/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{...}}'
```

**响应格式**（SSE）：
```
event: message
data: {"result":{...},"jsonrpc":"2.0","id":1}
```

---

## 模式 4：测试文件不真实

**症状**：仓库测试夹具（test fixtures）用 CLI 解析时报格式错误。

**根因**：测试夹具常为 mock/占位数据，不是真实格式文件。`.fig` 测试文件可能只是空壳或 oracle 快照。

**检测方法**：
```bash
# 优先用 .pen（JSON 文本格式）而非 .fig（二进制 ZIP 格式）
find . -name '*.pen' -not -path './node_modules/*'

# 对比文件大小——真实文件 > 1KB，mock 通常 < 100B
ls -la tests/fixtures/*.fig
```

**修复**：用可读格式（.pen）验证功能正常，再找真实 .fig 文件做端到端测试。

---

## 验证清单（Phase 5C 速查）

每次独立安装后，逐项完成：

- [ ] **shebang 检查**：`head -1 $(which <cmd>)` → 运行时是否匹配 dist 依赖？
- [ ] **版本号**：`<cmd> --version` 或 `<cmd> --help` 有正常输出
- [ ] **端口发现**：别信 README，读源码 `grep port dist/` + `ss -tlnp` 确认
- [ ] **基础命令**：用一个简单命令验证核心功能（如 `tree`、`formats`、`info`）
- [ ] **端到端**：用真实数据文件执行完整操作（优先可读格式）
- [ ] **MCP 协议**（如适用）：initialize → tools/list → 至少一个 tool call
- [ ] **记录环境约束**：运行时版本、平台限制、已知问题
