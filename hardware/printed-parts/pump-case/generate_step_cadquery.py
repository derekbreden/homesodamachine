from pathlib import Path
import math

import cadquery as cq

# ── Footprint ──
FOOTPRINT_X = 70.0
FOOTPRINT_Z = 70.0
CORNER_R = 6.0
WALL_THICKNESS = 3.0

CENTER_X = FOOTPRINT_X / 2
CENTER_Z = FOOTPRINT_Z / 2

# ── Outer ramp (must reach octagon wall at rounded-corner diagonal) ──
BASE_THICKNESS = 3.0
RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT = 18.0

# ── Skirt ──
SKIRT_UPPER_HEIGHT = 21.0
SKIRT_THICKNESS = 3.0
SKIRT_FLARE_PER_SIDE = 3.0
SKIRT_FLARE_HEIGHT = SKIRT_FLARE_PER_SIDE  # 45 degrees
SKIRT_LOWER_HEIGHT = 10.0

# ── Pump bore geometry ──
# The bore is a 43mm square rotated 45 degrees, then trimmed to an octagon
# spanning 53mm corner-to-corner. Each long edge has a ledge indentation.
BORE_SQUARE_SIDE = 43.0
LEDGE_DEPTH = 1.5
LEDGE_SHELF_SPAN = 26.03

BORE_HALF_DIAG = BORE_SQUARE_SIDE * math.sqrt(2) / 2
BORE_HALF_SPAN = 53.0 / 2

# Each octagon vertex sits at (vertex_near, vertex_far) or (vertex_far, vertex_near)
VERTEX_FAR  = BORE_HALF_SPAN
VERTEX_NEAR = BORE_HALF_DIAG - BORE_HALF_SPAN

# ── M3 mounting holes ── 50mm square pattern centered on pump
HOLE_R = 3.3 / 2.0
HOLE_POSITIONS = [
    (CENTER_X - 25.0, CENTER_Z + 25.0),
    (CENTER_X + 25.0, CENTER_Z + 25.0),
    (CENTER_X + 25.0, CENTER_Z - 25.0),
    (CENTER_X - 25.0, CENTER_Z - 25.0),
]

# ── Shared constants ──
OVERCUT = 0.1
ARC_SEGMENTS = 8


# ── Polygon generators ──

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
    """Return the pump bore octagon (with ledge indentations) as (x, z) points
    centered at the origin."""
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

        # Determine which side of this edge faces the bore center
        mid_x, mid_z = (start_x + end_x) / 2, (start_z + end_z) / 2
        unit_x, unit_z = edge_dx / edge_length, edge_dz / edge_length
        normal_x, normal_z = unit_z, -unit_x
        if normal_x * (-mid_x) + normal_z * (-mid_z) < 0:
            normal_x, normal_z = -normal_x, -normal_z
        inward_is_left = (normal_x * (-unit_z) + normal_z * unit_x) > 0

        # Ledge profile: flat entry → 45° ramp in → shelf → 45° ramp out → flat exit
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
    """Offset each edge of a closed polygon outward (left-normal direction)
    by distance, returning new vertices at the intersections of adjacent
    offset edges."""
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
    """Return polygon points for a rounded rectangle centered at origin."""
    hw, hh = width / 2, height / 2
    pts = []
    corners = [
        ( hw - radius,  hh - radius,   0,  90),
        (-hw + radius,  hh - radius,  90, 180),
        (-hw + radius, -hh + radius, 180, 270),
        ( hw - radius, -hh + radius, 270, 360),
    ]
    for cx, cz, start_deg, end_deg in corners:
        for i in range(n):
            angle = math.radians(start_deg + (end_deg - start_deg) * i / n)
            pts.append((cx + radius * math.cos(angle), cz + radius * math.sin(angle)))
    return pts


OCTAGON_WALL_OUTER_EXTENT = VERTEX_FAR + WALL_THICKNESS

# ── Tower geometry (octagon → cylinder transition above the case) ──
TOWER_HEIGHT = 60.0
PLATFORM_THICKNESS = 3.0
CAP_THICKNESS = 3.0
CYLINDER_ID = 37.0
CYLINDER_OD = CYLINDER_ID + 2 * WALL_THICKNESS
CYLINDER_R_OUTER = CYLINDER_OD / 2
CYLINDER_R_INNER = CYLINDER_ID / 2

RAMP_FROM_OCTAGON_TO_CYLINDER_HEIGHT = OCTAGON_WALL_OUTER_EXTENT - CYLINDER_R_OUTER
OCTAGON_TO_CYLINDER_SCALE = CYLINDER_R_OUTER / OCTAGON_WALL_OUTER_EXTENT


# ── Build the solid ──

footprint       = rounded_rect_profile(FOOTPRINT_X, FOOTPRINT_Z, CORNER_R)
footprint_after_ramp = rounded_rect_profile(
    FOOTPRINT_X - 2 * RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT, FOOTPRINT_Z - 2 * RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT, CORNER_R)

solid = (
    cq.Workplane("XZ")
    .workplane(offset=0)
    .center(CENTER_X, CENTER_Z)
    .polyline(footprint).close()
    .workplane(offset=-BASE_THICKNESS)
    .polyline(footprint).close()
    .workplane(offset=-RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT)
    .polyline(footprint_after_ramp).close()
    .loft(ruled=True)
)

