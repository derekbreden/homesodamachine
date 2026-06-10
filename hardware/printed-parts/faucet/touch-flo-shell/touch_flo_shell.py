"""Touch-Flo shell — printed shroud that wraps the harvested faucet
body, the flavor tubes, and the lever swing volume. Sits on top of
the touch-flo-mounting-plate. The dispense tip carries the cradle for
the flavor display (DISPLAY CRADLE section).

Frame: world +Z is height (up), world ±X is lateral (symmetric across
the X=0 plane), world -Y is forward (dispense direction — the gooseneck
arcs toward -Y, where the user's glass sits). The body's threaded shank
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
sys.path.insert(0, str(_here.parent.parent))  # for _touch_flo_interface
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
from _cadq_export import export_step
from _touch_flo_interface import (
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


# ZONE 1 — first [13 mm](ZONE1_HEIGHT); body is a full ⌀[31.5 mm](BODY_OD) cylinder here

zone1_z_bottom = 0.0
zone1_z_top = 13.0
zone1_height = zone1_z_top - zone1_z_bottom  # [13 mm](ZONE1_HEIGHT)

bore_clearance = 0.25  # mm per side

# Body bore — [32 mm](BODY_BORE_D); body OD [31.5 mm](BODY_OD).
body_bore_diameter = 31.5 + 2.0 * bore_clearance
body_bore_x = 0.0
body_bore_y = 0.0

# Flavor-tube pill — 1/4" OD LLDPE tubes (6.35 mm OD), tangent to the
# body's +Y face (Y=+15.75) and tangent to each other at X=0.
# [13.4 mm](PILL_L) long axis (X), [7.05 mm](PILL_W) short axis (Y).
flavor_pill_center = (0.0, +flavor_tube_depth)

# [14.53 mm](FLAVOR_PILL_Y_MINUS) — flat -Y edge of the flavor pill
# cutout in zones 1-4, on the body-bore +Y wall at the cutout's X corners.
flavor_pill_y_minus_edge = min(
    +flavor_tube_depth - pill_width_y / 2.0,
    +math.sqrt((body_bore_diameter / 2.0) ** 2 - (pill_length_x / 2.0) ** 2),
)


# SHELL OUTER
wall_thickness_min = 3.0
_body_bore_farthest_from_shell_center = (
    (shell_center_y - body_bore_y) + body_bore_diameter / 2.0
)  # = [19.18 mm](BODY_BORE_FARTHEST)
_pill_farthest_from_shell_center = (
    (+flavor_tube_depth + pill_width_y / 2.0) - shell_center_y
)  # = [19.27 mm](PILL_FARTHEST)
# [22.27 mm](SHELL_OUTER_R) outer-cylinder radius.
shell_outer_r = (
    max(_body_bore_farthest_from_shell_center, _pill_farthest_from_shell_center)
    + wall_thickness_min
)


# ZONE 2

zone2_z_bottom = zone1_z_top  # [13 mm](BODY_CYL_TOP_Z)
zone2_z_top = 39.0  # body plateau
zone2_height = zone2_z_top - zone2_z_bottom  # [26 mm](ZONE2_HEIGHT)

# Body rectangle dimensions
body_rect_long_y = 31.5  # depth axis
body_rect_short_x = 17.0  # lateral axis

body_bore_rect_long_y = body_rect_long_y + 2.0 * bore_clearance  # [32 mm](BODY_BORE_RECT_LONG)
body_bore_rect_short_x = body_rect_short_x + 2.0 * bore_clearance  # [17.5 mm](BODY_BORE_RECT_SHORT)

# Cove transition fillet — matches the body's transition_fillet_r.
cove_r = 6.0

zone2_bore_z_bottom = zone1_z_top + bore_clearance  # [13.25 mm](ZONE2_BORE_Z_BOTTOM)

# [3 mm](WALL_MIN) cylindrical shell wall above the body cyl top before the cove.
shell_outer_lip = wall_thickness_min + bore_clearance  # [3.25 mm](SHELL_OUTER_LIP)
zone1_outer_z_top = zone1_z_top + shell_outer_lip  # [16.25 mm](ZONE1_OUTER_Z_TOP)
zone2_outer_z_bottom = zone1_outer_z_top  # [16.25 mm](ZONE1_OUTER_Z_TOP)


# BASE PODS — two lateral pods on the +-X sides of the foot, each hosting one
# plate-to-shell screw boss. Mechanism: heat-set insert in the shell, screw up
# from under the plate (head recessed in the plate bottom) through the plate
# boss, clamping the plate up into the shell. These two lateral anchors are the
# ENTIRE shell-to-body retention — the shank nut only clamps the metal body to
# the plate, not the shell.
#
# Nested fastener chain (BNUOK M3 SHCS 304 SS, head ~5.43 mm measured; ruthex
# M3 insert). Counterbore + boss are plate-side; the boss hole, insert pocket,
# and pod live in the shell — but the whole chain is derived here so wall
# thickness is one knob.
base_pod_counterbore_dia = 5.55     # M3 SHCS head ~5.43 measured + ~0.1 clearance
base_pod_shank_dia = 3.9            # M3 shank clearance — plate boss bore up to the insert
base_pod_wall = 3.0                 # wall added at each step (plate boss wall = shell wall)
base_pod_slip = 0.10                # boss-to-hole diametral slip fit
base_pod_boss_dia = base_pod_counterbore_dia + 2.0 * base_pod_wall  # plate boss OD
base_pod_hole_dia = base_pod_boss_dia + base_pod_slip               # shell pocket
base_pod_radius = base_pod_hole_dia / 2.0 + base_pod_wall           # pod outer
base_pod_center_y = shell_center_y  # foot-circle (and plate) center line, +Y
# Center slides outward as the pod grows: placed so the pod's inner edge sits
# tangent to the body bore (a base_pod_wall-thick wall from the pocket to the bore).
base_pod_center_x = math.sqrt(
    (body_bore_diameter / 2.0 + base_pod_radius) ** 2 - base_pod_center_y ** 2
)
# Third pod on the front (−Y) centerline — the anchor the two lateral bosses
# can't be: both sit on the X-axis, so they give no front/back couple. Same
# radius and same bore tangency as the laterals (inner edge touches the body
# bore, base_pod_wall from the pocket to the bore), straight in front.
base_pod_front_center_x = 0.0
base_pod_front_center_y = -(body_bore_diameter / 2.0 + base_pod_radius)  # -24.825
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
)  # 5.25 mm = 4 mm insert engagement + 1.25 mm relief


# LEVER SWING CLEARANCE — chamfer wedge cut into the top -Y corner of
# the rect column, where the pressed lever's taper passes through.

lever_x_half = 6.5
lever_clearance_x_half = lever_x_half + bore_clearance  # [6.75 mm](LEVER_CLEAR_X_HALF)
lever_ramp_depth = 1.0
tangent_overshoot = 0.002

shell_rect_y_half = shell_outer_r  # [22.27 mm](SHELL_OUTER_R)
shell_rect_x_half = body_bore_rect_short_x / 2.0 + wall_thickness_min  # [11.75 mm](SHELL_RECT_X_HALF)
shell_rect_y_width = 2.0 * shell_rect_y_half
shell_rect_x_width = 2.0 * shell_rect_x_half
shell_rect_y_max = shell_center_y + shell_rect_y_half  # [25.45 mm](SHELL_RECT_Y_MAX) (toward back)
shell_rect_y_min = shell_center_y - shell_rect_y_half  # [-19.1 mm](SHELL_RECT_Y_MIN) (toward user)

lever_ramp_y_min = shell_center_y - shell_outer_r  # [-19.1 mm](SHELL_RECT_Y_MIN), outer rect face -Y side
_bore_y_at_lever_x = math.sqrt(
    (body_bore_diameter / 2.0) ** 2 - lever_clearance_x_half ** 2
)  # ≈ [14.51 mm](BORE_Y_AT_LEVER_X) — bore-cyl tangent at the cut's X half-span
lever_ramp_y_start = -(_bore_y_at_lever_x + tangent_overshoot)  # ≈ [-14.51 mm](LEVER_RAMP_Y_START)


# ZONE 3 — arch wraps (two wings at ±X)
#
# Body arches: 1.5 mm ridges at X = ±7.75, full Y width (±15.75); profile
# in (Y, Z) is a 2 mm foot from Z=39→41 then a 3-point arc through
# (∓15.75, 41) and (0, 46).
# Plateau between the arches (X ∈ ±[6.75 mm](WING_INNER_X)) is open.

zone3_z_bottom = zone2_z_top  # [39 mm](ZONE3_Z_BOTTOM)

arch_z_base = 41.0  # body foot top
arch_z_peak = 46.0  # body arc peak
body_arch_inner_x = 7.0
body_arch_outer_x = 8.5

shell_arch_bore_inner_x = body_arch_inner_x - bore_clearance  # [6.75 mm](SHELL_ARCH_BORE_INNER_X)
shell_arch_bore_outer_x = body_arch_outer_x + bore_clearance  # [8.75 mm](SHELL_ARCH_BORE_OUTER_X)
shell_arch_bore_z_foot_top = arch_z_base + bore_clearance  # [41.25 mm](SHELL_ARCH_BORE_Z_FOOT_TOP)
shell_arch_bore_z_peak = arch_z_peak + bore_clearance  # [46.25 mm](SHELL_ARCH_BORE_Z_PEAK)

shell_arch_z_foot_top = arch_z_base + shell_outer_lip  # [44.25 mm](SHELL_ARCH_Z_FOOT_TOP)
shell_arch_z_peak = arch_z_peak + shell_outer_lip  # [49.25 mm](SHELL_ARCH_Z_PEAK)
wing_inner_x = shell_arch_bore_inner_x  # [6.75 mm](WING_INNER_X)
wing_outer_x = shell_rect_x_half  # [11.75 mm](SHELL_RECT_X_HALF)

# ZONE 3 — plateau fill (between the wings, Y ≥ fill_y_min).
water_tube_y = +8.875
# 3/8" LLDPE water tube, internal to the faucet head — sealed in the
# body's 10.0 mm port via a printed TPU bushing (see
# ../touch-flo-tpu-o-ring/).
water_tube_od = 0.375 * 25.4  # [9.525 mm](WATER_TUBE_OD)
# [10.22 mm](WATER_HOLE_D) water bore.
water_hole_diameter = water_tube_od + 2.0 * bore_clearance + 0.20

# 1/4" LLDPE flavor tubes, tangent to the water tube at the dispense
# point and sitting behind it (more +Y).
flavor_tube_post_bend_y = water_tube_y + math.sqrt(
    (water_tube_od / 2.0 + flavor_tube_od / 2.0) ** 2
    - flavor_tube_x_offset ** 2
)  # ≈ [16.15 mm](FLAVOR_POST_BEND_Y)

fill_y_min = +10.46  # back third of water tube (Y ≥ [10.46 mm](FILL_Y_MIN))


# ZONE 4 — rect column above the arch (water tube + flavor pill cutouts).
zone4_z_bottom = shell_arch_z_foot_top  # [44.25 mm](SHELL_ARCH_Z_FOOT_TOP)
# Clears the pressed-lever head corner (Y=+6.78, Z=54.024), which sits
# inside zone 5's water-circle outline (Y=+[8.875 mm](WATER_TUBE_Y),
# R=[9.112 mm](TUBE_SHELL_WATER_R)); zone 5's bottom is above it.
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
tube_shell_water_r_outer = water_hole_diameter / 2.0 + zone5_wall   # [9.112 mm](TUBE_SHELL_WATER_R)
tube_shell_pill_x_half_outer = pill_length_x / 2.0 + zone5_wall
tube_shell_x_half_outer = max(tube_shell_water_r_outer, tube_shell_pill_x_half_outer)
tube_shell_x_outer = 2.0 * tube_shell_x_half_outer
# Water → flavor offset along world Y; positive — flavor sits behind water.
flavor_offset_y_from_water = flavor_tube_post_bend_y - water_tube_y  # ≈ [7.275 mm](FLAVOR_OFFSET_Y)


# ZONE 6 — gooseneck wrapper around the bent dispense tubes: zone 5's
# cross-section swept along a bent path above the lever-swing envelope.
# Mirrors constants in `faucet-assembly`.

gn_bend1_r = 30.0
gn_bend2_r = 40.0
gn_bend1_sweep_rad = math.radians(30.0)
gn_bend2_sweep_rad = math.radians(110.0)
# 35 mm above the lever rest top (at zone2_z_top + 13 = 52).
gn_bend1_z_mid = zone2_z_top + 48.0  # [87 mm](GN_BEND1_Z_MID)
gn_bend1_z_start = (
    gn_bend1_z_mid
    - gn_bend1_r * math.sin(gn_bend1_sweep_rad / 2.0)
)  # ≈ [79.24 mm](GN_BEND1_Z_START)
gn_mid_straight_len = 115.0
gn_tip_straight_len = 25.0


# SPLITS — the shell prints in THREE pieces, mating at two 20 mm slip-fit
# joints along the gooseneck:
#   SPLIT A: angled-spout ↔ upper-bend, at end of mid-straight / start
#     of bend 2. Mating faces perpendicular to the spout tangent.
#   SPLIT B: upper-bend ↔ dispense-tip, at end of bend 2 / start of tip.
#     Bend 2 is a [110°](GN_BEND2_SWEEP_DEG) arc at R=gn_bend2_r; the 20 mm overlap
#     follows the arc.
# Fit: male OD ≡ female ID in CAD; slip clearance comes from print tolerance.

# Per-joint, per-side overlap depth (mm along spout / arc) and wall (mm),
# mapped onto a `shrink` (inward offset of the outer cross-section):
#   socket shrink = socket_wall
#   plug   shrink = zone5_wall − plug_wall
split_a_socket_overlap_len = 20.0
split_a_plug_overlap_len = 19.0
split_a_socket_wall = 2.0
split_a_plug_wall = 1.95

split_b_socket_overlap_len = 20.0
split_b_plug_overlap_len = 18.0
split_b_socket_wall = 2.0
split_b_plug_wall = 1.92

split_a_socket_shrink = split_a_socket_wall
split_a_plug_shrink = zone5_wall - split_a_plug_wall
split_b_socket_shrink = split_b_socket_wall
split_b_plug_shrink = zone5_wall - split_b_plug_wall

# Mid-straight tangent in path-local (a, b) — points up the spout toward bend 2.
_mid_tan_yz = (math.sin(gn_bend1_sweep_rad), math.cos(gn_bend1_sweep_rad))

# SPLIT A cutting-plane normal in world (X, Y, Z), perpendicular to the tangent.
split_normal = (0.0, -_mid_tan_yz[0], _mid_tan_yz[1])

# End of mid-straight (= SPLIT A junction) in world coords.
_bend1_end_yz = (
    gn_bend1_r * (1.0 - math.cos(gn_bend1_sweep_rad)),
    (gn_bend1_z_start - zone5_z_top) + gn_bend1_r * math.sin(gn_bend1_sweep_rad),
)
split_junction_y = water_tube_y - _bend1_end_yz[0] - gn_mid_straight_len * _mid_tan_yz[0]
split_junction_z = zone5_z_top + _bend1_end_yz[1] + gn_mid_straight_len * _mid_tan_yz[1]

# Bottom of SPLIT A's overlap zone, per side (socket = female cavity;
# plug = male tongue), at asymmetric depths.
split_a_socket_overlap_y = split_junction_y + split_a_socket_overlap_len * _mid_tan_yz[0]
split_a_socket_overlap_z = split_junction_z - split_a_socket_overlap_len * _mid_tan_yz[1]
split_a_plug_overlap_y = split_junction_y + split_a_plug_overlap_len * _mid_tan_yz[0]
split_a_plug_overlap_z = split_junction_z - split_a_plug_overlap_len * _mid_tan_yz[1]


# SPLIT B geometry — bend↔tip joint.
#
# All `_path_*` constants below are in path-local 2D coords: local axes
# (a, b) map to world (-Y, +Z); X=0, origin at world (0, water_tube_y,
# zone5_z_top).

# Bend-2 sub-arc covering the last overlap_len mm of bend 2 — separate
# arcs for the female socket and the male plug.
split_b_socket_angle_rad = split_b_socket_overlap_len / gn_bend2_r
split_b_plug_angle_rad = split_b_plug_overlap_len / gn_bend2_r

# Cumulative path rotations from the +Z origin tangent.
_path_total_rot = gn_bend1_sweep_rad + gn_bend2_sweep_rad  # rotation at end of bend 2
_path_socket_start_rot = _path_total_rot - split_b_socket_angle_rad
_path_socket_mid_rot = _path_total_rot - split_b_socket_angle_rad / 2.0
_path_plug_start_rot = _path_total_rot - split_b_plug_angle_rad
_path_plug_mid_rot = _path_total_rot - split_b_plug_angle_rad / 2.0

# Tangent unit-vectors in path-local (a, b).
_tan_after_bend1 = (math.sin(gn_bend1_sweep_rad), math.cos(gn_bend1_sweep_rad))
_tan_after_bend2 = (math.sin(_path_total_rot), math.cos(_path_total_rot))
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
_path_p3 = (  # end of mid-straight / start of bend 2 (= SPLIT A junction)
    _path_p2[0] + gn_mid_straight_len * _tan_after_bend1[0],
    _path_p2[1] + gn_mid_straight_len * _tan_after_bend1[1],
)
# Bend-2 arc center.
_path_center_bend2 = (
    _path_p3[0] + gn_bend2_r * math.cos(gn_bend1_sweep_rad),
    _path_p3[1] - gn_bend2_r * math.sin(gn_bend1_sweep_rad),
)
_path_p4 = (  # end of bend 2 / start of tip (= SPLIT B junction)
    _path_center_bend2[0] - gn_bend2_r * math.cos(_path_total_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_total_rot),
)
_path_socket_start = (  # bend-2 point split_b_socket_overlap_len arc-length before p4
    _path_center_bend2[0] - gn_bend2_r * math.cos(_path_socket_start_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_socket_start_rot),
)
_path_socket_mid = (  # midpoint of the female socket sub-arc
    _path_center_bend2[0] - gn_bend2_r * math.cos(_path_socket_mid_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_socket_mid_rot),
)
_path_plug_start = (  # bend-2 point split_b_plug_overlap_len arc-length before p4
    _path_center_bend2[0] - gn_bend2_r * math.cos(_path_plug_start_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_plug_start_rot),
)
_path_plug_mid = (  # midpoint of the male plug sub-arc
    _path_center_bend2[0] - gn_bend2_r * math.cos(_path_plug_mid_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_plug_mid_rot),
)
_path_p5 = (  # end of tip
    _path_p4[0] + gn_tip_straight_len * _tan_after_bend2[0],
    _path_p4[1] + gn_tip_straight_len * _tan_after_bend2[1],
)

# SPLIT B mating-plane geometry in world coords.
split_b_junction_y = water_tube_y - _path_p4[0]
split_b_junction_z = zone5_z_top + _path_p4[1]
split_b_socket_overlap_y = water_tube_y - _path_socket_start[0]
split_b_socket_overlap_z = zone5_z_top + _path_socket_start[1]
split_b_plug_overlap_y = water_tube_y - _path_plug_start[0]
split_b_plug_overlap_z = zone5_z_top + _path_plug_start[1]


# ZONE 3 OUTER ARCH — single circular arc from the wing bottom
# (zone3_z_bottom at the -Y end) up to zone4_z_top at Y=fill_y_min,
# tangent-horizontal at the high end. Center is directly below the high end.
_back_arch_dy = fill_y_min - shell_rect_y_min  # [29.56 mm](BACK_ARCH_DY) (positive depth span)
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

# Zone 5's tube-shell Y extents at X=0: water tube on -Y, flavor pill on +Y.
_z5_y_min = water_tube_y - tube_shell_water_r_outer  # ≈ [-0.2375 mm](Z5_Y_MIN)
_z5_y_max = flavor_tube_post_bend_y + (pill_width_y + 2.0 * zone5_wall) / 2.0

# Zone 4.5 Y extents — back edge follows the rect column; front edge
# matched-margin from zone 5.
zone45_front_y = _z5_y_min - (shell_rect_y_max - _z5_y_max)

# Top sits 3 mm above zone 4's top on the back side (lid sits flat on
# zone 4 top). The front bottom follows the back-arch curve down to
# ≈ Z=[55.04 mm](ZONE45_Z_BOT_FRONT).
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


def water_tube_cyl(z_bottom: float, z_height: float) -> cq.Workplane:
    """Water-tube bore cylinder (R = water_hole_diameter/2 at (0, water_tube_y)) over the Z range."""
    return (
        _horizontal_plane(z_bottom)
        .moveTo((0.0, water_tube_y))
        .circle(water_hole_diameter / 2.0)
        .extrude(z_height)
    ).unwrap()


def body_bore_cyl(z_bottom: float, z_height: float) -> cq.Workplane:
    """Body bore cylinder (R = body_bore_diameter/2 at origin) over the Z range."""
    return (
        _horizontal_plane(z_bottom)
        .moveTo((body_bore_x, body_bore_y))
        .circle(body_bore_diameter / 2.0)
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
    body_bore = body_bore_cyl(zone1_z_bottom, zone2_bore_z_bottom - zone1_z_bottom)
    pill = _flavor_pill_flat_y_minus(zone1_z_bottom, zone1_height)
    return body_bore.union(pill)


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
    yet. Unioned into the shell outer before the inner cuts, so the body bore
    trims any inboard material."""
    return _base_pod_teardrops(base_pod_z_bottom, base_pod_z_top - base_pod_z_bottom)


