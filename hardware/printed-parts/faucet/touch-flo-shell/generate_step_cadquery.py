"""Touch-Flo shell — printed shroud that wraps around the harvested
faucet body, the flavor tubes, and the lever swing volume. Sits on top
of the touch-flo-mounting-plate.

Grown bottom-up, one zone at a time. See the per-zone comments for what
each zone does and why."""

import math
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import export_step


# Shifted +X so the +X edge of the shell extends past the wider 1/4"
# flavor cutout with a real wall. Was 1.5875 (matching the mounting
# plate). Mounting plate sits asymmetrically under the shell until the
# plate is re-centered in a follow-up.
shell_center_x = 3.175
shell_center_y = 0.0


# ZONE 1 — first 13 mm; body is a full Ø 31.5 mm cylinder here

zone1_z_bottom = 0.0
zone1_z_top = 13.0
zone1_height = zone1_z_top - zone1_z_bottom  # 13 mm

# Body-to-bore slip-fit clearance — applied per-side (per-direction)
# uniformly: X faces, Y faces, radial cylinder, AND face-to-face Z
# interfaces all get the same gap. So bore radii / half-widths add
# this once per side, and the bore's Z transitions lift by this much
# above the body's Z transitions.
bore_clearance = 0.25  # mm per side

# Body bore (cylinder) — body OD 31.5 mm + 2 × clearance per side
body_bore_diameter = 31.5 + 2.0 * bore_clearance  # 32.0
body_bore_x = 0.0
body_bore_y = 0.0

# Flavor-tube pill — sized for 1/4" OD LLDPE flavor tubes (6.35 mm OD),
# tangent to the body's +X face (X=15.75) and tangent to each other at Y=0.
# (Mounting plate not yet updated to match — coming in a later pass.)
flavor_tube_x = 18.925  # body_r + tube_r = 15.75 + 3.175
flavor_tube_hole_dia = 6.85  # 6.35 OD + 0.5 mm clearance
flavor_tube_y_offset = 3.175  # = tube_r, tubes touch at Y=0
pill_length_y = 2 * flavor_tube_y_offset + flavor_tube_hole_dia  # 13.2
pill_width_x = flavor_tube_hole_dia  # 6.85

# Flat -X edge of the flavor pill cutout in zones 1-4 (the base shell).
# Pulled in (more -X) past the natural pill -X edge so the cutout's
# corners (at Y=±pill_length_y/2) land on the body bore's cyl curve
# in zone 1. With 1/4" flavor tubes the natural pill -X (= 15.5) is
# OUTSIDE the cyl bore at the corner Y=±6.6 (bore +X there is 14.57)
# — leaving a thin sliver of shell material between cutout and bore.
# Computing -X as `min(natural pill edge, bore +X at corner Y)` makes
# the flat side reach the bore wherever the natural pill would not.
# With smaller (1/8") tubes the natural pill is inside the bore at
# its corners, so this min picks the natural value and nothing changes.
flavor_pill_x_minus_edge = min(
    flavor_tube_x - pill_width_x / 2.0,
    math.sqrt((body_bore_diameter / 2.0) ** 2 - (pill_length_y / 2.0) ** 2),
)  # ≈ 14.575


# SHELL OUTER (derived from wall-thickness target)
#
# The wall-thickness target applies at the body bore's farthest edge
# from the shell center. With shell_center_x chosen to balance walls on
# both sides (body bore -X edge vs. flavor pill +X edge), the two
# extremes are equidistant from the shell center (19.175 mm), so the
# target applies cleanly to both.
wall_thickness_min = 3.0
_body_bore_farthest_from_shell_center = (
    (shell_center_x - body_bore_x) + body_bore_diameter / 2.0
)  # = 19.175 mm
shell_outer_r = _body_bore_farthest_from_shell_center + wall_thickness_min


# ZONE 2 — cylinder → rectangle transition + rect column

zone2_z_bottom = zone1_z_top  # 13.0
zone2_z_top = 39.0  # body plateau
zone2_height = zone2_z_top - zone2_z_bottom  # 26.0

# Body rectangle dimensions (mirrored from valve-body-reference)
body_rect_long = 31.5  # X
body_rect_short = 17.0  # Y

# Body bore in zone 2 — match body rect with clearance per side
body_bore_rect_long = body_rect_long + 2.0 * bore_clearance  # 32.0
body_bore_rect_short = body_rect_short + 2.0 * bore_clearance  # 17.5

# Cove transition fillet (matches the body's transition_fillet_r)
cove_r = 6.0

# Bore Z transitions lift by bore_clearance above the body's Z
# transitions so face-to-face Z interfaces get the same per-side
# clearance as X/Y.
zone2_bore_bottom = zone1_z_top + bore_clearance  # 13.25

# Outer surface lifts by wall_thickness_min + bore_clearance above the
# body's cylinder top, so 3 mm of solid shell wall sits above the bore
# step. Without the lift, the outer cove would tangent the body's cyl
# ledge at Z=13 from above with no vertical wall material over it.
shell_outer_lip = wall_thickness_min + bore_clearance  # 3.25
zone1_outer_top = zone1_z_top + shell_outer_lip  # 16.25
zone2_outer_bot = zone1_outer_top  # 16.25


# LEVER SWING CLEARANCE — a chamfer wedge cut into the top -X corner of
# the rect column, where the pressed lever's taper passes through.
#
# Two anchor points define the wedge (slope falls out of them):
#   1. -X end: outer rect face at Z = zone2_z_top − lever_ramp_depth.
#   2. +X end: the bore-cylinder tangent at the cut's Y half-span, so
#      the wedge terminates exactly where the wall ends at the lever's
#      Y-edge (any further +X is inside the bore — no wall to cut).
#
# tangent_overshoot pushes the +X end a hair past the exact tangent.
# Exactly at the tangent, the CAD kernel can render the coincident edge
# as a microscopic zero-thickness sliver of uncut wall; the overshoot
# puts the wedge's +X end just inside the bore, giving a clean termination.

lever_y_half = 6.5  # lever physical Y span
lever_clearance_y_half = lever_y_half + bore_clearance  # 6.75
lever_ramp_depth = 1.0  # cut depth at outer rect face
tangent_overshoot = 0.002  # mm past bore tangent
lever_ramp_x_min = shell_center_x - shell_outer_r  # -19, outer rect face on -X side
_bore_x_at_lever_y = -math.sqrt(
    (body_bore_diameter / 2.0) ** 2 - lever_clearance_y_half ** 2
)  # ≈ -14.5061 — bore-cylinder tangent at the cut's Y half-span
lever_ramp_x_start = _bore_x_at_lever_y - tangent_overshoot  # ≈ -14.5081

# Shell rectangle. X width matches the cylinder OD so the X faces flow
# straight up from the cylinder. Y half is body-bore-Y plus the wall.
shell_rect_x_half = shell_outer_r  # 22.175
shell_rect_y_half = body_bore_rect_short / 2.0 + wall_thickness_min  # 11.75
shell_rect_x_width = 2.0 * shell_rect_x_half
shell_rect_y_width = 2.0 * shell_rect_y_half
shell_rect_x_min = shell_center_x - shell_rect_x_half  # -19.0
shell_rect_x_max = shell_center_x + shell_rect_x_half  # 25.35


# ZONE 3 — Arch wraps (two wings at ±Y)
#
# Body arches: 1.5 mm wide ridges at Y = ±7.75, full X width
# (±15.75), profile in ZX = 2 mm rectangular foot from Z=39→41 plus
# a 3-point arc through (±15.75, 41) and (0, 46).
#
# The shell wraps each arch with WALL+GAP outside (top, +Y/-Y outer
# face, X foot ends) — same lift pattern as zone 2's outer cyl over
# the body's cyl top. The plateau between the arches (Y ∈ ±6.75) is
# OPEN — no shell material there. So each shell wing's plateau-side
# Y face is the bore's plateau-side Y face; they share the same edge.

zone3_z_bottom = zone2_z_top  # 39

arch_base_z = 41.0  # body foot top
arch_peak_z = 46.0  # body arc peak
body_arch_inner_y = 7.0  # body arch face nearest plateau
body_arch_outer_y = 8.5  # body arch face nearest shell exterior

