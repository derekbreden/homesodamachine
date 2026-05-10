"""
Touch-Flo mounting plate — printed disc that supports the harvested
Touch-Flo faucet body, the two flavor tubes that pass alongside it,
and (eventually) the shell that wraps around the assembly.

GEOMETRY
========
- Ø 54.35 mm, 5 mm thick disc — sized so the plate's edge sits 5 mm
  out from the shell base's outer cylinder (Ø 44.35 = SHELL_OUTER_R
  × 2). 5 mm matches the standard wall / margin elsewhere in the
  shell. Factory plate was Ø 44.5; this is bigger.
- Plate spans Z = [-5, 0] in world coords; top face flush with the
  deck plane (= body bottom in the faucet-assembly).
- Plate center at world (3.175, 0) — the midpoint of the assembly's
  lateral footprint at Z = 0 with 1/4" flavor tubes:
    -X edge: body cylindrical base at X = -15.75
    +X edge: outer wall of the +X flavor tube at X = +22.10
    midpoint: +3.175
  This puts the body at world (0, 0) shifted -3.175 mm in X relative
  to the plate center, by design. Plate center matches the shell's
  SHELL_CENTER_X for concentric stack-up.

HOLES
=====
1. Shank hole — Ø 12.6 mm at world (0, 0). Matches the factory
   mounting plate's clearance for the 11 mm threaded shank
   (~14.5% diametric clearance).
2. Flavor-tube pill slot — at world (18.925, 0), oriented along Y.
   Per-tube Ø would be 6.85 mm (= 6.35 OD + 0.5 mm clearance applied
   to the 1/4" flavor tubes), but the two tubes are only 6.35 mm
   apart center-to-center, so the per-tube circles overlap by
   ~0.5 mm. We model the combined opening as a single pill
   (rounded-rectangle) slot for cleaner printability:
     - Length (Y, end-to-end): 13.2 mm
     - Width (X):              6.85 mm

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
# PLATE DIMENSIONS
# ═══════════════════════════════════════════════════════

PLATE_DIAMETER  = 54.35   # mm — 5 mm radial gap to shell base (Ø 44.35)
PLATE_THICKNESS = 5.0     # mm
PLATE_CENTER_X  = 3.175   # mm — assembly footprint midpoint with
                           # 1/4" flavor tubes; matches SHELL_CENTER_X
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

# Flavor-tube pill slot. The two 1/4" (6.35 mm) LLDPE tubes are tangent
# in Y at centers ± 3.175.
FLAVOR_TUBE_OD       = 6.35
FLAVOR_TUBE_HOLE_DIA = 6.85                    # 6.35 OD + 0.5 mm clearance
FLAVOR_TUBE_X        = 18.925
FLAVOR_TUBE_Y_OFFSET = 3.175

PILL_SLOT_LENGTH_Y = 2 * FLAVOR_TUBE_Y_OFFSET + FLAVOR_TUBE_HOLE_DIA  # 13.2
PILL_SLOT_WIDTH_X  = FLAVOR_TUBE_HOLE_DIA                              # 6.85


# ═══════════════════════════════════════════════════════
# AESTHETIC TREATMENTS
# ═══════════════════════════════════════════════════════

# Fillet on the top outer edge — softens the visible ring around the
# body once the plate is installed. 2 mm on a 5 mm plate (40% of
# thickness) reads as an intentional finished edge without eating the
# flat landing area the body and shell sit on.
TOP_OUTER_FILLET_R = 2.0   # mm


# ═══════════════════════════════════════════════════════
# GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════

def build_mounting_plate() -> cq.Workplane:
    """Build the disc with shank hole, flavor-tube pill slot, and
    top-outer-edge fillet.

    Order of operations:
      1. Solid disc.
      2. Fillet the top outer edge — applied BEFORE the holes so the
         outer circle is the only top-face edge at that moment, no
         selector trickery needed.
      3. Cut the shank and pill holes (these stay sharp-edged).

    All cuts pass through the full 5 mm thickness.
    """
    plate = (
        cq.Workplane("XY")
        .workplane(offset=PLATE_Z_BOTTOM)
        .moveTo(PLATE_CENTER_X, PLATE_CENTER_Y)
        .circle(PLATE_DIAMETER / 2.0)
        .extrude(PLATE_THICKNESS)
    )

    # Fillet the single top edge (the outer circle) before any holes
    # introduce additional top-face edges.
    plate = plate.faces(">Z").edges().fillet(TOP_OUTER_FILLET_R)

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
    export_step(plate, str(out))

    print("Touch-Flo mounting plate")
    print(f"  Disc:           Ø{PLATE_DIAMETER} mm × {PLATE_THICKNESS} mm thick")
    print(f"  Center:         X = {PLATE_CENTER_X}, Y = {PLATE_CENTER_Y}")
    print(f"  Z range:        {PLATE_Z_BOTTOM} → {PLATE_Z_TOP}")
    print(f"  Shank hole:     Ø{SHANK_HOLE_DIAMETER} mm at "
          f"({SHANK_HOLE_X}, {SHANK_HOLE_Y})")
    print(f"  Flavor pill:    {PILL_SLOT_LENGTH_Y} × {PILL_SLOT_WIDTH_X} mm "
          f"at ({FLAVOR_TUBE_X}, 0), Y-oriented")
    print(f"  Top outer R:    {TOP_OUTER_FILLET_R} mm fillet")
    print(f"-> {out.name}")
