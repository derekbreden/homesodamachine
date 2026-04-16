"""
Foam-bag shell: racetrack variant.

Same two-piece design (bottom cup + upper shell) as the circular version,
but the cross-section is a stadium (racetrack) matching the pressed
carbonator tube shape.

Racetrack geometry (from endcap DXF, tube OD):
  Two semicircles of radius R connected by two flat sides of length L.
  Long axis along X.  All concentric layers share the same flat length;
  only the semicircle radius grows with each offset layer.

Bottom cup:  Z=0 to PLAT_BOTTOM.  Prints right-side up (floor on bed).
Upper shell: Z=Z_BOT to SHELL_HEIGHT.  Prints right-side up.
             Inner wall + channel rings touch bed at Z_BOT.
             Annular floor bridges inner wall to channel inner ring at
             Z=PLAT_BOTTOM (3 mm above bed).
"""

import math
from pathlib import Path
import cadquery as cq

# ── Racetrack base dimensions (tube OD, inches → mm) ──

TANK_OD_SEMI_R = 2.000 * 25.4     # 50.8 mm — tube outer semicircle radius
TANK_FLAT_LEN  = 1.600 * 25.4     # 40.64 mm — flat length (constant all layers)

# ── Layer offsets (same as circular version) ──

INSULATION_GAP = 6.0               # foam insulation around tank
CLEARANCE      = 1.0               # assembly clearance
INNER_FOAM_GAP = 6.35              # 1/4-inch foam inside shell
WALL           = 1.0               # printed wall thickness
FLOOR          = 1.0
FLOOR_FOAM_GAP = 25.4              # 1-inch foam at the bottom

# ── Racetrack semicircle radii for each concentric layer ──
# FLAT stays constant; only semi_r grows with each offset.

FLAT = TANK_FLAT_LEN                                               # 40.64

COLD_CORE_SR      = TANK_OD_SEMI_R + INSULATION_GAP + CLEARANCE   # 57.8
SHELL_SR          = COLD_CORE_SR + INNER_FOAM_GAP                  # 64.15
SHELL_OR_SR       = SHELL_SR + WALL                                # 65.15

CRADLE_DEPTH      = 25.0
CRADLE_ARC_DEG    = 90.7
HALF_CRADLE       = CRADLE_ARC_DEG / 2

OUTER_SHELL_IR_SR = SHELL_OR_SR + CRADLE_DEPTH                    # 90.15
OUTER_SHELL_OR_SR = OUTER_SHELL_IR_SR + WALL                      # 91.15

TANK_HEIGHT  = 152.4
SHELL_HEIGHT = TANK_HEIGHT + 10.0 + 3 * 25.4                      # 238.6

# ── Derived Z levels ──

PLAT_BOTTOM       = FLOOR + FLOOR_FOAM_GAP                        # 26.4
PLATFORM_Z        = PLAT_BOTTOM + FLOOR                            # 27.4
CHANNEL_DEPTH     = 3.0
CHANNEL_CLEARANCE = 0.5

Z_BOT         = PLAT_BOTTOM - CHANNEL_DEPTH                       # 23.4
Z_SPLIT       = PLAT_BOTTOM                                        # 26.4
CHAMFER_H     = WALL + CHANNEL_CLEARANCE                           # 1.5
Z_CHAMFER_TOP = PLAT_BOTTOM + CHAMFER_H                           # 27.9

# ── Channel ring semi_r values ──

R_INNER_OR_SR  = OUTER_SHELL_IR_SR - CHANNEL_CLEARANCE            # 89.65
R_INNER_IR_SR  = R_INNER_OR_SR - WALL                              # 88.65
R_OUTER_IR_SR  = OUTER_SHELL_OR_SR + CHANNEL_CLEARANCE            # 91.65
R_OUTER_OR_SR  = R_OUTER_IR_SR + WALL                              # 92.65

IC_INNER_OR_SR = SHELL_SR - CHANNEL_CLEARANCE                     # 63.65
IC_INNER_IR_SR = IC_INNER_OR_SR - WALL                             # 62.65
IC_OUTER_IR_SR = SHELL_OR_SR + CHANNEL_CLEARANCE                  # 65.65
IC_OUTER_OR_SR = IC_OUTER_IR_SR + WALL                             # 66.65

