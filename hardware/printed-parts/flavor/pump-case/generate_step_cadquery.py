"""Pump case — two-piece snap-fit enclosure for a peristaltic pump.

The case is built as one combined solid, then split with a stepped cut
into a base and a cap.

Base: base plate with octagon-to-footprint ramp, octagon pump bore,
      M3 mounting holes, a cylindrical tower below, and a pogo connector pocket.
Cap:  asymmetric flared skirt (wide on +Z, narrow on -Z) with a lower
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

from snap import apply_ramp_out_first, apply_ramp_in_first
from _cadq_export import export_step


# Physical dimensions
footprint_x = 70.0
footprint_z = 70.0
corner_r = 6.0
wall_thickness = 3.0

center_x = footprint_x / 2
center_z = footprint_z / 2

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

# M3 mounting holes
hole_r = 3.3 / 2.0
hole_positions = [
    (center_x - 25.0, center_z + 25.0),
    (center_x + 25.0, center_z + 25.0),
    (center_x + 25.0, center_z - 25.0),
    (center_x - 25.0, center_z - 25.0),
]

# Tower
tower_height = 60.0
platform_thickness = 3.0
cap_thickness = 3.0
cylinder_id = 37.0
cylinder_od = cylinder_id + 2 * wall_thickness
cylinder_r_outer = cylinder_od / 2
cylinder_r_inner = cylinder_id / 2

# Lower extension
lower_height = 23.0
lower_cap_thickness = 3.0
lower_footprint_straight = skirt_wide_straight_height

# Stepped split
step_height = 19.0
step_z_clearance = 6.0

# Snap fits
snap_zone_width = 20.0
snap_wall_height = 9.0
snap_deflection = 1.5

# Arch notches
arch_radius = 4.5

# Pogo connector
pogo_outer_length = 12.7
pogo_outer_width = 4.2
pogo_outer_depth = 1.0
pogo_inner_length = 14.7
pogo_inner_width = 4.2
pogo_y_offset = 13.5
pogo_ridge_length = 24.5
pogo_ridge_width = 10.0
pogo_ridge_depth = 0.7  # thin outer wall so pogo pins protrude further

# Shared constants
overcut = 0.1
arc_segments = 8


# Derived geometry
octagon_wall_outer_extent = vertex_far + wall_thickness

bore_depth = base_thickness + ramp_from_skirt_to_octagon_height
tower_base_y = -bore_depth
ramp_from_octagon_to_cylinder_height = octagon_wall_outer_extent - cylinder_r_outer
octagon_to_cylinder_scale = cylinder_r_outer / octagon_wall_outer_extent

footprint_half_extent = footprint_x / 2


def case_workplane(y_offset):
    """XZ workplane at world Y = y_offset, centered on the case (X = center_x, Z = center_z).

    +Y in the workplane's local frame maps to +Y in world coords; subsequent
    .extrude(h) extrudes along world +Y with positive h.
    """
    return cq.Workplane("XZ").workplane(offset=y_offset).center(center_x, center_z)


# Polygon generators

class Turtle:
    """Logo-style turtle that accumulates (x, z) polygon points."""

    def __init__(self, x, z, heading_deg):
        self.x = x
        self.z = z
        self.heading = math.radians(heading_deg)
        self.points = []

    def forward(self, dist):
        self.x += dist * math.cos(self.heading)
        self.z += dist * math.sin(self.heading)
        self.points.append((self.x, self.z))

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
        start_x, start_z = vertices[i]
        end_x, end_z = vertices[(i + 1) % 8]
        pts.append((start_x, start_z))

        if i not in long_edge_indices:
            continue

        edge_dx, edge_dz = end_x - start_x, end_z - start_z
        edge_length = math.hypot(edge_dx, edge_dz)
        edge_heading = math.degrees(math.atan2(edge_dz, edge_dx))

        mid_x, mid_z = (start_x + end_x) / 2, (start_z + end_z) / 2
        unit_x, unit_z = edge_dx / edge_length, edge_dz / edge_length
        normal_x, normal_z = unit_z, -unit_x
        if normal_x * (-mid_x) + normal_z * (-mid_z) < 0:
            normal_x, normal_z = -normal_x, -normal_z
        inward_is_left = (normal_x * (-unit_z) + normal_z * unit_x) > 0

        ledge_ramp_length = ledge_depth * math.sqrt(2)
        entry_length = (edge_length - ledge_shelf_span) / 2
        shelf_length = ledge_shelf_span - 2 * ledge_depth

        t = Turtle(start_x, start_z, edge_heading)
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
        x1, z1 = pts[i]
        x2, z2 = pts[(i + 1) % n]
        dx, dz = x2 - x1, z2 - z1
        length = math.hypot(dx, dz)
        nx, nz = -dz / length, dx / length
        edges.append((dx, dz, nx, nz))

    result = []
    for i in range(n):
        prev = (i - 1) % n
        ax = pts[prev][0] + distance * edges[prev][2]
        az = pts[prev][1] + distance * edges[prev][3]
        adx, adz = edges[prev][0], edges[prev][1]

        bx = pts[i][0] + distance * edges[i][2]
        bz = pts[i][1] + distance * edges[i][3]
        bdx, bdz = edges[i][0], edges[i][1]

        det = adx * bdz - adz * bdx
        if abs(det) < 1e-10:
            result.append((bx, bz))
        else:
            t = ((bx - ax) * bdz - (bz - az) * bdx) / det
            result.append((ax + t * adx, az + t * adz))

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
    for cx, cz, start_deg, end_deg in corners:
        for i in range(n + 1):
            angle = math.radians(start_deg + (end_deg - start_deg) * i / n)
            pts.append((cx + radius * math.cos(angle), cz + radius * math.sin(angle)))
    return pts


def split_skirt_profile(wide_half_extent, wide_radius,
                        narrow_half_extent, narrow_radius,
                        transition_z_plus=None, transition_z_minus=None,
                        wide_half_extent_z=None, narrow_half_extent_z=None,
                        n=arc_segments):
    """Asymmetric profile: wider on +Z, narrower on -Z, with diagonal transitions.

    The +Z half and -Z half can flare/taper independently. Transition Z
    values keep the seam wall in a fixed vertical plane as the two halves
    change size at different rates.
    """
    wide_radius = max(wide_radius, 0.01)
    narrow_radius = max(narrow_radius, 0.01)
    if wide_half_extent_z is None:
        wide_half_extent_z = wide_half_extent
    if narrow_half_extent_z is None:
        narrow_half_extent_z = narrow_half_extent
    wide_corner_center_x = wide_half_extent - wide_radius
    wide_corner_center_z = wide_half_extent_z - wide_radius
    narrow_corner_center_x = narrow_half_extent - narrow_radius
    narrow_corner_center_z = narrow_half_extent_z - narrow_radius

    if transition_z_plus is None:
        transition_z_plus = max((wide_half_extent - narrow_half_extent) / 2, 0.01)
    if transition_z_minus is None:
        transition_z_minus = -transition_z_plus

    pts = []

    for i in range(n + 1):
        a = math.radians(90 * i / n)
        pts.append((wide_corner_center_x + wide_radius * math.cos(a),
                    wide_corner_center_z + wide_radius * math.sin(a)))
    for i in range(n + 1):
        a = math.radians(90 + 90 * i / n)
        pts.append((-wide_corner_center_x + wide_radius * math.cos(a),
                    wide_corner_center_z + wide_radius * math.sin(a)))

    pts.append((-wide_half_extent, transition_z_plus))
    pts.append((-narrow_half_extent, transition_z_minus))

    for i in range(n + 1):
        a = math.radians(180 + 90 * i / n)
        pts.append((-narrow_corner_center_x + narrow_radius * math.cos(a),
                    -narrow_corner_center_z + narrow_radius * math.sin(a)))
    for i in range(n + 1):
        a = math.radians(270 + 90 * i / n)
        pts.append((narrow_corner_center_x + narrow_radius * math.cos(a),
                    -narrow_corner_center_z + narrow_radius * math.sin(a)))

    pts.append((narrow_half_extent, transition_z_minus))
    pts.append((wide_half_extent, transition_z_plus))

    return pts


# Bore profiles (shared by bore construction and tower)
bore_profile = bore_octagon_profile()
bore_wall_profile = offset_polygon(bore_profile, wall_thickness)
bore_wall_profile_at_cylinder = [
    (x * octagon_to_cylinder_scale, z * octagon_to_cylinder_scale)
    for x, z in bore_wall_profile
]


# Skirt profiles (shared by skirt, lower extension, split, and snap fits).
#
# The skirt splits asymmetrically: +Z half flares outward (70→76), -Z half
# tapers inward (70→62). Both flares are at 45 degrees. The transition wall
# stays in a fixed vertical plane by tracking each endpoint's Z independently.
# The same profile set is used by the outer skirt surface and (shrunk by
# skirt_wall) by the inner cavity.

skirt_base_half_extent = footprint_half_extent
skirt_wide_half_extent = skirt_base_half_extent + skirt_wide_flare_per_side
skirt_narrow_half_extent = skirt_base_half_extent - skirt_narrow_taper_per_side
# At the moment the wide flare completes (3mm), the narrow side
# has only tapered by 3 of its 4mm.
skirt_mid_narrow_half_extent = skirt_base_half_extent - skirt_wide_flare_per_side

# Narrow straight section is shorter so both halves land together.
skirt_narrow_straight_height = (
    skirt_wide_straight_height
    - (skirt_narrow_taper_per_side - skirt_wide_flare_per_side)
)

# Transition Z coordinates keep the seam wall in the vertical plane
# X + Z = -skirt_base_half_extent at every Y level.
skirt_tz_symmetric = (0.01, -0.01)
skirt_tz_mid = (skirt_wide_flare_per_side, -skirt_wide_flare_per_side)
skirt_tz_end = (skirt_wide_flare_per_side, -skirt_narrow_taper_per_side)
skirt_transition_z_end_plus = skirt_tz_end[0]

skirt_y_steps = [
    skirt_upper_height,
    skirt_wide_flare_per_side,
    skirt_narrow_taper_per_side - skirt_wide_flare_per_side,
    skirt_narrow_straight_height,
]
skirt_bottom_offset = sum(skirt_y_steps)
skirt_bottom_y = -skirt_bottom_offset


def _skirt_profile_set(wall_offset):
    """Five skirt cross-section profiles, top-of-skirt to bottom-of-skirt.

    wall_offset shrinks each half-extent and radius by that amount and
    shifts each transition Z so the resulting seam plane stays a full
    wall_offset perpendicular distance inward from the wall_offset=0 set
    (the seam runs at 45 degrees in the XZ plane).
    """
    # The seam diagonal is at 45 deg, so a wall-thickness X-offset only gives
    # wall/sqrt(2) perpendicular thickness. Shift transition Z values so the
    # inner seam plane is a full wall-thickness perpendicular from outer.
    seam_z_shift = wall_offset * (math.sqrt(2) - 1)

    base_he = skirt_base_half_extent - wall_offset
    wide_he = skirt_wide_half_extent - wall_offset
    narrow_he = skirt_narrow_half_extent - wall_offset
    mid_narrow_he = skirt_mid_narrow_half_extent - wall_offset
    radius = corner_r - wall_offset

    tz_symmetric_plus, tz_symmetric_minus = skirt_tz_symmetric
    tz_mid_plus = skirt_tz_mid[0] + seam_z_shift
    tz_mid_minus = skirt_tz_mid[1] + seam_z_shift
    tz_end_plus = skirt_tz_end[0] + seam_z_shift
    tz_end_minus = skirt_tz_end[1] + seam_z_shift

    symmetric = split_skirt_profile(
        base_he, radius, base_he, radius,
        tz_symmetric_plus, tz_symmetric_minus,
    )
    mid = split_skirt_profile(
        wide_he, radius, mid_narrow_he, radius,
        tz_mid_plus, tz_mid_minus,
        wide_half_extent_z=base_he, narrow_half_extent_z=base_he,
    )
    end = split_skirt_profile(
        wide_he, radius, narrow_he, radius,
        tz_end_plus, tz_end_minus,
        wide_half_extent_z=base_he, narrow_half_extent_z=base_he,
    )
    return [symmetric, symmetric, mid, end, end]


skirt_outer_profiles = _skirt_profile_set(0)
skirt_inner_profiles = _skirt_profile_set(skirt_wall)


# Feature functions — base plate and bore

def build_base_plate_with_ramp():
    """Ramped platform from the 70x70 footprint down to the octagon bore."""
    footprint = rounded_rect_profile(footprint_x, footprint_z, corner_r)
    footprint_at_ramp_bottom = rounded_rect_profile(
        footprint_x - 2 * ramp_from_skirt_to_octagon_height,
        footprint_z - 2 * ramp_from_skirt_to_octagon_height,
        corner_r)

    return (
        case_workplane(0)
        .polyline(footprint).close()
        .workplane(offset=-base_thickness)
        .polyline(footprint).close()
        .workplane(offset=-ramp_from_skirt_to_octagon_height)
        .polyline(footprint_at_ramp_bottom).close()
        .loft(ruled=True)
    )


def add_bore_wall_and_cut_bore(solid):
    """Add octagon bore wall, then cut the bore cavity."""
    bore_wall = (
        case_workplane(0)
        .polyline(bore_wall_profile).close()
        .extrude(-bore_depth)
    )
    bore_cavity = (
        case_workplane(0)
        .polyline(bore_profile).close()
        .extrude(-(bore_depth + overcut))
    )
    return solid.union(bore_wall).cut(bore_cavity)


def cut_mounting_holes(solid):
    """M3 mounting holes through the base plate and bore wall."""
    for hx, hz in hole_positions:
        hole = (
            cq.Workplane("XZ")
            .workplane(offset=0)
            .center(hx, hz)
            .circle(hole_r)
            .extrude(-(bore_depth + overcut))
        )
        solid = solid.cut(hole)
    return solid


# Feature functions — skirt

def loft_profile_stack(start_y_offset, y_steps, profiles, overcut_last_step=False):
    """Loft a stack of profiles, each on its own offset workplane.

    Profiles are placed on workplanes at cumulative offsets: the first at
    start_y_offset, each subsequent at the previous + the next y_step. If
    overcut_last_step, the final step is extended by overcut to ensure a
    cut profile pierces cleanly through a sibling solid boundary.
    """
    wp = case_workplane(start_y_offset).polyline(profiles[0]).close()
    for i, (step, profile) in enumerate(zip(y_steps, profiles[1:])):
        extra = overcut if (overcut_last_step and i == len(y_steps) - 1) else 0
        wp = wp.workplane(offset=step + extra).polyline(profile).close()
    return wp.loft(ruled=True)


def build_skirt():
    """Asymmetric flared skirt: wide on +Z, narrow on -Z."""
    skirt_outer = loft_profile_stack(0, skirt_y_steps, skirt_outer_profiles)
    skirt_cavity = loft_profile_stack(0, skirt_y_steps, skirt_inner_profiles, overcut_last_step=True)
    return skirt_outer.cut(skirt_cavity)


# Feature functions — tower

def build_tower():
    """Octagon platform, octagon-to-cylinder ramp, and cylindrical tower."""
    tower_platform = (
        case_workplane(tower_base_y)
        .polyline(bore_wall_profile).close()
        .extrude(-platform_thickness)
    )

    tower_ramp = (
        case_workplane(tower_base_y - platform_thickness)
        .polyline(bore_wall_profile).close()
        .workplane(offset=-ramp_from_octagon_to_cylinder_height)
        .polyline(bore_wall_profile_at_cylinder).close()
        .loft(ruled=True)
    )

    tower_cylinder = (
        case_workplane(tower_base_y)
        .circle(cylinder_r_outer)
        .extrude(-tower_height)
    )

    tower = tower_platform.union(tower_ramp).union(tower_cylinder)

    tower_bore_depth = tower_height - cap_thickness
    tower_bore = (
        case_workplane(tower_base_y + overcut)
        .circle(cylinder_r_inner)
        .extrude(-(tower_bore_depth + overcut))
    )
    return tower.cut(tower_bore)


# Feature functions — lower extension

def _lower_profile_set(wall_offset):
    """Four lower-extension cross-section profiles, top to bottom of lower section.

    Same wall_offset semantics as _skirt_profile_set: the wall_offset=0 set
    is the outer surface; the wall_offset=skirt_wall set is the inner cavity.
    """
    narrow_he = skirt_narrow_half_extent - wall_offset
    base_he = skirt_base_half_extent - wall_offset
    radius = corner_r - wall_offset
    narrow_symmetric = split_skirt_profile(
        narrow_he, radius, narrow_he, radius,
        0.01, -0.01,
        wide_half_extent_z=base_he, narrow_half_extent_z=base_he,
    )
    top = _skirt_profile_set(wall_offset)[-1]
    return [top, top, narrow_symmetric, narrow_symmetric]


def build_lower_extension():
    """Lower portion extending from skirt bottom: taper to uniform, then cap."""
    lower_ramp_height = (skirt_base_half_extent + skirt_wide_flare_per_side
                         - skirt_narrow_half_extent)
    lower_uniform_straight = (lower_height - lower_ramp_height
                              - lower_footprint_straight)
    lower_y_steps = [lower_footprint_straight, lower_ramp_height,
                     lower_uniform_straight]

    lower_outer_profiles = _lower_profile_set(0)
    lower_inner_profiles = _lower_profile_set(skirt_wall)

    lower_outer = loft_profile_stack(skirt_bottom_offset, lower_y_steps, lower_outer_profiles)
    lower_inner = loft_profile_stack(skirt_bottom_offset, lower_y_steps, lower_inner_profiles,
                                     overcut_last_step=True)
    lower_shell = lower_outer.cut(lower_inner)

    lower_cap_offset = skirt_bottom_offset + lower_height
    lower_cap = (
        case_workplane(lower_cap_offset)
        .polyline(lower_outer_profiles[-1]).close()
        .extrude(lower_cap_thickness)
    )
    return lower_shell.union(lower_cap)


# Feature functions — arch notches, split, snaps

def cut_arch_notches(combined):
    """Semicircular notches on the +Z face for wire routing."""
    z_face_outer = center_z + footprint_half_extent
    arch_hole_xs = [
        corner_r + arch_radius - 4,
        footprint_x - corner_r - arch_radius + 4,
    ]

    for ax in arch_hole_xs:
        arch_cutter = (
            cq.Workplane("XY")
            .workplane(offset=z_face_outer + overcut)
            .center(ax, skirt_bottom_y)
            .circle(arch_radius)
            .extrude(-(skirt_wall + 3 + overcut))
        )
        combined = combined.cut(arch_cutter)
    return combined


def split_into_base_and_cap(combined):
    """Stepped split creating base (with tower) and cap (with lower extension).

    The two parts meet at two different Y levels:
      Wide half (+Z):   at skirt_bottom_offset (original mating surface)
      Narrow half (-Z): step_height higher into the skirt
    The boundary follows the seam diagonal.
    """
    step_offset = skirt_bottom_offset - step_height
    lower_end_offset = skirt_bottom_offset + lower_height + lower_cap_thickness + overcut

    full_slab = (
        case_workplane(skirt_bottom_offset)
        .rect(100, 100)
        .extrude(lower_end_offset - skirt_bottom_offset)
    )

    step_z = skirt_transition_z_end_plus + step_z_clearance
    narrow_box = [(-50, -50), (50, -50), (50, step_z + overcut), (-50, step_z + overcut)]
    narrow_step = (
        case_workplane(step_offset)
        .polyline(narrow_box).close()
        .extrude(skirt_bottom_offset - step_offset)
    )

    step_cutter = full_slab.union(narrow_step)

    base = combined.cut(step_cutter)
    cap = combined.intersect(step_cutter)
    return base, cap


def add_snap_fits(base, cap):
    """Snap-fit ramps on four interior walls where base meets cap."""
    step_offset = skirt_bottom_offset - step_height

    snap_plus_z_inner = center_z + footprint_half_extent - wall_thickness
    snap_minus_z_inner = center_z - footprint_half_extent + wall_thickness
    snap_plus_x_narrow_inner = center_x + footprint_half_extent - wall_thickness
    snap_minus_x_narrow_inner = center_x - footprint_half_extent + wall_thickness

    wide_split_y = -skirt_bottom_offset
    narrow_split_y = -step_offset

    yz_zone_start = center_x - snap_zone_width / 2
    yz_zone_end = center_x + snap_zone_width / 2
    xy_narrow_zone_start = center_z - skirt_narrow_half_extent + corner_r + 0.5
    xy_narrow_zone_end = xy_narrow_zone_start + snap_zone_width

    snap_faces = [
        (snap_plus_z_inner, +1, wide_split_y, "YZ",
         yz_zone_start, yz_zone_end, snap_wall_height),
        (snap_minus_z_inner, -1, narrow_split_y, "YZ",
         yz_zone_start, yz_zone_end, snap_wall_height),
        (snap_plus_x_narrow_inner, +1, narrow_split_y, "XY",
         xy_narrow_zone_start, xy_narrow_zone_end, snap_wall_height),
        (snap_minus_x_narrow_inner, -1, narrow_split_y, "XY",
         xy_narrow_zone_start, xy_narrow_zone_end, snap_wall_height),
    ]

    for inner_face, sign, split_y, plane, zone_start, zone_end, wall_height in snap_faces:
        base = apply_ramp_out_first(
            solid=base,
            coordinate_inner_wall=inner_face,
            coordinate_zone_start=zone_start,
            coordinate_zone_end=zone_end,
            coordinate_lowest_possible_snap_base_in_wall=split_y + wall_height,
            coordinate_top_of_wall=split_y,
            orientation_outward_sign=sign,
            orientation_plane=plane,
            orientation_height_sign=-1,
            orientation_height_axis="Y",
            deflection_distance=snap_deflection,
        )
        cap = apply_ramp_in_first(
            solid=cap,
            coordinate_inner_wall=inner_face,
            coordinate_zone_start=zone_start,
            coordinate_zone_end=zone_end,
            coordinate_lowest_possible_snap_base_in_wall=split_y - wall_height,
            coordinate_top_of_wall=split_y,
            orientation_outward_sign=sign,
            orientation_plane=plane,
            orientation_height_sign=+1,
            orientation_height_axis="Y",
            deflection_distance=snap_deflection,
        )

    return base, cap


# Feature functions — pogo connector pocket

def add_pogo_pocket(base):
    """Stepped pill pocket on the +Z face with an outward pill ridge for pogo mating."""
    z_face_outer = center_z + footprint_half_extent
    pogo_y = skirt_bottom_y + pogo_y_offset

    ridge = (
        cq.Workplane("XY")
        .workplane(offset=z_face_outer)
        .center(center_x, pogo_y)
        .slot2D(pogo_ridge_length, pogo_ridge_width)
        .extrude(pogo_ridge_depth)
    )
    base = base.union(ridge)

    outer_step = (
        cq.Workplane("XY")
        .workplane(offset=z_face_outer + pogo_ridge_depth + overcut)
        .center(center_x, pogo_y)
        .slot2D(pogo_outer_length, pogo_outer_width)
        .extrude(-(pogo_outer_depth + overcut))
    )
    inner_step = (
        cq.Workplane("XY")
        .workplane(offset=z_face_outer + overcut)
        .center(center_x, pogo_y)
        .slot2D(pogo_inner_length, pogo_inner_width)
        .extrude(-(wall_thickness + 2 * overcut))
    )
    return base.cut(outer_step).cut(inner_step)


# Assembly

def build_pump_case():
    solid = build_base_plate_with_ramp()
    solid = solid.union(build_skirt())
    solid = add_bore_wall_and_cut_bore(solid)
    solid = cut_mounting_holes(solid)
    solid = solid.union(build_tower())
    combined = solid.union(build_lower_extension())
    combined = cut_arch_notches(combined)
    base, cap = split_into_base_and_cap(combined)
    base, cap = add_snap_fits(base, cap)
    base = add_pogo_pocket(base)
    return base, cap


def main():
    base, cap = build_pump_case()
    export_step(base, str(_here / "pump-case-base-cadquery.step"))
    export_step(cap, str(_here / "pump-case-cap-cadquery.step"))
    print("-> pump-case-base-cadquery.step")
    print("-> pump-case-cap-cadquery.step")


if __name__ == "__main__":
    main()
