"""
Touch-Flo shell — printed shroud that wraps around the harvested faucet
body, the flavor tubes, and the lever swing volume. Sits on top of the
touch-flo-mounting-plate.

Grown bottom-up, one zone at a time. Currently covers zones 1, 2,
and 3 — through the body's arch peaks at Z=46 (shell goes ~3 mm
above). See the per-section comments for what each zone does and why.

Regenerate:  tools/cad-venv/bin/python generate_step_cadquery.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import export_step


# SHELL CENTER (lateral)

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
flavor_tube_x = 18.925  # = BODY_R + tube_R = 15.75 + 3.175
flavor_tube_hole_dia = 6.85  # = 6.35 OD + 0.5 mm clearance
flavor_tube_y_offset = 3.175  # = tube_R, tubes touch at Y=0
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
# Wall thickness is set at the body bore's farthest edge from the
# shell center. The body bore is offset by shell_center_x mm from
# shell center, so its farthest perimeter point (in -X) sits at
# distance shell_center_x + body_bore_radius from the shell center.
#
# With shell_center_x chosen to balance walls on both sides (body
# bore -X edge vs. flavor pill +X edge), the two extremes are
# equidistant from the shell center: 19.175 mm. wall_thickness_min
# applies cleanly to both.
# Target at body bore's -X edge AND at the flavor pill's +X edge
# (both at 19.175 mm from shell center, by construction).
wall_thickness_min = 3.0

_body_bore_farthest_from_shell_center = (
    (shell_center_x - body_bore_x) + body_bore_diameter / 2.0
)  # = 19.175 mm

shell_outer_r = _body_bore_farthest_from_shell_center + wall_thickness_min
shell_outer_diameter = 2.0 * shell_outer_r  # = 44.35 mm


# ZONE 2 — cylinder → rectangle transition + rect column

zone2_z_bottom = zone1_z_top  # 13.0
zone2_z_top = 39.0  # body plateau
zone2_height = zone2_z_top - zone2_z_bottom  # 26.0

# Body rectangle dimensions (mirrored from valve-body-reference)
body_rect_long = 31.5  # X
body_rect_short = 17.0  # Y

# Body bore in zone 2 — match body rect with clearance per side
body_bore_rect_long = body_rect_long  + 2.0 * bore_clearance  # 32.0
body_bore_rect_short = body_rect_short + 2.0 * bore_clearance  # 17.5

# Cove transition fillet (matches the body's transition_fillet_r)
cove_r = 6.0

# Bore Z transitions lift by bore_clearance above the body's Z
# transitions so face-to-face Z interfaces get the same per-side
# clearance as X/Y. The body's cylinder top face sits at Z=zone1_z_top
# (=13); the shell's bore step (where the bore narrows from cyl to
# rect+filler+cove) sits bore_clearance higher.
zone2_bore_bottom = zone1_z_top + bore_clearance  # 13.25
cove_top_z = zone2_bore_bottom + cove_r  # 18.25 (bore cove top)

# Outer surface lifts by WALL + bore_clearance above the body's cyl
# top, so that 3 mm of solid shell wall sits above the bore step
# (i.e., 3.25 mm above the body's cyl top face, with the extra
# 0.25 mm being the bore's Z clearance). Without the lift, the outer
# cove tangents the body's cyl ledge at Z=13 from above and there
# would be no vertical wall material over the body's top face.
shell_outer_lip = wall_thickness_min + bore_clearance  # 3.25
zone1_outer_top = zone1_z_top + shell_outer_lip  # 16.25
zone2_outer_bot = zone1_outer_top  # 16.25
cove_top_outer_z = zone2_outer_bot + cove_r  # 21.25 (outer cove top)


# LEVER SWING CLEARANCE
#
# A single triangular ramp wedge cut into the top -X corner of the
# rect column, where the pressed lever's taper passes through. The
# wedge is a flat-plane chamfer extruded over the lever's Y span;
# the visible cut on the wall is the wedge clipped against two
# curved boundaries:
#
#   1. The shell's outer surface — rect face at Y=0, curving inward
#      to the outer cylinder at higher |Y| (corner clip).
#   2. The body bore — cylinder R=BODY_BORE_R around (0, 0), so the
#      wall's inner edge is at X = -sqrt(R² - Y²) for any given Y.
#
# Anchors (geometry-defined, not free parameters):
#   - Top of cut:    Z = zone2_z_top (top face of rect column).
#   - -X end depth:  lever_ramp_depth below Z_TOP at X = lever_ramp_x_min
#                    (the rect outer face — depth applies along the
#                    flat-rect part at Y near 0).
#   - +X end:        the bore-cylinder tangent at the cut's Y_HALF,
#                    so the wedge terminates exactly where the wall
#                    ends at the lever's Y-edge (any further +X is
#                    inside the bore — no wall to cut).
#
# A small tangent_overshoot pushes the +X end a hair past the exact
# tangent. At exactly the tangent the wedge edge is coincident with
# the bore cylinder, which the CAD kernel can render as a microscopic
# zero-thickness triangular sliver of uncut wall (visible only at
# extreme zoom). The overshoot puts the wedge's +X end just inside
# the bore (empty space), giving a clean termination.
#
# The slope angle is therefore DERIVED, not specified. With
# DEPTH=1.0 and X_MIN=-19, X_START≈-14.508, the slope works out to
# about 12.5° from horizontal — but the angle is incidental; what
# matters is the two anchor points.

lever_y_half = 6.5  # lever physical Y span
lever_clearance_y_half = lever_y_half + bore_clearance  # 6.75

lever_ramp_depth = 1.0  # cut depth at outer rect face
tangent_overshoot = 0.002  # mm past bore tangent

# X_MIN: outer rect face on -X side
lever_ramp_x_min = shell_center_x - shell_outer_r  # = -19.0

# X_START: bore-cylinder tangent at cut's Y_HALF, plus overshoot
_bore_r = body_bore_diameter / 2.0  # = 16.0
_bore_x_at_lever_y = -math.sqrt(_bore_r**2 - lever_clearance_y_half**2)  # ≈ -14.5061
lever_ramp_x_start = _bore_x_at_lever_y - tangent_overshoot  # ≈ -14.5081

# Derived slope (informational; not used as input to geometry)
lever_ramp_angle_deg = math.degrees(
    math.atan(lever_ramp_depth / (lever_ramp_x_start - lever_ramp_x_min))
)

# Shell rectangle. X width matches the cylinder OD so the X faces flow
# straight up from the cylinder. Y half is body-bore-Y plus the wall.
shell_rect_x_half = shell_outer_r  # 22.175
shell_rect_y_half = body_bore_rect_short / 2.0 + wall_thickness_min  # 11.75
shell_rect_x_width = 2.0 * shell_rect_x_half
shell_rect_y_width = 2.0 * shell_rect_y_half


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
arch_x_half = body_rect_long / 2.0  # 15.75 — body arch X extent
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

# ZONE 3 — plateau fill (between the wings, X ≥ fill_x_min)
#
# Fills the plateau region behind the back third of the water tube,
# matching the wings' arch profile so the shell reads as one continuous
# swept arch shape across the back. Tube cutouts:
#   - Water tube: Ø10 cylinder at the port center, full Z. Only the
#     +X portion of the cylinder overlaps the fill, so the result is
#     a curved opening on the fill's -X face.
#   - Flavor tubes: a rounded rectangle covering the bend trajectory.
#     X span = post-bend tube edge to pre-bend tube edge (= pill width
#     extension across the bend X delta); Y span = pill_length_y.
#     Corner radius = pill_width_x/2 so the rounding matches the
#     existing pill's end radius.
water_tube_x = 8.875
# 3/8" LLDPE — sealed in body's 9.75 mm port via a TPU O-ring (0.225 mm
# radial gap).
water_tube_od = 0.375 * 25.4  # 9.525
# NOTE: the 3/8" OD here is the 3-tube dispense spout's center tube
# *inside* the faucet head — NOT the supply line. The harvested
# Westbrass R2031-NL-62 valve body itself IS the 1/4"→3/8" adapter:
# its bottom threaded metal rod accepts 1/4" OD LLDPE supply tubing
# from the foam-shell exit (vessel→here is 1/4" OD throughout); the
# 3/8" OD tube only exists above this port, internal to the head.
water_hole_diameter = water_tube_od + 2.0 * bore_clearance  # 10.025

# 1/4" LLDPE flavor tube — used to derive POST_BEND_X so the flavor
# tube butts up against the water tube at the dispense point.
flavor_tube_od = 0.25 * 25.4  # 6.35 — 1/4" LLDPE
flavor_tube_pre_bend_x = flavor_tube_x  # 18.925
# Butt the flavor tube against the water tube at the dispense point.
# In 3D, each flavor tube sits at Y=±flavor_tube_y_offset (so they
# also touch each other), so X-tangency is Pythagorean:
#   (X_FINAL - water_tube_x)² + Y_OFFSET² = (R_water + R_flavor)²
flavor_tube_post_bend_x = water_tube_x + math.sqrt(
    (water_tube_od / 2.0 + flavor_tube_od / 2.0) ** 2
    - flavor_tube_y_offset ** 2
)  # ≈ 16.150

fill_x_min = 10.46  # back third of water tube


# ZONE 4 — tube wrapper above the arch
#
# A 3 mm-thick shell wrapping just the tube cutouts (water tube + flavor
# pill), starting at the base of the arch (Z=44.25) and extending up to
# zone4_z_top. Built as two pieces unioned:
#   - Water tube wrapper: constant-OD tube cylinder around water_tube_x.
#   - Flavor wrapper: straight pill at flavor_tube_x (flat-X- variant via
#     _flavor_pill_flat_x_minus). The earlier loft-from-rounded-rect-to-pill
#     transitioning toward flavor_tube_post_bend_x was removed when the
#     base/tube-shell split made the bend handled outside the base shell.
zone4_z_bottom = shell_arch_foot_top_z  # 44.25
# Zone 4 top must clear the lever's pressed-down envelope. The lever's
# head corner at original (X=9, Z=52) rotates -18° around pivot
# (1.5, 46) to (6.78, 54.024). That point sits inside zone 5's water-
# circle outer outline (centered at X=8.875, R=9.0125), so zone 5's
# bottom — and therefore zone 4's top — must be above it. The first
# PETG test print showed ~1 mm clearance was too tight in practice;
# bumped to 57.5 mm for ~3.5 mm clearance above 54.024.
zone4_z_top = 57.5
zone4_height = zone4_z_top - zone4_z_bottom  # 10.75
zone4_wall = wall_thickness_min  # 3.0


# ZONE 5 — tube wrapper above the lever
#
# Above zone 4 (which ends at Z=zone4_z_top=57.5 — high enough to clear
# the lever's swing envelope), the shell wraps just the tubes with a
# 3 mm wall. Cross-section is the union of:
#   - water cylinder bore + 3 mm wall
#   - flavor pill bore + 3 mm wall
# straight-extruded vertically. This zone "violates" fill_x_min —
# the wrapper around the water tube (centered at X=8.875) extends
# in -X past fill_x_min, but that's safe because we're now above
# the lever's reach.
zone5_z_bottom = zone4_z_top  # 57.5
zone5_z_top = zone4_z_top + 10.0  # 67.5
zone5_height = zone5_z_top - zone5_z_bottom  # 10
# Uniform wall around the tube wraps now that the shell is one piece
# (no dowel features needing thicker wall).
zone5_wall = wall_thickness_min  # 3.0


# ZONE 6 — gooseneck wrapper around the bent dispense tubes
#
# Pure continuation of zone 5's cross-section along the same bent
# path the dispense tubes follow above the lever-swing envelope.
# Same wall thickness, same water/flavor/fill layout, rotated through
# the gooseneck bends.
#
# Path (in tube-local XZ plane, origin at the zone 5 / zone 6 seam):
#   1. vertical lift from Z=0 up to Z=gn_bend1_start_z − zone5_z_top
#   2. bend 1 — gn_bend1_sweep_rad at R = gn_bend1_r, bending toward -X
#   3. gn_mid_straight_len angled straight
#   4. bend 2 — gn_bend2_sweep_rad at R = gn_bend2_r
#   5. gn_tip_straight_len tip
#
# Sweep frame: cross-section centered on the water tube. The flavor
# pill's +X offset (flavor_tube_post_bend_x − water_tube_x ≈ 6.148 mm)
# is carried in the LOCAL frame, so as the tangent rotates through
# each bend the pill traces a parallel-offset arc at the larger
# radius (water R + 6.148) — matching the actual flavor tubes'
# centerlines.
#
# These mirror constants in the assembly (`faucet-assembly`); if the
# assembly's gooseneck moves, update both.

gn_bend1_r = 30.0  # water tube — bend 1
gn_bend2_r = 40.0  # water tube — bend 2
gn_bend1_sweep_rad = math.radians(30.0)
gn_bend2_sweep_rad = math.radians(110.0)
lever_top_z = zone2_z_top + 13.0  # 52
gn_bend1_mid_z = lever_top_z + 35.0  # 87
gn_bend1_start_z = (
    gn_bend1_mid_z
    - gn_bend1_r * math.sin(gn_bend1_sweep_rad / 2.0)
)  # ≈ 79.24
gn_mid_straight_len = 115.0
gn_tip_straight_len = 25.0
zone6_wall = zone5_wall  # 3.0


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
_new_arch_low_x = shell_center_x - shell_rect_x_half  # rect_x_min = -19
_new_arch_low_z = zone3_z_bottom  # 39
_new_arch_high_x = fill_x_min  # 10.46
_new_arch_high_z = zone4_z_top  # 55
_new_arch_dx = _new_arch_high_x - _new_arch_low_x  # 29.46
_new_arch_c_z = (
    (_new_arch_high_z + _new_arch_low_z) / 2.0
    - _new_arch_dx**2 / (2.0 * (_new_arch_high_z - _new_arch_low_z))
)  # ≈ 19.88
_new_arch_r = _new_arch_high_z - _new_arch_c_z  # ≈ 35.12
# Midpoint of the arc — angular midway between high end (90° from
# center, directly above) and low end.
_new_arch_a_low = math.atan2(_new_arch_low_z - _new_arch_c_z,
                              _new_arch_low_x - _new_arch_high_x)
_new_arch_a_mid = (math.pi / 2.0 + _new_arch_a_low) / 2.0
new_arch_mid_x = _new_arch_high_x + _new_arch_r * math.cos(_new_arch_a_mid)  # ≈ -6.28
new_arch_mid_z = _new_arch_c_z + _new_arch_r * math.sin(_new_arch_a_mid)  # ≈ 50.75


# ZONE 4.5 — block above the lever, up to the gooseneck bend start
#
# A tall block capping the lever swing volume from above and reaching
# up to the gooseneck bend start (Z=gn_bend1_start_z ≈ 78.78). The -X
# edge sits at zone45_front_x — chosen so the front margin (zone 4.5
# front X to zone 5's water-circle -X edge) matches the back margin
# (zone 4.5 back X to zone 5's flavor-pill +X edge), giving zone 5
# visually centered when looking down the X axis. This pulls the
# front past the lever's "ridge" line lever_ridge_x (the X where the
# pressed lever's tilted top crosses the rest lever's flat top at
# Z=lever_rest_top_z), but the lid's bottom on the arch curve still
# clears the lever's swing envelope by ~0.9 mm there.
#
# Bottom face = arch curve from (zone45_front_x, arch_z) up to
# (fill_x_min, zone4_z_top), then flat at zone4_z_top out to the +X
# cylinder back. Top face = flat at zone45_z_top. Both -X and +X
# edges curve inward at large |Y| via mirrored cylinder clips of
# radius shell_outer_r.
#
# Lever swing geometry mirrors the assembly's build_lever — pivot
# parallel to Y at (lever_pivot_x, *, lever_pivot_z), pressed-down
# rotates by lever_pressed_angle about that axis.

lever_pivot_x = 1.5
lever_pivot_z = zone2_z_top + 7.0  # 46 — = PLATEAU_Z+1+6
lever_pressed_angle = math.radians(18.0)
lever_rest_top_z = zone2_z_top + 13.0  # 52 — = PLATEAU_Z+1+12
_lever_dz_pivot = lever_rest_top_z - lever_pivot_z  # 6

# Closed form for where pressed top crosses Z=lever_rest_top_z:
# Z'(X0) = Z_pivot + (X0-X_pivot)·sin θ + dz_pivot·cos θ = Z_rest
#   ⇒  (X0-X_pivot) = dz_pivot·(1-cos θ)/sin θ
# X'(X0) = X_pivot + (X0-X_pivot)·cos θ - dz_pivot·sin θ
#   ⇒  X' = X_pivot - dz_pivot·(1-cos θ)/sin θ = X_pivot - dz_pivot·tan(θ/2)
# Informational — the visible "ridge" of the lever swing envelope.
# Not directly used in the build (zone45_front_x overrides it).
lever_ridge_x = (
    lever_pivot_x
    - _lever_dz_pivot * math.tan(lever_pressed_angle / 2.0)
)  # ≈ 0.55

# Zone 5's X extents at Y=0, used to derive zone 4.5's matched-margin
# front X. Mirrors the cross-section in build_zone5_outer.
_z5_water_r_outer = water_hole_diameter / 2.0 + zone5_wall  # 9.0125
_z5_flavor_x_half = (pill_width_x + 2.0 * zone5_wall) / 2.0  # 7.425
_z5_x_min = water_tube_x - _z5_water_r_outer  # -0.1375
_z5_x_max = flavor_tube_post_bend_x + _z5_flavor_x_half  # 23.575

zone45_back_x = shell_center_x + shell_outer_r  # 25.35
_zone45_x_margin = zone45_back_x - _z5_x_max  # 1.775
zone45_front_x = _z5_x_min - _zone45_x_margin  # ≈ -1.9125

# 3 mm tall on the back side (where the lid sits flat on zone 4 top);
# taller on the front side because the lid bottom follows the back-arch
# curve down to ≈ Z=52.75.
zone45_z_top = zone4_z_top + 3.0  # 60.5
zone45_bot_z_at_front = (
    _new_arch_c_z
    + math.sqrt(_new_arch_r ** 2 - (zone45_front_x - fill_x_min) ** 2)
)  # ≈ 52.75

# Mid-point of the bottom arch sub-arc, between zone45_front_x end
# and fill_x_min end.
_a_front = math.atan2(
    zone45_bot_z_at_front - _new_arch_c_z,
    zone45_front_x - fill_x_min,
)
_a_high = math.pi / 2.0  # fill_x_min end is directly above arch center
_a_mid45 = (_a_front + _a_high) / 2.0
zone45_bot_mid_x = fill_x_min + _new_arch_r * math.cos(_a_mid45)
zone45_bot_mid_z = _new_arch_c_z + _new_arch_r * math.sin(_a_mid45)


# HEAT-SET INSERT POCKETS — mounting-plate retention

# Two M3 brass heat-set inserts press into the bottom face of the
# shell. Mounting plate sits below the shell with M3 × 8 mm 316 SS
# ultra-low-profile socket cap screws (McMaster 91223A413) coming up
# from below the plate, through plate clearance holes + counterbores,
# and threading into these inserts.
#
# Insert: ruthex M3 short (Amazon B09ZHSGHXD) — Ø 4.6 knurl OD /
#   Ø 3.9 body / 4 mm length. Recommended install hole Ø 4.0; knurls
#   bite into the plastic on heat-press.
#
# Pocket location: θ = ±45° about the body center, r = 20 mm — in
# the shell's "rear shoulder" wall material (between the body bore
# and the shell outer cylinder, well clear of the pill slot). At this
# point all four wall margins hold ≥ 2 mm:
#   - to body bore (Ø 31.5 cyl @ origin):       2.25 mm
#   - to shell outer (Ø 44.35 cyl @ +X 3.175):  2.28 mm
#   - to pill slot (X-edge at corner Y):        5.66 mm
#   - between the two pockets (Y separation):   24.28 mm
#
# Pocket Z range: 0 → insert_pocket_depth (5 mm = 4 mm insert + 1 mm
# relief at the top to receive plastic displaced during heat-press).
# Lives entirely in zone 1 outer (which extends to Z = 16.25), with
# ~11 mm of solid material above the pocket ceiling.

insert_pocket_diameter = 4.0  # mm — recommended hole for ruthex M3 short
insert_pocket_depth = 5.0  # mm — 4 insert + 1 relief
insert_r_from_body = 20.0  # mm — radial distance of insert center from body center (0,0)
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

    - Clip volume in zones 2 and 3 (bore region), where the shell bore
      must follow the body's rect ∩ cyl outline rather than a plain
      rect.

    - Cut volume in zones 3-fill outer and zone 4 outer, ABOVE the
      body's plateau (Z > zone2_z_top = 39). The body has ended there,
      so this column is empty space. Two reasons to keep the shell out
      of it:

        1. The flavor tubes' S-bend passes through this region (going
           from the body's flavor channel at X=17.3375 down to the
           post-bend X=15.023). They don't need a shell wrap here —
           the body's flavor channel locates them below, and zone 4.5
           (the lid) holds them from above.

        2. Printed support material inside the dispense-tube channel
           needs a path out. Leaving the body-bore column open all
           the way up to zone4_z_top gives the central cavity an
           opening at the back, so support can be extracted after
           printing.

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
    """Flavor pill cutout at flavor_tube_x with the X- side flattened.

    Same as the original slot2D pill (pill_length_y × pill_width_x, Y-oriented),
    but the X- side has square corners at (flavor_pill_x_minus_edge,
    ±pill_length_y/2) instead of the rounded transitions to the Y+/Y-
    semicircular caps. Removes thin shell features on the X- side of the
    cutout that print poorly. The Y+/Y- caps and the X+ side stay rounded.

    The flat -X edge sits at flavor_pill_x_minus_edge, which is pulled
    past the natural slot2D edge when needed so the corners reach the
    body bore in zone 1. See the constant's definition for the rule.

    Construction: union of the original slot2D and a rectangle that
    covers everything from flavor_pill_x_minus_edge up to flavor_tube_x
    on the X- side, so the flat edge ends up at flavor_pill_x_minus_edge
    regardless of whether the slot2D edge is closer or farther.
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
    body_bore_height = zone2_bore_bottom - zone1_z_bottom
    body_bore = (
        cq.Workplane("XY")
        .workplane(offset=zone1_z_bottom)
        .moveTo(body_bore_x, body_bore_y)
        .circle(body_bore_diameter / 2.0)
        .extrude(body_bore_height)
    )
    pill = _flavor_pill_flat_x_minus(zone1_z_bottom, zone1_height)
    return body_bore.union(pill)


