#!/usr/bin/env python3
"""Whether `web/`'s test suite passes on this tree.

THE SUITE IS NOT A `check_*.py`, SO NOTHING RAN IT. `checks.py` finds its checks by globbing
`check_*.py`, which is what makes a check added tomorrow run tomorrow — and it is also why a
suite written in another language is outside the set no matter how long it has been red. 209
node tests sat at HEAD with failures nobody was reading. This is the glob's name for them.

IT RUNS THE SUITE RATHER THAN RESTATING IT. `npm test` is the whole contract; this reads its
TAP and reports what failed.

NOT RUN IS RED, NOT GREEN. Without `web/node_modules` the suite cannot run, and a check that
answers green because it never asked is the exact shape being repaired here — green renders
nothing on the site, so a silent skip is indistinguishable from a passing suite. The repair
is one command and it is printed.

NO CLOCK AND NO COUNTS THAT MOVE ON THEIR OWN. `checks.py --json` is committed, so a verdict
holding durations would commit on every commit forever. TAP carries `duration_ms` on every
assertion and a total on the run; none of it is read here. What is printed is which tests
failed, by name, in the order TAP numbered them.
"""

import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
WEB = _ROOT / "web"

#: Long enough for the suite's own slow members — several stand the dependency scanner against
#: the live tree and take seconds each — and short enough that a hang is reported rather than
#: inherited by the reader that runs this.
TIMEOUT_S = 300


def failures(tap: str) -> list:
    """The name of every TAP assertion that did not pass, in the order TAP numbered them.

    `not ok <n> - <name>`. The number is the suite's own index and the name is the test's, so
    two runs over one tree write these bytes identically."""
    out = []
    for line in tap.splitlines():
        stripped = line.strip()
        if not stripped.startswith("not ok "):
            continue
        rest = stripped[len("not ok "):]
        name = rest.split(" - ", 1)[1] if " - " in rest else rest
        out.append(name.strip())
    return out


def main(argv) -> int:
    if not (WEB / "node_modules").is_dir():
        print("web/node_modules is absent, so the suite did not run")
        print("  cd web && npm ci")
        return 1

    try:
        run = subprocess.run(["npm", "test"], cwd=str(WEB), capture_output=True,
                             text=True, timeout=TIMEOUT_S)
    except FileNotFoundError:
        print("npm is not on PATH, so the suite did not run")
        print("  install node, then: cd web && npm ci")
        return 1
    except subprocess.TimeoutExpired:
        print(f"the suite did not finish within {TIMEOUT_S}s")
        print("  cd web && npm test")
        return 1

    tap = (run.stdout or "") + (run.stderr or "")
    bad = failures(tap)

    if run.returncode == 0 and not bad:
        print("check_web_tests: web's suite passes")
        return 0

    if bad:
        print(f"{len(bad)} test(s) in web/ fail:")
        for name in bad:
            print(f"    {name}")
    else:
        print(f"web's suite exited {run.returncode} without naming a failed test")

    print("  cd web && npm test")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
