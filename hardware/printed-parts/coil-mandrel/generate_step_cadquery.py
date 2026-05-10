"""
Plan A coil winding mandrel.

A 3D-printed forming mandrel that the user wraps soft-annealed 1/4" OD
copper tubing around to produce a pre-formed helical coil.  The coil
then stretches over the 5" OD round 316L SS pressure vessel.

Geometry:
  Solid right-circular cylinder with axis along Z.  A helical groove
  in the center winding zone cradles the 1/4" copper tube and enforces
  a 3/8" pitch.  0.75" plain cylindrical zones at each end serve as
  handle/clamp zones for winding.

Springback compensation (the whole reason this part exists):
  Hand-winding copper directly onto the 5" tank releases to a 1-3 mm
  radial gap between the coil and the tank — soft-annealed copper
  springs back loose.  Bending instead onto an undersize mandrel and
  stretching the resulting coil over the tank biases the spring
  direction inward (clamping the coil against the tank + 3M 425 foil
  tape), not outward.

  Tank OD = 5.000" = 127.0 mm (R = 63.5 mm).  Mandrel ODs are picked
  undersize by the desired radial springback compensation.  The first
  print queue empirically brackets the right value; off-the-shelf
  4.500" Sched 40 PVC pipe (≈6.35 mm radial undersize) is a fourth
  data point.

  Plan B uses the same approach with a racetrack mandrel ~2% undersize
  (1.5 mm radial); see plan-b/coil-mandrel/.
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

# Mandrel ODs to generate, in mm.  Tank OD is 5.000" = 127.0 mm.
#
#   Mandrel OD     Radial undersize    Notes
#   ----------     ----------------    -----
#   117.0 mm       5.0 mm              tighter clamp, harder install
#   119.0 mm       4.0 mm              recommended starting point
#   121.0 mm       3.0 mm              looser clamp, easier install
MANDREL_ODS_MM = [117.0, 119.0, 121.0]

# Mandrel length zones (along Z).
TOTAL_LEN_IN  = 7.5
HANDLE_LEN_IN = 0.75
WIND_LEN_IN   = 6.0    # matches the 6" tank tube height

TOTAL_LEN  = TOTAL_LEN_IN  * 25.4    # 190.5 mm
HANDLE_LEN = HANDLE_LEN_IN * 25.4    # 19.05 mm
WIND_LEN   = WIND_LEN_IN   * 25.4    # 152.4 mm

Z_GROOVE_START = HANDLE_LEN                  # 19.05 mm (top of lower handle)
Z_GROOVE_END   = HANDLE_LEN + WIND_LEN       # 171.45 mm (bottom of upper handle)

# Helical groove parameters.
TUBE_OD_IN  = 0.250                          # 1/4" copper tubing OD
TUBE_RAD_IN = TUBE_OD_IN / 2                 # 0.125" groove radius & depth

TUBE_OD  = TUBE_OD_IN  * 25.4                # 6.35 mm
TUBE_RAD = TUBE_RAD_IN * 25.4                # 3.175 mm

# 3/8" pitch leaves 1/8" between adjacent 1/4" loops on the tank
# surface — matches handwork.md's "single-layer wrap at ~1/8" pitch"
# (inter-loop spacing, not center-to-center).
PITCH_IN  = 0.375
PITCH     = PITCH_IN * 25.4                  # 9.525 mm per wrap

# 16 wraps × 0.375" pitch = 6.000" wind zone, exactly filling the tank
# height.
NUM_WRAPS = 16

# B-spline fit resolution for the helical path.  parametricCurve samples
# the path at N points and fits a smooth B-spline through them.  See
# plan-b/coil-mandrel/generate_step_cadquery.py for the polyline-vs-
# B-spline rationale (~500x STEP-size penalty for polyline sweeps).
CURVE_FIT_N = 600


# ═══════════════════════════════════════════════════════
# HELICAL GROOVE PATH
# ═══════════════════════════════════════════════════════

def helix_point(t_wraps, mandrel_radius):
    """(x, y, z) point on the helical groove centerline.

    t_wraps ∈ [0, NUM_WRAPS]; integer part picks the wrap, fractional
    part picks the angular position around the cylinder.
    """
    theta = 2 * math.pi * t_wraps
    x = mandrel_radius * math.cos(theta)
    y = mandrel_radius * math.sin(theta)
    z = Z_GROOVE_START + t_wraps * PITCH
    return x, y, z


def build_helical_groove_cut(mandrel_radius):
    """Sweep a circular cross-section along the helical path."""
    def path_func(t):
        return helix_point(t * NUM_WRAPS, mandrel_radius)

    path = cq.Workplane("XY").parametricCurve(path_func, N=CURVE_FIT_N)

    # Sweep profile: circle of TUBE_RAD perpendicular to the initial
    # path tangent.  The groove cuts a semicircular channel of depth
    # TUBE_RAD into the cylinder surface (the inner half of the swept
    # tube lies inside the mandrel; the outer half hangs in free space
    # but is harmless to boolean-subtract).
    start_pt = path_func(0.0)
    near_pt  = path_func(1.0 / CURVE_FIT_N)
    tangent  = (
        near_pt[0] - start_pt[0],
        near_pt[1] - start_pt[1],
        near_pt[2] - start_pt[2],
    )

    profile_plane = cq.Plane(
        origin=start_pt,
        xDir=(0, 0, 1),          # any direction perpendicular-ish to tangent
        normal=tangent,
    )

    profile = cq.Workplane(profile_plane).circle(TUBE_RAD)

    return profile.sweep(path)


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def cylinder(radius, z_bot, z_top):
    return (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, z_bot))
        .circle(radius)
        .extrude(z_top - z_bot)
    )


def build_mandrel(mandrel_od_mm):
    radius = mandrel_od_mm / 2

    body   = cylinder(radius, 0, TOTAL_LEN)
    groove = build_helical_groove_cut(radius)

    # Skip clean() — the helical sweep's sampled polyline produces a
    # high face count that trips OCCT's shape-upgrader on the result.
    cut_body = body.cut(groove, clean=False)

    # Restore clean handle zones.  The helical sweep profile (circle of
    # radius TUBE_RAD) bleeds slightly past Z_GROOVE_START and Z_GROOVE_END
    # into the handle zones.  Union the original handle cylinders back
    # on top to fill in any bleed, leaving the handle zones smooth.
    lower_handle = cylinder(radius, 0, HANDLE_LEN)
    upper_handle = cylinder(radius, HANDLE_LEN + WIND_LEN, TOTAL_LEN)
    return (cut_body
            .union(lower_handle, clean=False)
            .union(upper_handle, clean=False))


out_dir = Path(__file__).resolve().parent

for od in MANDREL_ODS_MM:
    mandrel = build_mandrel(od)
    solids = mandrel.solids().vals()
    print(f"\nMandrel OD {od:.1f} mm "
          f"(radial undersize {(127.0 - od) / 2:.2f} mm): "
          f"{len(solids)} solid(s)")
    for i, s in enumerate(solids):
        bb = s.BoundingBox()
        print(f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
              f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")
    out_path = out_dir / f"coil-mandrel-{int(round(od))}mm.step"
    export_step(mandrel, str(out_path))
    print(f"  Exported: {out_path}")