def _base_pod_front(z_bottom: float, z_height: float) -> cq.Workplane:
    """The front (−Y) pod solid over a Z range — the foam-shell boss idiom (see
    cold-core/_outer_shell.build_attachment_bosses): a ⌀(2*base_pod_radius)
    cylinder over the boss, plus a flat-sided web box of the same width running
    inboard (+Y) to fuse into the foot wall. A 'D': round front, flat sides
    (parallel to Y) into the wall, tangent to the body bore."""
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
    (mirrors the body's build_transition_cove)."""
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
    """Zone 2 inner — body cross-section (rect + cove + cyl clip) at
    bore_clearance per side, plus the flavor-tube pill through."""
    bore_zone2_height = zone2_z_top - zone2_bore_z_bottom
    bore = _rect_cove_cyl(
        body_bore_x, body_bore_y,
        body_bore_rect_short_x, body_bore_rect_long_y,
        zone2_bore_z_bottom, zone2_z_top,
        body_bore_cyl(zone2_bore_z_bottom, bore_zone2_height),
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
    """Two arch wings at ±X wrapping the body's arch ridges."""
    wing_thickness = wing_outer_x - wing_inner_x
    wings = _arch_extrude(+wing_inner_x, +wing_thickness).union(
        _arch_extrude(-wing_outer_x, +wing_thickness)
    )
    return wings.intersect(shell_outer_cyl(zone3_z_bottom, zone4_z_top - zone3_z_bottom))


def build_zone3_inner_cut() -> cq.Workplane:
    """Two arch bores at ±X mirroring the body arches with bore_clearance."""
    bore_y_oversize = body_bore_diameter / 2.0 + 2.0

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
    return bores.intersect(body_bore_cyl(zone3_z_bottom, shell_arch_bore_z_peak - zone3_z_bottom))


def build_zone3_fill_outer() -> cq.Workplane:
    """Plateau fill behind fill_y_min — the wings' arch profile extruded
    across the plateau X range, body bore column cut away."""
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
        .cut(body_bore_cyl(zone3_z_bottom, z_height))
    )


def build_zone3_fill_inner_cut() -> cq.Workplane:
    """Tube cutouts through the plateau fill: water tube + straight flavor
    pill at flavor_pill_center. The bend lives in the tube shell above."""
    z_height = shell_arch_z_peak - zone3_z_bottom
    water_hole = water_tube_cyl(zone3_z_bottom, z_height)
    flavor_pill = _flavor_pill_flat_y_minus(zone3_z_bottom, z_height)
    return water_hole.union(flavor_pill)


def build_zone4_outer() -> cq.Workplane:
    """Zone 4 outer — rect ∩ outer cyl at Y ≥ fill_y_min, body bore column cut away."""
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
        .cut(body_bore_cyl(zone4_z_bottom, zone4_height))
    )


