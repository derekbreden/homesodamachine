"""SVG path construction for colored markings on the enclosure.

The line-art SVG is produced by CadQuery's HLR (vector edges only). To
get FILLED colored regions in the same SVG, we compute the projected 2D
shapes analytically from the same 3D geometry HLR runs on, and emit
them as `<path fill=...>` regions clipped against the projected
silhouettes of features that occlude them.

Coordinate system here is the SVG "inner coords" — the local frame
inside the outer `<g transform="scale(s, -s) translate(...)">` block
that cq.exporters.export wraps the line art in. The y-flip in that
transform means inner coords are y-up.

Projection formulas in unrotated CAD coords (the model's natural frame,
+Y-up), derived empirically from box-corner mappings in the cq.exporters
output for each iso direction:

- iso-front (projectionDir=(1, 1, -1) on the rotated drawing frame):
    inner_x = (x + z) / sqrt(2)
    inner_y = (-x + 2y + z) / sqrt(6)
- iso-back (projectionDir=(1, -1, 1) on the rotated drawing frame):
    inner_x = (x - z) / sqrt(2)
    inner_y = (-x + 2y - z) / sqrt(6)
"""

import math
from typing import Tuple


def project_to_inner(world_xyz: Tuple[float, float, float], iso: str) -> Tuple[float, float]:
    """Project a CAD-frame world point to SVG inner coords."""
    x, y, z = world_xyz
    if iso == "front":
        return (x + z) / math.sqrt(2), (-x + 2 * y + z) / math.sqrt(6)
    if iso == "back":
        return (x - z) / math.sqrt(2), (-x + 2 * y - z) / math.sqrt(6)
    raise ValueError(f"unknown iso direction: {iso}")


# In both iso projections the cup axis is world +X. Its projection is a
# direction in inner-coord space:
#   iso-front:  (1/sqrt(2), -1/sqrt(6))   (magnitude sqrt(2/3))
#   iso-back:   (1/sqrt(2), -1/sqrt(6))   (same direction in this view)
# For a circle in world's YZ plane (perpendicular to the cup axis), the
# projection is an ellipse with semi-major r and semi-minor r/sqrt(3).
# Major axis direction in inner coords is perpendicular to the projected
# cup axis — at 60° from +inner_x for iso-front, 120° for iso-back.

ELLIPSE_MAJOR_DEG = {"front": 60.0, "back": 120.0}


def _project_yz_circle_point(
    iso: str, center_world: Tuple[float, float, float], radius: float, angle_rad: float
) -> Tuple[float, float]:
    """Project a point on a circle in the world's YZ plane (perpendicular
    to the cup axis) to inner SVG coords.

    The circle is centered at `center_world`, radius `radius`. The point
    is at `angle_rad` around the axis — 0 along +Y, π/2 along +Z.
    """
    cx, cy, cz = center_world
    y = cy + radius * math.cos(angle_rad)
    z = cz + radius * math.sin(angle_rad)
    return project_to_inner((cx, y, z), iso)


def _ellipse_arc_polyline(
    iso: str,
    center_world: Tuple[float, float, float],
    radius: float,
    start_deg: float,
    sweep_deg: float,
    n_samples: int = 64,
) -> str:
    """Emit SVG `L` path commands sampling an arc of a YZ-plane circle.

    `start_deg` and `sweep_deg` are angles in the world's YZ plane
    (0° = +Y, 90° = +Z). The first sample is at `start_deg`; the last
    is at `start_deg + sweep_deg`. Returns "Lx,y Lx,y ..." (no leading
    Move, no trailing space) — the caller emits the opening M.
    """
    parts = []
    for i in range(1, n_samples + 1):
        a = math.radians(start_deg + sweep_deg * i / n_samples)
        ix, iy = _project_yz_circle_point(iso, center_world, radius, a)
        parts.append(f"L{ix:.4f},{iy:.4f}")
    return " ".join(parts)


