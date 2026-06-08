"""Water-tightness test coupon — a 4 fl oz open-top cup with 3 mm walls
and a 3 mm floor, printed in PETG at the reservoir's wall spec.

Open-top cylinder: interior ⌀50 × 60.2 mm (4 fl oz = 118.3 mL), outer
⌀56 × 63.2 mm. The interior holds exactly 4 fl oz to the rim."""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
from _cadq_export import export_step

volume_target = 4 * 29573.5

wall_thickness = 3.0
floor_thickness = 3.0
interior_radius = 25.0
interior_height = volume_target / (math.pi * interior_radius**2)

outer_radius = interior_radius + wall_thickness
outer_height = floor_thickness + interior_height

# Cavity overshoots the rim so it cuts a clean open top.
rim_overshoot = 1.0


def build_water_test_cup():
    outer = cq.Workplane("XY").circle(outer_radius).extrude(outer_height)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=floor_thickness)
        .circle(interior_radius)
        .extrude(interior_height + rim_overshoot)
    )
    return outer.cut(cavity)


def main():
    cup = build_water_test_cup()
    export_step(cup, str(_here.parent / "water-test-cup.step"))
    print("-> water-test-cup.step")


if __name__ == "__main__":
    main()