def build_zone4_inner_cut() -> cq.Workplane:
    """Tube cavity: water-tube cyl + straight flavor pill. Straight cuts
    only — the flavor bend lives in the tube shell above."""
    water_inner = water_tube_cyl(zone4_z_bottom, zone4_height)
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
    (0, water_tube_y, zone5_z_top)."""
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
    """Tube-shell outer cross-section, centered on the water tube: one
    connected region of water slot + flavor pill (offset -Y) + fill rect."""
    water_y_width = 2.0 * tube_shell_water_r_outer
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
        .circle(water_hole_diameter / 2.0)
        .push([(0, flavor_offset_y_from_water)])
        .slot(pill_straight, pill_width_y, angle=0, mode="a")
        .clean()
    )


def _sweep_along_gooseneck(sketch: cq.Sketch) -> cq.Workplane:
    """`sketch` swept along the gooseneck path, placed at the zone-5 seam
    (0, water_tube_y, zone5_z_top)."""
    profile = cq.Workplane(_profile_plane).placeSketch(sketch)
    swept = profile.sweep(_gooseneck_path_at_origin(), transition="right")
    return swept.translate((0, water_tube_y, zone5_z_top))


def build_zone6_outer() -> cq.Workplane:
    return _sweep_along_gooseneck(_tube_shell_outer_sketch())


def build_zone6_inner_cut() -> cq.Workplane:
    return _sweep_along_gooseneck(_tube_shell_inner_sketch())


def _tube_shell_outer_shrunk_sketch(shrink: float) -> cq.Sketch:
    """_tube_shell_outer_sketch offset inward by `shrink` mm (centers fixed)."""
    water_y_width = 2.0 * (tube_shell_water_r_outer - shrink)
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


def _split_overlap_slab(overlap_y: float, overlap_z: float) -> cq.Workplane:
    """Slab between the overlap plane and the junction plane, both perpendicular to the angled-spout tangent."""
    above_overlap = _split_plane_halfspace(
        (0.0, overlap_y, overlap_z), split_normal, sign=+1,
    )
    below_junction = _split_plane_halfspace(
        (0.0, split_junction_y, split_junction_z), split_normal, sign=-1,
    )
    return above_overlap.intersect(below_junction)


def _sweep_segment_in_path_local(
    start_yz: tuple,
    tangent_yz: tuple,
    path_workplane: cq.Workplane,
    sketch: cq.Sketch,
) -> cq.Workplane:
    """`sketch` swept along `path_workplane`, profile perpendicular to
    `tangent_yz` at `start_yz` (path-local 2D on _path_plane), placed at
    world (0, water_tube_y, zone5_z_top)."""
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
    return swept.translate((0, water_tube_y, zone5_z_top))


def _tip_subpath() -> cq.Workplane:
    """Dispense-tip straight path (_path_p4 → _path_p5) in path-local (a, b)."""
    return (
        cq.Workplane(_path_plane)
        .moveTo(*_path_p4)
        .lineTo(*_path_p5)
    )


def _bend_overlap_subarc(start_yz: tuple, mid_yz: tuple) -> cq.Workplane:
    """Bend-2 sub-arc from `start_yz` through `mid_yz` to `_path_p4` (SPLIT B junction), path-local (a, b)."""
    return (
        cq.Workplane(_path_plane)
        .moveTo(*start_yz)
        .threePointArc(mid_yz, _path_p4)
    )


def _build_tip_section(sketch: cq.Sketch) -> cq.Workplane:
    """`sketch` swept along the dispense-tip path."""
    return _sweep_segment_in_path_local(
        _path_p4, _tan_after_bend2, _tip_subpath(), sketch,
    )


def _build_bend_overlap(sketch: cq.Sketch, *, side: str) -> cq.Workplane:
    """`sketch` swept along the last split_b_<side>_overlap_len mm of
    bend 2. `side` "socket" (longer) or "plug" (shorter)."""
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
# The flavor display lies along the tip, screen out the top skin, lower
# edge flush with the tip end. Its bounding back (the metal feet under
# the PCB) sinks display_pocket_inset into the zone5_wall wall above the
# flavor pill, leaving display_web_over_pill of web over the pill bore.
#
# Tip frame: s = distance up-spout from the tip end plane along the tip
# axis; n = distance from the water-tube centerline along the tip's top
# normal; x = world X. The device sits display_line_width up the tip —
# behind the PCB cover — occupying s ∈ [end wall, end wall +
# housing_length], n ∈ [floor, floor + total_depth].
#
# The cradle parts at the SPLIT B junction plane: the tip piece carries
# the pocket's straight-zone portion and the plug; the bend piece
# carries everything beyond the junction — the cradle walls, their
# below-floor flank pads, and the head wall closing the cradle's top
# end — and presses the display in as the arc-slide joint closes.
# Through the joint's overlap the pocket floor is the tip piece's tube
# wall (the plug's top, shaved flush by the cavity); the bend piece
# carries no floor there. The cradle never collides with the plug
# during the slide: the walls and pads sit laterally outside it, and
# the bend piece's material at the plug's width stays outside the
# socket surface — the joint's own fit is the slide clearance.
#
# Retention: nothing overhangs the display face — the walls and head
# wall all stop just over the face plane. Axially the device's rounded
# corners bear on the cavity's rounded corners (open end) and the head
# wall (top end). At the open end the PCB band is closed by a
# one-extrusion cover, so only the housing shows there — the bare PCB
# and under-PCB components face stays hidden; the housing band remains
# open. Lift is friction, gravity, and the wires.

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
display_wall_top_above_face = 0.10  # walls stop here — no overhang over the face
display_outline_corner_r = display_corner_r  # cradle plan outline echoes the device
display_wire_hole_dia = 3.0       # wire drop from the cavity into the pill cusp
display_wire_hole_s = 35.0        # within the plug web — one piece, clear of the seam
display_drain_dia = 3.0           # pocket-floor drain, same drop as the wires
# Drain at the floor's low corner, edge tangent to the PCB cover's back:
# splash that gets past the housing drops into the pill cusp and runs
# out the nozzle end alongside the tubes.
display_drain_s = display_line_width + display_drain_dia / 2.0

# Head-wall face = the device's top end (the device starts one end-wall
# thickness up from the open end face).
display_s_top = display_line_width + display_housing_length
display_collar_half_x = (
    display_housing_width / 2.0 + display_cradle_clearance + display_collar_wall
)
display_wall_top_n = (
    display_floor_n + display_total_depth + display_wall_top_above_face
)
_pcb_band_half_x = display_pcb_width / 2.0 + display_cradle_clearance
# Step to the housing band 0.05 below the device's own PCB→housing step,
# so the housing's overhang ledge never reaches the narrower PCB band.
_pcb_band_n_top = display_floor_n + display_pcb_top_z - 0.05
_housing_band_half_x = display_housing_width / 2.0 + display_cradle_clearance
_block_n_bottom = display_floor_n - 4.0
# The collar's outer faces extend below _block_n_bottom by the width of
# the bottom overhang beside the spout there (collar half-width minus
# the slot surface's x at that level) — transition stock, not a
# transition: a 45-degree blend from the new bottom edge would land on
# the spout exactly at the old bottom level.
_slot_end_arc_x = tube_shell_x_half_outer - (pill_width_y / 2.0 + zone5_wall)
_skirt_drop = display_collar_half_x - (
    _slot_end_arc_x
    + math.sqrt(
        (pill_width_y / 2.0 + zone5_wall) ** 2
        - (_block_n_bottom - flavor_offset_y_from_water) ** 2
    )
)
_cradle_n_bottom = _block_n_bottom - _skirt_drop


def _tip_frame():
    """(tip_end, s_hat, n_hat) in world: tip end on the water centerline,
    unit vectors up-spout along the tip and out the tip's top normal."""
    ta, tb = _tan_after_bend2
    tip_end = cq.Vector(0.0, water_tube_y - _path_p5[0], zone5_z_top + _path_p5[1])
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


