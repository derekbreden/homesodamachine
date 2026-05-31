"""Touch-Flo faucet assembly — work-in-progress build-up of the user's
faucet vision on top of the reference valve body.

A growing assembly model that combines the harvested Touch-Flo valve
body (read from `../valve-body-reference/touch-flo-valve-body-reference.step`)
with the parts we are designing around it. The script writes a single
multi-solid STEP file so each iteration can be eyeballed in a viewer.

This is NOT the printed shell. The shell will be a separate file that
wraps around the assembly described here. This file is the body +
tubes + (eventually) other inserts that the shell must accommodate.

Coordinates: the repo's +Z-up frame. +Z is height (the body axis runs
along +Z), +X is lateral (the two flavor tubes mirror across the
X = 0 plane), -Y is the front — the gooseneck dispenses toward -Y (the
user's side) and the lever points toward -Y, so the water port and
flavor-tube pill sit BEHIND the body axis at world +Y (the back).

Parts currently modeled:
1. Valve body (loaded from the reference STEP — delivered seated in the
   repo frame: water port toward +Y / back, lever side toward -Y /
   front; loaded without further rotation).
2. Water dispense tube — Ø 9.525 mm (3/8" LLDPE), inserted into the
   body's 10.0 mm water port and extending up through the gooseneck.
   The printed TPU bushing sealing the 0.475 mm diametric (0.2375 mm
   radial) gap (see ../../../printed-parts/faucet/touch-flo-tpu-o-ring/)
   is not modeled here (geometry only; envelope is the bare 9.525 mm OD).
3. Two flavor dispense tubes — Ø 1/4" (6.35 mm), behind the water
   tube. Each tube starts at depth Y = +18.925 mm (butting against the
   body's back face and the other flavor tube), runs vertical from
   Z = -50, then S-bends just above the plateau to come in tangent
   against the water tube. After the bends the tubes run vertical to
   Z = 79, butted against the water tube. Not inserted into the body.
4. Lever (build_lever) — swing-clearance blob. Union of the lever in
   rest position and pressed-down position (+18° around X axis through
   Y = +1.5, Z = 46), each with vertical water-tube clearance for both
   extremes.
5. Mounting plate (loaded from `../../../printed-parts/faucet/touch-flo-mounting-plate/`).
   Ø 54.35 × 4 mm disc centered at depth Y = +3.175, spans Z = [-4, 0].
   Shank hole at (0, 0); flavor-tube pill slot at Y = +18.925. 5 mm
   radial gap from the shell base (Ø 44.35) so the plate reads as a
   finished shoulder under the shell.
6. Shell (loaded from `../../../printed-parts/faucet/touch-flo-shell/`).
   Single-piece shroud covering zones 1–6, centered at depth
   Y = +3.175. Outer Ø 44.35 mm cylindrical base (zone 1, Z = [0, 13])
   → cove transition into a 41.175 × 23.5 mm rectangular column
   (zone 2, Z = [13, 39]) → arch wings + plateau fill over the body's
   arched top (zone 3, Z = [39, 44.25]) → tube wrapper above the arch
   and lever (zones 4 + 4.5 + 5, Z = [44.25, 67.5]) → gooseneck
   wrapper following the bent dispense tubes through bend 1, mid
   straight, bend 2, and the tip (zone 6).
7. Mounting gasket (loaded from `../../../printed-parts/faucet/touch-flo-mounting-gasket/`).
   Ø 54.35 × 2.0 mm TPU 90A disc, sits between the mounting plate and
   the countertop (Z = [-6, -4]). Hole pattern mirrors the plate.

Regenerate:
    tools/cad-venv/bin/python faucet_assembly.py
"""

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
from _cadq_export import export_assembly
from docgen import substitute_py_comments


# Resolve sibling part directories and the harvested-body reference STEP.
_assembly_dir = Path(__file__).resolve().parent
_harvested_dir = _assembly_dir.parent
_repo_hardware_dir = _harvested_dir.parent.parent
_faucet_printed_dir = _repo_hardware_dir / "printed-parts" / "faucet"

