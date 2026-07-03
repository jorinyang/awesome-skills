#!/usr/bin/env python3
"""Ad-hoc verification of expiry_checker.py Windows patch (2026-07-03).

Run after ANY change to expiry_checker.py mark_expired() or its environment
injection logic. This is NOT a test suite — it's a focused 14-assertion probe
that mocks subprocess.run and validates the patched behavior in isolation.

Why this exists: the original two Windows bugs (SYSTEM-user expanduser
resolves wrong + lark-cli.cmd vs lark-cli extension) were both silent
failures — the script exited 0 but marked zero documents. Mocking
subprocess lets us assert *intent* (correct argv, correct PATH) without
needing lark-cli to actually be installed or the API to be reachable.

Usage:
    python3 scripts/verify_expiry_checker_patch.py

Returns exit 0 on all-pass, exit 1 on any fail. Cleanup-safe (no temp files).
"""
import os
import sys
import subprocess
from unittest import mock

SCRIPT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "expiry_checker.py",
)
AORUS_NPM = r"C:\Users\Aorus\AppData\Roaming\npm"


def assert_true(cond, msg):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {msg}")
    return bool(cond)


def main():
    # Force import from the same dir as this script
    sys.path.insert(0, os.path.dirname(SCRIPT))
    import expiry_checker as ec  # noqa: E402

    print("=== Verifying expiry_checker.py patch ===\n")

    # --- [1] Source-level invariants ---
    print("[1] Source-level invariants:")
    src = open(SCRIPT, encoding="utf-8").read()
    ok = True
    ok &= assert_true(AORUS_NPM in src, "AORUS_NPM path present in source")
    ok &= assert_true("lark-cli.cmd" in src, "source uses 'lark-cli.cmd' explicitly")
    ok &= assert_true(
        "os.name" in src and ('"nt"' in src or "'nt'" in src),
        "source has os.name=='nt' guard",
    )
    ok &= assert_true(
        "expanduser resolves wrong" in src.lower() or "systemprofile" in src.lower(),
        "source documents the SYSTEM-user expanduser pitfall",
    )

    # --- [2] Behavior: mark_expired() with mocked subprocess ---
    print("\n[2] mark_expired() behavior (mocked subprocess):")
    captured = {}

    def fake_run(argv, *args, **kwargs):
        captured["argv"] = list(argv)
        captured["env"] = dict(kwargs.get("env", {}))
        return subprocess.CompletedProcess(args=argv, returncode=0, stdout='{"ok":true}', stderr="")

    fake_doc = {"obj_token": "TEST_TOKEN_123", "title": "2026-05-30_测试文档"}
    fake_rule = {"type": "酒店/交通价格", "weight": 0.2}
    fake_age = 34

    with mock.patch.object(ec.subprocess, "run", side_effect=fake_run):
        rc_ok = ec.mark_expired(fake_doc, fake_rule, fake_age, dry_run=False)

    ok &= assert_true(rc_ok is True, "mark_expired() returns True")
    argv0 = captured.get("argv", [None])[0]
    expected_bin = "lark-cli.cmd" if os.name == "nt" else "lark-cli"
    ok &= assert_true(
        argv0 == expected_bin,
        f"argv[0] is platform-correct: {argv0!r} (expected {expected_bin!r})",
    )
    ok &= assert_true(
        AORUS_NPM in captured.get("env", {}).get("PATH", ""),
        "subprocess env PATH contains Aorus npm dir",
    )
    ok &= assert_true(
        "drive" in captured.get("argv", []) and "+add-comment" in captured.get("argv", []),
        "argv contains 'drive +add-comment'",
    )
    ok &= assert_true(
        "TEST_TOKEN_123" in captured.get("argv", []),
        "argv contains doc obj_token",
    )

    # --- [3] Dry-run mode does NOT call subprocess ---
    print("\n[3] Dry-run isolation:")
    captured.clear()
    with mock.patch.object(ec.subprocess, "run", side_effect=fake_run):
        rc_dry = ec.mark_expired(fake_doc, fake_rule, fake_age, dry_run=True)
    ok &= assert_true(rc_dry is True, "dry-run returns True")
    ok &= assert_true(len(captured) == 0, "dry-run does NOT invoke subprocess")

    # --- [4] Syntax sanity ---
    print("\n[4] Script syntax:")
    import py_compile
    try:
        py_compile.compile(SCRIPT, doraise=True)
        ok &= assert_true(True, "script compiles without syntax errors")
    except py_compile.PyCompileError as e:
        ok &= assert_true(False, f"compile failed: {e}")

    # --- [5] Windows PATH resolution sanity (manual) ---
    print("\n[5] PATH resolution sanity (Windows-specific):")
    bad_home = os.path.expanduser("~/AppData/Roaming/npm")
    ok &= assert_true(
        "systemprofile" in bad_home or "Users" not in bad_home,
        f"expanduser('~/...') under SYSTEM resolves to {bad_home!r}",
    )
    ok &= assert_true(
        os.path.isdir(AORUS_NPM),
        f"AORUS_NPM dir exists: {AORUS_NPM}",
    )
    ok &= assert_true(
        os.path.isfile(os.path.join(AORUS_NPM, "lark-cli.cmd")),
        f"lark-cli.cmd shim exists at {AORUS_NPM}/lark-cli.cmd",
    )

    # --- Final ---
    print("\n" + "=" * 50)
    if ok:
        print("ALL CHECKS PASSED")
        return 0
    else:
        print("SOME CHECKS FAILED — see above")
        return 1


if __name__ == "__main__":
    sys.exit(main())