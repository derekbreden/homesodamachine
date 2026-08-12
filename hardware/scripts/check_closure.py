#!/usr/bin/env python3
"""check_closure.py — whether the source walk names every module a build actually reads.

`_realized.source_files` reads import statements to say whose text can decide what a module
draws, and that answer is what keys the wall cache and what every `.sources.json` records. A
module the walk misses is a module that can move while a cached wall, a card and a document all
hold still.

    tools/cad-venv/bin/python hardware/scripts/check_closure.py     (0 = covered, 1 = a gap)

WHAT THIS COSTS IS ONE BUILD. It stands the machine through the same call the generators use,
watches which of this repo's modules Python loads while that runs, and asks the walk whether it
named each one. `_realized.ENTRY_POINTS` is what makes this worth running: the walk stops at
`main` and `selftest`, so the modules a RUN imports to export and draw are left out of the
shape's closure, and this is the reading that says nothing else went with them.
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_HW = next(p for p in _HERE.parents if p.name == "hardware")
_ROOT = _HW.parent
for _p in (_HW / "scripts", _HW / "manifold-layout"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import _realized                                        # noqa: E402


def repo_modules() -> dict:
    """`{module name: file}` for every loaded module whose file is in this repo."""
    out = {}
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f or not f.endswith(".py"):
            continue
        path = Path(f).resolve()
        if _ROOT in path.parents and "site-packages" not in path.parts:
            out[name] = path
    return out


def main() -> int:
    import enclosure_assembly as ea

    walked = set(_realized.source_files(ea.__file__))
    mine = set(repo_modules().values())            # loaded to get here, not by the build

    print("standing the machine...")
    ea.build_enclosure_assembly()

    loaded = repo_modules()
    missed = sorted((n, p) for n, p in loaded.items() if p not in walked and p not in mine)

    print(f"  the walk names {len(walked)} files")
    print(f"  the build read {len(loaded)} of this repo's modules")
    for name, path in missed:
        print(f"  MISSED {name:32} {path.relative_to(_ROOT)}")
    if missed:
        print(f"\n{len(missed)} module(s) decide the build and are not in its closure. A cached "
              f"wall, a card and a document all hold still while these move. Import them outside "
              f"`_realized.ENTRY_POINTS`, or name them where the walk can reach.")
        return 1
    print("\nevery module the build read is named by the walk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
