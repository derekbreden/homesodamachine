"""Peristaltic tube — the flexible PETG hollow cylinder that runs
through the Kamoer KPP pump head. Prints vase-mode standing on its
−Z end face; the spiral seam rises along the tube axis (Z)."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from _cadq_export import export_step
from docgen import substitute_py_comments


# Bore diameter matches the Kamoer KPP small-bore pump head.
inner_diameter = 3.2
wall_thickness = 1.6
# [6.4 mm](OUTER_D) outer diameter = inner_diameter + 2 × wall_thickness.
outer_diameter = inner_diameter + 2 * wall_thickness
tube_length = 150.0


def build_tube():
    """Hollow cylinder, axis along Z."""
    outer = (
        cq.Workplane("XY")
        .circle(outer_diameter / 2)
        .extrude(tube_length)
    )
    inner = (
        cq.Workplane("XY")
        .circle(inner_diameter / 2)
        .extrude(tube_length)
    )
    return outer.cut(inner)


def main():
    tube = build_tube()
    export_step(tube, str(_here / "peristaltic-tube.step"))
    print("-> peristaltic-tube.step")

    variables = {
        "OUTER_D": f"{outer_diameter:.4g} mm",
    }
    substitute_py_comments(
        __file__,
        variables=variables,
        expected_counts={
            "OUTER_D": 1,
        },
    )


if __name__ == "__main__":
    main()
