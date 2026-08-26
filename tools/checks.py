#!/usr/bin/env python3
"""checks.py — every check in this tree, run against this tree, in one place.

    tools/cad-venv/bin/python tools/checks.py            every check, a line each
    tools/cad-venv/bin/python tools/checks.py --list     name them and run none
    tools/cad-venv/bin/python tools/checks.py --json P   write the verdict to P as well

FOUND BY GLOB, NOT BY LIST. `check_*.py` under `hardware/scripts/`, `tools/` and `tools/bazel/`
is the whole set, so a check added tomorrow is run tomorrow. A list is a second place to
remember, and the thing being guarded here is checks nobody remembers to run.

`--json` CARRIES NO CLOCK. Durations and a run time are in the terminal reading and not in the
file, so an unchanged tree writes byte-identical bytes and `checks_now.py`, which commits it,
finds nothing to commit.

A SELFTEST AND A CHECK ANSWER DIFFERENT QUESTIONS. `selftests.json` registers four of these and
`tools/bazel/selftest.sh` runs `<script> selftest` — the script's own rules held against
fixtures it builds. That passes while the same script, run against the tree, reports rot: the
rules are right and the tree does not satisfy them. This runs the second question.

IT REPORTS AND HOLDS NOTHING. Exit is non-zero when a check is red, which is a status for
whoever asked, and no caller here treats it as permission — `derive` runs it with
`continue-on-error` so the reconcile finishes and the red rides out with it. A check that could
stop the tree reaching the site would be the one thing this tree does not do.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIRS = ("hardware/scripts", "tools", "tools/bazel")
PY = ROOT / "tools" / "cad-venv" / "bin" / "python"


def checks() -> list:
    seen, out = set(), []
    for d in DIRS:
        for p in sorted((ROOT / d).glob("check_*.py")):
            rel = str(p.relative_to(ROOT))
            if rel not in seen:
                seen.add(rel)
                out.append(rel)
    return out


def verdict(rows: list, red: list) -> dict:
    """The reading with nothing volatile in it, for the file the site serves.

    NO DURATIONS AND NO TIMESTAMP: what each check found, and nothing about the machine that
    ran it. When the reading was taken is the date of the commit carrying it.

    `[build]` IS THE MACHINE TALKING AND IT CARRIES PIDS. A check that imports a CAD generator
    takes `_run_lock.py`'s global lock, which narrates whose build it is queueing behind:

        [build] a manual build is already running (pid 76191, enclosure_assembly.py) — waiting

    Those lines differ every run, so a verdict holding them differs every run, and this file is
    committed. The terminal reading above keeps them — there they say why a check took 900s.
    """
    detail = {}
    for rel, out, err in red:
        body = ((out or "") + (err or "")).strip().splitlines()
        kept = [ln.rstrip() for ln in body if ln.strip() and not ln.lstrip().startswith("[build]")]
        detail[rel] = kept[-25:]
    return {
        "green": not red,
        "checks": [{"check": rel, "status": "ok" if code == 0 else "red", "note": note}
                   for rel, code, _took, note in rows],
        "detail": detail,
    }


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="name them and run none")
    ap.add_argument("--json", metavar="PATH", help="also write the verdict here, clock-free")
    args = ap.parse_args(argv)

    found = checks()
    if args.list:
        for c in found:
            print(f"  {c}")
        print(f"{len(found)} check(s)")
        return 0

    python = str(PY) if PY.exists() else sys.executable
    red, rows = [], []
    for rel in found:
        started = time.time()
        run = subprocess.run([python, rel], cwd=str(ROOT),
                             capture_output=True, text=True)
        took = time.time() - started
        tail = [ln for ln in (run.stdout or run.stderr).splitlines() if ln.strip()]
        rows.append((rel, run.returncode, took, tail[-1].strip() if tail else ""))
        if run.returncode != 0:
            red.append((rel, run.stdout, run.stderr))

    width = max(len(r) for r, *_ in rows)
    for rel, code, took, note in rows:
        mark = "ok  " if code == 0 else "RED "
        print(f"  {mark} {rel:<{width}}  {took:5.1f}s  {note[:64]}")

    print(f"\n{len(rows) - len(red)}/{len(rows)} green, "
          f"{sum(t for _, _, t, _ in rows):.0f}s total")

    for rel, out, err in red:
        print(f"\n──── {rel} ────")
        body = (out or "") + (err or "")
        for ln in body.strip().splitlines()[-25:]:
            print(f"  {ln}")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(verdict(rows, red), indent=2, sort_keys=True,
                                  ensure_ascii=False) + "\n")

    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
