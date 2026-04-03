"""
Left Wall — CadQuery STEP Generation Script
Season 2, Phase 7, Item 17 of the pump cartridge build sequence.

Specification source: hardware/printed-parts/cartridge/left-wall/planning/parts.md

The left wall is a flat panel in the YZ plane with thickness in X.
The interior face (at X=WALL_T) carries 10 rails — two rails per rail pair,
forming channels that guide the back panel, front panel, bottom panel, top panel,
pump tray, and coupler tray. No retention, detent, or exterior track features.

Coordinate system (part local frame):
  Origin: wall back-bottom-exterior corner (X=0, Y=0, Z=0)
  X: wall thickness axis — exterior face (X=0) to interior face (X=WALL_T=3.0mm)
     Rails protrude from X=3.0mm inward to X=6.0mm (+X direction into interior)
  Y: back-to-front axis — back (Y=0) to front (Y=WALL_Y=133.0mm)
  Z: height axis — bottom (Z=0) to top (Z=WALL_Z=79.0mm)
  Envelope (wall body only): 3.0mm (X) x 133.0mm (Y) x 79.0mm (Z)
  Envelope (with rails):  6.0mm (X) x 133.0mm (Y) x 79.0mm (Z)
"""

import sys
from pathlib import Path

# Script is at: hardware/printed-parts/cartridge/left-wall/generate_step_cadquery.py
# parents[4] = project root
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq

# Part parameters (from planning/parts.md)

# Wall body
WALL_T = 3.0     # X — wall thickness (exterior face to interior face)
WALL_Y = 188.0   # Y — wall depth (back to front)
WALL_Z = 114.0   # Z — wall height (bottom to top)

# Rail geometry
RAIL_H = 3.0      # X — rail protrusion height from interior face (into interior)
RAIL_W = 2.0      # width of each rail in the separation axis direction
CHANNEL_W = 3.4  # gap between rail inner faces (3mm panel + 0.2mm clearance each side)

# Derived
INTERIOR_X = WALL_T           # X=3.0mm — interior face of wall
RAIL_TIP_X  = WALL_T + RAIL_H  # X=6.0mm — inner face of rails (tip of protrusion)
PASS_THRU_GAP = RAIL_W + CHANNEL_W  # 5.4mm total allowing pass through

# Interior plate Y positions (wall coordinates)
PUMP_TRAY_Y_CENTER = 111.5   # pump tray center (shifted +55mm from 56.5)
COUPLER_TRAY_Y_CENTER = 30.0 # TODO: determine actual position

# Interior coordinate span (between panel inner faces)
INTERIOR_Y_START = 5.0       # inner face of back panel (Y)
INTERIOR_Y_END   = 183.0     # inner face of front panel (Y)
INTERIOR_Z_START = 5.0       # inner face of bottom panel (Z)
INTERIOR_Z_END   = 108.6     # inner face of top rail (Z)

# Modeling

# Feature 1: Wall body
# XY workplane: box(W, D, H, centered=False) → X:[0,W] Y:[0,D] Z:[0,H]
# box(WALL_T, WALL_Y, WALL_Z, centered=False) → X:[0,3.0] Y:[0,133.0] Z:[0,79.0]
wall = cq.Workplane("XY").box(WALL_T, WALL_Y, WALL_Z, centered=False)
print(f"  [+] Feature 1: Wall body ({WALL_T} x {WALL_Y} x {WALL_Z} mm, X x Y x Z)")

# Helper: add a rail to the wall.
# All rails protrude from the interior face X=WALL_T in +X direction.
# Rail is a box: X span = WALL_T to WALL_T+RAIL_H, Y span = [y0, y0+rail_dy], Z span = [z0, z0+rail_dz]
# Uses XY workplane: transformed(offset=Vector(x0, y0, z0)).box(dx, dy, dz, centered=False)
# → X:[x0, x0+dx], Y:[y0, y0+dy], Z:[z0, z0+dz]
def add_rail(label, y0, z0, rail_dy, rail_dz):
    """Add a rail at the given Y,Z start position with the given Y,Z dimensions.
    Rail X span: WALL_T to WALL_T+RAIL_H (protrudes from interior face inward)."""
    rail = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(WALL_T, y0, z0))
        .box(RAIL_H, rail_dy, rail_dz, centered=False)
    )
    print(f"  [+] {label}: Y={y0:.1f}..{y0+rail_dy:.1f}, Z={z0:.1f}..{z0+rail_dz:.1f}, X={WALL_T:.1f}..{RAIL_TIP_X:.1f}")
    return rail

