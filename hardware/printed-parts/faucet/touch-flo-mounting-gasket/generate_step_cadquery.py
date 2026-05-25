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

Regenerate: tools/cad-venv/bin/python generate_step_cadquery.py
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
from _cadq_export import export_step
from docgen import substitute_py_comments


# Disc — Ø matches the mounting plate; [2 mm](GASKET_T) thick gives ~0.4 mm
# of 20%-squish travel for TPU 90A on a 0.4 mm nozzle.
# [54.35 mm](GASKET_D) outer disc, [2 mm](GASKET_T) thick.
gasket_diameter = 54.35
gasket_thickness = 2.0
gasket_center = (3.175, 0.0)

# Top face flush with the mounting plate's bottom face; bottom face
# sits on the countertop surface plane.
plate_z_bottom = -4.0
gasket_z_range = (plate_z_bottom - gasket_thickness, plate_z_bottom)


# Hole geometry — mirrored exactly from the mounting plate.
# [12.6 mm](SHANK_HOLE_D) shank pocket — matches the body's threaded shank + clearance.
shank_hole_diameter = 12.6
shank_hole_center = (0.0, 0.0)

# [6.85 mm](FLAVOR_TUBE_HOLE_D) per-tube hole = [6.35 mm](FLAVOR_TUBE_OD) OD + 0.5 mm clearance.
flavor_tube_od = 6.35
flavor_tube_hole_diameter = flavor_tube_od + 0.5
# [18.925 mm](FLAVOR_TUBE_X) pill center +X from the shank — shared with the shell.
flavor_tube_center = (18.925, 0.0)

# Pill slot covers both 1/4" flavor tubes (centers ±flavor_tube_y_offset
# in Y) as one rounded-rectangle, matching the mounting plate. Length is
# end-to-end (Y); width is the per-tube hole diameter (X).
flavor_tube_y_offset = 3.175
# [13.2 mm](PILL_L) pill long axis (Y) = 2 × y_offset + hole_dia.
pill_slot_length_y = 2 * flavor_tube_y_offset + flavor_tube_hole_diameter
# [6.85 mm](PILL_W) pill short axis (X) = hole_dia.
pill_slot_width_x = flavor_tube_hole_diameter


def gasket_workplane(center):
    """Gasket bottom-face workplane with the pen at `center`. Caller
    draws the 2D footprint and extrudes through `gasket_thickness`."""
    return (
        cq.Workplane("XY")
        .workplane(offset=gasket_z_range[0])
        .moveTo(*center)
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
    pill_slot = (
        gasket_workplane(flavor_tube_center)
        .slot2D(pill_slot_length_y, pill_slot_width_x, angle=90)
        .extrude(gasket_thickness)
    )
    return gasket.cut(shank_hole).cut(pill_slot)


def main():
    gasket = build_mounting_gasket()
    out = Path(__file__).resolve().parent / "touch-flo-mounting-gasket.step"
    export_step(gasket, str(out))
    print(f"-> {out.name}")

    # Short names scoped to this part. Units live inside the value so
    # the script controls them — change a unit in source and every
    # dynamic-comment marker follows.
    variables = {
        "GASKET_D": f"{gasket_diameter:g} mm",
        "GASKET_T": f"{gasket_thickness:g} mm",
        "SHANK_HOLE_D": f"{shank_hole_diameter:g} mm",
        "FLAVOR_TUBE_OD": f"{flavor_tube_od:g} mm",
        "FLAVOR_TUBE_HOLE_D": f"{flavor_tube_hole_diameter:g} mm",
        "FLAVOR_TUBE_X": f"{flavor_tube_center[0]:g} mm",
        "PILL_L": f"{pill_slot_length_y:g} mm",
        "PILL_W": f"{pill_slot_width_x:g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "GASKET_D": 1,
            "GASKET_T": 2,
            "SHANK_HOLE_D": 1,
            "FLAVOR_TUBE_OD": 1,
            "FLAVOR_TUBE_HOLE_D": 1,
            "FLAVOR_TUBE_X": 1,
            "PILL_L": 1,
            "PILL_W": 1,
        },
    )
    print("-> generate_step_cadquery.py (self)")


if __name__ == "__main__":
    main()
