"""
Plan A coil winding mandrel.

Hollow PETG-printed mandrel for hand-winding 1/4" OD copper around the
5" round 316L pressure vessel.  4 mm solid PETG wall (no infill) with
a real helical groove that fully cradles the 1/4" copper, at 3/8"
pitch over a 6" wind zone.

Why the previous "OCCT can't do helical cuts" wasn't actually true
-----------------------------------------------------------------
A previous version of this script declared OCCT BOP fundamentally
incapable of cutting a helix from a cylinder, after testing four
approaches that all produced invalid solids.  That was wrong — the
helix curve was geometrically perfect (verified by direct OCCT
sampling: degree-14 BSpline, 210 control poles, every sample landed
exactly on R), and the boolean cut DOES work.  Two contributing
sources of confusion that misled me:

  1. cq.Wire.positionAt() is broken for the helix BSpline.  Sampling
     "by length" returned the same junk point at every parametric
     position, while .startPoint(), .endPoint(), and direct OCCT
     curve.Value(u) returned correct values.  Looked like a broken
     helix; was a CadQuery sampling bug.
  2. sweep(isFrenet=True) is flaky on helix-on-cylinder geometry —
     fails at certain R values, succeeds at others, and a 0.01 mm
     radius perturbation flips the result.  sweep(isFrenet=False)
     (parallel transport) is reliable across every R, body type, and
     wrap count tested.

Tested across R = 54.5 ... 60.5 mm × {hollow body, solid body} ×
{Frenet, no-Frenet}: no-Frenet is OK in all 36 cells; Frenet is BAD
in 8 of 36.  See conversation history for the full sweep table.
Cut volume with the half-cradle profile (radius = TUBE_RAD = 3.175 mm
centered on the cylinder surface) consistently removes ~87,000 mm^3
matching the expected half-tube-volume of the swept solid.

Plan B's coil-mandrel still has the same parametricCurve B-spline
collapse bug (its racetrack helix path collapses to ~220 mm length vs
the 4663 mm a real path should have); the no-Frenet sweep fix doesn't
apply directly (no makeHelix equivalent for racetrack cross-section).
Not touched here — fallback inventory only.

Springback compensation
-----------------------
The 1/4" copper sits IN the half-cradle groove with its centerline at
radius = mandrel_R (the helix path is on the cylinder surface, and the
copper nests into the groove with its center on that path).  Net copper
bend radius = mandrel_R; ODs are picked so that radius is undersize
relative to the 5" tank by the desired springback compensation.
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

# Mandrel ODs to generate, in mm.  Copper nests into the half-cradle
# groove with its centerline at radius = mandrel_R.
#
#   Mandrel OD   Copper bend R    Net undersize    Notes
#   ----------   --------------   -------------    -----
#   117.0 mm     58.5             5.0 mm           tighter clamp, harder install
#   119.0 mm     59.5             4.0 mm           recommended starting point
#   121.0 mm     60.5             3.0 mm           looser clamp, easier install
MANDREL_ODS_MM = [117.0, 119.0, 121.0]

# Wall thickness.  4 mm = ~10 perimeters at 0.4 mm extrusion width =
# solid PETG all the way through, no infill, no flex.  After the
# helical groove cuts 3.175 mm into the wall, 0.825 mm of material
# remains under the groove — thin but acceptable for PETG; the wall
# ABOVE and BELOW the groove (in the helical "crests" between turns)
# is the full 4 mm and carries the structure.
WALL_MM = 4.0

# Length zones.  6" wind zone matching tank height, 0.75" plain
# cylindrical handle zones top and bottom.  Handle zones are restored
# by unioning hollow rings on top of the cut, since the swept tube
# extends ±TUBE_RAD into the handle zones at each end.
TOTAL_LEN_IN  = 7.5
HANDLE_LEN_IN = 0.75
WIND_LEN_IN   = 6.0

TOTAL_LEN  = TOTAL_LEN_IN  * 25.4    # 190.5 mm
HANDLE_LEN = HANDLE_LEN_IN * 25.4    # 19.05 mm
WIND_LEN   = WIND_LEN_IN   * 25.4    # 152.4 mm

# 16 wraps × 0.375" pitch = 6.000" wind zone.
PITCH_IN  = 0.375
PITCH     = PITCH_IN * 25.4          # 9.525 mm per wrap


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def hollow_ring(outer_r, inner_r, z_bot, z_top):
    return (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, z_bot))
        .circle(outer_r).circle(inner_r)
        .extrude(z_top - z_bot)
    )


def build_mandrel(mandrel_od_mm):
    outer_r = mandrel_od_mm / 2
    inner_r = outer_r - WALL_MM

    body = hollow_ring(outer_r, inner_r, 0, TOTAL_LEN)

    # Helical groove.  cq.Wire.makeHelix produces a true OCCT
    # BSplineCurve helix (verified geometrically correct).  Sweep a
    # circular profile of radius TUBE_RAD centered on the cylinder
    # surface — the inner half of the swept tube becomes the cradle,
    # the outer half hangs in free space and is harmlessly subtracted.
    helix = cq.Wire.makeHelix(
        pitch=PITCH, height=WIND_LEN, radius=outer_r
    ).translate((0, 0, HANDLE_LEN))

    sp = helix.startPoint().toTuple()
    profile_plane = cq.Plane(origin=sp, xDir=(0, 0, 1), normal=(0, 1, 0))
    profile = cq.Workplane(profile_plane).circle(TUBE_RAD)

    # isFrenet=False (parallel transport) is reliable; isFrenet=True
    # produces invalid solids at certain R values.
    swept_groove = profile.sweep(cq.Workplane(obj=helix), isFrenet=False)

    cut_body = body.cut(swept_groove, clean=False)

    # Restore clean handle zones — the swept tube bleeds ±TUBE_RAD
    # past the wind-zone boundaries at each end.
    lower_handle = hollow_ring(outer_r, inner_r, 0, HANDLE_LEN)
    upper_handle = hollow_ring(outer_r, inner_r,
                               HANDLE_LEN + WIND_LEN, TOTAL_LEN)
    return (cut_body
            .union(lower_handle, clean=False)
            .union(upper_handle, clean=False))


out_dir = Path(__file__).resolve().parent

for od in MANDREL_ODS_MM:
    mandrel = build_mandrel(od)
    solids = mandrel.solids().vals()
    bend_r = od / 2   # copper nests in groove, centerline on cylinder surface
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
