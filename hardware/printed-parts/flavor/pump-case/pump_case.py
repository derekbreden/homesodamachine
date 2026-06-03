"""Pump case — two-piece enclosure for a peristaltic pump.

Base: base plate with octagon-to-footprint ramp, octagon pump bore,
      a cylindrical tower below, and a pogo connector pocket.
Cap:  asymmetric flared skirt (wide on +Y, narrow on -Y) with a lower
      extension that tapers to uniform width.

The two parts mate at a stepped split surface and lock together with
snap-fit ramps on four interior walls.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from world_workplane import WorldWorkplane, xy_plane_z_up, xz_plane_y_up
from snap import Frame, apply_ramp_out_first, apply_ramp_in_first
from _cadq_export import export_step
from docgen import substitute_py_comments


# Physical dimensions
footprint_x = 70.0
footprint_y = 70.0
corner_r = 6.0
wall_thickness = 3.0

center_x = footprint_x / 2
center_y = footprint_y / 2
footprint_half_extent = footprint_x / 2

base_thickness = 3.0
ramp_from_skirt_to_octagon_height = 18.0

# Skirt
skirt_upper_height = 21.0
skirt_wall = wall_thickness
skirt_wide_flare_per_side = 3.0
skirt_narrow_taper_per_side = 4.0
skirt_wide_straight_height = 4.5

# Pump bore
bore_square_side = 43.0
ledge_depth = 1.5
ledge_shelf_span = 26.03

bore_half_diag = bore_square_side * math.sqrt(2) / 2
bore_half_span = 53.0 / 2

vertex_far = bore_half_span
vertex_near = bore_half_diag - bore_half_span

# Tower
tower_height = 60.0
tower_cap_thickness = 3.0
cylinder_id = 37.0
cylinder_r_inner = cylinder_id / 2

# Lower extension
lower_height = 23.0
lower_cap_thickness = 3.0
lower_footprint_straight = skirt_wide_straight_height

# Stepped split
step_height = 19.0
step_y_clearance = 6.0

# Snap fits
snap_zone_width = 20.0
snap_wall_height = 9.0
snap_deflection = 1.0

# Arch notches
arch_radius = 4.5

# Pogo connector
pogo_outer_length = 12.7
pogo_outer_width = 4.2
pogo_outer_depth = 1.0
pogo_inner_length = 14.7
pogo_inner_width = 4.2
pogo_z_offset = 13.5
pogo_ridge_length = 24.5
pogo_ridge_width = 10.0
pogo_ridge_depth = 0.7  # outer-wall thickness the pogo pins protrude through


# Outer envelope of the assembled case, including the snaps, tubes, and
# pogo that protrude past the bare base/cap solids.

# Snap protrudes past the footprint; silicone tubes extend past the case body.
snap_protrusion_per_side = 2.5
tube_protrusion_length = 11.3

# [75.0 mm](CASE_OUTER_X) is the full width of the assembled case
case_outer_x = footprint_x + 2 * snap_protrusion_per_side

# [88.0 mm](CASE_OUTER_Y) is the full depth of the assembled case, with the protruding tubes included
case_outer_y = (footprint_y + 2 * skirt_wide_flare_per_side
                + pogo_ridge_depth + tube_protrusion_length)

# [135.5 mm](CASE_OUTER_Z) is the full height of the assembled case
case_outer_z = (base_thickness + ramp_from_skirt_to_octagon_height + tower_height
                + skirt_upper_height + skirt_wide_flare_per_side
                + skirt_wide_straight_height + lower_height + lower_cap_thickness)

# Half-extent of the stepped-split cutter slab.  Exceeds the case's X and
# Y footprint half-extents so the cut pierces through to free air on every
# side.
cutter_half_extent = max(case_outer_x, case_outer_y) / 2 + 5.0


# Slop added to cut depths so they pierce cleanly through sibling solid
# boundaries.
overcut = 0.1
# Polygonization count per quarter-circle for round-corner profiles.
arc_segments = 8


# Coordinate convention
# ---------------------
# Every `_y` and `_z` in this file is a signed world coordinate.
# Distances/heights/thicknesses are unsigned magnitudes.
#
# Origin is at the center of the case footprint, on the bore-opening
# face of the base plate.  +Z points toward the tower (away from the
# cap); -Z points toward the skirt top (toward the cap).  Construction
# uses the following cross-section levels:
#
#   z = [+81 mm](CYLINDER_BOTTOM_Z) — tower cylinder's far face
#   z = [+21 mm](BORE_BOTTOM_Z) — bore wall's far face (octagonal bore cavity ends here)
#   z = [+8 mm](CYLINDER_TOP_Z) — tower cylinder's near face
#   z = [+3 mm](BASE_PLATE_FAR_Z) — base plate's far face
#   z = 0 — base plate's bore-opening face — origin
#   z = [-9.5 mm](NARROW_SPLIT_Z) — narrow-half cap-side step (the stepped split)
#   z = [-28.5 mm](SKIRT_BOTTOM_Z) — skirt's wide-half mating edge with the cap
#   z = [-51.5 mm](LOWER_CAP_TOP_Z) — lower cap's interior face (cavity ends here)
#   z = [-54.5 mm](LOWER_CAP_BOTTOM_Z) — lower cap's exterior face (case's far end)

octagon_wall_outer_extent = vertex_far + wall_thickness

bore_depth = base_thickness + ramp_from_skirt_to_octagon_height
bore_bottom_z = bore_depth  # [+21 mm](BORE_BOTTOM_Z)

# Inward step from the cylinder to the octagonal bore wall at the
# cardinals.
cylinder_cardinal_step = 0.5
cylinder_r_outer = octagon_wall_outer_extent + cylinder_cardinal_step

# Cylinder's top Z, where its top edge is tangent to the base-plate
# ramp at the cardinals.
cylinder_top_z = footprint_half_extent + base_thickness - cylinder_r_outer  # [+8 mm](CYLINDER_TOP_Z)
cylinder_bottom_z = bore_bottom_z + tower_height  # [+81 mm](CYLINDER_BOTTOM_Z)


# Polygon generators

class Turtle:
    """Logo-style turtle that accumulates (x, y) polygon points."""

    def __init__(self, x, y, heading_deg):
        self.x = x
        self.y = y
        self.heading = math.radians(heading_deg)
        self.points = []

    def forward(self, dist):
        self.x += dist * math.cos(self.heading)
        self.y += dist * math.sin(self.heading)
        self.points.append((self.x, self.y))

    def left(self, deg):
        self.heading += math.radians(deg)

    def right(self, deg):
        self.heading -= math.radians(deg)


def bore_octagon_profile():
    """Pump bore octagon with ledge indentations, centered at origin."""
    vf = vertex_far
    vn = vertex_near

    vertices = [
        (vn, vf), (vf, vn), (vf, -vn), (vn, -vf),
        (-vn, -vf), (-vf, -vn), (-vf, vn), (-vn, vf),
    ]
    long_edge_indices = {0, 2, 4, 6}

    pts = []
    for i in range(8):
        start_x, start_y = vertices[i]
        end_x, end_y = vertices[(i + 1) % 8]
        pts.append((start_x, start_y))

        if i not in long_edge_indices:
            continue

        edge_dx, edge_dy = end_x - start_x, end_y - start_y
        edge_length = math.hypot(edge_dx, edge_dy)
        edge_heading = math.degrees(math.atan2(edge_dy, edge_dx))

        mid_x, mid_y = (start_x + end_x) / 2, (start_y + end_y) / 2
        unit_x, unit_y = edge_dx / edge_length, edge_dy / edge_length
        normal_x, normal_y = unit_y, -unit_x
        if normal_x * (-mid_x) + normal_y * (-mid_y) < 0:
            normal_x, normal_y = -normal_x, -normal_y
        inward_is_left = (normal_x * (-unit_y) + normal_y * unit_x) > 0

        ledge_ramp_length = ledge_depth * math.sqrt(2)
        entry_length = (edge_length - ledge_shelf_span) / 2
        shelf_length = ledge_shelf_span - 2 * ledge_depth

        t = Turtle(start_x, start_y, edge_heading)
        t.forward(entry_length)
        if inward_is_left:
            t.left(45); t.forward(ledge_ramp_length); t.right(45)
            t.forward(shelf_length)
            t.right(45); t.forward(ledge_ramp_length); t.left(45)
        else:
            t.right(45); t.forward(ledge_ramp_length); t.left(45)
            t.forward(shelf_length)
            t.left(45); t.forward(ledge_ramp_length); t.right(45)
        t.forward(entry_length)

        pts.extend(t.points[:-1])

    return pts


def offset_polygon(pts, distance):
    """Offset each edge of a closed polygon outward by distance."""
    n = len(pts)

    edges = []
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        nx, ny = -dy / length, dx / length
        edges.append((dx, dy, nx, ny))

    result = []
    for i in range(n):
        prev = (i - 1) % n
        ax = pts[prev][0] + distance * edges[prev][2]
        ay = pts[prev][1] + distance * edges[prev][3]
        adx, ady = edges[prev][0], edges[prev][1]

        bx = pts[i][0] + distance * edges[i][2]
        by = pts[i][1] + distance * edges[i][3]
        bdx, bdy = edges[i][0], edges[i][1]

        det = adx * bdy - ady * bdx
        if abs(det) < 1e-10:
            result.append((bx, by))
        else:
            t = ((bx - ax) * bdy - (by - ay) * bdx) / det
            result.append((ax + t * adx, ay + t * ady))

    return result


def rounded_rect_profile(width, height, radius, n=arc_segments):
    """Polygon points for a rounded rectangle centered at origin."""
    hw, hh = width / 2, height / 2
    pts = []
    corners = [
        (hw - radius, hh - radius, 0, 90),
        (-hw + radius, hh - radius, 90, 180),
        (-hw + radius, -hh + radius, 180, 270),
        (hw - radius, -hh + radius, 270, 360),
    ]
    for cx, cy, start_deg, end_deg in corners:
        for i in range(n + 1):
            angle = math.radians(start_deg + (end_deg - start_deg) * i / n)
            pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return pts


def split_skirt_profile(wide_half_extent, wide_radius,
                        narrow_half_extent, narrow_radius,
                        transition_y_plus=None, transition_y_minus=None,
                        wide_half_extent_y=None, narrow_half_extent_y=None,
                        n=arc_segments):
    """Asymmetric profile: wider on +Y, narrower on -Y, with diagonal transitions."""
    wide_radius = max(wide_radius, 0.01)
    narrow_radius = max(narrow_radius, 0.01)
    if wide_half_extent_y is None:
        wide_half_extent_y = wide_half_extent
    if narrow_half_extent_y is None:
        narrow_half_extent_y = narrow_half_extent
    wide_corner_center_x = wide_half_extent - wide_radius
    wide_corner_center_y = wide_half_extent_y - wide_radius
    narrow_corner_center_x = narrow_half_extent - narrow_radius
    narrow_corner_center_y = narrow_half_extent_y - narrow_radius

    if transition_y_plus is None:
        transition_y_plus = max((wide_half_extent - narrow_half_extent) / 2, 0.01)
    if transition_y_minus is None:
        transition_y_minus = -transition_y_plus

    pts = []

    for i in range(n + 1):
        a = math.radians(90 * i / n)
        pts.append((wide_corner_center_x + wide_radius * math.cos(a),
                    wide_corner_center_y + wide_radius * math.sin(a)))
    for i in range(n + 1):
        a = math.radians(90 + 90 * i / n)
        pts.append((-wide_corner_center_x + wide_radius * math.cos(a),
                    wide_corner_center_y + wide_radius * math.sin(a)))

    pts.append((-wide_half_extent, transition_y_plus))
    pts.append((-narrow_half_extent, transition_y_minus))

    for i in range(n + 1):
        a = math.radians(180 + 90 * i / n)
        pts.append((-narrow_corner_center_x + narrow_radius * math.cos(a),
                    -narrow_corner_center_y + narrow_radius * math.sin(a)))
    for i in range(n + 1):
        a = math.radians(270 + 90 * i / n)
        pts.append((narrow_corner_center_x + narrow_radius * math.cos(a),
                    -narrow_corner_center_y + narrow_radius * math.sin(a)))

    pts.append((narrow_half_extent, transition_y_minus))
    pts.append((wide_half_extent, transition_y_plus))

    return pts


# Bore profiles (shared by bore construction and tower)
bore_profile = bore_octagon_profile()
bore_wall_profile = offset_polygon(bore_profile, wall_thickness)


# Skirt profiles (shared by skirt, lower extension, the split, and snap fits).
#
# The skirt splits asymmetrically: +Y half flares outward ([70](FOOTPRINT_X)→[76](SKIRT_WIDE_WIDTH)), -Y half
# tapers inward ([70](FOOTPRINT_X)→[62](SKIRT_NARROW_WIDTH)). Both flares are at 45 degrees. The transition wall
# stays in a fixed vertical plane by tracking each endpoint's Y independently.
# The same profile set is used by the outer skirt surface and (shrunk by
# skirt_wall) by the inner cavity.

skirt_base_half_extent = footprint_half_extent
skirt_wide_half_extent = skirt_base_half_extent + skirt_wide_flare_per_side
skirt_narrow_half_extent = skirt_base_half_extent - skirt_narrow_taper_per_side
skirt_wide_full_width = 2 * skirt_wide_half_extent
skirt_narrow_full_width = 2 * skirt_narrow_half_extent
# At the moment the wide flare completes ([3mm](SKIRT_WIDE_FLARE)), the narrow side
# has only tapered by [3mm](SKIRT_WIDE_FLARE) of its [4mm](SKIRT_NARROW_TAPER).
skirt_mid_narrow_half_extent = skirt_base_half_extent - skirt_wide_flare_per_side

# Both skirt halves terminate at skirt_bottom_z; the narrow side's deeper
# taper leaves it a correspondingly shorter straight section.
skirt_narrow_straight_height = (
    skirt_wide_straight_height
    - (skirt_narrow_taper_per_side - skirt_wide_flare_per_side)
)

# Transition Y coordinates (the +/- Y endpoints of the diagonal seam wall
# at each profile's Z level). They keep the seam wall in the vertical
# plane X + Y = -skirt_base_half_extent at every Z as the +Y half flares
# and the -Y half tapers at different rates.
skirt_transition_y_symmetric = (0.01, -0.01)
skirt_transition_y_mid = (skirt_wide_flare_per_side, -skirt_wide_flare_per_side)
skirt_transition_y_end = (skirt_wide_flare_per_side, -skirt_narrow_taper_per_side)
skirt_transition_y_end_plus = skirt_transition_y_end[0]

# Signed world-Z deltas between the five skirt cross-section levels.
# Each entry is negative because the skirt grows from z=0 (base plate)
# toward more negative Z (away from the bore, toward the cap).
skirt_z_steps = [
    -skirt_upper_height,
    -skirt_wide_flare_per_side,
    -(skirt_narrow_taper_per_side - skirt_wide_flare_per_side),
    -skirt_narrow_straight_height,
]
skirt_bottom_z = sum(skirt_z_steps)  # [-28.5 mm](SKIRT_BOTTOM_Z), case's wide-half mating edge with the cap

# Z level of the cap-side stepped split — narrow half (-Y) meets the cap
# step_height higher into the skirt than the wide half (+Y).
narrow_split_z = skirt_bottom_z + step_height  # [-9.5 mm](NARROW_SPLIT_Z)

# Lower cap Z anchors. The lower extension is a hollow shell from
# skirt_bottom_z to lower_cap_top_z; the closing wall (the "lower cap")
# fills lower_cap_top_z..lower_cap_bottom_z. lower_cap_bottom_z is the
# case's outermost face on the -Z end.
lower_cap_top_z = skirt_bottom_z - lower_height  # [-51.5 mm](LOWER_CAP_TOP_Z)
lower_cap_bottom_z = lower_cap_top_z - lower_cap_thickness  # [-54.5 mm](LOWER_CAP_BOTTOM_Z)

# World Y of the case's +Y outer face.
pos_y_face_y = center_y + footprint_half_extent


def _skirt_profile_set(wall_offset):
    """Five skirt cross-section profiles, top-of-skirt to bottom-of-skirt."""
    # Shift of the transition Y values that holds the inner seam plane a full
    # perpendicular wall_offset inward from the outer, the seam at 45 deg in XY.
    seam_y_shift = wall_offset * (math.sqrt(2) - 1)

    base_he = skirt_base_half_extent - wall_offset
    wide_he = skirt_wide_half_extent - wall_offset
    narrow_he = skirt_narrow_half_extent - wall_offset
    mid_narrow_he = skirt_mid_narrow_half_extent - wall_offset
    radius = corner_r - wall_offset

    ty_symmetric_plus, ty_symmetric_minus = skirt_transition_y_symmetric
    ty_mid_plus = skirt_transition_y_mid[0] + seam_y_shift
    ty_mid_minus = skirt_transition_y_mid[1] + seam_y_shift
    ty_end_plus = skirt_transition_y_end[0] + seam_y_shift
    ty_end_minus = skirt_transition_y_end[1] + seam_y_shift

    symmetric = split_skirt_profile(
        base_he, radius, base_he, radius,
        ty_symmetric_plus, ty_symmetric_minus,
    )
    mid = split_skirt_profile(
        wide_he, radius, mid_narrow_he, radius,
        ty_mid_plus, ty_mid_minus,
        wide_half_extent_y=base_he, narrow_half_extent_y=base_he,
    )
    end = split_skirt_profile(
        wide_he, radius, narrow_he, radius,
        ty_end_plus, ty_end_minus,
        wide_half_extent_y=base_he, narrow_half_extent_y=base_he,
    )
    return [symmetric, symmetric, mid, end, end]


skirt_outer_profiles = _skirt_profile_set(0)
skirt_inner_profiles = _skirt_profile_set(skirt_wall)


def build_base_plate_with_ramp():
    """Base plate (z=0..+3) plus the 45° ramp (z=+3..+21) shrinking from
    the 70x70 footprint to a 34x34 footprint that meets the octagon bore wall."""
    footprint = rounded_rect_profile(footprint_x, footprint_y, corner_r)
    footprint_at_ramp_bottom = rounded_rect_profile(
        footprint_x - 2 * ramp_from_skirt_to_octagon_height,
        footprint_y - 2 * ramp_from_skirt_to_octagon_height,
        corner_r)

    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .center(center_x, center_y)
        .polyline(footprint).close()
        .workplane(offset=base_thickness)
        .polyline(footprint).close()
        .workplane(offset=ramp_from_skirt_to_octagon_height)
        .polyline(footprint_at_ramp_bottom).close()
        .loft(ruled=True)
    )


def add_bore_wall(solid):
    """Octagonal bore wall around the pump-flange seat, unioned onto solid."""
    bore_wall = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .center(center_x, center_y)
        .polyline(bore_wall_profile).close()
        .extrude(bore_depth)
    )
    return solid.union(bore_wall)


def cut_bore_cavity(solid):
    """Octagonal pump-flange seat (with ledges) cut through the bore wall
    and the tower cylinder material overlapping the bore-wall region."""
    bore_cavity = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .center(center_x, center_y)
        .polyline(bore_profile).close()
        .extrude(bore_depth + overcut)
    )
    return solid.cut(bore_cavity)


def loft_profile_stack(start_world_z, z_steps, profiles, overcut_last_step=False):
    """Loft a stack of profiles at successive world-Z levels.

    start_world_z: world Z of the first profile.
    z_steps: signed world-Z deltas between consecutive profiles.
    overcut_last_step: extend the last delta by overcut in the same
        direction as the loft's travel, so a cut profile pierces cleanly
        through a sibling solid boundary.
    """
    wp = (WorldWorkplane(xy_plane_z_up)
          .workplane(offset=start_world_z)
          .center(center_x, center_y)
          .polyline(profiles[0]).close())
    for i, (step, profile) in enumerate(zip(z_steps, profiles[1:])):
        is_last = i == len(z_steps) - 1
        extra = math.copysign(overcut, step) if (overcut_last_step and is_last) else 0
        wp = wp.workplane(offset=step + extra).polyline(profile).close()
    return wp.loft(ruled=True)


def build_skirt():
    """Asymmetric flared skirt: wide on +Y, narrow on -Y."""
    skirt_outer = loft_profile_stack(0, skirt_z_steps, skirt_outer_profiles)
    skirt_cavity = loft_profile_stack(0, skirt_z_steps, skirt_inner_profiles, overcut_last_step=True)
    return skirt_outer.cut(skirt_cavity)


def build_tower():
    """Cylindrical tower extending downward from cylinder_top_z. Its outer
    radius circumscribes the octagonal bore wall, overlapping it on the
    outside from above the bore wall's far face."""
    tower_cylinder = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=cylinder_top_z)
        .center(center_x, center_y)
        .circle(cylinder_r_outer)
        .extrude(cylinder_bottom_z - cylinder_top_z)
    )

    tower_bore_depth = tower_height - tower_cap_thickness
    tower_bore = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=bore_bottom_z - overcut)
        .center(center_x, center_y)
        .circle(cylinder_r_inner)
        .extrude(tower_bore_depth + overcut)
    )
    return tower_cylinder.cut(tower_bore)


