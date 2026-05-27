"""Touch-Flo shell — printed shroud that wraps the harvested faucet
body, the flavor tubes, and the lever swing volume. Sits on top of
the touch-flo-mounting-plate.

Frame: world +Y is height (up), world ±X is lateral (symmetric across
the X=0 plane), world +Z is forward (dispense direction — the gooseneck
arcs toward +Z, where the user's glass sits). The body's threaded shank
runs along world Y at world (X, Z) = (0, 0).

Grown bottom-up, one zone at a time."""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
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
    pill_width_z,
    flavor_tube_depth,
)
from docgen import substitute_md, substitute_py_comments
from world_workplane import WorldWorkplane, xz_plane_y_up


# ============================================================
# WORLD FRAME PRIMITIVES
# ============================================================

# Horizontal cross-sections (extruded along world +Y for the vertical
# zones) use WorldWorkplane(xz_plane_y_up) so (world_x, world_z) tuples
# pass through unchanged and `.extrude(h)` extrudes +h along world +Y.
#
# Vertical cross-sections (extruded along world ±X for the lateral
# zones — arches, lever clearance, zone 4.5 lid) use the custom plane
# below: normal=+X, local-X=world+Y (height), local-Y=world+Z (depth).
# Drawing a profile writes (height, depth) tuples.

def _horizontal_plane(y_offset):
    """WorldWorkplane on the XZ plane at world Y = y_offset, +Y normal.
    Coordinates are (world_x, world_z); .extrude(h) extrudes +h along +Y."""
    return WorldWorkplane(xz_plane_y_up).workplane(offset=y_offset)


_yz_plane_x_normal = cq.Plane(
    origin=(0, 0, 0),
    xDir=(0, 1, 0),       # local +X = world +Y (height)
    normal=(1, 0, 0),     # extrude along world +X (lateral)
)


def _vertical_plane(x_offset):
    """Workplane on the YZ plane at world X = x_offset, +X normal.
    Local-X = world +Y (height); Local-Y = world +Z (depth).
    Drawing writes (height, depth) tuples; .extrude(h) extrudes +h
    along world +X."""
    return cq.Workplane(_yz_plane_x_normal).workplane(offset=x_offset)


# Shell shifted -Z (toward the back) so the +Z edge extends past the
# wider 1/4" flavor cutout with a real wall.
shell_center_x = 0.0
shell_center_z = -3.175


# ZONE 1 — first 13 mm; body is a full Ø 31.5 mm cylinder here

zone1_y_bottom = 0.0
zone1_y_top = 13.0
zone1_height = zone1_y_top - zone1_y_bottom  # 13 mm

# Body-to-bore slip-fit clearance — applied per-side (per-direction)
# uniformly: ±X faces, ±Z faces, radial cylinder, AND face-to-face Y
# interfaces all get the same gap.
bore_clearance = 0.25  # mm per side

# Body bore (cylinder) — [32 mm](BODY_BORE_D), body OD 31.5 mm + 2 × clearance per side.
body_bore_diameter = 31.5 + 2.0 * bore_clearance
body_bore_x = 0.0
body_bore_z = 0.0

# Flavor-tube pill — sized for 1/4" OD LLDPE flavor tubes (6.35 mm OD),
# tangent to the body's -Z face (Z=-15.75) and tangent to each other at X=0.
# Geometry imported from _touch_flo_interface (single source of truth
# across shell / mounting plate / gasket / under-counter plate):
#   flavor_tube_od, flavor_tube_x_offset, flavor_tube_hole_dia,
#   pill_length_x, pill_width_z, flavor_tube_depth.
# [13.4 mm](PILL_L) pill long axis (X) = 2 × x_offset + hole_dia.
# [7.05 mm](PILL_W) pill short axis (Z) = hole_dia.
flavor_pill_center = (0.0, -flavor_tube_depth)

# [14.53 mm](FLAVOR_PILL_Z_PLUS) — flat +Z edge of the flavor pill
# cutout in zones 1-4. Max of (natural pill +Z edge, body-bore -Z at
# corner X). At 1/4" tubes the bore intercept binds — pulling the flat
# edge toward -Z onto the bore wall closes off the thin sliver between
# pill and bore at the cutout's X corners (±pill_length_x/2).
flavor_pill_z_plus_edge = max(
    -flavor_tube_depth + pill_width_z / 2.0,
    -math.sqrt((body_bore_diameter / 2.0) ** 2 - (pill_length_x / 2.0) ** 2),
)


# SHELL OUTER
#
# Outer-cylinder radius = wall_thickness_min beyond whichever extreme
# is farthest from shell center — the body bore's +Z edge or the
# flavor pill's -Z edge.
wall_thickness_min = 3.0
_body_bore_farthest_from_shell_center = (
    (body_bore_z - shell_center_z) + body_bore_diameter / 2.0
)  # = 19.175 mm
_pill_farthest_from_shell_center = (
    shell_center_z - (-flavor_tube_depth - pill_width_z / 2.0)
)  # = 19.275 mm at flavor_tube_hole_dia = 7.05
# [22.27 mm](SHELL_OUTER_R) outer-cylinder radius.
shell_outer_r = (
    max(_body_bore_farthest_from_shell_center, _pill_farthest_from_shell_center)
    + wall_thickness_min
)


# ZONE 2 — cylinder → rectangle transition + rect column

zone2_y_bottom = zone1_y_top  # 13.0
zone2_y_top = 39.0  # body plateau
zone2_height = zone2_y_top - zone2_y_bottom  # 26.0

# Body rectangle dimensions (mirrored from valve-body-reference)
body_rect_long_z = 31.5  # depth axis
body_rect_short_x = 17.0  # lateral axis

# Body bore in zone 2 — body rect + clearance per side
body_bore_rect_long_z = body_rect_long_z + 2.0 * bore_clearance  # 32.0
body_bore_rect_short_x = body_rect_short_x + 2.0 * bore_clearance  # 17.5

# Cove transition fillet (matches the body's transition_fillet_r)
cove_r = 6.0

# Bore Y transitions lift by bore_clearance above the body's Y
# transitions so face-to-face Y interfaces get the same per-side
# clearance as ±X and ±Z.
zone2_bore_y_bottom = zone1_y_top + bore_clearance  # 13.25

# Outer surface lifts by wall_thickness_min + bore_clearance above the
# body's cylinder top, leaving a 3 mm cylindrical shell wall directly
# above the body cyl top face before the cove transition begins.
shell_outer_lip = wall_thickness_min + bore_clearance  # 3.25
zone1_outer_y_top = zone1_y_top + shell_outer_lip  # 16.25
zone2_outer_y_bottom = zone1_outer_y_top  # 16.25


# LEVER SWING CLEARANCE — chamfer wedge cut into the top +Z corner of
# the rect column, where the pressed lever's taper passes through.
#
# Two anchor points define the wedge (slope falls out of them):
#   1. +Z end: outer rect face at Y = zone2_y_top − lever_ramp_depth.
#   2. -Z end: the bore-cylinder tangent at the cut's X half-span (the
#      wedge ends exactly where the wall ends at the lever's X-edge —
#      further -Z is inside the bore, no wall to cut).
#
# tangent_overshoot pushes the -Z end a hair past the exact tangent so
# the cut terminates cleanly through the bore wall rather than at a
# coincident-edge sliver.

lever_x_half = 6.5
lever_clearance_x_half = lever_x_half + bore_clearance  # 6.75
lever_ramp_depth = 1.0
tangent_overshoot = 0.002

shell_rect_z_half = shell_outer_r  # 22.175
shell_rect_x_half = body_bore_rect_short_x / 2.0 + wall_thickness_min  # 11.75
shell_rect_z_width = 2.0 * shell_rect_z_half
shell_rect_x_width = 2.0 * shell_rect_x_half
shell_rect_z_max = shell_center_z + shell_rect_z_half  # +19.0 (toward user)
shell_rect_z_min = shell_center_z - shell_rect_z_half  # -25.35 (toward back)

lever_ramp_z_max = shell_center_z + shell_outer_r  # +19, outer rect face +Z side
_bore_z_at_lever_x = math.sqrt(
    (body_bore_diameter / 2.0) ** 2 - lever_clearance_x_half ** 2
)  # ≈ 14.5061 — bore-cyl tangent at the cut's X half-span
lever_ramp_z_start = _bore_z_at_lever_x + tangent_overshoot  # ≈ 14.5081


