from pathlib import Path

import cadquery as cq

# Panel body
PANEL_W = 170.0   # X
PANEL_D =   3.0   # Y (channel portion)
PANEL_H = 103.6   # Z

# Extension dimensions
EDGE_W = 3.0      # X — width of left/right edges that sit in wall channels
EXT_DEPTH = 2.0   # Y — how far the middle extends beyond the channel edges

# Finger access hole
HOLE_W  = 100.0   # X
HOLE_H  =  30.0   # Z
HOLE_X0 =  35.0   # X start
HOLE_Z0 =  12.0   # Z start

# Panel body
panel = cq.Workplane("XY").box(PANEL_W, PANEL_D, PANEL_H, centered=False)

# Middle extension (2mm outward in -Y)
extension = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(EDGE_W, -EXT_DEPTH, 0.0))
    .box(PANEL_W - 2 * EDGE_W, EXT_DEPTH, PANEL_H, centered=False)
)
panel = panel.union(extension)

# Finger access hole (through-hole along Y, cuts through full thickness including extension)
hole = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(HOLE_X0, -EXT_DEPTH, HOLE_Z0))
    .box(HOLE_W, PANEL_D + EXT_DEPTH, HOLE_H, centered=False)
)
panel = panel.cut(hole)

# Export STEP file
OUT_DIR = Path(__file__).parent
STEP_PATH = OUT_DIR / "front-panel-cadquery.step"
cq.exporters.export(panel, str(STEP_PATH))
print(f"Exported STEP to: {STEP_PATH}")
