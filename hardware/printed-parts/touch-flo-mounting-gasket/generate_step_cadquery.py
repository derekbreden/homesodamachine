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
- Plate spans Z = [-7, -5] in world coords; top face flush with the
  mounting plate's bottom face (PLATE_Z_BOTTOM = -5 in the plate
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


# ═══════════════════════════════════════════════════════
# GASKET DIMENSIONS
# ═══════════════════════════════════════════════════════

GASKET_DIAMETER  = 54.35   # mm — matches mounting plate OD
GASKET_THICKNESS = 2.0     # mm — TPU 90A; ~20% compression headroom
GASKET_CENTER_X  = 3.175   # mm — matches mounting plate center
GASKET_CENTER_Y  = 0.0

# Stacks immediately under the mounting plate (whose bottom face is
# at world Z = -5.0). Top of gasket meets bottom of plate; bottom of
# gasket sits on the countertop surface.
GASKET_Z_TOP     = -5.0
GASKET_Z_BOTTOM  = GASKET_Z_TOP - GASKET_THICKNESS  # -7.0


# ═══════════════════════════════════════════════════════
# HOLE GEOMETRY (mirrored exactly from mounting plate)
# ═══════════════════════════════════════════════════════

SHANK_HOLE_DIAMETER = 12.6
SHANK_HOLE_X        = 0.0
SHANK_HOLE_Y        = 0.0

FLAVOR_TUBE_OD       = 6.35
FLAVOR_TUBE_HOLE_DIA = 6.85                    # 6.35 OD + 0.5 mm clearance
FLAVOR_TUBE_X        = 18.925
FLAVOR_TUBE_Y_OFFSET = 3.175

PILL_SLOT_LENGTH_Y = 2 * FLAVOR_TUBE_Y_OFFSET + FLAVOR_TUBE_HOLE_DIA  # 13.2
PILL_SLOT_WIDTH_X  = FLAVOR_TUBE_HOLE_DIA                              # 6.85


# ═══════════════════════════════════════════════════════
# GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════

def build_mounting_gasket() -> cq.Workplane:
    """Build the TPU disc with shank hole and flavor-tube pill slot.

    No fillets — TPU at 2 mm with sharp edges compresses cleanly, and
    sharp edges grip the plate above and the countertop below better
    than rounded ones.

    All cuts pass through the full 2 mm thickness.
    """
    gasket = (
        cq.Workplane("XY")
        .workplane(offset=GASKET_Z_BOTTOM)
        .moveTo(GASKET_CENTER_X, GASKET_CENTER_Y)
        .circle(GASKET_DIAMETER / 2.0)
        .extrude(GASKET_THICKNESS)
    )

    shank_hole = (
        cq.Workplane("XY")
        .workplane(offset=GASKET_Z_BOTTOM)
        .moveTo(SHANK_HOLE_X, SHANK_HOLE_Y)
        .circle(SHANK_HOLE_DIAMETER / 2.0)
        .extrude(GASKET_THICKNESS)
    )
    gasket = gasket.cut(shank_hole)

    pill_slot = (
        cq.Workplane("XY")
        .workplane(offset=GASKET_Z_BOTTOM)
        .moveTo(FLAVOR_TUBE_X, 0)
        .slot2D(PILL_SLOT_LENGTH_Y, PILL_SLOT_WIDTH_X, angle=90)
        .extrude(GASKET_THICKNESS)
    )
    gasket = gasket.cut(pill_slot)

    return gasket


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    gasket = build_mounting_gasket()

    out = Path(__file__).resolve().parent / "touch-flo-mounting-gasket.step"
    export_step(gasket, str(out))

    print("Touch-Flo mounting gasket")
    print(f"  Material:       Bambu TPU 90A (black)")
    print(f"  Disc:           Ø{GASKET_DIAMETER} mm × {GASKET_THICKNESS} mm thick")
    print(f"  Center:         X = {GASKET_CENTER_X}, Y = {GASKET_CENTER_Y}")
    print(f"  Z range:        {GASKET_Z_BOTTOM} → {GASKET_Z_TOP}")
    print(f"  Shank hole:     Ø{SHANK_HOLE_DIAMETER} mm at "
          f"({SHANK_HOLE_X}, {SHANK_HOLE_Y})")
    print(f"  Flavor pill:    {PILL_SLOT_LENGTH_Y} × {PILL_SLOT_WIDTH_X} mm "
          f"at ({FLAVOR_TUBE_X}, 0), Y-oriented")
    print(f"-> {out.name}")
