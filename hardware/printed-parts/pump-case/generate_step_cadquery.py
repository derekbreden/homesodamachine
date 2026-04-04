from pathlib import Path
import math

import cadquery as cq

# --- Dimensions ---
PLATE_W = 70.0
PLATE_D = 18.0          # total height (Y axis)
PLATE_H = 70.0
BASE_THICKNESS = 3.0     # solid floor at bottom
WALL_THICKNESS = 3.0     # wall around octagon bore
RAMP_HEIGHT = PLATE_D - BASE_THICKNESS  # 15mm of ramp above base
CORNER_R = 6.0           # fillet radius on 70x70 footprint corners

# Diamond (45-degree-rotated square) cutout for pump base
DIAMOND_SIDE = 43.0
LEDGE_DEPTH  = 1.5

# Pump center
PUMP_CX = PLATE_W / 2
PUMP_CZ = PLATE_H / 2

PUMP_CUTOUTS = [("cutout-1", PUMP_CX, PUMP_CZ)]

HOLE_DIA = 3.3
HOLE_R = HOLE_DIA / 2.0

# M3 holes — 50mm square pattern centered on pump
HOLES = [
    ("1-A", PUMP_CX - 25.0, PUMP_CZ + 25.0),
    ("1-B", PUMP_CX + 25.0, PUMP_CZ + 25.0),
    ("1-C", PUMP_CX + 25.0, PUMP_CZ - 25.0),
    ("1-D", PUMP_CX - 25.0, PUMP_CZ - 25.0),
]

# Octagon geometry
DIAMOND_HALF_DIAG = DIAMOND_SIDE * math.sqrt(2) / 2
TRIMMED_HALF_DIAG = 53.0 / 2


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


def _octagon_with_ledges():
    """Build octagon polygon with ledge indentations on all 4 long edges."""
    _t = TRIMMED_HALF_DIAG
    _d = DIAMOND_HALF_DIAG - _t

    base = [
        ( _d,  _t), ( _t,  _d), ( _t, -_d), ( _d, -_t),
        (-_d, -_t), (-_t, -_d), (-_t,  _d), (-_d,  _t),
    ]
    long_edges = {0, 2, 4, 6}

    pts = []
    for i in range(8):
        sx, sz = base[i]
        ex, ez = base[(i + 1) % 8]
        pts.append((sx, sz))

        if i not in long_edges:
            continue

        dx, dz = ex - sx, ez - sz
        elen = math.hypot(dx, dz)
        heading = math.degrees(math.atan2(dz, dx))

        mx, mz = (sx + ex) / 2, (sz + ez) / 2
        ux, uz = dx / elen, dz / elen
        nx, nz = uz, -ux
        if nx * (-mx) + nz * (-mz) < 0:
            nx, nz = -nx, -nz
        inward_is_left = (nx * (-uz) + nz * ux) > 0

        ramp_hyp = LEDGE_DEPTH * math.sqrt(2)
        shelf_total = 26.03
        entry = (elen - shelf_total) / 2
        par = shelf_total - 2 * LEDGE_DEPTH

        t = Turtle(sx, sz, heading)
        t.forward(entry)
        if inward_is_left:
            t.left(45);  t.forward(ramp_hyp); t.right(45)
            t.forward(par)
            t.right(45); t.forward(ramp_hyp); t.left(45)
        else:
            t.right(45); t.forward(ramp_hyp); t.left(45)
            t.forward(par)
            t.left(45);  t.forward(ramp_hyp); t.right(45)
        t.forward(entry)

        pts.extend(t.points[:-1])

    return pts


# --- Build the solid ---

def _rounded_rect_sketch(wp):
    """Create a rounded-rectangle face on the given workplane."""
    return (
        wp
        .center(PUMP_CX, PUMP_CZ)
        .sketch()
        .rect(PLATE_W, PLATE_H)
        .vertices()
        .fillet(CORNER_R)
        .finalize()
    )


# Base plate with rounded corners (y=0 to y=3)
base = _rounded_rect_sketch(
    cq.Workplane("XZ").workplane(offset=0)
).extrude(-BASE_THICKNESS)

# Upper block with rounded corners (y=3 to y=18), then chamfered.
# The chamfer follows the fillet arcs, producing a smooth rounded ramp at corners.
upper = _rounded_rect_sketch(
    cq.Workplane("XZ").workplane(offset=-BASE_THICKNESS)
).extrude(-RAMP_HEIGHT)

upper = upper.edges(">Y").chamfer(RAMP_HEIGHT - 0.1)

# Wall prism — offset octagon extruded full height.
# Ensures 3mm wall around the bore even where the ramp cuts past it.
_t = TRIMMED_HALF_DIAG
_d = DIAMOND_HALF_DIAG - _t
_t_off = _t + WALL_THICKNESS
_d_off = _d + WALL_THICKNESS * (math.sqrt(2) - 1)

offset_oct = [
    ( _d_off,  _t_off),
    ( _t_off,  _d_off),
    ( _t_off, -_d_off),
    ( _d_off, -_t_off),
    (-_d_off, -_t_off),
    (-_t_off, -_d_off),
    (-_t_off,  _d_off),
    (-_d_off,  _t_off),
]

wall_prism = (
    cq.Workplane("XZ")
    .workplane(offset=0)
    .center(PUMP_CX, PUMP_CZ)
    .polyline(offset_oct).close()
    .extrude(-PLATE_D)
)

solid = base.union(upper).union(wall_prism)

# Cut octagon bore through everything
for cutout_id, cx, cz in PUMP_CUTOUTS:
    overcut = 0.1
    pts = _octagon_with_ledges()
    octagon = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(cx, cz)
        .polyline(pts).close()
        .extrude(-(PLATE_D + overcut))
    )
    solid = solid.cut(octagon)

# Cut M3 clearance holes through everything
for hole_id, hx, hz in HOLES:
    overcut = 0.1
    cyl = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(-(PLATE_D + overcut))
    )
    solid = solid.cut(cyl)

# Export
OUTPUT_STEP = Path(__file__).resolve().parent / "pump-case-cadquery.step"
cq.exporters.export(solid, str(OUTPUT_STEP))
print(f"Exported → {OUTPUT_STEP}")