def _lower_profile_set(wall_offset):
    """Four lower-extension cross-section profiles, top to bottom of lower section."""
    narrow_he = skirt_narrow_half_extent - wall_offset
    base_he = skirt_base_half_extent - wall_offset
    radius = corner_r - wall_offset
    narrow_symmetric = split_skirt_profile(
        narrow_he, radius, narrow_he, radius,
        0.01, -0.01,
        wide_half_extent_y=base_he, narrow_half_extent_y=base_he,
    )
    top = _skirt_profile_set(wall_offset)[-1]
    return [top, top, narrow_symmetric, narrow_symmetric]


def build_lower_extension():
    """Lower portion extending from skirt bottom: taper to uniform, then cap."""
    lower_ramp_height = (skirt_base_half_extent + skirt_wide_flare_per_side
                         - skirt_narrow_half_extent)
    lower_uniform_straight = (lower_height - lower_ramp_height
                              - lower_footprint_straight)
    # Lower extension extends in -Z, away from the base plate.
    lower_z_steps = [-lower_footprint_straight, -lower_ramp_height,
                     -lower_uniform_straight]

    lower_outer_profiles = _lower_profile_set(0)
    lower_inner_profiles = _lower_profile_set(skirt_wall)

    lower_outer = loft_profile_stack(skirt_bottom_z, lower_z_steps, lower_outer_profiles)
    lower_inner = loft_profile_stack(skirt_bottom_z, lower_z_steps, lower_inner_profiles,
                                     overcut_last_step=True)
    lower_shell = lower_outer.cut(lower_inner)

    lower_cap = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=lower_cap_top_z)
        .center(center_x, center_y)
        .polyline(lower_outer_profiles[-1]).close()
        .extrude(-lower_cap_thickness)
    )
    return lower_shell.union(lower_cap)


