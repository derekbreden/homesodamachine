"""
Plan A coil winding mandrel — single first-attempt mandrel.

Hollow PETG-printed mandrel for hand-winding 1/4" OD copper around the
5" round 316L pressure vessel.  4 mm solid PETG wall (no infill) with
a shallow helical guide groove sized so the copper nests cleanly into
the cradle but only 1 mm deep — easy to lift off after winding.

Sized to align the coil's start and end with the foam-bag-shell's
copper inlet/outlet plugs so the user's exit bends are purely radial
(no vertical jog).

Geometry chain
--------------
- Springback compensation: 4 mm net radial undersize from the 5" tank.
- Shallow groove: profile R = TUBE_RAD (3.175 mm, matches copper) but
  the helix path is offset 2.175 mm outward of the cylinder surface,
  so the cut depth is only 1 mm.  Copper centerline rests at radius
  (mandrel_R + 2.175).
- Solving back: mandrel_R = TANK_R − undersize − groove_offset =
  63.5 − 4 − 2.175 = 57.325 → mandrel OD = 114.65 mm.
- Wind length 120.4 mm = Y span between inlet plug (Y=46) and outlet
  plug (Y=166.4) in the foam-bag-shell — coil ends exit through the
  plugs with purely radial (no vertical) bends.
- 9.687 wraps total = 9 full wraps + 247.4° fractional wrap, where
  247.4° is the CCW azimuthal delta from the inlet plug at azimuth
  146.31° to the outlet plug at azimuth 33.69° in the foam-bag-shell.
  Right-hand helix (default makeHelix direction).  Pitch = 120.4 /
  9.687 = 12.43 mm = 0.489" — close to but not exactly the 0.5" of
  Plan B; driven by alignment, not by roundness.

Why "shallow + same-R" cradle works for both nest and removal
-------------------------------------------------------------
The cradle and copper share the same circle radius R = TUBE_RAD.  When
the cradle is offset outward, the copper still nests perfectly (the
inner half of the copper occupies the inner half of the would-be-full
cradle), but only the bottom 1 mm of the copper is BELOW the cylinder
surface.  Lifting the wound coil off the mandrel is then a 1 mm radial
displacement vs the 3.175 mm of a full half-cradle.

OCCT BOP fix retained
---------------------
isFrenet=False (parallel transport) — verified reliable across all R
values; isFrenet=True is flaky for helix-on-cylinder cuts.  See git
log for the diagnostic sweep.
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
# COPPER, TANK, AND TARGET COMPENSATION
# ═══════════════════════════════════════════════════════

TUBE_OD_IN = 0.250
TUBE_RAD   = (TUBE_OD_IN / 2) * 25.4   # 3.175 mm

TANK_OD_MM = 127.0                     # 5" carbonator tank OD
TANK_R     = TANK_OD_MM / 2            # 63.5 mm

NET_UNDERSIZE_MM = 4.0                 # springback compensation target


# ═══════════════════════════════════════════════════════
# GROOVE GEOMETRY (shallow, same-R cradle)
# ═══════════════════════════════════════════════════════

GROOVE_DEPTH_MM    = 1.0
GROOVE_PROFILE_R   = TUBE_RAD                                   # 3.175 mm
GROOVE_OFFSET      = GROOVE_PROFILE_R - GROOVE_DEPTH_MM         # 2.175 mm

# Copper centerline rests at the cradle profile center radius —
# same as mandrel_R + GROOVE_OFFSET.
MANDREL_R  = TANK_R - NET_UNDERSIZE_MM - GROOVE_OFFSET          # 57.325 mm
MANDREL_OD = 2 * MANDREL_R                                       # 114.65 mm

WALL_MM = 4.0


# ═══════════════════════════════════════════════════════
# FOAM-BAG-SHELL ALIGNMENT
# ═══════════════════════════════════════════════════════

# Plug positions in foam-bag-shell coords (Y is the cylinder axis).
# From hardware/printed-parts/foam-bag-shell/generate_step_cadquery.py
# cut_slit_and_build_plug_for_copper_inlet:
#   inlet  (which=0): origin (-30, 46.0,  20)
#   outlet (which=1): origin ( 30, 166.4, 20)
PLUG_INLET_X,  PLUG_INLET_Y,  PLUG_INLET_Z  = -30.0,  46.0, 20.0
PLUG_OUTLET_X, PLUG_OUTLET_Y, PLUG_OUTLET_Z =  30.0, 166.4, 20.0

WIND_LEN_MM = PLUG_OUTLET_Y - PLUG_INLET_Y                       # 120.4 mm

PLUG_INLET_AZ_DEG  = math.degrees(math.atan2(PLUG_INLET_Z,  PLUG_INLET_X))   # 146.31°
PLUG_OUTLET_AZ_DEG = math.degrees(math.atan2(PLUG_OUTLET_Z, PLUG_OUTLET_X))  # 33.69°

# CCW azimuthal delta from inlet to outlet (right-hand helix climbs CCW).
PLUG_DELTA_CCW = (PLUG_OUTLET_AZ_DEG - PLUG_INLET_AZ_DEG) % 360  # 247.38°

# Total wraps = N full + fractional wrap that spans the azimuthal delta.
# N=9 picked as the smallest "first-attempt" wrap count below the user's
# 12-wrap cap; pitch falls out from alignment.
N_FULL_WRAPS    = 9
NUM_WRAPS_TOTAL = N_FULL_WRAPS + PLUG_DELTA_CCW / 360            # 9.687
PITCH           = WIND_LEN_MM / NUM_WRAPS_TOTAL                  # 12.43 mm


# ═══════════════════════════════════════════════════════
# MANDREL LENGTH ZONES
# ═══════════════════════════════════════════════════════

HANDLE_LEN_IN = 0.75
HANDLE_LEN    = HANDLE_LEN_IN * 25.4                             # 19.05 mm
TOTAL_LEN     = HANDLE_LEN + WIND_LEN_MM + HANDLE_LEN            # 158.5 mm


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


def build_mandrel():
    outer_r = MANDREL_R
    inner_r = outer_r - WALL_MM

    body = hollow_ring(outer_r, inner_r, 0, TOTAL_LEN)

    # Helical groove.  Path is offset OUTWARD by GROOVE_OFFSET so the
    # profile circle (R = TUBE_RAD around the path) cuts only
    # GROOVE_DEPTH_MM into the cylinder.
    path_radius = outer_r + GROOVE_OFFSET
    helix = cq.Wire.makeHelix(
        pitch=PITCH, height=WIND_LEN_MM, radius=path_radius
    ).translate((0, 0, HANDLE_LEN))

    sp = helix.startPoint().toTuple()
    profile_plane = cq.Plane(origin=sp, xDir=(0, 0, 1), normal=(0, 1, 0))
    profile = cq.Workplane(profile_plane).circle(GROOVE_PROFILE_R)

    swept_groove = profile.sweep(cq.Workplane(obj=helix), isFrenet=False)
    cut_body = body.cut(swept_groove, clean=False)

    # Restore clean handle zones — the swept tube bleeds ±GROOVE_PROFILE_R
    # past the wind-zone boundaries at each end.
    lower_handle = hollow_ring(outer_r, inner_r, 0, HANDLE_LEN)
    upper_handle = hollow_ring(outer_r, inner_r,
                               HANDLE_LEN + WIND_LEN_MM, TOTAL_LEN)
    return (cut_body
            .union(lower_handle, clean=False)
            .union(upper_handle, clean=False))


print(f"Tank OD:          {TANK_OD_MM:.1f} mm (R = {TANK_R:.2f})")
print(f"Net undersize:    {NET_UNDERSIZE_MM:.1f} mm radial")
print(f"Mandrel OD:       {MANDREL_OD:.2f} mm (R = {MANDREL_R:.3f})")
print(f"Wall thickness:   {WALL_MM:.1f} mm  (groove backing: {WALL_MM - GROOVE_DEPTH_MM:.1f} mm)")
print(f"Groove:           profile R={GROOVE_PROFILE_R} mm, "
      f"offset {GROOVE_OFFSET:.3f} mm, depth {GROOVE_DEPTH_MM:.1f} mm")
print(f"Wind length:      {WIND_LEN_MM:.1f} mm  (foam-shell plug Y span: {PLUG_INLET_Y} → {PLUG_OUTLET_Y})")
print(f"Inlet plug az:    {PLUG_INLET_AZ_DEG:.2f}°")
print(f"Outlet plug az:   {PLUG_OUTLET_AZ_DEG:.2f}°")
print(f"CCW alignment Δ:  {PLUG_DELTA_CCW:.2f}°")
print(f"Wraps:            {NUM_WRAPS_TOTAL:.4f}  ({N_FULL_WRAPS} full + "
      f"{PLUG_DELTA_CCW:.2f}° fractional)")
print(f"Pitch:            {PITCH:.3f} mm  ({PITCH/25.4:.4f}\")")
print(f"Total mandrel Z:  {TOTAL_LEN:.1f} mm  (handle {HANDLE_LEN:.2f} + "
      f"wind {WIND_LEN_MM:.1f} + handle {HANDLE_LEN:.2f})")

mandrel = build_mandrel()
solids = mandrel.solids().vals()
print(f"\nResult: {len(solids)} solid(s)")
for i, s in enumerate(solids):
    bb = s.BoundingBox()
    print(
        f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
        f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}], "
        f"V={s.Volume():.0f} mm^3, valid={s.isValid()}, "
        f"faces={len(s.Faces())}"
    )

out_path = Path(__file__).resolve().parent / "coil-mandrel.step"
export_step(mandrel, str(out_path))
print(f"\nExported: {out_path}")
