"""Faucet shell — printed shroud that wraps the harvested Westbrass,
the flavor tubes, and the lever swing volume. Sits on top of
the above-counter plate. The dispense tip carries the cradle for
the faucet display (DISPLAY CRADLE section).

Frame: world +Z is height (up), world ±X is lateral (symmetric across
the X=0 plane), world -Y is forward (dispense direction — the gooseneck
arcs toward -Y, where the user's glass sits). The Westbrass's threaded shank
runs along world Z at world (X, Y) = (0, 0)."""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_here.parent.parent))  # for _faucet_interface
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
import fits
from _cadq_export import export_assembly
from _materials import C_FAUCET_BLACK, one_body
import _faucet_interface
from _faucet_interface import (
    flavor_tube_od,
    flavor_tube_x_offset,
    flavor_tube_hole_dia,
    pill_length_x,
    pill_width_y,
    flavor_tube_depth,
    display_housing_width,
    display_housing_length,
    display_pcb_width,
    display_corner_r,
    display_pcb_corner_r,
    display_total_depth,
    display_pcb_top_z,
    display_cover_wall,
    display_cover_slip,
    display_cover_lap,
    display_cover_over_face,
    display_cover_cbore_depth,
    display_cover_screw_len,
)
from docgen import substitute_md, substitute_py_comments
from world_workplane import WorldWorkplane, xy_plane_z_up, xz_plane_y_up


# ============================================================
# WORLD FRAME PRIMITIVES
# ============================================================

def _horizontal_plane(z_offset):
    """XY plane at world Z = z_offset; coords (world_x, world_y), +Z normal."""
    return WorldWorkplane(xy_plane_z_up).workplane(offset=z_offset)


_yz_plane_x_normal = cq.Plane(
    origin=(0, 0, 0),
    xDir=(0, 1, 0),       # local +X = world +Y (depth)
    normal=(1, 0, 0),     # extrude along world +X (lateral)
)


def _vertical_plane(x_offset):
    """YZ plane at world X = x_offset; local (depth, height) = (world +Y, world +Z), +X normal."""
    return cq.Workplane(_yz_plane_x_normal).workplane(offset=x_offset)


shell_center_x = 0.0
shell_center_y = +3.175


# ZONE 1 — first [13 mm](ZONE1_HEIGHT); the Westbrass is a full ⌀[31.5 mm](WESTBRASS_OD) cylinder here

zone1_z_bottom = 0.0
zone1_z_top = 13.0
zone1_height = zone1_z_top - zone1_z_bottom  # [13 mm](ZONE1_HEIGHT)

bore_clearance = 0.25  # mm per side

# Westbrass bore — [32 mm](WESTBRASS_BORE_D); Westbrass OD [31.5 mm](WESTBRASS_OD).
westbrass_bore_diameter = 31.5 + 2.0 * bore_clearance
westbrass_bore_x = 0.0
westbrass_bore_y = 0.0

# Flavor-tube pill — 1/4" OD LLDPE tubes ([6.35 mm](FLAVOR_TUBE_OD) OD), tangent to the
# Westbrass's +Y face (Y=+[15.75 mm](WESTBRASS_RECT_LONG_HALF)) and tangent to each other at X=0.
# [13.6 mm](PILL_L) long axis (X), [7.25 mm](PILL_W) short axis (Y).
flavor_pill_center = (0.0, +flavor_tube_depth)

# [14.48 mm](FLAVOR_PILL_Y_MINUS) — flat -Y edge of the flavor pill
# cutout in zones 1-4, on the Westbrass-bore +Y wall at the cutout's X corners.
flavor_pill_y_minus_edge = min(
    +flavor_tube_depth - pill_width_y / 2.0,
    +math.sqrt((westbrass_bore_diameter / 2.0) ** 2 - (pill_length_x / 2.0) ** 2),
)


# SHELL OUTER
wall_thickness_min = 3.0
_westbrass_bore_farthest_from_shell_center = (
    (shell_center_y - westbrass_bore_y) + westbrass_bore_diameter / 2.0
)  # = [19.18 mm](WESTBRASS_BORE_FARTHEST)
_pill_farthest_from_shell_center = (
    (+flavor_tube_depth + pill_width_y / 2.0) - shell_center_y
)  # = [19.38 mm](PILL_FARTHEST)
# [22.38 mm](SHELL_OUTER_R) outer-cylinder radius.
shell_outer_r = (
    max(_westbrass_bore_farthest_from_shell_center, _pill_farthest_from_shell_center)
    + wall_thickness_min
)


# ZONE 2

zone2_z_bottom = zone1_z_top  # [13 mm](WESTBRASS_CYL_TOP_Z)
zone2_z_top = 39.0  # Westbrass plateau
zone2_height = zone2_z_top - zone2_z_bottom  # [26 mm](ZONE2_HEIGHT)

# Body rectangle dimensions
westbrass_rect_long_y = 31.5  # depth axis
westbrass_rect_short_x = 17.0  # lateral axis

westbrass_bore_rect_long_y = westbrass_rect_long_y + 2.0 * bore_clearance  # [32 mm](WESTBRASS_BORE_RECT_LONG)
westbrass_bore_rect_short_x = westbrass_rect_short_x + 2.0 * bore_clearance  # [17.5 mm](WESTBRASS_BORE_RECT_SHORT)

# Cove transition fillet — matches the Westbrass's transition_fillet_r.
cove_r = 6.0

zone2_bore_z_bottom = zone1_z_top + bore_clearance  # [13.25 mm](ZONE2_BORE_Z_BOTTOM)

# [3 mm](WALL_MIN) cylindrical shell wall above the Westbrass cyl top before the cove.
shell_outer_lip = wall_thickness_min + bore_clearance  # [3.25 mm](SHELL_OUTER_LIP)
zone1_outer_z_top = zone1_z_top + shell_outer_lip  # [16.25 mm](ZONE1_OUTER_Z_TOP)
zone2_outer_z_bottom = zone1_outer_z_top  # [16.25 mm](ZONE1_OUTER_Z_TOP)


# BASE PODS — two lateral pods on the +-X sides of the foot plus a third on
# the front (−Y) centerline, each hosting one plate-to-shell screw boss.
# Mechanism: heat-set insert in the shell, screw up from under the plate (head
# recessed in the plate bottom) through the plate boss, clamping the plate up
# into the shell. These three anchors close the shell and plate around the
# fitted Westbrass. The retained donor washer and shank nut remain loose
# on the shank until they clamp the final countertop + under-counter-plate stack.
#
# Nested fastener chain (BNUOK M3 SHCS 304 SS, head ~5.43 mm measured; ruthex
# M3 insert). Counterbore + boss are plate-side; the boss hole, insert pocket,
# and pod live in the shell — but the whole chain is derived here so wall
# thickness is one knob.
base_pod_counterbore_dia = 6.15     # clearance bore over the M3 SHCS head (~5.43
                                    # measured) — the head bears on the shank-bore
                                    # ring, so nothing registers on this wall
base_pod_shank_dia = 3.9            # M3 shank clearance — plate boss bore up to the insert
base_pod_wall = 3.0                 # wall added at each step (plate boss wall = shell wall)
base_pod_slip = 2.0 * fits.slip     # boss-to-hole diametral slip fit; the three pins
                                    # enter together, led in by `boss_chamfer` on each
base_pod_boss_dia = base_pod_counterbore_dia + 2.0 * base_pod_wall  # plate boss OD
base_pod_hole_dia = base_pod_boss_dia + base_pod_slip               # shell pocket
base_pod_radius = base_pod_hole_dia / 2.0 + base_pod_wall           # pod outer
base_pod_center_y = shell_center_y  # foot-circle (and plate) center line, +Y
# Center slides outward as the pod grows: placed so the pod's inner edge sits
# tangent to the Westbrass bore (a base_pod_wall-thick wall from the pocket to the bore).
base_pod_center_x = math.sqrt(
    (westbrass_bore_diameter / 2.0 + base_pod_radius) ** 2 - base_pod_center_y ** 2
)
# Third pod on the front (−Y) centerline — the anchor the two lateral bosses
# can't be: both sit on the X-axis, so they give no front/back couple. Same
# radius and same bore tangency as the laterals (inner edge touches the Westbrass
# bore, base_pod_wall from the pocket to the bore), straight in front.
base_pod_front_center_x = 0.0
base_pod_front_center_y = -(westbrass_bore_diameter / 2.0 + base_pod_radius)  # [-25.27 mm](BASE_POD_FRONT_CENTER_Y)
# All three pod centers (both laterals + the front) — the boss-hole/insert
# pattern, shared with the plate so its bosses land on exactly the same points.
base_pod_centers = [
    (+base_pod_center_x, base_pod_center_y),
    (-base_pod_center_x, base_pod_center_y),
    (base_pod_front_center_x, base_pod_front_center_y),
]
base_pod_z_bottom = zone1_z_bottom  # deck plane, Z=0
base_pod_z_top = zone1_outer_z_top  # match the base-cylinder top
base_pod_hole_depth = 8.0           # boss engagement depth up from the deck; an
                                    # M3x12 reaches a ruthex M3 insert seated above
# ruthex M3 short heat-set insert (⌀4.2 OD), seated opening-DOWN onto the boss
# hole: the M3x12 driven up from under the plate exits the boss top and threads
# into it. ⌀4 pocket — the knurled OD melts into ⌀4. Depth runs from the
# boss-hole top to one base_pod_wall below the pod top, so the cap over the
# insert is the same one-knob wall as everywhere else.
base_pod_insert_dia = 4.0
base_pod_insert_depth = (
    base_pod_z_top - base_pod_z_bottom - base_pod_hole_depth - base_pod_wall
)  # [5.25 mm](BASE_POD_INSERT_DEPTH) = 4 mm insert engagement + 1.25 mm relief


# LEVER SWING CLEARANCE — chamfer wedge cut into the top -Y corner of
# the rect column, where the pressed lever's taper passes through.

lever_x_half = 6.5
lever_clearance_x_half = lever_x_half + bore_clearance  # [6.75 mm](LEVER_CLEAR_X_HALF)
lever_ramp_depth = 1.0
tangent_overshoot = 0.002

shell_rect_y_half = shell_outer_r  # [22.38 mm](SHELL_OUTER_R)
shell_rect_x_half = westbrass_bore_rect_short_x / 2.0 + wall_thickness_min  # [11.75 mm](SHELL_RECT_X_HALF)
shell_rect_y_width = 2.0 * shell_rect_y_half
shell_rect_x_width = 2.0 * shell_rect_x_half
shell_rect_y_max = shell_center_y + shell_rect_y_half  # [25.55 mm](SHELL_RECT_Y_MAX) (toward back)
shell_rect_y_min = shell_center_y - shell_rect_y_half  # [-19.2 mm](SHELL_RECT_Y_MIN) (toward user)

lever_ramp_y_min = shell_center_y - shell_outer_r  # [-19.2 mm](SHELL_RECT_Y_MIN), outer rect face -Y side
_bore_y_at_lever_x = math.sqrt(
    (westbrass_bore_diameter / 2.0) ** 2 - lever_clearance_x_half ** 2
)  # ≈ [14.51 mm](BORE_Y_AT_LEVER_X) — bore-cyl tangent at the cut's X half-span
lever_ramp_y_start = -(_bore_y_at_lever_x + tangent_overshoot)  # ≈ [-14.51 mm](LEVER_RAMP_Y_START)


