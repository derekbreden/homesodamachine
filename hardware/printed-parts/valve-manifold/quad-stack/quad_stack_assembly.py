"""Quad-stack assembly — 3 source-selection cells stacked.

Three quad-trays (`../quad-tray/`, each a floor + two side walls), each holding
4 Beduan valves + 2 Y-dividers, stacked one `stack_pitch` (63 mm) apart. Each
floor rests on the wall tops below, clearing the coils.

A flat cq.Assembly of pre-positioned solids, colored + named, written as one
multi-solid STEP via export_assembly. The /3d viewer renders all solids gray.
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
    _hw / "printed-parts" / "valve-manifold" / "quad-tray",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import quad_tray as q

N_LEVELS = 3
PITCH = q.stack_pitch  # 63 mm

TRAY_COLOR = cq.Color(0.85, 0.78, 0.62)     # PETG tan
VALVE_COLOR = cq.Color(0.20, 0.22, 0.26)    # solenoid body/coil, dark
DIVIDER_COLOR = cq.Color(0.30, 0.55, 0.85)  # divider, blue


def build_stack():
    tray = q.build_quad_tray().val()
    parts = q.build_assembly()  # one cell's worth: VA VB VC VD YA YB (solids)

    assy = cq.Assembly(name="quad-stack-assembly")
    for i in range(N_LEVELS):
        dz = i * PITCH
        assy.add(tray.translate((0, 0, dz)), name=f"tray-{i}", color=TRAY_COLOR)
        for k in ("VA", "VB", "VC", "VD"):
            assy.add(parts[k].translate((0, 0, dz)), name=f"{k}-{i}", color=VALVE_COLOR)
        for k in ("YA", "YB"):
            assy.add(parts[k].translate((0, 0, dz)), name=f"{k}-{i}", color=DIVIDER_COLOR)
    return assy


def main():
    export_assembly(build_stack(), str(_here.parent / "quad-stack-assembly.step"))
    print("-> quad-stack-assembly.step")


if __name__ == "__main__":
    main()
