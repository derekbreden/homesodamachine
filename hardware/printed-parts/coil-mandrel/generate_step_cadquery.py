"""
Plan A coil winding mandrel.

Hollow PETG-printed mandrel for hand-winding 1/4" OD copper around the
5" round 316L pressure vessel.  4 mm solid PETG wall — no infill, no
groove, no features.  Pitch is set by a separate spacer wire wound
alongside the copper, not by anything on the mandrel.

The spacer-wire pitch technique
-------------------------------
Wind the 1/4" (6.35 mm) copper tubing alongside a 1/8" (3.175 mm)
diameter spacer rod (steel, brass, or hardwood dowel — anything stiff
of that diameter).  The two run side-by-side around the mandrel; on
each loop the copper advances axially by the combined width of one
copper + one spacer = 9.525 mm = 3/8" exactly.  Pull the spacer out
after the wind; the copper coil has 3/8" pitch with 1/8" between
adjacent loops, which is the spec in handwork.md.

This is the standard spring-winder technique for setting even pitch
on a smooth mandrel, and it bypasses the need for the mandrel itself
to encode the helix.

Why no helical groove on the mandrel
------------------------------------
Four approaches all failed in OCCT BOP:

  1. parametricCurve sweep + cut — B-spline path collapsed to a near-
     straight curve (192 mm vs the 5984 mm of a true 16-wrap helix).
     Cut produced a tiny artifact, not a groove.
  2. cq.Wire.makeHelix + sweep + cut — path was correct (5984 mm),
     swept tube valid, but boolean cut returned an invalid 0-volume
     solid.  OOMs with clean=True.
  3. 16 single-wrap iterative cuts — each individual cut produced
     an invalid solid; cumulative volume went impossibly negative.
  4. Helical ridge via additive union — produced a "valid" solid but
     with broken topology (volume came out 200k where 270k expected,
     i.e. union effectively cut a strip out of the cylinder rather
     than adding the ridge).

OCCT's boolean engine cannot reconcile a swept-helix tube with a
cylinder, in either direction.  Plan B's coil-mandrel hits the same
bug (its racetrack-helix path collapses to ~220 mm vs ~4663 mm
expected); its STEP exports cleanly but contains no real groove.

A previous version of this script stacked 16 toroidal grooves
(makeTorus cuts work cleanly) along the wind zone, intending them as
"approximate helix" pitch markers.  That was wrong: a stack of flat
rings is geometrically NOT a helix, and a continuously-wound copper
coil would either kink at every ring transition or skip the rings
entirely.  Reverted.

Springback compensation
-----------------------
The wound copper centerline rests one tube radius (3.175 mm) outside
the smooth cylinder OD, so the copper bend radius = mandrel_R +
TUBE_RAD.  ODs are picked so the bend radius is undersize relative to
the 5" tank by the desired springback compensation.
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

# Mandrel ODs to generate, in mm.  Copper sits on the smooth cylinder
# surface, so the centerline is at radius (mandrel_OD/2 + TUBE_RAD).
#
#   Mandrel OD   Copper bend R       Net undersize    Notes
#   ----------   --------------      -------------    -----
#   111.0 mm     55.5+3.175 = 58.7   4.8 mm           tighter clamp, harder install
#   113.0 mm     56.5+3.175 = 59.7   3.8 mm           recommended starting point
#   115.0 mm     57.5+3.175 = 60.7   2.8 mm           looser clamp, easier install
MANDREL_ODS_MM = [111.0, 113.0, 115.0]

# Wall thickness.  4 mm = ~10 perimeters at 0.4 mm extrusion width =
# solid PETG all the way through, no infill, no flex.  Mechanical
# loads on a winding mandrel are tiny (~20 N tangential bend force per
# loop, balanced around the circumference so net crush is zero), but
# the user wants real structure to handle by feel — 4 mm gives that
# without doubling print time vs 5 mm.
WALL_MM = 4.0

# Length zones — same as before: 6" wind zone matching tank height,
# 0.75" plain handle zones top and bottom.
TOTAL_LEN_IN = 7.5
TOTAL_LEN    = TOTAL_LEN_IN * 25.4   # 190.5 mm


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def build_mandrel(mandrel_od_mm):
    outer_r = mandrel_od_mm / 2
    inner_r = outer_r - WALL_MM

    # Hollow open-tube: annular cross-section extruded along Z.  Open
    # at both ends — no end caps, so trapped-air problems don't happen
    # during print and the slicer doesn't need to bridge anything.
    return (
        cq.Workplane("XY")
        .circle(outer_r)
        .circle(inner_r)
        .extrude(TOTAL_LEN)
    )


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
            f"V={s.Volume():.0f} mm^3, valid={s.isValid()}"
        )
    out_path = out_dir / f"coil-mandrel-{int(round(od))}mm.step"
    export_step(mandrel, str(out_path))
    print(f"  Exported: {out_path}")
