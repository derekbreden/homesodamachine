"""
Foam-bag shell: racetrack variant.

Two-piece clamshell (bottom cup + upper shell) whose cross-section is a
stadium (racetrack) matching the pressed carbonator tube shape.

Racetrack geometry:
  Two semicircles of radius R connected by two flat sides of length FLAT.
  Long axis along X.  All concentric layers share the same flat length;
  only the semicircle radius grows with each offset layer.

Bottom cup:  Z=0 to PLAT_BOTTOM.  Prints right-side up (floor on bed).
Upper shell: Z=Z_BOT to SHELL_HEIGHT.  Prints right-side up.

Stacking channels run around the perimeter at the split line.  Each
channel is a closed-loop sweep (outer arc, radial wall, inner arc,
radial wall) whose cross-section has a wide ridge at the base and a
narrow wall above.  A V-shaped groove is cut along the same path to
create the mating slot for the bottom cup's ridge.
"""

import math
from pathlib import Path
import cadquery as cq


# ═══════════════════════════════════════════════════════
# PHYSICAL DIMENSIONS
# ═══════════════════════════════════════════════════════

TANK_OD_SEMI_R = 2.000 * 25.4       # 50.8 mm — tube outer semicircle radius
TANK_FLAT_LEN  = 1.600 * 25.4       # 40.64 mm — flat length between semicircles

INSULATION_GAP = 6.0                 # foam insulation around tank
CLEARANCE      = 1.0                 # assembly clearance
INNER_FOAM_GAP = 6.35               # 1/4-inch foam inside shell
WALL           = 1.0                 # printed wall thickness
FLOOR          = 1.0
FLOOR_FOAM_GAP = 25.4               # 1-inch foam at the bottom

CRADLE_DEPTH   = 25.0               # radial depth of bag cradle zone
CRADLE_ARC_DEG = 109.4               # angular span of each bag cradle
HALF_CRADLE    = CRADLE_ARC_DEG / 2

OUTER_FOAM_GAP = 6.35               # 1/4-inch foam outside bags

TANK_HEIGHT    = 152.4
SHELL_HEIGHT   = TANK_HEIGHT + 10.0 + 3 * 25.4   # 238.6

FOAM_HOLE_DIA  = 8.0
DIAMOND_SIZE   = 10.0
OVERLAP        = 1.0                 # boolean overlap for reliable unions


# ═══════════════════════════════════════════════════════
# RACETRACK LAYER RADII (semicircle radii; flat length is constant)
# ═══════════════════════════════════════════════════════

FLAT     = TANK_FLAT_LEN                                             # 40.64
HALF_FLAT = FLAT / 2                                                 # 20.32

COLD_CORE_SR      = TANK_OD_SEMI_R + INSULATION_GAP + CLEARANCE     # 57.8
SHELL_SR          = COLD_CORE_SR + INNER_FOAM_GAP                   # 64.15
SHELL_OR_SR       = SHELL_SR + WALL                                  # 65.15

OUTER_SHELL_IR_SR = SHELL_OR_SR + CRADLE_DEPTH                      # 90.15
OUTER_SHELL_OR_SR = OUTER_SHELL_IR_SR + WALL                        # 91.15

OUTERMOST_IR_SR   = OUTER_SHELL_OR_SR + OUTER_FOAM_GAP              # 97.50
OUTERMOST_OR_SR   = OUTERMOST_IR_SR + WALL                          # 98.50


# ═══════════════════════════════════════════════════════
# Z LEVELS
# ═══════════════════════════════════════════════════════

PLAT_BOTTOM       = FLOOR + FLOOR_FOAM_GAP                          # 26.4
PLATFORM_Z        = PLAT_BOTTOM + FLOOR                             # 27.4
CHANNEL_DEPTH     = 3.0
CHANNEL_CLEARANCE = 0.5

Z_BOT         = PLAT_BOTTOM - CHANNEL_DEPTH                         # 23.4
Z_SPLIT       = PLAT_BOTTOM                                          # 26.4
CHAMFER_H     = WALL + CHANNEL_CLEARANCE                             # 1.5
Z_CHAMFER_TOP = PLAT_BOTTOM + CHAMFER_H                             # 27.9