def cut_arch_notches(combined):
    """Semicircular notches on the +Y face for wire routing."""
    arch_hole_xs = [
        corner_r + arch_radius - 4,
        footprint_x - corner_r - arch_radius + 4,
    ]
    arch_cut_depth = skirt_wall + wall_thickness
    for ax in arch_hole_xs:
        arch_cutter = (
            WorldWorkplane(xz_plane_y_up)
            .workplane(offset=pos_y_face_y + overcut)
            .center(ax, skirt_bottom_z)
            .circle(arch_radius)
            .extrude(-(arch_cut_depth + overcut))
        )
        combined = combined.cut(arch_cutter)
    return combined


def split_into_base_and_cap(combined):
    """Stepped split creating base (with tower) and cap (with lower extension).

    The two parts meet at two different Z levels:
      Wide half (+Y):   at skirt_bottom_z
      Narrow half (-Y): step_height higher into the skirt
    The boundary follows the seam diagonal.
    """
    lower_end_z = lower_cap_bottom_z - overcut

    full_slab = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=skirt_bottom_z)
        .center(center_x, center_y)
        .rect(2 * cutter_half_extent, 2 * cutter_half_extent)
        .extrude(lower_end_z - skirt_bottom_z)
    )

    step_y = skirt_transition_y_end_plus + step_y_clearance
    narrow_box = [
        (-cutter_half_extent, -cutter_half_extent),
        (cutter_half_extent, -cutter_half_extent),
        (cutter_half_extent, step_y + overcut),
        (-cutter_half_extent, step_y + overcut),
    ]
    narrow_step = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=narrow_split_z)
        .center(center_x, center_y)
        .polyline(narrow_box).close()
        .extrude(skirt_bottom_z - narrow_split_z)
    )

    step_cutter = full_slab.union(narrow_step)

    base = combined.cut(step_cutter)
    cap = combined.intersect(step_cutter)
    return base, cap