# ZONE 3 — Arch wraps (two wings at ±X)
#
# Body arches: 1.5 mm wide ridges at X = ±7.75, full Z width (±15.75),
# profile in (Z, Y) = 2 mm rectangular foot from Y=39→41 plus a 3-point
# arc through (∓15.75, 41) and (0, 46).
#
# Shell wraps each arch with WALL+GAP outside (top, +X/-X outer face,
# Z foot ends). Plateau between the arches (X ∈ ±6.75) is OPEN — each
# shell wing's plateau-side X face IS the bore's plateau-side X face.

zone3_y_bottom = zone2_y_top  # 39

arch_y_base = 41.0  # body foot top
arch_y_peak = 46.0  # body arc peak
body_arch_inner_x = 7.0
body_arch_outer_x = 8.5

shell_arch_bore_inner_x = body_arch_inner_x - bore_clearance  # 6.75
shell_arch_bore_outer_x = body_arch_outer_x + bore_clearance  # 8.75
shell_arch_bore_y_foot_top = arch_y_base + bore_clearance  # 41.25
shell_arch_bore_y_peak = arch_y_peak + bore_clearance  # 46.25

shell_arch_y_foot_top = arch_y_base + shell_outer_lip  # 44.25
shell_arch_y_peak = arch_y_peak + shell_outer_lip  # 49.25
wing_inner_x = shell_arch_bore_inner_x  # 6.75
wing_outer_x = shell_rect_x_half  # 11.75

# ZONE 3 — plateau fill (between the wings, Z ≤ fill_z_max). Fills the
# plateau region behind the back third of the water tube, matching the
# wings' arch profile so the shell reads as one continuous swept arch
# shape across the back.
water_tube_z = -8.875
# 3/8" LLDPE — sealed in the body's 10.0 mm port via a printed TPU
# bushing (see ../touch-flo-tpu-o-ring/). The 3/8" OD is the 3-tube
# dispense spout's center tube INSIDE the faucet head — NOT the
# supply line. The harvested Westbrass R2031-NL-62 valve body IS the
# 1/4"→3/8" adapter; the 3/8" tube only exists above this port,
# internal to the head.
water_tube_od = 0.375 * 25.4  # 9.525
# [10.22 mm](WATER_HOLE_D) water bore = OD + 2 × clearance per side + 0.20 mm slack.
water_hole_diameter = water_tube_od + 2.0 * bore_clearance + 0.20

# 1/4" LLDPE flavor tube. The flavor tube butts up against the water
# tube at the dispense point. Each flavor tube sits at
# X=±flavor_tube_x_offset (touching each other along X), so the
# Z-tangency at the dispense point is Pythagorean:
#   (post_bend_z − water_tube_z)² + x_offset² = (r_water + r_flavor)²
# The flavor tubes sit BEHIND the water tube (more -Z) at the dispense
# point — opposite sign of the bend offset.
flavor_tube_post_bend_z = water_tube_z - math.sqrt(
    (water_tube_od / 2.0 + flavor_tube_od / 2.0) ** 2
    - flavor_tube_x_offset ** 2
)  # ≈ -16.150

fill_z_max = -10.46  # back third of water tube (Z ≤ -10.46)


# ZONE 4 — rect column continuation above the arch (water tube +
# flavor pill cutouts), from the arch foot up to zone4_y_top.
zone4_y_bottom = shell_arch_y_foot_top  # 44.25
# Zone 4 top clears the lever's pressed-down envelope by ≈3.5 mm above
# the pressed-lever head corner (Z=-6.78, Y=54.024) — that corner sits
# inside zone 5's water-circle outer outline (centered at Z=-8.875,
# R=9.0125), so zone 5's bottom must be above it.
zone4_y_top = 57.5
zone4_height = zone4_y_top - zone4_y_bottom  # 13.25


# ZONE 5 — tube wrapper above the lever. Above zone 4 the shell
# wraps just the tubes (water cyl bore + flavor pill bore, each +
# 3 mm wall), straight-extruded vertically. This zone extends in +Z
# past fill_z_max — safe because we're above the lever's reach.
zone5_y_bottom = zone4_y_top  # 57.5
zone5_y_top = zone4_y_top + 10.0  # 67.5
zone5_height = zone5_y_top - zone5_y_bottom  # 10
zone5_wall = wall_thickness_min + 1

# Tube-shell cross-section vocabulary — shared by zone 5's vertical
# extrusion and zone 6's sweep along the gooseneck path.
#
# Water and flavor share the same outer X half-width — the larger of
# (water bore + wall) and (flavor pill + wall) — so the cross-section's
# +X and -X outer apexes meet at the same X across the Z range. Each
# side's Z width stays at natural: extreme +Z (around the water bore)
# and extreme -Z (around the flavor pill) are both zone5_wall. The
# "stretch" is only in X (the smaller side picks up extra wall thickness
# on its X apex); the Z side walls don't thicken.
tube_shell_water_r_outer = water_hole_diameter / 2.0 + zone5_wall   # 9.0125
tube_shell_pill_x_half_outer = pill_length_x / 2.0 + zone5_wall
tube_shell_x_half_outer = max(tube_shell_water_r_outer, tube_shell_pill_x_half_outer)
tube_shell_x_outer = 2.0 * tube_shell_x_half_outer
# Offset from water tube to flavor pill along world Z. Negative — flavor
# sits BEHIND water.
flavor_offset_z_from_water = flavor_tube_post_bend_z - water_tube_z  # ≈ -7.275


# ZONE 6 — gooseneck wrapper around the bent dispense tubes. Pure
# continuation of zone 5's cross-section along a bent path above the
# lever-swing envelope.
#
# Path (in the depth-height plane, origin at the zone 5 / zone 6 seam):
#   1. vertical lift from Y=0 up to Y=gn_bend1_y_start − zone5_y_top
#   2. bend 1 — gn_bend1_sweep_rad at R = gn_bend1_r, bending toward +Z
#   3. gn_mid_straight_len angled straight
#   4. bend 2 — gn_bend2_sweep_rad at R = gn_bend2_r
#   5. gn_tip_straight_len tip
#
# The flavor pill's -Z offset is carried in the LOCAL frame of the
# sweep, so as the tangent rotates through each bend the pill traces a
# parallel-offset arc at the larger radius — matching the actual flavor
# tubes' centerlines.
#
# Mirrors constants in `faucet-assembly` — if the assembly's gooseneck
# moves, both files update.

gn_bend1_r = 30.0
gn_bend2_r = 40.0
gn_bend1_sweep_rad = math.radians(30.0)
gn_bend2_sweep_rad = math.radians(110.0)
# 35 mm above the lever rest top (at zone2_y_top + 13 = 52).
gn_bend1_y_mid = zone2_y_top + 48.0  # 87
gn_bend1_y_start = (
    gn_bend1_y_mid
    - gn_bend1_r * math.sin(gn_bend1_sweep_rad / 2.0)
)  # ≈ 79.24
gn_mid_straight_len = 115.0
gn_tip_straight_len = 25.0


# SPLITS — the shell prints in THREE pieces, mating at two 20 mm slip-fit
# joints along the gooseneck:
#
#   SPLIT A: angled-spout ↔ upper-bend (end of mid-straight / start of bend 2).
#     - Female SOCKET on the angled-spout (bottom): 2 mm outer wall over
#       the top 20 mm of the spout; original bores absorbed into the
#       socket cavity.
#     - Male PLUG on the upper-bend (middle, bottom end): 20 mm of the
#       spout cross-section offset 2 mm INWARD; original bores carried
#       through so the tubes pass continuously across the joint.
#     - MATING FACES: planes perpendicular to the angled-spout's
#       centerline tangent. Junction plane at the end of the mid-straight;
#       overlap plane 20 mm back along the same tangent.
#
#   SPLIT B: upper-bend ↔ dispense-tip (end of bend 2 / start of tip).
#     - Same joint pattern: female SOCKET on the upper-bend (middle, top
#       end); male PLUG on the dispense-tip (top).
#     - The upper-bend is a 110° arc at R=gn_bend2_r, so the 20 mm
#       overlap is measured along the ARC — both pieces in this zone
#       follow the curve. The female cavity and the male plug are both
#       swept along the last `split_overlap_len / gn_bend2_r` rad
#       (≈ 28.65°) of bend 2.
#     - MATING FACES: cross-section perpendicular to the bend's tangent
#       at each end of the sub-arc. The junction-end face is also
#       perpendicular to the tip's tangent (they coincide there).
#
#   FIT (both joints): exactly coincident — male OD ≡ female ID in CAD.
#   Slip clearance comes from print tolerance.

