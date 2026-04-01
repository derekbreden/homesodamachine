"""
Left Wall — CadQuery STEP Generation Script
Season 2, Phase 7, Item 17 of the pump cartridge build sequence.

Specification source: hardware/printed-parts/cartridge/left-wall/planning/parts.md

The left wall is a flat panel in the YZ plane with thickness in X.
The interior face (at X=WALL_T) carries 10 rail lip bars — two lips per rail,
forming channels that guide the front panel, back panel, bottom panel, top panel,
pump tray, and coupler tray. No retention, detent, or exterior track features.

Coordinate system (part local frame):
  Origin: wall front-bottom-exterior corner (X=0, Y=0, Z=0)
  X: wall thickness axis — exterior face (X=0) to interior face (X=WALL_T=3.0mm)
     Rail lips protrude from X=3.0mm inward to X=6.0mm (+X direction into interior)
  Y: front-to-back axis — front (Y=0) to back (Y=WALL_Y=133.0mm)
  Z: height axis — bottom (Z=0) to top (Z=WALL_Z=79.0mm)
  Envelope (wall body only): 3.0mm (X) x 133.0mm (Y) x 79.0mm (Z)
  Envelope (with rail lips):  6.0mm (X) x 133.0mm (Y) x 79.0mm (Z)
"""

import sys
from pathlib import Path

# Add tools/ to sys.path for step_validate import
# Script is at: hardware/printed-parts/cartridge/left-wall/generate_step_cadquery.py
# parents[4] = project root
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ==============================================================================
# Part parameters (from planning/parts.md)
# ==============================================================================

# Wall body
WALL_T = 3.0     # X — wall thickness (exterior face to interior face)
WALL_Y = 133.0   # Y — wall depth (front to back)
WALL_Z = 105.0   # Z — wall height (bottom to top, was 79.0)

# Rail geometry
LIP_H = 3.0      # X — lip protrusion height from interior face (into interior)
LIP_W = 2.0      # width of each lip in the separation axis direction
CHANNEL_W = 3.4  # gap between lip inner faces (3mm panel + 0.2mm clearance each side)

# Derived
INTERIOR_X = WALL_T           # X=3.0mm — interior face of wall
LIP_TIP_X  = WALL_T + LIP_H  # X=6.0mm — inner face of rail lips (tip of protrusion)
PASS_THRU_GAP = LIP_W + CHANNEL_W  # 5.4mm total allowing pass through

# Interior plate Y positions (wall coordinates)
PUMP_TRAY_Y_CENTER = 56.5    # pump tray front face Y=55.0, back face Y=58.0, center=56.5
COUPLER_TRAY_Y_CENTER = 30.0 # TODO: determine actual position

# Interior coordinate span (between panel inner faces)
INTERIOR_Y_START = 5.0       # inner face of front panel (Y)
INTERIOR_Y_END   = 128.0     # inner face of back panel (Y)
INTERIOR_Z_START = 5.0       # inner face of bottom panel (Z)
INTERIOR_Z_END   = 99.6      # inner face of top rail (Z)

# ==============================================================================
# Rubric 1 — Feature Planning Table (MANDATORY, before coding)
# ==============================================================================

