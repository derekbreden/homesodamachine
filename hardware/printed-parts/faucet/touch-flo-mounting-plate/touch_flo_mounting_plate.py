"""Touch-Flo mounting plate — printed PETG disc that supports the
harvested Touch-Flo faucet body and the two flavor tubes that pass
alongside it. See README.md."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_here.parent))  # for _touch_flo_interface
from _cadq_export import export_step
from _touch_flo_interface import (
    flavor_tube_x,
    flavor_tube_y_offset,
    pill_length_y as pill_slot_length_y,
    pill_width_x as pill_slot_width_x,
    shank_hole_diameter,
)
from docgen import substitute_md, substitute_py_comments


# [54.35 mm](PLATE_D) disc.
plate_radius = 54.35 / 2
# [4 mm](PLATE_T) thick.
plate_thickness = 4.0
# Top face flush with the deck plane (Z=0); plate hangs below.
plate_z_range = (-plate_thickness, 0.0)
# [3.175 mm](PLATE_X) X offset, Z = 0.
plate_center = (3.175, 0.0)


# [11 mm](SHANK_OD) threaded shank clearance.
shank_diameter_nominal = 11.0
shank_hole_radius = shank_hole_diameter / 2
shank_hole_center = (0.0, 0.0)


# Flavor-tube pill slot. The two 1/4" LLDPE tubes are centered at
# ±flavor_tube_y_offset (separation [6.35 mm](TUBE_CENTER_Y)), combined
# into one Y-oriented pill (rounded-rectangle) opening.
# [18.93 mm](PLATE_FLAVOR_X) +X offset of pill slot center from world origin.
pill_slot_center = (flavor_tube_x, 0.0)
# [13.4 mm](PLATE_PILL_L) pill long axis (Y).
# [7.05 mm](PLATE_PILL_W) pill short axis (X).


# [2 mm](TOP_FILLET_R) fillet on the top outer edge.
top_outer_fillet_r = 2.0


def vertical_cylinder(center, radius, z_range):
    """Z-axis cylinder: 2D center, radius, and Z extent."""
    z_min, z_max = z_range
    return (
        cq.Workplane("XY")
        .workplane(offset=z_min)
        .moveTo(*center)
        .circle(radius)
        .extrude(z_max - z_min)
    )


def vertical_y_slot(center, length_y, width_x, z_range):
    """Z-axis pill (rounded-rectangle) prism with long axis along Y."""
    z_min, z_max = z_range
    return (
        cq.Workplane("XY")
        .workplane(offset=z_min)
        .moveTo(*center)
        .slot2D(length_y, width_x, angle=90)
        .extrude(z_max - z_min)
    )


def build_mounting_plate() -> cq.Workplane:
    """Build the disc with shank hole, flavor-tube pill slot, and
    top-outer-edge fillet. The top-outer fillet is applied before the
    holes are cut, so the outer circle is the only top-face edge at
    that moment."""
    plate = vertical_cylinder(plate_center, plate_radius, plate_z_range)
    plate = plate.faces(">Z").edges().fillet(top_outer_fillet_r)

    plate = plate.cut(vertical_cylinder(shank_hole_center, shank_hole_radius, plate_z_range))
    plate = plate.cut(vertical_y_slot(pill_slot_center, pill_slot_length_y, pill_slot_width_x, plate_z_range))

    return plate


def main():
    plate = build_mounting_plate()

    # Authoring frame is the upstream Z-up (matches the harvested
    # Westbrass valve body the plate seats against). Rotate to the
    # repo's +Y-up frame at the STEP export boundary so downstream
    # consumers — drawings, the assembly's HLR projector — read it
    # in the same convention as the cold-core / enclosure.
    # Map: old (X, Y, Z) -> new (-Y, Z, -X)
    #   +Z body-up        -> +Y (height)
    #   -X gooseneck side -> +Z (toward the user)
    #   +Y lateral        -> -X
    out = _here / "touch-flo-mounting-plate.step"
    export_step(
        plate
        .rotate((0, 0, 0), (0, 0, 1), 90)
        .rotate((0, 0, 0), (1, 0, 0), -90),
        str(out),
    )

    print(f"-> {out.name}")

    variables = {
        "PLATE_D": f"{2 * plate_radius:.4g} mm",
        "PLATE_T": f"{plate_thickness:.4g} mm",
        "PLATE_X": f"{plate_center[0]:.4g} mm",
        "PLATE_Z_BOTTOM": f"{plate_z_range[0]:.4g}",
        "SHANK_HOLE_D": f"{2 * shank_hole_radius:.4g} mm",
        "SHANK_OD": f"{shank_diameter_nominal:.4g} mm",
        "TUBE_CENTER_Y": f"{2 * flavor_tube_y_offset:.4g} mm",
        "PLATE_FLAVOR_X": f"{pill_slot_center[0]:.4g} mm",
        "PLATE_PILL_L": f"{pill_slot_length_y:.4g} mm",
        "PLATE_PILL_W": f"{pill_slot_width_x:.4g} mm",
        "TOP_FILLET_R": f"{top_outer_fillet_r:.4g} mm",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "PLATE_D": 1,
            "PLATE_T": 1,
            "PLATE_X": 1,
            "PLATE_Z_BOTTOM": 1,
            "SHANK_HOLE_D": 1,
            "SHANK_OD": 1,
            "TUBE_CENTER_Y": 1,
            "PLATE_FLAVOR_X": 1,
            "PLATE_PILL_L": 1,
            "PLATE_PILL_W": 1,
            "TOP_FILLET_R": 1,
        },
    )
    print("-> README.md")

    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "PLATE_D": 1,
            "PLATE_T": 1,
            "PLATE_X": 1,
            "SHANK_OD": 1,
            "TUBE_CENTER_Y": 1,
            "PLATE_FLAVOR_X": 1,
            "PLATE_PILL_L": 1,
            "PLATE_PILL_W": 1,
            "TOP_FILLET_R": 1,
        },
    )
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