# Bore (inner cut): body arch + bore_clearance per side
shell_arch_bore_inner_y = body_arch_inner_y - bore_clearance  # 6.75
shell_arch_bore_outer_y = body_arch_outer_y + bore_clearance  # 8.75
shell_arch_bore_foot_top_z = arch_base_z + bore_clearance  # 41.25
shell_arch_bore_peak_z = arch_peak_z + bore_clearance  # 46.25

# Outer wing: WALL+GAP above the body arch in Z; outer-Y matches the
# rect col Y_HALF so the wing sits flush atop zone 2; inner-Y matches
# the bore (plateau open, no extra shell material on plateau side).
shell_arch_foot_top_z = arch_base_z + shell_outer_lip  # 44.25
shell_arch_peak_z = arch_peak_z + shell_outer_lip  # 49.25
wing_inner_y = shell_arch_bore_inner_y  # 6.75
wing_outer_y = shell_rect_y_half  # 11.75

# ZONE 3 — plateau fill (between the wings, X ≥ fill_x_min). Fills the
# plateau region behind the back third of the water tube, matching the
# wings' arch profile so the shell reads as one continuous swept arch
# shape across the back.
water_tube_x = 8.875
# 3/8" LLDPE — sealed in the body's 9.75 mm port via a TPU O-ring
# (0.225 mm radial gap). The 3/8" OD here is the 3-tube dispense spout's
# center tube INSIDE the faucet head — NOT the supply line. The
# harvested Westbrass R2031-NL-62 valve body IS the 1/4"→3/8" adapter;
# the 3/8" tube only exists above this port, internal to the head.
water_tube_od = 0.375 * 25.4  # 9.525
water_hole_diameter = water_tube_od + 2.0 * bore_clearance  # 10.025

# 1/4" LLDPE flavor tube. The flavor tube butts up against the water
# tube at the dispense point. Each flavor tube sits at
# Y=±flavor_tube_y_offset (so they also touch each other), so the
# X-tangency at the dispense point is Pythagorean:
#   (post_bend_x − water_tube_x)² + y_offset² = (r_water + r_flavor)²
flavor_tube_od = 0.25 * 25.4  # 6.35
flavor_tube_post_bend_x = water_tube_x + math.sqrt(
    (water_tube_od / 2.0 + flavor_tube_od / 2.0) ** 2
    - flavor_tube_y_offset ** 2
)  # ≈ 16.150

fill_x_min = 10.46  # back third of water tube


# ZONE 4 — rect column continuation above the arch (water tube +
# flavor pill cutouts), from the arch foot up to zone4_z_top.
zone4_z_bottom = shell_arch_foot_top_z  # 44.25
# Zone 4 top must clear the lever's pressed-down envelope. The lever's
# head corner at rest (X=9, Z=52) rotates -18° around pivot (1.5, 46)
# to (6.78, 54.024). That point sits inside zone 5's water-circle outer
# outline (centered at X=8.875, R=9.0125), so zone 5's bottom — and
# therefore zone 4's top — must be above it. The first PETG test print
# showed ~1 mm clearance was too tight; bumped to 57.5 mm for ~3.5 mm
# clearance above 54.024.
zone4_z_top = 57.5
zone4_height = zone4_z_top - zone4_z_bottom  # 10.75


# ZONE 5 — tube wrapper above the lever. Above zone 4 (which ends high
# enough to clear the lever's swing envelope), the shell wraps just the
# tubes (water cyl bore + flavor pill bore, each + 3 mm wall),
# straight-extruded vertically. This zone "violates" fill_x_min — the
# wrapper around the water tube extends in -X past it, but that's safe
# because we're now above the lever's reach.
zone5_z_bottom = zone4_z_top  # 57.5
zone5_z_top = zone4_z_top + 10.0  # 67.5
zone5_height = zone5_z_top - zone5_z_bottom  # 10
zone5_wall = wall_thickness_min + 1

# Tube-shell cross-section vocabulary — shared by zone 5's vertical
# extrusion and zone 6's sweep along the gooseneck path.
#
# Water and flavor share the same outer Y half-width — the larger of
# (water bore + wall) and (flavor pill + wall) — so the cross-section's
# Y+ and Y- outer apexes meet at the same Y across the X range. Each
# side's X width stays at natural — the walls on the extreme -X
# (around the water bore) and extreme +X (around the flavor pill) are
# both zone5_wall. The "stretch" is only in Y (the smaller side picks
# up extra wall thickness on its Y apex); the X side walls don't thicken.
tube_shell_water_r_outer = water_hole_diameter / 2.0 + zone5_wall   # 9.0125
tube_shell_pill_y_half_outer = pill_length_y / 2.0 + zone5_wall
tube_shell_y_half_outer = max(tube_shell_water_r_outer, tube_shell_pill_y_half_outer)
tube_shell_y_outer = 2.0 * tube_shell_y_half_outer
# +X offset from the water tube to the flavor pill — used both as the
# fill-rect span between the two bores and as the parallel-arc offset in
# the gooseneck sweep.
flavor_offset_x_from_water = flavor_tube_post_bend_x - water_tube_x


# ZONE 6 — gooseneck wrapper around the bent dispense tubes. Pure
# continuation of zone 5's cross-section along a bent path above the
# lever-swing envelope.
#
# Path (in tube-local XZ plane, origin at the zone 5 / zone 6 seam):
#   1. vertical lift from Z=0 up to Z=gn_bend1_start_z − zone5_z_top
#   2. bend 1 — gn_bend1_sweep_rad at R = gn_bend1_r, bending toward -X
#   3. gn_mid_straight_len angled straight
#   4. bend 2 — gn_bend2_sweep_rad at R = gn_bend2_r
#   5. gn_tip_straight_len tip
#
# The flavor pill's +X offset is carried in the LOCAL frame of the
# sweep, so as the tangent rotates through each bend the pill traces a
# parallel-offset arc at the larger radius — matching the actual flavor
# tubes' centerlines.
#
# These mirror constants in the assembly (`faucet-assembly`); if the
# assembly's gooseneck moves, update both.

