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

SHELL_CENTER_X = 1.5875    # match the mounting plate's lateral center
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

# Flavor-tube pill (mirrored from the mounting plate)
FLAVOR_TUBE_X        = 17.3375
FLAVOR_TUBE_HOLE_DIA = 3.6
FLAVOR_TUBE_Y_OFFSET = 1.5875
PILL_LENGTH_Y = 2 * FLAVOR_TUBE_Y_OFFSET + FLAVOR_TUBE_HOLE_DIA   # 6.775
PILL_WIDTH_X  = FLAVOR_TUBE_HOLE_DIA                                # 3.6


# ═══════════════════════════════════════════════════════
# SHELL OUTER (derived from wall-thickness target)
# ═══════════════════════════════════════════════════════
#
# Wall thickness is set at the body bore's farthest edge from the
# shell center. The body bore is offset by SHELL_CENTER_X mm from
# shell center, so its farthest perimeter point (in -X) sits at
# distance SHELL_CENTER_X + body_bore_radius from the shell center.
# The pill's +X semicircle is ~0.04 mm farther; the wall is ~0.04 mm
# thinner there. Acceptable.
WALL_THICKNESS_MIN = 3.0   # mm — target at the body bore's -X edge

_BODY_BORE_FARTHEST_FROM_SHELL_CENTER = (
    (SHELL_CENTER_X - BODY_BORE_X) + BODY_BORE_DIAMETER / 2.0
)   # = 17.5875 mm

SHELL_OUTER_R        = _BODY_BORE_FARTHEST_FROM_SHELL_CENTER + WALL_THICKNESS_MIN
SHELL_OUTER_DIAMETER = 2.0 * SHELL_OUTER_R   # = 41.175 mm


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
COVE_R = 5.0

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
SHELL_RECT_X_HALF  = SHELL_OUTER_R                                        # 20.5875
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
WATER_TUBE_OD       = 9.5
WATER_HOLE_DIAMETER = WATER_TUBE_OD + 2.0 * BORE_CLEARANCE          # 10.0

FLAVOR_TUBE_PRE_BEND_X  = FLAVOR_TUBE_X                             # 17.3375
FLAVOR_TUBE_POST_BEND_X = 15.0105

FLAVOR_CUTOUT_CX     = (FLAVOR_TUBE_PRE_BEND_X + FLAVOR_TUBE_POST_BEND_X) / 2.0   # 16.174
FLAVOR_CUTOUT_WIDTH  = (FLAVOR_TUBE_PRE_BEND_X - FLAVOR_TUBE_POST_BEND_X) + PILL_WIDTH_X   # 5.927
FLAVOR_CUTOUT_LENGTH = PILL_LENGTH_Y                                              # 6.775
FLAVOR_CUTOUT_R      = PILL_WIDTH_X / 2.0                                         # 1.8

FILL_X_MIN = 10.46                                                  # back third of water tube


# ZONE 4 — tube wrapper above the arch
#
# A 3 mm-thick shell wrapping just the tube cutouts (water tube + flavor
# slot), starting at the base of the arch (Z=44.25) and extending up to
# ~1.7 mm past the assembly's S-bend completion (bend ends at Z=50.31).
# Built as two pieces unioned:
#   - Water tube wrapper: constant-OD tube (Ø16 outer, Ø10 inner)
#     extruded straight up. No transition.
#   - Flavor wrapper: lofted between bottom and top rounded-rectangle
#     cross-sections — bottom matches zone 3's flavor cutout (rounded
#     rect at FLAVOR_CUTOUT_CX), top matches the existing pill from
#     zones 1+2 (PILL_LENGTH_Y × PILL_WIDTH_X at FLAVOR_TUBE_POST_BEND_X).
#     Linear loft draws the cavity in toward the water tube as Z rises.
ZONE4_Z_BOTTOM = SHELL_ARCH_FOOT_TOP_Z                              # 44.25
ZONE4_Z_TOP    = 52.0                                               # ~1.7 mm past S-bend end (50.31)
ZONE4_HEIGHT   = ZONE4_Z_TOP - ZONE4_Z_BOTTOM                       # 7.75
ZONE4_WALL     = WALL_THICKNESS_MIN                                 # 3.0


# ═══════════════════════════════════════════════════════
# GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════

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
    pill = (
        cq.Workplane("XY")
        .workplane(offset=ZONE1_Z_BOTTOM)
        .moveTo(FLAVOR_TUBE_X, 0)
        .slot2D(PILL_LENGTH_Y, PILL_WIDTH_X, angle=90)
        .extrude(ZONE1_HEIGHT)
    )
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
    pill = (
        cq.Workplane("XY")
        .workplane(offset=ZONE2_Z_BOTTOM)
        .moveTo(FLAVOR_TUBE_X, 0)
        .slot2D(PILL_LENGTH_Y, PILL_WIDTH_X, angle=90)
        .extrude(ZONE2_HEIGHT)
    )

    return bore.union(pill)


