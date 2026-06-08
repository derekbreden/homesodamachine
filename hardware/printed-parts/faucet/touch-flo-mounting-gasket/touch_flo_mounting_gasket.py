"""Touch-Flo mounting gasket — printed-TPU disc between the rigid
mounting plate (above) and the kitchen countertop (below). Seals spills
out of the deck hole, conforms to surface irregularities so the plate
doesn't rock, anti-rotates under handle torque, and holds preload on the
under-counter nut as the cabinet wood moves seasonally.

Material: Bambu TPU 90A (black).

Disc diameter and hole pattern match the mounting plate; the rigid plate
locates the parts, the gasket seals around them.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_here.parent.parent))  # for _touch_flo_interface
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
from _cadq_export import export_step
from _touch_flo_interface import (
    flavor_tube_od,
    flavor_tube_hole_dia as flavor_tube_hole_diameter,
    flavor_tube_depth,
    pill_length_x,
    pill_width_y,
    shank_hole_diameter,
)
from docgen import substitute_py_comments
from world_workplane import WorldWorkplane, xy_plane_z_up


# Disc Ø matches the mounting plate; [2 mm](GASKET_T) compresses under clamp load.
# [54.35 mm](GASKET_D) outer disc, [2 mm](GASKET_T) thick.
gasket_diameter = 54.35
gasket_thickness = 2.0
# Center offset [3.175 mm](GASKET_Y) +Y (toward the appliance back); no
# lateral offset.
gasket_center = (0.0, +3.175)

# Top face flush with the mounting plate's bottom face; bottom face on
# the countertop surface plane.
plate_z_bottom = -4.0
gasket_z_range = (plate_z_bottom - gasket_thickness, plate_z_bottom)


# Hole pattern matches the mounting plate.
# [12.6 mm](SHANK_HOLE_D) shank pocket — fits the body's threaded shank.
# Centered on the body axis (world origin).
shank_hole_center = (0.0, 0.0)

# [7.05 mm](FLAVOR_TUBE_HOLE_D) per-tube hole = [6.35 mm](FLAVOR_TUBE_OD) OD + 0.7 mm clearance.
# [18.93 mm](FLAVOR_TUBE_Y) pill center +Y from the shank (toward the
# appliance back, opposite the gooseneck dispense side) — shared with the
# shell.
flavor_tube_center = (0.0, +flavor_tube_depth)

# One rounded-rectangle slot covering both 1/4" flavor tubes.
# Long axis LATERAL (world X); short axis DEPTH (world Y).
# [13.4 mm](PILL_L) pill long axis (lateral, world X).
# [7.05 mm](PILL_W) pill short axis (depth, world Y).


def gasket_workplane(center):
    """Gasket bottom-face XY workplane, pen at world (x, y) `center`, +Z normal."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=gasket_z_range[0])
        .moveTo(center)
    )


def build_mounting_gasket():
    """Disc with shank hole and flavor-tube pill slot; sharp edges, no fillets."""
    gasket = (
        gasket_workplane(gasket_center)
        .circle(gasket_diameter / 2.0)
        .extrude(gasket_thickness)
    )
    shank_hole = (
        gasket_workplane(shank_hole_center)
        .circle(shank_hole_diameter / 2.0)
        .extrude(gasket_thickness)
    )
    # Long axis along world X (lateral).
    pill_slot = (
        gasket_workplane(flavor_tube_center)
        .slot2D(pill_length_x, pill_width_y, angle=0)
        .extrude(gasket_thickness)
    )
    return gasket.cut(shank_hole).cut(pill_slot).unwrap()


def main():
    gasket = build_mounting_gasket()
    out = Path(__file__).resolve().parent / "touch-flo-mounting-gasket.step"
    export_step(gasket, str(out))
    print(f"-> {out.name}")

    variables = {
        "GASKET_D": f"{gasket_diameter:.4g} mm",
        "GASKET_T": f"{gasket_thickness:.4g} mm",
        "GASKET_Y": f"{gasket_center[1]:.4g} mm",
        "SHANK_HOLE_D": f"{shank_hole_diameter:.4g} mm",
        "FLAVOR_TUBE_OD": f"{flavor_tube_od:.4g} mm",
        "FLAVOR_TUBE_HOLE_D": f"{flavor_tube_hole_diameter:.4g} mm",
        "FLAVOR_TUBE_Y": f"{flavor_tube_center[1]:.4g} mm",
        "PILL_L": f"{pill_length_x:.4g} mm",
        "PILL_W": f"{pill_width_y:.4g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "GASKET_D": 1,
            "GASKET_T": 2,
            "GASKET_Y": 1,
            "SHANK_HOLE_D": 1,
            "FLAVOR_TUBE_OD": 1,
            "FLAVOR_TUBE_HOLE_D": 1,
            "FLAVOR_TUBE_Y": 1,
            "PILL_L": 1,
            "PILL_W": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