def ring_annulus_path_d(
    iso: str,
    center_world: Tuple[float, float, float],
    r_outer: float,
    r_inner: float,
) -> str:
    """SVG path `d` for the filled annulus of a ring at `center_world` in
    the world's YZ plane. Uses fill-rule="evenodd" so the inner ellipse
    cuts a hole.
    """
    # Outer ellipse (full loop)
    start_o = _project_yz_circle_point(iso, center_world, r_outer, 0.0)
    outer = f"M{start_o[0]:.4f},{start_o[1]:.4f} " + _ellipse_arc_polyline(
        iso, center_world, r_outer, 0.0, 360.0
    ) + " Z"

    # Inner ellipse (reverse direction for evenodd hole)
    start_i = _project_yz_circle_point(iso, center_world, r_inner, 0.0)
    inner = f"M{start_i[0]:.4f},{start_i[1]:.4f} " + _ellipse_arc_polyline(
        iso, center_world, r_inner, 0.0, -360.0
    ) + " Z"

    return outer + " " + inner


def cup_silhouette_path_d(
    iso: str,
    center_world: Tuple[float, float, float],
    cup_length: float,
    cup_radius: float,
) -> str:
    """SVG path `d` for the projected silhouette of a finite cylinder
    along world +X. `center_world` is the back cap center (at x=W); the
    front cap is at +cup_length along world +X.

    Silhouette = back cap "outer" half + tangent line + front cap "outer"
    half + tangent line, traced as a closed loop.

    The "outer" half of each cap is the half facing away from the other
    cap in projection. For a +X axis cylinder in either iso projection,
    the tangent angles (in YZ plane around the axis, 0°=+Y, 90°=+Z) are
    found by surface_normal · projection_dir = 0; for both iso views
    that lands at YZ angles 135° and 315° on the cap.
    """
    cx, cy, cz = center_world
    L = cup_length
    r = cup_radius
    front_center = (cx + L, cy, cz)

    # YZ-plane angles where the cylinder's surface normal is perpendicular
    # to the view direction. Surface normal at YZ angle a is (0, cos a,
    # sin a). The projection direction in world coords for each iso
    # (after the linter's rotation is unwound):
    #   iso-front: (1, 1, -1) on rotated frame  ⇒ in world  (1, 1, 1)/√3
    #     (rotation +90° around +X sends y→-z, z→y, so projection_dir
    #     rotates as (1, 1, -1)_rot → (1, -1, 1)_world? Quick check:
    #     plug y=0,z=0 into formulas → matches y=0 on the cup axis)
    # The math collapses: cos a + sin a = 0 for iso-front, cos a - sin a
    # = 0 for iso-back, so:
    if iso == "front":
        tangent_a_deg = 135.0
        tangent_b_deg = 315.0
    elif iso == "back":
        tangent_a_deg = 45.0
        tangent_b_deg = 225.0
    else:
        raise ValueError(f"unknown iso direction: {iso}")

    # The "outer" arc of each cap sweeps 180° from one tangent to the
    # other. Which 180° depends on which side faces away from the cup
    # axis projection — for both iso views the cup projects so the
    # front cap sits down-and-right of the back cap in inner coords;
    # the back cap's outer half is up-and-left, the front cap's is
    # down-and-right.
    #
    # In YZ angle terms, the outer-half centerline for the back cap is
    # at the YZ angle that maps to the outer projected direction. We
    # don't need to know it exactly — empirically the back cap's outer
    # arc sweeps from tangent_a -> tangent_b going through the angles
    # NOT crossing the cup axis projection. Pick sweep direction by
    # trying both at render time and verifying.
    back_sweep = -180.0  # CW in YZ-angle terms
    front_sweep = 180.0  # CCW

    back_start = _project_yz_circle_point(iso, center_world, r, math.radians(tangent_a_deg))
    back_end = _project_yz_circle_point(iso, center_world, r, math.radians(tangent_a_deg + back_sweep))
    front_start = _project_yz_circle_point(iso, front_center, r, math.radians(tangent_a_deg + back_sweep))
    front_end = _project_yz_circle_point(iso, front_center, r, math.radians(tangent_a_deg + back_sweep + front_sweep))

    parts = [f"M{back_start[0]:.4f},{back_start[1]:.4f}"]
    parts.append(_ellipse_arc_polyline(iso, center_world, r, tangent_a_deg, back_sweep))
    parts.append(f"L{front_start[0]:.4f},{front_start[1]:.4f}")
    parts.append(_ellipse_arc_polyline(iso, front_center, r, tangent_a_deg + back_sweep, front_sweep))
    parts.append(f"L{back_start[0]:.4f},{back_start[1]:.4f}")
    parts.append("Z")
    return " ".join(parts)