ref_body_step = _harvested_dir / "valve-body-reference" / "touch-flo-valve-body-reference.step"

# +Z-up workplane helpers (matching the convention used by the printed
# parts, the cold-core, and the enclosure). World (x, y) tuples on the
# deck plane; extrude along +Z.
sys.path.insert(0, str(_repo_hardware_dir / "printed-parts" / "cadlib"))
from world_workplane import WorldWorkplane, xy_plane_z_up

# Each printed part's public build_*() function already returns +Z-up.
sys.path.insert(0, str(_faucet_printed_dir / "touch-flo-mounting-plate"))
sys.path.insert(0, str(_faucet_printed_dir / "touch-flo-mounting-gasket"))
sys.path.insert(0, str(_faucet_printed_dir / "touch-flo-shell"))
import touch_flo_mounting_plate
import touch_flo_mounting_gasket
import touch_flo_shell


# Reference body geometry. Duplicated from
# `../valve-body-reference/valve_body_reference.py` — keep in sync.
# The Westbrass body's water port sits at depth Y = +port_center_depth
# (BEHIND the body axis, toward the back); +Z is the body's vertical axis.
port_center_depth = 8.875
plateau_z = 39.0
body_od = 31.50  # cylinder OD = rectangle long dim
body_r = body_od / 2
shank_length = 50.0  # shank extends from Z=0 down to Z=-shank_length


# Water dispense tube — ⌀[9.525 mm](WATER_TUBE_OD) (3/8" LLDPE) — drops into the body's
# 10.0 mm water port. The 0.475 mm diametric (0.2375 mm radial) gap is
# taken up by a printed TPU bushing on the real tube (not modeled).
# Extends a comfortable amount into the port for retention, and runs
# through the gooseneck.
# [9.525 mm](WATER_TUBE_OD) — 3/8" LLDPE in millimeters.
water_tube_od = 0.375 * 25.4
water_tube_r = water_tube_od / 2.0
water_tube_above_plateau = 40.0
water_tube_into_port = 15.0
# [24 mm](WATER_TUBE_Z_BOTTOM) — plateau_z minus water_tube_into_port.
water_tube_z_bottom = plateau_z - water_tube_into_port
# [79 mm](WATER_TUBE_Z_TOP) — plateau_z plus water_tube_above_plateau.
water_tube_z_top = plateau_z + water_tube_above_plateau


# Flavor dispense tubes — Ø 1/4" — sit BEHIND the water tube. Not
# inserted into the body. At their lower (deeper) depth, each tube is
# tangent to
#   - the back face of the body (Y = -body_r)
#   - the other flavor tube (so both touch at X = 0)
# Mirror across X = 0: one at +X, one at -X. Z span runs from the
# bottom of the shank up to the top of the water tube.
# [6.35 mm](FLAVOR_TUBE_OD) — 1/4" LLDPE in millimeters.
flavor_tube_od = 1.0 / 4.0 * 25.4
flavor_tube_r = flavor_tube_od / 2.0
# [18.93 mm](FLAVOR_TUBE_DEPTH_LOWER) — tangent to body +Y (back) face (body_r + flavor_tube_r).
flavor_tube_depth_lower = body_r + flavor_tube_r
flavor_tube_x_offset = flavor_tube_r  # ± — tangent to other tube at X=0
flavor_tube_z_bottom = -shank_length
flavor_tube_z_top = water_tube_z_top

# Upper depth is set by tangency to the water tube at the same X:
#   (depth_upper - port_center_depth)² + x_offset² = (water_tube_r + flavor_tube_r)²
# with X constant through both bends.
# [16.1498 mm](FLAVOR_TUBE_DEPTH_UPPER) — Pythagorean tangency to water tube.
flavor_tube_depth_upper = port_center_depth + math.sqrt(
    (water_tube_r + flavor_tube_r) ** 2 - flavor_tube_x_offset ** 2
)

