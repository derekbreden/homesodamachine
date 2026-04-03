from pathlib import Path

import cadquery as cq

PLATE_W     = 170.0
PLATE_D     = 3.0
PLATE_H     = 103.6
SPLIT_Z     = 34.3
BOSS_H_HALF = PLATE_H - SPLIT_Z

BOSS_OD     = 16.0
BOSS_ID     = 9.5
BOSS_R_OUT  = BOSS_OD / 2.0
BOSS_R_IN   = BOSS_ID / 2.0
FULL_DEPTH  = 12.08
BOSS_H      = FULL_DEPTH - PLATE_D

HOLE_DIA    = 9.5
HOLE_R      = HOLE_DIA / 2.0

HOLES = [
    ("H1/B1", 59.5, 34.3),
    ("H2/B2", 76.5, 34.3),
    ("H3/B3", 93.5, 34.3),
    ("H4/B4", 110.5, 34.3),
]

STRUT_BORE_W = 6.4
STRUT_BORE_H = 6.4

# Only top two strut bores are in the boss half
STRUT_BORES_BOSS = [
    ("S-TL",   9.0, 51.1),
    ("S-TR", 161.0, 51.1),
]

MID_Y_BASE  = PLATE_D / 2.0
MID_Y_BOSS  = PLATE_D + BOSS_H / 2.0
MID_Y_BORE  = FULL_DEPTH / 2.0
OVERCUT     = 0.1

MID_Z_BOSS_HALF = (SPLIT_Z + PLATE_H) / 2.0

# Build the full tray body, then cut off the bottom half.

plate = (
    cq.Workplane("XY")
    .box(PLATE_W, PLATE_D, PLATE_H, centered=False)
)

for feat_id, hx, hz in HOLES:
    boss = (
        cq.Workplane("XZ")
        .workplane(offset=-PLATE_D)
        .center(hx, hz)
        .circle(BOSS_R_OUT)
        .extrude(-BOSS_H)
    )
    plate = plate.union(boss)

for feat_id, hx, hz in HOLES:
    bore = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(-(FULL_DEPTH + OVERCUT))
    )
    plate = plate.cut(bore)

for bore_id, cx, cz in STRUT_BORES_BOSS:
    x0 = cx - STRUT_BORE_W / 2
    z0 = cz - STRUT_BORE_H / 2
    bore_box = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x0, -OVERCUT / 2, z0))
        .box(STRUT_BORE_W, PLATE_D + OVERCUT, STRUT_BORE_H, centered=False)
    )
    plate = plate.cut(bore_box)

# Cut the bottom half (Z=0 to Z=SPLIT_Z) to produce the boss half.
bottom_cut = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(-OVERCUT / 2, -OVERCUT / 2, -OVERCUT))
    .box(PLATE_W + OVERCUT, FULL_DEPTH + OVERCUT, SPLIT_Z + OVERCUT, centered=False)
)
plate = plate.cut(bottom_cut)

OUTPUT_STEP = Path(__file__).resolve().parent / "coupler-tray-boss-half-cadquery.step"
cq.exporters.export(plate, str(OUTPUT_STEP))
print(f"Exported -> {OUTPUT_STEP}")
