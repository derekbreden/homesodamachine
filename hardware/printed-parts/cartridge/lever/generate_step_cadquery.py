from pathlib import Path

import cadquery as cq

# Plate
PLATE_W  = 40.0   # X
PLATE_D  =   4.0   # Y
PLATE_H  =  43.6   # Z

# Strut holes (receive separately printed struts)
STRUT_HOLE_W = 6.0   # X (no clearance, snap fit)
STRUT_HOLE_H = 6.0   # Z
STRUT_HOLES = {
    "TL": (  7.0, 35.6),
    "TR": (33.0, 35.6),
    "BL": (  7.0,  8.0),
    "BR": (33.0,  8.0),
}

# Plate body
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# Strut holes -- 6.2x6.2 rectangular through-holes in Y
lever = plate
for label, (cx, cz) in STRUT_HOLES.items():
    x0 = cx - STRUT_HOLE_W / 2
    z0 = cz - STRUT_HOLE_H / 2
    overcut = 0.1
    hole = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x0, -overcut / 2, z0))
        .box(STRUT_HOLE_W, PLATE_D + overcut, STRUT_HOLE_H, centered=False)
    )
    lever = lever.cut(hole)

# Export
STEP_PATH = Path(__file__).parent / "lever-cadquery.step"
cq.exporters.export(lever, str(STEP_PATH))
print(f"Exported {STEP_PATH}")
