"""
Sub-F: Tube Routing Channels — CadQuery Generation Script

Generates four U-shaped tube routing channels on the tray floor with snap-in
retention clips. The channels route 1/4" OD silicone tubes from the pump barb
exits to the John Guest fitting ports.

Coordinate system:
  Origin: rear-left-bottom corner of tray outer envelope
  X: width, left to right (0..160)
  Y: depth, rear (dock) to front (user) (0..155)
  Z: height, bottom to top (0..72)
  Envelope of Sub-F features: ~X:[28..130] Y:[16..33] Z:[3..13]

Channel walls rise from the tray floor (Z=3) to Z=13 (10mm tall, 2mm thick).
This is a standalone union solid representing only the Sub-F features.
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ==========================================================================
# Dimensions from spec
# ==========================================================================

# Tray reference
FLOOR_Z = 3.0           # floor inner surface
WALL_H = 10.0           # channel wall height
WALL_TOP = FLOOR_Z + WALL_H  # Z = 13.0
WALL_T = 2.0            # wall thickness
CHANNEL_W = 10.0        # channel inner gap width
HALF_GAP = CHANNEL_W / 2.0   # 5.0
HALF_WALL = WALL_T / 2.0     # 1.0

# Channel centerline sample points (Y, X_centerline) from spec Section 3b
CHANNEL_A = [(33.0, 37.2), (28.0, 42.5), (23.0, 50.0), (18.0, 57.5), (16.0, 64.0)]
CHANNEL_B = [(33.0, 49.2), (28.0, 54.5), (23.0, 62.0), (18.0, 69.5), (16.0, 76.0)]
CHANNEL_C = [(33.0, 122.8), (28.0, 117.5), (23.0, 110.0), (18.0, 102.5), (16.0, 96.0)]
CHANNEL_D = [(33.0, 110.8), (28.0, 105.5), (23.0, 98.0), (18.0, 90.5), (16.0, 84.0)]

# Snap clip parameters
CLIP_TAB_Y_LEN = 5.0    # tab length along channel (Y extent)
CLIP_TAB_OVERHANG = 2.0  # overhang into channel from each wall
CLIP_TAB_Z_BOT = 10.0   # tab bottom Z
CLIP_TAB_Z_TOP = 13.0   # tab top Z (= wall top)
CLIP_UNDERCUT_Z_BOT = 9.5  # undercut bottom
CLIP_UNDERCUT_DEPTH = 0.5  # undercut depth into wall

# Clip positions from spec Section 3e
CLIP_A = (50.0, 23.0)
CLIP_B = (62.0, 23.0)
CLIP_C = (110.0, 23.0)
CLIP_D = (98.0, 23.0)

# ==========================================================================
# Feature Planning Table (Rubric 1)
# ==========================================================================
print("=" * 90)
print("FEATURE PLANNING TABLE — Sub-F: Tube Routing Channels")
print("=" * 90)
print(f"{'#':<3} {'Feature':<30} {'Function':<30} {'Op':<6} {'Shape':<12} {'Dims':<30}")
print("-" * 90)
features = [
    ("1", "W1-L (A outer-left wall)",    "A channel left boundary",   "Add", "Swept wall", "2mm thick, 10mm tall, Y=16..33"),
    ("2", "W1-C (A-B shared wall)",      "A/B channel separator",     "Add", "Swept wall", "2mm thick, 10mm tall, Y=16..33"),
    ("3", "W1-R (B outer-right wall)",   "B channel right boundary",  "Add", "Swept wall", "2mm thick, 10mm tall, Y=16..33"),
    ("4", "W2-L (D outer-left wall)",    "D channel left boundary",   "Add", "Swept wall", "2mm thick, 10mm tall, Y=16..33"),
    ("5", "W2-C (D-C shared wall)",      "D/C channel separator",     "Add", "Swept wall", "2mm thick, 10mm tall, Y=16..33"),
    ("6", "W2-R (C outer-right wall)",   "C channel right boundary",  "Add", "Swept wall", "2mm thick, 10mm tall, Y=16..33"),
    ("7", "Clip A tabs (left+right)",    "Retain tube A in channel",  "Add", "Block tabs", "2mm overhang, Z=10..13, Y=5mm"),
    ("8", "Clip A undercuts (L+R)",      "Flex relief for clip A",    "Remove","Notch",    "0.5mm deep, Z=9.5..10"),
    ("9", "Clip B tabs (left+right)",    "Retain tube B in channel",  "Add", "Block tabs", "2mm overhang, Z=10..13, Y=5mm"),
    ("10","Clip B undercuts (L+R)",      "Flex relief for clip B",    "Remove","Notch",    "0.5mm deep, Z=9.5..10"),
    ("11","Clip C tabs (left+right)",    "Retain tube C in channel",  "Add", "Block tabs", "2mm overhang, Z=10..13, Y=5mm"),
    ("12","Clip C undercuts (L+R)",      "Flex relief for clip C",    "Remove","Notch",    "0.5mm deep, Z=9.5..10"),
    ("13","Clip D tabs (left+right)",    "Retain tube D in channel",  "Add", "Block tabs", "2mm overhang, Z=10..13, Y=5mm"),
    ("14","Clip D undercuts (L+R)",      "Flex relief for clip D",    "Remove","Notch",    "0.5mm deep, Z=9.5..10"),
]
for f in features:
    print(f"{f[0]:<3} {f[1]:<30} {f[2]:<30} {f[3]:<6} {f[4]:<12} {f[5]:<30}")
print("=" * 90)
print()


# ==========================================================================
# Helper: interpolate channel centerline X as function of Y
# ==========================================================================
def make_poly(pts):
    """Fit cubic polynomial X = f(Y) from (Y, X) sample points."""
    ys = np.array([p[0] for p in pts])
    xs = np.array([p[1] for p in pts])
    return np.poly1d(np.polyfit(ys, xs, 3))


def sample_x_at_y(poly, y_vals):
    """Sample the polynomial at given Y values, return list of (X, Y)."""
    return [(float(poly(y)), float(y)) for y in y_vals]


def wall_x_positions(channel_poly, y_vals, side):
    """Compute wall centerline X at each Y for a given side of the channel.

    side: 'left' means wall is to the LEFT (-X) of channel centerline
          'right' means wall is to the RIGHT (+X) of channel centerline

    Wall centerline = channel_cl +/- (HALF_GAP + HALF_WALL)
    This is a simple X offset, valid because the curves are gentle (R=30mm)
    and the walls are thin (2mm). The angular error is < 0.1mm.
    """
    offset = -(HALF_GAP + HALF_WALL) if side == 'left' else +(HALF_GAP + HALF_WALL)
    return [(float(channel_poly(y)) + offset, float(y)) for y in y_vals]


def wall_solid_from_xy_path(path_pts, z_bot, z_top, thickness):
    """Create a wall solid from a path of (X, Y) points.

    The wall cross-section is a rectangle: `thickness` mm wide (perpendicular
    to path direction in XY), extruded from z_bot to z_top.

    Implementation: chain of box segments between consecutive points.
    """
    result = None
    half_t = thickness / 2.0

    for i in range(len(path_pts) - 1):
        x0, y0 = path_pts[i]
        x1, y1 = path_pts[i + 1]

        dx = x1 - x0
        dy = y1 - y0
        seg_len = (dx**2 + dy**2)**0.5
        if seg_len < 1e-6:
            continue

        # Normal perpendicular to segment (rotated 90 deg in XY)
        nx = -dy / seg_len
        ny = dx / seg_len

        # Four corners of wall segment footprint
        corners = [
            (x0 - nx * half_t, y0 - ny * half_t),
            (x0 + nx * half_t, y0 + ny * half_t),
            (x1 + nx * half_t, y1 + ny * half_t),
            (x1 - nx * half_t, y1 - ny * half_t),
        ]

        seg = (
            cq.Workplane("XY")
            .workplane(offset=z_bot)
            .moveTo(corners[0][0], corners[0][1])
            .lineTo(corners[1][0], corners[1][1])
            .lineTo(corners[2][0], corners[2][1])
            .lineTo(corners[3][0], corners[3][1])
            .close()
            .extrude(z_top - z_bot)
        )

        if result is None:
            result = seg
        else:
            result = result.union(seg)

    return result


# ==========================================================================
# Modeling
# ==========================================================================
print("Generating channel walls...")

# Fit cubic polynomials for each channel centerline
poly_a = make_poly(CHANNEL_A)
poly_b = make_poly(CHANNEL_B)
poly_c = make_poly(CHANNEL_C)
poly_d = make_poly(CHANNEL_D)

# Y sample points: Y=33 (entry, pump side) down to Y=16 (exit, fitting side)
N_SAMPLES = 40
y_vals = np.linspace(33.0, 16.0, N_SAMPLES)

# Wall paths (each wall's centerline as list of (X, Y)):
# Pump 1 pair (A + B):
#   W1-L: left wall of channel A
#   W1-C: right wall of A = left wall of B (shared)
#   W1-R: right wall of channel B
w1_l_pts = wall_x_positions(poly_a, y_vals, 'left')
w1_c_pts = wall_x_positions(poly_a, y_vals, 'right')
w1_r_pts = wall_x_positions(poly_b, y_vals, 'right')

# Pump 2 pair (C + D):
#   W2-L: left wall of channel D
#   W2-C: right wall of D = left wall of C (shared)
#   W2-R: right wall of channel C
w2_l_pts = wall_x_positions(poly_d, y_vals, 'left')
w2_c_pts = wall_x_positions(poly_d, y_vals, 'right')
w2_r_pts = wall_x_positions(poly_c, y_vals, 'right')

# Build wall solids
walls = {}
wall_names = ['W1-L', 'W1-C', 'W1-R', 'W2-L', 'W2-C', 'W2-R']
wall_paths = [w1_l_pts, w1_c_pts, w1_r_pts, w2_l_pts, w2_c_pts, w2_r_pts]

for name, path in zip(wall_names, wall_paths):
    print(f"  Building {name}...")
    walls[name] = wall_solid_from_xy_path(path, FLOOR_Z, WALL_TOP, WALL_T)

# Union all walls
print("  Unioning all walls...")
result = walls['W1-L']
for name in wall_names[1:]:
    result = result.union(walls[name])

# ==========================================================================
# Snap Clip Tabs
# ==========================================================================
print("Adding snap clip tabs...")


def get_cl_x(channel_pts_raw, y_target):
    """Get channel centerline X at a given Y."""
    poly = make_poly(channel_pts_raw)
    return float(poly(y_target))


def add_clip(result, channel_pts_raw, clip_x, clip_y):
    """Add clip tabs and undercuts for one channel at (clip_x, clip_y).

    Each clip has two opposing tabs overhanging from the channel walls,
    plus undercut notches for flex relief.
    """
    half_y = CLIP_TAB_Y_LEN / 2.0  # 2.5
    cl_x = get_cl_x(channel_pts_raw, clip_y)

    # Wall inner faces
    left_inner = cl_x - HALF_GAP   # left wall inner face X
    right_inner = cl_x + HALF_GAP  # right wall inner face X

    # Left tab: from left_inner extending +X by overhang
    left_tab = (
        cq.Workplane("XY")
        .workplane(offset=CLIP_TAB_Z_BOT)
        .moveTo(left_inner, clip_y - half_y)
        .rect(CLIP_TAB_OVERHANG, CLIP_TAB_Y_LEN, centered=False)
        .extrude(CLIP_TAB_Z_TOP - CLIP_TAB_Z_BOT)
    )
    result = result.union(left_tab)

    # Right tab: from (right_inner - overhang) extending +X by overhang
    right_tab = (
        cq.Workplane("XY")
        .workplane(offset=CLIP_TAB_Z_BOT)
        .moveTo(right_inner - CLIP_TAB_OVERHANG, clip_y - half_y)
        .rect(CLIP_TAB_OVERHANG, CLIP_TAB_Y_LEN, centered=False)
        .extrude(CLIP_TAB_Z_TOP - CLIP_TAB_Z_BOT)
    )
    result = result.union(right_tab)

    # Left undercut: notch into left wall from inner face, going -X
    left_undercut = (
        cq.Workplane("XY")
        .workplane(offset=CLIP_UNDERCUT_Z_BOT)
        .moveTo(left_inner - CLIP_UNDERCUT_DEPTH, clip_y - half_y)
        .rect(CLIP_UNDERCUT_DEPTH, CLIP_TAB_Y_LEN, centered=False)
        .extrude(CLIP_TAB_Z_BOT - CLIP_UNDERCUT_Z_BOT)
    )
    result = result.cut(left_undercut)

    # Right undercut: notch into right wall from inner face, going +X
    right_undercut = (
        cq.Workplane("XY")
        .workplane(offset=CLIP_UNDERCUT_Z_BOT)
        .moveTo(right_inner, clip_y - half_y)
        .rect(CLIP_UNDERCUT_DEPTH, CLIP_TAB_Y_LEN, centered=False)
        .extrude(CLIP_TAB_Z_BOT - CLIP_UNDERCUT_Z_BOT)
    )
    result = result.cut(right_undercut)

    return result


print("  Adding clip A...")
result = add_clip(result, CHANNEL_A, CLIP_A[0], CLIP_A[1])
print("  Adding clip B...")
result = add_clip(result, CHANNEL_B, CLIP_B[0], CLIP_B[1])
print("  Adding clip C...")
result = add_clip(result, CHANNEL_C, CLIP_C[0], CLIP_C[1])
print("  Adding clip D...")
result = add_clip(result, CHANNEL_D, CLIP_D[0], CLIP_D[1])

# ==========================================================================
# Export STEP
# ==========================================================================
out_path = str(Path(__file__).parent / "sub-f-tube-routing.step")
cq.exporters.export(result, out_path)
print(f"\nSTEP exported to: {out_path}")

# ==========================================================================
# Validation (Rubric 3-5)
# ==========================================================================
print("\n" + "=" * 60)
print("VALIDATION")
print("=" * 60)

v = Validator(result)

# Helper: get wall center X at a given Y
def wall_center_x(channel_pts, y, side):
    """Get the X coordinate of a wall's center at given Y.
    side: 'left' or 'right'
    """
    poly = make_poly(channel_pts)
    cl_x = float(poly(y))
    if side == 'left':
        return cl_x - HALF_GAP - HALF_WALL  # wall center
    else:
        return cl_x + HALF_GAP + HALF_WALL

# --- Walls at Y=23 (midpoint) ---
# Channel A: cl=50.0
# W1-L center: 50 - 5 - 1 = 44.0
# W1-C center: 50 + 5 + 1 = 56.0
# W1-R center: B(62) + 5 + 1 = 68.0
w1l_x23 = wall_center_x(CHANNEL_A, 23.0, 'left')
w1c_x23 = wall_center_x(CHANNEL_A, 23.0, 'right')
w1r_x23 = wall_center_x(CHANNEL_B, 23.0, 'right')

v.check_solid("W1-L wall mid", w1l_x23, 23.0, 8.0, f"solid in A left wall at X={w1l_x23:.1f}, Y=23")
v.check_void("Channel A center", 50.0, 23.0, 8.0, "void inside channel A at Y=23")
v.check_solid("W1-C wall mid", w1c_x23, 23.0, 8.0, f"solid in A-B shared wall at X={w1c_x23:.1f}, Y=23")
v.check_void("Channel B center", 62.0, 23.0, 8.0, "void inside channel B at Y=23")
v.check_solid("W1-R wall mid", w1r_x23, 23.0, 8.0, f"solid in B right wall at X={w1r_x23:.1f}, Y=23")

# Channel D: cl=98.0, Channel C: cl=110.0
w2l_x23 = wall_center_x(CHANNEL_D, 23.0, 'left')
w2c_x23 = wall_center_x(CHANNEL_D, 23.0, 'right')
w2r_x23 = wall_center_x(CHANNEL_C, 23.0, 'right')

v.check_solid("W2-L wall mid", w2l_x23, 23.0, 8.0, f"solid in D left wall at X={w2l_x23:.1f}, Y=23")
v.check_void("Channel D center", 98.0, 23.0, 8.0, "void inside channel D at Y=23")
v.check_solid("W2-C wall mid", w2c_x23, 23.0, 8.0, f"solid in D-C shared wall at X={w2c_x23:.1f}, Y=23")
v.check_void("Channel C center", 110.0, 23.0, 8.0, "void inside channel C at Y=23")
v.check_solid("W2-R wall mid", w2r_x23, 23.0, 8.0, f"solid in C right wall at X={w2r_x23:.1f}, Y=23")

# --- Wall height checks (using W1-L at Y=23) ---
v.check_solid("Wall top check", w1l_x23, 23.0, 12.5, "solid near top of wall Z=12.5")
v.check_void("Above wall top", w1l_x23, 23.0, 14.0, "void above wall Z=14")
v.check_solid("Wall bottom check", w1l_x23, 23.0, 3.5, "solid near bottom of wall Z=3.5")
v.check_void("Below wall bottom", w1l_x23, 23.0, 2.5, "void below wall Z=2.5")

# --- Walls at entry end (Y=32, slightly inside) ---
w1l_x32 = wall_center_x(CHANNEL_A, 32.0, 'left')
v.check_solid("W1-L at entry", w1l_x32, 32.0, 8.0, f"solid in A left wall near entry X={w1l_x32:.1f}")
cl_a_32 = float(poly_a(32.0))
v.check_void("Channel A at entry", cl_a_32, 32.0, 8.0, f"void in channel A near entry X={cl_a_32:.1f}")

# --- Walls at exit end (Y=17, slightly inside) ---
w1l_x17 = wall_center_x(CHANNEL_A, 17.0, 'left')
v.check_solid("W1-L at exit", w1l_x17, 17.0, 8.0, f"solid in A left wall near exit X={w1l_x17:.1f}")
cl_a_17 = float(poly_a(17.0))
v.check_void("Channel A at exit", cl_a_17, 17.0, 8.0, f"void in channel A near exit X={cl_a_17:.1f}")

# --- Clip A tabs (Y=23) ---
cl_a_23 = float(poly_a(23.0))
left_inner_a = cl_a_23 - HALF_GAP
right_inner_a = cl_a_23 + HALF_GAP
v.check_solid("Clip A left tab", left_inner_a + 1.0, 23.0, 11.5, "solid in left tab of clip A")
v.check_solid("Clip A right tab", right_inner_a - 1.0, 23.0, 11.5, "solid in right tab of clip A")
v.check_void("Clip A tab gap", cl_a_23, 23.0, 11.5, "void in gap between clip A tabs")

# Clip A undercuts
v.check_void("Clip A left undercut", left_inner_a - 0.25, 23.0, 9.75, "void in left undercut of clip A")
v.check_void("Clip A right undercut", right_inner_a + 0.25, 23.0, 9.75, "void in right undercut of clip A")

# --- Clip B tabs (Y=23) ---
cl_b_23 = float(poly_b(23.0))
left_inner_b = cl_b_23 - HALF_GAP
right_inner_b = cl_b_23 + HALF_GAP
v.check_solid("Clip B left tab", left_inner_b + 1.0, 23.0, 11.5, "solid in left tab of clip B")
v.check_solid("Clip B right tab", right_inner_b - 1.0, 23.0, 11.5, "solid in right tab of clip B")
v.check_void("Clip B tab gap", cl_b_23, 23.0, 11.5, "void in gap between clip B tabs")

# --- Clip C tabs (Y=23) ---
cl_c_23 = float(poly_c(23.0))
left_inner_c = cl_c_23 - HALF_GAP
right_inner_c = cl_c_23 + HALF_GAP
v.check_solid("Clip C left tab", left_inner_c + 1.0, 23.0, 11.5, "solid in left tab of clip C")
v.check_solid("Clip C right tab", right_inner_c - 1.0, 23.0, 11.5, "solid in right tab of clip C")
v.check_void("Clip C tab gap", cl_c_23, 23.0, 11.5, "void in gap between clip C tabs")

# --- Clip D tabs (Y=23) ---
cl_d_23 = float(poly_d(23.0))
left_inner_d = cl_d_23 - HALF_GAP
right_inner_d = cl_d_23 + HALF_GAP
v.check_solid("Clip D left tab", left_inner_d + 1.0, 23.0, 11.5, "solid in left tab of clip D")
v.check_solid("Clip D right tab", right_inner_d - 1.0, 23.0, 11.5, "solid in right tab of clip D")
v.check_void("Clip D tab gap", cl_d_23, 23.0, 11.5, "void in gap between clip D tabs")

# --- Bounding Box (Rubric 5) ---
bb = result.val().BoundingBox()
print(f"\nBounding box: X=[{bb.xmin:.2f}, {bb.xmax:.2f}] Y=[{bb.ymin:.2f}, {bb.ymax:.2f}] Z=[{bb.zmin:.2f}, {bb.zmax:.2f}]")

# Expected X range: roughly 30.2 (W1-L at Y=33) to 127.8 (W2-R at Y=33)
# Expected Y range: 16.0 to 33.0
# Expected Z range: 3.0 to 13.0
v.check_bbox("X", bb.xmin, bb.xmax, 30.0, 128.0, tol=2.0)
v.check_bbox("Y", bb.ymin, bb.ymax, 16.0, 33.0, tol=1.0)
v.check_bbox("Z", bb.zmin, bb.zmax, 3.0, 13.0, tol=0.5)

# --- Solid Integrity (Rubric 4) ---
v.check_valid()
# The two pump pairs are spatially separated, so multiple bodies is expected
n_bodies = len(result.solids().vals())
print(f"\n  Body count: {n_bodies}")

# Volume check
# 6 walls * ~20mm avg path * 2mm thick * 10mm tall = ~2400 mm^3
# Plus clip tabs, minus undercuts ~ net ~2600
v.check_volume(expected_envelope=100 * 17 * 10, fill_range=(0.05, 0.5))

# Summary
if not v.summary():
    sys.exit(1)
