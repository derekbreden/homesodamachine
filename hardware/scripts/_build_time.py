#!/usr/bin/env python3
"""Seconds a generator run takes, written into build-time.md's [value](NAME) markers.
Fourth of the ledger scripts, beside _bom_totals.py (dollars), _labor_totals.py (attended
minutes) and _machine_time.py (machine hours). This one owns SECONDS SOMEBODY WAITS.

`_cadq_export` calls `record` at process exit, once per run that cut something. This reads
what those runs left.

THE FIGURE IS THE SMALLEST READING IN A WINDOW OF [5](BT_WINDOW). Four runs of the
enclosure's canonicalization on an idle machine spread 2.6 %; the same four with six cores
busy spread 14.4 %, every one of them above the idle floor.

Inside [10](BT_BAND) % of the figure already in the file, the figure already in the file
stands.

The readings are this machine's and are not tracked. The figure they settle on is. A
checkout that has run nothing moves nothing here.

Rows are hand-kept, as bom.md's are — which generators a reader wants is a judgement, and
`--check` names a generator that has readings and no row.

Run:  python3 hardware/scripts/_build_time.py           # re-derive + write markers
      python3 hardware/scripts/_build_time.py --check    # exit 1 on an untracked
                                                         # generator or a stale marker
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BT = HERE.parent / "ledger" / "build-time.md"

#: This machine's rolling windows. Untracked — see .gitignore.
SAMPLES = HERE.parent / "ledger" / ".build-time.samples.json"

sys.path.insert(
    0, str(next(p for p in HERE.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
from docgen import cells, substitute_md   # noqa: E402

#: How many runs a generator's window holds. The figure is the smallest of them.
WINDOW = 5

#: How far a new reading has to be from the one in the file before it replaces it.
BAND = 0.10


def record(label, seconds):
    """Keep `seconds` as one reading of `label`, dropping the oldest past WINDOW.

    Called from a process on its way out; it raises nothing. A reading that does not land
    costs the ledger one run."""
    try:
        data = json.loads(SAMPLES.read_text(encoding="utf-8")) if SAMPLES.exists() else {}
    except (OSError, ValueError):
        data = {}
    runs = [float(x) for x in data.get(label, [])][-(WINDOW - 1):]
    runs.append(round(float(seconds), 2))
    data[label] = runs
    tmp = SAMPLES.with_name(SAMPLES.name + ".tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(tmp, SAMPLES)
    except OSError:
        pass


def held():
    """{generator: seconds} — the smallest reading in each window."""
    try:
        data = json.loads(SAMPLES.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {k: min(float(x) for x in v) for k, v in data.items() if v}


def marker_of(gen):
    """A generator's marker name. `manifold-layout/enclosure_assembly.py` → BT_ENCLOSURE_ASSEMBLY."""
    return "BT_" + Path(gen).stem.strip("_").upper()


def fmt(seconds):
    """The believable increment: one decimal under ten seconds, none over."""
    return f"{seconds:.1f}" if seconds < 10 else f"{round(seconds):d}"


def settle(standing, got):
    """The text a row carries: `got`, unless it lands inside BAND of the text already there."""
    try:
        was = float(standing)
    except (TypeError, ValueError):
        return fmt(got)
    return standing if was and abs(got - was) / was < BAND else fmt(got)


def rows():
    """[(generator path, marker, standing text)] over build-time.md's table, which is what
    says WHICH generators this file carries. A row names its generator in the first cell."""
    out, text = [], BT.read_text(encoding="utf-8")
    for ln in text.splitlines():
        if not ln.startswith("|"):
            continue
        c = cells(ln)
        if len(c) < 3 or all(set(x) <= set("-: ") for x in c):
            continue
        m = re.search(r"\((/[^)]+\.py)\)", c[0])
        if not m:
            continue
        gen = m.group(1).lstrip("/")
        mk = marker_of(gen)
        standing = re.search(r"\[([^\]]*)\]\(%s\)" % mk, ln)
        out.append((gen, mk, standing.group(1) if standing else None))
    return out


def figures():
    """({marker: text}, [generators with readings and no row])."""
    seen = held()
    variables = {"BT_WINDOW": str(WINDOW), "BT_BAND": str(int(BAND * 100))}
    carried = set()
    for gen, mk, standing in rows():
        carried.add(gen)
        got = seen.get(gen)
        if got is None:
            variables[mk] = standing if standing is not None else "—"
        else:
            variables[mk] = settle(standing, got)
    orphans = sorted(g for g in seen if g not in carried)
    return variables, orphans


def main():
    variables, orphans = figures()

    if "--check" in sys.argv:
        if orphans:
            print("generators with readings and no row in build-time.md:")
            for g in orphans:
                print(f"  {g}  {fmt(held()[g])} s")
            return 1
        text = BT.read_text(encoding="utf-8")
        stale = [f"  [{m.group(1)}]({name}) should be [{v}]({name})"
                 for name, v in variables.items()
                 for m in [re.search(r"\[([^\]]*)\]\(%s\)" % name, text)]
                 if m and m.group(1) != str(v)]
        if stale:
            print("build-time.md markers are stale — run _build_time.py:")
            print("\n".join(stale))
            return 1
        print("build-time.md figures ✓")
        return 0

    substitute_md(BT, variables)
    seen = held()
    for gen, mk, _ in rows():
        got = seen.get(gen)
        mark = "" if got is None else f"   (window min of {len(json.loads(SAMPLES.read_text())[gen])})"
        print(f"  {variables[mk]:>5} s  {gen}{mark}")
    if orphans:
        print("\nreadings with no row:")
        for g in orphans:
            print(f"  {g}  {fmt(seen[g])} s")
    return 0


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


if __name__ == "__main__":
    sys.exit(selftest() if sys.argv[1:2] == ["selftest"] else main())