# ═══════════════════════════════════════════════════════
# CHANNEL DIMENSIONS
# ═══════════════════════════════════════════════════════

# Channel rings straddle each wall with clearance gaps.
# "Inner channel" straddles the inner shell wall (SHELL_SR / SHELL_OR_SR).
# "Outer channel" straddles the outer shell wall (OUTER_SHELL_IR_SR / OUTER_SHELL_OR_SR).
# "Outermost channel" straddles the outermost wall (OUTERMOST_IR_SR / OUTERMOST_OR_SR).

INNER_CHANNEL_INNER_OR_SR = SHELL_SR - CHANNEL_CLEARANCE            # 63.65
INNER_CHANNEL_INNER_IR_SR = INNER_CHANNEL_INNER_OR_SR - WALL        # 62.65
INNER_CHANNEL_OUTER_IR_SR = SHELL_OR_SR + CHANNEL_CLEARANCE         # 65.65
INNER_CHANNEL_OUTER_OR_SR = INNER_CHANNEL_OUTER_IR_SR + WALL        # 66.65

OUTER_CHANNEL_INNER_OR_SR = OUTER_SHELL_IR_SR - CHANNEL_CLEARANCE   # 89.65
OUTER_CHANNEL_INNER_IR_SR = OUTER_CHANNEL_INNER_OR_SR - WALL        # 88.65
OUTER_CHANNEL_OUTER_IR_SR = OUTER_SHELL_OR_SR + CHANNEL_CLEARANCE   # 91.65
OUTER_CHANNEL_OUTER_OR_SR = OUTER_CHANNEL_OUTER_IR_SR + WALL        # 92.65

OUTERMOST_CHANNEL_INNER_OR_SR = OUTERMOST_IR_SR - CHANNEL_CLEARANCE # 97.00
OUTERMOST_CHANNEL_INNER_IR_SR = OUTERMOST_CHANNEL_INNER_OR_SR - WALL # 96.00
OUTERMOST_CHANNEL_OUTER_IR_SR = OUTERMOST_OR_SR + CHANNEL_CLEARANCE # 99.00
OUTERMOST_CHANNEL_OUTER_OR_SR = OUTERMOST_CHANNEL_OUTER_IR_SR + WALL # 100.00

# Sweep path centerlines (midpoint of each channel's clearance gap)
INNER_CHANNEL_PATH_SR    = (SHELL_SR + SHELL_OR_SR) / 2             # 64.65
OUTER_CHANNEL_PATH_SR    = (OUTER_CHANNEL_INNER_OR_SR
                            + OUTER_CHANNEL_OUTER_IR_SR) / 2        # 90.65
OUTERMOST_CHANNEL_PATH_SR = (OUTERMOST_CHANNEL_INNER_OR_SR
                             + OUTERMOST_CHANNEL_OUTER_IR_SR) / 2   # 98.00

# Sweep profile widths
CHANNEL_GROOVE_HALF_WIDTH = WALL / 2 + CHANNEL_CLEARANCE            # 1.0
CHANNEL_RIDGE_HALF_WIDTH  = CHANNEL_GROOVE_HALF_WIDTH + WALL         # 2.0
CHANNEL_GROOVE_PEAK_Z     = Z_SPLIT + CHANNEL_GROOVE_HALF_WIDTH     # 27.4
CHANNEL_WALL_OVERLAP_TOP  = Z_CHAMFER_TOP + 5                       # 32.9


# ═══════════════════════════════════════════════════════
# POCKET LAYOUT
# ═══════════════════════════════════════════════════════

# Each pocket sits on a semicircular end of the racetrack.
# (center_angle_deg, semicircle_center_x)
POCKETS = [(0.0, HALF_FLAT), (180.0, -HALF_FLAT)]

# Gap arcs connect pockets across the flat sides.
# (start_sc_x, start_deg, junction_deg, end_sc_x, end_deg)
GAP_ARC_DEFS = [
    ( HALF_FLAT,  HALF_CRADLE,       90,  -HALF_FLAT, 180 - HALF_CRADLE),
    (-HALF_FLAT,  180 + HALF_CRADLE, 270,   HALF_FLAT, 360 - HALF_CRADLE),
]