FEATURE_TABLE = """
LEFT WALL — FEATURE PLANNING TABLE (Rubric 1)
==============================================

Part envelope (wall body): 3.0mm (X) x 133.0mm (Y) x 79.0mm (Z)
Part envelope (with lips): 6.0mm (X) x 133.0mm (Y) x 79.0mm (Z)

Coordinate system (Rubric 2):
  Origin: wall front-bottom-exterior corner (X=0, Y=0, Z=0)
  X: wall thickness, exterior (X=0) to interior face (X=3.0); lips extend to X=6.0
  Y: front-to-back, Y=0..133.0mm
  Z: bottom-to-top, Z=0..79.0mm

Interior face: X=3.0mm. Lip protrusion: +X to X=6.0mm.
Channel width (gap between lip inner faces): 3.4mm.
Lip width (in separation axis): 2.0mm. Lip height (protrusion): 3.0mm.

Interior Y span: Y=5.0..128.0mm (123.0mm — inner faces of front and back panels)
Interior Z span: Z=5.0..73.6mm (68.6mm — inner faces of bottom and top panels)

  PASS_THRU_GAP = LIP_W + CHANNEL_W = 5.4mm — gap at each end of a lip where perpendicular panels pass through.

  #   Feature Name                Op    Shape    Axis  Y/Z position                      Z/Y run span                           Notes
  1   Wall body                   Add   Box      —     Origin (0,0,0)                    3.0(X) x 133.0(Y) x 79.0(Z)           Base panel
  2   Front panel Lip A           Add   Box      Z     Y=0.0..2.0                        Z=5.4..73.6 (gapped at bottom+top)     Front edge
  3   Front panel Lip B           Add   Box      Z     Y=5.4..7.4                        Z=5.4..73.6 (gapped at bottom+top)     Channel Y=2.0..5.4
  4   Back panel Lip A            Add   Box      Z     Y=125.6..127.6                    Z=5.4..73.6 (gapped at bottom+top)     Channel Y=127.6..131.0
  5   Back panel Lip B            Add   Box      Z     Y=131.0..133.0                    Z=5.4..73.6 (gapped at bottom+top)     Back edge
  6   Bottom panel Lip A          Add   Box      Y     Z=0.0..2.0                        Y=0..133.0 (full width)                Bottom edge
  7   Bottom panel Lip B          Add   Box      Y     Z=5.4..7.4                        Y=5.4..127.6 (gapped at front+back)    Channel Z=2.0..5.4
  8   Top panel / plate-top Lip A Add   Box      Y     Z=71.6..73.6                      Y=5.4..127.6 (gapped at front+back)    Shared: top panel + plate top
  9   Top panel / plate-top Lip B Add   Box      Y     Z=77.0..79.0                      Y=5.4..127.6 (gapped at front+back)    Top edge; channel Z=73.6..77.0
  Total: 1 wall body + 8 rail lip bars = 9 features

Panel/plate rail channels:
  Front panel:  Y=2.0..5.4mm (3.4mm wide in Y), slides in Z
  Back panel:   Y=127.6..131.0mm (3.4mm wide in Y), slides in Z
  Bottom panel: Z=2.0..5.4mm (3.4mm wide in Z), slides in Y
  Top panel:    Z=73.6..77.0mm (3.4mm wide in Z), slides in Z from above

Pass-through gaps: Each lip is shortened by PASS_THRU_GAP (5.4mm) at each end where
a perpendicular panel's rail crosses. This prevents lip bars from colliding at corners.
Exception: Bottom Lip A runs full width (Z=0..2 is below where vertical lips start).

Interior validation points:
  Interior Y: 5.0mm to 128.0mm (123.0mm span)
  Interior Z: 5.0mm to 73.6mm (68.6mm span — matches plate height exactly)
"""

print("=" * 70)
print("LEFT WALL — CadQuery STEP Generation")
print("=" * 70)
print(FEATURE_TABLE)
print("Building model...")

# ==============================================================================
# Rubric 2 — Coordinate System Declaration (in FEATURE_TABLE above)
# ==============================================================================

# ==============================================================================
# Modeling
# ==============================================================================

# ------------------------------------------------------------------------------
# Feature 1: Wall body
# XY workplane: box(W, D, H, centered=False) → X:[0,W] Y:[0,D] Z:[0,H]
# box(WALL_T, WALL_Y, WALL_Z, centered=False) → X:[0,3.0] Y:[0,133.0] Z:[0,79.0]
# ------------------------------------------------------------------------------
wall = cq.Workplane("XY").box(WALL_T, WALL_Y, WALL_Z, centered=False)
print(f"  [+] Feature 1: Wall body ({WALL_T} x {WALL_Y} x {WALL_Z} mm, X x Y x Z)")

