"""
Plan A coil winding mandrel.

Hollow PETG-printed mandrel for hand-winding 1/4" OD copper around the
5" round 316L pressure vessel.  4 mm solid PETG wall (no infill) with
16 toroidal pitch-guide grooves stacked along the 6" wind zone at
3/8" spacing.

Why toroidal rings instead of a true helical groove
---------------------------------------------------
Three approaches to a helical groove all produced invalid solids in
OCCT's boolean engine:

  1. parametricCurve sweep — the B-spline fit through 600 path samples
     collapsed to a near-straight curve (192 mm length vs the 5984 mm
     a true 16-wrap helix should have).  The cut produced a tiny
     artifact, not a groove.
  2. cq.Wire.makeHelix + sweep — path was correct (5984 mm length),
     swept tube was valid, but the boolean cut returned a 0-volume
     invalid solid (52 faces of broken topology).  OOMs with clean=True.
  3. 16 single-wrap iterative cuts — each individual cut produced an
     invalid solid; cumulative volume became impossibly negative after
     16 cuts.

OCCT cannot reconcile a swept helical tube with a cylinder.  Plan B's
coil-mandrel hits the same bug; its racetrack-helix path collapses to
~220 mm (vs expected ~4663 mm) and its STEP, though it exports cleanly,
contains no real groove either.

Toroidal cuts are clean OCCT primitives.  cq.Solid.makeTorus produces
a valid groove ring with one boolean operation per cut.  Six faces
per cut (3 cylinder + 2 plane + 1 torus), no topology drama.  The
tradeoff is the rings don't form a continuous spiral — the copper has
to step from one ring to the next at each wrap end — but for hand
winding with soft-annealed copper the difference is barely felt; the
rings serve as pitch-spacing references rather than a true helix.

Springback compensation
-----------------------
The 4 mm wide × 2 mm deep U-channel grooves are narrower than the
6.35 mm copper tube, so the wound tube rides on the groove rim, not
in the cradle.  Copper centerline rests at mandrel_R + TUBE_RAD = R +
3.175 mm; net copper bend radius = mandrel_R + TUBE_RAD.  ODs are
picked so the bend radius is undersize relative to the 5" tank by the
desired springback compensation.

Plan B's coil-mandrel still has the original bug.  Same diagnosis,
different fix (a racetrack equivalent to torus-stack would build a
racetrack-shaped channel at each Z level).  Not done here — it's
fallback inventory, revive only if Plan A welds prove unreliable.
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
# PHYSICAL DIMENSIONS (inches → mm)
# ═══════════════════════════════════════════════════════

TUBE_OD_IN = 0.250
TUBE_RAD   = (TUBE_OD_IN / 2) * 25.4   # 3.175 mm

TANK_OD_MM = 127.0                     # 5" carbonator tank OD
TANK_R     = TANK_OD_MM / 2            # 63.5 mm

# Mandrel ODs to generate, in mm.  Copper sits on the groove rim
# (groove is narrower than the tube), so the copper centerline is at
# radius (mandrel_OD/2 + TUBE_RAD).
#
#   Mandrel OD   Copper bend R       Net undersize    Notes
#   ----------   --------------      -------------    -----
#   111.0 mm     55.5+3.175 = 58.7   4.8 mm           tighter clamp, harder install
#   113.0 mm     56.5+3.175 = 59.7   3.8 mm           recommended starting point
#   115.0 mm     57.5+3.175 = 60.7   2.8 mm           looser clamp, easier install
MANDREL_ODS_MM = [111.0, 113.0, 115.0]

# Wall thickness.  4 mm is roughly 10 perimeters at 0.4 mm extrusion
# width — solid PETG all the way through, no infill, no flex.
# Mechanical loads on a winding mandrel are tiny (~20 N tangential
# bend force per loop, balanced around the circumference so net crush
# is zero), but the user wants real structure that handles by feel
# rather than a hollow shell with sparse internal lattice.  Backing
# under the 2 mm groove is 2 mm.
WALL_MM = 4.0

# Groove geometry.  2 mm minor radius torus centered on the cylinder
# surface produces a 4 mm wide × 2 mm deep U-channel.  Narrower than
# the 6.35 mm copper tube — copper rides on the groove rim and the
# ring serves as a pitch-spacing reference, not a tight cradle.
GROOVE_PROFILE_RAD = 2.0

# Wind zone (along Z).  Same as before: 6" tank height, 16 rings at
# 3/8" pitch, 0.75" plain handle zones top and bottom.
TOTAL_LEN_IN  = 7.5
HANDLE_LEN_IN = 0.75
WIND_LEN_IN   = 6.0

TOTAL_LEN  = TOTAL_LEN_IN  * 25.4    # 190.5 mm
HANDLE_LEN = HANDLE_LEN_IN * 25.4    # 19.05 mm
WIND_LEN   = WIND_LEN_IN   * 25.4    # 152.4 mm

PITCH_IN  = 0.375
PITCH     = PITCH_IN * 25.4          # 9.525 mm per ring
NUM_RINGS = 16

# Center the 16-ring stack within the wind zone.  Total ring span =
# 15 × PITCH = 142.875 mm; wind zone = 152.4 mm; slack = 9.525 mm,
# half on each end → first ring at HANDLE_LEN + PITCH/2.
RING_FIRST_Z = HANDLE_LEN + PITCH / 2


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def build_mandrel(mandrel_od_mm):
    outer_r = mandrel_od_mm / 2
    inner_r = outer_r - WALL_MM

    body = (
        cq.Workplane("XY")
        .circle(outer_r)
        .circle(inner_r)
        .extrude(TOTAL_LEN)
    )

    for i in range(NUM_RINGS):
        z = RING_FIRST_Z + i * PITCH
        torus = cq.Solid.makeTorus(
            outer_r,
            GROOVE_PROFILE_RAD,
            pnt=cq.Vector(0, 0, z),
            dir=cq.Vector(0, 0, 1),
        )
        body = body.cut(torus, clean=False)

    return body


out_dir = Path(__file__).resolve().parent

for od in MANDREL_ODS_MM:
    mandrel = build_mandrel(od)
    solids = mandrel.solids().vals()
    bend_r = od / 2 + TUBE_RAD
    undersize = TANK_R - bend_r
    print(
        f"\nMandrel OD {od:.1f} mm "
        f"(copper bend R {bend_r:.2f} mm, "
        f"net undersize {undersize:.2f} mm): "
        f"{len(solids)} solid(s)"
    )
    for i, s in enumerate(solids):
        bb = s.BoundingBox()
        print(
            f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
            f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}], "
            f"V={s.Volume():.0f} mm^3, valid={s.isValid()}, "
            f"faces={len(s.Faces())}"
        )
    out_path = out_dir / f"coil-mandrel-{int(round(od))}mm.step"
    export_step(mandrel, str(out_path))
    print(f"  Exported: {out_path}")
