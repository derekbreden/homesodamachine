"""
Touch-Flo shell — printed shroud that wraps around the harvested faucet
body, the flavor tubes, and (eventually) the lever swing volume. Sits
on top of the touch-flo-mounting-plate.

WORK IN PROGRESS — GROWING BOTTOM-UP
====================================
This file is being grown one zone at a time, starting at the deck and
moving up. Currently covers ZONE 1 + ZONE 2 — the first 39 mm of the
body, through the cylinder→rectangle transition.

ZONE 1 — Z = 0 → 13 — cylindrical region
========================================
- Outer:  filled cylinder, Ø 41.175 mm, centered at world (1.5875, 0).
  Diameter derived from the wall-thickness target (3 mm) at the body
  bore's farthest edge from the shell center.
- Inner hole: union of body bore (Ø 32 mm at world (0, 0)) and the
  flavor-tube pill (6.775 × 3.6 mm at world (17.3375, 0)). The two
  cuts merge into a single connected opening because the body and
  flavor tubes are tangent in the assembly.

ZONE 2 — cylinder→rectangle transition + rect column
=====================================================
The OUTER and INNER (bore) zones have different Z bounds: the bore
follows the body's actual transition Z (13–18) so it clears the body
correctly, while the outer surface lifts its transition by one wall
thickness (SHELL_OUTER_LIP = 3 mm) to put cylindrical shell material
ABOVE the body's cylinder top face. Without this lift, the outer cove
would tangent the body's cylinder ledge from above and there would be
no vertical wall material over the body's top face.

Outer (Z = 16 → 39):
- Rectangle: 41.175 × 23.5 mm (X × Y), centered at the shell center.
  Same X width as the zone 1 cylinder OD (so the X faces flow
  straight up from the cylinder edge with no step). Y faces shrink
  inward by 8.84 mm per side relative to the cylinder edge.
- Cove transition on each Y face, R = 5 mm (mirrors the body's
  transition_fillet_r), spanning Z = 16 → 21. Tangent to the rect
  Y face at Z = 21 and to the cylinder ledge at Z = 16.
- Rectangle corners are clipped to the shell's outer cylinder
  (R = 20.5875 mm) — same approach as the body.

Inner / bore (Z = 13 → 39):
- Inner cut: built with the SAME construction pattern as the body's
  outer (rect column + filler block on each Y face + cove cutter +
  cylinder clip), at 0.5 mm offset dimensions for slip-fit clearance.
  So the bore above the cove follows the body's rect∩cylinder
  profile — its X "faces" are curved arcs, not flat — and through
  the cove zone the bore mirrors the body's outward-bulging
  filler+cove rather than running straight through as a Ø 32
  cylinder (which would poke past the shell's outer cove surface).
  Plus the flavor-tube pill all the way through.

WALL THICKNESS NOTES
====================
Shell zone 1 cylinder OD is derived to give exactly the target wall
thickness at the body bore's farthest point from the shell center
(world (-16, 0), which is 17.5875 mm from the shell center at
(1.5875, 0)). The pill's +X semicircle has a slightly-farther extreme
at ~17.63 mm from the shell center, so the wall at the pill is
~0.04 mm thinner than the target. Acceptable; would need to bump the
OD by ~0.1 mm to make the pill the minimum.

In zone 2, the rectangle inherits the same X half-width as the
cylinder R, so the wall at the X face matches zone 1. Y faces are
3 mm thick over the body bore's Y extent (8.75 mm).

REGENERATE
==========
    tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path

import cadquery as cq


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
# The cutout is built in the lever's REST frame as a 3 mm-thick slab
# that hugs the lever's bottom contour from below by BORE_CLEARANCE,
# then rotated -18° around the pivot at (X=1.5, Z=46) to land in the
# pressed-down position. Result: the cut's surfaces are sloped at the
# lever's pressed-down angle and ride directly under the pressed lever
# instead of dropping into a flat-bottomed pocket below it.
#
# Lever rest geometry (mirrored from faucet-assembly's build_lever):
#   - Head: X∈[-6, +9], Z∈[40, 52], bottom flat at Z=40
#   - Taper: bottom rises from Z=44.5 at X=-6 to Z=49 at X=-42
# These two segments form a stepped bottom contour, so the cutout is
# built as two slabs unioned together.

LEVER_PIVOT_X = 1.5
LEVER_PIVOT_Z = 46.0
LEVER_PRESS_ANGLE_DEG = -18.0

LEVER_HEAD_X_MIN = -6.0
LEVER_HEAD_X_MAX = +9.0
LEVER_HEAD_BOT_Z_REST = 40.0

LEVER_TAPER_X_MIN = -42.0                                          # user end
LEVER_TAPER_BOT_Z_AT_JUNCTION_REST = 44.5
LEVER_TAPER_BOT_Z_AT_USER_REST     = 49.0

LEVER_Y_HALF         = 6.5
LEVER_CLEARANCE_Y_HALF = LEVER_Y_HALF + BORE_CLEARANCE              # 6.75
LEVER_CLEARANCE_THICK  = 3.0                                        # mm (in rest frame)
LEVER_HEAD_X_MAX_CUT   = LEVER_HEAD_X_MAX + 2.0                     # +X margin past head end

# Shell rectangle. X width matches the cylinder OD so the X faces flow
# straight up from the cylinder. Y half is body-bore-Y plus the wall.
SHELL_RECT_X_HALF  = SHELL_OUTER_R                                        # 20.5875
SHELL_RECT_Y_HALF  = BODY_BORE_RECT_SHORT / 2.0 + WALL_THICKNESS_MIN      # 11.75
SHELL_RECT_X_WIDTH = 2.0 * SHELL_RECT_X_HALF
SHELL_RECT_Y_WIDTH = 2.0 * SHELL_RECT_Y_HALF


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


def build_lever_clearance() -> cq.Workplane:
    """Sloped slab hugging the lever's pressed-down underside.

    Built in the lever's REST frame as a 3 mm-thick volume sitting
    BORE_CLEARANCE below the lever's bottom contour, then rotated by
    LEVER_PRESS_ANGLE_DEG around the pivot to land under the pressed
    lever. Two pieces:

      - Head slab: rectangle X∈[-6, +11], Z∈[36.75, 39.75] (3 mm
        below the head's flat bottom at rest Z=40, minus clearance).
      - Taper slab: trapezoid following the taper's sloped bottom
        from X=-6 to X=-42, 3 mm thick perpendicular to the rest-Z
        axis (top edge BORE_CLEARANCE below taper bottom).

    After rotation, the cut surfaces are sloped at the lever's
    pressed-down angle, so the cutout depth in world Z is
    ~3·cos(18°) ≈ 2.85 mm and the cut hugs the pressed lever instead
    of dropping into a flat-bottomed pocket beneath it.
    """
    head_top = LEVER_HEAD_BOT_Z_REST - BORE_CLEARANCE                    # 39.75
    head_bot = head_top - LEVER_CLEARANCE_THICK                          # 36.75
    taper_top_junction = LEVER_TAPER_BOT_Z_AT_JUNCTION_REST - BORE_CLEARANCE  # 44.25
    taper_top_user     = LEVER_TAPER_BOT_Z_AT_USER_REST     - BORE_CLEARANCE  # 48.75
    taper_bot_junction = taper_top_junction - LEVER_CLEARANCE_THICK      # 41.25
    taper_bot_user     = taper_top_user     - LEVER_CLEARANCE_THICK      # 45.75

    y_half = LEVER_CLEARANCE_Y_HALF

    head_slab = (
        cq.Workplane("XZ")
        .workplane(offset=-y_half)
        .polyline([
            (LEVER_HEAD_X_MAX_CUT, head_bot),
            (LEVER_HEAD_X_MIN,     head_bot),
            (LEVER_HEAD_X_MIN,     head_top),
            (LEVER_HEAD_X_MAX_CUT, head_top),
        ]).close()
        .extrude(2.0 * y_half)
    )
    taper_slab = (
        cq.Workplane("XZ")
        .workplane(offset=-y_half)
        .polyline([
            (LEVER_HEAD_X_MIN,  taper_bot_junction),
            (LEVER_TAPER_X_MIN, taper_bot_user),
            (LEVER_TAPER_X_MIN, taper_top_user),
            (LEVER_HEAD_X_MIN,  taper_top_junction),
        ]).close()
        .extrude(2.0 * y_half)
    )

    pivot_a = (LEVER_PIVOT_X, 0, LEVER_PIVOT_Z)
    pivot_b = (LEVER_PIVOT_X, 1, LEVER_PIVOT_Z)
    return head_slab.union(taper_slab).rotate(pivot_a, pivot_b, LEVER_PRESS_ANGLE_DEG)


def build_shell() -> cq.Workplane:
    """Top-level shell — zones 1 and 2 unioned, with combined inner cut."""
    outer = build_zone1_outer().union(build_zone2_outer())
    inner = (
        build_zone1_inner_cut()
        .union(build_zone2_inner_cut())
        .union(build_lever_clearance())
    )
    return outer.cut(inner)


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    shell = build_shell()

    out = Path(__file__).resolve().parent / "touch-flo-shell.step"
    cq.exporters.export(shell, str(out))

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
    print(f"  Lever clearance: {LEVER_CLEARANCE_THICK} mm-thick slab in rest frame, "
          f"Y = ±{LEVER_CLEARANCE_Y_HALF}")
    print(f"                   rotated {LEVER_PRESS_ANGLE_DEG}° around pivot "
          f"({LEVER_PIVOT_X}, 0, {LEVER_PIVOT_Z}) — hugs pressed lever underside")
    print(f"-> {out.name}")