# ZONE 3 — arch wraps (two wings at ±X)
#
# Body arches: 1.5 mm ridges at X = ±7.75, full Y width (±15.75); profile
# in (Y, Z) is a 2 mm foot from Z=39→41 then a 3-point arc through
# (∓15.75, 41) and (0, 46).
# Plateau between the arches (X ∈ ±[6.75 mm](WING_INNER_X)) is open.

zone3_z_bottom = zone2_z_top  # [39 mm](ZONE3_Z_BOTTOM)

arch_z_base = 41.0  # Westbrass foot top
arch_z_peak = 46.0  # Westbrass arc peak
westbrass_arch_inner_x = 7.0
westbrass_arch_outer_x = 8.5

shell_arch_bore_inner_x = westbrass_arch_inner_x - bore_clearance  # [6.75 mm](SHELL_ARCH_BORE_INNER_X)
shell_arch_bore_outer_x = westbrass_arch_outer_x + bore_clearance  # [8.75 mm](SHELL_ARCH_BORE_OUTER_X)
shell_arch_bore_z_foot_top = arch_z_base + bore_clearance  # [41.25 mm](SHELL_ARCH_BORE_Z_FOOT_TOP)
shell_arch_bore_z_peak = arch_z_peak + bore_clearance  # [46.25 mm](SHELL_ARCH_BORE_Z_PEAK)

shell_arch_z_foot_top = arch_z_base + shell_outer_lip  # [44.25 mm](SHELL_ARCH_Z_FOOT_TOP)
shell_arch_z_peak = arch_z_peak + shell_outer_lip  # [49.25 mm](SHELL_ARCH_Z_PEAK)
wing_inner_x = shell_arch_bore_inner_x  # [6.75 mm](WING_INNER_X)
wing_outer_x = shell_rect_x_half  # [11.75 mm](SHELL_RECT_X_HALF)

# ZONE 3 — plateau fill (between the wings, Y ≥ fill_y_min).
soda_faucet_tube_y = +8.875
# 3/8" LLDPE soda faucet tube, internal to the faucet — sealed in the
# Westbrass's 10.0 mm port via a printed TPU bushing (see
# ../tpu-o-ring/).
soda_faucet_tube_od = 0.375 * 25.4  # [9.525 mm](SODA_FAUCET_TUBE_OD)
# [10.22 mm](SODA_FAUCET_HOLE_D) water bore.
soda_faucet_hole_diameter = soda_faucet_tube_od + 2.0 * bore_clearance + 0.20

# 1/4" LLDPE flavor tubes, tangent to the soda faucet tube at the dispense
# point and sitting behind it (more +Y).
flavor_tube_post_bend_y = soda_faucet_tube_y + math.sqrt(
    (soda_faucet_tube_od / 2.0 + flavor_tube_od / 2.0) ** 2
    - flavor_tube_x_offset ** 2
)  # ≈ [16.15 mm](FLAVOR_POST_BEND_Y)

fill_y_min = +10.46  # back third of the soda faucet tube (Y ≥ [10.46 mm](FILL_Y_MIN))


# ZONE 4 — rect column above the arch (soda faucet tube + flavor pill cutouts).
zone4_z_bottom = shell_arch_z_foot_top  # [44.25 mm](SHELL_ARCH_Z_FOOT_TOP)
# Clears the pressed-lever head corner (Y=+6.78, Z=54.024), which sits
# inside zone 5's water-circle outline (Y=+[8.875 mm](SODA_FAUCET_TUBE_Y),
# R=[9.112 mm](TUBE_SHELL_SODA_R)); zone 5's bottom is above it.
zone4_z_top = 57.5
zone4_height = zone4_z_top - zone4_z_bottom  # [13.25 mm](ZONE4_HEIGHT)


# ZONE 5 — tube wrapper above the lever: water cyl bore + flavor pill
# bore, each + [4 mm](ZONE5_WALL) wall, extending in -Y past fill_y_min.
zone5_z_bottom = zone4_z_top  # [57.5 mm](ZONE5_Z_BOTTOM)
zone5_z_top = zone4_z_top + 10.0  # [67.5 mm](ZONE5_Z_TOP)
zone5_height = zone5_z_top - zone5_z_bottom  # [10 mm](ZONE5_HEIGHT)
zone5_wall = wall_thickness_min + 1

# Tube-shell cross-section — shared by zone 5's vertical extrusion and
# zone 6's gooseneck sweep. Water and flavor share one outer X half-width
# (the larger of the two); Y side walls stay at zone5_wall.
tube_shell_soda_r_outer = soda_faucet_hole_diameter / 2.0 + zone5_wall   # [9.112 mm](TUBE_SHELL_SODA_R)
tube_shell_pill_x_half_outer = pill_length_x / 2.0 + zone5_wall
tube_shell_x_half_outer = max(tube_shell_soda_r_outer, tube_shell_pill_x_half_outer)
tube_shell_x_outer = 2.0 * tube_shell_x_half_outer
# Water → flavor offset along world Y; positive — flavor sits behind water.
flavor_offset_y_from_water = flavor_tube_post_bend_y - soda_faucet_tube_y  # ≈ [7.275 mm](FLAVOR_OFFSET_Y)


# ZONE 6 — gooseneck wrapper around the bent tubes: zone 5's
# cross-section swept along a bent path above the lever-swing envelope.
# Mirrors constants in `faucet-assembly`.

gn_bend1_r = 30.0
gn_bend2_r = 40.0
gn_bend1_sweep_rad = math.radians(30.0)
gn_bend2_sweep_rad = math.radians(110.0)
# 35 mm above the lever rest top (at zone2_z_top + 13 = [52 mm](LEVER_REST_TOP_Z)).
gn_bend1_z_mid = zone2_z_top + 48.0  # [87 mm](GN_BEND1_Z_MID)
gn_bend1_z_start = (
    gn_bend1_z_mid
    - gn_bend1_r * math.sin(gn_bend1_sweep_rad / 2.0)
)  # ≈ [79.24 mm](GN_BEND1_Z_START)
gn_mid_straight_len = 115.0
gn_tip_straight_len = 25.0


# SPLIT — the shell prints in TWO pieces, meeting at one 20 mm slip-fit
# joint on bend 2, at half the gooseneck's total turn. Each piece then
# carries [70°](SPLIT_JUNCTION_ROT) of turn and prints with its build direction on its own
# half's angular midpoint, so the steepest overhang either piece can
# reach is a quarter of the total turn (PRINTING section). The joint's
# mating surfaces follow the arc: the tip swings shut about the bend-2
# axis.
# Fit: the plug's outer surface sits slip/2 inside the socket's cavity
# surface, all the way around the cross-section.

_path_total_rot = gn_bend1_sweep_rad + gn_bend2_sweep_rad  # [140°](GN_TOTAL_ROT) at the tip
split_junction_rot = _path_total_rot / 2.0  # [70°](SPLIT_JUNCTION_ROT)

# Per-side overlap depth (mm of arc), socket wall (mm), and diametral
# slip (mm), mapped onto `shrink`s (inward offsets of the outer
# cross-section):
#   socket shrink = socket_wall
#   plug   shrink = socket_shrink + slip / 2
split_socket_overlap_len = 20.0
split_plug_overlap_len = 18.0
split_socket_wall = 2.0
split_slip = 2.0 * fits.slip

split_socket_shrink = split_socket_wall
split_plug_shrink = split_socket_shrink + split_slip / 2.0


# SPLIT geometry.
#
# All `_path_*` constants below are in path-local 2D coords: local axes
# (a, b) map to world (-Y, +Z); X=0, origin at world (0, soda_faucet_tube_y,
# zone5_z_top).

# Bend-2 sub-arcs covering the last overlap_len mm of arc before the
# junction — separate arcs for the female socket and the male plug.
split_socket_angle_rad = split_socket_overlap_len / gn_bend2_r
split_plug_angle_rad = split_plug_overlap_len / gn_bend2_r

# Cumulative path rotations from the +Z origin tangent.
_path_socket_start_rot = split_junction_rot - split_socket_angle_rad
_path_socket_mid_rot = split_junction_rot - split_socket_angle_rad / 2.0
_path_plug_start_rot = split_junction_rot - split_plug_angle_rad
_path_plug_mid_rot = split_junction_rot - split_plug_angle_rad / 2.0

# Tangent unit-vectors in path-local (a, b).
_tan_after_bend1 = (math.sin(gn_bend1_sweep_rad), math.cos(gn_bend1_sweep_rad))
_tan_after_bend2 = (math.sin(_path_total_rot), math.cos(_path_total_rot))
_tan_at_junction = (
    math.sin(split_junction_rot), math.cos(split_junction_rot),
)
_tan_at_socket_start = (
    math.sin(_path_socket_start_rot), math.cos(_path_socket_start_rot),
)
_tan_at_plug_start = (
    math.sin(_path_plug_start_rot), math.cos(_path_plug_start_rot),
)

# Path-local waypoints, working forward from the path origin.
_path_z_lift = gn_bend1_z_start - zone5_z_top
_path_p2 = (  # end of bend 1 / start of mid-straight
    gn_bend1_r * (1.0 - math.cos(gn_bend1_sweep_rad)),
    _path_z_lift + gn_bend1_r * math.sin(gn_bend1_sweep_rad),
)
_path_p3 = (  # end of mid-straight / start of bend 2
    _path_p2[0] + gn_mid_straight_len * _tan_after_bend1[0],
    _path_p2[1] + gn_mid_straight_len * _tan_after_bend1[1],
)
# Bend-2 arc center.
_path_center_bend2 = (
    _path_p3[0] + gn_bend2_r * math.cos(gn_bend1_sweep_rad),
    _path_p3[1] - gn_bend2_r * math.sin(gn_bend1_sweep_rad),
)


def _bend2_point(rot: float) -> tuple:
    """Path-local (a, b) on bend 2 at cumulative rotation `rot` from vertical."""
    return (
        _path_center_bend2[0] - gn_bend2_r * math.cos(rot),
        _path_center_bend2[1] + gn_bend2_r * math.sin(rot),
    )


_path_junction = _bend2_point(split_junction_rot)
_path_socket_start = _bend2_point(_path_socket_start_rot)
_path_socket_mid = _bend2_point(_path_socket_mid_rot)
_path_plug_start = _bend2_point(_path_plug_start_rot)
_path_plug_mid = _bend2_point(_path_plug_mid_rot)
_path_p4 = _bend2_point(_path_total_rot)  # end of bend 2 / start of tip
_path_p5 = (  # end of tip
    _path_p4[0] + gn_tip_straight_len * _tan_after_bend2[0],
    _path_p4[1] + gn_tip_straight_len * _tan_after_bend2[1],
)

# SPLIT mating-plane geometry in world coords. The plane is
# perpendicular to the gooseneck tangent at the junction.
split_normal = (0.0, -_tan_at_junction[0], _tan_at_junction[1])
split_junction_y = soda_faucet_tube_y - _path_junction[0]  # [-73.6 mm](SPLIT_JUNCTION_Y)
split_junction_z = zone5_z_top + _path_junction[1]  # [211.4 mm](SPLIT_JUNCTION_Z)


