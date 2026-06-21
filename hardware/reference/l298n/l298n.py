"""Reference solid for the L298N dual H-bridge motor-driver module
(bom: B0C5JCF5RS), 1x on the driver tray — drives both Kamoer peristaltic pumps
and makes the onboard 5 V logic rail.

The classic red L298N module: ~43.5 mm square, tall finned heatsink, 4 corner
mounting holes. Footprint + hole pattern are well established; the heatsink
height is approximate.

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

name = "l298n"
length = 43.5
width = 43.5
pcb_t = 1.6
envelope_z = 27.0      # finned heatsink
pin_drop = 2.5
hole_dia = 3.2
holes = [(sx * 18.75, sy * 18.75) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    heatsink = (
        cq.Workplane("XY").box(25.0, 23.0, envelope_z - pcb_t, centered=(True, True, False))
        .translate((0.0, 5.0, pcb_t))
    )
    # Screw-terminal strips on two opposite edges.
    term = None
    for sy in (-1.0, 1.0):
        strip = (
            cq.Workplane("XY").box(length - 8.0, 7.0, 10.0, centered=(True, True, False))
            .translate((0.0, sy * (width / 2.0 - 4.5), pcb_t))
        )
        term = strip if term is None else term.union(strip)
    pins = (
        cq.Workplane("XY").box(length - 12.0, width - 16.0, pin_drop, centered=(True, True, False))
        .translate((0.0, 0.0, -pin_drop))
    )
    part = pcb.union(heatsink).union(term).union(pins)
    for hx, hy in holes:
        part = part.cut(
            cq.Workplane("XY").workplane(offset=-pin_drop).center(hx, hy)
            .circle(hole_dia / 2.0).extrude(pin_drop + pcb_t)
        )
    return part


def main():
    export_step(build(), str(_here.parent / "l298n.step"))
    print("-> l298n.step")


if __name__ == "__main__":
    main()
