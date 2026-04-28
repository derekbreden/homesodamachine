"""
Touch-Flo mounting plate — printed disc that supports the harvested
Touch-Flo faucet body, the two flavor tubes that pass alongside it,
and (eventually) the shell that wraps around the assembly.

GEOMETRY
========
- Ø 50 mm, 5 mm thick disc (factory plate is Ø 44.5 mm; this is "a
  bit bigger, but not by much" per the user's call).
- Plate spans Z = [-5, 0] in world coords; top face flush with the
  deck plane (= body bottom in the faucet-assembly).
- Plate center at world (1.5875, 0) — the midpoint of the assembly's
  lateral footprint at Z = 0:
    -X edge: body cylindrical base at X = -15.75
    +X edge: outer wall of the +X flavor tube at X = +18.925
    midpoint: +1.5875
  This puts the body at world (0, 0) shifted -1.5875 mm in X relative
  to the plate center, by design.

HOLES
=====
1. Shank hole — Ø 12.6 mm at world (0, 0). Matches the factory
   mounting plate's clearance for the 11 mm threaded shank
   (~14.5% diametric clearance).
2. Flavor-tube pill slot — at world (17.3375, 0), oriented along Y.
   Per-tube Ø would be 3.6 mm (factory clearance ratio applied to
   the 3.175 mm flavor tubes), but the two tubes are only 3.175 mm
   apart center-to-center, so the per-tube circles overlap by
   ~0.425 mm. We model the combined opening as a single pill
   (rounded-rectangle) slot for cleaner printability:
     - Length (Y, end-to-end): 6.775 mm
     - Width (X):              3.6 mm

REGENERATE
==========
    tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path

import cadquery as cq


# ═══════════════════════════════════════════════════════
# PLATE DIMENSIONS
# ═══════════════════════════════════════════════════════

PLATE_DIAMETER  = 50.0    # mm
PLATE_THICKNESS = 5.0     # mm
PLATE_CENTER_X  = 1.5875  # mm — assembly footprint midpoint
PLATE_CENTER_Y  = 0.0
PLATE_Z_TOP     = 0.0
PLATE_Z_BOTTOM  = PLATE_Z_TOP - PLATE_THICKNESS  # -5.0


# ═══════════════════════════════════════════════════════
# HOLE GEOMETRY (mirrored from faucet-assembly)
# ═══════════════════════════════════════════════════════

# Shank — clearance for the 11 mm threaded shank. 12.6 mm matches the
# factory mounting plate.
SHANK_HOLE_DIAMETER = 12.6
SHANK_HOLE_X        = 0.0
SHANK_HOLE_Y        = 0.0

# Flavor-tube pill slot. The two 1/8" (3.175 mm) tubes are tangent in
# Y at centers ± 1.5875.
FLAVOR_TUBE_OD       = 3.175
FLAVOR_TUBE_HOLE_DIA = 3.6                     # ~14.5% diametric clearance
FLAVOR_TUBE_X        = 17.3375
FLAVOR_TUBE_Y_OFFSET = 1.5875

PILL_SLOT_LENGTH_Y = 2 * FLAVOR_TUBE_Y_OFFSET + FLAVOR_TUBE_HOLE_DIA  # 6.775
PILL_SLOT_WIDTH_X  = FLAVOR_TUBE_HOLE_DIA                              # 3.6


# ═══════════════════════════════════════════════════════
# GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════

def build_mounting_plate() -> cq.Workplane:
    """Build the disc with shank hole and flavor-tube pill slot.

    All cuts pass through the full 5 mm thickness.
    """
    plate = (
        cq.Workplane("XY")
        .workplane(offset=PLATE_Z_BOTTOM)
        .moveTo(PLATE_CENTER_X, PLATE_CENTER_Y)
        .circle(PLATE_DIAMETER / 2.0)
        .extrude(PLATE_THICKNESS)
    )

    shank_hole = (
        cq.Workplane("XY")
        .workplane(offset=PLATE_Z_BOTTOM)
        .moveTo(SHANK_HOLE_X, SHANK_HOLE_Y)
        .circle(SHANK_HOLE_DIAMETER / 2.0)
        .extrude(PLATE_THICKNESS)
    )
    plate = plate.cut(shank_hole)

    pill_slot = (
        cq.Workplane("XY")
        .workplane(offset=PLATE_Z_BOTTOM)
        .moveTo(FLAVOR_TUBE_X, 0)
        .slot2D(PILL_SLOT_LENGTH_Y, PILL_SLOT_WIDTH_X, angle=90)
        .extrude(PLATE_THICKNESS)
    )
    plate = plate.cut(pill_slot)

    return plate


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    plate = build_mounting_plate()

    out = Path(__file__).resolve().parent / "touch-flo-mounting-plate.step"
    cq.exporters.export(plate, str(out))

    print("Touch-Flo mounting plate")
    print(f"  Disc:           Ø{PLATE_DIAMETER} mm × {PLATE_THICKNESS} mm thick")
    print(f"  Center:         X = {PLATE_CENTER_X}, Y = {PLATE_CENTER_Y}")
    print(f"  Z range:        {PLATE_Z_BOTTOM} → {PLATE_Z_TOP}")
    print(f"  Shank hole:     Ø{SHANK_HOLE_DIAMETER} mm at "
          f"({SHANK_HOLE_X}, {SHANK_HOLE_Y})")
    print(f"  Flavor pill:    {PILL_SLOT_LENGTH_Y} × {PILL_SLOT_WIDTH_X} mm "
          f"at ({FLAVOR_TUBE_X}, 0), Y-oriented")
    print(f"-> {out.name}")