# PRINTING — each piece beds on the face at the far end of its own half
# of the turn and tilts until its build direction lands on that half's
# angular midpoint. The overhang on a swept flank is then the angle
# between the build direction and the local tangent, which over a half
# of length split_junction_rot never exceeds half of it. Splitting the
# turn in half and bisecting each half is what puts the worst visible
# overhang at a quarter of the whole.
#
# The base beds on its foot (Z=0) with the -Y edge lifted; the tip beds
# on the joint end with the crown lifted.
#
# Build direction of each piece, as a path rotation: the angular
# midpoint of the half it carries.
print_base_build_rot = split_junction_rot / 2.0
print_tip_build_rot = (split_junction_rot + _path_total_rot) / 2.0
# Tilt off the bed face. The foot is square to the path at rotation 0
# and the joint face to the path at the junction, so each tilt is the
# distance from that end round to the build direction — [35°](PRINT_TILT) both.
print_base_tilt_rad = print_base_build_rot
print_tip_tilt_rad = print_tip_build_rot - split_junction_rot
max_print_overhang_rad = _path_total_rot / 4.0  # [35°](MAX_PRINT_OVERHANG)


# ZONE 3 OUTER ARCH — single circular arc from the wing bottom
# (zone3_z_bottom at the -Y end) up to zone4_z_top at Y=fill_y_min,
# tangent-horizontal at the high end. Center is directly below the high end.
_back_arch_dy = fill_y_min - shell_rect_y_min  # [29.66 mm](BACK_ARCH_DY) (positive depth span)
back_arch_center_z = (
    (zone4_z_top + zone3_z_bottom) / 2.0
    - _back_arch_dy ** 2 / (2.0 * (zone4_z_top - zone3_z_bottom))
)
back_arch_r = zone4_z_top - back_arch_center_z
# Angular midpoint of the arc, between the high end (fill_y_min) and the
# low end (shell_rect_y_min, the -Y front/user edge of the rect column).
_back_arch_a_low = math.atan2(zone3_z_bottom - back_arch_center_z,
                              shell_rect_y_min - fill_y_min)
_back_arch_a_mid = (math.pi / 2.0 + _back_arch_a_low) / 2.0
back_arch_mid_y = fill_y_min + back_arch_r * math.cos(_back_arch_a_mid)
back_arch_mid_z = back_arch_center_z + back_arch_r * math.sin(_back_arch_a_mid)


# ZONE 4.5 — block capping the lever swing volume from above, reaching
# up to Z=gn_bend1_z_start ≈ [79.24 mm](GN_BEND1_Z_START).

# Zone 5's tube-shell Y extents at X=0: soda faucet tube on -Y, flavor pill on +Y.
_z5_y_min = soda_faucet_tube_y - tube_shell_soda_r_outer  # ≈ [-0.2375 mm](Z5_Y_MIN)
_z5_y_max = flavor_tube_post_bend_y + (pill_width_y + 2.0 * zone5_wall) / 2.0

# Zone 4.5 Y extents — back edge follows the rect column; front edge
# matched-margin from zone 5.
zone45_front_y = _z5_y_min - (shell_rect_y_max - _z5_y_max)

# Top sits 3 mm above zone 4's top on the back side (lid sits flat on
# zone 4 top). The front bottom follows the back-arch curve down to
# ≈ Z=[55.05 mm](ZONE45_Z_BOT_FRONT).
zone45_z_top = zone4_z_top + 3.0  # [60.5 mm](ZONE45_Z_TOP)
zone45_z_bottom_at_front = (
    back_arch_center_z
    + math.sqrt(back_arch_r ** 2 - (zone45_front_y - fill_y_min) ** 2)
)

# Mid-point of the bottom arch sub-arc, between zone45_front_y end
# and fill_y_min end.
_a_front = math.atan2(
    zone45_z_bottom_at_front - back_arch_center_z,
    zone45_front_y - fill_y_min,
)
_a_high = math.pi / 2.0  # fill_y_min end is directly above arch center
_a_mid45 = (_a_front + _a_high) / 2.0
zone45_bot_mid_y = fill_y_min + back_arch_r * math.cos(_a_mid45)
zone45_bot_mid_z = back_arch_center_z + back_arch_r * math.sin(_a_mid45)


# Joinery and retention: see ASSEMBLY.md.


# ============================================================
# GEOMETRY BUILDERS
# ============================================================

def shell_outer_cyl(z_bottom: float, z_height: float) -> cq.Workplane:
    """Shell outer cylinder (R = shell_outer_r at shell_center) over the Z range."""
    return (
        _horizontal_plane(z_bottom)
        .moveTo((shell_center_x, shell_center_y))
        .circle(shell_outer_r)
        .extrude(z_height)
    ).unwrap()


def soda_faucet_tube_cyl(z_bottom: float, z_height: float) -> cq.Workplane:
    """Soda-faucet-tube bore cylinder (R = soda_faucet_hole_diameter/2 at (0, soda_faucet_tube_y)) over the Z range."""
    return (
        _horizontal_plane(z_bottom)
        .moveTo((0.0, soda_faucet_tube_y))
        .circle(soda_faucet_hole_diameter / 2.0)
        .extrude(z_height)
    ).unwrap()


def westbrass_bore_cyl(z_bottom: float, z_height: float) -> cq.Workplane:
    """Westbrass bore cylinder (R = westbrass_bore_diameter/2 at origin) over the Z range."""
    return (
        _horizontal_plane(z_bottom)
        .moveTo((westbrass_bore_x, westbrass_bore_y))
        .circle(westbrass_bore_diameter / 2.0)
        .extrude(z_height)
    ).unwrap()


def _flavor_pill_flat_y_minus(z_bottom: float, z_height: float) -> cq.Workplane:
    """Flavor pill cutout (pill_length_x × pill_width_y, X long axis) at
    flavor_pill_center, -Y side flattened to flavor_pill_y_minus_edge."""
    pill = (
        _horizontal_plane(z_bottom)
        .moveTo(flavor_pill_center)
        .slot2D(pill_length_x, pill_width_y, angle=0)
        .extrude(z_height)
    ).unwrap()
    pill_center_y = flavor_pill_center[1]
    fill_width = pill_center_y - flavor_pill_y_minus_edge
    fill_rect = (
        _horizontal_plane(z_bottom)
        .moveTo((0.0, pill_center_y - fill_width / 2.0))
        .rect(pill_length_x, fill_width)
        .extrude(z_height)
    ).unwrap()
    return pill.union(fill_rect)


def build_zone1_outer() -> cq.Workplane:
    """Filled cylinder, from the deck up to zone1_outer_z_top."""
    return shell_outer_cyl(zone1_z_bottom, zone1_outer_z_top - zone1_z_bottom)


def build_zone1_inner_cut() -> cq.Workplane:
    """Body bore + flavor-tube pill."""
    westbrass_bore = westbrass_bore_cyl(zone1_z_bottom, zone2_bore_z_bottom - zone1_z_bottom)
    pill = _flavor_pill_flat_y_minus(zone1_z_bottom, zone1_height)
    return westbrass_bore.union(pill)


def _base_pod_teardrops(z_bottom: float, z_height: float) -> cq.Workplane:
    """The two teardrop pods as a solid over a Z range. A base_pod_radius round
    outboard end (over the boss) with two FLAT sides — the common tangent lines
    between the pod circle and the foot cylinder, tangent at both ends so the
    pod blends into the foot with no concave notch."""
    R = shell_outer_r
    r = base_pod_radius
    cx = base_pod_center_x
    cy = base_pod_center_y
    # Common external tangent between foot (O=(0,cy), R) and pod (C=(cx,cy), r):
    # unit normal to the tangent line, at perpendicular distance R from O, r from C.
    nx = (R - r) / cx
    ny = math.sqrt(1.0 - nx * nx)
    Tf_u = (R * nx, cy + R * ny)        # tangent point on the foot, upper
    Tp_u = (cx + r * nx, cy + r * ny)   # tangent point on the pod, upper
    tip = (cx + r, cy)                  # outboard tip
    Tp_l = (cx + r * nx, cy - r * ny)
    Tf_l = (R * nx, cy - R * ny)
    plus = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(*Tf_u)
        .lineTo(*Tp_u)
        .threePointArc(tip, Tp_l)
        .lineTo(*Tf_l)
        .close()
        .extrude(z_height)
    ).val()
    minus = plus.mirror("YZ")
    return cq.Workplane(obj=plus.fuse(minus))


def build_base_pods() -> cq.Workplane:
    """The two solid teardrop pods over the foot (deck plane to base-cylinder
    top), placeholders for the lateral screw bosses — no pockets or inserts
    yet. Unioned into the shell outer before the inner cuts, so the Westbrass bore
    trims any inboard material."""
    return _base_pod_teardrops(base_pod_z_bottom, base_pod_z_top - base_pod_z_bottom)


def _base_pod_front(z_bottom: float, z_height: float) -> cq.Workplane:
    """The front (−Y) pod solid over a Z range — the foam-shell boss idiom (see
    cold-core/_outer_shell.build_attachment_bosses): a ⌀(2*base_pod_radius)
    cylinder over the boss, plus a flat-sided web box of the same width running
    inboard (+Y) to fuse into the foot wall. A 'D': round front, flat sides
    (parallel to Y) into the wall, tangent to the Westbrass bore."""
    r = base_pod_radius
    cx, cy = base_pod_front_center_x, base_pod_front_center_y
    boss = (
        _horizontal_plane(z_bottom)
        .moveTo((cx, cy))
        .circle(r)
        .extrude(z_height)
        .unwrap()
        .val()
    )
    # The web's flat sides (x = cx ± r) cross the foot cylinder at this front Y;
    # run a little past it (toward the foot center) so it fuses solidly.
    web_inboard_y = base_pod_center_y - math.sqrt(shell_outer_r ** 2 - r ** 2) + 2.5
    wy0, wy1 = sorted((cy, web_inboard_y))
    web = (
        _horizontal_plane(z_bottom)
        .moveTo((cx, (wy0 + wy1) / 2.0))
        .rect(2.0 * r, wy1 - wy0)
        .extrude(z_height)
        .unwrap()
        .val()
    )
    return cq.Workplane(obj=boss.fuse(web))


def build_base_pod_front() -> cq.Workplane:
    """The front (−Y) pod over the foot (deck plane to base-cylinder top),
    placeholder for the third screw boss. No pocket or insert yet."""
    return _base_pod_front(base_pod_z_bottom, base_pod_z_top - base_pod_z_bottom)


def build_base_pod_holes() -> cq.Workplane:
    """Per-pod inner cuts: the blind boss-hole pocket (⌀base_pod_hole_dia rising
    base_pod_hole_depth from the foot bottom, receiving the plate boss) with the
    heat-set insert pocket (⌀base_pod_insert_dia, base_pod_insert_depth) stacked
    coaxially above it. The insert opening faces down onto the boss hole so the
    M3x12 driven up from under the plate threads into it. Same pattern at all
    three pod centers (both laterals + the front)."""
    cuts = []
    for center in base_pod_centers:
        boss_hole = (
            _horizontal_plane(base_pod_z_bottom)
            .moveTo(center)
            .circle(base_pod_hole_dia / 2.0)
            .extrude(base_pod_hole_depth)
            .unwrap()
            .val()
        )
        insert_pocket = (
            _horizontal_plane(base_pod_z_bottom + base_pod_hole_depth)
            .moveTo(center)
            .circle(base_pod_insert_dia / 2.0)
            .extrude(base_pod_insert_depth)
            .unwrap()
            .val()
        )
        cuts.append(boss_hole.fuse(insert_pocket))
    return cq.Workplane(obj=cuts[0].fuse(*cuts[1:]))


