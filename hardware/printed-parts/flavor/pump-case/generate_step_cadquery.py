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

from snap import Frame, apply_ramp_out_first, apply_ramp_in_first
from world_workplane import WorldWorkplane, xz_plane_y_up, xy_plane_z_up
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
cap_thickness = 3.0
cylinder_id = 37.0
cylinder_r_inner = cylinder_id / 2
# cylinder_r_outer is set in the derived-geometry section below — its
# value matches the octagonal bore wall's outer extent so the bore-to-
# tower joint needs no ramp.

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

# Slop added to cut depths so they pierce cleanly through sibling solid
# boundaries (the resulting STEP is unaffected — the excess lives in the
# air outside the parent).
overcut = 0.1
# Polygonization count per quarter-circle for round-corner profiles.
arc_segments = 8


# Coordinate convention
# ---------------------
# Every `_y` and `_z` in this file is a signed world coordinate.
# Distances/heights/thicknesses are unsigned magnitudes.
#
# Origin is at the center of the case footprint, on the bore-opening
# face of the base plate.  +Y points toward the tower (away from the
# cap); -Y points toward the skirt top (toward the cap).  Construction
# uses the following horizontal levels:
#
#   y = +81      tower cylinder's far face (its bottom in install orientation)
#   y = +21      bore wall's far face (octagonal bore cavity ends here)
#   y =  +8      tower cylinder's near face — cylinder top tangent to
#                the base-plate ramp at the cardinals; overlaps the bore
#                wall in y∈[+8,+21] (containing it strictly inside the
#                larger radius — no tangent meeting at the cardinals)
#   y =  +3      base plate's lower face
#   y =   0      base plate's bore-opening face — origin
#   y =  -9.5    narrow-half cap-side step (the stepped split)
#   y = -28.5    skirt's wide-half mating edge with the cap
#   y = -51.5    cap lower extension's far face
#   y = -54.5    cap lower extension's closing-wall outer face

octagon_wall_outer_extent = vertex_far + wall_thickness

bore_depth = base_thickness + ramp_from_skirt_to_octagon_height
bore_bottom_y = bore_depth                                        # +21

# The tower's outer radius sits 0.5 mm beyond the bore wall's outer
# extent at the cardinals (octagon_wall_outer_extent = 29.5, cylinder
# = 30.0).  The cylinder strictly contains the bore wall instead of
# meeting it tangentially at the cardinals — no knife-edge joint
# anywhere, just an inward step of 0.5 mm at the cardinals and ~5 mm
# at the diagonals as the layer transitions from cylinder up into the
# bore-wall section.
cylinder_r_outer = octagon_wall_outer_extent + 0.5

# The cylinder's top face sits at Y=+8, the Y level at which the
# base-plate ramp's cardinal half-extent equals cylinder_r_outer (the
# ramp at Y=+8 is at 38 - 8 = 30.0).  The cylinder's top edge is
# therefore exactly tangent to the ramp at the cardinals — no bumps
# protruding past the ramp at the cylinder's top face.  Below this Y
# the cylinder overlaps the bore-wall region down to bore_bottom_y;
# in that overlap the cylinder is the outer surface (the bore wall is
# fully contained inside it).
cylinder_top_y = 8
cylinder_bottom_y = bore_bottom_y + tower_height                  # +81

footprint_half_extent = footprint_x / 2


def case_workplane(world_y):
    """XZ-aligned workplane at world Y = world_y, with the in-plane
    origin shifted to (world X = center_x, world Z = center_z).

    Built on xz_plane_y_up so subsequent .workplane(offset=dy) shifts
    by dy along world +Y, .extrude(h) extrudes h along world +Y, and
    polyline/center args accept world (x, z) tuples (the wrapper
    handles the local-Y chirality flip).

    Because of the centering, polyline points passed downstream are
    interpreted as case-centered (x, z) — i.e., (0, 0) is the case's
    central axis, not a corner.  Pre-built profiles like the bore
    octagon and the rounded-rect footprints are already centered at
    origin and need no further shifting.
    """
    return (WorldWorkplane(xz_plane_y_up)
            .workplane(offset=world_y)
            .center(center_x, center_z))


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

