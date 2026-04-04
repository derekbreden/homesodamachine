from pathlib import Path
import math

import cadquery as cq

# Plate envelope — sized for a single Kamoer pump
# Original two-pump tray: 170mm wide. Single pump center was at x=50.7
# with 25mm margin to each mounting hole edge. Keep same proportions.
PLATE_W = 70.0
PLATE_D = 18.0
PLATE_H = 70.0

# Diamond (45-degree-rotated square) cutout for pump base
DIAMOND_SIDE = 43.0
LEDGE_DEPTH  = 1.5

# Single pump cutout centered on the plate
PUMP_CX = PLATE_W / 2
PUMP_CZ = PLATE_H / 2

PUMP_CUTOUTS = [
    ("cutout-1", PUMP_CX, PUMP_CZ),
]

HOLE_DIA = 3.3
HOLE_R = HOLE_DIA / 2.0

# M3 hole XZ positions — 50mm square pattern centered on pump
HOLES = [
    ("1-A", PUMP_CX - 25.0, PUMP_CZ + 25.0),
    ("1-B", PUMP_CX + 25.0, PUMP_CZ + 25.0),
    ("1-C", PUMP_CX + 25.0, PUMP_CZ - 25.0),
    ("1-D", PUMP_CX - 25.0, PUMP_CZ - 25.0),
]

# Modeling

plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# Octagon cutouts with ledges
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
    """Build octagon polygon with ledge indentations on all 4 long edges.

    Each long edge gets a LEDGE_DEPTH-deep shelf along its middle,
    with 45-degree entry/exit ramps. This reduces the cutout (adds material)
    along the long edges.

    Returns list of (x, z) tuples relative to octagon center.
    """
    _t = TRIMMED_HALF_DIAG
    _d = DIAMOND_HALF_DIAG - _t

    # 8 base vertices (clockwise from top-right of top short side)
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
    plate = plate.cut(octagon)

# M3 clearance holes (through Y)
for hole_id, hx, hz in HOLES:
    overcut = 0.1
    cyl = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(-(PLATE_D + overcut))
    )
    plate = plate.cut(cyl)

# Export STEP file
OUTPUT_STEP = Path(__file__).resolve().parent / "pump-case-cadquery.step"
cq.exporters.export(plate, str(OUTPUT_STEP))
print(f"Exported → {OUTPUT_STEP}")
