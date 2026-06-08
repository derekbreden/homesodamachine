"""Touch-Flo mounting plate — printed PETG disc that supports the
harvested Touch-Flo faucet body and the two flavor tubes that pass
alongside it. See README.md."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_here.parent))  # for _touch_flo_interface
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
from _cadq_export import export_step
from _touch_flo_interface import (
    flavor_tube_depth,
    pill_length_x,
    pill_width_y,
    shank_hole_diameter,
)
from docgen import substitute_md, substitute_py_comments
from world_workplane import WorldWorkplane, xy_plane_z_up


# [54.35 mm](PLATE_D) disc.
plate_radius = 54.35 / 2
# [4 mm](PLATE_T) thick.
plate_thickness = 4.0
# Top face flush with the deck plane (Z=0); plate hangs below.
plate_z_range = (-plate_thickness, 0.0)
# Disc is offset [3.175 mm](PLATE_Y) toward the back of the appliance
# (+Y in the +Z-up frame); no lateral offset.
plate_center = (0.0, +3.175)


# [11 mm](SHANK_OD) threaded shank clearance.
shank_diameter_nominal = 11.0
shank_hole_radius = shank_hole_diameter / 2
shank_hole_center = (0.0, 0.0)


# Flavor-tube pill slot. The two 1/4" LLDPE tubes are centered at
# ±flavor_tube_x_offset in the lateral direction (separation
# [6.35 mm](TUBE_CENTER_X)), combined into one X-oriented pill
# (rounded-rectangle) opening.
# [18.93 mm](PLATE_FLAVOR_Y) +Y offset of pill slot center from world origin
# (toward the back of the appliance).
pill_slot_center = (0.0, +flavor_tube_depth)
# [13.4 mm](PLATE_PILL_L) pill long axis — lateral, along world X.
# [7.05 mm](PLATE_PILL_W) pill short axis — depth, along world Y.


# [2 mm](TOP_FILLET_R) fillet on the top outer edge.
top_outer_fillet_r = 2.0


def vertical_cylinder(center, radius, z_range):
    """+Z-axis cylinder: world (x, y) center tuple, radius, and Z extent."""
    z_min, z_max = z_range
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=z_min)
        .moveTo(center)
        .circle(radius)
        .extrude(z_max - z_min)
        .unwrap()
    )


def vertical_x_slot(center, length_x, width_y, z_range):
    """+Z-axis pill (rounded-rectangle) prism with long axis along world X."""
    z_min, z_max = z_range
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=z_min)
        .moveTo(center)
        .slot2D(length_x, width_y, angle=0)
        .extrude(z_max - z_min)
        .unwrap()
    )


def build_mounting_plate() -> cq.Workplane:
    """Disc with shank hole, flavor-tube pill slot, and top-outer-edge fillet."""
    plate = vertical_cylinder(plate_center, plate_radius, plate_z_range)
    plate = plate.faces(">Z").edges().fillet(top_outer_fillet_r)

    plate = plate.cut(vertical_cylinder(shank_hole_center, shank_hole_radius, plate_z_range))
    plate = plate.cut(vertical_x_slot(pill_slot_center, pill_length_x, pill_width_y, plate_z_range))

    return plate


def main():
    plate = build_mounting_plate()

    out = _here / "touch-flo-mounting-plate.step"
    export_step(plate, str(out))

    print(f"-> {out.name}")

    variables = {
        "PLATE_D": f"{2 * plate_radius:.4g} mm",
        "PLATE_T": f"{plate_thickness:.4g} mm",
        "PLATE_Y": f"{plate_center[1]:.4g} mm",
        "PLATE_Z_BOTTOM": f"{plate_z_range[0]:.4g}",
        "SHANK_HOLE_D": f"{2 * shank_hole_radius:.4g} mm",
        "SHANK_OD": f"{shank_diameter_nominal:.4g} mm",
        "TUBE_CENTER_X": f"{pill_length_x - pill_width_y:.4g} mm",
        "PLATE_FLAVOR_Y": f"{pill_slot_center[1]:.4g} mm",
        "PLATE_PILL_L": f"{pill_length_x:.4g} mm",
        "PLATE_PILL_W": f"{pill_width_y:.4g} mm",
        "TOP_FILLET_R": f"{top_outer_fillet_r:.4g} mm",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "PLATE_D": 1,
            "PLATE_T": 1,
            "PLATE_Y": 1,
            "PLATE_Z_BOTTOM": 1,
            "SHANK_HOLE_D": 1,
            "SHANK_OD": 1,
            "TUBE_CENTER_X": 1,
            "PLATE_FLAVOR_Y": 1,
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
            "PLATE_Y": 1,
            "SHANK_OD": 1,
            "TUBE_CENTER_X": 1,
            "PLATE_FLAVOR_Y": 1,
            "PLATE_PILL_L": 1,
            "PLATE_PILL_W": 1,
            "TOP_FILLET_R": 1,
        },
    )
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
