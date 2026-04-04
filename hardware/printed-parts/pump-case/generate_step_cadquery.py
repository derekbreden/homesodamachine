from pathlib import Path
import math

import cadquery as cq

# ── Case envelope ──
CASE_X = 70.0           # width  (X axis)
CASE_Y = 18.0           # height (Y axis, vertical)
CASE_Z = 70.0           # depth  (Z axis)
BASE_THICKNESS = 3.0
WALL_THICKNESS = 3.0
RAMP_HEIGHT = CASE_Y - BASE_THICKNESS
CORNER_R = 6.0

CENTER_X = CASE_X / 2
CENTER_Z = CASE_Z / 2

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


def rounded_rect_profile(width, height, radius, n=ARC_SEGMENTS):
    """Return CCW polygon points for a rounded rectangle centered at origin.

    All calls must use the same n so the loft can match edges between sections.
    """
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


# ── Wall prism profile ──
# Offset the octagon outward by WALL_THICKNESS to define the minimum wall
# around the bore. Short edges shift straight out; 45-degree edges shift
# by a smaller amount at each vertex.
DIAGONAL_EDGE_VERTEX_OFFSET = WALL_THICKNESS * (math.sqrt(2) - 1)
WALL_OUTER_FAR  = VERTEX_FAR + WALL_THICKNESS
WALL_OUTER_NEAR = VERTEX_NEAR + DIAGONAL_EDGE_VERTEX_OFFSET

WALL_OCTAGON = [
    ( WALL_OUTER_NEAR,  WALL_OUTER_FAR),
    ( WALL_OUTER_FAR,   WALL_OUTER_NEAR),
    ( WALL_OUTER_FAR,  -WALL_OUTER_NEAR),
    ( WALL_OUTER_NEAR, -WALL_OUTER_FAR),
    (-WALL_OUTER_NEAR, -WALL_OUTER_FAR),
    (-WALL_OUTER_FAR,  -WALL_OUTER_NEAR),
    (-WALL_OUTER_FAR,   WALL_OUTER_NEAR),
    (-WALL_OUTER_NEAR,  WALL_OUTER_FAR),
]


# ── Build the solid ──

# Loft combines base plate and ramp in one shape:
#   y=0:  full footprint, R=6  (bottom of base plate)
#   y=3:  full footprint, R=6  (top of base plate — same shape keeps it flat)
#   y=18: ramp top, R=6        (45° inward from base)
ramp_top_size = CASE_X - 2 * RAMP_HEIGHT

base_profile = rounded_rect_profile(CASE_X, CASE_Z, CORNER_R)
top_profile  = rounded_rect_profile(ramp_top_size, ramp_top_size, CORNER_R)

solid = (
    cq.Workplane("XZ")
    .workplane(offset=0)
    .center(CENTER_X, CENTER_Z)
    .polyline(base_profile).close()
    .workplane(offset=-BASE_THICKNESS)
    .polyline(base_profile).close()
    .workplane(offset=-RAMP_HEIGHT)
    .polyline(top_profile).close()
    .loft()
)

# Wall prism ensures minimum wall thickness around bore at all heights
wall_prism = (
    cq.Workplane("XZ")
    .workplane(offset=0)
    .center(CENTER_X, CENTER_Z)
    .polyline(WALL_OCTAGON).close()
    .extrude(-CASE_Y)
)

solid = solid.union(wall_prism)

# Bore cutout
bore_profile = bore_octagon_profile()
bore_cutter = (
    cq.Workplane("XZ")
    .workplane(offset=0)
    .center(CENTER_X, CENTER_Z)
    .polyline(bore_profile).close()
    .extrude(-(CASE_Y + OVERCUT))
)
solid = solid.cut(bore_cutter)

# M3 mounting holes
for hx, hz in HOLE_POSITIONS:
    hole_cutter = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(-(CASE_Y + OVERCUT))
    )
    solid = solid.cut(hole_cutter)

# ── Export ──
OUTPUT_STEP = Path(__file__).resolve().parent / "pump-case-cadquery.step"
cq.exporters.export(solid, str(OUTPUT_STEP))
print(f"Exported → {OUTPUT_STEP}")
