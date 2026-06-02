"""Assembled bag-circuit tray: the tray with its 4 valves + 2 Y-dividers
seated in place.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw,
    _hw / "reference" / "beduan-solenoid",
    _hw / "printed-parts" / "valve-manifold" / "single-tray",
    _here.parent,
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import bag_circuit_tray as t

TRAY_COLOR = cq.Color(0.85, 0.78, 0.62)     # PETG tan
VALVE_COLOR = cq.Color(0.20, 0.22, 0.26)    # solenoid body/coil, dark
DIVIDER_COLOR = cq.Color(0.30, 0.55, 0.85)  # divider, blue


def build():
    assy = cq.Assembly(name="bag-circuit-assembly")
    assy.add(t.build_bag_circuit_tray().val(), name="tray", color=TRAY_COLOR)
    for nm, part in t.build_assembly().items():
        color = DIVIDER_COLOR if nm.startswith("Y") else VALVE_COLOR
        assy.add(part, name=nm, color=color)
    return assy


def main():
    export_assembly(build(), str(_here.parent / "bag-circuit-assembly.step"))
    print("-> bag-circuit-assembly.step")


if __name__ == "__main__":
    main()
