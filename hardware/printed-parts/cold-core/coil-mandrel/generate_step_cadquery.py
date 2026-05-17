"""
Coil winding mandrel — single first-attempt mandrel.

Hollow PETG-printed mandrel for hand-winding 1/4" OD copper around the
5" round 316L pressure vessel.  5 mm solid PETG wall (no infill) with
a shallow helical guide groove sized so the copper nests cleanly into
the cradle but only 1 mm deep — easy to lift off after winding.

Sized to align the coil's start and end with the foam-shell's
copper inlet/outlet plugs so the user's exit bends are purely radial
(no vertical jog).

What "X mm undersize" means here
--------------------------------
"X mm undersize" = the stretch needed to slip the as-wound coil onto
the tank. After winding, the copper bottom sits at radius
(mandrel_radius − groove_depth) = the coil's inner radius. For the
coil to clamp the tank, we want this inner radius to be X mm SMALLER
than the tank radius (so the coil has to stretch X mm radially to fit
on).

  coil_inner_radius_after_winding = mandrel_radius − groove_depth
  X = tank_radius − coil_inner_radius_after_winding
  → mandrel_radius = tank_radius − X + groove_depth

For the 5" tank (R = 63.5 mm), 3 mm as-wound undersize, 1 mm groove:
  mandrel_radius = 63.5 − 3 + 1 = 61.5 → OD = 123 mm (mandrel surface)
  groove bottom diameter = 121 mm

This is the as-WOUND stretch; observed springback (1–3 mm radial)
relaxes the coil, so the post-release stretch is (X − Δ_spring) mm.
3 mm is on the loose end — picked deliberately by the user as a
first-attempt value after the previous 4 mm-as-wound version felt
too tight when test-fit on the tank.

(A previous version mis-defined undersize as the COPPER CENTERLINE
displacement from the tank surface, which gave the wrong sign on the
groove offset and produced an OD that was ~6 mm too small. See git
log around that commit.)

Geometry chain
--------------
- 3 mm as-wound undersize → mandrel OD 123 mm.
- Shallow groove: profile radius = tube_radius (3.175 mm, matches
  copper) but the helix path is offset 2.175 mm outward of the
  cylinder surface, so the cut depth is only 1 mm. Copper still
  nests perfectly into the cradle (same R), but only 1 mm engaged
  — easy to lift off.
- Wind length 120.4 mm = Y span between inlet plug (Y=46) and outlet
  plug (Y=166.4) in the foam-shell — coil ends exit through the
  plugs with purely radial (no vertical) bends.
- 9.687 wraps total = 9 full wraps + 247.4° fractional, where 247.4°
  is the CCW azimuthal delta from inlet plug at azimuth 146.31° to
  outlet plug at azimuth 33.69°. Right-hand helix. Pitch = 120.4 /
  9.687 = 12.43 mm = 0.489" — close to but not exactly the round-number
  0.5" pitch, driven by alignment to the foam-shell plug positions
  rather than by aesthetic roundness.

Wall thickness (5 mm) bumped from 4 mm because the 4 mm test print
was just slightly more flexible than wanted — well within mechanical
margin but stable feel matters for a hand-handled tool.

OCCT BOP fix retained
---------------------
isFrenet=False (parallel transport) — verified reliable across all R
values; isFrenet=True is flaky for helix-on-cylinder cuts. See git
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

tube_od_in = 0.250
tube_radius = (tube_od_in / 2) * 25.4  # 3.175 mm

tank_od = 127.0  # 5" carbonator tank OD
tank_radius = tank_od / 2  # 63.5 mm

# As-wound stretch needed to slip the coil onto the tank. See the
# docstring: this is tank_radius − coil_inner_radius_after_winding, NOT
# the copper centerline displacement.
net_undersize = 3.0


# ═══════════════════════════════════════════════════════
# GROOVE GEOMETRY (shallow, same-R cradle)
# ═══════════════════════════════════════════════════════

groove_depth = 1.0
groove_profile_radius = tube_radius  # 3.175 mm
groove_offset = groove_profile_radius - groove_depth  # 2.175 mm

# Coil inner radius after winding = mandrel_radius − groove_depth
# (copper bottom rests at the groove bottom). Solve for mandrel_radius
# such that coil_inner_radius = tank_radius − net_undersize:
mandrel_radius = tank_radius - net_undersize + groove_depth  # 61.5 mm
mandrel_od = 2 * mandrel_radius  # 123.0 mm

wall = 5.0


# ═══════════════════════════════════════════════════════
# FOAM-SHELL ALIGNMENT
# ═══════════════════════════════════════════════════════

# Plug positions in foam-shell coords (Y is the cylinder axis).
# From hardware/printed-parts/cold-core/_foam_shell_geometry.py
# cut_slit_and_build_plug_for_copper_inlet:
#   inlet  (which=0): origin (-30, 46.0,  20)
#   outlet (which=1): origin ( 30, 166.4, 20)
plug_inlet_x, plug_inlet_y, plug_inlet_z = -30.0, 46.0, 20.0
plug_outlet_x, plug_outlet_y, plug_outlet_z = 30.0, 166.4, 20.0

wind_length = plug_outlet_y - plug_inlet_y  # 120.4 mm

plug_inlet_azimuth = math.degrees(math.atan2(plug_inlet_z, plug_inlet_x))  # 146.31°
plug_outlet_azimuth = math.degrees(math.atan2(plug_outlet_z, plug_outlet_x))  # 33.69°

# CCW azimuthal delta from inlet to outlet (right-hand helix climbs CCW).
plug_ccw_delta = (plug_outlet_azimuth - plug_inlet_azimuth) % 360  # 247.38°

# Total wraps = N full + fractional wrap that spans the azimuthal delta.
# N=9 picked as the smallest "first-attempt" wrap count below the user's
# 12-wrap cap; pitch falls out from alignment.
full_wraps = 9
total_wraps = full_wraps + plug_ccw_delta / 360  # 9.687
pitch = wind_length / total_wraps  # 12.43 mm


# ═══════════════════════════════════════════════════════
# MANDREL LENGTH ZONES
# ═══════════════════════════════════════════════════════

# Mandrel runs along +Z: lower handle, wind zone, upper handle.
handle_length_in = 0.75
handle_length = handle_length_in * 25.4  # 19.05 mm
total_length = handle_length + wind_length + handle_length  # 158.5 mm

lower_handle_z_range = (0, handle_length)
wind_z_range = (handle_length, handle_length + wind_length)
upper_handle_z_range = (handle_length + wind_length, total_length)


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def hollow_ring(outer_r, inner_r, z_range):
    z_min, z_max = min(z_range), max(z_range)
    return (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, z_min))
        .circle(outer_r).circle(inner_r)
        .extrude(z_max - z_min)
    )


def build_mandrel():
    outer_r = mandrel_radius
    inner_r = outer_r - wall

    full_z_range = (lower_handle_z_range[0], upper_handle_z_range[1])
    body = hollow_ring(outer_r, inner_r, full_z_range)

    # Helical groove. Path is offset OUTWARD by groove_offset so the
    # profile circle (radius = tube_radius around the path) cuts only
    # groove_depth into the cylinder.
    helix_path_radius = outer_r + groove_offset
    helix = cq.Wire.makeHelix(
        pitch=pitch, height=wind_length, radius=helix_path_radius
    ).translate((0, 0, wind_z_range[0]))

    helix_start = helix.startPoint().toTuple()
    profile_plane = cq.Plane(origin=helix_start, xDir=(0, 0, 1), normal=(0, 1, 0))
    profile = cq.Workplane(profile_plane).circle(groove_profile_radius)

    swept_groove = profile.sweep(cq.Workplane(obj=helix), isFrenet=False)
    cut_body = body.cut(swept_groove, clean=False)

    # Restore clean handle zones — the swept tube bleeds ±groove_profile_radius
    # past the wind-zone boundaries at each end.
    lower_handle = hollow_ring(outer_r, inner_r, lower_handle_z_range)
    upper_handle = hollow_ring(outer_r, inner_r, upper_handle_z_range)
    return (cut_body
            .union(lower_handle, clean=False)
            .union(upper_handle, clean=False))


groove_bottom_d = mandrel_od - 2 * groove_depth

print(f"Tank OD:               {tank_od:.1f} mm (R = {tank_radius:.2f})")
print(f"As-wound undersize:    {net_undersize:.1f} mm radial stretch")
print(f"Mandrel surface OD:    {mandrel_od:.2f} mm (R = {mandrel_radius:.3f})")
print(f"Groove bottom OD:      {groove_bottom_d:.2f} mm "
      f"(= tank_od − 2·undersize = {tank_od - 2 * net_undersize:.1f})")
print(f"Wall thickness:        {wall:.1f} mm  "
      f"(groove backing: {wall - groove_depth:.1f} mm)")
print(f"Groove:                profile R={groove_profile_radius} mm, "
      f"offset {groove_offset:.3f} mm, depth {groove_depth:.1f} mm")
print(f"Wind length:           {wind_length:.1f} mm  "
      f"(foam-shell plug Y span: {plug_inlet_y} → {plug_outlet_y})")
print(f"Inlet plug azimuth:    {plug_inlet_azimuth:.2f}°")
print(f"Outlet plug azimuth:   {plug_outlet_azimuth:.2f}°")
print(f"CCW alignment delta:   {plug_ccw_delta:.2f}°")
print(f"Wraps:                 {total_wraps:.4f}  ({full_wraps} full + "
      f"{plug_ccw_delta:.2f}° fractional)")
print(f"Pitch:                 {pitch:.3f} mm  ({pitch / 25.4:.4f}\")")
print(f"Total mandrel Z:       {total_length:.1f} mm  (handle {handle_length:.2f} + "
      f"wind {wind_length:.1f} + handle {handle_length:.2f})")

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