# ── Sweep profile dimensions ──

OVERLAP       = 1.0
IC_OL_TOP     = Z_CHAMFER_TOP + 5
RC_GAP_HALF   = WALL / 2 + CHANNEL_CLEARANCE                      # 1.0
RC_RIDGE_HALF = RC_GAP_HALF + WALL                                 # 2.0
RC_PEAK_Z     = Z_SPLIT + RC_GAP_HALF                             # 27.4

R_PATH_INNER_SR = (SHELL_SR + SHELL_OR_SR) / 2                    # 64.65
R_PATH_OUTER_SR = (R_INNER_OR_SR + R_OUTER_IR_SR) / 2             # 90.65

HALF_FLAT     = FLAT / 2                                            # 20.32
FOAM_HOLE_DIA = 8.0
DIAMOND_SIZE  = 10.0


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def rt_solid(semi_r, z_bot, z_top):
    """Solid racetrack (stadium) prism.  Long axis along X."""
    return (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, z_bot))
        .slot2D(FLAT + 2 * semi_r, 2 * semi_r)
        .extrude(z_top - z_bot)
    )


def rt_shell(inner_sr, outer_sr, z_bot, z_top):
    """Hollow racetrack shell (outer minus inner)."""
    outer = rt_solid(outer_sr, z_bot, z_top)
    inner = rt_solid(inner_sr, z_bot - 0.1, z_top + 0.1)
    return outer.cut(inner)


def sc_pt(sc_x, sr, angle_rad):
    """Point on a semicircle centered at (sc_x, 0) at given angle."""
    return (sc_x + sr * math.cos(angle_rad),
            sr * math.sin(angle_rad))


# Pocket definitions: (center_angle_deg, semicircle_center_x)
POCKETS = [(0.0, HALF_FLAT), (180.0, -HALF_FLAT)]


# ═══════════════════════════════════════════════════════
# BOTTOM CUP
# ═══════════════════════════════════════════════════════
#
# Racetrack cup: solid floor from Z=0 to FLOOR, walls up to PLAT_BOTTOM.
# Foam cavity between FLOOR and PLAT_BOTTOM inside the walls.

bottom_cup = rt_solid(OUTER_SHELL_OR_SR, 0, PLAT_BOTTOM)
inner_void = rt_solid(OUTER_SHELL_IR_SR, FLOOR, PLAT_BOTTOM + 1)
bottom_cup = bottom_cup.cut(inner_void)

# ── Diamond foam-cavity holes (at 90° and 270° — on the flat portions) ──

FOAM_MID_Z = FLOOR + FLOOR_FOAM_GAP / 2

for angle_deg in [90, 270]:
    diamond = (
        cq.Workplane("YZ")
        .transformed(offset=(0, 0, OUTER_SHELL_IR_SR - 2))
        .moveTo(0, FOAM_MID_Z - DIAMOND_SIZE / 2)
        .lineTo(DIAMOND_SIZE / 2, FOAM_MID_Z)
        .lineTo(0, FOAM_MID_Z + DIAMOND_SIZE / 2)
        .lineTo(-DIAMOND_SIZE / 2, FOAM_MID_Z)
        .close()
        .extrude(WALL + 4)
    )
    diamond = diamond.rotate((0, 0, 0), (0, 0, 1), angle_deg)
    bottom_cup = bottom_cup.cut(diamond)

# ── Internal bag-pocket walls ──

BC_WALL_BOTTOM       = FLOOR / 2
BC_WALL_RADIAL_INNER = SHELL_SR
BC_WALL_RADIAL_OUTER = OUTER_SHELL_IR_SR + OVERLAP