# ═══════════════════════════════════════════════════════
# RACETRACK GEOMETRY HELPERS
# ═══════════════════════════════════════════════════════

def racetrack_solid(semi_r, z_bot, z_top):
    """Solid racetrack (stadium) prism.  Long axis along X."""
    return (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, z_bot))
        .slot2D(FLAT + 2 * semi_r, 2 * semi_r)
        .extrude(z_top - z_bot)
    )


def racetrack_shell(inner_sr, outer_sr, z_bot, z_top):
    """Hollow racetrack shell (outer minus inner)."""
    outer = racetrack_solid(outer_sr, z_bot, z_top)
    inner = racetrack_solid(inner_sr, z_bot - 0.1, z_top + 0.1)
    return outer.cut(inner)


def semicircle_point(semicircle_center_x, radius, angle_rad):
    """Point on a semicircle centered at (semicircle_center_x, 0)."""
    return (semicircle_center_x + radius * math.cos(angle_rad),
            radius * math.sin(angle_rad))


# ═══════════════════════════════════════════════════════
# CHANNEL PATH BUILDERS
# ═══════════════════════════════════════════════════════
#
# Each channel type has its own path shape but all share the same
# cross-section profile.  Path builders return (wire, profile_plane)
# so the caller can sweep either a ridge body or a groove cut.

def build_pocket_channel_path(pocket_deg, semicircle_center_x):
    """Closed-loop path for a pocket channel.

    The path traces: outer arc along the outer channel ring,
    radial wall inward along one divider, inner arc along the
    inner channel ring, radial wall outward along the other divider.

    CadQuery miters the four corners via transition='right'.
    """
    clockwise_divider_angle = math.radians(pocket_deg - HALF_CRADLE)
    countercw_divider_angle = math.radians(pocket_deg + HALF_CRADLE)
    pocket_center_angle     = math.radians(pocket_deg)

    sc_x = semicircle_center_x
    outer_ring_at_countercw_divider = semicircle_point(sc_x, OUTER_CHANNEL_PATH_SR, countercw_divider_angle)
    outer_ring_arc_midpoint         = semicircle_point(sc_x, OUTER_CHANNEL_PATH_SR, pocket_center_angle)
    outer_ring_at_clockwise_divider = semicircle_point(sc_x, OUTER_CHANNEL_PATH_SR, clockwise_divider_angle)
    inner_ring_at_clockwise_divider = semicircle_point(sc_x, INNER_CHANNEL_PATH_SR, clockwise_divider_angle)
    inner_ring_arc_midpoint         = semicircle_point(sc_x, INNER_CHANNEL_PATH_SR, pocket_center_angle)
    inner_ring_at_countercw_divider = semicircle_point(sc_x, INNER_CHANNEL_PATH_SR, countercw_divider_angle)

    wire = (
        cq.Workplane("XY")
        .moveTo(*outer_ring_at_countercw_divider)
        .threePointArc(outer_ring_arc_midpoint, outer_ring_at_clockwise_divider)
        .lineTo(*inner_ring_at_clockwise_divider)
        .threePointArc(inner_ring_arc_midpoint, inner_ring_at_countercw_divider)
        .lineTo(*outer_ring_at_countercw_divider)
        .wire().val()
    )

    profile_plane = cq.Plane(
        origin=(outer_ring_at_countercw_divider[0], outer_ring_at_countercw_divider[1], 0),
        xDir=(math.cos(countercw_divider_angle), math.sin(countercw_divider_angle), 0),
        normal=(math.sin(countercw_divider_angle), -math.cos(countercw_divider_angle), 0),
    )

    return wire, profile_plane