def build_zone3_outer() -> cq.Workplane:
    """Two arch wings at ±Y wrapping the body's arch ridges."""
    rect_x_min = SHELL_CENTER_X - SHELL_RECT_X_HALF
    rect_x_max = SHELL_CENTER_X + SHELL_RECT_X_HALF

    def wing(y_bottom: float, y_height: float) -> cq.Workplane:
        return (
            cq.Workplane("XZ")
            .workplane(offset=y_bottom)
            .moveTo(rect_x_min, ZONE3_Z_BOTTOM)
            .lineTo(rect_x_max, ZONE3_Z_BOTTOM)
            .lineTo(rect_x_max, SHELL_ARCH_FOOT_TOP_Z)
            .lineTo(ARCH_X_HALF, SHELL_ARCH_FOOT_TOP_Z)
            .threePointArc((0, SHELL_ARCH_PEAK_Z),
                           (-ARCH_X_HALF, SHELL_ARCH_FOOT_TOP_Z))
            .lineTo(rect_x_min, SHELL_ARCH_FOOT_TOP_Z)
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
        .extrude(SHELL_ARCH_PEAK_Z - ZONE3_Z_BOTTOM)
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


def build_zone3_fill_outer() -> cq.Workplane:
    """Plateau fill behind FILL_X_MIN — same arch profile as the wings,
    extruded across the plateau Y range."""
    rect_x_min = SHELL_CENTER_X - SHELL_RECT_X_HALF
    rect_x_max = SHELL_CENTER_X + SHELL_RECT_X_HALF
    fill_y_thickness = 2.0 * WING_INNER_Y                            # 13.5

    arch_solid = (
        cq.Workplane("XZ")
        .workplane(offset=-WING_INNER_Y)
        .moveTo(rect_x_min, ZONE3_Z_BOTTOM)
        .lineTo(rect_x_max, ZONE3_Z_BOTTOM)
        .lineTo(rect_x_max, SHELL_ARCH_FOOT_TOP_Z)
        .lineTo(ARCH_X_HALF, SHELL_ARCH_FOOT_TOP_Z)
        .threePointArc((0, SHELL_ARCH_PEAK_Z),
                       (-ARCH_X_HALF, SHELL_ARCH_FOOT_TOP_Z))
        .lineTo(rect_x_min, SHELL_ARCH_FOOT_TOP_Z)
        .close()
        .extrude(fill_y_thickness)
    )

    keep_x_box = (
        cq.Workplane("XY")
        .workplane(offset=ZONE3_Z_BOTTOM)
        .moveTo((FILL_X_MIN + rect_x_max) / 2.0, 0)
        .rect(rect_x_max - FILL_X_MIN, fill_y_thickness)
        .extrude(SHELL_ARCH_PEAK_Z - ZONE3_Z_BOTTOM)
    )

    clip_cyl = (
        cq.Workplane("XY")
        .workplane(offset=ZONE3_Z_BOTTOM)
        .moveTo(SHELL_CENTER_X, SHELL_CENTER_Y)
        .circle(SHELL_OUTER_R)
        .extrude(SHELL_ARCH_PEAK_Z - ZONE3_Z_BOTTOM)
    )
    return arch_solid.intersect(keep_x_box).intersect(clip_cyl)


def build_zone3_fill_inner_cut() -> cq.Workplane:
    """Tube cutouts through the plateau fill: water tube + flavor pills."""
    z_height = SHELL_ARCH_PEAK_Z - ZONE3_Z_BOTTOM

    water_hole = (
        cq.Workplane("XY")
        .workplane(offset=ZONE3_Z_BOTTOM)
        .moveTo(WATER_TUBE_X, 0)
        .circle(WATER_HOLE_DIAMETER / 2.0)
        .extrude(z_height)
    )

    flavor_slot = (
        cq.Workplane("XY")
        .workplane(offset=ZONE3_Z_BOTTOM)
        .moveTo(FLAVOR_CUTOUT_CX, 0)
        .rect(FLAVOR_CUTOUT_WIDTH, FLAVOR_CUTOUT_LENGTH)
        .extrude(z_height)
        .edges("|Z")
        .fillet(FLAVOR_CUTOUT_R)
    )

    return water_hole.union(flavor_slot)


def _rounded_rect_sketch(cx: float, w: float, h: float, r: float) -> cq.Sketch:
    return (
        cq.Sketch()
        .rect(w, h)
        .vertices()
        .fillet(r)
        .moved(cq.Location(cq.Vector(cx, 0, 0)))
    )


def _zone4_outer_bottom_sketch() -> cq.Sketch:
    """Bottom of zone 4 outer loft: zone 3's outer cross-section
    (rect ∩ outer cyl) restricted to X ≥ FILL_X_MIN."""
    x_at_y_half = SHELL_CENTER_X + math.sqrt(SHELL_OUTER_R**2 - SHELL_RECT_Y_HALF**2)
    rect_x_max = SHELL_CENTER_X + SHELL_RECT_X_HALF
    y_half = SHELL_RECT_Y_HALF
    return (
        cq.Sketch()
        .segment((FILL_X_MIN, -y_half), (x_at_y_half, -y_half))
        .arc((x_at_y_half, -y_half), (rect_x_max, 0), (x_at_y_half, +y_half))
        .segment((x_at_y_half, +y_half), (FILL_X_MIN, +y_half))
        .segment((FILL_X_MIN, +y_half), (FILL_X_MIN, -y_half))
        .assemble()
    )


def build_zone4_outer() -> cq.Workplane:
    """Three lofts unioned:
      1. From below: cyl-clipped rect at Z=44.25 (XY plane) → tube
         wrapper at Z=52 (XY plane). Vertical loft.
      2. From +Y side: arch lens (X∈[FILL_X_MIN, ARCH_X_HALF], Z under
         the arc) at Y=+11.75 swept inward across to Y=0 in parallel
         XZ planes.
      3. From -Y side: mirror of (2).

    The three lofts are unioned with no surface blending — internal
    seams will be visible where the solids meet, but the union covers
    the volume the user described.
    """
    # Arc geometry (the body arch's outer arc, lifted by SHELL_OUTER_LIP):
    # passes through (X=±15.75, Z=44.25) and (X=0, Z=49.25).
    # Center at (X=0, Z=21.944), radius 27.305.
    _arc_cz = 21.944
    _arc_r2 = 27.305 ** 2
    _arc_z_at_fill = _arc_cz + math.sqrt(_arc_r2 - FILL_X_MIN ** 2)              # ≈ 47.17
    _arc_mid_x     = (FILL_X_MIN + ARCH_X_HALF) / 2.0                            # ≈ 13.105
    _arc_mid_z     = _arc_cz + math.sqrt(_arc_r2 - _arc_mid_x ** 2)              # ≈ 45.90

    # ──────────────────────────────────────────────
    # Loft 1: from below (XY plane), water + flavor
    # ──────────────────────────────────────────────
    bottom_sk_at_Z = _zone4_outer_bottom_sketch().moved(
        cq.Location(cq.Vector(0, 0, ZONE4_Z_BOTTOM))
    )
    water_top_sk = cq.Sketch().circle(WATER_HOLE_DIAMETER / 2.0 + ZONE4_WALL).moved(
        cq.Location(cq.Vector(WATER_TUBE_X, 0, ZONE4_Z_TOP))
    )
    flavor_top_sk = cq.Sketch().slot(
        PILL_LENGTH_Y - PILL_WIDTH_X,
        PILL_WIDTH_X + 2.0 * ZONE4_WALL,
        angle=90,
    ).moved(
        cq.Location(cq.Vector(FLAVOR_TUBE_POST_BEND_X, 0, ZONE4_Z_TOP))
    )
    water_loft = cq.Workplane("XY").placeSketch(bottom_sk_at_Z, water_top_sk).loft(ruled=True)
    flavor_loft = cq.Workplane("XY").placeSketch(bottom_sk_at_Z, flavor_top_sk).loft(ruled=True)
    loft_from_below = water_loft.union(flavor_loft)

    # ──────────────────────────────────────────────
    # Lofts 2 & 3: from side (XZ at Y=±11.75) up to top (XY at Z=52)
    # Built via Workplane chaining with copyWorkplane — avoids the
    # face-normal flip that Sketch.moved() with rotation produces.
    # ──────────────────────────────────────────────
    def _side_loft_to_circle(y_side: float, cx: float, cy: float, r: float) -> cq.Workplane:
        return (
            cq.Workplane("XZ").workplane(offset=y_side)
            .moveTo(FILL_X_MIN, ZONE4_Z_BOTTOM)
            .lineTo(ARCH_X_HALF, ZONE4_Z_BOTTOM)
            .threePointArc((_arc_mid_x, _arc_mid_z), (FILL_X_MIN, _arc_z_at_fill))
            .close()
            .copyWorkplane(cq.Workplane("XY").workplane(offset=ZONE4_Z_TOP))
            .moveTo(cx, cy)
            .circle(r)
            .loft(ruled=True)
        )

    def _side_loft_to_slot(y_side: float, cx: float, cy: float,
                            length: float, width: float) -> cq.Workplane:
        return (
            cq.Workplane("XZ").workplane(offset=y_side)
            .moveTo(FILL_X_MIN, ZONE4_Z_BOTTOM)
            .lineTo(ARCH_X_HALF, ZONE4_Z_BOTTOM)
            .threePointArc((_arc_mid_x, _arc_mid_z), (FILL_X_MIN, _arc_z_at_fill))
            .close()
            .copyWorkplane(cq.Workplane("XY").workplane(offset=ZONE4_Z_TOP))
            .moveTo(cx, cy)
            .slot2D(length, width, angle=90)
            .loft(ruled=True)
        )

    side_loft_pos_water = _side_loft_to_circle(
        +SHELL_RECT_Y_HALF, WATER_TUBE_X, 0, WATER_HOLE_DIAMETER / 2.0 + ZONE4_WALL,
    )
    side_loft_pos_flavor = _side_loft_to_slot(
        +SHELL_RECT_Y_HALF, FLAVOR_TUBE_POST_BEND_X, 0,
        PILL_LENGTH_Y + 2.0 * ZONE4_WALL,
        PILL_WIDTH_X + 2.0 * ZONE4_WALL,
    )
    side_loft_neg_water = _side_loft_to_circle(
        -SHELL_RECT_Y_HALF, WATER_TUBE_X, 0, WATER_HOLE_DIAMETER / 2.0 + ZONE4_WALL,
    )
    side_loft_neg_flavor = _side_loft_to_slot(
        -SHELL_RECT_Y_HALF, FLAVOR_TUBE_POST_BEND_X, 0,
        PILL_LENGTH_Y + 2.0 * ZONE4_WALL,
        PILL_WIDTH_X + 2.0 * ZONE4_WALL,
    )
    side_loft_pos = side_loft_pos_water.union(side_loft_pos_flavor)
    side_loft_neg = side_loft_neg_water.union(side_loft_neg_flavor)

    # ──────────────────────────────────────────────
    # Union all three + FILL_X_MIN clip
    # ──────────────────────────────────────────────
    keep_x_min_cut = (
        cq.Workplane("XY")
        .workplane(offset=ZONE4_Z_BOTTOM - 1)
        .moveTo(FILL_X_MIN - 50, 0)
        .rect(100, 200)
        .extrude(ZONE4_HEIGHT + 2)
    )
    return (
        loft_from_below
        .union(side_loft_pos)
        .union(side_loft_neg)
        .cut(keep_x_min_cut)
    )


def build_zone4_inner_cut() -> cq.Workplane:
    """Tube cavity: constant water-tube cyl unioned with lofted flavor cavity."""
    water_inner = (
        cq.Workplane("XY")
        .workplane(offset=ZONE4_Z_BOTTOM)
        .moveTo(WATER_TUBE_X, 0)
        .circle(WATER_HOLE_DIAMETER / 2.0)
        .extrude(ZONE4_HEIGHT)
    )

    bottom_inner_sk = _rounded_rect_sketch(
        FLAVOR_CUTOUT_CX, FLAVOR_CUTOUT_WIDTH, FLAVOR_CUTOUT_LENGTH, FLAVOR_CUTOUT_R,
    ).moved(cq.Location(cq.Vector(0, 0, ZONE4_Z_BOTTOM)))
    top_inner_sk = _rounded_rect_sketch(
        FLAVOR_TUBE_POST_BEND_X, PILL_WIDTH_X, PILL_LENGTH_Y, PILL_WIDTH_X / 2.0,
    ).moved(cq.Location(cq.Vector(0, 0, ZONE4_Z_TOP)))
    flavor_inner = (
        cq.Workplane("XY")
        .placeSketch(bottom_inner_sk, top_inner_sk)
        .loft(ruled=True)
    )

    return water_inner.union(flavor_inner)


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


def build_shell() -> cq.Workplane:
    """Top-level shell — zones unioned, with combined inner cut."""
    outer = (
        build_zone1_outer()
        .union(build_zone2_outer())
        .union(build_zone3_outer())
        .union(build_zone3_fill_outer())
        .union(build_zone4_outer())
    )
    inner = (
        build_zone1_inner_cut()
        .union(build_zone2_inner_cut())
        .union(build_zone3_inner_cut())
        .union(build_zone3_fill_inner_cut())
        .union(build_zone4_inner_cut())
        .union(build_lever_clearance())
    )
    return outer.cut(inner)


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    shell = build_shell()

    out = Path(__file__).resolve().parent / "touch-flo-shell.step"
    export_step(shell, str(out))

    print("Touch-Flo shell (work in progress)")
    print(f"  Center:          X = {SHELL_CENTER_X}, Y = {SHELL_CENTER_Y}")
    print(f"  Wall target:     {WALL_THICKNESS_MIN} mm "
          f"(~{WALL_THICKNESS_MIN - 0.04:.2f} mm at pill +X semicircle)")
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
