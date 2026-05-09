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


# ═══════════════════════════════════════════════════════
# SHELL CENTER (lateral)
# ═══════════════════════════════════════════════════════

SHELL_CENTER_X = 3.175     # shifted +X so the +X edge of the shell
                            # extends past the wider 1/4" flavor cutout
                            # with a real wall. Was 1.5875 (matching the
                            # mounting plate). Now mounting plate sits
                            # asymmetrically under the shell until the
                            # plate is re-centered in a follow-up.
SHELL_CENTER_Y = 0.0


# ═══════════════════════════════════════════════════════
# ZONE 1 — first 13 mm; body is a full Ø 31.5 mm cylinder here
# ═══════════════════════════════════════════════════════

ZONE1_Z_BOTTOM = 0.0
ZONE1_Z_TOP    = 13.0
ZONE1_HEIGHT   = ZONE1_Z_TOP - ZONE1_Z_BOTTOM      # 13 mm

# Body-to-bore slip-fit clearance — applied per-side (per-direction)
# uniformly: X faces, Y faces, radial cylinder, AND face-to-face Z
# interfaces all get the same gap. So bore radii / half-widths add
# this once per side, and the bore's Z transitions lift by this much
# above the body's Z transitions.
BORE_CLEARANCE = 0.25   # mm per side

# Body bore (cylinder) — body OD 31.5 mm + 2 × clearance per side
BODY_BORE_DIAMETER = 31.5 + 2.0 * BORE_CLEARANCE   # 32.0
BODY_BORE_X        = 0.0
BODY_BORE_Y        = 0.0

# Flavor-tube pill — sized for 1/4" OD LLDPE flavor tubes (6.35 mm OD),
# tangent to the body's +X face (X=15.75) and tangent to each other at Y=0.
# (Mounting plate not yet updated to match — coming in a later pass.)
FLAVOR_TUBE_X        = 18.925   # = BODY_R + tube_R = 15.75 + 3.175
FLAVOR_TUBE_HOLE_DIA = 6.85     # = 6.35 OD + 0.5 mm clearance
FLAVOR_TUBE_Y_OFFSET = 3.175    # = tube_R, tubes touch at Y=0
PILL_LENGTH_Y = 2 * FLAVOR_TUBE_Y_OFFSET + FLAVOR_TUBE_HOLE_DIA   # 13.2
PILL_WIDTH_X  = FLAVOR_TUBE_HOLE_DIA                                # 6.85

# Flat -X edge of the flavor pill cutout in zones 1-4 (the base shell).
# Pulled in (more -X) past the natural pill -X edge so the cutout's
# corners (at Y=±PILL_LENGTH_Y/2) land on the body bore's cyl curve
# in zone 1. With 1/4" flavor tubes the natural pill -X (= 15.5) is
# OUTSIDE the cyl bore at the corner Y=±6.6 (bore +X there is 14.57)
# — leaving a thin sliver of shell material between cutout and bore.
# Computing -X as `min(natural pill edge, bore +X at corner Y)` makes
# the flat side reach the bore wherever the natural pill would not.
# With smaller (1/8") tubes the natural pill is inside the bore at
# its corners, so this min picks the natural value and nothing changes.
FLAVOR_PILL_X_MINUS_EDGE = min(
    FLAVOR_TUBE_X - PILL_WIDTH_X / 2.0,
    math.sqrt((BODY_BORE_DIAMETER / 2.0) ** 2 - (PILL_LENGTH_Y / 2.0) ** 2),
)                                                                    # ≈ 14.575


# ═══════════════════════════════════════════════════════
# SHELL OUTER (derived from wall-thickness target)
# ═══════════════════════════════════════════════════════
#
# Wall thickness is set at the body bore's farthest edge from the
# shell center. The body bore is offset by SHELL_CENTER_X mm from
# shell center, so its farthest perimeter point (in -X) sits at
# distance SHELL_CENTER_X + body_bore_radius from the shell center.
#
# With SHELL_CENTER_X chosen to balance walls on both sides (body
# bore -X edge vs. flavor pill +X edge), the two extremes are
# equidistant from the shell center: 19.175 mm. WALL_THICKNESS_MIN
# applies cleanly to both.
WALL_THICKNESS_MIN = 3.0   # mm — target at body bore's -X edge AND
                            # at the flavor pill's +X edge (both at
                            # 19.175 mm from shell center, by construction)

_BODY_BORE_FARTHEST_FROM_SHELL_CENTER = (
    (SHELL_CENTER_X - BODY_BORE_X) + BODY_BORE_DIAMETER / 2.0
)   # = 19.175 mm

SHELL_OUTER_R        = _BODY_BORE_FARTHEST_FROM_SHELL_CENTER + WALL_THICKNESS_MIN
SHELL_OUTER_DIAMETER = 2.0 * SHELL_OUTER_R   # = 44.35 mm


# ═══════════════════════════════════════════════════════
# ZONE 2 — cylinder → rectangle transition + rect column
# ═══════════════════════════════════════════════════════

ZONE2_Z_BOTTOM = ZONE1_Z_TOP                       # 13.0
ZONE2_Z_TOP    = 39.0                              # body plateau
ZONE2_HEIGHT   = ZONE2_Z_TOP - ZONE2_Z_BOTTOM      # 26.0

# Body rectangle dimensions (mirrored from valve-body-reference)
BODY_RECT_LONG  = 31.5     # X
BODY_RECT_SHORT = 17.0     # Y

# Body bore in zone 2 — match body rect with clearance per side
BODY_BORE_RECT_LONG  = BODY_RECT_LONG  + 2.0 * BORE_CLEARANCE   # 32.0
BODY_BORE_RECT_SHORT = BODY_RECT_SHORT + 2.0 * BORE_CLEARANCE   # 17.5

# Cove transition fillet (matches the body's transition_fillet_r)
COVE_R = 6.0

# Bore Z transitions lift by BORE_CLEARANCE above the body's Z
# transitions so face-to-face Z interfaces get the same per-side
# clearance as X/Y. The body's cylinder top face sits at Z=ZONE1_Z_TOP
# (=13); the shell's bore step (where the bore narrows from cyl to
# rect+filler+cove) sits BORE_CLEARANCE higher.
ZONE2_BORE_BOTTOM = ZONE1_Z_TOP + BORE_CLEARANCE                 # 13.25
COVE_TOP_Z        = ZONE2_BORE_BOTTOM + COVE_R                   # 18.25 (bore cove top)

# Outer surface lifts by WALL + BORE_CLEARANCE above the body's cyl
# top, so that 3 mm of solid shell wall sits above the bore step
# (i.e., 3.25 mm above the body's cyl top face, with the extra
# 0.25 mm being the bore's Z clearance). Without the lift, the outer
# cove tangents the body's cyl ledge at Z=13 from above and there
# would be no vertical wall material over the body's top face.
SHELL_OUTER_LIP   = WALL_THICKNESS_MIN + BORE_CLEARANCE          # 3.25
ZONE1_OUTER_TOP   = ZONE1_Z_TOP + SHELL_OUTER_LIP                # 16.25
ZONE2_OUTER_BOT   = ZONE1_OUTER_TOP                              # 16.25
COVE_TOP_OUTER_Z  = ZONE2_OUTER_BOT + COVE_R                     # 21.25 (outer cove top)


# ═══════════════════════════════════════════════════════
# LEVER SWING CLEARANCE
# ═══════════════════════════════════════════════════════
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
#   - Top of cut:    Z = ZONE2_Z_TOP (top face of rect column).
#   - -X end depth:  LEVER_RAMP_DEPTH below Z_TOP at X = LEVER_RAMP_X_MIN
#                    (the rect outer face — depth applies along the
#                    flat-rect part at Y near 0).
#   - +X end:        the bore-cylinder tangent at the cut's Y_HALF,
#                    so the wedge terminates exactly where the wall
#                    ends at the lever's Y-edge (any further +X is
#                    inside the bore — no wall to cut).
#
# A small TANGENT_OVERSHOOT pushes the +X end a hair past the exact
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

LEVER_Y_HALF           = 6.5                                        # lever physical Y span
LEVER_CLEARANCE_Y_HALF = LEVER_Y_HALF + BORE_CLEARANCE              # 6.75

LEVER_RAMP_DEPTH      = 1.0                                         # cut depth at outer rect face
TANGENT_OVERSHOOT     = 0.002                                       # mm past bore tangent

# X_MIN: outer rect face on -X side
LEVER_RAMP_X_MIN      = SHELL_CENTER_X - SHELL_OUTER_R              # = -19.0

# X_START: bore-cylinder tangent at cut's Y_HALF, plus overshoot
_BORE_R = BODY_BORE_DIAMETER / 2.0                                  # = 16.0
_BORE_X_AT_LEVER_Y = -math.sqrt(_BORE_R**2 - LEVER_CLEARANCE_Y_HALF**2)  # ≈ -14.5061
LEVER_RAMP_X_START    = _BORE_X_AT_LEVER_Y - TANGENT_OVERSHOOT      # ≈ -14.5081

# Derived slope (informational; not used as input to geometry)
LEVER_RAMP_ANGLE_DEG  = math.degrees(
    math.atan(LEVER_RAMP_DEPTH / (LEVER_RAMP_X_START - LEVER_RAMP_X_MIN))
)

# Shell rectangle. X width matches the cylinder OD so the X faces flow
# straight up from the cylinder. Y half is body-bore-Y plus the wall.
SHELL_RECT_X_HALF  = SHELL_OUTER_R                                        # 22.175
SHELL_RECT_Y_HALF  = BODY_BORE_RECT_SHORT / 2.0 + WALL_THICKNESS_MIN      # 11.75
SHELL_RECT_X_WIDTH = 2.0 * SHELL_RECT_X_HALF
SHELL_RECT_Y_WIDTH = 2.0 * SHELL_RECT_Y_HALF


# ═══════════════════════════════════════════════════════
# ZONE 3 — Arch wraps (two wings at ±Y)
# ═══════════════════════════════════════════════════════
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

ZONE3_Z_BOTTOM = ZONE2_Z_TOP                                       # 39