gn_bend1_r = 30.0  # water tube — bend 1
gn_bend2_r = 40.0  # water tube — bend 2
gn_bend1_sweep_rad = math.radians(30.0)
gn_bend2_sweep_rad = math.radians(110.0)
# 35 mm above the lever rest top (at zone2_z_top + 13 = 52).
gn_bend1_mid_z = zone2_z_top + 48.0  # 87
gn_bend1_start_z = (
    gn_bend1_mid_z
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
# After the 2026-05-19 test-fit, joint A's curved male wouldn't seat past
# ~7/20 mm — drop the male wall there to add radial clearance and shorten
# the male overlap. Joint B's straight male came up ~2 mm short of full
# seating — thin both walls and shorten the male overlap.
split_a_socket_overlap_len = 20.0
split_a_plug_overlap_len = 19.0
split_a_socket_wall = 2.0
split_a_plug_wall = 1.9

split_b_socket_overlap_len = 20.0
split_b_plug_overlap_len = 18.0
split_b_socket_wall = 1.9
split_b_plug_wall = 1.9

split_a_socket_shrink = split_a_socket_wall
split_a_plug_shrink = zone5_wall - split_a_plug_wall
split_b_socket_shrink = split_b_socket_wall
split_b_plug_shrink = zone5_wall - split_b_plug_wall

# Mid-straight tangent in the path-local XZ plane — rotation of (0, 1)
# CCW by gn_bend1_sweep_rad. Points UP the spout (toward bend 2).
_mid_tan_xz = (-math.sin(gn_bend1_sweep_rad), math.cos(gn_bend1_sweep_rad))

# Cutting-plane normal for SPLIT A in world (Y=0; centerline is in X-Z).
split_normal = (_mid_tan_xz[0], 0.0, _mid_tan_xz[1])

# End of mid-straight (= SPLIT A junction) in world coords. Closed-form
# continuation of _gooseneck_path_at_origin's math: bend-1-end +
# gn_mid_straight_len along the mid-straight tangent.
_bend1_end_xz = (
    gn_bend1_r * (math.cos(gn_bend1_sweep_rad) - 1.0),
    (gn_bend1_start_z - zone5_z_top) + gn_bend1_r * math.sin(gn_bend1_sweep_rad),
)
split_junction_x = water_tube_x + _bend1_end_xz[0] + gn_mid_straight_len * _mid_tan_xz[0]
split_junction_z = zone5_z_top + _bend1_end_xz[1] + gn_mid_straight_len * _mid_tan_xz[1]

# Bottom of SPLIT A's overlap zone for each side (socket = female cavity
# in the bottom piece; plug = male tongue on the middle piece). Females
# and males now have asymmetric depths — see the split_*_overlap_len
# block above.
split_a_socket_overlap_x = split_junction_x - split_a_socket_overlap_len * _mid_tan_xz[0]
split_a_socket_overlap_z = split_junction_z - split_a_socket_overlap_len * _mid_tan_xz[1]
split_a_plug_overlap_x = split_junction_x - split_a_plug_overlap_len * _mid_tan_xz[0]
split_a_plug_overlap_z = split_junction_z - split_a_plug_overlap_len * _mid_tan_xz[1]


# SPLIT B geometry — bend↔tip joint. Cuts here aren't simple halfspaces
# because the overlap follows bend 2's curve; we cut with sub-sweep
# SOLIDS (swept along just the affected segment) instead.
#
# All `_path_*` constants below are in path-local 2D coords (XZ, Y=0,
# origin at world (water_tube_x, 0, zone5_z_top)), forming a closed-form
# re-derivation of `_gooseneck_path_at_origin`'s waypoint math so the
# sub-sweep paths align exactly with the full sweep through the joint.

# Bend-2 sub-arc covering the last overlap_len mm of bend 2 — separate
# arcs for the female socket (cut out of the middle piece) and the male
# plug (built up on the top piece).
split_b_socket_angle_rad = split_b_socket_overlap_len / gn_bend2_r
split_b_plug_angle_rad = split_b_plug_overlap_len / gn_bend2_r

# Cumulative path rotations (from the path origin's +Z tangent, CCW in XZ).
_path_total_rot = gn_bend1_sweep_rad + gn_bend2_sweep_rad  # rotation at end of bend 2
_path_socket_start_rot = _path_total_rot - split_b_socket_angle_rad
_path_socket_mid_rot = _path_total_rot - split_b_socket_angle_rad / 2.0
_path_plug_start_rot = _path_total_rot - split_b_plug_angle_rad
_path_plug_mid_rot = _path_total_rot - split_b_plug_angle_rad / 2.0

# Tangent unit-vectors in path-local XZ (= world XZ direction; Y=0).
# Tangent at rotation r = rotate((0, 1), r) = (-sin r, cos r).
_tan_after_bend1 = (-math.sin(gn_bend1_sweep_rad), math.cos(gn_bend1_sweep_rad))
_tan_after_bend2 = (-math.sin(_path_total_rot), math.cos(_path_total_rot))
_tan_at_socket_start = (
    -math.sin(_path_socket_start_rot), math.cos(_path_socket_start_rot),
)
_tan_at_plug_start = (
    -math.sin(_path_plug_start_rot), math.cos(_path_plug_start_rot),
)

# Path-local waypoints, working forward from the path origin.
_path_z_lift = gn_bend1_start_z - zone5_z_top
_path_p2 = (  # end of bend 1 / start of mid-straight
    -gn_bend1_r + gn_bend1_r * math.cos(gn_bend1_sweep_rad),
    _path_z_lift + gn_bend1_r * math.sin(gn_bend1_sweep_rad),
)
_path_p3 = (  # end of mid-straight / start of bend 2 (= SPLIT A junction)
    _path_p2[0] + gn_mid_straight_len * _tan_after_bend1[0],
    _path_p2[1] + gn_mid_straight_len * _tan_after_bend1[1],
)
# Bend-2 center: from p3 step gn_bend2_r perpendicular-left-of-tangent
# (CCW perp of tan1 = (-tan1_z, tan1_x) = (-cos θ1, -sin θ1)).
_path_center_bend2 = (
    _path_p3[0] - gn_bend2_r * math.cos(gn_bend1_sweep_rad),
    _path_p3[1] - gn_bend2_r * math.sin(gn_bend1_sweep_rad),
)
# Position on bend 2's arc at cumulative rotation r:
#   center + gn_bend2_r * (cos r, sin r).
_path_p4 = (  # end of bend 2 / start of tip (= SPLIT B junction)
    _path_center_bend2[0] + gn_bend2_r * math.cos(_path_total_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_total_rot),
)
_path_socket_start = (  # bend-2 point split_b_socket_overlap_len arc-length before p4
    _path_center_bend2[0] + gn_bend2_r * math.cos(_path_socket_start_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_socket_start_rot),
)
_path_socket_mid = (  # midpoint of the female socket sub-arc (for threePointArc)
    _path_center_bend2[0] + gn_bend2_r * math.cos(_path_socket_mid_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_socket_mid_rot),
)
_path_plug_start = (  # bend-2 point split_b_plug_overlap_len arc-length before p4
    _path_center_bend2[0] + gn_bend2_r * math.cos(_path_plug_start_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_plug_start_rot),
)
_path_plug_mid = (  # midpoint of the male plug sub-arc (for threePointArc)
    _path_center_bend2[0] + gn_bend2_r * math.cos(_path_plug_mid_rot),
    _path_center_bend2[1] + gn_bend2_r * math.sin(_path_plug_mid_rot),
)
_path_p5 = (  # end of tip
    _path_p4[0] + gn_tip_straight_len * _tan_after_bend2[0],
    _path_p4[1] + gn_tip_straight_len * _tan_after_bend2[1],
)

# World coords for SPLIT B mating-plane geometry — parity with SPLIT A.
split_b_junction_x = water_tube_x + _path_p4[0]
split_b_junction_z = zone5_z_top + _path_p4[1]
split_b_socket_overlap_x = water_tube_x + _path_socket_start[0]
split_b_socket_overlap_z = zone5_z_top + _path_socket_start[1]
split_b_plug_overlap_x = water_tube_x + _path_plug_start[0]
split_b_plug_overlap_z = zone5_z_top + _path_plug_start[1]


# ZONE 3 OUTER ARCH — full-height curve from wing bottom to zone 4
#
# The wing/fill arch is a single circular arc that spans the wing's
# full Z range (zone3_z_bottom at the low-X end up to zone4_z_top at
# X=fill_x_min), tangent-horizontal at the high end so it meets zone
# 4's flat top surface smoothly. The arch covers the full -X extent
# of the wing — there is no flat foot-top segment.
#
# Geometry: circular arc whose center is directly below the high end
# (fill_x_min, c_z) so the tangent there is horizontal. Solving
# distance(center, low_end) == distance(center, high_end) gives c_z.
_back_arch_dx = fill_x_min - shell_rect_x_min  # 29.46
back_arch_center_z = (
    (zone4_z_top + zone3_z_bottom) / 2.0
    - _back_arch_dx ** 2 / (2.0 * (zone4_z_top - zone3_z_bottom))
)  # ≈ 19.88
back_arch_r = zone4_z_top - back_arch_center_z  # ≈ 35.12
# Midpoint of the arc — angular midway between high end (90° from
# center, directly above) and low end.
_back_arch_a_low = math.atan2(zone3_z_bottom - back_arch_center_z,
                              shell_rect_x_min - fill_x_min)
_back_arch_a_mid = (math.pi / 2.0 + _back_arch_a_low) / 2.0
back_arch_mid_x = fill_x_min + back_arch_r * math.cos(_back_arch_a_mid)  # ≈ -6.28
back_arch_mid_z = back_arch_center_z + back_arch_r * math.sin(_back_arch_a_mid)  # ≈ 50.75


# ZONE 4.5 — block above the lever, up to the gooseneck bend start
#
# A tall block capping the lever swing volume from above and reaching
# up to the gooseneck bend start (Z=gn_bend1_start_z ≈ 78.78). The -X
# edge sits at zone45_front_x — chosen so the front margin (zone 4.5
# front X to zone 5's water-circle -X edge) matches the back margin
# (zone 4.5 back X to zone 5's flavor-pill +X edge), giving zone 5
# visually centered when looking down the X axis. The front edge sits
# past the pressed-lever's ridge line, but the lid's bottom on the arch
# curve still clears the lever's swing envelope by ~0.9 mm there.
#
# Bottom face = arch curve from (zone45_front_x, arch_z) up to
# (fill_x_min, zone4_z_top), then flat at zone4_z_top out to the +X
# cylinder back. Top face = flat at zone45_z_top. Both -X and +X
# edges curve inward at large |Y| via mirrored cylinder clips of
# radius shell_outer_r.

# Zone 5's tube-shell X extents at Y=0 — used to derive zone 4.5's
# matched-margin front X.
_z5_x_min = water_tube_x - tube_shell_water_r_outer  # -0.1375
_z5_x_max = flavor_tube_post_bend_x + (pill_width_x + 2.0 * zone5_wall) / 2.0  # 23.575

# Zone 4.5 X extents — back edge follows the rect column; front edge
# matched-margin from zone 5's X extents so zone 5 sits visually
# centered above zone 4.5.
zone45_front_x = _z5_x_min - (shell_rect_x_max - _z5_x_max)  # ≈ -1.9125

# 3 mm tall on the back side (where the lid sits flat on zone 4 top);
# taller on the front side because the lid bottom follows the back-arch
# curve down to ≈ Z=52.75.
zone45_z_top = zone4_z_top + 3.0  # 60.5
zone45_bot_z_at_front = (
    back_arch_center_z
    + math.sqrt(back_arch_r ** 2 - (zone45_front_x - fill_x_min) ** 2)
)  # ≈ 52.75

# Mid-point of the bottom arch sub-arc, between zone45_front_x end
# and fill_x_min end.
_a_front = math.atan2(
    zone45_bot_z_at_front - back_arch_center_z,
    zone45_front_x - fill_x_min,
)
_a_high = math.pi / 2.0  # fill_x_min end is directly above arch center
_a_mid45 = (_a_front + _a_high) / 2.0
zone45_bot_mid_x = fill_x_min + back_arch_r * math.cos(_a_mid45)
zone45_bot_mid_z = back_arch_center_z + back_arch_r * math.sin(_a_mid45)


# HEAT-SET INSERT POCKETS — mounting-plate retention. Two M3 brass
# heat-set inserts (ruthex M3 short, Amazon B09ZHSGHXD — Ø 4.6 knurl OD,
# Ø 3.9 body, 4 mm length) press into the bottom face of the shell. The
# mounting plate threads to them with M3 × 8 mm SS socket cap screws
# (McMaster 91223A413) coming up from below.
#
# Pocket location: θ = ±45° about the body center, r = 20 mm — the
# shell's "rear shoulder" wall material (between body bore and shell
# outer cylinder, well clear of the pill slot). All four wall margins
# hold ≥ 2 mm; pockets live entirely in zone 1 outer (Z < 16.25), with
# ~11 mm of solid material above the pocket ceiling.

insert_pocket_diameter = 4.0  # recommended install hole for ruthex M3 short
insert_pocket_depth = 5.0  # 4 mm insert engagement + 1 mm relief
insert_r_from_body = 20.0  # mm from body center to insert center
insert_theta_deg = 45.0  # angle from +X about body center
insert_x = insert_r_from_body * math.cos(math.radians(insert_theta_deg))  # ≈ 14.142
insert_y_offset = insert_r_from_body * math.sin(math.radians(insert_theta_deg))  # ≈ 14.142


# GEOMETRY BUILDERS

def shell_outer_cyl(z_bottom: float, z_height: float) -> cq.Workplane:
    """Shell's outer cylinder (R = shell_outer_r, centered at shell_center)
    over the given Z range. Used both as the zone-1 outer surface and as
    a clip volume for the rect-column zones."""
    return (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(shell_center_x, shell_center_y)
        .circle(shell_outer_r)
        .extrude(z_height)
    )


def water_tube_cyl(z_bottom: float, z_height: float) -> cq.Workplane:
    """Water-tube bore cylinder (R = water_hole_diameter/2 at
    (water_tube_x, 0)) over the given Z range."""
    return (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(water_tube_x, 0)
        .circle(water_hole_diameter / 2.0)
        .extrude(z_height)
    )


def body_bore_cyl(z_bottom: float, z_height: float) -> cq.Workplane:
    """Body bore cylinder (R = body_bore_diameter/2 at origin) over the
    given Z range.

    Two roles:

    - Clip in zones 2 and 3 (bore region), where the shell bore must
      follow the body's rect ∩ cyl outline rather than a plain rect.

    - Cut in zones 3-fill outer and zone 4 outer, ABOVE the body's
      plateau (Z > zone2_z_top = 39). The body has ended there, so this
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
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(body_bore_x, body_bore_y)
        .circle(body_bore_diameter / 2.0)
        .extrude(z_height)
    )


def _flavor_pill_flat_x_minus(z_bottom: float, z_height: float) -> cq.Workplane:
    """Flavor pill cutout at flavor_tube_x with the X- side flattened —
    same as the standard slot2D pill (pill_length_y × pill_width_x,
    Y-oriented), but with square corners at (flavor_pill_x_minus_edge,
    ±pill_length_y/2) instead of rounded transitions to the Y caps.
    Removes thin shell features on the X- side of the cutout that print
    poorly; the Y+/Y- caps and the X+ side stay rounded.

    Built as union of the standard slot2D and a rectangle that extends
    from flavor_pill_x_minus_edge to flavor_tube_x on the X- side, so
    the flat edge ends up at flavor_pill_x_minus_edge regardless of
    whether the slot2D edge is closer or farther.
    """
    pill = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(flavor_tube_x, 0)
        .slot2D(pill_length_y, pill_width_x, angle=90)
        .extrude(z_height)
    )
    fill_width = flavor_tube_x - flavor_pill_x_minus_edge
    fill_rect = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(flavor_tube_x - fill_width / 2.0, 0)
        .rect(fill_width, pill_length_y)
        .extrude(z_height)
    )
    return pill.union(fill_rect)


def build_zone1_outer() -> cq.Workplane:
    """Filled cylinder, from the deck up to zone1_outer_top.

    zone1_outer_top sits shell_outer_lip above the body's cylinder top
    (which is at zone1_z_top). That lift gives the shell a flat
    cylindrical wall directly above the body's cylinder top face,
    instead of starting the cove transition at the same Z where the
    body's cylinder ends.
    """
    return shell_outer_cyl(zone1_z_bottom, zone1_outer_top - zone1_z_bottom)


def build_zone1_inner_cut() -> cq.Workplane:
    """Combined body bore + flavor-tube pill, as one solid to subtract.

    Body bore extends from Z=zone1_z_bottom up to zone2_bore_bottom
    (= zone1_z_top + bore_clearance = 13.25), so the bore's Z step
    sits bore_clearance above the body's cyl top face at Z=13.

    Body bore and pill overlap by 0.4625 mm in X at the body/pill
    seam, so the result is a single connected hole.
    """
    body_bore = body_bore_cyl(zone1_z_bottom, zone2_bore_bottom - zone1_z_bottom)
    pill = _flavor_pill_flat_x_minus(zone1_z_bottom, zone1_height)
    return body_bore.union(pill)


def build_insert_pockets() -> cq.Workplane:
    """Two heat-set insert pockets in the shell's bottom face.

    Each pocket is a Ø insert_pocket_diameter cylinder extruded UP from
    Z=0 by insert_pocket_depth, positioned at (insert_x, ±insert_y_offset)
    — the rear-shoulder zones at θ=±45°, r=20 from the body center.
    Lives entirely within zone 1 outer (which extends to Z =
    zone1_outer_top = 16.25), with ~11 mm of solid material above the
    pocket ceiling.

    Returned as a single union for the caller to subtract from the
    shell solid.
    """
    return (
        cq.Workplane("XY")
        .workplane(offset=zone1_z_bottom)
        .pushPoints([(insert_x, +insert_y_offset), (insert_x, -insert_y_offset)])
        .circle(insert_pocket_diameter / 2.0)
        .extrude(insert_pocket_depth)
    )


def _rect_cove_cyl(
    center_x: float, center_y: float,
    rect_x_width: float, rect_y_width: float,
    z_bottom: float, z_top: float,
    clip_cyl: cq.Workplane,
) -> cq.Workplane:
    """Rect column with cove-filleted ±Y faces, clipped to a cylinder.

    Construction (mirrors the body's `build_transition_cove`):
      - Rectangle column from z_bottom to z_top, centered at (center_x,
        center_y), with the given X/Y widths.
      - Filler block (cove_r wide × cove_r tall, full X extent) on each
        Y face at the bottom of the column.
      - Cove cutter (cylinder along X axis, R = cove_r) scoops a concave
        arc from each filler.
      - The supplied clip cylinder rounds the rect corners (and, in the
        bore case, the rect X faces) to follow the cylinder profile.
    """
    z_height = z_top - z_bottom
    rect_y_half = rect_y_width / 2.0
    ext_x = rect_x_width / 2.0 + 2.0  # generous half-extent in X for filler/cutter

    rect = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(center_x, center_y)
        .rect(rect_x_width, rect_y_width)
        .extrude(z_height)
    )

    def filler(y_sign: int) -> cq.Workplane:
        flat_y = center_y + y_sign * rect_y_half
        blk_cy = flat_y + y_sign * (cove_r / 2.0)
        return (
            cq.Workplane("XY")
            .workplane(offset=z_bottom)
            .moveTo(center_x, blk_cy)
            .rect(2.0 * ext_x, cove_r)
            .extrude(cove_r)
        )

    def cove_cutter(y_sign: int) -> cq.Workplane:
        flat_y = center_y + y_sign * rect_y_half
        cove_cy = flat_y + y_sign * cove_r
        cove_cz = z_bottom + cove_r
        return (
            cq.Workplane("YZ")
            .workplane(offset=center_x - ext_x)
            .moveTo(cove_cy, cove_cz)
            .circle(cove_r)
            .extrude(2.0 * ext_x)
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
    """Outer geometry for zone 2 — rect column with cove-filleted ±Y
    faces, corners clipped to the shell's outer cylinder.

    Zone 2 OUTER starts shell_outer_lip above the body's cylinder top
    (i.e., at Z = zone2_outer_bot = 16, not at the body's transition Z
    of 13). This leaves a 3 mm cylindrical shell wall above the body's
    cylinder top face. The bore is unaffected — see build_zone2_inner_cut.
    """
    z_height = zone2_z_top - zone2_outer_bot
    return _rect_cove_cyl(
        shell_center_x, shell_center_y,
        shell_rect_x_width, shell_rect_y_width,
        zone2_outer_bot, zone2_z_top,
        shell_outer_cyl(zone2_outer_bot, z_height),
    )


def build_zone2_inner_cut() -> cq.Workplane:
    """Inner cut for zone 2 — mirrors the body's cross-section with
    bore_clearance per side.

    The bore is built with the SAME construction as the body's outer
    (rect column + cove-filleted ±Y faces + cylinder clip). This matters
    in two places:
      1. Above the cove (Z=18 → 39), the body's rect column is itself
         intersected with body_r=15.75 — so its X faces and corners
         are curved arcs, not flat. The bore must follow that.
      2. Through the cove zone (Z=13 → 18), the body bulges OUT in Y
         to meet the cylinder ledge. A simple Ø32 cylindrical bore
         here would extend past the shell's outer cove surface and
         eat through the wall. Mirroring the body's filler+cove
         keeps the bore inside the shell.

    Plus the flavor-tube pill all the way through.
    """
    bore_zone2_height = zone2_z_top - zone2_bore_bottom
    bore = _rect_cove_cyl(
        body_bore_x, body_bore_y,
        body_bore_rect_long, body_bore_rect_short,
        zone2_bore_bottom, zone2_z_top,
        body_bore_cyl(zone2_bore_bottom, bore_zone2_height),
    )
    # Flavor-tube pill (full Z range — pill has no body-equivalent
    # transition, so it just runs from zone2_z_bottom continuously).
    pill = _flavor_pill_flat_x_minus(zone2_z_bottom, zone2_height)
    return bore.union(pill)


def _arch_extrude(y_bottom: float, y_height: float) -> cq.Workplane:
    """The outer arch profile in XZ — flat bottom at zone3_z_bottom, flat
    top at zone4_z_top from +X back to fill_x_min, then the back-arch
    curve down-left to shell_rect_x_min — extruded across
    [y_bottom, y_bottom + y_height].

    Shared by the zone-3 wings (extruded across each wing's Y thickness)
    and the zone-3 plateau fill (extruded across the central Y range).
    """
    return (
        cq.Workplane("XZ")
        .workplane(offset=y_bottom)
        .moveTo(shell_rect_x_min, zone3_z_bottom)
        .lineTo(shell_rect_x_max, zone3_z_bottom)
        .lineTo(shell_rect_x_max, zone4_z_top)
        .lineTo(fill_x_min, zone4_z_top)
        .threePointArc((back_arch_mid_x, back_arch_mid_z),
                       (shell_rect_x_min, zone3_z_bottom))
        .close()
        .extrude(y_height)
    )


def build_zone3_outer() -> cq.Workplane:
    """Two arch wings at ±Y wrapping the body's arch ridges."""
    wing_thickness = wing_outer_y - wing_inner_y
    wings = _arch_extrude(+wing_inner_y, +wing_thickness).union(
        _arch_extrude(-wing_outer_y, +wing_thickness)
    )
    return wings.intersect(shell_outer_cyl(zone3_z_bottom, zone4_z_top - zone3_z_bottom))


def build_zone3_inner_cut() -> cq.Workplane:
    """Two arch bores at ±Y mirroring the body arches with bore_clearance."""
    bore_x_oversize = body_bore_diameter / 2.0 + 2.0  # generous; bore-cyl-clipped below

    def bore(y_bottom: float, y_height: float) -> cq.Workplane:
        return (
            cq.Workplane("XZ")
            .workplane(offset=y_bottom)
            .moveTo(-bore_x_oversize, zone3_z_bottom)
            .lineTo(+bore_x_oversize, zone3_z_bottom)
            .lineTo(+bore_x_oversize, shell_arch_bore_foot_top_z)
            .threePointArc((0, shell_arch_bore_peak_z),
                           (-bore_x_oversize, shell_arch_bore_foot_top_z))
            .close()
            .extrude(y_height)
        )

    bore_thickness = shell_arch_bore_outer_y - shell_arch_bore_inner_y
    bores = bore(+shell_arch_bore_inner_y, +bore_thickness).union(
        bore(-shell_arch_bore_outer_y, +bore_thickness)
    )
    return bores.intersect(body_bore_cyl(zone3_z_bottom, shell_arch_bore_peak_z - zone3_z_bottom))


def build_zone3_fill_outer() -> cq.Workplane:
    """Plateau fill behind fill_x_min — same arch profile as the wings,
    extruded across the plateau Y range. The body bore column is cut
    away (see body_bore_cyl for why).
    """
    fill_y_thickness = 2.0 * wing_inner_y  # 13.5
    z_height = zone4_z_top - zone3_z_bottom

    arch_solid = _arch_extrude(-wing_inner_y, fill_y_thickness)
    keep_x_box = (
        cq.Workplane("XY")
        .workplane(offset=zone3_z_bottom)
        .moveTo((fill_x_min + shell_rect_x_max) / 2.0, 0)
        .rect(shell_rect_x_max - fill_x_min, fill_y_thickness)
        .extrude(z_height)
    )
    return (
        arch_solid
        .intersect(keep_x_box)
        .intersect(shell_outer_cyl(zone3_z_bottom, z_height))
        .cut(body_bore_cyl(zone3_z_bottom, z_height))
    )


def build_zone3_fill_inner_cut() -> cq.Workplane:
    """Tube cutouts through the plateau fill: water tube + straight flavor
    pill at flavor_tube_x. The bend lives in the tube shell above (the
    LLDPE flavor tubes flex through the socket area on the way down)."""
    z_height = shell_arch_peak_z - zone3_z_bottom
    water_hole = water_tube_cyl(zone3_z_bottom, z_height)
    flavor_pill = _flavor_pill_flat_x_minus(zone3_z_bottom, z_height)
    return water_hole.union(flavor_pill)


def build_zone4_outer() -> cq.Workplane:
    """Vertical extrusion of the cyl-clipped rect at X ≥ fill_x_min.

    Cross-section matches zone 2's outline above its cove (rect ∩ outer
    cyl, no cove since the cove only lives at Z=16.25→21.25 in zone 2).
    The same outline is extruded straight up from zone4_z_bottom to
    zone4_z_top — straight vertical sides, no taper. Wall thickness
    around the tubes is whatever falls out of (outer minus inner cut),
    not a fixed 3 mm offset.

    The body bore column is cut away (see body_bore_cyl for why) —
    the central column stays open, so the flavor tubes' S-bend passes
    through unwrapped and printed support material can be extracted
    from the dispense channel.
    """
    z_height = zone4_height
    rect = (
        cq.Workplane("XY")
        .workplane(offset=zone4_z_bottom)
        .moveTo(shell_center_x, shell_center_y)
        .rect(shell_rect_x_width, shell_rect_y_width)
        .extrude(z_height)
    )
    # X ≥ fill_x_min half-space — oversized in Y and Z so it doesn't clip
    # anything else in the rect.
    keep_pos_x = (
        cq.Workplane("XY")
        .workplane(offset=zone4_z_bottom - 1)
        .moveTo(fill_x_min + 50, 0)
        .rect(100, 200)
        .extrude(z_height + 2)
    )
    return (
        rect
        .intersect(shell_outer_cyl(zone4_z_bottom, z_height))
        .intersect(keep_pos_x)
        .cut(body_bore_cyl(zone4_z_bottom, zone4_height))
    )


def build_zone4_inner_cut() -> cq.Workplane:
    """Tube cavity: water-tube cyl + straight flavor pill at flavor_tube_x.
    Straight cuts only — the flavor bend lives in the tube shell above."""
    water_inner = water_tube_cyl(zone4_z_bottom, zone4_height)
    flavor_pill = _flavor_pill_flat_x_minus(zone4_z_bottom, zone4_height)
    return water_inner.union(flavor_pill)


def build_zone45_outer() -> cq.Workplane:
    """Zone 4.5 — tall block capping the lever swing volume, reaching
    up to the gooseneck bend start.

    XZ profile (CCW), extruded across full Y range, then clipped by
    two cylinders (back + front, mirrored across the block's X
    midpoint) so the +X and -X edges have matching rounded curves:
      start at (zone45_front_x, zone45_bot_z_at_front)
      → arch up to (fill_x_min, zone4_z_top)
      → flat to (shell_rect_x_max, zone4_z_top)
      → vertical up to (shell_rect_x_max, zone45_z_top)
      → flat back to (zone45_front_x, zone45_z_top)
      → close (vertical down to start)

    Back clip: shell_outer_r cylinder centered at shell_center_x — the
    same cylinder zones 1-4 use (curves the +X corner inward at large |Y|).
    Front clip: shell_outer_r cylinder centered at zone45_front_x +
    shell_outer_r, mirroring the back clip across the block's X
    midpoint. At Y=0 both clips are tangent to the block's -X / +X
    edges; at |Y| = shell_rect_y_half both edges curve inward by the
    same amount.
    """
    y_half = shell_rect_y_half  # 11.75
    profile_solid = (
        cq.Workplane("XZ")
        .workplane(offset=-y_half)
        .moveTo(zone45_front_x, zone45_bot_z_at_front)
        .threePointArc(
            (zone45_bot_mid_x, zone45_bot_mid_z),
            (fill_x_min, zone4_z_top),
        )
        .lineTo(shell_rect_x_max, zone4_z_top)
        .lineTo(shell_rect_x_max, zone45_z_top)
        .lineTo(zone45_front_x, zone45_z_top)
        .close()
        .extrude(2.0 * y_half)
    )

    z_min = zone45_bot_z_at_front
    clip_height = (zone45_z_top - z_min) + 1.0
    back_clip = shell_outer_cyl(z_min - 0.5, clip_height)
    front_clip = (
        cq.Workplane("XY")
        .workplane(offset=z_min - 0.5)
        .moveTo(zone45_front_x + shell_outer_r, shell_center_y)
        .circle(shell_outer_r)
        .extrude(clip_height)
    )
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


def _gooseneck_path_at_origin() -> cq.Workplane:
    """Gooseneck path in XZ at origin: vertical lift to bend 1, bend 1,
    mid straight, bend 2, tip straight. Bends toward -X. Bend 1 uses
    gn_bend1_r, bend 2 uses gn_bend2_r (independent radii).

    Path origin (s=0) is at zone5_z_top — the seam between the tube
    shell vertical extrusion below and the gooseneck sweep above.
    """
    z_lift = gn_bend1_start_z - zone5_z_top

    p_bottom = (0.0, 0.0)
    p_bend_start = (0.0, z_lift)

    mid1, end1, tan1 = _arc_from_tangent(
        p_bend_start, (0.0, 1.0), gn_bend1_r, gn_bend1_sweep_rad, ccw=True
    )
    mid_end = (end1[0] + gn_mid_straight_len * tan1[0],
               end1[1] + gn_mid_straight_len * tan1[1])
    mid2, end2, tan2 = _arc_from_tangent(
        mid_end, tan1, gn_bend2_r, gn_bend2_sweep_rad, ccw=True
    )
    tip_end = (end2[0] + gn_tip_straight_len * tan2[0],
               end2[1] + gn_tip_straight_len * tan2[1])

    return (
        cq.Workplane("XZ")
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

    Single connected region: water slot + flavor pill (offset +X) +
    fill rectangle between them. The mode='a' flag unions each shape
    into the running sketch so the sweep sees one face.

    The water and flavor sides are both Y-oriented slots (not circle +
    pill); see this module's tube_shell_y_outer / tube_shell_water_r_outer
    constants for the underlying vocabulary.

    NOTE: cq.Sketch.slot(w, h) takes w as the *straight section* length
    (between the rounded ends), not the overall length — opposite of
    Workplane.slot2D's convention. Total length along the long axis is
    w + h, so w_straight = total - h.
    """
    water_x_width = 2.0 * tube_shell_water_r_outer
    water_slot_straight = tube_shell_y_outer - water_x_width
    pill_short_total = pill_width_x + 2.0 * zone5_wall
    pill_straight = tube_shell_y_outer - pill_short_total
    return (
        cq.Sketch()
        .slot(water_slot_straight, water_x_width, angle=90)
        .push([(flavor_offset_x_from_water, 0)])
        .slot(pill_straight, pill_short_total, angle=90, mode="a")
        .reset()
        .push([(flavor_offset_x_from_water / 2.0, 0)])
        .rect(flavor_offset_x_from_water, tube_shell_y_outer, mode="a")
        .clean()
    )


def _tube_shell_inner_sketch() -> cq.Sketch:
    """Tube-shell inner cross-section as a Sketch, for the gooseneck
    sweep. See _tube_shell_outer_sketch's note about cq.Sketch.slot
    conventions."""
    pill_straight = pill_length_y - pill_width_x  # 3.175
    return (
        cq.Sketch()
        .circle(water_hole_diameter / 2.0)
        .push([(flavor_offset_x_from_water, 0)])
        .slot(pill_straight, pill_width_x, angle=90, mode="a")
        .clean()
    )


def _sweep_along_gooseneck(sketch: cq.Sketch) -> cq.Workplane:
    """Sweep the given tube-shell cross-section along the gooseneck path,
    then place at (water_tube_x, 0, zone5_z_top) — the seam atop zone 5's
    vertical extrusion of the same cross-section."""
    profile = cq.Workplane("XY").placeSketch(sketch)
    swept = profile.sweep(_gooseneck_path_at_origin(), transition="right")
    return swept.translate((water_tube_x, 0, zone5_z_top))


def build_zone6_outer() -> cq.Workplane:
    return _sweep_along_gooseneck(_tube_shell_outer_sketch())


def build_zone6_inner_cut() -> cq.Workplane:
    return _sweep_along_gooseneck(_tube_shell_inner_sketch())


# SPLIT — geometry builders for the angled-spout ↔ upper-bend joint.

def _tube_shell_outer_shrunk_sketch(shrink: float) -> cq.Sketch:
    """Outer cross-section offset INWARD by `shrink` mm.

    Reconstructed with parameters reduced by 2·shrink so the resulting
    boundary is the exact 2D inward offset of _tube_shell_outer_sketch:
    each slot's width and total Y-length shrink by 2·shrink (centers
    fixed; straight-section length unchanged), and the fill rect's Y
    matches the new shorter slot Y. Slot centers + fill-rect X are
    unchanged, so the three primitives still union into one connected
    region everywhere the original did.
    """
    water_x_width = 2.0 * (tube_shell_water_r_outer - shrink)
    new_y_outer = tube_shell_y_outer - 2.0 * shrink
    water_slot_straight = new_y_outer - water_x_width
    pill_short_total = pill_width_x + 2.0 * (zone5_wall - shrink)
    pill_straight = new_y_outer - pill_short_total
    return (
        cq.Sketch()
        .slot(water_slot_straight, water_x_width, angle=90)
        .push([(flavor_offset_x_from_water, 0)])
        .slot(pill_straight, pill_short_total, angle=90, mode="a")
        .reset()
        .push([(flavor_offset_x_from_water / 2.0, 0)])
        .rect(flavor_offset_x_from_water, new_y_outer, mode="a")
        .clean()
    )


def _build_zone6_outer_shrunk(shrink: float) -> cq.Workplane:
    """Gooseneck outer with the cross-section offset inward by `shrink`.

    Same path as build_zone6_outer; only the swept profile changes.
    Used twice for the split joint:
      - As the SOCKET-CAVITY cutter on the angled-spout (bottom) piece —
        intersected with the 20 mm overlap slab and cut from the bottom
        shell, leaving a `shrink`-thick uniform outer wall.
      - As the PLUG OUTER on the upper-bend (top) piece — intersected
        with the same slab, then the original bores cut through it.
    """
    return _sweep_along_gooseneck(_tube_shell_outer_shrunk_sketch(shrink))


def _split_plane_halfspace(origin: tuple, normal: tuple, sign: int,
                           extent: float = 600.0) -> cq.Workplane:
    """Solid filling the halfspace on one side of a plane.

    sign = +1: halfspace in the +normal direction (above the plane).
    sign = -1: halfspace in the −normal direction (below the plane).
    The halfspace is a 2·extent × 2·extent × extent box stuck to the
    plane — extent must comfortably envelop the shell on that side.
    """
    plane = cq.Plane(
        origin=cq.Vector(*origin),
        xDir=cq.Vector(0, 1, 0),  # Y axis lies in the plane (normal is in XZ)
        normal=cq.Vector(*normal),
    )
    return cq.Workplane(plane).rect(2.0 * extent, 2.0 * extent).extrude(sign * extent)


def _split_overlap_slab(overlap_x: float, overlap_z: float) -> cq.Workplane:
    """The slab between the overlap plane (below) and the junction plane
    (above), both perpendicular to the angled-spout tangent. Caller picks
    which overlap-plane coords to use — socket (deeper) vs plug (shorter).

    Intersect with shrunk-outer / bores to get the male plug or the
    socket-cavity cutter — only the relevant spout chunk, not the full sweep.
    """
    above_overlap = _split_plane_halfspace(
        (overlap_x, 0.0, overlap_z), split_normal, sign=+1,
    )
    below_junction = _split_plane_halfspace(
        (split_junction_x, 0.0, split_junction_z), split_normal, sign=-1,
    )
    return above_overlap.intersect(below_junction)


# SPLIT B — sub-segment sweeps for the bend↔tip joint.
#
# Unlike SPLIT A, this joint can't use halfspace cuts: the junction
# plane (perpendicular to the tip's tangent) tilts so steeply through
# the model that an "above junction" halfspace clips a sliver of the
# mid-straight's lower end (mid-straight start is ≈+1.7 mm into the
# +tan2 halfspace despite being on the back side of the path). We
# isolate the affected regions with CUTTING SOLIDS instead — fresh
# sweeps along the dispense-tip path and the last-20-mm bend-2 sub-arc.

def _sweep_segment_in_path_local(
    start_xz: tuple,
    tangent_xz: tuple,
    path_workplane: cq.Workplane,
    sketch: cq.Sketch,
) -> cq.Workplane:
    """Sweep `sketch` along `path_workplane`, with the profile placed
    perpendicular to `tangent_xz` at `start_xz`. Inputs are in
    path-local 2D coords on the XZ plane (Y=0). Result is translated
    by (water_tube_x, 0, zone5_z_top) to land in world.

    The profile workplane's local-X axis is set to the 90° CW rotation
    of the tangent in XZ — i.e. `(tangent_xz[1], 0, -tangent_xz[0])`.
    This matches the rigid-frame orientation that
    `_sweep_along_gooseneck` produces at any point along the gooseneck
    (local-Y stays = world Y; local-X rotates around Y with the path).
    Consequence: a sub-sweep starting partway along the gooseneck path
    aligns cross-section-for-cross-section with the full sweep there,
    so cutting one from the other leaves no residue at the seam.
    """
    normal = (tangent_xz[0], 0.0, tangent_xz[1])
    xdir = (tangent_xz[1], 0.0, -tangent_xz[0])
    plane = cq.Plane(
        origin=cq.Vector(start_xz[0], 0.0, start_xz[1]),
        xDir=cq.Vector(*xdir),
        normal=cq.Vector(*normal),
    )
    profile = cq.Workplane(plane).placeSketch(sketch)
    swept = profile.sweep(path_workplane, transition="right")
    return swept.translate((water_tube_x, 0, zone5_z_top))


def _tip_subpath() -> cq.Workplane:
    """The dispense-tip's 25 mm straight path in path-local XZ coords.
    Start = _path_p4 (end of bend 2 / SPLIT B junction);
    end   = _path_p5 (= start + gn_tip_straight_len along tan2)."""
    return (
        cq.Workplane("XZ")
        .moveTo(*_path_p4)
        .lineTo(*_path_p5)
    )


def _bend_overlap_subarc(start_xz: tuple, mid_xz: tuple) -> cq.Workplane:
    """A bend-2 sub-arc from `start_xz` through `mid_xz` to `_path_p4`
    (the SPLIT B junction), in path-local XZ. Caller supplies the
    socket-length or plug-length endpoints."""
    return (
        cq.Workplane("XZ")
        .moveTo(*start_xz)
        .threePointArc(mid_xz, _path_p4)
    )


def _build_tip_section(sketch: cq.Sketch) -> cq.Workplane:
    """Sweep `sketch` along just the dispense-tip path. Use for:
      - tip outer (with _tube_shell_outer_sketch) — the visible spout
        portion of the top piece, and the cutter that removes the tip
        from the middle piece;
      - tip inner (with _tube_shell_inner_sketch) — the bores cut
        through the tip section so the tubes can pass."""
    return _sweep_segment_in_path_local(
        _path_p4, _tan_after_bend2, _tip_subpath(), sketch,
    )


def _build_bend_overlap(sketch: cq.Sketch, *, side: str) -> cq.Workplane:
    """Sweep `sketch` along the last `split_b_<side>_overlap_len` mm of
    bend 2 (the SPLIT B overlap zone). `side` is "socket" (longer, cut
    from the middle piece's female cavity) or "plug" (shorter, used to
    build the top piece's male tongue and its bore cut)."""
    if side == "socket":
        start_xz, mid_xz, tan_start = _path_socket_start, _path_socket_mid, _tan_at_socket_start
    elif side == "plug":
        start_xz, mid_xz, tan_start = _path_plug_start, _path_plug_mid, _tan_at_plug_start
    else:
        raise ValueError(f"side must be 'socket' or 'plug', got {side!r}")
    return _sweep_segment_in_path_local(
        start_xz, tan_start, _bend_overlap_subarc(start_xz, mid_xz), sketch,
    )


def build_lever_clearance() -> cq.Workplane:
    """Single triangular ramp wedge cut into the top of the rect column.

    In the XZ plane, the cut is a right triangle:
      - top edge flat at Z=zone2_z_top (39), from X=lever_ramp_x_min
        to X=lever_ramp_x_start
      - vertical edge at X=lever_ramp_x_min, dropping lever_ramp_depth
        below Z=39
      - sloped (ramp) edge from the bottom of the vertical edge back up
        to the +X start point at Z=39 (slope is whatever falls out of
        the two anchor points — ~12.5°, not a parameter)

    Extruded ±lever_clearance_y_half in Y. Single piece.
    """
    z_top = zone2_z_top
    z_bot = z_top - lever_ramp_depth
    y_half = lever_clearance_y_half
    return (
        cq.Workplane("XZ")
        .workplane(offset=-y_half)
        .polyline([
            (lever_ramp_x_min, z_bot),
            (lever_ramp_x_min, z_top),
            (lever_ramp_x_start, z_top),
        ]).close()
        .extrude(2.0 * y_half)
    )


# Tube-shell vertical section — wraps inside the lid. Spans the lid's
# Z range (zone5_z_bottom = zone4_z_top up to zone5_z_top). The outer
# cross-section is dominated by the lid block in the union, so it's not
# visible from outside; the wraps only carry the bore through the lid.
# Above zone5_z_top the gooseneck (zone 6) emerges with the tube wraps
# becoming visible as the spout.


def _tube_shell_outer_section(z_bottom: float, z_height: float) -> cq.Workplane:
    """Tube wrap outer (water Y-slot + flavor pill + fill rect, all
    zone5_wall on the X sides) extruded vertically over the given Z
    range. See _tube_shell_outer_sketch for the cross-section."""
    water_x_width = 2.0 * tube_shell_water_r_outer
    water_outer = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(water_tube_x, 0)
        .slot2D(tube_shell_y_outer, water_x_width, angle=90)
        .extrude(z_height)
    )
    flavor_outer = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(flavor_tube_post_bend_x, 0)
        .slot2D(tube_shell_y_outer, pill_width_x + 2.0 * zone5_wall, angle=90)
        .extrude(z_height)
    )
    fill_rect = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo((water_tube_x + flavor_tube_post_bend_x) / 2.0, 0)
        .rect(flavor_offset_x_from_water, tube_shell_y_outer)
        .extrude(z_height)
    )
    return water_outer.union(flavor_outer).union(fill_rect)


def _tube_shell_inner_section(z_bottom: float, z_height: float) -> cq.Workplane:
    """Tube hole cross-section (water cyl + flavor pill) extruded vertically."""
    flavor_inner = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(flavor_tube_post_bend_x, 0)
        .slot2D(pill_length_y, pill_width_x, angle=90)
        .extrude(z_height)
    )
    return water_tube_cyl(z_bottom, z_height).union(flavor_inner)