# S-bend absorbs the depth offset between lower and upper positions.
# Bend radius chosen for clean hand-bending of 1/8" SS — 2.5× OD, well
# above the kink threshold and visually generous. Bend angle is derived
# from 2·R·(1 − cos θ) = depth_offset (no middle straight); both bends
# use the same R and θ.
flavor_bend_radius = 8.0
_flavor_depth_offset = flavor_tube_depth_lower - flavor_tube_depth_upper
# [0.5978 rad](FLAVOR_BEND_THETA) — per-bend angle absorbing the S-bend depth offset.
flavor_bend_theta_rad = math.acos(1.0 - _flavor_depth_offset / (2.0 * flavor_bend_radius))

# How far above the plateau the first bend starts. Kept short to mimic
# the user's "shortly after that, as shortly as is reasonable."
pre_bend_rise = 3.0
# [42 mm](PRE_BEND_Z) — plateau_z plus pre_bend_rise; S-bend starts here.
pre_bend_z = plateau_z + pre_bend_rise


# Gooseneck — above the lever's swing envelope all three tubes sweep
# forward (toward -Y, toward the user) with the same shape:
#   1. vertical straight up to bend 1 start
#   2. bend 1 — sweep gn_bend1_sweep_rad at R = gn_bend1_r (tighter)
#   3. angled straight of gn_mid_straight_len
#   4. bend 2 — sweep gn_bend2_sweep_rad at R = gn_bend2_r (wider)
#   5. tip straight of gn_tip_straight_len
# The tip's exit angle below horizontal = (bend1_sweep + bend2_sweep) - 90°.
# Bend-1 midpoint is anchored at Z = lever_top_z + 35, so the start of
# bend 1 sits gn_bend1_r·sin(bend1_sweep/2) below that.
# [52 mm](LEVER_TOP_Z) — plateau_z plus 13 mm lever-top offset.
lever_top_z = plateau_z + 13.0
gn_bend1_r = 30.0
gn_bend2_r = 40.0
gn_bend1_sweep_rad = math.radians(30.0)
gn_bend2_sweep_rad = math.radians(110.0)
# [87 mm](GN_BEND_MID_Z) — bend-1 midpoint anchored 35 mm above lever_top_z.
gn_bend1_mid_z = lever_top_z + 35.0
# [79.24 mm](GN_BEND_START_Z) — bend-1 midpoint minus R·sin(sweep/2).
gn_bend1_start_z = gn_bend1_mid_z - gn_bend1_r * math.sin(gn_bend1_sweep_rad / 2.0)
gn_mid_straight_len = 115.0
gn_tip_straight_len = 25.0

# Flavor tubes sit further +Y than the water tube (deeper, behind it).
# The gooseneck bends toward -Y (forward, toward the user), so flavor
# tubes are on the OUTSIDE of every bend and must trace parallel-offset arcs
# sharing each bend's center of curvature with water — i.e. at the
# *larger* radius water_r + offset_depth. Otherwise the tubes ride
# into each other through the bend (the perpendicular component of the
# centerline separation shrinks below water_r + flavor_r).
_gn_flavor_depth_offset = flavor_tube_depth_upper - port_center_depth
# [37.2748 mm](GN_FLAVOR_BEND_ONE_R) — gn_bend1_r + flavor parallel offset.
gn_flavor_bend1_r = gn_bend1_r + _gn_flavor_depth_offset
# [47.2748 mm](GN_FLAVOR_BEND_TWO_R) — gn_bend2_r + flavor parallel offset.
gn_flavor_bend2_r = gn_bend2_r + _gn_flavor_depth_offset


def load_valve_body():
    """Load the harvested valve body. The harvested STEP is authored
    Z-up matching the repo frame — no rotation is needed on import."""
    return cq.importers.importStep(str(ref_body_step))