# Transition Z coordinates (the +/- Z endpoints of the diagonal seam wall
# at each profile's Y level). They keep the seam wall in the vertical
# plane X + Z = -skirt_base_half_extent at every Y as the +Z half flares
# and the -Z half tapers at different rates.
skirt_transition_z_symmetric = (0.01, -0.01)
skirt_transition_z_mid = (skirt_wide_flare_per_side, -skirt_wide_flare_per_side)
skirt_transition_z_end = (skirt_wide_flare_per_side, -skirt_narrow_taper_per_side)
skirt_transition_z_end_plus = skirt_transition_z_end[0]

# Signed world-Y deltas between the five skirt cross-section levels.
# Each entry is negative because the skirt grows from y=0 (base plate)
# toward more negative Y (away from the bore, toward the cap).
skirt_y_steps = [
    -skirt_upper_height,
    -skirt_wide_flare_per_side,
    -(skirt_narrow_taper_per_side - skirt_wide_flare_per_side),
    -skirt_narrow_straight_height,
]
skirt_bottom_y = sum(skirt_y_steps)                # -28.5; case's wide-half mating edge with the cap

# Y level of the cap-side stepped split — narrow half (-Z) meets the cap
# step_height higher into the skirt than the wide half (+Z).
narrow_split_y = skirt_bottom_y + step_height      # -9.5

# World Z of the case's +Z outer face.
pos_z_face_z = center_z + footprint_half_extent


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

    tz_symmetric_plus, tz_symmetric_minus = skirt_transition_z_symmetric
    tz_mid_plus = skirt_transition_z_mid[0] + seam_z_shift
    tz_mid_minus = skirt_transition_z_mid[1] + seam_z_shift
    tz_end_plus = skirt_transition_z_end[0] + seam_z_shift
    tz_end_minus = skirt_transition_z_end[1] + seam_z_shift

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


def build_base_plate_with_ramp():
    """Base plate (y=0..+3) plus the 45° ramp (y=+3..+21) shrinking from
    the 70x70 footprint to a 34x34 footprint that meets the octagon bore wall."""
    footprint = rounded_rect_profile(footprint_x, footprint_z, corner_r)
    footprint_at_ramp_bottom = rounded_rect_profile(
        footprint_x - 2 * ramp_from_skirt_to_octagon_height,
        footprint_z - 2 * ramp_from_skirt_to_octagon_height,
        corner_r)

    return (
        case_workplane(0)
        .polyline(footprint).close()
        .workplane(offset=base_thickness)
        .polyline(footprint).close()
        .workplane(offset=ramp_from_skirt_to_octagon_height)
        .polyline(footprint_at_ramp_bottom).close()
        .loft(ruled=True)
    )


def add_bore_wall(solid):
    """Add the octagonal bore wall around the pump-flange seat. The bore
    cavity (the hollow interior with ledges) is NOT cut here — see
    cut_bore_cavity, which runs after the tower cylinder is unioned so
    the cavity also pierces the cylinder's overlap with the bore region."""
    bore_wall = (
        case_workplane(0)
        .polyline(bore_wall_profile).close()
        .extrude(bore_depth)
    )
    return solid.union(bore_wall)


def cut_bore_cavity(solid):
    """Cut the octagonal pump-flange seat (with ledges) through the bore
    wall and any tower cylinder material that overlaps the bore-wall
    region.  Must run after build_tower has been unioned in, otherwise
    the cylinder fills the cavity back in."""
    bore_cavity = (
        case_workplane(0)
        .polyline(bore_profile).close()
        .extrude(bore_depth + overcut)
    )
    return solid.cut(bore_cavity)


def cut_mounting_holes(solid):
    """M3 mounting holes through the base plate and bore wall."""
    for hx, hz in hole_positions:
        hole = (
            WorldWorkplane(xz_plane_y_up)
            .workplane(offset=0)
            .center(hx, hz)
            .circle(hole_r)
            .extrude(bore_depth + overcut)
        )
        solid = solid.cut(hole)
    return solid