def _rect_cove_cyl(
    center_x: float, center_y: float,
    rect_x_width: float, rect_y_width: float,
    z_bottom: float, z_top: float,
    clip_cyl: cq.Workplane,
) -> cq.Workplane:
    """Rect column with cove-filleted ±X faces, clipped to a cylinder
    (mirrors the Westbrass's build_transition_cove)."""
    z_height = z_top - z_bottom
    rect_x_half = rect_x_width / 2.0
    ext_y = rect_y_width / 2.0 + 2.0

    rect = (
        _horizontal_plane(z_bottom)
        .moveTo((center_x, center_y))
        .rect(rect_x_width, rect_y_width)
        .extrude(z_height)
    ).unwrap()

    def filler(x_sign: int) -> cq.Workplane:
        flat_x = center_x + x_sign * rect_x_half
        blk_cx = flat_x + x_sign * (cove_r / 2.0)
        return (
            _horizontal_plane(z_bottom)
            .moveTo((blk_cx, center_y))
            .rect(cove_r, 2.0 * ext_y)
            .extrude(cove_r)
        ).unwrap()

    def cove_cutter(x_sign: int) -> cq.Workplane:
        flat_x = center_x + x_sign * rect_x_half
        cove_cx = flat_x + x_sign * cove_r
        cove_cz = z_bottom + cove_r
        # Cylinder axis along world Y.
        return (
            WorldWorkplane(xz_plane_y_up)
            .workplane(offset=center_y - ext_y)
            .moveTo((cove_cx, cove_cz))
            .circle(cove_r)
            .extrude(2.0 * ext_y)
            .unwrap()
        )

    return (
        rect
        .union(filler(+1))
        .union(filler(-1))
        .cut(cove_cutter(+1))
        .cut(cove_cutter(-1))
        .intersect(clip_cyl)
    )


def build_zone2_outer() -> cq.Workplane:
    """Zone 2 outer — rect column with cove-filleted ±X faces, clipped to the
    shell outer cylinder WITH the base pods carried up through the transition,
    so the cove builds onto the teardrops, not just the round base."""
    z_height = zone2_z_top - zone2_outer_z_bottom
    clip = cq.Workplane(obj=shell_outer_cyl(zone2_outer_z_bottom, z_height).val().fuse(
        _base_pod_teardrops(zone2_outer_z_bottom, z_height).val()
    ))
    return _rect_cove_cyl(
        shell_center_x, shell_center_y,
        shell_rect_x_width, shell_rect_y_width,
        zone2_outer_z_bottom, zone2_z_top,
        clip,
    )


def build_zone2_inner_cut() -> cq.Workplane:
    """Zone 2 inner — Westbrass cross-section (rect + cove + cyl clip) at
    bore_clearance per side, plus the flavor-tube pill through."""
    bore_zone2_height = zone2_z_top - zone2_bore_z_bottom
    bore = _rect_cove_cyl(
        westbrass_bore_x, westbrass_bore_y,
        westbrass_bore_rect_short_x, westbrass_bore_rect_long_y,
        zone2_bore_z_bottom, zone2_z_top,
        westbrass_bore_cyl(zone2_bore_z_bottom, bore_zone2_height),
    )
    pill = _flavor_pill_flat_y_minus(zone2_z_bottom, zone2_height)
    return bore.union(pill)


def _arch_extrude(x_bottom: float, x_height: float) -> cq.Workplane:
    """Outer arch profile in the (Y, Z) plane — flat bottom at
    zone3_z_bottom, flat top at zone4_z_top from +Y back to fill_y_min,
    then the back-arch curve down to shell_rect_y_min — extruded along +X."""
    return (
        _vertical_plane(x_bottom)
        .moveTo(shell_rect_y_min, zone3_z_bottom)
        .lineTo(shell_rect_y_max, zone3_z_bottom)
        .lineTo(shell_rect_y_max, zone4_z_top)
        .lineTo(fill_y_min, zone4_z_top)
        .threePointArc((back_arch_mid_y, back_arch_mid_z),
                       (shell_rect_y_min, zone3_z_bottom))
        .close()
        .extrude(x_height)
    )


def build_zone3_outer() -> cq.Workplane:
    """Two arch wings at ±X wrapping the Westbrass's arch ridges."""
    wing_thickness = wing_outer_x - wing_inner_x
    wings = _arch_extrude(+wing_inner_x, +wing_thickness).union(
        _arch_extrude(-wing_outer_x, +wing_thickness)
    )
    return wings.intersect(shell_outer_cyl(zone3_z_bottom, zone4_z_top - zone3_z_bottom))


def build_zone3_inner_cut() -> cq.Workplane:
    """Two arch bores at ±X mirroring the Westbrass arches with bore_clearance."""
    bore_y_oversize = westbrass_bore_diameter / 2.0 + 2.0

    def bore(x_bottom: float, x_height: float) -> cq.Workplane:
        return (
            _vertical_plane(x_bottom)
            .moveTo(+bore_y_oversize, zone3_z_bottom)
            .lineTo(-bore_y_oversize, zone3_z_bottom)
            .lineTo(-bore_y_oversize, shell_arch_bore_z_foot_top)
            .threePointArc((0, shell_arch_bore_z_peak),
                           (+bore_y_oversize, shell_arch_bore_z_foot_top))
            .close()
            .extrude(x_height)
        )

    bore_thickness = shell_arch_bore_outer_x - shell_arch_bore_inner_x
    bores = bore(+shell_arch_bore_inner_x, +bore_thickness).union(
        bore(-shell_arch_bore_outer_x, +bore_thickness)
    )
    return bores.intersect(westbrass_bore_cyl(zone3_z_bottom, shell_arch_bore_z_peak - zone3_z_bottom))


def build_zone3_fill_outer() -> cq.Workplane:
    """Plateau fill behind fill_y_min — the wings' arch profile extruded
    across the plateau X range, Westbrass bore column cut away."""
    fill_x_thickness = 2.0 * wing_inner_x  # [13.5 mm](FILL_X_THICKNESS)
    z_height = zone4_z_top - zone3_z_bottom

    arch_solid = _arch_extrude(-wing_inner_x, fill_x_thickness)
    keep_y_box = (
        _horizontal_plane(zone3_z_bottom)
        .moveTo((0.0, (fill_y_min + shell_rect_y_max) / 2.0))
        .rect(fill_x_thickness, shell_rect_y_max - fill_y_min)
        .extrude(z_height)
    ).unwrap()
    return (
        arch_solid
        .intersect(keep_y_box)
        .intersect(shell_outer_cyl(zone3_z_bottom, z_height))
        .cut(westbrass_bore_cyl(zone3_z_bottom, z_height))
    )


def build_zone3_fill_inner_cut() -> cq.Workplane:
    """Tube cutouts through the plateau fill: soda faucet tube + straight flavor
    pill at flavor_pill_center. The bend lives in the tube shell above."""
    z_height = shell_arch_z_peak - zone3_z_bottom
    water_hole = soda_faucet_tube_cyl(zone3_z_bottom, z_height)
    flavor_pill = _flavor_pill_flat_y_minus(zone3_z_bottom, z_height)
    return water_hole.union(flavor_pill)


def build_zone4_outer() -> cq.Workplane:
    """Zone 4 outer — rect ∩ outer cyl at Y ≥ fill_y_min, Westbrass bore column cut away."""
    z_height = zone4_height
    rect = (
        _horizontal_plane(zone4_z_bottom)
        .moveTo((shell_center_x, shell_center_y))
        .rect(shell_rect_x_width, shell_rect_y_width)
        .extrude(z_height)
    ).unwrap()
    # Y ≥ fill_y_min half-space.
    keep_pos_y = (
        _horizontal_plane(zone4_z_bottom - 1)
        .moveTo((0.0, fill_y_min + 50))
        .rect(200, 100)
        .extrude(z_height + 2)
    ).unwrap()
    return (
        rect
        .intersect(shell_outer_cyl(zone4_z_bottom, z_height))
        .intersect(keep_pos_y)
        .cut(westbrass_bore_cyl(zone4_z_bottom, zone4_height))
    )


def build_zone4_inner_cut() -> cq.Workplane:
    """Tube cavity: water-tube cyl + straight flavor pill. Straight cuts
    only — the flavor bend lives in the tube shell above."""
    water_inner = soda_faucet_tube_cyl(zone4_z_bottom, zone4_height)
    flavor_pill = _flavor_pill_flat_y_minus(zone4_z_bottom, zone4_height)
    return water_inner.union(flavor_pill)


def build_zone45_outer() -> cq.Workplane:
    """Zone 4.5 — tall block capping the lever swing volume, reaching up
    to the gooseneck bend start. Two mirrored shell_outer_r cylinder
    clips (back at shell_center_y, front at zone45_front_y + shell_outer_r)
    round the +Y / -Y edges symmetrically."""
    x_half = shell_rect_x_half
    profile_solid = (
        _vertical_plane(-x_half)
        .moveTo(zone45_front_y, zone45_z_bottom_at_front)
        .threePointArc(
            (zone45_bot_mid_y, zone45_bot_mid_z),
            (fill_y_min, zone4_z_top),
        )
        .lineTo(shell_rect_y_max, zone4_z_top)
        .lineTo(shell_rect_y_max, zone45_z_top)
        .lineTo(zone45_front_y, zone45_z_top)
        .close()
        .extrude(2.0 * x_half)
    )

    z_min = zone45_z_bottom_at_front
    clip_height = (zone45_z_top - z_min) + 1.0
    back_clip = shell_outer_cyl(z_min - 0.5, clip_height)
    front_clip = (
        _horizontal_plane(z_min - 0.5)
        .moveTo((shell_center_x, zone45_front_y + shell_outer_r))
        .circle(shell_outer_r)
        .extrude(clip_height)
    ).unwrap()
    return profile_solid.intersect(back_clip).intersect(front_clip)


def _arc_from_tangent(start, tangent, radius, theta_rad, ccw):
    """(mid, end, end_tangent) for a 2D arc from `start` along `tangent`, sweeping `theta_rad` at `radius`."""
    sign = +1 if ccw else -1
    if ccw:
        perp = (-tangent[1], tangent[0])
    else:
        perp = (tangent[1], -tangent[0])
    center = (start[0] + radius * perp[0], start[1] + radius * perp[1])
    rad = (start[0] - center[0], start[1] - center[1])

    def _rot(v, a):
        c, s = math.cos(a), math.sin(a)
        return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)

    rad_mid = _rot(rad, sign * theta_rad / 2.0)
    rad_end = _rot(rad, sign * theta_rad)

    mid = (center[0] + rad_mid[0], center[1] + rad_mid[1])
    end = (center[0] + rad_end[0], center[1] + rad_end[1])
    end_tangent = _rot(tangent, sign * theta_rad)
    return mid, end, end_tangent


