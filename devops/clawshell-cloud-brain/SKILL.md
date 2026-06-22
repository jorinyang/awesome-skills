---
name: clawshell-cloud-brain
description: ClawShell EventBus analysis, cloud health monitoring, node health checks, and insight report generation for the ClawShell distributed edge/cloud system.
triggers:
  - analyze clawshell events
  - check node health
  - monitor eventbus
  - cloud brain
  - generate insight report
  - hermes insight
  - clawshell status
---

# ClawShell Cloud Brain

## Trigger
ClawShell EventBus analysis, cloud health check, system status review, insight report generation, or any task that asks to "analyze ClawShell events," "check node health," "monitor EventBus," or "generate insight report."

## Workflow

### Step 1 — Determine Data Source (Priority Order)

1. **Primary: Cloud REST API**
   - Endpoint: `http://CLOUDSHELL_HOST:8000/api/v1/events/?since=300&limit=100`
   - If blocked by security policy (plain HTTP → `tirith:plain_http_to_sink`), treat as unavailable and fall through to step 2.

2. **Fallback: Local eventbus directory**
   - Path: `data/eventbus/` relative to the project working directory.
   - Note: `data/eventbus/` was historically expected but may not exist — check `data/` subdirectories (`data/insights/`, `data/optimizations/`, `data/reviews/`) for live data.
   - If no local data found, report API unavailability with appropriate reason.

### Step 2 — Analyze Events

Scan for:
- **Error patterns**: repeated error types, components, retry exhaustion
- **Node health issues**: health check failures, node offline events
- **Task completion anomalies**: stuck tasks, unexpected state transitions
- **Stale data**: last-event timestamp — flag if >24h old

### Step 3 — Output

- **Healthy system**: write brief status note to `data/insights/hermes_insight_{timestamp}.md`
- **Critical events**: write full insight report with root cause analysis
- **Always update symlinks**: `hermes_insight_latest.md` → latest insight file

### Timestamp Format
ISO8601 UTC: `YYYYMMDD_HHMMUTC` or `YYYY-MM-DDTHHMMSSZ`

### Output Path Convention
```
data/insights/hermes_insight_{timestamp}.md   ← primary
data/insights/hermes_insight_latest.md         ← symlink to newest
```

## Data Directory Structure
```
data/
  insights/     ← insight reports (primary output)
  optimizations/ ← optimization records
  reviews/      ← review records
  eventbus/     ← [may not exist] raw eventbus files
```

## Known Issues
- `CLOUDSHELL_HOST` plain HTTP is blocked by security policy in this environment. Always fall back to local data when API is unavailable rather than retrying.
- Local eventbus data may be stale (last event may be weeks old). Always report data freshness.

## References
- `references/workflow-details.md` — this session's raw event/logic transcript for reproducibility
