import cadquery as cq
from pathlib import Path

# Wall body
WALL_T = 3.0
WALL_Y = 188.0
WALL_Z = 114.0

# Rail geometry
RAIL_H = 3.0
RAIL_W = 2.0
CHANNEL_W = 3.4  # 3mm panel + 0.2mm clearance each side

# Derived
INTERIOR_X = 0.0
RAIL_TIP_X = -RAIL_H
PASS_THRU_GAP = RAIL_W + CHANNEL_W

# Interior plate Y positions (wall coordinates)
PUMP_TRAY_Y_CENTER = 111.5
COUPLER_TRAY_Y_CENTER = 30.0  # TODO: determine actual position

# Interior coordinate span (between panel inner faces)
INTERIOR_Y_START = 5.0
INTERIOR_Y_END = 183.0
INTERIOR_Z_START = 5.0
INTERIOR_Z_END = 108.6


# Right wall rails protrude from X=0 (interior face) in -X direction.
# Rail box: X from -RAIL_H to 0, Y from y0 to y0+rail_dy, Z from z0 to z0+rail_dz.
def add_rail_right(y0, z0, rail_dy, rail_dz):
    return (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(-RAIL_H, y0, z0))
        .box(RAIL_H, rail_dy, rail_dz, centered=False)
    )


# Wall body
wall = cq.Workplane("XY").box(WALL_T, WALL_Y, WALL_Z, centered=False)

# Back panel rails (panel slides in -Z, gripped in Y)
BACK_PANEL_RAIL_EXT_Y0 = 0.0
BACK_PANEL_RAIL_INT_Y0 = 5.4

rail_back_panel_ext = add_rail_right(
    y0=BACK_PANEL_RAIL_EXT_Y0, z0=PASS_THRU_GAP, rail_dy=RAIL_W, rail_dz=WALL_Z - PASS_THRU_GAP * 2)
wall = wall.union(rail_back_panel_ext)

rail_back_panel_int = add_rail_right(
    y0=BACK_PANEL_RAIL_INT_Y0, z0=PASS_THRU_GAP, rail_dy=RAIL_W, rail_dz=WALL_Z - PASS_THRU_GAP * 2)
wall = wall.union(rail_back_panel_int)

# Front panel rails (panel slides in -Z, gripped in Y at front)
FRONT_PANEL_RAIL_EXT_Y0 = WALL_Y - RAIL_W
FRONT_PANEL_RAIL_INT_Y0 = WALL_Y - RAIL_W - CHANNEL_W - RAIL_W

rail_front_panel_int = add_rail_right(
    y0=FRONT_PANEL_RAIL_INT_Y0, z0=PASS_THRU_GAP, rail_dy=RAIL_W, rail_dz=WALL_Z - 2 * PASS_THRU_GAP)
wall = wall.union(rail_front_panel_int)

rail_front_panel_ext = add_rail_right(
    y0=FRONT_PANEL_RAIL_EXT_Y0, z0=PASS_THRU_GAP, rail_dy=RAIL_W, rail_dz=WALL_Z - 2 * PASS_THRU_GAP)
wall = wall.union(rail_front_panel_ext)

# Bottom panel rails (panel slides in +Y, gripped in Z at bottom)
BOTTOM_PANEL_RAIL_EXT_Z0 = 0.0
BOTTOM_PANEL_RAIL_INT_Z0 = 5.4

rail_bottom_panel_ext = add_rail_right(
    y0=0.0, z0=BOTTOM_PANEL_RAIL_EXT_Z0, rail_dy=WALL_Y, rail_dz=RAIL_W)
wall = wall.union(rail_bottom_panel_ext)

rail_bottom_panel_int = add_rail_right(
    y0=PASS_THRU_GAP, z0=BOTTOM_PANEL_RAIL_INT_Z0, rail_dy=WALL_Y - 2 * PASS_THRU_GAP, rail_dz=RAIL_W)
wall = wall.union(rail_bottom_panel_int)

# Top panel / plate-top rails (shared rail — top panel slides in -Z, tray top edges slide in +Y)
TOP_PANEL_RAIL_INT_Z0 = INTERIOR_Z_END - RAIL_W
TOP_PANEL_RAIL_EXT_Z0 = INTERIOR_Z_END + CHANNEL_W

rail_top_panel_int = add_rail_right(
    y0=PASS_THRU_GAP, z0=TOP_PANEL_RAIL_INT_Z0, rail_dy=WALL_Y - 2 * PASS_THRU_GAP, rail_dz=RAIL_W)
wall = wall.union(rail_top_panel_int)

rail_top_panel_ext = add_rail_right(
    y0=PASS_THRU_GAP, z0=TOP_PANEL_RAIL_EXT_Z0, rail_dy=WALL_Y - 2 * PASS_THRU_GAP, rail_dz=RAIL_W)
wall = wall.union(rail_top_panel_ext)

# Interior plate rails (plates slide in -Z, gripped in Y)
# Vertical rail pairs at each plate Y position, gapped at bottom/top for horizontal rails.
for y_center in [PUMP_TRAY_Y_CENTER, COUPLER_TRAY_Y_CENTER]:
    rail_back_y0 = y_center - CHANNEL_W / 2 - RAIL_W
    rail_front_y0 = y_center + CHANNEL_W / 2

    rail_back = add_rail_right(
        y0=rail_back_y0, z0=PASS_THRU_GAP, rail_dy=RAIL_W, rail_dz=WALL_Z - PASS_THRU_GAP * 2)
    wall = wall.union(rail_back)

    rail_front = add_rail_right(
        y0=rail_front_y0, z0=PASS_THRU_GAP, rail_dy=RAIL_W, rail_dz=WALL_Z - PASS_THRU_GAP * 2)
    wall = wall.union(rail_front)

# Cutouts in horizontal rails for interior plates to pass through
for y_center in [PUMP_TRAY_Y_CENTER, COUPLER_TRAY_Y_CENTER]:
    cutout_y0 = y_center - CHANNEL_W / 2
    for cut_z0 in [BOTTOM_PANEL_RAIL_INT_Z0, TOP_PANEL_RAIL_INT_Z0, TOP_PANEL_RAIL_EXT_Z0]:
        cutout = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(-RAIL_H, cutout_y0, cut_z0))
            .box(RAIL_H, CHANNEL_W, RAIL_W, centered=False)
        )
        wall = wall.cut(cutout)

# Export
OUTPUT_STEP = Path(__file__).resolve().parent / "right-wall-cadquery.step"
cq.exporters.export(wall, str(OUTPUT_STEP))
print(f"Exported → {OUTPUT_STEP}")