def build_gap_channel_path(start_sc_x, start_deg, junction_deg, end_sc_x, end_deg):
    """Open path for a gap channel spanning two semicircles across a flat.

    The path goes: arc along the start semicircle, straight across the
    flat section, arc along the end semicircle.
    """
    start_angle    = math.radians(start_deg)
    junction_angle = math.radians(junction_deg)
    end_angle      = math.radians(end_deg)

    start_divider          = semicircle_point(start_sc_x, OUTER_CHANNEL_PATH_SR, start_angle)
    start_semicircle_junction = semicircle_point(start_sc_x, OUTER_CHANNEL_PATH_SR, junction_angle)
    end_semicircle_junction   = semicircle_point(end_sc_x,   OUTER_CHANNEL_PATH_SR, junction_angle)
    end_divider            = semicircle_point(end_sc_x,   OUTER_CHANNEL_PATH_SR, end_angle)

    start_arc_midpoint_angle = (start_angle + junction_angle) / 2
    start_arc_midpoint = semicircle_point(start_sc_x, OUTER_CHANNEL_PATH_SR, start_arc_midpoint_angle)
    end_arc_midpoint_angle = (junction_angle + end_angle) / 2
    end_arc_midpoint = semicircle_point(end_sc_x, OUTER_CHANNEL_PATH_SR, end_arc_midpoint_angle)

    wire = (
        cq.Workplane("XY")
        .moveTo(*start_divider)
        .threePointArc(start_arc_midpoint, start_semicircle_junction)
        .lineTo(*end_semicircle_junction)
        .threePointArc(end_arc_midpoint, end_divider)
        .wire().val()
    )

    profile_plane = cq.Plane(
        origin=(start_divider[0], start_divider[1], 0),
        xDir=(-math.cos(start_angle), -math.sin(start_angle), 0),
        normal=(-math.sin(start_angle), math.cos(start_angle), 0),
    )

    return wire, profile_plane


def build_outermost_channel_path():
    """Full racetrack loop for the outermost channel.

    Unlike pocket/gap channels which are split by dividers, the outermost
    channel is one continuous loop around the entire perimeter.
    """
    R = OUTERMOST_CHANNEL_PATH_SR

    wire = (
        cq.Workplane("XY")
        .moveTo(HALF_FLAT, -R)
        .threePointArc((HALF_FLAT + R, 0), (HALF_FLAT, R))
        .lineTo(-HALF_FLAT, R)
        .threePointArc((-HALF_FLAT - R, 0), (-HALF_FLAT, -R))
        .close()
        .wire().val()
    )

    profile_plane = cq.Plane(
        origin=(HALF_FLAT, -R, 0),
        xDir=(0, 1, 0),
        normal=(1, 0, 0),
    )

    return wire, profile_plane


# ═══════════════════════════════════════════════════════
# CHANNEL SWEEP HELPERS
# ═══════════════════════════════════════════════════════
#
# All channels share two cross-section profiles:
#   - Ridge body: wide base (CHANNEL_RIDGE_HALF_WIDTH) with chamfered
#     shoulders and a narrow wall that overlaps into adjacent walls.
#   - Groove cut: V-shaped notch (CHANNEL_GROOVE_HALF_WIDTH) that creates
#     the mating slot for the bottom cup.

def sweep_channel_ridge(path_wire, profile_plane, closed_loop=False):
    """Sweep the ridge profile along a path to add channel material."""
    swept = (
        cq.Workplane(profile_plane)
        .moveTo(-CHANNEL_RIDGE_HALF_WIDTH, Z_BOT)
        .lineTo(-CHANNEL_RIDGE_HALF_WIDTH, Z_SPLIT)
        .lineTo(-WALL / 2, Z_CHAMFER_TOP)
        .lineTo(-WALL / 2, CHANNEL_WALL_OVERLAP_TOP)
        .lineTo(WALL / 2, CHANNEL_WALL_OVERLAP_TOP)
        .lineTo(WALL / 2, Z_CHAMFER_TOP)
        .lineTo(CHANNEL_RIDGE_HALF_WIDTH, Z_SPLIT)
        .lineTo(CHANNEL_RIDGE_HALF_WIDTH, Z_BOT)
        .close()
    )
    if closed_loop:
        return swept.sweep(path_wire, transition='right')
    return swept.sweep(path_wire)


