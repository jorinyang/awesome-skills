#!/usr/bin/env bash
# OpenPencil CI 设计自动化管线
# 用法: bash design-ci.sh <design-file.fig|.pen> [--strict]
#
# 依赖:
#   - Bun 运行时 (bun)
#   - @open-pencil/mcp (npm install -g)
#   - curl
#
# 流程:
#   1. 启动 MCP HTTP Server (后台)
#   2. 等待就绪
#   3. 初始化 MCP 会话
#   4. 执行设计检查 (describe → analyze_*)
#   5. 导出预览图
#   6. 生成报告 → 关闭 Server

set -euo pipefail

DESIGN_FILE="${1:-}"
STRICT="${2:-}"
MCP_HOST="${MCP_HOST:-127.0.0.1}"
MCP_PORT="${MCP_PORT:-7600}"
BUN="${BUN:-bun}"

# ── 检查输入 ──
if [ -z "$DESIGN_FILE" ]; then
  echo "用法: $0 <design-file> [--strict]"
  exit 1
fi

if [ ! -f "$DESIGN_FILE" ]; then
  echo "❌ 文件不存在: $DESIGN_FILE"
  exit 1
fi

# 设置 MCP root 为设计文件所在目录
export OPENPENCIL_MCP_ROOT="$(dirname "$(realpath "$DESIGN_FILE")")"

# ── Step 1: 启动 MCP HTTP Server ──
echo "🚀 启动 OpenPencil MCP Server..."
MCP_PID=""
cleanup() {
  if [ -n "$MCP_PID" ] && kill -0 "$MCP_PID" 2>/dev/null; then
    kill "$MCP_PID" 2>/dev/null || true
    echo "🛑 MCP Server 已关闭"
  fi
}
trap cleanup EXIT

# 后台启动（Bun 运行时）
$BUN "$(npm root -g)/@open-pencil/mcp/dist/index.mjs" &
MCP_PID=$!

# ── Step 2: 等待就绪 ──
echo "⏳ 等待 MCP Server 就绪..."
for i in $(seq 1 30); do
  if curl -s "http://${MCP_HOST}:${MCP_PORT}/mcp" -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{"jsonrpc":"2.0","id":0,"method":"ping","params":{}}' 2>/dev/null | grep -q .; then
    echo "✅ MCP Server 就绪 (pid=$MCP_PID)"
    break
  fi
  sleep 0.5
done

# ── Step 3: MCP 初始化 ──
mcp_call() {
  local method="$1" params="$2" id="${3:-99}"
  curl -s "http://${MCP_HOST}:${MCP_PORT}/mcp" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -H "Mcp-Session-Id: ${MCP_SESSION}" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":${id},\"method\":\"${method}\",\"params\":${params}}"
}

# 初始化会话
echo "🔌 初始化 MCP 会话..."
INIT_RESULT=$(curl -s "http://${MCP_HOST}:${MCP_PORT}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"ci-pipeline","version":"1.0"}}}')

MCP_SESSION=$(echo "$INIT_RESULT" | grep -oP 'mcp-session-id:\s*\K[^\r\n]+' || true)

if [ -z "$MCP_SESSION" ]; then
  # 从 verbose curl 提取 session
  MCP_SESSION=$(curl -s -v "http://${MCP_HOST}:${MCP_PORT}/mcp" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"ci-pipeline","version":"1.0"}}}' 2>&1 | grep -i 'mcp-session-id:' | awk '{print $3}' | tr -d '\r')
fi

if [ -z "$MCP_SESSION" ]; then
  echo "❌ 无法获取 MCP Session ID"
  exit 1
fi

echo "   Session: $MCP_SESSION"

# 发送 initialized 通知
curl -s "http://${MCP_HOST}:${MCP_PORT}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: ${MCP_SESSION}" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}' > /dev/null 2>&1

# ── Step 4: 打开设计文件 ──
FILENAME=$(basename "$DESIGN_FILE")
echo "📂 打开设计文件: $FILENAME"
OPEN_RESULT=$(mcp_call "tools/call" "{\"name\":\"open_file\",\"arguments\":{\"path\":\"${FILENAME}\"}}" 2)

echo "$OPEN_RESULT" | python3 -c "
import sys, json
for line in sys.stdin:
    if line.startswith('data: '):
        msg = json.loads(line[6:])
        if 'error' in msg:
            print(f'   ⚠️  open_file: {msg[\"error\"]}')
        elif 'result' in msg:
            content = msg['result'].get('content', [{}])
            text = content[0].get('text', '') if content else ''
            print(f'   ✅ 已打开: {text[:120]}')