for pocket_deg, sc_x in POCKETS:
    # Radial divider walls at ±HALF_CRADLE from each semicircle center
    for local_angle in [HALF_CRADLE, -HALF_CRADLE]:
        angle = pocket_deg + local_angle
        bc_div = (
            cq.Workplane("XZ")
            .moveTo(BC_WALL_RADIAL_INNER, BC_WALL_BOTTOM)
            .lineTo(BC_WALL_RADIAL_INNER, PLAT_BOTTOM)
            .lineTo(BC_WALL_RADIAL_OUTER, PLAT_BOTTOM)
            .lineTo(BC_WALL_RADIAL_OUTER, BC_WALL_BOTTOM)
            .close()
            .extrude(WALL / 2, both=True)
        )
        bc_div = bc_div.rotate((0, 0, 0), (0, 0, 1), angle)
        bc_div = bc_div.translate((sc_x, 0, 0))
        bottom_cup = bottom_cup.union(bc_div, tol=0.05)

    # Arc wall at inner shell radius spanning the cradle arc
    bc_arc = (
        cq.Workplane("XZ")
        .moveTo(SHELL_SR, BC_WALL_BOTTOM)
        .lineTo(SHELL_SR, PLAT_BOTTOM)
        .lineTo(SHELL_OR_SR, PLAT_BOTTOM)
        .lineTo(SHELL_OR_SR, BC_WALL_BOTTOM)
        .close()
        .revolve(CRADLE_ARC_DEG, (0, 0, 0), (0, 1, 0))
    )
    bc_arc = bc_arc.rotate((0, 0, 0), (0, 0, 1), pocket_deg - HALF_CRADLE)
    bc_arc = bc_arc.translate((sc_x, 0, 0))
    bottom_cup = bottom_cup.union(bc_arc, tol=0.05)