def sweep_channel_groove(path_wire, profile_plane, closed_loop=False):
    """Sweep the groove profile along a path to cut the stacking slot."""
    swept = (
        cq.Workplane(profile_plane)
        .moveTo(-CHANNEL_GROOVE_HALF_WIDTH, Z_BOT - 0.1)
        .lineTo(-CHANNEL_GROOVE_HALF_WIDTH, Z_SPLIT)
        .lineTo(0, CHANNEL_GROOVE_PEAK_Z)
        .lineTo(CHANNEL_GROOVE_HALF_WIDTH, Z_SPLIT)
        .lineTo(CHANNEL_GROOVE_HALF_WIDTH, Z_BOT - 0.1)
        .close()
    )
    if closed_loop:
        return swept.sweep(path_wire, transition='right')
    return swept.sweep(path_wire)


# ═══════════════════════════════════════════════════════
# BOTTOM CUP
# ═══════════════════════════════════════════════════════

def build_bottom_cup():
    cup = racetrack_solid(OUTERMOST_OR_SR, 0, FLOOR)
    cup = cup.union(
        racetrack_shell(OUTER_SHELL_IR_SR, OUTER_SHELL_OR_SR, FLOOR, PLAT_BOTTOM),
        tol=0.05)
    cup = cup.union(
        racetrack_shell(OUTERMOST_IR_SR, OUTERMOST_OR_SR, FLOOR, PLAT_BOTTOM),
        tol=0.05)

    cup = cut_foam_cavity_diamonds(cup)
    cup = add_bag_pocket_walls(cup)
    return cup


def cut_foam_cavity_diamonds(cup):
    """Diamond-shaped holes through walls for foam cavity airflow."""
    foam_mid_z = FLOOR + FLOOR_FOAM_GAP / 2

    for wall_inner_sr in [OUTER_SHELL_IR_SR, OUTERMOST_IR_SR]:
        for angle_deg in [90, 270]:
            diamond = (
                cq.Workplane("YZ")
                .transformed(offset=(0, 0, wall_inner_sr - 2))
                .moveTo(0, foam_mid_z - DIAMOND_SIZE / 2)
                .lineTo(DIAMOND_SIZE / 2, foam_mid_z)
                .lineTo(0, foam_mid_z + DIAMOND_SIZE / 2)
                .lineTo(-DIAMOND_SIZE / 2, foam_mid_z)
                .close()
                .extrude(WALL + 4)
            )
            diamond = diamond.rotate((0, 0, 0), (0, 0, 1), angle_deg)
            cup = cup.cut(diamond)
    return cup


def add_bag_pocket_walls(cup):
    """Radial dividers and arc walls that form bag pockets in the bottom cup."""
    pocket_wall_bottom  = FLOOR / 2
    pocket_wall_radial_inner = SHELL_SR
    pocket_wall_radial_outer = OUTER_SHELL_IR_SR + OVERLAP

    for pocket_deg, sc_x in POCKETS:
        for local_angle in [HALF_CRADLE, -HALF_CRADLE]:
            angle = pocket_deg + local_angle
            radial_wall = (
                cq.Workplane("XZ")
                .moveTo(pocket_wall_radial_inner, pocket_wall_bottom)
                .lineTo(pocket_wall_radial_inner, PLAT_BOTTOM)
                .lineTo(pocket_wall_radial_outer, PLAT_BOTTOM)
                .lineTo(pocket_wall_radial_outer, pocket_wall_bottom)
                .close()
                .extrude(WALL / 2, both=True)
            )
            radial_wall = radial_wall.rotate((0, 0, 0), (0, 0, 1), angle)
            radial_wall = radial_wall.translate((sc_x, 0, 0))
            cup = cup.union(radial_wall, tol=0.05)

        arc_wall = (
            cq.Workplane("XZ")
            .moveTo(SHELL_SR, pocket_wall_bottom)
            .lineTo(SHELL_SR, PLAT_BOTTOM)
            .lineTo(SHELL_OR_SR, PLAT_BOTTOM)
            .lineTo(SHELL_OR_SR, pocket_wall_bottom)
            .close()
            .revolve(CRADLE_ARC_DEG, (0, 0, 0), (0, 1, 0))
        )
        arc_wall = arc_wall.rotate((0, 0, 0), (0, 0, 1), pocket_deg - HALF_CRADLE)
        arc_wall = arc_wall.translate((sc_x, 0, 0))
        cup = cup.union(arc_wall, tol=0.05)

    return cup


