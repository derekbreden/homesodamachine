"""
Pump Tray v3 — CadQuery STEP Generation Script
Build sequence line: Widen pump tray — make the pump tray wider so that the
strut bores can be moved outward and no longer overlap the pump mounting holes.

Specification source: hardware/printed-parts/cartridge/pump-tray/planning/parts.md

v3 change: Plate widened from 137.2mm to 140.0mm. Pump pattern re-centered.
Strut bores moved outward to X=4.0/136.0 (from 10.0/127.2), fully clearing
the M3 mounting holes with 1.85mm edge-to-edge gap.

Coordinate system (part local frame):
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width axis — left to right, 0..140.0mm
  Y: plate thickness axis — front face (Y=0, pump bracket side) to back face (Y=3.0mm, motor side)
  Z: plate height axis — bottom to top, 0..68.6mm
  Envelope: 140.0mm (X) × 3.0mm (Y) × 68.6mm (Z)
"""

from pathlib import Path

import cadquery as cq

# Part parameters (from parts.md v3)

# Plate envelope
PLATE_W = 170.0   # X — width left to right (was 140.0 in v3)
PLATE_D = 3.0     # Y — thickness front to back
PLATE_H = 103.6   # Z — height bottom to top (was 68.6, +35mm)

# Diamond (45°-rotated square) cutout for pump base
DIAMOND_SIDE = 43.0  # side length of the square before rotation
LEDGE_DEPTH  = 1.5   # perpendicular inset from each long edge toward hole center

# Pump base cutout centers (XZ positions)
# Pump center-to-center: 68.6mm. Plate center: 70.0mm.
# Pump 1: 70.0 - 34.3 = 35.7. Pump 2: 70.0 + 34.3 = 104.3.
PUMP_CUTOUTS = [
    ("cutout-1", 50.7,  34.3),   # Pump 1 (was 35.7, +15mm for wider plate)
    ("cutout-2", 119.3, 34.3),   # Pump 2 (was 104.3, +15mm for wider plate)
]

# M3 clearance hole diameter
HOLE_DIA = 3.3
HOLE_R = HOLE_DIA / 2.0

# M3 hole XZ positions — 50mm square pattern around each motor bore, re-centered
HOLES = [
    ("1-A", 25.7,  59.3),   # Pump 1, top-left (was 10.7, +15mm)
    ("1-B", 75.7,  59.3),   # Pump 1, top-right (was 60.7, +15mm)
    ("1-C", 75.7,   9.3),   # Pump 1, bottom-right (was 60.7, +15mm)
    ("1-D", 25.7,   9.3),   # Pump 1, bottom-left (was 10.7, +15mm)
    ("2-A", 94.3,  59.3),   # Pump 2, top-left (was 79.3, +15mm)
    ("2-B", 144.3, 59.3),   # Pump 2, top-right (was 129.3, +15mm)
    ("2-C", 144.3,  9.3),   # Pump 2, bottom-right (was 129.3, +15mm)
    ("2-D", 94.3,   9.3),   # Pump 2, bottom-left (was 79.3, +15mm)
]

# Strut bore parameters
# Strut cross-section on release plate: 6.0 x 6.0 mm
# Bore clearance: 0.2mm per side × 2 sides = 0.4mm total
# Bore size: 6.0 + 0.4 = 6.4 mm per axis
STRUT_SIZE = 6.0
BORE_CLEARANCE = 0.4
STRUT_BORE_W = STRUT_SIZE + BORE_CLEARANCE  # 6.4 mm (X)
STRUT_BORE_H = STRUT_SIZE + BORE_CLEARANCE  # 6.4 mm (Z)

# Strut bore center positions (X, Z) — moved outward to clear M3 holes
STRUT_BORES = [
    ("S-TL",   9.0, 51.1),   # Top-Left
    ("S-TR", 161.0, 51.1),   # Top-Right
    ("S-BL",   9.0, 17.5),   # Bottom-Left
    ("S-BR", 161.0, 17.5),   # Bottom-Right
]

print("PUMP TRAY v3 — CadQuery STEP Generation")

# Modeling

