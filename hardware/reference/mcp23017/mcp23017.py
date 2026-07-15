"""Reference solid for the MCP23017 I2C 16-bit GPIO-expander breakout
(bom: B07P2H1NZG = the Waveshare MCP23017 IO Expansion Board), used 2x on the
controller tray (0x20, 0x21).

Geometry calipered from the physical board. Frame follows the module_tray
convention: X = length = the 38.5 mm long axis, Y = width = the 23.3 mm short
axis, Z up from the PCB underside; origin at the footprint centre, Z = 0 the
standoff plane. (length = X, width = Y is what logic_tray / module_tray
consume — keep it that way so the floor outline and bosses align.)

  Footprint     38.5 (X, length) x 23.3 (Y, width)
  Mount holes   2x M2 (dia 2.0) at (16.75, +/-9.4) -- both at the +X (I2C) end,
                18.8 apart across the short axis, hole centre 2.5 from the +X edge
  GPIO headers  2x 10-pin 2.54mm running along X at Y = +/-10 (span 22.86, X=+1.5)
  I2C header    6-pin 2.54mm running along Y at X = +17.25 (span 12.7), between holes
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

name = "mcp"
length = 38.5          # X (long axis)
width = 23.3           # Y (short axis)
pcb_t = 1.6
envelope_z = 13.0      # 2.54 mm pin headers (tallest)
pin_drop = 3.0
hole_dia = 2.0         # M2
holes = [(16.75, 9.4), (16.75, -9.4)]   # both at the +X (I2C) end, 18.8 apart


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    chip = (
        cq.Workplane("XY").box(12.0, 8.0, 3.0, centered=(True, True, False))
        .translate((1.5, 0.0, pcb_t))
    )
    # Two 10-pin GPIO header strips running along the long (X) axis, at Y = +/-10.
    hdr = None
    for sy in (-1.0, 1.0):
        strip = (
            cq.Workplane("XY").box(22.86, 3.0, envelope_z - pcb_t, centered=(True, True, False))
            .translate((1.5, sy * 10.0, pcb_t))
        )
        hdr = strip if hdr is None else hdr.union(strip)
    # 6-pin I2C header running along the short (Y) axis at the +X end.
    hdr = hdr.union(
        cq.Workplane("XY").box(3.0, 12.7, envelope_z - pcb_t, centered=(True, True, False))
        .translate((17.25, 0.0, pcb_t))
    )
    pins = (
        cq.Workplane("XY").box(20.0, 6.0, pin_drop, centered=(True, True, False))
        .translate((1.5, 0.0, -pin_drop))
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