ARCH_BASE_Z       = 41.0                                           # body foot top
ARCH_PEAK_Z       = 46.0                                           # body arc peak
ARCH_X_HALF       = BODY_RECT_LONG / 2.0                           # 15.75 — body arch X extent
BODY_ARCH_INNER_Y = 7.0                                            # body arch face nearest plateau
BODY_ARCH_OUTER_Y = 8.5                                            # body arch face nearest shell exterior

# Bore (inner cut): body arch + BORE_CLEARANCE per side
SHELL_ARCH_BORE_INNER_Y    = BODY_ARCH_INNER_Y - BORE_CLEARANCE    # 6.75
SHELL_ARCH_BORE_OUTER_Y    = BODY_ARCH_OUTER_Y + BORE_CLEARANCE    # 8.75
SHELL_ARCH_BORE_FOOT_TOP_Z = ARCH_BASE_Z + BORE_CLEARANCE          # 41.25
SHELL_ARCH_BORE_PEAK_Z     = ARCH_PEAK_Z + BORE_CLEARANCE          # 46.25

# Outer wing: WALL+GAP above the body arch in Z; outer-Y matches the
# rect col Y_HALF so the wing sits flush atop zone 2; inner-Y matches
# the bore (plateau open, no extra shell material on plateau side).
SHELL_ARCH_FOOT_TOP_Z = ARCH_BASE_Z + SHELL_OUTER_LIP              # 44.25
SHELL_ARCH_PEAK_Z     = ARCH_PEAK_Z + SHELL_OUTER_LIP              # 49.25
WING_INNER_Y          = SHELL_ARCH_BORE_INNER_Y                    # 6.75
WING_OUTER_Y          = SHELL_RECT_Y_HALF                          # 11.75

# ZONE 3 — plateau fill (between the wings, X ≥ FILL_X_MIN)
#
# Fills the plateau region behind the back third of the water tube,
# matching the wings' arch profile so the shell reads as one continuous
# swept arch shape across the back. Tube cutouts:
#   - Water tube: Ø10 cylinder at the port center, full Z. Only the
#     +X portion of the cylinder overlaps the fill, so the result is
#     a curved opening on the fill's -X face.
#   - Flavor tubes: a rounded rectangle covering the bend trajectory.
#     X span = post-bend tube edge to pre-bend tube edge (= pill width
#     extension across the bend X delta); Y span = PILL_LENGTH_Y.
#     Corner radius = PILL_WIDTH_X/2 so the rounding matches the
#     existing pill's end radius.
WATER_TUBE_X        = 8.875
WATER_TUBE_OD       = 0.375 * 25.4                                  # 9.525 — 3/8" LLDPE
                                                                     # (sealed in body's
                                                                     # 9.75 mm port via
                                                                     # a TPU O-ring —
                                                                     # 0.225 mm radial gap)
WATER_HOLE_DIAMETER = WATER_TUBE_OD + 2.0 * BORE_CLEARANCE          # 10.025

# 1/4" LLDPE flavor tube — used to derive POST_BEND_X so the flavor
# tube butts up against the water tube at the dispense point.
FLAVOR_TUBE_OD          = 0.25 * 25.4                               # 6.35 — 1/4" LLDPE
FLAVOR_TUBE_PRE_BEND_X  = FLAVOR_TUBE_X                             # 18.925
# Butt the flavor tube against the water tube at the dispense point.
# In 3D, each flavor tube sits at Y=±FLAVOR_TUBE_Y_OFFSET (so they
# also touch each other), so X-tangency is Pythagorean:
#   (X_FINAL - WATER_TUBE_X)² + Y_OFFSET² = (R_water + R_flavor)²
FLAVOR_TUBE_POST_BEND_X = WATER_TUBE_X + math.sqrt(
    (WATER_TUBE_OD / 2.0 + FLAVOR_TUBE_OD / 2.0) ** 2
    - FLAVOR_TUBE_Y_OFFSET ** 2
)                                                                    # ≈ 16.150

FILL_X_MIN = 10.46                                                  # back third of water tube


# ZONE 4 — tube wrapper above the arch
#
# A 3 mm-thick shell wrapping just the tube cutouts (water tube + flavor
# pill), starting at the base of the arch (Z=44.25) and extending up to
# ZONE4_Z_TOP. Built as two pieces unioned:
#   - Water tube wrapper: constant-OD tube cylinder around WATER_TUBE_X.
#   - Flavor wrapper: straight pill at FLAVOR_TUBE_X (flat-X- variant via
#     _flavor_pill_flat_x_minus). The earlier loft-from-rounded-rect-to-pill
#     transitioning toward FLAVOR_TUBE_POST_BEND_X was removed when the
#     base/tube-shell split made the bend handled outside the base shell.
ZONE4_Z_BOTTOM = SHELL_ARCH_FOOT_TOP_Z                              # 44.25
# Zone 4 top must clear the lever's pressed-down envelope. The lever's
# head corner at original (X=9, Z=52) rotates -18° around pivot
# (1.5, 46) to (6.78, 54.024). That point sits inside zone 5's water-
# circle outer outline (centered at X=8.875, R=9.0125), so zone 5's
# bottom — and therefore zone 4's top — must be above it. The first
# PETG test print showed ~1 mm clearance was too tight in practice;
# bumped to 57.5 mm for ~3.5 mm clearance above 54.024.
ZONE4_Z_TOP    = 57.5
ZONE4_HEIGHT   = ZONE4_Z_TOP - ZONE4_Z_BOTTOM                       # 10.75
ZONE4_WALL     = WALL_THICKNESS_MIN                                 # 3.0


# ═══════════════════════════════════════════════════════
# ZONE 5 — tube wrapper above the lever
# ═══════════════════════════════════════════════════════
#
# Above zone 4 (which ends at Z=ZONE4_Z_TOP=57.5 — high enough to clear
# the lever's swing envelope), the shell wraps just the tubes with a
# 3 mm wall. Cross-section is the union of:
#   - water cylinder bore + 3 mm wall
#   - flavor pill bore + 3 mm wall
# straight-extruded vertically. This zone "violates" FILL_X_MIN —
# the wrapper around the water tube (centered at X=8.875) extends
# in -X past FILL_X_MIN, but that's safe because we're now above
# the lever's reach.
ZONE5_Z_BOTTOM = ZONE4_Z_TOP                                        # 57.5
ZONE5_Z_TOP    = ZONE4_Z_TOP + 10.0                                 # 67.5
ZONE5_HEIGHT   = ZONE5_Z_TOP - ZONE5_Z_BOTTOM                       # 10
ZONE5_WALL     = WALL_THICKNESS_MIN                                 # 3.0 — matches
                                                                     # the rest of
                                                                     # the shell now
                                                                     # that the tubes
                                                                     # are bigger.
                                                                     # Used inside the
                                                                     # base lid socket
                                                                     # (everything that
                                                                     # has to fit through
                                                                     # the socket cut).
ZONE5_WALL_ABOVE = 4.0                                              # mm — wall above
                                                                     # the lid socket
                                                                     # (exposed gooseneck
                                                                     # + the upper part
                                                                     # of the tube shell
                                                                     # vertical above
                                                                     # WALL_TRANSITION_Z).
                                                                     # Thicker so dowel
                                                                     # pin/hole features
                                                                     # have enough wall
                                                                     # to print and hold
                                                                     # tolerance.


# ═══════════════════════════════════════════════════════
# ZONE 6 — gooseneck wrapper around the bent dispense tubes
# ═══════════════════════════════════════════════════════
#
# Pure continuation of zone 5's cross-section along the same bent
# path the dispense tubes follow above the lever-swing envelope.
# Same wall thickness, same water/flavor/fill layout, rotated through
# the gooseneck bends.
#
# Path (in tube-local XZ plane, origin at the zone 5 / zone 6 seam):
#   1. vertical lift from Z=0 up to Z=GN_BEND1_START_Z − ZONE5_Z_TOP
#   2. bend 1 — GN_BEND1_SWEEP_RAD at R = GN_BEND1_R, bending toward -X
#   3. GN_MID_STRAIGHT_LEN angled straight
#   4. bend 2 — GN_BEND2_SWEEP_RAD at R = GN_BEND2_R
#   5. GN_TIP_STRAIGHT_LEN tip
#
# Sweep frame: cross-section centered on the water tube. The flavor
# pill's +X offset (FLAVOR_TUBE_POST_BEND_X − WATER_TUBE_X ≈ 6.148 mm)
# is carried in the LOCAL frame, so as the tangent rotates through
# each bend the pill traces a parallel-offset arc at the larger
# radius (water R + 6.148) — matching the actual flavor tubes'
# centerlines.
#
# These mirror constants in the assembly (`faucet-assembly`); if the
# assembly's gooseneck moves, update both.

GN_BEND1_R          = 30.0                                           # water tube — bend 1
GN_BEND2_R          = 40.0                                           # water tube — bend 2
GN_BEND1_SWEEP_RAD  = math.radians(30.0)
GN_BEND2_SWEEP_RAD  = math.radians(110.0)
LEVER_TOP_Z         = ZONE2_Z_TOP + 13.0                             # 52
GN_BEND1_MID_Z      = LEVER_TOP_Z + 35.0                             # 87
GN_BEND1_START_Z    = (
    GN_BEND1_MID_Z
    - GN_BEND1_R * math.sin(GN_BEND1_SWEEP_RAD / 2.0)
)                                                                    # ≈ 79.24
GN_MID_STRAIGHT_LEN = 115.0
GN_TIP_STRAIGHT_LEN = 25.0
ZONE6_WALL          = ZONE5_WALL_ABOVE                               # 4.0 — gooseneck
                                                                     # is entirely above
                                                                     # the lid socket


