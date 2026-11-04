#!/usr/bin/env python3
"""Generator timing windows and stable document figures, maintained in Rust."""
import json
import sys
from pathlib import Path
from _ledger_rust import call, main as _main

HERE = Path(__file__).resolve().parent
BT = HERE.parent / 'ledger/build-time.md'
SAMPLES = HERE.parent / 'ledger/.build-time.samples.json'
WINDOW = 5
BAND = 0.10

def record(label, seconds):
    try:
        call('build.record', samples=SAMPLES, label=label, seconds=seconds)
    except Exception:
        pass

def held():
    return call('build.held', samples=SAMPLES)

def marker_of(gen):
    return call('build.marker', gen=gen)

def fmt(seconds):
    return call('build.fmt', seconds=seconds)

def settle(standing, got):
    return call('build.settle', standing=standing, seconds=got)

def rows():
    return [tuple(row) for row in call('build.rows', build_time=BT)]

def figures():
    return tuple(call('build.figures', samples=SAMPLES, build_time=BT))

def main():
    return _main('build.main', samples=SAMPLES, build_time=BT, check='--check' in sys.argv)

def selftest() -> int:
    """A busier machine does not move a row, and slower work does.

    WHAT THIS HOLDS IS A RULE AND NOT A DIMENSION: no reading of this machine is asserted.
    The fixture writes its own window and asks what this file makes of it."""
    import tempfile

    global SAMPLES
    holds = 0

    def check(label, got, want):
        nonlocal holds
        ok = got == want
        holds += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:46s} got {got!r}  want {want!r}")

    was = SAMPLES
    with tempfile.TemporaryDirectory() as d:
        SAMPLES = Path(d) / "samples.json"

        # A window carrying one idle run and three under load reads as the idle one.
        SAMPLES.write_text(json.dumps({"g/a.py": [5.65, 9.09, 10.48, 5.71]}))
        check("a loaded window reads as its idle floor", held()["g/a.py"], 5.65)

        # WINDOW readings are kept and the oldest falls off.
        SAMPLES.unlink()
        for s in range(1, WINDOW + 3):
            record("g/b.py", float(s))
        kept = json.loads(SAMPLES.read_text())["g/b.py"]
        check("a window holds WINDOW readings", len(kept), WINDOW)
        check("and drops the oldest", kept[0], float(3))
    SAMPLES = was

    check("a busier machine does not move the row", settle("5.6", 5.9), "5.6")
    check("slower work does", settle("5.6", 7.0), "7.0")
    check("a row with no figure yet takes one", settle("—", 5.65), "5.7")
    check("over ten seconds drops the decimal", fmt(12.4), "12")
    check("a generator's marker is its stem",
          marker_of("hardware/manifold-layout/enclosure_assembly.py"),
          "BT_ENCLOSURE_ASSEMBLY")
    check("a leading underscore is not part of the name",
          marker_of("hardware/assembly/_cold_core_sync.py"), "BT_COLD_CORE_SYNC")

    print("selftest: OK" if not holds else f"selftest: {holds} FAILED")
    return 1 if holds else 0


if __name__ == '__main__':
    sys.exit(selftest() if sys.argv[1:2] == ['selftest'] else main())
