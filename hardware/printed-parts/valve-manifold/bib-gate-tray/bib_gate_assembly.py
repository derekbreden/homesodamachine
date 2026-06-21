"""Assembled BiB-gate tray: the tray with its 2 valves + 4 Y-dividers seated
in place.
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
    _hw / "printed-parts" / "valve-manifold" / "bag-circuit-tray",
    _here.parent,
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import bib_gate_tray as t

TRAY_COLOR = cq.Color(0.85, 0.78, 0.62)     # PETG tan
VALVE_COLOR = cq.Color(0.20, 0.22, 0.26)    # solenoid body/coil, dark
DIVIDER_COLOR = cq.Color(0.30, 0.55, 0.85)  # divider/tee, blue
ELBOW_COLOR = cq.Color(0.80, 0.45, 0.20)    # elbow, copper


def _part_color(nm):
    if nm.startswith("E"):
        return ELBOW_COLOR
    if nm.startswith("Y"):
        return DIVIDER_COLOR
    return VALVE_COLOR


def build():
    assy = cq.Assembly(name="bib-gate-assembly")
    assy.add(t.build_bib_gate_tray().val(), name="tray", color=TRAY_COLOR)
    for nm, part in t.build_assembly().items():
        assy.add(part, name=nm, color=_part_color(nm))
    return assy


def main():
    export_assembly(build(), str(_here.parent / "bib-gate-assembly.step"))
    print("-> bib-gate-assembly.step")


if __name__ == "__main__":
    main()