# ═══════════════════════════════════════════════════════
# ZONE 3 OUTER ARCH — full-height curve from wing bottom to zone 4
# ═══════════════════════════════════════════════════════
#
# The wing/fill arch is a single circular arc that spans the wing's
# full Z range (ZONE3_Z_BOTTOM at the low-X end up to ZONE4_Z_TOP at
# X=FILL_X_MIN), tangent-horizontal at the high end so it meets zone
# 4's flat top surface smoothly. The arch covers the full -X extent
# of the wing — there is no flat foot-top segment.
#
# Geometry: circular arc whose center is directly below the high end
# (FILL_X_MIN, c_z) so the tangent there is horizontal. Solving
# distance(center, low_end) == distance(center, high_end) gives c_z.
_NEW_ARCH_LOW_X  = SHELL_CENTER_X - SHELL_RECT_X_HALF                # rect_x_min = -19
_NEW_ARCH_LOW_Z  = ZONE3_Z_BOTTOM                                    # 39
_NEW_ARCH_HIGH_X = FILL_X_MIN                                        # 10.46
_NEW_ARCH_HIGH_Z = ZONE4_Z_TOP                                       # 55
_NEW_ARCH_DX     = _NEW_ARCH_HIGH_X - _NEW_ARCH_LOW_X                # 29.46
_NEW_ARCH_C_Z    = (
    (_NEW_ARCH_HIGH_Z + _NEW_ARCH_LOW_Z) / 2.0
    - _NEW_ARCH_DX**2 / (2.0 * (_NEW_ARCH_HIGH_Z - _NEW_ARCH_LOW_Z))
)                                                                    # ≈ 19.88
_NEW_ARCH_R      = _NEW_ARCH_HIGH_Z - _NEW_ARCH_C_Z                  # ≈ 35.12
# Midpoint of the arc — angular midway between high end (90° from
# center, directly above) and low end.
_NEW_ARCH_A_LOW  = math.atan2(_NEW_ARCH_LOW_Z - _NEW_ARCH_C_Z,
                              _NEW_ARCH_LOW_X - _NEW_ARCH_HIGH_X)
_NEW_ARCH_A_MID  = (math.pi / 2.0 + _NEW_ARCH_A_LOW) / 2.0
NEW_ARCH_MID_X   = _NEW_ARCH_HIGH_X + _NEW_ARCH_R * math.cos(_NEW_ARCH_A_MID)   # ≈ -6.28
NEW_ARCH_MID_Z   = _NEW_ARCH_C_Z + _NEW_ARCH_R * math.sin(_NEW_ARCH_A_MID)      # ≈ 50.75


# ═══════════════════════════════════════════════════════
# ZONE 4.5 — block above the lever, up to the gooseneck bend start
# ═══════════════════════════════════════════════════════
#
# A tall block capping the lever swing volume from above and reaching
# up to the gooseneck bend start (Z=GN_BEND1_START_Z ≈ 78.78). The -X
# edge sits at ZONE45_FRONT_X — chosen so the front margin (zone 4.5
# front X to zone 5's water-circle -X edge) matches the back margin
# (zone 4.5 back X to zone 5's flavor-pill +X edge), giving zone 5
# visually centered when looking down the X axis. This pulls the
# front past the lever's "ridge" line LEVER_RIDGE_X (the X where the
# pressed lever's tilted top crosses the rest lever's flat top at
# Z=LEVER_REST_TOP_Z), but the lid's bottom on the arch curve still
# clears the lever's swing envelope by ~0.9 mm there.
#
# Bottom face = arch curve from (ZONE45_FRONT_X, arch_z) up to
# (FILL_X_MIN, ZONE4_Z_TOP), then flat at ZONE4_Z_TOP out to the +X
# cylinder back. Top face = flat at ZONE45_Z_TOP. Both -X and +X
# edges curve inward at large |Y| via mirrored cylinder clips of
# radius SHELL_OUTER_R.
#
# Lever swing geometry mirrors the assembly's build_lever — pivot
# parallel to Y at (LEVER_PIVOT_X, *, LEVER_PIVOT_Z), pressed-down
# rotates by LEVER_PRESSED_ANGLE about that axis.

LEVER_PIVOT_X        = 1.5
LEVER_PIVOT_Z        = ZONE2_Z_TOP + 7.0          # 46 — = PLATEAU_Z+1+6
LEVER_PRESSED_ANGLE  = math.radians(18.0)
LEVER_REST_TOP_Z     = ZONE2_Z_TOP + 13.0         # 52 — = PLATEAU_Z+1+12
_LEVER_DZ_PIVOT      = LEVER_REST_TOP_Z - LEVER_PIVOT_Z   # 6

# Closed form for where pressed top crosses Z=LEVER_REST_TOP_Z:
# Z'(X0) = Z_pivot + (X0-X_pivot)·sin θ + dz_pivot·cos θ = Z_rest
#   ⇒  (X0-X_pivot) = dz_pivot·(1-cos θ)/sin θ
# X'(X0) = X_pivot + (X0-X_pivot)·cos θ - dz_pivot·sin θ
#   ⇒  X' = X_pivot - dz_pivot·(1-cos θ)/sin θ = X_pivot - dz_pivot·tan(θ/2)
# Informational — the visible "ridge" of the lever swing envelope.
# Not directly used in the build (ZONE45_FRONT_X overrides it).
LEVER_RIDGE_X = (
    LEVER_PIVOT_X
    - _LEVER_DZ_PIVOT * math.tan(LEVER_PRESSED_ANGLE / 2.0)
)                                                  # ≈ 0.55

# Zone 5's X extents at Y=0, used to derive zone 4.5's matched-margin
# front X. Mirrors the cross-section in build_zone5_outer.
_Z5_WATER_R_OUTER = WATER_HOLE_DIAMETER / 2.0 + ZONE5_WALL           # 9.0125
_Z5_FLAVOR_X_HALF = (PILL_WIDTH_X + 2.0 * ZONE5_WALL) / 2.0          # 7.425
_Z5_X_MIN         = WATER_TUBE_X - _Z5_WATER_R_OUTER                 # -0.1375
_Z5_X_MAX         = FLAVOR_TUBE_POST_BEND_X + _Z5_FLAVOR_X_HALF      # 23.575

ZONE45_BACK_X      = SHELL_CENTER_X + SHELL_OUTER_R                  # 25.35
_ZONE45_X_MARGIN   = ZONE45_BACK_X - _Z5_X_MAX                       # 1.775
ZONE45_FRONT_X     = _Z5_X_MIN - _ZONE45_X_MARGIN                    # ≈ -1.9125

ZONE45_Z_TOP                = (ZONE4_Z_TOP + GN_BEND1_START_Z) / 2.0  # halfway between
                                                                       # zone 4 top and
                                                                       # gooseneck bend start
                                                                       # ≈ 68.37
# Z above which the tube shell switches from ZONE5_WALL (3 mm) to
# ZONE5_WALL_ABOVE (4 mm). Set to the lid top so the entire region
# that has to fit through the base's lid socket stays at 3 mm wall —
# the base socket is unchanged.
WALL_TRANSITION_Z           = ZONE45_Z_TOP                            # ≈ 68.37
ZONE45_BOT_Z_AT_FRONT       = (
    _NEW_ARCH_C_Z
    + math.sqrt(_NEW_ARCH_R ** 2 - (ZONE45_FRONT_X - FILL_X_MIN) ** 2)
)                                                  # ≈ 52.75

# Mid-point of the bottom arch sub-arc, between ZONE45_FRONT_X end
# and FILL_X_MIN end.
_a_front = math.atan2(
    ZONE45_BOT_Z_AT_FRONT - _NEW_ARCH_C_Z,
    ZONE45_FRONT_X - FILL_X_MIN,
)
_a_high  = math.pi / 2.0       # FILL_X_MIN end is directly above arch center
_a_mid45 = (_a_front + _a_high) / 2.0
ZONE45_BOT_MID_X = FILL_X_MIN + _NEW_ARCH_R * math.cos(_a_mid45)
ZONE45_BOT_MID_Z = _NEW_ARCH_C_Z + _NEW_ARCH_R * math.sin(_a_mid45)


# ═══════════════════════════════════════════════════════
# GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════

def _flavor_pill_flat_x_minus(z_bottom: float, z_height: float) -> cq.Workplane:
    """Flavor pill cutout at FLAVOR_TUBE_X with the X- side flattened.

    Same as the original slot2D pill (PILL_LENGTH_Y × PILL_WIDTH_X, Y-oriented),
    but the X- side has square corners at (FLAVOR_PILL_X_MINUS_EDGE,
    ±PILL_LENGTH_Y/2) instead of the rounded transitions to the Y+/Y-
    semicircular caps. Removes thin shell features on the X- side of the
    cutout that print poorly. The Y+/Y- caps and the X+ side stay rounded.

    The flat -X edge sits at FLAVOR_PILL_X_MINUS_EDGE, which is pulled
    past the natural slot2D edge when needed so the corners reach the
    body bore in zone 1. See the constant's definition for the rule.

    Construction: union of the original slot2D and a rectangle that
    covers everything from FLAVOR_PILL_X_MINUS_EDGE up to FLAVOR_TUBE_X
    on the X- side, so the flat edge ends up at FLAVOR_PILL_X_MINUS_EDGE
    regardless of whether the slot2D edge is closer or farther.
    """
    pill = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(FLAVOR_TUBE_X, 0)
        .slot2D(PILL_LENGTH_Y, PILL_WIDTH_X, angle=90)
        .extrude(z_height)
    )
    fill_width = FLAVOR_TUBE_X - FLAVOR_PILL_X_MINUS_EDGE
    fill_rect = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(FLAVOR_TUBE_X - fill_width / 2.0, 0)
        .rect(fill_width, PILL_LENGTH_Y)
        .extrude(z_height)
    )
    return pill.union(fill_rect)


def build_zone1_outer() -> cq.Workplane:
    """Filled cylinder, from the deck up to ZONE1_OUTER_TOP.

    ZONE1_OUTER_TOP sits SHELL_OUTER_LIP above the body's cylinder top
    (which is at ZONE1_Z_TOP). That lift gives the shell a flat
    cylindrical wall directly above the body's cylinder top face,
    instead of starting the cove transition at the same Z where the
    body's cylinder ends.
    """
    return (
        cq.Workplane("XY")
        .workplane(offset=ZONE1_Z_BOTTOM)
        .moveTo(SHELL_CENTER_X, SHELL_CENTER_Y)
        .circle(SHELL_OUTER_R)
        .extrude(ZONE1_OUTER_TOP - ZONE1_Z_BOTTOM)
    )


