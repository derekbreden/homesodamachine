#!/usr/bin/env python3
"""check_build_exit.py — every build ends through an exit the lock can see.

A generator takes the global CAD build lock by importing `_cadq_export`, and the lock
publishes the build's status for anyone following it (`_run_lock.py`): the signal
handler reports 143, `sys.excepthook` reports an unhandled exception, and `sys.exit` is
wrapped. `raise SystemExit` reaches none of them — CPython neither routes it through
`excepthook` nor exposes its code to `atexit` — so a build ending that way lands on the
lock's normal-exit status of 0, and a follower reads a failed gate as a pass.

FAILS (exit 1) on a `raise SystemExit` in any script that takes the lock. Scripts that
do not import `_cadq_export` hold no lock and nobody follows them, so they are free to
raise it.

    python3 hardware/scripts/check_build_exit.py
"""

import re
import sys
from pathlib import Path

_HW = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"__pycache__", ".pio", "node_modules", "cad-venv", "pcb-venv"}
TAKES_LOCK = re.compile(r"^\s*(?:from\s+_cadq_export\s+import|import\s+_cadq_export)", re.M)
RAISES = re.compile(r"^\s*raise\s+SystemExit\b", re.M)

failures = []
scanned = 0

for path in sorted(_HW.rglob("*.py")):
    if any(part in SKIP_DIRS or part.startswith(".") for part in path.parts):
        continue
    try:
        src = path.read_text()
    except OSError:
        continue
    if not TAKES_LOCK.search(src):
        continue
    scanned += 1
    for m in RAISES.finditer(src):
        line = src[: m.start()].count("\n") + 1
        failures.append(f"{path.relative_to(_HW.parent)}:{line}")

print(f"lock-taking scripts scanned: {scanned}")
if failures:
    print(f"\n{len(failures)} build(s) end on a status the lock cannot record:")
    for f in failures:
        print(f"  ✗ {f}  — use sys.exit(...) so a follower reads the failure")
    sys.exit(1)
print("✓ every lock-taking script ends through sys.exit or an exception")
