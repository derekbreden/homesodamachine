"""Assembled Lite power tray: the tray with the PSU and the three Wago AC
distribution connectors seated, plus the ground ring-terminal stack.

No relay — the Lite has no compressor and no SeaFlo diaphragm pump, so there is
nothing to switch. ``build_assembly(L)`` takes a ``Layout`` from power_tray and
seats the parts."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"
for _p in (
    _hw / "scripts",
    _hw / "reference" / "meanwell-irm90",
    _hw / "reference" / "wago-221-413",
    _hw / "reference" / "ground-ring-stack",
    _here.parent,
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import power_tray as t          # the Lite tray (this directory)
import meanwell_irm90 as psu
import wago_221_413 as wago
import ground_ring_stack as gnd

TRAY_COLOR = cq.Color(0.85, 0.78, 0.62)    # PETG tan
PSU_COLOR = cq.Color(0.30, 0.32, 0.36)     # encapsulated brick, dark
WAGO_COLOR = cq.Color(0.85, 0.45, 0.15)    # orange levers
GND_COLOR = cq.Color(0.80, 0.80, 0.83)     # tin-plated lugs + stainless screw


def build_assembly(L, name="power-assembly"):
    assy = cq.Assembly(name=name)
    assy.add(t.build_tray(L).val(), name="tray", color=TRAY_COLOR)
    assy.add(
        psu.build().val().rotate((0, 0, 0), (0, 0, 1), L.psu_rot)
        .translate((L.psu_c[0], L.psu_c[1], t.floor_t + t.psu_boss_h)),
        name="PSU", color=PSU_COLOR,
    )
    # Wagos: butt-bottom centre at the slot origin, tilted up toward the wire end.
    for i, (cx, by) in enumerate(L.wago_places):
        w = (wago.build().val().translate((0, wago.depth / 2.0, 0))
             .rotate((0, 0, 0), (1, 0, 0), t.wago_tilt)
             .translate((cx, by, t.floor_t)))
        assy.add(w, name=f"wago{i}", color=WAGO_COLOR)
    # Ground ring-terminal stack clamped to the heat-set boss (Z=0 at boss top).
    assy.add(
        gnd.build().val().translate((L.gnd_c[0], L.gnd_c[1], t.floor_t + t.gnd_boss_h)),
        name="ground-stack", color=GND_COLOR,
    )
    return assy


def main():
    export_assembly(build_assembly(t.LAYOUT, "power-assembly"), str(_here.parent / "power-assembly.step"))
    print("-> power-assembly.step")


if __name__ == "__main__":
    main()