def add_snap_fits(base, cap):
    """Snap-fit ramps on four interior walls where base meets cap.

    The base wall grows a ramp_out_first zigzag; the cap wall grows the
    complementary ramp_in_first zigzag. The two interleave across the split,
    their tips reaching past the mating plane to wrap around each other and
    lock the halves together — the solids slide past without interpenetrating.

    Each snap grows along Z from its split plane. The +Y wide-split snap sits
    on the flared face; the -Y, +X, -X snaps sit on the narrow-split faces.
    """
    snap_plus_y_inner = pos_y_face_y - wall_thickness
    snap_minus_y_inner = center_y - footprint_half_extent + wall_thickness
    snap_plus_x_inner = center_x + footprint_half_extent - wall_thickness
    snap_minus_x_inner = center_x - footprint_half_extent + wall_thickness

    # ±Y snaps extrude along X (plane YZ, +X normal); zone spans X about center.
    yz_zone_range = (center_x - snap_zone_width / 2, center_x + snap_zone_width / 2)
    # ±X snaps extrude along Y (plane ZX, +Y normal); zone spans Y from just
    # inside the narrow-face corner.
    zx_zone_start = center_y - skirt_narrow_half_extent + corner_r + 0.5
    zx_zone_range = (zx_zone_start, zx_zone_start + snap_zone_width)

    snap_faces = [
        (snap_plus_y_inner, +1, skirt_bottom_z, "YZ", yz_zone_range),
        (snap_minus_y_inner, -1, narrow_split_z, "YZ", yz_zone_range),
        (snap_plus_x_inner, +1, narrow_split_z, "ZX", zx_zone_range),
        (snap_minus_x_inner, -1, narrow_split_z, "ZX", zx_zone_range),
    ]

    for inner_face, sign, split_z, plane, zone_range in snap_faces:
        base_frame = Frame(extrusion_plane=plane, outward_sign=sign,
                           up_axis="Z", up_sign=-1)
        cap_frame = Frame(extrusion_plane=plane, outward_sign=sign,
                          up_axis="Z", up_sign=+1)
        base = apply_ramp_out_first(
            base,
            frame=base_frame,
            inner_wall_at=inner_face,
            wall_top_at=split_z,
            wall_height=snap_wall_height,
            zone_range=zone_range,
            deflection_distance=snap_deflection,
        )
        cap = apply_ramp_in_first(
            cap,
            frame=cap_frame,
            inner_wall_at=inner_face,
            wall_top_at=split_z,
            wall_height=snap_wall_height,
            zone_range=zone_range,
            deflection_distance=snap_deflection,
        )

    return base, cap


