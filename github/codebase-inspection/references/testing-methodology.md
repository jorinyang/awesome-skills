# Repository Testing Methodology

Step-by-step playbook for comprehensive Python repository testing and audit.

## Pre-flight

```bash
git clone <repo_url> /tmp/repo-test
cd /tmp/repo-test
```

## Step 1: Structure Discovery (parallel subagents OK)

Two parallel tasks:
1. **Tree + metadata**: `find . -type f | head -200`, read README, pyproject.toml, MANIFEST.json
2. **Source inventory**: Read all .py files, catalog classes/functions/imports

Output: directory tree, file sizes, module map, dependency list, entry points.

## Step 2: Run Existing Tests

```bash
# Create isolated env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt 2>/dev/null
pip install pytest pytest-xdist httpx 2>/dev/null

# Run with full output
python -m pytest tests/ -v --tb=long 2>&1
```

Record:
- Which files pytest collects (some may be standalone scripts)
- Fixture resolution errors (parameter names mistaken for fixtures)
- Pass/fail counts per file
- Warnings (PytestReturnNotNoneWarning, deprecation)

## Step 3: API Signature Inspection

Before writing ANY test, inspect actual signatures:

```python
import inspect
import sys
sys.path.insert(0, '/tmp/repo-test')

from target_module import TargetClass

# Constructor
print(inspect.signature(TargetClass.__init__))

# All callable public methods
for name in sorted(dir(TargetClass)):
    if not name.startswith('_'):
        attr = getattr(TargetClass, name)
        if callable(attr):
            try:
                print(f"  {name}{inspect.signature(attr)}")
            except:
                print(f"  {name}(...)")
        elif isinstance(attr, property):
            print(f"  {name} [property]")
```

**Common mismatches discovered:**
| Assumed | Actual |
|---------|--------|
| `ClawShellEvent(data={})` | `ClawShellEvent(payload={})` |
| `Task(assigned_edge="n1")` | `Task(assigned_to="n1")` |
| `EdgeNode(name="n1")` | `EdgeNode(node_name="n1")` |
| `Insight(source_edge="n1")` | `Insight(source_edges=["n1"])` |
| `bus.stats()` | `bus.get_stats()` (property vs method) |
| `sm.publish_skill(...)` | `sm.publish({...})` |
| `Step(type="sequential")` | `Step(step_type=StepType.TASK)` |

## Step 4: Iterative Test Writing

Use `execute_code` (NOT delegate_task — subagents timeout at 600s on test loops):

```python
import sys
sys.path.insert(0, '/tmp/repo-test')

results = []
def test(name, fn):
    try:
        fn()
        results.append(("PASS", name, ""))
    except Exception as e:
        results.append(("FAIL", name, f"{type(e).__name__}: {e}"))

# Write tests grouped by module
def test_feature_x():
    obj = SomeClass()
    result = obj.method(arg1, arg2)
    assert result is not None

test("module/feature_x", test_feature_x)

# Print summary
for status, name, err in results:
    print(f"{'✅' if status=='PASS' else '❌'} {name}")
    if err: print(f"   └─ {err}")
```

Iterate: run → fix failures by re-inspecting → rerun.

## Step 5: Scenario Tests

After unit tests stabilize, test full workflows:

- **Lifecycle flows**: create → use → complete → verify
- **State machines**: all valid transitions + invalid transition guards
- **Pipeline tests**: module A output → module B input
- **Concurrent access**: 5 threads writing simultaneously

## Step 6: Boundary Tests

- Empty data / None fields
- Unicode / Emoji / special chars
- Very long strings (100K+)
- Invalid enum values
- Non-existent IDs
- Malformed JSON

## Step 7: Report Generation

Structure:

```markdown
# <Project> v<X.Y.Z> — Comprehensive Test Report

## Executive Summary
| Metric | Value |
|--------|-------|
| Total tests | N |
| Passed | N |
| Failed | N |
| Pass rate | X% |

## Existing Test Suite Analysis
- pytest results per file
- Coverage gaps identified
- Fixture/collection issues

## Unit Test Results (grouped by module)
| Category | Pass | Fail | Total | Rate |
|----------|------|------|-------|------|

## Scenario Test Results
- Lifecycle flows
- State machine transitions
- Pipeline integration

## Boundary Test Results
- Edge cases tested
- Thread safety results

## Issues Found
### High Priority
### Medium Priority
### Low Priority

## Recommendations
```

## Anti-patterns to Avoid

1. **Don't assume — inspect**: Always check actual API before writing tests
2. **Don't use subagents for test loops**: They timeout. Use execute_code.
3. **Don't write change-detector tests**: Test relationships, not snapshots
4. **Don't skip existing test analysis**: Run pytest first to find baseline issues
5. **Don't ignore version inconsistencies**: Check all version sources