# Per-joint, per-side overlap depth (mm along the spout / arc) and
# resulting wall thickness (mm). The "wall" parameter has different
# meanings on each side: on the female it's the remaining outer-shell
# thickness around the cavity; on the male it's the radial thickness of
# the plug material between the bore OD and the plug OD. Both map onto
# the same `shrink` (inward offset of the outer cross-section):
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

# Mid-straight tangent in the path-local depth-height plane (local 2D
# axes match world (Z, Y)) — rotation of (0, 1) CCW by gn_bend1_sweep_rad.
# Points UP the spout (toward bend 2). The bend rotates toward +Z, so
# the +Z component of the tangent grows positive.
_mid_tan_zy = (math.sin(gn_bend1_sweep_rad), math.cos(gn_bend1_sweep_rad))

# Cutting-plane normal for SPLIT A in world (X=0; centerline is in Y-Z).
# (X, Y, Z) tuple. The plane is perpendicular to the tangent.
split_normal = (0.0, _mid_tan_zy[1], _mid_tan_zy[0])

# End of mid-straight (= SPLIT A junction) in world coords. Closed-form
# continuation of _gooseneck_path_at_origin's math: bend-1-end +
# gn_mid_straight_len along the mid-straight tangent.
_bend1_end_zy = (
    gn_bend1_r * (1.0 - math.cos(gn_bend1_sweep_rad)),
    (gn_bend1_y_start - zone5_y_top) + gn_bend1_r * math.sin(gn_bend1_sweep_rad),
)
split_junction_z = water_tube_z + _bend1_end_zy[0] + gn_mid_straight_len * _mid_tan_zy[0]
split_junction_y = zone5_y_top + _bend1_end_zy[1] + gn_mid_straight_len * _mid_tan_zy[1]

# Bottom of SPLIT A's overlap zone for each side (socket = female cavity
# in the bottom piece; plug = male tongue on the middle piece). Females
# and males have asymmetric depths — see split_*_overlap_len above.
split_a_socket_overlap_z = split_junction_z - split_a_socket_overlap_len * _mid_tan_zy[0]
split_a_socket_overlap_y = split_junction_y - split_a_socket_overlap_len * _mid_tan_zy[1]
split_a_plug_overlap_z = split_junction_z - split_a_plug_overlap_len * _mid_tan_zy[0]
split_a_plug_overlap_y = split_junction_y - split_a_plug_overlap_len * _mid_tan_zy[1]


# SPLIT B geometry — bend↔tip joint. Halfspace cuts don't work here:
# the junction plane (perpendicular to the tip's tangent) tilts so
# steeply through the model that an "above junction" halfspace clips a
# sliver of the mid-straight's lower end (≈+1.7 mm into the +tan2
# halfspace despite being on the back side of the path). Affected
# regions are isolated with CUTTING SOLIDS instead — fresh sweeps along
# the dispense-tip path and the last-20-mm bend-2 sub-arc.
#
# All `_path_*` constants below are in path-local 2D coords (local axes
# match world (Z, Y), X=0, origin at world (0, zone5_y_top, water_tube_z)),
# forming a closed-form re-derivation of `_gooseneck_path_at_origin`'s
# waypoint math so the sub-sweep paths align exactly with the full sweep
# through the joint.

# Bend-2 sub-arc covering the last overlap_len mm of bend 2 — separate
# arcs for the female socket (cut out of the middle piece) and the male
# plug (built up on the top piece).
split_b_socket_angle_rad = split_b_socket_overlap_len / gn_bend2_r
split_b_plug_angle_rad = split_b_plug_overlap_len / gn_bend2_r

# Cumulative path rotations (from the path origin's +Y tangent, CCW in
# the depth-height plane — toward +Z).
_path_total_rot = gn_bend1_sweep_rad + gn_bend2_sweep_rad  # rotation at end of bend 2
_path_socket_start_rot = _path_total_rot - split_b_socket_angle_rad
_path_socket_mid_rot = _path_total_rot - split_b_socket_angle_rad / 2.0
_path_plug_start_rot = _path_total_rot - split_b_plug_angle_rad
_path_plug_mid_rot = _path_total_rot - split_b_plug_angle_rad / 2.0

# Tangent unit-vectors in path-local (z, y) (= world (Z, Y); X=0).
# Tangent at rotation r = rotate((0, 1), r) toward +Z = (sin r, cos r).
_tan_after_bend1 = (math.sin(gn_bend1_sweep_rad), math.cos(gn_bend1_sweep_rad))
_tan_after_bend2 = (math.sin(_path_total_rot), math.cos(_path_total_rot))
_tan_at_socket_start = (
    math.sin(_path_socket_start_rot), math.cos(_path_socket_start_rot),
)
_tan_at_plug_start = (
    math.sin(_path_plug_start_rot), math.cos(_path_plug_start_rot),
)

# Path-local waypoints, working forward from the path origin.
_path_y_lift = gn_bend1_y_start - zone5_y_top
_path_p2 = (  # end of bend 1 / start of mid-straight
    gn_bend1_r * (1.0 - math.cos(gn_bend1_sweep_rad)),
    _path_y_lift + gn_bend1_r * math.sin(gn_bend1_sweep_rad),
)
_path_p3 = (  # end of mid-straight / start of bend 2 (= SPLIT A junction)
    _path_p2[0] + gn_mid_straight_len * _tan_after_bend1[0],
    _path_p2[1] + gn_mid_straight_len * _tan_after_bend1[1],
)
# Bend-2 center: from p3 step gn_bend2_r perpendicular-right-of-tangent
# in the (Z, Y) plane (bending toward +Z = CCW perpendicular for the
# +Z-curving bend). CCW perp of tan1 = (-tan1_y, tan1_x); center sits
# OPPOSITE the bend, so it's p3 + (+tan1_y, -tan1_x) * R
# = p3 + (cos θ1, -sin θ1) * R.
_path_center_bend2 = (
    _path_p3[0] + gn_bend2_r * math.cos(gn_bend1_sweep_rad),
    _path_p3[1] - gn_bend2_r * math.sin(gn_bend1_sweep_rad),
)
# Position on bend 2's arc at cumulative rotation r:
#   center + gn_bend2_r * (-cos r, sin r).
_path_p4 = (  # end of bend 2 / start of tip (= SPLIT B junction)
    _path_center_bend2[0] - gn_bend2_r * math.cos(_path_total_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_total_rot),
)
_path_socket_start = (  # bend-2 point split_b_socket_overlap_len arc-length before p4
    _path_center_bend2[0] - gn_bend2_r * math.cos(_path_socket_start_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_socket_start_rot),
)
_path_socket_mid = (  # midpoint of the female socket sub-arc (for threePointArc)
    _path_center_bend2[0] - gn_bend2_r * math.cos(_path_socket_mid_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_socket_mid_rot),
)
_path_plug_start = (  # bend-2 point split_b_plug_overlap_len arc-length before p4
    _path_center_bend2[0] - gn_bend2_r * math.cos(_path_plug_start_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_plug_start_rot),
)
_path_plug_mid = (  # midpoint of the male plug sub-arc (for threePointArc)
    _path_center_bend2[0] - gn_bend2_r * math.cos(_path_plug_mid_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_plug_mid_rot),
)
_path_p5 = (  # end of tip
    _path_p4[0] + gn_tip_straight_len * _tan_after_bend2[0],
    _path_p4[1] + gn_tip_straight_len * _tan_after_bend2[1],
)

# World coords for SPLIT B mating-plane geometry — parity with SPLIT A.
split_b_junction_z = water_tube_z + _path_p4[0]
split_b_junction_y = zone5_y_top + _path_p4[1]
split_b_socket_overlap_z = water_tube_z + _path_socket_start[0]
split_b_socket_overlap_y = zone5_y_top + _path_socket_start[1]
split_b_plug_overlap_z = water_tube_z + _path_plug_start[0]
split_b_plug_overlap_y = zone5_y_top + _path_plug_start[1]


# ZONE 3 OUTER ARCH — full-height curve from wing bottom to zone 4
#
# Wing/fill arch is a single circular arc spanning the wing's full Y
# range (zone3_y_bottom at the -Z end up to zone4_y_top at Z=fill_z_max),
# tangent-horizontal at the high end so it meets zone 4's flat top
# surface smoothly. Center is directly below the high end (fill_z_max,
# c_y); solving distance(center, low_end) == distance(center, high_end)
# gives c_y.
_back_arch_dz = shell_rect_z_max - fill_z_max  # 29.46 (positive depth span)
back_arch_center_y = (
    (zone4_y_top + zone3_y_bottom) / 2.0
    - _back_arch_dz ** 2 / (2.0 * (zone4_y_top - zone3_y_bottom))
)
back_arch_r = zone4_y_top - back_arch_center_y
# Midpoint of the arc — angular midway between high end (90° from
# center, directly above at fill_z_max) and low end (at shell_rect_z_max,
# the +Z front edge of the rect column).
_back_arch_a_low = math.atan2(zone3_y_bottom - back_arch_center_y,
                              shell_rect_z_max - fill_z_max)
