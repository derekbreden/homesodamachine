"""Assembled AC hub: the printed hub with its three Wago 221-413 lever nuts
seated butt-first in their pockets.

``build_assembly(L)`` takes a ``Layout`` from ac_hub. The ground ring-terminal
stack is not here — it clamps to a cap column of its own, not to this part."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "wago-221-413",
    _here.parent,
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import ac_hub as t
import wago_221_413 as wago

HUB_COLOR = cq.Color(0.85, 0.78, 0.62)     # PETG tan
WAGO_COLOR = cq.Color(0.85, 0.45, 0.15)    # orange levers


def build_assembly(L, name="ac-hub-assembly"):
    assy = cq.Assembly(name=name)
    assy.add(t.build_hub(L).val(), name="hub", color=HUB_COLOR)
    # Wagos: butt face on the pocket's −Y wall, flat on the floor, wire end +Y.
    for i, (cx, by) in enumerate(L.wago_places):
        w = (wago.build().val().translate((0, wago.depth / 2.0, 0))
             .translate((cx, by, t.floor_t)))
        assy.add(w, name=f"wago{i}", color=WAGO_COLOR)
    return assy


def main():
    export_assembly(build_assembly(t.LAYOUT, "ac-hub-assembly"),
                    str(_here.parent / "ac-hub-assembly.step"))
    print("-> ac-hub-assembly.step")


if __name__ == "__main__":
    main()
