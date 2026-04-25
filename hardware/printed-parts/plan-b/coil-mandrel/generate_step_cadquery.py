"""
Coil winding mandrel.

A 3D-printed forming mandrel that the user wraps soft-annealed 1/4" OD
copper tubing around to produce a pre-formed helical coil.  The coil
then slips over a racetrack-shaped stainless-steel pressure vessel.

Geometry:
  Solid racetrack-cross-section cylinder with axis along Z.  A helical
  groove in the center winding zone cradles the 1/4" copper tube and
  enforces the 0.5" pitch.  0.75" plain racetrack zones at each end
  serve as handle/clamp zones for winding.

The racetrack footprint is intentionally ~2% undersize relative to the
target 5.566" x 3.966" tank to compensate for soft-copper springback.
"""

import math
from pathlib import Path
import cadquery as cq


# ═══════════════════════════════════════════════════════
# PHYSICAL DIMENSIONS (inches -> mm)
# ═══════════════════════════════════════════════════════

# Racetrack cross-section (long axis along X, short axis along Y).
SEMI_R_IN    = 1.925                          # 3.85 / 2
FLAT_LEN_IN  = 1.600                          # 5.45 - 3.85

SEMI_R       = SEMI_R_IN   * 25.4             # 48.895 mm
FLAT_LEN     = FLAT_LEN_IN * 25.4             # 40.640 mm

# Mandrel length (Z extent).
TOTAL_LEN_IN = 7.5
HANDLE_LEN_IN = 0.75
WIND_LEN_IN  = 6.0                            # 12 wraps * 0.5" pitch

TOTAL_LEN    = TOTAL_LEN_IN  * 25.4           # 190.5 mm
HANDLE_LEN   = HANDLE_LEN_IN * 25.4           # 19.05 mm
WIND_LEN     = WIND_LEN_IN   * 25.4           # 152.4 mm

Z_GROOVE_START = HANDLE_LEN                   # 19.05 mm (top of lower handle)
Z_GROOVE_END   = HANDLE_LEN + WIND_LEN        # 171.45 mm (bottom of upper handle)

# Helical groove parameters.
TUBE_OD_IN   = 0.250                          # 1/4" copper tubing OD
TUBE_RAD_IN  = TUBE_OD_IN / 2                 # 0.125" groove radius & depth

TUBE_OD      = TUBE_OD_IN  * 25.4             # 6.35 mm
TUBE_RAD     = TUBE_RAD_IN * 25.4             # 3.175 mm

PITCH_IN     = 0.5
PITCH        = PITCH_IN * 25.4                # 12.7 mm per wrap
NUM_WRAPS    = 12

# Fit resolution for the helical path B-spline.  parametricCurve samples
# the path at N points and fits a smooth B-spline through them.  At
# N = 600 over 12 wraps, that's 50 samples per wrap — ample to capture
# the racetrack-perimeter shape (4 tangent discontinuities per wrap at
# the flat/semicircle boundaries) without over-smoothing the corners.
CURVE_FIT_N = 600


# ═══════════════════════════════════════════════════════
# RACETRACK BODY
# ═══════════════════════════════════════════════════════

def racetrack_solid(semi_r, flat_len, z_bot, z_top):
    """Solid racetrack (stadium) prism.  Long axis along X."""
    return (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, z_bot))
        .slot2D(flat_len + 2 * semi_r, 2 * semi_r)
        .extrude(z_top - z_bot)
    )


# ═══════════════════════════════════════════════════════
# RACETRACK PERIMETER PARAMETRIZATION
# ═══════════════════════════════════════════════════════
#
# perimeter_xy(s) maps a normalized arc-length parameter s ∈ [0, 1)
# to an (x, y) point on the racetrack perimeter at radius SEMI_R.
#
# Zones (in order of increasing s):
#   A: top flat     — (+HALF_FLAT, +SEMI_R) -> (-HALF_FLAT, +SEMI_R)
#   B: left semi    — angle +90° around (-HALF_FLAT, 0) to -90°
#   C: bottom flat  — (-HALF_FLAT, -SEMI_R) -> (+HALF_FLAT, -SEMI_R)
#   D: right semi   — angle -90° around (+HALF_FLAT, 0) to +90°

HALF_FLAT     = FLAT_LEN / 2
ARC_LEN_SEMI  = math.pi * SEMI_R
PERIMETER     = 2 * FLAT_LEN + 2 * ARC_LEN_SEMI

S_A_END = FLAT_LEN / PERIMETER
S_B_END = (FLAT_LEN + ARC_LEN_SEMI) / PERIMETER
S_C_END = (2 * FLAT_LEN + ARC_LEN_SEMI) / PERIMETER
# S_D_END == 1.0