_back_arch_a_mid = (math.pi / 2.0 + _back_arch_a_low) / 2.0
back_arch_mid_z = fill_z_max + back_arch_r * math.cos(_back_arch_a_mid)
back_arch_mid_y = back_arch_center_y + back_arch_r * math.sin(_back_arch_a_mid)


# ZONE 4.5 — block above the lever, up to the gooseneck bend start
#
# A tall block capping the lever swing volume from above and reaching
# up to Y=gn_bend1_y_start ≈ 78.78. The +Z (front-facing) edge sits at
# zone45_front_z — chosen so the front margin (zone 4.5 front Z to zone
# 5's water-circle +Z edge) matches the back margin (zone 4.5 back Z to
# zone 5's flavor-pill -Z edge), centering zone 5 visually over zone 4.5
# in the depth axis.
#
# Bottom face = arch curve from (zone45_front_z, arch_y) up to
# (fill_z_max, zone4_y_top), then flat at zone4_y_top out to the -Z
# (back) cylinder. Top face = flat at zone45_y_top. Both +Z and -Z
# edges curve inward at large |X| via mirrored cylinder clips of
# radius shell_outer_r.

# Zone 5's tube-shell Z extents at X=0 — used to derive zone 4.5's
# matched-margin front Z. Water tube on the +Z side; flavor pill on
# the -Z side.
_z5_z_max = water_tube_z + tube_shell_water_r_outer  # ≈ +0.1375
_z5_z_min = flavor_tube_post_bend_z - (pill_width_z + 2.0 * zone5_wall) / 2.0

# Zone 4.5 Z extents — back edge follows the rect column; front edge
# matched-margin from zone 5.
zone45_front_z = _z5_z_max + (_z5_z_min - shell_rect_z_min)

# Top sits 3 mm above zone 4's top on the back side (lid sits flat on
# zone 4 top). The front bottom follows the back-arch curve down to
# ≈ Y=52.75.
zone45_y_top = zone4_y_top + 3.0  # 60.5
zone45_y_bottom_at_front = (
    back_arch_center_y
    + math.sqrt(back_arch_r ** 2 - (zone45_front_z - fill_z_max) ** 2)
)

# Mid-point of the bottom arch sub-arc, between zone45_front_z end
# and fill_z_max end.
_a_front = math.atan2(
    zone45_y_bottom_at_front - back_arch_center_y,
    zone45_front_z - fill_z_max,
)
_a_high = math.pi / 2.0  # fill_z_max end is directly above arch center
_a_mid45 = (_a_front + _a_high) / 2.0
zone45_bot_mid_z = fill_z_max + back_arch_r * math.cos(_a_mid45)
zone45_bot_mid_y = back_arch_center_y + back_arch_r * math.sin(_a_mid45)


# Retention is gravity-only during sub-assembly handling; shank-nut
# clamping (body → plate → TPU gasket → countertop) takes over once
# the under-counter install finishes. See ASSEMBLY.md for joinery.


# ============================================================
# GEOMETRY BUILDERS
# ============================================================

def shell_outer_cyl(y_bottom: float, y_height: float) -> cq.Workplane:
    """Shell's outer cylinder (R = shell_outer_r, centered at shell_center
    on world XZ) over the given Y range. Used both as the zone-1 outer
    surface and as a clip volume for the rect-column zones."""
    return (
        _horizontal_plane(y_bottom)
        .moveTo((shell_center_x, shell_center_z))
        .circle(shell_outer_r)
        .extrude(y_height)
    ).unwrap()


def water_tube_cyl(y_bottom: float, y_height: float) -> cq.Workplane:
    """Water-tube bore cylinder (R = water_hole_diameter/2 at
    (0, water_tube_z)) over the given Y range."""
    return (
        _horizontal_plane(y_bottom)
        .moveTo((0.0, water_tube_z))
        .circle(water_hole_diameter / 2.0)
        .extrude(y_height)
    ).unwrap()


def body_bore_cyl(y_bottom: float, y_height: float) -> cq.Workplane:
    """Body bore cylinder (R = body_bore_diameter/2 at origin) over the
    given Y range.

    Two roles:

    - Clip in zones 2 and 3 (bore region), where the shell bore must
      follow the body's rect ∩ cyl outline rather than a plain rect.

    - Cut in zones 3-fill outer and zone 4 outer, ABOVE the body's
      plateau (Y > zone2_y_top = 39). The body has ended there, so this
      column is empty space. Keeping the shell out of it (a) leaves
      room for the flavor tubes' S-bend, located by the body's flavor
      channel below and the zone 4.5 lid above, and (b) gives printed
      support material inside the dispense channel a path out.

      Cutting is applied LOCALLY in zones 3-fill and 4 — NOT at the
      build_shell level — because zone 4.5 needs to span this column
      unbroken (the lid is the structural element holding the tubes
      up there).
    """
    return (
        _horizontal_plane(y_bottom)
        .moveTo((body_bore_x, body_bore_z))
        .circle(body_bore_diameter / 2.0)
        .extrude(y_height)
    ).unwrap()


def _flavor_pill_flat_z_plus(y_bottom: float, y_height: float) -> cq.Workplane:
    """Flavor pill cutout at (0, -flavor_tube_depth) with the +Z side
    flattened — standard slot2D pill (pill_length_x × pill_width_z,
    X-oriented long axis) unioned with a rectangle extending from
    flavor_pill_z_plus_edge to the pill center on the +Z side. The flat
    edge lands at flavor_pill_z_plus_edge; the X+/X- caps and the -Z
    side stay rounded.
    """
    pill = (
        _horizontal_plane(y_bottom)
        .moveTo(flavor_pill_center)
        .slot2D(pill_length_x, pill_width_z, angle=0)
        .extrude(y_height)
    ).unwrap()
    pill_center_z = flavor_pill_center[1]
    fill_width = flavor_pill_z_plus_edge - pill_center_z
    fill_rect = (
        _horizontal_plane(y_bottom)
        .moveTo((0.0, pill_center_z + fill_width / 2.0))
        .rect(pill_length_x, fill_width)
        .extrude(y_height)
    ).unwrap()
    return pill.union(fill_rect)


def build_zone1_outer() -> cq.Workplane:
    """Filled cylinder, from the deck up to zone1_outer_y_top."""
    return shell_outer_cyl(zone1_y_bottom, zone1_outer_y_top - zone1_y_bottom)


def build_zone1_inner_cut() -> cq.Workplane:
    """Combined body bore + flavor-tube pill, as one solid to subtract.

    Body bore extends from Y=zone1_y_bottom up to zone2_bore_y_bottom
    (= zone1_y_top + bore_clearance = 13.25), so the bore's Y step
    sits bore_clearance above the body's cyl top face at Y=13.

    Body bore and pill overlap by 0.4625 mm in Z at the body/pill
    seam, so the result is a single connected hole.
    """
    body_bore = body_bore_cyl(zone1_y_bottom, zone2_bore_y_bottom - zone1_y_bottom)
    pill = _flavor_pill_flat_z_plus(zone1_y_bottom, zone1_height)
    return body_bore.union(pill)