# Features 2-3: Back panel rails (panel slides in -Z, gripped in Y)
# Exterior rail: Y=0.0..2.0mm, Interior rail: Y=5.4..7.4mm
# Channel: Y=2.0..5.4mm (3.4mm wide)
# Rails run full Z height (Z=0..WALL_Z)
BACK_PANEL_RAIL_EXT_Y0 = 0.0
BACK_PANEL_RAIL_INT_Y0 = 5.4   # = RAIL_W + CHANNEL_W = 2.0 + 3.4

rail_back_panel_ext = add_rail("Feature 2: Back panel rail exterior",
                       y0=BACK_PANEL_RAIL_EXT_Y0, z0=PASS_THRU_GAP, rail_dy=RAIL_W, rail_dz=WALL_Z - PASS_THRU_GAP * 2)
wall = wall.union(rail_back_panel_ext)

rail_back_panel_int = add_rail("Feature 3: Back panel rail interior",
                       y0=BACK_PANEL_RAIL_INT_Y0, z0=PASS_THRU_GAP, rail_dy=RAIL_W, rail_dz=WALL_Z - PASS_THRU_GAP * 2)
wall = wall.union(rail_back_panel_int)
print(f"    Back panel channel: Y={BACK_PANEL_RAIL_EXT_Y0+RAIL_W:.1f}..{BACK_PANEL_RAIL_INT_Y0:.1f}mm ({CHANNEL_W}mm wide)")

# Features 4-5: Front panel rails (panel slides in -Z, gripped in Y at front)
# Exterior rail: Y=125.6..127.6mm, Interior rail: Y=131.0..133.0mm
# Channel: Y=127.6..131.0mm (3.4mm wide)
# FRONT_PANEL_RAIL_EXT_Y0 + RAIL_W = WALL_Y → FRONT_PANEL_RAIL_EXT_Y0 = WALL_Y - RAIL_W = 133.0 - 2.0 = 131.0
# FRONT_PANEL_RAIL_INT_Y0 = WALL_Y - RAIL_W - CHANNEL_W - RAIL_W = 133.0 - 2.0 - 3.4 - 2.0 = 125.6
FRONT_PANEL_RAIL_EXT_Y0 = WALL_Y - RAIL_W         # 131.0
FRONT_PANEL_RAIL_INT_Y0 = WALL_Y - RAIL_W - CHANNEL_W - RAIL_W  # 125.6

rail_front_panel_int = add_rail("Feature 4: Front panel rail interior",
                      y0=FRONT_PANEL_RAIL_INT_Y0, z0=PASS_THRU_GAP, rail_dy=RAIL_W, rail_dz=WALL_Z - 2 * PASS_THRU_GAP)
wall = wall.union(rail_front_panel_int)

rail_front_panel_ext = add_rail("Feature 5: Front panel rail exterior",
                      y0=FRONT_PANEL_RAIL_EXT_Y0, z0=PASS_THRU_GAP, rail_dy=RAIL_W, rail_dz=WALL_Z - 2 * PASS_THRU_GAP)
wall = wall.union(rail_front_panel_ext)
print(f"    Front panel channel: Y={FRONT_PANEL_RAIL_INT_Y0+RAIL_W:.1f}..{FRONT_PANEL_RAIL_EXT_Y0:.1f}mm ({CHANNEL_W}mm wide)")

# Features 6-7: Bottom panel rails (panel slides in +Y, gripped in Z at bottom)
# Exterior rail: Z=0.0..2.0mm, Interior rail: Z=5.4..7.4mm
# Channel: Z=2.0..5.4mm (3.4mm wide)
# Rails run full Y depth (Y=0..WALL_Y)
BOTTOM_PANEL_RAIL_EXT_Z0 = 0.0
BOTTOM_PANEL_RAIL_INT_Z0 = 5.4   # = RAIL_W + CHANNEL_W

rail_bottom_panel_ext = add_rail("Feature 6: Bottom panel rail exterior",
                        y0=0.0, z0=BOTTOM_PANEL_RAIL_EXT_Z0, rail_dy=WALL_Y, rail_dz=RAIL_W)
wall = wall.union(rail_bottom_panel_ext)

rail_bottom_panel_int = add_rail("Feature 7: Bottom panel rail interior",
                        y0=PASS_THRU_GAP, z0=BOTTOM_PANEL_RAIL_INT_Z0, rail_dy=WALL_Y - 2 * PASS_THRU_GAP, rail_dz=RAIL_W)
wall = wall.union(rail_bottom_panel_int)
print(f"    Bottom panel channel: Z={BOTTOM_PANEL_RAIL_EXT_Z0+RAIL_W:.1f}..{BOTTOM_PANEL_RAIL_INT_Z0:.1f}mm ({CHANNEL_W}mm wide)")

