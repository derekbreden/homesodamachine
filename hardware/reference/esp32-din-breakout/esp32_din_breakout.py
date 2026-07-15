"""Reference solid for the ESP32-DevKitC-32E on its DIN-rail terminal breakout
(lite-bom: B09MQJWQN2 on B0BW4SJ5X2), the Lite logic-tray MCU carrier.

The carrier is the "ESP32 Super Breakout Board DIN Rail Mount" (naughtystarts,
B0BW4SJ5X2): the DevKitC sockets into 2x19 2.54 mm rows, with 3.81 mm screw
terminals down both long edges, and it ships with a **bracket for 35 mm DIN
rail**. So its native mounting is a DIN-rail clip, not 4 corner bosses — on a
flat tray it wants a short DIN-rail segment (or screws through the PCB mounting
holes the silkscreen documents).

**Footprint is estimated** — the listing publishes pitches (2x19 @ 2.54, screw
@ 3.81) but not the overall PCB size, and it's a DIN-mount board. Verify by
caliper; the hole pattern below is a placeholder.

Frame: X = length, Y = width, Z up from the carrier underside; origin at the
footprint centre, Z = 0 the standoff plane.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

name = "esp32"
length = 72.0          # X (carrier, estimated)
width = 54.0           # Y (DevKitC + screw terminals both edges, estimated)
pcb_t = 1.6
envelope_z = 16.0      # ESP32 module + sockets
pin_drop = 2.5
hole_dia = 3.2
din_rail_mount = True   # ships with a 35 mm DIN-rail bracket
holes = [(sx * 32.0, sy * 23.0) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]  # placeholder


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    # ESP32-DevKitC module socketed across the middle.
    esp = (
        cq.Workplane("XY").box(54.0, 28.0, envelope_z - pcb_t, centered=(True, True, False))
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
        cq.Workplane("XY").box(48.0, 20.0, pin_drop, centered=(True, True, False))
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
