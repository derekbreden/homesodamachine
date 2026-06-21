"""Reference solid for the DS3231 RTC module (bom: B09LLMYBM1), 1x on the
controller tray — the I2C real-time clock.

The common ZS-042 form factor: ~38 x 22 mm with a coin-cell holder on top.
**Geometry estimated** from typical DS3231 modules; verify by caliper.

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

name = "ds3231"
length = 38.0
width = 22.0
pcb_t = 1.6
envelope_z = 14.0      # coin-cell holder on top
pin_drop = 2.5
hole_dia = 3.0
holes = [(sx * 16.0, sy * 8.0) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    batt = (
        cq.Workplane("XY").box(22.0, 20.0, envelope_z - pcb_t, centered=(True, True, False))
        .translate((-4.0, 0.0, pcb_t))
    )
    pins = (
        cq.Workplane("XY").box(20.0, 6.0, pin_drop, centered=(True, True, False))
        .translate((0.0, 0.0, -pin_drop))
    )
    part = pcb.union(batt).union(pins)
    for hx, hy in holes:
        part = part.cut(
            cq.Workplane("XY").workplane(offset=-pin_drop).center(hx, hy)
            .circle(hole_dia / 2.0).extrude(pin_drop + pcb_t)
        )
    return part


def main():
    export_step(build(), str(_here.parent / "ds3231-rtc.step"))
    print("-> ds3231-rtc.step")


if __name__ == "__main__":
    main()
