"""Reference solid for the ULN2803A high-current Darlington driver module
(bom: B0F872W528, 2-pc), used 2x on the driver tray — sinks the 12 solenoids +
condenser fan.

A generic reseller module with input/output screw terminals — **geometry
estimated**; verify by caliper (footprint + hole pattern).

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
length = 65.0
width = 33.0
pcb_t = 1.6
envelope_z = 12.0
pin_drop = 3.0
hole_dia = 3.0
holes = [(sx * 29.0, sy * 13.0) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    chip = (
        cq.Workplane("XY").box(40.0, 12.0, envelope_z - pcb_t, centered=(True, True, False))
        .translate((0.0, 0.0, pcb_t))
    )
    # Input / output screw-terminal strips on the two long edges.
    term = None
    for sy in (-1.0, 1.0):
        strip = (
            cq.Workplane("XY").box(length - 10.0, 8.0, 9.0, centered=(True, True, False))
            .translate((0.0, sy * (width / 2.0 - 5.0), pcb_t))
        )
        term = strip if term is None else term.union(strip)
    pins = (
        cq.Workplane("XY").box(length - 12.0, width - 14.0, pin_drop, centered=(True, True, False))
        .translate((0.0, 0.0, -pin_drop))
    )
    part = pcb.union(chip).union(term).union(pins)
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