" 2>/dev/null || echo "   ⚠️  文件打开待验证（可能需要 .fig 格式）"

# ── Step 5: 执行检查 ──
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 设计检查报告: $FILENAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 5a: describe - 获取文件概览
echo ""
echo "### 文件概览"
DESC_RESULT=$(mcp_call "tools/call" "{\"name\":\"describe\",\"arguments\":{}}" 3)
echo "$DESC_RESULT" | python3 -c "
import sys, json
for line in sys.stdin:
    if line.startswith('data: '):
        msg = json.loads(line[6:])
        if 'result' in msg:
            content = msg['result'].get('content', [{}])
            text = content[0].get('text', '') if content else json.dumps(msg['result'])
            print(text[:500])
        elif 'error' in msg:
            print(f'⚠️  describe 失败: {msg[\"error\"][:200]}')
" 2>/dev/null || echo "⚠️  describe 不可用"

# 5b: analyze_colors - 色彩分析
echo ""
echo "### 色彩分析"
COLORS_RESULT=$(mcp_call "tools/call" "{\"name\":\"analyze_colors\",\"arguments\":{}}" 4) 
echo "$COLORS_RESULT" | python3 -c "
import sys, json
for line in sys.stdin:
    if line.startswith('data: '):
        msg = json.loads(line[6:])
        if 'result' in msg:
            content = msg['result'].get('content', [{}])
            text = content[0].get('text', '') if content else ''
            lines = text.split('\n')[:15]
            print('\n'.join(lines))
        elif 'error' in msg:
            print(f'⚠️  analyze_colors 失败: {msg[\"error\"][:200]}')
" 2>/dev/null || echo "⚠️  analyze_colors 不可用"

# 5c: analyze_typography - 字体分析
echo ""
echo "### 字体分析"
TYPO_RESULT=$(mcp_call "tools/call" "{\"name\":\"analyze_typography\",\"arguments\":{}}" 5)
echo "$TYPO_RESULT" | python3 -c "
import sys, json
for line in sys.stdin:
    if line.startswith('data: '):
        msg = json.loads(line[6:])
        if 'result' in msg:
            content = msg['result'].get('content', [{}])
            text = content[0].get('text', '') if content else ''
            lines = text.split('\n')[:10]
            print('\n'.join(lines))
        elif 'error' in msg:
            print(f'⚠️  analyze_typography 失败: {msg[\"error\"][:200]}')
" 2>/dev/null || echo "⚠️  analyze_typography 不可用"

# 5d: 严格模式下追加 analyze_spacing
if [ "$STRICT" = "--strict" ]; then
  echo ""
  echo "### 间距分析 (strict)"
  SPACING_RESULT=$(mcp_call "tools/call" "{\"name\":\"analyze_spacing\",\"arguments\":{}}" 6)
  echo "$SPACING_RESULT" | python3 -c "
import sys, json
for line in sys.stdin:
    if line.startswith('data: '):
        msg = json.loads(line[6:])
        if 'result' in msg:
            content = msg['result'].get('content', [{}])
            text = content[0].get('text', '') if content else ''
            print(text[:300])
  " 2>/dev/null || echo "⚠️  analyze_spacing 不可用"
fi

# ── Step 6: 导出预览 ──
echo ""
echo "### 导出预览"
EXPORT_DIR="/tmp/openpencil-ci-exports"
mkdir -p "$EXPORT_DIR"
EXPORT_FILE="$EXPORT_DIR/${FILENAME%.*}_preview.png"
EXPORT_RESULT=$(mcp_call "tools/call" "{\"name\":\"export_image\",\"arguments\":{\"format\":\"png\",\"scale\":1,\"path\":\"${EXPORT_FILE}\"}}" 7)
echo "$EXPORT_RESULT" | python3 -c "
import sys, json
for line in sys.stdin:
    if line.startswith('data: '):
        msg = json.loads(line[6:])
        if 'result' in msg:
            content = msg['result'].get('content', [{}])
            text = content[0].get('text', '') if content else ''
            print(f'   ✅ {text[:200]}')
        elif 'error' in msg:
            print(f'   ⚠️  导出失败: {msg[\"error\"][:200]}')
" 2>/dev/null || echo "   ⚠️  export 不可用"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 管线完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
