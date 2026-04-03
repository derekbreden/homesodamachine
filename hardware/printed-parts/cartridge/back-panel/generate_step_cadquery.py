from pathlib import Path
import cadquery as cq

# Panel body
PANEL_W = 170.0
PANEL_D = 3.0
PANEL_H = 103.6

# Extension dimensions
EDGE_W = 3.0
EXT_DEPTH = 2.0

# Installed position in assembly frame
# Back panel rail channel: Y=127.6..131.0mm (3.4mm wide)
# Panel thickness 3.0mm: clearance = (3.4 - 3.0) / 2 = 0.2mm each side
PANEL_Y0 = 127.8
PANEL_Y1 = 130.8

# Hole geometry — pass 9.57mm John Guest collet OD with 0.2mm loose-fit tolerance
HOLE_DIA = 7.00
HOLE_R   = HOLE_DIA / 2.0

# Coupler XZ centers (from coupler-tray boss half script, assembly frame)
# All 4 couplers at Z=34.3mm (the coupler tray split plane / coupler centers)
HOLES = [
    ("H1", 59.5, 34.3),
    ("H2", 76.5, 34.3),
    ("H3", 93.5, 34.3),
    ("H4", 110.5, 34.3),
]

MID_Y   = (PANEL_Y0 + PANEL_Y1) / 2.0
OVERCUT = 0.1

# Build model

# Panel body: XY workplane box translated to panel Y position
panel = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0.0, PANEL_Y0, 0.0))
    .box(PANEL_W, PANEL_D, PANEL_H, centered=False)
)

# Middle extension: 2mm outward (+Y) beyond the main slab,
# excluding the 3mm left/right edges that sit in the wall channels.
extension = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(EDGE_W, PANEL_Y1, 0.0))
    .box(PANEL_W - 2 * EDGE_W, EXT_DEPTH, PANEL_H, centered=False)
)
panel = panel.union(extension)

# Tube stub holes H1..H4
# XZ workplane normal is -Y. workplane(offset=-N) places the workplane at Y=N.
# extrude(D) goes in the -Y direction, so the cylinder spans Y=(N-D) to Y=N.
# We set workplane at Y=PANEL_Y1+EXT_DEPTH+OVERCUT and extrude through full thickness.
for i, (hid, hx, hz) in enumerate(HOLES, start=2):
    FULL_D = PANEL_D + EXT_DEPTH
    hole = (
        cq.Workplane("XZ")
        .workplane(offset=-(PANEL_Y1 + EXT_DEPTH + OVERCUT))
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(FULL_D + 2 * OVERCUT)
    )
    panel = panel.cut(hole)

# Export STEP file

OUTPUT_STEP = Path(__file__).resolve().parent / "back-panel-cadquery.step"
cq.exporters.export(panel, str(OUTPUT_STEP))
print(f"Exported -> {OUTPUT_STEP}")
