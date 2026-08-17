#!/usr/bin/env python3
"""Firecrawl 健康守护脚本
每 5 分钟由 Hermes cron 触发。健康时静默，异常时自动修复并告警。

策略:
  1. curl 健康检查 → 健康则静默退出
  2. 异常 → docker compose restart (快速)
  3. restart 无效 → docker compose up -d (完整重建)
  4. 仍无效 → 告警
"""

import subprocess
import time
import os

COMPOSE_DIR = r"C:\Users\Aorus\tmp\firecrawl-selfhost"
HEALTH_CHECK = [
    "curl", "-sf", "--connect-timeout", "5", "--max-time", "20",
    "-X", "POST", "http://localhost:3002/v1/search",
    "-H", "Content-Type: application/json",
    "-d", '{"query":"h","limit":1}'
]
RETRY_WAIT = 15


def run(cmd, cwd=None, timeout=30):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True,
                          text=True, timeout=timeout)
        return r.returncode, r.stdout[:500], r.stderr[:500]
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except FileNotFoundError as e:
        return -1, "", f"CMD_NOT_FOUND:{e}"


def check_firecrawl():
    """Returns True if Firecrawl responds with 2xx."""
    code, stdout, stderr = run(HEALTH_CHECK, timeout=25)
    return code == 0, f"code={code}"


def check_docker():
    code, _, __ = run(["docker", "ps"], timeout=10)
    return code == 0


def compose_restart():
    """Fast restart — keep containers, just restart processes."""
    code, out, err = run(["docker", "compose", "restart"], cwd=COMPOSE_DIR, timeout=60)
    return code == 0, (out + err)[:300]


def compose_up():
    """Full up — recreate if config changed, pull if needed."""
    code, out, err = run(["docker", "compose", "up", "-d", "--no-recreate"],
                        cwd=COMPOSE_DIR, timeout=120)
    return code == 0, (out + err)[:300]


def main():
    # 1. Health check
    healthy, detail = check_firecrawl()
    if healthy:
        return  # Silent = healthy

    # 2. Docker running?
    if not check_docker():
        print(f"⚠️ Firecrawl 不可用 ({detail})，Docker 未运行")
        return

    # 3. Fast restart first
    print(f"⚠️ Firecrawl 不可用 ({detail})，尝试 restart...")
    ok, out = compose_restart()
    if ok:
        time.sleep(RETRY_WAIT)
        if check_firecrawl()[0]:
            print("✅ Firecrawl restart 恢复")
            return

    # 4. Full up as fallback
    print(f"  → restart 未恢复，尝试 up -d...")
    ok, out = compose_up()
    if ok:
        time.sleep(RETRY_WAIT)
        if check_firecrawl()[0]:
            print("✅ Firecrawl up -d 恢复")
            return

    # 5. Failed
    print(f"❌ Firecrawl 修复失败 ({detail})")
    print(f"  → 手动: cd {COMPOSE_DIR} && docker compose logs --tail=30")


if __name__ == "__main__":
    main()