bc_solids = bottom_cup.solids().vals()
print(f"Bottom cup: {len(bc_solids)} solid(s)")
for i, s in enumerate(bc_solids):
    bb = s.BoundingBox()
    print(f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
          f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Part A: Inner body (floor + inner wall)
# ═══════════════════════════════════════════════════════
#
# Floor: solid racetrack from Z_BOT to Z_BOT+FLOOR at R_INNER_IR_SR
# Inner wall: racetrack shell at SHELL_SR / SHELL_OR_SR from Z_BOT to top

inner_body_floor = rt_solid(R_INNER_IR_SR, Z_BOT, Z_BOT + FLOOR)
inner_body_wall  = rt_shell(SHELL_SR, SHELL_OR_SR, Z_BOT, SHELL_HEIGHT)
inner_body = inner_body_floor.union(inner_body_wall, tol=0.1)

ib_solids = inner_body.solids().vals()
print(f"\nInner body: {len(ib_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Part B: Outer wall
# ═══════════════════════════════════════════════════════

outer_wall = rt_shell(OUTER_SHELL_IR_SR, OUTER_SHELL_OR_SR,
                       Z_CHAMFER_TOP, SHELL_HEIGHT)

ow_solids = outer_wall.solids().vals()
print(f"Outer wall: {len(ow_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Union (inner body + outer wall)
# ═══════════════════════════════════════════════════════

upper_shell = inner_body.union(outer_wall, tol=0.1)
us_solids = upper_shell.solids().vals()
print(f"\nAfter inner_body + outer_wall: {len(us_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Pocket channels (closed-loop sweep)
# ═══════════════════════════════════════════════════════
#
# Each pocket channel is a closed loop: outer arc → radial → inner arc → radial.
# On the racetrack, pockets live entirely on the semicircular ends.
# Path points are offset from the semicircle center (sc_x, 0).

for pocket_deg, sc_x in POCKETS:
    a_lo  = math.radians(pocket_deg - HALF_CRADLE)
    a_hi  = math.radians(pocket_deg + HALF_CRADLE)
    a_mid = math.radians(pocket_deg)

    RO = R_PATH_OUTER_SR
    RI = R_PATH_INNER_SR

    pA = sc_pt(sc_x, RO, a_hi)
    pB = sc_pt(sc_x, RO, a_mid)
    pC = sc_pt(sc_x, RO, a_lo)
    pD = sc_pt(sc_x, RI, a_lo)
    pE = sc_pt(sc_x, RI, a_mid)
    pF = sc_pt(sc_x, RI, a_hi)

    path_wire = (
        cq.Workplane("XY")
        .moveTo(*pA)
        .threePointArc(pB, pC)
        .lineTo(*pD)
        .threePointArc(pE, pF)
        .lineTo(*pA)
        .wire().val()
    )

    profile_plane = cq.Plane(
        origin=(pA[0], pA[1], 0),
        xDir=(math.cos(a_hi), math.sin(a_hi), 0),
        normal=(math.sin(a_hi), -math.cos(a_hi), 0),
    )

    swept_body = (
        cq.Workplane(profile_plane)
        .moveTo(-RC_RIDGE_HALF, Z_BOT)
        .lineTo(-RC_RIDGE_HALF, Z_SPLIT)
        .lineTo(-WALL / 2, Z_CHAMFER_TOP)
        .lineTo(-WALL / 2, IC_OL_TOP)
        .lineTo(WALL / 2, IC_OL_TOP)
        .lineTo(WALL / 2, Z_CHAMFER_TOP)
        .lineTo(RC_RIDGE_HALF, Z_SPLIT)
        .lineTo(RC_RIDGE_HALF, Z_BOT)
        .close()
        .sweep(path_wire, transition='right')
    )
    upper_shell = upper_shell.union(swept_body, tol=0.1)


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Gap arc sweeps (composite racetrack paths)
# ═══════════════════════════════════════════════════════
#
# Gap arcs span from one semicircle across a flat section to the other.
# Each path is: semicircle arc + straight line + semicircle arc.
#
# Gap 1: right SC (+HC) → top flat → left SC (180-HC)
# Gap 2: left SC (180+HC) → bottom flat → right SC (360-HC)

GAP_ARC_DEFS = [
    # (start_sc_x, start_deg, junction_deg, end_sc_x, end_deg)
    ( HALF_FLAT,  HALF_CRADLE,       90,  -HALF_FLAT, 180 - HALF_CRADLE),
    (-HALF_FLAT,  180 + HALF_CRADLE, 270,  HALF_FLAT, 360 - HALF_CRADLE),
]

for start_sc_x, start_deg, junc_deg, end_sc_x, end_deg in GAP_ARC_DEFS:
    R = R_PATH_OUTER_SR

    a_start = math.radians(start_deg)
    a_junc  = math.radians(junc_deg)
    a_end   = math.radians(end_deg)

    p_start      = sc_pt(start_sc_x, R, a_start)
    p_junc_start = sc_pt(start_sc_x, R, a_junc)
    p_junc_end   = sc_pt(end_sc_x,   R, a_junc)
    p_end        = sc_pt(end_sc_x,   R, a_end)

    # Midpoints for threePointArc (average angle on each semicircle)
    a_mid1 = (a_start + a_junc) / 2
    p_mid1 = sc_pt(start_sc_x, R, a_mid1)
    a_mid2 = (a_junc + a_end) / 2
    p_mid2 = sc_pt(end_sc_x, R, a_mid2)

    gap_path = (
        cq.Workplane("XY")
        .moveTo(*p_start)
        .threePointArc(p_mid1, p_junc_start)   # start SC arc
        .lineTo(*p_junc_end)                    # flat segment
        .threePointArc(p_mid2, p_end)           # end SC arc
        .wire().val()
    )

    gap_profile_plane = cq.Plane(
        origin=(p_start[0], p_start[1], 0),
        xDir=(-math.cos(a_start), -math.sin(a_start), 0),
        normal=(-math.sin(a_start), math.cos(a_start), 0),
    )

    gap_body = (
        cq.Workplane(gap_profile_plane)
        .moveTo(-RC_RIDGE_HALF, Z_BOT)
        .lineTo(-RC_RIDGE_HALF, Z_SPLIT)
        .lineTo(-WALL / 2, Z_CHAMFER_TOP)
        .lineTo(-WALL / 2, IC_OL_TOP)
        .lineTo(WALL / 2, IC_OL_TOP)
        .lineTo(WALL / 2, Z_CHAMFER_TOP)
        .lineTo(RC_RIDGE_HALF, Z_SPLIT)
        .lineTo(RC_RIDGE_HALF, Z_BOT)
        .close()
        .sweep(gap_path)
    )
    upper_shell = upper_shell.union(gap_body, tol=0.1)

us_solids = upper_shell.solids().vals()
print(f"After + all channel bodies: {len(us_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Dividers
# ═══════════════════════════════════════════════════════

DIVIDER_FLOOR = Z_BOT + FLOOR / 2

for pocket_deg, sc_x in POCKETS:
    for local_angle in [HALF_CRADLE, -HALF_CRADLE]:
        angle = pocket_deg + local_angle
        div = (
            cq.Workplane("XZ")
            .moveTo(SHELL_OR_SR - OVERLAP, Z_CHAMFER_TOP)
            .lineTo(SHELL_OR_SR - 0.1, SHELL_HEIGHT)
            .lineTo(OUTER_SHELL_IR_SR + OVERLAP, SHELL_HEIGHT)
            .lineTo(OUTER_SHELL_IR_SR + OVERLAP, Z_CHAMFER_TOP)
            .lineTo(R_INNER_IR_SR, Z_SPLIT)
            .lineTo(R_INNER_IR_SR, DIVIDER_FLOOR)
            .lineTo(IC_OUTER_OR_SR, DIVIDER_FLOOR)
            .lineTo(IC_OUTER_OR_SR, Z_SPLIT)
            .lineTo(SHELL_OR_SR - OVERLAP, Z_CHAMFER_TOP)
            .close()
            .extrude(WALL / 2, both=True)
        )
        div = div.rotate((0, 0, 0), (0, 0, 1), angle)
        div = div.translate((sc_x, 0, 0))
        upper_shell = upper_shell.union(div, tol=0.1)

us_solids = upper_shell.solids().vals()
print(f"After + dividers: {len(us_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Groove cuts
# ═══════════════════════════════════════════════════════

# ── Pocket groove cuts (closed-loop, same paths as pocket bodies) ──

for pocket_deg, sc_x in POCKETS:
    a_lo  = math.radians(pocket_deg - HALF_CRADLE)
    a_hi  = math.radians(pocket_deg + HALF_CRADLE)
    a_mid = math.radians(pocket_deg)

    RO = R_PATH_OUTER_SR
    RI = R_PATH_INNER_SR

    pA = sc_pt(sc_x, RO, a_hi)
    pB = sc_pt(sc_x, RO, a_mid)
    pC = sc_pt(sc_x, RO, a_lo)
    pD = sc_pt(sc_x, RI, a_lo)
    pE = sc_pt(sc_x, RI, a_mid)
    pF = sc_pt(sc_x, RI, a_hi)

    path_wire = (
        cq.Workplane("XY")
        .moveTo(*pA)
        .threePointArc(pB, pC)
        .lineTo(*pD)
        .threePointArc(pE, pF)
        .lineTo(*pA)
        .wire().val()
    )

    profile_plane = cq.Plane(
        origin=(pA[0], pA[1], 0),
        xDir=(math.cos(a_hi), math.sin(a_hi), 0),
        normal=(math.sin(a_hi), -math.cos(a_hi), 0),
    )

    swept_groove = (
        cq.Workplane(profile_plane)
        .moveTo(-RC_GAP_HALF, Z_BOT - 0.1)
        .lineTo(-RC_GAP_HALF, Z_SPLIT)
        .lineTo(0, RC_PEAK_Z)
        .lineTo(RC_GAP_HALF, Z_SPLIT)
        .lineTo(RC_GAP_HALF, Z_BOT - 0.1)
        .close()
        .sweep(path_wire, transition='right')
    )
    upper_shell = upper_shell.cut(swept_groove)

# ── Gap arc groove cuts (composite paths, same as gap bodies) ──

for start_sc_x, start_deg, junc_deg, end_sc_x, end_deg in GAP_ARC_DEFS:
    R = R_PATH_OUTER_SR

    a_start = math.radians(start_deg)
    a_junc  = math.radians(junc_deg)
    a_end   = math.radians(end_deg)

    p_start      = sc_pt(start_sc_x, R, a_start)
    p_junc_start = sc_pt(start_sc_x, R, a_junc)
    p_junc_end   = sc_pt(end_sc_x,   R, a_junc)
    p_end        = sc_pt(end_sc_x,   R, a_end)

    a_mid1 = (a_start + a_junc) / 2
    p_mid1 = sc_pt(start_sc_x, R, a_mid1)
    a_mid2 = (a_junc + a_end) / 2
    p_mid2 = sc_pt(end_sc_x, R, a_mid2)

    gap_path = (
        cq.Workplane("XY")
        .moveTo(*p_start)
        .threePointArc(p_mid1, p_junc_start)
        .lineTo(*p_junc_end)
        .threePointArc(p_mid2, p_end)
        .wire().val()
    )

    gap_groove_plane = cq.Plane(
        origin=(p_start[0], p_start[1], 0),
        xDir=(-math.cos(a_start), -math.sin(a_start), 0),
        normal=(-math.sin(a_start), math.cos(a_start), 0),
    )

    gap_groove = (
        cq.Workplane(gap_groove_plane)
        .moveTo(-RC_GAP_HALF, Z_BOT - 0.1)
        .lineTo(-RC_GAP_HALF, Z_SPLIT)
        .lineTo(0, RC_PEAK_Z)
        .lineTo(RC_GAP_HALF, Z_SPLIT)
        .lineTo(RC_GAP_HALF, Z_BOT - 0.1)
        .close()
        .sweep(gap_path)
    )
    upper_shell = upper_shell.cut(gap_groove)

us_solids = upper_shell.solids().vals()
print(f"After + swept groove cuts: {len(us_solids)} solid(s)")


# ── Center floor hole ──

center_hole = (
    cq.Workplane("XY")
    .transformed(offset=(0, 0, Z_BOT - 1))
    .circle(FOAM_HOLE_DIA / 2)
    .extrude(FLOOR + 2)
)
upper_shell = upper_shell.cut(center_hole)

# ── Cradle floor cuts ──

DIVIDER_ANGULAR_CLEARANCE = math.degrees((WALL / 2 + 0.2) / SHELL_OR_SR)
CUT_ARC = CRADLE_ARC_DEG - 2 * DIVIDER_ANGULAR_CLEARANCE

for pocket_deg, sc_x in POCKETS:
    cradle_cut = (
        cq.Workplane("XZ")
        .moveTo(SHELL_OR_SR, Z_BOT - 0.1)
        .lineTo(SHELL_OR_SR, Z_BOT + FLOOR + 0.1)
        .lineTo(OUTER_SHELL_IR_SR, Z_BOT + FLOOR + 0.1)
        .lineTo(OUTER_SHELL_IR_SR, Z_BOT - 0.1)
        .close()
        .revolve(CUT_ARC, (0, 0, 0), (0, 1, 0))
    )
    cradle_cut = cradle_cut.rotate(
        (0, 0, 0), (0, 0, 1), pocket_deg - CUT_ARC / 2
    )
    cradle_cut = cradle_cut.translate((sc_x, 0, 0))
    upper_shell = upper_shell.cut(cradle_cut)

us_solids = upper_shell.solids().vals()
print(f"After cradle floor cuts: {len(us_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# DIAGNOSTICS
# ═══════════════════════════════════════════════════════

for name, part in [("Bottom cup", bottom_cup), ("Upper shell", upper_shell)]:
    solids = part.solids().vals()
    print(f"\n{name}: {len(solids)} solid(s)")
    for i, s in enumerate(solids):
        bb = s.BoundingBox()
        print(f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
              f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")

print(f"\nRacetrack: flat_len={FLAT:.2f} mm")
print(f"  Semi_r layers:")
print(f"    Inner wall:  {SHELL_SR:.2f} / {SHELL_OR_SR:.2f}")
print(f"    Path inner:  {R_PATH_INNER_SR:.2f}")
print(f"    Path outer:  {R_PATH_OUTER_SR:.2f}")
print(f"    Inner ring:  {R_INNER_IR_SR:.2f} / {R_INNER_OR_SR:.2f}")
print(f"    Gap:         {R_INNER_OR_SR:.2f} - {R_OUTER_IR_SR:.2f}  "
      f"({R_OUTER_IR_SR - R_INNER_OR_SR:.1f} mm)")
print(f"    Outer ring:  {R_OUTER_IR_SR:.2f} / {R_OUTER_OR_SR:.2f}")
print(f"    Outer wall:  {OUTER_SHELL_IR_SR:.2f} / {OUTER_SHELL_OR_SR:.2f}")
print(f"  Overall envelope: "
      f"{FLAT + 2 * OUTER_SHELL_OR_SR:.1f} x {2 * OUTER_SHELL_OR_SR:.1f} mm")


# ═══════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

bottom_path = out_dir / "foam-bag-shell-bottom.step"
cq.exporters.export(bottom_cup, str(bottom_path))
print(f"\nExported: {bottom_path}")

upper_path = out_dir / "foam-bag-shell-upper.step"
cq.exporters.export(upper_shell, str(upper_path))
print(f"Exported: {upper_path}")
