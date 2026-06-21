"""Reference solid for the Mean Well IRM-90-12ST — 12 V / 6.7 A encapsulated
AC-DC power module (the screw-terminal "ST" variant), used 1x on the power tray.

Geometry from the official Mean Well IRM-90-SPEC mechanical drawing: a potted
brick whose two short ends step down to 6.7 mm ledges carrying the screw-terminal
blocks (AC in on one end, DC out on the other).

Coordinate frame
----------------
- X = width (52 mm), Y = length (109 mm), Z = height up from the base.
- Origin at the footprint center; Z = 0 the mounting (base) plane.
- AC 2-pole screw block at +Y end, DC 4-pole screw block at -Y end.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

# --- Measured / datasheet geometry ----------------------------------------
width = 52.0           # X
length = 109.0         # Y
height = 33.5          # Z, potted-body top
ledge_h = 6.7          # stepped terminal-end height
ledge_len = 13.0       # Y length of each stepped end (terminals sit here)
hole_dia = 3.5         # 4-ψ3.5, M3 clearance
hole_dx = 33.0 / 2.0   # +/-16.5 across width
hole_dy = 98.0 / 2.0   # +/-49 along length
mass_g = 219.0


def build():
    mid = length - 2 * ledge_len
    body = cq.Workplane("XY").box(width, mid, height, centered=(True, True, False))
    # Stepped terminal ledges + a representative screw-terminal block on each.
    for sy, blk_w in ((1.0, 16.0), (-1.0, 25.0)):   # +Y = AC (2-pole), -Y = DC (4-pole)
        ledge = (
            cq.Workplane("XY")
            .box(width, ledge_len, ledge_h, centered=(True, True, False))
            .translate((0.0, sy * (length - ledge_len) / 2.0, 0.0))
        )
        block = (
            cq.Workplane("XY")
            .box(blk_w, 8.0, 7.0, centered=(True, True, False))
            .translate((0.0, sy * (length / 2.0 - 6.0), ledge_h))
        )
        body = body.union(ledge).union(block)
    # Four mounting holes.
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            body = body.cut(
                cq.Workplane("XY")
                .center(sx * hole_dx, sy * hole_dy)
                .circle(hole_dia / 2.0)
                .extrude(height)
            )
    return body


def main():
    export_step(build(), str(_here.parent / "meanwell-irm90.step"))
    print("-> meanwell-irm90.step")


if __name__ == "__main__":
    main()
