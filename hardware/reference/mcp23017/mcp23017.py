"""Reference solid for the MCP23017 I2C GPIO-expander breakout (bom: B07P2H1NZG),
used 2x on the controller tray (0x20, 0x21).

A generic reseller breakout with no controlled drawing — **geometry estimated**
from typical MCP23017 modules; verify by caliper (footprint + whether/where it
has mounting holes).

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
length = 35.0
width = 25.0
pcb_t = 1.6
envelope_z = 12.0
pin_drop = 3.0
hole_dia = 3.0
holes = [(sx * 15.0, sy * 9.5) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    chip = (
        cq.Workplane("XY").box(20.0, 12.0, envelope_z - pcb_t, centered=(True, True, False))
        .translate((0.0, 0.0, pcb_t))
    )
    pins = (
        cq.Workplane("XY").box(19.0, 6.0, pin_drop, centered=(True, True, False))
        .translate((0.0, 0.0, -pin_drop))
    )
    part = pcb.union(chip).union(pins)
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
