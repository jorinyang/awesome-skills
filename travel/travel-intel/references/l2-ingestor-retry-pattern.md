# L2 Ingestor 99991400 Retry Pattern

**Added**: 2026-06-14 | **Version**: l2_ingestor.py v2 (with retry)

## The Pattern

```python
MAX_RETRIES = 3  # retry on 99991400 rate-limit errors
RETRY_DELAY = 15  # seconds

def ingest_one(item, cls, node, date_str):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # ... API call to lark-cli docs +create ...
            
            if data.get("ok"):
                return True, detail
            else:
                err = data.get("error", {})
                code = err.get('code', 0)
                if code == 99991400 and attempt < MAX_RETRIES:
                    print(f"    ⏳ 99991400 retry {attempt}/{MAX_RETRIES} in {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)
                    continue  # retry the loop
                return False, detail
        except Exception as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return False, str(e)
        finally:
            # Always clean up temp XML file
            if os.path.exists(xml_file):
                os.unlink(xml_file)
    
    return False, "max retries exceeded"
```

## Key Design Decisions

1. **finally inside loop**: The `finally` block runs every iteration (including on `continue`), so cleanup happens before retry. The temp XML is recreated at the start of each iteration — this is safe.

2. **3 retries, 15s delay**: More aggressive than the original no-retry approach. In practice (2026-06-14, 52 items) no retries were needed with BATCH=6/COOL=15/DELAY=5.

3. **Exception retries too**: Network/JSON errors also get retried (not just 99991400), since transient failures can look like exceptions.

## Script Versions in /tmp

| Version | BATCH | COOL | DELAY | RETRY | Notes |
|---------|:-----:|:----:|:-----:|:-----:|-------|
| `/tmp/l2_ingestor_v2.py` | 8 | 12s | 4s | ❌ None | Early version, sub-token stale |
| `/tmp/l2_ingestor_fixed.py` | 8 | 12s | 4s | ❌ None | PARENT_TOKEN fallback added |
| `scripts/l2_ingestor.py` | 6 | 15s | 5s | ✅ 3x/15s | Current: retry + conservative batching |

## lark-cli @file Path Requirement

lark-cli 1.0.40 requires `--content @filename` to use a **relative path** within the current working directory. The script handles this by:
1. Writing XML to `/tmp/l2_<timestamp>.xml`
2. Extracting basename via `os.path.basename(xml_file)`
3. Running `subprocess.run(..., cwd="/tmp")` so `@basename` resolves correctly

If lark-cli is upgraded, verify this behavior hasn't changed.
