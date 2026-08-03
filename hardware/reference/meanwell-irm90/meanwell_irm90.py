"""Reference solid for the Mean Well IRM-90-12ST — 12 V / 6.7 A encapsulated
AC-DC power module (the screw-terminal "ST" variant), used 1x on the electronics
shelf.

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

# The two screw blocks on their ledges. Each is entered from ABOVE — a ferrule goes down under
# a captive screw — and its station is its own top face, looking +Z.
block_inset = 6.0      # block centre in from the module's own end
block_h = 7.0          # block height off its ledge
block_w = {1.0: 16.0, -1.0: 25.0}    # +Y = AC (2-pole), -Y = DC (4-pole)
block_len = 8.0


def _block(sy):
    return ((0.0, sy * (length / 2.0 - block_inset), ledge_h + block_h), (0.0, 0.0, 1.0))


def ac_in():
    """The AC primary's screw block, at the face a ferrule lands on: `(position, outward
    axis)` in the module's own frame."""
    return _block(1.0)


def dc_out():
    """The DC secondary's screw block, the same way."""
    return _block(-1.0)


def build():
    mid = length - 2 * ledge_len
    body = cq.Workplane("XY").box(width, mid, height, centered=(True, True, False))
    # Stepped terminal ledges + a representative screw-terminal block on each, each block
    # standing at its own station.
    for sy in (1.0, -1.0):
        ledge = (
            cq.Workplane("XY")
            .box(width, ledge_len, ledge_h, centered=(True, True, False))
            .translate((0.0, sy * (length - ledge_len) / 2.0, 0.0))
        )
        (bx, by, btop), _axis = _block(sy)
        block = (
            cq.Workplane("XY")
            .box(block_w[sy], block_len, block_h, centered=(True, True, False))
            .translate((bx, by, btop - block_h))
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
