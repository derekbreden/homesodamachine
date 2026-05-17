"""
Touch-Flo mounting gasket — printed-TPU disc that sits between the
rigid mounting plate (above) and the kitchen countertop (below).

PURPOSE
=======
- Water seal: stops countertop spills from wicking into the deck hole.
- Compliance: countertops are never perfectly flat; the gasket
  conforms to surface irregularities so the rigid plate doesn't rock.
- Anti-rotation friction: TPU's high CoF against laminate/stone keeps
  the assembly from twisting under handle torque.
- Clamping spring: elastic element that maintains preload on the
  under-counter nut as the cabinet wood swells/shrinks seasonally.
- Marring protection: keeps the printed plate off the countertop
  surface.
- Vibration / handle-action damping.

MATERIAL
========
Bambu TPU 90A (black). 90A is the gasket-industry-standard hardness:
soft enough to compress and seal under faucet clamp load, firm enough
to resist cold-flow over years. 95A reads too rigid against an uneven
countertop; 85A reads too spongy under sustained bolt preload.

GEOMETRY
========
- Ø 54.35 mm — exactly matches the mounting plate OD. Compresses to a
  ~Ø 55 ring under load; near-invisible from a normal viewing angle.
- 2.0 mm thick — print floor for TPU 90A on a 0.4 mm nozzle is ~1.2 mm
  (3 perimeters); 2.0 mm gives ~0.4 mm of compression travel at 20%
  squish, well within Touch-Flo shank thread engagement.
- Gasket spans Z = [-6, -4] in world coords; top face flush with the
  mounting plate's bottom face (PLATE_Z_BOTTOM = -4 in the plate
  script). Bottom face = countertop surface plane in this assembly.
- Plate center at world (3.175, 0) — same as the mounting plate, so
  the two stack concentrically.

HOLES (mirrored exactly from the mounting plate)
================================================
The hole pattern MUST match the plate exactly. Smaller holes deform
under shank/tube pressure; larger holes leak. Same-size = the rigid
plate is what locates the parts; the gasket just seals around them.

1. Shank hole — Ø 12.6 mm at world (0, 0).
2. Flavor-tube pill slot — 13.2 × 6.85 mm at world (18.925, 0),
   Y-oriented.

REGENERATE
==========
    tools/cad-venv/bin/python generate_step_cadquery.py
"""

import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import export_step


# Disc — Ø matches the mounting plate; 2.0 mm thick gives ~0.4 mm of
# 20%-squish travel for TPU 90A on a 0.4 mm nozzle.
gasket_diameter = 54.35
gasket_thickness = 2.0
gasket_center = (3.175, 0.0)

# Stacks immediately under the mounting plate (whose bottom face is at
# world Z = -4.0). Top of gasket meets bottom of plate; bottom of
# gasket sits on the countertop surface.
gasket_z_top = -4.0
gasket_z_range = (gasket_z_top - gasket_thickness, gasket_z_top)


# Hole geometry — mirrored exactly from the mounting plate. Same size
# leak-proofs the gasket-to-plate joint: smaller deforms under shank/
# tube pressure, larger leaks.
shank_hole_diameter = 12.6
shank_hole_center = (0.0, 0.0)

flavor_tube_hole_diameter = 6.85  # 6.35 OD + 0.5 mm clearance
flavor_tube_center = (18.925, 0.0)

# Pill slot covers both 1/4" flavor tubes (centers ±3.175 in Y) as one
# rounded-rectangle, matching the mounting plate. Length is end-to-end
# (Y); width is the per-tube hole diameter (X).
flavor_tube_y_offset = 3.175
pill_slot_length_y = 2 * flavor_tube_y_offset + flavor_tube_hole_diameter  # 13.2
pill_slot_width_x = flavor_tube_hole_diameter                              # 6.85


def build_mounting_gasket():
    """Build the TPU disc with shank hole and flavor-tube pill slot.

    No fillets — TPU at 2 mm with sharp edges compresses cleanly, and
    sharp edges grip the plate above and the countertop below better
    than rounded ones.

    All cuts pass through the full 2 mm thickness.
    """
    gasket = (
        cq.Workplane("XY")
        .workplane(offset=gasket_z_range[0])
        .moveTo(*gasket_center)
        .circle(gasket_diameter / 2.0)
        .extrude(gasket_thickness)
    )

    shank_hole = (
        cq.Workplane("XY")
        .workplane(offset=gasket_z_range[0])
        .moveTo(*shank_hole_center)
        .circle(shank_hole_diameter / 2.0)
        .extrude(gasket_thickness)
    )
    gasket = gasket.cut(shank_hole)

    pill_slot = (
        cq.Workplane("XY")
        .workplane(offset=gasket_z_range[0])
        .moveTo(*flavor_tube_center)
        .slot2D(pill_slot_length_y, pill_slot_width_x, angle=90)
        .extrude(gasket_thickness)
    )
    gasket = gasket.cut(pill_slot)

    return gasket


if __name__ == "__main__":
    gasket = build_mounting_gasket()

    out = Path(__file__).resolve().parent / "touch-flo-mounting-gasket.step"
    export_step(gasket, str(out))

    print("Touch-Flo mounting gasket")
    print(f"  Material:       Bambu TPU 90A (black)")
    print(f"  Disc:           Ø{gasket_diameter} mm × {gasket_thickness} mm thick")
    print(f"  Center:         {gasket_center}")
    print(f"  Z range:        {gasket_z_range[0]} → {gasket_z_range[1]}")
    print(f"  Shank hole:     Ø{shank_hole_diameter} mm at {shank_hole_center}")
    print(f"  Flavor pill:    {pill_slot_length_y} × {pill_slot_width_x} mm "
          f"at {flavor_tube_center}, Y-oriented")
    print(f"-> {out.name}")