def build_zone1_inner_cut() -> cq.Workplane:
    """Combined body bore + flavor-tube pill, as one solid to subtract.

    Body bore extends from Z=ZONE1_Z_BOTTOM up to ZONE2_BORE_BOTTOM
    (= ZONE1_Z_TOP + BORE_CLEARANCE = 13.25), so the bore's Z step
    sits BORE_CLEARANCE above the body's cyl top face at Z=13.

    Body bore and pill overlap by 0.4625 mm in X at the body/pill
    seam, so the result is a single connected hole.
    """
    body_bore_height = ZONE2_BORE_BOTTOM - ZONE1_Z_BOTTOM
    body_bore = (
        cq.Workplane("XY")
        .workplane(offset=ZONE1_Z_BOTTOM)
        .moveTo(BODY_BORE_X, BODY_BORE_Y)
        .circle(BODY_BORE_DIAMETER / 2.0)
        .extrude(body_bore_height)
    )
    pill = _flavor_pill_flat_x_minus(ZONE1_Z_BOTTOM, ZONE1_HEIGHT)
    return body_bore.union(pill)


def build_zone2_outer() -> cq.Workplane:
    """Outer geometry for zone 2.

    Construction mirrors the body's `build_transition_cove`:
      - Rectangle column from Z=ZONE2_OUTER_BOT to ZONE2_Z_TOP.
      - Filler block (R wide × R tall, full X extent) on each Y face.
      - Cove cutter (cylinder along X axis, R = COVE_R) scoops a
        concave arc from each filler.
      - Cylinder clip rounds the rectangle corners to follow the
        shell outer cylinder profile.

    Zone 2 OUTER starts SHELL_OUTER_LIP above the body's cylinder top
    (i.e., at Z = ZONE2_OUTER_BOT = 16, not at the body's transition Z
    of 13). This leaves a 3 mm cylindrical shell wall above the body's
    cylinder top face. The bore is unaffected — see build_zone2_inner_cut.
    """
    z_height = ZONE2_Z_TOP - ZONE2_OUTER_BOT

    rect = (
        cq.Workplane("XY")
        .workplane(offset=ZONE2_OUTER_BOT)
        .moveTo(SHELL_CENTER_X, SHELL_CENTER_Y)
        .rect(SHELL_RECT_X_WIDTH, SHELL_RECT_Y_WIDTH)
        .extrude(z_height)
    )

    R = COVE_R
    ext_x = SHELL_RECT_X_HALF + 2.0   # generous half-extent in X for filler/cutter

    def filler(y_sign: int) -> cq.Workplane:
        flat_y_world = SHELL_CENTER_Y + y_sign * SHELL_RECT_Y_HALF
        blk_cy_world = flat_y_world + y_sign * (R / 2.0)
        return (
            cq.Workplane("XY")
            .workplane(offset=ZONE2_OUTER_BOT)
            .moveTo(SHELL_CENTER_X, blk_cy_world)
            .rect(2.0 * ext_x, R)
            .extrude(R)
        )

    def cove_cutter(y_sign: int) -> cq.Workplane:
        flat_y_world  = SHELL_CENTER_Y + y_sign * SHELL_RECT_Y_HALF
        cove_cy_world = flat_y_world + y_sign * R
        cove_cz_world = ZONE2_OUTER_BOT + R
        return (
            cq.Workplane("YZ")
            .workplane(offset=SHELL_CENTER_X - ext_x)
            .moveTo(cove_cy_world, cove_cz_world)
            .circle(R)
            .extrude(2.0 * ext_x)
        )

    outer = (
        rect
        .union(filler(+1))
        .union(filler(-1))
        .cut(cove_cutter(+1))
        .cut(cove_cutter(-1))
    )

    # Clip to the shell's outer cylinder profile so rect corners follow
    # the cylinder rather than sticking out as sharp points.
    clip_cyl = (
        cq.Workplane("XY")
        .workplane(offset=ZONE2_OUTER_BOT)
        .moveTo(SHELL_CENTER_X, SHELL_CENTER_Y)
        .circle(SHELL_OUTER_R)
        .extrude(z_height)
    )
    return outer.intersect(clip_cyl)


def build_zone2_inner_cut() -> cq.Workplane:
    """Inner cut for zone 2 — mirrors the body's cross-section with
    0.5 mm dimensional clearance for slip-fit assembly.

    The bore is built with the SAME construction as the body's outer:
      - Rect column 32 × 17.5 mm from Z=13 to Z=39
      - Filler block (R wide × R tall, full X extent) on each Y face
        at Z=13 to Z=18
      - Cove cutter (cylinder along X, R=5 mm) scoops the concave arc
        from each filler
      - Cylinder clip (R=16 mm) trims the rect corners and X faces
        into the body's rect∩cylinder profile

    This matters in two places:
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
    R_bore = COVE_R
    ext_x_bore = BODY_BORE_RECT_LONG / 2.0 + 2.0   # generous half-extent in X
    bore_zone2_height = ZONE2_Z_TOP - ZONE2_BORE_BOTTOM    # 25.75

    # Bore rect column — starts at ZONE2_BORE_BOTTOM (lifted by clearance)
    rect_col = (
        cq.Workplane("XY")
        .workplane(offset=ZONE2_BORE_BOTTOM)
        .moveTo(BODY_BORE_X, BODY_BORE_Y)
        .rect(BODY_BORE_RECT_LONG, BODY_BORE_RECT_SHORT)
        .extrude(bore_zone2_height)
    )

    def filler(y_sign: int) -> cq.Workplane:
        flat_y_world = BODY_BORE_Y + y_sign * (BODY_BORE_RECT_SHORT / 2.0)
        blk_cy_world = flat_y_world + y_sign * (R_bore / 2.0)
        return (
            cq.Workplane("XY")
            .workplane(offset=ZONE2_BORE_BOTTOM)
            .moveTo(BODY_BORE_X, blk_cy_world)
            .rect(2.0 * ext_x_bore, R_bore)
            .extrude(R_bore)
        )

    def cove_cutter(y_sign: int) -> cq.Workplane:
        flat_y_world  = BODY_BORE_Y + y_sign * (BODY_BORE_RECT_SHORT / 2.0)
        cove_cy_world = flat_y_world + y_sign * R_bore
        cove_cz_world = ZONE2_BORE_BOTTOM + R_bore
        return (
            cq.Workplane("YZ")
            .workplane(offset=BODY_BORE_X - ext_x_bore)
            .moveTo(cove_cy_world, cove_cz_world)
            .circle(R_bore)
            .extrude(2.0 * ext_x_bore)
        )

    bore = (
        rect_col
        .union(filler(+1))
        .union(filler(-1))
        .cut(cove_cutter(+1))
        .cut(cove_cutter(-1))
    )

    # Cylinder clip — match the body's rect∩cylinder profile
    clip_cyl = (
        cq.Workplane("XY")
        .workplane(offset=ZONE2_BORE_BOTTOM)
        .moveTo(BODY_BORE_X, BODY_BORE_Y)
        .circle(BODY_BORE_DIAMETER / 2.0)
        .extrude(bore_zone2_height)
    )
    bore = bore.intersect(clip_cyl)

    # Flavor-tube pill (full Z range — pill has no body-equivalent
    # transition, so it just runs from ZONE2_Z_BOTTOM continuously)
    pill = _flavor_pill_flat_x_minus(ZONE2_Z_BOTTOM, ZONE2_HEIGHT)

    return bore.union(pill)


def build_zone3_outer() -> cq.Workplane:
    """Two arch wings at ±Y wrapping the body's arch ridges."""
    rect_x_min = SHELL_CENTER_X - SHELL_RECT_X_HALF
    rect_x_max = SHELL_CENTER_X + SHELL_RECT_X_HALF

    def wing(y_bottom: float, y_height: float) -> cq.Workplane:
        # Profile (in XZ plane), traversed CCW:
        #   bottom-left (rect_x_min, ZONE3_Z_BOTTOM)
        #   → bottom-right (rect_x_max, ZONE3_Z_BOTTOM)
        #   → up to ZONE4_Z_TOP at +X
        #   → left along top to FILL_X_MIN at ZONE4_Z_TOP
        #   → arch down-left back to start (rect_x_min, ZONE3_Z_BOTTOM)
        return (
            cq.Workplane("XZ")
            .workplane(offset=y_bottom)
            .moveTo(rect_x_min, ZONE3_Z_BOTTOM)
            .lineTo(rect_x_max, ZONE3_Z_BOTTOM)
            .lineTo(rect_x_max, ZONE4_Z_TOP)
            .lineTo(FILL_X_MIN, ZONE4_Z_TOP)
            .threePointArc((NEW_ARCH_MID_X, NEW_ARCH_MID_Z),
                           (rect_x_min, ZONE3_Z_BOTTOM))
            .close()
            .extrude(y_height)
        )

    wing_thickness = WING_OUTER_Y - WING_INNER_Y
    wings = wing(+WING_INNER_Y, +wing_thickness).union(
        wing(-WING_OUTER_Y, +wing_thickness)
    )

    clip_cyl = (
        cq.Workplane("XY")
        .workplane(offset=ZONE3_Z_BOTTOM)
        .moveTo(SHELL_CENTER_X, SHELL_CENTER_Y)
        .circle(SHELL_OUTER_R)
        .extrude(ZONE4_Z_TOP - ZONE3_Z_BOTTOM)
    )
    return wings.intersect(clip_cyl)


def build_zone3_inner_cut() -> cq.Workplane:
    """Two arch bores at ±Y mirroring the body arches with BORE_CLEARANCE."""
    bore_x_oversize = BODY_BORE_DIAMETER / 2.0 + 2.0     # generous; bore-cyl-clipped below

    def bore(y_bottom: float, y_height: float) -> cq.Workplane:
        return (
            cq.Workplane("XZ")
            .workplane(offset=y_bottom)
            .moveTo(-bore_x_oversize, ZONE3_Z_BOTTOM)
            .lineTo(+bore_x_oversize, ZONE3_Z_BOTTOM)
            .lineTo(+bore_x_oversize, SHELL_ARCH_BORE_FOOT_TOP_Z)
            .threePointArc((0, SHELL_ARCH_BORE_PEAK_Z),
                           (-bore_x_oversize, SHELL_ARCH_BORE_FOOT_TOP_Z))
            .close()
            .extrude(y_height)
        )

    bore_thickness = SHELL_ARCH_BORE_OUTER_Y - SHELL_ARCH_BORE_INNER_Y
    bores = bore(+SHELL_ARCH_BORE_INNER_Y, +bore_thickness).union(
        bore(-SHELL_ARCH_BORE_OUTER_Y, +bore_thickness)
    )

    clip_cyl = (
        cq.Workplane("XY")
        .workplane(offset=ZONE3_Z_BOTTOM)
        .moveTo(BODY_BORE_X, BODY_BORE_Y)
        .circle(BODY_BORE_DIAMETER / 2.0)
        .extrude(SHELL_ARCH_BORE_PEAK_Z - ZONE3_Z_BOTTOM)
    )
    return bores.intersect(clip_cyl)