def perimeter_xy(s):
    """(x, y) on the racetrack perimeter at radius SEMI_R.

    s is a fractional arc-length parameter in [0, 1); s=0 starts at
    (+HALF_FLAT, +SEMI_R) and walks counterclockwise when viewed from +Z.
    """
    s = s % 1.0
    arc = s * PERIMETER

    if s < S_A_END:
        # Zone A: top flat, +X -> -X at y = +SEMI_R
        x = HALF_FLAT - arc
        y = SEMI_R
        return x, y

    if s < S_B_END:
        # Zone B: left semicircle, centered at (-HALF_FLAT, 0)
        local_arc = arc - FLAT_LEN
        theta = math.pi / 2 + local_arc / SEMI_R   # +90° -> +270° (= -90°)
        x = -HALF_FLAT + SEMI_R * math.cos(theta)
        y = SEMI_R * math.sin(theta)
        return x, y

    if s < S_C_END:
        # Zone C: bottom flat, -X -> +X at y = -SEMI_R
        local_arc = arc - (FLAT_LEN + ARC_LEN_SEMI)
        x = -HALF_FLAT + local_arc
        y = -SEMI_R
        return x, y

    # Zone D: right semicircle, centered at (+HALF_FLAT, 0)
    local_arc = arc - (2 * FLAT_LEN + ARC_LEN_SEMI)
    theta = -math.pi / 2 + local_arc / SEMI_R     # -90° -> +90°
    x = HALF_FLAT + SEMI_R * math.cos(theta)
    y = SEMI_R * math.sin(theta)
    return x, y


# ═══════════════════════════════════════════════════════
# HELICAL GROOVE PATH
# ═══════════════════════════════════════════════════════

def helix_point(t_wraps):
    """(x, y, z) point on the helical groove centerline.

    t_wraps ∈ [0, NUM_WRAPS]; integer part picks the wrap, fractional
    part picks the angular position around the racetrack.
    """
    s = t_wraps - math.floor(t_wraps)       # fractional part, [0, 1)
    x, y = perimeter_xy(s)
    z = Z_GROOVE_START + t_wraps * PITCH
    return x, y, z


def build_helical_groove_cut():
    """Sweep a circular cross-section along the racetrack-helix path.

    Builds a single smooth B-spline path via parametricCurve — the
    curve is fit from CURVE_FIT_N samples and represented in the STEP
    output as one continuous NURBS curve, yielding a single NURBS tube
    surface when swept.  Contrast with a polyline sweep, which produces
    one planar face segment per polyline edge and bloats the STEP by
    ~500x for a curve of this resolution.
    """
    # Smooth parametric path: maps t ∈ [0, 1] to the helix at 0..NUM_WRAPS.
    def path_func(t):
        return helix_point(t * NUM_WRAPS)

    path = cq.Workplane("XY").parametricCurve(path_func, N=CURVE_FIT_N)

    # Sweep profile: circle of TUBE_RAD, perpendicular to the initial
    # path tangent.  The groove cuts a semicircular channel of depth
    # TUBE_RAD into the racetrack surface (the inner half of the swept
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

    profile = (
        cq.Workplane(profile_plane)
        .circle(TUBE_RAD)
    )

    swept = profile.sweep(path)
    return swept


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def build_mandrel():
    body  = racetrack_solid(SEMI_R, FLAT_LEN, 0, TOTAL_LEN)
    groove = build_helical_groove_cut()
    # Skip clean() — the helical sweep's sampled polyline produces a
    # high face count that trips OCCT's shape-upgrader on the result.
    cut_body = body.cut(groove, clean=False)

    # Restore clean handle zones.  The helical sweep profile (circle of
    # radius TUBE_RAD) bleeds slightly past Z_GROOVE_START and Z_GROOVE_END
    # into the handle zones.  Union the original handle racetrack solids
    # back on top to fill in any bleed, leaving the handle zones smooth.
    lower_handle = racetrack_solid(SEMI_R, FLAT_LEN, 0, HANDLE_LEN)
    upper_handle = racetrack_solid(SEMI_R, FLAT_LEN,
                                   HANDLE_LEN + WIND_LEN, TOTAL_LEN)
    return (cut_body
            .union(lower_handle, clean=False)
            .union(upper_handle, clean=False))


mandrel = build_mandrel()

solids = mandrel.solids().vals()
print(f"Mandrel: {len(solids)} solid(s)")
for i, s in enumerate(solids):
    bb = s.BoundingBox()
    print(f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
          f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")

out_dir = Path(__file__).resolve().parent
out_path = out_dir / "coil-mandrel.step"
cq.exporters.export(mandrel, str(out_path))
print(f"\nExported: {out_path}")