def load_mounting_plate():
    """Build the printed mounting plate in the repo's +Z-up frame.
    Source of truth: see
    `hardware/printed-parts/faucet/touch-flo-mounting-plate/touch_flo_mounting_plate.py`."""
    return touch_flo_mounting_plate.build_mounting_plate()


def load_mounting_gasket():
    """Build the printed-TPU mounting gasket in the repo's +Z-up frame.
    Source of truth: see
    `hardware/printed-parts/faucet/touch-flo-mounting-gasket/touch_flo_mounting_gasket.py`."""
    return touch_flo_mounting_gasket.build_mounting_gasket()


def load_shell():
    """Build the printed shell in the repo's +Z-up frame.
    Source of truth: see
    `hardware/printed-parts/faucet/touch-flo-shell/touch_flo_shell.py`."""
    return touch_flo_shell.build_shell()


def _arc_from_tangent(start, tangent, radius, theta_rad, ccw):
    """Compute waypoints of an arc starting at `start` with `tangent`,
    sweeping `theta_rad` with the given `radius`.

    Pure 2D math — no world-frame dependency; just (a, b) tuples in
    whatever 2D space the caller is drawing on.

    ccw=True: tangent rotates counterclockwise. ccw=False: clockwise.
    Returns (mid, end, end_tangent) — all in the same 2D frame."""
    sign = +1 if ccw else -1
    if ccw:
        perp_to_tangent = (-tangent[1], tangent[0])
    else:
        perp_to_tangent = (tangent[1], -tangent[0])
    center = (start[0] + radius * perp_to_tangent[0], start[1] + radius * perp_to_tangent[1])
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


def _gooseneck_segments(start, tangent, bend1_r, bend2_r):
    """Waypoints for the four-segment gooseneck path starting at
    `start` with `tangent`: bend 1 (R=bend1_r, sweep=gn_bend1_sweep_rad)
    → mid straight (gn_mid_straight_len) → bend 2 (R=bend2_r,
    sweep=gn_bend2_sweep_rad) → tip straight (gn_tip_straight_len).
    Both bends turn CCW in the path's 2D frame (the tube_path_plane
    below maps that to a bend toward -world Y — toward the user).

    Returns ((arc1_mid, arc1_end), mid_end, (arc2_mid, arc2_end),
    tip_end) — call sites unpack into threePointArc / lineTo calls."""
    arc1_mid, arc1_end, tan1 = _arc_from_tangent(
        start, tangent, bend1_r, gn_bend1_sweep_rad, ccw=True
    )
    mid_end = (arc1_end[0] + gn_mid_straight_len * tan1[0],
               arc1_end[1] + gn_mid_straight_len * tan1[1])
    arc2_mid, arc2_end, tan2 = _arc_from_tangent(
        mid_end, tan1, bend2_r, gn_bend2_sweep_rad, ccw=True
    )
    tip_end = (arc2_end[0] + gn_tip_straight_len * tan2[0],
               arc2_end[1] + gn_tip_straight_len * tan2[1])
    return (arc1_mid, arc1_end), mid_end, (arc2_mid, arc2_end), tip_end


# Plane for sketching the tube centerline paths. The path lives in the
# world Y-Z plane (the tubes have no lateral X motion), with
#   2D x  =  +world Y   (positive 2D x points BACK)
#   2D y  =  +world Z   (positive 2D y points UP)
# Choosing 2D x = +world Y means the existing CCW arc helpers' positive
# perp direction (which is `-tangent[1], +tangent[0]`, i.e. "left of
# tangent") points in -2D x = -world Y, so a CCW arc bends the path in
# -Y — toward the user / where the gooseneck dispenses (the front of
# the appliance).
tube_path_plane = cq.Plane(origin=(0, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))


