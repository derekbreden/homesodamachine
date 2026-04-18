"""
Pump case: two-piece snap-fit enclosure for a peristaltic pump.

The case is built as one combined solid, then split with a stepped cut
into a base and a cap.

Base: base plate with octagon-to-footprint ramp, octagon pump bore,
      M3 mounting holes, a cylindrical tower below, and a pogo connector pocket.
Cap:  asymmetric flared skirt (wide on +Z, narrow on -Z) with a lower
      extension that tapers to uniform width.

The two parts mate at a stepped split surface and lock together with
snap-fit ramps on four interior walls.
"""

from pathlib import Path
import math
import sys

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cadlib"))
from snap import apply_ramp_out_first, apply_ramp_in_first


# ═══════════════════════════════════════════════════════
# PHYSICAL DIMENSIONS
# ═══════════════════════════════════════════════════════

FOOTPRINT_X = 70.0
FOOTPRINT_Z = 70.0
CORNER_R = 6.0
WALL_THICKNESS = 3.0

CENTER_X = FOOTPRINT_X / 2
CENTER_Z = FOOTPRINT_Z / 2

BASE_THICKNESS = 3.0
RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT = 18.0

# ── Skirt ──
SKIRT_UPPER_HEIGHT = 21.0
SKIRT_WALL = WALL_THICKNESS
SKIRT_WIDE_FLARE_PER_SIDE = 3.0
SKIRT_NARROW_TAPER_PER_SIDE = 4.0
SKIRT_WIDE_STRAIGHT_HEIGHT = 4.5

# ── Pump bore ──
BORE_SQUARE_SIDE = 43.0
LEDGE_DEPTH = 1.5
LEDGE_SHELF_SPAN = 26.03

BORE_HALF_DIAG = BORE_SQUARE_SIDE * math.sqrt(2) / 2
BORE_HALF_SPAN = 53.0 / 2

VERTEX_FAR = BORE_HALF_SPAN
VERTEX_NEAR = BORE_HALF_DIAG - BORE_HALF_SPAN

# ── M3 mounting holes ──
HOLE_R = 3.3 / 2.0
HOLE_POSITIONS = [
    (CENTER_X - 25.0, CENTER_Z + 25.0),
    (CENTER_X + 25.0, CENTER_Z + 25.0),
    (CENTER_X + 25.0, CENTER_Z - 25.0),
    (CENTER_X - 25.0, CENTER_Z - 25.0),
]

# ── Tower ──
TOWER_HEIGHT = 60.0
PLATFORM_THICKNESS = 3.0
CAP_THICKNESS = 3.0
CYLINDER_ID = 37.0
CYLINDER_OD = CYLINDER_ID + 2 * WALL_THICKNESS
CYLINDER_R_OUTER = CYLINDER_OD / 2
CYLINDER_R_INNER = CYLINDER_ID / 2

# ── Lower extension ──
LOWER_HEIGHT = 23.0
LOWER_CAP_THICKNESS = 3.0
LOWER_FOOTPRINT_STRAIGHT = SKIRT_WIDE_STRAIGHT_HEIGHT

# ── Stepped split ──
STEP_HEIGHT = 19.0
STEP_Z_CLEARANCE = 6.0

# ── Snap fits ──
SNAP_ZONE_WIDTH = 20.0
SNAP_WALL_HEIGHT = 9.0
SNAP_DEFLECTION = 1.5

# ── Arch notches ──
ARCH_RADIUS = 4.5

# ── Pogo connector ──
POGO_OUTER_LENGTH = 12.5
POGO_OUTER_WIDTH = 4.0
POGO_OUTER_DEPTH = 1.0
POGO_INNER_LENGTH = 14.5
POGO_INNER_WIDTH = 4.0
POGO_Y_OFFSET = 13.5          # offset above SKIRT_BOTTOM_Y (was implicit 10)
POGO_RIDGE_LENGTH = 24.5
POGO_RIDGE_WIDTH = 10.0
POGO_RIDGE_DEPTH = 1.0

# ── Shared constants ──
OVERCUT = 0.1
ARC_SEGMENTS = 8


# ═══════════════════════════════════════════════════════
# DERIVED GEOMETRY
# ═══════════════════════════════════════════════════════

OCTAGON_WALL_OUTER_EXTENT = VERTEX_FAR + WALL_THICKNESS