# Helper: add a rail lip bar to the wall.
# All lips protrude from the interior face X=WALL_T in +X direction.
# Lip is a box: X span = WALL_T to WALL_T+LIP_H, Y span = [y0, y0+lip_dy], Z span = [z0, z0+lip_dz]
# Uses XY workplane: transformed(offset=Vector(x0, y0, z0)).box(dx, dy, dz, centered=False)
# → X:[x0, x0+dx], Y:[y0, y0+dy], Z:[z0, z0+dz]
def add_lip(label, y0, z0, lip_dy, lip_dz):
    """Add a rail lip bar at the given Y,Z start position with the given Y,Z dimensions.
    Lip X span: WALL_T to WALL_T+LIP_H (protrudes from interior face inward)."""
    lip = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(WALL_T, y0, z0))
        .box(LIP_H, lip_dy, lip_dz, centered=False)
    )
    print(f"  [+] {label}: Y={y0:.1f}..{y0+lip_dy:.1f}, Z={z0:.1f}..{z0+lip_dz:.1f}, X={WALL_T:.1f}..{LIP_TIP_X:.1f}")
    return lip

# ------------------------------------------------------------------------------
# Features 2-3: Front panel rail lips (panel slides in -Z, gripped in Y)
# Lip A: Y=0.0..2.0mm, Lip B: Y=5.4..7.4mm
# Channel: Y=2.0..5.4mm (3.4mm wide)
# Lips run full Z height (Z=0..WALL_Z)
# ------------------------------------------------------------------------------
FRONT_LIP_A_Y0 = 0.0
FRONT_LIP_B_Y0 = 5.4   # = LIP_W + CHANNEL_W = 2.0 + 3.4

lip_front_a = add_lip("Feature 2: Front panel Lip A",
                       y0=FRONT_LIP_A_Y0, z0=PASS_THRU_GAP, lip_dy=LIP_W, lip_dz=WALL_Z - PASS_THRU_GAP * 2)
wall = wall.union(lip_front_a)

lip_front_b = add_lip("Feature 3: Front panel Lip B",
                       y0=FRONT_LIP_B_Y0, z0=PASS_THRU_GAP, lip_dy=LIP_W, lip_dz=WALL_Z - PASS_THRU_GAP * 2)
wall = wall.union(lip_front_b)
print(f"    Front panel channel: Y={FRONT_LIP_A_Y0+LIP_W:.1f}..{FRONT_LIP_B_Y0:.1f}mm ({CHANNEL_W}mm wide)")

# ------------------------------------------------------------------------------
# Features 4-5: Back panel rail lips (panel slides in -Z, gripped in Y at back)
# Lip A: Y=125.6..127.6mm, Lip B: Y=131.0..133.0mm
# Channel: Y=127.6..131.0mm (3.4mm wide)
# BACK_LIP_B_Y0 + LIP_W = WALL_Y → BACK_LIP_B_Y0 = WALL_Y - LIP_W = 133.0 - 2.0 = 131.0
# BACK_LIP_A_Y0 = WALL_Y - LIP_W - CHANNEL_W - LIP_W = 133.0 - 2.0 - 3.4 - 2.0 = 125.6
# ------------------------------------------------------------------------------
BACK_LIP_B_Y0 = WALL_Y - LIP_W         # 131.0
BACK_LIP_A_Y0 = WALL_Y - LIP_W - CHANNEL_W - LIP_W  # 125.6

lip_back_a = add_lip("Feature 4: Back panel Lip A",
                      y0=BACK_LIP_A_Y0, z0=PASS_THRU_GAP, lip_dy=LIP_W, lip_dz=WALL_Z - 2 * PASS_THRU_GAP)
wall = wall.union(lip_back_a)

lip_back_b = add_lip("Feature 5: Back panel Lip B",
                      y0=BACK_LIP_B_Y0, z0=PASS_THRU_GAP, lip_dy=LIP_W, lip_dz=WALL_Z - 2 * PASS_THRU_GAP)
wall = wall.union(lip_back_b)
print(f"    Back panel channel: Y={BACK_LIP_A_Y0+LIP_W:.1f}..{BACK_LIP_B_Y0:.1f}mm ({CHANNEL_W}mm wide)")

