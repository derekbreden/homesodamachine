"""Giant arrangement of all four tray assemblies (first pass — arranged, not
a final stack).

The [fluid-topology](../../../topology/fluid-topology.md) realized as four
trays placed in space to show how they connect:

- nozzle-gate → bag-circuit → bib-gate sit in series along X. Each tray's
  pump/channel side faces the next: nozzle's Y-D/Y-G outlets toward bag's
  V-F/V-I, bag's V-E/V-H toward bib's Y-C/Y-F (bib is turned 180° about Z so
  its outlets face back toward bag).
- source-select rides above bib-gate, turned 180° about Z so its V-C/V-D
  outlets sit over bib-gate's two Tee branches (which point up).

Connecting tube runs are not modeled; the trays are spaced to leave room for
them. A flat cq.Assembly of pre-positioned, colored solids exported as one
multi-solid STEP. The /3d viewer renders all gray.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_vm = _hw / "printed-parts" / "valve-manifold"
for _p in (
    _hw,
    _hw / "printed-parts" / "reference" / "beduan-solenoid",
    _vm / "single-tray",
    _vm / "bag-circuit-tray",
    _vm / "source-select-tray",
    _vm / "nozzle-gate-tray",
    _vm / "bib-gate-tray",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import source_select_tray as ss
import bag_circuit_tray as bc
import nozzle_gate_tray as nz
import bib_gate_tray as bg

TRAY = cq.Color(0.85, 0.78, 0.62)
VALVE = cq.Color(0.20, 0.22, 0.26)
TEE = cq.Color(1.00, 0.70, 0.30)
DIVIDER = cq.Color(0.30, 0.55, 0.85)
TEE_NAMES = {"YE", "YH", "YKA", "YKB"}

# (label, tray solid, parts dict, rot_z about origin, translate)
PLACEMENTS = [
    ("nozzle", nz.build_nozzle_gate_tray, nz.build_assembly, 0.0, (-135.0, 0.0, 0.0)),
    ("bag", bc.build_bag_circuit_tray, bc.build_assembly, 0.0, (0.0, 0.0, 0.0)),
    ("bib", bg.build_bib_gate_tray, bg.build_assembly, 180.0, (170.0, 0.0, 0.0)),
    ("source", ss.build_source_select_tray, ss.build_assembly, 180.0, (252.0, 0.0, 72.0)),
]


def _color(nm):
    if nm in TEE_NAMES:
        return TEE
    if nm.startswith("Y"):
        return DIVIDER
    return VALVE


def build():
    assy = cq.Assembly(name="manifold-arrangement")
    for label, tray_fn, parts_fn, rotz, t in PLACEMENTS:
        def xf(s):
            return s.rotate((0, 0, 0), (0, 0, 1), rotz).translate(t)

        assy.add(xf(tray_fn().val()), name=f"{label}-tray", color=TRAY)
        for nm, solid in parts_fn().items():
            assy.add(xf(solid), name=f"{label}-{nm}", color=_color(nm))
    return assy


def main():
    export_assembly(build(), str(_here.parent / "manifold-arrangement.step"))
    print("-> manifold-arrangement.step")


if __name__ == "__main__":
    main()