TOWER_BASE_Y = -(BASE_THICKNESS + RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT)
RAMP_FROM_OCTAGON_TO_CYLINDER_HEIGHT = OCTAGON_WALL_OUTER_EXTENT - CYLINDER_R_OUTER
OCTAGON_TO_CYLINDER_SCALE = CYLINDER_R_OUTER / OCTAGON_WALL_OUTER_EXTENT

FOOTPRINT_HALF_EXTENT = FOOTPRINT_X / 2


# ═══════════════════════════════════════════════════════
# POLYGON GENERATORS
# ═══════════════════════════════════════════════════════

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
    vf = VERTEX_FAR
    vn = VERTEX_NEAR

    vertices = [
        ( vn,  vf), ( vf,  vn), ( vf, -vn), ( vn, -vf),
        (-vn, -vf), (-vf, -vn), (-vf,  vn), (-vn,  vf),
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

        ledge_ramp_length = LEDGE_DEPTH * math.sqrt(2)
        entry_length = (edge_length - LEDGE_SHELF_SPAN) / 2
        shelf_length = LEDGE_SHELF_SPAN - 2 * LEDGE_DEPTH

        t = Turtle(start_x, start_z, edge_heading)
        t.forward(entry_length)
        if inward_is_left:
            t.left(45);  t.forward(ledge_ramp_length); t.right(45)
            t.forward(shelf_length)
            t.right(45); t.forward(ledge_ramp_length); t.left(45)
        else:
            t.right(45); t.forward(ledge_ramp_length); t.left(45)
            t.forward(shelf_length)
            t.left(45);  t.forward(ledge_ramp_length); t.right(45)
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


def rounded_rect_profile(width, height, radius, n=ARC_SEGMENTS):
    """Polygon points for a rounded rectangle centered at origin."""
    hw, hh = width / 2, height / 2
    pts = []
    corners = [
        ( hw - radius,  hh - radius,   0,  90),
        (-hw + radius,  hh - radius,  90, 180),
        (-hw + radius, -hh + radius, 180, 270),
        ( hw - radius, -hh + radius, 270, 360),
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
                        n=ARC_SEGMENTS):
    """Asymmetric profile: wider on +Z, narrower on -Z, with diagonal transitions.

    The +Z half and -Z half can flare/taper independently.  Transition Z
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


# ═══════════════════════════════════════════════════════
# BORE PROFILES (shared by bore construction and tower)
# ═══════════════════════════════════════════════════════

BORE_PROFILE = bore_octagon_profile()
BORE_WALL_PROFILE = offset_polygon(BORE_PROFILE, WALL_THICKNESS)
BORE_WALL_PROFILE_AT_CYLINDER = [
    (x * OCTAGON_TO_CYLINDER_SCALE, z * OCTAGON_TO_CYLINDER_SCALE)
    for x, z in BORE_WALL_PROFILE
]


# ═══════════════════════════════════════════════════════
# SKIRT PROFILES (shared by skirt, lower extension, split, and snap fits)
# ═══════════════════════════════════════════════════════

def compute_skirt_profiles():
    """Compute the outer and inner profiles at each Y-level of the skirt.

    The skirt splits asymmetrically: +Z half flares outward (70→76),
    -Z half tapers inward (70→62).  Both are at 45 degrees.  The
    transition wall stays in a fixed vertical plane by tracking each
    endpoint's Z independently.

    Returns (outer_profiles, inner_profiles, y_steps).
    """
    base_half_extent = FOOTPRINT_HALF_EXTENT
    base_radius = CORNER_R
    wall = SKIRT_WALL

    wide_half_extent = base_half_extent + SKIRT_WIDE_FLARE_PER_SIDE
    narrow_half_extent = base_half_extent - SKIRT_NARROW_TAPER_PER_SIDE

    # At the moment the wide flare completes (3mm), the narrow side
    # has only tapered by 3 of its 4mm
    mid_narrow_half_extent = base_half_extent - SKIRT_WIDE_FLARE_PER_SIDE

    # Narrow straight section is shorter so both halves land together
    narrow_straight_height = (
        SKIRT_WIDE_STRAIGHT_HEIGHT
        - (SKIRT_NARROW_TAPER_PER_SIDE - SKIRT_WIDE_FLARE_PER_SIDE)
    )

    # Transition Z coordinates keep the seam wall in the vertical plane
    # X + Z = -base_half_extent at every Y level
    tz_symmetric_plus  =  0.01
    tz_symmetric_minus = -0.01
    tz_mid_plus  =  SKIRT_WIDE_FLARE_PER_SIDE
    tz_mid_minus = -SKIRT_WIDE_FLARE_PER_SIDE
    tz_end_plus  =  SKIRT_WIDE_FLARE_PER_SIDE
    tz_end_minus = -SKIRT_NARROW_TAPER_PER_SIDE

    outer_profiles = [
        split_skirt_profile(base_half_extent, base_radius,
                            base_half_extent, base_radius,
                            tz_symmetric_plus, tz_symmetric_minus),
        split_skirt_profile(base_half_extent, base_radius,
                            base_half_extent, base_radius,
                            tz_symmetric_plus, tz_symmetric_minus),
        split_skirt_profile(wide_half_extent, base_radius,
                            mid_narrow_half_extent, base_radius,
                            tz_mid_plus, tz_mid_minus,
                            wide_half_extent_z=base_half_extent,
                            narrow_half_extent_z=base_half_extent),
        split_skirt_profile(wide_half_extent, base_radius,
                            narrow_half_extent, base_radius,
                            tz_end_plus, tz_end_minus,
                            wide_half_extent_z=base_half_extent,
                            narrow_half_extent_z=base_half_extent),
        split_skirt_profile(wide_half_extent, base_radius,
                            narrow_half_extent, base_radius,
                            tz_end_plus, tz_end_minus,
                            wide_half_extent_z=base_half_extent,
                            narrow_half_extent_z=base_half_extent),
    ]

    # Inner profiles: wall thickness inward from each half-extent and radius.
    # The seam diagonal is at 45 deg, so a wall-thickness X-offset only gives
    # wall/sqrt(2) perpendicular thickness.  Shift inner transition Z values
    # so the inner seam plane is a full wall-thickness perpendicular from outer.
    inner_base_half_extent = base_half_extent - wall
    inner_base_radius = base_radius - wall
    inner_wide_half_extent = wide_half_extent - wall
    inner_wide_radius = base_radius - wall
    inner_narrow_half_extent = narrow_half_extent - wall
    inner_narrow_radius = base_radius - wall
    inner_mid_narrow_half_extent = mid_narrow_half_extent - wall
    inner_mid_narrow_radius = base_radius - wall

    seam_z_shift = wall * (math.sqrt(2) - 1)
    itz_symmetric_plus  = tz_symmetric_plus
    itz_symmetric_minus = tz_symmetric_minus
    itz_mid_plus  = tz_mid_plus  + seam_z_shift
    itz_mid_minus = tz_mid_minus + seam_z_shift
    itz_end_plus  = tz_end_plus  + seam_z_shift
    itz_end_minus = tz_end_minus + seam_z_shift

    inner_profiles = [
        split_skirt_profile(inner_base_half_extent, inner_base_radius,
                            inner_base_half_extent, inner_base_radius,
                            itz_symmetric_plus, itz_symmetric_minus),
        split_skirt_profile(inner_base_half_extent, inner_base_radius,
                            inner_base_half_extent, inner_base_radius,
                            itz_symmetric_plus, itz_symmetric_minus),
        split_skirt_profile(inner_wide_half_extent, inner_wide_radius,
                            inner_mid_narrow_half_extent, inner_mid_narrow_radius,
                            itz_mid_plus, itz_mid_minus,
                            wide_half_extent_z=inner_base_half_extent,
                            narrow_half_extent_z=inner_base_half_extent),
        split_skirt_profile(inner_wide_half_extent, inner_wide_radius,
                            inner_narrow_half_extent, inner_narrow_radius,
                            itz_end_plus, itz_end_minus,
                            wide_half_extent_z=inner_base_half_extent,
                            narrow_half_extent_z=inner_base_half_extent),
        split_skirt_profile(inner_wide_half_extent, inner_wide_radius,
                            inner_narrow_half_extent, inner_narrow_radius,
                            itz_end_plus, itz_end_minus,
                            wide_half_extent_z=inner_base_half_extent,
                            narrow_half_extent_z=inner_base_half_extent),
    ]

    y_steps = [
        SKIRT_UPPER_HEIGHT,
        SKIRT_WIDE_FLARE_PER_SIDE,
        SKIRT_NARROW_TAPER_PER_SIDE - SKIRT_WIDE_FLARE_PER_SIDE,
        narrow_straight_height,
    ]

    return outer_profiles, inner_profiles, y_steps, narrow_half_extent, tz_end_plus


SKIRT_OUTER_PROFILES, SKIRT_INNER_PROFILES, SKIRT_Y_STEPS, \
    SKIRT_NARROW_HALF_EXTENT, SKIRT_TRANSITION_Z_END_PLUS = compute_skirt_profiles()

SKIRT_BOTTOM_OFFSET = sum(SKIRT_Y_STEPS)
SKIRT_BOTTOM_Y = -SKIRT_BOTTOM_OFFSET


# ═══════════════════════════════════════════════════════
# FEATURE FUNCTIONS — BASE PLATE AND BORE
# ═══════════════════════════════════════════════════════

def build_base_plate_with_ramp():
    """Ramped platform from the 70x70 footprint down to the octagon bore."""
    footprint = rounded_rect_profile(FOOTPRINT_X, FOOTPRINT_Z, CORNER_R)
    footprint_at_ramp_bottom = rounded_rect_profile(
        FOOTPRINT_X - 2 * RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT,
        FOOTPRINT_Z - 2 * RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT,
        CORNER_R)

    return (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(CENTER_X, CENTER_Z)
        .polyline(footprint).close()
        .workplane(offset=-BASE_THICKNESS)
        .polyline(footprint).close()
        .workplane(offset=-RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT)
        .polyline(footprint_at_ramp_bottom).close()
        .loft(ruled=True)
    )


def add_bore_wall_and_cut_bore(solid):
    """Add octagon bore wall, then cut the bore cavity."""
    bore_depth = BASE_THICKNESS + RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT

    bore_wall = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(CENTER_X, CENTER_Z)
        .polyline(BORE_WALL_PROFILE).close()
        .extrude(-bore_depth)
    )
    solid = solid.union(bore_wall)

    bore_cavity = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(CENTER_X, CENTER_Z)
        .polyline(BORE_PROFILE).close()
        .extrude(-(bore_depth + OVERCUT))
    )
    return solid.cut(bore_cavity)


def cut_mounting_holes(solid):
    """M3 mounting holes through the base plate and bore wall."""
    bore_depth = BASE_THICKNESS + RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT

    for hx, hz in HOLE_POSITIONS:
        hole = (
            cq.Workplane("XZ")
            .workplane(offset=0)
            .center(hx, hz)
            .circle(HOLE_R)
            .extrude(-(bore_depth + OVERCUT))
        )
        solid = solid.cut(hole)
    return solid


# ═══════════════════════════════════════════════════════
# FEATURE FUNCTIONS — SKIRT
# ═══════════════════════════════════════════════════════

def build_skirt():
    """Asymmetric flared skirt: wide on +Z, narrow on -Z."""
    skirt_outer = cq.Workplane("XZ").workplane(offset=0).center(CENTER_X, CENTER_Z)
    skirt_outer = skirt_outer.polyline(SKIRT_OUTER_PROFILES[0]).close()
    for step, profile in zip(SKIRT_Y_STEPS, SKIRT_OUTER_PROFILES[1:]):
        skirt_outer = skirt_outer.workplane(offset=step).polyline(profile).close()
    skirt_outer = skirt_outer.loft(ruled=True)

    skirt_cavity = cq.Workplane("XZ").workplane(offset=0).center(CENTER_X, CENTER_Z)
    skirt_cavity = skirt_cavity.polyline(SKIRT_INNER_PROFILES[0]).close()
    for i, (step, profile) in enumerate(zip(SKIRT_Y_STEPS, SKIRT_INNER_PROFILES[1:])):
        extra = OVERCUT if i == len(SKIRT_Y_STEPS) - 1 else 0
        skirt_cavity = skirt_cavity.workplane(offset=step + extra).polyline(profile).close()
    skirt_cavity = skirt_cavity.loft(ruled=True)

    return skirt_outer.cut(skirt_cavity)


# ═══════════════════════════════════════════════════════
# FEATURE FUNCTIONS — TOWER
# ═══════════════════════════════════════════════════════

def build_tower():
    """Octagon platform, octagon-to-cylinder ramp, and cylindrical tower."""
    tower_platform = (
        cq.Workplane("XZ")
        .workplane(offset=TOWER_BASE_Y)
        .center(CENTER_X, CENTER_Z)
        .polyline(BORE_WALL_PROFILE).close()
        .extrude(-PLATFORM_THICKNESS)
    )

    tower_ramp = (
        cq.Workplane("XZ")
        .workplane(offset=TOWER_BASE_Y - PLATFORM_THICKNESS)
        .center(CENTER_X, CENTER_Z)
        .polyline(BORE_WALL_PROFILE).close()
        .workplane(offset=-RAMP_FROM_OCTAGON_TO_CYLINDER_HEIGHT)
        .polyline(BORE_WALL_PROFILE_AT_CYLINDER).close()
        .loft(ruled=True)
    )

    tower_cylinder = (
        cq.Workplane("XZ")
        .workplane(offset=TOWER_BASE_Y)
        .center(CENTER_X, CENTER_Z)
        .circle(CYLINDER_R_OUTER)
        .extrude(-TOWER_HEIGHT)
    )

    tower = tower_platform.union(tower_ramp).union(tower_cylinder)

    tower_bore_depth = TOWER_HEIGHT - CAP_THICKNESS
    tower_bore = (
        cq.Workplane("XZ")
        .workplane(offset=TOWER_BASE_Y + OVERCUT)
        .center(CENTER_X, CENTER_Z)
        .circle(CYLINDER_R_INNER)
        .extrude(-(tower_bore_depth + OVERCUT))
    )
    return tower.cut(tower_bore)


# ═══════════════════════════════════════════════════════
# FEATURE FUNCTIONS — LOWER EXTENSION
# ═══════════════════════════════════════════════════════

def build_lower_extension():
    """Lower portion extending from skirt bottom: taper to uniform, then cap."""
    lower_ramp_height = (FOOTPRINT_HALF_EXTENT + SKIRT_WIDE_FLARE_PER_SIDE
                         - SKIRT_NARROW_HALF_EXTENT)
    lower_uniform_straight = (LOWER_HEIGHT - lower_ramp_height
                              - LOWER_FOOTPRINT_STRAIGHT)

    inner_narrow_half_extent = SKIRT_NARROW_HALF_EXTENT - SKIRT_WALL
    inner_narrow_radius = CORNER_R - SKIRT_WALL
    inner_base_half_extent = FOOTPRINT_HALF_EXTENT - SKIRT_WALL

    lower_outer_profiles = [
        SKIRT_OUTER_PROFILES[-1],
        SKIRT_OUTER_PROFILES[-1],
        split_skirt_profile(SKIRT_NARROW_HALF_EXTENT, CORNER_R,
                            SKIRT_NARROW_HALF_EXTENT, CORNER_R,
                            0.01, -0.01,
                            wide_half_extent_z=FOOTPRINT_HALF_EXTENT,
                            narrow_half_extent_z=FOOTPRINT_HALF_EXTENT),
        split_skirt_profile(SKIRT_NARROW_HALF_EXTENT, CORNER_R,
                            SKIRT_NARROW_HALF_EXTENT, CORNER_R,
                            0.01, -0.01,
                            wide_half_extent_z=FOOTPRINT_HALF_EXTENT,
                            narrow_half_extent_z=FOOTPRINT_HALF_EXTENT),
    ]

    lower_inner_profiles = [
        SKIRT_INNER_PROFILES[-1],
        SKIRT_INNER_PROFILES[-1],
        split_skirt_profile(inner_narrow_half_extent, inner_narrow_radius,
                            inner_narrow_half_extent, inner_narrow_radius,
                            0.01, -0.01,
                            wide_half_extent_z=inner_base_half_extent,
                            narrow_half_extent_z=inner_base_half_extent),
        split_skirt_profile(inner_narrow_half_extent, inner_narrow_radius,
                            inner_narrow_half_extent, inner_narrow_radius,
                            0.01, -0.01,
                            wide_half_extent_z=inner_base_half_extent,
                            narrow_half_extent_z=inner_base_half_extent),
    ]

    lower_y_steps = [LOWER_FOOTPRINT_STRAIGHT, lower_ramp_height,
                     lower_uniform_straight]

    lower_outer = (
        cq.Workplane("XZ")
        .workplane(offset=SKIRT_BOTTOM_OFFSET)
        .center(CENTER_X, CENTER_Z)
    )
    lower_outer = lower_outer.polyline(lower_outer_profiles[0]).close()
    for step, prof in zip(lower_y_steps, lower_outer_profiles[1:]):
        lower_outer = lower_outer.workplane(offset=step).polyline(prof).close()
    lower_outer = lower_outer.loft(ruled=True)

    lower_inner = (
        cq.Workplane("XZ")
        .workplane(offset=SKIRT_BOTTOM_OFFSET)
        .center(CENTER_X, CENTER_Z)
    )
    lower_inner = lower_inner.polyline(lower_inner_profiles[0]).close()
    for i, (step, prof) in enumerate(zip(lower_y_steps, lower_inner_profiles[1:])):
        extra = OVERCUT if i == len(lower_y_steps) - 1 else 0
        lower_inner = lower_inner.workplane(offset=step + extra).polyline(prof).close()
    lower_inner = lower_inner.loft(ruled=True)

    lower_shell = lower_outer.cut(lower_inner)

    lower_cap_offset = SKIRT_BOTTOM_OFFSET + LOWER_HEIGHT
    lower_cap = (
        cq.Workplane("XZ")
        .workplane(offset=lower_cap_offset)
        .center(CENTER_X, CENTER_Z)
        .polyline(lower_outer_profiles[-1]).close()
        .extrude(LOWER_CAP_THICKNESS)
    )
    return lower_shell.union(lower_cap)


# ═══════════════════════════════════════════════════════
# FEATURE FUNCTIONS — ARCH NOTCHES, SPLIT, SNAPS
# ═══════════════════════════════════════════════════════

def cut_arch_notches(combined):
    """Semicircular notches on the +Z face for wire routing."""
    z_face_outer = CENTER_Z + FOOTPRINT_HALF_EXTENT
    arch_hole_xs = [
        CORNER_R + ARCH_RADIUS - 4,
        FOOTPRINT_X - CORNER_R - ARCH_RADIUS + 4,
    ]

    for ax in arch_hole_xs:
        arch_cutter = (
            cq.Workplane("XY")
            .workplane(offset=z_face_outer + OVERCUT)
            .center(ax, SKIRT_BOTTOM_Y)
            .circle(ARCH_RADIUS)
            .extrude(-(SKIRT_WALL + 3 + OVERCUT))
        )
        combined = combined.cut(arch_cutter)
    return combined


def split_into_base_and_cap(combined):
    """Stepped split creating base (with tower) and cap (with lower extension).

    The two parts meet at two different Y levels:
      Wide half (+Z):   at skirt_bottom_offset (original mating surface)
      Narrow half (-Z): STEP_HEIGHT higher into the skirt
    The boundary follows the seam diagonal.
    """
    step_offset = SKIRT_BOTTOM_OFFSET - STEP_HEIGHT
    lower_end_offset = SKIRT_BOTTOM_OFFSET + LOWER_HEIGHT + LOWER_CAP_THICKNESS + OVERCUT

    full_slab = (
        cq.Workplane("XZ")
        .workplane(offset=SKIRT_BOTTOM_OFFSET)
        .center(CENTER_X, CENTER_Z)
        .rect(100, 100)
        .extrude(lower_end_offset - SKIRT_BOTTOM_OFFSET)
    )

    step_z = SKIRT_TRANSITION_Z_END_PLUS + STEP_Z_CLEARANCE
    narrow_box = [(-50, -50), (50, -50), (50, step_z + OVERCUT), (-50, step_z + OVERCUT)]
    narrow_step = (
        cq.Workplane("XZ")
        .workplane(offset=step_offset)
        .center(CENTER_X, CENTER_Z)
        .polyline(narrow_box).close()
        .extrude(SKIRT_BOTTOM_OFFSET - step_offset)
    )

    step_cutter = full_slab.union(narrow_step)

    base = combined.cut(step_cutter)
    cap = combined.intersect(step_cutter)
    return base, cap


def add_snap_fits(base, cap):
    """Snap-fit ramps on four interior walls where base meets cap."""
    step_offset = SKIRT_BOTTOM_OFFSET - STEP_HEIGHT

    snap_plus_z_inner = CENTER_Z + FOOTPRINT_HALF_EXTENT - WALL_THICKNESS
    snap_minus_z_inner = CENTER_Z - FOOTPRINT_HALF_EXTENT + WALL_THICKNESS
    snap_plus_x_narrow_inner = CENTER_X + FOOTPRINT_HALF_EXTENT - WALL_THICKNESS
    snap_minus_x_narrow_inner = CENTER_X - FOOTPRINT_HALF_EXTENT + WALL_THICKNESS

    wide_split_y = -SKIRT_BOTTOM_OFFSET
    narrow_split_y = -step_offset

    yz_zone_start = CENTER_X - SNAP_ZONE_WIDTH / 2
    yz_zone_end = CENTER_X + SNAP_ZONE_WIDTH / 2
    xy_narrow_zone_start = CENTER_Z - SKIRT_NARROW_HALF_EXTENT + CORNER_R + 0.5
    xy_narrow_zone_end = xy_narrow_zone_start + SNAP_ZONE_WIDTH

    snap_faces = [
        (snap_plus_z_inner,         +1, wide_split_y,    "YZ",
         yz_zone_start, yz_zone_end, SNAP_WALL_HEIGHT),
        (snap_minus_z_inner,        -1, narrow_split_y,  "YZ",
         yz_zone_start, yz_zone_end, SNAP_WALL_HEIGHT),
        (snap_plus_x_narrow_inner,  +1, narrow_split_y,  "XY",
         xy_narrow_zone_start, xy_narrow_zone_end, SNAP_WALL_HEIGHT),
        (snap_minus_x_narrow_inner, -1, narrow_split_y,  "XY",
         xy_narrow_zone_start, xy_narrow_zone_end, SNAP_WALL_HEIGHT),
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
            deflection_distance=SNAP_DEFLECTION,
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
            deflection_distance=SNAP_DEFLECTION,
        )

    return base, cap


# ═══════════════════════════════════════════════════════
# FEATURE FUNCTIONS — POGO CONNECTOR POCKET
# ═══════════════════════════════════════════════════════

def add_pogo_pocket(base):
    """Stepped pill pocket on the +Z face with an outward pill ridge for pogo mating."""
    z_face_outer = CENTER_Z + FOOTPRINT_HALF_EXTENT
    pogo_y = SKIRT_BOTTOM_Y + POGO_Y_OFFSET

    ridge = (
        cq.Workplane("XY")
        .workplane(offset=z_face_outer)
        .center(CENTER_X, pogo_y)
        .slot2D(POGO_RIDGE_LENGTH, POGO_RIDGE_WIDTH)
        .extrude(POGO_RIDGE_DEPTH)
    )
    base = base.union(ridge)

    outer_step = (
        cq.Workplane("XY")
        .workplane(offset=z_face_outer + POGO_RIDGE_DEPTH + OVERCUT)
        .center(CENTER_X, pogo_y)
        .slot2D(POGO_OUTER_LENGTH, POGO_OUTER_WIDTH)
        .extrude(-(POGO_OUTER_DEPTH + OVERCUT))
    )
    inner_step = (
        cq.Workplane("XY")
        .workplane(offset=z_face_outer + OVERCUT)
        .center(CENTER_X, pogo_y)
        .slot2D(POGO_INNER_LENGTH, POGO_INNER_WIDTH)
        .extrude(-(WALL_THICKNESS + 2 * OVERCUT))
    )
    return base.cut(outer_step).cut(inner_step)


# ═══════════════════════════════════════════════════════
# ASSEMBLY
# ═══════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

base, cap = build_pump_case()

for name, part in [("Base", base), ("Cap", cap)]:
    solids = part.solids().vals()
    print(f"{name}: {len(solids)} solid(s)")
    for i, s in enumerate(solids):
        bb = s.BoundingBox()
        print(f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
              f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")

OUTPUT_DIR = Path(__file__).resolve().parent
cq.exporters.export(base, str(OUTPUT_DIR / "pump-case-base-cadquery.step"))
print("Exported → pump-case-base-cadquery.step")
cq.exporters.export(cap, str(OUTPUT_DIR / "pump-case-cap-cadquery.step"))
print("Exported → pump-case-cap-cadquery.step")
