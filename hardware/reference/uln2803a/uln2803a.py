"""Reference solid for the ULN2803A 8-channel Darlington driver module
(bom: B0F872W528, 2-pc), used 2x on the driver tray — sink the 10 solenoid
coils + the condenser fan to GND; COM tied to 12 V for flyback.

Geometry calipered from the physical board: a small purple SOIC breakout with
the ULN2803A SOIC-18 centred, a 9-pin 2.54 mm header along each long edge
(1B-8B+GND / 1C-8C+COM), and 2 mounting holes on the centreline.

Frame follows the module_tray convention: X = length = the 24 mm axis (the two
9-pin rows run along X), Y = width = the 23 mm axis (the rows sit at Y = +/-10),
Z up from the PCB underside; origin at the footprint centre, Z = 0 the standoff
plane. (length = X, width = Y is what logic_tray / module_tray consume.)

  Footprint     24 (X, length) x 23 (Y, width)
  Mount holes   2x dia 3.0 at (+/-8.75, 0) -- on the Y=0 centreline, 17.5 apart in X
  Channel rows  2x 9-pin 2.54mm running along X at Y = +/-10 (span 20.32, X=+0.34)
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

name = "uln"
length = 24.0          # X (the 9-pin rows run along this axis)
width = 23.0           # Y (the two rows sit at Y = +/-10)
pcb_t = 1.6
envelope_z = 12.0      # 2.54 mm headers (tallest)
pin_drop = 3.0
hole_dia = 3.0
holes = [(8.75, 0.0), (-8.75, 0.0)]   # centreline, 17.5 apart in X


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    chip = (
        cq.Workplane("XY").box(12.0, 8.0, 3.5, centered=(True, True, False))
        .translate((0.0, 0.0, pcb_t))
    )
    # Two 9-pin channel-header strips running along the long (X) axis, at Y = +/-10.
    hdr = None
    for sy in (-1.0, 1.0):
        strip = (
            cq.Workplane("XY").box(20.32, 3.0, envelope_z - pcb_t, centered=(True, True, False))
            .translate((0.34, sy * 10.0, pcb_t))
        )
        hdr = strip if hdr is None else hdr.union(strip)
    pins = (
        cq.Workplane("XY").box(20.0, 6.0, pin_drop, centered=(True, True, False))
        .translate((0.34, 0.0, -pin_drop))
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
