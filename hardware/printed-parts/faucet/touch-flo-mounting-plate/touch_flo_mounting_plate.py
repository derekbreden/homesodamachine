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
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
from _cadq_export import export_step
# _touch_flo_interface still uses upstream Z-up suffixes; aliased to
# neutral names here. See the gasket script's import for the rationale.
from _touch_flo_interface import (
    flavor_tube_x as flavor_tube_depth_offset,
    pill_length_y as pill_lateral_extent,
    pill_width_x as pill_depth_extent,
    shank_hole_diameter,
)
from docgen import substitute_md, substitute_py_comments
from world_workplane import WorldWorkplane, xz_plane_y_up


# [54.35 mm](PLATE_D) disc.
plate_radius = 54.35 / 2
# [4 mm](PLATE_T) thick.
plate_thickness = 4.0
# Top face flush with the deck plane (Y=0); plate hangs below.
plate_y_range = (-plate_thickness, 0.0)
# Disc is offset [3.175 mm](PLATE_Z) toward the back of the appliance
# (-Z in the +Y-up frame). World (x, z) tuple — no lateral offset.
plate_center = (0.0, -3.175)


# [11 mm](SHANK_OD) threaded shank clearance.
shank_diameter_nominal = 11.0
shank_hole_radius = shank_hole_diameter / 2
shank_hole_center = (0.0, 0.0)


# Flavor-tube pill slot. The two 1/4" LLDPE tubes are centered at
# ±flavor_tube_x_offset in the lateral direction (separation
# [6.35 mm](TUBE_CENTER_X)), combined into one X-oriented pill
# (rounded-rectangle) opening.
# [18.93 mm](PLATE_FLAVOR_Z) -Z offset of pill slot center from world origin
# (toward the back of the appliance).
pill_slot_center = (0.0, -flavor_tube_depth_offset)
# [13.4 mm](PLATE_PILL_L) pill long axis — lateral, along world X.
# [7.05 mm](PLATE_PILL_W) pill short axis — depth, along world Z.


# [2 mm](TOP_FILLET_R) fillet on the top outer edge.
top_outer_fillet_r = 2.0


def vertical_cylinder(center, radius, y_range):
    """+Y-axis cylinder: world (x, z) center tuple, radius, and Y extent."""
    y_min, y_max = y_range
    return (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=y_min)
        .moveTo(center)
        .circle(radius)
        .extrude(y_max - y_min)
        .unwrap()
    )


def vertical_x_slot(center, length_x, width_z, y_range):
    """+Y-axis pill (rounded-rectangle) prism with long axis along world X."""
    y_min, y_max = y_range
    return (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=y_min)
        .moveTo(center)
        .slot2D(length_x, width_z, angle=0)
        .extrude(y_max - y_min)
        .unwrap()
    )


def build_mounting_plate() -> cq.Workplane:
    """Build the disc with shank hole, flavor-tube pill slot, and
    top-outer-edge fillet. The top-outer fillet is applied before the
    holes are cut, so the outer circle is the only top-face edge at
    that moment."""
    plate = vertical_cylinder(plate_center, plate_radius, plate_y_range)
    plate = plate.faces(">Y").edges().fillet(top_outer_fillet_r)

    plate = plate.cut(vertical_cylinder(shank_hole_center, shank_hole_radius, plate_y_range))
    plate = plate.cut(vertical_x_slot(pill_slot_center, pill_lateral_extent, pill_depth_extent, plate_y_range))

    return plate


def main():
    plate = build_mounting_plate()

    out = _here / "touch-flo-mounting-plate.step"
    export_step(plate, str(out))

    print(f"-> {out.name}")

    variables = {
        "PLATE_D": f"{2 * plate_radius:.4g} mm",
        "PLATE_T": f"{plate_thickness:.4g} mm",
        "PLATE_Z": f"{-plate_center[1]:.4g} mm",
        "PLATE_Y_BOTTOM": f"{plate_y_range[0]:.4g}",
        "SHANK_HOLE_D": f"{2 * shank_hole_radius:.4g} mm",
        "SHANK_OD": f"{shank_diameter_nominal:.4g} mm",
        # Lateral tube-center separation = pill_long - hole_dia.
        # (pill_lateral_extent = 2·y_offset + hole_dia, pill_depth_extent = hole_dia.)
        "TUBE_CENTER_X": f"{pill_lateral_extent - pill_depth_extent:.4g} mm",
        "PLATE_FLAVOR_Z": f"{-pill_slot_center[1]:.4g} mm",
        "PLATE_PILL_L": f"{pill_lateral_extent:.4g} mm",
        "PLATE_PILL_W": f"{pill_depth_extent:.4g} mm",
        "TOP_FILLET_R": f"{top_outer_fillet_r:.4g} mm",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "PLATE_D": 1,
            "PLATE_T": 1,
            "PLATE_Z": 1,
            "PLATE_Y_BOTTOM": 1,
            "SHANK_HOLE_D": 1,
            "SHANK_OD": 1,
            "TUBE_CENTER_X": 1,
            "PLATE_FLAVOR_Z": 1,
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
            "PLATE_Z": 1,
            "SHANK_OD": 1,
            "TUBE_CENTER_X": 1,
            "PLATE_FLAVOR_Z": 1,
            "PLATE_PILL_L": 1,
            "PLATE_PILL_W": 1,
            "TOP_FILLET_R": 1,
        },
    )
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
