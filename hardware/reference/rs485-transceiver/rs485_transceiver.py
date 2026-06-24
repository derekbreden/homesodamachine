"""Reference solid for the ALMOCN TTL-to-RS485 auto-direction transceiver
(bom: B09998FY4X), 1x on the controller tray — base side of the SIG-7 link to
the front 4.3" config display (the 4.3B has onboard RS485).

Geometry calipered from the physical board: a blue PCB with a 3-position 5.08 mm
screw-terminal block (A+ / B- / Earth) on one short end and a 4-pin 2.54 mm
header (VCC / TXD / RXD / GND) on the other, with 4 mounting holes ~2 mm in the
corners. The module is auto-direction (no DE/RE pin), runs VCC at 3.3 V on the
carrier, carries an onboard (default-OFF) 120 ohm R0 termination, and routes NO
12 V anywhere. The "Earth" terminal is an isolated chassis/shield reference, not
the chip GND.

Frame follows the module_tray convention: X = length = the 51.85 mm long axis,
Y = width = the 22.75 mm short axis, Z up from the PCB underside; origin at the
footprint centre, Z = 0 the standoff plane. (length = X, width = Y is what
controller_tray / logic_tray / module_tray consume.)

  Footprint     51.85 (X, length) x 22.75 (Y, width)
  Mount holes   4x dia 2.0 (M2) in the corners at (+/-23.8, +/-9.5)
                -- c-t-c 47.6 along X, 19.0 along Y
  Screw term    3-pos 5.08 mm (A+/B-/Earth) at the -X end, along Y
  TTL header    4-pin 2.54 mm (VCC/TXD/RXD/GND) at the +X end, along Y
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

name = "rs485"
length = 51.85         # X (long axis)
width = 22.75          # Y (short axis)
pcb_t = 1.6
envelope_z = 11.0      # 3-pos screw-terminal block is the tallest part
pin_drop = 2.5
hole_dia = 2.0         # M2
holes = [(-23.8, -9.5), (-23.8, 9.5), (23.8, -9.5), (23.8, 9.5)]   # 4 corners


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    # 3-position 5.08 mm screw-terminal block (A+/B-/Earth) on the -X end.
    term = (
        cq.Workplane("XY").box(10.0, 16.5, envelope_z - pcb_t, centered=(True, True, False))
        .translate((-21.925, 0.0, pcb_t))
    )
    # 4-pin 2.54 mm header (VCC/TXD/RXD/GND) on the +X end, plus its pin drop.
    hdr = (
        cq.Workplane("XY").box(3.0, 10.16, 6.0, centered=(True, True, False))
        .translate((18.725, 0.0, pcb_t))
    )
    pins = (
        cq.Workplane("XY").box(3.0, 7.62, pin_drop, centered=(True, True, False))
        .translate((18.725, 0.0, -pin_drop))
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