def _arc_zone(n0: float, n1: float) -> cq.Workplane:
    """Tip-frame slab covering the bend-arc side of the SPLIT B junction
    plane (s ≥ tip length) between n0 and n1 — the parting tool that
    assigns the cradle's beyond-junction material to the bend piece."""
    return _cradle_prism(60.0, gn_tip_straight_len, display_s_top + 60.0, n0, n1)


def _cradle_outline() -> cq.Workplane:
    """The cradle's plan outline: rounded at the head-wall end, square at
    the open end. The tip piece prints standing on the open end face, so
    a plan corner rounded at that end would overhang from the first
    layer; the head-wall end's plan shrinks as the print rises, which is
    the printable direction. The head-wall arcs run continuously across
    the block/head-wall seam."""
    n0 = _cradle_n_bottom - 5.0
    n1 = display_wall_top_n + 5.0
    rounded = _cradle_prism(
        display_collar_half_x,
        0.0, display_s_top + display_cap_thickness,
        n0, n1,
        corner_r=display_outline_corner_r,
    )
    square_open_end = _cradle_prism(
        display_collar_half_x, 0.0, 10.0, n0, n1,
    )
    return rounded.union(square_open_end)


def _cradle_block() -> cq.Workplane:
    """Collar block: plain slab from the transition-stock bottom to just
    over the face plane, spanning the device length, trimmed to the
    rounded plan outline, with the skirt chamfer already cut. The
    chamfer applies here — before the block joins the spout — so it can
    only ever remove cradle material, never the swept tube. The cavity
    bands carve the pocket out of this."""
    slab = _cradle_prism(
        display_collar_half_x, 0.0, display_s_top,
        _cradle_n_bottom, display_wall_top_n,
    )
    return slab.intersect(_cradle_outline()).cut(_skirt_chamfer())