def build_water_dispense_tube():
    """Bent water tube — vertical from inside the body's port up to the
    gooseneck, then bend 1, mid straight, bend 2, tip straight. Profile
    is Ø water_tube_od swept along the centerline path."""
    # Path-local 2D frame: (back-depth, height). Built around the path
    # origin; translated to the body's port at the end.
    p_bottom = (0.0, 0.0)
    p_gn_start = (0.0, gn_bend1_start_z - water_tube_z_bottom)

    arc1, mid_end, arc2, tip_end = _gooseneck_segments(
        p_gn_start, (0.0, 1.0), gn_bend1_r, gn_bend2_r
    )

    path = (
        cq.Workplane(tube_path_plane)
        .moveTo(*p_bottom)
        .lineTo(*p_gn_start)
        .threePointArc(*arc1)
        .lineTo(*mid_end)
        .threePointArc(*arc2)
        .lineTo(*tip_end)
    )
    # Circular cross-section drawn on a horizontal plane (perpendicular
    # to the path's starting +Z tangent).
    profile = cq.Workplane(xy_plane_z_up).circle(water_tube_r)
    tube = profile.sweep(path, transition="round")
    return tube.translate((0, +port_center_depth, water_tube_z_bottom))


def _build_flavor_tube_at_origin():
    """Build one bent flavor tube at the path origin (2D path-frame
    origin, not yet in its world position).

    Path:
      1. Vertical from the path origin up to the S-bend start (pre_bend_z)
      2. S-bend (CCW + CW pair) shifting depth by
         flavor_tube_depth_lower − flavor_tube_depth_upper toward the
         water tube, ending tangent to +Z by construction
      3. Vertical from S-bend end up to the gooseneck start
         (Z = gn_bend1_start_z, in tube-local coords)
      4. Gooseneck: bend 1 → mid straight → bend 2 → tip, all bending
         toward -Y (toward the user). Each bend uses its own parallel-
         offset radius (gn_flavor_bend1_r / gn_flavor_bend2_r), so the
         flavor tube traces a parallel-offset arc on the outside of
         each gooseneck bend, staying tangent to the water tube.
    """
    p_bottom = (0.0, 0.0)
    p_s_bend_start = (0.0, pre_bend_z - flavor_tube_z_bottom)

    # S-bend (CCW then CW, ends tangent to +Z by construction).
    s1_mid, s1_end, s1_tangent = _arc_from_tangent(
        p_s_bend_start, (0.0, 1.0), flavor_bend_radius, flavor_bend_theta_rad, ccw=True
    )
    s2_mid, s2_end, s2_tangent = _arc_from_tangent(
        s1_end, s1_tangent, flavor_bend_radius, flavor_bend_theta_rad, ccw=False
    )

    # Vertical to the gooseneck start, depth unchanged.
    p_gn_start = (s2_end[0], gn_bend1_start_z - flavor_tube_z_bottom)

    arc1, mid_end, arc2, tip_end = _gooseneck_segments(
        p_gn_start, s2_tangent, gn_flavor_bend1_r, gn_flavor_bend2_r
    )

    path = (
        cq.Workplane(tube_path_plane)
        .moveTo(*p_bottom)
        .lineTo(*p_s_bend_start)
        .threePointArc(s1_mid, s1_end)
        .threePointArc(s2_mid, s2_end)
        .lineTo(*p_gn_start)
        .threePointArc(*arc1)
        .lineTo(*mid_end)
        .threePointArc(*arc2)
        .lineTo(*tip_end)
    )

    profile = cq.Workplane(xy_plane_z_up).circle(flavor_tube_r)
    return profile.sweep(path, transition="round")


def build_flavor_tube(x_sign):
    """One Ø 1/4" flavor tube placed at its world position.

    Built at the path origin, then translated to
    (x_sign · flavor_tube_x_offset, +flavor_tube_depth_lower,
    flavor_tube_z_bottom) — i.e. to +Y, behind the body axis (the back).
    x_sign ∈ {±1} selects which lateral side; the two tubes mirror
    across the X = 0 plane."""
    tube = _build_flavor_tube_at_origin()
    return tube.translate((
        x_sign * flavor_tube_x_offset,
        +flavor_tube_depth_lower,
        flavor_tube_z_bottom,
    ))


