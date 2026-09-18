"""Faucet shell — printed shroud that wraps the harvested Westbrass,
the flavor tubes, and the lever swing volume. Sits on top of
the above-counter plate. The dispense tip carries the cradle for
the faucet display (DISPLAY CRADLE section).

Frame: world +Z is height (up), world ±X is lateral (symmetric across
the X=0 plane), world -Y is forward (dispense direction — the gooseneck
arcs toward -Y, where the user's glass sits). The Westbrass's threaded shank
runs along world Z at world (X, Y) = (0, 0)."""

import io
import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh

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
# Manifold validation and the ledger of named geometric bounds.
import flute_skin as _flute_skin
import _stated_bounds as _bounds
from _cadq_export import export_assembly
from _materials import C_FAUCET_BLACK, one_body
import _faucet_interface
import _display_snap
from _faucet_interface import (
    above_counter_gasket_thickness,
    above_counter_plate_thickness,
    flavor_tube_od,
    flavor_tube_x_offset,
    flavor_tube_hole_dia,
    pill_length_x,
    pill_width_y,
    flavor_tube_depth,
    display_housing_width,
    display_housing_length,
    display_pcb_width,
    display_pcb_length,
    display_corner_r,
    display_pcb_corner_r,
    display_total_depth,
    display_pcb_top_z,
    display_cover_slip,
    display_cover_lap,
    display_cover_over_face,
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
wall_thickness_min = 2.0

# The donor and lever envelope owns the lower arch's construction datum.
show_wall = 4.2
print_layer_height = 0.24
print_bead_width = 0.42

_westbrass_bore_farthest_from_shell_center = (
    (shell_center_y - westbrass_bore_y) + westbrass_bore_diameter / 2.0
)  # = [19.18 mm](WESTBRASS_BORE_FARTHEST)
# THE PILL'S FARTHEST POINT IS ON AN END CAP AND NOT ON ITS BACK EDGE. The cutout is a slot
# with its cap circles at (±`flavor_tube_x_offset`, `flavor_tube_depth`), and the shell's outer
# is a cylinder about `shell_center` — so the corner that reaches furthest from that centre is a
# cap's own rim, `pill_width_y / 2` out from a centre standing off the axis in X as well as Y.
# Read on the +Y edge alone the reach comes back 0.32 mm short, and the wall over the cap's
# shoulder is that much thinner than the figure says.
_pill_farthest_from_shell_center = (
    math.hypot(flavor_tube_x_offset, flavor_tube_depth - shell_center_y) + pill_width_y / 2.0
)  # = [19.69 mm](PILL_FARTHEST)
# [23.89 mm](SHELL_OUTER_R) outer-cylinder radius.
shell_outer_r = (
    max(_westbrass_bore_farthest_from_shell_center, _pill_farthest_from_shell_center)
    + show_wall
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

# [2 mm](WALL_MIN) cylindrical shell wall above the Westbrass cyl top before the cove.
shell_outer_lip = wall_thickness_min + bore_clearance  # [2.25 mm](SHELL_OUTER_LIP)
zone1_outer_z_top = zone1_z_top + shell_outer_lip  # [15.25 mm](ZONE1_OUTER_Z_TOP)
zone2_outer_z_bottom = zone1_outer_z_top  # [15.25 mm](ZONE1_OUTER_Z_TOP)


# BASE JOINT — three hidden M3 screws clamp the plate against the shell.
# Three pedestals register the plate before the screws are tightened.
foot_width = 58.0
foot_depth = 59.0
foot_center_y = 0.0
base_pod_counterbore_dia = 6.15
base_pod_shank_dia = 3.9
base_pod_wall = wall_thickness_min
base_pod_center_x = 20.0
base_pod_center_y = 10.0
base_pod_front_center_x = 0.0
base_pod_front_center_y = -22.3
base_pod_centers = [
    (+base_pod_center_x, base_pod_center_y),
    (-base_pod_center_x, base_pod_center_y),
    (base_pod_front_center_x, base_pod_front_center_y),
]
base_pod_z_bottom = zone1_z_bottom
base_pod_insert_dia = 4.0
base_insert_outer_dia = 4.6
base_insert_length = 4.0
base_pedestal_dia = base_pod_shank_dia + 2.0 * base_pod_wall
base_pedestal_height = 2.2
base_pedestal_chamfer = 0.4
base_pod_hole_dia = base_pedestal_dia + 2.0 * fits.slip
base_pod_hole_depth = base_pedestal_height + 1.0
base_insert_bottom_z = base_pod_z_bottom + base_pod_hole_depth
base_pod_insert_depth = base_insert_length + 1.25
base_pod_z_top = base_insert_bottom_z + base_pod_insert_depth + base_pod_wall
base_pod_radius = base_insert_outer_dia / 2.0 + base_pod_wall
base_screw_length = 8.0
base_screw_head_height = 3.0
base_screw_head_recess = 0.2
base_screw_counterbore_depth = base_screw_head_height + base_screw_head_recess
base_screw_seat_z = -above_counter_plate_thickness + base_screw_counterbore_depth
base_plate_seat_thickness = base_pedestal_height - base_screw_seat_z
# Positive material is measured against the inserted brass envelope, not its pilot.
_base_insert_wall = _bounds.bound(
    "faucet-base-insert-wall", "The base inserts keep a full wall to the Westbrass cavity",
    f"at least {wall_thickness_min:g} mm")
for _x, _y in base_pod_centers:
    _stock = math.hypot(_x, _y) - westbrass_bore_diameter / 2.0 - base_insert_outer_dia / 2.0
    _base_insert_wall(_stock >= wall_thickness_min,
                      f"insert at ({_x:g}, {_y:g}) has {_stock:.4f} mm to the donor cavity")
_bounds.state(
    "faucet-base-screw-seat", "The hidden screw head bears on a full printed wall",
    f"at least {wall_thickness_min:g} mm", base_plate_seat_thickness >= wall_thickness_min - 1e-9,
    f"the {above_counter_plate_thickness:g} mm plate and {base_pedestal_height:g} mm pedestal "
    f"retain {base_plate_seat_thickness:g} mm above the {base_screw_counterbore_depth:g} mm counterbore")


lever_x_half = 6.5
lever_fit_clearance = 0.35
lever_sweep_allowance = 0.005
lever_insertion_front_y = -65.0
lever_rest_back_y = 9.0
lever_clearance_x_half = lever_x_half + lever_fit_clearance
lever_clearance_y_back = lever_rest_back_y + lever_fit_clearance + lever_sweep_allowance
lever_rest_top_z = zone2_z_top + 13.0

shell_rect_y_half = shell_outer_r  # [23.89 mm](SHELL_OUTER_R)
shell_rect_x_half = westbrass_bore_rect_short_x / 2.0 + show_wall  # [12.95 mm](SHELL_RECT_X_HALF)
shell_rect_y_width = 2.0 * shell_rect_y_half
shell_rect_x_width = 2.0 * shell_rect_x_half
shell_rect_y_max = shell_center_y + shell_rect_y_half  # [27.07 mm](SHELL_RECT_Y_MAX) (toward back)
shell_rect_y_min = shell_center_y - shell_rect_y_half  # [-20.72 mm](SHELL_RECT_Y_MIN) (toward user)

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

shell_arch_z_foot_top = arch_z_base + shell_outer_lip  # [43.25 mm](SHELL_ARCH_Z_FOOT_TOP)
shell_arch_z_peak = arch_z_peak + shell_outer_lip  # [48.25 mm](SHELL_ARCH_Z_PEAK)
wing_inner_x = shell_arch_bore_inner_x  # [6.75 mm](WING_INNER_X)
wing_outer_x = shell_rect_x_half  # [12.95 mm](SHELL_RECT_X_HALF)

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
# neoFlo LLDPE-4 (1/4-inch OD) supplier bend radius: 1 inch.
# https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf
flavor_bend_min_radius = 25.4
flavor_bend_radius = 40.0
flavor_bend_start_z = 42.0
flavor_bend_angle_rad = math.acos(
    1.0 - (flavor_tube_depth - flavor_tube_post_bend_y) / (2.0 * flavor_bend_radius)
)

fill_y_min = +10.46  # back third of the soda faucet tube (Y ≥ [10.46 mm](FILL_Y_MIN))


# ZONE 4 — rect column above the arch (soda faucet tube + flavor pill cutouts).
zone4_z_bottom = shell_arch_z_foot_top  # [43.25 mm](SHELL_ARCH_Z_FOOT_TOP)
# Clears the pressed-lever head corner (Y=+6.78, Z=54.024), which sits
# inside zone 5's water-circle outline (Y=+[8.875 mm](SODA_FAUCET_TUBE_Y),
# R=[9.262 mm](TUBE_SHELL_SODA_R)); zone 5's bottom is above it.
zone4_z_top = 57.5
zone4_height = zone4_z_top - zone4_z_bottom  # [14.25 mm](ZONE4_HEIGHT)


# ZONE 5 — round tube wrapper above the lever, carrying the soda bore
# and flavor pill. Its wall contains both halves of the curved joint.
zone5_z_bottom = zone4_z_top  # [57.5 mm](ZONE5_Z_BOTTOM)
zone5_z_top = zone4_z_top + 10.0  # [67.5 mm](ZONE5_Z_TOP)
zone5_height = zone5_z_top - zone5_z_bottom  # [10 mm](ZONE5_HEIGHT)
# Water → flavor offset along world Y; positive — flavor sits behind water.
flavor_offset_y_from_water = flavor_tube_post_bend_y - soda_faucet_tube_y  # ≈ [7.275 mm](FLAVOR_OFFSET_Y)

split_socket_wall = wall_thickness_min
split_plug_wall = wall_thickness_min
split_slip = 2.0 * fits.slip
zone5_wall = split_socket_wall + split_slip / 2.0 + split_plug_wall

signal_lane_width = 5.0
signal_lane_depth = 1.8
signal_lane_center_n = 11.55
signal_ribbon_max_width = 4.1
signal_ribbon_max_depth = 1.3
_tube_soda_bore_r = soda_faucet_hole_diameter / 2.0
_tube_pill_bore_r = pill_width_y / 2.0
_tube_pill_cap_x = (pill_length_x - pill_width_y) / 2.0
_tube_bore_caps = (
    (_tube_pill_cap_x, flavor_offset_y_from_water, _tube_pill_bore_r),
    ((signal_lane_width - signal_lane_depth) / 2.0,
     signal_lane_center_n, signal_lane_depth / 2.0),
)
# Equal reach to the lower soda bore and the limiting upper passage end caps.
tube_shell_center_y = max(
    (x * x + y * y - (_tube_soda_bore_r - radius) ** 2)
    / (2.0 * (y + _tube_soda_bore_r - radius))
    for x, y, radius in _tube_bore_caps)
tube_shell_bore_radius = tube_shell_center_y + _tube_soda_bore_r
tube_shell_outer_r = tube_shell_bore_radius + zone5_wall
tube_shell_soda_r_outer = tube_shell_outer_r - tube_shell_center_y  # [9.262 mm](TUBE_SHELL_SODA_R)
tube_shell_pill_x_half_outer = pill_length_x / 2.0 + zone5_wall
tube_shell_x_half_outer = tube_shell_outer_r
tube_shell_x_outer = 2.0 * tube_shell_x_half_outer

display_neck_outer_r = tube_shell_outer_r

_neck_walls = _bounds.bound(
    "faucet-neck-joint-walls", "The circular gooseneck joint carries two full walls",
    f"socket and plug at least {wall_thickness_min:g} mm")
_neck_walls(split_socket_wall >= wall_thickness_min,
            f"socket wall {split_socket_wall:g} mm")
_neck_plug_min_wall = tube_shell_outer_r - split_socket_wall - split_slip / 2.0 - max(
    tube_shell_center_y + _tube_soda_bore_r,
    *(math.hypot(x, y - tube_shell_center_y) + radius for x, y, radius in _tube_bore_caps),
)
_neck_walls(_neck_plug_min_wall >= wall_thickness_min - 1e-9,
            f"plug wall {_neck_plug_min_wall:.4f} mm around all tube and cable passages")


# ZONE 6 — gooseneck wrapper around the bent tubes: zone 5's
# cross-section swept along one circular arc above the lever-swing envelope.
# Mirrors constants in `faucet-assembly`.

gn_bend1_sweep_rad = math.radians(30.0)
gn_bend2_sweep_rad = math.radians(110.0)
gn_mid_straight_len = 0.0
gn_tip_straight_len = 25.0
gn_outlet_y = -133.99672200476698
gn_outlet_z = 180.38874339162197
_path_total_rot = gn_bend1_sweep_rad + gn_bend2_sweep_rad  # [140°](GN_TOTAL_ROT) at the tip
gn_bend1_r = (
    soda_faucet_tube_y - gn_outlet_y - gn_tip_straight_len * math.sin(_path_total_rot)
) / (1.0 - math.cos(_path_total_rot))
gn_bend2_r = gn_bend1_r
gn_bend1_z_start = (
    gn_outlet_z - gn_bend1_r * math.sin(_path_total_rot)
    - gn_tip_straight_len * math.cos(_path_total_rot)
)  # ≈ [153.4 mm](GN_BEND1_Z_START)
gn_bend1_z_mid = (
    gn_bend1_z_start + gn_bend1_r * math.sin(gn_bend1_sweep_rad / 2.0)
)  # [172 mm](GN_BEND1_Z_MID)


# SPLIT — the shell prints in TWO pieces, meeting at one 20 mm slip-fit
# joint on bend 2, at half the gooseneck's total turn. Each piece carries
# [70°](SPLIT_JUNCTION_ROT) of turn; its bed orientation is set in the
# PRINTING section. The joint's mating surfaces follow the arc: the tip
# swings shut about the bend-2 axis.
# Fit: the plug's outer surface sits slip/2 inside the socket's cavity
# surface, all the way around the cross-section.

split_junction_rot = _path_total_rot / 2.0  # [70°](SPLIT_JUNCTION_ROT)

# Per-side overlap depth (mm of arc), socket wall (mm), and diametral
# slip (mm), mapped onto `shrink`s (inward offsets of the outer
# cross-section):
#   socket shrink = socket_wall
#   plug   shrink = socket_shrink + slip / 2
split_socket_overlap_len = 20.0
split_plug_overlap_len = 18.0

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
split_junction_y = soda_faucet_tube_y - _path_junction[0]  # [-38.37 mm](SPLIT_JUNCTION_Y)
split_junction_z = zone5_z_top + _path_junction[1]  # [220.9 mm](SPLIT_JUNCTION_Z)

# PRINTING — the base beds on its foot (Z=0) with the -Y edge lifted
# [15°](PRINT_TILT), keeping the long straight neck close to vertical.
# The tip beds on the joint end with the crown lifted and its build
# direction at the angular midpoint of the sweep it carries.
print_base_build_rot = math.radians(15.0)
print_tip_build_rot = (split_junction_rot + _path_total_rot) / 2.0
# Tilt off the bed face. The foot is square to the path at rotation 0
# and the joint face to the path at the junction.
print_base_tilt_rad = print_base_build_rot
print_tip_tilt_rad = print_tip_build_rot - split_junction_rot
max_print_overhang_rad = max(
    print_base_build_rot,
    split_junction_rot - print_base_build_rot,
    print_tip_build_rot - split_junction_rot,
    _path_total_rot - print_tip_build_rot,
)  # [55°](MAX_PRINT_OVERHANG)


# ZONE 3 OUTER ARCH — single circular arc from the wing bottom
# (zone3_z_bottom at the -Y end) up to zone4_z_top at Y=fill_y_min,
# tangent-horizontal at the high end. Center is directly below the high end.
_back_arch_dy = fill_y_min - shell_rect_y_min  # [31.18 mm](BACK_ARCH_DY) (positive depth span)
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
# up to Z=gn_bend1_z_start ≈ [153.4 mm](GN_BEND1_Z_START).

# Round gooseneck section at world X=0.
_z5_y_min = soda_faucet_tube_y + tube_shell_center_y - tube_shell_outer_r
_z5_y_max = soda_faucet_tube_y + tube_shell_center_y + tube_shell_outer_r

# Zone 4.5 Y extents — back edge follows the rect column; front edge
# matched-margin from zone 5.
zone45_front_y = _z5_y_min - (shell_rect_y_max - _z5_y_max)

# Top sits 3 mm above zone 4's top on the back side (lid sits flat on
# zone 4 top). The front bottom follows the back-arch curve down to
# ≈ Z=[55.31 mm](ZONE45_Z_BOT_FRONT).
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


def build_zone1_inner_cut() -> cq.Workplane:
    """Body bore + flavor-tube pill."""
    westbrass_bore = westbrass_bore_cyl(zone1_z_bottom, zone2_bore_z_bottom - zone1_z_bottom)
    pill = _flavor_pill_flat_y_minus(zone1_z_bottom, zone1_height)
    return westbrass_bore.union(pill)


def build_base_pod_holes() -> cq.Workplane:
    """Three pedestal sockets, each with an insert pilot opening through its roof."""
    cuts = []
    for center in base_pod_centers:
        socket = (_horizontal_plane(base_pod_z_bottom).moveTo(center)
                  .circle(base_pod_hole_dia / 2.0).extrude(base_pod_hole_depth).unwrap())
        insert = (_horizontal_plane(base_insert_bottom_z).moveTo(center)
                  .circle(base_pod_insert_dia / 2.0).extrude(base_pod_insert_depth).unwrap())
        cuts.append(socket.val().fuse(insert.val()))
    return cq.Workplane(obj=cq.Compound.makeCompound(cuts))


def build_foot_outline(z_bottom: float, z_height: float) -> cq.Workplane:
    """Shared oval perimeter of the shell, above-counter plate and gasket."""
    return (cq.Workplane("XY").workplane(offset=z_bottom)
            .center(0.0, foot_center_y).ellipse(foot_width / 2.0, foot_depth / 2.0)
            .extrude(z_height))


def build_lower_outer() -> cq.Workplane:
    """Continuous oval lower shell, terminating on the round gooseneck section."""
    sections = (
        (0.0, foot_width, foot_depth, foot_center_y),
        (8.5, foot_width, foot_depth, foot_center_y),
        (20.0, 43.0, 53.5, 4.25),
        (34.0, 40.0, 52.5, 5.25),
        (43.0, 38.0, 50.0, 5.0),
        (59.0, 27.0, 29.0, 11.5),
    )
    wires = [cq.Workplane("XY").workplane(offset=z).center(0.0, cy)
             .ellipse(width / 2.0, depth / 2.0).val()
             for z, width, depth, cy in sections]
    neck = _tube_shell_outer_sketch()._faces.Faces()[0].outerWire()
    wires.append(neck.translate((0.0, soda_faucet_tube_y, 65.0)))
    loft = cq.Solid.makeLoft(wires, ruled=False)
    neck_land = cq.Solid.extrudeLinear(
        wires[-1], [], cq.Vector(0.0, 0.0, zone5_z_top + 0.2 - 65.0))
    return cq.Workplane(obj=loft.fuse(neck_land)).clean()


# The ribbon leaves the counter beside the flavor pair, inside the metal
# mounting plate's existing open channel.
signal_lower_exit_x = 9.3
signal_lower_exit_y = 17.0


def _lower_signal_stations():
    top_y = flavor_tube_depth + signal_lane_center_n - flavor_offset_y_from_water
    return ((14.0, signal_lower_exit_x, signal_lower_exit_y),
            (18.0, signal_lower_exit_x, 20.0),
            (23.0, signal_lower_exit_x, 22.5),
            (27.0, 6.0, top_y),
            (32.0, 1.0, top_y),
            (36.0, 0.0, top_y),
            (39.0, 0.0, top_y))


def _lower_signal_profile(z, x, y, width, depth, rounded):
    wp = cq.Workplane("XY").workplane(offset=z).center(x, y)
    return (wp.slot2D(width, depth) if rounded else wp.rect(width, depth)).val()


def _lower_signal_solid(width, depth, rounded, bottom_z, straight_overlap=0.2,
                        turn_clearance=0.0):
    stations = _lower_signal_stations()
    wires = [_lower_signal_profile(z, x, y, width + 2.0 * turn_clearance,
                                   depth + 2.0 * turn_clearance, rounded)
             for z, x, y in stations]
    turn = cq.Solid.makeLoft(wires, ruled=False)
    vertical = (_lower_signal_profile(bottom_z, signal_lower_exit_x,
                                     signal_lower_exit_y, width, depth, rounded))
    straight = cq.Solid.extrudeLinear(vertical, [], cq.Vector(0.0, 0.0, stations[0][0] + straight_overlap - bottom_z))
    return cq.Workplane(obj=straight.fuse(turn))


def build_lower_signal_ribbon() -> cq.Workplane:
    """Maximum stated 4.1×1.3 mm ribbon envelope through the complete mount stack."""
    return _lower_signal_solid(signal_ribbon_max_width, signal_ribbon_max_depth, False, -50.0)


def build_lower_signal_lane() -> cq.Workplane:
    """Cable lane with a broad opening to the flavor passage, leaving no thin fin."""
    from shapely.geometry import MultiPoint

    # Carry the vertical relief beyond the ribbon's straight-to-turn join so
    # its square corner has clearance from the passage's transition ledge.
    # The curved run needs additional normal clearance at its oblique sections.
    lane = _lower_signal_solid(signal_lane_width, signal_lane_depth, True, -6.2,
                               straight_overlap=1.2, turn_clearance=0.05)
    stations = _lower_signal_stations()
    wires = []
    for z, x, y in stations:
        # Join the existing flat-sided flavor opening to the capsule's
        # interior. A convex bridge removes the material wedge between the
        # pill side and the capsule end throughout the straight/turn handoff.
        # Its cable-end rectangle stays 0.1 mm inside the capsule's flat
        # sides so their union has positive overlap without coincident faces.
        # Cross the shared pill boundary slightly so subtraction cannot leave
        # a coincident face enclosing the very wedge this connector removes.
        overlap = 0.02
        pill_half_x = pill_length_x / 2.0 + overlap
        lane_half_x = (signal_lane_width - signal_lane_depth) / 2.0
        lane_half_y = signal_lane_depth / 2.0 - 0.1
        points = [(px, py)
                  for px in (-pill_half_x, pill_half_x)
                  for py in (flavor_pill_y_minus_edge - overlap,
                             flavor_tube_depth + overlap)]
        points.extend((px, py)
                      for px in (x - lane_half_x, x + lane_half_x)
                      for py in (y - lane_half_y, y + lane_half_y))
        outline = list(MultiPoint(points).convex_hull.exterior.coords)[:-1]
        wires.append(cq.Workplane("XY").workplane(offset=z)
                     .polyline(outline).close().val())
    upper = cq.Solid.makeLoft(wires, ruled=False)
    lower = cq.Solid.extrudeLinear(wires[0].translate((0.0, 0.0, -20.2)), [], cq.Vector(0.0, 0.0, 20.4))
    return lane.union(cq.Workplane(obj=upper.fuse(lower)))


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
            .lineTo(+bore_y_oversize, zone3_z_bottom)
            .wire()
            .extrude(x_height)
        )

    bore_thickness = shell_arch_bore_outer_x - shell_arch_bore_inner_x
    bores = bore(+shell_arch_bore_inner_x, +bore_thickness).union(
        bore(-shell_arch_bore_outer_x, +bore_thickness)
    )
    return bores.intersect(westbrass_bore_cyl(zone3_z_bottom, shell_arch_bore_z_peak - zone3_z_bottom))


def build_lower_soda_inner_cut() -> cq.Workplane:
    """Straight soda-tube passage from the donor outlet into the swept neck."""
    return soda_faucet_tube_cyl(zone3_z_bottom, zone5_z_top + 0.5 - zone3_z_bottom)


def _flavor_transition_path() -> cq.Workplane:
    """The lower S-bend path, relative to the flavor-pair center at its lower end."""
    start_z, end_z = zone3_z_bottom - 0.5, zone5_z_top + 0.5
    start = (0.0, flavor_bend_start_z - start_z)
    mid1, end1, tangent = _arc_from_tangent(
        start, (0.0, 1.0), flavor_bend_radius, flavor_bend_angle_rad, ccw=False)
    mid2, end2, _ = _arc_from_tangent(
        end1, tangent, flavor_bend_radius, flavor_bend_angle_rad, ccw=True)
    return (cq.Workplane(_path_plane).moveTo(0.0, 0.0).lineTo(*start)
            .threePointArc(mid1, end1).threePointArc(mid2, end2)
            .lineTo(end2[0], end_z - start_z).wire())


def build_flavor_transition_inner_cut() -> cq.Workplane:
    """The flavor pair's pill swept through its lower S bend into the neck bores."""
    return (cq.Workplane(_profile_plane).slot2D(pill_length_x, pill_width_y)
            .sweep(_flavor_transition_path(), transition="right")
            .translate((0.0, flavor_tube_depth, zone3_z_bottom - 0.5)))


def build_signal_transition_inner_cut() -> cq.Workplane:
    """Ribbon clearance following the lower flavor S bend, above its tube pair."""
    return (cq.Workplane(_profile_plane)
            .center(0.0, signal_lane_center_n - flavor_offset_y_from_water)
            .slot2D(signal_lane_width, signal_lane_depth)
            .sweep(_flavor_transition_path(), transition="right")
            .translate((0.0, flavor_tube_depth, zone3_z_bottom - 0.5)))


def build_signal_transition_ribbon() -> cq.Workplane:
    """Maximum stated ribbon envelope through the lower S bend."""
    return (cq.Workplane(_profile_plane)
            .center(0.0, signal_lane_center_n - flavor_offset_y_from_water)
            .rect(signal_ribbon_max_width, signal_ribbon_max_depth)
            .sweep(_flavor_transition_path(), transition="right")
            .translate((0.0, flavor_tube_depth, zone3_z_bottom - 0.5)))


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


def _gooseneck_path_at_origin(tip_length: float | None = None,
                             *, bend_sweep_rad: float | None = None) -> cq.Workplane:
    """Gooseneck path in path-local (a, b): vertical lift, circular arc,
    tip straight. Origin (s=0) lands in world at
    (0, soda_faucet_tube_y, zone5_z_top)."""
    z_lift = gn_bend1_z_start - zone5_z_top
    tip_length = gn_tip_straight_len if tip_length is None else tip_length
    bend_sweep_rad = _path_total_rot if bend_sweep_rad is None else bend_sweep_rad

    p_bottom = (0.0, 0.0)
    p_bend_start = (0.0, z_lift)

    arc_mid, arc_end, tip_tangent = _arc_from_tangent(
        p_bend_start, (0.0, 1.0), gn_bend1_r, bend_sweep_rad, ccw=False
    )
    tip_end = (arc_end[0] + tip_length * tip_tangent[0],
               arc_end[1] + tip_length * tip_tangent[1])

    path = (
        cq.Workplane(_path_plane)
        .moveTo(*p_bottom)
        .lineTo(*p_bend_start)
        .threePointArc(arc_mid, arc_end)
    )
    if tip_length > 1e-8:
        path = path.lineTo(*tip_end)
    return path.wire()


def _tube_shell_outer_sketch() -> cq.Sketch:
    """Circular neck enclosing the soda, flavor-pair and signal-cable passages."""
    return cq.Sketch().push([(0.0, tube_shell_center_y)]).circle(tube_shell_outer_r)


def _tube_shell_inner_sketch(*, include_signal: bool = True) -> cq.Sketch:
    """Soda circle and flavor pill, optionally including the parallel ribbon lane."""
    pill_straight = pill_length_x - pill_width_y  # [6.35 mm](PILL_STRAIGHT_INNER)
    sketch = (
        cq.Sketch()
        .circle(soda_faucet_hole_diameter / 2.0)
        .push([(0, flavor_offset_y_from_water)])
        .slot(pill_straight, pill_width_y, angle=0, mode="a")
    )
    if include_signal:
        sketch = (sketch.reset().push([(0.0, signal_lane_center_n)])
                  .slot(signal_lane_width - signal_lane_depth, signal_lane_depth,
                        angle=0, mode="a"))
    return sketch.clean()


def _sweep_along_gooseneck(sketch: cq.Sketch) -> cq.Workplane:
    """`sketch` swept along the gooseneck path, placed at the zone-5 seam
    (0, soda_faucet_tube_y, zone5_z_top)."""
    profile = cq.Workplane(_profile_plane).placeSketch(sketch)
    swept = profile.sweep(_gooseneck_path_at_origin(), transition="right")
    return swept.translate((0, soda_faucet_tube_y, zone5_z_top))


def build_display_neck_reference(shrink: float = 0.0) -> cq.Workplane:
    """Constant circular head profile used by its cover, lips and grooves."""
    sketch = cq.Sketch().push([(0.0, tube_shell_center_y)]).circle(
        display_neck_outer_r - shrink)
    return _sweep_along_gooseneck(sketch)


def build_zone6_outer() -> cq.Workplane:
    """Uniform circular stem, bend and dispense tip."""
    return _sweep_along_gooseneck(_tube_shell_outer_sketch())


def build_zone6_inner_cut() -> cq.Workplane:
    """The soda and flavor passages continue to the dispense face."""
    return _sweep_along_gooseneck(_tube_shell_inner_sketch(include_signal=False))


def _signal_neck_path() -> cq.Workplane:
    """Stop the signal lane on the arc where its internal side branch begins."""
    angle = _path_total_rot - math.asin(
        (display_ribbon_join_s - gn_tip_straight_len)
        / (gn_bend1_r + signal_lane_center_n))
    return _gooseneck_path_at_origin(0.0, bend_sweep_rad=angle)


def build_signal_neck_inner_cut() -> cq.Workplane:
    """The signal passage stops inside the head, leaving the outlet face closed."""
    return (cq.Workplane(_profile_plane).center(0.0, signal_lane_center_n)
            .slot2D(signal_lane_width, signal_lane_depth)
            .sweep(_signal_neck_path(), transition="right")
            .translate((0.0, soda_faucet_tube_y, zone5_z_top)))


def build_signal_neck_ribbon() -> cq.Workplane:
    """Maximum ribbon envelope from the lower S bend to the internal side branch."""
    return (cq.Workplane(_profile_plane).center(0.0, signal_lane_center_n)
            .rect(signal_ribbon_max_width, signal_ribbon_max_depth)
            .sweep(_signal_neck_path(), transition="right")
            .translate((0.0, soda_faucet_tube_y, zone5_z_top)))


def _tube_shell_outer_shrunk_sketch(shrink: float) -> cq.Sketch:
    """_tube_shell_outer_sketch offset inward by `shrink` mm (centers fixed)."""
    return cq.Sketch().push([(0.0, tube_shell_center_y)]).circle(tube_shell_outer_r - shrink)


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
        .wire()
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
# Tip frame: s runs up-gooseneck from the tube exit, n points out through
# the display face, and x is world X. The headerless vendor components,
# corrected to the caliper PCB height, clear the real tubes by 0.30064 mm.
# Four small feet pads support the display; the space over the tubes is open.
# The vendor USB-C shell extends beyond the PCB and housing's lower end.
# Bounds use the device's centred XY / feet-Z frame.
display_usb_reference_file = "ESP32-S3-Touch-LCD-1_47_20250411.stp"
display_usb_reference_url = "https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.47/ESP32-S3-Touch-LCD-1.47-2D3D.zip"
display_usb_reference_sha256 = "15fddd5d2b699d0b7c5160f2e11f176a672e7b305604f43a6dbaa30b8cc0059e"
display_usb_reference_bounds = (
    (-4.799962, -22.484226, 0.750479),
    (4.780038, -14.954223, 4.910479),
)
display_usb_half_width = math.ceil(max(abs(row[0]) for row in display_usb_reference_bounds) * 100.0) / 100.0
display_usb_y_range = (math.floor(display_usb_reference_bounds[0][1] * 100.0) / 100.0,
                       math.ceil(display_usb_reference_bounds[1][1] * 100.0) / 100.0)
display_usb_top_z = math.ceil(display_usb_reference_bounds[1][2] * 100.0) / 100.0
dispense_face_thickness = 2.0  # [2 mm](DISPENSE_FACE_T)
display_feet_n = 10.10
display_floor_n = display_feet_n
display_pocket_inset = tube_shell_center_y + display_neck_outer_r - display_feet_n
display_cradle_clearance = 0.25
display_wire_bend_radius = 2.5
display_ribbon_join_s = 46.0
display_ribbon_reference_start_s = display_ribbon_join_s + 0.5
display_ribbon_side_x = -8.2
display_ribbon_side_radius = 8.0
display_ribbon_side_drop = 0.0
display_ribbon_side_lift = 0.40
display_ribbon_side_run_n = 11.10
display_ribbon_pcb_gap = 0.30
display_s_bottom = (dispense_face_thickness - display_usb_y_range[0]
                    - display_housing_length / 2.0)
display_s_top = display_s_bottom + display_housing_length + 2.0 * display_cradle_clearance
_display_housing_center_s = display_s_bottom + display_cradle_clearance + display_housing_length / 2.0
display_face_n = display_feet_n + display_total_depth
display_cosmetic_wall = 1.30
display_cover_top_n = display_face_n + display_cover_over_face + display_cosmetic_wall
display_cover_bottom_n = display_feet_n - 6.8
display_cover_shoulder_n = display_feet_n + 0.5
display_cover_face_width = 27.5
display_cover_end_margin = 1.25
display_cover_face_length = display_s_top + display_cover_end_margin
_display_cover_center_s = display_cover_face_length / 2.0
display_cover_skirt_width = 2.0 * (display_neck_outer_r + display_cover_slip + display_cosmetic_wall)
display_cover_skirt_length = display_cover_face_length + 5.1
display_cover_face_r = 7.25
display_cover_skirt_r = 10.0
display_cover_skirt_rear_s = _display_cover_center_s + display_cover_skirt_length / 2.0
# Rear lower edge: s = s0 + ds_dn * n.
display_cover_rear_rim_s0 = 41.7
display_cover_rear_rim_ds_dn = 0.6
display_head_s_min = 0.0
display_head_s_max = display_cover_skirt_rear_s + 0.2
display_clip_s_bottom = (_display_cover_center_s - display_cover_skirt_length / 2.0
                         + display_cover_skirt_r + _display_snap.END_MARGIN)
display_clip_s_top = (_display_cover_center_s + display_cover_skirt_length / 2.0
                      - display_cover_skirt_r - _display_snap.END_MARGIN)
display_clip_bottom_n = display_cover_bottom_n
display_clip_top_n = display_clip_bottom_n + _display_snap.LIP_HEIGHT
display_clip_lip_radius = display_neck_outer_r - _display_snap.ENGAGEMENT
display_clip_groove_radius = display_clip_lip_radius - _display_snap.RADIAL_SLIP
display_foot_pad_width = 3.0
display_foot_pad_depth = wall_thickness_min
# Factory assembly: place the display in the open cover, approach from the
# outlet at S=-slide, translate along S while lifted, then seat along -N.
display_cartridge_lift_n = 7.5
display_cartridge_slide_s = 60.0
display_loading_travel_n = 25.0
display_foot_envelope_r = math.sqrt(3.0)  # 3 mm across-flats vendor hex standoff.
display_foot_centers = tuple((x, display_s_bottom + display_cradle_clearance
                                  + display_housing_length / 2.0 + y)
                           for x in (-8.5, 8.5) for y in (-19.5, 19.5))
# Viewed from the glass, the cable termination is in the southwest corner.
display_ribbon_terminal_y = -11.0
display_ribbon_terminal_s = _display_housing_center_s + display_ribbon_terminal_y

def _tip_frame():
    """(tube exit, up-gooseneck tangent, outward display normal)."""
    ta, tb = _tan_after_bend2
    tip_end = cq.Vector(0.0, soda_faucet_tube_y - _path_p5[0], zone5_z_top + _path_p5[1])
    return tip_end, cq.Vector(0.0, ta, -tb), cq.Vector(0.0, tb, ta)


def _cradle_prism(half_x: float, s0: float, s1: float, n0: float, n1: float,
                  corner_r: float = 0.0) -> cq.Workplane:
    tip_end, _, n_hat = _tip_frame()
    plane = cq.Plane(origin=tip_end, xDir=cq.Vector(1, 0, 0), normal=n_hat)
    sketch = cq.Sketch().push([(0.0, (s0 + s1) / 2.0)]).rect(2.0 * half_x, s1 - s0)
    if corner_r > 0.0:
        sketch = sketch.reset().vertices().fillet(corner_r)
    return cq.Workplane(plane).workplane(offset=n0).placeSketch(sketch).extrude(n1 - n0)


def _display_world(native: cq.Workplane) -> cq.Workplane:
    """Place a native (x, s, n) solid in the assembled faucet frame."""
    tip_end, _, n_hat = _tip_frame()
    plane = cq.Plane(origin=tip_end, xDir=(1.0, 0.0, 0.0), normal=n_hat)
    return cq.Workplane(obj=native.val().transformShape(plane.rG))


def _display_outline_wire(width: float, length: float, radius: float,
                          n: float, *, center_s: float = _display_cover_center_s) -> cq.Wire:
    """Matched eight-edge rounded outline for the shallow display shroud."""
    h, r = width / 2.0, radius
    a = center_s - length / 2.0
    b = center_s + length / 2.0
    q = r / math.sqrt(2.0)
    return (cq.Workplane("XY").workplane(offset=n)
            .moveTo(-h + r, a).lineTo(h - r, a)
            .threePointArc((h - r + q, a + r - q), (h, a + r))
            .lineTo(h, b - r)
            .threePointArc((h - r + q, b - r + q), (h - r, b))
            .lineTo(-h + r, b)
            .threePointArc((-h + r - q, b - r + q), (-h, b - r))
            .lineTo(-h, a + r)
            .threePointArc((-h + r - q, a + r - q), (-h + r, a))
            .close().val())


def build_display_outer_envelope() -> cq.Workplane:
    """Tapered rounded display shroud."""
    rows = (
        (display_cover_skirt_width, display_cover_skirt_length,
         display_cover_skirt_r, display_cover_bottom_n),
        (display_cover_skirt_width, display_cover_skirt_length,
         display_cover_skirt_r, display_cover_shoulder_n),
        (display_cover_face_width, display_cover_face_length,
         display_cover_face_r, display_cover_top_n),
    )
    loft = _display_world(cq.Workplane(obj=cq.Solid.makeLoft(
        [_display_outline_wire(*row) for row in rows], ruled=False)))
    return loft.intersect(_cradle_prism(
        30.0, display_head_s_min, display_head_s_max + 1.0, -30.0, 40.0))


def build_display_cover_inner_envelope() -> cq.Workplane:
    """Display clearance below the bezel with a vertical rear wall."""
    rows = (
        (display_cover_skirt_width - 2.0 * display_cosmetic_wall,
         50.0, 8.7, display_cover_bottom_n - 1.0),
        (display_cover_skirt_width - 2.0 * display_cosmetic_wall,
         50.0, 8.7, display_cover_shoulder_n),
        (display_housing_width + 2.0 * display_cradle_clearance,
         display_housing_length + 2.0 * display_cradle_clearance,
         display_corner_r + display_cradle_clearance,
         display_face_n + display_cover_over_face),
    )
    loft = _display_world(cq.Workplane(obj=cq.Solid.makeLoft(
        [_display_outline_wire(*row, center_s=_display_housing_center_s) for row in rows], ruled=False)))
    return loft.intersect(_cradle_prism(50.0, -20.0, display_s_top, -30.0, 40.0))


def build_display_neck_clearance() -> cq.Workplane:
    """The shroud's open lip follows the round neck without a square shoe."""
    return build_display_neck_reference(-display_cover_slip)


def build_display_feet_pads() -> cq.Workplane:
    """Four 3 mm square bearing pads under the measured metal feet."""
    solids = []
    h = display_foot_pad_width / 2.0
    for x, s in display_foot_centers:
        solids.append(_cradle_prism(
            h, s - h, s + h, display_feet_n - display_foot_pad_depth,
            display_feet_n).translate((x, 0.0, 0.0)).val())
    return cq.Workplane(obj=cq.Compound.makeCompound(solids))


def build_display_cover_lips() -> cq.Workplane:
    """Two broad seated lips continuous with the cover's side walls."""
    band = _cradle_prism(display_cover_skirt_width / 2.0 + 1.0,
                         display_clip_s_bottom, display_clip_s_top,
                         display_clip_bottom_n, display_clip_top_n)
    inner = build_display_neck_reference(display_neck_outer_r - display_clip_lip_radius)
    return build_display_outer_envelope().intersect(band).cut(inner)


def build_display_retention_grooves() -> cq.Workplane:
    """Side grooves with preload roots, flat floors and retaining shoulders."""
    band = _cradle_prism(display_neck_outer_r + 1.0,
                         display_clip_s_bottom - _display_snap.END_SLIP,
                         display_clip_s_top + _display_snap.END_SLIP,
                         display_clip_bottom_n,
                         display_clip_top_n + _display_snap.BEARING_SLIP)
    core = build_display_neck_reference(display_neck_outer_r - display_clip_groove_radius)
    return band.cut(core)


def _display_cavity() -> cq.Workplane:
    device_opening = _cradle_prism(
        display_neck_outer_r + wall_thickness_min, dispense_face_thickness, display_s_top,
        display_feet_n, display_cover_top_n + 1.0,
    )
    open_channel = _cradle_prism(
        6.75, dispense_face_thickness, display_s_top, 0.0, display_feet_n + 0.1)
    return device_opening.union(open_channel)


def build_display_usb_keepout() -> cq.Workplane:
    """Conservative connector envelope from the vendor STEP, without fit clearance."""
    low, high = display_usb_reference_bounds
    return _cradle_prism(
        (high[0] - low[0]) / 2.0,
        _display_housing_center_s + low[1], _display_housing_center_s + high[1],
        display_floor_n + low[2], display_floor_n + high[2],
    ).translate(((low[0] + high[0]) / 2.0, 0.0, 0.0))


def _display_ribbon_sweep(width: float, depth: float, top_n: float) -> cq.Workplane:
    """The flat ribbon leaves the neck into the open volume below the PCB.

    Sections follow explicit frames: width stays perpendicular to the lateral
    turn, without the sudden ribbon twist of a Frenet frame at an inflection.
    The S bend passes inside the rear foot and reaches the southwest termination.
    """
    origin, along, outward = _tip_frame()
    frames = []

    def natural(s):
        radius = gn_bend1_r + signal_lane_center_n
        square = math.sqrt(radius * radius - (s - gn_tip_straight_len) ** 2)
        return square - gn_bend1_r, -(s - gn_tip_straight_len) / square

    def add(x, s, n, dx, ds, dn):
        point = (x, s, n)
        if not frames or math.dist(frames[-1][0], point) >= 1e-8:
            frames.append((point, (dx, ds, dn)))

    for s in (display_ribbon_reference_start_s,
              (display_ribbon_reference_start_s + display_ribbon_join_s) / 2.0,
              display_ribbon_join_s):
        n, slope = natural(s)
        add(0.0, s, n, 0.0, -1.0, -slope)
    side = math.copysign(1.0, display_ribbon_side_x)
    side_x, radius = abs(display_ribbon_side_x), display_ribbon_side_radius
    angle = math.acos(1.0 - side_x / (2.0 * radius))
    for phase in (0, 1):
        for step in range(13):
            u = angle * step / 12.0
            turn = u if phase == 0 else angle - u
            if phase == 0:
                x = radius * (1.0 - math.cos(u))
                s = display_ribbon_join_s - radius * math.sin(u)
            else:
                x = radius * (1.0 - 2.0 * math.cos(angle) + math.cos(turn))
                s = display_ribbon_join_s - radius * (2.0 * math.sin(angle) - math.sin(turn))
            dx, ds = math.sin(turn), -math.cos(turn)
            n, slope = natural(s)
            fraction = x / side_x
            n += (-display_ribbon_side_drop * fraction ** 4
                  + display_ribbon_side_lift * 4.0 * fraction * (1.0 - fraction))
            dn = (slope * ds - 4.0 * display_ribbon_side_drop * fraction ** 3 * dx / side_x
                  + 4.0 * display_ribbon_side_lift * (1.0 - 2.0 * fraction) * dx / side_x)
            add(side*x, s, n, side*dx, ds, dn)
    x, s0, n0 = frames[-1][0]
    _, ds, dn = frames[-1][1]
    run_in = 3.0
    m0 = run_in * dn / -ds
    for step in range(1, 13):
        t = step / 12.0
        n = ((2*t**3 - 3*t*t + 1)*n0 + (t**3 - 2*t*t + t)*m0
             + (-2*t**3 + 3*t*t)*display_ribbon_side_run_n)
        dn = ((6*t*t - 6*t)*n0 + (3*t*t - 4*t + 1)*m0
              + (-6*t*t + 6*t)*display_ribbon_side_run_n)
        add(x, s0 - run_in*t, n, 0.0, -run_in, dn)
    side_start = s0 - run_in
    pre_rise_s = display_ribbon_terminal_s + display_wire_bend_radius
    for step in range(1, 9):
        add(x, side_start + (pre_rise_s-side_start)*step/8,
            display_ribbon_side_run_n, 0.0, -1.0, 0.0)
    for step in range(1, 17):
        turn = math.pi / 2.0 * step / 16.0
        s = pre_rise_s - display_wire_bend_radius * math.sin(turn)
        n = display_ribbon_side_run_n + display_wire_bend_radius * (1.0 - math.cos(turn))
        add(x, s, n, 0.0, -math.cos(turn), math.sin(turn))
    if top_n <= frames[-1][0][2]:
        raise ValueError("ribbon termination must reach above its smooth PCB-side bend")
    add(x, s, top_n, 0.0, 0.0, 1.0)

    wires = []
    for (x, s, n), (dx, ds, dn) in frames:
        centre = origin + cq.Vector(x, 0, 0) + along.multiply(s) + outward.multiply(n)
        tangent = cq.Vector(dx, 0, 0) + along.multiply(ds) + outward.multiply(dn)
        cross = cq.Vector(-ds, 0, 0) + along.multiply(dx)
        if cross.Length < 1e-8:
            cross = cq.Vector(1, 0, 0)
        section = cq.Workplane(cq.Plane(origin=centre, xDir=cross, normal=tangent))
        wires.append(section.rect(width, depth).val())
    return cq.Workplane(obj=cq.Solid.makeLoft(wires))


def build_display_ribbon_transition() -> cq.Workplane:
    """Maximum SIG-6 envelope up to the factory wire fan-out beside the PCB."""
    return _display_ribbon_sweep(signal_ribbon_max_width, signal_ribbon_max_depth,
                                 display_feet_n + _faucet_interface.display_pcb_bottom_z
                                 - display_ribbon_pcb_gap)


def build_lever_overhead_clearance() -> cq.Workplane:
    """Circular overhead relief above the lever's resting top."""
    front_y = fill_y_min - math.sqrt(
        back_arch_r ** 2 - (lever_rest_top_z - back_arch_center_z) ** 2)
    front_angle = math.atan2(lever_rest_top_z - back_arch_center_z,
                             front_y - fill_y_min)
    rear_z = back_arch_center_z + math.sqrt(
        back_arch_r ** 2 - (lever_clearance_y_back - fill_y_min) ** 2)
    rear_angle = math.atan2(rear_z - back_arch_center_z,
                            lever_clearance_y_back - fill_y_min)
    mid_angle = (front_angle + rear_angle) / 2.0
    mid = (fill_y_min + back_arch_r * math.cos(mid_angle),
           back_arch_center_z + back_arch_r * math.sin(mid_angle))
    return (_vertical_plane(-lever_clearance_x_half)
            .moveTo(front_y, lever_rest_top_z)
            .threePointArc(mid, (lever_clearance_y_back, rear_z))
            .lineTo(lever_clearance_y_back, lever_rest_top_z)
            .lineTo(front_y, lever_rest_top_z).wire()
            .extrude(2.0 * lever_clearance_x_half))


def build_lever_front_clearance() -> cq.Workplane:
    """Open central span ahead of the rounded neck cap, above the resting lever."""
    opening = cq.Solid.makeBox(
        2.0 * lever_clearance_x_half, fill_y_min - lever_insertion_front_y,
        zone5_z_top - lever_rest_top_z,
        cq.Vector(-lever_clearance_x_half, lever_insertion_front_y, lever_rest_top_z))
    cap = cq.Solid.makeCylinder(
        shell_outer_r, zone5_z_top - lever_rest_top_z,
        cq.Vector(0.0, zone45_front_y + shell_outer_r, lever_rest_top_z))
    return cq.Workplane(obj=opening.cut(cap))


def build_lever_clearance() -> cq.Workplane:
    """Lever travel, overhead relief and straight front insertion corridor."""
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union

    clearance = lever_fit_clearance
    pivot_y = 1.5
    pivot_z = zone2_z_top + 7.0
    travel_deg = 18
    x_half = lever_clearance_x_half
    profile = (
        (-42.0, zone2_z_top + 10.0),
        (-42.0, lever_rest_top_z),
        (lever_rest_back_y, lever_rest_top_z),
        (lever_rest_back_y, zone2_z_top + 1.0),
        (-6.0, zone2_z_top + 1.0),
        (-6.0, zone2_z_top + 4.5),
    )
    poses = []
    for angle in range(travel_deg + 1):
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        poses.append([(pivot_y + c * (y - pivot_y) - s * (z - pivot_z),
                       pivot_z + s * (y - pivot_y) + c * (z - pivot_z))
                      for y, z in profile])
    # The complete lever body enters from the front before its donor attachment closes.
    regions = [Polygon(pose) for pose in poses]
    regions.append(box(lever_insertion_front_y, zone2_z_top + 1.0, -5.9, lever_rest_top_z))
    # Sweep each edge between adjacent poses in the planar profile before extruding.
    # The 0.005 mm allowance covers the <0.002 mm one-degree arc sag and simplification.
    for before, after in zip(poses, poses[1:]):
        for i in range(len(profile)):
            j = (i + 1) % len(profile)
            regions.append(Polygon((before[i], before[j], after[j], after[i])).buffer(0))
    envelope_allowance = clearance + lever_sweep_allowance
    outline = unary_union(regions).simplify(0.001).buffer(envelope_allowance, join_style=2)
    # Connect the donor's open plateau to the rest-lever corridor. This region
    # stays inside the donor footprint and opens the complete space under the
    # lever; the side arch bores and rear structural wall retain their stock.
    plateau_join = box(-westbrass_bore_rect_long_y / 2.0, zone2_z_top - 0.01,
                       lever_clearance_y_back,
                       zone2_z_top + 1.0 - envelope_allowance + 0.01)
    outline = outline.union(plateau_join)
    return (_vertical_plane(-x_half).polyline(list(outline.exterior.coords)[:-1]).close()
            .extrude(2.0 * x_half)
            .union(build_lever_overhead_clearance())
            .union(build_lever_front_clearance()))


def _tube_shell_outer_section(z_bottom: float, z_height: float) -> cq.Workplane:
    """Circular tube-shell cross-section extruded vertically over the Z range."""
    return (
        _horizontal_plane(z_bottom)
        .moveTo((0.0, soda_faucet_tube_y + tube_shell_center_y))
        .circle(tube_shell_outer_r)
        .extrude(z_height)
    ).unwrap()


def _tube_shell_inner_section(z_bottom: float, z_height: float) -> cq.Workplane:
    """The complete tube and ribbon passage extruded vertically."""
    return (cq.Workplane(_profile_plane).workplane(offset=z_bottom)
            .placeSketch(_tube_shell_inner_sketch()).extrude(z_height)
            .translate((0.0, soda_faucet_tube_y, 0.0)))


# ============================================================
# PUBLIC SHELL BUILDERS
# ============================================================

def build_shell() -> cq.Workplane:
    """Faucet shell — full reference solid (un-split), all zones
    unioned, with the display cradle on the dispense tip. Split for
    printing into two pieces at the gooseneck's angular midpoint:
    build_shell_base and build_shell_tip."""
    outer_parts = [
        build_lower_outer().val(),
        build_zone6_outer().val(),
        build_display_feet_pads().val(),
    ]
    outer = cq.Workplane(obj=outer_parts[0].fuse(*outer_parts[1:]))
    inner_parts = [
        build_zone1_inner_cut().val(),
        build_base_pod_holes().val(),
        build_zone2_inner_cut().val(),
        build_zone3_inner_cut().val(),
        build_zone6_inner_cut().val(),
        build_signal_neck_inner_cut().val(),
        build_lever_clearance().val(),
        _display_cavity().val(),
        build_display_retention_grooves().val(),
        build_lower_signal_lane().val(),
        build_lower_soda_inner_cut().val(),
        build_flavor_transition_inner_cut().val(),
        build_signal_transition_inner_cut().val(),
    ]
    part = outer.val()
    for cutter in inner_parts:
        part = part.cut(cutter)
    return cq.Workplane(obj=part.clean())


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
    plug = plug_outer.cut(build_zone6_inner_cut()).cut(build_signal_neck_inner_cut())
    return full.intersect(above_junction).union(plug)


def print_height(shape: cq.Workplane, build_rot: float) -> float:
    """Height of `shape` on the bed when built along the gooseneck tangent
    at path rotation `build_rot` — the piece's print orientation."""
    return shape.rotate((0, 0, 0), (1, 0, 0), -math.degrees(build_rot)).val().BoundingBox().zlen


# Absolute millimetre deflection and angular deflection of the printable surface.
piece_mesh_tol = 0.005
piece_mesh_angle = 0.05


def piece_mesh(solid) -> trimesh.Trimesh:
    """Absolute-tolerance print mesh, on a copy without cached triangulation."""
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_REVERSED
    from OCP.TopLoc import TopLoc_Location

    solid = solid.val() if hasattr(solid, "val") else solid
    meshed = solid.copy(mesh=False)
    triangulator = BRepMesh_IncrementalMesh(
        meshed.wrapped, piece_mesh_tol, False, piece_mesh_angle, False)
    if not triangulator.IsDone():
        raise ValueError("the absolute-tolerance print triangulation did not finish")
    points, tris = [], []
    for face in meshed.Faces():
        location = TopLoc_Location()
        poly = BRep_Tool.Triangulation_s(face.wrapped, location)
        if poly is None or poly.NbTriangles() == 0:
            raise ValueError("a printable face has no triangulation")
        offset = len(points)
        transform = location.Transformation()
        for i in range(1, poly.NbNodes()+1):
            point = poly.Node(i).Transformed(transform)
            points.append((point.X(), point.Y(), point.Z()))
        for i in range(1, poly.NbTriangles()+1):
            a, b, c = poly.Triangle(i).Get()
            if face.wrapped.Orientation() == TopAbs_REVERSED:
                b, c = c, b
            tris.append((offset+a-1, offset+b-1, offset+c-1))
    mesh = trimesh.Trimesh(vertices=points, faces=tris, process=True)
    mesh.merge_vertices()
    return mesh


def write_bed_file(solid, path):
    """The printed surface, checked as serialized STL before replacing the bed file."""
    path = Path(path)
    mesh = piece_mesh(solid)
    data = mesh.export(file_type="stl")
    written = trimesh.load_mesh(io.BytesIO(data), file_type="stl")
    loose = _flute_skin.non_manifold_edges(written)
    print(f"-> {path.name}  ({len(mesh.faces)} facets, "
          f"{'watertight' if written.is_watertight else 'NOT WATERTIGHT'})")
    if loose or not written.is_watertight:
        raise ValueError(
            f"{path.name}: a slicer refuses this — {loose} non-manifold edge(s), "
            f"watertight={written.is_watertight}, over {len(written.faces)} facets")
    path.write_bytes(data)
    return mesh


def main():
    out_dir = Path(__file__).resolve().parent
    full = build_shell()
    base = build_shell_base(full)
    tip = build_shell_tip(full)
    for name, shape in (("shell", full), ("base", base), ("tip", tip)):
        if not shape.val().isValid() or len(shape.val().Solids()) != 1:
            raise ValueError(f"{name}: expected one valid printable solid")
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
    write_bed_file(base, out_dir / "faucet-shell-base.stl")
    write_bed_file(tip, out_dir / "faucet-shell-tip.stl")

    variables = {
        "DISPENSE_FACE_T": f"{dispense_face_thickness:g} mm",
        "NECK_DIAMETER": f"{2.0 * tube_shell_outer_r:.3f} mm",
        "FOOT_WIDTH": f"{foot_width:g} mm",
        "FOOT_DEPTH": f"{foot_depth:g} mm",
        "PLATE_T": f"{above_counter_plate_thickness:g} mm",
        "PEDESTAL_H": f"{base_pedestal_height:g} mm",
        "BASE_INSERT_Z": f"{base_insert_bottom_z:g} mm",
        "BASE_INSERT_L": f"{base_insert_length:g} mm",
        "BASE_CBORE_D": f"{base_pod_counterbore_dia:g} mm",
        "BASE_CBORE_DEPTH": f"{base_screw_counterbore_depth:g} mm",
        "BASE_SCREW_L": f"{base_screw_length:g} mm",
        "BASE_X": f"{base_pod_center_x:g}",
        "BASE_Y": f"{base_pod_center_y:g}",
        "BASE_FRONT_Y": f"{base_pod_front_center_y:g}",
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
        "SHOW_WALL": f"{show_wall:.4g} mm",
        "PRINT_LAYER": f"{print_layer_height:.4g} mm",
        "PRINT_BEAD": f"{print_bead_width:.4g} mm",
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
        "SHELL_RECT_X_HALF": f"{shell_rect_x_half:.4g} mm",
        "SHELL_RECT_Y_MAX": f"{shell_rect_y_max:.4g} mm",
        "SHELL_RECT_Y_MIN": f"{shell_rect_y_min:.4g} mm",
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
        "SPLIT_PLUG_WALL": f"{split_plug_wall:.4g} mm",
        "SPLIT_SLIP": f"{split_slip:.4g} mm",
        "DISPLAY_INSTALL_LIFT": f"{display_cartridge_lift_n:g} mm",
        "PRINT_TILT": f"{math.degrees(print_base_tilt_rad):.0f}°",
        "MAX_PRINT_OVERHANG": f"{math.degrees(max_print_overhang_rad):.0f}°",
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

    # The bounds this file states about its own constants, read at import. `check_show_faces.py`
    # is where they are held for the board; this is the reading the run itself leaves.
    print()
    _bounds.report()


if __name__ == "__main__":
    main()
