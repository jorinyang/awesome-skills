#!/bin/bash
# L1 本地采集定时任务 — WSL crontab 入口
#   L1a: 百度 + 夸克 通用搜索 (browser_collector.py)
#   L1b: 微博热搜 + 知乎热榜 社交热榜扫描 (hotlist_collector.py)
# L3 深度采集已迁移至 Bitable 队列 → l3_poller.py
# 用法: bash l3_cron.sh [industry|competitor|all]
# 日志: ~/.hermes-feishu/logs/browser_collect_YYYY-MM-DD.log

# ⚠️ 不用 set -e — 健康检查失败不应该终止脚本

# crontab 环境无完整 PATH，显式添加 lark-cli + opencli 所在目录
export PATH="$HOME/.local/bin:$HOME/.hermes/node/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$HOME/.hermes-feishu/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/browser_collect_$(date +%Y-%m-%d).log"
MODE="${1:-all}"

# ── agent-browser 健康检查 ★ (2026-06-13) ──────────────────
# 长期运行的 agent-browser Chrome 进程会逐渐僵死（~10 天后全量 timeout）。
# 采集前先验证 agent-browser 响应，失败则自动重启。
echo "=== health-check 开始 $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"

AGENT_BROWSER="$HOME/.local/bin/agent-browser"
HEALTHY=false

for attempt in 1 2; do
    RESULT=$(timeout 10 "$AGENT_BROWSER" eval "1+1" 2>&1) || true
    # agent-browser eval 返回裸值 (如 "2")，不是 JSON 字符串
    if [ "$RESULT" = "2" ]; then
        HEALTHY=true
        echo "[health-check] agent-browser OK (attempt=$attempt)" >> "$LOG_FILE"
        break
    fi
    echo "[health-check] agent-browser unresponsive (attempt=$attempt): $RESULT" >> "$LOG_FILE"

    if [ "$attempt" -eq 1 ]; then
        echo "[health-check] killing stale agent-browser + Chrome processes..." >> "$LOG_FILE"
        pkill -f "agent-browser" 2>/dev/null || true
        pkill -f "agent-browser-chrome" 2>/dev/null || true
        sleep 3
        echo "[health-check] restarting agent-browser..." >> "$LOG_FILE"
        "$AGENT_BROWSER" >> "$LOG_FILE" 2>&1 &
        sleep 5
    fi
done

if [ "$HEALTHY" = false ]; then
    echo "[health-check] FATAL: agent-browser still unresponsive after restart." >> "$LOG_FILE"
    echo "=== health-check 失败 $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"
    exit 1
fi

echo "=== health-check 通过 $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# ── L1a: 百度 + 夸克 通用搜索 ────────────────────────────
echo "=== L1a browser_collector 开始 $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"

cd "$SCRIPT_DIR"
python3 browser_collector.py --mode "$MODE" --channel L1 --push >> "$LOG_FILE" 2>&1

RET_L1A=$?
echo "=== L1a browser_collector 结束 $(date '+%Y-%m-%d %H:%M:%S') exit=$RET_L1A ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# ── L1b: 社交热榜扫描 (微博+知乎) ──────────────────────
# 非关键路径：opencli 依赖 Chrome + daemon，失败不影响整体退出码
echo "=== L1b hotlist_collector 开始 $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"

python3 hotlist_collector.py --push >> "$LOG_FILE" 2>&1 || {
    echo "=== L1b hotlist_collector 失败 (opencli/Chrome 可能未运行) ===" >> "$LOG_FILE"
}
echo "=== L1b hotlist_collector 结束 $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit $RET_L1A