# ------------------------------------------------------------------------------
# Features 6-7: Bottom panel rail lips (panel slides in +Y, gripped in Z at bottom)
# Lip A: Z=0.0..2.0mm, Lip B: Z=5.4..7.4mm
# Channel: Z=2.0..5.4mm (3.4mm wide)
# Lips run full Y depth (Y=0..WALL_Y)
# ------------------------------------------------------------------------------
BOTTOM_LIP_A_Z0 = 0.0
BOTTOM_LIP_B_Z0 = 5.4   # = LIP_W + CHANNEL_W

lip_bottom_a = add_lip("Feature 6: Bottom panel Lip A",
                        y0=0.0, z0=BOTTOM_LIP_A_Z0, lip_dy=WALL_Y, lip_dz=LIP_W)
wall = wall.union(lip_bottom_a)

lip_bottom_b = add_lip("Feature 7: Bottom panel Lip B",
                        y0=PASS_THRU_GAP, z0=BOTTOM_LIP_B_Z0, lip_dy=WALL_Y - 2 * PASS_THRU_GAP, lip_dz=LIP_W)
wall = wall.union(lip_bottom_b)
print(f"    Bottom panel channel: Z={BOTTOM_LIP_A_Z0+LIP_W:.1f}..{BOTTOM_LIP_B_Z0:.1f}mm ({CHANNEL_W}mm wide)")

# ------------------------------------------------------------------------------
# Features 8-9: Top panel / plate-top rail lips (shared rail)
# Top panel slides in -Z from above; pump/coupler tray top edge slides in +Y.
# Same channel position serves both motions.
# Lip A: Z=71.6..73.6mm, Lip B: Z=77.0..79.0mm
# Channel: Z=73.6..77.0mm (3.4mm wide)
# INTERIOR_Z_END = 73.6mm = inner face of top panel = top edge of interior plates
# TOP_LIP_A top face at Z=73.6mm → TOP_LIP_A_Z0 = 73.6 - LIP_W = 71.6
# TOP_LIP_B_Z0 = 73.6 + CHANNEL_W = 73.6 + 3.4 = 77.0
# TOP_LIP_B_Z0 + LIP_W = 77.0 + 2.0 = 79.0 = WALL_Z ✓
# Lips run full Y depth (Y=0..WALL_Y)
# ------------------------------------------------------------------------------
TOP_LIP_A_Z0 = INTERIOR_Z_END - LIP_W         # 73.6 - 2.0 = 71.6
TOP_LIP_B_Z0 = INTERIOR_Z_END + CHANNEL_W      # 73.6 + 3.4 = 77.0

lip_top_a = add_lip("Feature 8: Top panel / plate-top Lip A",
                     y0=PASS_THRU_GAP, z0=TOP_LIP_A_Z0, lip_dy=WALL_Y - 2 * PASS_THRU_GAP, lip_dz=LIP_W)
wall = wall.union(lip_top_a)

lip_top_b = add_lip("Feature 9: Top panel / plate-top Lip B",
                     y0=PASS_THRU_GAP, z0=TOP_LIP_B_Z0, lip_dy=WALL_Y - 2 * PASS_THRU_GAP, lip_dz=LIP_W)
wall = wall.union(lip_top_b)
print(f"    Top panel/plate-top channel: Z={TOP_LIP_A_Z0+LIP_W:.1f}..{TOP_LIP_B_Z0:.1f}mm ({CHANNEL_W}mm wide)")

# ------------------------------------------------------------------------------
# Features 10-13: Interior plate rail lips (plates slide in -Z, gripped in Y)
# Same structure as front/back panel rails — vertical lip pairs at each plate's
# Y position, running Z=PASS_THRU_GAP to Z=WALL_Z-2*PASS_THRU_GAP (gapped at
# bottom and top for horizontal rails).
# ------------------------------------------------------------------------------
for label, y_center in [("Pump tray", PUMP_TRAY_Y_CENTER),
                         ("Coupler tray", COUPLER_TRAY_Y_CENTER)]:
    lip_a_y0 = y_center - CHANNEL_W / 2 - LIP_W  # outer lip
    lip_b_y0 = y_center + CHANNEL_W / 2            # inner lip

    lip_a = add_lip(f"{label} Lip A",
                    y0=lip_a_y0, z0=PASS_THRU_GAP, lip_dy=LIP_W, lip_dz=WALL_Z - PASS_THRU_GAP * 2)
    wall = wall.union(lip_a)

    lip_b = add_lip(f"{label} Lip B",
                    y0=lip_b_y0, z0=PASS_THRU_GAP, lip_dy=LIP_W, lip_dz=WALL_Z - PASS_THRU_GAP * 2)
    wall = wall.union(lip_b)
    print(f"    {label} channel: Y={lip_a_y0+LIP_W:.1f}..{lip_b_y0:.1f}mm ({CHANNEL_W}mm wide)")