def _cradle_block_tip_owned() -> cq.Workplane:
    """The cradle block up to the SPLIT B junction plane — the tip
    piece's share. The bend piece keeps everything beyond it: the walls,
    their below-floor flank pads (one continuous solid), and the head
    wall."""
    return _cradle_block().cut(_arc_zone(_block_n_bottom - 80.0, display_wall_top_n + 80.0))


def _end_throat(half_x: float, corner_r: float, n0: float, n1: float) -> cq.Workplane:
    """Square-cornered opening for a band's first display_line_width of
    depth. Its side lands exactly where the band's corner arc reaches one
    extrusion width of end wall, so the wall starts at printable
    thickness with no sliver left behind the step."""
    reach = math.sqrt(corner_r ** 2 - (corner_r - display_line_width) ** 2)
    return _cradle_prism(
        half_x - corner_r + reach, -1.0, display_line_width, n0, n1,
    )


def _display_cavity() -> cq.Workplane:
    """Pocket cut, applied after the block is unioned: PCB band (feet +
    components + board) starting behind the one-extrusion PCB cover, and
    housing band open to the end face with its first extrusion of depth
    squared off. The housing band runs past the wall top — the cavity is
    open sky above the face; the rounded band corners are what stop the
    device's down-tip slide."""
    pcb_r = display_pcb_corner_r + display_cradle_clearance
    housing_r = display_corner_r + display_cradle_clearance
    pcb_band = _cradle_prism(
        _pcb_band_half_x, display_line_width, display_s_top,
        display_floor_n, _pcb_band_n_top,
        corner_r=pcb_r,
    )
    housing_band = _cradle_prism(
        _housing_band_half_x, 0.0, display_s_top,
        _pcb_band_n_top, display_wall_top_n + 5.0,
        corner_r=housing_r,
    )
    return (
        pcb_band
        .union(housing_band)
        .union(_end_throat(_housing_band_half_x, housing_r,
                           _pcb_band_n_top, display_wall_top_n + 5.0))
    )


