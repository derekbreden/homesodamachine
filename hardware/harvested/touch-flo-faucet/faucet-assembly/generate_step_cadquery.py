"""
Touch-Flo faucet assembly — work-in-progress build-up of the user's
faucet vision on top of the reference valve body.

WHAT THIS IS
============
A growing assembly model that combines the harvested Touch-Flo valve
body (read from `../valve-body-reference/touch-flo-valve-body-reference.step`)
with the parts we are designing around it. The script writes a single
multi-solid STEP file so each iteration can be eyeballed in a viewer.

This is NOT the printed shell. The shell will be a separate file that
wraps around the assembly described here. This file is the body +
tubes + (eventually) other inserts that the shell must accommodate.

PARTS CURRENTLY MODELED
=======================
1. Valve body (loaded from the reference STEP — never modified here).
2. Water dispense tube — Ø 9.5 mm × straight section, inserted into
   the body's water port and extending 40 mm above the plateau.
   O-rings on the actual tube exist but are not modeled (geometry
   only; envelope is the bare 9.5 mm OD).
3. Two flavor dispense tubes — Ø 1/8" (3.175 mm), behind the water
   tube. Each tube starts at X = BODY_R + tube_R = 17.3375 mm (butting
   against the body's +X rectangular face and the other flavor tube),
   runs vertical from Z = -50, then S-bends just above the plateau to
   come in tangent against the water tube. After the bends the tubes
   run vertical to Z = 79, butted against the water tube. Not inserted
   into the body.
4. Lever (build_lever) — swing-clearance blob. Union of the lever in
   rest position and pressed-down position (-18° around X=1.5, Z=46),
   each with vertical water-tube clearance for both extremes.
5. Mounting plate (loaded from `../../../printed-parts/touch-flo-mounting-plate/`).
   50 mm × 5 mm disc centered at (1.5875, 0), spans Z = [-5, 0]. Shank
   hole at (0, 0); flavor-tube pill slot at (17.3375, 0).
6. Shell (loaded from `../../../printed-parts/touch-flo-shell/`).
   Work-in-progress, growing bottom-up. Currently covers zones 1 and 2
   (Z = [0, 39]): cylindrical base (Ø 41.175 mm), cove transition on
   the Y faces (R = 5 mm), then a 41.175 × 23.5 mm rectangular column
   with corners clipped to the cylinder profile. Inner cut transitions
   from cylindrical bore to rectangular bore at Z=18 with the flavor-
   tube pill running through.

REGENERATE
==========
    tools/cad-venv/bin/python generate_step_cadquery.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import save_assembly


# ═══════════════════════════════════════════════════════
# REFERENCE BODY GEOMETRY (mirrored from valve-body-reference)
# ═══════════════════════════════════════════════════════
#
# These constants are duplicated from
# `../valve-body-reference/generate_step_cadquery.py`.
# If they change there, update them here too.
#
PORT_CENTER_X = 8.875        # mm — water port center (X axis)
PORT_CENTER_Y = 0.0          # mm — water port center (Y axis)
PLATEAU_Z     = 39.0         # mm — top face of the rectangular body
BODY_OD       = 31.50        # mm — cylinder OD = rectangle long dim
BODY_R        = BODY_OD / 2  # mm — 15.75 mm
SHANK_LENGTH  = 50.0         # mm — shank extends from Z=0 down to Z=-SHANK_LENGTH


# ═══════════════════════════════════════════════════════
# WATER DISPENSE TUBE
# ═══════════════════════════════════════════════════════
#
# A straight Ø 9.5 mm tube that drops into the 9.75 mm water port.
# The 0.25 mm radial gap is taken up by O-rings on the real tube
# (not modeled). The tube extends a comfortable amount into the
# port for retention, and 40 mm above the plateau for visualization.
# Eventually this tube will be bent; for now it is a straight stub.
#
WATER_TUBE_OD            = 0.25 * 25.4   # 6.35 mm — 1/4" LLDPE tubing
                                          # (replaces the factory 9.5 mm tube;
                                          # sealed in body's 9.75 mm port via
                                          # a printed TPU grommet — separate part)
WATER_TUBE_ABOVE_PLATEAU = 40.0   # mm — length above the plateau
WATER_TUBE_INTO_PORT     = 15.0   # mm — length inserted into the port

WATER_TUBE_Z_BOTTOM = PLATEAU_Z - WATER_TUBE_INTO_PORT     # 24.0 mm
WATER_TUBE_Z_TOP    = PLATEAU_Z + WATER_TUBE_ABOVE_PLATEAU # 79.0 mm
WATER_TUBE_LENGTH   = WATER_TUBE_Z_TOP - WATER_TUBE_Z_BOTTOM


# ═══════════════════════════════════════════════════════
# FLAVOR DISPENSE TUBES (×2)
# ═══════════════════════════════════════════════════════
#
# Two Ø 1/8" tubes behind the water tube. They are NOT inserted into
# the body — they sit alongside it. Each tube is tangent to:
#   - the +X rectangular face of the body (X = BODY_R = 15.75 mm)
#   - the other flavor tube (so both touch at Y = 0)
#
# Mirror across the X-Z plane: one at +Y, one at -Y.
# Tube centers are therefore at:
#   X = BODY_R + (FLAVOR_TUBE_OD / 2) = 17.3375 mm
#   Y = ± (FLAVOR_TUBE_OD / 2)        = ±1.5875 mm
#
# Z span matches the working height of the assembly:
#   bottom = bottom of the shank (Z = -SHANK_LENGTH = -50 mm)
#   top    = top of the water tube  (Z = WATER_TUBE_Z_TOP = 79 mm)
#
FLAVOR_TUBE_OD       = 1.0/8.0 * 25.4   # 3.175 mm — 1/8"
FLAVOR_TUBE_R        = FLAVOR_TUBE_OD / 2.0
FLAVOR_TUBE_X        = BODY_R + FLAVOR_TUBE_R           # 17.3375 mm — initial X
FLAVOR_TUBE_Y_OFFSET = FLAVOR_TUBE_R                    # ±1.5875 mm — constant
FLAVOR_TUBE_Z_BOTTOM = -SHANK_LENGTH                    # -50.0 mm
FLAVOR_TUBE_Z_TOP    = WATER_TUBE_Z_TOP                 # 79.0 mm

# S-bend geometry: each flavor tube rises vertical, S-bends in toward
# the water tube just above the plateau, then runs vertical again
# tangent to the water tube up to the top.
#
# Final X position is set by tangency to the water tube at the same Y:
#   (X_FINAL - PORT_CENTER_X)² + Y_OFFSET² = (WATER_TUBE_R + FLAVOR_TUBE_R)²
# with Y constant through both bends.
WATER_TUBE_R = WATER_TUBE_OD / 2.0
_dx_sq = (WATER_TUBE_R + FLAVOR_TUBE_R) ** 2 - FLAVOR_TUBE_Y_OFFSET ** 2
FLAVOR_TUBE_X_FINAL = PORT_CENTER_X + math.sqrt(_dx_sq)  # 15.012 mm

# X offset the S-bend has to absorb (positive number, magnitude only)
_x_offset = FLAVOR_TUBE_X - FLAVOR_TUBE_X_FINAL          # 2.326 mm

# Bend radius: chosen for clean hand-bending of 1/8" SS — 2.5× OD,
# well above the kink threshold and visually generous.
FLAVOR_BEND_RADIUS    = 8.0
# Bend angle is then derived: 2·R·(1 − cos θ) = X_offset (with no middle
# straight). Both bends use the same radius and angle.
FLAVOR_BEND_THETA_RAD = math.acos(1.0 - _x_offset / (2.0 * FLAVOR_BEND_RADIUS))
FLAVOR_BEND_THETA_DEG = math.degrees(FLAVOR_BEND_THETA_RAD)

# How far above the plateau the first bend starts. Kept short to mimic
# the user's "shortly after that, as shortly as is reasonable."
PRE_BEND_RISE = 3.0                                      # mm above plateau
PRE_BEND_Z    = PLATEAU_Z + PRE_BEND_RISE                # 42.0 mm

# Geometry checks:
#  - lower straight (tube-local Z=0 → Z=PRE_BEND_Z − Z_BOTTOM = 94 mm)
#  - bend 1 (arc length R·θ ≈ 4.4 mm, Z gain R·sin θ ≈ 4.2 mm)
#  - bend 2 (mirror of bend 1)


# ═══════════════════════════════════════════════════════
# GOOSENECK BEND (shared between water + flavor tubes)
# ═══════════════════════════════════════════════════════
#
# Above the lever's swing envelope, all three tubes (water + 2 flavor)
# sweep forward toward -X via the same gooseneck shape:
#   1. vertical straight up to bend 1 start
#   2. bend 1 — GN_BEND1_SWEEP_RAD at R = GN_BEND1_R
#   3. angled straight of GN_MID_STRAIGHT_LEN (rises forward)
#   4. bend 2 — GN_BEND2_SWEEP_RAD at R = GN_BEND2_R
#   5. tip straight of GN_TIP_STRAIGHT_LEN
#
# Each bend has its own radius — bend 1 is tighter (faster turn out
# of vertical), bend 2 is wider (gentler curve at the top, sweeping
# the tip down toward the user). The tip's exit angle below horizontal
# = (GN_BEND1_SWEEP_RAD + GN_BEND2_SWEEP_RAD) - 90°.
#
# Bend-1 midpoint is anchored at Z = LEVER_TOP_Z + 35, so the start of
# bend 1 sits GN_BEND1_R·sin(GN_BEND1_SWEEP_RAD/2) below that. Forward
# direction is -X (lever / user side).
LEVER_TOP_Z         = PLATEAU_Z + 13.0                   # 52.0 mm
GN_BEND1_R          = 30.0                               # water tube — bend 1
GN_BEND2_R          = 40.0                               # water tube — bend 2 (wider)
GN_BEND1_SWEEP_RAD  = math.radians(30.0)
GN_BEND2_SWEEP_RAD  = math.radians(110.0)
GN_BEND1_MID_Z      = LEVER_TOP_Z + 35.0                 # 87.0
GN_BEND1_START_Z    = (
    GN_BEND1_MID_Z
    - GN_BEND1_R * math.sin(GN_BEND1_SWEEP_RAD / 2.0)
)                                                        # ≈ 79.24
GN_MID_STRAIGHT_LEN = 115.0
GN_TIP_STRAIGHT_LEN = 25.0

# Flavor tube bend radii through the gooseneck.
# The flavor tubes sit at +X of the water tube (X-offset in their
# local frame = FLAVOR_TUBE_X_FINAL - PORT_CENTER_X). The gooseneck
# bends toward -X, so flavor tubes are on the OUTSIDE of every bend
# and must trace parallel-offset arcs sharing each bend's center of
# curvature with water — i.e. at the *larger* radius
# R_water + offset_X. Otherwise the tubes ride into each other
# through the bend (the perpendicular component of the centerline
# separation shrinks below R_water + R_flavor).
_GN_FLAVOR_OFFSET   = FLAVOR_TUBE_X_FINAL - PORT_CENTER_X    # ≈ 4.49
GN_FLAVOR_BEND1_R   = GN_BEND1_R + _GN_FLAVOR_OFFSET         # ≈ 34.49
GN_FLAVOR_BEND2_R   = GN_BEND2_R + _GN_FLAVOR_OFFSET         # ≈ 64.49


# ═══════════════════════════════════════════════════════
# REFERENCE BODY LOADING
# ═══════════════════════════════════════════════════════

REF_BODY_STEP = (
    Path(__file__).resolve().parent.parent
    / "valve-body-reference"
    / "touch-flo-valve-body-reference.step"
)

MOUNTING_PLATE_STEP = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "printed-parts"
    / "touch-flo-mounting-plate"
    / "touch-flo-mounting-plate.step"
)

SHELL_STEP = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "printed-parts"
    / "touch-flo-shell"
    / "touch-flo-shell.step"
)


def load_valve_body() -> cq.Workplane:
    """Load the harvested valve body from the reference STEP file.

    Read-only — this file never modifies the body geometry.
    """
    return cq.importers.importStep(str(REF_BODY_STEP))


def load_mounting_plate() -> cq.Workplane:
    """Load the printed mounting plate from its printed-parts STEP.

    Read-only here — see
    `hardware/printed-parts/touch-flo-mounting-plate/generate_step_cadquery.py`
    for the source of truth.
    """
    return cq.importers.importStep(str(MOUNTING_PLATE_STEP))


def load_shell() -> cq.Workplane:
    """Load the printed shell from its printed-parts STEP.

    Read-only here — see
    `hardware/printed-parts/touch-flo-shell/generate_step_cadquery.py`
    for the source of truth.
    """
    return cq.importers.importStep(str(SHELL_STEP))


# ═══════════════════════════════════════════════════════
# TUBE BUILDERS
# ═══════════════════════════════════════════════════════

def build_water_dispense_tube() -> cq.Workplane:
    """Bent water tube — vertical from inside the body's port up to
    the gooseneck, then bend 1, mid straight, bend 2, tip straight.
    Profile is Ø WATER_TUBE_OD swept along the centerline path.
    """
    # Tube-local (X-Z) frame: bottom at (0, 0), Z=0 == WATER_TUBE_Z_BOTTOM.
    z_bend_start_local = GN_BEND1_START_Z - WATER_TUBE_Z_BOTTOM

    p_bottom     = (0.0, 0.0)
    p_bend_start = (0.0, z_bend_start_local)

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

    path = (
        cq.Workplane("XZ")
        .moveTo(*p_bottom)
        .lineTo(*p_bend_start)
        .threePointArc(mid1, end1)
        .lineTo(*mid_end)
        .threePointArc(mid2, end2)
        .lineTo(*tip_end)
    )
    profile = cq.Workplane("XY").circle(WATER_TUBE_OD / 2.0)
    tube = profile.sweep(path, transition="round")
    return tube.translate((PORT_CENTER_X, PORT_CENTER_Y, WATER_TUBE_Z_BOTTOM))


def _arc_from_tangent(start, tangent, radius, theta_rad, ccw):
    """Compute waypoints of an arc starting at `start` with `tangent`,
    sweeping `theta_rad` with the given `radius`.

    ccw=True: tangent rotates counterclockwise (tube turns left when
    looking along +Y).
    ccw=False: clockwise.

    Returns (mid, end, end_tangent) — all in the same 2D X-Z frame.
    """
    sign = +1 if ccw else -1
    # Center is perpendicular to tangent, on the bending side.
    if ccw:
        perp = (-tangent[1], tangent[0])    # rotate tangent +90°
    else:
        perp = (tangent[1], -tangent[0])    # rotate tangent -90°
    center = (start[0] + radius * perp[0], start[1] + radius * perp[1])

    # Radial vector from center to start.
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


def _build_flavor_tube_at_origin() -> cq.Workplane:
    """Build one bent flavor tube at the origin.

    Tube-local frame: bottom of the tube at Z = 0, X = 0, going +Z.
    Path:
      1. Vertical from Z=0 up to the S-bend start (PRE_BEND_Z)
      2. S-bend (CCW + CW pair) shifting X by _x_offset toward -X,
         tangent back to (0, 1) at the end
      3. Vertical from S-bend end up to the gooseneck start (Z =
         GN_BEND1_START_Z, in tube-local coords)
      4. Gooseneck: bend 1 → mid straight → bend 2 → tip, all
         bending toward -X. Each bend uses its own parallel-offset
         radius (GN_FLAVOR_BEND1_R / GN_FLAVOR_BEND2_R).
    """
    pre_bend_z_local     = PRE_BEND_Z - FLAVOR_TUBE_Z_BOTTOM
    gn_bend_start_local  = GN_BEND1_START_Z - FLAVOR_TUBE_Z_BOTTOM

    p0 = (0.0, 0.0)
    p1 = (0.0, pre_bend_z_local)

    # S-bend (CCW then CW, returns to vertical).
    mid_s1, end_s1, tan_s1 = _arc_from_tangent(
        p1, (0.0, 1.0), FLAVOR_BEND_RADIUS, FLAVOR_BEND_THETA_RAD, ccw=True
    )
    mid_s2, end_s2, tan_s2 = _arc_from_tangent(
        end_s1, tan_s1, FLAVOR_BEND_RADIUS, FLAVOR_BEND_THETA_RAD, ccw=False
    )
    # tan_s2 is back to (0, 1) by construction.

    # Vertical to the gooseneck start, X unchanged.
    p_gn_start = (end_s2[0], gn_bend_start_local)

    # Gooseneck — each bend uses GN_FLAVOR_BENDn_R (= water's GN_BENDn_R
    # plus the X offset between flavor and water centerlines), so the
    # flavor tube traces a parallel-offset arc on the outside of each
    # bend, staying tangent to the water tube.
    mid1, end1, tan1 = _arc_from_tangent(
        p_gn_start, tan_s2, GN_FLAVOR_BEND1_R, GN_BEND1_SWEEP_RAD, ccw=True
    )
    mid_end = (end1[0] + GN_MID_STRAIGHT_LEN * tan1[0],
               end1[1] + GN_MID_STRAIGHT_LEN * tan1[1])
    mid2, end2, tan2 = _arc_from_tangent(
        mid_end, tan1, GN_FLAVOR_BEND2_R, GN_BEND2_SWEEP_RAD, ccw=True
    )
    tip_end = (end2[0] + GN_TIP_STRAIGHT_LEN * tan2[0],
               end2[1] + GN_TIP_STRAIGHT_LEN * tan2[1])

    path = (
        cq.Workplane("XZ")
        .moveTo(*p0)
        .lineTo(*p1)
        .threePointArc(mid_s1, end_s1)
        .threePointArc(mid_s2, end_s2)
        .lineTo(*p_gn_start)
        .threePointArc(mid1, end1)
        .lineTo(*mid_end)
        .threePointArc(mid2, end2)
        .lineTo(*tip_end)
    )

    profile = cq.Workplane("XY").circle(FLAVOR_TUBE_R)
    return profile.sweep(path, transition="round")


def build_flavor_tube(y_sign: int) -> cq.Workplane:
    """One Ø 1/8" flavor tube placed at its world position.

    Built at the origin, then translated to (FLAVOR_TUBE_X,
    y_sign · FLAVOR_TUBE_Y_OFFSET, FLAVOR_TUBE_Z_BOTTOM).
    """
    tube = _build_flavor_tube_at_origin()
    return tube.translate((
        FLAVOR_TUBE_X,
        y_sign * FLAVOR_TUBE_Y_OFFSET,
        FLAVOR_TUBE_Z_BOTTOM,
    ))


def build_lever() -> cq.Workplane:
    """The lever as a swing-clearance blob: union of rest position +
    pressed-down position.

    The shell needs to clear the volume the lever sweeps through during
    actuation, not just the rest envelope. Modeling that as the union
    of the two extremes (0° and -18° around the pivot at X=1.5, Z=46)
    is a deliberate approximation — visually an "ugly blob" — but it
    captures what the shell must avoid. Each position carries its own
    vertical water-tube clearance cut.
    """
    cut_cylinder = (
        cq.Workplane("XY")
        .workplane(offset=PLATEAU_Z + 1)
        .moveTo(9, 0)
        .circle(WATER_TUBE_OD / 2 + 1)  # slightly larger than water tube for clearance
        .extrude(50)
    )
    add_taper = (
        cq.Workplane("YZ")
        .workplane(offset=-6)
        .moveTo(0, PLATEAU_Z + 4.5)
        .rect(13, 8.5, centered=(True, False))
        .workplane(offset=-36)
        .moveTo(0, PLATEAU_Z + 1 + 9)
        .rect(13, 3, centered=(True, False))
        .loft(combine=True)
    )

    # Bare lever shape — no clearance cuts, in the rest position.
    base_lever = (
        cq.Workplane("YZ")
        .workplane(offset=9)
        .moveTo(0, PLATEAU_Z + 1)
        .rect(13, 12, centered=(True, False))
        .extrude(-15)
        .union(add_taper)
    )

    # Pivot axis: parallel to Y at (X=1.5, Z=46).
    pivot_a = (1.5, 0, PLATEAU_Z + 1 + 6)
    pivot_b = (1.5, 1, PLATEAU_Z + 1 + 6)

    # Rest position: lever as-is, with its rest-position water-tube cut.
    lever_rest = base_lever.cut(cut_cylinder)

    # Pressed-down position: rotate -18° around the pivot, then take
    # the same vertical water-tube clearance cut. The cut is vertical
    # in world coordinates, so it correctly clears the upright water
    # tube even though the lever itself is tilted.
    lever_pressed = lever_rest.rotate(pivot_a, pivot_b, -18).cut(cut_cylinder)

    lever_rest_final = lever_pressed.rotate(pivot_a, pivot_b, 18)

    # Union of both extremes — the swing-clearance envelope.
    return lever_rest_final.union(lever_pressed)


# ═══════════════════════════════════════════════════════
# ASSEMBLY
# ═══════════════════════════════════════════════════════

def build_assembly() -> cq.Assembly:
    """Combine the reference body and our new parts into one assembly."""
    body = load_valve_body()
    water_tube = build_water_dispense_tube()
    flavor_tube_pos_y = build_flavor_tube(+1)
    flavor_tube_neg_y = build_flavor_tube(-1)
    lever = build_lever()
    mounting_plate = load_mounting_plate()
    shell = load_shell()

    silver = cq.Color(0.85, 0.85, 0.88)        # near-stainless silver
    petg_tan = cq.Color(0.85, 0.78, 0.62)      # printed-part tan

    assy = cq.Assembly(name="touch-flo-faucet-assembly")
    assy.add(body, name="valve_body", color=cq.Color("black"))
    assy.add(water_tube, name="water_dispense_tube", color=silver)
    assy.add(flavor_tube_pos_y, name="flavor_tube_pos_y", color=silver)
    assy.add(flavor_tube_neg_y, name="flavor_tube_neg_y", color=silver)
    assy.add(lever, name="lever", color=silver)
    assy.add(mounting_plate, name="mounting_plate", color=petg_tan)
    assy.add(shell, name="shell", color=petg_tan)
    return assy


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def main():
    assy = build_assembly()

    here = Path(__file__).resolve().parent
    out  = here / "touch-flo-faucet-assembly.step"
    # cq.Assembly.save() emits a deprecation warning in this CadQuery
    # version but still produces correct multi-solid STEP. The
    # cq.exporters.export(assy, ...) replacement currently rejects
    # Assembly objects on this install — revisit when the venv is bumped.
    save_assembly(assy, str(out))

    print("Touch-Flo faucet assembly")
    print(f"  Reference body:        {REF_BODY_STEP.name}")
    print(f"  Water dispense tube:   Ø{WATER_TUBE_OD:.3f} mm")
    print(f"                         Z_bottom = {WATER_TUBE_Z_BOTTOM:.2f} mm "
          f"({WATER_TUBE_INTO_PORT} mm into port)")
    print(f"                         vertical → gooseneck")
    print(f"                         center at X={PORT_CENTER_X} mm, Y={PORT_CENTER_Y} mm")
    print(f"  Flavor tubes (×2):     Ø{FLAVOR_TUBE_OD:.3f} mm")
    print(f"                         Z_bottom = {FLAVOR_TUBE_Z_BOTTOM:.1f} mm")
    print(f"                         lower X = {FLAVOR_TUBE_X:.4f} mm "
          f"(tangent to body +X + to each other)")
    print(f"                         upper X = {FLAVOR_TUBE_X_FINAL:.4f} mm "
          f"(tangent to water tube + to each other)")
    print(f"                         Y = ±{FLAVOR_TUBE_Y_OFFSET:.4f} mm (constant)")
    print(f"                         S-bend: 2 × R{FLAVOR_BEND_RADIUS:.1f} mm "
          f"@ {FLAVOR_BEND_THETA_DEG:.2f}° starting at Z = {PRE_BEND_Z:.1f}")
    _b1_deg = math.degrees(GN_BEND1_SWEEP_RAD)
    _b2_deg = math.degrees(GN_BEND2_SWEEP_RAD)
    _tip_below_horiz = (_b1_deg + _b2_deg) - 90.0
    print(f"  Gooseneck:             bend 1 {_b1_deg:.0f}°, bend 2 {_b2_deg:.0f}°, "
          f"midpoint Z={GN_BEND1_MID_Z:.1f}, start Z={GN_BEND1_START_Z:.2f}")
    print(f"                         bend 1: water R={GN_BEND1_R:.2f} mm, "
          f"flavor R={GN_FLAVOR_BEND1_R:.2f} mm (parallel offset)")
    print(f"                         bend 2: water R={GN_BEND2_R:.2f} mm, "
          f"flavor R={GN_FLAVOR_BEND2_R:.2f} mm (parallel offset)")
    print(f"                         {GN_MID_STRAIGHT_LEN} mm angled straight "
          f"@ {_b1_deg:.0f}° from vertical")
    print(f"                         {GN_TIP_STRAIGHT_LEN} mm tip "
          f"({_tip_below_horiz:.0f}° below horizontal)")
    print(f"  Mounting plate:        loaded from printed-parts/")
    print(f"                         {MOUNTING_PLATE_STEP.name}")
    print(f"  Shell (zones 1+2):     loaded from printed-parts/")
    print(f"                         {SHELL_STEP.name}")
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