def _body_bore_above_body_cut(z_bottom: float, z_height: float) -> cq.Workplane:
    """Body bore cylinder (R = BODY_BORE_DIAMETER/2 at origin) over the
    given Z range, used as a CUT in zone 3 fill outer and zone 4 outer.

    Above the body's plateau (Z > ZONE2_Z_TOP = 39) the body has ended,
    so this column of the body bore is empty space. We keep the shell
    from filling it for two reasons:

      1. The flavor tubes' S-bend passes through this region (going
         from the body's flavor channel at X=17.3375 down to the
         post-bend X=15.023). They don't need a shell wrap here —
         the body's flavor channel locates them below, and zone 4.5
         (the lid) holds them from above.

      2. Printed support material inside the dispense-tube channel
         needs a path out. Leaving the body-bore column open all
         the way up to ZONE4_Z_TOP gives the central cavity an
         opening at the back, so support can be extracted after
         printing.

    Note: applied LOCAL to zones 3 fill and 4 — NOT at the build_shell
    level — because zone 4.5 needs to span this column unbroken (the
    lid is the structural element holding the tubes up there).
    """
    return (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(BODY_BORE_X, BODY_BORE_Y)
        .circle(BODY_BORE_DIAMETER / 2.0)
        .extrude(z_height)
    )


def build_zone3_fill_outer() -> cq.Workplane:
    """Plateau fill behind FILL_X_MIN — same arch profile as the wings,
    extruded across the plateau Y range. The body bore column is cut
    away (see _body_bore_above_body_cut for why).
    """
    rect_x_min = SHELL_CENTER_X - SHELL_RECT_X_HALF
    rect_x_max = SHELL_CENTER_X + SHELL_RECT_X_HALF
    fill_y_thickness = 2.0 * WING_INNER_Y                            # 13.5

    arch_solid = (
        cq.Workplane("XZ")
        .workplane(offset=-WING_INNER_Y)
        .moveTo(rect_x_min, ZONE3_Z_BOTTOM)
        .lineTo(rect_x_max, ZONE3_Z_BOTTOM)
        .lineTo(rect_x_max, ZONE4_Z_TOP)
        .lineTo(FILL_X_MIN, ZONE4_Z_TOP)
        .threePointArc((NEW_ARCH_MID_X, NEW_ARCH_MID_Z),
                       (rect_x_min, ZONE3_Z_BOTTOM))
        .close()
        .extrude(fill_y_thickness)
    )

    keep_x_box = (
        cq.Workplane("XY")
        .workplane(offset=ZONE3_Z_BOTTOM)
        .moveTo((FILL_X_MIN + rect_x_max) / 2.0, 0)
        .rect(rect_x_max - FILL_X_MIN, fill_y_thickness)
        .extrude(ZONE4_Z_TOP - ZONE3_Z_BOTTOM)
    )

    clip_cyl = (
        cq.Workplane("XY")
        .workplane(offset=ZONE3_Z_BOTTOM)
        .moveTo(SHELL_CENTER_X, SHELL_CENTER_Y)
        .circle(SHELL_OUTER_R)
        .extrude(ZONE4_Z_TOP - ZONE3_Z_BOTTOM)
    )

    return (
        arch_solid
        .intersect(keep_x_box)
        .intersect(clip_cyl)
        .cut(_body_bore_above_body_cut(
            ZONE3_Z_BOTTOM, ZONE4_Z_TOP - ZONE3_Z_BOTTOM
        ))
    )


def build_zone3_fill_inner_cut() -> cq.Workplane:
    """Tube cutouts through the plateau fill: water tube + straight flavor pill.

    Flavor cut is a straight pill at FLAVOR_TUBE_X (matching zones 1+2). The
    bend that previously lived here is no longer needed — with the new
    base/tube-shell split, the LLDPE flavor tubes are routed through the
    tube shell first (post-bend at FLAVOR_TUBE_POST_BEND_X) and then dropped
    into the base; they flex through the socket area on the way down.
    """
    z_height = SHELL_ARCH_PEAK_Z - ZONE3_Z_BOTTOM

    water_hole = (
        cq.Workplane("XY")
        .workplane(offset=ZONE3_Z_BOTTOM)
        .moveTo(WATER_TUBE_X, 0)
        .circle(WATER_HOLE_DIAMETER / 2.0)
        .extrude(z_height)
    )

    flavor_pill = _flavor_pill_flat_x_minus(ZONE3_Z_BOTTOM, z_height)

    return water_hole.union(flavor_pill)


def build_zone4_outer() -> cq.Workplane:
    """Vertical extrusion of the cyl-clipped rect at X ≥ FILL_X_MIN.

    Cross-section matches zone 2's outline above its cove (rect ∩ outer
    cyl, no cove since the cove only lives at Z=16.25→21.25 in zone 2).
    The same outline is extruded straight up from ZONE4_Z_BOTTOM to
    ZONE4_Z_TOP — straight vertical sides, no taper. Wall thickness
    around the tubes is whatever falls out of (outer minus inner cut),
    not a fixed 3 mm offset.

    The body bore column is cut away (see _body_bore_above_body_cut for
    why) — the central column stays open, so the flavor tubes' S-bend
    passes through unwrapped and printed support material can be
    extracted from the dispense channel.
    """
    z_height = ZONE4_HEIGHT

    rect = (
        cq.Workplane("XY")
        .workplane(offset=ZONE4_Z_BOTTOM)
        .moveTo(SHELL_CENTER_X, SHELL_CENTER_Y)
        .rect(SHELL_RECT_X_WIDTH, SHELL_RECT_Y_WIDTH)
        .extrude(z_height)
    )
    clip_cyl = (
        cq.Workplane("XY")
        .workplane(offset=ZONE4_Z_BOTTOM)
        .moveTo(SHELL_CENTER_X, SHELL_CENTER_Y)
        .circle(SHELL_OUTER_R)
        .extrude(z_height)
    )
    keep_x = (
        cq.Workplane("XY")
        .workplane(offset=ZONE4_Z_BOTTOM - 1)
        .moveTo(FILL_X_MIN + 50, 0)
        .rect(100, 200)
        .extrude(z_height + 2)
    )
    return (
        rect
        .intersect(clip_cyl)
        .intersect(keep_x)
        .cut(_body_bore_above_body_cut(ZONE4_Z_BOTTOM, ZONE4_HEIGHT))
    )


def build_zone4_inner_cut() -> cq.Workplane:
    """Tube cavity: water-tube cyl + straight flavor pill at FLAVOR_TUBE_X.

    Previously this was a 3D loft from a wider rounded-rect at the bottom
    to a pill at FLAVOR_TUBE_POST_BEND_X at the top, transitioning the
    flavor tube position. With the new base/tube-shell split, the bend
    is handled in the tube shell + the socket area above, so the base
    just needs straight pill clearance at FLAVOR_TUBE_X.
    """
    water_inner = (
        cq.Workplane("XY")
        .workplane(offset=ZONE4_Z_BOTTOM)
        .moveTo(WATER_TUBE_X, 0)
        .circle(WATER_HOLE_DIAMETER / 2.0)
        .extrude(ZONE4_HEIGHT)
    )

    flavor_pill = _flavor_pill_flat_x_minus(ZONE4_Z_BOTTOM, ZONE4_HEIGHT)

    return water_inner.union(flavor_pill)


