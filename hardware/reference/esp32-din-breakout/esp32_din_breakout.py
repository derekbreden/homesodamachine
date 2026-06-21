"""Reference solid for the ESP32-DevKitC-32E pre-mounted on its DIN-rail
screw-terminal breakout (bom: B09MQJWQN2 on B0BW4SJ5X2), the controller-tray MCU.

The thing that bolts to the tray is the breakout carrier (the DevKitC plugs into
its sockets), so the footprint + mounting holes are the carrier's. **Geometry is
estimated** from typical ESP32 DIN-rail breakouts — verify by caliper; the
carrier size and hole pattern especially.

Frame: X = length, Y = width, Z up from the carrier underside; origin at the
footprint centre, Z = 0 the mounting (standoff) plane.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

name = "esp32"
length = 100.0         # X (carrier, estimated)
width = 66.0           # Y
pcb_t = 1.6
envelope_z = 15.0      # ESP32 module + sockets above the carrier
pin_drop = 2.5
hole_dia = 3.2
holes = [(sx * 44.0, sy * 28.0) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    # ESP32-DevKitC module socketed across the middle.
    esp = (
        cq.Workplane("XY").box(55.0, 28.0, envelope_z - pcb_t, centered=(True, True, False))
        .translate((0.0, 0.0, pcb_t))
    )
    # Screw-terminal strips down both long edges.
    term = None
    for sy in (-1.0, 1.0):
        strip = (
            cq.Workplane("XY").box(length - 8.0, 9.0, 9.0, centered=(True, True, False))
            .translate((0.0, sy * (width / 2.0 - 6.0), pcb_t))
        )
        term = strip if term is None else term.union(strip)
    pins = (
        cq.Workplane("XY").box(60.0, 40.0, pin_drop, centered=(True, True, False))
        .translate((0.0, 0.0, -pin_drop))
    )
    part = pcb.union(esp).union(term).union(pins)
    for hx, hy in holes:
        part = part.cut(
            cq.Workplane("XY").workplane(offset=-pin_drop).center(hx, hy)
            .circle(hole_dia / 2.0).extrude(pin_drop + pcb_t)
        )
    return part


def main():
    export_step(build(), str(_here.parent / "esp32-din-breakout.step"))
    print("-> esp32-din-breakout.step")


if __name__ == "__main__":
    main()