# Feature 1: Plate body
# box(W, D, H, centered=False) → X:[0,140.0] Y:[0,3.0] Z:[0,68.6]
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)
print("  [+] Feature 1: Plate body (140.0 × 3.0 × 68.6 mm)")

# Features 2-3: Octagon cutouts with ledges
# Start with diamond (43mm square @ 45°), trim corners so corner-to-corner
# span shrinks to 53mm. Then add a 3mm-deep ledge on each long edge —
# 45° ramps in/out with a parallel shelf running along the middle.
import math
DIAMOND_HALF_DIAG = DIAMOND_SIDE * math.sqrt(2) / 2  # corner-to-corner half diagonal
TRIMMED_HALF_DIAG = 53.0 / 2                          # trimmed corner-to-corner half

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
    with 45° entry/exit ramps. This reduces the cutout (adds material)
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
    long_edges = {0, 2, 4, 6}  # indices where long edges start

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

        # Inward-turn direction: which way is "toward hole center" from this edge?
        mx, mz = (sx + ex) / 2, (sz + ez) / 2
        ux, uz = dx / elen, dz / elen
        nx, nz = uz, -ux
        if nx * (-mx) + nz * (-mz) < 0:
            nx, nz = -nx, -nz
        inward_is_left = (nx * (-uz) + nz * ux) > 0

        # Ledge profile along each long edge:
        #   entry | 45° ramp in | shelf | 45° ramp out | entry
        #
        # shelf_total (26.03mm) is the span from first ramp start to last ramp end.
        # Entry is whatever remains at each end of the long edge.
        ramp_hyp = LEDGE_DEPTH * math.sqrt(2)        # 45° ramp true travel
        shelf_total = 26.03
        entry = (elen - shelf_total) / 2
        par = shelf_total - 2 * LEDGE_DEPTH           # flat shelf between ramps

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
    print(f"  [-] Feature: Octagon {cutout_id} at X={cx}, Z={cz} "
          f"(43mm square @ 45°, trimmed to {2*TRIMMED_HALF_DIAG:.1f}mm span, "
          f"{LEDGE_DEPTH}mm ledges on long edges)")

# Features 4-11: M3 clearance holes (3.3mm dia, through Y)
# Same approach as motor bores.
for hole_id, hx, hz in HOLES:
    overcut = 0.1
    cyl = (
        cq.Workplane("XZ")
        .workplane(offset=0)        # plane at Y=0 (front face)
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(-(PLATE_D + overcut))
        # negative extrude on XZ → +Y direction
    )
    plate = plate.cut(cyl)
    print(f"  [-] Feature: Hole {hole_id} at X={hx}, Z={hz}")

# Features 12-15: Strut bores (6.4 x 6.4 mm rectangular, through Y)
#
# Each bore is a rectangular through-hole centered at (cx, cz) in the XZ plane,
# running from Y=0 to Y=3.0mm.
#
# Approach: create a box at the bore position and cut it from the plate.
# Box corner at (cx - STRUT_BORE_W/2, 0, cz - STRUT_BORE_H/2),
# dimensions (STRUT_BORE_W, PLATE_D + overcut, STRUT_BORE_H).
# Using overcut to ensure clean through-cut.
for bore_id, cx, cz in STRUT_BORES:
    overcut = 0.1
    x0 = cx - STRUT_BORE_W / 2   # left X edge of bore
    z0 = cz - STRUT_BORE_H / 2   # bottom Z edge of bore
    bore_box = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x0, -overcut / 2, z0))
        .box(STRUT_BORE_W, PLATE_D + overcut, STRUT_BORE_H, centered=False)
    )
    plate = plate.cut(bore_box)
    print(f"  [-] Feature: Strut bore {bore_id} at X={cx}, Z={cz} "
          f"(rect {STRUT_BORE_W}×{STRUT_BORE_H} mm)")

print()
print()

# Export STEP file

OUTPUT_STEP = Path(__file__).resolve().parent / "pump-tray-cadquery.step"
print(f"Exporting STEP file → {OUTPUT_STEP}")
cq.exporters.export(plate, str(OUTPUT_STEP))
print()
