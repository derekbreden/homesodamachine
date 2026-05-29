"""Water-tightness test coupon — a 4 fl oz open-top cup with 3 mm walls
and a 3 mm floor, printed in PETG. Fill it with water and watch the walls
and floor for weeping or seepage; it stands in for the reservoir's 3 mm
wall spec without printing the whole reservoir.

Open-top cylinder: interior ⌀50 × ~60.2 mm (4 fl oz = 118.3 mL), outer
⌀56 × ~63.2 mm. Interior height is derived from the volume target so the
fill line is exactly 4 fl oz."""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
from _cadq_export import export_step

# 4 US fluid ounces in mm³ (1 fl oz = 29.5735 mL).
volume_target = 4 * 29573.5

wall_thickness = 3.0
floor_thickness = 3.0
interior_radius = 25.0
interior_height = volume_target / (math.pi * interior_radius**2)

outer_radius = interior_radius + wall_thickness
outer_height = floor_thickness + interior_height


def build_water_test_cup():
    outer = cq.Workplane("XY").circle(outer_radius).extrude(outer_height)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=floor_thickness)
        .circle(interior_radius)
        .extrude(interior_height + 1.0)  # overshoot opens the top cleanly
    )
    return outer.cut(cavity)


def main():
    cup = build_water_test_cup()
    export_step(cup, str(_here.parent / "water-test-cup.step"))
    print("-> water-test-cup.step")


if __name__ == "__main__":
    main()