def loft_profile_stack(start_world_y, y_steps, profiles, overcut_last_step=False):
    """Loft a stack of profiles at successive world-Y levels.

    start_world_y: world Y of the first profile.
    y_steps: signed world-Y deltas between consecutive profiles.
    overcut_last_step: extend the last delta by overcut in the same
        direction as the loft's travel, so a cut profile pierces cleanly
        through a sibling solid boundary.
    """
    wp = case_workplane(start_world_y).polyline(profiles[0]).close()
    for i, (step, profile) in enumerate(zip(y_steps, profiles[1:])):
        is_last = i == len(y_steps) - 1
        extra = math.copysign(overcut, step) if (overcut_last_step and is_last) else 0
        wp = wp.workplane(offset=step + extra).polyline(profile).close()
    return wp.loft(ruled=True)


def build_skirt():
    """Asymmetric flared skirt: wide on +Z, narrow on -Z."""
    skirt_outer = loft_profile_stack(0, skirt_y_steps, skirt_outer_profiles)
    skirt_cavity = loft_profile_stack(0, skirt_y_steps, skirt_inner_profiles, overcut_last_step=True)
    return skirt_outer.cut(skirt_cavity)


def build_tower():
    """Cylindrical tower extending downward from cylinder_top_y. The
    outer radius (cylinder_r_outer) circumscribes the octagonal bore
    wall, so there's no octagon-to-cylinder transition — the tower is
    a single uniform-radius cylinder.  The cylinder starts above the
    bore wall's far face, overlapping it on the outside; the bore
    cavity inside stays at its original Y range (it's the pump body's
    clearance, separate from the tower's outer shape)."""
    tower_cylinder = (
        case_workplane(cylinder_top_y)
        .circle(cylinder_r_outer)
        .extrude(cylinder_bottom_y - cylinder_top_y)
    )

    tower_bore_depth = tower_height - cap_thickness
    tower_bore = (
        case_workplane(bore_bottom_y - overcut)
        .circle(cylinder_r_inner)
        .extrude(tower_bore_depth + overcut)
    )
    return tower_cylinder.cut(tower_bore)


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
    # Lower extension continues away from the base plate in the same -Y
    # direction the skirt was growing in.
    lower_y_steps = [-lower_footprint_straight, -lower_ramp_height,
                     -lower_uniform_straight]

    lower_outer_profiles = _lower_profile_set(0)
    lower_inner_profiles = _lower_profile_set(skirt_wall)

    lower_outer = loft_profile_stack(skirt_bottom_y, lower_y_steps, lower_outer_profiles)
    lower_inner = loft_profile_stack(skirt_bottom_y, lower_y_steps, lower_inner_profiles,
                                     overcut_last_step=True)
    lower_shell = lower_outer.cut(lower_inner)

    lower_cap_top_y = skirt_bottom_y - lower_height
    lower_cap = (
        case_workplane(lower_cap_top_y)
        .polyline(lower_outer_profiles[-1]).close()
        .extrude(-lower_cap_thickness)
    )
    return lower_shell.union(lower_cap)


def cut_arch_notches(combined):
    """Semicircular notches on the +Z face for wire routing."""
    arch_hole_xs = [
        corner_r + arch_radius - 4,
        footprint_x - corner_r - arch_radius + 4,
    ]
    arch_cut_depth = skirt_wall + wall_thickness
    for ax in arch_hole_xs:
        arch_cutter = (
            cq.Workplane(xy_plane_z_up)
            .workplane(offset=pos_z_face_z + overcut)
            .center(ax, skirt_bottom_y)
            .circle(arch_radius)
            .extrude(-(arch_cut_depth + overcut))
        )
        combined = combined.cut(arch_cutter)
    return combined