def build_insert_pockets() -> cq.Workplane:
    """Two heat-set insert pockets in the shell's bottom face.

    Each pocket is a Ø insert_pocket_diameter cylinder extruded UP
    from Z=0 by insert_pocket_depth, positioned at world
    (insert_x, ±insert_y_offset) — the rear-shoulder zones at θ=±45°,
    r=20 from the body center. Lives entirely within zone 1 outer
    (which extends to Z = zone1_outer_top = 16.25), with ~11 mm of
    solid material above the pocket ceiling.

    Returned as a single union for the caller to subtract from the
    shell solid.
    """
    pockets = None
    for y_sign in (+1, -1):
        sx = insert_x
        sy = y_sign * insert_y_offset
        pocket = (
            cq.Workplane("XY")
            .workplane(offset=zone1_z_bottom)
            .moveTo(sx, sy)
            .circle(insert_pocket_diameter / 2.0)
            .extrude(insert_pocket_depth)
        )
        pockets = pocket if pockets is None else pockets.union(pocket)
    return pockets


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
    top at zone4_z_top from +X back to fill_x_min, then the new_arch arc
    down-left to rect_x_min — extruded across [y_bottom, y_bottom + y_height].

    Shared by the zone-3 wings (extruded across each wing's Y thickness)
    and the zone-3 plateau fill (extruded across the central Y range).
    """
    rect_x_min = shell_center_x - shell_rect_x_half
    rect_x_max = shell_center_x + shell_rect_x_half
    return (
        cq.Workplane("XZ")
        .workplane(offset=y_bottom)
        .moveTo(rect_x_min, zone3_z_bottom)
        .lineTo(rect_x_max, zone3_z_bottom)
        .lineTo(rect_x_max, zone4_z_top)
        .lineTo(fill_x_min, zone4_z_top)
        .threePointArc((new_arch_mid_x, new_arch_mid_z),
                       (rect_x_min, zone3_z_bottom))
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
    rect_x_max = shell_center_x + shell_rect_x_half
    fill_y_thickness = 2.0 * wing_inner_y  # 13.5
    z_height = zone4_z_top - zone3_z_bottom

    arch_solid = _arch_extrude(-wing_inner_y, fill_y_thickness)
    keep_x_box = (
        cq.Workplane("XY")
        .workplane(offset=zone3_z_bottom)
        .moveTo((fill_x_min + rect_x_max) / 2.0, 0)
        .rect(rect_x_max - fill_x_min, fill_y_thickness)
        .extrude(z_height)
    )
    return (
        arch_solid
        .intersect(keep_x_box)
        .intersect(shell_outer_cyl(zone3_z_bottom, z_height))
        .cut(body_bore_cyl(zone3_z_bottom, z_height))
    )


def build_zone3_fill_inner_cut() -> cq.Workplane:
    """Tube cutouts through the plateau fill: water tube + straight flavor pill.

    Flavor cut is a straight pill at flavor_tube_x (matching zones 1+2). The
    bend that previously lived here is no longer needed — with the new
    base/tube-shell split, the LLDPE flavor tubes are routed through the
    tube shell first (post-bend at flavor_tube_post_bend_x) and then dropped
    into the base; they flex through the socket area on the way down.
    """
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
    keep_x = (
        cq.Workplane("XY")
        .workplane(offset=zone4_z_bottom - 1)
        .moveTo(fill_x_min + 50, 0)
        .rect(100, 200)
        .extrude(z_height + 2)
    )
    return (
        rect
        .intersect(shell_outer_cyl(zone4_z_bottom, z_height))
        .intersect(keep_x)
        .cut(body_bore_cyl(zone4_z_bottom, zone4_height))
    )


def build_zone4_inner_cut() -> cq.Workplane:
    """Tube cavity: water-tube cyl + straight flavor pill at flavor_tube_x.

    Previously this was a 3D loft from a wider rounded-rect at the bottom
    to a pill at flavor_tube_post_bend_x at the top, transitioning the
    flavor tube position. With the new base/tube-shell split, the bend
    is handled in the tube shell + the socket area above, so the base
    just needs straight pill clearance at flavor_tube_x.
    """
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
      → flat to (rect_x_max, zone4_z_top)
      → vertical up to (rect_x_max, zone45_z_top)
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
    rect_x_max = shell_center_x + shell_rect_x_half  # 25.35
    y_half = shell_rect_y_half  # 11.75

    profile_solid = (
        cq.Workplane("XZ")
        .workplane(offset=-y_half)
        .moveTo(zone45_front_x, zone45_bot_z_at_front)
        .threePointArc(
            (zone45_bot_mid_x, zone45_bot_mid_z),
            (fill_x_min, zone4_z_top),
        )
        .lineTo(rect_x_max, zone4_z_top)
        .lineTo(rect_x_max, zone45_z_top)
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


def _zone6_outer_sketch() -> cq.Sketch:
    """Zone 5's outer cross-section centered on the water tube.

    Single connected region: water slot + flavor pill (offset +X) +
    fill rectangle between them. The mode='a' flag unions each shape
    into the running sketch so the sweep sees one face.

    Both the water side and the flavor side are Y-oriented slots
    (rather than circle + pill). They share the same outer Y total
    `2 * max(natural water_r_outer, natural pill_y_half)`, so the
    cross-section's Y+ and Y- outer apexes meet at the same Y across
    the X range. Each side's X width stays at natural — that is, the
    walls on the extreme X- (around the water bore) and extreme X+
    (around the flavor pill) are both zone5_wall. The "stretch" is
    only in Y (where the smaller side picks up extra wall thickness
    on its Y apex) — the X side walls don't thicken.

    When water dominates the natural Y (small flavor tubes), the
    water "slot" degenerates to a circle (slot_straight = 0) and the
    flavor pill stretches in Y. When flavor dominates (current 1/4
    tubes), the flavor "pill" stays a pill and the water slot picks
    up a straight section in the middle.

    NOTE: cq.Sketch.slot(w, h) takes w as the *straight section* length
    (between the rounded ends), not the overall length — opposite of
    Workplane.slot2D's convention. Total length along the long axis is
    w + h, so w_straight = total - h.
    """
    flavor_offset_x = flavor_tube_post_bend_x - water_tube_x
    natural_water_r = water_hole_diameter / 2.0 + zone6_wall
    natural_pill_y_half = pill_length_y / 2.0 + zone6_wall
    y_half = max(natural_water_r, natural_pill_y_half)
    y_total = 2.0 * y_half

    water_x_width = 2.0 * natural_water_r
    water_slot_straight = y_total - water_x_width

    pill_short_total = pill_width_x + 2.0 * zone6_wall
    pill_straight = y_total - pill_short_total
    return (
        cq.Sketch()
        .slot(water_slot_straight, water_x_width, angle=90)
        .push([(flavor_offset_x, 0)])
        .slot(pill_straight, pill_short_total, angle=90, mode="a")
        .reset()
        .push([(flavor_offset_x / 2.0, 0)])
        .rect(flavor_offset_x, y_total, mode="a")
        .clean()
    )


def _zone6_inner_sketch() -> cq.Sketch:
    """Zone 5's inner-cut cross-section centered on the water tube.

    See _zone6_outer_sketch's note about cq.Sketch.slot conventions.
    """
    flavor_offset_x = flavor_tube_post_bend_x - water_tube_x
    pill_straight = pill_length_y - pill_width_x  # 3.175
    return (
        cq.Sketch()
        .circle(water_hole_diameter / 2.0)
        .push([(flavor_offset_x, 0)])
        .slot(pill_straight, pill_width_x, angle=90, mode="a")
        .clean()
    )


def build_zone6_outer() -> cq.Workplane:
    """Sweep the outer cross-section along the gooseneck path, then
    place at (water_tube_x, 0, zone5_z_top). Sits on top of the tube
    shell vertical extrusion below.
    """
    profile = cq.Workplane("XY").placeSketch(_zone6_outer_sketch())
    swept = profile.sweep(_gooseneck_path_at_origin(), transition="right")
    return swept.translate((water_tube_x, 0, zone5_z_top))


def build_zone6_inner_cut() -> cq.Workplane:
    """Inner cut for zone 6 — same path, inner cross-section."""
    profile = cq.Workplane("XY").placeSketch(_zone6_inner_sketch())
    swept = profile.sweep(_gooseneck_path_at_origin(), transition="right")
    return swept.translate((water_tube_x, 0, zone5_z_top))


def build_lever_clearance() -> cq.Workplane:
    """Single triangular ramp wedge cut into the top of the rect column.

    In the XZ plane, the cut is a right triangle:
      - top edge flat at Z=zone2_z_top (39), from X=lever_ramp_x_min
        to X=lever_ramp_x_start
      - vertical edge at X=lever_ramp_x_min, dropping lever_ramp_depth
        below Z=39
      - sloped (ramp) edge at lever_ramp_angle_deg, from the bottom of
        the vertical edge back up to the +X start point at Z=39

    Extruded ±lever_clearance_y_half in Y. Single piece.
    """
    z_top = zone2_z_top
    z_bot = z_top - lever_ramp_depth
    y_half = lever_clearance_y_half

    return (
        cq.Workplane("XZ")
        .workplane(offset=-y_half)
        .polyline([
            (lever_ramp_x_min,   z_bot),
            (lever_ramp_x_min,   z_top),
            (lever_ramp_x_start, z_top),
        ]).close()
        .extrude(2.0 * y_half)
    )


# TUBE SHELL VERTICAL — wraps inside the lid
#
# Tube wraps that span the lid's Z range (zone5_z_bottom = zone4_z_top up
# to zone5_z_top). The wraps' outer cross-section is dominated by the
# lid block in the union, so it's not visible from outside — the wraps
# only carry the bore through the lid (water cyl + flavor pill at upper
# X). Above zone5_z_top the gooseneck (zone 6) emerges with the tube
# wraps becoming visible as the spout.
#
# No socket / no tongue / no split / no dowels — the shell is one piece.
# Earlier revisions split this into a base and two tube halves with a
# press-fit tongue+socket and dowel pins; that infrastructure has been
# removed in favor of single-piece printing.


def _tube_shell_outer_section(z_bottom: float, z_height: float) -> cq.Workplane:
    """Tube wrap outer (water Y-slot + flavor pill + fill rect, all
    zone5_wall on the X sides) extruded vertically over the given Z
    range.

    Water and flavor sides share the same outer Y half-width — the
    larger of (water bore + wall) and (flavor pill + wall) — so the
    cross-section's Y+ and Y- outer apexes meet at the same Y across
    the X range. The water side is a Y-oriented slot rather than a
    circle, so the wall on the extreme -X face stays at zone5_wall
    (= 3 mm) — only the Y apex thickens. See _zone6_outer_sketch's
    docstring for details.
    """
    natural_water_r = water_hole_diameter / 2.0 + zone5_wall
    natural_pill_y_half = pill_length_y / 2.0 + zone5_wall
    y_half = max(natural_water_r, natural_pill_y_half)
    y_total = 2.0 * y_half
    water_x_width = 2.0 * natural_water_r
    water_outer = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(water_tube_x, 0)
        .slot2D(y_total, water_x_width, angle=90)
        .extrude(z_height)
    )
    flavor_outer = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(flavor_tube_post_bend_x, 0)
        .slot2D(y_total,
                pill_width_x + 2.0 * zone5_wall, angle=90)
        .extrude(z_height)
    )
    fill_rect = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo((water_tube_x + flavor_tube_post_bend_x) / 2.0, 0)
        .rect(flavor_tube_post_bend_x - water_tube_x, y_total)
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
    """Touch-Flo shell — single piece for printing.

    All zones unioned into one solid:
      - Zones 1–4: body wraps + lever clearance
      - Zone 4.5: lid above the lever
      - Zone 5: tube wraps inside the lid (provides the bore through the
                lid; outer is dominated by the lid in the union)
      - Zone 6: gooseneck (the visible spout above the lid)

    Earlier revisions split this into a base shell + two tube halves
    with a press-fit tongue+socket and dowel pins; that's gone now in
    favor of single-piece printing. Gooseneck overhangs will need
    slicer-generated supports.
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


def main():
    out = Path(__file__).resolve().parent / "touch-flo-shell.step"
    export_step(build_shell(), str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