# ------------------------------------------------------------------------------
# Cutouts in horizontal lips for interior plates to pass through
# Each cutout is CHANNEL_W (3.4mm) wide in Y, centered on the plate Y center.
# Applied to: Bottom Lip B, Top Lip A, Top Lip B
# ------------------------------------------------------------------------------
for label, y_center in [("pump tray", PUMP_TRAY_Y_CENTER),
                         ("coupler tray", COUPLER_TRAY_Y_CENTER)]:
    cutout_y0 = y_center - CHANNEL_W / 2
    for cut_label, cut_z0, cut_dz in [
        ("Bottom Lip B", BOTTOM_LIP_B_Z0, LIP_W),
        ("Top Lip A", TOP_LIP_A_Z0, LIP_W),
        ("Top Lip B", TOP_LIP_B_Z0, LIP_W),
    ]:
        cutout = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(WALL_T, cutout_y0, cut_z0))
            .box(LIP_H, CHANNEL_W, cut_dz, centered=False)
        )
        wall = wall.cut(cutout)
        print(f"  [-] Cutout in {cut_label} for {label}: Y={cutout_y0:.1f}..{cutout_y0+CHANNEL_W:.1f}")

# ==============================================================================
# Export STEP file
# ==============================================================================

OUTPUT_STEP = Path(__file__).resolve().parent / "left-wall-cadquery.step"
print(f"Exporting STEP file → {OUTPUT_STEP}")
cq.exporters.export(wall, str(OUTPUT_STEP))
print("Export complete.")
print()

# ==============================================================================
# Validation (Rubrics 3, 4, 5)
# ==============================================================================

print("=" * 70)
print("VALIDATION")
print("=" * 70)
print()

v = Validator(wall)

# Interior face X probe level — used for all lip probes
# Solid at X=4.5 (mid-depth of lip, between X=3.0 and X=6.0)
LIP_MID_X = WALL_T + LIP_H / 2   # 3.0 + 1.5 = 4.5
WALL_MID_X = WALL_T / 2           # 1.5

# --- Feature 1: Wall body ---
print("--- Feature 1: Wall body ---")
v.check_solid("Wall body interior center",
              WALL_MID_X, WALL_Y / 2, WALL_Z / 2,
              "solid at wall body center")
v.check_solid("Wall body front face",
              WALL_MID_X, 0.1, WALL_Z / 2,
              "solid near Y=0 front face")
v.check_solid("Wall body back face",
              WALL_MID_X, WALL_Y - 0.1, WALL_Z / 2,
              "solid near Y=WALL_Y back face")
v.check_solid("Wall body bottom face",
              WALL_MID_X, WALL_Y / 2, 0.1,
              "solid near Z=0 bottom face")
v.check_solid("Wall body top face",
              WALL_MID_X, WALL_Y / 2, WALL_Z - 0.1,
              "solid near Z=WALL_Z top face")
v.check_solid("Wall body exterior face",
              0.1, WALL_Y / 2, WALL_Z / 2,
              "solid near X=0 exterior face")
v.check_solid("Wall body interior face",
              WALL_T - 0.1, WALL_Y / 2, WALL_Z / 2,
              "solid just inside interior face")
# Void outside wall
v.check_void("Void beyond exterior face",
             -0.5, WALL_Y / 2, WALL_Z / 2,
             "void outside exterior face X<0")
v.check_void("Void beyond interior face (no lip)",
             WALL_T + LIP_H + 0.5, WALL_Y / 2, 30.0,
             "void past lip tip X>6.0 in a region with no lips (Z=30mm, no lip there)")
print()