def split_into_base_and_cap(combined):
    """Stepped split creating base (with tower) and cap (with lower extension).

    The two parts meet at two different Y levels:
      Wide half (+Z):   at skirt_bottom_y (original mating surface)
      Narrow half (-Z): step_height higher into the skirt
    The boundary follows the seam diagonal.
    """
    lower_end_y = skirt_bottom_y - lower_height - lower_cap_thickness - overcut

    # Oversized rectangular cutter: the 70x70 case lives inside the 100x100
    # span so the cut always pierces through to free air.
    cutter_extent = 50.0

    full_slab = (
        case_workplane(skirt_bottom_y)
        .rect(2 * cutter_extent, 2 * cutter_extent)
        .extrude(lower_end_y - skirt_bottom_y)
    )

    step_z = skirt_transition_z_end_plus + step_z_clearance
    narrow_box = [
        (-cutter_extent, -cutter_extent),
        (cutter_extent, -cutter_extent),
        (cutter_extent, step_z + overcut),
        (-cutter_extent, step_z + overcut),
    ]
    narrow_step = (
        case_workplane(narrow_split_y)
        .polyline(narrow_box).close()
        .extrude(skirt_bottom_y - narrow_split_y)
    )

    step_cutter = full_slab.union(narrow_step)

    base = combined.cut(step_cutter)
    cap = combined.intersect(step_cutter)
    return base, cap


def add_snap_fits(base, cap):
    """Snap-fit ramps on four interior walls where base meets cap."""
    snap_plus_z_inner = pos_z_face_z - wall_thickness
    snap_minus_z_inner = center_z - footprint_half_extent + wall_thickness
    snap_plus_x_narrow_inner = center_x + footprint_half_extent - wall_thickness
    snap_minus_x_narrow_inner = center_x - footprint_half_extent + wall_thickness

    yz_zone_range = (center_x - snap_zone_width / 2, center_x + snap_zone_width / 2)
    xy_narrow_zone_start = center_z - skirt_narrow_half_extent + corner_r + 0.5
    xy_narrow_zone_range = (xy_narrow_zone_start, xy_narrow_zone_start + snap_zone_width)

    snap_faces = [
        (snap_plus_z_inner, +1, skirt_bottom_y, "YZ", yz_zone_range),
        (snap_minus_z_inner, -1, narrow_split_y, "YZ", yz_zone_range),
        (snap_plus_x_narrow_inner, +1, narrow_split_y, "XY", xy_narrow_zone_range),
        (snap_minus_x_narrow_inner, -1, narrow_split_y, "XY", xy_narrow_zone_range),
    ]

    for inner_face, sign, split_y, plane, zone_range in snap_faces:
        base_frame = Frame(extrusion_plane=plane, outward_sign=sign,
                           up_axis="Y", up_sign=-1)
        cap_frame = Frame(extrusion_plane=plane, outward_sign=sign,
                          up_axis="Y", up_sign=+1)
        base = apply_ramp_out_first(
            base,
            frame=base_frame,
            inner_wall_at=inner_face,
            wall_top_at=split_y,
            wall_height=snap_wall_height,
            zone_range=zone_range,
            deflection_distance=snap_deflection,
        )
        cap = apply_ramp_in_first(
            cap,
            frame=cap_frame,
            inner_wall_at=inner_face,
            wall_top_at=split_y,
            wall_height=snap_wall_height,
            zone_range=zone_range,
            deflection_distance=snap_deflection,
        )

    return base, cap


def add_pogo_pocket(base):
    """Stepped pill pocket on the +Z face with an outward pill ridge for pogo mating."""
    pogo_y = skirt_bottom_y + pogo_y_offset

    ridge = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=pos_z_face_z)
        .center(center_x, pogo_y)
        .slot2D(pogo_ridge_length, pogo_ridge_width)
        .extrude(pogo_ridge_depth)
    )
    base = base.union(ridge)

    outer_step = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=pos_z_face_z + pogo_ridge_depth + overcut)
        .center(center_x, pogo_y)
        .slot2D(pogo_outer_length, pogo_outer_width)
        .extrude(-(pogo_outer_depth + overcut))
    )
    inner_step = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=pos_z_face_z + overcut)
        .center(center_x, pogo_y)
        .slot2D(pogo_inner_length, pogo_inner_width)
        .extrude(-(wall_thickness + 2 * overcut))
    )
    return base.cut(outer_step).cut(inner_step)


# Assembly

def build_pump_case():
    solid = build_base_plate_with_ramp()
    solid = solid.union(build_skirt())
    solid = add_bore_wall(solid)
    solid = cut_mounting_holes(solid)
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


if __name__ == "__main__":
    main()