# ═══════════════════════════════════════════════════════
# UPPER SHELL
# ═══════════════════════════════════════════════════════

def build_upper_shell():
    shell = build_shell_walls()
    shell = cut_center_floor_hole(shell)
    shell = cut_bag_cradle_floors(shell)       # before channels, so sweeps restore their own floor
    shell = add_pocket_channels(shell)
    shell = add_gap_channels(shell)
    shell = add_outermost_channel(shell)
    shell = add_pocket_dividers(shell)         # after channel bodies, before groove cuts
    shell = cut_pocket_channel_grooves(shell)  # after dividers, so grooves cut through them
    shell = cut_gap_channel_grooves(shell)
    shell = cut_outermost_channel_groove(shell)
    return shell


def build_shell_walls():
    """Inner wall, outer wall, outermost wall, and the floor connecting them."""
    floor = racetrack_solid(OUTERMOST_CHANNEL_OUTER_OR_SR, Z_BOT, Z_BOT + FLOOR)
    inner_wall = racetrack_shell(SHELL_SR, SHELL_OR_SR, Z_BOT, SHELL_HEIGHT)
    shell = floor.union(inner_wall, tol=0.1)

    outer_wall = racetrack_shell(OUTER_SHELL_IR_SR, OUTER_SHELL_OR_SR,
                                  Z_CHAMFER_TOP, SHELL_HEIGHT)
    shell = shell.union(outer_wall, tol=0.1)

    outermost_wall = racetrack_shell(OUTERMOST_IR_SR, OUTERMOST_OR_SR,
                                      Z_CHAMFER_TOP, SHELL_HEIGHT)
    shell = shell.union(outermost_wall, tol=0.1)
    return shell


def cut_center_floor_hole(shell):
    """Hole through the center of the floor for foam cavity airflow."""
    hole = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, Z_BOT - 1))
        .circle(FOAM_HOLE_DIA / 2)
        .extrude(FLOOR + 2)
    )
    return shell.cut(hole)


def cut_bag_cradle_floors(shell):
    """Remove floor under each bag cradle so bags can drop through.

    This runs before channel sweeps.  The sweeps will restore floor
    material under their own radial walls with exact geometry.
    """
    divider_angular_clearance = math.degrees((WALL / 2 + 0.2) / SHELL_OR_SR)
    cradle_cut_arc = CRADLE_ARC_DEG - 2 * divider_angular_clearance

    for pocket_deg, sc_x in POCKETS:
        cradle_cut = (
            cq.Workplane("XZ")
            .moveTo(INNER_CHANNEL_OUTER_OR_SR, Z_BOT - 0.1)
            .lineTo(INNER_CHANNEL_OUTER_OR_SR, Z_BOT + FLOOR + 0.1)
            .lineTo(OUTER_CHANNEL_INNER_IR_SR, Z_BOT + FLOOR + 0.1)
            .lineTo(OUTER_CHANNEL_INNER_IR_SR, Z_BOT - 0.1)
            .close()
            .revolve(cradle_cut_arc, (0, 0, 0), (0, 1, 0))
        )
        cradle_cut = cradle_cut.rotate(
            (0, 0, 0), (0, 0, 1), pocket_deg - cradle_cut_arc / 2)
        cradle_cut = cradle_cut.translate((sc_x, 0, 0))
        shell = shell.cut(cradle_cut)

    return shell


def add_pocket_channels(shell):
    """Sweep channel ridge bodies around each pocket's closed loop."""
    for pocket_deg, sc_x in POCKETS:
        path_wire, profile_plane = build_pocket_channel_path(pocket_deg, sc_x)
        pocket_channel = sweep_channel_ridge(path_wire, profile_plane, closed_loop=True)
        shell = shell.union(pocket_channel, tol=0.1)
    return shell


