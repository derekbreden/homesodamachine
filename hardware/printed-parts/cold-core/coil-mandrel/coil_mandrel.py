"""
Coil winding mandrel.

Hollow PETG cylinder for hand-winding 1/4" OD copper around the 5"
round 316L pressure vessel. 5 mm solid PETG wall, with a shallow
helical guide groove 1 mm deep that cradles the copper.

The coil's inner radius after winding is net_undersize mm smaller than
the tank radius, so the coil stretches radially to clamp the tank.

Coil start and end align with the foam-shell's copper inlet/outlet
plugs; exit bends are purely radial (no vertical jog).
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from _cadq_export import export_step
from docgen import substitute_py_comments


# ═══════════════════════════════════════════════════════
# COPPER, TANK, AND TARGET COMPENSATION
# ═══════════════════════════════════════════════════════

tube_od_in = 0.250
# [3.175 mm](TUBE_R) — 1/4" copper tube radius.
tube_radius = (tube_od_in / 2) * 25.4

tank_od = 127.0  # 5" carbonator tank OD
# [63.5 mm](TANK_R) — tank radius.
tank_radius = tank_od / 2

# Radial stretch to slip the coil onto the tank: the as-wound coil
# inner radius is this much smaller than the tank radius. Not the
# copper centerline displacement.
net_undersize = 3.0


# ═══════════════════════════════════════════════════════
# GROOVE GEOMETRY (shallow, same-R cradle)
# ═══════════════════════════════════════════════════════

groove_depth = 1.0
groove_profile_radius = tube_radius
# [2.175 mm](GROOVE_OFFSET) — helix path is offset OUTWARD this much so the
# tube_radius profile cuts only groove_depth into the cylinder.
groove_offset = groove_profile_radius - groove_depth

# Copper bottom rests at the groove bottom, so the coil inner radius is
# mandrel_radius − groove_depth, net_undersize mm under the tank radius.
# [61.5 mm](MANDREL_R) — radius of the mandrel cylinder surface.
mandrel_radius = tank_radius - net_undersize + groove_depth
# [123 mm](MANDREL_OD) — mandrel outer surface diameter.
mandrel_od = 2 * mandrel_radius

wall = 5.0
# [56.5 mm](MANDREL_INNER_R) — hollow ring inner radius.
mandrel_inner_radius = mandrel_radius - wall
mandrel_r_range = (mandrel_inner_radius, mandrel_radius)


# ═══════════════════════════════════════════════════════
# FOAM-SHELL ALIGNMENT
# ═══════════════════════════════════════════════════════

# Plug positions in foam-shell coords (Y is the cylinder axis).
plug_inlet_x, plug_inlet_y, plug_inlet_z = -30.0, 46.0, 20.0
plug_outlet_x, plug_outlet_y, plug_outlet_z = 30.0, 166.4, 20.0

# [120.4 mm](WIND_LENGTH) — Y span between foam-shell inlet and outlet plugs.
wind_length = plug_outlet_y - plug_inlet_y

plug_inlet_azimuth = math.degrees(math.atan2(plug_inlet_z, plug_inlet_x))
plug_outlet_azimuth = math.degrees(math.atan2(plug_outlet_z, plug_outlet_x))

# CCW azimuthal delta from inlet to outlet (right-hand helix climbs CCW).
plug_ccw_delta = (plug_outlet_azimuth - plug_inlet_azimuth) % 360

# [9](FULL_WRAPS) full wraps; the fractional wrap spans the azimuthal delta.
full_wraps = 9
total_wraps = full_wraps + plug_ccw_delta / 360
# [12.43 mm](PITCH) — helix pitch, 0.489".
pitch = wind_length / total_wraps


# ═══════════════════════════════════════════════════════
# MANDREL LENGTH ZONES
# ═══════════════════════════════════════════════════════

# Mandrel runs along +Z: lower handle, wind zone, upper handle.
handle_length_in = 0.75
# [19.05 mm](HANDLE_LENGTH) — 0.75" handle on each end.
handle_length = handle_length_in * 25.4
# [158.5 mm](TOTAL_LENGTH) — full mandrel length along the Z axis.
total_length = handle_length + wind_length + handle_length

mandrel_z_range = (0, total_length)
lower_handle_z_range = (mandrel_z_range[0], handle_length)
wind_z_range = (lower_handle_z_range[1], lower_handle_z_range[1] + wind_length)
upper_handle_z_range = (wind_z_range[1], mandrel_z_range[1])


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def hollow_ring(r_range, z_range):
    r_min, r_max = min(r_range), max(r_range)
    z_min, z_max = min(z_range), max(z_range)
    return (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, z_min))
        .circle(r_max).circle(r_min)
        .extrude(z_max - z_min)
    )


def build_mandrel():
    body = hollow_ring(mandrel_r_range, mandrel_z_range)

    # Helical groove.
    helix_path_radius = mandrel_radius + groove_offset
    helix = cq.Wire.makeHelix(
        pitch=pitch, height=wind_length, radius=helix_path_radius
    ).translate((0, 0, wind_z_range[0]))

    helix_start = helix.startPoint().toTuple()
    profile_plane = cq.Plane(origin=helix_start, xDir=(0, 0, 1), normal=(0, 1, 0))
    profile = cq.Workplane(profile_plane).circle(groove_profile_radius)

    swept_groove = profile.sweep(cq.Workplane(obj=helix), isFrenet=False)
    cut_body = body.cut(swept_groove, clean=False)

    # The handle zones are ungrooved; the swept groove overshoots the
    # wind zone by groove_profile_radius at each end.
    lower_handle = hollow_ring(mandrel_r_range, lower_handle_z_range)
    upper_handle = hollow_ring(mandrel_r_range, upper_handle_z_range)
    return (cut_body
            .union(lower_handle, clean=False)
            .union(upper_handle, clean=False))


# [121 mm](GROOVE_BOTTOM_OD) — diameter at the bottom of the helical groove.
groove_bottom_od = mandrel_od - 2 * groove_depth


def main():
    print(f"Tank OD:               {tank_od:.1f} mm (R = {tank_radius:.2f})")
    print(f"As-wound undersize:    {net_undersize:.1f} mm radial stretch")
    print(f"Mandrel surface OD:    {mandrel_od:.2f} mm (R = {mandrel_radius:.3f})")
    print(f"Groove bottom OD:      {groove_bottom_od:.2f} mm "
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

    variables = {
        "TUBE_R": f"{tube_radius:.4g} mm",
        "TANK_R": f"{tank_radius:.4g} mm",
        "GROOVE_OFFSET": f"{groove_offset:.4g} mm",
        "MANDREL_R": f"{mandrel_radius:.4g} mm",
        "MANDREL_OD": f"{mandrel_od:.4g} mm",
        "MANDREL_INNER_R": f"{mandrel_inner_radius:.4g} mm",
        "WIND_LENGTH": f"{wind_length:.4g} mm",
        "PITCH": f"{pitch:.4g} mm",
        "HANDLE_LENGTH": f"{handle_length:.4g} mm",
        "TOTAL_LENGTH": f"{total_length:.4g} mm",
        "GROOVE_BOTTOM_OD": f"{groove_bottom_od:.4g} mm",
        "FULL_WRAPS": f"{full_wraps:.4g}",  # bare count, no unit
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "TUBE_R": 1,
            "TANK_R": 1,
            "GROOVE_OFFSET": 1,
            "MANDREL_R": 1,
            "MANDREL_OD": 1,
            "MANDREL_INNER_R": 1,
            "WIND_LENGTH": 1,
            "PITCH": 1,
            "HANDLE_LENGTH": 1,
            "TOTAL_LENGTH": 1,
            "GROOVE_BOTTOM_OD": 1,
            "FULL_WRAPS": 1,
        },
    )
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
