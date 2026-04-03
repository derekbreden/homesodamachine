from pathlib import Path
import math

import cadquery as cq

# Plate envelope
PLATE_W = 170.0
PLATE_D = 3.0
PLATE_H = 103.6

# Diamond (45-degree-rotated square) cutout for pump base
DIAMOND_SIDE = 43.0
LEDGE_DEPTH  = 1.5

# Pump base cutout centers (XZ positions)
PUMP_CUTOUTS = [
    ("cutout-1", 50.7,  34.3),
    ("cutout-2", 119.3, 34.3),
]

HOLE_DIA = 3.3
HOLE_R = HOLE_DIA / 2.0

# M3 hole XZ positions — 50mm square pattern around each motor bore
HOLES = [
    ("1-A", 25.7,  59.3),
    ("1-B", 75.7,  59.3),
    ("1-C", 75.7,   9.3),
    ("1-D", 25.7,   9.3),
    ("2-A", 94.3,  59.3),
    ("2-B", 144.3, 59.3),
    ("2-C", 144.3,  9.3),
    ("2-D", 94.3,   9.3),
]

# Strut bore parameters
# Bore clearance: 0.2mm per side, 0.4mm total
STRUT_SIZE = 6.0
BORE_CLEARANCE = 0.4
STRUT_BORE_W = STRUT_SIZE + BORE_CLEARANCE
STRUT_BORE_H = STRUT_SIZE + BORE_CLEARANCE

# Strut bore center positions (X, Z)
STRUT_BORES = [
    ("S-TL",  12.0, 48.1),
    ("S-TR", 158.0, 48.1),
    ("S-BL",  12.0, 20.5),
    ("S-BR", 158.0, 20.5),
]

# Modeling

plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# Octagon cutouts with ledges
# Start with diamond (43mm square at 45 degrees), trim corners so corner-to-corner
# span shrinks to 53mm. Then add a ledge on each long edge —
# 45-degree ramps in/out with a parallel shelf running along the middle.
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

        # Determine which direction is "toward hole center" from this edge
        mx, mz = (sx + ex) / 2, (sz + ez) / 2
        ux, uz = dx / elen, dz / elen
        nx, nz = uz, -ux
        if nx * (-mx) + nz * (-mz) < 0:
            nx, nz = -nx, -nz
        inward_is_left = (nx * (-uz) + nz * ux) > 0

        # Ledge profile along each long edge:
        #   entry | 45-degree ramp in | shelf | 45-degree ramp out | entry
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

        pts.extend(t.points[:-1])  # last point coincides with next vertex

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
        # negative extrude on XZ goes in +Y direction
    )
    plate = plate.cut(cyl)

# Strut bores (rectangular through-holes in Y)
# Each bore is a box centered at (cx, cz) in XZ, running through the plate thickness.
for bore_id, cx, cz in STRUT_BORES:
    overcut = 0.1
    x0 = cx - STRUT_BORE_W / 2
    z0 = cz - STRUT_BORE_H / 2
    bore_box = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x0, -overcut / 2, z0))
        .box(STRUT_BORE_W, PLATE_D + overcut, STRUT_BORE_H, centered=False)
    )
    plate = plate.cut(bore_box)

# Export STEP file
OUTPUT_STEP = Path(__file__).resolve().parent / "pump-tray-cadquery.step"
cq.exporters.export(plate, str(OUTPUT_STEP))
print(f"Exported → {OUTPUT_STEP}")