# Gooseneck path plane (Y-Z, X=0). Local (a, b) ↔ world (-Y, +Z);
# bending CW from the +Z tangent bends toward -Y (toward the user).
_path_plane = cq.Plane(
    origin=(0, 0, 0),
    xDir=(0, -1, 0),    # local +X = world -Y (forward, toward user)
    normal=(-1, 0, 0),  # local +Y = world +Z (normal × xDir = +Z)
)


# Gooseneck sweep profile plane: normal = +Z, local (X, Y) = world (X, Y).
_profile_plane = cq.Plane(
    origin=(0, 0, 0),
    xDir=(1, 0, 0),
    normal=(0, 0, 1),
)


def _gooseneck_path_at_origin() -> cq.Workplane:
    """Gooseneck path in path-local (a, b): vertical lift, bend 1, mid
    straight, bend 2, tip straight. Origin (s=0) lands in world at
    (0, soda_faucet_tube_y, zone5_z_top)."""
    z_lift = gn_bend1_z_start - zone5_z_top

    p_bottom = (0.0, 0.0)
    p_bend_start = (0.0, z_lift)

    mid1, end1, tan1 = _arc_from_tangent(
        p_bend_start, (0.0, 1.0), gn_bend1_r, gn_bend1_sweep_rad, ccw=False
    )
    mid_end = (end1[0] + gn_mid_straight_len * tan1[0],
               end1[1] + gn_mid_straight_len * tan1[1])
    mid2, end2, tan2 = _arc_from_tangent(
        mid_end, tan1, gn_bend2_r, gn_bend2_sweep_rad, ccw=False
    )
    tip_end = (end2[0] + gn_tip_straight_len * tan2[0],
               end2[1] + gn_tip_straight_len * tan2[1])

    return (
        cq.Workplane(_path_plane)
        .moveTo(*p_bottom)
        .lineTo(*p_bend_start)
        .threePointArc(mid1, end1)
        .lineTo(*mid_end)
        .threePointArc(mid2, end2)
        .lineTo(*tip_end)
    )


def _tube_shell_outer_sketch() -> cq.Sketch:
    """Tube-shell outer cross-section, centered on the soda faucet tube: one
    connected region of water slot + flavor pill (offset -Y) + fill rect."""
    water_y_width = 2.0 * tube_shell_soda_r_outer
    water_slot_straight = tube_shell_x_outer - water_y_width
    pill_short_total = pill_width_y + 2.0 * zone5_wall
    pill_straight = tube_shell_x_outer - pill_short_total
    return (
        cq.Sketch()
        .slot(water_slot_straight, water_y_width, angle=0)
        .push([(0, flavor_offset_y_from_water)])
        .slot(pill_straight, pill_short_total, angle=0, mode="a")
        .reset()
        .push([(0, flavor_offset_y_from_water / 2.0)])
        .rect(tube_shell_x_outer, -flavor_offset_y_from_water, mode="a")
        .clean()
    )


def _tube_shell_inner_sketch() -> cq.Sketch:
    """Tube-shell inner cross-section: water circle + flavor pill (offset -Y)."""
    pill_straight = pill_length_x - pill_width_y  # [6.35 mm](PILL_STRAIGHT_INNER)
    return (
        cq.Sketch()
        .circle(soda_faucet_hole_diameter / 2.0)
        .push([(0, flavor_offset_y_from_water)])
        .slot(pill_straight, pill_width_y, angle=0, mode="a")
        .clean()
    )


def _sweep_along_gooseneck(sketch: cq.Sketch) -> cq.Workplane:
    """`sketch` swept along the gooseneck path, placed at the zone-5 seam
    (0, soda_faucet_tube_y, zone5_z_top)."""
    profile = cq.Workplane(_profile_plane).placeSketch(sketch)
    swept = profile.sweep(_gooseneck_path_at_origin(), transition="right")
    return swept.translate((0, soda_faucet_tube_y, zone5_z_top))


def build_zone6_outer() -> cq.Workplane:
    return _sweep_along_gooseneck(_tube_shell_outer_sketch())


def build_zone6_inner_cut() -> cq.Workplane:
    return _sweep_along_gooseneck(_tube_shell_inner_sketch())


def _tube_shell_outer_shrunk_sketch(shrink: float) -> cq.Sketch:
    """_tube_shell_outer_sketch offset inward by `shrink` mm (centers fixed)."""
    water_y_width = 2.0 * (tube_shell_soda_r_outer - shrink)
    new_x_outer = tube_shell_x_outer - 2.0 * shrink
    water_slot_straight = new_x_outer - water_y_width
    pill_short_total = pill_width_y + 2.0 * (zone5_wall - shrink)
    pill_straight = new_x_outer - pill_short_total
    return (
        cq.Sketch()
        .slot(water_slot_straight, water_y_width, angle=0)
        .push([(0, flavor_offset_y_from_water)])
        .slot(pill_straight, pill_short_total, angle=0, mode="a")
        .reset()
        .push([(0, flavor_offset_y_from_water / 2.0)])
        .rect(new_x_outer, -flavor_offset_y_from_water, mode="a")
        .clean()
    )


def _build_zone6_outer_shrunk(shrink: float) -> cq.Workplane:
    """Gooseneck outer with the cross-section offset inward by `shrink`."""
    return _sweep_along_gooseneck(_tube_shell_outer_shrunk_sketch(shrink))


def _split_plane_halfspace(origin: tuple, normal: tuple, sign: int,
                           extent: float = 600.0) -> cq.Workplane:
    """Solid filling one side of a plane: sign +1 = +normal side, -1 = −normal side."""
    plane = cq.Plane(
        origin=cq.Vector(*origin),
        xDir=cq.Vector(1, 0, 0),  # world X lies in the plane (normal is in YZ)
        normal=cq.Vector(*normal),
    )
    return cq.Workplane(plane).rect(2.0 * extent, 2.0 * extent).extrude(sign * extent)


def _sweep_segment_in_path_local(
    start_yz: tuple,
    tangent_yz: tuple,
    path_workplane: cq.Workplane,
    sketch: cq.Sketch,
) -> cq.Workplane:
    """`sketch` swept along `path_workplane`, profile perpendicular to
    `tangent_yz` at `start_yz` (path-local 2D on _path_plane), placed at
    world (0, soda_faucet_tube_y, zone5_z_top)."""
    # tangent in world (X, Y, Z) — path-local (a, b) → world (-a, b)
    normal = (0.0, -tangent_yz[0], tangent_yz[1])
    xdir = (1.0, 0.0, 0.0)
    plane = cq.Plane(
        origin=cq.Vector(0.0, -start_yz[0], start_yz[1]),
        xDir=cq.Vector(*xdir),
        normal=cq.Vector(*normal),
    )
    profile = cq.Workplane(plane).placeSketch(sketch)
    swept = profile.sweep(path_workplane, transition="right")
    return swept.translate((0, soda_faucet_tube_y, zone5_z_top))


def _bend_overlap_subarc(start_yz: tuple, mid_yz: tuple) -> cq.Workplane:
    """Bend-2 sub-arc from `start_yz` through `mid_yz` to `_path_junction`, path-local (a, b)."""
    return (
        cq.Workplane(_path_plane)
        .moveTo(*start_yz)
        .threePointArc(mid_yz, _path_junction)
    )


def _build_bend_overlap(sketch: cq.Sketch, *, side: str) -> cq.Workplane:
    """`sketch` swept along the split_<side>_overlap_len mm of bend 2
    below the junction. `side` "socket" (longer) or "plug" (shorter)."""
    if side == "socket":
        start_yz, mid_yz, tan_start = _path_socket_start, _path_socket_mid, _tan_at_socket_start
    elif side == "plug":
        start_yz, mid_yz, tan_start = _path_plug_start, _path_plug_mid, _tan_at_plug_start
    else:
        raise ValueError(f"side must be 'socket' or 'plug', got {side!r}")
    return _sweep_segment_in_path_local(
        start_yz, tan_start, _bend_overlap_subarc(start_yz, mid_yz), sketch,
    )


# ============================================================
# DISPLAY CRADLE — pocket + collar on the dispense tip
# ============================================================
# The faucet display lies along the tip, screen out the top skin, walled
# on all four edges. Its bounding back (the metal feet under
# the PCB) sinks display_pocket_inset into the zone5_wall wall above the
# flavor pill, leaving display_web_over_pill of web over the pill bore.
#
# Tip frame: s = distance up-gooseneck from the tip end plane along the tip
# axis; n = distance from the water-tube centerline along the tip's top
# normal; x = world X. The device sits display_line_width up the tip —
# behind the PCB cover — occupying s ∈ [end wall, end wall +
# housing_length], n ∈ [floor, floor + total_depth].
#
# The whole cradle rides the tip piece — the SPLIT junction is 33 mm of
# arc up-gooseneck of the cradle's back end, so nothing here crosses a
# seam.
#
# The tip prints with its axis 55 degrees below the print horizontal
# and up-gooseneck pointing down, so the cradle's back end is the
# lowest cradle material on the plate and a square end there would be a
# 55-degree overhang. It ramps instead, at cradle_back_slope_rad, over
# stock added beyond the head wall so the pocket keeps its full length.
#
# Retention is the display cover plate, screwed down over the device.
# The cradle parts at display_cover_land_n — the device's own
# PCB-to-housing step — so the shell holds the board and the plate comes
# down over the housing and finishes over the face. Nothing on the shell
# reaches past that step, and the seam a hand finds around the cradle is
# a step the device already has.
#
# The plate butts the land the whole way round and is held by two
# things: the hook the south wall makes for it (below), and one M3 above
# the device's north edge, threading a ruthex insert set into the shell
# from the land.

display_web_over_pill = 1.0
display_pocket_inset = zone5_wall - display_web_over_pill
# Pocket floor (= device feet plane), from the water centerline along n.
display_floor_n = (
    flavor_offset_y_from_water + pill_width_y / 2.0 + zone5_wall
    - display_pocket_inset
)

