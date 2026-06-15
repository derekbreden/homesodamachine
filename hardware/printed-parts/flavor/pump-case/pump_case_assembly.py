"""Assembled pump case: the base and cap seated together as a connected pair.

build_pump_case() returns the two halves in shared world coordinates, so they
are added at their as-built positions — fully mated, not exploded. The base's
tower and the cap's lower extension meet at the stepped split, and the four
snap protrusions on each half overlap in Z with their mates so the two halves
hold together.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _here.parent):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import pump_case as pc

BASE_COLOR = cq.Color(0.85, 0.78, 0.62)  # PETG tan
CAP_COLOR = cq.Color(0.30, 0.55, 0.85)   # PETG, contrasting tone


def build():
    base, cap = pc.build_pump_case()
    assy = cq.Assembly(name="pump-case-assembly")
    assy.add(base.val(), name="base", color=BASE_COLOR)
    assy.add(cap.val(), name="cap", color=CAP_COLOR)
    return assy


def main():
    export_assembly(build(), str(_here.parent / "pump-case-assembly.step"))
    print("-> pump-case-assembly.step")


if __name__ == "__main__":
    main()
