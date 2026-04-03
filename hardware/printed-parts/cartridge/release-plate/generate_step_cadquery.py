from pathlib import Path

import cadquery as cq

# Plate
PLATE_W = 160.0  # X
PLATE_D = 5.0    # Y
PLATE_H = 43.6   # Z

# Stepped bore zone diameters
Z1_D = 15.60    # Zone 1 (outer counterbore)
Z2_D = 10.07    # Zone 2 (inner lip bore)
Z3_D = 7.00     # Zone 3 (tube clearance through-hole)
Z1_R = Z1_D / 2
Z2_R = Z2_D / 2
Z3_R = Z3_D / 2

# Zone Y boundaries (Y=0 fitting-facing, Y=5 user-facing)
Y_USER     = 5.0
Y_Z1_FLOOR = 3.6
Y_Z2_FLOOR = 2.4
Y_FITTING  = 0.0

# Bore center positions (X, Z)
BORE_CENTERS = [
    (54.5, 21.8),   # A
    (71.5, 21.8),   # B
    (88.5, 21.8),   # C
    (105.5, 21.8),  # D
]

# Strut holes (receive separately printed struts)
STRUT_HOLE_W = 6.0   # X (no clearance, snap fit)
STRUT_HOLE_H = 6.0   # Z
STRUT_HOLES = {
    "TL": (7.0,   35.6),
    "TR": (153.0, 35.6),
    "BL": (7.0,    8.0),
    "BR": (153.0,  8.0),
}

# Plate body
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# Stepped bores -- 3-zone cylinders running Y=5 to Y=0
# XZ workplane: offset=-Y_pos places plane at Y=Y_pos, positive extrude goes -Y
for bore_idx, (cx, cz) in enumerate(BORE_CENTERS):
    zone1 = (
        cq.Workplane("XZ")
        .workplane(offset=-Y_USER)
        .center(cx, cz)
        .circle(Z1_R)
        .extrude(Y_USER - Y_Z1_FLOOR)
    )
    plate = plate.cut(zone1)

    zone2 = (
        cq.Workplane("XZ")
        .workplane(offset=-Y_Z1_FLOOR)
        .center(cx, cz)
        .circle(Z2_R)
        .extrude(Y_Z1_FLOOR - Y_Z2_FLOOR)
    )
    plate = plate.cut(zone2)

    zone3 = (
        cq.Workplane("XZ")
        .workplane(offset=-Y_Z2_FLOOR)
        .center(cx, cz)
        .circle(Z3_R)
        .extrude(Y_Z2_FLOOR - Y_FITTING)
    )
    plate = plate.cut(zone3)

# Strut holes -- 6.2x6.2 rectangular through-holes in Y
for label, (cx, cz) in STRUT_HOLES.items():
    x0 = cx - STRUT_HOLE_W / 2
    z0 = cz - STRUT_HOLE_H / 2
    overcut = 0.1
    hole = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x0, -overcut / 2, z0))
        .box(STRUT_HOLE_W, PLATE_D + overcut, STRUT_HOLE_H, centered=False)
    )
    plate = plate.cut(hole)

# Export
output_path = Path(__file__).parent / "release-plate-cadquery.step"
cq.exporters.export(plate, str(output_path))
print(f"Exported {output_path}")