# Lever pivot — axis parallel to world X at (Y = lever_pivot_y, Z = lever_pivot_z).
# The lever swings between rest (0°) and pressed (+lever_press_angle_deg)
# around this axis, sweeping the clearance volume the shell must avoid.
lever_pivot_y = +1.5
lever_pivot_z = plateau_z + 7.0
lever_press_angle_deg = 18.0


def build_lever():
    """The lever as a swing-clearance blob: union of rest position +
    pressed-down position.

    The shell needs to clear the volume the lever sweeps through during
    actuation, not just the rest envelope. Modeling that as the union
    of the two extremes (0° and -lever_press_angle_deg around the pivot)
    is a deliberate approximation — visually an "ugly blob" — but it
    captures what the shell must avoid. Each position carries its own
    vertical water-tube clearance cut.

    Geometry:
      - The lever's body is a 13 (X) × 15 (Y) × 12 (Z) box,
        centered laterally on X = 0, spanning depth Y = [-6, +9]
        (so its back end abuts the body at +Y and its front face sits
        at Y = -6, where the user presses), at height Z = [plateau_z+1,
        plateau_z+13].
      - From the front face it tapers forward as a 13 × shrinking-Z
        tongue out to Y = -42 — the visible "handle" sticking out
        toward the user.
      - The pivot axis is parallel to world X (lateral), passing
        through (X = 0, Y = +1.5, Z = plateau_z + 7), so the lever
        rotates in the Y-Z plane (no lateral motion).
    """
    # Cylinder cut for the water tube clearance through the lever.
    # The water tube sits at world Y = +port_center_depth (just back of
    # the body axis); the cut is 0.125 mm further +Y to give a small
    # clearance margin. Vertical cut along +Z from the lever's bottom
    # face upward; tall enough (50 mm) to cover both lever positions.
    cut_cylinder = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=plateau_z + 1)
        .moveTo((0, +(port_center_depth + 0.125)))
        .circle(water_tube_r + 1)
        .extrude(50)
        .unwrap()
    )

    # Tapered tongue extending forward (toward -Y, the user) from the
    # lever's front face. First rect at the front face (Y = -6):
    # 13 (X) × 8.5 (Z), anchored at the bottom in Z so the top edge sits
    # at plateau_z+13. Second rect 36 mm further forward (Y = -42):
    # 13 × 3, anchored at the bottom in Z so the top edge stays at
    # plateau_z+13 (same as the first rect's top edge) and the bottom
    # edge rises from plateau_z+4.5 up to plateau_z+10. Loft connects
    # them — the tongue narrows in Z as it extends forward.
    #
    # Plane: xDir=(1,0,0), normal=(0,-1,0) (sketch perpendicular to
    # world -Y, the front depth direction; workplane offset advances
    # toward -Y). localY = +Z world (height up). Sketch local (x, y)
    # maps to world (x, -offset, y).
    _taper_plane = cq.Plane(
        origin=(0, 0, 0),
        xDir=(1, 0, 0),
        normal=(0, -1, 0),
    )
    add_taper = (
        cq.Workplane(_taper_plane)
        .workplane(offset=6)
        .moveTo(0, plateau_z + 4.5)
        .rect(13, 8.5, centered=(True, False))
        .workplane(offset=36)
        .moveTo(0, plateau_z + 10)
        .rect(13, 3, centered=(True, False))
        .loft(combine=True)
    )

    # Bare lever shape — no clearance cuts, in the rest position.
    # 13 (X) × 15 (Y) footprint, 12 (Z) tall.
    base_lever = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=plateau_z + 1)
        .moveTo((0, +1.5))
        .rect(13, 15)
        .extrude(12)
        .unwrap()
        .union(add_taper)
    )

    # Pivot axis along world X through (X=0, Y=lever_pivot_y, Z=lever_pivot_z).
    # Axis direction +X (so rotation by +lever_press_angle_deg around the
    # axis takes -Y toward -Z, dropping the lever's front tongue — which
    # now points toward -Y, the user — when pressed).
    pivot_a = (0, lever_pivot_y, lever_pivot_z)
    pivot_b = (1, lever_pivot_y, lever_pivot_z)

    # Rest position: lever as-is, with its rest-position water-tube cut.
    lever_rest = base_lever.cut(cut_cylinder)

    # Pressed-down position: rotate down around the pivot, then take
    # the same vertical water-tube clearance cut. The cut is vertical
    # in world coords (+Z axis), so it correctly clears the upright
    # water tube even though the lever itself is tilted.
    lever_pressed = lever_rest.rotate(pivot_a, pivot_b, +lever_press_angle_deg).cut(cut_cylinder)
    lever_rest_final = lever_pressed.rotate(pivot_a, pivot_b, -lever_press_angle_deg)

    # Union of both extremes — the swing-clearance envelope.
    return lever_rest_final.union(lever_pressed)