def build_shell() -> cq.Workplane:
    """Touch-Flo shell — full reference solid (un-split).

    For printing, this solid is split into THREE pieces along the
    gooseneck at two 20 mm slip-fit joints — see build_shell_bottom
    (angled-spout), build_shell_middle (upper-bend), and
    build_shell_top (dispense-tip). This single-solid form is kept for
    assembly visualization and as the source the bottom / middle
    splits operate on.

    All zones unioned into one solid:
      - Zones 1–4: body wraps + lever clearance
      - Zone 4.5: lid above the lever
      - Zone 5: tube wraps inside the lid (provides the bore through the
                lid; outer is dominated by the lid in the union)
      - Zone 6: gooseneck (the visible spout above the lid)

    Gooseneck overhangs will need slicer-generated supports.
    """
    outer = (
        build_zone1_outer()
        .union(build_zone2_outer())
        .union(build_zone3_outer())
        .union(build_zone3_fill_outer())
        .union(build_zone4_outer())
        .union(build_zone45_outer())
        .union(_tube_shell_outer_section(zone5_z_bottom, zone5_height))
        .union(build_zone6_outer())
    )
    inner = (
        build_zone1_inner_cut()
        .union(build_zone2_inner_cut())
        .union(build_zone3_inner_cut())
        .union(build_zone3_fill_inner_cut())
        .union(build_zone4_inner_cut())
        .union(_tube_shell_inner_section(zone5_z_bottom, zone5_height))
        .union(build_zone6_inner_cut())
        .union(build_lever_clearance())
        .union(build_insert_pockets())
    )
    return outer.cut(inner)