# --- Features 2-3: Front panel rail ---
print("--- Features 2-3: Front panel rail ---")
# Lip A: Y=0..2.0, Z=0..79.0
LIP_A_Y_MID = FRONT_LIP_A_Y0 + LIP_W / 2    # 1.0
v.check_solid("Front Lip A solid mid",
              LIP_MID_X, LIP_A_Y_MID, WALL_Z / 2,
              f"solid inside front Lip A (X={LIP_MID_X}, Y={LIP_A_Y_MID}, Z={WALL_Z/2})")
# Lip B: Y=5.4..7.4
LIP_B_Y_MID = FRONT_LIP_B_Y0 + LIP_W / 2    # 6.4
v.check_solid("Front Lip B solid mid",
              LIP_MID_X, LIP_B_Y_MID, WALL_Z / 2,
              f"solid inside front Lip B (X={LIP_MID_X}, Y={LIP_B_Y_MID}, Z={WALL_Z/2})")
# Channel void: Y=2.0..5.4, mid Z
FRONT_CHANNEL_Y_MID = (FRONT_LIP_A_Y0 + LIP_W + FRONT_LIP_B_Y0) / 2   # (2.0+5.4)/2 = 3.7
v.check_void("Front panel channel void",
             LIP_MID_X, FRONT_CHANNEL_Y_MID, WALL_Z / 2,
             f"void in front panel channel (Y={FRONT_CHANNEL_Y_MID})")
# Lip A does not extend beyond wall front face
v.check_void("Void beyond front Lip A tip",
             LIP_TIP_X + 0.5, LIP_A_Y_MID, WALL_Z / 2,
             "void past lip tip in +X direction")
print()

# --- Features 4-5: Back panel rail ---
print("--- Features 4-5: Back panel rail ---")
LIP_A_BACK_Y_MID = BACK_LIP_A_Y0 + LIP_W / 2   # 126.6
LIP_B_BACK_Y_MID = BACK_LIP_B_Y0 + LIP_W / 2   # 132.0
v.check_solid("Back Lip A solid mid",
              LIP_MID_X, LIP_A_BACK_Y_MID, WALL_Z / 2,
              f"solid inside back Lip A (Y={LIP_A_BACK_Y_MID})")
v.check_solid("Back Lip B solid mid",
              LIP_MID_X, LIP_B_BACK_Y_MID, WALL_Z / 2,
              f"solid inside back Lip B (Y={LIP_B_BACK_Y_MID})")
BACK_CHANNEL_Y_MID = (BACK_LIP_A_Y0 + LIP_W + BACK_LIP_B_Y0) / 2   # (127.6+131.0)/2=129.3
v.check_void("Back panel channel void",
             LIP_MID_X, BACK_CHANNEL_Y_MID, WALL_Z / 2,
             f"void in back panel channel (Y={BACK_CHANNEL_Y_MID})")
print()

# --- Features 6-7: Bottom panel rail ---
print("--- Features 6-7: Bottom panel rail ---")
LIP_A_BTM_Z_MID = BOTTOM_LIP_A_Z0 + LIP_W / 2   # 1.0
LIP_B_BTM_Z_MID = BOTTOM_LIP_B_Z0 + LIP_W / 2   # 6.4
v.check_solid("Bottom Lip A solid mid",
              LIP_MID_X, WALL_Y / 2, LIP_A_BTM_Z_MID,
              f"solid inside bottom Lip A (Z={LIP_A_BTM_Z_MID})")
v.check_solid("Bottom Lip B solid mid",
              LIP_MID_X, WALL_Y / 2, LIP_B_BTM_Z_MID,
              f"solid inside bottom Lip B (Z={LIP_B_BTM_Z_MID})")
BOTTOM_CHANNEL_Z_MID = (BOTTOM_LIP_A_Z0 + LIP_W + BOTTOM_LIP_B_Z0) / 2  # (2.0+5.4)/2=3.7
v.check_void("Bottom panel channel void",
             LIP_MID_X, WALL_Y / 2, BOTTOM_CHANNEL_Z_MID,
             f"void in bottom panel channel (Z={BOTTOM_CHANNEL_Z_MID})")
print()