def build_assembly():
    """Combine the reference body and our new parts into one assembly,
    in the repo's +Z-up frame."""
    body = load_valve_body()
    water_tube = build_water_dispense_tube()
    flavor_tube_pos_x = build_flavor_tube(+1)
    flavor_tube_neg_x = build_flavor_tube(-1)
    lever = build_lever()
    mounting_plate = load_mounting_plate()
    mounting_gasket = load_mounting_gasket()
    shell = load_shell()

    silver = cq.Color(0.85, 0.85, 0.88)  # near-stainless silver
    petg_tan = cq.Color(0.85, 0.78, 0.62)  # printed-part tan
    tpu_black = cq.Color(0.15, 0.15, 0.15)  # TPU 90A black gasket — slightly
                                            # lighter than the body so the two
                                            # read apart

    assy = cq.Assembly(name="touch-flo-faucet-assembly")
    assy.add(body, name="valve_body", color=cq.Color("black"))
    assy.add(water_tube, name="water_dispense_tube", color=silver)
    assy.add(flavor_tube_pos_x, name="flavor_tube_pos_x", color=silver)
    assy.add(flavor_tube_neg_x, name="flavor_tube_neg_x", color=silver)
    assy.add(lever, name="lever", color=silver)
    assy.add(mounting_plate, name="mounting_plate", color=petg_tan)
    assy.add(mounting_gasket, name="mounting_gasket", color=tpu_black)
    assy.add(shell, name="shell", color=petg_tan)
    return assy