def _rect_cove_cyl(
    center_x: float, center_z: float,
    rect_x_width: float, rect_z_width: float,
    y_bottom: float, y_top: float,
    clip_cyl: cq.Workplane,
) -> cq.Workplane:
    """Rect column with cove-filleted ±X faces, clipped to a cylinder.

    Construction (mirrors the body's `build_transition_cove`):
      - Rectangle column from y_bottom to y_top, centered at (center_x,
        center_z) on world XZ, with the given X/Z widths.
      - Filler block (cove_r tall × cove_r wide, full Z extent) on each
        X face at the bottom of the column.
      - Cove cutter (cylinder along world Z axis, R = cove_r) scoops a
        concave arc from each filler.
      - The supplied clip cylinder rounds the rect corners (and, in the
        bore case, the rect Z faces) to follow the cylinder profile.
    """
    y_height = y_top - y_bottom
    rect_x_half = rect_x_width / 2.0
    ext_z = rect_z_width / 2.0 + 2.0

    rect = (
        _horizontal_plane(y_bottom)
        .moveTo((center_x, center_z))
        .rect(rect_x_width, rect_z_width)
        .extrude(y_height)
    ).unwrap()

    def filler(x_sign: int) -> cq.Workplane:
        flat_x = center_x + x_sign * rect_x_half
        blk_cx = flat_x + x_sign * (cove_r / 2.0)
        return (
            _horizontal_plane(y_bottom)
            .moveTo((blk_cx, center_z))
            .rect(cove_r, 2.0 * ext_z)
            .extrude(cove_r)
        ).unwrap()

    def cove_cutter(x_sign: int) -> cq.Workplane:
        flat_x = center_x + x_sign * rect_x_half
        cove_cx = flat_x + x_sign * cove_r
        cove_cy = y_bottom + cove_r
        # Cylinder axis along world Z.
        return (
            cq.Workplane("XY")
            .workplane(offset=center_z - ext_z)
            .moveTo(cove_cx, cove_cy)
            .circle(cove_r)
            .extrude(2.0 * ext_z)
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
    """Outer geometry for zone 2 — rect column with cove-filleted ±X
    faces, corners clipped to the shell's outer cylinder.

    Starts at Y=zone2_outer_y_bottom (= shell_outer_lip above the body
    cyl top), giving a 3 mm cylindrical shell wall above the body cyl
    top face before the cove transition.
    """
    y_height = zone2_y_top - zone2_outer_y_bottom
    return _rect_cove_cyl(
        shell_center_x, shell_center_z,
        shell_rect_x_width, shell_rect_z_width,
        zone2_outer_y_bottom, zone2_y_top,
        shell_outer_cyl(zone2_outer_y_bottom, y_height),
    )


def build_zone2_inner_cut() -> cq.Workplane:
    """Inner cut for zone 2 — mirrors the body's cross-section with
    bore_clearance per side.

    The bore uses the SAME construction as the body's outer (rect
    column + cove-filleted ±X faces + cylinder clip). This matters in
    two places:
      1. Above the cove (Y=18 → 39), the body's rect column is itself
         intersected with body_r=15.75 — its Z faces and corners are
         curved arcs, not flat. The bore follows that.
      2. Through the cove zone (Y=13 → 18), the body bulges OUT in X
         to meet the cylinder ledge. A simple Ø32 cylindrical bore
         here would extend past the shell's outer cove surface and
         eat through the wall. Mirroring the body's filler+cove keeps
         the bore inside the shell.

    Plus the flavor-tube pill all the way through.
    """
    bore_zone2_height = zone2_y_top - zone2_bore_y_bottom
    bore = _rect_cove_cyl(
        body_bore_x, body_bore_z,
        body_bore_rect_short_x, body_bore_rect_long_z,
        zone2_bore_y_bottom, zone2_y_top,
        body_bore_cyl(zone2_bore_y_bottom, bore_zone2_height),
    )
    pill = _flavor_pill_flat_z_plus(zone2_y_bottom, zone2_height)
    return bore.union(pill)


def _arch_extrude(x_bottom: float, x_height: float) -> cq.Workplane:
    """The outer arch profile in the depth-height plane (Z, Y) — flat
    bottom at zone3_y_bottom, flat top at zone4_y_top from -Z back to
    fill_z_max, then the back-arch curve right-down to shell_rect_z_min —
    extruded across [x_bottom, x_bottom + x_height] along world +X.

    Profile is authored on `_vertical_plane(x_bottom)` whose local axes
    are (world Y, world Z) — drawing writes (height, depth) tuples.

    Shared by the zone-3 wings (extruded across each wing's X thickness)
    and the zone-3 plateau fill (extruded across the central X range).
    """
    return (
        _vertical_plane(x_bottom)
        .moveTo(zone3_y_bottom, shell_rect_z_max)
        .lineTo(zone3_y_bottom, shell_rect_z_min)
        .lineTo(zone4_y_top, shell_rect_z_min)
        .lineTo(zone4_y_top, fill_z_max)
        .threePointArc((back_arch_mid_y, back_arch_mid_z),
                       (zone3_y_bottom, shell_rect_z_max))
        .close()
        .extrude(x_height)
    )


def build_zone3_outer() -> cq.Workplane:
    """Two arch wings at ±X wrapping the body's arch ridges."""
    wing_thickness = wing_outer_x - wing_inner_x
    wings = _arch_extrude(+wing_inner_x, +wing_thickness).union(
        _arch_extrude(-wing_outer_x, +wing_thickness)
    )
    return wings.intersect(shell_outer_cyl(zone3_y_bottom, zone4_y_top - zone3_y_bottom))


def build_zone3_inner_cut() -> cq.Workplane:
    """Two arch bores at ±X mirroring the body arches with bore_clearance."""
    bore_z_oversize = body_bore_diameter / 2.0 + 2.0  # generous; bore-cyl-clipped below

    def bore(x_bottom: float, x_height: float) -> cq.Workplane:
        return (
            _vertical_plane(x_bottom)
            .moveTo(zone3_y_bottom, +bore_z_oversize)
            .lineTo(zone3_y_bottom, -bore_z_oversize)
            .lineTo(shell_arch_bore_y_foot_top, -bore_z_oversize)
            .threePointArc((shell_arch_bore_y_peak, 0),
                           (shell_arch_bore_y_foot_top, +bore_z_oversize))
            .close()
            .extrude(x_height)
        )

    bore_thickness = shell_arch_bore_outer_x - shell_arch_bore_inner_x
    bores = bore(+shell_arch_bore_inner_x, +bore_thickness).union(
        bore(-shell_arch_bore_outer_x, +bore_thickness)
    )
    return bores.intersect(body_bore_cyl(zone3_y_bottom, shell_arch_bore_y_peak - zone3_y_bottom))


def build_zone3_fill_outer() -> cq.Workplane:
    """Plateau fill behind fill_z_max — same arch profile as the wings,
    extruded across the plateau X range. The body bore column is cut
    away (see body_bore_cyl).
    """
    fill_x_thickness = 2.0 * wing_inner_x  # 13.5
    y_height = zone4_y_top - zone3_y_bottom

    arch_solid = _arch_extrude(-wing_inner_x, fill_x_thickness)
    keep_z_box = (
        _horizontal_plane(zone3_y_bottom)
        .moveTo((0.0, (fill_z_max + shell_rect_z_min) / 2.0))
        .rect(fill_x_thickness, fill_z_max - shell_rect_z_min)
        .extrude(y_height)
    ).unwrap()
    return (
        arch_solid
        .intersect(keep_z_box)
        .intersect(shell_outer_cyl(zone3_y_bottom, y_height))
        .cut(body_bore_cyl(zone3_y_bottom, y_height))
    )


def build_zone3_fill_inner_cut() -> cq.Workplane:
    """Tube cutouts through the plateau fill: water tube + straight flavor
    pill at flavor_pill_center. The bend lives in the tube shell above."""
    y_height = shell_arch_y_peak - zone3_y_bottom
    water_hole = water_tube_cyl(zone3_y_bottom, y_height)
    flavor_pill = _flavor_pill_flat_z_plus(zone3_y_bottom, y_height)
    return water_hole.union(flavor_pill)


def build_zone4_outer() -> cq.Workplane:
    """Vertical extrusion of the cyl-clipped rect at Z ≤ fill_z_max.

    Cross-section matches zone 2's outline above its cove (rect ∩ outer
    cyl). Straight-extruded from zone4_y_bottom to zone4_y_top — no
    taper. Wall thickness around the tubes falls out of (outer minus
    inner cut), not a fixed 3 mm offset.

    The body bore column is cut away (see body_bore_cyl).
    """
    y_height = zone4_height
    rect = (
        _horizontal_plane(zone4_y_bottom)
        .moveTo((shell_center_x, shell_center_z))
        .rect(shell_rect_x_width, shell_rect_z_width)
        .extrude(y_height)
    ).unwrap()
    # Z ≤ fill_z_max half-space — oversized in X and Y so it doesn't clip
    # anything else in the rect.
    keep_neg_z = (
        _horizontal_plane(zone4_y_bottom - 1)
        .moveTo((0.0, fill_z_max - 50))
        .rect(200, 100)
        .extrude(y_height + 2)
    ).unwrap()
    return (
        rect
        .intersect(shell_outer_cyl(zone4_y_bottom, y_height))
        .intersect(keep_neg_z)
        .cut(body_bore_cyl(zone4_y_bottom, zone4_height))
    )


def build_zone4_inner_cut() -> cq.Workplane:
    """Tube cavity: water-tube cyl + straight flavor pill. Straight cuts
    only — the flavor bend lives in the tube shell above."""
    water_inner = water_tube_cyl(zone4_y_bottom, zone4_height)
    flavor_pill = _flavor_pill_flat_z_plus(zone4_y_bottom, zone4_height)
    return water_inner.union(flavor_pill)


def build_zone45_outer() -> cq.Workplane:
    """Zone 4.5 — tall block capping the lever swing volume, reaching
    up to the gooseneck bend start.

    Profile authored on the depth-height plane (local axes (height,
    depth) = (world Y, world Z)), extruded across the full X range,
    then clipped by two cylinders (back + front, mirrored across the
    block's Z midpoint) so the -Z and +Z edges have matching rounded
    curves:
      start at (zone45_y_bottom_at_front, zone45_front_z)
      → arch down to (zone4_y_top, fill_z_max)
      → flat back to (zone4_y_top, shell_rect_z_min)
      → vertical up to (zone45_y_top, shell_rect_z_min)
      → flat forward to (zone45_y_top, zone45_front_z)
      → close (vertical down to start)

    Back clip: shell_outer_r cylinder centered at shell_center_z.
    Front clip: shell_outer_r cylinder centered at zone45_front_z −
    shell_outer_r, mirroring the back clip across the block's Z
    midpoint. At X=0 both clips are tangent to the block's -Z / +Z
    edges; at |X| = shell_rect_x_half both edges curve inward equally.
    """
    x_half = shell_rect_x_half
    profile_solid = (
        _vertical_plane(-x_half)
        .moveTo(zone45_y_bottom_at_front, zone45_front_z)
        .threePointArc(
            (zone45_bot_mid_y, zone45_bot_mid_z),
            (zone4_y_top, fill_z_max),
        )
        .lineTo(zone4_y_top, shell_rect_z_min)
        .lineTo(zone45_y_top, shell_rect_z_min)
        .lineTo(zone45_y_top, zone45_front_z)
        .close()
        .extrude(2.0 * x_half)
    )

    y_min = zone45_y_bottom_at_front
    clip_height = (zone45_y_top - y_min) + 1.0
    back_clip = shell_outer_cyl(y_min - 0.5, clip_height)
    front_clip = (
        _horizontal_plane(y_min - 0.5)
        .moveTo((shell_center_x, zone45_front_z - shell_outer_r))
        .circle(shell_outer_r)
        .extrude(clip_height)
    ).unwrap()
    return profile_solid.intersect(back_clip).intersect(front_clip)


def _arc_from_tangent(start, tangent, radius, theta_rad, ccw):
    """Compute (mid, end, end_tangent) for a 2D arc starting at `start`
    with `tangent`, sweeping `theta_rad` at `radius`. CCW rotates the
    tangent counterclockwise in the plane.
    """
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


# Gooseneck path lives in the depth-height plane (Y-Z, X=0). Local 2D
# (a, b) ↔ world (Z, Y). The path workplane is perpendicular to world
# +X, with local-X = world +Z (depth forward) and local-Y = world +Y
# (height up). Bending CW in this 2D plane (from +Y tangent) bends the
# path toward +Z. (Standard CCW from +Y tangent would go toward -Z.)
_path_plane = cq.Plane(
    origin=(0, 0, 0),
    xDir=(0, 0, 1),     # local +X = world +Z
    normal=(-1, 0, 0),  # local +Y = world +Y (normal × xDir = +Y)
)


# Cross-section profile plane for the gooseneck sweep. Normal = +Y
# matches the path's starting tangent (vertical lift). Local-X is
# -world-X — the lateral flip is invisible to the symmetric cross-
# section (centered on X=0). Local-Y = +world-Z so push offsets
# applied along world Z (the water → flavor depth direction) pass
# through unchanged.
_profile_plane = cq.Plane(
    origin=(0, 0, 0),
    xDir=(-1, 0, 0),
    normal=(0, 1, 0),
)


def _gooseneck_path_at_origin() -> cq.Workplane:
    """Gooseneck path in (Z, Y) at origin: vertical lift to bend 1, bend 1,
    mid straight, bend 2, tip straight. Bends toward +Z (forward).
    Bend 1 uses gn_bend1_r, bend 2 uses gn_bend2_r.

    Path origin (s=0) is at (z=0, y=0); placed in world at (X=0,
    Y=zone5_y_top, Z=water_tube_z) by the caller.
    """
    y_lift = gn_bend1_y_start - zone5_y_top

    p_bottom = (0.0, 0.0)
    p_bend_start = (0.0, y_lift)

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
    """Tube-shell outer cross-section as a Sketch, centered on the water
    tube. Used by the gooseneck sweep (Sketch is needed for sweep).

    Single connected region: water slot + flavor pill (offset -Z) +
    fill rectangle between them. The mode='a' flag unions each shape
    into the running sketch so the sweep sees one face.

    Sketch is drawn in the LOCAL 2D frame of the sweep's starting
    cross-section plane. At the path origin (tangent = +Y, workplane
    normal = -X), the sketch's local-X = world +X (lateral) and
    local-Y = world +Z (depth). So `angle=0` slots run laterally (long
    axis along world X) — matching the standalone zone-5 vertical
    extrusion's pill orientation.

    NOTE: cq.Sketch.slot(w, h) takes w as the *straight section* length
    (between the rounded ends), not the overall length — opposite of
    Workplane.slot2D's convention. Total length along the long axis is
    w + h, so w_straight = total - h.
    """
    water_z_width = 2.0 * tube_shell_water_r_outer
    water_slot_straight = tube_shell_x_outer - water_z_width
    pill_short_total = pill_width_z + 2.0 * zone5_wall
    pill_straight = tube_shell_x_outer - pill_short_total
    return (
        cq.Sketch()
        .slot(water_slot_straight, water_z_width, angle=0)
        .push([(0, flavor_offset_z_from_water)])
        .slot(pill_straight, pill_short_total, angle=0, mode="a")
        .reset()
        .push([(0, flavor_offset_z_from_water / 2.0)])
        .rect(tube_shell_x_outer, -flavor_offset_z_from_water, mode="a")
        .clean()
    )


def _tube_shell_inner_sketch() -> cq.Sketch:
    """Tube-shell inner cross-section as a Sketch, for the gooseneck
    sweep. See _tube_shell_outer_sketch for sketch-frame +
    cq.Sketch.slot conventions."""
    pill_straight = pill_length_x - pill_width_z  # 3.175
    return (
        cq.Sketch()
        .circle(water_hole_diameter / 2.0)
        .push([(0, flavor_offset_z_from_water)])
        .slot(pill_straight, pill_width_z, angle=0, mode="a")
        .clean()
    )


def _sweep_along_gooseneck(sketch: cq.Sketch) -> cq.Workplane:
    """Sweep the given tube-shell cross-section along the gooseneck path,
    then place at world (0, zone5_y_top, water_tube_z) — the seam atop
    zone 5's vertical extrusion of the same cross-section."""
    profile = cq.Workplane(_profile_plane).placeSketch(sketch)
    swept = profile.sweep(_gooseneck_path_at_origin(), transition="right")
    return swept.translate((0, zone5_y_top, water_tube_z))


def build_zone6_outer() -> cq.Workplane:
    return _sweep_along_gooseneck(_tube_shell_outer_sketch())


def build_zone6_inner_cut() -> cq.Workplane:
    return _sweep_along_gooseneck(_tube_shell_inner_sketch())


def _tube_shell_outer_shrunk_sketch(shrink: float) -> cq.Sketch:
    """Outer cross-section offset INWARD by `shrink` mm.

    Reconstructed with parameters reduced by 2·shrink so the resulting
    boundary is the exact 2D inward offset of _tube_shell_outer_sketch:
    each slot's height and total X-length shrink by 2·shrink (centers
    fixed; straight-section length unchanged), and the fill rect's X
    matches the new shorter slot X. Slot centers + fill-rect Z stay
    fixed, so the three primitives still union into one connected
    region everywhere the original did.
    """
    water_z_width = 2.0 * (tube_shell_water_r_outer - shrink)
    new_x_outer = tube_shell_x_outer - 2.0 * shrink
    water_slot_straight = new_x_outer - water_z_width
    pill_short_total = pill_width_z + 2.0 * (zone5_wall - shrink)
    pill_straight = new_x_outer - pill_short_total
    return (
        cq.Sketch()
        .slot(water_slot_straight, water_z_width, angle=0)
        .push([(0, flavor_offset_z_from_water)])
        .slot(pill_straight, pill_short_total, angle=0, mode="a")
        .reset()
        .push([(0, flavor_offset_z_from_water / 2.0)])
        .rect(new_x_outer, -flavor_offset_z_from_water, mode="a")
        .clean()
    )


def _build_zone6_outer_shrunk(shrink: float) -> cq.Workplane:
    """Gooseneck outer with the cross-section offset inward by `shrink`.

    Same path as build_zone6_outer; only the swept profile changes.
    Used twice for the split joint:
      - As the SOCKET-CAVITY cutter on the angled-spout (bottom) piece:
        intersected with the 20 mm overlap slab and cut from the bottom
        shell, leaving a `shrink`-thick uniform outer wall.
      - As the PLUG OUTER on the upper-bend (top) piece: intersected
        with the same slab, then the original bores cut through it.
    """
    return _sweep_along_gooseneck(_tube_shell_outer_shrunk_sketch(shrink))


def _split_plane_halfspace(origin: tuple, normal: tuple, sign: int,
                           extent: float = 600.0) -> cq.Workplane:
    """Solid filling the halfspace on one side of a plane.

    sign = +1: halfspace in the +normal direction (above the plane).
    sign = -1: halfspace in the −normal direction (below the plane).
    The halfspace is a 2·extent × 2·extent × extent box stuck to the
    plane — extent must envelop the shell on that side.
    """
    plane = cq.Plane(
        origin=cq.Vector(*origin),
        xDir=cq.Vector(1, 0, 0),  # world X lies in the plane (normal is in YZ)
        normal=cq.Vector(*normal),
    )
    return cq.Workplane(plane).rect(2.0 * extent, 2.0 * extent).extrude(sign * extent)


def _split_overlap_slab(overlap_z: float, overlap_y: float) -> cq.Workplane:
    """The slab between the overlap plane (below) and the junction plane
    (above), both perpendicular to the angled-spout tangent. Caller picks
    which overlap-plane coords to use — socket (deeper) vs plug (shorter).

    Intersect with shrunk-outer / bores to get the male plug or the
    socket-cavity cutter — only the relevant spout chunk, not the full sweep.
    """
    above_overlap = _split_plane_halfspace(
        (0.0, overlap_y, overlap_z), split_normal, sign=+1,
    )
    below_junction = _split_plane_halfspace(
        (0.0, split_junction_y, split_junction_z), split_normal, sign=-1,
    )
    return above_overlap.intersect(below_junction)


def _sweep_segment_in_path_local(
    start_zy: tuple,
    tangent_zy: tuple,
    path_workplane: cq.Workplane,
    sketch: cq.Sketch,
) -> cq.Workplane:
    """Sweep `sketch` along `path_workplane`, with the profile placed
    perpendicular to `tangent_zy` at `start_zy`. Inputs are in
    path-local 2D coords on the (world Z, world Y) plane (X=0). Result
    is translated by world (0, zone5_y_top, water_tube_z) to land in
    world.

    The profile workplane's xDir is set to world -X (matching
    _profile_plane), so the cross-section's local frame is identical to
    the main sweep's profile at the path origin (local-X = -world-X,
    local-Y = +world-Z). This matches the rigid-frame orientation that
    `_sweep_along_gooseneck` produces at any point along the gooseneck.
    Consequence: a sub-sweep starting partway along the gooseneck path
    aligns cross-section-for-cross-section with the full sweep there,
    so cutting one from the other leaves no residue at the seam.
    """
    normal = (0.0, tangent_zy[1], tangent_zy[0])  # tangent in world (X, Y, Z)
    xdir = (-1.0, 0.0, 0.0)
    plane = cq.Plane(
        origin=cq.Vector(0.0, start_zy[1], start_zy[0]),
        xDir=cq.Vector(*xdir),
        normal=cq.Vector(*normal),
    )
    profile = cq.Workplane(plane).placeSketch(sketch)
    swept = profile.sweep(path_workplane, transition="right")
    return swept.translate((0, zone5_y_top, water_tube_z))


def _tip_subpath() -> cq.Workplane:
    """The dispense-tip's 25 mm straight path in path-local (Z, Y) coords.
    Start = _path_p4 (end of bend 2 / SPLIT B junction);
    end   = _path_p5 (= start + gn_tip_straight_len along tan2)."""
    return (
        cq.Workplane(_path_plane)
        .moveTo(*_path_p4)
        .lineTo(*_path_p5)
    )


def _bend_overlap_subarc(start_zy: tuple, mid_zy: tuple) -> cq.Workplane:
    """A bend-2 sub-arc from `start_zy` through `mid_zy` to `_path_p4`
    (the SPLIT B junction), in path-local (Z, Y). Caller supplies the
    socket-length or plug-length endpoints."""
    return (
        cq.Workplane(_path_plane)
        .moveTo(*start_zy)
        .threePointArc(mid_zy, _path_p4)
    )


def _build_tip_section(sketch: cq.Sketch) -> cq.Workplane:
    """Sweep `sketch` along just the dispense-tip path. Use for:
      - tip outer (with _tube_shell_outer_sketch) — visible spout
        portion of the top piece, and the cutter that removes the tip
        from the middle piece;
      - tip inner (with _tube_shell_inner_sketch) — bores cut through
        the tip section so the tubes can pass."""
    return _sweep_segment_in_path_local(
        _path_p4, _tan_after_bend2, _tip_subpath(), sketch,
    )


def _build_bend_overlap(sketch: cq.Sketch, *, side: str) -> cq.Workplane:
    """Sweep `sketch` along the last `split_b_<side>_overlap_len` mm of
    bend 2 (the SPLIT B overlap zone). `side` is "socket" (longer, cut
    from the middle piece's female cavity) or "plug" (shorter, used to
    build the top piece's male tongue and its bore cut)."""
    if side == "socket":
        start_zy, mid_zy, tan_start = _path_socket_start, _path_socket_mid, _tan_at_socket_start
    elif side == "plug":
        start_zy, mid_zy, tan_start = _path_plug_start, _path_plug_mid, _tan_at_plug_start
    else:
        raise ValueError(f"side must be 'socket' or 'plug', got {side!r}")
    return _sweep_segment_in_path_local(
        start_zy, tan_start, _bend_overlap_subarc(start_zy, mid_zy), sketch,
    )


def build_lever_clearance() -> cq.Workplane:
    """Single triangular ramp wedge cut into the top of the rect column
    on the +Z (toward-user) side, where the pressed lever's taper
    crosses the rect-column top corner.

    Profile in the depth-height plane (local axes (height, depth) =
    (world Y, world Z)) — a right triangle:
      - top edge flat at Y=zone2_y_top (39), from Z=lever_ramp_z_max
        (+19, outer rect face) inward to Z=lever_ramp_z_start (≈+14.51,
        bore tangent + overshoot)
      - vertical edge at Z=lever_ramp_z_max, dropping lever_ramp_depth
        below Y=39
      - sloped (ramp) edge from the bottom of the vertical edge back to
        the -Z start point at Y=39

    Extruded ±lever_clearance_x_half in X.
    """
    y_top = zone2_y_top
    y_bot = y_top - lever_ramp_depth
    x_half = lever_clearance_x_half
    return (
        _vertical_plane(-x_half)
        .polyline([
            (y_bot, lever_ramp_z_max),
            (y_top, lever_ramp_z_max),
            (y_top, lever_ramp_z_start),
        ]).close()
        .extrude(2.0 * x_half)
    )


# Tube-shell vertical section — wraps inside the lid. Spans the lid's
# Y range (zone5_y_bottom = zone4_y_top up to zone5_y_top). The outer
# cross-section is dominated by the lid block in the union, so it's not
# visible from outside; the wraps only carry the bore through the lid.
# Above zone5_y_top the gooseneck (zone 6) emerges with the tube wraps
# becoming visible as the spout.


def _tube_shell_outer_section(y_bottom: float, y_height: float) -> cq.Workplane:
    """Tube wrap outer (water X-slot + flavor pill + fill rect, all
    zone5_wall on the Z sides) extruded vertically over the given Y
    range. See _tube_shell_outer_sketch for the cross-section."""
    water_z_width = 2.0 * tube_shell_water_r_outer
    water_outer = (
        _horizontal_plane(y_bottom)
        .moveTo((0.0, water_tube_z))
        .slot2D(tube_shell_x_outer, water_z_width, angle=0)
        .extrude(y_height)
    ).unwrap()
    flavor_outer = (
        _horizontal_plane(y_bottom)
        .moveTo((0.0, flavor_tube_post_bend_z))
        .slot2D(tube_shell_x_outer, pill_width_z + 2.0 * zone5_wall, angle=0)
        .extrude(y_height)
    ).unwrap()
    fill_rect = (
        _horizontal_plane(y_bottom)
        .moveTo((0.0, (water_tube_z + flavor_tube_post_bend_z) / 2.0))
        .rect(tube_shell_x_outer, -flavor_offset_z_from_water)
        .extrude(y_height)
    ).unwrap()
    return water_outer.union(flavor_outer).union(fill_rect)


def _tube_shell_inner_section(y_bottom: float, y_height: float) -> cq.Workplane:
    """Tube hole cross-section (water cyl + flavor pill) extruded vertically."""
    flavor_inner = (
        _horizontal_plane(y_bottom)
        .moveTo((0.0, flavor_tube_post_bend_z))
        .slot2D(pill_length_x, pill_width_z, angle=0)
        .extrude(y_height)
    ).unwrap()
    return water_tube_cyl(y_bottom, y_height).union(flavor_inner)


# ============================================================
# PUBLIC SHELL BUILDERS
# ============================================================

def build_shell() -> cq.Workplane:
    """Touch-Flo shell — full reference solid (un-split), in the
    repo's +Y-up frame.

    For printing, this solid is split into THREE pieces along the
    gooseneck at two 20 mm slip-fit joints — see build_shell_bottom
    (angled-spout), build_shell_middle (upper-bend), and
    build_shell_top (dispense-tip). The single-solid form serves
    assembly visualization and is the source the bottom / middle
    splits operate on.

    All zones unioned into one solid:
      - Zones 1–4: body wraps + lever clearance
      - Zone 4.5: lid above the lever
      - Zone 5: tube wraps inside the lid (provides the bore through the
                lid; outer is dominated by the lid in the union)
      - Zone 6: gooseneck (the visible spout above the lid)

    Gooseneck overhangs need slicer-generated supports.
    """
    outer = (
        build_zone1_outer()
        .union(build_zone2_outer())
        .union(build_zone3_outer())
        .union(build_zone3_fill_outer())
        .union(build_zone4_outer())
        .union(build_zone45_outer())
        .union(_tube_shell_outer_section(zone5_y_bottom, zone5_height))
        .union(build_zone6_outer())
    )
    inner = (
        build_zone1_inner_cut()
        .union(build_zone2_inner_cut())
        .union(build_zone3_inner_cut())
        .union(build_zone3_fill_inner_cut())
        .union(build_zone4_inner_cut())
        .union(_tube_shell_inner_section(zone5_y_bottom, zone5_height))
        .union(build_zone6_inner_cut())
        .union(build_lever_clearance())
    )
    return outer.cut(inner)


def build_shell_bottom(full_shell: cq.Workplane | None = None) -> cq.Workplane:
    """Angled-spout piece — bottom of the split, with the female socket.
    In the repo's +Y-up frame.

    Everything below the SPLIT A junction plane, with the top 20 mm of
    the spout hollowed out down to a 2 mm uniform wall (the female
    socket) that receives the middle piece's male plug. The original
    water + flavor bores in the overlap zone are absorbed into the
    socket cavity.
    """
    full = full_shell if full_shell is not None else build_shell()
    below_junction = _split_plane_halfspace(
        (0.0, split_junction_y, split_junction_z), split_normal, sign=-1,
    )
    socket_cavity = _build_zone6_outer_shrunk(split_a_socket_shrink).intersect(
        _split_overlap_slab(split_a_socket_overlap_z, split_a_socket_overlap_y)
    )
    return full.intersect(below_junction).cut(socket_cavity)


def build_shell_middle(full_shell: cq.Workplane | None = None) -> cq.Workplane:
    """Upper-bend piece — middle of the split, with the male plug for
    SPLIT A (bottom end) and the female socket for SPLIT B (top end).
    In the repo's +Y-up frame.

    Built in two stages:
      1. SPLIT A (spout↔bend): keep everything ABOVE the SPLIT A
         junction plane, then add the angled-spout-direction male plug.
      2. SPLIT B (bend↔tip): cut out the dispense-tip section, then cut
         out a shrunk-cross-section sweep along the last 20 mm of
         bend 2 — leaving a 2 mm female socket wall over the curved
         overlap zone. Original bores in that zone are absorbed into
         the socket cavity.
    """
    full = full_shell if full_shell is not None else build_shell()
    above_junction_a = _split_plane_halfspace(
        (0.0, split_junction_y, split_junction_z), split_normal, sign=+1,
    )
    overlap_slab_a = _split_overlap_slab(
        split_a_plug_overlap_z, split_a_plug_overlap_y
    )
    plug_outer_a = _build_zone6_outer_shrunk(split_a_plug_shrink).intersect(overlap_slab_a)
    plug_bores_a = build_zone6_inner_cut().intersect(overlap_slab_a)
    plug_a = plug_outer_a.cut(plug_bores_a)
    bend_plus_tip = full.intersect(above_junction_a).union(plug_a)

    tip_section = _build_tip_section(_tube_shell_outer_sketch())
    bend_socket_cavity = _build_bend_overlap(
        _tube_shell_outer_shrunk_sketch(split_b_socket_shrink), side="socket",
    )
    return bend_plus_tip.cut(tip_section).cut(bend_socket_cavity)


def build_shell_top(full_shell: cq.Workplane | None = None) -> cq.Workplane:
    """Dispense-tip piece — top of the split, with the male plug for
    SPLIT B (bend↔tip joint). In the repo's +Y-up frame.

    Constructed entirely from fresh sub-sweeps (not extracted from the
    full shell), so the plug follows bend 2's curve back through the
    last 20 mm of arc:
      - Tip section = outer sweep along the 25 mm tip path, minus the
        original water + flavor bores.
      - Male plug = SHRUNK-outer sweep along the last 20 mm of bend 2
        (curved OD ≡ middle piece's curved socket ID), minus the
        original bores so the tubes pass through unbroken.
    The two solids union at the SPLIT B junction plane.

    `full_shell` accepted for signature parity with the other two
    builders but unused — the top piece is constructed from fresh
    sub-sweeps.
    """
    _ = full_shell
    tip_outer = _build_tip_section(_tube_shell_outer_sketch())
    tip_inner = _build_tip_section(_tube_shell_inner_sketch())
    tip = tip_outer.cut(tip_inner)

    plug_outer = _build_bend_overlap(
        _tube_shell_outer_shrunk_sketch(split_b_plug_shrink), side="plug",
    )
    plug_inner = _build_bend_overlap(_tube_shell_inner_sketch(), side="plug")
    plug = plug_outer.cut(plug_inner)

    return tip.union(plug)


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
        "BODY_OD": f"{body_rect_long_z:.4g} mm",
        "BODY_RECT_LONG": f"{body_rect_long_z:.4g} mm",
        "BODY_RECT_SHORT": f"{body_rect_short_x:.4g} mm",
        "BODY_CYL_TOP_Y": f"{zone1_y_top:.4g} mm",
        "BORE_COVE_Y": f"{zone2_bore_y_bottom + cove_r:.4g} mm",
        "PILL_L": f"{pill_length_x:.4g} mm",
        "PILL_W": f"{pill_width_z:.4g} mm",
        "FLAVOR_TUBE_Z": f"{-flavor_pill_center[1]:.4g} mm",
        "FLAVOR_PILL_Z_PLUS": f"{-flavor_pill_z_plus_edge:.4g} mm",
        "SHELL_OUTER_R": f"{shell_outer_r:.4g} mm",
        "WATER_HOLE_D": f"{water_hole_diameter:.4g} mm",
    }
    substitute_md(
        out_dir / "ASSEMBLY.md",
        variables=variables,
        expected_counts={
            "BORE_CLEAR": 1,
            "PILL_L": 1,
            "PILL_W": 2,
            "FLAVOR_TUBE_Z": 2,
            "BODY_OD": 2,
            "BODY_RECT_LONG": 1,
            "BODY_RECT_SHORT": 1,
            "BODY_CYL_TOP_Y": 1,
            "BORE_COVE_Y": 1,
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
            "PILL_L": 1,
            "PILL_W": 1,
            "FLAVOR_PILL_Z_PLUS": 1,
            "SHELL_OUTER_R": 1,
            "WATER_HOLE_D": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