def _skirt_chamfer() -> cq.Workplane:
    """Transition cut from the collar's pre-skirt bottom edges down to
    the spout: wedge prisms whose faces run from the outline at
    _block_n_bottom to the spout's fill-rect flank at the skirt bottom,
    plus the same profile revolved about each head-corner axis. Around
    the corners the bend carries the spout's flank inboard of the
    straight landing line, so the cone face tucks into the flank there —
    the curved portion of the landing."""
    tip_end, s_hat, n_hat = _tip_frame()
    corner_s = display_s_top + display_cap_thickness - display_outline_corner_r
    corner_x = display_collar_half_x - display_outline_corner_r
    # Wedge cross-section, x measured outboard: toe on the fill-rect
    # flank at the skirt bottom, hinge at the outline on the old bottom.
    # The profile bottoms exactly at the skirt plane — below it is spout,
    # and the cut must never reach the spout (revolved at the corner, a
    # deeper margin sweeps an annular trench through it).
    wedge_profile = [
        (tube_shell_x_half_outer, _cradle_n_bottom),
        (display_collar_half_x, _block_n_bottom),
        (display_collar_half_x + 4.0, _block_n_bottom),
        (display_collar_half_x + 4.0, _cradle_n_bottom),
    ]
    # Revolve profile, radius measured from the corner axis (the side
    # face sits display_outline_corner_r from it).
    ring_profile = [
        (x - corner_x, n) for (x, n) in wedge_profile
    ]
    fp_plane = cq.Plane(origin=tip_end, xDir=cq.Vector(1, 0, 0), normal=n_hat)
    xs_plane = cq.Plane(
        origin=tip_end + s_hat.multiply(corner_s),
        xDir=cq.Vector(1, 0, 0),
        normal=s_hat.multiply(-1.0),
    )
    wedge = (
        cq.Workplane(xs_plane)
        .polyline(wedge_profile).close()
        .extrude(corner_s + 1.0)
    )
    rev_plane = cq.Plane(
        origin=tip_end + s_hat.multiply(corner_s) + cq.Vector(corner_x, 0, 0),
        xDir=cq.Vector(1, 0, 0),
        normal=s_hat.multiply(-1.0),
    )
    ring = (
        cq.Workplane(rev_plane)
        .polyline(ring_profile).close()
        .revolve(360.0, (0, 0), (0, 1))
    )
    quad = (
        cq.Workplane(fp_plane).workplane(offset=_cradle_n_bottom - 4.0)
        .center(corner_x + 15.0, corner_s + 15.0)
        .rect(30.0, 30.0)
        .extrude(_block_n_bottom - _cradle_n_bottom + 8.0)
    )
    # Back bevel between the two corner axes: the same profile as the
    # cones' back-azimuth end, so cone and bevel meet tangentially —
    # without it, the quadrant boundary leaves a step facet where the
    # back skirt pokes past the spout skin. Extends past the back face
    # harmlessly: the chamfer only ever subtracts from cradle parts.
    s_back = display_s_top + display_cap_thickness
    back_profile = [
        (s_back - _skirt_drop, _cradle_n_bottom),
        (s_back, _block_n_bottom),
        (s_back + 4.0, _block_n_bottom),
        (s_back + 4.0, _cradle_n_bottom),
    ]
    back_plane = cq.Plane(
        origin=tip_end + cq.Vector(-corner_x, 0, 0),
        xDir=s_hat,
        normal=cq.Vector(1, 0, 0),
    )
    back = (
        cq.Workplane(back_plane)
        .polyline(back_profile).close()
        .extrude(2.0 * corner_x)
    )
    plus_side = wedge.union(ring.intersect(quad))
    return plus_side.union(plus_side.mirror("YZ")).union(back)