def main():
    assy = build_assembly()

    out = _assembly_dir / "touch-flo-faucet-assembly.step"
    # cq.Assembly.save() emits a deprecation warning in this CadQuery
    # version but still produces correct multi-solid STEP. The
    # cq.exporters.export(assy, ...) replacement currently rejects
    # Assembly objects on this install — revisit when the venv is bumped.
    export_assembly(assy, str(out))

    bend1_deg = math.degrees(gn_bend1_sweep_rad)
    bend2_deg = math.degrees(gn_bend2_sweep_rad)
    tip_below_horiz = (bend1_deg + bend2_deg) - 90.0
    print("Touch-Flo faucet assembly")
    print(f"  Reference body:        {ref_body_step.name}")
    print(f"  Water dispense tube:   Ø{water_tube_od:.3f} mm")
    print(f"                         Z_bottom = {water_tube_z_bottom:.2f} mm "
          f"({water_tube_into_port} mm into port)")
    print(f"                         vertical → gooseneck")
    print(f"                         center at X=0, Y={+port_center_depth:.3f} mm")
    print(f"  Flavor tubes (×2):     Ø{flavor_tube_od:.3f} mm")
    print(f"                         Z_bottom = {flavor_tube_z_bottom:.1f} mm")
    print(f"                         lower depth = {flavor_tube_depth_lower:.4f} mm "
          f"(tangent to body back face + to each other)")
    print(f"                         upper depth = {flavor_tube_depth_upper:.4f} mm "
          f"(tangent to water tube + to each other)")
    print(f"                         X = ±{flavor_tube_x_offset:.4f} mm (constant)")
    print(f"                         S-bend: 2 × R{flavor_bend_radius:.1f} mm "
          f"@ {math.degrees(flavor_bend_theta_rad):.2f}° starting at Z = {pre_bend_z:.1f}")
    print(f"  Gooseneck:             bend 1 {bend1_deg:.0f}°, bend 2 {bend2_deg:.0f}°, "
          f"midpoint Z={gn_bend1_mid_z:.1f}, start Z={gn_bend1_start_z:.2f}")
    print(f"                         bend 1: water R={gn_bend1_r:.2f} mm, "
          f"flavor R={gn_flavor_bend1_r:.2f} mm (parallel offset)")
    print(f"                         bend 2: water R={gn_bend2_r:.2f} mm, "
          f"flavor R={gn_flavor_bend2_r:.2f} mm (parallel offset)")
    print(f"                         {gn_mid_straight_len} mm angled straight "
          f"@ {bend1_deg:.0f}° from vertical")
    print(f"                         {gn_tip_straight_len} mm tip "
          f"({tip_below_horiz:.0f}° below horizontal)")
    print(f"  Mounting plate:        touch_flo_mounting_plate.build_mounting_plate()")
    print(f"  Mounting gasket:       touch_flo_mounting_gasket.build_mounting_gasket()")
    print(f"  Shell (zones 1-6):     touch_flo_shell.build_shell()")
    print(f"-> {out.name}")

    substitute_py_comments(
        Path(__file__),
        variables={
            "WATER_TUBE_OD": f"{water_tube_od:.4g} mm",
            "WATER_TUBE_Z_BOTTOM": f"{water_tube_z_bottom:.4g} mm",
            "WATER_TUBE_Z_TOP": f"{water_tube_z_top:.4g} mm",
            "FLAVOR_TUBE_OD": f"{flavor_tube_od:.4g} mm",
            "FLAVOR_TUBE_DEPTH_LOWER": f"{flavor_tube_depth_lower:.4g} mm",
            "FLAVOR_TUBE_DEPTH_UPPER": f"{flavor_tube_depth_upper:.4f} mm",
            "FLAVOR_BEND_THETA": f"{flavor_bend_theta_rad:.4f} rad",
            "PRE_BEND_Z": f"{pre_bend_z:.4g} mm",
            "LEVER_TOP_Z": f"{lever_top_z:.4g} mm",
            "GN_BEND_MID_Z": f"{gn_bend1_mid_z:.4g} mm",
            "GN_BEND_START_Z": f"{gn_bend1_start_z:.2f} mm",
            "GN_FLAVOR_BEND_ONE_R": f"{gn_flavor_bend1_r:.4f} mm",
            "GN_FLAVOR_BEND_TWO_R": f"{gn_flavor_bend2_r:.4f} mm",
        },
        expected_counts={
            "WATER_TUBE_OD": 2,
            "WATER_TUBE_Z_BOTTOM": 1,
            "WATER_TUBE_Z_TOP": 1,
            "FLAVOR_TUBE_OD": 1,
            "FLAVOR_TUBE_DEPTH_LOWER": 1,
            "FLAVOR_TUBE_DEPTH_UPPER": 1,
            "FLAVOR_BEND_THETA": 1,
            "PRE_BEND_Z": 1,
            "LEVER_TOP_Z": 1,
            "GN_BEND_MID_Z": 1,
            "GN_BEND_START_Z": 1,
            "GN_FLAVOR_BEND_ONE_R": 1,
            "GN_FLAVOR_BEND_TWO_R": 1,
        },
    )


if __name__ == "__main__":
    main()