display_cradle_clearance = 0.25   # per side, cavity walls vs device
# One extrusion of the 0.6 nozzle (its 0.62 line width) — the unit the
# cradle's printable thicknesses build from. The PCB band's opening is
# closed by an end wall this thick (the cover over the bare PCB at the
# open end), the device sits this far up the tip to make room for it,
# and the housing band's first this-much of depth is squared off — its
# corner tangency would otherwise leave a zero-angle layer-1 sliver the
# slicer silently drops.
display_line_width = 0.62
display_collar_wall = 3.0 * display_line_width    # sides — three slicer lines
display_cap_thickness = 3.0 * display_line_width  # head wall — the same three
display_wire_hole_dia = 3.0       # wire drop from the cavity into the pill cusp
display_wire_hole_s = 35.0        # drops through the pocket floor into the pill cusp
display_drain_dia = 3.0           # pocket-floor drain, same drop as the wires
# THE SOUTH WALL IS THE COVER'S HOOK. The screw is at the far end of
# the plate, so on its own it leaves the bezel's grip on the device's
# bottom edge hanging off 50 mm of cantilever. The wall between the
# device and the dispense end carries a tongue off the plate instead:
# its top third stands display_cover_hook_lap further up-gooseneck than
# the rest, and the plate's tongue goes under that.
#
# So this wall is no longer one thickness. It is a skin at the end face
# thick enough to carry the overhanging third, the reach of that
# overhang, the tongue's riser, and the travel that gets the one under
# the other — and the device sits north of all four.
display_cover_hook_skin = display_cover_wall  # end-face skin the roof cantilevers off
display_cover_hook_lap = display_cover_wall   # how far the roof reaches over the tongue
display_cover_hook_stem = display_cover_wall  # the tongue's riser, off the plate
# The plate is set down this far up-gooseneck of home, where the tongue
# clears the roof and drops straight into the notch, and pushed to the
# spout until the riser stops against the roof's face.
display_cover_hook_travel = (
    display_cover_hook_lap + display_cover_slip
)  # [2.16 mm](DISPLAY_COVER_HOOK_TRAVEL)
# The cavity's south and north faces. The cavity clears the device by
# display_cradle_clearance at each end the way it does at each side.
display_s_bottom = (
    display_cover_hook_skin + display_cover_hook_lap
    + display_cover_hook_stem + display_cover_hook_travel
)  # [7.74 mm](DISPLAY_S_BOTTOM)
display_s_top = (
    display_s_bottom + display_housing_length + 2.0 * display_cradle_clearance
)  # [46.86 mm](DISPLAY_S_TOP)
# Drain at the floor's south corner, edge tangent to the south wall:
# splash that gets past the housing drops into the pill cusp and runs
# out the gooseneck exit alongside the tubes.
display_drain_s = display_s_bottom + display_drain_dia / 2.0
display_collar_half_x = (
    display_housing_width / 2.0 + display_cradle_clearance + display_collar_wall
)
# The device's face, and the plate's outer face over it.
display_face_n = display_floor_n + display_total_depth  # [22.25 mm](DISPLAY_FACE_N)
display_cover_top_n = display_face_n + display_cover_over_face + display_cover_wall
_pcb_band_half_x = display_pcb_width / 2.0 + display_cradle_clearance
# Step to the housing band 0.05 below the device's own PCB→housing step,
# so the housing's overhang ledge never reaches the narrower PCB band.
_pcb_band_n_top = display_floor_n + display_pcb_top_z - 0.05
_housing_band_half_x = display_housing_width / 2.0 + display_cradle_clearance
# THE CRADLE PARTS HERE. The shell stops at the step the device's own
# board makes under its housing; everything above it is the cover plate.
display_cover_land_n = _pcb_band_n_top  # [17.2 mm](DISPLAY_COVER_LAND_N)
# How the south wall's inner face divides. Off the floor, only enough
# air to keep the tongue from landing on it — everything else is section,
# split evenly between the tongue and the roof over it, because the two
# carry the same load in opposite directions and neither should be the
# one that gives.
display_cover_hook_relief = 0.5  # air under the tongue
_cradle_wall_h = display_cover_land_n - display_floor_n  # [5.3 mm](CRADLE_WALL_H)
display_cover_hook_n0 = display_floor_n + display_cover_hook_relief  # [12.4 mm](DISPLAY_COVER_HOOK_N0)
display_cover_hook_n1 = (
    display_cover_hook_n0 + display_cover_land_n
) / 2.0  # [14.8 mm](DISPLAY_COVER_HOOK_N1) — [2.4 mm](DISPLAY_COVER_HOOK_T) of each
# The tongue is the wall's own straight run wide — the cavity's south
# face is a rounded rectangle's end, and this is the flat of it. Wall
# is left standing either side of the notch, and that is what still
# stops the device.
display_cover_hook_half_x = (
    _housing_band_half_x - (display_corner_r + display_cradle_clearance)
)  # [6.5 mm](DISPLAY_COVER_HOOK_HALF_X)
# The tongue's own stations along the tip. The riser stands against the
# roof's up-gooseneck face, and the tongue reaches back under the roof
# from there to within a slip of the notch's own end.
display_cover_hook_s0 = display_cover_hook_skin + display_cover_slip
display_cover_hook_s1 = (
    display_cover_hook_skin + display_cover_hook_lap + display_cover_hook_stem
)  # [5.58 mm](DISPLAY_COVER_HOOK_S1)
display_cover_stem_s0 = display_cover_hook_skin + display_cover_hook_lap  # [3.72 mm](DISPLAY_COVER_STEM_S0)
# The one screw, on the centreline north of the device. Same chain as the
# base pods: a ruthex M3 short set opening-up into the shell from the
# land, a clearance shank through the plate, and the head sunk in a
# counterbore. ⌀4 pocket — the knurled ⌀4.2 OD melts into ⌀4.
display_cover_insert_dia = base_pod_insert_dia
display_cover_boss_wall = 1.5             # material round the insert
display_cover_shank_dia = base_pod_shank_dia
display_cover_cbore_dia = base_pod_counterbore_dia
display_cover_insert_len = 4.0            # ruthex M3 short body
display_cover_bore_relief = 1.25          # somewhere for a long screw to go
display_cover_insert_depth = display_cover_insert_len + display_cover_bore_relief
display_cover_boss_dia = display_cover_insert_dia + 2.0 * display_cover_boss_wall  # [7 mm](DISPLAY_COVER_BOSS_DIA)
# Boss centre: clear of the cavity's north face by the head wall and its
# own radius, so the pocket stands in solid shell.
display_cover_screw_s = (
    display_s_top + display_cap_thickness + display_cover_insert_dia / 2.0
)  # [52.22 mm](DISPLAY_COVER_SCREW_S)
_block_n_bottom = display_floor_n - 4.0
# The collar's outer faces extend below _block_n_bottom by the width of
# the bottom overhang beside the gooseneck there (collar half-width minus
# the slot surface's x at that level) — transition stock, not a
# transition: a 45-degree blend from the new bottom edge would land on
# the gooseneck exactly at the old bottom level.
_slot_end_arc_x = tube_shell_x_half_outer - (pill_width_y / 2.0 + zone5_wall)
_skirt_drop = display_collar_half_x - (
    _slot_end_arc_x
    + math.sqrt(
        (pill_width_y / 2.0 + zone5_wall) ** 2
        - (_block_n_bottom - flavor_offset_y_from_water) ** 2
    )
)
_cradle_n_bottom = _block_n_bottom - _skirt_drop
# The cradle prisms are cut from stock reaching this far below the skirt
# bottom. Past the tip's straight the gooseneck turns away from the tip
# axis, so a prism floor struck in the tip's frame stands off the tube;
# the skirt cut, which is struck in the tube's own frame, is what gives
# the cradle its floor, and this stock is only what that cut trims.
_cradle_stock_drop = 20.0
_cradle_prism_n_bottom = _cradle_n_bottom - _cradle_stock_drop
# Local Y the skirt cut's slab reaches down to. Bounded so its inner
# radius stays well clear of the axis around bend 1, the tightest the
# gooseneck turns.
_skirt_slab_n_bottom = -25.0
# The cradle's back end ramps onto the gooseneck rather than ending
# square. In the tip's print orientation a face at angle t from the tip
# axis overhangs by 90 degrees minus t minus the tip's own tilt, so
# holding the ramp to the same max_print_overhang_rad the swept flanks
# carry fixes it at [20°](CRADLE_BACK_SLOPE).
cradle_back_slope_rad = math.pi / 2.0 - 2.0 * max_print_overhang_rad
# Ramp origin, at the skirt bottom. Set so the slope clears the cover
# plate's counterbore at the plate's own outer face: the cradle's back
# end is one unbroken slope from the plate's top down onto the tube,
# crossing the seam without stepping, and the screw stands in solid
# material on both sides of it.
cradle_back_s = (
    display_cover_screw_s + display_cover_cbore_dia / 2.0 + display_cover_boss_wall
    + (display_cover_top_n - _cradle_n_bottom) * math.tan(cradle_back_slope_rad)
)  # [68.42 mm](CRADLE_BACK_S)
# The head wall is cut from stock reaching this far back, so the ramp —
# not the prism's own square end — is what closes the cradle at every
# depth of _cradle_stock_drop. Cut short, the stock the ramp has not
# reached yet ends facing straight up-gooseneck, and the tip's print
# orientation makes that the steepest face on the part.
_cradle_prism_back_s = cradle_back_s + (
    _cradle_stock_drop * math.tan(cradle_back_slope_rad)
)


def _tip_frame():
    """(tip_end, s_hat, n_hat) in world: tip end on the water centerline,
    unit vectors up-gooseneck along the tip and out the tip's top normal."""
    ta, tb = _tan_after_bend2
    tip_end = cq.Vector(0.0, soda_faucet_tube_y - _path_p5[0], zone5_z_top + _path_p5[1])
    s_hat = cq.Vector(0.0, ta, -tb)
    n_hat = cq.Vector(0.0, tb, ta)
    return tip_end, s_hat, n_hat


def _cradle_prism(half_x: float, s0: float, s1: float, n0: float, n1: float,
                  corner_r: float = 0.0) -> cq.Workplane:
    """Tip-frame box |x| ≤ half_x, s ∈ [s0, s1], n ∈ [n0, n1], with the
    n-axis edges optionally filleted (rounded-rect footprint)."""
    tip_end, _, n_hat = _tip_frame()
    plane = cq.Plane(origin=tip_end, xDir=cq.Vector(1, 0, 0), normal=n_hat)
    sketch = cq.Sketch().push([(0.0, (s0 + s1) / 2.0)]).rect(2.0 * half_x, s1 - s0)
    if corner_r > 0.0:
        sketch = sketch.reset().vertices().fillet(corner_r)
    return (
        cq.Workplane(plane).workplane(offset=n0)
        .placeSketch(sketch)
        .extrude(n1 - n0)
    )


def _cradle_back_slope() -> cq.Workplane:
    """Everything up-gooseneck of the cradle's back ramp — the tool that
    turns a square back end into a slope onto the gooseneck. The plane
    runs through cradle_back_s at the skirt bottom and rises at
    cradle_back_slope_rad, meeting the head wall's back face at the
    collar top."""
    tip_end, s_hat, n_hat = _tip_frame()
    normal = (
        s_hat.multiply(math.cos(cradle_back_slope_rad))
        + n_hat.multiply(math.sin(cradle_back_slope_rad))
    )
    origin = (
        tip_end + s_hat.multiply(cradle_back_s) + n_hat.multiply(_cradle_n_bottom)
    )
    plane = cq.Plane(origin=origin, xDir=cq.Vector(1, 0, 0), normal=normal)
    return cq.Workplane(plane).rect(400.0, 400.0).extrude(200.0)


def _cradle_block() -> cq.Workplane:
    """Collar block: plain slab from the transition-stock bottom to just
    over the face plane, spanning the device length, with the skirt
    chamfer already cut. The chamfer applies here — before the block
    joins the gooseneck — so it can only ever remove cradle material,
    never the swept tube. The block's plan is a rectangle: the back
    ramp is what shapes its up-gooseneck end, and a plan corner rounded
    into that ramp would face up-gooseneck under the ramp's foot. The
    cavity bands carve the pocket out of this."""
    slab = _cradle_prism(
        display_collar_half_x, 0.0, display_s_top,
        _cradle_prism_n_bottom, display_cover_land_n,
    )
    return slab.cut(_skirt_chamfer())


