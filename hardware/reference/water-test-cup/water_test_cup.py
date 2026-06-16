"""Water-tightness test coupon — a 4 fl oz open-top cup with [3 mm](WALL_THICKNESS) walls
and a [3 mm](FLOOR_THICKNESS) floor, printed in PETG at the reservoir's wall spec.

Open-top cylinder: interior ⌀[50 mm](INTERIOR_DIAMETER) × [60.25 mm](INTERIOR_HEIGHT) (4 fl oz = [118.3 mL](VOLUME_TARGET_ML)), outer
⌀[56 mm](OUTER_DIAMETER) × [63.25 mm](OUTER_HEIGHT). The interior holds exactly 4 fl oz to the rim."""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_step
from docgen import substitute_py_comments

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
    substitute_py_comments(
        Path(__file__),
        variables={
            "WALL_THICKNESS": f"{wall_thickness:.4g} mm",
            "FLOOR_THICKNESS": f"{floor_thickness:.4g} mm",
            "INTERIOR_DIAMETER": f"{2 * interior_radius:.4g} mm",
            "INTERIOR_HEIGHT": f"{interior_height:.4g} mm",
            "VOLUME_TARGET_ML": f"{volume_target / 1000:.4g} mL",
            "OUTER_DIAMETER": f"{2 * outer_radius:.4g} mm",
            "OUTER_HEIGHT": f"{outer_height:.4g} mm",
        },
        expected_counts={
            "WALL_THICKNESS": 1,
            "FLOOR_THICKNESS": 1,
            "INTERIOR_DIAMETER": 1,
            "INTERIOR_HEIGHT": 1,
            "VOLUME_TARGET_ML": 1,
            "OUTER_DIAMETER": 1,
            "OUTER_HEIGHT": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