# ── Skirt: upper (straight) + flare (45° outward) + lower (straight) ──

skirt_upper_inner = rounded_rect_profile(
    FOOTPRINT_X - 2 * SKIRT_THICKNESS,
    FOOTPRINT_Z - 2 * SKIRT_THICKNESS,
    CORNER_R - SKIRT_THICKNESS)

skirt_lower_x = FOOTPRINT_X + 2 * SKIRT_FLARE_PER_SIDE
skirt_lower_z = FOOTPRINT_Z + 2 * SKIRT_FLARE_PER_SIDE
skirt_lower_r = CORNER_R + SKIRT_FLARE_PER_SIDE
skirt_lower_outer = rounded_rect_profile(skirt_lower_x, skirt_lower_z, skirt_lower_r)
skirt_lower_inner = rounded_rect_profile(
    skirt_lower_x - 2 * SKIRT_THICKNESS,
    skirt_lower_z - 2 * SKIRT_THICKNESS,
    skirt_lower_r - SKIRT_THICKNESS)

# Outer shell: upper straight → flare → lower straight
skirt_outer = (
    cq.Workplane("XZ")
    .workplane(offset=0)
    .center(CENTER_X, CENTER_Z)
    .polyline(footprint).close()
    .workplane(offset=SKIRT_UPPER_HEIGHT)
    .polyline(footprint).close()
    .workplane(offset=SKIRT_FLARE_HEIGHT)
    .polyline(skirt_lower_outer).close()
    .workplane(offset=SKIRT_LOWER_HEIGHT)
    .polyline(skirt_lower_outer).close()
    .loft(ruled=True)
)

# Inner cavity: same structure, thinner profiles
skirt_cavity = (
    cq.Workplane("XZ")
    .workplane(offset=0)
    .center(CENTER_X, CENTER_Z)
    .polyline(skirt_upper_inner).close()
    .workplane(offset=SKIRT_UPPER_HEIGHT)
    .polyline(skirt_upper_inner).close()
    .workplane(offset=SKIRT_FLARE_HEIGHT)
    .polyline(skirt_lower_inner).close()
    .workplane(offset=SKIRT_LOWER_HEIGHT + OVERCUT)
    .polyline(skirt_lower_inner).close()
    .loft(ruled=True)
)

skirt = skirt_outer.cut(skirt_cavity)
solid = solid.union(skirt)

bore_profile = bore_octagon_profile()
wall_profile = offset_polygon(bore_profile, WALL_THICKNESS)

wall_prism = (
    cq.Workplane("XZ")
    .workplane(offset=0)
    .center(CENTER_X, CENTER_Z)
    .polyline(wall_profile).close()
    .extrude(-(BASE_THICKNESS + RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT))
)

solid = solid.union(wall_prism)
bore_cutter = (
    cq.Workplane("XZ")
    .workplane(offset=0)
    .center(CENTER_X, CENTER_Z)
    .polyline(bore_profile).close()
    .extrude(-(BASE_THICKNESS + RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT + OVERCUT))
)
solid = solid.cut(bore_cutter)

# M3 mounting holes
for hx, hz in HOLE_POSITIONS:
    hole_cutter = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(-(BASE_THICKNESS + RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT + OVERCUT))
    )
    solid = solid.cut(hole_cutter)

# ── Tower: octagon platform + ramp + cylinder + cap ──

tower_base_y = -(BASE_THICKNESS + RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT)

tower_platform = (
    cq.Workplane("XZ")
    .workplane(offset=tower_base_y)
    .center(CENTER_X, CENTER_Z)
    .polyline(wall_profile).close()
    .extrude(-PLATFORM_THICKNESS)
)

wall_profile_at_cylinder = [
    (x * OCTAGON_TO_CYLINDER_SCALE, z * OCTAGON_TO_CYLINDER_SCALE)
    for x, z in wall_profile
]

tower_ramp = (
    cq.Workplane("XZ")
    .workplane(offset=tower_base_y - PLATFORM_THICKNESS)
    .center(CENTER_X, CENTER_Z)
    .polyline(wall_profile).close()
    .workplane(offset=-RAMP_FROM_OCTAGON_TO_CYLINDER_HEIGHT)
    .polyline(wall_profile_at_cylinder).close()
    .loft(ruled=True)
)

tower_cylinder = (
    cq.Workplane("XZ")
    .workplane(offset=tower_base_y)
    .center(CENTER_X, CENTER_Z)
    .circle(CYLINDER_R_OUTER)
    .extrude(-TOWER_HEIGHT)
)

tower = tower_platform.union(tower_ramp).union(tower_cylinder)

tower_bore_depth = TOWER_HEIGHT - CAP_THICKNESS
tower_bore = (
    cq.Workplane("XZ")
    .workplane(offset=tower_base_y + OVERCUT)
    .center(CENTER_X, CENTER_Z)
    .circle(CYLINDER_R_INNER)
    .extrude(-(tower_bore_depth + OVERCUT))
)
tower = tower.cut(tower_bore)

solid = solid.union(tower)

# ── Export ──
OUTPUT_STEP = Path(__file__).resolve().parent / "pump-case-cadquery.step"
cq.exporters.export(solid, str(OUTPUT_STEP))
print(f"Exported → {OUTPUT_STEP}")