def add_pogo_pocket(base):
    """Stepped pill pocket on the +Y face with an outward pill ridge for pogo mating."""
    pogo_z = skirt_bottom_z + pogo_z_offset

    ridge = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=pos_y_face_y)
        .center(center_x, pogo_z)
        .slot2D(pogo_ridge_length, pogo_ridge_width)
        .extrude(pogo_ridge_depth)
    )
    base = base.union(ridge)

    outer_step = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=pos_y_face_y + pogo_ridge_depth + overcut)
        .center(center_x, pogo_z)
        .slot2D(pogo_outer_length, pogo_outer_width)
        .extrude(-(pogo_outer_depth + overcut))
    )
    inner_step = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=pos_y_face_y + overcut)
        .center(center_x, pogo_z)
        .slot2D(pogo_inner_length, pogo_inner_width)
        .extrude(-(wall_thickness + 2 * overcut))
    )
    return base.cut(outer_step).cut(inner_step)


# Assembly

def build_pump_case():
    solid = build_base_plate_with_ramp()
    solid = solid.union(build_skirt())
    solid = add_bore_wall(solid)
    solid = solid.union(build_tower())
    solid = cut_bore_cavity(solid)
    combined = solid.union(build_lower_extension())
    combined = cut_arch_notches(combined)
    base, cap = split_into_base_and_cap(combined)
    base, cap = add_snap_fits(base, cap)
    base = add_pogo_pocket(base)
    return base, cap


