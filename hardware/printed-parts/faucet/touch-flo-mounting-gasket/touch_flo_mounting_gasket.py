"""Touch-Flo mounting gasket — printed-TPU disc that sits between the
rigid mounting plate (above) and the kitchen countertop (below). Seals
spills out of the deck hole, conforms to surface irregularities so the
plate doesn't rock, anti-rotates under handle torque, and maintains
preload on the under-counter nut as the cabinet wood moves seasonally.

Material: Bambu TPU 90A (black). 90A is the gasket-industry-standard
hardness — soft enough to seal under clamp load, firm enough to resist
cold-flow over years. 95A reads too rigid against an uneven countertop;
85A too spongy under sustained bolt preload.

The hole pattern matches the mounting plate exactly. Same size leak-
proofs the joint: smaller deforms under shank/tube pressure, larger
leaks. The rigid plate locates the parts; the gasket just seals around
them.

Regenerate: tools/cad-venv/bin/python touch_flo_mounting_gasket.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
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


# Disc — Ø matches the mounting plate; [2 mm](GASKET_T) thick gives ~0.4 mm
# of 20%-squish travel for TPU 90A on a 0.4 mm nozzle.
# [54.35 mm](GASKET_D) outer disc, [2 mm](GASKET_T) thick.
gasket_diameter = 54.35
gasket_thickness = 2.0
# Disc center is offset slightly toward the back of the appliance
# (-Y in the repo's +Z-up frame). World (x, y) tuple — no lateral
# offset, [3.175 mm](GASKET_Y) toward the back.
gasket_center = (0.0, -3.175)

# Top face flush with the mounting plate's bottom face; bottom face
# sits on the countertop surface plane. +Z is height.
plate_z_bottom = -4.0
gasket_z_range = (plate_z_bottom - gasket_thickness, plate_z_bottom)


# Hole geometry — mirrored exactly from the mounting plate, via
# _touch_flo_interface (single source of truth for the stack-up).
# [12.6 mm](SHANK_HOLE_D) shank pocket — matches the body's threaded shank + clearance.
# Centered on the body axis (world origin).
shank_hole_center = (0.0, 0.0)

# [7.05 mm](FLAVOR_TUBE_HOLE_D) per-tube hole = [6.35 mm](FLAVOR_TUBE_OD) OD + 0.7 mm clearance.
# (Was 6.85 mm at 0.5 mm clearance until 2026-05-25; promoted to match
# the shell's print-validated attempt-15 value.)
# [18.93 mm](FLAVOR_TUBE_Y) pill center -Y from the shank (toward the back
# of the appliance, opposite the gooseneck dispense side) — shared with
# the shell.
flavor_tube_center = (0.0, -flavor_tube_depth)

# Pill slot covers both 1/4" flavor tubes (centers at ±flavor_tube_x_offset
# in world X) as one rounded-rectangle, matching the mounting plate.
# Long axis runs LATERAL (world X); short axis runs DEPTH (world Y).
# [13.4 mm](PILL_L) pill long axis (lateral, world X).
# [7.05 mm](PILL_W) pill short axis (depth, world Y).


def gasket_workplane(center):
    """Gasket bottom-face workplane with the pen at world (x, y) tuple
    `center`. Caller draws the 2D footprint on the world XY plane and
    extrudes through `gasket_thickness` in +Z."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=gasket_z_range[0])
        .moveTo(center)
    )


def build_mounting_gasket():
    """Disc with shank hole and flavor-tube pill slot. No fillets — TPU
    at 2 mm with sharp edges compresses cleanly, and sharp edges grip
    the plate above and the countertop below better than rounded ones."""
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
    # slot2D angle=0 — long axis along the workplane X = world X (lateral).
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

    # Short names scoped to this part. Units live inside the value so
    # the script controls them — change a unit in source and every
    # dynamic-comment marker follows.
    variables = {
        "GASKET_D": f"{gasket_diameter:.4g} mm",
        "GASKET_T": f"{gasket_thickness:.4g} mm",
        "GASKET_Y": f"{-gasket_center[1]:.4g} mm",
        "SHANK_HOLE_D": f"{shank_hole_diameter:.4g} mm",
        "FLAVOR_TUBE_OD": f"{flavor_tube_od:.4g} mm",
        "FLAVOR_TUBE_HOLE_D": f"{flavor_tube_hole_diameter:.4g} mm",
        "FLAVOR_TUBE_Y": f"{-flavor_tube_center[1]:.4g} mm",
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