def build_shell_bottom(full_shell: cq.Workplane | None = None) -> cq.Workplane:
    """Angled-spout piece — bottom half of the split, with the female socket.

    Everything below the SPLIT A junction plane, with the top 20 mm of
    the spout hollowed out down to a 2 mm uniform wall (the female
    socket) that receives build_shell_middle's male plug. The original
    water + flavor bores in the overlap zone are absorbed into the
    socket cavity.
    """
    full = build_shell() if full_shell is None else full_shell
    below_junction = _split_plane_halfspace(
        (split_junction_x, 0.0, split_junction_z), split_normal, sign=-1,
    )
    socket_cavity = _build_zone6_outer_shrunk(split_a_socket_shrink).intersect(
        _split_overlap_slab(split_a_socket_overlap_x, split_a_socket_overlap_z)
    )
    return full.intersect(below_junction).cut(socket_cavity)


def build_shell_middle(full_shell: cq.Workplane | None = None) -> cq.Workplane:
    """Upper-bend piece — middle of the split, with the male plug for
    SPLIT A (bottom end) and the female socket for SPLIT B (top end).

    Built in two stages:
      1. SPLIT A (spout↔bend): keep everything ABOVE the SPLIT A
         junction plane, then add the angled-spout-direction male plug
         (same construction as the previous two-piece build_shell_top).
      2. SPLIT B (bend↔tip): cut out the dispense-tip section, then cut
         out a shrunk-cross-section sweep along the last 20 mm of
         bend 2 — leaving a 2 mm female socket wall over the curved
         overlap zone. Original bores in that zone are absorbed into
         the socket cavity.
    """
    full = build_shell() if full_shell is None else full_shell

    # SPLIT A — keep upper-bend + tip side; add the male plug going down
    # into the angled-spout's socket.
    above_junction_a = _split_plane_halfspace(
        (split_junction_x, 0.0, split_junction_z), split_normal, sign=+1,
    )
    overlap_slab_a = _split_overlap_slab(
        split_a_plug_overlap_x, split_a_plug_overlap_z
    )
    plug_outer_a = _build_zone6_outer_shrunk(split_a_plug_shrink).intersect(overlap_slab_a)
    plug_bores_a = build_zone6_inner_cut().intersect(overlap_slab_a)
    plug_a = plug_outer_a.cut(plug_bores_a)
    bend_plus_tip = full.intersect(above_junction_a).union(plug_a)

    # SPLIT B — strip the dispense tip off the top, then hollow out the
    # socket overlap region of bend 2 down to the socket-wall thickness.
    tip_section = _build_tip_section(_tube_shell_outer_sketch())
    bend_socket_cavity = _build_bend_overlap(
        _tube_shell_outer_shrunk_sketch(split_b_socket_shrink), side="socket",
    )
    return bend_plus_tip.cut(tip_section).cut(bend_socket_cavity)


def build_shell_top(full_shell: cq.Workplane | None = None) -> cq.Workplane:
    """Dispense-tip piece — top of the split, with the male plug for
    SPLIT B (bend↔tip joint).

    Constructed entirely from fresh sub-sweeps (not extracted from the
    full shell), so the plug follows bend 2's curve back through the
    last 20 mm of arc:
      - Tip section = outer sweep along the 25 mm tip path, minus the
        original water + flavor bores.
      - Male plug = SHRUNK-outer sweep along the last 20 mm of bend 2
        (so its curved OD ≡ middle piece's curved socket ID), minus the
        original bores so the tubes pass through unbroken.
    The two solids union at the SPLIT B junction plane.

    `full_shell` accepted for signature parity with the other two
    builders but unused.
    """
    _ = full_shell  # unused — top piece doesn't derive from the full shell

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


if __name__ == "__main__":
    main()