# --- Features 8-9: Top panel / plate-top rail ---
print("--- Features 8-9: Top panel / plate-top rail ---")
LIP_A_TOP_Z_MID = TOP_LIP_A_Z0 + LIP_W / 2   # 72.6
LIP_B_TOP_Z_MID = TOP_LIP_B_Z0 + LIP_W / 2   # 78.0
v.check_solid("Top Lip A solid mid",
              LIP_MID_X, WALL_Y / 2, LIP_A_TOP_Z_MID,
              f"solid inside top Lip A (Z={LIP_A_TOP_Z_MID})")
v.check_solid("Top Lip B solid mid",
              LIP_MID_X, WALL_Y / 2, LIP_B_TOP_Z_MID,
              f"solid inside top Lip B (Z={LIP_B_TOP_Z_MID})")
TOP_CHANNEL_Z_MID = INTERIOR_Z_END + CHANNEL_W / 2   # 73.6 + 1.7 = 75.3
v.check_void("Top panel channel void",
             LIP_MID_X, WALL_Y / 2, TOP_CHANNEL_Z_MID,
             f"void in top panel channel (Z={TOP_CHANNEL_Z_MID})")
print()

# --- Channel width verification (orientation check) ---
# Verify channel widths are correct in the separation axis.
# Front/back channel: 3.4mm in Y. Bottom/top/plate channels: 3.4mm in Z.
print("--- Channel width orientation checks ---")

# Front panel channel: solid outside Lip A in -Y (no wall below Y=0)
# Just check solid inside Lip A and void in channel
v.check_solid("Front channel: solid in Lip A at Y=1.0",
              LIP_MID_X, 1.0, WALL_Z / 2,
              "solid at Y=1.0 (inside front Lip A, Y=0..2.0)")
v.check_void("Front channel: void at Y=3.7",
             LIP_MID_X, 3.7, WALL_Z / 2,
             "void at Y=3.7 (inside front panel channel, Y=2.0..5.4)")
v.check_solid("Front channel: solid in Lip B at Y=6.4",
              LIP_MID_X, 6.4, WALL_Z / 2,
              "solid at Y=6.4 (inside front Lip B, Y=5.4..7.4)")
# Verify channel is NOT solid at wrong Z orientation (rotation check):
# If lips ran in Y direction instead of Z, the probe at different Z would miss the lip.
# Confirm solid at Z=20mm and Z=60mm within Lip A Y range (lip runs full Z)
v.check_solid("Front Lip A full Z run at Z=20",
              LIP_MID_X, 1.0, 20.0,
              "solid at Z=20mm — front Lip A runs full height")
v.check_solid("Front Lip A full Z run at Z=60",
              LIP_MID_X, 1.0, 60.0,
              "solid at Z=60mm — front Lip A runs full height")

# Bottom panel channel: solid in Lip A at Z=1.0, void at Z=3.7, solid in Lip B at Z=6.4
v.check_solid("Bottom channel: solid in Lip A at Z=1.0",
              LIP_MID_X, WALL_Y / 2, 1.0,
              "solid at Z=1.0 (inside bottom Lip A, Z=0..2.0)")
v.check_void("Bottom channel: void at Z=3.7",
             LIP_MID_X, WALL_Y / 2, 3.7,
             "void at Z=3.7 (inside bottom panel channel, Z=2.0..5.4)")
v.check_solid("Bottom channel: solid in Lip B at Z=6.4",
              LIP_MID_X, WALL_Y / 2, 6.4,
              "solid at Z=6.4 (inside bottom Lip B, Z=5.4..7.4)")
# Confirm bottom Lip A runs full Y length
v.check_solid("Bottom Lip A full Y run at Y=10",
              LIP_MID_X, 10.0, 1.0,
              "solid at Y=10mm — bottom Lip A runs full depth")
v.check_solid("Bottom Lip A full Y run at Y=120",
              LIP_MID_X, 120.0, 1.0,
              "solid at Y=120mm — bottom Lip A runs full depth")

# Top channel: void at Z=101.3 (center of top channel, 99.6..103.0)
v.check_void("Top channel center void at Z=101.3",
             LIP_MID_X, WALL_Y / 2, 101.3,
             "void at Z=101.3 (top channel center)")