def build_zone45_outer() -> cq.Workplane:
    """Zone 4.5 — tall block capping the lever swing volume, reaching
    up to the gooseneck bend start.

    XZ profile (CCW), extruded across full Y range, then clipped by
    two cylinders (back + front, mirrored across the block's X
    midpoint) so the +X and -X edges have matching rounded curves:
      start at (ZONE45_FRONT_X, ZONE45_BOT_Z_AT_FRONT)
      → arch up to (FILL_X_MIN, ZONE4_Z_TOP)
      → flat to (rect_x_max, ZONE4_Z_TOP)
      → vertical up to (rect_x_max, ZONE45_Z_TOP)
      → flat back to (ZONE45_FRONT_X, ZONE45_Z_TOP)
      → close (vertical down to start)

    Back clip: SHELL_OUTER_R cylinder centered at SHELL_CENTER_X — the
    same cylinder zones 1-4 use (curves the +X corner inward at large |Y|).
    Front clip: SHELL_OUTER_R cylinder centered at ZONE45_FRONT_X +
    SHELL_OUTER_R, mirroring the back clip across the block's X
    midpoint. At Y=0 both clips are tangent to the block's -X / +X
    edges; at |Y| = SHELL_RECT_Y_HALF both edges curve inward by the
    same amount.
    """
    rect_x_max = SHELL_CENTER_X + SHELL_RECT_X_HALF        # 25.35
    y_half     = SHELL_RECT_Y_HALF                          # 11.75

    profile_solid = (
        cq.Workplane("XZ")
        .workplane(offset=-y_half)
        .moveTo(ZONE45_FRONT_X, ZONE45_BOT_Z_AT_FRONT)
        .threePointArc(
            (ZONE45_BOT_MID_X, ZONE45_BOT_MID_Z),
            (FILL_X_MIN, ZONE4_Z_TOP),
        )
        .lineTo(rect_x_max, ZONE4_Z_TOP)
        .lineTo(rect_x_max, ZONE45_Z_TOP)
        .lineTo(ZONE45_FRONT_X, ZONE45_Z_TOP)
        .close()
        .extrude(2.0 * y_half)
    )

    z_min = ZONE45_BOT_Z_AT_FRONT
    z_max = ZONE45_Z_TOP
    clip_height = (z_max - z_min) + 1.0

    back_clip_cyl = (
        cq.Workplane("XY")
        .workplane(offset=z_min - 0.5)
        .moveTo(SHELL_CENTER_X, SHELL_CENTER_Y)
        .circle(SHELL_OUTER_R)
        .extrude(clip_height)
    )
    front_clip_cyl = (
        cq.Workplane("XY")
        .workplane(offset=z_min - 0.5)
        .moveTo(ZONE45_FRONT_X + SHELL_OUTER_R, SHELL_CENTER_Y)
        .circle(SHELL_OUTER_R)
        .extrude(clip_height)
    )
    return profile_solid.intersect(back_clip_cyl).intersect(front_clip_cyl)


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
    GN_BEND1_R, bend 2 uses GN_BEND2_R (independent radii).

    Path origin (s=0) is at WALL_TRANSITION_Z (= lid top), so the
    gooseneck starts where the 4 mm wall takes over from the 3 mm
    wall vertical section beneath.
    """
    z_lift = GN_BEND1_START_Z - WALL_TRANSITION_Z

    p_bottom     = (0.0, 0.0)
    p_bend_start = (0.0, z_lift)

    mid1, end1, tan1 = _arc_from_tangent(
        p_bend_start, (0.0, 1.0), GN_BEND1_R, GN_BEND1_SWEEP_RAD, ccw=True
    )
    mid_end = (end1[0] + GN_MID_STRAIGHT_LEN * tan1[0],
               end1[1] + GN_MID_STRAIGHT_LEN * tan1[1])
    mid2, end2, tan2 = _arc_from_tangent(
        mid_end, tan1, GN_BEND2_R, GN_BEND2_SWEEP_RAD, ccw=True
    )
    tip_end = (end2[0] + GN_TIP_STRAIGHT_LEN * tan2[0],
               end2[1] + GN_TIP_STRAIGHT_LEN * tan2[1])

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
    (around the flavor pill) are both ZONE5_WALL. The "stretch" is
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
    flavor_offset_x = FLAVOR_TUBE_POST_BEND_X - WATER_TUBE_X
    natural_water_r = WATER_HOLE_DIAMETER / 2.0 + ZONE6_WALL
    natural_pill_y_half = PILL_LENGTH_Y / 2.0 + ZONE6_WALL
    y_half = max(natural_water_r, natural_pill_y_half)
    y_total = 2.0 * y_half

    water_x_width = 2.0 * natural_water_r
    water_slot_straight = y_total - water_x_width

    pill_short_total = PILL_WIDTH_X + 2.0 * ZONE6_WALL
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
    flavor_offset_x = FLAVOR_TUBE_POST_BEND_X - WATER_TUBE_X
    pill_straight = PILL_LENGTH_Y - PILL_WIDTH_X                 # 3.175
    return (
        cq.Sketch()
        .circle(WATER_HOLE_DIAMETER / 2.0)
        .push([(flavor_offset_x, 0)])
        .slot(pill_straight, PILL_WIDTH_X, angle=90, mode="a")
        .clean()
    )


def build_zone6_outer() -> cq.Workplane:
    """Sweep the outer cross-section along the gooseneck path, then
    place at (WATER_TUBE_X, 0, WALL_TRANSITION_Z).

    Sits on top of the 3 mm wall vertical extrusion (which extends
    from TUBE_SHELL_BOTTOM_Z up to WALL_TRANSITION_Z = lid top). Zone
    6 uses ZONE6_WALL = ZONE5_WALL_ABOVE = 4 mm — visible 1 mm step
    on the outer at the seam.
    """
    profile = cq.Workplane("XY").placeSketch(_zone6_outer_sketch())
    swept = profile.sweep(_gooseneck_path_at_origin(), transition="right")
    return swept.translate((WATER_TUBE_X, 0, WALL_TRANSITION_Z))


def build_zone6_inner_cut() -> cq.Workplane:
    """Inner cut for zone 6 — same path, inner cross-section.

    Bore is unchanged across the wall transition — only the outer
    profile steps. Inner cut continues the vertical bore from the
    3 mm wall section below.
    """
    profile = cq.Workplane("XY").placeSketch(_zone6_inner_sketch())
    swept = profile.sweep(_gooseneck_path_at_origin(), transition="right")
    return swept.translate((WATER_TUBE_X, 0, WALL_TRANSITION_Z))


def build_lever_clearance() -> cq.Workplane:
    """Single triangular ramp wedge cut into the top of the rect column.

    In the XZ plane, the cut is a right triangle:
      - top edge flat at Z=ZONE2_Z_TOP (39), from X=LEVER_RAMP_X_MIN
        to X=LEVER_RAMP_X_START
      - vertical edge at X=LEVER_RAMP_X_MIN, dropping LEVER_RAMP_DEPTH
        below Z=39
      - sloped (ramp) edge at LEVER_RAMP_ANGLE_DEG, from the bottom of
        the vertical edge back up to the +X start point at Z=39

    Extruded ±LEVER_CLEARANCE_Y_HALF in Y. Single piece.
    """
    z_top = ZONE2_Z_TOP
    z_bot = z_top - LEVER_RAMP_DEPTH
    y_half = LEVER_CLEARANCE_Y_HALF

    return (
        cq.Workplane("XZ")
        .workplane(offset=-y_half)
        .polyline([
            (LEVER_RAMP_X_MIN,   z_bot),
            (LEVER_RAMP_X_MIN,   z_top),
            (LEVER_RAMP_X_START, z_top),
        ]).close()
        .extrude(2.0 * y_half)
    )


# ═══════════════════════════════════════════════════════
# SPLIT FOR PRINTING — base + tube shell with socket+tongue press-fit
# ═══════════════════════════════════════════════════════
#
# Two-part split for support-free printing:
#   - BASE shell    : zones 1-4 + zone 4.5 (the wider lid) + lever clearance,
#                     single piece. The lid has a SOCKET cut into it where the
#                     tube shell's tongue plugs in.
#   - TUBE shell    : 3 mm wall around the tubes from TUBE_SHELL_BOTTOM_Z
#                     up to WALL_TRANSITION_Z (= lid top) — fits the base
#                     socket. Above WALL_TRANSITION_Z, ZONE5_WALL_ABOVE
#                     (4 mm) takes over for the exposed gooseneck so the
#                     dowel features have enough wall to print and hold.
#                     Split into +Y and -Y halves at Y=0 so each half prints
#                     cut-side-down on the bed, eliminating supports for the
#                     gooseneck overhangs.
#
# Base ↔ tube interface: PRESS-FIT (no flat mating surface, no dowels). The
# tube shell's tongue inserts into the lid socket from above. Cross-section
# of socket = tube shell outer + SOCKET_CLEARANCE radial.
#
# Tube ↔ tube half interface: dowel pins at the Y=0 cut plane (still needed
# to align the two halves to each other).

# ─── Press-fit socket+tongue parameters ───
SOCKET_DEPTH       = 5.0    # mm — how far the tube shell tongue extends below
                            # zone 5's nominal bottom (current ZONE5_Z_BOTTOM)
SOCKET_CLEARANCE   = 0.15   # mm — radial clearance around tube shell outer
                            # (per side) — tight fit, may need adjustment

TUBE_SHELL_BOTTOM_Z = ZONE5_Z_BOTTOM - SOCKET_DEPTH   # 52.5
SOCKET_TOP_Z        = ZONE45_Z_TOP                    # 68.37 — clears zone 6
                                                       # vertical lift through lid
TUBE_SHELL_HEIGHT_VERTICAL = WALL_TRANSITION_Z - TUBE_SHELL_BOTTOM_Z  # 68.37 - 52.5 ≈ 15.87
                                                                       # extends up to the
                                                                       # lid top, covering
                                                                       # everything that
                                                                       # has to fit inside
                                                                       # the base socket.
                                                                       # Above this Z, the
                                                                       # gooseneck (zone 6)
                                                                       # takes over with
                                                                       # ZONE5_WALL_ABOVE.


# ─── Tube-half dowels (horizontal, Y axis, at the Y=0 cut plane) ───
# One half carries the dowels integrated into the print; the other half has
# matching holes. Dowel and hole share radius and length exactly — friction
# fit will be tuned by trial-and-error from this starting point.
DOWEL_R                    = 1.1
DOWEL_LEN                  = 2.5
DOWEL_BEARING_HALF_Y_SIGN  = -1   # -Y half carries the dowels

# Cross-section local-X positions for dowels. Local frame is centered on the
# water tube; local +X points toward the flavor pill. The dowels live in the
# 4 mm wall section above the lid (ZONE5_WALL_ABOVE = 4 mm thick), so the
# wall midpoint sits 2 mm out from the bore on each side.
#   Water -X wall:  local_x ∈ [-9.0125 (outer), -5.0125 (bore)] → midpoint -7.0125
#   Flavor +X wall: local_x ∈ [+10.700 (bore), +14.700 (outer)] → midpoint +12.700
_DOWEL_LOCAL_X_WATER  = -(WATER_HOLE_DIAMETER / 2.0 + ZONE5_WALL_ABOVE / 2.0)
_DOWEL_LOCAL_X_FLAVOR = (
    (FLAVOR_TUBE_POST_BEND_X - WATER_TUBE_X)
    + (PILL_WIDTH_X / 2.0 + ZONE5_WALL_ABOVE / 2.0)
)


def _path_pos_and_bitangent_at_s(s: float) -> tuple[float, float, float, float]:
    """World (X, Z) on the tube shell's centerline path and bitangent (Bx, Bz)
    at arclength s. Bitangent is in world XZ plane (= local +X direction in
    the cross-section sketch, which points toward the flavor pill).

    s = 0 corresponds to the gooseneck path origin =
    (WATER_TUBE_X, 0, WALL_TRANSITION_Z). Positive s walks up into the
    short vertical lift, then bend 1, mid-straight, bend 2, and the tip
    straight. Negative s would walk down into the 3 mm wall vertical
    extrusion below the lid; the dowels live in the 4 mm wall above.
    """
    z_lift   = GN_BEND1_START_Z - WALL_TRANSITION_Z
    arc1_len = GN_BEND1_R * GN_BEND1_SWEEP_RAD
    arc1_end_s = z_lift + arc1_len
    mid_end_s  = arc1_end_s + GN_MID_STRAIGHT_LEN
    arc2_len = GN_BEND2_R * GN_BEND2_SWEEP_RAD
    arc2_end_s = mid_end_s + arc2_len

    if s <= z_lift:
        # Vertical: tangent (0, 1), bitangent (1, 0).
        path_x_local, path_z_local = 0.0, s
        tan_x, tan_z = 0.0, 1.0
    elif s < arc1_end_s:
        # Bend 1: ccw arc, R = GN_BEND1_R, center at (-R, z_lift) in path-local XZ
        angle = (s - z_lift) / GN_BEND1_R
        path_x_local = -GN_BEND1_R + GN_BEND1_R * math.cos(angle)
        path_z_local = z_lift + GN_BEND1_R * math.sin(angle)
        tan_x, tan_z = -math.sin(angle), math.cos(angle)
    else:
        # Past bend 1: compute end1 and tan1
        end1_x = -GN_BEND1_R + GN_BEND1_R * math.cos(GN_BEND1_SWEEP_RAD)
        end1_z = z_lift + GN_BEND1_R * math.sin(GN_BEND1_SWEEP_RAD)
        tan1_x = -math.sin(GN_BEND1_SWEEP_RAD)
        tan1_z =  math.cos(GN_BEND1_SWEEP_RAD)
        if s < mid_end_s:
            # Mid-straight along tan1
            ds = s - arc1_end_s
            path_x_local = end1_x + ds * tan1_x
            path_z_local = end1_z + ds * tan1_z
            tan_x, tan_z = tan1_x, tan1_z
        else:
            # Past mid-straight: compute mid_end and bend 2 center
            mid_end_x = end1_x + GN_MID_STRAIGHT_LEN * tan1_x
            mid_end_z = end1_z + GN_MID_STRAIGHT_LEN * tan1_z
            # Bend 2 center: 90° ccw of tan1 from mid_end at distance R
            # perpendicular ccw of (a, b) is (-b, a)
            cx2 = mid_end_x + GN_BEND2_R * (-tan1_z)
            cz2 = mid_end_z + GN_BEND2_R *   tan1_x
            rad0_x = mid_end_x - cx2
            rad0_z = mid_end_z - cz2
            angle2 = min(s - mid_end_s, arc2_len) / GN_BEND2_R
            cos_a, sin_a = math.cos(angle2), math.sin(angle2)
            rad_x = rad0_x*cos_a - rad0_z*sin_a
            rad_z = rad0_x*sin_a + rad0_z*cos_a
            tan_x = tan1_x*cos_a - tan1_z*sin_a
            tan_z = tan1_x*sin_a + tan1_z*cos_a
            if s < arc2_end_s:
                # Inside bend 2
                path_x_local = cx2 + rad_x
                path_z_local = cz2 + rad_z
            else:
                # Tip straight: extend along tan2 from end2
                end2_x = cx2 + rad_x
                end2_z = cz2 + rad_z
                ds = s - arc2_end_s
                path_x_local = end2_x + ds * tan_x
                path_z_local = end2_z + ds * tan_z

    # Bitangent = tangent rotated 90° clockwise = (tan_z, -tan_x).
    # At s=0, tan = (0, 1) → bit = (1, 0) = +X (matching the sketch's local +X).
    bit_x, bit_z =  tan_z, -tan_x
    world_x = WATER_TUBE_X     + path_x_local
    world_z = WALL_TRANSITION_Z + path_z_local
    return world_x, world_z, bit_x, bit_z


def _dowel_xz(s: float, local_x: float) -> tuple[float, float]:
    """World (X, Z) of a dowel hole at path arclength s and cross-section local_x."""
    px, pz, bx, bz = _path_pos_and_bitangent_at_s(s)
    return px + local_x * bx, pz + local_x * bz


# Three pairs of dowels — all in the 4 mm wall section above the lid:
#   - Bottom pair: 5 mm above WALL_TRANSITION_Z (= lid top), in the
#     vertical-lift portion of the gooseneck. World Z ≈ 73.37.
#   - Middle pair: at the midpoint of the gooseneck mid-straight section.
#   - Top pair (Z+ end / "goose head"): at the midpoint of the tip-straight
#     section (12.5 mm = GN_TIP_STRAIGHT_LEN/2 from the tip end).
# The 3 mm wall vertical section below the lid (Z = TUBE_SHELL_BOTTOM_Z to
# WALL_TRANSITION_Z) has no dowels — the two tube-shell halves are held
# together there by the socket press-fit alone, since 3 mm wall is too
# thin for the dowel features to print reliably.
# Each pair has one dowel in the water -X wall midpoint and one in the
# flavor +X wall midpoint, with positions rotated through the cross-section's
# local frame at each path arclength.
_S_BOTTOM = 5.0   # 5 mm above WALL_TRANSITION_Z, in the vertical lift
_S_MIDDLE = (
    (GN_BEND1_START_Z - WALL_TRANSITION_Z)
    + GN_BEND1_R * GN_BEND1_SWEEP_RAD
    + GN_MID_STRAIGHT_LEN / 2.0
)
_S_TIP = (
    (GN_BEND1_START_Z - WALL_TRANSITION_Z)
    + GN_BEND1_R * GN_BEND1_SWEEP_RAD
    + GN_MID_STRAIGHT_LEN
    + GN_BEND2_R * GN_BEND2_SWEEP_RAD
    + GN_TIP_STRAIGHT_LEN / 2.0
)

TUBE_HALF_DOWEL_POSITIONS_XZ = [
    _dowel_xz(_S_BOTTOM, _DOWEL_LOCAL_X_WATER),
    _dowel_xz(_S_BOTTOM, _DOWEL_LOCAL_X_FLAVOR),
    _dowel_xz(_S_MIDDLE, _DOWEL_LOCAL_X_WATER),
    _dowel_xz(_S_MIDDLE, _DOWEL_LOCAL_X_FLAVOR),
    _dowel_xz(_S_TIP,    _DOWEL_LOCAL_X_WATER),
    _dowel_xz(_S_TIP,    _DOWEL_LOCAL_X_FLAVOR),
]


def _tube_shell_outer_section(z_bottom: float, z_height: float) -> cq.Workplane:
    """Tube wrap outer (water Y-slot + flavor pill + fill rect, all
    ZONE5_WALL on the X sides) extruded vertically over the given Z
    range.

    Water and flavor sides share the same outer Y half-width — the
    larger of (water bore + wall) and (flavor pill + wall) — so the
    cross-section's Y+ and Y- outer apexes meet at the same Y across
    the X range. The water side is a Y-oriented slot rather than a
    circle, so the wall on the extreme -X face stays at ZONE5_WALL
    (= 3 mm) — only the Y apex thickens. See _zone6_outer_sketch's
    docstring for details.
    """
    natural_water_r = WATER_HOLE_DIAMETER / 2.0 + ZONE5_WALL
    natural_pill_y_half = PILL_LENGTH_Y / 2.0 + ZONE5_WALL
    y_half = max(natural_water_r, natural_pill_y_half)
    y_total = 2.0 * y_half
    water_x_width = 2.0 * natural_water_r
    water_outer = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(WATER_TUBE_X, 0)
        .slot2D(y_total, water_x_width, angle=90)
        .extrude(z_height)
    )
    flavor_outer = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(FLAVOR_TUBE_POST_BEND_X, 0)
        .slot2D(y_total,
                PILL_WIDTH_X + 2.0 * ZONE5_WALL, angle=90)
        .extrude(z_height)
    )
    fill_rect = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo((WATER_TUBE_X + FLAVOR_TUBE_POST_BEND_X) / 2.0, 0)
        .rect(FLAVOR_TUBE_POST_BEND_X - WATER_TUBE_X, y_total)
        .extrude(z_height)
    )
    return water_outer.union(flavor_outer).union(fill_rect)


def _tube_shell_inner_section(z_bottom: float, z_height: float) -> cq.Workplane:
    """Tube hole cross-section (water cyl + flavor pill) extruded vertically."""
    water_inner = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(WATER_TUBE_X, 0)
        .circle(WATER_HOLE_DIAMETER / 2.0)
        .extrude(z_height)
    )
    flavor_inner = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(FLAVOR_TUBE_POST_BEND_X, 0)
        .slot2D(PILL_LENGTH_Y, PILL_WIDTH_X, angle=90)
        .extrude(z_height)
    )
    return water_inner.union(flavor_inner)


def _socket_cutter(z_bottom: float, z_height: float) -> cq.Workplane:
    """Socket cross-section (tube shell outer + SOCKET_CLEARANCE radial)
    extruded vertically over the given Z range.

    Cuts material away from the base shell so the tube shell's tongue can
    insert. Tracks the same shared-Y rule as _tube_shell_outer_section
    (water side is a Y-oriented slot, not a circle), plus SOCKET_CLEARANCE
    on every dimension so the socket matches the tongue with uniform
    radial clearance.
    """
    natural_water_r_socket = WATER_HOLE_DIAMETER / 2.0 + ZONE5_WALL + SOCKET_CLEARANCE
    natural_pill_y_half_socket = PILL_LENGTH_Y / 2.0 + ZONE5_WALL + SOCKET_CLEARANCE
    y_half_socket = max(natural_water_r_socket, natural_pill_y_half_socket)
    y_total_socket = 2.0 * y_half_socket
    water_x_width_socket = 2.0 * natural_water_r_socket
    pill_width_socket  = PILL_WIDTH_X  + 2.0 * (ZONE5_WALL + SOCKET_CLEARANCE)
    water_socket = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(WATER_TUBE_X, 0)
        .slot2D(y_total_socket, water_x_width_socket, angle=90)
        .extrude(z_height)
    )
    flavor_socket = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo(FLAVOR_TUBE_POST_BEND_X, 0)
        .slot2D(y_total_socket, pill_width_socket, angle=90)
        .extrude(z_height)
    )
    fill_socket = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .moveTo((WATER_TUBE_X + FLAVOR_TUBE_POST_BEND_X) / 2.0, 0)
        .rect(FLAVOR_TUBE_POST_BEND_X - WATER_TUBE_X, y_total_socket)
        .extrude(z_height)
    )
    return water_socket.union(flavor_socket).union(fill_socket)


def _make_split_box(y_sign: int) -> cq.Workplane:
    """Halfspace box covering Y >= 0 (sign +1) or Y <= 0 (sign -1)."""
    big = 500.0
    if y_sign > 0:
        box = cq.Solid.makeBox(
            2.0 * big, big, 2.0 * big,
            pnt=cq.Vector(-big, 0.0, -big),
        )
    else:
        box = cq.Solid.makeBox(
            2.0 * big, big, 2.0 * big,
            pnt=cq.Vector(-big, -big, -big),
        )
    return cq.Workplane("XY").newObject([box])


def _make_tube_half_dowel_features(y_sign: int) -> cq.Workplane:
    """Cylinders for the dowel features at the Y=0 cut plane.

    All cylinders point from the bearing half's cut face into the other half.
    The bearing half UNIONs them in (as integrated dowels); the other half
    CUTs them away (as matching holes). Both halves use the same cylinder
    geometry — exact match for radius and length.
    """
    EPS = 0.1  # CSG overlap on each end of the cut plane
    direction_sign = -DOWEL_BEARING_HALF_Y_SIGN  # +1 if -Y bears dowels
    is_bearing = (y_sign == DOWEL_BEARING_HALF_Y_SIGN)
    if is_bearing:
        # Dowel cylinder: extends from EPS inside the bearing half (so the
        # union is robust) up to DOWEL_LEN past the cut plane.
        y_start = -EPS * direction_sign
        length  = DOWEL_LEN + EPS
    else:
        # Hole cylinder: cuts from EPS past the cut plane (overlap into the
        # bearing half is harmless — that half does its own intersect first)
        # to DOWEL_LEN + EPS into the non-bearing half.
        y_start = -EPS * direction_sign
        length  = DOWEL_LEN + 2 * EPS

    result = None
    for x, z in TUBE_HALF_DOWEL_POSITIONS_XZ:
        cyl = cq.Solid.makeCylinder(
            DOWEL_R, length,
            pnt=cq.Vector(x, y_start, z),
            dir=cq.Vector(0.0, float(direction_sign), 0.0),
        )
        wp = cq.Workplane("XY").newObject([cyl])
        result = wp if result is None else result.union(wp)
    return result


def build_base_shell() -> cq.Workplane:
    """Lower portion: zones 1-4 + zone 4.5 (the wider lid) + lever clearance.

    Includes a socket cut where the tube shell's tongue plugs in. The socket
    spans Z = TUBE_SHELL_BOTTOM_Z (extends 5 mm below zone 4 top, into zone 4)
    up to ZONE45_Z_TOP (the lid top — far enough to clear zone 6's vertical
    lift coming up through the lid).
    """
    outer = (
        build_zone1_outer()
        .union(build_zone2_outer())
        .union(build_zone3_outer())
        .union(build_zone3_fill_outer())
        .union(build_zone4_outer())
        .union(build_zone45_outer())
    )
    inner = (
        build_zone1_inner_cut()
        .union(build_zone2_inner_cut())
        .union(build_zone3_inner_cut())
        .union(build_zone3_fill_inner_cut())
        .union(build_zone4_inner_cut())
        .union(build_lever_clearance())
    )
    socket = _socket_cutter(
        TUBE_SHELL_BOTTOM_Z,
        SOCKET_TOP_Z - TUBE_SHELL_BOTTOM_Z,
    )
    return outer.cut(inner).cut(socket)


def build_tube_shell() -> cq.Workplane:
    """Tube shell: 3 mm wall around tubes from TUBE_SHELL_BOTTOM_Z up to
    WALL_TRANSITION_Z (= lid top) — sized to fit the base socket — then
    4 mm wall (ZONE5_WALL_ABOVE) for the gooseneck above."""
    vertical_outer = _tube_shell_outer_section(
        TUBE_SHELL_BOTTOM_Z, TUBE_SHELL_HEIGHT_VERTICAL,
    )
    vertical_inner = _tube_shell_inner_section(
        TUBE_SHELL_BOTTOM_Z, TUBE_SHELL_HEIGHT_VERTICAL,
    )
    outer = vertical_outer.union(build_zone6_outer())
    inner = vertical_inner.union(build_zone6_inner_cut())
    return outer.cut(inner)


def build_tube_shell_half(tube_shell: cq.Workplane, y_sign: int) -> cq.Workplane:
    """One half of the tube shell. The bearing half (DOWEL_BEARING_HALF_Y_SIGN)
    has integrated dowels protruding from its Y=0 cut face; the other half
    has matching holes."""
    half = tube_shell.intersect(_make_split_box(y_sign), clean=False)
    features = _make_tube_half_dowel_features(y_sign)
    if y_sign == DOWEL_BEARING_HALF_Y_SIGN:
        return half.union(features, clean=False)
    return half.cut(features, clean=False)


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    base = build_base_shell()
    tube = build_tube_shell()

    # Assembled-view shell = base ∪ tube. The 0.15 mm socket clearance
    # leaves a thin internal gap between socket walls and tongue surface,
    # but visually reads as one continuous solid. This file is what the
    # faucet-assembly script loads to show the shell in full context.
    shell = base.union(tube)
    out = Path(__file__).resolve().parent / "touch-flo-shell.step"
    export_step(shell, str(out))

    print("Touch-Flo shell (work in progress)")
    print(f"  Center:          X = {SHELL_CENTER_X}, Y = {SHELL_CENTER_Y}")
    print(f"  Wall target:     {WALL_THICKNESS_MIN} mm "
          f"(thins to ~2.68 mm at pill +X cap shoulder)")
    print()
    print(f"  Per-side clearance:  {BORE_CLEARANCE} mm "
          f"(applied uniformly: X, Y, radial, AND face-to-face Z)")
    print()
    print(f"  Outer cylinder:  Ø{SHELL_OUTER_DIAMETER:.3f} mm, "
          f"Z = {ZONE1_Z_BOTTOM} → {ZONE1_OUTER_TOP}")
    print(f"                   (lifted {SHELL_OUTER_LIP} mm = WALL+GAP "
          f"above body cyl top at Z={ZONE1_Z_TOP})")
    print(f"  Outer rect+cove: {SHELL_RECT_X_WIDTH:.3f} × {SHELL_RECT_Y_WIDTH} mm, "
          f"Z = {ZONE2_OUTER_BOT} → {ZONE2_Z_TOP}")
    print(f"                   (corners clipped to Ø{SHELL_OUTER_DIAMETER:.3f} cylinder)")
    print(f"    Cove:          R = {COVE_R} mm on Y faces, Z = {ZONE2_OUTER_BOT} → {COVE_TOP_OUTER_Z}")
    print()
    print(f"  Bore cylinder:   Ø{BODY_BORE_DIAMETER} mm at "
          f"({BODY_BORE_X}, {BODY_BORE_Y}), Z = {ZONE1_Z_BOTTOM} → {ZONE2_BORE_BOTTOM}")
    print(f"                   (lifted {BORE_CLEARANCE} mm above body cyl top "
          f"so the bore step gets the same Z gap as the X/Y gaps)")
    print(f"  Bore rect+cove:  {BODY_BORE_RECT_LONG} × {BODY_BORE_RECT_SHORT} mm rect "
          f"∩ Ø{BODY_BORE_DIAMETER} cyl, Z = {ZONE2_BORE_BOTTOM} → {ZONE2_Z_TOP}")
    print(f"                   with R = {COVE_R} mm cove on Y faces, "
          f"Z = {ZONE2_BORE_BOTTOM} → {COVE_TOP_Z}")
    print(f"                   (mirrors body's filler+cove construction)")
    print()
    print(f"  Flavor pill:     {PILL_LENGTH_Y} × {PILL_WIDTH_X} mm "
          f"at ({FLAVOR_TUBE_X}, 0), Y-oriented, full Z = 0 → {ZONE2_Z_TOP}")
    print()
    print(f"  Lever clearance: chamfer ramp on top -X corner, "
          f"Y = ±{LEVER_CLEARANCE_Y_HALF}, top at Z={ZONE2_Z_TOP}")
    print(f"                   -X end:  X={LEVER_RAMP_X_MIN} (outer rect face), "
          f"depth {LEVER_RAMP_DEPTH} mm")
    print(f"                   +X end:  X={LEVER_RAMP_X_START:.4f} "
          f"(bore tangent at Y_HALF = {_BORE_X_AT_LEVER_Y:.4f} "
          f"− {TANGENT_OVERSHOOT} overshoot)")
    print(f"                   slope:   {LEVER_RAMP_ANGLE_DEG:.2f}° (derived)")
    print(f"-> {out.name}")

    # ─── Base + tube-halves for support-free printing ───
    out_base = Path(__file__).resolve().parent / "touch-flo-shell-base.step"
    export_step(base, str(out_base))

    tube_pos = build_tube_shell_half(tube, +1)
    out_tube_pos = Path(__file__).resolve().parent / "touch-flo-shell-tube-half-pos-y.step"
    export_step(tube_pos, str(out_tube_pos))

    tube_neg = build_tube_shell_half(tube, -1)
    out_tube_neg = Path(__file__).resolve().parent / "touch-flo-shell-tube-half-neg-y.step"
    export_step(tube_neg, str(out_tube_neg))

    bearing_label = "-Y" if DOWEL_BEARING_HALF_Y_SIGN < 0 else "+Y"
    print()
    print(f"  Base shell:      zones 1-4 + zone 4.5 (lid) + lever clearance, single piece")
    print(f"                   socket cut Z = {TUBE_SHELL_BOTTOM_Z} → {SOCKET_TOP_Z} "
          f"({SOCKET_DEPTH} mm into zone 4 + full zone 4.5 at the tube footprint)")
    print(f"                   socket cross-section = tube outer + {SOCKET_CLEARANCE} mm radial clearance")
    print(f"  Tube shell:      {ZONE5_WALL:.0f} mm wall up to lid top (Z = {WALL_TRANSITION_Z:.2f}), "
          f"then {ZONE5_WALL_ABOVE:.0f} mm above for the gooseneck;")
    print(f"                   tongue extends {SOCKET_DEPTH} mm below zone 5's nominal bottom "
          f"(Z = {TUBE_SHELL_BOTTOM_Z}) into the base socket. Split at Y=0 into two halves.")
    print(f"                   {len(TUBE_HALF_DOWEL_POSITIONS_XZ)} integrated dowels Ø{2*DOWEL_R:.1f} × "
          f"{DOWEL_LEN} mm on the {bearing_label} half; matching holes on the other half")
    print(f"-> {out_base.name}")
    print(f"-> {out_tube_pos.name}")
    print(f"-> {out_tube_neg.name}")
