"""Reference solid for the ULN2803A 8-channel Darlington driver module
(bom: B0F872W528, 2-pc), used 2x on the driver tray — sink the 12 solenoid
coils + the condenser fan to GND; COM tied to 12 V for flyback.

Geometry read off the Amazon product photos (B0F872W528): a small purple PCB
with the ULN2803A SOIC-18 in the centre, a 9-pin 2.54 mm header along each long
edge (1B-8B+GND / 1C-8C+COM), and **2 plated mounting holes placed diagonally**.
This is the compact SOIC breakout, NOT a screw-terminal slab. Footprint estimated
from the photo — verify by caliper.

Frame: X = length, Y = width, Z up from the PCB underside; origin at the
footprint centre, Z = 0 the standoff plane.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

name = "uln"
length = 31.0          # X (9-pin header direction)
width = 22.0           # Y
pcb_t = 1.6
envelope_z = 12.0      # 2.54 mm headers (tallest)
pin_drop = 3.0
hole_dia = 3.0
holes = [(-11.0, 8.0), (11.0, -8.0)]   # 2 holes, diagonal


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    chip = (
        cq.Workplane("XY").box(12.0, 8.0, 3.5, centered=(True, True, False))
        .translate((0.0, 0.0, pcb_t))
    )
    # 9-pin header strips along the long (±Y) edges.
    hdr = None
    for sy in (-1.0, 1.0):
        strip = (
            cq.Workplane("XY").box(length - 6.0, 3.0, envelope_z - pcb_t, centered=(True, True, False))
            .translate((0.0, sy * (width / 2.0 - 2.5), pcb_t))
        )
        hdr = strip if hdr is None else hdr.union(strip)
    pins = (
        cq.Workplane("XY").box(14.0, 6.0, pin_drop, centered=(True, True, False))
        .translate((0.0, 0.0, -pin_drop))
    )
    part = pcb.union(chip).union(hdr).union(pins)
    for hx, hy in holes:
        part = part.cut(
            cq.Workplane("XY").workplane(offset=-pin_drop).center(hx, hy)
            .circle(hole_dia / 2.0).extrude(pin_drop + pcb_t)
        )
    return part


def main():
    export_step(build(), str(_here.parent / "uln2803a.step"))
    print("-> uln2803a.step")


if __name__ == "__main__":
    main()
