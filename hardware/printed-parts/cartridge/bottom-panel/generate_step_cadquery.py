from pathlib import Path

import cadquery as cq

# Part parameters

PANEL_W = 170.0   # X — panel width (left to right, was 140.0)
PANEL_D = 188.0   # Y — panel depth (back to front, full wall length)
PANEL_T = 3.0     # Z — panel thickness (fits 3.4mm channel, 0.2mm clearance each side)

EDGE_W = 3.0      # X — width of left/right edges that sit in wall channels
EXT_DEPTH = 2.0   # Z — how far the middle extends below the channel edges

# Modeling

panel = cq.Workplane("XY").box(PANEL_W, PANEL_D, PANEL_T, centered=False)

# Middle extension — 2mm downward below the main slab,
# excluding the 3mm left and right edges that sit in the wall channels.
extension = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(EDGE_W, 0, -EXT_DEPTH))
    .box(PANEL_W - 2 * EDGE_W, PANEL_D, EXT_DEPTH, centered=False)
)
panel = panel.union(extension)

# Export STEP file
OUTPUT_STEP = Path(__file__).resolve().parent / "bottom-panel-cadquery.step"
print(f"Exporting STEP file → {OUTPUT_STEP}")
cq.exporters.export(panel, str(OUTPUT_STEP))