def _display_cavity() -> cq.Workplane:
    """Pocket cut, applied after the block is unioned: PCB band (feet +
    components + board) under a housing band, both walled on all four
    edges and both clearing the device by display_cradle_clearance. The
    housing band runs past the land — above it the cavity is open sky,
    and the cover plate is what closes it; the rounded band corners are
    what stop the device's slide along the tip."""
    pcb_r = display_pcb_corner_r + display_cradle_clearance
    housing_r = display_corner_r + display_cradle_clearance
    pcb_band = _cradle_prism(
        _pcb_band_half_x, display_s_bottom, display_s_top,
        display_floor_n, _pcb_band_n_top,
        corner_r=pcb_r,
    )
    housing_band = _cradle_prism(
        _housing_band_half_x, display_s_bottom, display_s_top,
        _pcb_band_n_top, display_cover_land_n + 5.0,
        corner_r=housing_r,
    )
    return pcb_band.union(housing_band)


def _display_cover_hook_notch() -> cq.Workplane:
    """The notch in the south wall the cover plate's tongue hooks into.

    The wall between the device and the dispense end is
    display_cover_hook_half_x of straight either side of the centreline
    — the flat of the cavity's rounded end — and this takes that flat
    out over the wall's bottom two thirds, and out again over the top
    third everything up-gooseneck of display_cover_stem_s0. What is
    left is a roof: the top third, reaching display_cover_hook_lap
    further up-gooseneck than the wall under it, cantilevered off the
    end-face skin. The plate's tongue goes under it.

    The wall outboard of the notch is untouched, so the device still
    stops against full-height wall on both sides of the tongue.

    The roof's underside faces down the cradle's normal, which in the
    tip's print orientation is [35°](CRADLE_BACK_SLOPE_PEER) — the same
    the swept flanks carry. It costs the shell nothing."""
    half_x = display_cover_hook_half_x + display_cover_slip
    under = _cradle_prism(
        half_x, display_cover_hook_skin, display_s_bottom,
        display_floor_n, display_cover_hook_n1,
    )
    slot = _cradle_prism(
        half_x, display_cover_stem_s0, display_s_bottom,
        display_cover_hook_n1, display_cover_land_n + 1.0,
    )
    return under.union(slot)


def _display_cover_insert_bore() -> cq.Workplane:
    """The ruthex M3 pocket, struck down the tip's own normal from the
    land north of the device. Opening up: the cover plate's screw comes
    down the same axis into it."""
    tip_end, s_hat, n_hat = _tip_frame()
    plane = cq.Plane(origin=tip_end, xDir=cq.Vector(1, 0, 0), normal=n_hat)
    return (
        cq.Workplane(plane).workplane(offset=display_cover_land_n)
        .moveTo(0.0, display_cover_screw_s)
        .circle(display_cover_insert_dia / 2.0)
        .extrude(-display_cover_insert_depth)
    )


def _skirt_slab_sketch() -> cq.Sketch:
    """Cross-section filling the tube-frame section below the skirt
    bottom, wide enough in X to swallow the collar. X is world X the
    whole length of the sweep, so only the Y reach has to respect the
    bend radius."""
    depth = _cradle_n_bottom - _skirt_slab_n_bottom
    return (
        cq.Sketch()
        .push([(0.0, (_cradle_n_bottom + _skirt_slab_n_bottom) / 2.0)])
        .rect(4.0 * display_collar_half_x, depth)
    )


def _skirt_wedge_sketch() -> cq.Sketch:
    """Chamfer cross-section on the +X flank, toe on the fill-rect flank
    at the skirt bottom and hinge at the collar's outline on the block
    bottom. At the skirt bottom the tube's section is its fill rect, so
    the toe lands on the flank for every station of the sweep."""
    return cq.Sketch().polygon([
        (tube_shell_x_half_outer, _cradle_n_bottom),
        (display_collar_half_x, _block_n_bottom),
        (display_collar_half_x + 4.0, _block_n_bottom),
        (display_collar_half_x + 4.0, _cradle_n_bottom),
    ])


def _skirt_chamfer() -> cq.Workplane:
    """The cradle's floor and the chamfer that lands it on the gooseneck,
    both struck as sweeps in the tube's own cross-section frame so they
    track the flank around the bend. Cut in the tip's straight frame
    instead, the floor stands off the tube once the bend turns the
    section away from it and the chamfer's toe stops short of the flank,
    leaving a ribbon of collar floor in the air. The cut is applied
    before the cradle parts join the gooseneck, so it can only ever
    subtract from them."""
    floor = _sweep_along_gooseneck(_skirt_slab_sketch())
    wedge = _sweep_along_gooseneck(_skirt_wedge_sketch())
    return floor.union(wedge).union(wedge.mirror("YZ"))


def _display_head_wall() -> cq.Workplane:
    """Head wall past the display's north end — the device's axial stop,
    and the block the cover plate's insert is set into. Same bottom and
    top planes as the collar block, so the cradle reads as one
    rectangle; runs back past the screw boss and is then cut to the
    ramp, which leaves the wall's face square for its full height and
    the stock behind it a slope. Skirt chamfer cut before it joins the
    gooseneck (same rule as the block)."""
    return (
        _cradle_prism(
            display_collar_half_x, display_s_top, _cradle_prism_back_s,
            _cradle_prism_n_bottom, display_cover_land_n,
        )
        .cut(_skirt_chamfer())
        .cut(_cradle_back_slope())
    )


def _web_drop_hole(s_pos: float, dia: float) -> cq.Workplane:
    """Ø dia drop through the web at (x = 0, s = s_pos), from the pill
    cusp void up through the pocket floor."""
    tip_end, _, n_hat = _tip_frame()
    plane = cq.Plane(origin=tip_end, xDir=cq.Vector(1, 0, 0), normal=n_hat)
    return (
        cq.Workplane(plane).workplane(offset=7.0)
        .moveTo(0.0, s_pos)
        .circle(dia / 2.0)
        .extrude(display_floor_n - 7.0 + 0.5)
    )


def _display_wire_hole() -> cq.Workplane:
    """Wire drop near the cradle's top end: display wires leave the
    under-PCB cavity into the pill cusp and ride down the shell with the
    flavor tubes."""
    return _web_drop_hole(display_wire_hole_s, display_wire_hole_dia)


def _display_drain_hole() -> cq.Workplane:
    """Pocket-floor drain at the floor's low corner, edge tangent to the
    PCB cover's back: splash that gets past the housing drops into the
    pill cusp and runs out the gooseneck exit alongside the tubes."""
    return _web_drop_hole(display_drain_s, display_drain_dia)


def build_lever_clearance() -> cq.Workplane:
    """Triangular ramp wedge cut into the top of the rect column on the
    -Y (toward-user) side, where the pressed lever's taper crosses the
    rect-column top corner."""
    z_top = zone2_z_top
    z_bot = z_top - lever_ramp_depth
    x_half = lever_clearance_x_half
    return (
        _vertical_plane(-x_half)
        .polyline([
            (lever_ramp_y_min, z_bot),
            (lever_ramp_y_min, z_top),
            (lever_ramp_y_start, z_top),
        ]).close()
        .extrude(2.0 * x_half)
    )


def _tube_shell_outer_section(z_bottom: float, z_height: float) -> cq.Workplane:
    """Tube-shell outer cross-section (water slot + flavor pill + fill rect) extruded vertically over the Z range."""
    water_y_width = 2.0 * tube_shell_soda_r_outer
    water_outer = (
        _horizontal_plane(z_bottom)
        .moveTo((0.0, soda_faucet_tube_y))
        .slot2D(tube_shell_x_outer, water_y_width, angle=0)
        .extrude(z_height)
    ).unwrap()
    flavor_outer = (
        _horizontal_plane(z_bottom)
        .moveTo((0.0, flavor_tube_post_bend_y))
        .slot2D(tube_shell_x_outer, pill_width_y + 2.0 * zone5_wall, angle=0)
        .extrude(z_height)
    ).unwrap()
    fill_rect = (
        _horizontal_plane(z_bottom)
        .moveTo((0.0, (soda_faucet_tube_y + flavor_tube_post_bend_y) / 2.0))
        .rect(tube_shell_x_outer, -flavor_offset_y_from_water)
        .extrude(z_height)
    ).unwrap()
    return water_outer.union(flavor_outer).union(fill_rect)


def _tube_shell_inner_section(z_bottom: float, z_height: float) -> cq.Workplane:
    """Tube hole cross-section (water cyl + flavor pill) extruded vertically."""
    flavor_inner = (
        _horizontal_plane(z_bottom)
        .moveTo((0.0, flavor_tube_post_bend_y))
        .slot2D(pill_length_x, pill_width_y, angle=0)
        .extrude(z_height)
    ).unwrap()
    return soda_faucet_tube_cyl(z_bottom, z_height).union(flavor_inner)


# ============================================================
# PUBLIC SHELL BUILDERS
# ============================================================

def build_shell() -> cq.Workplane:
    """Faucet shell — full reference solid (un-split), all zones
    unioned, with the display cradle on the dispense tip. Split for
    printing into two pieces at the gooseneck's angular midpoint:
    build_shell_base and build_shell_tip."""
    outer_parts = [
        build_zone1_outer().val(),
        build_base_pods().val(),
        build_base_pod_front().val(),
        build_zone2_outer().val(),
        build_zone3_outer().val(),
        build_zone3_fill_outer().val(),
        build_zone4_outer().val(),
        build_zone45_outer().val(),
        _tube_shell_outer_section(zone5_z_bottom, zone5_height).val(),
        build_zone6_outer().val(),
        _cradle_block().val(),
        _display_head_wall().val(),
    ]
    outer = cq.Workplane(obj=outer_parts[0].fuse(*outer_parts[1:]))
    inner_parts = [
        build_zone1_inner_cut().val(),
        build_base_pod_holes().val(),
        build_zone2_inner_cut().val(),
        build_zone3_inner_cut().val(),
        build_zone3_fill_inner_cut().val(),
        build_zone4_inner_cut().val(),
        _tube_shell_inner_section(zone5_z_bottom, zone5_height).val(),
        build_zone6_inner_cut().val(),
        build_lever_clearance().val(),
        _display_cavity().val(),
        _display_cover_hook_notch().val(),
        _display_cover_insert_bore().val(),
        _display_wire_hole().val(),
        _display_drain_hole().val(),
    ]
    inner = cq.Workplane(obj=inner_parts[0].fuse(*inner_parts[1:]))
    return outer.cut(inner)


def build_shell_base(full_shell: cq.Workplane | None = None) -> cq.Workplane:
    """Base piece — everything below the SPLIT junction plane, with the
    last split_socket_overlap_len mm of gooseneck hollowed to a
    split_socket_wall female socket. The socket cavity is the swept
    cross-section offset inward, so its surface follows bend 2's arc and
    the tip's plug swings into it about the bend-2 axis."""
    full = full_shell if full_shell is not None else build_shell()
    below_junction = _split_plane_halfspace(
        (0.0, split_junction_y, split_junction_z), split_normal, sign=-1,
    )
    socket_cavity = _build_bend_overlap(
        _tube_shell_outer_shrunk_sketch(split_socket_shrink), side="socket",
    )
    return full.intersect(below_junction).cut(socket_cavity)


