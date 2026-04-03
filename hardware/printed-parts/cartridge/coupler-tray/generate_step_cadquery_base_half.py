from pathlib import Path

import cadquery as cq

PLATE_W     = 170.0
PLATE_D     = 3.0
PLATE_H     = 103.6
SPLIT_Z     = 34.3
BASE_H      = SPLIT_Z

BOSS_OD     = 16.0
BOSS_ID     = 9.5
BOSS_R_OUT  = BOSS_OD / 2.0
BOSS_R_IN   = BOSS_ID / 2.0
FULL_DEPTH  = 12.08
BOSS_H      = FULL_DEPTH - PLATE_D

HOLE_DIA    = 9.5
HOLE_R      = HOLE_DIA / 2.0

# Hole/boss centers — 1x4 row, all at the split plane
HOLES = [
    ("H1/B1", 59.5, 34.3),
    ("H2/B2", 76.5, 34.3),
    ("H3/B3", 93.5, 34.3),
    ("H4/B4", 110.5, 34.3),
]

STRUT_BORE_W = 6.4
STRUT_BORE_H = 6.4

# Only bottom two strut bores are in the base half
STRUT_BORES_BASE = [
    ("S-BL",   9.0, 17.5),
    ("S-BR", 161.0, 17.5),
]

MID_Y_BASE  = PLATE_D / 2.0
MID_Y_BOSS  = PLATE_D + BOSS_H / 2.0
MID_Y_BORE  = FULL_DEPTH / 2.0
OVERCUT     = 0.1

# Build the full tray body first, then cut off the top half.
# The semicircular features are produced automatically by the
# boolean intersection with the split plane.

plate = (
    cq.Workplane("XY")
    .box(PLATE_W, PLATE_D, PLATE_H, centered=False)
)

# Bosses — full cylinders on the back face
for feat_id, hx, hz in HOLES:
    # XZ workplane offset to back face; extrude into -Y (away from front)
    boss = (
        cq.Workplane("XZ")
        .workplane(offset=-PLATE_D)
        .center(hx, hz)
        .circle(BOSS_R_OUT)
        .extrude(-BOSS_H)
    )
    plate = plate.union(boss)

# Through-bores — full depth through plate and bosses
for feat_id, hx, hz in HOLES:
    bore = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(-(FULL_DEPTH + OVERCUT))
    )
    plate = plate.cut(bore)

# Bottom strut bores (top pair lives in the boss half)
for bore_id, cx, cz in STRUT_BORES_BASE:
    x0 = cx - STRUT_BORE_W / 2
    z0 = cz - STRUT_BORE_H / 2
    bore_box = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x0, -OVERCUT / 2, z0))
        .box(STRUT_BORE_W, PLATE_D + OVERCUT, STRUT_BORE_H, centered=False)
    )
    plate = plate.cut(bore_box)

# Cut the top half (Z=SPLIT_Z to Z=PLATE_H) to produce the base half.
# This single cut simultaneously removes the upper plate body, turns each
# full cylindrical boss into a semicircular half-boss, and turns each full
# circular bore into a semicircular channel on the mating face.
top_cut = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0, -OVERCUT / 2, SPLIT_Z))
    .box(PLATE_W + OVERCUT, FULL_DEPTH + OVERCUT, PLATE_H - SPLIT_Z + OVERCUT, centered=False)
)
plate = plate.cut(top_cut)

# Export STEP file
OUTPUT_STEP = Path(__file__).resolve().parent / "coupler-tray-base-half-cadquery.step"
cq.exporters.export(plate, str(OUTPUT_STEP))
print(f"Exported -> {OUTPUT_STEP}")