v.check_solid("Top Lip A at Z=98.6",
              LIP_MID_X, WALL_Y / 2, 98.6,
              "solid at Z=98.6 (inside top Lip A, Z=97.6..99.6)")

print()

# --- Interior clear zone: no lips in the interior mid-wall ---
print("--- Interior clear zone ---")
# Interior Y=5..128, Z=5..73.6, X=3..6. Mid-wall in this zone should be VOID
# (no rail lips reach into the middle of the interior).
# Check mid-interior: Y=66.5 (middle of interior), Z=39.3 (middle of interior height).
# At X=4.5 (inside lip zone), this should be void since no lip runs here.
v.check_void("Interior mid zone void (no lip)",
             LIP_MID_X, 66.5, 39.3,
             "void in mid-interior region — no rail lip here (Y=66.5, Z=39.3)")
v.check_void("Interior mid zone void 2 (no lip)",
             LIP_MID_X, 30.0, 39.3,
             "void at Y=30, Z=39.3 — no rail lip in this region")
# Wall body IS solid at same XY but mid-Z
v.check_solid("Wall body solid in clear zone",
              1.5, 66.5, 39.3,
              "solid in wall body at X=1.5, Y=66.5, Z=39.3")
print()

# --- Bounding box (Rubric 5) ---
print("--- Bounding box (Rubric 5) ---")
bb = wall.val().BoundingBox()
print(f"  Actual bounding box:")
print(f"    X: [{bb.xmin:.3f}, {bb.xmax:.3f}]  (expected [0, {LIP_TIP_X}])")
print(f"    Y: [{bb.ymin:.3f}, {bb.ymax:.3f}]  (expected [0, {WALL_Y}])")
print(f"    Z: [{bb.zmin:.3f}, {bb.zmax:.3f}]  (expected [0, {WALL_Z}])")

v.check_bbox("X", bb.xmin, bb.xmax, 0.0, LIP_TIP_X)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, WALL_Y)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, WALL_Z)
print()

# --- Solid integrity (Rubric 4) ---
print("--- Solid integrity (Rubric 4) ---")
v.check_valid()
v.check_single_body()

# Volume estimate:
# Wall body: 3.0 x 133.0 x 79.0 = 31503 mm^3
# Lip bars (10 total):
#   Front A: 3.0 x 2.0 x 79.0 = 474 mm^3
#   Front B: 3.0 x 2.0 x 79.0 = 474 mm^3
#   Back A:  3.0 x 2.0 x 79.0 = 474 mm^3
#   Back B:  3.0 x 2.0 x 79.0 = 474 mm^3
#   Bottom A: 3.0 x 133.0 x 2.0 = 798 mm^3
#   Bottom B: 3.0 x 133.0 x 2.0 = 798 mm^3
#   Top A:    3.0 x 133.0 x 2.0 = 798 mm^3
#   Top B:    3.0 x 133.0 x 2.0 = 798 mm^3
#   Plate btm A: 3.0 x 133.0 x 2.0 = 798 mm^3
#   Plate btm B: 3.0 x 133.0 x 2.0 = 798 mm^3
# Total lips: 4*474 + 6*798 = 1896 + 4788 = 6684 mm^3
# Some overlap at corners (lips share the same XZ/YZ region at edges) — subtract ~10%
# Total estimated: 31503 + 6684*0.9 ~ 31503 + 6016 = 37519 mm^3
# Envelope: 6.0 x 133.0 x 79.0 = 63054 mm^3
# Fill ratio: 37519 / 63054 ~ 0.595 — within (0.4, 0.9)
envelope_vol = LIP_TIP_X * WALL_Y * WALL_Z
v.check_volume(expected_envelope=envelope_vol, fill_range=(0.40, 0.90))
print()

# --- Summary ---
passed = v.summary()

if not passed:
    print()
    print("FAIL: Validation failures detected. Fix model before use.")
    sys.exit(1)

print()
print(f"SUCCESS: STEP file written to:")
print(f"  {OUTPUT_STEP}")
print("Done.")
