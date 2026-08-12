"""What this tree owes, and running it.

    python3 hardware/scripts/owed.py            # what is stale, and the commands for it
    python3 hardware/scripts/owed.py --run      # run them until nothing is owed
    python3 hardware/scripts/owed.py selftest

`check_doc_sources`, `check_cards` and `check_scenes` each name the generator that would
make a stale thing current — `run tools/cad-venv/bin/python …` — and between them they know
exactly what a commit owes. This runs that set and nothing else.

IT RUNS TO A FIXPOINT, because one generator can stale another: a sync that rewrites a
figure moves the file a second doc watches. Each pass asks the checks again and runs what is
newly owed, and a pass that adds nothing is where it stops. A pass that owes the same set
twice is a generator that cannot make its own doc current, which is reported rather than
looped on.

IT EXITS, and that is most of the point. A background task that ends hands its session the
completion and the output together, so there is nothing here to watch and no reason to
follow a log: the last line is the verdict and the exit code carries it. Nothing in this
tree needs `tail -f`.
"""

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve()
_HW = _HERE.parent.parent
_ROOT = _HW.parent
_PY = _ROOT / "tools" / "cad-venv" / "bin" / "python"

CHECKS = ("check_doc_sources.py", "check_cards.py", "check_scenes.py")
MAX_PASSES = 4

# Both shapes the checks print: a bare `run <cmd>`, and the cards' `…; run <cmd>` which names
# the script without the interpreter in front of it.
_RUN = re.compile(r"\brun\s+(?P<cmd>\S+(?:\s+\S+)*?)\s*$")


def _ask() -> tuple:
    """Every generator the checks name, in the order they name it, and whether all three
    came back clean."""
    owed, clean = [], True
    for check in CHECKS:
        p = subprocess.run([str(_PY), str(_HW / "scripts" / check)],
                           cwd=str(_ROOT), capture_output=True, text=True)
        if p.returncode != 0:
            clean = False
        for line in (p.stdout + p.stderr).splitlines():
            m = _RUN.search(line.strip())
            if not m:
                continue
            cmd = m.group("cmd").strip()
            if not cmd.startswith("tools/"):
                cmd = f"tools/cad-venv/bin/python {cmd}"
            if cmd not in owed:
                owed.append(cmd)
    return owed, clean


def _run(cmd: str) -> tuple:
    t0 = time.time()
    p = subprocess.run(cmd, shell=True, cwd=str(_ROOT), capture_output=True, text=True)
    return p.returncode, time.time() - t0, (p.stdout + p.stderr)


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", action="store_true", help="run what is owed, to a fixpoint")
    args = ap.parse_args(argv)

    owed, clean = _ask()
    if not owed:
        print("nothing owed — every doc, card and scene carries what its sources make"
              if clean else "nothing to run, but a check is unhappy — read it directly")
        return 0 if clean else 1

    if not args.run:
        print(f"{len(owed)} generator(s) owed:")
        for c in owed:
            print(f"  {c}")
        print("\n  python3 hardware/scripts/owed.py --run")
        return 1

    t0 = time.time()
    ran, seen = 0, None
    for pass_no in range(1, MAX_PASSES + 1):
        if not owed:
            break
        if owed == seen:
            print(f"\nFAILED: the same {len(owed)} generator(s) are owed after running them — "
                  f"one of these cannot make its own doc current:")
            for c in owed:
                print(f"  {c}")
            return 1
        seen = list(owed)
        print(f"pass {pass_no}: {len(owed)} owed")
        for cmd in owed:
            rc, secs, out = _run(cmd)
            ran += 1
            name = cmd.split()[-1].split("/")[-1]
            print(f"  {secs:5.0f}s  exit={rc}  {name}")
            if rc != 0:
                print(f"\nFAILED: {cmd}")
                print("\n".join(out.strip().splitlines()[-15:]))
                return 2
        owed, clean = _ask()

    total = time.time() - t0
    if owed:
        print(f"\nSTILL OWED after {MAX_PASSES} passes: {len(owed)}")
        for c in owed:
            print(f"  {c}")
        return 1
    print(f"\ngreen — {ran} generator(s) in {total:.0f}s, nothing owed")
    return 0


def selftest():
    owed, clean = _ask()
    assert isinstance(owed, list), "the checks did not answer with a list"
    for c in owed:
        assert c.startswith("tools/cad-venv/bin/python "), f"{c} is not runnable as printed"
        assert (_ROOT / c.split()[1]).is_file(), f"{c.split()[1]} is not a file"
    print(f"  the checks name {len(owed)} generator(s), every one of them runnable")
    print(f"  all three checks clean: {clean}")
    print("owed selftest OK")


if __name__ == "__main__":
    if "selftest" in sys.argv[1:]:
        selftest()
        raise SystemExit(0)
    raise SystemExit(main(sys.argv[1:]))