# Features 8-9: Top panel / plate-top rails (shared rail)
# Top panel slides in -Z from above; pump/coupler tray top edge slides in +Y.
# Same channel position serves both motions.
# Exterior rail: Z=71.6..73.6mm, Interior rail: Z=77.0..79.0mm
# Channel: Z=73.6..77.0mm (3.4mm wide)
# INTERIOR_Z_END = 73.6mm = inner face of top panel = top edge of interior plates
# TOP_PANEL_RAIL_INT top face at Z=73.6mm → TOP_PANEL_RAIL_INT_Z0 = 73.6 - RAIL_W = 71.6
# TOP_PANEL_RAIL_EXT_Z0 = 73.6 + CHANNEL_W = 73.6 + 3.4 = 77.0
# TOP_PANEL_RAIL_EXT_Z0 + RAIL_W = 77.0 + 2.0 = 79.0 = WALL_Z ✓
# Rails run full Y depth (Y=0..WALL_Y)
TOP_PANEL_RAIL_INT_Z0 = INTERIOR_Z_END - RAIL_W         # 73.6 - 2.0 = 71.6
TOP_PANEL_RAIL_EXT_Z0 = INTERIOR_Z_END + CHANNEL_W      # 73.6 + 3.4 = 77.0

rail_top_panel_int = add_rail("Feature 8: Top panel / plate-top rail interior",
                     y0=PASS_THRU_GAP, z0=TOP_PANEL_RAIL_INT_Z0, rail_dy=WALL_Y - 2 * PASS_THRU_GAP, rail_dz=RAIL_W)
wall = wall.union(rail_top_panel_int)

rail_top_panel_ext = add_rail("Feature 9: Top panel / plate-top rail exterior",
                     y0=PASS_THRU_GAP, z0=TOP_PANEL_RAIL_EXT_Z0, rail_dy=WALL_Y - 2 * PASS_THRU_GAP, rail_dz=RAIL_W)
wall = wall.union(rail_top_panel_ext)
print(f"    Top panel/plate-top channel: Z={TOP_PANEL_RAIL_INT_Z0+RAIL_W:.1f}..{TOP_PANEL_RAIL_EXT_Z0:.1f}mm ({CHANNEL_W}mm wide)")

# Features 10-13: Interior plate rails (plates slide in -Z, gripped in Y)
# Same structure as back/front panel rails — vertical rail pairs at each plate's
# Y position, running Z=PASS_THRU_GAP to Z=WALL_Z-2*PASS_THRU_GAP (gapped at
# bottom and top for horizontal rails).
for label, y_center in [("Pump tray", PUMP_TRAY_Y_CENTER),
                         ("Coupler tray", COUPLER_TRAY_Y_CENTER)]:
    rail_back_y0 = y_center - CHANNEL_W / 2 - RAIL_W  # back rail
    rail_front_y0 = y_center + CHANNEL_W / 2            # front rail

    rail_back = add_rail(f"{label} rail back",
                    y0=rail_back_y0, z0=PASS_THRU_GAP, rail_dy=RAIL_W, rail_dz=WALL_Z - PASS_THRU_GAP * 2)
    wall = wall.union(rail_back)

    rail_front = add_rail(f"{label} rail front",
                    y0=rail_front_y0, z0=PASS_THRU_GAP, rail_dy=RAIL_W, rail_dz=WALL_Z - PASS_THRU_GAP * 2)
    wall = wall.union(rail_front)
    print(f"    {label} channel: Y={rail_back_y0+RAIL_W:.1f}..{rail_front_y0:.1f}mm ({CHANNEL_W}mm wide)")

# Cutouts in horizontal rails for interior plates to pass through
# Each cutout is CHANNEL_W (3.4mm) wide in Y, centered on the plate Y center.
# Applied to: Bottom panel rail interior, Top panel rail interior, Top panel rail exterior
for label, y_center in [("pump tray", PUMP_TRAY_Y_CENTER),
                         ("coupler tray", COUPLER_TRAY_Y_CENTER)]:
    cutout_y0 = y_center - CHANNEL_W / 2
    for cut_label, cut_z0, cut_dz in [
        ("Bottom panel rail interior", BOTTOM_PANEL_RAIL_INT_Z0, RAIL_W),
        ("Top panel rail interior", TOP_PANEL_RAIL_INT_Z0, RAIL_W),
        ("Top panel rail exterior", TOP_PANEL_RAIL_EXT_Z0, RAIL_W),
    ]:
        cutout = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(WALL_T, cutout_y0, cut_z0))
            .box(RAIL_H, CHANNEL_W, cut_dz, centered=False)
        )
        wall = wall.cut(cutout)
        print(f"  [-] Cutout in {cut_label} for {label}: Y={cutout_y0:.1f}..{cutout_y0+CHANNEL_W:.1f}")

# Export STEP file

OUTPUT_STEP = Path(__file__).resolve().parent / "left-wall-cadquery.step"
print(f"Exporting STEP file → {OUTPUT_STEP}")
cq.exporters.export(wall, str(OUTPUT_STEP))
print()
