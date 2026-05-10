"""
Touch-Flo mounting plate — printed disc that supports the harvested
Touch-Flo faucet body, the two flavor tubes that pass alongside it,
and (eventually) the shell that wraps around the assembly.

GEOMETRY
========
- Ø 54.35 mm, 4 mm thick disc — sized so the plate's edge sits 5 mm
  out from the shell base's outer cylinder (Ø 44.35 = SHELL_OUTER_R
  × 2). 5 mm matches the standard wall / margin elsewhere in the
  shell. Factory plate was Ø 44.5; this is bigger.
- Plate spans Z = [-4, 0] in world coords; top face flush with the
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
3. Screw clearance holes (×2, mirrored across Y=0) — Ø 3.9 mm
   through, with Ø 5.7 × 1.25 mm counterbore on the BOTTOM face for
   the screw head. Located at θ = ±45° about the body center, r = 20
   from body center (world (14.142, ±14.142)) — the shell's "rear
   shoulder" wall material. Hosts M3 × 8 mm 316 SS ultra-low-profile
   socket cap screws (McMaster 91223A413) that thread into M3 brass
   heat-set inserts (ruthex short, Amazon B09ZHSGHXD) pressed into
   the shell above. Head Ø 5.5 × 1.0 tall sits 0.25 mm below the
   plate's bottom face; Ø 3.8 unthreaded shoulder under the head
   passes through the Ø 3.9 clearance with 0.05 mm/side fit.

REGENERATE
==========
    tools/cad-venv/bin/python generate_step_cadquery.py
"""

import math
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
PLATE_THICKNESS = 4.0     # mm — was 5; trimmed 1 mm to free shank
                           # thread engagement for the under-counter nut
                           # once the 2 mm TPU gasket is in the stack
PLATE_CENTER_X  = 3.175   # mm — assembly footprint midpoint with
                           # 1/4" flavor tubes; matches SHELL_CENTER_X
PLATE_CENTER_Y  = 0.0
PLATE_Z_TOP     = 0.0
PLATE_Z_BOTTOM  = PLATE_Z_TOP - PLATE_THICKNESS  # -4.0


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
# SCREW HOLES — heat-set retention to shell
# ═══════════════════════════════════════════════════════

# Two M3 socket-cap screws come up from below the plate, pass through
# clearance + counterbore, and thread into M3 brass heat-set inserts
# pressed into the touch-flo-shell above. Mirrored across Y=0; placed
# in the shell's "rear shoulder" wall material between the body bore
# and the shell outer cylinder, well clear of the pill slot.
#
# Screw — McMaster 91223A413: 316 SS ultra-low-profile socket head,
#   M3 × 0.5 × 8 mm, head Ø 5.5 × 1.0 mm tall, 2 mm hex socket,
#   Ø 3.8 unthreaded shoulder under the head.
#
# Insert — ruthex M3 short (Amazon B09ZHSGHXD): Ø 4.6 knurl OD /
#   Ø 3.9 body / 4 mm length, recommended install hole Ø 4.0.

# Clearance for the Ø 3.8 shoulder under the head (0.05 mm/side).
# Tight by intent — close fit aids screw alignment. If FDM print
# comes in undersize for this hole, drill out with a #29 (3.9 mm)
# bit before trying to install screws.
SCREW_HOLE_DIAMETER = 3.9

# Clearance for the Ø 5.5 head (0.1 mm/side). 1.25 mm deep =
# 1.0 mm head height + 0.25 mm clearance, so the head sits 0.25 mm
# below the bottom face. Plate material remaining above the
# counterbore (Z = -2.75 to 0): 2.75 mm.
SCREW_COUNTERBORE_DIAMETER = 5.7
SCREW_COUNTERBORE_DEPTH    = 1.25

# Position: θ = ±45° about the body center (0, 0), r = 20 mm.
# At this point all four wall margins hold ≥ 2 mm:
#   - to body bore (Ø 31.5 cyl @ origin):  2.25 mm
#   - to shell outer (Ø 44.35 cyl @ +X 3.175): 2.28 mm
#   - to pill slot (Y top edge at +6.6):     5.54 mm
#   - between the two screws (Y separation): 24.28 mm
SCREW_R_FROM_BODY  = 20.0
SCREW_THETA_DEG    = 45.0
SCREW_X            = SCREW_R_FROM_BODY * math.cos(math.radians(SCREW_THETA_DEG))   # ≈ 14.142
SCREW_Y_OFFSET     = SCREW_R_FROM_BODY * math.sin(math.radians(SCREW_THETA_DEG))   # ≈ 14.142


# ═══════════════════════════════════════════════════════
# AESTHETIC TREATMENTS
# ═══════════════════════════════════════════════════════

# Fillet on the top outer edge — softens the visible ring around the
# body once the plate is installed. 2 mm on a 4 mm plate (50% of
# thickness — half-bullnose, half-flat side) reads as an intentional
# finished edge without eating the flat landing area the body and
# shell sit on.
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

    All cuts pass through the full 4 mm thickness.
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

    # Two screw clearance holes (through) + counterbores (bottom face),
    # mirrored across Y=0.
    for y_sign in (+1, -1):
        sx = SCREW_X
        sy = y_sign * SCREW_Y_OFFSET

        clear = (
            cq.Workplane("XY")
            .workplane(offset=PLATE_Z_BOTTOM)
            .moveTo(sx, sy)
            .circle(SCREW_HOLE_DIAMETER / 2.0)
            .extrude(PLATE_THICKNESS)
        )
        plate = plate.cut(clear)

        cbore = (
            cq.Workplane("XY")
            .workplane(offset=PLATE_Z_BOTTOM)
            .moveTo(sx, sy)
            .circle(SCREW_COUNTERBORE_DIAMETER / 2.0)
            .extrude(SCREW_COUNTERBORE_DEPTH)
        )
        plate = plate.cut(cbore)

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
    print(f"  Screw clear:    Ø{SCREW_HOLE_DIAMETER} mm at "
          f"({SCREW_X:.3f}, ±{SCREW_Y_OFFSET:.3f}) "
          f"[θ=±{SCREW_THETA_DEG}°, r={SCREW_R_FROM_BODY} from body]")
    print(f"  Screw cbore:    Ø{SCREW_COUNTERBORE_DIAMETER} × "
          f"{SCREW_COUNTERBORE_DEPTH} mm deep, bottom face")
    print(f"  Top outer R:    {TOP_OUTER_FILLET_R} mm fillet")
    print(f"-> {out.name}")
