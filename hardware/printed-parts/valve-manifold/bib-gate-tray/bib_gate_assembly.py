"""Assembled BiB-gate tray: the tray with its 2 valves + 4 Y-dividers seated
in place. A flat cq.Assembly of pre-positioned solids, colored and named,
written as one multi-solid STEP. The /3d viewer renders all gray.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw,
    _hw / "printed-parts" / "reference" / "beduan-solenoid",
    _hw / "printed-parts" / "valve-manifold" / "single-tray",
    _hw / "printed-parts" / "valve-manifold" / "bag-circuit-tray",
    _here.parent,
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import bib_gate_tray as t

TRAY_COLOR = cq.Color(0.85, 0.78, 0.62)     # PETG tan
VALVE_COLOR = cq.Color(0.20, 0.22, 0.26)    # solenoid body/coil, dark
DIVIDER_COLOR = cq.Color(0.30, 0.55, 0.85)  # divider, blue


def build():
    assy = cq.Assembly(name="bib-gate-assembly")
    assy.add(t.build_bib_gate_tray().val(), name="tray", color=TRAY_COLOR)
    for nm, part in t.build_assembly().items():
        color = DIVIDER_COLOR if nm.startswith("Y") else VALVE_COLOR
        assy.add(part, name=nm, color=color)
    return assy


def main():
    export_assembly(build(), str(_here.parent / "bib-gate-assembly.step"))
    print("-> bib-gate-assembly.step")


if __name__ == "__main__":
    main()
