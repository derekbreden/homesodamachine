"""Reference solid for the ALMOCN TTL-to-RS485 auto-direction transceiver
(bom: B09998FY4X), 1x on the controller tray — base side of the SIG-7 link to
the front 4.3" config display (the 4.3B has onboard RS485).

Geometry read off the Amazon product photos (B09998FY4X): a blue PCB with a
3-position screw terminal block on the RS485 end and a 4-pin 2.54 mm header on
the TTL end, with **2 plated mounting holes placed diagonally** (one by the screw
terminal, one by the connector). A verified review notes the holes match the
Adafruit Feather mounting pattern. Footprint estimated from the photo using the
screw-terminal pitch as scale — verify by caliper.

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

name = "rs485"
length = 44.0          # X (estimated from photo)
width = 18.0           # Y
pcb_t = 1.6
envelope_z = 11.0      # screw terminal block is the tallest part
pin_drop = 2.5
hole_dia = 3.0
holes = [(-18.0, 6.0), (18.0, -6.0)]   # 2 holes, diagonal (one per end)


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    # 3-position screw terminal block on the +X (RS485) end.
    term = (
        cq.Workplane("XY").box(11.0, 14.0, envelope_z - pcb_t, centered=(True, True, False))
        .translate((length / 2.0 - 8.0, 0.0, pcb_t))
    )
    # 4-pin header on the -X (TTL) end.
    hdr = (
        cq.Workplane("XY").box(11.0, 4.0, 6.0, centered=(True, True, False))
        .translate((-length / 2.0 + 7.0, 0.0, pcb_t))
    )
    pins = (
        cq.Workplane("XY").box(10.0, 4.0, pin_drop, centered=(True, True, False))
        .translate((-length / 2.0 + 7.0, 0.0, -pin_drop))
    )
    part = pcb.union(term).union(hdr).union(pins)
    for hx, hy in holes:
        part = part.cut(
            cq.Workplane("XY").workplane(offset=-pin_drop).center(hx, hy)
            .circle(hole_dia / 2.0).extrude(pin_drop + pcb_t)
        )
    return part


def main():
    export_step(build(), str(_here.parent / "rs485-transceiver.step"))
    print("-> rs485-transceiver.step")


if __name__ == "__main__":
    main()
