"""Reference solid for the MCP23017 I2C 16-bit GPIO-expander breakout
(bom: B07P2H1NZG = the Waveshare MCP23017 IO Expansion Board), used 2x on the
controller tray (0x20, 0x21).

Footprint and hole spec from the Waveshare user manual: 38 x 23 mm, hole size
2.0 mm (M2). Two mounting holes, both at ONE short end (the I2C-header / address-
pad end), ~19 mm apart across the width; the opposite (PH2.0-connector) end has
none — so the board mounts cantilevered from one end. Two 10-pin GPIO headers run
along the long edges. Hole centre inset estimated from photos.

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

name = "mcp"
length = 38.0
width = 23.0
pcb_t = 1.6
envelope_z = 13.0      # 2.54 mm pin headers (tallest)
pin_drop = 3.0
hole_dia = 2.0         # M2
holes = [(17.0, 9.5), (17.0, -9.5)]   # both at one short end, ~19 mm apart


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    chip = (
        cq.Workplane("XY").box(12.0, 8.0, 3.0, centered=(True, True, False))
        .translate((0.0, 0.0, pcb_t))
    )
    # Two 10-pin header strips along the long (±Y) edges.
    hdr = None
    for sy in (-1.0, 1.0):
        strip = (
            cq.Workplane("XY").box(length - 8.0, 3.0, envelope_z - pcb_t, centered=(True, True, False))
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
    export_step(build(), str(_here.parent / "mcp23017.step"))
    print("-> mcp23017.step")


if __name__ == "__main__":
    main()