def _display_head_wall() -> cq.Workplane:
    """Bend-piece head wall past the display's top end — closes the
    cradle's top end and is the display's axial stop as SPLIT B closes.
    Same bottom and top planes as the collar block, so the cradle reads
    as one rectangle; trimmed to the shared plan outline, with the skirt
    chamfer cut before it joins the spout (same rule as the block)."""
    return (
        _cradle_prism(
            display_collar_half_x, display_s_top, display_s_top + display_cap_thickness,
            _cradle_n_bottom, display_wall_top_n,
        )
        .intersect(_cradle_outline())
        .cut(_skirt_chamfer())
    )


def _middle_floor_clearance() -> cq.Workplane:
    """The bend piece carries no floor through the joint's overlap — the
    pocket floor there is the tip piece's tube wall. This clears the
    sliver of bend-piece wall that rises past the socket surface toward
    the floor plane under the display. Bounded outside the socket
    surface and inside the pocket footprint, so the piece's flanks,
    skin, and head wall are untouched."""
    center_y = water_tube_y - _path_center_bend2[0]
    center_z = zone5_z_top + _path_center_bend2[1]
    socket_r = (
        gn_bend2_r
        + flavor_offset_y_from_water + pill_width_y / 2.0 + zone5_wall
        - split_b_socket_shrink
    )
    annulus = (
        cq.Workplane(cq.Plane(
            origin=cq.Vector(-40.0, center_y, center_z),
            xDir=cq.Vector(0, 1, 0),
            normal=cq.Vector(1, 0, 0),
        ))
        .circle(120.0)
        .circle(socket_r - 0.05)
        .extrude(80.0)
    )
    under_display = _cradle_prism(
        _pcb_band_half_x, gn_tip_straight_len, display_s_top,
        3.0, display_floor_n,
    )
    return annulus.intersect(under_display)


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
    pill cusp and runs out the nozzle end alongside the tubes."""
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
    water_y_width = 2.0 * tube_shell_water_r_outer
    water_outer = (
        _horizontal_plane(z_bottom)
        .moveTo((0.0, water_tube_y))
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
        .moveTo((0.0, (water_tube_y + flavor_tube_post_bend_y) / 2.0))
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
    return water_tube_cyl(z_bottom, z_height).union(flavor_inner)


# ============================================================
# PUBLIC SHELL BUILDERS
# ============================================================

def build_shell() -> cq.Workplane:
    """Touch-Flo shell — full reference solid (un-split), all zones
    unioned, with the display cradle on the dispense tip. Split for
    printing into three pieces along the gooseneck: build_shell_bottom
    (angled-spout), build_shell_middle (upper-bend), build_shell_top
    (dispense-tip)."""
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
        _display_wire_hole().val(),
        _display_drain_hole().val(),
    ]
    inner = cq.Workplane(obj=inner_parts[0].fuse(*inner_parts[1:]))
    return outer.cut(inner)


def build_shell_bottom(full_shell: cq.Workplane | None = None) -> cq.Workplane:
    """Angled-spout piece — everything below the SPLIT A junction plane,
    top 20 mm of the spout hollowed to a 2 mm-wall female socket."""
    full = full_shell if full_shell is not None else build_shell()
    below_junction = _split_plane_halfspace(
        (0.0, split_junction_y, split_junction_z), split_normal, sign=-1,
    )
    socket_cavity = _build_zone6_outer_shrunk(split_a_socket_shrink).intersect(
        _split_overlap_slab(split_a_socket_overlap_y, split_a_socket_overlap_z)
    )
    return full.intersect(below_junction).cut(socket_cavity)


def build_shell_middle(full_shell: cq.Workplane | None = None) -> cq.Workplane:
    """Upper-bend piece — male plug at the SPLIT A (bottom) end, female
    socket at the SPLIT B (top) end. The piece carries the cradle beyond
    the junction plane — walls, flank pads, and head wall, inherited
    from the full shell — and presses the display in as the joint
    closes; it gives up only the cradle's straight-zone block."""
    full = full_shell if full_shell is not None else build_shell()
    above_junction_a = _split_plane_halfspace(
        (0.0, split_junction_y, split_junction_z), split_normal, sign=+1,
    )
    overlap_slab_a = _split_overlap_slab(
        split_a_plug_overlap_y, split_a_plug_overlap_z
    )
    plug_outer_a = _build_zone6_outer_shrunk(split_a_plug_shrink).intersect(overlap_slab_a)
    plug_bores_a = build_zone6_inner_cut().intersect(overlap_slab_a)
    plug_a = plug_outer_a.cut(plug_bores_a)
    bend_plus_tip = full.intersect(above_junction_a).union(plug_a)

    tip_section = _build_tip_section(_tube_shell_outer_sketch())
    bend_socket_cavity = _build_bend_overlap(
        _tube_shell_outer_shrunk_sketch(split_b_socket_shrink), side="socket",
    )
    return (
        bend_plus_tip
        .cut(tip_section)
        .cut(bend_socket_cavity)
        .cut(_cradle_block_tip_owned())
        .cut(_middle_floor_clearance())
    )


def build_shell_top(full_shell: cq.Workplane | None = None) -> cq.Workplane:
    """Dispense-tip piece — male plug for the SPLIT B (bend↔tip) joint,
    carrying the cradle's straight-zone portion: pocket, PCB cover, and
    walls up to the junction plane. The plug keeps its full tube wall;
    where it rises past the floor plane the cavity shaves it flush — its
    top is the pocket floor through the joint's overlap."""
    _ = full_shell
    tip_outer = _build_tip_section(_tube_shell_outer_sketch())
    tip_inner = _build_tip_section(_tube_shell_inner_sketch())
    plug_outer = _build_bend_overlap(
        _tube_shell_outer_shrunk_sketch(split_b_plug_shrink), side="plug",
    )
    plug_inner = _build_bend_overlap(_tube_shell_inner_sketch(), side="plug")
    plug = plug_outer.cut(plug_inner)

    return (
        tip_outer
        .union(_cradle_block_tip_owned())
        .union(plug)
        .cut(tip_inner)
        .cut(_display_cavity())
        .cut(_display_drain_hole())
        .cut(_display_wire_hole())
    )