def build_shell_tip(full_shell: cq.Workplane | None = None) -> cq.Workplane:
    """Tip piece — everything above the SPLIT junction plane, carrying
    the whole display cradle, plus a male plug reaching
    split_plug_overlap_len mm back down bend 2 into the base's socket. The
    plug is the swept cross-section offset inward with the tube bores
    taken out: a closed ring, so the joint bears all the way around."""
    full = full_shell if full_shell is not None else build_shell()
    above_junction = _split_plane_halfspace(
        (0.0, split_junction_y, split_junction_z), split_normal, sign=+1,
    )
    plug_outer = _build_bend_overlap(
        _tube_shell_outer_shrunk_sketch(split_plug_shrink), side="plug",
    )
    plug = plug_outer.cut(build_zone6_inner_cut())
    return full.intersect(above_junction).union(plug)


def print_height(shape: cq.Workplane, build_rot: float) -> float:
    """Height of `shape` on the bed when built along the gooseneck tangent
    at path rotation `build_rot` — the piece's print orientation."""
    w = cq.Vector(0.0, -math.sin(build_rot), math.cos(build_rot))
    heights = [cq.Vector(*v.toTuple()).dot(w) for v in shape.val().Vertices()]
    return max(heights) - min(heights)


def main():
    out_dir = Path(__file__).resolve().parent
    full = build_shell()
    base = build_shell_base(full)
    tip = build_shell_tip(full)
    # faucet-shell.step is the TRUE assembly — the two printed pieces as
    # separate solids in their assembled positions, joint voids, seam
    # and all — not the unsplit design solid the pieces derive from.
    # Separate solids, not a union: a boolean union fuses the joint's
    # nominal-contact faces and dissolves the seam.
    assembled = cq.Assembly(name="faucet-shell")
    assembled.add(base, name="shell_base", color=C_FAUCET_BLACK)
    assembled.add(tip, name="shell_tip", color=C_FAUCET_BLACK)

    full_out = out_dir / "faucet-shell.step"
    base_out = out_dir / "faucet-shell-base.step"
    tip_out = out_dir / "faucet-shell-tip.step"
    export_assembly(assembled, str(full_out))
    for shape, out in ((base, base_out), (tip, tip_out)):
        export_assembly(one_body(shape, out.stem, C_FAUCET_BLACK), str(out))
    print(f"-> {full_out.name}")
    print(f"-> {base_out.name}")
    print(f"-> {tip_out.name}")

    variables = {
        "BORE_CLEAR": f"{bore_clearance:.4g} mm",
        "WESTBRASS_BORE_D": f"{westbrass_bore_diameter:.4g} mm",
        "WESTBRASS_OD": f"{westbrass_rect_long_y:.4g} mm",
        "WESTBRASS_RECT_LONG": f"{westbrass_rect_long_y:.4g} mm",
        "WESTBRASS_RECT_SHORT": f"{westbrass_rect_short_x:.4g} mm",
        "WESTBRASS_CYL_TOP_Z": f"{zone1_z_top:.4g} mm",
        "BORE_COVE_Z": f"{zone2_bore_z_bottom + cove_r:.4g} mm",
        "PILL_L": f"{pill_length_x:.4g} mm",
        "PILL_W": f"{pill_width_y:.4g} mm",
        "FLAVOR_TUBE_OD": f"{flavor_tube_od:.4g} mm",
        "WESTBRASS_RECT_LONG_HALF": f"{westbrass_rect_long_y / 2.0:.4g} mm",
        "LEVER_REST_TOP_Z": f"{zone2_z_top + 13:.4g} mm",
        "FLAVOR_TUBE_Y": f"{flavor_pill_center[1]:.4g} mm",
        "FLAVOR_PILL_Y_MINUS": f"{flavor_pill_y_minus_edge:.4g} mm",
        "BASE_POD_FRONT_CENTER_Y": f"{base_pod_front_center_y:.4g} mm",
        "SHELL_OUTER_R": f"{shell_outer_r:.4g} mm",
        "SODA_FAUCET_HOLE_D": f"{soda_faucet_hole_diameter:.4g} mm",
        "WALL_MIN": f"{wall_thickness_min:.4g} mm",
        "ZONE1_HEIGHT": f"{zone1_height:.4g} mm",
        "ZONE2_HEIGHT": f"{zone2_height:.4g} mm",
        "ZONE4_HEIGHT": f"{zone4_height:.4g} mm",
        "ZONE5_HEIGHT": f"{zone5_height:.4g} mm",
        "ZONE5_WALL": f"{zone5_wall:.4g} mm",
        "WESTBRASS_BORE_FARTHEST": f"{_westbrass_bore_farthest_from_shell_center:.4g} mm",
        "PILL_FARTHEST": f"{_pill_farthest_from_shell_center:.4g} mm",
        "WESTBRASS_BORE_RECT_LONG": f"{westbrass_bore_rect_long_y:.4g} mm",
        "WESTBRASS_BORE_RECT_SHORT": f"{westbrass_bore_rect_short_x:.4g} mm",
        "ZONE2_BORE_Z_BOTTOM": f"{zone2_bore_z_bottom:.4g} mm",
        "SHELL_OUTER_LIP": f"{shell_outer_lip:.4g} mm",
        "ZONE1_OUTER_Z_TOP": f"{zone1_outer_z_top:.4g} mm",
        "LEVER_CLEAR_X_HALF": f"{lever_clearance_x_half:.4g} mm",
        "SHELL_RECT_X_HALF": f"{shell_rect_x_half:.4g} mm",
        "SHELL_RECT_Y_MAX": f"{shell_rect_y_max:.4g} mm",
        "SHELL_RECT_Y_MIN": f"{shell_rect_y_min:.4g} mm",
        "BORE_Y_AT_LEVER_X": f"{_bore_y_at_lever_x:.4g} mm",
        "LEVER_RAMP_Y_START": f"{lever_ramp_y_start:.4g} mm",
        "ZONE3_Z_BOTTOM": f"{zone3_z_bottom:.4g} mm",
        "WING_INNER_X": f"{wing_inner_x:.4g} mm",
        "SHELL_ARCH_BORE_INNER_X": f"{shell_arch_bore_inner_x:.4g} mm",
        "SHELL_ARCH_BORE_OUTER_X": f"{shell_arch_bore_outer_x:.4g} mm",
        "SHELL_ARCH_BORE_Z_FOOT_TOP": f"{shell_arch_bore_z_foot_top:.4g} mm",
        "SHELL_ARCH_BORE_Z_PEAK": f"{shell_arch_bore_z_peak:.4g} mm",
        "SHELL_ARCH_Z_FOOT_TOP": f"{shell_arch_z_foot_top:.4g} mm",
        "SHELL_ARCH_Z_PEAK": f"{shell_arch_z_peak:.4g} mm",
        "SODA_FAUCET_TUBE_OD": f"{soda_faucet_tube_od:.4g} mm",
        "SODA_FAUCET_TUBE_Y": f"{soda_faucet_tube_y:.4g} mm",
        "TUBE_SHELL_SODA_R": f"{tube_shell_soda_r_outer:.4g} mm",
        "FLAVOR_POST_BEND_Y": f"{flavor_tube_post_bend_y:.4g} mm",
        "FILL_Y_MIN": f"{fill_y_min:.4g} mm",
        "FILL_X_THICKNESS": f"{2.0 * wing_inner_x:.4g} mm",
        "PILL_STRAIGHT_INNER": f"{pill_length_x - pill_width_y:.4g} mm",
        "FLAVOR_OFFSET_Y": f"{flavor_offset_y_from_water:.4g} mm",
        "ZONE5_Z_BOTTOM": f"{zone5_z_bottom:.4g} mm",
        "ZONE5_Z_TOP": f"{zone5_z_top:.4g} mm",
        "GN_BEND1_Z_MID": f"{gn_bend1_z_mid:.4g} mm",
        "GN_BEND1_Z_START": f"{gn_bend1_z_start:.4g} mm",
        "GN_BEND2_SWEEP_DEG": f"{math.degrees(gn_bend2_sweep_rad):.0f}°",
        "GN_TOTAL_ROT": f"{math.degrees(_path_total_rot):.0f}°",
        "SPLIT_JUNCTION_ROT": f"{math.degrees(split_junction_rot):.0f}°",
        "SPLIT_JUNCTION_Y": f"{split_junction_y:.4g} mm",
        "SPLIT_JUNCTION_Z": f"{split_junction_z:.4g} mm",
        "SPLIT_OVERLAP": f"{split_socket_overlap_len:.4g} mm",
        "SPLIT_SOCKET_WALL": f"{split_socket_wall:.4g} mm",
        "SPLIT_SLIP": f"{split_slip:.4g} mm",
        "PRINT_TILT": f"{math.degrees(print_base_tilt_rad):.0f}°",
        "MAX_PRINT_OVERHANG": f"{math.degrees(max_print_overhang_rad):.0f}°",
        "CRADLE_BACK_SLOPE": f"{math.degrees(cradle_back_slope_rad):.0f}°",
        "CRADLE_BACK_S": f"{cradle_back_s:.4g} mm",
        "BASE_PRINT_HEIGHT": f"{print_height(base, print_base_build_rot):.1f} mm",
        "TIP_PRINT_HEIGHT": f"{print_height(tip, print_tip_build_rot):.1f} mm",
        "BACK_ARCH_DY": f"{_back_arch_dy:.4g} mm",
        "Z5_Y_MIN": f"{_z5_y_min:.4g} mm",
        "ZONE45_Z_TOP": f"{zone45_z_top:.4g} mm",
        "ZONE45_Z_BOT_FRONT": f"{zone45_z_bottom_at_front:.4g} mm",
    }
    substitute_md(
        out_dir / "ASSEMBLY.md",
        variables=variables,
    )
    print("-> ASSEMBLY.md")
    substitute_md(
        out_dir / "MATERIAL.md",
        variables=variables,
    )
    print("-> MATERIAL.md")
    substitute_py_comments(
        Path(__file__),
        variables=variables,
    )
    print(f"-> {Path(__file__).name} (self)")

    # Pinned dimensions living in the shared interface helper's prose.
    interface_variables = {
        "FLAVOR_TUBE_X_OFFSET": f"{_faucet_interface.flavor_tube_x_offset:.4g} mm",
        "FLAVOR_TUBE_HOLE_DIA": f"{_faucet_interface.flavor_tube_hole_dia:.4g} mm",
        "PILL_LENGTH_X": f"{_faucet_interface.pill_length_x:.4g} mm",
        "PILL_WIDTH_Y": f"{_faucet_interface.pill_width_y:.4g} mm",
        "FLAVOR_TUBE_DEPTH": f"{_faucet_interface.flavor_tube_depth:.5g} mm",
        "DISPLAY_HOUSING_OVERHANG": (
            f"{(_faucet_interface.display_housing_width - _faucet_interface.display_pcb_width) / 2.0:.4g} mm"
        ),
        "DISPLAY_PCB_BOTTOM_Z": f"{_faucet_interface.display_pcb_bottom_z:.4g} mm",
        "DISPLAY_PCB_TOP_Z": f"{_faucet_interface.display_pcb_top_z:.4g} mm",
    }
    substitute_py_comments(
        Path(_faucet_interface.__file__),
        variables=interface_variables,
    )
    print(f"-> {Path(_faucet_interface.__file__).name} (interface)")


if __name__ == "__main__":
    main()