def add_gap_channels(shell):
    """Sweep channel ridge bodies along the gap arcs between pockets."""
    for gap_def in GAP_ARC_DEFS:
        path_wire, profile_plane = build_gap_channel_path(*gap_def)
        gap_channel = sweep_channel_ridge(path_wire, profile_plane)
        shell = shell.union(gap_channel, tol=0.1)
    return shell


def add_outermost_channel(shell):
    """Sweep channel ridge body around the full outermost racetrack loop."""
    path_wire, profile_plane = build_outermost_channel_path()
    outermost_channel = sweep_channel_ridge(path_wire, profile_plane, closed_loop=True)
    return shell.union(outermost_channel, tol=0.1)


def add_pocket_dividers(shell):
    """Radial walls between pockets, spanning from inner wall to outer wall."""
    divider_floor = Z_BOT + FLOOR / 2

    for pocket_deg, sc_x in POCKETS:
        for local_angle in [HALF_CRADLE, -HALF_CRADLE]:
            angle = pocket_deg + local_angle
            pocket_divider = (
                cq.Workplane("XZ")
                .moveTo(SHELL_OR_SR - OVERLAP, Z_CHAMFER_TOP)
                .lineTo(SHELL_OR_SR - 0.1, SHELL_HEIGHT)
                .lineTo(OUTER_SHELL_IR_SR + OVERLAP, SHELL_HEIGHT)
                .lineTo(OUTER_SHELL_IR_SR + OVERLAP, Z_CHAMFER_TOP)
                .lineTo(OUTER_CHANNEL_INNER_IR_SR, Z_SPLIT)
                .lineTo(OUTER_CHANNEL_INNER_IR_SR, divider_floor)
                .lineTo(INNER_CHANNEL_OUTER_OR_SR, divider_floor)
                .lineTo(INNER_CHANNEL_OUTER_OR_SR, Z_SPLIT)
                .lineTo(SHELL_OR_SR - OVERLAP, Z_CHAMFER_TOP)
                .close()
                .extrude(WALL / 2, both=True)
            )
            pocket_divider = pocket_divider.rotate((0, 0, 0), (0, 0, 1), angle)
            pocket_divider = pocket_divider.translate((sc_x, 0, 0))
            shell = shell.union(pocket_divider, tol=0.1)

    return shell


def cut_pocket_channel_grooves(shell):
    """Cut V-shaped grooves along each pocket's closed-loop channel path."""
    for pocket_deg, sc_x in POCKETS:
        path_wire, profile_plane = build_pocket_channel_path(pocket_deg, sc_x)
        pocket_groove = sweep_channel_groove(path_wire, profile_plane, closed_loop=True)
        shell = shell.cut(pocket_groove)
    return shell


def cut_gap_channel_grooves(shell):
    """Cut V-shaped grooves along each gap arc channel path."""
    for gap_def in GAP_ARC_DEFS:
        path_wire, profile_plane = build_gap_channel_path(*gap_def)
        gap_groove = sweep_channel_groove(path_wire, profile_plane)
        shell = shell.cut(gap_groove)
    return shell


def cut_outermost_channel_groove(shell):
    """Cut V-shaped groove along the full outermost racetrack channel path."""
    path_wire, profile_plane = build_outermost_channel_path()
    outermost_groove = sweep_channel_groove(path_wire, profile_plane, closed_loop=True)
    return shell.cut(outermost_groove)


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

bottom_cup = build_bottom_cup()
upper_shell = build_upper_shell()

for name, part in [("Bottom cup", bottom_cup), ("Upper shell", upper_shell)]:
    solids = part.solids().vals()
    print(f"{name}: {len(solids)} solid(s)")
    for i, s in enumerate(solids):
        bb = s.BoundingBox()
        print(f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
              f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")

out_dir = Path(__file__).resolve().parent

bottom_path = out_dir / "foam-bag-shell-bottom.step"
cq.exporters.export(bottom_cup, str(bottom_path))
print(f"\nExported: {bottom_path}")

upper_path = out_dir / "foam-bag-shell-upper.step"
cq.exporters.export(upper_shell, str(upper_path))
print(f"Exported: {upper_path}")