def main():
    out_dir = Path(__file__).resolve().parent
    full = build_shell()
    bottom = build_shell_bottom(full)
    middle = build_shell_middle(full)
    top = build_shell_top(full)

    full_out = out_dir / "touch-flo-shell.step"
    bottom_out = out_dir / "touch-flo-shell-bottom.step"
    middle_out = out_dir / "touch-flo-shell-middle.step"
    top_out = out_dir / "touch-flo-shell-top.step"
    export_step(full, str(full_out))
    export_step(bottom, str(bottom_out))
    export_step(middle, str(middle_out))
    export_step(top, str(top_out))
    print(f"-> {full_out.name}")
    print(f"-> {bottom_out.name}")
    print(f"-> {middle_out.name}")
    print(f"-> {top_out.name}")

    variables = {
        "BORE_CLEAR": f"{bore_clearance:.4g} mm",
        "BODY_BORE_D": f"{body_bore_diameter:.4g} mm",
        "BODY_OD": f"{body_rect_long_y:.4g} mm",
        "BODY_RECT_LONG": f"{body_rect_long_y:.4g} mm",
        "BODY_RECT_SHORT": f"{body_rect_short_x:.4g} mm",
        "BODY_CYL_TOP_Z": f"{zone1_z_top:.4g} mm",
        "BORE_COVE_Z": f"{zone2_bore_z_bottom + cove_r:.4g} mm",
        "PILL_L": f"{pill_length_x:.4g} mm",
        "PILL_W": f"{pill_width_y:.4g} mm",
        "FLAVOR_TUBE_Y": f"{flavor_pill_center[1]:.4g} mm",
        "FLAVOR_PILL_Y_MINUS": f"{flavor_pill_y_minus_edge:.4g} mm",
        "SHELL_OUTER_R": f"{shell_outer_r:.4g} mm",
        "WATER_HOLE_D": f"{water_hole_diameter:.4g} mm",
        "WALL_MIN": f"{wall_thickness_min:.4g} mm",
        "ZONE1_HEIGHT": f"{zone1_height:.4g} mm",
        "ZONE2_HEIGHT": f"{zone2_height:.4g} mm",
        "ZONE4_HEIGHT": f"{zone4_height:.4g} mm",
        "ZONE5_HEIGHT": f"{zone5_height:.4g} mm",
        "ZONE5_WALL": f"{zone5_wall:.4g} mm",
        "BODY_BORE_FARTHEST": f"{_body_bore_farthest_from_shell_center:.4g} mm",
        "PILL_FARTHEST": f"{_pill_farthest_from_shell_center:.4g} mm",
        "BODY_BORE_RECT_LONG": f"{body_bore_rect_long_y:.4g} mm",
        "BODY_BORE_RECT_SHORT": f"{body_bore_rect_short_x:.4g} mm",
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
        "WATER_TUBE_OD": f"{water_tube_od:.4g} mm",
        "WATER_TUBE_Y": f"{water_tube_y:.4g} mm",
        "TUBE_SHELL_WATER_R": f"{tube_shell_water_r_outer:.4g} mm",
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
        "BACK_ARCH_DY": f"{_back_arch_dy:.4g} mm",
        "Z5_Y_MIN": f"{_z5_y_min:.4g} mm",
        "ZONE45_Z_TOP": f"{zone45_z_top:.4g} mm",
        "ZONE45_Z_BOT_FRONT": f"{zone45_z_bottom_at_front:.4g} mm",
    }
    substitute_md(
        out_dir / "ASSEMBLY.md",
        variables=variables,
        expected_counts={
            "BORE_CLEAR": 1,
            "PILL_L": 1,
            "PILL_W": 2,
            "FLAVOR_TUBE_Y": 2,
            "BODY_OD": 2,
            "BODY_RECT_LONG": 1,
            "BODY_RECT_SHORT": 1,
            "BODY_CYL_TOP_Z": 1,
            "BORE_COVE_Z": 1,
        },
    )
    print("-> ASSEMBLY.md")
    substitute_md(
        out_dir / "MATERIAL.md",
        variables=variables,
        expected_counts={},
    )
    print("-> MATERIAL.md")
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "BODY_BORE_D": 1,
            "BODY_OD": 2,
            "BODY_CYL_TOP_Z": 1,
            "PILL_L": 1,
            "PILL_W": 1,
            "FLAVOR_PILL_Y_MINUS": 1,
            "SHELL_OUTER_R": 2,
            "WATER_HOLE_D": 1,
            "WALL_MIN": 1,
            "ZONE1_HEIGHT": 2,
            "ZONE2_HEIGHT": 1,
            "ZONE4_HEIGHT": 1,
            "ZONE5_HEIGHT": 1,
            "ZONE5_WALL": 1,
            "BODY_BORE_FARTHEST": 1,
            "PILL_FARTHEST": 1,
            "BODY_BORE_RECT_LONG": 1,
            "BODY_BORE_RECT_SHORT": 1,
            "ZONE2_BORE_Z_BOTTOM": 1,
            "SHELL_OUTER_LIP": 1,
            "ZONE1_OUTER_Z_TOP": 2,
            "LEVER_CLEAR_X_HALF": 1,
            "SHELL_RECT_X_HALF": 2,
            "SHELL_RECT_Y_MAX": 1,
            "SHELL_RECT_Y_MIN": 2,
            "BORE_Y_AT_LEVER_X": 1,
            "LEVER_RAMP_Y_START": 1,
            "ZONE3_Z_BOTTOM": 1,
            "WING_INNER_X": 2,
            "SHELL_ARCH_BORE_INNER_X": 1,
            "SHELL_ARCH_BORE_OUTER_X": 1,
            "SHELL_ARCH_BORE_Z_FOOT_TOP": 1,
            "SHELL_ARCH_BORE_Z_PEAK": 1,
            "SHELL_ARCH_Z_FOOT_TOP": 2,
            "SHELL_ARCH_Z_PEAK": 1,
            "WATER_TUBE_OD": 1,
            "WATER_TUBE_Y": 1,
            "TUBE_SHELL_WATER_R": 2,
            "FLAVOR_POST_BEND_Y": 1,
            "FILL_Y_MIN": 1,
            "FILL_X_THICKNESS": 1,
            "PILL_STRAIGHT_INNER": 1,
            "FLAVOR_OFFSET_Y": 1,
            "ZONE5_Z_BOTTOM": 1,
            "ZONE5_Z_TOP": 1,
            "GN_BEND1_Z_MID": 1,
            "GN_BEND1_Z_START": 2,
            "GN_BEND2_SWEEP_DEG": 1,
            "BACK_ARCH_DY": 1,
            "Z5_Y_MIN": 1,
            "ZONE45_Z_TOP": 1,
            "ZONE45_Z_BOT_FRONT": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
