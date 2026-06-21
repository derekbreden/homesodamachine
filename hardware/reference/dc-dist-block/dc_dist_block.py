"""Reference solid for the 12 V DC distribution block, 1x on the driver tray —
the + / GND rails off the PSU secondary (DC-1 in, DC-2/4/6/8/9 out).

**Placeholder.** The DC-distribution hardware is not yet chosen (Wago 221 stack
vs. screw block vs. bus bar — see electronics-shelf.md Open items), so this is a
generic terminal-block envelope just to hold the footprint. Verify / replace
once the part is picked.

Frame: X = length, Y = width, Z up from the underside; origin at the footprint
centre, Z = 0 the standoff plane.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

name = "dcdist"
length = 50.0
width = 26.0
pcb_t = 2.0
envelope_z = 18.0
pin_drop = 0.0
hole_dia = 3.2
holes = [(sx * 22.0, 0.0) for sx in (-1.0, 1.0)]   # two end mounting ears


def build():
    body = cq.Workplane("XY").box(length, width, envelope_z, centered=(True, True, False))
    for hx, hy in holes:
        body = body.cut(
            cq.Workplane("XY").center(hx, hy).circle(hole_dia / 2.0).extrude(envelope_z)
        )
    return body


def main():
    export_step(build(), str(_here.parent / "dc-dist-block.step"))
    print("-> dc-dist-block.step")


if __name__ == "__main__":
    main()
