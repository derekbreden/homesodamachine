"""Assembled single-valve tray: the tray with its one valve seated.

The valve and nothing else. No divider, no tee, no elbow — the tray carries no
fitting, so neither does its assembly.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "beduan-solenoid",
    _hw / "printed-parts" / "valve-manifold" / "single-tray",
    _hw / "printed-parts" / "valve-manifold" / "two-valve-tray",
    _here.parent,
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import single_valve_tray as t

TRAY_COLOR = cq.Color(0.85, 0.78, 0.62)   # PETG tan
VALVE_COLOR = cq.Color(0.20, 0.22, 0.26)  # solenoid body/coil, dark


def build():
    assy = cq.Assembly(name="single-valve-assembly")
    assy.add(t.build_single_valve_tray().val(), name="tray", color=TRAY_COLOR)
    for nm, part in t.build_assembly().items():
        assy.add(part, name=nm, color=VALVE_COLOR)
    return assy


def main():
    export_assembly(build(), str(_here.parent / "single-valve-assembly.step"))
    print("-> single-valve-assembly.step")


if __name__ == "__main__":
    main()
