"""Reservoir corner supports — teardrop posts at the bag-pocket corners.

Each support is a vertical post rising from the bag-pocket floor (z=0,
fusing with the outer-shell floor) to the reservoir's flat exterior floor
bottom. At a far-+X corner the post is a cylinder sized to the pocket
inner-corner fillet (radius bag_pocket_corner_inner_radius), seated on the
fillet center so its arc is coincident with the rounded corner and tangent
to both pocket inner faces, webbed to the two flanking walls by the two
square-corner regions beside the corner (the "teardrop"). The diagonal
region faces open pocket interior and is clear.

Eight posts: the four corners of the +X pocket plus the four of the −X
pocket (a mirror of the +X set across YZ). Each pocket has two far-+X
corners (teardrops) and two centerward corners. The centerward wall is a
curved tank-wrapping arc with no fillet to nest, so those posts are clip
cylinders intersected with the pocket cavity, conforming to both the ±Y
wall and the curved centerward wall.

Post tops meet the reservoir's flat exterior floor bottom
(floor_flat_bottom_z), the flat underside the reservoir rests on."""

import sys
from pathlib import Path

import cadquery as cq
from world_workplane import xy_plane_z_up

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))
sys.path.insert(0, str(_here / "reservoir"))

import reservoir as _R
import _cold_core_interface as _I
import _reservoir_pocket_walls as _PW

support_radius = _I.bag_pocket_corner_inner_radius

# Fillet-center X of the far-+X corners, shared by both ±Y posts.
_cx = _I.bag_pocket_far_inner_x - support_radius

# Centerward-corner clip cylinder, centered under the reservoir's
# curve-corner. Radius reaches past both walls and back to the corner vertex
# so the fill spans the corner.
centerward_clip_radius = 10.0

# Horizontal plane the reservoir rests on; posts build past it, then cut
# flat to it.
_flat_bottom_z = _R.floor_flat_bottom_z
_build_top_z = _flat_bottom_z + 2.0


def _above_flat_bottom():
    """Solid filling everything above the reservoir's flat exterior floor
    bottom (a horizontal plane at _flat_bottom_z)."""
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=_flat_bottom_z)
        .rect(4000, 4000)
        .extrude(1000)
    )


def _corner_teardrop(y_sign):
    """Teardrop post at the far-+X × (y_sign·Y) pocket corner: corner
    cylinder plus the two webs against the +X and ±Y walls, rising to the
    reservoir floor underside."""
    cy = y_sign * (_I.bag_pocket_y_inner_max - support_radius)
    top_z = _build_top_z

    post = _R._z_cylinder((_cx, cy), (0.0, top_z), 2 * support_radius).unwrap()
    # Web against the +X wall (right edge at the +X inner face), below the
    # pocket corner.
    post = post.union(
        _I.make_box((_cx, _cx + support_radius), (cy, cy - y_sign * support_radius), (0.0, top_z))
    )
    # Web against the ±Y wall (outer edge at the ±Y inner face), inboard of
    # the pocket corner.
    post = post.union(
        _I.make_box((_cx - support_radius, _cx), (cy, cy + y_sign * support_radius), (0.0, top_z))
    )
    return post


def _centerward_teardrop(y_sign):
    """Fill at the centerward × (y_sign·Y) pocket corner — the junction
    where the ±Y wall meets the curved tank-wrapping wall. A clip cylinder
    seated under the reservoir's curve-corner, intersected with the pocket
    cavity, conforming to the flat ±Y face and the curved centerward
    face."""
    cx, cy = _R.insert_positions_for_side_plus_1[3 if y_sign > 0 else 4]
    top_z = _build_top_z
    clip = _R._z_cylinder((cx, cy), (0.0, top_z), 2 * centerward_clip_radius).unwrap()
    return clip.intersect(_PW.build_plus_x_cavity(top_z).unwrap())


def build_reservoir_supports():
    """All eight pocket-corner posts: the four +X-pocket corners plus the
    four −X-pocket corners (mirror across YZ), tops flat at the reservoir's
    flat exterior floor bottom."""
    plus_x = (
        _corner_teardrop(-1)
        .union(_corner_teardrop(+1))
        .union(_centerward_teardrop(-1))
        .union(_centerward_teardrop(+1))
    )
    supports = plus_x.union(plus_x.mirror("YZ"))
    return supports.cut(_above_flat_bottom())