def main():
    base, cap = build_pump_case()
    export_step(base.unwrap(), str(_here / "pump-case-base-cadquery.step"))
    export_step(cap.unwrap(), str(_here / "pump-case-cap-cadquery.step"))
    print("-> pump-case-base-cadquery.step")
    print("-> pump-case-cap-cadquery.step")

    substitute_py_comments(
        _here / "pump_case.py",
        variables={
            "CASE_OUTER_X": f"{case_outer_x:.1f} mm",
            "CASE_OUTER_Y": f"{case_outer_y:.1f} mm",
            "CASE_OUTER_Z": f"{case_outer_z:.1f} mm",
            "CYLINDER_BOTTOM_Z": f"{cylinder_bottom_z:+g} mm",
            "BORE_BOTTOM_Z": f"{bore_bottom_z:+g} mm",
            "CYLINDER_TOP_Z": f"{cylinder_top_z:+g} mm",
            "BASE_PLATE_FAR_Z": f"+{base_thickness:.4g} mm",
            "NARROW_SPLIT_Z": f"{narrow_split_z:+g} mm",
            "SKIRT_BOTTOM_Z": f"{skirt_bottom_z:+g} mm",
            "LOWER_CAP_TOP_Z": f"{lower_cap_top_z:+g} mm",
            "LOWER_CAP_BOTTOM_Z": f"{lower_cap_bottom_z:+g} mm",
            "FOOTPRINT_X": f"{footprint_x:.4g}",
            "SKIRT_WIDE_WIDTH": f"{skirt_wide_full_width:.4g}",
            "SKIRT_NARROW_WIDTH": f"{skirt_narrow_full_width:.4g}",
            "SKIRT_WIDE_FLARE": f"{skirt_wide_flare_per_side:.4g}mm",
            "SKIRT_NARROW_TAPER": f"{skirt_narrow_taper_per_side:.4g}mm",
        },
        expected_counts={
            "CASE_OUTER_X": 1,
            "CASE_OUTER_Y": 1,
            "CASE_OUTER_Z": 1,
            "CYLINDER_BOTTOM_Z": 2,
            "BORE_BOTTOM_Z": 2,
            "CYLINDER_TOP_Z": 2,
            "BASE_PLATE_FAR_Z": 1,
            "NARROW_SPLIT_Z": 2,
            "SKIRT_BOTTOM_Z": 2,
            "LOWER_CAP_TOP_Z": 2,
            "LOWER_CAP_BOTTOM_Z": 2,
            "FOOTPRINT_X": 2,
            "SKIRT_WIDE_WIDTH": 1,
            "SKIRT_NARROW_WIDTH": 1,
            "SKIRT_WIDE_FLARE": 2,
            "SKIRT_NARROW_TAPER": 1,
        },
    )
    print("-> updated comments in pump_case.py")


if __name__ == "__main__":
    main()
